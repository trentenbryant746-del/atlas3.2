"""
The gate. Three measurements, and a negative control on each.

  IN-TEMPLATE      every curriculum record, all rules present.
                   Expected near 100% and it means almost nothing: the rules
                   and the data share a generator. Reported to prove the
                   harness works, not to claim anything.

  HELD-OUT         one rule removed, then its own questions asked. The number
                   that matters is not accuracy -- it is whether the system
                   DECLINES instead of guessing. A lookup would return its
                   nearest stored string and be confidently wrong; a rule
                   system should say UNCOVERED.

  REFUSAL CONTROL  questions it must refuse. If it answers these, every
                   number above is worthless.

Correctness is never taken from the corpus: every answer is recomputed and
compared against the stored one, and disagreement is reported both ways.
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine import route as R                                   # noqa: E402
from rules.arith import RULES, BY_NAME                          # noqa: E402

# bundled so the repo is self-contained; the environment variable lets a
# different copy be pointed at without editing code.
CURRICULUM = Path(os.environ.get(
    "ATLAS_CURRICULUM",
    str(ROOT / "data" / "external" / "reasoning-curriculum.jsonl")))

REFUSE = [
    "What is the capital of France?",
    "Integrate x^2 dx.",
    "Calculate the meaning of life.",
    "Who wrote Hamlet?",
    "Calculate 5 ÷ 0. Show a brief check.",
    "Prove the Collatz conjecture.",
    "Evaluate: (100 + 27) ÷ -9 ^ 96.",
    "Solve for y: 3y^2 + 2 = 50.",
]


def load():
    return [json.loads(l) for l in CURRICULUM.read_text().splitlines() if l.strip()]


def run(records, disabled=()):
    """-> verdict counts, plus agreement with the stored answers."""
    keep = [r for r in RULES if r.name not in disabled]
    saved, R.RULES = R.RULES, keep
    v = Counter(); agree = 0; disagree = []
    by_rule = defaultdict(Counter)
    try:
        for rec in records:
            res = R.route(rec["prompt"])
            v[res.verdict] += 1
            by_rule[res.rule or "-"][res.verdict] += 1
            if res.verdict == R.ANSWERED:
                if res.answer == rec["answer"].strip():
                    agree += 1
                else:
                    disagree.append((rec["prompt"], rec["answer"], res.answer))
    finally:
        R.RULES = saved
    return v, agree, disagree, by_rule


def which_rule(prompt):
    for r in RULES:
        if r.match(prompt) is not None:
            return r.name
    return None


def main():
    recs = load()
    print(f"curriculum: {len(recs)} records\n")

    # ---------- 1. in-template ----------
    v, agree, disagree, _ = run(recs)
    n = len(recs)
    print("1. IN-TEMPLATE  (all rules present)")
    print(f"   verdicts {dict(v)}")
    print(f"   recomputed answer agrees with stored: {agree}/{n} ({agree/n:.2%})")
    if disagree:
        print(f"   DISAGREEMENTS ({len(disagree)}):")
        for p, stored, mine in disagree[:5]:
            print(f"     {p[:54]}  stored {stored!r} recomputed {mine!r}")
    print("   (near-100% here is expected and proves nothing: the rules and")
    print("    the corpus share a generator.)\n")

    # ---------- 2. held-out ----------
    print("2. HELD-OUT  (rule removed, then its own questions asked)")
    print(f"   {'rule':<10}{'its questions':>15}{'UNCOVERED':>12}{'WRONG':>8}"
          f"{'declined':>11}")
    print("   " + "-" * 56)
    owned = defaultdict(list)
    for rec in recs:
        owned[which_rule(rec["prompt"])].append(rec)
    total_wrong = 0
    for rule in RULES:
        mine = owned.get(rule.name, [])
        if not mine:
            continue
        v2, ag2, dis2, _ = run(mine, disabled={rule.name})
        unc = v2[R.UNCOVERED] + v2[R.AMBIGUOUS]
        wrong = v2[R.ANSWERED] - ag2 + v2[R.CONTRADICTED]
        answered_anyway = v2[R.ANSWERED]
        total_wrong += wrong
        print(f"   {rule.name:<10}{len(mine):>15}{unc:>12}{wrong:>8}"
              f"{unc/len(mine):>10.0%}")
    print(f"\n   total wrong answers when the owning rule is absent: {total_wrong}")
    print("   (a lookup system returns its nearest stored answer here and is")
    print("    confidently wrong; declining is the correct behaviour.)\n")

    # ---------- 3. refusal control ----------
    print("3. REFUSAL CONTROL  (must not answer)")
    leaked = []
    for q in REFUSE:
        res = R.route(q)
        mark = "refused" if res.verdict != R.ANSWERED else "ANSWERED -- LEAK"
        if res.verdict == R.ANSWERED:
            leaked.append((q, res.answer))
        print(f"   {mark:<17} {q[:52]}")
    print()
    if leaked:
        print(f"   GATE IS BLIND: answered {len(leaked)} it should have refused.")
        return 1
    print("   all refused -- the gate can tell coverage from competence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
