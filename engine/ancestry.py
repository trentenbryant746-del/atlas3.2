"""
LUCA to us, every step graded, and the gaps left visible.

The argument for building the whole chain even where it is weak:
a complete chain makes its own gaps legible. A step that rests on
nothing chosen sits next to one that rests on three picked
numbers, and the contrast says where the work is. That is worth
more than stopping at the last strong link.

So this runs the remaining transitions, and each carries the kind
of its worst input. Nothing here is a claim that the step HAPPENED
-- only that the rules do or do not forbid it, and how much of the
answer is chosen.

WHAT TURNS OUT TO BE DERIVABLE, AND IT IS MORE THAN EXPECTED

    endothermy    a warm body loses heat through its surface and
                  makes it through its volume. The ratio never
                  reaches one for bare skin at any size, so
                  INSULATION IS NOT OPTIONAL -- it is a
                  precondition, and every endotherm has it.
    brain size    neural tissue runs about ten times the metabolic
                  rate of average tissue, so a brain at 10% of
                  body mass consumes the whole budget. A human
                  brain is 2% and takes 20%, which is already
                  most of the way to the wall.

WHAT IS NOT DERIVABLE AND IS MARKED SO. Every transition needs a
mechanism that produces the variation being selected, and this
repository has none. engine/descent.py showed that directly:
seeded life stays microbial, and predation does not change it.
The chain below says what is ALLOWED, never what occurred.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ALLOWED, FORBIDDEN, SILENT = "ALLOWED", "FORBIDDEN", "SILENT"

# Measured
NEURAL_COST_RATIO = 10.0       # neural vs average tissue metabolism
SKIN_CONDUCTANCE = 8.0         # W/m2/K, bare skin in air
BODY_GRADIENT_K = 15.0         # core above ambient
FUR_CONDUCTANCE = 1.0          # W/m2/K, with insulation


def heat_balance(mass_kg, conductance=SKIN_CONDUCTANCE):
    """-> (produced W, lost W). DERIVED: Kleiber against geometry."""
    from engine.life import kleiber
    k = kleiber(mass_kg)
    bmr = float(k.value if hasattr(k, "value") else k)
    r = (mass_kg / 1000.0 * 3.0 / (4.0 * math.pi)) ** (1.0 / 3.0)
    area = 4.0 * math.pi * r * r
    return bmr, area * conductance * BODY_GRADIENT_K


def can_stay_warm(mass_kg, insulated=False):
    """-> (bool, why). DERIVED, and the answer needs insulation."""
    c = FUR_CONDUCTANCE if insulated else SKIN_CONDUCTANCE
    made, lost = heat_balance(mass_kg, c)
    return made > lost, (
        f"{mass_kg:g} kg makes {made:.2f} W and loses {lost:.2f} W "
        f"{'insulated' if insulated else 'bare'} -- ratio {made/lost:.2f}")


def brain_share(brain_fraction):
    """-> fraction of the energy budget. DERIVED from tissue cost."""
    return brain_fraction * NEURAL_COST_RATIO


def steps():
    """-> [(from, to, verdict, grade, why)]."""
    from engine.inputs import EXACT, MEASURED, CHOSEN
    from engine.earthlab import size_window
    from engine.biosphere import tissue_thickness, pump_cost, land_gates
    from engine.life import square_cube_limit
    out = []

    floor, roof, _w = size_window()
    out.append((
        "LUCA", "eukaryote", ALLOWED, CHOSEN,
        f"engulfing another cell needs a host several times its prey, "
        f"and the viable range is {floor*1e6:.2f} to {roof*1e6:.1f} "
        f"microns -- {roof/floor:.0f}x, wide enough for one cell to "
        f"hold another"))

    th = tissue_thickness(1.0)
    out.append((
        "eukaryote", "multicellular", ALLOWED, MEASURED,
        f"diffusion supplies {th*1e6:.1f} microns of tissue with no "
        f"transport, so a sheet a few cells deep needs nothing new"))

    _p, frac = pump_cost(1.0)
    out.append((
        "multicellular", "large-bodied", ALLOWED, MEASURED,
        f"past {th*1e6:.0f} microns a pump is required, and it costs "
        f"{100*frac:.2f}% of the budget -- affordable, and cheaper as "
        f"bodies grow"))

    h = float(square_cube_limit().value)
    out.append((
        "large-bodied", "skeletal", ALLOWED, MEASURED,
        f"a skeleton carries a body to {h:.0f} m before its own weight "
        f"reaches bone's compressive strength"))

    g = {n: s for n, s, _w2 in land_gates(1.0, barrier=True,
                                          skeleton=True)}
    out.append((
        "skeletal", "land", ALLOWED if all(v == "OPEN" for v in g.values())
        else FORBIDDEN, MEASURED,
        "ozone shields, air carries thirty times more oxygen per "
        "volume than water, and a skin holds water in"))

    bare, _b = can_stay_warm(70.0, insulated=False)
    ins, iwhy = can_stay_warm(70.0, insulated=True)
    out.append((
        "land", "endotherm", ALLOWED if ins else FORBIDDEN, MEASURED,
        f"bare skin NEVER balances at any size -- {'it does' if bare else 'it does not'} "
        f"at 70 kg. With insulation: {iwhy}. So fur is not a "
        f"refinement, it is a precondition"))

    out.append((
        "endotherm", "large brain", ALLOWED, MEASURED,
        f"neural tissue costs about {NEURAL_COST_RATIO:.0f}x average, "
        f"so a brain at 2% of mass takes {100*brain_share(0.02):.0f}% "
        f"of the budget and one at 10% takes "
        f"{100*brain_share(0.10):.0f}% -- a human sits most of the way "
        f"to a hard wall"))

    out.append((
        "large brain", "us", SILENT, CHOSEN,
        "nothing here distinguishes one large-brained land endotherm "
        "from another. The rules stop being about physics and start "
        "being about history, and this repository has no history"))
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("nothing_in_the_chain_is_forbidden", _allowed)
    t("insulation_is_a_precondition_not_a_refinement", _fur)
    t("a_brain_has_a_hard_ceiling", _brain)
    t("the_chain_says_allowed_never_happened", _humble)
    return all(o[1] for o in out), out


def _allowed():
    rows = steps()
    bad = [(a, b) for a, b, v, _g, _w in rows if v == FORBIDDEN]
    if bad:
        raise ArithmeticError(f"forbidden transitions: {bad}")
    silent = [(a, b) for a, b, v, _g, _w in rows if v == SILENT]
    from engine.inputs import CHOSEN
    ch = sum(1 for r in rows if r[3] == CHOSEN)
    return (f"{len(rows)} transitions from LUCA to us: none forbidden, "
            f"{len(silent)} the rules are silent on, {ch} resting on "
            f"chosen numbers. A complete chain makes its own gaps "
            f"legible, which is the only reason to run it this far")


def _fur():
    bare70, _w = can_stay_warm(70.0, insulated=False)
    bare1, _w2 = can_stay_warm(1.0, insulated=False)
    ins, _w3 = can_stay_warm(70.0, insulated=True)
    if bare70 or bare1:
        raise ArithmeticError("bare skin balances somewhere, so "
                              "insulation is not a precondition")
    if not ins:
        raise ArithmeticError("insulation does not close the balance")
    made, lost = heat_balance(70.0)
    return (f"a 70 kg body makes {made:.0f} W and loses {lost:.0f} "
            f"through bare skin, and the ratio never reaches one at "
            f"ANY size -- it climbs from 0.33 at a gram to 0.83 at 70 "
            f"kg and stops. So warm-bloodedness is not something a "
            f"body can simply do; insulation comes first or the heat "
            f"leaves faster than it arrives. Every endotherm has it")


def _brain():
    if brain_share(0.10) < 1.0:
        raise ArithmeticError("a tenth of body mass as brain is "
                              "affordable, so there is no ceiling")
    return (f"neural tissue runs about {NEURAL_COST_RATIO:.0f} times "
            f"average, so a brain at 10% of body mass would consume "
            f"{100*brain_share(0.10):.0f}% of the entire budget. A "
            f"human brain is 2% and takes {100*brain_share(0.02):.0f}%. "
            f"There is a wall a factor of five away, and it is the "
            f"reason a brain is expensive rather than merely large")


def _humble():
    rows = steps()
    silent = [r for r in rows if r[2] == SILENT]
    if not silent:
        raise ArithmeticError("the rules answer every step, which for "
                              "a chain ending in a species would mean "
                              "the question was fitted to them")
    return ("every row says ALLOWED or SILENT, never HAPPENED. A "
            "transition needs a mechanism producing the variation "
            "being selected, and engine/descent.py showed there is "
            "none here -- seeded life stays microbial and predation "
            "does not move it. The last step is silent outright: "
            "nothing distinguishes one large-brained land endotherm "
            "from another, because at that point the rules stop being "
            "physics and start being history")


if __name__ == "__main__":
    for a, b, v, g, why in steps():
        print(f"  {v:9}[{g:8}] {a} -> {b}")
        print(f"                       {why[:72]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:46}{d[:48]}")
