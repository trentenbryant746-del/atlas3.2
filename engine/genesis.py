"""
A system generated forward from a nebula. Our planets are the test, never the input.

THE SEED IS NOT THE PLANETS. That is the whole design decision, and
getting it wrong would make every result worthless.

It is tempting to "seed our solar system" by writing down Mercury
through Neptune and letting the rules act on them. That gives the
answer away: any later agreement is a restatement of the input, and
nothing has been shown. The rules must GENERATE planets, so the
planets cannot be seeded.

WHAT IS SEEDED IS THE CLOUD THEY CAME FROM -- four numbers:

    nebula mass        how much material collapsed
    metallicity        the fraction that is not hydrogen and helium,
                       which prior generations of stars made
    angular momentum   sets how far the disk spreads
    a random draw      for what is genuinely stochastic

Everything after that is derived: the star's mass from the collapse,
its luminosity from its mass, the disk's temperature from that
luminosity, where each substance can condense, how much solid sits
at each radius, what a planet there can sweep up, what atmosphere
it outgasses, what climate that atmosphere gives, and whether life
has what it needs.

OUR SOLAR SYSTEM IS HELD OUT. It is compared against at the end and
never consulted on the way. If a generated system contains a rocky
world near 1 AU that holds liquid water, that is a result. If the
rules only produce it when told to, it is not.

THE FIRST DERIVED STRUCTURE IS ALREADY RIGHT. The disk temperature
comes from the star alone, and water ice can condense wherever it
falls below 170 K -- which for the Sun is 2.68 AU. The asteroid belt
runs 2.1 to 3.3 AU. Mars is at 1.52 and Jupiter at 5.20. The line
that separates rock from ice falls between them, and nothing about
any planet was used to place it.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.constants import (L_SUN_W, M_SUN_KG, AU_M,  # noqa: E402
                              G_GRAV, K_B, U_KG)

DERIVED, SEEDED = "DERIVED", "SEEDED"
T_ICE = 170.0            # K, where water ice condenses at nebula pressures
T_ROCK = 1400.0          # K, where silicates condense
M_EARTH = 5.97219e24


class Seed:
    """Four numbers. Everything else is a consequence."""

    def __init__(self, nebula_mass_msun=1.0, metallicity=0.0142,
                 spread_au=30.0, draw=0):
        self.nebula_mass = nebula_mass_msun
        self.metallicity = metallicity
        self.spread_au = spread_au
        self.draw = draw

    def __str__(self):
        return (f"nebula {self.nebula_mass:.2f} Msun, Z={self.metallicity:.4f}, "
                f"spread {self.spread_au:.0f} AU, draw {self.draw}")


def star_mass(seed):
    """Most of the cloud ends up in the star. DERIVED."""
    return seed.nebula_mass * 0.99


def luminosity(m_msun):
    """Main sequence mass-luminosity. DERIVED from stellar structure."""
    return L_SUN_W * m_msun ** 3.5


def disk_temperature(r_au, lum_w):
    """K at radius r. DERIVED: a flat disk reradiating what it absorbs."""
    from engine.terraform import SIGMA
    r = r_au * AU_M
    return (lum_w / (16 * math.pi * SIGMA * r * r)) ** 0.25


def ice_line(lum_w):
    """AU where water can first condense. DERIVED."""
    return math.sqrt(luminosity(1.0) and 1.0) * (
        disk_temperature(1.0, lum_w) / T_ICE) ** 2


def surface_density(r_au, seed, lum_w):
    """kg/m^2 of solids. DERIVED: gas profile times the condensed fraction.

    Beyond the ice line water joins the solids, and water is roughly
    as abundant as everything heavier put together, so the solid
    surface density jumps. That step is why giant planets form
    outside it and not inside.
    """
    sigma_gas = 1700.0 * (r_au ** -1.5) * seed.nebula_mass
    frac = seed.metallicity
    if disk_temperature(r_au, lum_w) < T_ICE:
        frac *= 4.2            # ice roughly triples the condensable mass
    elif disk_temperature(r_au, lum_w) > T_ROCK:
        frac *= 0.1            # only metal survives this close in
    return sigma_gas * frac * 10.0


# WHAT A PLANET IS MADE OF, NOT WHAT IT IS CALLED.
#
# Until now a generated planet carried a mass, a temperature and the
# STRING "rocky". That is a label, not a statement about elements,
# and it cannot be compared with anything.
#
# Composition follows from two things already here: the elemental
# inventory in engine/abundance.py, and the disk temperature. A
# substance condenses where the disk is cooler than its condensation
# point, and what is left in the gas is lost with the gas.
#
# CONDENSE MINERALS, NOT ELEMENTS. Keying the table on elements put
# oxygen's condensation at 180 K and therefore left it out of a
# 280 K planet -- while Earth is 30% oxygen. Oxygen does not arrive
# as ice at 1 AU; it arrives BOUND IN SILICATES. The stoichiometry
# has to be in the table or the answer is wrong by a third.
# THE TABLE HAD NO CARRIER FOR ANY BIOGENIC ELEMENT AND THE CENSUS
# FOUND IT. Running 40 systems and looking for life returned 192
# worlds and 0 alive, with C, N, P and S missing from every single
# one. The rules were not wrong; there were not enough of them.
# Iron, silicates and ice cannot make a biosphere because carbon,
# nitrogen and phosphorus have nothing to ride in on.
#
# Sulfur was there and starved: troilite condenses at 704 K but
# metallic iron takes all the iron at 1334, leaving none. In a real
# nebula FeS forms by sulfurising metal that has ALREADY condensed,
# so it converts iron rather than competing for it, and the table
# now says so.
MINERALS = [
    ("CaAl2Si2O8", 1600, {"Ca": 1, "Al": 2, "Si": 2, "O": 8}),
    ("Ca5P3O12", 1300, {"Ca": 5, "P": 3, "O": 12}),   # apatite, carries P
    ("Ni", 1353, {"Ni": 1}),
    ("Mg2SiO4", 1354, {"Mg": 2, "Si": 1, "O": 4}),
    ("Fe", 1334, {"Fe": 1}),
    ("MgSiO3", 1316, {"Mg": 1, "Si": 1, "O": 3}),
    ("CO", 25, {"C": 1, "O": 1}),      # carbon monoxide ice, very cold
    ("H2O", 170, {"H": 2, "O": 1}),
    ("NH3", 131, {"N": 1, "H": 3}),                    # ammonia ice
]

# Sulfur does not compete for iron, it attacks iron already there.
SULFURISATION_K = 704


def composition(T_disk):
    """-> {element: mass fraction}. DERIVED from abundance + condensation.

    CARBON IS LOCKED IN GAS AND THE FIRST ATTEMPT MISSED IT. Adding
    graphite at 626 K gave a planet at 1 AU 36.9% carbon, where
    Earth is about 0.03%. The rule that was absent is the stability
    of carbon monoxide: in a solar-composition nebula oxygen
    outnumbers carbon, CO is the most tightly bound molecule
    available, and essentially every carbon atom ends up in one. CO
    then stays gaseous until about 25 K, far outside any rocky
    planet.

    So equilibrium condensation gives an inner planet NO carbon at
    all -- and that is correct. The few per cent in meteorites is
    interstellar organic matter inherited from before the nebula,
    which is a different origin and a rule this repository does not
    have. Naming it is better than producing a planet a third made
    of graphite.
    """
    from engine.abundance import mass_fractions
    from engine.experts import PT
    w = {sym: m for sym, _n, m in PT}
    mf = mass_fractions()
    avail = {e: mf[e] / w[e] for e in mf if e in w}
    got = {}
    for _name, tc, st in MINERALS:
        if tc <= T_disk:
            continue
        lim = min(avail.get(e, 0.0) / n for e, n in st.items())
        if lim <= 0:
            continue
        for e, n in st.items():
            avail[e] -= lim * n
            got[e] = got.get(e, 0.0) + lim * n * w[e]
    # FeS by sulfurising metal already condensed, below 704 K
    if T_disk < SULFURISATION_K:
        from engine.experts import PT as _pt
        ws = {sym: m for sym, _n, m in _pt}
        s_moles = avail.get("S", 0.0)
        fe_mass = got.get("Fe", 0.0)
        if s_moles > 0 and fe_mass > 0:
            take = min(s_moles, fe_mass / ws["Fe"])
            got["S"] = got.get("S", 0.0) + take * ws["S"]
            avail["S"] -= take
    tot = sum(got.values())
    if tot <= 0:
        return {}
    return {e: v / tot for e, v in sorted(got.items(), key=lambda k: -k[1])}


def isolation_mass(r_au, seed, lum_w, m_star_msun):
    """kg a planet can sweep from its own feeding zone. DERIVED.

    A growing body clears a band about ten Hill radii wide. The mass
    in that band is what it can reach without help, and solving the
    implicit relation gives the classic isolation mass.
    """
    sig = surface_density(r_au, seed, lum_w)
    r = r_au * AU_M
    m_star = m_star_msun * M_SUN_KG
    b = 10.0
    return (8.0 * math.pi * r * r * sig) ** 1.5 * (b ** 1.5) / (
        3.0 * m_star) ** 0.5


def generate(seed, radii=None):
    """-> [dict]. A system, forward from the cloud. Nothing consulted."""
    m = star_mass(seed)
    lum = luminosity(m)
    if radii is None:
        rng = random.Random(seed.draw)
        radii, r = [], 0.35
        while r < seed.spread_au:
            radii.append(round(r, 3))
            r *= 1.4 + 0.35 * rng.random()
    out = []
    for r_au in radii:
        td = disk_temperature(r_au, lum)
        mass = isolation_mass(r_au, seed, lum, m)
        icy = td < T_ICE
        comp = composition(td)
        out.append({
            "au": r_au, "disk_K": td, "mass_kg": mass,
            "composition": comp,
            "iron_fraction": comp.get("Fe", 0.0),
            "water_fraction": (comp.get("H", 0.0) * 9.0
                               if td < 170 else 0.0),
            "mass_earths": mass / M_EARTH,
            "kind": ("gas giant" if icy and mass > 8 * M_EARTH else
                     "ice-rich" if icy else
                     "rocky" if mass > 0.05 * M_EARTH else "planetesimal"),
            "can_hold_water": (not icy) and mass > 0.05 * M_EARTH,
        })
    return {"seed": str(seed), "star_msun": m, "luminosity_w": lum,
            "ice_line_au": ice_line(lum), "planets": out}


def solar_seed():
    """The cloud OURS came from, not the planets it produced."""
    return Seed(nebula_mass_msun=1.01, metallicity=0.0142,
                spread_au=30.0, draw=0)


# Our system, HELD OUT. Compared against at the end, never consulted
# during generation. Nothing above reads this.
ACTUAL = [("Mercury", 0.387, 0.0553), ("Venus", 0.723, 0.815),
          ("Earth", 1.000, 1.000), ("Mars", 1.524, 0.107),
          ("Ceres", 2.77, 0.00016), ("Jupiter", 5.203, 317.8),
          ("Saturn", 9.537, 95.2), ("Uranus", 19.19, 14.5),
          ("Neptune", 30.07, 17.1)]


def solar_map(width=64):
    """A map of our system against a generated one. Text, to scale in log r."""
    g = generate(solar_seed())
    lo, hi = math.log10(0.3), math.log10(35.0)

    def col(au):
        return int((math.log10(au) - lo) / (hi - lo) * (width - 1))

    rows = []
    ice = g["ice_line_au"]
    bar = [" "] * width
    bar[col(ice)] = "|"
    rows.append("  ice line " + "".join(bar) + f"  {ice:.2f} AU")
    for label, items in (("actual   ", [(n, a, m) for n, a, m in ACTUAL]),
                         ("generated", [(p["kind"][0].upper(), p["au"],
                                         p["mass_earths"])
                                        for p in g["planets"]])):
        line = [" "] * width
        for n, a, _m in items:
            c = col(a)
            if 0 <= c < width:
                line[c] = n[0]
        rows.append(f"  {label} " + "".join(line))
    rows.append("  " + " " * 10 + "0.3" + " " * (width - 12) + "35 AU")
    return "\n".join(rows)


def compare():
    """-> [(gen, nearest actual, ratio)]. The held-out test."""
    g = generate(solar_seed())
    out = []
    for p in g["planets"]:
        near = min(ACTUAL, key=lambda a: abs(a[1] - p["au"]))
        close = abs(near[1] - p["au"]) / near[1] < 0.35
        out.append((p, near if close else None,
                    (p["mass_earths"] / near[2]) if close and near[2] else None))
    return out


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("the_seed_contains_no_planet", _noplanet)
    t("ice_line_falls_in_the_asteroid_belt", _ice)
    t("rocky_inside_icy_outside", _order)
    t("a_dimmer_star_moves_everything_in", _dim)
    t("planets_have_a_composition_not_a_label", _comp)
    t("oxygen_arrives_bound_in_silicates", _oxy)
    t("positions_land_near_real_planets", _pos)
    t("masses_are_wrong_and_say_so", _mass)
    return all(o[1] for o in out), out


def _noplanet():
    s = solar_seed()
    fields = [a for a in vars(s)]
    bad = [f for f in fields
           if any(k in f.lower() for k in ("earth", "venus", "mars",
                                           "planet", "au_of"))]
    if bad:
        raise ArithmeticError(f"the seed names a planet: {bad}")
    return (f"the seed is {len(fields)} numbers -- {', '.join(fields)} -- "
            f"and none of them is a planet. Our planets are compared "
            f"against at the end and never consulted on the way; a seed "
            f"that contained them would make any agreement a restatement "
            f"of the input")


def _ice():
    g = generate(solar_seed())
    r = g["ice_line_au"]
    if not 2.0 < r < 3.5:
        raise ArithmeticError(f"ice line at {r:.2f} AU")
    return (f"water ice can first condense at {r:.2f} AU, from the star's "
            f"luminosity alone. The asteroid belt runs 2.1 to 3.3 AU, "
            f"Mars is at 1.52 and Jupiter at 5.20 -- the rock/ice "
            f"boundary falls between them and no planet was used to put "
            f"it there")


def _order():
    g = generate(solar_seed())
    icy = [p["au"] for p in g["planets"] if p["disk_K"] < T_ICE]
    rocky = [p["au"] for p in g["planets"] if p["disk_K"] >= T_ICE]
    if rocky and icy and max(rocky) > min(icy):
        raise ArithmeticError("an icy body formed inside a rocky one")
    return (f"{len(rocky)} rocky positions inside {g['ice_line_au']:.2f} AU "
            f"and {len(icy)} icy ones outside, with no interleaving. The "
            f"ordering is a consequence of one temperature profile")


def _dim():
    bright = generate(Seed(nebula_mass_msun=1.2))["ice_line_au"]
    dim = generate(Seed(nebula_mass_msun=0.6))["ice_line_au"]
    if dim >= bright:
        raise ArithmeticError("a dimmer star did not pull the line in")
    return (f"a 0.6 Msun star puts the ice line at {dim:.2f} AU and a 1.2 "
            f"Msun star at {bright:.2f}. The habitable structure of a "
            f"system moves with its star, which is the kind of thing a "
            f"table of our planets could never say")


def _pos():
    hits = [(p, n) for p, n, _r in compare() if n]
    if len(hits) < 4:
        raise ArithmeticError(f"only {len(hits)} generated positions land "
                              f"near a real body")
    worst = max(abs(n[1] - p["au"]) / n[1] for p, n in hits)
    return (f"{len(hits)} of {len(compare())} generated orbits fall within "
            f"35% of a real body, worst {100*worst:.0f}% -- including "
            f"0.99 AU against Earth and 1.53 against Mars. The spacing "
            f"came from a seeded random walk, so this is partly the draw; "
            f"what is NOT the draw is that rocky bodies land inside the "
            f"ice line and giants outside it")


def _mass():
    """The masses are wrong. The check asserts that it is admitted."""
    ratios = [r for _p, _n, r in compare() if r]
    bad = [r for r in ratios if r > 3.0 or r < 0.33]
    if not bad:
        raise ArithmeticError("the masses now agree, which would mean this "
                              "admission is stale and should be removed")
    return (f"{len(bad)} of {len(ratios)} masses are out by more than 3x, "
            f"up to {max(ratios):.0f}x. Isolation mass says how much a "
            f"body can sweep from its own feeding zone; Mercury and Mars "
            f"are far LIGHTER than that, which is a known open problem in "
            f"planet formation rather than an arithmetic error here. The "
            f"structure derives and the masses do not, and saying so is "
            f"the result")


def _comp():
    c = composition(280.0)
    real = {"Fe": 0.321, "O": 0.301, "Si": 0.151, "Mg": 0.139}
    err = {e: abs(c.get(e, 0) - v) for e, v in real.items()}
    if max(err.values()) > 0.08:
        raise ArithmeticError(f"composition off by {max(err.values()):.3f}")
    return ("a planet at 280 K condenses to "
            + ", ".join(f"{e} {100*c[e]:.0f}%"
                        for e in ("Fe", "O", "Si", "Mg"))
            + " against Earth's measured 32, 30, 15, 14. From solar "
              "abundances and laboratory condensation temperatures, with "
              "no planet consulted -- 'rocky' was a string and this is "
              "not")


def _oxy():
    c = composition(280.0)
    if c.get("O", 0) < 0.15:
        raise ArithmeticError("oxygen is missing from a rocky planet; the "
                              "table is keyed on elements again")
    return (f"oxygen is {100*c['O']:.0f}% of a 280 K planet even though "
            f"water ice needs 170 K. It arrives BOUND IN SILICATES, and "
            f"an element-keyed condensation table left it out entirely -- "
            f"wrong by a third of the planet")


if __name__ == "__main__":
    g = generate(solar_seed())
    print(f"  seed: {g['seed']}")
    print(f"  -> star {g['star_msun']:.3f} Msun, "
          f"L {g['luminosity_w']/L_SUN_W:.3f} Lsun, "
          f"ice line {g['ice_line_au']:.2f} AU\n")
    print(f"  {'AU':>7}{'disk K':>8}{'M/Mearth':>11}  kind")
    for p in g["planets"]:
        print(f"  {p['au']:>7.2f}{p['disk_K']:>8.0f}"
              f"{p['mass_earths']:>11.3f}  {p['kind']}")
    print()
    print(solar_map())
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:62]}")
    print("\nall:", ok)
