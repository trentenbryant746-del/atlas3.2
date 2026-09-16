"""
Turn induced expressions into rules the router can use.

A complete rule is pattern + derive + check. Induction supplies DERIVE. The
pattern -- which spans of text are the operands, and which questions this
rule is even about -- is still supplied by a human. That boundary is real and
is not papered over here: the system learns the computation, not the
recognition.

The induced pair (derive, alt) becomes check_kind REDUNDANT when the two are
structurally different, and NONE otherwise. REDUNDANT here is weaker than a
hand-written check: both expressions were fitted to the same examples, so
they agree on the training set by construction. What their disagreement
detects is OVERFITTING on new input, not incorrectness. Labelled accordingly.
"""
from __future__ import annotations

import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.induce import synthesize, ev                        # noqa: E402
from rules.kinds import Rule, REDUNDANT, NONE                   # noqa: E402


def fmt(v):
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    return str(v)


def learn(name, subject, pattern, examples, max_size=9, node_cap=3_000_000):
    """examples: [(args, Fraction)] -> (Rule, report) or (None, report)"""
    d, alt, st = synthesize(examples, max_size=max_size, node_cap=node_cap)
    if d is None:
        return None, {"found": False, **st}
    rule = Rule(
        name=name, subject=subject, pattern=pattern,
        derive=lambda *a: ev(d, [int(x) for x in a]),
        check=(lambda *a: ev(alt, [int(x) for x in a])) if alt else None,
        check_kind=REDUNDANT if alt else NONE,
        source=None if alt else "induced, no independent second derivation",
        fmt=fmt,
    )
    return rule, {"found": True, "derive": str(d), "alt": str(alt), **st}


if __name__ == "__main__":
    # end to end: never-before-seen operation -> usable rule
    from fractions import Fraction as F
    ex = [([n], F(3 * n + 7)) for n in (1, 4, 9, 12, 20, 33)]
    pat = re.compile(r'triple\s+(-?\d+)\s+and add seven', re.I)
    rule, rep = learn("triple_plus_7", "arith.learned", pat, ex)
    print("induction report:", {k: rep[k] for k in ("found", "derive", "alt")})
    print("rule:", rule.describe())
    print()
    for q in ("triple 25 and add seven", "triple -4 and add seven",
              "what is the capital of France"):
        args = rule.bind(q)
        if args is None:
            print(f'  "{q}" -> no match (correctly declined)')
            continue
        a = rule.answer(args)
        v = rule.verify(args, a)
        print(f'  "{q}" -> {a}   check={"agreed" if v else "DISAGREED" if v is False else "none"}')
