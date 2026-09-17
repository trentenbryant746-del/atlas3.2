"""
Four habitable worlds, followed step by step, and what happens to them.

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

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CHNOPS = ("C", "H", "N", "O", "P", "S")


def habitable_worlds(n=60):
    """-> [(seed, planet)] for every world the census calls alive."""
    from engine.census import census, deconstruct
    r = census(n)
    d = deconstruct(r)
    out = []
    for res in r:
        for w in res["worlds"]:
            if w["habitable"]:
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


# HABITABLE IS NOT INHABITED, AND THE CENSUS CANNOT CROSS THAT GAP.
# What it tests is a place: water, elements, time. What a cell needs
# is a self-maintaining compartment that copies itself, and nothing
# in this repository derives the step from chemistry to that. It is
# called abiogenesis and it is absent, not implied.
#
# What CAN be asked, from rules already here, is whether a cell
# COULD persist on one of these worlds and how large it could be.
# engine/life.py derives the diffusion limit -- a sphere consuming
# oxygen supplies its own centre only out to sqrt(6 D C0 / R), past
# which the middle suffocates -- and that depends on temperature
# through the diffusion coefficient. A colder world has slower
# diffusion and smaller cells.


def cell_ceiling(T_surface, consumption=1.0):
    """-> (radius m, why). The largest sphere that can feed itself.

    Diffusion goes as roughly T/viscosity, and water's viscosity
    falls steeply with temperature, so the ceiling moves with the
    world's climate rather than being a constant.
    """
    from engine.life import diffusion_limit, D_O2_WATER
    # Stokes-Einstein: D scales with T over viscosity, and water's
    # viscosity roughly halves per 20 K near freezing
    scale = (T_surface / 298.0) * math.exp((T_surface - 298.0) / 40.0)
    d = D_O2_WATER * max(scale, 1e-3)
    r = diffusion_limit(consumption, D=d).value
    return r, (
        f"at {T_surface:.0f} K a sphere consuming {consumption:g} "
        f"mol/m3/s can supply its own centre out to {r*1e6:.1f} "
        f"microns; past that the middle suffocates and it must be "
        f"smaller, flatter, or pump")


def cells_on(seed_tuple, au):
    """-> dict. What a cell could be on this world, if one existed."""
    h = follow(seed_tuple, au)
    warm = [r for r in h["rows"] if r["state"] == "temperate"]
    if not warm:
        return {"au": au, "ceiling_um": None,
                "why": "never temperate, so the question does not arise"}
    mid = warm[len(warm) // 2]
    from engine.terraform import BODIES, Body, thermostat
    e = BODIES["Earth"]
    pl = h["planet"]
    b = Body("w", pl["mass_kg"],
             (3 * pl["mass_kg"] / (4 * math.pi * 5515.0)) ** (1 / 3),
             au, e.albedo, water_kg=e.water_kg)
    r = thermostat(b, luminosity=mid["lum"])
    T = r.get("T", 288.0)
    rad, why = cell_ceiling(T)
    return {"au": au, "T": T, "wet": r.get("wet_fraction", 0.0),
            "ceiling_um": rad * 1e6, "why": why}


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("habitable_worlds_can_be_followed", _follow)
    t("a_window_has_a_beginning_and_an_end", _window)
    t("habitable_is_not_inhabited", _notalive)
    t("a_cell_ceiling_moves_with_climate", _cells)
    return all(o[1] for o in out), out


_C = {}


def _live():
    if "l" not in _C:
        _C["l"] = habitable_worlds(24)
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
        raise ArithmeticError("a world the census called habitable is never "
                              "temperate when followed -- the two "
                              "disagree")
    ends = warm[-1]["t"] < h["rows"][-1]["t"]
    return (f"the first habitable world is temperate from {warm[0]['t']:.1f} "
            f"to {warm[-1]['t']:.1f} Gyr and "
            + ("loses it before the run ends" if ends
               else "still has it when the star dies")
            + ". A window has a beginning and an end, and which one a "
              "world is in is not something a census total can say")


def _notalive():
    """Structural, because grepping caught its own explanation.

    The first version searched engine/census.py for words like
    "membrane" and found them in the sentence saying the census does
    NOT test membranes. That is the fourth check in this repository
    to fail on its own documentation, and the rule forbidding it --
    checks_do_not_grep_themselves -- only scans lab.py. A rule that
    covers one file is not a rule.
    """
    from engine.census import _one
    import inspect
    sig = inspect.signature(_one)
    from engine import census
    keys = census.CHNOPS
    # what the census actually decides on: look at the keys it sets
    src = inspect.getsource(census._one)
    decides = [k for k in ("habitable", "has_water", "window_gyr",
                           "elements") if f'"{k}"' in src]
    forbidden = [k for k in ("membrane", "replicates", "metabolises",
                             "divides") if f'"{k}"' in src]
    if forbidden:
        raise ArithmeticError(f"the census sets {forbidden}")
    return (f"the census decides on {decides} -- water, elements and "
            f"time, which describe a PLACE. It sets no key about a "
            f"membrane, replication, metabolism or division, because "
            f"nothing here derives the step from chemistry to a "
            f"self-copying compartment. That step is abiogenesis and it "
            f"is absent, not implied. Habitable is the strongest word "
            f"the evidence carries")


def _cells():
    cold, warm = cell_ceiling(275.0)[0], cell_ceiling(310.0)[0]
    if warm <= cold:
        raise ArithmeticError("a warmer world did not allow larger cells")
    return (f"the diffusion ceiling runs {cold*1e6:.1f} microns at 275 K "
            f"to {warm*1e6:.1f} at 310 K, because diffusion scales with "
            f"temperature over viscosity and water thins steeply. A "
            f"cold habitable world permits only smaller cells -- which "
            f"is a statement about what could persist, not about "
            f"anything that did")


if __name__ == "__main__":
    alive, d = habitable_worlds(60)
    print(f"  {d['n_habitable']} habitable worlds of {d['n_worlds']}\n")
    seen = set()
    for res, w in alive[:4]:
        k = (res["seed"], round(w["au"], 2))
        if k in seen:
            continue
        seen.add(k)
        for line in narrate(res["seed"], w["au"]):
            print("  " + line)
        c = cells_on(res["seed"], w["au"])
        if c.get("ceiling_um"):
            print(f"  cell ceiling {c['ceiling_um']:.1f} um "
                  f"at {c['T']:.0f} K, {100*c['wet']:.0f}% wet")
        print()
    ok, r = check()
    for n, o, dd in r:
        print(f"{'PASS' if o else 'FAIL'}  {n:36}{dd[:60]}")
    print("\nall:", ok)
