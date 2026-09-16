"""
Answer generation, governed by how the answer is checked.

This is the point of the taxonomy. "Generate more prompts and answers and
they will naturally be right" is true for exactly one of the two kinds:

  DERIVED / DERIVED_UNCHECKED
            the rule produces the answer by computation. Checked or not, the
            pair is reproducible from the rule, so generating is safe.
            Every generated pair is verified at the moment it is made. Volume
            is free and carries no risk -- but it also carries no NEW
            information, because the generator already contained the answer.
            Generating 10^6 of these compresses back to the rule.

  ASSERTED  no derivation exists. Producing a new one does not generate an
            answer, it INVENTS A FACT. Refused here, by policy, not by
            configuration.

So the honest version of "astronomically many pairs" is: unlimited where a
check exists, zero where one does not.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rules.general import RULES                                 # noqa: E402
from rules.kinds import ASSERTED                                # noqa: E402

WORDS = ["frankenstein", "atlas", "belt", "router", "compression", "eve",
         "curriculum", "primitive", "verdict", "namespace"]
SNIPPETS = ["def f(x): return x+1", "x = [1,2,3]", "def f(x) return x+1",
            "for i in range(3): print(i)", "class A: pass", "if True print(1)"]

SAMPLERS = {
    "f_to_c":    lambda r: (f"convert {r.randint(-100, 300)} degrees F to celsius",),
    "reverse":   lambda r: (f'reverse the string "{r.choice(WORDS)}"',),
    "weekday":   lambda r: (lambda y, m, d:
                            (f"what day of the week is {y:04d}-{m:02d}-{d:02d}",))(
                                r.randint(1900, 2100), r.randint(1, 12), r.randint(1, 28)),
    "syllogism": lambda r: (lambda a, b, c:
                            (f"All {a} are {b}. All {b} are {c}. Are all {a} {c}?",))(
                                *r.sample(WORDS, 3)),
    "py_syntax": lambda r: (f"is this valid python: {r.choice(SNIPPETS)}",),
}


def generate(n_per_rule=2000, seed=7):
    rng = random.Random(seed)
    made, verified, refused = 0, 0, []
    failures = []
    for rule in RULES:
        if rule.kind == ASSERTED:
            refused.append(rule.name)
            continue
        sampler = SAMPLERS.get(rule.name)
        if sampler is None:
            continue
        for _ in range(n_per_rule):
            q = sampler(rng)[0]
            args = rule.bind(q)
            if args is None:
                failures.append(("unbindable", q))
                continue
            try:
                ans = rule.answer(args)
            except Exception as e:
                failures.append((f"derive raised {type(e).__name__}", q))
                continue
            made += 1
            ok = rule.verify(args, ans)
            if ok:
                verified += 1
            else:
                failures.append(("check disagreed", q))
    return made, verified, refused, failures


def main() -> int:
    made, verified, refused, failures = generate()
    print(f"generated  {made:,} prompt/answer pairs")
    print(f"verified   {verified:,}/{made:,}  "
          f"({verified/max(made,1):.2%}) at the moment of creation")
    print(f"failures   {len(failures)}")
    for what, q in failures[:5]:
        print(f"   {what}: {q[:60]}")
    print()
    print(f"REFUSED generation for {len(refused)} ASSERTED rule(s): {refused}")
    print("  no derivation exists for these, so producing a new pair would")
    print("  invent a fact rather than generate an answer.")
    print()
    print("what this volume is worth:")
    print(f"  {made:,} pairs compress back to "
          f"{len([r for r in RULES if r.kind != ASSERTED])} rules plus their")
    print("  parameter samples. The count is not evidence of knowledge --")
    print("  it is evidence the generator ran.")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
