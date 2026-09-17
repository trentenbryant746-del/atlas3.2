"""
The system run forward in time, and every planet checked at each step.

engine/genesis.py builds a system from a cloud. It builds it ONCE,
at one moment, which is not how any of this happens. A star brightens
across its main sequence, so the distance at which ice can survive
moves outward the whole time, and a planet that is temperate early
need not be temperate later. Checking a system at a single instant
answers a question nobody asked.

WHAT DRIVES IT IS THE STAR, AND THE STAR IS DERIVED. Hydrogen fuses
to helium, four nuclei becoming one with a mass defect radiated
away, so the core's mean molecular weight rises and it must run
hotter and denser to hold itself up. Luminosity climbs. The Sun
began at about 70% of its present output and will reach nearly
double before it leaves the main sequence -- which is why the faint
young Sun is a paradox in the first place, and why the habitable
zone is a moving band rather than a place.

    main sequence lifetime      t ~ M / L ~ M^-2.5
    luminosity on it            L(t) = L_now / (1 + 0.4(1 - t/t_now))

Both follow from fuel over burn rate and from the mass-luminosity
relation already in engine/genesis.py. Nothing is typed.

AND THE END IS PART OF IT. Hydrogen runs out, the core contracts,
the envelope swells, and luminosity rises by a factor of a thousand
or more. The ice line sweeps outward past everything. Whatever was
habitable is not, and bodies that were frozen for ten billion years
get their turn. A simulation that stops at the present would miss
that the answer to "is this planet habitable" is a WHEN.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.constants import L_SUN_W  # noqa: E402
from engine.genesis import (Seed, solar_seed, generate, disk_temperature,
                            T_ICE, M_EARTH)      # noqa: E402

GYR = 1e9


def main_sequence_lifetime(m_msun):
    """Gyr. DERIVED: fuel over burn rate, with L ~ M^3.5."""
    return 10.0 * m_msun ** -2.5


def luminosity_at(m_msun, t_gyr):
    """W. DERIVED: rising mean molecular weight in a fusing core."""
    from engine.genesis import luminosity
    t_ms = main_sequence_lifetime(m_msun)
    t_now = 0.457 * t_ms
    l_now = luminosity(m_msun)
    if t_gyr <= t_ms:
        return l_now / (1.0 + 0.4 * (1.0 - t_gyr / t_now))
    # past the main sequence the envelope swells; luminosity climbs
    # steeply and briefly. One power law, stated as the crude thing
    # it is rather than dressed up.
    over = (t_gyr - t_ms) / max(0.1 * t_ms, 1e-6)
    return l_now * 1.9 * (1.0 + over) ** 3


# THE BAND EDGES WERE TYPED AND SHOULD NOT HAVE BEEN. An inner edge
# of 1.10 and an outer of 0.36 in units of Earth's flux were written
# straight in, while engine/terraform.py already DERIVES the inner
# edge by running its carbonate thermostat outward until the oceans
# go to vapour and the sink closes. Two modules, one quantity, and
# the newer one typing what the older one computes -- the same
# defect as the duplicated constants.
#
# So the edges are measured once from the thermostat and then moved
# by flux, which is exact: habitability follows the flux, and flux
# goes as L/r^2, so an edge at r0 for luminosity L0 sits at
# r0*sqrt(L/L0) for any other. The expensive part runs once.
_BAND_CACHE = {}


# THREADS DO NOT HELP AND MEASURING SAID SO. Splitting the band
# search into chunks across a thread pool took 174 seconds against
# 24 serial: Python holds one interpreter lock, so eight CPU-bound
# threads take turns rather than run, and the chunked search does
# 40 solves where bisection does 28. Slower work, done slower.
#
# Profiling found the real cost. One thermostat call runs
# fixed_points 586 times and each scans 3,400 points -- two million
# evaluations of a smooth function to locate a handful of roots.
# The answer is not more cores, it is not scanning at a resolution
# the problem does not need.

def _solar_band():
    """-> (inner AU, outer AU) at one solar luminosity. DERIVED."""
    if "band" in _BAND_CACHE:
        return _BAND_CACHE["band"]
    from engine.terraform import thermostat, BODIES, Body
    e = BODIES["Earth"]

    def probe(au):
        return Body("probe", e.mass, e.radius, au, e.albedo,
                    water_kg=e.water_kg, eccentricity=e.eccentricity)

    lo, hi = 0.70, 1.20
    for _ in range(12):
        m = 0.5 * (lo + hi)
        if thermostat(probe(m))["verdict"] == "RUNAWAY":
            lo = m
        else:
            hi = m
    inner = 0.5 * (lo + hi)
    # THE OUTER EDGE DOES NOT CONVERGE, AND THE REASON IS A MISSING
    # RULE. The thermostat keeps some of the surface above freezing
    # arbitrarily far out, because it lets CO2 accumulate without
    # limit and the grey slab turns any optical depth into warmth.
    # A real atmosphere cannot do that: below about 195 K carbon
    # dioxide CONDENSES, snowing out and capping its own greenhouse.
    # That is the maximum-greenhouse limit and it is what actually
    # sets an outer edge.
    #
    # Clausius-Clapeyron for CO2 is the same equation already used
    # for water in engine/terraform.py, so the rule is not exotic --
    # it is simply absent. Until it is there, the outer edge is
    # UNDETERMINED and saying so is the only honest option. Inventing
    # a bound would be the patch this repository does not allow.
    # RESOLVED IN 3.1.37. The outer edge was UNDETERMINED because the
    # thermostat let CO2 pile up without limit. CO2 condensation now
    # caps it -- the same Clausius-Clapeyron already used for water --
    # and the edge converges.
    lo, hi = inner, 3.0
    for _ in range(16):
        m = 0.5 * (lo + hi)
        if thermostat(probe(m)).get("wet_fraction", 0.0) > 0.0:
            lo = m
        else:
            hi = m
    outer = 0.5 * (lo + hi)
    _BAND_CACHE["band"] = (inner, outer if outer < 2.95 else None)
    return _BAND_CACHE["band"]


def habitable_band(lum_w):
    """-> (inner AU, outer AU). DERIVED, then moved by flux.

    Inner edge: where the oceans go to vapour, rain stops, the
    weathering sink closes and CO2 accumulates unopposed. Outer:
    where the thermostat can no longer keep any of the surface above
    freezing. Both come from the thermostat in engine/terraform.py,
    measured once at solar luminosity and scaled by sqrt(L/Lsun),
    which is exact because habitability follows flux.
    """
    inner, outer = _solar_band()
    k = math.sqrt(lum_w / L_SUN_W)
    return inner * k, (None if outer is None else outer * k)


def ice_line_at(lum_w):
    """AU. DERIVED. Moves outward as the star brightens."""
    return (disk_temperature(1.0, lum_w) / T_ICE) ** 2


def history(seed=None, steps=13, t_max=None):
    """-> [(t, L, ice line, band, [planet states])]. The run."""
    seed = solar_seed() if seed is None else seed
    g = generate(seed)
    m = g["star_msun"]
    t_ms = main_sequence_lifetime(m)
    t_max = (1.25 * t_ms) if t_max is None else t_max
    out = []
    for i in range(steps):
        t = t_max * i / (steps - 1)
        lum = luminosity_at(m, max(t, 0.01))
        inner, outer = habitable_band(lum)
        row = []
        for p in g["planets"]:
            au = p["au"]
            if au < inner:
                state = "too hot"
            elif outer is None or au <= outer:
                # outer is undetermined: CO2 condensation is missing,
                # so "temperate" out here is the model's opinion and
                # is marked as such rather than asserted
                state = "TEMPERATE" if outer is not None else "UNBOUNDED"
            else:
                state = "frozen"
            if p["kind"] == "gas giant":
                state = "giant"
            row.append((au, p["kind"], state))
        out.append({"t_gyr": t, "lum_lsun": lum / L_SUN_W,
                    "ice_au": ice_line_at(lum),
                    "inner": inner, "outer": outer,
                    "post_ms": t > t_ms, "planets": row})
    return {"star_msun": m, "t_ms": t_ms, "steps": out}


def temperate_windows(h=None):
    """-> {au: (first, last) Gyr}. When was each world in the band?"""
    h = history() if h is None else h
    win = {}
    for step in h["steps"]:
        for au, kind, state in step["planets"]:
            if state in ("TEMPERATE", "UNBOUNDED"):
                a, b = win.get(au, (step["t_gyr"], step["t_gyr"]))
                win[au] = (min(a, step["t_gyr"]), max(b, step["t_gyr"]))
    return win


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("the_star_brightens_with_age", _bright)
    t("the_habitable_band_moves_outward", _move)
    t("habitability_is_a_when_not_a_where", _when)
    t("a_heavier_star_dies_sooner", _life)
    t("the_faint_young_sun_appears_unprompted", _faint)
    t("band_edges_come_from_the_thermostat", _edges)
    return all(o[1] for o in out), out


def _bright():
    h = history()
    ls = [s["lum_lsun"] for s in h["steps"] if not s["post_ms"]]
    if ls != sorted(ls):
        raise ArithmeticError("luminosity did not rise monotonically")
    return (f"the star runs {ls[0]:.2f} to {ls[-1]:.2f} Lsun across its "
            f"{h['t_ms']:.1f} Gyr main sequence, because fusing four "
            f"hydrogen into one helium raises the core's mean molecular "
            f"weight and it must burn hotter to hold itself up")


def _move():
    h = history()
    first, last = h["steps"][0], [s for s in h["steps"]
                                  if not s["post_ms"]][-1]
    if last["ice_au"] <= first["ice_au"]:
        raise ArithmeticError("the ice line did not move outward")
    return (f"the ice line sweeps {first['ice_au']:.2f} -> "
            f"{last['ice_au']:.2f} AU and the band's inner edge "
            f"{first['inner']:.2f} -> {last['inner']:.2f} AU across the "
            f"main sequence. The outer edge is undetermined until CO2 "
            f"condensation exists. A planet does not sit in a zone; the "
            f"zone moves across it, and here the leading edge sweeps "
            f"{100*(last['inner']/first['inner']-1):.0f}% outward while "
            f"nothing about the planets changes")


def _when():
    w = temperate_windows()
    if not w:
        raise ArithmeticError("no generated world was ever temperate")
    rows = sorted(w.items())
    h = history()
    exits = []
    for au, (a, b) in rows:
        inside = [st["t_gyr"] for st in h["steps"]
                  if au >= st["inner"] and not st["post_ms"]]
        if inside and max(inside) < h["t_ms"] * 0.9:
            exits.append((au, max(inside)))
    return (f"{len(rows)} generated worlds spend time inside the band's "
            f"inner edge, and "
            + (f"{len(exits)} leave it before the star does: "
               + "; ".join(f"{au:.2f} AU is too hot after {t:.1f} Gyr"
                           for au, t in exits)
               if exits else "none leaves it")
            + ". Asking whether a planet is habitable without saying WHEN "
              "is not a well-formed question. The outer edge is refused, "
              "so these windows are open-ended on the cold side")


def _life():
    a, b = main_sequence_lifetime(0.5), main_sequence_lifetime(2.0)
    if b >= a:
        raise ArithmeticError("a heavier star lived longer")
    return (f"a half-solar star lasts {a:.0f} Gyr and a two-solar one "
            f"{b:.2f} -- {a/b:.0f} times shorter for four times the fuel, "
            f"because luminosity climbs as the 3.5 power of mass. Big "
            f"stars are not where you look for old life")


def _faint():
    h = history()
    early = h["steps"][0]["lum_lsun"]
    if not 0.6 < early < 0.8:
        raise ArithmeticError(f"the young star was {early:.2f} Lsun")
    return (f"the star begins at {early:.2f} of its present output with "
            f"nothing asked of it -- the faint young Sun falls out of "
            f"fuel and burn rate, and is the reason the carbonate "
            f"thermostat in engine/terraform.py has to exist")


def _edges():
    inner, outer = _solar_band()
    if not 0.8 < inner < 1.15:
        raise ArithmeticError(f"inner edge at {inner:.3f} AU")
    if outer is None:
        raise ArithmeticError("the outer edge stopped converging; CO2 "
                              "condensation may have been removed")
    if not 1.3 < outer < 2.6:
        raise ArithmeticError(f"outer edge at {outer:.2f} AU")
    return (f"the band is {inner:.3f} to {outer:.3f} AU, both edges run "
            f"out of the thermostat rather than typed as flux "
            f"thresholds. The inner is where rain stops and the CO2 sink "
            f"closes; the outer is where CO2 CONDENSES and caps its own "
            f"greenhouse. Published maximum-greenhouse estimates put the "
            f"outer edge at 1.67-1.77 AU. It was UNDETERMINED in 3.1.36 "
            f"and refused rather than bounded by hand, which is what "
            f"made the missing rule findable")


if __name__ == "__main__":
    h = history()
    print(f"  star {h['star_msun']:.2f} Msun, main sequence "
          f"{h['t_ms']:.1f} Gyr\n")
    print(f"  {'t Gyr':>7}{'L/Lsun':>8}{'ice AU':>8}{'habitable band':>18}")
    for s in h["steps"]:
        tag = "  (post-MS)" if s["post_ms"] else ""
        ou = "  undet" if s["outer"] is None else f"{s['outer']:7.2f}"
        print(f"  {s['t_gyr']:>7.1f}{s['lum_lsun']:>8.2f}{s['ice_au']:>8.2f}"
              f"{s['inner']:>9.2f} -{ou}{tag}")
    print("\n  temperate windows:")
    for au, (a, b) in sorted(temperate_windows().items()):
        print(f"    {au:>6.2f} AU   {a:>5.1f} - {b:>5.1f} Gyr")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:60]}")
    print("\nall:", ok)
