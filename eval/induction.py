"""
Leave-one-rule-out induction. Does a rule derived from examples generalise?

For each of the 9 templates: take K examples, induce an expression from them
with no knowledge of the operation, then evaluate on every REMAINING example
of that template. Held-out by construction -- the induced rule never saw them.

Reported honestly, including the ones it cannot do. The search is enumerative
over a fixed basis and its cost is exponential in expression size, so rules
needing large expressions are expected to fail and are reported as failures
rather than omitted.

On the induced CHECK: a second expression fitted to the SAME examples is not
an independent verification of the first. Both were chosen to agree on the
training set. What it detects is OVERFITTING -- if two structurally different
functions coincide on the training examples and diverge on held-out ones, the
induction did not find the rule. That is worth having, but it is not proof.
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.induce import synthesize, ev                        # noqa: E402
from eval.gate import load, which_rule                          # noqa: E402
from rules.arith import BY_NAME, fmt                            # noqa: E402

K = 6                 # examples shown to the synthesizer
MAX_SIZE = 9
NODE_CAP = 3_000_000


def parse(rec):
    args = [int(x) for x in re.findall(r'-?\d+', rec["prompt"])]
    a = rec["answer"].strip()
    if "/" in a:
        n, d = a.split("/")
        return args, Fraction(int(n), int(d))
    return args, Fraction(int(a))


def main() -> int:
    recs = load()
    owned = defaultdict(list)
    for r in recs:
        owned[which_rule(r["prompt"])].append(r)

    print(f"induce from {K} examples, evaluate on the rest "
          f"(max expression size {MAX_SIZE})\n")
    print(f"{'rule':<10}{'train':>6}{'held-out':>10}{'correct':>9}"
          f"{'acc':>8}{'secs':>7}  induced")
    print("-" * 92)
    total_h = total_c = 0
    failed = []
    for name in ("add", "sub", "mul", "div", "meters", "pct",
                 "linear", "fracadd", "compound"):
        pool = owned.get(name, [])
        if not pool:
            continue
        train = [parse(r) for r in pool[:K]]
        held = [parse(r) for r in pool[K:]]
        t0 = time.time()
        d, alt, st = synthesize(train, max_size=MAX_SIZE, node_cap=NODE_CAP)
        dt = time.time() - t0
        if d is None:
            failed.append(name)
            print(f"{name:<10}{len(train):>6}{len(held):>10}{'-':>9}{'-':>8}"
                  f"{dt:>7.1f}  NOT FOUND (needs a larger expression)")
            continue
        ok = 0
        for args, tgt in held:
            try:
                ok += (ev(d, args) == tgt)
            except ZeroDivisionError:
                pass
        total_h += len(held); total_c += ok
        acc = ok / max(len(held), 1)
        print(f"{name:<10}{len(train):>6}{len(held):>10}{ok:>9}{acc:>8.1%}"
              f"{dt:>7.1f}  {d}")
    print("-" * 92)
    print(f"{'TOTAL':<10}{'':>6}{total_h:>10}{total_c:>9}"
          f"{total_c/max(total_h,1):>8.1%}")
    if failed:
        print(f"\nnot induced: {failed} -- these need expressions beyond "
              f"size {MAX_SIZE}; the search is exponential in size.")
    print("\nheld-out means the induced rule never saw these prompts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
