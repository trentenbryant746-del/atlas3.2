"""
Do the 9 rules reduce to fewer primitives? Verified, not asserted.

belt-atlas/tools/compress.py established the discipline: a compression claim
is only real if the compressed form REPRODUCES the original exactly, and if a
negative control shows the matcher can still fail. Same rule here. Each
composite rule is re-expressed using only the primitives, and the composition
is run against every curriculum record. One mismatch and the claim is dead.

This is the compression question asked properly: not "how many records can we
generate" -- that is free and uninformative -- but "how few independent rules
actually underlie them".
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rules.arith import RULES, BY_NAME, fmt                     # noqa: E402
from eval.gate import load, which_rule                          # noqa: E402

# ---- the proposed primitive basis -------------------------------------
ADD = lambda a, b: a + b
MUL = lambda a, b: a * b
NEG = lambda a: -a
INV = lambda a: Fraction(1, a)

PRIMS = {"ADD": ADD, "MUL": MUL, "NEG": NEG, "INV": INV}

# ---- every rule re-expressed in the basis -----------------------------
COMPOSED = {
    "add":      lambda a, b:       ADD(a, b),
    "sub":      lambda a, b:       ADD(a, NEG(b)),
    "mul":      lambda a, b:       MUL(a, b),
    "div":      lambda a, b:       MUL(a, INV(b)),
    "meters":   lambda a:          MUL(a, 100),
    "pct":      lambda a, b:       ADD(a, MUL(a, MUL(b, INV(100)))),
    "linear":   lambda a, b, c:    MUL(ADD(c, NEG(b)), INV(a)),
    "fracadd":  lambda a, b, c, d: MUL(ADD(MUL(a, d), MUL(c, b)),
                                       INV(MUL(b, d))),
    "compound": lambda a, b, c, d: ADD(MUL(ADD(a, b), c), NEG(d)),
}


def main():
    recs = load()
    print(f"9 rules -> {len(PRIMS)} primitives {sorted(PRIMS)}")
    print(f"verifying the composition against all {len(recs)} records\n")

    ok = {}
    bad = []
    for rec in recs:
        name = which_rule(rec["prompt"])
        rule = BY_NAME[name]
        args = rule.match(rec["prompt"])
        native = rule.answer(args)
        try:
            derived = fmt(COMPOSED[name](*args))
        except ZeroDivisionError:
            derived = "<div0>"
        stored = rec["answer"].strip()
        if native == derived == stored:
            ok[name] = ok.get(name, 0) + 1
        else:
            bad.append((name, rec["prompt"], stored, native, derived))

    print(f"{'rule':<10}{'records':>9}   composition")
    print("-" * 46)
    for r in RULES:
        n = ok.get(r.name, 0)
        w = sum(1 for b in bad if b[0] == r.name)
        mark = "reproduces exactly" if w == 0 else f"FAILS on {w}"
        print(f"{r.name:<10}{n:>9}   {mark}")
    print()

    if bad:
        print(f"COMPRESSION CLAIM REJECTED -- {len(bad)} mismatches")
        for name, p, s, nat, der in bad[:6]:
            print(f"  [{name}] {p[:46]}  stored {s} native {nat} derived {der}")
        return 1

    print(f"all {len(recs)} records reproduced from {len(PRIMS)} primitives.")
    print(f"9 surface rules -> {len(PRIMS)} independent operations "
          f"({9/len(PRIMS):.2f}x), verified on every record.")

    # ---- negative control -------------------------------------------
    # A basis that is genuinely insufficient must FAIL. If a crippled basis
    # still "reproduces" everything, the check is not checking anything.
    print("\nnegative control: drop INV from the basis")
    global INV
    keep = INV
    INV = lambda a: Fraction(1, 1)        # deliberately wrong
    broke = 0
    for rec in recs:
        name = which_rule(rec["prompt"])
        rule = BY_NAME[name]
        args = rule.match(rec["prompt"])
        try:
            if fmt(COMPOSED[name](*args)) != rec["answer"].strip():
                broke += 1
        except ZeroDivisionError:
            broke += 1
    INV = keep
    if broke == 0:
        print("  crippled basis still reproduced everything -- CHECK IS BLIND")
        return 1
    print(f"  crippled basis fails on {broke} records -- the check has teeth")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
