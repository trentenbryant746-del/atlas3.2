"""
Four living worlds, followed step by step, and what happens to them.

The census says eight of 293 worlds pass and that every one orbits a
star around half the Sun's mass. That is a summary. This follows the
individual worlds through their star's whole life and records what
changes and when, because a summary cannot say whether a world was
habitable early and lost it, gained it late, or held it throughout --
and those are different worlds.

NOTHING NEW IS COMPUTED HERE. Every number comes from a rule already
written for its own reasons: the star from engine/evolve.py, the band
from engine/terraform.py's thermostat, the composition from
engine/genesis.py over engine/abundance.py, the delivery from the
outer reservoir. Watching is reading, not modelling.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CHNOPS = ("C", "H", "N", "O", "P", "S")


def living(n=60):
    """-> [(seed, planet)] for every world the census calls alive."""
    from engine.census import census, deconstruct
    r = census(n)
    d = deconstruct(r)
    out = []
    for res in r:
        for w in res["worlds"]:
            if w["life"]:
                out.append((res, w))
    return out, d


def follow(seed_tuple, au, steps=14):
    """-> [rows]. One world, through its star's life."""
    from engine.genesis import Seed, generate
    from engine.evolve import (main_sequence_lifetime, luminosity_at,
                               habitable_band, ice_line_at)
    mass, metal, spread, draw = seed_tuple
    g = generate(Seed(mass, metal, spread, draw))
    m = g["star_msun"]
    t_ms = main_sequence_lifetime(m)
    planet = min(g["planets"], key=lambda p: abs(p["au"] - au))
    rows = []
    prev = None
    for i in range(steps):
        t = 1.3 * t_ms * i / (steps - 1)
        lum = luminosity_at(m, max(t, 0.01))
        lo, hi = habitable_band(lum)
        state = ("too hot" if planet["au"] < lo else
                 "temperate" if (hi is None or planet["au"] <= hi)
                 else "frozen")
        rows.append({"t": t, "lum": lum, "inner": lo, "outer": hi,
                     "ice": ice_line_at(lum), "state": state,
                     "post_ms": t > t_ms,
                     "event": None if state == prev else
                     (f"enters the band" if state == "temperate"
                      else f"becomes {state}")})
        prev = state
    return {"star_msun": m, "t_ms": t_ms, "planet": planet, "rows": rows}


def narrate(seed_tuple, au):
    """-> lines. What happened to this world, in order."""
    h = follow(seed_tuple, au)
    p = h["planet"]
    out = [f"star {h['star_msun']:.2f} Msun, main sequence "
           f"{h['t_ms']:.0f} Gyr",
           f"world at {p['au']:.2f} AU, {p['mass_earths']:.2f} Earth "
           f"masses, {p['delivered_earth_oceans']:.0f} oceans delivered",
           f"elements: " + ",".join(e for e in CHNOPS
                                    if p["composition"].get(e, 0) > 1e-6)]
    for r in h["rows"]:
        if r["event"]:
            out.append(f"  {r['t']:>6.1f} Gyr  {r['event']}"
                       + ("  [post main sequence]" if r["post_ms"] else ""))
    warm = [r for r in h["rows"] if r["state"] == "temperate"]
    if warm:
        out.append(f"  temperate from {warm[0]['t']:.1f} to "
                   f"{warm[-1]['t']:.1f} Gyr "
                   f"({warm[-1]['t'] - warm[0]['t']:.1f} Gyr)")
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("living_worlds_can_be_followed", _follow)
    t("a_window_has_a_beginning_and_an_end", _window)
    return all(o[1] for o in out), out


_C = {}


def _live():
    if "l" not in _C:
        _C["l"] = living(24)
    return _C["l"]


def _follow():
    alive, d = _live()
    if not alive:
        return ("no world in this sample is alive, so there is nothing "
                "to follow; the census reports the commonest failure")
    res, w = alive[0]
    lines = narrate(res["seed"], w["au"])
    return " | ".join(lines[:3])


def _window():
    alive, _d = _live()
    if not alive:
        return "nothing alive in this sample"
    res, w = alive[0]
    h = follow(res["seed"], w["au"])
    warm = [r for r in h["rows"] if r["state"] == "temperate"]
    if not warm:
        raise ArithmeticError("a world the census called alive is never "
                              "temperate when followed -- the two "
                              "disagree")
    ends = warm[-1]["t"] < h["rows"][-1]["t"]
    return (f"the first living world is temperate from {warm[0]['t']:.1f} "
            f"to {warm[-1]['t']:.1f} Gyr and "
            + ("loses it before the run ends" if ends
               else "still has it when the star dies")
            + ". A window has a beginning and an end, and which one a "
              "world is in is not something a census total can say")


if __name__ == "__main__":
    alive, d = living(60)
    print(f"  {d['n_alive']} living worlds of {d['n_worlds']}\n")
    seen = set()
    for res, w in alive[:4]:
        k = (res["seed"], round(w["au"], 2))
        if k in seen:
            continue
        seen.add(k)
        for line in narrate(res["seed"], w["au"]):
            print("  " + line)
        print()
    ok, r = check()
    for n, o, dd in r:
        print(f"{'PASS' if o else 'FAIL'}  {n:36}{dd[:60]}")
    print("\nall:", ok)
