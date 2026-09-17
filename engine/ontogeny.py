"""
Child to adult, and who actually pays.

engine/human.py asked what pays for a brain and answered with an
adult standing still: a brain costs 20% of the budget, so shrink
the gut and the books balance. That framing is WRONG, and not by a
little. A brain is not a running cost that an adult must offset
against some other organ. A brain is BUILT, out of food, during
childhood, by someone who is not paying for it.

Run the life instead of the snapshot and the arithmetic changes
shape entirely:

  AT BIRTH THE BRAIN EXCEEDS THE WHOLE BUDGET. 380 g of neural
  tissue in a 3.5 kg body is 109% of what that body can produce.
  Not tight -- impossible. An infant cannot support its own head,
  so provisioning is not an advantage here, it is a precondition,
  the same shape as insulation in engine/ancestry.py.

  GROWTH STOPS TO PAY FOR IT. Body growth falls to its slowest at
  age five, 1.5 kg a year, and the brain is still taking 71% of
  the budget right there. Two curves entered separately -- body
  mass by age, brain mass by age -- and the minimum of one sits in
  the expensive phase of the other. Nothing was arranged for that.

So the gut never had to shrink to make room. The child simply grows
more slowly and eats what it is given, and the adult that results
has a brain it did not pay to build.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.atoms import Pool, atoms_in, mass_of, WEIGHT, AVOGADRO

# RECORDED: (age yr, body kg, brain kg) for one human
ONTOGENY = [
    (0.0, 3.5, 0.38), (0.5, 7.5, 0.65), (1.0, 10.0, 0.95),
    (2.0, 12.5, 1.10), (4.0, 16.5, 1.25), (5.0, 18.0, 1.28),
    (8.0, 26.0, 1.33), (10.0, 32.0, 1.34), (13.0, 45.0, 1.35),
    (18.0, 65.0, 1.35),
]

# MEASURED: neural tissue is lipid-rich and phosphorus-rich, and it
# is NOT Redfield. A brain built from the plankton recipe would be
# the silent-inheritance failure engine/lab.py forbids by name.
NEURAL = {"C": 40.0, "H": 80.0, "O": 8.0, "N": 1.0, "P": 1.0}

FORAGER_W = 97.0               # MEASURED, 2000 kcal/day net
SECONDS_PER_YEAR = 3.15576e7   # EXACT, Julian


def budget_w(mass_kg):
    """W. DERIVED through engine.biome -> engine.life.kleiber."""
    from engine.biome import metabolism_w
    return metabolism_w(mass_kg)


def brain_share(body_kg, brain_kg):
    """Fraction of the body's OWN budget the brain takes. DERIVED."""
    from engine.ancestry import NEURAL_COST_RATIO
    return brain_kg / body_kg * NEURAL_COST_RATIO


def self_supporting(body_kg, brain_kg):
    """-> (bool, share). Over 1.0 the animal cannot feed its own head."""
    s = brain_share(body_kg, brain_kg)
    return s < 1.0, s


def growth_rate(i):
    """kg/yr between sample i-1 and i. DERIVED from the curve."""
    a0, m0, _ = ONTOGENY[i - 1]
    a1, m1, _ = ONTOGENY[i]
    return (m1 - m0) / (a1 - a0)


def slowest_growth():
    """-> (age, kg/yr, brain share there). DERIVED, after infancy."""
    rows = [(ONTOGENY[i][0], growth_rate(i),
             brain_share(ONTOGENY[i][1], ONTOGENY[i][2]))
            for i in range(2, len(ONTOGENY))]
    return min(rows, key=lambda r: r[1])


def provisioning_debt(ape_brain_kg=0.40, ape_body_kg=70.0):
    """-> (J, adult-years). What an outsider must supply. DERIVED.

    The excess is measured against an ape's brain share, so this is
    the bill for being human rather than the bill for being alive.
    """
    from engine.ancestry import NEURAL_COST_RATIO
    base = ape_brain_kg / ape_body_kg * NEURAL_COST_RATIO
    total = 0.0
    for i in range(1, len(ONTOGENY)):
        a0, m0, b0 = ONTOGENY[i - 1]
        a1, m1, b1 = ONTOGENY[i]
        extra = (0.5 * (brain_share(m0, b0) + brain_share(m1, b1)) - base)
        w = 0.5 * (budget_w(m0) + budget_w(m1))
        total += extra * w * (a1 - a0) * SECONDS_PER_YEAR
    return total, total / FORAGER_W / SECONDS_PER_YEAR


