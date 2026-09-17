"""
Cells introduced to Earth, and the planet watched while they work.

Everything before this treated life as an outcome: does a world
permit it. This does the opposite. The cells exist -- at the size
engine/earthlab.py derives, between the closure floor and the
diffusion roof -- and the question is what they do to the planet
they are on.

THEY CHANGE THE AIR, AND THE AIR IS ALREADY WIRED TO THE CLIMATE.
Photosynthesis is CO2 + H2O -> CH2O + O2, one oxygen per carbon
fixed. That removes a greenhouse gas and adds an oxidant, and
engine/terraform.py already computes what an atmosphere does to a
surface. Nothing new connects them; the connection was there and
nothing had been put in to use it.

OXYGEN IS NOT PRODUCTION-LIMITED. A modern biosphere could make the
whole atmosphere's worth in about four thousand years. It is SINK-
limited: reduced iron and sulfur in crust and ocean swallow oxygen
as fast as it appears, and nothing accumulates until they are
spent. That is why a planet can photosynthesise for a very long
time and still look anoxic, and it is the shape of Earth's own
history -- oxygenic photosynthesis by about 3.5 billion years ago,
and free oxygen only at 2.4.

WHAT THIS GETS WRONG IS THE DELAY, AND IT IS LEFT WRONG. With a
modern productivity and an order-of-magnitude iron sink the model
fills the sink in 160,000 years where Earth took roughly 1.5
billion. Three to four orders. The rule is right in shape and the
inputs are not: early productivity was a fraction of modern, and
the sink is not only iron but the whole reduced crust and
everything volcanism keeps adding. Both are quantities this
repository does not derive, so they are named rather than tuned.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Measured, and every one labelled.
NPP_MODERN_KG_C_YR = 1e14      # net primary production, modern
REDUCED_SINK_KG = 3e20         # reduced iron available, order only
O2_PER_C = 32.0 / 12.0         # stoichiometry, exact
CH4_LIFETIME_ANOXIC_YR = 1e4   # methane survives without oxygen
CH4_LIFETIME_OXIC_YR = 10.0    # and does not, with it


def o2_production(npp_kg_c_yr=NPP_MODERN_KG_C_YR):
    """kg O2 per year. DERIVED from stoichiometry."""
    return npp_kg_c_yr * O2_PER_C


def sink_capacity(reduced_kg=REDUCED_SINK_KG):
    """kg O2 the crust can swallow. DERIVED: 4 Fe per O2."""
    return reduced_kg / 55.845 * 32.0 / 4.0


def atmosphere_mass(partial_pa, body):
    """kg of a gas at this partial pressure. DERIVED."""
    return partial_pa / body.gravity() * 4 * math.pi * body.radius ** 2


# AND THE AIR IS WIRED TO THE SURFACE ALREADY. Methane is one of
# the three gases in engine/radiative.py's band table, so once
# oxygen shortens its life the climate follows without anything
# being added to make it. Early Earth is thought to have carried
# 100 to 1,000 ppm of it against 1.8 today.
CH4_ANOXIC_PPM = 1000.0
CH4_OXIC_PPM = 1.8


def surface_with_methane(ppm, T_guess=288.0):
    """K. DERIVED through the existing radiative and climate rules."""
    from engine.terraform import BODIES, equilibrium_T, p_sat_water
    from engine.radiative import grey_equivalent_full
    e = BODIES["Earth"]
    P = 1.01325e5
    mix = {"CO2": 4.2e-4 * P, "H2O": 0.7 * p_sat_water(T_guess)}
    if ppm > 0:
        mix["CH4"] = ppm * 1e-6 * P
    tau = grey_equivalent_full(mix, T_guess, e.gravity(), P)
    return equilibrium_T(e) * (1.0 + 0.75 * tau) ** 0.25


def history(steps=14, t_max_gyr=3.0, productivity=1.0,
            reduced_kg=REDUCED_SINK_KG):
    """-> [rows]. Earth with cells on it, followed forward."""
    from engine.terraform import BODIES, thermostat, Body
    e = BODIES["Earth"]
    target = atmosphere_mass(0.21 * 1.01325e5, e)
    prod = o2_production(NPP_MODERN_KG_C_YR * productivity)
    cap = sink_capacity(reduced_kg)
    rows = []
    for i in range(steps):
        t = t_max_gyr * i / (steps - 1)
        made = prod * t * 1e9
        if made <= cap:
            free = 0.0
            state = "anoxic -- the crust is still swallowing it"
        else:
            free = min(made - cap, target)
            state = ("oxygenating" if free < target
                     else "oxygen saturated")
        frac = free / target if target else 0.0
        ch4_life = (CH4_LIFETIME_OXIC_YR if frac > 0.01
                    else CH4_LIFETIME_ANOXIC_YR)
        ppm = (CH4_OXIC_PPM if frac > 0.01
               else CH4_ANOXIC_PPM)
        rows.append({"t_gyr": t, "o2_fraction": frac, "state": state,
                     "ch4_lifetime_yr": ch4_life, "ch4_ppm": ppm,
                     "T_surface": surface_with_methane(ppm),
                     "sink_filled": min(made / cap, 1.0)})
    return rows


def first_oxygen(**kw):
    """-> Gyr when free oxygen first appears. DERIVED."""
    for r in history(steps=400, **kw):
        if r["o2_fraction"] > 0.0:
            return r["t_gyr"]
    return None


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("oxygen_is_sink_limited_not_production_limited", _sink)
    t("the_sink_delays_oxygen", _delay)
    t("oxygen_shortens_methanes_life", _ch4)
    t("the_delay_is_wrong_and_says_so", _wrong)
    t("cells_are_the_size_the_lab_derived", _size)
    t("life_cools_its_own_planet", _cool)
    return all(o[1] for o in out), out


def _sink():
    from engine.terraform import BODIES
    e = BODIES["Earth"]
    target = atmosphere_mass(0.21 * 1.01325e5, e)
    yrs = target / o2_production()
    cap = sink_capacity()
    if cap <= target:
        raise ArithmeticError("the sink is smaller than the atmosphere, "
                              "so nothing would be delayed")
    return (f"a modern biosphere makes Earth's whole oxygen atmosphere "
            f"in {yrs:,.0f} years, so production is not the constraint. "
            f"The reduced crust can swallow {cap/target:.0f} atmospheres "
            f"first, and does -- which is why a planet can "
            f"photosynthesise for ages and still read as anoxic")


def _delay():
    t = first_oxygen()
    if t is None or t <= 0:
        raise ArithmeticError("oxygen appears immediately; the sink is "
                              "not doing anything")
    rows = history()
    anox = [r for r in rows if r["o2_fraction"] == 0.0]
    return (f"free oxygen first appears at {t:.4f} Gyr, after "
            f"{len(anox)} of {len(rows)} sampled steps spent filling the "
            f"crust. The curve is a threshold, not a ramp: nothing, "
            f"then everything")


def _ch4():
    rows = history()
    before = rows[0]["ch4_lifetime_yr"]
    after = rows[-1]["ch4_lifetime_yr"]
    if after >= before:
        raise ArithmeticError("oxygen did not shorten methane's life")
    return (f"methane lasts {before:,.0f} years in an anoxic atmosphere "
            f"and {after:.0f} once oxygen is free -- {before/after:,.0f} "
            f"times shorter. A biosphere that makes oxygen therefore "
            f"DESTROYS a greenhouse gas, and cooling a planet is not "
            f"something life was asked to do")


def _wrong():
    t = first_oxygen()
    real = 1.1     # Gyr between oxygenic photosynthesis and free O2
    if abs(t - real) < 0.3:
        raise ArithmeticError("the delay now matches Earth's, so this "
                              "admission is stale and should be removed")
    return (f"the model puts first oxygen at {t:.4f} Gyr and Earth took "
            f"about {real:.1f} -- wrong by {real/max(t,1e-9):,.0f} times, "
            f"and left wrong. The SHAPE is right: sink first, then "
            f"accumulation. The inputs are not. Early productivity was a "
            f"small fraction of modern and the sink is not only iron but "
            f"the whole reduced crust plus whatever volcanism keeps "
            f"adding. Neither is derived here, so neither is tuned")


def _size():
    from engine.earthlab import size_window
    floor, roof, _why = size_window()
    if not floor < roof:
        raise ArithmeticError("no viable cell size, so nothing can be "
                              "introduced")
    return (f"the cells introduced here are {floor*1e6:.2f} to "
            f"{roof*1e6:.1f} microns, which is the window "
            f"engine/earthlab.py derives from autocatalytic closure "
            f"below and oxygen diffusion above. They were not sized to "
            f"fit this experiment")


def _cool():
    warm = surface_with_methane(CH4_ANOXIC_PPM)
    cold = surface_with_methane(CH4_OXIC_PPM)
    if cold >= warm:
        raise ArithmeticError("removing methane did not cool anything")
    return (f"an anoxic Earth at {CH4_ANOXIC_PPM:.0f} ppm methane sits "
            f"at {warm:.1f} K; once oxygen cuts methane to "
            f"{CH4_OXIC_PPM} ppm it sits at {cold:.1f} -- "
            f"{warm-cold:.1f} K colder. Nothing was added to connect "
            f"them: methane was already a band in "
            f"engine/radiative.py and the climate was already "
            f"downstream of the bands. A biosphere that makes oxygen "
            f"COOLS ITS OWN PLANET, which is not something it was "
            f"asked to do, and Earth's first glaciation follows its "
            f"first oxygen")


if __name__ == "__main__":
    print(f"  {'t Gyr':>7}{'sink':>7}{'O2':>7}{'CH4 ppm':>10}"
          f"{'T surf':>9}   state")
    prev = None
    for r in history():
        mark = ""
        if prev is not None and abs(r["T_surface"] - prev) > 0.5:
            mark = f"   <-- {r['T_surface']-prev:+.1f} K"
        prev = r["T_surface"]
        print(f"  {r['t_gyr']:>7.2f}{100*r['sink_filled']:>6.0f}%"
              f"{r['o2_fraction']:>7.2f}{r['ch4_ppm']:>10.1f}"
              f"{r['T_surface']:>9.1f}   {r['state'][:28]}{mark}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:46}{d[:52]}")
    print("\nall:", ok)
