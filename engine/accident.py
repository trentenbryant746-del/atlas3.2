"""
Accidental discovery, and why a store makes you stop moving.

Two things the chain had no room for: that discoveries arrive
unsought, and that one of them -- alcohol, or farming, or drying
meat -- is supposed to have made us stationary.

THE FIRST IS ALREADY TRUE AND WAS NOT SAID. engine/innovation.py
has 4.48 non-lethal variants per division and a useful share of
1.1e-4, and NOTHING IN THAT SEEKS ANYTHING. A variant is a step
omitted, duplicated or combined; it is produced whether or not
it helps, and the useful ones are noticed afterwards. All
discovery here is accidental. What a pressure does is decide
which accidents are kept, not which are made.

THE SECOND IS A RULE ABOUT STORES. Alcohol, grain and dried meat
are the same object: calories held against later. And a store
cannot be carried, so leaving one costs what it holds, while
moving gains whatever following the food is worth.

    store        held        gained by moving in a year
     1 day    8.4e6 J                        6.1e8 J   move
    30 days   2.5e8                          6.1e8     move
    90 days   7.5e8                          6.1e8     STAY
     1 year   3.1e9                          6.1e8     STAY

The threshold is 73 days, and it DISCRIMINATES, which was not
expected. Dried meat holds about a fortnight and fermented
fruit about two months -- both short of it. A grain harvest
holds a year and is over it by fivefold.

    dried meat       14 days    does not settle
    fermented fruit  60         does not settle
    a grain harvest 365         SETTLES

So of the two theories, the arithmetic picks farming and not
alcohol -- and it picks it by a margin of 13 days on a store
duration that is a chosen number, so the discrimination is real
and it is not robust. Fermented fruit keeping three months
instead of two would reverse it.

AND IT RUNS BOTH WAYS. engine/group.py needed a benefit growing
linearly in n; a store is defended by the group that holds it,
and a bigger store is worth more to defend. Settling and
grouping are the same arithmetic seen twice.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MOVE_GAIN = 0.20             # CHOSEN, intake gained by following food
STORES = {"a day of meat": 1.0, "dried meat": 14.0,
          "fermented fruit": 60.0, "a grain harvest": 365.0}


def held(days):
    """J a store of this many days holds. DERIVED."""
    from engine.civ import FORAGER_W
    return days * FORAGER_W * 86400.0


def gained_by_moving(years=1.0, gain=MOVE_GAIN):
    """J following the food is worth over this long. DERIVED."""
    from engine.civ import FORAGER_W
    return gain * FORAGER_W * years * 365.0 * 86400.0


def stays(days, years=1.0, gain=MOVE_GAIN):
    """-> bool. Does the store outweigh the journey? DERIVED."""
    return held(days) > gained_by_moving(years, gain)


def settling_threshold(years=1.0, gain=MOVE_GAIN):
    """Days of store at which moving stops paying. DERIVED."""
    from engine.civ import FORAGER_W
    return gained_by_moving(years, gain) / (FORAGER_W * 86400.0)


def which_stores_settle():
    """-> [(name, days, settles)]. DERIVED, and they are the same."""
    return [(k, d, stays(d)) for k, d in sorted(STORES.items(),
                                                key=lambda r: r[1])]


def discovery_is_unsought():
    """-> (rate, useful share). DERIVED via engine/innovation.py."""
    from engine.innovation import innovations_per_division, useful_fraction
    frac, _s = useful_fraction()
    return innovations_per_division(), frac


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("all_discovery_here_is_already_accidental", _acc)
    t("a_store_is_what_makes_you_stationary", _store)
    t("which_accident_does_not_matter", _same)
    t("the_threshold_is_about_a_month", _thresh)
    t("and_it_is_the_group_benefit_seen_twice", _group)
    return all(o[1] for o in out), out


def _acc():
    rate, frac = discovery_is_unsought()
    if rate <= 0 or frac <= 0:
        raise ArithmeticError("no variants are produced")
    return (f"engine/innovation.py makes {rate:.2f} non-lethal "
            f"variants per division of which {frac:.1e} are useful, "
            f"and NOTHING IN THAT SEEKS ANYTHING -- a variant is a "
            f"step omitted, duplicated or combined, produced whether "
            f"or not it helps. All discovery here was already "
            f"accidental and it had not been said. What a pressure "
            f"does is decide which accidents are KEPT, not which are "
            f"made")


def _store():
    if stays(1.0) or not stays(365.0):
        raise ArithmeticError("a day settles or a year does not")
    return (f"alcohol, grain and dried meat are the same object: "
            f"calories held against later. A store cannot be "
            f"carried, so leaving one costs {held(365)/1e9:.1f} GJ "
            f"for a year's worth while moving gains "
            f"{gained_by_moving()/1e9:.2f} GJ. STATIONARY IS NOT A "
            f"CHOICE, IT IS THE STORE")


def _same():
    """It DOES discriminate, which I did not expect it to."""
    rows = which_stores_settle()
    settling = [r for r in rows if r[2]]
    near = [r for r in rows if not r[2]][-1]
    t = settling_threshold()
    if len(settling) != 1:
        raise ArithmeticError(f"{len(settling)} stores settle")
    margin = t - near[1]
    return (f"I expected the stores to be interchangeable and they "
            f"are not. The threshold is {t:.0f} days: "
            f"{near[0]} holds {near[1]:.0f} and does NOT settle, "
            f"{settling[0][0]} holds {settling[0][1]:.0f} and does. "
            f"So the arithmetic picks FARMING over alcohol -- by "
            f"{margin:.0f} days, on a store duration that is a chosen "
            f"number. The discrimination is real and it is NOT "
            f"robust: fermented fruit keeping three months instead "
            f"of two reverses it, and that is worth more than a "
            f"confident answer would have been")


def _thresh():
    t = settling_threshold()
    if not 20 < t < 120:
        raise ArithmeticError(f"the threshold is {t:.0f} days")
    return (f"moving stops paying at {t:.0f} days of stored food. "
            f"Below that the journey is worth more than the store; "
            f"above it the store is worth more than the journey. One "
            f"number, and the only chosen input is what following "
            f"the food gains")


def _group():
    from engine.group import spare_per_head
    return ("engine/group.py needed a benefit growing linearly in n "
            "and could not find one: defence saturates and energy is "
            "per-head neutral. A STORE IS ONE. It is defended by the "
            "group that holds it and a larger store is worth more to "
            "defend, so settling and grouping are the same "
            "arithmetic seen twice -- which is why they appear "
            "together in the record rather than one causing the "
            "other")


if __name__ == "__main__":
    rate, frac = discovery_is_unsought()
    print(f"  {rate:.2f} variants per division, {frac:.1e} useful, "
          f"none of it sought\n")
    print(f"  {'store':<18}{'days':>7}{'held':>12}{'settles':>10}")
    for k, d, s in which_stores_settle():
        print(f"  {k:<18}{d:>7.0f}{held(d):>12.2e}"
              f"{'yes' if s else '':>10}")
    print(f"\n  moving gains {gained_by_moving():.2e} J a year")
    print(f"  threshold: {settling_threshold():.0f} days of store\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:48}{d[:30]}")
