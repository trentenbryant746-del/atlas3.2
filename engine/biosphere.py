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
# CO2 + H2O -> CH2O + O2, so ONE O2 leaves per carbon fixed. The
# mass ratio is two oxygens over one carbon and the weights come
# from engine/atoms.py, not from 32/12 typed in again here.
from engine.atoms import WEIGHT as _W
FE_WEIGHT = 55.845       # g/mol, iron
O2_PER_C = 2.0 * _W["O"] / _W["C"]
CH4_LIFETIME_ANOXIC_YR = 1e4   # methane survives without oxygen
CH4_LIFETIME_OXIC_YR = 10.0    # and does not, with it


def o2_production(npp_kg_c_yr=NPP_MODERN_KG_C_YR):
    """kg O2 per year. DERIVED from stoichiometry."""
    return npp_kg_c_yr * O2_PER_C


def sink_capacity(reduced_kg=REDUCED_SINK_KG):
    """kg O2 the crust can swallow. DERIVED: 4 Fe + 3 O2 -> 2 Fe2O3,
    so three O2 per four iron, weights from engine/atoms.py."""
    return reduced_kg / FE_WEIGHT * (3.0 / 4.0) * 2.0 * _W["O"]


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


# FROM ONE CELL TO MANY, AND WHAT STOPS IT.
#
# Oxygen is the usual answer and it is not the whole one. Tissue
# thickness without a transport system is the same diffusion limit
# engine/life.py derives for a single cell, and it goes as the
# square root of oxygen -- so even FIVE TIMES present atmospheric
# oxygen buys only 120 microns. A body cannot be made thick by
# adding oxygen to the air.
#
#   0.5% of present O2      3.8 um of tissue
#   100%                   54.8 um
#   500%                  119.5 um
#
# That is a sheet a few cells deep, and it is what the earliest
# multicellular fossils look like: fronds and quilts, thin in one
# dimension. Getting thicker needs CIRCULATION -- a pump moving
# oxygen to tissue rather than tissue waiting for it -- and that is
# a different kind of thing from an atmosphere.
#
# Above that, the square-cube law takes over: engine/life.py puts a
# land skeleton's ceiling at 173 m before its own weight reaches
# bone's compressive strength.
AEROBIC_MIN_FRACTION = 0.01     # of present O2, for aerobic metabolism


def tissue_thickness(o2_fraction_of_present, consumption=1.0):
    """m of tissue suppliable without circulation. DERIVED."""
    from engine.life import diffusion_limit, D_O2_WATER, C_O2_WATER
    c0 = C_O2_WATER * max(o2_fraction_of_present, 1e-9)
    return diffusion_limit(consumption, D=D_O2_WATER, C0=c0).value


# IS CIRCULATION DERIVABLE, OR JUST ASSERTED? It is derivable, and
# the answer is that it is CHEAP -- which is why calling it a
# missing organ overstated the difficulty.
#
# A pump moves fluid against viscous resistance. Poiseuille gives
# the pressure a flow costs, Q = pi r^4 dP / (8 eta L), and the
# power is Q dP. The flow itself is set by demand: blood carries
# about 4e6 joules of oxygen per cubic metre, and engine/life.py's
# Kleiber relation says how many joules a body of a given mass
# needs.
#
#      1 ug     0.60% of the metabolic budget
#      1 g      0.11%
#      1 kg     0.02%
#     70 kg     0.01%     (a real heart is 1-2%, with a branching
#                          tree this single-vessel model omits)
#
# Pumping is affordable at every size and gets CHEAPER as bodies
# grow, because demand rises as mass^0.75 while a wider vessel's
# resistance falls as r^-4. So circulation is not a barrier that
# had to be crossed; it is the cheap answer to a problem that
# becomes unavoidable at about 55 microns, where diffusion stops
# reaching. Below that a pump is pure cost. Above it there is no
# alternative.
#
# WHAT IS NOT DERIVED IS THE ORGAN. That a pump pays for itself
# does not say how a lineage builds one, and this repository has no
# rule for that. The honest statement is narrower than "circulation
# is derivable": what is derivable is that nothing forbids it and
# the economics favour it at exactly the size diffusion fails.
BLOOD_VISCOSITY = 3.5e-3       # Pa s, measured
BLOOD_O2_J_PER_M3 = 0.2e6 * 20.0


