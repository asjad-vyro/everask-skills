#!/usr/bin/env python3
"""Check the staff list, and build the completion tracker from quiz responses.

Usage:
    python3 tracker.py check --staff staff.csv [--languages "English,Arabic,Urdu"]
    python3 tracker.py update --staff staff.csv --responses responses.json
        [--pass-mark 80] [--max-score 10] [--key key.json]
        [--deadline 2026-12-15] [--today 2026-11-30] [--out-dir tracker/]

staff.csv (or .json, a list of objects): one row per person. Headers are matched
loosely: name, email (work email), id (staff/employee ID), manager, manager email,
shift, language. Each person needs an email or an ID.

responses.json: the quiz responses. Pass Typeform's responses export as it comes
(one file per language form, comma-separated: --responses en.json,ar.json; the
person's email or ID is the answer or hidden field with ref "staff_id"), or a list:
    [{"respondent": "<email or staff ID they typed>", "submitted_at": "2026-11-20T10:03:00Z",
      "language": "Arabic", "score": 9}, ...]
    or, instead of "score", "answers": {"q1": "q1_c", ...} scored against --key
    (key.json: {"q1": "q1_c", ...}, the same choice refs in every language, or one
    such object per language: {"English": {...}, "Arabic": {...}}).
    "score" is points out of --max-score (default 10).

check prints: {"people", "rows", "problems", "by_manager", "by_shift", "by_language",
    "managers_without_email"}.
update prints: {"pass_mark", "people", "passed", "failed", "not_started", "all_passed",
    "rows", "dashboard": {"by_manager", "by_shift", "overall"}, "reminders",
    "unmatched_responses", "unscored_responses", "warnings"}; with --out-dir it also writes
    tracker.csv and dashboard.csv there.

A person is "Passed" only when a matched quiz response scored at or above the pass
mark. Nothing else marks anyone complete. Stdlib only, no network.
"""

import csv
import datetime as dt
import json
import os
import re
import sys

FIELDS = {
    "name": ("name", "full name", "employee name", "staff name", "worker", "employee"),
    "email": ("email", "work email", "e-mail", "email address", "work e-mail"),
    "id": ("id", "staff id", "employee id", "employee number", "staff number", "badge",
           "badge number", "payroll number", "employee no", "emp id"),
    "manager": ("manager", "line manager", "supervisor", "team leader", "team lead",
                "manager name", "reports to"),
    "manager_email": ("manager email", "manager e-mail", "line manager email",
                      "supervisor email", "manager work email"),
    "shift": ("shift", "shift pattern", "rota", "crew"),
    "language": ("language", "preferred language", "training language", "lang"),
}
TRACKER_COLUMNS = ["Name", "Email", "Staff ID", "Manager", "Shift", "Language", "Status",
                   "Best score %", "Attempts", "Passed on", "Last attempt", "Overdue"]


def norm_header(h):
    return re.sub(r"[\s_]+", " ", (h or "").strip().lower())


def load_staff(path):
    if path.lower().endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    else:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            sample = fh.read(4096)
            fh.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel
            raw = list(csv.DictReader(fh, dialect=dialect))
    lookup = {alias: field for field, aliases in FIELDS.items() for alias in aliases}
    rows = []
    for item in raw:
        row = {f: "" for f in FIELDS}
        for key, value in item.items():
            field = lookup.get(norm_header(key))
            if field and value is not None and not row[field]:
                row[field] = str(value).strip()
        row["email"] = row["email"].lower()
        if any(row.values()):
            rows.append(row)
    return rows


def person_keys(row):
    return [k for k in (row["email"].lower(), row["id"].strip().lower()) if k]


def count_by(rows, field):
    out = {}
    for r in rows:
        k = r[field] or "(not set)"
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))


def check(rows, languages):
    problems, seen = [], {}
    wanted = {l.strip().lower() for l in languages if l.strip()}
    for i, r in enumerate(rows, 1):
        who = r["name"] or r["email"] or r["id"] or "row %d" % i
        if not r["name"]:
            problems.append({"row": i, "who": who, "problem": "No name"})
        if not r["email"] and not r["id"]:
            problems.append({"row": i, "who": who, "problem": "No email or staff ID: their quiz cannot be matched"})
        elif r["email"] and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", r["email"]):
            problems.append({"row": i, "who": who, "problem": "Email looks wrong: %s" % r["email"]})
        for field, label in (("manager", "manager"), ("shift", "shift"), ("language", "language")):
            if not r[field]:
                problems.append({"row": i, "who": who, "problem": "No %s" % label})
        if r["language"] and wanted and r["language"].lower() not in wanted:
            problems.append({"row": i, "who": who,
                             "problem": "Language '%s' is not in the requested languages" % r["language"]})
        for k in person_keys(r):
            if k in seen:
                problems.append({"row": i, "who": who,
                                 "problem": "Same email or ID as row %d" % seen[k]})
            else:
                seen[k] = i
    managers = {}
    for r in rows:
        if r["manager"]:
            managers.setdefault(r["manager"], set())
            if r["manager_email"]:
                managers[r["manager"]].add(r["manager_email"])
    return {
        "people": len(rows), "rows": rows, "problems": problems,
        "by_manager": count_by(rows, "manager"), "by_shift": count_by(rows, "shift"),
        "by_language": count_by(rows, "language"),
        "managers_without_email": sorted(m for m, e in managers.items() if not e),
    }


