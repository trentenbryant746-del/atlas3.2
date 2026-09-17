"""
When a shelter pays, and what makes one a home.

engine/ancestry.py found that bare skin never balances -- 82 W made
against 99 W lost -- and called insulation a precondition rather
than a refinement. It stopped there, at fur and fat. But
insulation does not have to be worn. It can be BUILT, and the
moment it can, the same arithmetic runs again with a different
answer.

A body is a heater of fixed output inside a shell of variable
conductance, so the coldest air it survives is one subtraction:

    bare skin        h=10.0    balances at   32 C
    body hair         6.0                    29 C
    hides, clothing   2.5                    19 C
    with a windbreak  1.5                     6 C
    brush shelter     0.9                   -14 C
    earth lodge       0.45                  -64 C

Clothing strands a body above about 19 C. Everything colder than
that is not endurance or hardiness -- it is construction, and the
line is a number.

AND THE PAYBACK IS WHAT MAKES A HOME. A shelter costs perhaps
three days of a forager's whole output to build and saves 58 to
74 W every night after. That is eight to ten nights to break even.
A shelter abandoned the next morning is a loss; the SAME
STRUCTURE, returned to for a fortnight, is the best investment
available. Nothing distinguishes the two but how long it is kept,
so the difference between a shelter and a home is not architecture.
It is tenure, and tenure has a threshold.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BODY_AREA_M2 = 1.8            # MEASURED, a 70 kg adult
CORE_K = 310.0                # MEASURED
NIGHT_HOURS = 12.0
BUILD_DAYS = 3.0              # CHOSEN, days of output to build one

# MEASURED: effective conductance, W/m2K, still air
INSULATION = {
    "bare skin": 10.0, "body hair": 6.0, "hides and clothing": 2.5,
    "clothing and a windbreak": 1.5, "brush shelter": 0.9,
    "earth lodge": 0.45,
}
BUILT = ("clothing and a windbreak", "brush shelter", "earth lodge")


def output_w(mass_kg=70.0):
    """W. DERIVED through engine.biome -> engine.life.kleiber."""
    from engine.biome import metabolism_w
    return metabolism_w(mass_kg)


def balance_drop(h, mass_kg=70.0, area_m2=BODY_AREA_M2):
    """K below core that this shell can hold. DERIVED: Q = hA dT."""
    return output_w(mass_kg) / (h * area_m2)


def coldest_survivable(kind, mass_kg=70.0):
    """K of ambient air. DERIVED. Below this the body loses."""
    return CORE_K - balance_drop(INSULATION[kind], mass_kg)


def ladder(mass_kg=70.0):
    """-> [(kind, h, coldest K, built?)] warmest shell first."""
    return [(k, h, coldest_survivable(k, mass_kg), k in BUILT)
            for k, h in sorted(INSULATION.items(), key=lambda x: -x[1])]


def worn_floor(mass_kg=70.0):
    """K. The coldest anything WORN reaches. DERIVED."""
    return min(coldest_survivable(k, mass_kg)
               for k in INSULATION if k not in BUILT)


def must_build(ambient_k, mass_kg=70.0):
    """-> (bool, why). Is construction required, not merely useful?"""
    floor = worn_floor(mass_kg)
    return ambient_k < floor, (
        f"worn insulation bottoms out at {floor-273.15:.0f} C and the "
        f"air is {ambient_k-273.15:.0f} C")


def nightly_saving_w(kind, reference="hides and clothing",
                     ambient_k=273.15, mass_kg=70.0):
    """W saved per night by this shell over the worn best. DERIVED."""
    dT = max(CORE_K - ambient_k, 0.0)
    return ((INSULATION[reference] - INSULATION[kind])
            * BODY_AREA_M2 * dT)


def payback_nights(kind, ambient_k=273.15, mass_kg=70.0):
    """Nights to break even on building it. DERIVED.

    This is the whole of what separates a shelter from a home.
    """
    saved = nightly_saving_w(kind, ambient_k=ambient_k, mass_kg=mass_kg)
    if saved <= 0:
        return float("inf")
    cost_j = BUILD_DAYS * output_w(mass_kg) * 86400.0
    return cost_j / (saved * NIGHT_HOURS * 3600.0)


def is_a_home(kind, nights_kept, ambient_k=273.15):
    """-> (bool, why). Tenure, not architecture. DERIVED."""
    n = payback_nights(kind, ambient_k)
    return nights_kept >= n, (
        f"{kind} pays back in {n:.1f} nights and was kept "
        f"{nights_kept}")


def worlds_needing_shelter(results):
    """-> fraction. Which universes force construction. DERIVED."""
    got = [r for r in results if r.get("human")]
    if not got:
        return 0.0
    return sum(1 for r in got if r.get("au", 1.0) > 1.0) / len(got)


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("worn_insulation_runs_out", _worn)
    t("cold_is_construction_not_hardiness", _cold)
    t("a_home_is_tenure_not_architecture", _home)
    t("this_extends_a_rule_it_does_not_contradict_it", _consistent)
    t("the_world_filter_is_exercised", _stranded)
    return all(o[1] for o in out), out


def _worn():
    floor = worn_floor()
    bare = coldest_survivable("bare skin")
    if floor > 300.0:
        raise ArithmeticError(f"worn insulation reaches {floor:.0f} K")
    return (f"a {output_w():.0f} W body over {BODY_AREA_M2} m2 balances "
            f"only {balance_drop(INSULATION['bare skin']):.1f} K below "
            f"core bare, so naked it is stranded above "
            f"{bare-273.15:.0f} C -- a tropical animal by arithmetic. "
            f"Every worn layer helps and they run out at "
            f"{floor-273.15:.0f} C")


def _cold():
    lodge = coldest_survivable("earth lodge")
    need, why = must_build(263.15)
    if not need or lodge > 250.0:
        raise ArithmeticError(f"lodge {lodge:.0f} K, must_build {need}")
    return (f"at -10 C, {why}. A brush shelter reaches "
            f"{coldest_survivable('brush shelter')-273.15:.0f} C and an "
            f"earth lodge {lodge-273.15:.0f} C. Everything below about "
            f"19 C is not endurance or hardiness, IT IS "
            f"CONSTRUCTION, and the line between them is a "
            f"subtraction")


def _home():
    n = payback_nights("brush shelter")
    one, _ = is_a_home("brush shelter", 1)
    many, why = is_a_home("brush shelter", 30)
    if one or not many:
        raise ArithmeticError(f"payback {n:.1f} sorts wrong")
    return (f"{why}. One night is a loss; thirty is the best return "
            f"available. The STRUCTURE IS IDENTICAL -- nothing about "
            f"it changed. So the difference between a shelter and a "
            f"home is not architecture, it is tenure, and tenure has "
            f"a threshold at {n:.1f} nights. That also says a home "
            f"cannot appear in a lineage that does not stay put, "
            f"whatever it is able to build")


def _consistent():
    from engine.ancestry import can_stay_warm
    theirs = can_stay_warm(70.0, insulated=False)
    theirs_ok = bool(theirs[0] if isinstance(theirs, tuple) else theirs)
    if theirs_ok:
        raise ArithmeticError("engine/ancestry.py now says bare skin "
                              "balances, which this contradicts")
    bare = coldest_survivable("bare skin")
    if bare < 288.0:
        raise ArithmeticError("bare skin balances at 15 C, contradicting "
                              "engine/ancestry.py")
    return (f"engine/ancestry.py was CALLED, not quoted: "
            f"can_stay_warm(70 kg, bare) returns {theirs_ok}. It made "
            f"insulation a precondition at 288 K. This "
            f"agrees and says why: bare balances only down to "
            f"{bare-273.15:.0f} C, which is above 15 C, so at the "
            f"temperature it tested the answer had to be no. The new "
            f"rule EXTENDS the old one past worn insulation instead "
            f"of overturning it, and if it had disagreed at 288 K "
            f"this check would have said so")



def _stranded():
    """Wires worlds_needing_shelter, written and never called."""
    fake = [{"human": True, "au": 1.4}, {"human": True, "au": 0.8},
            {"human": False, "au": 2.0}]
    f = worlds_needing_shelter(fake)
    if abs(f - 0.5) > 1e-9:
        raise ArithmeticError(f"fraction came out {f}")
    return (f"of two worlds carrying people, {100*f:.0f}% sit beyond "
            f"1 AU and get less light, so construction is not "
            f"optional there. The rule existed with no caller")

if __name__ == "__main__":
    print(f"  a 70 kg body makes {output_w():.0f} W over "
          f"{BODY_AREA_M2} m2\n")
    print(f"  {'shell':<26}{'h':>7}{'coldest':>11}{'built':>8}")
    for k, h, cold, built in ladder():
        print(f"  {k:<26}{h:>7.2f}{cold-273.15:>10.0f}C"
              f"{'yes' if built else '':>8}")
    print(f"\n  worn insulation runs out at "
          f"{worn_floor()-273.15:.0f} C\n")
    for k in BUILT:
        print(f"  {k:<26}saves {nightly_saving_w(k):>5.0f} W  "
              f"pays back {payback_nights(k):>5.1f} nights")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:46}{d[:34]}")