def pump_cost(mass_kg, vessel_ratio=0.01):
    """-> (watts, fraction of budget). DERIVED from Poiseuille."""
    from engine.life import kleiber
    k = kleiber(mass_kg)
    bmr = float(k.value if hasattr(k, "value") else k)
    length = (mass_kg / 1000.0) ** (1.0 / 3.0)
    radius = length * vessel_ratio
    flow = bmr / BLOOD_O2_J_PER_M3
    dp = 8 * BLOOD_VISCOSITY * length * flow / (math.pi * radius ** 4)
    power = flow * dp
    return power, (power / bmr if bmr else float("inf"))


def circulation_pays(mass_kg):
    """-> (bool, why). Does the pump cost less than it enables?"""
    p, frac = pump_cost(mass_kg)
    return frac < 0.1, (
        f"a {mass_kg:g} kg body spends {100*frac:.2f}% of its metabolic "
        f"budget on pumping ({p:.2e} W). Affordable, and it gets "
        f"cheaper with size because demand rises as mass^0.75 while a "
        f"wider vessel's resistance falls as r^-4")


def body_gates(o2_fraction, circulation=False):
    """-> [(name, OPEN/SHUT, why)]. What a body can be at this O2."""
    from engine.life import square_cube_limit
    out = []
    aer = o2_fraction >= AEROBIC_MIN_FRACTION
    out.append(("aerobic", "OPEN" if aer else "SHUT",
                f"oxygen at {100*o2_fraction:.1f}% of present against the "
                f"{100*AEROBIC_MIN_FRACTION:.0f}% aerobic metabolism "
                f"needs -- below it a cell ferments, which yields about "
                f"a sixteenth as much and cannot pay for a body"))
    th = tissue_thickness(o2_fraction)
    out.append(("thin body", "OPEN" if th > 1e-5 else "SHUT",
                f"diffusion supplies {th*1e6:.1f} microns of tissue, so a "
                f"sheet a few cells deep. This is what the earliest "
                f"multicellular fossils are"))
    out.append(("thick body", "OPEN" if circulation else "SHUT",
                f"tissue thickness goes as the SQUARE ROOT of oxygen, so "
                f"five times present air buys 120 microns. A body cannot "
                f"be made thick by enriching the atmosphere; it needs a "
                f"pump, and circulation is "
                + ("present" if circulation else "ABSENT here")))
    h = float(square_cube_limit().value)
    out.append(("large on land", "OPEN" if circulation else "SHUT",
                f"once thick bodies exist the square-cube law binds "
                f"instead: {h:.0f} m before a skeleton crushes itself at "
                f"1% bone cross-section"))
    return out


# LAND. Four things change when a body leaves water, and only one
# of them is a planetary condition.
#
# UV: ozone is made FROM oxygen, so land needs oxygen twice -- to
# breathe and to build the shield. The Chapman steady state puts
# the column near sqrt(O2), and Beer-Lambert through ozone's
# Hartley band does the rest. It saturates fast: at 0.5% of present
# oxygen two parts in a thousand still reach the ground, and at 5%
# it is four parts in a billion. The shield is not a hard gate.
#
# DESICCATION: air at 288 K and half saturation pulls with 850 Pa
# against a body that is wet inside. A barrier is required.
#
# SUPPORT: buoyancy is gone and the skeleton carries everything.
# engine/life.py caps a land skeleton at 173 m.
#
# GAS: air holds about thirty times more oxygen per volume than
# water, so breathing gets EASIER. It is the one thing land makes
# simpler.
#
# AND THE PATTERN REPEATS. The planetary gate opens; the shut ones
# are a skin and a skeleton. That is the third time -- thick bodies
# needed a pump, land needs a cuticle and bones, and none of them
# is something a planet supplies.
OZONE_PRESENT_DU = 300.0
O3_CROSS_SECTION_CM2 = 1.1e-17
DU_TO_MOLECULES_CM2 = 2.687e16


