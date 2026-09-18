"""
Communication, and why it appears long before language.

engine/civ.py priced speech at 39 bit/s and said the value is
that it carries a selection another head already paid for. That
is language, and it is late. Almost everything that moves
signals -- and engine/group.py has the reason without having
noticed it.

A rank order costs contests. Sorted rather than all-pairs that
is n log n, so each member fights about log n times to find
their place: seven at a band of 144. engine/regard.py prices one
fight at 5.2 GJ of energy and expected life, so seven is most of
a lifetime's risk, and a group of 144 is unaffordable.

UNLESS THE OUTCOME IS ALREADY KNOWN. Reach and force are visible
before contact -- 80 cm2 of muscle against 40, or 1.75 m of haft
against a bare arm -- and when the asymmetry is visible there is
nothing to find out. A display settles it for a few seconds of
metabolism:

    a fight     5.2e9 J
    a display   9.7e2 J        a factor of five million

SO A SIGNAL IS A CONTEST NOT HELD, exactly as engine/regard.py
found regard to be a contest not repeated. It is not a courtesy
and not a precursor of language. It is the cheapest way to
settle something that has to be settled, and it appears wherever
rank does -- which is wherever a group is.

AND ITS CAPACITY SCALES WITH WHAT MUST BE DISTINGUISHED.
engine/comprehension.py counts constraints: 6 bind on a microbe
and 13 on a human, so 64 situations against 8,192. A signal must
separate the situations its sender needs separated, and log2 of
that count is the bits it must carry -- 6 for a microbe and 13
for us. That is why communication grows with understanding
rather than alongside it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DISPLAY_SECONDS = 10.0       # CHOSEN, how long a display lasts
VISIBLE_REACH_M = 0.1        # CHOSEN, reach difference that can be seen
VISIBLE_FORCE = 0.2          # CHOSEN, force ratio that can be seen


def display_cost(seconds=DISPLAY_SECONDS):
    """J to make a display. DERIVED: metabolism for its duration."""
    from engine.civ import FORAGER_W
    return FORAGER_W * seconds


def fight_cost():
    """J of energy and expected life. DERIVED via engine/regard.py."""
    from engine.regard import contest_cost
    spent, lost = contest_cost()
    return spent + lost


def settled_by_display(force_a, reach_a, force_b, reach_b):
    """-> bool. Is the outcome visible without contact? DERIVED."""
    if abs(reach_a - reach_b) > VISIBLE_REACH_M:
        return True
    hi = max(force_a, force_b, 1e-9)
    return abs(force_a - force_b) / hi > VISIBLE_FORCE


def saving():
    """-> ratio. What a display saves over a fight. DERIVED."""
    return fight_cost() / display_cost()


def signal_bits(organism):
    """Bits a signal must carry here. DERIVED via comprehension.

    A signal separates the situations its sender needs separated,
    and there are 2^constraints of those, so it needs one bit per
    binding constraint.
    """
    from engine.comprehension import binding, situations
    return math.log2(situations(organism)), len(binding(organism))


def contest_cost_with_display(n, visible=0.9):
    """J per head to settle rank in a group of n. DERIVED.

    Sorted contests are log n per head; a share of them are
    visible and cost a display instead of a fight.
    """
    per_head = math.log2(max(n, 2))
    return per_head * (visible * display_cost()
                       + (1 - visible) * fight_cost())


def affordable_group(visible=0.9, upto=500):
    """-> n. Where corpus benefit stops covering rank cost. DERIVED."""
    from engine.group import defence_value
    best = (1, 0.0)
    for n in range(2, upto):
        ben = defence_value(n)
        cost = contest_cost_with_display(n, visible)
        if ben - cost > best[1]:
            best = (n, ben - cost)
    return best[0]


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("a_signal_is_a_contest_not_held", _sig)
    t("it_works_when_the_asymmetry_is_visible", _vis)
    t("display_is_millions_of_times_cheaper", _cheap)
    t("capacity_scales_with_what_must_be_distinguished", _bits)
    t("and_it_is_what_lets_a_group_be_large", _grp)
    return all(o[1] for o in out), out


def _sig():
    f, d = fight_cost(), display_cost()
    if d >= f:
        raise ArithmeticError("a display costs as much as a fight")
    return (f"engine/group.py found each member must settle rank about "
            f"log n times -- seven at a band of 144 -- and "
            f"engine/regard.py prices one fight at {f/1e9:.1f} GJ, so "
            f"seven is most of a lifetime's risk. A SIGNAL IS A "
            f"CONTEST NOT HELD, exactly as regard is a contest not "
            f"repeated. Not a courtesy and not a precursor of "
            f"language -- the cheapest way to settle something that "
            f"has to be settled")


def _vis():
    from engine.inherit import force_from_area
    big, small = force_from_area(80e-4), force_from_area(40e-4)
    if not settled_by_display(big, 0.75, small, 0.75):
        raise ArithmeticError("a doubled muscle is not visible")
    if settled_by_display(big, 0.75, big, 0.75):
        raise ArithmeticError("an even match settles by display")
    return (f"reach and force are visible before contact: "
            f"{big:.0f} N against {small:.0f} N settles without a "
            f"blow, and so does 1.75 m of haft against a bare arm. "
            f"An even match does not -- there is nothing to read, so "
            f"it has to be fought. The signal carries information "
            f"only where information exists")


def _cheap():
    r = saving()
    if r < 1e5:
        raise ArithmeticError(f"a display only saves {r:.0e}")
    return (f"a fight is {fight_cost()/1e9:.1f} GJ and a display "
            f"{display_cost():.0f} J, a factor of {r:.1e}. That ratio "
            f"is why signalling is everywhere an organism has rank to "
            f"settle, which is everywhere there is a group -- long "
            f"before anything language-shaped")


def _bits():
    rows = [(o,) + signal_bits(o)
            for o in ("bacterium", "bee", "mouse", "human")]
    if rows[0][1] >= rows[-1][1]:
        raise ArithmeticError("signal capacity does not grow")
    return (f"a signal separates the situations its sender needs "
            f"separated, and engine/comprehension.py counts those as "
            f"2^constraints -- so the bits needed are one per "
            f"constraint: "
            + ", ".join(f"{o} {b:.0f}" for o, b, _n in rows)
            + ". COMMUNICATION GROWS WITH UNDERSTANDING rather than "
              "alongside it, because what must be said is what must "
              "be told apart")


def _grp():
    from engine.group import best_size
    plain, withsig = best_size()[0], affordable_group()
    if withsig <= plain:
        raise ArithmeticError(f"{plain} -> {withsig}")
    return (f"engine/group.py got an optimum of {plain} -- a family, "
            f"not a band -- because it charged every rank contest as "
            f"a fight. With nine in ten settled by display the "
            f"affordable group is {withsig}. Signalling is not a "
            f"refinement on group living, IT IS WHAT MAKES A GROUP "
            f"BIGGER THAN A FAMILY POSSIBLE")


if __name__ == "__main__":
    print(f"  a fight {fight_cost()/1e9:.1f} GJ, a display "
          f"{display_cost():.0f} J -- {saving():.1e}x\n")
    print(f"  {'organism':<12}{'constraints':>13}{'signal bits':>13}")
    for o in ("bacterium", "bee", "mouse", "human"):
        b, n = signal_bits(o)
        print(f"  {o:<12}{n:>13}{b:>13.0f}")
    from engine.group import best_size
    print(f"\n  group optimum: {best_size()[0]} charging fights, "
          f"{affordable_group()} with displays\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:48}{d[:30]}")
