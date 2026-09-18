"""
What prices regard: the contest you do not have to hold again.

engine/rank.py closed when rank has a price -- zero below the
carrying number, a whole 82 W life above it -- and left one
thing: what is derived is who EATS, not who is ADMIRED, and
whether those are the same is not a question those rules reached.

The reading that closes it is the obvious one and it is right:
allocation is the trophic rule applied inside a level. Who eats
is who can take, and taking is already derived -- reach and force
decide a contest between two humans with exactly the arithmetic
engine/tools.py used for a predator, 450 N from 60 cm2 of muscle
and 1.75 m of haft beating 0.75 m of arm.

But it is not the same rule, and the difference is where regard
comes from.

BETWEEN SPECIES THE LOSER IS EATEN. The energy transfers, which
is why a trophic level passes ten percent upward.

WITHIN ONE SPECIES THE LOSER IS NOT EATEN. Nothing transfers.
The contest produces no energy at all and costs both sides:

    a brief scuffle       0.2 MJ,  1% injury risk
    a real fight          4.2 MJ, 10%
    a fight to settle it 16.8 MJ, 25%

And allocation has to be decided perhaps daily -- seven thousand
times over twenty years. Fighting each one is unaffordable by
orders of magnitude.

REMEMBERING THE OUTCOME IS FREE. engine/learning.py already
priced that: erasing an entire brain costs 1.4 microjoules, so a
remembered rank costs nothing measurable against a fight's
megajoules. Regard is the memory of a settled contest, and what
it is worth is every contest it prevents.

That is why rank looks like a social fact and prices out as a
physical one.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

INJURY_YEARS_LOST = 20.0      # CHOSEN, a life cut short by injury
DECISIONS_PER_DAY = 1.0       # CHOSEN, how often allocation is settled
SOCIAL_YEARS = 20.0           # CHOSEN, how long a group holds together


def taking_capacity(muscle_cm2=60.0, haft_m=0.0, arm_m=0.75):
    """-> (force N, reach m). DERIVED via inherit and tools."""
    from engine.inherit import force_from_area
    return force_from_area(muscle_cm2 * 1e-4), arm_m + haft_m


def wins(a, b):
    """-> bool. Reach first, then force. DERIVED, same as predation."""
    fa, ra = a
    fb, rb = b
    if abs(ra - rb) > 1e-9:
        return ra > rb
    return fa > fb


def contest_cost(days=0.5, injury_risk=0.10):
    """-> (J spent, J of expected life lost). DERIVED."""
    from engine.civ import FORAGER_W
    from engine.biome import metabolism_w
    spent = FORAGER_W * days * 86400.0
    lost = injury_risk * metabolism_w(70.0) * INJURY_YEARS_LOST * 3.15576e7
    return spent, lost


def decisions(years=SOCIAL_YEARS, per_day=DECISIONS_PER_DAY):
    """How many times allocation must be settled. DERIVED."""
    return years * 365.0 * per_day


def cost_of_fighting_each(years=SOCIAL_YEARS):
    """J if every allocation is contested. DERIVED."""
    spent, lost = contest_cost()
    return decisions(years) * (spent + lost)


def cost_of_remembering():
    """J to hold a rank order in memory. DERIVED via learning."""
    from engine.learning import landauer_j, store_bits
    return landauer_j(store_bits())


def regard_is_worth(years=SOCIAL_YEARS):
    """-> (ratio, fought, remembered). What memory saves. DERIVED."""
    f, r = cost_of_fighting_each(years), cost_of_remembering()
    return f / max(r, 1e-30), f, r


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("who_eats_is_who_can_take", _take)
    t("but_the_loser_is_not_eaten_and_that_is_the_difference", _diff)
    t("a_contest_produces_nothing_and_costs_both", _cost)
    t("regard_is_the_contest_not_held_again", _mem)
    t("what_this_still_does_not_say", _residue)
    return all(o[1] for o in out), out


def _take():
    armed = taking_capacity(60.0, 1.75)
    bare = taking_capacity(60.0, 0.0)
    strong = taking_capacity(80.0, 0.0)
    weak = taking_capacity(40.0, 0.0)
    if not wins(armed, bare) or not wins(strong, weak):
        raise ArithmeticError("the contest does not resolve")
    return (f"allocation is the trophic rule applied inside a level: "
            f"who eats is who can take. And taking was already "
            f"derived -- {armed[0]:.0f} N from 60 cm2 of muscle, "
            f"{armed[1]:.2f} m of reach with a haft against "
            f"{bare[1]:.2f} bare. The same two quantities "
            f"engine/tools.py used to settle a predator settle this, "
            f"and nothing new was needed to say who wins")


def _diff():
    from engine.biome import TRANSFER_FRACTION
    return (f"but it is NOT the same rule. Between species the loser "
            f"is eaten and {100*TRANSFER_FRACTION:.0f}% of the energy "
            f"transfers -- that is what a trophic level is. Within "
            f"one species the loser is not eaten and NOTHING "
            f"TRANSFERS. The contest produces no energy at all, and "
            f"that difference is where regard comes from")


def _cost():
    spent, lost = contest_cost()
    n = decisions()
    if spent <= 0 or lost <= 0:
        raise ArithmeticError("a contest is free")
    return (f"a real fight costs {spent/1e6:.1f} MJ and a 10% chance "
            f"of {lost/1e9:.1f} GJ of life, and allocation must be "
            f"settled about {n:,.0f} times over twenty years. "
            f"Fighting each one costs "
            f"{cost_of_fighting_each()/1e12:.1f} TJ, which is "
            f"unaffordable by orders of magnitude")


def _mem():
    ratio, fought, remembered = regard_is_worth()
    if ratio < 1e6:
        raise ArithmeticError(f"memory only saves {ratio:.1e}")
    return (f"remembering the outcome is free: engine/learning.py "
            f"puts erasing an ENTIRE brain at {remembered:.1e} J, "
            f"against {fought:.1e} J of fighting every decision -- a "
            f"ratio of {ratio:.1e}. REGARD IS THE MEMORY OF A "
            f"SETTLED CONTEST, and what it is worth is every contest "
            f"it prevents. That is why rank looks like a social fact "
            f"and prices out as a physical one")


def _residue():
    return ("what is still not derived is which contests are ever "
            "held. This says a settled order is worth enormously "
            "more than fighting, and it does not say how the first "
            "order is set or when it is re-opened -- the same shape "
            "as engine/frozen.py, which says a code is locked and is "
            "blind to which one. Something selects HAVING a rank "
            "order and is indifferent to WHO is where, so rank is "
            "arbitrary in the way the genetic code is arbitrary")


if __name__ == "__main__":
    armed, bare = taking_capacity(60.0, 1.75), taking_capacity(60.0)
    print(f"  armed {armed[0]:.0f} N at {armed[1]:.2f} m beats bare "
          f"{bare[0]:.0f} N at {bare[1]:.2f} m: {wins(armed, bare)}\n")
    spent, lost = contest_cost()
    print(f"  one fight: {spent/1e6:.1f} MJ + 10% of "
          f"{lost/1e9:.1f} GJ of life")
    print(f"  decisions over 20 years: {decisions():,.0f}")
    ratio, f, r = regard_is_worth()
    print(f"  fight each one: {f:.2e} J")
    print(f"  remember instead: {r:.2e} J")
    print(f"  ratio: {ratio:.2e}\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:52}{d[:26]}")
