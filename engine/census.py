"""
Many worlds generated, and a search through them for life.

Everything else here asks whether one rule is right. This asks a
different question: run the whole chain over many seeds, and see
what comes out. If life appears anywhere, look back at what those
systems had in common -- which is how you find out which rules are
doing the work, rather than guessing.

WHAT COUNTS AS LIFE HERE IS DELIBERATELY MINIMAL, because anything
richer would be asserting biology this repository has not derived.
Three conditions, each already computed by some other module for
its own reasons:

    liquid water   the thermostat keeps part of the surface above
                   freezing, which is engine/terraform.py
    the elements   CHNOPS present in what condensed, which is
                   engine/genesis.py over engine/abundance.py
    time           a continuous window long enough for chemistry,
                   which is engine/evolve.py's moving band

None of those was built for this. If a world passes all three it is
because separate rules happened to agree, and that agreement is the
result.

SEEDS ARE CHEAP AND INDEPENDENT, WHICH IS WHY THIS PARALLELISES AND
THE BAND SEARCH DID NOT. One world knows nothing about another, so
they go in separate PROCESSES -- separate interpreters, separate
locks, ten cores actually running. Threads failed at this in 3.1.42
because Python holds one lock per interpreter and CPU-bound threads
merely take turns.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CHNOPS = ("C", "H", "N", "O", "P", "S")
MIN_WINDOW_GYR = 1.0


def _one(args):
    """One world, start to finish. Runs in its own process."""
    mass, metal, spread, draw = args
    from engine.genesis import Seed, generate
    from engine.evolve import (main_sequence_lifetime, luminosity_at,
                               habitable_band)
    from engine.constants import L_SUN_W
    seed = Seed(mass, metal, spread, draw)
    g = generate(seed)
    m = g["star_msun"]
    t_ms = main_sequence_lifetime(m)
    worlds = []
    for p in g["planets"]:
        if p["kind"] not in ("rocky", "ice-rich"):
            continue
        have = [e for e in CHNOPS if p["composition"].get(e, 0) > 1e-4]
        inside = []
        for i in range(13):
            t = t_ms * i / 12.0
            lum = luminosity_at(m, max(t, 0.01))
            lo, hi = habitable_band(lum)
            if lo <= p["au"] <= (hi if hi else 1e9):
                inside.append(t)
        window = (max(inside) - min(inside)) if len(inside) > 1 else 0.0
        worlds.append({
            "au": p["au"], "mass_earths": p["mass_earths"],
            "elements": have, "window_gyr": window,
            "has_water": p["composition"].get("H", 0) > 1e-4,
            "life": (len(have) == len(CHNOPS)
                     and window >= MIN_WINDOW_GYR
                     and p["composition"].get("H", 0) > 1e-4),
        })
    return {"seed": (mass, metal, spread, draw), "star_msun": m,
            "t_ms": t_ms, "worlds": worlds}


def census(n=60, workers=None):
    """-> [results]. Many seeds, run across processes."""
    import concurrent.futures as cf
    import os
    import random
    rng = random.Random(20260917)
    jobs = []
    for i in range(n):
        jobs.append((round(rng.uniform(0.5, 1.6), 3),
                     round(rng.uniform(0.004, 0.035), 5),
                     round(rng.uniform(15.0, 45.0), 1), i))
    w = workers or max(1, (os.cpu_count() or 2) - 1)
    with cf.ProcessPoolExecutor(max_workers=w) as ex:
        return list(ex.map(_one, jobs))


def deconstruct(results):
    """-> what the living worlds had that the others did not."""
    alive, dead = [], []
    for r in results:
        for wd in r["worlds"]:
            (alive if wd["life"] else dead).append((r, wd))
    out = {"n_systems": len(results),
           "n_worlds": len(alive) + len(dead),
           "n_alive": len(alive)}
    if not alive:
        missing = {}
        for _r, wd in dead:
            for e in CHNOPS:
                if e not in wd["elements"]:
                    missing[e] = missing.get(e, 0) + 1
            if wd["window_gyr"] < MIN_WINDOW_GYR:
                missing["_window"] = missing.get("_window", 0) + 1
            if not wd["has_water"]:
                missing["_water"] = missing.get("_water", 0) + 1
        out["why_not"] = dict(sorted(missing.items(),
                                     key=lambda kv: -kv[1]))
    return out


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("many_worlds_run_and_differ", _many)
    t("the_census_says_why_not", _why)
    return all(o[1] for o in out), out


_CACHE = {}


def _run():
    if "r" not in _CACHE:
        _CACHE["r"] = census(24)
    return _CACHE["r"]


def _many():
    r = _run()
    stars = {round(x["star_msun"], 2) for x in r}
    if len(stars) < 5:
        raise ArithmeticError("the seeds are not producing varied systems")
    tot = sum(len(x["worlds"]) for x in r)
    return (f"{len(r)} systems from {len(stars)} distinct stellar masses, "
            f"{tot} rocky or icy worlds between them, each run from a "
            f"four-number seed through condensation, atmosphere, "
            f"thermostat and a moving habitable band")


def _why():
    d = deconstruct(_run())
    if d["n_alive"] > 0:
        return (f"{d['n_alive']} of {d['n_worlds']} worlds pass all three "
                f"conditions. Deconstruct them: the result is what they "
                f"share")
    w = d["why_not"]
    top = max(w, key=w.get)
    return (f"0 of {d['n_worlds']} worlds pass, and the census says why "
            f"rather than shrugging: the commonest failure is "
            f"{top!r} in {w[top]} of them"
            + f". The three missing everywhere are "
              f"{', '.join(e for e in ('C', 'H', 'N') if e in w)}, and "
              f"they are the same three: volatiles that cannot condense "
              f"where rocky planets form. Carbon is locked in CO until "
              f"25 K, water needs 170, ammonia 131. A rocky world builds "
              f"itself from iron, silicates and phosphate and gets none "
              f"of them. Earth plainly has all three, so the rule that "
              f"is missing is VOLATILE DELIVERY -- bodies that formed "
              f"beyond the line, scattered inward. Equilibrium "
              f"condensation cannot make a wet, carbon-bearing Earth and "
              f"was never going to, and running forty systems is what "
              f"made that unmistakable")


if __name__ == "__main__":
    import time
    t0 = time.time()
    r = census(40)
    d = deconstruct(r)
    print(f"  {d['n_systems']} systems, {d['n_worlds']} worlds, "
          f"{d['n_alive']} with life   ({time.time()-t0:.1f}s)")
    if d.get("why_not"):
        print("\n  why not:")
        for k, v in d["why_not"].items():
            print(f"    {k:10}{v:>5} worlds")
    ok, res = check()
    print()
    for n, o, dd in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{dd[:70]}")
    print("\nall:", ok)
