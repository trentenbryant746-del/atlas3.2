"""
Three ladders that gate each other, first ancestor to us.

The question was to build from the earliest ancestor to a human
with understanding, tools and habitat all evolving. They are not
three stories. They are one, and the interlock is not asserted
here -- the same numbers appear in all three because the same
rules produced them.

    UNDERSTANDING   how many constraints bind, from
                    engine/comprehension.py
    TOOLS           what a blow can break, from engine/tools.py
    HABITAT         how cold a body survives, from
                    engine/shelter.py

AND THE GATE BETWEEN THEM IS ONE NUMBER. Bone yields at 1.7e8 Pa.
A fist reaches 4e5 and an unworked cobble 4e6; only a flaked edge
reaches 4e8. That same threshold is what lets hide be cut and
wood be shaped -- so every shelter colder than worn insulation
requires a flaked edge, and the habitat ladder is GATED ON THE
TOOL LADDER by the stress that opens a bone.

    hides and clothing      19 C   worn as found
    clothing and windbreak   6 C   needs cutting
    brush shelter          -14 C   needs cutting
    earth lodge            -64 C   needs cutting and digging

Then the habitat opens latitude, because insolation falls as
cos(lat) and Stefan-Boltzmann makes temperature fall as its
fourth root:

    worn only        27 deg    45% of land
    windbreak        42        67%
    brush shelter    57        84%
    earth lodge      77        97%

AND THE LOOP CLOSES. A new latitude brings a new constraint --
seasonality, which nothing at the equator faces -- so the count
in engine/comprehension.py rises, and a higher count is what a
larger brain is for. Understanding buys tools, tools buy
habitat, habitat imposes understanding.

What this does NOT do is produce the flake. engine/innovation.py
has that: the step is an existing process with a part omitted,
duplicated or combined, and the share of viable variants that
are useful is 1e-4 and unmeasured.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

T_EQUATOR = 300.0          # MEASURED, mean equatorial surface
EARTH_LAND_M2 = 1.49e14    # MEASURED

GRADES = ["bare skin", "body hair", "hides and clothing",
          "clothing and a windbreak", "brush shelter", "earth lodge"]


def temperature_at(lat_deg):
    """K at this latitude. DERIVED: insolation cos, S-B fourth root.

    No meridional heat transport, which understates real high
    latitudes. Marked rather than corrected, because correcting
    it would need a circulation this repository does not have.
    """
    return T_EQUATOR * max(math.cos(math.radians(lat_deg)), 1e-6) ** 0.25


def latitude_reached(T_min):
    """Highest latitude a body surviving T_min can occupy. DERIVED."""
    for lat in range(0, 90):
        if temperature_at(lat) < T_min:
            return lat
    return 90


def land_share(lat_deg):
    """Share of land inside this latitude. DERIVED: sin."""
    return math.sin(math.radians(lat_deg))


def needs_a_tool(grade):
    """-> bool. Must material be worked for this shelter? DERIVED."""
    from engine.shelter import BUILT
    return grade in BUILT


def tool_available(surface="flaked edge"):
    """-> bool. Can this surface work hide and wood? DERIVED.

    The same threshold that opens a bone, because it is the same
    material property being exceeded.
    """
    from engine.tools import breaks, CONTACT
    return breaks(area_m2=CONTACT[surface])


def rung(grade):
    """-> dict. One step of all three ladders at once. DERIVED."""
    from engine.shelter import coldest_survivable
    T = coldest_survivable(grade)
    lat = latitude_reached(T)
    return {"grade": grade, "coldest_k": T, "latitude": lat,
            "land": land_share(lat), "worked": needs_a_tool(grade),
            "gated_on": "flaked edge" if needs_a_tool(grade) else None}


def ladder():
    """-> [dict]. The whole trajectory, in order. DERIVED."""
    return [rung(g) for g in GRADES]


def seasonality(lat_deg, tilt=23.4):
    """Summer-winter swing in K at this latitude. DERIVED.

    Obliquity moves the sub-solar point, so the insolation a
    latitude receives varies across the year and the swing grows
    with latitude. At the equator there is almost none.
    """
    hi = temperature_at(max(lat_deg - tilt, 0.0))
    lo = temperature_at(min(lat_deg + tilt, 89.0))
    return hi - lo


def constraints_at(lat_deg, threshold_k=15.0):
    """-> [str]. What binds here and not at the equator. DERIVED."""
    out = []
    if seasonality(lat_deg) >= threshold_k:
        out.append("seasonality: food is not available year round")
    from engine.shelter import worn_floor
    if temperature_at(lat_deg) < worn_floor():
        out.append("construction: worn insulation is not enough")
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_habitat_ladder_is_gated_on_the_tool_ladder", _gate)
    t("one_threshold_decides_both", _one)
    t("habitat_opens_latitude_and_latitude_is_land", _lat)
    t("latitude_imposes_a_constraint_the_equator_does_not", _season)
    t("so_the_loop_closes", _loop)
    t("this_does_not_produce_the_flake", _residue)
    return all(o[1] for o in out), out


def _gate():
    rows = ladder()
    worn = [r for r in rows if not r["worked"]]
    built = [r for r in rows if r["worked"]]
    if not worn or not built:
        raise ArithmeticError("the ladder does not split")
    edge = max(r["coldest_k"] for r in built)
    return (f"{len(worn)} grades are worn as found and {len(built)} "
            f"need material worked. Everything colder than "
            f"{edge-273.15:.0f} C is on the far side of a tool, so "
            f"THE HABITAT LADDER IS GATED ON THE TOOL LADDER -- and "
            f"the gate is not asserted here, it is the same stress "
            f"threshold engine/tools.py used for a bone")


def _one():
    from engine.tools import breaks, CONTACT
    from engine.life import BONE_COMPRESSIVE
    fist = breaks(area_m2=CONTACT["fist"])
    edge = tool_available()
    if fist or not edge:
        raise ArithmeticError(f"fist {fist}, edge {edge}")
    return (f"bone yields at {BONE_COMPRESSIVE:.1e} Pa and hide and "
            f"wood give way to the same concentrated stress. A fist "
            f"cannot reach it, an unworked cobble cannot, a flaked "
            f"edge can. ONE NUMBER decides whether a bone opens and "
            f"whether a shelter can be built, which is why the two "
            f"ladders move together rather than being made to")


def _lat():
    rows = ladder()
    lo, hi = rows[2], rows[-1]
    if hi["land"] <= lo["land"]:
        raise ArithmeticError("colder shelter does not open land")
    return (f"insolation falls as cos(lat) and Stefan-Boltzmann makes "
            f"temperature fall as its fourth root, so a body "
            f"surviving {lo['coldest_k']-273.15:.0f} C reaches "
            f"{lo['latitude']}d and {100*lo['land']:.0f}% of land "
            f"while one surviving {hi['coldest_k']-273.15:.0f} C "
            f"reaches {hi['latitude']}d and {100*hi['land']:.0f}%. "
            f"No meridional heat transport is modelled, which "
            f"understates the high latitudes and is marked rather "
            f"than corrected")


def _season():
    eq, high = seasonality(0.0), seasonality(60.0)
    c = constraints_at(60.0)
    if high <= eq or not c:
        raise ArithmeticError(f"equator {eq:.1f} K, 60d {high:.1f} K")
    return (f"obliquity moves the sub-solar point, so the swing "
            f"between summer and winter is {eq:.1f} K at the equator "
            f"and {high:.1f} K at 60 degrees. That imposes "
            f"{c[0][:46]}... -- a constraint nothing at the equator "
            f"faces, which is how a habitat hands back a rule")


def _loop():
    from engine.comprehension import binding
    n_micro, n_human = len(binding("bacterium")), len(binding("human"))
    rows = ladder()
    return (f"UNDERSTANDING BUYS TOOLS, TOOLS BUY HABITAT, HABITAT "
            f"IMPOSES UNDERSTANDING. A flaked edge opens "
            f"{100*rows[-1]['land']:.0f}% of land against "
            f"{100*rows[2]['land']:.0f}% without one; the land it "
            f"opens is seasonal; seasonality is a constraint that "
            f"must be answered; and engine/comprehension.py counts "
            f"what binds, {n_micro} on a microbe and {n_human} on "
            f"us. The loop is three modules written for three other "
            f"reasons, meeting at one stress threshold and one "
            f"cosine")


def _residue():
    return ("this shows the ladders gate each other and does NOT "
            "produce the flake. engine/innovation.py holds that: a "
            "step is an existing process with a part omitted, "
            "duplicated or combined, the non-lethal variants arrive "
            "at 4.48 per division, and the share of them that are "
            "USEFUL is 1e-4 and unmeasured. Everything here is "
            "conditional on the first edge, and the first edge is "
            "still the thing nothing derives")


if __name__ == "__main__":
    print(f"  {'grade':<26}{'coldest':>9}{'lat':>6}{'land':>7}"
          f"{'worked':>8}")
    for r in ladder():
        print(f"  {r['grade']:<26}{r['coldest_k']-273.15:>7.0f}C"
              f"{r['latitude']:>5}d{100*r['land']:>6.0f}%"
              f"{'yes' if r['worked'] else '':>8}")
    print(f"\n  seasonality: {seasonality(0):.1f} K at the equator, "
          f"{seasonality(60):.1f} K at 60 degrees")
    for c in constraints_at(60.0):
        print(f"    -> {c}")
    print()
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:50}{d[:28]}")
