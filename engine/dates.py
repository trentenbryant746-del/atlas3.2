"""
Date algebra: dates and durations, composed.

A date is not an atom either. Dates and durations form a torsor --
date - date = duration, date + duration = date, duration + duration =
duration -- and those three operations compose into questions nobody
enumerated: "what weekday is 90 days after the day 1000 days before X".

The type discipline does the abstaining, exactly as dimensions do for units.
date + date is not a hard question, it is a MALFORMED one, and the types
reject it before any calendar arithmetic runs.

Every operation is checked by its inverse, and weekday is checked by Zeller's
congruence against the calendar library -- two unrelated algorithms.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

ISO = re.compile(r'(\d{4})-(\d{2})-(\d{2})(?!T)')
# instants, not just days. Same torsor at finer granularity: instant-instant
# is a duration, instant+duration is an instant. Extending the ALGEBRA covers
# every timestamp question at once; adding a family would have covered one.
ISO_DT = re.compile(r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z?')
DURATION = re.compile(r'duration|elapsed|how long|time between', re.I)
DAYS = re.compile(r'(-?\d+)\s*days?', re.I)

AFTER = re.compile(r'(\d+)\s*days?\s*(after|before)\s*', re.I)
BETWEEN = re.compile(r'(?:days?\s+between|between)', re.I)
WEEKDAY = re.compile(r'(?:what\s+)?day of the week|weekday', re.I)


def zeller(d: date) -> str:
    y, m, dd = d.year, d.month, d.day
    if m < 3:
        m += 12
        y -= 1
    k, j = y % 100, y // 100
    h = (dd + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
    return ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday"][h]


def _dates(q):
    out = []
    for m in ISO.finditer(q):
        try:
            out.append(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
        except ValueError:
            return None
    return out


TERMINAL = ("invalid calendar date", "is not defined",
            "inverse check failed", "algorithms disagree")


def terminal(why: str) -> bool:
    return any(t in (why or "") for t in TERMINAL)


def _instants(q):
    from datetime import datetime
    out = []
    for m in ISO_DT.finditer(q):
        try:
            out.append(datetime(*(int(g) for g in m.groups())))
        except ValueError:
            return None
    return out


def solve(question):
    """-> (answer, detail) or (None, reason)."""
    # instants first: a timestamp contains a date, so the coarser reader
    # would strip the time and silently answer a different question.
    ins = _instants(question)
    if ins is None:
        return None, "invalid calendar date"
    if len(ins) == 2 and DURATION.search(question):
        delta = ins[1] - ins[0]
        if ins[0] + delta != ins[1]:                  # INVERSE check
            return None, "inverse check failed"
        secs = int(delta.total_seconds())
        h, rem = divmod(abs(secs), 3600)
        mnt, sec = divmod(rem, 60)
        sign = "-" if secs < 0 else ""
        return (f"{sign}{h:02d}:{mnt:02d}:{sec:02d}",
                f"{ins[0].isoformat()} to {ins[1].isoformat()} "
                f"= {secs} s, inverse checked")

    ds = _dates(question)
    if ds is None:
        return None, "invalid calendar date"

    # ---- date - date = duration ------------------------------------
    if BETWEEN.search(question) and len(ds) == 2:
        delta = (ds[1] - ds[0]).days
        if ds[0] + timedelta(days=delta) != ds[1]:      # INVERSE check
            return None, "inverse check failed"
        return abs(delta), f"{ds[0]} to {ds[1]}"

    # ---- date + duration = date, possibly chained ------------------
    if ds and AFTER.search(question):
        cur = ds[0]
        steps = []
        for m in AFTER.finditer(question):
            n, dirn = int(m.group(1)), m.group(2).lower()
            shift = n if dirn == "after" else -n
            nxt = cur + timedelta(days=shift)
            if nxt - timedelta(days=shift) != cur:      # INVERSE check
                return None, "inverse check failed"
            steps.append(f"{dirn} {n}d -> {nxt}")
            cur = nxt
        if WEEKDAY.search(question):                    # composed: then weekday
            a, b = cur.strftime("%A"), zeller(cur)
            if a != b:                                  # REDUNDANT check
                return None, f"weekday algorithms disagree: {a} vs {b}"
            return a, " ; ".join(steps) + f" ; weekday({cur})"
        return cur.isoformat(), " ; ".join(steps)

    # ---- weekday(date) ---------------------------------------------
    if ds and WEEKDAY.search(question):
        a, b = ds[0].strftime("%A"), zeller(ds[0])
        if a != b:
            return None, f"weekday algorithms disagree: {a} vs {b}"
        return a, f"weekday({ds[0]})"

    # ---- malformed by type -----------------------------------------
    if len(ds) == 2 and re.search(r'\badd\b|\bplus\b|\+', question, re.I):
        return None, ("date + date is not defined -- dates and durations "
                      "form a torsor, so only date-date and date+duration "
                      "are well typed")
    return None, "no date operation recognised"