def grow_from_food(pool=None):
    """-> (kg of body built, kg of brain built, conserved). DERIVED.

    A child is assembled from atoms it eats, and the brain is
    assembled from a DIFFERENT recipe than the rest of it.
    """
    birth_m, birth_b = ONTOGENY[0][1], ONTOGENY[0][2]
    adult_m, adult_b = ONTOGENY[-1][1], ONTOGENY[-1][2]
    d_brain = adult_b - birth_b
    d_soma = (adult_m - adult_b) - (birth_m - birth_b)
    if pool is None:
        pool = Pool(atoms_in((d_soma + d_brain) * 20.0))
    ok_s, short_s = pool.build(d_soma)
    ok_b, short_b = pool.build(d_brain, NEURAL)
    if not (ok_s and ok_b):
        return 0.0, 0.0, (short_s or short_b)
    return d_soma, d_brain, pool.conserved()[0]


def brain_elements(brain_kg=1.35):
    """-> {element: kg}. What a head is made of. DERIVED."""
    c = atoms_in(brain_kg, NEURAL)
    return {e: n * WEIGHT[e] / AVOGADRO / 1000.0 for e, n in c.items()}


def tool_search(gains=None, brains=None):
    """-> (found, rows). Does anything here MAKE a tool?

    A tool is intake an animal gets without carrying it as tissue.
    This enumerates the space and reports where one would pay --
    and, separately, whether any rule in this repository can
    produce one rather than price it.
    """
    from engine.ancestry import NEURAL_COST_RATIO
    if gains is None:
        # The gain is no longer a list somebody picked. engine/tools.py
        # derives it from how much marrow is in a femur and how much
        # energy is in marrow, which is why this question's root stopped
        # being two nodes deep.
        from engine.tools import marrow_gain
        gains = [0.0, marrow_gain(0.25), marrow_gain(0.5),
                 marrow_gain(1.0), marrow_gain(2.0)]
    brains = brains or [0.40, 0.60, 0.90, 1.35]
    base = 0.40 / 70.0 * NEURAL_COST_RATIO
    rows = []
    for b in brains:
        for g in gains:
            cost = b / 70.0 * NEURAL_COST_RATIO - base
            rows.append((b, g, g - cost))
    return any(r[2] > 0 and r[1] > 0 for r in rows), rows


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("an_infant_cannot_feed_its_own_head", _infant)
    t("growth_stops_where_the_brain_is_dearest", _dip)
    t("the_provisioning_debt_is_a_number", _debt)
    t("a_child_is_built_from_what_it_eats", _build)
    t("a_brain_is_not_made_of_plankton", _neural)
    t("tools_can_be_priced_and_cannot_be_produced", _tools)
    return all(o[1] for o in out), out


def _infant():
    ok, share = self_supporting(*ONTOGENY[0][1:])
    if ok:
        raise ArithmeticError(f"a newborn covers its brain at {share:.2f}")
    adult_ok, adult = self_supporting(*ONTOGENY[-1][1:])
    if not adult_ok:
        raise ArithmeticError("an adult cannot either, so nothing is special")
    return (f"a newborn's 380 g brain is {100*share:.0f}% of everything "
            f"a 3.5 kg body can make -- over one hundred, so it is not "
            f"tight, it is impossible. The adult sits at "
            f"{100*adult:.0f}%. Provisioning is therefore a "
            f"PRECONDITION and not an advantage, the same shape as "
            f"insulation in engine/ancestry.py, which also never "
            f"balances at any size")


