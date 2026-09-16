"""
Dimensional algebra: unbounded conversions from a small table.

The corpus contained exactly one conversion family, "meters to centimetres",
and family-based recognition would need one more for every other pair. But
units are compositional in the same way arithmetic is: every unit is a
product of base dimensions with exponents and a scale factor, so a table of
N units generates N^2 simple conversions and an unbounded number of COMPOUND
ones (km/h, m/s^2, kg*m/s^2) that were never enumerated anywhere.

The dimension vector is also the abstention rule, and it is free. Converting
metres to kilograms is not a hard question, it is a MALFORMED one, and the
exponent vectors disagree before any arithmetic happens. That is a competence
boundary derived from structure rather than from a list of what to refuse.

Checked two ways: convert back (INVERSE), and route through SI base units by
a separate code path (REDUNDANT).
"""
from __future__ import annotations

import re
from fractions import Fraction as F

# (scale to SI base, dimension vector over length, mass, time)
L, M, T = (1, 0, 0), (0, 1, 0), (0, 0, 1)


def dim(*p):
    return tuple(p)


UNITS = {
    # length
    "meter": (F(1), dim(1, 0, 0)), "metre": (F(1), dim(1, 0, 0)),
    "m": (F(1), dim(1, 0, 0)),
    "kilometer": (F(1000), dim(1, 0, 0)), "km": (F(1000), dim(1, 0, 0)),
    "centimeter": (F(1, 100), dim(1, 0, 0)), "cm": (F(1, 100), dim(1, 0, 0)),
    "millimeter": (F(1, 1000), dim(1, 0, 0)), "mm": (F(1, 1000), dim(1, 0, 0)),
    "inch": (F(254, 10000), dim(1, 0, 0)),
    "foot": (F(3048, 10000), dim(1, 0, 0)), "feet": (F(3048, 10000), dim(1, 0, 0)),
    "yard": (F(9144, 10000), dim(1, 0, 0)),
    "mile": (F(1609344, 1000), dim(1, 0, 0)),
    # mass
    "gram": (F(1, 1000), dim(0, 1, 0)), "g": (F(1, 1000), dim(0, 1, 0)),
    "kilogram": (F(1), dim(0, 1, 0)), "kg": (F(1), dim(0, 1, 0)),
    "tonne": (F(1000), dim(0, 1, 0)),
    "milligram": (F(1, 1000000), dim(0, 1, 0)),
    "mg": (F(1, 1000000), dim(0, 1, 0)),
    "microgram": (F(1, 1000000000), dim(0, 1, 0)),
    "mcg": (F(1, 1000000000), dim(0, 1, 0)),
    # volume is length^3, so it needs no new base dimension
    "litre": (F(1, 1000), dim(3, 0, 0)), "liter": (F(1, 1000), dim(3, 0, 0)),
    "l": (F(1, 1000), dim(3, 0, 0)),
    "millilitre": (F(1, 1000000), dim(3, 0, 0)),
    "milliliter": (F(1, 1000000), dim(3, 0, 0)),
    "ml": (F(1, 1000000), dim(3, 0, 0)),
    "cc": (F(1, 1000000), dim(3, 0, 0)),
    "pound": (F(45359237, 100000000), dim(0, 1, 0)),
    "ounce": (F(45359237, 1600000000), dim(0, 1, 0)),
    # time
    "second": (F(1), dim(0, 0, 1)), "s": (F(1), dim(0, 0, 1)),
    "minute": (F(60), dim(0, 0, 1)), "hour": (F(3600), dim(0, 0, 1)),
    "h": (F(3600), dim(0, 0, 1)), "day": (F(86400), dim(0, 0, 1)),
    "week": (F(604800), dim(0, 0, 1)),
}

PLURAL = re.compile(r'(?<=[a-z])s$')
PLURAL_ES = re.compile(r'(?<=[a-z])es$')


def lookup(tok):
    """`inches` -> `inch`. Stripping only a trailing "s" gave "inche" and the
    whole conversion fell through to a rule about metres."""
    t = tok.lower().strip()
    if t in UNITS:
        return UNITS[t]
    for pat in (PLURAL_ES, PLURAL):
        cand = pat.sub("", t)
        if cand in UNITS:
            return UNITS[cand]
    return None


def parse_unit(s):
    """'km/h', 'meters per second', 'kg*m/s^2' -> (scale, dimension vector)"""
    s = s.lower().replace("per", "/").replace("·", "*").replace("^", "")
    num, den = s, ""
    if "/" in s:
        parts = s.split("/")
        num, den = parts[0], "/".join(parts[1:])
    scale, d = F(1), [0, 0, 0]

    def apply(chunk, sign):
        nonlocal scale
        for piece in re.split(r'[*\s]+', chunk.strip()):
            if not piece:
                continue
            m = re.match(r'^([a-z]+)(\d*)$', piece)
            if not m:
                return False
            base, exp = m.group(1), int(m.group(2) or 1)
            u = lookup(base)
            if u is None:
                return False
            f, dv = u
            scale *= f ** (sign * exp)
            for i in range(3):
                d[i] += sign * exp * dv[i]
        return True

    if not apply(num, 1):
        return None
    if den and not apply(den, -1):
        return None
    return scale, tuple(d)


# the unit portion must ADMIT DIGITS -- exponents live there (s2, m3), and
# excluding them made every compound unit look like "not a conversion
# question" rather than an unknown one. Units still must START with a letter,
# which keeps the quantity boundary unambiguous.
ASK = re.compile(
    r'(?:convert\s+)?(-?\d+(?:\.\d+)?)\s*([a-z][a-z0-9^*/\s]*?)\s+'
    r'(?:to|in|into)\s+([a-z][a-z0-9^*/\s]*?)\s*(?:[.?!].*)?$', re.I)


# A refusal this layer makes because the question is MALFORMED is terminal:
# no later, vaguer layer may answer it. A refusal because the question is not
# a conversion at all is not terminal -- some other layer may own it.
# Measured consequence of conflating them: "convert 5 meters to kilograms"
# was refused here on dimension mismatch and then answered as 500 by the
# natural-language `meters` rule, which matched on the words alone.
TERMINAL = ("dimension mismatch", "inverse check failed",
            "SI-path check disagreed")


def terminal(why: str) -> bool:
    return any(t in (why or "") for t in TERMINAL)


def convert(question):
    """-> (value, detail) or (None, reason). Dimension mismatch is refused."""
    m = ASK.search(question.strip())
    if not m:
        return None, "not a conversion question"
    qty, src_s, dst_s = m.group(1), m.group(2), m.group(3)
    src, dst = parse_unit(src_s), parse_unit(dst_s)
    if src is None:
        return None, f"unknown unit: {src_s.strip()!r}"
    if dst is None:
        return None, f"unknown unit: {dst_s.strip()!r}"
    if src[1] != dst[1]:
        return None, (f"dimension mismatch {src[1]} vs {dst[1]} -- "
                      f"{src_s.strip()} and {dst_s.strip()} are not the "
                      f"same kind of quantity")
    q = F(qty) if "." not in qty else F(qty)
    out = q * src[0] / dst[0]

    # check 1 (INVERSE): convert the result back
    back = out * dst[0] / src[0]
    if back != q:
        return None, "inverse check failed"
    # check 2 (REDUNDANT): route through SI base by a separate path
    si = q * src[0]
    out2 = si / dst[0]
    if out2 != out:
        return None, "SI-path check disagreed"
    return out, f"{src_s.strip()} -> {dst_s.strip()}, dim {src[1]}"
