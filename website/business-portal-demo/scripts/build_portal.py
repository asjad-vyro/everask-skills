#!/usr/bin/env python3
"""Build a one-file clickable portal demo from a config.

Usage: python3 build_portal.py config.json out.html

Validates the config, generates clearly fake sample rows from the fields,
fills templates/portal.html, syntax-checks the page script with node when node
exists, checks the file has no external URLs, and prints a JSON report.
Standard library only.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "templates", "portal.html")
MAX_WORKING = 8
TYPES = {"text", "number", "date", "select", "email", "phone", "textarea", "boolean"}
DEFAULT_LABELS = {
    "demo_badge": "Demo: sample data", "demo_note": "front-end prototype, no server, no real login",
    "pick_role": "Choose a demo role", "demo_accounts": "Demo account (no real password)",
    "sign_in": "Enter as", "sign_out": "Sign out", "dashboard": "Dashboard", "search": "Search",
    "add": "Add", "edit": "Edit", "delete": "Delete", "save": "Save", "cancel": "Cancel",
    "back": "Back", "details": "Details", "actions": "Actions", "no_rows": "No records",
    "confirm_delete": "Delete this record?",
    "reset": "Reset demo data", "confirm_reset": "Restore the original sample data? Your changes will be lost.",
    "records": "records", "total_of": "Total", "by": "by", "next_step": "next step",
    "next_step_note": "This module is planned for the next step and is not built in this demo.",
    "required": "Required", "role": "Role", "yes": "Yes", "no": "No", "sample": "Sample",
    "menu": "Menu", "read_only": "View only",
}


def die(msg):
    print(json.dumps({"ok": False, "error": msg}, ensure_ascii=False))
    sys.exit(2)


def slug(s, fallback):
    t = re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")
    return t or fallback


def sample_row(m, i, sample):
    row = {"_id": i}
    singular = m.get("singular") or m["name"]
    for n, f in enumerate(m["fields"]):
        t, k = f["type"], f["key"]
        if t == "text":
            row[k] = "%s %s %d" % (sample, singular, i) if n == 0 else "%s %d" % (f["label"], i)
        elif t == "number":
            row[k] = 100 * i
        elif t == "date":
            row[k] = "2025-01-%02d" % ((i * 3) % 28 + 1)
        elif t == "select":
            row[k] = f["options"][(i - 1) % len(f["options"])]
        elif t == "email":
            row[k] = "sample%d@example.com" % i
        elif t == "phone":
            row[k] = "555-01%02d" % i
        elif t == "textarea":
            row[k] = "%s %d" % (f["label"], i)
        elif t == "boolean":
            row[k] = i % 2 == 0
    return row


def main():
    if len(sys.argv) < 3:
        die("usage: build_portal.py config.json out.html")
    try:
        cfg = json.load(open(sys.argv[1], encoding="utf-8"))
    except Exception as e:
        die("cannot read config: %s" % e)
    out = sys.argv[2]
    title = cfg.get("title")
    if not title:
        die("config needs 'title'")
    given = cfg.get("labels", {})
    labels = dict(DEFAULT_LABELS)
    labels.update(given)
    lang = cfg.get("lang", "en")
    mods_in = cfg.get("modules", [])
    if not mods_in:
        die("config needs at least one module")
    roles_in = cfg.get("roles", [])
    if not roles_in:
        die("config needs at least one role")
    modules, ids = [], set()
    for n, m in enumerate(mods_in):
        if not m.get("name"):
            die("module %d has no name" % (n + 1))
        mid = m.get("id") or slug(m["name"], "m%d" % (n + 1))
        if mid in ids:
            die("duplicate module id %r (give modules distinct 'id' values)" % mid)
        ids.add(mid)
        nm = dict(m, id=mid)
        if n >= MAX_WORKING:
            nm["status"] = "next"
            nm["fields"] = nm.get("fields", [])
            nm["rows"] = []
        else:
            nm["status"] = "working"
            fs = m.get("fields") or die("module %r needs 'fields'" % m["name"])
            keys = set()
            nf = []
            for f in fs:
                if not f.get("label"):
                    die("a field in %r has no label" % m["name"])
                f = dict(f)
                f["key"] = f.get("key") or slug(f["label"], "f%d" % (len(nf) + 1))
                if f["key"] in keys:
                    die("duplicate field key %r in %r" % (f["key"], m["name"]))
                keys.add(f["key"])
                f["type"] = f.get("type", "text")
                if f["type"] not in TYPES:
                    die("field %r has unknown type %r (use %s)" % (f["label"], f["type"], ", ".join(sorted(TYPES))))
                if f["type"] == "select" and not f.get("options"):
                    die("select field %r needs 'options'" % f["label"])
                f["required"] = bool(f.get("required", False))
                nf.append(f)
            nm["fields"] = nf
            if m.get("rows"):
                nm["rows"] = []
                for i, r in enumerate(m["rows"], 1):
                    rr = dict(r)
                    rr["_id"] = i
                    nm["rows"].append(rr)
            else:
                cnt = max(5, min(8, int(m.get("seed", 6))))
                nm["rows"] = [sample_row(nm, i, labels["sample"]) for i in range(1, cnt + 1)]
        modules.append(nm)
    roles, rids = [], set()
    for n, r in enumerate(roles_in):
        if not r.get("name"):
            die("role %d has no name" % (n + 1))
        rid = r.get("id") or slug(r["name"], "r%d" % (n + 1))
        if rid in rids:
            die("duplicate role id %r" % rid)
        rids.add(rid)
        for key in ("modules", "readonly"):
            v = r.get(key)
            if isinstance(v, list):
                for x in v:
                    if x not in ids:
                        die("role %r lists unknown module id %r" % (r["name"], x))
        roles.append({"id": rid, "name": r["name"], "modules": r.get("modules", "*"),
                      "readonly": r.get("readonly", [])})
    accent = cfg.get("accent", "#2457c5")
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        die("accent must look like #2457c5")
    rtl = bool(cfg.get("rtl", False))
    final = {"key": slug(cfg.get("key") or title, "app"), "title": title, "lang": lang,
             "labels": labels, "roles": roles, "modules": modules}
    blob = json.dumps(final, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")
    html = open(TEMPLATE, encoding="utf-8").read()
    esc = lambda s: str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    html = (html.replace("__CONFIG_JSON__", blob).replace("__LANG__", esc(lang))
            .replace("__DIR__", "rtl" if rtl else "ltr").replace("__TITLE__", esc(title))
            .replace("__ACCENT__", accent))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    # checks
    rep = {"ok": True, "file": out, "bytes": len(html.encode("utf-8")),
           "modules_working": [m["name"] for m in modules if m["status"] == "working"],
           "modules_next_step": [m["name"] for m in modules if m["status"] == "next"],
           "roles": [{"name": r["name"], "sees": r["modules"], "view_only": r["readonly"]} for r in roles],
           "rows_per_module": {m["name"]: len(m["rows"]) for m in modules if m["status"] == "working"}}
    ext = re.findall(r"(?:https?:)?//[A-Za-z0-9.-]+\.[A-Za-z]{2,}[^\s\"'<>]*", html)
    rep["external_urls"] = sorted(set(ext))
    scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
    node = shutil.which("node")
    if not node:
        rep["syntax_check"] = "skipped (node not found)"
    else:
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "page.js")
            open(p, "w", encoding="utf-8").write("\n".join(scripts))
            r = subprocess.run([node, "--check", p], capture_output=True, text=True)
            rep["syntax_check"] = "passed" if r.returncode == 0 else "FAILED: " + r.stderr[-400:]
    if not role_has_login_view(final):
        rep["warning"] = "no role can see any module"
    if lang != "en":
        rep["untranslated_labels"] = sorted(k for k in DEFAULT_LABELS if k not in given)
    if rep["external_urls"] or rep["syntax_check"].startswith("FAILED"):
        rep["ok"] = False
    print(json.dumps(rep, ensure_ascii=False, indent=1))


def role_has_login_view(final):
    mids = {m["id"] for m in final["modules"]}
    return any(r["modules"] == "*" or (set(r["modules"]) & mids) for r in final["roles"])


if __name__ == "__main__":
    main()