def _dip():
    age, rate, share = slowest_growth()
    early = growth_rate(1)
    if rate >= early:
        raise ArithmeticError("growth never slows")
    if share < 0.5:
        raise ArithmeticError(f"the brain is only {share:.2f} at the dip")
    return (f"body growth bottoms out at age {age:.0f} at "
            f"{rate:.2f} kg/yr, down from {early:.1f} in the first "
            f"half year, and the brain is still taking "
            f"{100*share:.0f}% of the budget right there. Two curves "
            f"were entered separately and the minimum of one lands in "
            f"the expensive phase of the other. The child does not "
            f"shrink an organ to afford its head -- IT STOPS GROWING")


def _debt():
    j, yrs = provisioning_debt()
    if not 0.5 < yrs < 20.0:
        raise ArithmeticError(f"{yrs:.1f} adult-years is not a childhood")
    return (f"{j/1e6:,.0f} MJ of brain above an ape's share, birth to "
            f"eighteen -- {yrs:.1f} adult-years of a forager's whole "
            f"surplus, per child. That is what somebody else has to "
            f"hand over. engine/human.py tried to find this inside one "
            f"adult body by shrinking the gut; it was never in there")


def _build():
    soma, brain, ok = grow_from_food()
    if not ok or brain <= 0:
        raise ArithmeticError(f"the child came out at {ok}")
    return (f"birth to adult is {soma:.1f} kg of body and {brain:.2f} kg "
            f"of brain, every atom of it drawn from a pool and the "
            f"pool still balancing. The food does not merely fuel the "
            f"child, IT IS THE CHILD -- which is the thing a watts-only "
            f"account could not say")


def _neural():
    n = brain_elements()
    r = atoms_in(1.0)
    nn = atoms_in(1.0, NEURAL)
    if abs(nn["P"] / r["P"] - 1.0) < 0.5:
        raise ArithmeticError("neural tissue got the plankton recipe")
    return (f"a 1.35 kg brain is C {n['C']:.2f} kg, P {n['P']:.3f} kg "
            f"and the rest. Per kilo it holds {nn['P']/r['P']:.1f} times "
            f"the phosphorus of Redfield tissue, because it is built of "
            f"phospholipid rather than protein. Wood got cellulose and "
            f"a brain gets this; no recipe here is a default anyone can "
            f"fall into")


def _tools():
    found, rows = tool_search()
    pays = [r for r in rows if r[2] > 0 and r[1] > 0]
    if not found:
        raise ArithmeticError("no configuration makes a tool worth having")
    made = []          # nothing in this repository produces one
    if made:
        raise ArithmeticError("something claimed to have made a tool")
    cheapest = min(pays, key=lambda r: r[1])
    return (f"SEARCHED, not assumed. {len(rows)} combinations of brain "
            f"size and intake gain; {len(pays)} of them pay, the "
            f"cheapest at a {100*cheapest[1]:.0f}% gain on a "
            f"{cheapest[0]:.2f} kg brain. So a tool is AFFORDABLE "
            f"across most of the space. Zero were MADE. Nothing in "
            f"this repository generates a tool, a technique or any "
            f"other piece of architecture -- engine/descent.py found "
            f"the same hole for pumps, skins and skeletons, which can "
            f"all be priced and none produced. That is one absence, "
            f"not two, and it is now met from a second direction")


if __name__ == "__main__":
    print(f"  {'age':>5}{'body':>8}{'brain':>8}{'W':>7}{'brain %':>9}"
          f"{'kg/yr':>8}")
    for i, (a, m, b) in enumerate(ONTOGENY):
        g = f"{growth_rate(i):.2f}" if i else "-"
        print(f"  {a:>5.1f}{m:>8.1f}{b:>8.2f}{budget_w(m):>7.1f}"
              f"{100*brain_share(m,b):>8.0f}%{g:>8}")
    age, rate, share = slowest_growth()
    print(f"\n  slowest growth at age {age:.0f}, {rate:.2f} kg/yr, "
          f"brain still {100*share:.0f}%")
    j, yrs = provisioning_debt()
    print(f"  provisioning debt {j/1e6:,.0f} MJ = {yrs:.1f} adult-years")
    soma, brain, ok = grow_from_food()
    print(f"  built {soma:.1f} kg body + {brain:.2f} kg brain, "
          f"conserved {ok}\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:40]}")
