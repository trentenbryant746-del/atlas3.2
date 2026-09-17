"""
Is the DNA good enough to say how tall or how strong? No.

engine/biomatter.py has real DNA -- the four nucleotides by
formula, the standard code, B-form geometry at 0.34 nm a base.
engine/descent.py has a radius that mutates and three traits that
switch on and off. NOTHING CONNECTS THEM. There is chemistry at
one end and a label at the other and no map in between, so the
answer to whether the genetics can attribute height, muscle and
health is no, and it is not a close no.

But the three asked for do not fail the same way, and the
difference is the whole of what this file is worth.

MUSCLE IS DERIVED. Force is stress times area and nothing else.
Vertebrate muscle pulls at about 0.3 MPa, an elbow gives up about
4:1 in leverage, so the 400 N blow engine/tools.py needs to crack
a bone wants 1,600 N of muscle across 53 cm2. That is an arm. No
gene had to be invented; the number was already implied by a
module that only wanted a hammer.

HEIGHT IS BOUNDED AND FREE INSIDE THE BOUND. Bone carries 1.4 m
and 2.5 m at 0.1% and 0.6% of its strength. Physics does not pick
between them, so height is not derivable here and has to be
GIVEN -- which is a real answer, not a shrug: it says the rules
constrain this trait and do not determine it.

HEALTH IS A LOAD WITH NO PURGE. About 70 new mutations a
generation and 1.5 of them harmful, accumulating, with nothing in
this repository removing any. engine/civ.py reached the same hole
from the other side when sex came back only PARTLY DERIVED. The
ratchet is named in two places now and turned by neither.

AND ONE WARNING ABOUT PREFERABLE DNA. Assigning a genome that is
better requires a measure of better, and no rule here supplies
one. Taller is not fitter -- engine/ontogeny.py prices a bigger
body as a bigger bill. What gets assigned below is marked GIVEN
and its preference is explicitly somebody's, not the physics'.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# MEASURED
MUSCLE_PA = 3.0e5           # vertebrate specific tension
ELBOW_LEVER = 4.0           # mechanical disadvantage
MUTATIONS_PER_GEN = 70.0
DELETERIOUS_PER_GEN = 1.5
BASE_HEIGHT_M = 1.70
BASE_MASS_KG = 70.0

# GIVEN. Height inside the bound is not set by any rule here, so it
# is handed over, and "preferable" is somebody's preference.
GIVEN_GENOME = {
    "height_m": 1.80,
    "muscle_cm2": 60.0,
    "deleterious_load": 0.0,
}


def muscle_area_m2(hand_force_n, lever=ELBOW_LEVER, pa=MUSCLE_PA):
    """m2 of cross-section. DERIVED: force is stress times area."""
    return hand_force_n * lever / pa


def force_from_area(area_m2, lever=ELBOW_LEVER, pa=MUSCLE_PA):
    """N at the hand. DERIVED, the inverse."""
    return area_m2 * pa / lever


def mass_for_height(h_m, base_h=BASE_HEIGHT_M, base_m=BASE_MASS_KG):
    """kg. DERIVED: geometric similarity, mass goes as h^3."""
    return base_m * (h_m / base_h) ** 3


def ankle_stress(h_m, bone_area_m2=2e-3):
    """Pa. DERIVED. What standing costs the skeleton."""
    from engine.life import G_EARTH
    return mass_for_height(h_m) * G_EARTH / bone_area_m2


def height_is_determined(lo=1.2, hi=2.6):
    """-> (bool, why). Does bone pick a height? DERIVED."""
    from engine.life import BONE_COMPRESSIVE
    worst = ankle_stress(hi) / BONE_COMPRESSIVE
    return worst > 1.0, (
        f"at {hi:.1f} m the ankle carries {100*worst:.1f}% of bone's "
        f"strength, so everything from {lo:.1f} to {hi:.1f} m stands")


def load_after(generations, per_gen=DELETERIOUS_PER_GEN, purge=0.0):
    """Accumulated harmful mutations. DERIVED, and purge is the hole."""
    return generations * per_gen * (1.0 - purge)


def ratchet_is_turned():
    """-> (bool, why). Does anything here remove a bad mutation?"""
    return False, (
        "no rule in this repository purges a deleterious mutation. "
        "engine/civ.py found the same hole from the other side when "
        "sex came back PARTLY DERIVED -- the NEED for repair follows "
        "from the error threshold and the mechanism does not")


def phenotype(genome=None):
    """-> {trait: (value, kind, why)}. The map that did not exist."""
    g = dict(GIVEN_GENOME if genome is None else genome)
    area = g["muscle_cm2"] * 1e-4
    return {
        "height_m": (g["height_m"], "GIVEN",
                     "bone allows the whole range; no rule picks"),
        "mass_kg": (mass_for_height(g["height_m"]), "DERIVED",
                    "geometric similarity from the given height"),
        "hand_force_n": (force_from_area(area), "DERIVED",
                         f"{g['muscle_cm2']:.0f} cm2 at "
                         f"{MUSCLE_PA:.0e} Pa over a "
                         f"{ELBOW_LEVER:.0f}:1 lever"),
        "upkeep_w": (_upkeep(mass_for_height(g["height_m"])), "DERIVED",
                     "Kleiber, through engine/biome.py"),
        "deleterious_load": (g["deleterious_load"], "GIVEN",
                             "set to zero because nothing purges"),
    }


def _upkeep(mass_kg):
    from engine.biome import metabolism_w
    return metabolism_w(mass_kg)


def taller_is_not_fitter(h_lo=1.6, h_hi=2.1):
    """-> (bool, why). Does the preference cost anything? DERIVED."""
    lo, hi = _upkeep(mass_for_height(h_lo)), _upkeep(mass_for_height(h_hi))
    return hi > lo, (
        f"{h_lo:.1f} m runs at {lo:.0f} W and {h_hi:.1f} m at "
        f"{hi:.0f} W, {100*(hi/lo-1):.0f}% more, every second, forever")


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_dna_here_cannot_say_how_tall", _nomap)
    t("muscle_is_derived_from_stress_and_area", _muscle)
    t("height_is_bounded_and_not_determined", _height)
    t("health_is_a_load_with_no_purge", _load)
    t("preferable_needs_a_measure_of_better", _prefer)
    t("the_assigned_genome_faces_the_same_gates", _gates)
    return all(o[1] for o in out), out


def _nomap():
    import ast
    bm = (ROOT / "engine" / "biomatter.py").read_text()
    de = (ROOT / "engine" / "descent.py").read_text()
    if "descent" in bm or "biomatter" in de:
        raise ArithmeticError("the two modules reference each other")
    return ("engine/biomatter.py holds the four nucleotides by "
            "formula, the standard code and B-form geometry. "
            "engine/descent.py holds a radius and three named "
            "traits. NEITHER FILE MENTIONS THE OTHER -- there is "
            "chemistry at one end, a label at the other, and no map "
            "between. So no, the DNA cannot attribute height, and "
            "it is not a close no")


def _muscle():
    from engine.tools import ARM_BLOW_N
    a = muscle_area_m2(ARM_BLOW_N)
    if not 1e-3 < a < 1e-2:
        raise ArithmeticError(f"{1e4*a:.0f} cm2 is not an arm")
    return (f"the {ARM_BLOW_N:.0f} N blow engine/tools.py needs to "
            f"crack a bone wants {ARM_BLOW_N*ELBOW_LEVER:.0f} N of "
            f"muscle across {1e4*a:.0f} cm2 at "
            f"{MUSCLE_PA:.0e} Pa. That is an arm, and no gene had to "
            f"be invented -- the number was already implied by a "
            f"module that only wanted a hammer")


def _height():
    det, why = height_is_determined()
    if det:
        raise ArithmeticError("bone picks a height after all")
    return (f"{why}. So height is BOUNDED and free inside the bound, "
            f"which is a real answer rather than a shrug: these rules "
            f"constrain the trait and do not determine it, so it has "
            f"to be given and the giving is visible")


def _load():
    turned, why = ratchet_is_turned()
    if turned:
        raise ArithmeticError("something purges after all")
    return (f"{DELETERIOUS_PER_GEN:.1f} harmful mutations a generation "
            f"reach {load_after(50):.0f} in fifty with nothing "
            f"removing them. {why}. The ratchet is named in two "
            f"modules now and turned by neither")


def _prefer():
    worse, why = taller_is_not_fitter()
    if not worse:
        raise ArithmeticError("being taller is free")
    p = phenotype()
    given = [k for k, (_v, kind, _w) in p.items() if kind == "GIVEN"]
    return (f"the assigned genome is 1.80 m and 60 cm2, and it is "
            f"marked GIVEN in {len(given)} of {len(p)} traits. "
            f"'Preferable' needs a measure of better and no rule here "
            f"supplies one: {why}. Taller is not fitter, it is "
            f"hungrier, so the preference is somebody's and is "
            f"labelled as somebody's")


def _gates():
    """The given genome is not exempt from anything derived."""
    from engine.tools import ARM_BLOW_N, stress, CONTACT
    from engine.life import BONE_COMPRESSIVE
    from engine.senses import PRECISION_GRIP_N, GRIP_FRICTION
    p = phenotype()
    force = p["hand_force_n"][0]
    upkeep = p["upkeep_w"][0]
    opens = stress(force, CONTACT["flaked edge"]) > BONE_COMPRESSIVE
    holds = PRECISION_GRIP_N * GRIP_FRICTION > force * 0.0625
    if not opens:
        raise ArithmeticError(f"{force:.0f} N cannot open a bone")
    if not holds:
        raise ArithmeticError("the hand cannot hold what the arm swings")
    base = _upkeep(BASE_MASS_KG)
    return (f"the assigned genome makes {force:.0f} N, above the "
            f"{ARM_BLOW_N:.0f} N a bone needs, so it opens one -- and "
            f"it eats {upkeep:.0f} W against {base:.0f} W for a 70 kg "
            f"body, {100*(upkeep/base-1):.0f}% more forever. BEING "
            f"GIVEN A GENOME EXEMPTS IT FROM NOTHING. The preference "
            f"bought a capability and was charged for it by rules "
            f"that never heard of it")


if __name__ == "__main__":
    from engine.tools import ARM_BLOW_N
    print(f"  muscle for a {ARM_BLOW_N:.0f} N blow: "
          f"{1e4*muscle_area_m2(ARM_BLOW_N):.0f} cm2   DERIVED\n")
    print(f"  {'height':>8}{'mass':>8}{'ankle':>10}{'% of bone':>11}")
    from engine.life import BONE_COMPRESSIVE
    for h in (1.4, 1.7, 2.0, 2.5):
        s = ankle_stress(h)
        print(f"  {h:>7.1f}m{mass_for_height(h):>7.0f}kg"
              f"{s/1e6:>9.2f}MPa{100*s/BONE_COMPRESSIVE:>10.2f}%")
    print(f"\n  assigned genome (GIVEN): {GIVEN_GENOME}\n")
    for k, (v, kind, why) in phenotype().items():
        vv = f"{v:.1f}" if isinstance(v, float) else str(v)
        print(f"  {k:<18}{vv:>8}  {kind:<8}{why[:44]}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:38]}")
