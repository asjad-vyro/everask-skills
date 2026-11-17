#!/usr/bin/env python3
"""Structural check of an OpenAPI 3.1 YAML file (stdlib only, regex based).
Assumes ordinary block-style YAML with consistent indentation. Not a full validator."""
import re, sys, collections

if len(sys.argv) != 2:
    sys.exit("usage: check_openapi.py openapi.yaml")
lines = open(sys.argv[1], encoding="utf-8").read().splitlines()

def indent(s): return len(s) - len(s.lstrip(" "))
def key_of(s):
    m = re.match(r'\s*["\']?([^"\':]+)["\']?\s*:', s)
    return m.group(1).strip() if m else None

problems = []
# top-level sections and component definitions
section = None; comp = None
defs = collections.defaultdict(set)
comp_indent = None
for ln in lines:
    if not ln.strip() or ln.lstrip().startswith("#"): continue
    i = indent(ln)
    if i == 0:
        section = key_of(ln); comp = None; continue
    if section == "components":
        if comp_indent is None: comp_indent = i
        if i == comp_indent: comp = key_of(ln)
        elif i == comp_indent * 2 and comp:
            k = key_of(ln)
            if k: defs[comp].add(k)

if "openapi: 3.1" not in "\n".join(lines): problems.append("missing 'openapi: 3.1.x' line")
if re.search(r'^\s*nullable\s*:', "\n".join(lines), re.M): problems.append("uses 'nullable:' (3.0 syntax); use type: [X, \"null\"]")

refs = re.findall(r'\$ref:\s*["\']?#/components/(\w+)/([^"\'\s}]+)', "\n".join(lines))
used = collections.Counter()
for kind, name in refs:
    used[(kind, name)] += 1
    if name not in defs[kind]:
        problems.append(f"$ref to missing components/{kind}/{name}")

# operations
methods = {"get", "put", "post", "delete", "patch", "options", "head", "trace"}
ops = []  # dict per operation
in_paths = False; cur_path = None; cur = None; path_i = None; op_i = None
global_security = any(re.match(r'security\s*:\s*(\[\s*\{|\s*$)', l) and not l.startswith(" ") for l in lines) \
    and any(l.startswith("security:") for l in lines)
for ln in lines:
    if not ln.strip() or ln.lstrip().startswith("#"): continue
    i = indent(ln)
    if i == 0:
        in_paths = key_of(ln) == "paths"; cur = None; continue
    if not in_paths: continue
    if path_i is None: path_i = i
    if i == path_i:
        cur_path = key_of(ln); cur = None; continue
    k = key_of(ln)
    if op_i is None and k in methods: op_i = i
    if i == op_i and k in methods:
        cur = {"path": cur_path, "method": k, "id": None, "codes": set(), "security": None, "resp": False}
        ops.append(cur); continue
    if cur is None: continue
    step = op_i - path_i
    if i == op_i + step:
        if k == "operationId": cur["id"] = ln.split(":", 1)[1].strip().strip("\"'")
        elif k == "security": cur["security"] = ln.split(":", 1)[1].strip()
        elif k == "responses": cur["resp"] = True
    elif cur["resp"] and i == op_i + 2 * step and k and re.fullmatch(r'\d{3}|default|[1-5]XX', k):
        cur["codes"].add(k)

ids = collections.Counter(o["id"] for o in ops if o["id"])
for o in ops:
    tag = f'{o["method"].upper()} {o["path"]}'
    if not o["id"]: problems.append(f"{tag}: no operationId")
    elif ids[o["id"]] > 1: problems.append(f"{tag}: duplicate operationId {o['id']}")
    if not o["resp"] or not o["codes"]: problems.append(f"{tag}: no responses found")
    elif not any(c.startswith("2") or c == "default" or c == "2XX" for c in o["codes"]): problems.append(f"{tag}: no 2xx response")
    public = o["security"] is not None and o["security"].replace(" ", "") == "[]"
    if global_security and not public and o["codes"] and "401" not in o["codes"]:
        problems.append(f"{tag}: secured but no 401 response")

unused = [n for n in defs["schemas"] if used[("schemas", n)] == 0]
for n in unused: problems.append(f"schema {n} is never referenced (fine if intentional)")

print(f"paths: {len({o['path'] for o in ops})}  operations: {len(ops)}  schemas: {len(defs['schemas'])}  "
      f"parameters: {len(defs['parameters'])}  responses: {len(defs['responses'])}  securitySchemes: {len(defs['securitySchemes'])}")
if problems:
    print("PROBLEMS:"); [print(" -", p) for p in problems]
else:
    print("No structural problems found.")
