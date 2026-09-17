"""
The last step, and what it costs to take it.

engine/ancestry.py walks LUCA to us in eight transitions and the
last one CROSSES: no rule there distinguishes one large-brained
land endotherm from another. This file asks the only version of
that question with a number in it -- WHAT PAYS FOR THE BRAIN --
and follows the answer wherever it goes.

A 70 kg body runs at 82 W. Neural tissue costs about ten times
average, so going from an ape's 400 g of brain to our 1350 g adds
13.6% of the whole budget, 11.1 W, every second for life. Nothing
carries that for free.

The expensive-tissue answer is that something else got smaller,
and the gut is the candidate: shrink it from an ape's proportion
to ours and 15.6% of the budget comes back, 12.8 W, which covers
the brain with change. That arithmetic works.

But it only works if the food got easier, because a small gut
cannot digest a large one's diet -- and making food easier is
what a brain is FOR. So the answer is circular, and this file
does not hide that. It asks whether the circle is a ramp that can
be climbed or a threshold that cannot, and the difference is
decidable: if each small increment of brain pays for itself
through the processing it buys, the bootstrap resolves the way
walking does. If it does not, the human is a bootstrap of exactly
the same shape as the origin of life in engine/earthlab.py, and
this repository has now found the same hole twice.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.atoms import REDFIELD, atoms_in, mass_of, Pool

BODY_KG = 70.0                 # RECORDED, a human
APE_BRAIN_KG = 0.40            # RECORDED, chimpanzee
HUMAN_BRAIN_KG = 1.35          # RECORDED
APE_GUT_FRACTION = 0.030       # RECORDED, great ape
HUMAN_GUT_FRACTION = 0.017     # RECORDED
GUT_COST_RATIO = 12.0          # MEASURED, gut vs average tissue
COOKING_GAIN = 0.35            # MEASURED, extra energy from cooked food


def budget_w(mass_kg=BODY_KG):
    """W. DERIVED through engine.biome.metabolism_w -> life.kleiber."""
    from engine.biome import metabolism_w
    return metabolism_w(mass_kg)


def brain_cost(brain_kg, mass_kg=BODY_KG):
    """-> (fraction of budget, W). DERIVED."""
    from engine.ancestry import NEURAL_COST_RATIO
    f = brain_kg / mass_kg * NEURAL_COST_RATIO
    return f, f * budget_w(mass_kg)


def gut_saving(from_f=APE_GUT_FRACTION, to_f=HUMAN_GUT_FRACTION,
               mass_kg=BODY_KG):
    """-> (fraction of budget freed, W). DERIVED."""
    f = (from_f - to_f) * GUT_COST_RATIO
    return f, f * budget_w(mass_kg)


def gut_needed(diet_quality):
    """Body fraction. DERIVED: poorer food needs more gut to hold
    it long enough, so the requirement goes inversely with how much
    of the food is already available when swallowed."""
    ref_q = 0.50                      # CHOSEN, raw ape forage
    return APE_GUT_FRACTION * ref_q / max(diet_quality, 1e-6)


def pays_at(brain_kg, diet_quality, mass_kg=BODY_KG):
    """-> (net W, cost W, freed W). Does THIS brain pay at THIS diet?"""
    _, cost = brain_cost(brain_kg, mass_kg)
    g = gut_needed(diet_quality)
    freed = (APE_GUT_FRACTION - g) * GUT_COST_RATIO * budget_w(mass_kg)
    base = brain_cost(APE_BRAIN_KG, mass_kg)[1]
    return freed - (cost - base), cost, freed


def ramp(steps=20, q_from=0.50, q_to=0.50 * (1.0 + COOKING_GAIN)):
    """-> [(brain kg, diet quality, net W)]. DERIVED.

    Walk brain and diet up together in small steps and ask at every
    one whether the animal is better off than the step before. If
    it is, the circle is a ramp.
    """
    out = []
    for i in range(steps + 1):
        t = i / steps
        b = APE_BRAIN_KG + t * (HUMAN_BRAIN_KG - APE_BRAIN_KG)
        q = q_from + t * (q_to - q_from)
        out.append((b, q, pays_at(b, q)[0]))
    return out


def diet_implied_by_gut(gut_f=HUMAN_GUT_FRACTION):
    """Diet quality the RECORDED human gut requires. DERIVED."""
    return APE_GUT_FRACTION * 0.50 / gut_f


def break_even_gain(lo=0.0, hi=3.0):
    """Diet improvement at which the whole climb stops losing."""
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if ramp(q_to=0.50 * (1.0 + mid))[-1][2] >= 0.0:
            hi = mid
        else:
            lo = mid
    return hi


def is_a_ramp(tol=1e-9):
    """-> (bool, first step that loses). DERIVED."""
    r = ramp()
    for i in range(1, len(r)):
        if r[i][2] < r[i - 1][2] - tol:
            return False, i
    return True, None


def tool_pays(reach_gain, brain_kg=HUMAN_BRAIN_KG, mass_kg=BODY_KG):
    """-> (bool, why). A tool is only a tool if it feeds you more
    than the head that made it costs."""
    f, w = brain_cost(brain_kg, mass_kg)
    base_f, _ = brain_cost(APE_BRAIN_KG, mass_kg)
    extra = f - base_f
    return reach_gain > extra, (
        f"the extra brain costs {100*extra:.1f}% of the budget, so a "
        f"tool must raise intake by more than that. At "
        f"{100*reach_gain:.0f}% it "
        + ("pays" if reach_gain > extra else "does NOT pay"))


def body_atoms(mass_kg=BODY_KG):
    """-> ({element: kg}, conserved). Required by engine/atoms.py:
    a life module that makes a body says what it is made of."""
    from engine.atoms import WEIGHT, AVOGADRO
    counts = atoms_in(mass_kg)
    kg = {e: n * WEIGHT[e] / AVOGADRO / 1000.0 for e, n in counts.items()}
    p = Pool(atoms_in(mass_kg * 2.0))
    p.build(mass_kg)
    p.die(mass_kg)
    return kg, p.conserved()[0]


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_gut_trade_was_the_wrong_question", _tradeoff)
    t("cooking_alone_does_not_explain_the_gut", _ramp)
    t("the_two_routes_to_the_gut_are_compared", _clash)
    t("a_tool_must_feed_the_head_that_made_it", _tool)
    t("a_human_is_made_of_atoms_and_returns_them", _matter)
    t("nothing_here_says_it_happened", _humble)
    t("the_ramp_test_is_exercised", _stranded)
    return all(o[1] for o in out), out


def _tradeoff():
    """INVERTED, kept. The arithmetic stands; the framing does not."""
    from engine.ontogeny import ONTOGENY, brain_share, provisioning_debt
    _, cost = brain_cost(HUMAN_BRAIN_KG)
    _, base = brain_cost(APE_BRAIN_KG)
    _, freed = gut_saving()
    if freed < (cost - base):
        raise ArithmeticError("the arithmetic itself stopped working")
    infant = brain_share(ONTOGENY[0][1], ONTOGENY[0][2])
    if infant <= 1.0:
        raise ArithmeticError("a newborn can feed its own head after all")
    _, yrs = provisioning_debt()
    return (f"INVERTED, kept. The sum is still right -- {freed:.1f} W "
            f"freed against {cost-base:.1f} W spent -- and it answers "
            f"nothing, because it prices an ADULT STANDING STILL, as "
            f"though a brain were a running cost some organ must "
            f"offset. A brain is built, out of food, in childhood, by "
            f"someone else. engine/ontogeny.py runs the life instead "
            f"of the snapshot: a newborn's brain is {100*infant:.0f}% "
            f"of everything its own body can make, and the {yrs:.1f} "
            f"adult-years a child costs were never inside one body to "
            f"be found by rearranging its organs")


def _ramp():
    """MISSING_RULE, named not tuned."""
    need = break_even_gain()
    implied = diet_implied_by_gut() / 0.50 - 1.0
    r = ramp()
    if r[-1][2] >= 0:
        raise ArithmeticError("cooking covered it after all")
    if need < COOKING_GAIN:
        raise ArithmeticError("break-even is below cooking; no gap left")
    return (f"MISSING_RULE, and NARROWED. This used to say cooking "
            f"fails to pay for the brain; engine/ontogeny.py showed "
            f"the brain was never waiting on the gut. What is left is "
            f"still real and now stands on its own: the human gut IS "
            f"smaller, and nothing here explains how far. Walk brain "
            f"and diet up together and the "
            f"climb LOSES ground the whole way, {r[0][2]:.2f} W to "
            f"{r[-1][2]:.2f} W. It only breaks even at a "
            f"{100*need:.0f}% diet improvement, and cooking is "
            f"measured at {100*COOKING_GAIN:.0f}% -- short by a factor "
            f"of {need/COOKING_GAIN:.2f} -- and {implied/COOKING_GAIN:.2f} "
            f"against the {100*implied:.0f}% the recorded gut implies. "
            f"So cooking alone does not "
            f"pay for a human brain. COOKING_GAIN was NOT raised to "
            f"close this. What is absent is whatever else made the "
            f"food cheaper: meat is denser per gram, pounding and "
            f"cutting digest food outside the body, and sharing "
            f"spreads a bad day. None of those has a rule here, and "
            f"the gap says how big they have to be together")


def _clash():
    """A CLASH between two routes to the same number, reported."""
    implied = diet_implied_by_gut()
    _, cost = brain_cost(HUMAN_BRAIN_KG)
    _, base = brain_cost(APE_BRAIN_KG)
    _, freed = gut_saving()
    if freed <= (cost - base):
        raise ArithmeticError("the recorded route stopped working too")
    return (f"CLASH, and both sides are kept. Route one takes the "
            f"RECORDED ape and human gut fractions and finds the trade "
            f"works: {freed:.1f} W freed against {cost-base:.1f} W "
            f"spent. Route two models the gut from diet quality and "
            f"finds it does not. They disagree because the recorded "
            f"human gut implies a diet {100*(implied/0.50-1):.0f}% "
            f"better than raw forage and nothing here supplies more "
            f"than {100*COOKING_GAIN:.0f}%. The trade is real; the "
            f"reason the gut could shrink that far is not derived. "
            f"Neither number was moved to make them agree")


def _tool():
    small, _ = tool_pays(0.05)
    big, _ = tool_pays(0.30)
    if small or not big:
        raise ArithmeticError("the tool threshold is not where it should be")
    return (f"the extra brain over an ape's costs "
            f"{100*(brain_cost(HUMAN_BRAIN_KG)[0]-brain_cost(APE_BRAIN_KG)[0]):.1f}% "
            f"of the budget. A tool returning 5% does not pay for it; "
            f"one returning 30% does. Cooking is measured at about "
            f"{100*COOKING_GAIN:.0f}%. So tool use is affordable here "
            f"-- which is not the same as saying anything made one")


def _matter():
    kg, ok = body_atoms()
    if not ok:
        raise ArithmeticError("a human did not return its atoms")
    top = sorted(kg.items(), key=lambda x: -x[1])[:3]
    return (f"a {BODY_KG:.0f} kg human is "
            + ", ".join(f"{e} {v:.1f} kg" for e, v in top)
            + f" and the rest, built from a pool and returned to it "
              f"whole. The same rule that catches a forest growing out "
              f"of nothing catches a person")


def _humble():
    return ("every row here says CAN, never DID. The gut can pay for "
            "the brain, the climb can be walked in increments, a tool "
            "can return more than it costs. What no rule in this "
            "repository reaches is why this lineage and not the other "
            "large-brained land endotherms -- engine/ancestry.py marks "
            "that step RECORDED and it stays RECORDED. The path is "
            "shown to be open. It is not shown to have been taken")



def _stranded():
    """Wires is_a_ramp, written and never called."""
    ok, where = is_a_ramp()
    if ok:
        raise ArithmeticError("the climb became a ramp")
    return (f"is_a_ramp() returns False, losing ground at step "
            f"{where} of twenty. It is the predicate behind the "
            f"cooking MISSING_RULE and it had no caller of its own")

if __name__ == "__main__":
    print(f"  a {BODY_KG:.0f} kg body runs at {budget_w():.0f} W\n")
    _, c = brain_cost(HUMAN_BRAIN_KG)
    _, b = brain_cost(APE_BRAIN_KG)
    _, f = gut_saving()
    print(f"  brain {1000*APE_BRAIN_KG:.0f} -> {1000*HUMAN_BRAIN_KG:.0f} g "
          f"costs {c-b:>5.1f} W")
    print(f"  gut shrunk to ours         frees {f:>5.1f} W")
    print(f"  net                              {f-(c-b):>5.1f} W\n")
    print(f"  {'brain kg':>10}{'diet q':>9}{'net W':>9}")
    r = ramp()
    for row in (r[0], r[5], r[10], r[15], r[20]):
        print(f"  {row[0]:>10.2f}{row[1]:>9.3f}{row[2]:>9.2f}")
    print(f"\n  a ramp, never losing ground: {is_a_ramp()[0]}\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:42]}")
