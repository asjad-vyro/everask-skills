#!/usr/bin/env python3
"""Rota solver. Usage: python3 solve_rota.py problem.json [--out rota.xlsx]

Reads a JSON problem, assigns people to shift slots so every hard rule holds,
balances fairness, re-checks the result from scratch, optionally writes an
.xlsx (rota grid, hours and counts, rule check) and prints one JSON result.
Standard library plus openpyxl (only for --out). Never invents anything: a rule
or limit that is not in the problem is not applied.
"""
import json
import random
import sys
import time

ARGS = sys.argv[1:]


def fail(msg):
    print(json.dumps({"status": "error", "error": msg}, ensure_ascii=False))
    sys.exit(2)


# ---------------------------------------------------------------- load
def hm(s):
    h, m = str(s).split(":")
    return int(h) * 60 + int(m)


class Problem:
    def __init__(self, d):
        self.d = d
        self.days = [str(x) for x in d.get("days", [])]
        if not self.days:
            fail("'days' is empty")
        self.wl = int(d.get("week_length", 7))
        self.shifts = d.get("shifts", [])
        if not self.shifts:
            fail("'shifts' is empty")
        self.sname = [s["name"] for s in self.shifts]
        if len(set(self.sname)) != len(self.sname):
            fail("duplicate shift names")
        self.start, self.dur, self.night = [], [], []
        for s in self.shifts:
            if "start" in s and "end" in s:
                a, b = hm(s["start"]), hm(s["end"])
                dur = (b - a) % 1440 or 1440
            elif "hours" in s:
                a, dur = hm(s.get("start", "00:00")), int(round(float(s["hours"]) * 60))
            else:
                fail("shift %r needs start+end or hours" % s["name"])
            if "hours" in s:
                dur = int(round(float(s["hours"]) * 60))
            self.start.append(a)
            self.dur.append(dur)
            self.night.append(bool(s.get("night", False)))
        self.people = d.get("people", [])
        if not self.people:
            fail("'people' is empty")
        self.pname = [p["name"] for p in self.people]
        if len(set(self.pname)) != len(self.pname):
            fail("duplicate person names")
        self.rules = d.get("rules", {})
        self.labels = d.get("labels", {})
        self.weekend = d.get("weekend_days", [])
        self.nd = len(self.days)
        # units
        self.units = []  # (day, shift_idx, role)
        for row in d.get("demand", []):
            if row["shift"] not in self.sname:
                fail("demand names unknown shift %r" % row["shift"])
            si = self.sname.index(row["shift"])
            for di in range(self.nd):
                if self.match(row.get("day", "*"), di):
                    for _ in range(int(row.get("count", 1))):
                        self.units.append((di, si, row.get("role")))
        if not self.units:
            fail("'demand' produces no slots")
        self.unavail_day = []
        self.unavail_slot = []
        for p in self.people:
            ud = set()
            us = set()
            for spec in p.get("unavailable_days", []):
                for di in range(self.nd):
                    if self.match(spec, di):
                        ud.add(di)
            for it in p.get("unavailable", []):
                for di in range(self.nd):
                    if self.match(it.get("day", "*"), di):
                        if "shift" in it and it["shift"] in self.sname:
                            us.add((di, self.sname.index(it["shift"])))
                        elif "shift" not in it:
                            ud.add(di)
            self.unavail_day.append(ud)
            self.unavail_slot.append(us)
        self.forbidden = []
        for a, b in self.rules.get("forbidden_next_day", []):
            if a in self.sname and b in self.sname:
                self.forbidden.append((self.sname.index(a), self.sname.index(b)))
            else:
                fail("forbidden_next_day names unknown shift: %r" % [a, b])

    def match(self, spec, di):
        if spec == "*":
            return True
        if isinstance(spec, list):
            return any(self.match(x, di) for x in spec)
        if spec == "weekend":
            return self.is_weekend(di)
        if spec == "weekday":
            return not self.is_weekend(di)
        if isinstance(spec, int):
            return spec == di
        return self.days[di] == str(spec)

    def is_weekend(self, di):
        return any(self.match(w, di) for w in self.weekend)

    def week(self, di):
        return di // self.wl

    # effective limits (None = not set)
    def lim(self, pi, key):
        v = self.people[pi].get(key)
        return v if v is not None else self.rules.get(key)

    def can_do_role(self, pi, role):
        if not role:
            return True
        p = self.people[pi]
        return p.get("role") == role or role in p.get("skills", [])

    def abs_start(self, di, si):
        return di * 1440 + self.start[si]

    def abs_end(self, di, si):
        return di * 1440 + self.start[si] + self.dur[si]


