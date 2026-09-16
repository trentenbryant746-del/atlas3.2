"""
End-to-end rule discovery: raw (prompt, answer) pairs -> working rules.

Nothing is supplied. No regexes, no template labels, no hint which question
is arithmetic and which is not. The two inductions compose:

    engine/pattern.py   recovers the TEMPLATE and its capture groups
    engine/induce.py    recovers the COMPUTATION over those groups

and the result is a Rule the router can answer with. This closes the limit
named in the README as the sharpest one: previously a human wrote the
pattern and only `derive` was learned.

What is still supplied: the primitive basis (ADD/MUL/NEG/INV, constants) and
the prior that a numeric literal is a candidate operand. Both are weaker than
writing the rule, and both are stated rather than hidden.
"""
from __future__ import annotations

import sys
import time
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.pattern import induce_patterns                      # noqa: E402
from engine.induce import synthesize, ev                        # noqa: E402
from rules.kinds import Rule, REDUNDANT, NONE                   # noqa: E402


def to_fraction(s):
    s = s.strip()
    if "/" in s:
        n, d = s.split("/")
        return Fraction(int(n), int(d))
    return Fraction(int(s))


def fmt(v):
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    return str(v)


def discover(pairs, k=6, max_size=9, node_cap=3_000_000, min_support=20):
    """pairs: [(prompt, answer_str)] -> (rules, report)"""
    prompts = [p for p, _ in pairs]
    ans = dict(pairs)
    pats = induce_patterns(prompts, min_support=min_support)

    rules, report = [], []
    for i, p in enumerate(pats):
        rx = p["regex"]
        members = [q for q in prompts if rx.search(q)]
        examples = []
        for q in members[:k]:
            m = rx.search(q)
            try:
                examples.append(([int(g) for g in m.groups()],
                                 to_fraction(ans[q])))
            except (ValueError, ZeroDivisionError):
                continue
        if len(examples) < 3:
            report.append({"n": p["n"], "found": False,
                           "why": "too few parseable examples"})
            continue
        t0 = time.time()
        d, alt, st = synthesize(examples, max_size=max_size, node_cap=node_cap)
        dt = time.time() - t0
        if d is None:
            report.append({"n": p["n"], "found": False, "secs": dt,
                           "example": p["example"],
                           "why": f"no expression up to size {max_size}"})
            continue
        rule = Rule(
            name=f"learned_{i}", subject="learned",
            pattern=rx,
            derive=(lambda dd: lambda *a: ev(dd, [int(x) for x in a]))(d),
            check=((lambda aa: lambda *a: ev(aa, [int(x) for x in a]))(alt)
                   if alt else None),
            check_kind=REDUNDANT if alt else NONE,
            fmt=fmt,
        )
        rules.append((rule, members))
        report.append({"n": p["n"], "found": True, "derive": str(d),
                       "alt": str(alt), "secs": dt, "arity": p["arity"],
                       "example": p["example"]})
    return rules, report


def main() -> int:
    from eval.gate import load
    recs = load()
    pairs = [(r["prompt"], r["answer"]) for r in recs]
    K = 6
    print(f"{len(pairs)} raw (prompt, answer) pairs. No labels, no regexes, "
          f"no rule names.\n")

    rules, report = discover(pairs, k=K)
    print(f"{'n':>6}{'arity':>6}{'secs':>7}  derived expression")
    print("-" * 78)
    for r in report:
        if r["found"]:
            print(f"{r['n']:>6}{r['arity']:>6}{r['secs']:>7.1f}  {r['derive']}")
        else:
            print(f"{r['n']:>6}{'-':>6}{r.get('secs',0):>7.1f}  FAILED: {r['why']}")
    print()

    # held-out: every instance beyond the K the synthesiser saw
    total = correct = 0
    ans = dict(pairs)
    for rule, members in rules:
        for q in members[K:]:
            m = rule.pattern.search(q)
            total += 1
            try:
                got = rule.answer([g for g in m.groups()])
            except Exception:
                continue
            correct += (got == ans[q].strip())
    print(f"HELD-OUT  {correct}/{total}  {correct/max(total,1):.2%}")
    print(f"  (every instance the synthesiser never saw, across all "
          f"{len(rules)} discovered rules)")
    return 0 if correct == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
