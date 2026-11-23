#!/usr/bin/env python3
"""Forward/backward pass scheduler. Standard library only.

Usage: python3 -I schedule.py input.json [output.json]
Without output.json the result is printed to stdout.

Input JSON:
{
  "start_date": "YYYY-MM-DD" or null,      # day 1 = first working day on/after it
  "work_week": [0,1,2,3,4],                # weekday numbers, Monday=0 (default Mon-Fri)
  "holidays": ["YYYY-MM-DD", ...],         # optional non-working dates
  "deadline": "YYYY-MM-DD" or null,        # optional; checked against the end date
  "tasks": [{"id": "T1", "name": "...", "owner": "...", "duration": 3,
             "depends_on": ["T0"], "status": "Not started"}]
}
duration = working days (integer >= 0; 0 is a milestone). Dependencies are
finish-to-start: a task starts the working day after its last predecessor ends.
"""
import json
import sys
from datetime import date, timedelta


def parse_date(s, what, errors):
    try:
        return date.fromisoformat(str(s))
    except ValueError:
        errors.append("%s is not a valid YYYY-MM-DD date: %r" % (what, s))
        return None


def find_cycle(ids, preds):
    """Return one cycle as a list of ids, or None (iterative DFS)."""
    state = {i: 0 for i in ids}  # 0 new, 1 on stack, 2 done
    for root in ids:
        if state[root]:
            continue
        stack = [(root, iter(preds[root]))]
        path = [root]
        state[root] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
                path.pop()
            elif state[nxt] == 1:
                return path[path.index(nxt):] + [nxt]
            elif state[nxt] == 0:
                state[nxt] = 1
                stack.append((nxt, iter(preds[nxt])))
                path.append(nxt)
    return None


