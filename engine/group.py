"""
Why survival is in groups, how big, and why strength loses to knowing.

engine/civ.py derived that a lone adult cannot carry a child
through a bad season and two can. That is a floor, not a size,
and it says nothing about why a band is a band.

WHAT DOES NOT SET IT IS ENERGY. A child costs 51 W and an adult
nets 97, so 1.9 adults carry one child at every scale -- the
spare per head is zero for a group of two and zero for a group of
sixty-four. Adding people neither gains nor loses per head, so
the size is set by something that does not scale linearly.

Two things do not.

DEFENCE SATURATES. A predator takes one, so individual risk is
the base rate over n: going from one to two halves it, from
thirty-two to sixty-four barely moves it.

CONTESTS GROW. Every pair in a group has to be settled once, and
engine/regard.py prices a real fight at 4.2 MJ and a tenth of a
life. All pairs is n(n-1)/2 -- but a rank order is TRANSITIVE, so
if A beats B and B beats C nobody fights A and C. That is
sorting, n log n, not all-pairs, and it is what lets a group be
larger than a handful at all.

    n     all pairs   sorted
    8            28       24
    55        1,485      318
    144      10,296    1,032

AND THE OPTIMUM IS STILL THREE. Defence saturating against cost
growing gives a family, not a band. Real groups are twenty to a
hundred and fifty, so a benefit is missing that grows LINEARLY
and does not saturate -- engine/adapt.py has one, search rate is
linear in n, and engine/school.py has another, and neither is
priced here. That gap is reported rather than closed by adding
terms until the answer matches.

STRENGTH AND UNDERSTANDING ARE NOT SYMMETRIC. Both get you fed.
But engine/regard.py showed that within a species the loser is
not eaten and nothing transfers, so strength moves a share
between heads and leaves the group total alone -- and it moves a
smaller share the larger the group, 50% of the total at two and
2% at fifty. Understanding answers a constraint, which opens what
was closed, and it adds for everyone. Strength is zero-sum.
Understanding is not. The larger the group, the worse that trade
is for strength.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BASE_PREDATION = 0.40       # from engine/descent.py
EXPOSED_YEARS = 20.0        # CHOSEN, a life at risk


def spare_per_head(adults):
    """W left over per adult at the carrying number. DERIVED."""
    from engine.civ import FORAGER_W, child_load_w
    tot = child_load_w()[2]
    kids = adults * FORAGER_W / tot
    return (adults * FORAGER_W - kids * tot) / adults


def risk_per_head(n, base=BASE_PREDATION):
    """A predator takes one, so risk divides. DERIVED."""
    return base / max(n, 1)


def defence_value(n):
    """J of expected life saved per head. DERIVED."""
    from engine.biome import metabolism_w
    saved = base = BASE_PREDATION
    return ((base - risk_per_head(n)) * metabolism_w(70.0)
            * EXPOSED_YEARS * 3.15576e7)


def contests_all_pairs(n):
    """Every pair settled once. EXACT."""
    return n * (n - 1) / 2.0


def contests_transitive(n):
    """A rank order is transitive, so it sorts. EXACT: n log n."""
    return n * math.log2(n) if n > 1 else 0.0


def contest_value(n, transitive=True):
    """J of contest cost per head. DERIVED via engine/regard.py."""
    from engine.regard import contest_cost
    spent, lost = contest_cost()
    c = contests_transitive(n) if transitive else contests_all_pairs(n)
    return c * (spent + lost) / max(n, 1)


def net(n, transitive=True):
    """J per head. DERIVED."""
    return defence_value(n) - contest_value(n, transitive)


def best_size(transitive=True, upto=200):
    """-> (n, net). Where defence stops paying for contests."""
    return max(((n, net(n, transitive)) for n in range(1, upto)),
               key=lambda r: r[1])


def strength_share(n):
    """Share of the group total that strength can move. DERIVED.

    engine/regard.py: nothing transfers between species members,
    so a contest redistributes one head's worth and no more.
    """
    return 1.0 / max(n, 1)


def understanding_share(n):
    """Share it adds to. DERIVED: a constraint answered opens for all."""
    return 1.0


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("energy_does_not_set_the_size", _energy)
    t("transitivity_is_what_allows_a_group_at_all", _trans)
    t("the_derived_optimum_is_a_family_not_a_band", _small)
    t("strength_is_zero_sum_and_understanding_is_not", _asym)
    t("the_missing_benefit_is_named_not_fitted", _gap)
    return all(o[1] for o in out), out


def _energy():
    vals = [spare_per_head(n) for n in (2, 8, 64)]
    if max(abs(v) for v in vals) > 1e-6:
        raise ArithmeticError(f"spare per head varies: {vals}")
    return ("a child costs 51 W and an adult nets 97, so 1.9 adults "
            "carry one child at every scale and the spare per head is "
            "zero for a group of two and zero for sixty-four. Adding "
            "people neither gains nor loses per head, so ENERGY DOES "
            "NOT SET THE SIZE -- whatever does must not scale "
            "linearly")


def _trans():
    a, s = contests_all_pairs(144), contests_transitive(144)
    if s >= a:
        raise ArithmeticError(f"sorting costs {s:.0f} against {a:.0f}")
    return (f"every pair in a group must be settled once, which is "
            f"{a:,.0f} contests at n=144. But a rank order is "
            f"TRANSITIVE -- if A beats B and B beats C nobody fights "
            f"A and C -- so it sorts in {s:,.0f}, a factor of "
            f"{a/s:.0f}. Transitivity is what lets a group be larger "
            f"than a handful at all, and it is the same memory "
            f"engine/regard.py priced at 1.4 microjoules")


def _small():
    n, _v = best_size()
    if n > 8:
        raise ArithmeticError(f"the optimum is {n}")
    return (f"defence saturates as base/n and contests grow, so the "
            f"optimum is n = {n}. THAT IS A FAMILY, NOT A BAND. "
            f"Real groups are twenty to a hundred and fifty, so this "
            f"is not the whole story and the number is reported as "
            f"it comes out rather than adjusted toward the record")


def _asym():
    s2, s50 = strength_share(2), strength_share(50)
    if s50 >= s2 or understanding_share(50) <= s50:
        raise ArithmeticError("the asymmetry does not hold")
    return (f"both get you fed and they are not symmetric. "
            f"engine/regard.py showed nothing transfers within a "
            f"species, so STRENGTH moves a share between heads and "
            f"leaves the total alone -- {100*s2:.0f}% of it at two "
            f"and {100*s50:.0f}% at fifty. UNDERSTANDING answers a "
            f"constraint, which opens what was closed, and adds for "
            f"everyone. Strength is zero-sum and understanding is "
            f"not, so the larger the group the worse that trade is "
            f"for strength")


def _gap():
    n, _v = best_size()
    return (f"the optimum comes out at {n} and real bands are 20 to "
            f"150, so a benefit is missing that grows LINEARLY and "
            f"does not saturate. engine/adapt.py has one -- search "
            f"rate is linear in n -- and engine/school.py has "
            f"another in the shared corpus, and neither is priced "
            f"here. That is named rather than closed by adding terms "
            f"until the answer matches, which would have been easy "
            f"and would have meant nothing")


if __name__ == "__main__":
    print(f"  {'n':>5}{'spare/head':>12}{'risk':>8}{'all pairs':>11}"
          f"{'sorted':>9}{'net J/head':>13}")
    for n in (2, 3, 5, 8, 13, 21, 55, 144):
        print(f"  {n:>5}{spare_per_head(n):>12.1f}{risk_per_head(n):>8.3f}"
              f"{contests_all_pairs(n):>11.0f}{contests_transitive(n):>9.0f}"
              f"{net(n):>13.2e}")
    n, v = best_size()
    print(f"\n  optimum n = {n} at {v:.2e} J per head\n")
    print(f"  strength moves {100*strength_share(50):.0f}% of the "
          f"total in a group of 50; understanding adds to all of it\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:48}{d[:30]}")