# ---------------------------------------------------------------- state
class State:
    def __init__(self, P):
        self.P = P
        self.pd = [dict() for _ in P.people]  # day -> shift idx
        self.owner = {}  # unit index -> person idx
        self.hours = [0.0] * len(P.people)
        self.wk = [0] * len(P.people)
        self.nt = [0] * len(P.people)

    def reason(self, pi, di, si, role=None, skip_static=False):
        """None if person pi may take shift si on day di, else why not."""
        P = self.P
        if not P.can_do_role(pi, role):
            return "role"
        if di in P.unavail_day[pi] or (di, si) in P.unavail_slot[pi]:
            return "unavailable"
        pd = self.pd[pi]
        if di in pd:
            return "already on shift that day"
        # week caps
        w = P.week(di)
        wdays = [d for d in pd if P.week(d) == w]
        ms = P.lim(pi, "max_shifts_per_week")
        if ms is not None and len(wdays) + 1 > ms:
            return "max shifts per week"
        mh = P.lim(pi, "max_hours_per_week")
        if mh is not None:
            h = sum(P.dur[pd[d]] for d in wdays) / 60.0 + P.dur[si] / 60.0
            if h > mh + 1e-9:
                return "max hours per week"
        if P.night[si]:
            mn = P.lim(pi, "max_night_shifts_per_week")
            if mn is not None and sum(1 for d in wdays if P.night[pd[d]]) + 1 > mn:
                return "max night shifts per week"
        if P.is_weekend(di):
            mw = P.lim(pi, "max_weekend_shifts")
            if mw is not None and sum(1 for d in pd if P.is_weekend(d)) + 1 > mw:
                return "max weekend shifts"
        mc = P.lim(pi, "max_consecutive_days")
        if mc is not None:
            run = 1
            d = di - 1
            while d in pd:
                run += 1
                d -= 1
            d = di + 1
            while d in pd:
                run += 1
                d += 1
            if run > mc:
                return "max consecutive days"
        rest = P.rules.get("min_rest_hours")
        for dd in (di - 1, di + 1):
            if dd in pd:
                if dd < di:
                    ps, ns = pd[dd], si
                    pdd, ndd = dd, di
                else:
                    ps, ns = si, pd[dd]
                    pdd, ndd = di, dd
                if (ps, ns) in P.forbidden:
                    return "forbidden shift sequence"
                if rest is not None:
                    gap = (P.abs_start(ndd, ns) - P.abs_end(pdd, ps)) / 60.0
                    if gap < rest - 1e-9:
                        return "min rest between shifts"
        return None

    def add(self, ui, pi):
        di, si, _ = self.P.units[ui]
        self.pd[pi][di] = si
        self.owner[ui] = pi
        self.hours[pi] += self.P.dur[si] / 60.0
        self.wk[pi] += 1 if self.P.is_weekend(di) else 0
        self.nt[pi] += 1 if self.P.night[si] else 0

    def remove(self, ui):
        pi = self.owner.pop(ui)
        di, si, _ = self.P.units[ui]
        del self.pd[pi][di]
        self.hours[pi] -= self.P.dur[si] / 60.0
        self.wk[pi] -= 1 if self.P.is_weekend(di) else 0
        self.nt[pi] -= 1 if self.P.night[si] else 0
        return pi

    def copy_owner(self):
        return dict(self.owner)


def fte(P, pi):
    return float(P.people[pi].get("fte", 1) or 1)


def spreads(P, st):
    n = len(P.people)
    lo = [st.hours[i] / fte(P, i) for i in range(n)]
    can_wk = [i for i in range(n) if any(P.is_weekend(d) and d not in P.unavail_day[i] for d in range(P.nd))] or list(range(n))
    wk = [st.wk[i] / fte(P, i) for i in can_wk]
    nt = [st.nt[i] / fte(P, i) for i in range(n)]
    return max(lo) - min(lo), max(wk) - min(wk), max(nt) - min(nt)


