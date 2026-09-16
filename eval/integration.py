"""
Every corpus through the one entry point, plus a cross-layer disagreement hunt.

Wiring introduces a failure that no component has on its own: two layers that
both answer, differently. The component tests cannot see it because each is
run in isolation. So the last section asks every layer that CAN answer a
question to answer it, and reports any disagreement -- those are integration
bugs by definition, since the layers are supposed to be about the same world.
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import atlas                                                    # noqa: E402
from engine import dates as _d, units as _u, parse as _p        # noqa: E402
from engine import nl as _nl, route as _r                       # noqa: E402
from eval.gate import load                                      # noqa: E402


def section(name):
    print(f"\n=== {name} ===")


def main() -> int:
    fails = 0

    # 1 -- the curriculum, through the front door
    section("curriculum (5,737 generator-formatted prompts)")
    recs = load()
    ok = wrong = abst = 0
    bad = []
    for r in recs:
        a = atlas.ask(r["prompt"])
        if not a:
            abst += 1
        elif str(a.value) == r["answer"].strip():
            ok += 1
        else:
            wrong += 1
            if len(bad) < 4:
                bad.append((r["prompt"][:50], r["answer"], a.value, a.mechanism))
    print(f"  answered+correct {ok}   wrong {wrong}   abstained {abst}")
    for b in bad:
        print(f"    {b}")
    fails += wrong

    # 2 -- novel arithmetic, no family
    section("novel compositional arithmetic")
    rng = random.Random(4)

    def gen(d):
        if d == 0 or rng.random() < 0.3:
            return str(rng.randint(1, 30))
        return f"({gen(d-1)} {rng.choice(['+','-','×','÷'])} {gen(d-1)})"

    def exact(s):
        import re
        py = re.sub(r'(\d+)', r'F(\1)', s.replace("×", "*").replace("÷", "/"))
        return eval(py, {"__builtins__": {}, "F": F}, {})

    n = c = 0
    for _ in range(600):
        s = gen(rng.randint(2, 4))
        if not any(ch in s for ch in "+-×÷"):
            continue
        try:
            want = exact(s)
        except ZeroDivisionError:
            continue
        n += 1
        a = atlas.ask(f"Evaluate: {s}.")
        c += (a and str(a.value) == (str(want.numerator) if want.denominator == 1
                                     else f"{want.numerator}/{want.denominator}"))
    print(f"  {c}/{n}")
    fails += (n - c)

    # 3 -- units and dates
    section("units and dates")
    cases = [("convert 3 miles to inches", "190080"),
             ("convert 100 km/h to meters per second", "250/9"),
             ("how many days between 2026-01-01 and 2026-09-15", 257),
             ("what date is 1000 days after 2026-09-15", "2029-06-11"),
             ("what day of the week is 90 days after 100 days before 2026-09-15",
              "Saturday")]
    for q, want in cases:
        a = atlas.ask(q)
        good = a and str(a.value) == str(want)
        print(f"  {'ok ' if good else 'FAIL'} {q[:54]:<56} {a.value}")
        fails += (not good)

    # 4 -- must refuse
    section("must refuse")
    refuse = ["who wrote Hamlet", "convert 5 meters to kilograms",
              "add 2026-01-01 and 2026-09-15", "what day of the week is 2026-02-30",
              "integrate x squared dx", "what is the capital of France",
              "solve for y: 3y squared + 2 = 50"]
    for q in refuse:
        a = atlas.ask(q)
        leak = bool(a)
        print(f"  {'LEAK' if leak else 'ok  '} {q[:54]:<56} {a.value if leak else ''}")
        fails += leak

    # 5 -- cross-layer disagreement
    section("cross-layer disagreement")
    probes = [r["prompt"] for r in recs[:1500]] + \
             [q for q, _ in cases] + refuse
    disagree = 0
    for q in probes:
        vals = {}
        v, w = _d.solve(q)
        if v is not None:
            vals["dates"] = str(v)
        v, w = _u.convert(q)
        if v is not None:
            vals["units"] = atlas._fmt(v)
        v, w = _p.recognise(q)
        if v is not None:
            vals["arith"] = atlas._fmt(v)
        r = _r.route(q)
        if r.verdict == _r.ANSWERED:
            vals["rule"] = r.answer
        r = _nl.route_nl(q)
        if r.verdict == _r.ANSWERED:
            vals["nl"] = r.answer
        if len(set(vals.values())) > 1:
            disagree += 1
            if disagree <= 5:
                print(f"  DISAGREE {q[:46]:<48} {vals}")
    print(f"  {disagree} disagreements over {len(probes)} probes")
    fails += disagree

    print(f"\n{'PASS' if fails == 0 else str(fails) + ' FAILURES'}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