def parse_time(value):
    s = str(value or "").strip()
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    for parse in (dt.datetime.fromisoformat,
                  lambda x: dt.datetime.strptime(x, "%d/%m/%Y %H:%M"),
                  lambda x: dt.datetime.strptime(x, "%d/%m/%Y")):
        try:
            return parse(s)
        except ValueError:
            continue
    return None


def score_response(resp, key, max_score):
    """Return a percentage, or None when the response cannot be scored."""
    answers = resp.get("answers")
    if isinstance(answers, dict) and key:
        lang_key = key
        if all(isinstance(v, dict) for v in key.values()):
            lang_key = {k.lower(): v for k, v in key.items()}.get(str(resp.get("language", "")).lower())
            if not lang_key:
                return None
        correct = 0
        for q, right in lang_key.items():
            given = answers.get(q)
            if isinstance(right, list) or isinstance(given, list):
                ok = set(right if isinstance(right, list) else [right]) == \
                    set(given if isinstance(given, list) else [given])
            else:
                ok = given is not None and str(given).strip().lower() == str(right).strip().lower()
            correct += ok
        return 100.0 * correct / len(lang_key)
    score = resp.get("score")
    if isinstance(score, bool) or score in (None, ""):
        return None
    try:
        value = float(score)
    except (TypeError, ValueError):
        return None
    if value < 0 or value > max_score:
        return None
    return 100.0 * value / max_score


def from_typeform(item):
    """Flatten one Typeform response item into {respondent, submitted_at, language, score, answers}."""
    hidden = item.get("hidden") or {}
    out = {"submitted_at": item.get("submitted_at", ""),
           "language": hidden.get("language", item.get("language", "")),
           "respondent": hidden.get("staff_id") or hidden.get("email") or ""}
    answers = {}
    for a in item.get("answers") or []:
        ref = (a.get("field") or {}).get("ref", "")
        if a.get("type") == "choice":
            choice = a.get("choice") or {}
            answers[ref] = choice.get("ref") or choice.get("label")
        elif a.get("type") == "choices":
            choices = a.get("choices") or {}
            answers[ref] = choices.get("refs") or choices.get("labels") or []
        elif ref in ("staff_id", "email", "respondent") and not out["respondent"]:
            out["respondent"] = a.get("text") or a.get("email") or ""
    out["answers"] = answers
    calc = item.get("calculated") or {}
    if "score" in calc:
        out["score"] = calc["score"]
    for v in item.get("variables") or []:
        if v.get("key") == "score" and "number" in v:
            out["score"] = v["number"]
    return out


def load_responses(paths):
    responses = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        items = data.get("items", []) if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise ValueError("%s has no list of responses" % path)
        for item in items:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("answers"), list) or "calculated" in item or "hidden" in item:
                item = from_typeform(item)
            responses.append(item)
    return responses


