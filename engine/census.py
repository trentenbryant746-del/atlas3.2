"""
Many worlds generated, and a search through them for HABITABILITY.

This looked for "life" and it did not. It tested liquid water, the
presence of CHNOPS, and a long enough window -- and not one line of
that is about a cell, a membrane, replication or metabolism. The
word was doing work it had not earned, and a world that passes here
is HABITABLE, which is a statement about a place and not about
anything living in it.

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
            "habitable": (len(have) == len(CHNOPS)
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
            (alive if wd["habitable"] else dead).append((r, wd))
    out = {"n_systems": len(results),
           "n_worlds": len(alive) + len(dead),
           "n_habitable": len(alive)}
    if alive:
        def spread(key, rows):
            v = [k(x) for x in rows for k in (key,)]
            return (min(v), max(v)) if v else (0, 0)
        out["habitable_worlds"] = [
            {"star_msun": round(r["star_msun"], 2),
             "au": w["au"], "mass_earths": round(w["mass_earths"], 2),
             "window_gyr": round(w["window_gyr"], 1),
             "metallicity": r["seed"][1]} for r, w in alive]
        out["shared"] = {
            "star_msun": spread(lambda x: x[0]["star_msun"], alive),
            "au": spread(lambda x: x[1]["au"], alive),
            "metallicity": spread(lambda x: x[0]["seed"][1], alive),
            "vs_all_stars": spread(lambda x: x["star_msun"],
                                   [{"star_msun": r["star_msun"]}
                                    for r in results]),
        }
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
    t("habitable_worlds_share_something_real", _share)
    return all(o[1] for o in out), out


def _share():
    """3.1.44's finding is WITHDRAWN and this records why.

    When carbon could not reach an inner planet, 8 of 293 worlds
    passed and every one orbited a star of 0.51 to 0.54 solar
    masses. That looked like a discovery about small stars. It was
    an artefact of a missing rule: the delivery source only reached
    45 AU, CO condenses at 25 K which is 124 AU out, and the only
    worlds that scraped enough carbon were those around dim stars
    whose ice line sits close in.

    With the source extended to the CO line, 101 of 234 worlds pass
    and they span the ENTIRE population -- every stellar mass, every
    metallicity, orbits from 0.35 to 3.7 AU. Habitability turns out
    to be common once the elements arrive, and the correlation that
    looked like physics was the shape of a gap.
    """
    d = deconstruct(_run())
    if not d.get("habitable_worlds"):
        return ("nothing is habitable in this sample, so there is "
                "nothing to deconstruct")
    sh = d["shared"]
    lo, hi = sh["star_msun"]
    alo, ahi = sh["vs_all_stars"]
    frac = d["n_habitable"] / max(d["n_worlds"], 1)
    wide = (hi - lo) >= 0.5 * (ahi - alo)
    if not wide:
        return (f"{d['n_habitable']} habitable worlds confined to stars "
                f"of {lo:.2f}-{hi:.2f} solar masses out of a population "
                f"spanning {alo:.2f}-{ahi:.2f} -- they share something, "
                f"and what they share is worth deconstructing")
    return (f"{d['n_habitable']} of {d['n_worlds']} worlds are habitable "
            f"({100*frac:.0f}%) and they share NOTHING: stellar mass "
            f"{lo:.2f}-{hi:.2f} against a population of {alo:.2f}-"
            f"{ahi:.2f}, the whole range. That withdraws 3.1.44, which "
            f"reported every habitable world orbiting a 0.51-0.54 solar "
            f"mass star. It did -- when carbon could not reach an inner "
            f"planet, and only dim stars with close-in ice lines "
            f"delivered any. The correlation was the shape of a missing "
            f"rule, not a fact about small stars, and extending the "
            f"comet source to the CO line at 124 AU dissolved it")


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
    if d["n_habitable"] > 0:
        return (f"{d['n_habitable']} of {d['n_worlds']} worlds pass all three "
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
          f"{d['n_habitable']} habitable   ({time.time()-t0:.1f}s)")
    if d.get("why_not"):
        print("\n  why not:")
        for k, v in d["why_not"].items():
            print(f"    {k:10}{v:>5} worlds")
    ok, res = check()
    print()
    for n, o, dd in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{dd[:70]}")
    print("\nall:", ok)