def ozone_column(o2_fraction_of_present):
    """Dobson units. DERIVED: Chapman steady state goes as sqrt(O2)."""
    return OZONE_PRESENT_DU * math.sqrt(max(o2_fraction_of_present, 0.0))


def uv_transmitted(o2_fraction_of_present):
    """Fraction of damaging UV reaching the ground. DERIVED."""
    n = ozone_column(o2_fraction_of_present) * DU_TO_MOLECULES_CM2
    return math.exp(-n * O3_CROSS_SECTION_CM2)


def land_gates(o2_fraction, barrier=False, skeleton=False):
    """-> [(name, OPEN/SHUT, why)]. What leaving water requires."""
    from engine.terraform import p_sat_water
    from engine.life import square_cube_limit
    out = []
    uv = uv_transmitted(o2_fraction)
    out.append(("uv shield", "OPEN" if uv < 1e-6 else "SHUT",
                f"ozone {ozone_column(o2_fraction):.0f} DU passes "
                f"{uv:.1e} of the damaging band. Made from oxygen, so "
                f"land needs oxygen twice -- and it saturates fast"))
    deficit = 0.5 * p_sat_water(288.0)
    out.append(("water retention", "OPEN" if barrier else "SHUT",
                f"air at half saturation pulls {deficit:.0f} Pa against a "
                f"body wet inside; a cuticle or skin is "
                + ("present" if barrier else "ABSENT")))
    h = float(square_cube_limit().value)
    out.append(("support", "OPEN" if skeleton else "SHUT",
                f"buoyancy is gone and the skeleton carries everything, "
                f"up to {h:.0f} m; a skeleton is "
                + ("present" if skeleton else "ABSENT")))
    out.append(("gas exchange", "OPEN",
                "air holds about thirty times more oxygen per volume "
                "than water, so breathing is the one thing land makes "
                "easier"))
    return out


def prime_earth(steps=14):
    """Earth with every condition set as favourably as the rules allow."""
    return history(steps=steps, t_max_gyr=1.0, productivity=1.0,
                   reduced_kg=REDUCED_SINK_KG * 0.1)


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
    t("oxygen_alone_cannot_thicken_a_body", _thick)
    t("prime_earth_reaches_animals_but_not_by_air", _prime)
    t("circulation_is_cheap_and_that_is_derivable", _pump)
    t("but_the_organ_itself_is_not_derived", _organ)
    t("the_uv_shield_is_made_of_the_thing_it_protects", _uv)
    t("every_remaining_gate_is_architecture", _arch)
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


def _thick():
    a = tissue_thickness(1.0)
    b = tissue_thickness(5.0)
    if b / a > 3.0:
        raise ArithmeticError("thickness is not going as a square root")
    return (f"at present oxygen a body can be {a*1e6:.1f} microns thick "
            f"without circulation, and at FIVE times present only "
            f"{b*1e6:.1f} -- {b/a:.2f}x for 5x the air, because "
            f"diffusion goes as the square root. Thickness is not "
            f"bought from the atmosphere. It is bought with a pump")


def _prime():
    rows = prime_earth()
    best = max(r["o2_fraction"] for r in rows)
    g_no = {n: s for n, s, _w in body_gates(best, circulation=False)}
    g_yes = {n: s for n, s, _w in body_gates(best, circulation=True)}
    if g_no["aerobic"] != "OPEN":
        raise ArithmeticError("prime Earth cannot even reach aerobic")
    if g_no["thick body"] == "OPEN":
        raise ArithmeticError("a thick body formed without circulation")
    if g_yes["thick body"] != "OPEN":
        raise ArithmeticError("circulation did not open a thick body")
    return (f"Earth run at its best -- full productivity, a tenth the "
            f"reduced sink -- reaches {100*best:.0f}% of present oxygen. "
            f"That opens aerobic metabolism and a thin body, and it "
            f"does NOT open a thick one. Adding circulation opens it "
            f"immediately at the same oxygen. So the step to a large "
            f"animal is not an atmosphere, it is an organ, and no "
            f"amount of prime conditions substitutes")


