"""
Negative controls. Break each rule; the check must catch it.

A check that cannot detect a broken rule is decoration, and reporting it as
verification is worse than reporting nothing. Every DERIVED rule gets its
derive() sabotaged here, and the check has to notice. Any rule whose check
still agrees after sabotage is reported as BLIND and its verification claim
is void.

The ASSERTED rule is the control on the controls: it must be impossible to
verify, and the harness must say so rather than quietly passing it.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rules.general import RULES                                 # noqa: E402
from rules.kinds import ASSERTED                                # noqa: E402

PROBES = {
    "f_to_c":       "convert 212 degrees F to celsius",
    "reverse":      'reverse the string "frankenstein"',
    "weekday":      "what day of the week is 2026-09-15",
    "syllogism":    "All cats are mammals. All mammals are animals. "
                    "Are all cats animals?",
    "py_syntax":    "is this valid python: def f(x): return x+1",
    "earth_radius": "what is earth's mean radius",
}

# each sabotage returns a plausible-but-wrong answer of the right type
SABOTAGE = {
    "f_to_c":    lambda *a: 99.9,
    "reverse":   lambda *a: "notreversed",
    "weekday":   lambda *a: "Friday",
    "syllogism": lambda *a: "no",
    "py_syntax": lambda *a: "invalid",
}


def main() -> int:
    print(f"{'rule':<14}{'kind':<10}{'check':<11}{'honest':>8}{'sabotaged':>11}")
    print("-" * 56)
    blind, unverifiable = [], []
    for r in RULES:
        q = PROBES[r.name]
        args = r.bind(q)
        assert args is not None, f"probe does not match {r.name}"

        if r.kind == ASSERTED:
            ok = r.verify(args, r.answer(args))
            unverifiable.append(r.name)
            print(f"{r.name:<14}{'ASSERTED':<10}{'-':<11}{'n/a':>8}{'n/a':>11}"
                  f"   {'(cannot be verified -- correct)' if ok is None else 'LEAK'}")
            if ok is not None:
                blind.append(r.name)
            continue

        honest = r.verify(args, r.answer(args))
        real = r.derive
        r.derive = SABOTAGE[r.name]
        try:
            caught = r.verify(args, r.answer(args)) is False
        finally:
            r.derive = real
        print(f"{r.name:<14}{'DERIVED':<10}{r.check_kind:<11}"
              f"{'pass' if honest else 'FAIL':>8}{'caught' if caught else 'BLIND':>11}")
        if not caught or not honest:
            blind.append(r.name)

    print()
    if blind:
        print(f"  {len(blind)} rule(s) with a check that proves nothing: {blind}")
        print("  their verification claims are void.")
        return 1
    print(f"  every DERIVED check caught its sabotage.")
    print(f"  {len(unverifiable)} ASSERTED rule(s) correctly reported as "
          f"unverifiable rather than passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
