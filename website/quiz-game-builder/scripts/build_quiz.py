#!/usr/bin/env python3
"""Fill the quiz template from a spec file and check it.

Usage: python build_quiz.py TEMPLATE.html SPEC.json OUT.html
SPEC.json: {"config": {title, subtitle, lang, dir, timerSeconds, teams, shuffleQuestions,
            shuffleOptions, ui: {...only the keys you translate...}}, "questions": [...]}
Each question: {"q": str, "options": [str, ...], "answer": index, "explain": str (optional)}
"""
import json, re, sys

def between(text, start, end):
    a = text.index(start) + len(start)
    b = text.index(end)
    return a, b

def main():
    tpl_path, spec_path, out_path = sys.argv[1:4]
    tpl = open(tpl_path, encoding="utf-8").read()
    spec = json.load(open(spec_path, encoding="utf-8"))
    a, b = between(tpl, "/*CONFIG_START*/", "/*CONFIG_END*/")
    default = json.loads(re.search(r"const CONFIG = (\{.*\});", tpl[a:b], re.S).group(1))
    cfg = dict(default)
    user = spec.get("config", {})
    for k, v in user.items():
        if k == "ui":
            cfg["ui"] = {**default["ui"], **v}
        else:
            cfg[k] = v
    if cfg.get("lang", "en") != "en":
        missing = [k for k in default["ui"] if cfg["ui"][k] == default["ui"][k]]
        if missing:
            print("WARNING: these ui texts are still English, translate them unless identical in the language: " + ", ".join(missing))
    if cfg.get("dir") not in ("ltr", "rtl"):
        sys.exit("ERROR: config.dir must be ltr or rtl")
    qs = spec["questions"]
    errs = []
    if not qs:
        errs.append("no questions")
    for i, q in enumerate(qs, 1):
        if not q.get("q"):
            errs.append(f"q{i}: empty text")
        o = q.get("options", [])
        if not (2 <= len(o) <= 6):
            errs.append(f"q{i}: needs 2 to 6 options")
        elif len(set(map(str, o))) != len(o):
            errs.append(f"q{i}: duplicate options")
        if not isinstance(q.get("answer"), int) or not (0 <= q.get("answer", -1) < len(o)):
            errs.append(f"q{i}: answer must be an index into options")
    if errs:
        sys.exit("ERROR: " + "; ".join(errs))
    out = tpl[:a] + "\nconst CONFIG = " + json.dumps(cfg, ensure_ascii=False, indent=2).replace("</", "<\\/") + ";\n" + tpl[b:]
    a, b = between(out, "/*QUESTIONS_START*/", "/*QUESTIONS_END*/")
    out = out[:a] + "\nconst QUESTIONS = " + json.dumps(qs, ensure_ascii=False, indent=1).replace("</", "<\\/") + ";\n" + out[b:]
    open(out_path, "w", encoding="utf-8").write(out)
    print(f"OK: {len(qs)} questions written to {out_path}")
    for i, q in enumerate(qs, 1):
        print(f"{i}. {q['q']} -> {q['options'][q['answer']]}")

main()
