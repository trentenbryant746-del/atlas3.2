"""
A tool, produced rather than priced.

engine/ontogeny.py searched 28 combinations of brain size and
intake gain, found 21 of them affordable, and made none. The root
of that question was TWO NODES deep -- one constant and itself --
the shallowest anything in this repository stands on, and
engine/spine.py reports that as the answer: nothing feeds it
because nothing produces a tool to feed it. The same hole closed
around pumps, skins and skeletons in engine/descent.py. All can be
priced. None can be made.

A tool is the one piece of architecture that might be reachable,
for a reason that has nothing to do with cleverness: IT IS NOT
GROWN. A pump has to be built by a body out of its own budget and
inherited. A stone is already lying there. Nothing has to invent
it, encode it, or pay to carry it.

So the question becomes mechanical and it has an answer.

    a blow is a force over an area, and stress is F/A
    bone yields at 1.7e8 Pa, which engine/life.py already knew
    a fist spreads 400 N over 1e-3 m2  ->  4e5 Pa, short by 425x
    a cobble spreads it over 1e-4       ->  4e6 Pa, short by 42x
    a flaked edge over 1e-6             ->  4e8 Pa, THROUGH

Picking up a rock is not enough, and that falls out rather than
being asserted. The edge has to be MADE small. That is the line
between using an object and making a tool, and it is a number.

And the material chooses itself: wood and limestone fail before
bone does, granite and flint do not. Nobody told these rules to
prefer flint.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.life import BONE_COMPRESSIVE

# MEASURED: compressive strength, Pa
MATERIALS = {
    "wood": 5.0e7, "limestone": 1.2e8, "granite": 2.0e8,
    "flint": 5.0e8, "obsidian": 4.0e8,
}

# MEASURED: contact area of a striking surface, m2
CONTACT = {
    "fist": 1.0e-3, "heel of hand": 3.0e-4, "tooth": 2.0e-5,
    "unworked cobble": 1.0e-4, "flaked edge": 1.0e-6,
}

ARM_BLOW_N = 400.0          # MEASURED, a hammering blow
MARROW_KG_PER_FEMUR = 0.20  # MEASURED, large ungulate
MARROW_J_PER_KG = 2.93e7    # MEASURED, 700 kcal/100 g
FORAGER_DAY_J = 8.37e6      # MEASURED, 2000 kcal


def stress(force_n=ARM_BLOW_N, area_m2=CONTACT["fist"]):
    """Pa. DERIVED. The whole of it: force over area."""
    return force_n / area_m2


def breaks(target_pa=BONE_COMPRESSIVE, **kw):
    """-> bool. Does this blow exceed what it lands on? DERIVED."""
    return stress(**kw) > target_pa


def usable(material, target_pa=BONE_COMPRESSIVE):
    """-> bool. A tool that fails before its target is not a tool."""
    return MATERIALS[material] > target_pa


def what_works(target_pa=BONE_COMPRESSIVE, force_n=ARM_BLOW_N):
    """-> [(surface, material)]. Every combination that opens it."""
    return [(s, m) for s in CONTACT for m in MATERIALS
            if stress(force_n, CONTACT[s]) > target_pa and usable(m, target_pa)]


def body_alone(target_pa=BONE_COMPRESSIVE, force_n=ARM_BLOW_N):
    """-> (bool, shortfall). Can the animal do it unaided? DERIVED."""
    best = max(stress(force_n, CONTACT[s])
               for s in ("fist", "heel of hand", "tooth"))
    return best > target_pa, target_pa / best


def marrow_gain(bones_per_day=1.0):
    """-> fraction of a day's intake. DERIVED, not chosen.

    GATED ON ACCESS. An earlier version multiplied marrow constants
    and handed back a number whether or not anything could open the
    bone -- the payoff did not depend on the barrier, which is the
    same shape of error as pricing a tool nobody can make. If no
    surface and material combination gets through, the calories are
    still in there and the gain is zero.
    """
    if not what_works():
        return 0.0
    return (bones_per_day * MARROW_KG_PER_FEMUR * MARROW_J_PER_KG
            / FORAGER_DAY_J)


def reach_advantage(arm_m=0.75, haft_m=1.75, predator_m=1.0):
    """-> (bool, metres). A spear is geometry, not courage. DERIVED."""
    return (arm_m + haft_m) > predator_m, (arm_m + haft_m) - predator_m


def defended_risk(base_risk, arm_m=0.75, haft_m=1.75, predator_m=1.0):
    """-> risk. DERIVED: a predator that must close inside your reach
    is struck first, so the fraction of approaches that land is the
    fraction of the closing distance it survives."""
    ok, margin = reach_advantage(arm_m, haft_m, predator_m)
    if not ok:
        return base_risk
    return base_risk * (predator_m / (arm_m + haft_m))


def pays_for_a_brain(brain_kg=1.35, bones_per_day=1.0):
    """-> (bool, gain, cost). Closes the loop on engine/human.py."""
    from engine.ancestry import NEURAL_COST_RATIO
    gain = marrow_gain(bones_per_day)
    cost = (brain_kg - 0.40) / 70.0 * NEURAL_COST_RATIO
    return gain > cost, gain, cost


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("a_body_cannot_open_a_bone", _body)
    t("picking_up_a_rock_is_not_enough", _cobble)
    t("the_material_selects_itself", _material)
    t("the_intake_gain_is_derived_not_chosen", _gain)
    t("no_access_means_no_calories", _gated)
    t("a_spear_is_geometry", _spear)
    t("this_produces_a_tool_it_does_not_price_one", _produced)
    t("the_breaks_predicate_is_exercised", _stranded)
    return all(o[1] for o in out), out


def _body():
    ok, short = body_alone()
    if ok:
        raise ArithmeticError("a fist breaks bone, so nothing is needed")
    return (f"the hardest thing a body has spreads {ARM_BLOW_N:.0f} N "
            f"over {CONTACT['tooth']:.0e} m2 and reaches "
            f"{stress(area_m2=CONTACT['tooth']):.2e} Pa against bone's "
            f"{BONE_COMPRESSIVE:.1e} -- short by {short:.0f}x. The "
            f"calories inside a femur are unreachable to the animal "
            f"that killed it. That is the barrier, and it is a "
            f"material property, not a lack of wit")


def _cobble():
    c = stress(area_m2=CONTACT["unworked cobble"])
    f = stress(area_m2=CONTACT["flaked edge"])
    if c > BONE_COMPRESSIVE or f <= BONE_COMPRESSIVE:
        raise ArithmeticError("the cobble/flake line is not where it falls")
    return (f"an unworked cobble reaches {c:.1e} Pa and still fails by "
            f"{BONE_COMPRESSIVE/c:.0f}x. A flaked edge reaches {f:.1e} "
            f"and goes through. PICKING UP A ROCK IS NOT ENOUGH -- the "
            f"edge has to be made small, and the only variable is "
            f"contact area. That is the line between using an object "
            f"and making a tool and it is {CONTACT['unworked cobble']/CONTACT['flaked edge']:.0f}x "
            f"of area, nothing else")


def _material():
    good = sorted(m for m in MATERIALS if usable(m))
    bad = sorted(m for m in MATERIALS if not usable(m))
    if "wood" in good or "flint" in bad:
        raise ArithmeticError(f"the materials sorted wrong: {good}")
    return (f"{', '.join(bad)} fail before bone does; "
            f"{', '.join(good)} do not. A tool that breaks before its "
            f"target is not a tool, so the rock chooses itself out of "
            f"whatever is lying there. Nobody told these rules to "
            f"prefer flint over wood, and for a DIFFERENT job -- reach "
            f"-- wood wins, because the test is never the material, it "
            f"is the material against the target")


def _gain():
    ok, gain, cost = pays_for_a_brain()
    if not ok:
        raise ArithmeticError(f"marrow at {gain:.2f} does not cover {cost:.2f}")
    return (f"one femur a day is {100*gain:.0f}% of a forager's intake, "
            f"against the {100*cost:.0f}% a human brain costs over an "
            f"ape's. It pays with {gain/cost:.1f}x over. And this "
            f"number was NOT chosen -- engine/ontogeny.py had to be "
            f"handed a gain to test against; this one comes out of "
            f"how much marrow is in a femur and how much energy is in "
            f"marrow")


def _gated():
    real = marrow_gain()
    # globals(), NOT `import engine.tools as T`. Under `python3 -m`
    # this file is __main__, so importing it by name loads a SECOND
    # copy and the patch lands on the wrong one -- the same
    # two-copies-of-one-thing the duplicate-constant rule exists to
    # stop, arriving through the module system instead.
    g = globals()
    keep = dict(g["CONTACT"])
    try:
        g["CONTACT"] = {k: v for k, v in keep.items() if v >= 1e-4}
        blocked = marrow_gain()
    finally:
        g["CONTACT"] = keep
    if real <= 0 or blocked != 0.0:
        raise ArithmeticError(f"gain {real} with access, {blocked} without")
    return (f"take the flaked edge away and the gain goes to exactly "
            f"zero, not to something smaller. The calories do not "
            f"become partly available when the bone stays shut. An "
            f"earlier version multiplied marrow constants whether or "
            f"not anything could open it, which is pricing wearing "
            f"the clothes of producing")


def _spear():
    bare, _ = reach_advantage(haft_m=0.0)
    armed, margin = reach_advantage()
    risk = defended_risk(0.40)
    if bare or not armed:
        raise ArithmeticError("the reach comparison is backwards")
    return (f"an arm reaches 0.75 m and a large predator strikes at "
            f"1.0, so bare you are always inside its range and it is "
            f"never inside yours. Haft 1.75 m of wood and reach goes "
            f"to 2.5, a {margin:.2f} m margin, dropping predation risk "
            f"from 0.40 to {risk:.2f}. No courage, no tactics -- the "
            f"whole of it is which of two numbers is larger")


def _produced():
    works = what_works()
    if not works:
        raise ArithmeticError("nothing opens a bone")
    return (f"{len(works)} surface-and-material combinations open a "
            f"bone and every one was DERIVED: the force a body makes, "
            f"the area it lands on, and strengths already in "
            f"engine/life.py. Nothing here was handed a tool or told "
            f"one existed. This is the first piece of architecture "
            f"this repository has produced rather than priced -- and "
            f"it worked only because a tool is the one kind that is "
            f"NOT GROWN. A pump must be built by a body and inherited. "
            f"A stone is already lying there. The hole in "
            f"engine/descent.py is still open for everything that has "
            f"to be built")



def _stranded():
    """Wires breaks, which was written and never called."""
    fist = breaks(area_m2=CONTACT["fist"])
    flake = breaks(area_m2=CONTACT["flaked edge"])
    if fist or not flake:
        raise ArithmeticError(f"fist {fist}, flake {flake}")
    return ("breaks() says False for a fist and True for a flaked "
            "edge, which is the whole of this module in one "
            "predicate -- and nothing called it until now")

if __name__ == "__main__":
    print(f"  bone yields at {BONE_COMPRESSIVE:.1e} Pa\n")
    for s, a in sorted(CONTACT.items(), key=lambda x: -x[1]):
        v = stress(area_m2=a)
        print(f"  {s:<18}{a:>8.0e} m2{v:>11.2e} Pa  "
              f"{'THROUGH' if v > BONE_COMPRESSIVE else ''}")
    print()
    for m, c in sorted(MATERIALS.items(), key=lambda x: x[1]):
        print(f"  {m:<12}{c:>9.1e} Pa  "
              f"{'holds' if usable(m) else 'fails first'}")
    ok, gain, cost = pays_for_a_brain()
    print(f"\n  marrow from one femur: {100*gain:.0f}% of a day")
    print(f"  a human brain costs:   {100*cost:.0f}% over an ape's")
    print(f"  pays: {ok}  ({gain/cost:.1f}x)")
    print(f"  predation 0.40 -> {defended_risk(0.40):.2f} with a spear\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:46}{d[:36]}")