def objective(P, st):
    h, w, n = spreads(P, st)
    return h * 1000 + w * 30 + n * 10


# ---------------------------------------------------------------- solve
def solve(P, seed, tlimit):
    rng = random.Random(seed)
    t0 = time.time()
    U = len(P.units)
    st = State(P)
    best = {"n": -1, "owner": {}}
    nodes = [0]
    timed_out = [False]
    jitter = [rng.random() * 0.01 for _ in P.people]

    def cands(ui):
        di, si, role = P.units[ui]
        out = []
        for pi in range(len(P.people)):
            if st.reason(pi, di, si, role) is None:
                out.append(pi)
        return out

    def score(pi, ui):
        di, si, _ = P.units[ui]
        s = (st.hours[pi] + P.dur[si] / 60.0) / fte(P, pi)
        if P.is_weekend(di):
            s += (st.wk[pi] + 1) / fte(P, pi) * 3
        if P.night[si]:
            s += (st.nt[pi] + 1) / fte(P, pi) * 2
        return s + jitter[pi]

    def dfs():
        if time.time() - t0 > tlimit:
            return False
        nodes[0] += 1
        if len(st.owner) > best["n"]:
            best["n"] = len(st.owner)
            best["owner"] = st.copy_owner()
        if len(st.owner) == U:
            return True
        # most constrained unfilled unit
        pick, pc = None, None
        for ui in range(U):
            if ui in st.owner:
                continue
            c = cands(ui)
            if not c:
                return False
            if pc is None or len(c) < len(pc):
                pick, pc = ui, c
                if len(c) == 1:
                    break
        pc.sort(key=lambda pi: score(pi, pick))
        for pi in pc:
            st.add(pick, pi)
            if dfs():
                return True
            st.remove(pick)
            if time.time() - t0 > tlimit:
                return False
        return False

    sys.setrecursionlimit(10000)
    ok = dfs()
    timed_out[0] = time.time() - t0 > tlimit
    if not ok:
        # rebuild best partial then greedily fill what is still possible
        st = State(P)
        for ui, pi in best["owner"].items():
            st.add(ui, pi)
        for ui in sorted(range(U), key=lambda u: len(cands(u)) if u not in st.owner else 99):
            if ui in st.owner:
                continue
            c = cands(ui)
            if c:
                c.sort(key=lambda pi: score(pi, ui))
                st.add(ui, c[0])
    improve(P, st, rng, min(8.0, max(1.0, tlimit / 3)))
    return st, ok, nodes[0], timed_out[0]


def improve(P, st, rng, tlimit):
    """Local search: move or swap assignments to shrink the fairness spread."""
    t0 = time.time()
    cur = objective(P, st)
    n = len(P.people)
    stale = 0
    while time.time() - t0 < tlimit and stale < 4000 and cur > 0:
        stale += 1
        ui = rng.choice(list(st.owner.keys()))
        a = st.owner[ui]
        di, si, role = P.units[ui]
        b = rng.randrange(n)
        if b == a:
            continue
        # move
        st.remove(ui)
        if st.reason(b, di, si, role) is None:
            st.add(ui, b)
            new = objective(P, st)
            if new < cur - 1e-9:
                cur = new
                stale = 0
                continue
            st.remove(ui)
        st.add(ui, a)
        # swap with one of b's units
        bu = [u for u, p in st.owner.items() if p == b]
        if not bu:
            continue
        vj = rng.choice(bu)
        dj, sj, rj = P.units[vj]
        st.remove(ui)
        st.remove(vj)
        if (st.reason(b, di, si, role) is None) and (st.reason(a, dj, sj, rj) is None):
            st.add(ui, b)
            if st.reason(a, dj, sj, rj) is None:
                st.add(vj, a)
                new = objective(P, st)
                if new < cur - 1e-9:
                    cur = new
                    stale = 0
                    continue
                st.remove(ui)
                st.remove(vj)
            else:
                st.remove(ui)
        st.add(ui, a)
        st.add(vj, b)


