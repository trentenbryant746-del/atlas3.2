"""
Full audit. Every headline claim in the README, re-derived and checked here.

A claim that is not re-checked by this file is not a claim this repo makes.
Each entry states the number asserted and the number measured now, and
FAILS on disagreement rather than printing whatever it finds.
"""
from __future__ import annotations

import io
import math
import statistics
import sys
import contextlib
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RESULTS = []


def check(name, got, want, tol=0.0, unit=""):
    if isinstance(want, bool) or isinstance(got, bool):
        ok = got == want
    elif isinstance(want, (int, float)) and tol:
        ok = abs(got - want) <= tol
    else:
        ok = got == want
    RESULTS.append((name, got, want, ok, unit))
    return ok


def main() -> int:
    import atlas
    from eval.gate import load, which_rule
    from eval.induction import parse
    from engine.induce2 import synthesize_mim
    from engine.induce import ev
    from engine import route as R, units as U, dates as D, parse as P
    from engine.experts import PT, route_expert
    from engine.particles import ALL_PARTICLES, atom, bound_state
    from engine.nucleo import (primordial_helium, fusion_energy_MeV,
                               iron_peak, M_H_ATOM, M_HE4_ATOM, REACTIONS,
                               balances)
    from engine.epochs import can_bind
    from engine.cosmos import run, distance_to
    from engine.mixtures import observed
    from engine.chain import build, verify
    from engine.bind import Typed, bind
    from engine.ir import cross_verify, N as IRN, EXECUTABLE
    import json

    recs = load()

    # --- 1 curriculum, through the front door ---------------------------
    ok = sum(1 for r in recs
             if (a := atlas.ask(r["prompt"])) and str(a.value) == r["answer"].strip())
    check("curriculum answered correctly", ok, len(recs))

    # --- 2 induction recovers every rule, held-out ----------------------
    owned = defaultdict(list)
    for r in recs:
        owned[which_rule(r["prompt"])].append(r)
    tot = cor = 0
    for name, pool in owned.items():
        e, _ = synthesize_mim([parse(r) for r in pool[:6]], max_size=9)
        for args, tgt in [parse(r) for r in pool[6:]]:
            tot += 1
            try:
                cor += (ev(e, args) == tgt)
            except ZeroDivisionError:
                pass
    check("induction held-out", cor, tot)

    # --- 3 held-out benchmark from the other project --------------------
    bench = [json.loads(l) for l in
             (ROOT / "data" / "atlas-novel-sat-like.jsonl").read_text().splitlines() if l.strip()]
    answered = sum(1 for b in bench if atlas.ask(b["prompt"]))
    check("external benchmark answered", answered, len(bench))

    # --- 4 refusals ------------------------------------------------------
    refuse = ["who wrote Hamlet", "convert 5 meters to kilograms",
              "add 2026-01-01 and 2026-09-15", "what day of the week is 2026-02-30",
              "integrate x squared dx", "solve for y: 3y squared + 2 = 50"]
    check("must-refuse all refused", sum(1 for q in refuse if not atlas.ask(q)),
          len(refuse))

    # --- 5 physics -------------------------------------------------------
    check("periodic table size", len(PT), 118)
    check("hadrons satisfy Gell-Mann-Nishijima",
          sum(1 for p in ALL_PARTICLES if p.gell_mann_nishijima() is True),
          sum(1 for p in ALL_PARTICLES if p.is_hadron))
    Y, _ = primordial_helium()
    check("primordial helium Y_p", round(Y, 3), 0.245, tol=0.02)
    q = fusion_energy_MeV([(M_H_ATOM, 4)], [(M_HE4_ATOM, 1)])
    check("4H->He4 MeV", round(q, 2), 26.73, tol=0.05, unit="MeV")
    check("iron peak element Z", iron_peak()["Z"], 26)
    check("broken reaction refused",
          balances(*REACTIONS["BROKEN 4p -> He4 (no leptons)"]), False)

    # --- 6 typing and causality -----------------------------------------
    check("typed bind refuses dist+time",
          bind("add", Typed("d", (1, 0, 0)), Typed("t", (0, 0, 1))) is None, True)
    check("gold refused before ns_merger", can_bind(["Au"], "supernova")[0], False)
    check("gold allowed at ns_merger", can_bind(["Au"], "ns_merger")[0], True)

    # --- 7 cosmology: conservation, diversity, convergence ---------------
    sun, _ = observed("sun")
    hs, cons = [], True
    for i in range(60):
        stars, final, led = run(generations=4, seed=f"u{i}", dilution=5.0)
        hs.append(final.get("H", 0))
        cons = cons and all(l["conserved"] for l in led)
    check("mass conserved in every universe", cons, True)
    check("universes differ (sd > 0)", statistics.stdev(hs) > 1e-5, True)
    d, _n = distance_to(sun.fractions, final)
    check("distance to solar", round(d, 4), 0.0, tol=0.005)

    # --- 8 the chain -----------------------------------------------------
    states = [("a", {"x": 1}), ("b", {"x": 2}), ("c", {"x": 3})]
    ch = build("s", states)
    check("chain verifies", verify(ch, states)[0], True)
    check("chain head is 256 bits", len(ch["head"]) * 4, 256, unit="bits")
    tampered = [("a", {"x": 1}), ("b", {"x": 99}), ("c", {"x": 3})]
    check("chain detects tampering", verify(ch, tampered)[0], False)

    # --- 9 multi-backend codegen -----------------------------------------
    prog = [IRN("let", "x", 0), IRN("loop", 12, [IRN("add", "x", 3, 7),
                                                 IRN("emit", "x")])]
    agree, srcs, traces, _ = cross_verify(prog)
    check("backends agree", agree, True)
    # The claim being audited is that the executable backends AGREE,
    # not that there are three of them. engine/ir.py drops gdscript
    # when Godot is absent, which is correct; asserting the count made
    # a clean Linux or Windows box report 20/21 while the system was
    # working. Two agreeing is still cross-verification -- one is not,
    # because there is nothing to disagree with it.
    check("executable backends cross-verify", len(EXECUTABLE) >= 2, True)

    # --- report ----------------------------------------------------------
    w = max(len(r[0]) for r in RESULTS)
    print(f"{'claim':<{w}}  {'measured':>12}  {'expected':>12}   ")
    print("-" * (w + 34))
    bad = 0
    for name, got, want, ok, unit in RESULTS:
        bad += not ok
        print(f"{name:<{w}}  {str(got):>12}  {str(want):>12}   "
              f"{'ok' if ok else 'FAIL'}")
    print(f"\n{len(RESULTS) - bad}/{len(RESULTS)} claims verified")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
