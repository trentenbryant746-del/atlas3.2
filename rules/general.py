"""One rule per check kind, across domains, to show the form is not about maths."""
from __future__ import annotations

import ast
import re
from datetime import date, timedelta
from itertools import product

from rules.kinds import (Rule, INVERSE, IDENTITY, REDUNDANT, ENUMERATE,
                         EXTERNAL, NONE)

# ---------------------------------------------------------------- INVERSE
# temperature: derive F->C, check by converting back
def f_to_c(f):
    return round((int(f) - 32) * 5 / 9, 4)


def f_to_c_check(f):
    c = (int(f) - 32) * 5 / 9
    return round(((c * 9 / 5) + 32 - 32) * 5 / 9, 4)     # back and forth


# --------------------------------------------------------------- IDENTITY
# text reversal: reversing twice must return the input
def rev(s):
    return s[::-1]


def rev_check(s):
    out = s[::-1]
    return out if out[::-1] == s else "<identity failed>"


# -------------------------------------------------------------- REDUNDANT
# weekday from a date, two unrelated algorithms
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday"]


def weekday(y, m, d):
    return date(int(y), int(m), int(d)).strftime("%A")


def weekday_zeller(y, m, d):
    y, m, d = int(y), int(m), int(d)
    if m < 3:
        m += 12
        y -= 1
    k, j = y % 100, y // 100
    h = (d + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
    return ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday"][h]


# -------------------------------------------------------------- ENUMERATE
# syllogism validity, checked by exhausting a finite universe of models
def syllogism(a, b, c):
    """All A are B; all B are C -> all A are C. Derived by transitivity."""
    return "yes"


def syllogism_enumerate(a, b, c):
    """Exhaust every assignment over a 4-element universe; look for a
    counterexample to 'all A are C' given the premises."""
    for n in range(1, 5):
        for A, B, C in product([tuple(p) for p in product([0, 1], repeat=n)],
                               repeat=3):
            prem1 = all((not A[i]) or B[i] for i in range(n))
            prem2 = all((not B[i]) or C[i] for i in range(n))
            concl = all((not A[i]) or C[i] for i in range(n))
            if prem1 and prem2 and not concl:
                return "no"          # counterexample exists
    return "yes"


# --------------------------------------------------------------- EXTERNAL
# syntactic validity of a Python snippet, adjudicated by the real parser
def py_valid(src):
    try:
        ast.parse(src)
        return "valid"
    except SyntaxError:
        return "invalid"


def py_valid_check(src):
    try:
        compile(src, "<check>", "exec")     # a different entry point
        return "valid"
    except SyntaxError:
        return "invalid"


# ------------------------------------------------------------------- NONE
# an asserted fact. No derivation exists; it can only be attributed.
def earth_radius(_):
    return "6371 km"


RULES = [
    Rule("f_to_c", "unit.temperature",
         re.compile(r'(-?\d+)\s*(?:degrees\s*)?(?:F|fahrenheit)\b', re.I),
         f_to_c, f_to_c_check, INVERSE),
    Rule("reverse", "text.transform",
         re.compile(r'reverse the (?:string|text|word)\s+"([^"]+)"', re.I),
         rev, rev_check, IDENTITY),
    Rule("weekday", "date.calendar",
         re.compile(r'what day of the week (?:is|was)\s+(\d{4})-(\d{2})-(\d{2})',
                    re.I),
         weekday, weekday_zeller, REDUNDANT),
    Rule("syllogism", "logic.categorical",
         re.compile(r'all (\w+) are (\w+)[.,;]\s*all \2 are (\w+)[.,;]?\s*'
                    r'(?:are all \1 \3)', re.I),
         syllogism, syllogism_enumerate, ENUMERATE),
    Rule("py_syntax", "code.python",
         re.compile(r'is this valid python:\s*(.+)$', re.I | re.S),
         py_valid, py_valid_check, EXTERNAL),
    Rule("earth_radius", "fact.earth",
         re.compile(r"(earth)'?s? (?:mean )?radius", re.I),
         earth_radius, None, NONE,
         source="IAU/IUGG mean radius, quoted in belt-atlas data/net.tsv",
         derivable=False),
]