# ---------------------------------------------------------------- independent check
def check_all(P, owner):
    """Recompute every rule from the finished assignment. Returns rule report."""
    n = len(P.people)
    per = [dict() for _ in range(n)]  # day -> list of shifts
    for ui, pi in owner.items():
        di, si, _ = P.units[ui]
        per[pi].setdefault(di, []).append(si)
    rep = []

    def add(rule, kind, bad, ok_detail):
        if kind == "soft":
            status = "WARN" if bad else "PASS"
        else:
            status = "FAIL" if bad else "PASS"
        rep.append({"rule": rule, "type": kind, "status": status,
                    "details": "; ".join(bad) if bad else ok_detail})

    # coverage
    need = {}
    for di, si, role in P.units:
        need[(di, si, role)] = need.get((di, si, role), 0) + 1
    got = {}
    for ui, pi in owner.items():
        k = P.units[ui]
        got[k] = got.get(k, 0) + 1
    bad = []
    for k, v in need.items():
        if got.get(k, 0) < v:
            bad.append("%s %s%s: %d of %d filled" % (P.days[k[0]], P.sname[k[1]],
                       (" (" + k[2] + ")") if k[2] else "", got.get(k, 0), v))
    add("Every slot has the required number of people", "hard", bad,
        "all %d positions filled" % len(P.units))
    # one shift per day
    bad = ["%s on %s has %d shifts" % (P.pname[i], P.days[d], len(s))
           for i in range(n) for d, s in per[i].items() if len(s) > 1]
    add("At most one shift per person per day", "hard", bad, "holds for everyone")
    # availability and role
    bad = []
    for ui, pi in owner.items():
        di, si, role = P.units[ui]
        if di in P.unavail_day[pi] or (di, si) in P.unavail_slot[pi]:
            bad.append("%s on %s %s" % (P.pname[pi], P.days[di], P.sname[si]))
    add("Nobody is placed when unavailable", "hard", bad, "all stated unavailability respected")
    bad = []
    for ui, pi in owner.items():
        di, si, role = P.units[ui]
        if not P.can_do_role(pi, role):
            bad.append("%s on %s %s lacks %s" % (P.pname[pi], P.days[di], P.sname[si], role))
    if any(r for _, _, r in P.units):
        add("Role or skill required by a slot is met", "hard", bad, "holds for every slot")
    # weekly limits
    for key, label, fn in (
        ("max_shifts_per_week", "Maximum shifts per week", lambda i, ds: len(ds)),
        ("max_hours_per_week", "Maximum hours per week",
         lambda i, ds: sum(P.dur[s] for d in ds for s in per[i][d]) / 60.0),
        ("max_night_shifts_per_week", "Maximum night shifts per week",
         lambda i, ds: sum(1 for d in ds for s in per[i][d] if P.night[s])),
    ):
        if not any(P.lim(i, key) is not None for i in range(n)):
            continue
        bad = []
        for i in range(n):
            cap = P.lim(i, key)
            if cap is None:
                continue
            weeks = {}
            for d in per[i]:
                weeks.setdefault(P.week(d), []).append(d)
            for w, ds in weeks.items():
                v = fn(i, ds)
                if v > cap + 1e-9:
                    bad.append("%s week %d: %g > %g" % (P.pname[i], w + 1, v, cap))
        add(label, "hard", bad, "nobody over their limit")
    if any(P.lim(i, "max_weekend_shifts") is not None for i in range(n)):
        bad = []
        for i in range(n):
            cap = P.lim(i, "max_weekend_shifts")
            v = sum(1 for d in per[i] if P.is_weekend(d))
            if cap is not None and v > cap:
                bad.append("%s: %d > %d" % (P.pname[i], v, cap))
        add("Maximum weekend shifts", "hard", bad, "nobody over their limit")
    if any(P.lim(i, "max_consecutive_days") is not None for i in range(n)):
        bad = []
        for i in range(n):
            cap = P.lim(i, "max_consecutive_days")
            if cap is None:
                continue
            run = 0
            for d in range(P.nd):
                run = run + 1 if d in per[i] else 0
                if run > cap:
                    bad.append("%s works %d days in a row ending %s" % (P.pname[i], run, P.days[d]))
                    break
        add("Maximum consecutive working days", "hard", bad, "nobody over their limit")
    rest = P.rules.get("min_rest_hours")
    if rest is not None or P.forbidden:
        bad = []
        for i in range(n):
            for d in range(P.nd - 1):
                if d in per[i] and d + 1 in per[i]:
                    a, b = per[i][d][0], per[i][d + 1][0]
                    if (a, b) in P.forbidden:
                        bad.append("%s: %s then %s (%s to %s)" % (P.pname[i], P.sname[a], P.sname[b], P.days[d], P.days[d + 1]))
                    elif rest is not None:
                        gap = (P.abs_start(d + 1, b) - P.abs_end(d, a)) / 60.0
                        if gap < rest - 1e-9:
                            bad.append("%s: only %g h between %s %s and %s %s" % (
                                P.pname[i], gap, P.days[d], P.sname[a], P.days[d + 1], P.sname[b]))
        what = []
        if rest is not None:
            what.append("at least %g h rest between shifts" % rest)
        if P.forbidden:
            what.append("no " + ", ".join("%s then %s" % (P.sname[a], P.sname[b]) for a, b in P.forbidden) + " next day")
        add("Rest between shifts (" + "; ".join(what) + ")", "hard", bad, "holds for everyone")
    # soft: minimum shifts per week
    if any(P.lim(i, "min_shifts_per_week") is not None for i in range(n)):
        bad = []
        for i in range(n):
            cap = P.lim(i, "min_shifts_per_week")
            if cap is None:
                continue
            for w in range((P.nd + P.wl - 1) // P.wl):
                v = sum(1 for d in per[i] if P.week(d) == w)
                if v < cap:
                    bad.append("%s week %d: %d < %g" % (P.pname[i], w + 1, v, cap))
        add("Minimum shifts per week (target)", "soft", bad, "everyone reaches their minimum")
    return rep


def person_table(P, owner):
    n = len(P.people)
    rows = []
    for i in range(n):
        shifts = [P.units[u] for u, p in owner.items() if p == i]
        by = {nm: 0 for nm in P.sname}
        for di, si, _ in shifts:
            by[P.sname[si]] += 1
        rows.append({
            "person": P.pname[i], "role": P.people[i].get("role", ""),
            "shifts": len(shifts),
            "hours": round(sum(P.dur[si] for _, si, _ in shifts) / 60.0, 2),
            "weekend_shifts": sum(1 for di, _, _ in shifts if P.is_weekend(di)),
            "night_shifts": sum(1 for _, si, _ in shifts if P.night[si]),
            "by_shift": by, "fte": fte(P, i),
        })
    return rows


def diagnose(P, st):
    """For each unfilled position say how many people are blocked and why."""
    out = []
    seen = set()
    for ui, (di, si, role) in enumerate(P.units):
        if ui in st.owner or (di, si, role) in seen:
            continue
        seen.add((di, si, role))
        reasons = {}
        for pi in range(len(P.people)):
            r = st.reason(pi, di, si, role)
            if r:
                reasons.setdefault(r, []).append(P.pname[pi])
        out.append({
            "day": P.days[di], "shift": P.sname[si], "role": role,
            "missing": sum(1 for u, (a, b, c) in enumerate(P.units)
                           if (a, b, c) == (di, si, role) and u not in st.owner),
            "blocked_by": {k: v for k, v in reasons.items()},
        })
    return out


def capacity_note(P):
    caps = []
    for i in range(len(P.people)):
        ms = P.lim(i, "max_shifts_per_week")
        caps.append(ms if ms is not None else P.wl)
    weeks = (P.nd + P.wl - 1) // P.wl
    return {"positions_to_fill": len(P.units), "most_shifts_the_people_can_work_under_weekly_caps": int(sum(caps) * weeks)}


# ---------------------------------------------------------------- xlsx
PALETTE = ["BDD7EE", "FFE699", "C6E0B4", "F8CBAD", "D9C3E8", "B7DEE8", "FFD9E6", "E2EFDA"]


def write_xlsx(P, owner, rep, table, path, unfilled):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
    from openpyxl.utils import get_column_letter
    L = P.labels
    t = lambda k, dflt: L.get(k, dflt)
    wb = Workbook()
    ws = wb.active
    ws.title = t("sheet_rota", "Rota")[:31]
    thin = Side(style="thin", color="BBBBBB")
    box = Border(left=thin, right=thin, top=thin, bottom=thin)
    bold = Font(bold=True)
    head = PatternFill("solid", fgColor="DDDDDD")
    fills = {nm: PatternFill("solid", fgColor=PALETTE[i % len(PALETTE)]) for i, nm in enumerate(P.sname)}
    cell_of = {}  # (pi, di) -> text
    for ui, pi in owner.items():
        di, si, role = P.units[ui]
        cell_of[(pi, di)] = P.sname[si]
    people_down = P.d.get("layout", "people_down") != "days_down"
    title = P.d.get("title")
    r0 = 1
    if title:
        ws.cell(1, 1, title).font = Font(bold=True, size=14)
        r0 = 3
    name_h = t("person", "Person")
    if people_down:
        ws.cell(r0, 1, name_h)
        for d in range(P.nd):
            ws.cell(r0, 2 + d, P.days[d])
        for i in range(len(P.people)):
            ws.cell(r0 + 1 + i, 1, P.pname[i])
            for d in range(P.nd):
                v = cell_of.get((i, d), "")
                c = ws.cell(r0 + 1 + i, 2 + d, v)
                if v:
                    c.fill = fills[v]
        # coverage row
        cr = r0 + 1 + len(P.people)
        ws.cell(cr, 1, t("staffed", "People on duty"))
        for d in range(P.nd):
            ws.cell(cr, 2 + d, sum(1 for i in range(len(P.people)) if (i, d) in cell_of))
        last_r, last_c = cr, 1 + P.nd
    else:
        ws.cell(r0, 1, t("day", "Day"))
        for i in range(len(P.people)):
            ws.cell(r0, 2 + i, P.pname[i])
        for d in range(P.nd):
            ws.cell(r0 + 1 + d, 1, P.days[d])
            for i in range(len(P.people)):
                v = cell_of.get((i, d), "")
                c = ws.cell(r0 + 1 + d, 2 + i, v)
                if v:
                    c.fill = fills[v]
        last_r, last_c = r0 + P.nd, 1 + len(P.people)
    for r in range(r0, last_r + 1):
        for c in range(1, last_c + 1):
            x = ws.cell(r, c)
            x.border = box
            x.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            if r == r0 or c == 1:
                x.font = bold
                x.fill = head
    ws.column_dimensions["A"].width = 22
    for c in range(2, last_c + 1):
        ws.column_dimensions[get_column_letter(c)].width = 13
    ws.freeze_panes = ws.cell(r0 + 1, 2)
    # legend
    lr = last_r + 2
    ws.cell(lr, 1, t("legend", "Shifts")).font = bold
    for i, nm in enumerate(P.sname):
        s = P.shifts[i]
        txt = nm
        if "start" in s and "end" in s:
            txt += "  %s-%s" % (s["start"], s["end"])
        c = ws.cell(lr + 1 + i, 1, txt)
        c.fill = fills[nm]
    # sheet 2
    w2 = wb.create_sheet(t("sheet_hours", "Hours and counts")[:31])
    heads = [name_h, t("role", "Role"), t("shifts", "Shifts"), t("hours", "Hours"),
             t("weekend", "Weekend shifts"), t("nights", "Night shifts")] + P.sname
    for j, h in enumerate(heads):
        c = w2.cell(1, 1 + j, h)
        c.font = bold
        c.fill = head
    for i, r in enumerate(table):
        vals = [r["person"], r["role"], r["shifts"], r["hours"], r["weekend_shifts"], r["night_shifts"]] + \
               [r["by_shift"][nm] for nm in P.sname]
        for j, v in enumerate(vals):
            w2.cell(2 + i, 1 + j, v)
    tr = 2 + len(table)
    w2.cell(tr, 1, t("total", "Total")).font = bold
    for j in range(3, len(heads) + 1):
        w2.cell(tr, j, round(sum(w2.cell(r, j).value for r in range(2, tr)), 2)).font = bold
    w2.column_dimensions["A"].width = 22
    # sheet 3
    w3 = wb.create_sheet(t("sheet_rules", "Rule check")[:31])
    for j, h in enumerate([t("rule", "Rule"), t("type", "Type"), t("status", "Result"), t("details", "Details")]):
        c = w3.cell(1, 1 + j, h)
        c.font = bold
        c.fill = head
    colour = {"PASS": "C6EFCE", "FAIL": "FFC7CE", "WARN": "FFEB9C"}
    for i, r in enumerate(rep):
        rt = L.get("rule_text") or {}
        rule_txt = r["rule"]
        for en, tr in rt.items():
            rule_txt = rule_txt.replace(en, tr)
        det = L.get("ok_text") if (r["status"] == "PASS" and L.get("ok_text")) else r["details"]
        w3.cell(2 + i, 1, rule_txt)
        w3.cell(2 + i, 2, L.get("type_" + r["type"], r["type"]))
        c = w3.cell(2 + i, 3, r["status"])
        c.fill = PatternFill("solid", fgColor=colour[r["status"]])
        w3.cell(2 + i, 4, det).alignment = Alignment(wrap_text=True, vertical="top")
        w3.cell(2 + i, 1).alignment = Alignment(wrap_text=True, vertical="top")
    w3.column_dimensions["A"].width = 48
    w3.column_dimensions["B"].width = 8
    w3.column_dimensions["C"].width = 9
    w3.column_dimensions["D"].width = 80
    if P.d.get("rtl") or L.get("rtl"):
        for w in wb.worksheets:
            w.sheet_view.rightToLeft = True
    wb.save(path)


# ---------------------------------------------------------------- main
def main():
    if not ARGS or ARGS[0].startswith("-"):
        fail("usage: solve_rota.py problem.json [--out rota.xlsx]")
    try:
        d = json.load(open(ARGS[0], encoding="utf-8"))
    except Exception as e:
        fail("cannot read problem file: %s" % e)
    out = ARGS[ARGS.index("--out") + 1] if "--out" in ARGS else None
    P = Problem(d)
    tl = float(d.get("time_limit", 20))
    cn = capacity_note(P)
    short = cn["positions_to_fill"] > cn["most_shifts_the_people_can_work_under_weekly_caps"]
    if short:
        tl = 3.0
    best = None
    for k in range(3):
        st, ok, nodes, tout = solve(P, int(d.get("seed", 1)) + k, tl / (1 + k))
        score = (len(st.owner), -objective(P, st))
        if best is None or score > best[0]:
            best = (score, st, ok, nodes, tout)
        if len(st.owner) == len(P.units) and k >= 1:
            break
    _, st, ok, nodes, tout = best
    if short:
        tout = False
    owner = dict(st.owner)
    rep = check_all(P, owner)
    table = person_table(P, owner)
    full = len(owner) == len(P.units)
    hard_fail = [r for r in rep if r["status"] == "FAIL"]
    unfilled = [] if full else diagnose(P, st)
    h, w, n = spreads(P, st)
    res = {
        "status": "complete" if (full and not hard_fail) else "partial",
        "positions_total": len(P.units), "positions_filled": len(owner),
        "assignments": sorted(
            [{"person": P.pname[pi], "day": P.days[P.units[u][0]], "shift": P.sname[P.units[u][1]],
              "role": P.units[u][2]} for u, pi in owner.items()],
            key=lambda a: (P.days.index(a["day"]), P.sname.index(a["shift"]), a["person"])),
        "per_person": table,
        "rule_report": rep,
        "unfilled": unfilled,
        "fairness": {"hours_per_fte_spread": round(h, 2), "weekend_shifts_per_fte_spread": round(w, 2),
                     "night_shifts_per_fte_spread": round(n, 2)},
        "search": {"found_full_rota": ok, "proved_impossible": (not ok and not tout), "ran_out_of_time": tout, "nodes": nodes},
    }
    if not full:
        res["capacity"] = capacity_note(P)
    if out:
        try:
            write_xlsx(P, owner, rep, table, out, unfilled)
            res["xlsx"] = out
        except ImportError:
            res["xlsx_error"] = "openpyxl is not installed"
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