def _pump():
    rows = [(m, pump_cost(m)[1]) for m in (1e-6, 1e-3, 1.0, 70.0, 1e4)]
    if any(f > 0.1 for _m, f in rows):
        raise ArithmeticError("pumping costs more than a tenth of the "
                              "budget somewhere; it is not obviously "
                              "affordable and this reasoning changes")
    if rows[0][1] <= rows[-1][1]:
        raise ArithmeticError("pumping did not get cheaper with size")
    return ("Poiseuille against Kleiber: pumping costs "
            + ", ".join(f"{100*f:.2f}% at {m:g} kg" for m, f in rows)
            + ". Affordable everywhere and cheaper as bodies grow, "
              "because demand rises as mass^0.75 and resistance falls "
              "as r^-4. Circulation is not a barrier that had to be "
              "crossed -- it is the cheap answer to a problem that "
              "becomes unavoidable at 55 microns")


def _organ():
    ok, _w = circulation_pays(70.0)
    if not ok:
        raise ArithmeticError("the economics no longer favour a pump")
    return ("that a pump PAYS FOR ITSELF does not say how a lineage "
            "builds one, and there is no rule here for that. The "
            "derivable claim is narrower than 'circulation is "
            "derivable': nothing forbids it, and the economics favour "
            "it at exactly the size diffusion fails. The organ is "
            "still an absence, and a smaller one than it looked")


def _uv():
    weak, ok = uv_transmitted(0.005), uv_transmitted(0.05)
    if not (weak > ok):
        raise ArithmeticError("more oxygen did not block more UV")
    return (f"ozone is made from oxygen, so a planet cannot shield its "
            f"land before its air is breathable -- the same molecule "
            f"does both. It saturates quickly: {weak:.1e} of the "
            f"damaging band reaches the ground at 0.5% of present "
            f"oxygen and {ok:.1e} at 5%. The shield is not the hard "
            f"part of coming ashore")


def _arch():
    best = max(r["o2_fraction"] for r in prime_earth())
    bare = {n: s for n, s, _w in land_gates(best)}
    built = {n: s for n, s, _w in land_gates(best, barrier=True,
                                             skeleton=True)}
    env = [n for n, s in bare.items() if s == "OPEN"]
    shut = [n for n, s in bare.items() if s == "SHUT"]
    if not all(built[n] == "OPEN" for n in shut):
        raise ArithmeticError("a skin and a skeleton do not open the "
                              "remaining land gates")
    return (f"on prime Earth the environmental gates open ({', '.join(env)}) "
            f"and the shut ones are {', '.join(shut)} -- a skin and a "
            f"skeleton. Adding them opens everything at the same "
            f"oxygen. THIS IS THE THIRD TIME: a thick body needed a "
            f"pump, land needs a cuticle and bones, and not one of "
            f"them is something a planet supplies. Every barrier left "
            f"in this simulation is architecture")


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
    best = max(r["o2_fraction"] for r in prime_earth())
    print(f"\n  PRIME EARTH reaches {100*best:.0f}% of present O2\n")
    for label, circ in (("without circulation", False),
                        ("with circulation", True)):
        print(f"  {label}:")
        for n, st, w in body_gates(best, circ):
            print(f"    {'open' if st == 'OPEN' else 'SHUT'} {n:15}{w[:66]}")
    print("\n  ON LAND, at prime oxygen:")
    for label, kw in (("as a sea creature", {}),
                      ("with skin and skeleton",
                       {"barrier": True, "skeleton": True})):
        print(f"  {label}:")
        for n, st, w in land_gates(best, **kw):
            print(f"    {'open' if st == 'OPEN' else 'SHUT'} {n:16}{w[:62]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:46}{d[:52]}")
    print("\nall:", ok)
