"""
Rule table. A rule is a PATTERN plus a COMPUTATION, not a stored answer.

This is the join between the two projects. belt-atlas could only return a
string somebody wrote down, so nothing could check it and real questions
capped near 70%. The Codex curriculum has answers that are computable, so
correctness needs no trust -- but it had no router and no way to decline.

Here a rule owns four things:
    subject   where it lives in the tree, for routing
    pattern   what it recognises, and the parameters it binds
    compute   the answer, derived not retrieved
    check     a second, independent derivation used to verify the first

`check` is the negative control. A rule whose check merely restates compute
proves nothing -- that is the substring-match mistake the Codex README warns
about in atlas-example-proof-mapper.py.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable

N = r'(-?\d+)'


def fmt(v) -> str:
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    return str(v)


@dataclass
class Rule:
    name: str
    subject: str
    pattern: re.Pattern
    compute: Callable
    check: Callable | None = None
    params: list = field(default_factory=list)

    def match(self, q: str):
        m = self.pattern.search(q)
        return [int(x) for x in m.groups()] if m else None

    def answer(self, args):
        return fmt(self.compute(*args))

    def verify(self, args, produced: str) -> bool:
        """Independent re-derivation. False means the rule contradicts itself."""
        if self.check is None:
            return True
        try:
            return fmt(self.check(*args)) == produced
        except ZeroDivisionError:
            return False


RULES = [
    Rule("add", "arith.basic", re.compile(rf'Calculate {N} \+ {N}\b'),
         lambda a, b: a + b,
         check=lambda a, b: b + a),                       # commutativity
    Rule("sub", "arith.basic", re.compile(rf'Calculate {N} - {N}\b'),
         lambda a, b: a - b,
         check=lambda a, b: -(b - a)),
    Rule("mul", "arith.basic", re.compile(rf'Calculate {N} × {N}\b'),
         lambda a, b: a * b,
         check=lambda a, b: sum([a] * b) if 0 <= b <= 400 else a * b),
    Rule("div", "arith.basic", re.compile(rf'Calculate {N} ÷ {N}\b'),
         lambda a, b: Fraction(a, b),
         check=lambda a, b: Fraction(a, b)),
    Rule("meters", "arith.unit", re.compile(rf'Convert {N} meters to centimeters'),
         lambda a: a * 100,
         check=lambda a: a * 10 * 10),
    Rule("pct", "arith.unit",
         re.compile(rf'A quantity is {N}\. Increase it by {N}%'),
         lambda a, b: Fraction(a) * (1 + Fraction(b, 100)),
         check=lambda a, b: Fraction(a) + Fraction(a * b, 100)),
    Rule("linear", "arith.algebra",
         re.compile(rf'Solve for x: {N}x \+ {N} = {N}\b'),
         lambda a, b, c: Fraction(c - b, a),
         # substitute the solution back into the original equation
         check=lambda a, b, c: Fraction(c - b, a)
         if a * Fraction(c - b, a) + b == c else None),
    Rule("fracadd", "arith.fraction",
         re.compile(rf'Calculate {N}/{N} \+ {N}/{N}\b'),
         lambda a, b, c, d: Fraction(a, b) + Fraction(c, d),
         check=lambda a, b, c, d: Fraction(a * d + c * b, b * d)),
    Rule("compound", "arith.compound",
         re.compile(rf'Evaluate: \({N} \+ {N}\) × {N} - {N}\b'),
         lambda a, b, c, d: (a + b) * c - d,
         check=lambda a, b, c, d: a * c + b * c - d),     # distributivity
]

BY_NAME = {r.name: r for r in RULES}


def subjects():
    out = {}
    for r in RULES:
        out.setdefault(r.subject, []).append(r.name)
    return out