def update(rows, responses, pass_mark, max_score, key, deadline, today):
    index = {}
    for i, r in enumerate(rows):
        for k in person_keys(r):
            index.setdefault(k, i)
    attempts = {i: [] for i in range(len(rows))}
    unmatched, unscored = [], []
    for resp in responses:
        who = str(resp.get("respondent") or resp.get("email") or resp.get("staff_id")
                  or resp.get("id") or "").strip().lower()
        if who not in index:
            unmatched.append({"respondent": who, "submitted_at": resp.get("submitted_at", ""),
                              "note": "No one on the staff list has this email or ID; not added"})
            continue
        pct = score_response(resp, key, max_score)
        when = parse_time(resp.get("submitted_at"))
        if pct is None:
            unscored.append({"respondent": who, "submitted_at": resp.get("submitted_at", ""),
                             "note": "No usable score or answers; not counted"})
            continue
        attempts[index[who]].append((pct, when))

    out_rows = []
    for i, r in enumerate(rows):
        tries = attempts[i]
        passed = sorted((w for p, w in tries if p >= pass_mark and w), key=lambda w: w.replace(tzinfo=None))
        passed_any = any(p >= pass_mark for p, w in tries)
        status = "Passed" if passed_any else ("Failed (retake)" if tries else "Not started")
        last = max((w for p, w in tries if w), default=None, key=lambda w: w.replace(tzinfo=None))
        overdue = bool(deadline and today > deadline and not passed_any)
        out_rows.append({
            "Name": r["name"], "Email": r["email"], "Staff ID": r["id"], "Manager": r["manager"],
            "Manager email": r["manager_email"], "Shift": r["shift"], "Language": r["language"],
            "Status": status,
            "Best score %": round(max(p for p, w in tries), 1) if tries else "",
            "Attempts": len(tries),
            "Passed on": passed[0].date().isoformat() if passed else "",
            "Last attempt": last.date().isoformat() if last else "",
            "Overdue": "Yes" if overdue else "",
        })

    def group(field):
        groups = {}
        for row in out_rows:
            g = groups.setdefault(row[field] or "(not set)",
                                  {"staff": 0, "passed": 0, "failed": 0, "not_started": 0})
            g["staff"] += 1
            g[{"Passed": "passed", "Failed (retake)": "failed"}.get(row["Status"], "not_started")] += 1
        for g in groups.values():
            g["pct_passed"] = round(100.0 * g["passed"] / g["staff"], 1)
        return dict(sorted(groups.items()))

    total = len(out_rows)
    passed_n = sum(r["Status"] == "Passed" for r in out_rows)
    failed_n = sum(r["Status"] == "Failed (retake)" for r in out_rows)
    reminders = []
    for manager, members in sorted(_by_manager(out_rows).items()):
        incomplete = [{"name": m["Name"] or m["Email"] or m["Staff ID"], "status": m["Status"],
                       "best_score": m["Best score %"]} for m in members if m["Status"] != "Passed"]
        if incomplete:
            emails = sorted({m["Manager email"] for m in members if m["Manager email"]})
            reminders.append({"manager": manager, "manager_email": emails[0] if emails else "",
                              "incomplete": incomplete,
                              "deadline": deadline.isoformat() if deadline else "",
                              "days_left": (deadline - today).days if deadline else None})
    return {
        "pass_mark": pass_mark, "people": total, "passed": passed_n, "failed": failed_n,
        "not_started": total - passed_n - failed_n, "all_passed": total > 0 and passed_n == total,
        "rows": out_rows,
        "dashboard": {"by_manager": group("Manager"), "by_shift": group("Shift"),
                      "overall": {"staff": total, "passed": passed_n,
                                  "pct_passed": round(100.0 * passed_n / total, 1) if total else 0.0}},
        "reminders": reminders, "unmatched_responses": unmatched, "unscored_responses": unscored,
    }


def _by_manager(rows):
    out = {}
    for r in rows:
        out.setdefault(r["Manager"] or "(not set)", []).append(r)
    return out


def write_csvs(result, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    tracker = os.path.join(out_dir, "tracker.csv")
    with open(tracker, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=TRACKER_COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(result["rows"])
    dash = os.path.join(out_dir, "dashboard.csv")
    with open(dash, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Group", "Name", "Staff", "Passed", "Failed", "Not started", "% passed"])
        for label, key in (("Manager", "by_manager"), ("Shift", "by_shift")):
            for name, g in result["dashboard"][key].items():
                w.writerow([label, name, g["staff"], g["passed"], g["failed"], g["not_started"], g["pct_passed"]])
    return tracker, dash


def arg(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def fail(msg):
    print(json.dumps({"error": msg}))
    return 1


def main(argv):
    if not argv or argv[0] not in ("check", "update") or "--staff" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        rows = load_staff(arg(argv, "--staff"))
    except (OSError, ValueError, csv.Error) as exc:
        return fail("Could not read the staff list: %s" % exc)
    if not rows:
        return fail("The staff list is empty")
    if argv[0] == "check":
        langs = (arg(argv, "--languages", "") or "").split(",")
        print(json.dumps(check(rows, langs), ensure_ascii=False))
        return 0

    if not arg(argv, "--responses"):
        return fail("update needs --responses (the quiz responses file or files)")
    try:
        responses = load_responses([p for p in (arg(argv, "--responses") or "").split(",") if p])
        key = None
        if arg(argv, "--key"):
            with open(arg(argv, "--key"), encoding="utf-8") as fh:
                key = json.load(fh)
    except (OSError, TypeError, ValueError) as exc:
        return fail("Could not read the responses or answer key: %s" % exc)
    try:
        pass_mark = float(arg(argv, "--pass-mark", "80"))
        max_score = float(arg(argv, "--max-score", "10"))
        deadline = dt.date.fromisoformat(arg(argv, "--deadline")) if arg(argv, "--deadline") else None
        today = dt.date.fromisoformat(arg(argv, "--today")) if arg(argv, "--today") else dt.date.today()
    except ValueError as exc:
        return fail("Bad option value (dates are YYYY-MM-DD): %s" % exc)
    if not 0 < pass_mark <= 100 or max_score <= 0:
        return fail("--pass-mark must be 1-100 and --max-score above 0")
    result = update(rows, responses, pass_mark, max_score, key, deadline, today)
    result["warnings"] = []
    if not key and any(isinstance(r.get("answers"), dict) and r["answers"] for r in responses):
        result["warnings"].append("No answer key given: used the score the quiz reported. Pass --key "
                                  "so every answer is scored here (Typeform reports 0 when its form has no scoring).")
    if arg(argv, "--out-dir"):
        result["tracker_csv"], result["dashboard_csv"] = write_csvs(result, arg(argv, "--out-dir"))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