def schedule(data):
    errors, warnings = [], []
    tasks = data.get("tasks") or []
    work_week = sorted(set(data.get("work_week") or [0, 1, 2, 3, 4]))
    if not work_week or any((not isinstance(d, int)) or d < 0 or d > 6 for d in work_week):
        errors.append("work_week must be a list of weekday numbers 0-6 (Monday=0)")
        work_week = [0, 1, 2, 3, 4]
    holidays = set()
    for h in data.get("holidays") or []:
        d = parse_date(h, "holiday", errors)
        if d:
            holidays.add(d)
    start_date = None
    if data.get("start_date"):
        start_date = parse_date(data["start_date"], "start_date", errors)
    deadline = None
    if data.get("deadline"):
        deadline = parse_date(data["deadline"], "deadline", errors)

    # ---- validate tasks
    if not tasks:
        errors.append("no tasks given")
    ids, seen = [], set()
    for t in tasks:
        tid = str(t.get("id", "")).strip()
        if not tid:
            errors.append("a task has no id: %r" % t.get("name"))
            continue
        if tid in seen:
            errors.append("duplicate task id %s" % tid)
            continue
        seen.add(tid)
        ids.append(tid)
    byid = {str(t.get("id", "")).strip(): t for t in tasks}
    dur, preds = {}, {}
    for tid in ids:
        t = byid[tid]
        d = t.get("duration")
        if isinstance(d, bool) or not isinstance(d, int) or d < 0:
            errors.append("task %s: duration must be a whole number of working days (0 = milestone), got %r" % (tid, d))
            d = 1
        dur[tid] = d
        ps = [str(p).strip() for p in (t.get("depends_on") or [])]
        good = []
        for p in ps:
            if p == tid:
                errors.append("task %s depends on itself" % tid)
            elif p not in seen:
                errors.append("task %s depends on unknown task %s" % (tid, p))
            elif p not in good:
                good.append(p)
        preds[tid] = good
    if errors:
        return {"ok": False, "errors": errors, "warnings": warnings}
    cyc = find_cycle(ids, preds)
    if cyc:
        return {"ok": False, "errors": ["dependency cycle: " + " -> ".join(cyc)], "warnings": warnings}

    # ---- topological order (Kahn, keeps input order among equals)
    succs = {i: [] for i in ids}
    for i in ids:
        for p in preds[i]:
            succs[p].append(i)
    indeg = {i: len(preds[i]) for i in ids}
    order, ready = [], [i for i in ids if indeg[i] == 0]
    while ready:
        n = ready.pop(0)
        order.append(n)
        for s in succs[n]:
            indeg[s] -= 1
            if indeg[s] == 0:
                ready.append(s)

    # ---- forward pass (working-day numbers, 1-based; milestone: start = end)
    es, ef = {}, {}
    for n in order:
        after = max([ef[p] for p in preds[n]] or [0])
        if dur[n] == 0:
            es[n] = ef[n] = max(after, 1)
        else:
            es[n] = after + 1
            ef[n] = es[n] + dur[n] - 1
    project_days = max(ef.values())

    # ---- backward pass
    lf, ls = {}, {}
    for n in reversed(order):
        late = min([ls[s] - 1 if dur[s] > 0 else ls[s] for s in succs[n]] or [project_days])
        lf[n] = late
        ls[n] = late if dur[n] == 0 else late - dur[n] + 1
    slack = {n: ls[n] - es[n] for n in ids}
    critical = {n for n in ids if slack[n] == 0}

    # one critical chain, walked back from the last critical task
    tail = [n for n in ids if n in critical and ef[n] == project_days]
    chain = []
    cur = tail[0] if tail else None
    while cur:
        chain.append(cur)
        cp = [p for p in preds[cur] if p in critical and
              (ef[p] == es[cur] - 1 or (dur[cur] == 0 and ef[p] == es[cur]))]
        cur = cp[0] if cp else None
    chain.reverse()

    # ---- calendar
    wpw = len(work_week)
    day_dates = None
    if start_date:
        d = start_date
        if d.weekday() not in work_week or d in holidays:
            warnings.append("start_date %s is not a working day; day 1 is the next working day" % d.isoformat())
        day_dates = []
        while len(day_dates) < project_days:
            if d.weekday() in work_week and d not in holidays:
                day_dates.append(d)
            d += timedelta(days=1)
            if (d - start_date).days > 20000:
                errors.append("calendar never yields enough working days")
                return {"ok": False, "errors": errors, "warnings": warnings}

    def iso(day):
        return day_dates[day - 1].isoformat() if day_dates else None

    # ---- timeline columns
    daily = project_days <= 20
    columns = []
    if day_dates:
        if daily:
            for i, dd in enumerate(day_dates):
                columns.append({"label": dd.strftime("%d %b"), "from": dd.isoformat(), "to": dd.isoformat()})
            colof = lambda day: day
            unit = "day"
        else:
            monday0 = day_dates[0] - timedelta(days=day_dates[0].weekday())
            weeks = (day_dates[-1] - monday0).days // 7 + 1
            step = -(-weeks // 26)
            ncols = -(-weeks // step)
            for c in range(ncols):
                a = monday0 + timedelta(days=7 * step * c)
                b = a + timedelta(days=7 * step - 1)
                columns.append({"label": a.strftime("%d %b"), "from": a.isoformat(), "to": b.isoformat()})
            colof = lambda day: ((day_dates[day - 1] - monday0).days // 7) // step + 1
            unit = "week" if step == 1 else "%d weeks" % step
    else:
        if daily:
            columns = [{"label": "D%d" % i} for i in range(1, project_days + 1)]
            colof = lambda day: day
            unit = "day"
        else:
            weeks = -(-project_days // wpw)
            step = -(-weeks // 26)
            ncols = -(-weeks // step)
            for c in range(ncols):
                a = step * c + 1
                columns.append({"label": ("W%d" % a) if step == 1 else "W%d-%d" % (a, min(a + step - 1, weeks))})
            colof = lambda day: ((day - 1) // wpw) // step + 1
            unit = "week" if step == 1 else "%d weeks" % step

    out_tasks = []
    for n in ids:
        t = byid[n]
        out_tasks.append({
            "id": n, "name": t.get("name", ""), "owner": t.get("owner", ""),
            "status": t.get("status", ""), "duration": dur[n],
            "depends_on": preds[n],
            "start_day": es[n], "end_day": ef[n],
            "start": iso(es[n]), "end": iso(ef[n]),
            "start_week": (es[n] - 1) // wpw + 1, "end_week": (ef[n] - 1) // wpw + 1,
            "col_start": colof(es[n]), "col_end": colof(ef[n]),
            "slack_days": slack[n], "critical": n in critical,
            "milestone": dur[n] == 0,
        })

    end_date = iso(project_days)
    if deadline:
        if not day_dates:
            warnings.append("a deadline was given without a start_date; it was not checked")
        elif day_dates[-1] > deadline:
            late = sum(1 for d in day_dates if d > deadline)
            warnings.append("CONFLICT: the schedule ends %s, which is %d working day(s) after the deadline %s"
                            % (end_date, late, deadline.isoformat()))
    return {
        "ok": True, "errors": [], "warnings": warnings,
        "start_date": day_dates[0].isoformat() if day_dates else None,
        "end_date": end_date, "project_days": project_days,
        "project_weeks": -(-project_days // wpw),
        "critical_path": chain, "critical_ids": [n for n in ids if n in critical],
        "timeline": {"unit": unit, "columns": columns},
        "tasks": out_tasks,
    }


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        print(json.dumps({"ok": False, "errors": ["cannot read input: %s" % e], "warnings": []}))
        return 1
    result = schedule(data)
    text = json.dumps(result, indent=1, ensure_ascii=False)
    if len(argv) > 2:
        with open(argv[2], "w", encoding="utf-8") as f:
            f.write(text)
        print("ok=%s end_date=%s project_days=%s critical=%s warnings=%d errors=%d" % (
            result["ok"], result.get("end_date"), result.get("project_days"),
            "->".join(result.get("critical_path", [])), len(result["warnings"]), len(result["errors"])))
        for m in result["errors"] + result["warnings"]:
            print(m)
    else:
        print(text)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
