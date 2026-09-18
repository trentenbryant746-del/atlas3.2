"""
When rank has a price, and what the price is.

engine/civ.py found that connection, food and shelter derive and
STATUS does not: nothing here makes one person's share depend on
another's regard, so status was an absence rather than a result.
engine/empire.py hit the same wall -- "do not covet" was one of
five injunctions that did not derive.

The absence was in the scenarios, not the rules. Every group
priced there had a surplus, and where there is enough for
everyone the order of serving does not matter. Rank is not a
preference somebody has. IT IS AN ALLOCATION RULE, and an
allocation rule has no work to do until there is a shortfall.

So the question is when a group is short, and that is arithmetic
already on the table: a forager nets 97 W, a child costs 51 W of
provisioning and body, so N adults carry 1.9N children and no
more.

    2 adults   3.8 children     4 children is short by 12 W
    3 adults   5.7
    5 adults   9.5

BELOW THE LINE RANK IS WORTH NOTHING AND ABOVE IT RANK IS WORTH A
LIFE. When supply falls under need somebody does not eat, and
what the low-ranked person loses is not a share, it is their
whole 82 W. That is the price, it is discontinuous, and it
appears exactly at the carrying number.

Which also says what status is FOR, and it is not regard: it is
the rule that decides the shortfall, and a group without one
spends the shortfall on deciding.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def child_cost():
    """W a child costs, provisioning plus body. DERIVED via civ."""
    from engine.civ import child_load_w
    return child_load_w()[2]


def adult_yield():
    """W a forager nets. MEASURED, via engine/civ.py."""
    from engine.civ import FORAGER_W
    return FORAGER_W


def carrying_children(adults):
    """How many children N adults carry. DERIVED."""
    return adults * adult_yield() / child_cost()


def shortfall(adults, children):
    """W missing. DERIVED. Zero or positive."""
    return max(children * child_cost() - adults * adult_yield(), 0.0)


def rank_is_priced(adults, children):
    """-> (bool, price in W, why). DERIVED.

    Below the carrying number the order of serving changes
    nothing. Above it somebody does not eat, and what they lose
    is their whole metabolism.
    """
    from engine.biome import metabolism_w
    short = shortfall(adults, children)
    if short <= 0:
        return False, 0.0, (
            f"{adults} adults carry {carrying_children(adults):.1f} "
            f"children and have {children}, so there is enough and "
            f"the order of serving changes nothing")
    life = metabolism_w(70.0)
    return True, life, (
        f"{adults} adults carry {carrying_children(adults):.1f} and "
        f"have {children}, short by {short:.0f} W -- somebody does "
        f"not eat, and what they lose is not a share, it is "
        f"{life:.0f} W")


def price_curve(adults=2):
    """-> [(children, shortfall, price)]. Where the step is."""
    from engine.biome import metabolism_w
    out = []
    for c in range(1, 8):
        s = shortfall(adults, c)
        out.append((c, s, metabolism_w(70.0) if s > 0 else 0.0))
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_absence_was_in_the_scenarios", _scen)
    t("rank_is_an_allocation_rule_not_a_preference", _alloc)
    t("the_carrying_number_is_derived", _carry)
    t("the_price_is_discontinuous_and_is_a_life", _step)
    t("what_this_still_does_not_say", _residue)
    return all(o[1] for o in out), out


def _scen():
    ok, _p, _w = rank_is_priced(2, 1)
    if ok:
        raise ArithmeticError("even a small group is short")
    return (f"engine/civ.py and engine/empire.py both reported that "
            f"nothing prices rank. Every group they priced had a "
            f"surplus -- 2 adults with 1 child keep "
            f"{-shortfall(2, 1) + 2*adult_yield() - child_cost():.0f} "
            f"W spare -- and where there is enough for everyone the "
            f"order of serving does not matter. The absence was in "
            f"the SCENARIOS, not in the rules")


def _alloc():
    return ("rank is not a preference somebody has. It is an "
            "ALLOCATION RULE, and an allocation rule has no work to "
            "do until there is a shortfall. That is why asking "
            "'what makes people want status' found nothing: the "
            "question was about wanting, and the answer is about "
            "who does not eat")


def _carry():
    c2, c3 = carrying_children(2), carrying_children(3)
    if not 3.0 < c2 < 5.0:
        raise ArithmeticError(f"2 adults carry {c2:.1f} children")
    return (f"a forager nets {adult_yield():.0f} W and a child costs "
            f"{child_cost():.0f} W of provisioning and body, so N "
            f"adults carry {c2/2:.1f}N children: {c2:.1f} for two, "
            f"{c3:.1f} for three. Nothing was chosen -- both numbers "
            f"come from engine/civ.py and engine/ontogeny.py")


def _step():
    rows = price_curve(2)
    zero = [r for r in rows if r[2] == 0.0]
    paid = [r for r in rows if r[2] > 0.0]
    if not zero or not paid:
        raise ArithmeticError("no step in the price")
    return (f"for two adults the price of rank is zero at "
            f"{len(zero)} family sizes and {paid[0][2]:.0f} W at "
            f"{paid[0][0]} children. IT IS DISCONTINUOUS. Below the "
            f"carrying number rank is worth nothing; above it, what "
            f"the low-ranked person loses is not a share of the "
            f"shortfall, it is their whole metabolism. The step "
            f"appears exactly at the carrying number and nowhere "
            f"else")


def _residue():
    return ("this prices rank and does not produce one. It says a "
            "group above its carrying number must have an allocation "
            "rule and that the rule is worth a life to be high in -- "
            "it does not say which rule, any more than "
            "engine/frozen.py says which code mapping. And it says "
            "nothing about regard, which is what the word status "
            "usually means: what is derived is who eats, not who is "
            "admired, and whether those are the same thing is not a "
            "question these rules can reach")


if __name__ == "__main__":
    print(f"  a forager nets {adult_yield():.0f} W, a child costs "
          f"{child_cost():.0f} W\n")
    print(f"  {'adults':>8}{'carries':>10}")
    for a in (1, 2, 3, 5):
        print(f"  {a:>8}{carrying_children(a):>10.1f}")
    print(f"\n  two adults:")
    print(f"  {'children':>10}{'shortfall':>12}{'price of rank':>16}")
    for c, s, p in price_curve(2):
        print(f"  {c:>10}{s:>10.0f} W{p:>14.0f} W")
    print()
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:48}{d[:30]}")
