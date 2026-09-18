"""
Turn off death and see what actually binds.

The proposal was reasonable: stop humans dying, give them all the
time there is, and let them learn their way to everything. It is
the rule-cancelling move this repository already uses -- switch
one rule off, see what the world does, then work out why.

It does not work, and the reason is worth more than the proposal
would have been.

    a brain holds 1e14 synapses at 4.7 bits    4.7e14 bits, 59 TB
    the optic nerve delivers 1e6 x 10 bit/s    1e7 bit/s
    so the store fills in                      1.49 YEARS

A normal life already pours 47 times the store through that nerve.
An immortal one pours 671,489 times. Every one of those multiples
after the first has to go somewhere, and there is nowhere.

TIME WAS NEVER THE CONSTRAINT. Neither is energy: Landauer says
erasing the entire store costs 1.4 microjoules, which is nothing
against 82 W. A body could clear and refill its whole memory
thousands of times a second and not notice the bill.

What binds is capacity, and capacity is reached before the child
can walk. So the thing a brain does cannot be accumulation -- it
saturates too early for that to be the story. It has to be
SELECTION: deciding what not to keep. An immortal learner is not a
better learner, it is the same learner discarding 671,488 times
more.

That also says what mapping a brain while it learns would show.
Not a store filling up. A filter changing what it lets through.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# MEASURED
SYNAPSES = 1.0e14
BITS_PER_SYNAPSE = 4.7          # Bartol et al., from spine-head sizes
OPTIC_FIBRES = 1.0e6
BITS_PER_FIBRE_S = 10.0
BODY_TEMP_K = 310.0
from engine.constants import YEAR_S as SECONDS_PER_YEAR  # one home


def store_bits():
    """bits a brain can hold. DERIVED."""
    return SYNAPSES * BITS_PER_SYNAPSE


def intake_bits_s():
    """bits/s arriving through one sense. DERIVED."""
    return OPTIC_FIBRES * BITS_PER_FIBRE_S


def fill_time_years():
    """yr to saturate. DERIVED. The number the proposal turns on."""
    return store_bits() / intake_bits_s() / SECONDS_PER_YEAR


def landauer_j(bits=None):
    """J to erase. DERIVED: kT ln2, the floor under forgetting."""
    from engine.constants import K_B
    return (bits if bits is not None else store_bits()) * \
        K_B * BODY_TEMP_K * math.log(2.0)


def forgetting_cost_fraction(times_per_second=1.0):
    """Fraction of the body's budget spent clearing memory. DERIVED."""
    from engine.biome import metabolism_w
    return landauer_j() * times_per_second / metabolism_w(70.0)


def lived_multiples(years):
    """How many times over a life overfills the store. DERIVED."""
    return intake_bits_s() * years * SECONDS_PER_YEAR / store_bits()


def what_binds(years):
    """-> (name, why). Cancel death and ask what is left. DERIVED."""
    if years * SECONDS_PER_YEAR * intake_bits_s() < store_bits():
        return "time", "the store is not full yet"
    if forgetting_cost_fraction(1.0) > 0.01:
        return "energy", "clearing memory costs a measurable share"
    return "capacity", (
        f"the store filled at {fill_time_years():.2f} years and "
        f"{lived_multiples(years):,.0f}x has come through since")


def immortality_experiment(lives=(1.0, 18.0, 70.0, 700.0, 1e6)):
    """-> [(years, multiples, what binds)]. The rule switched off."""
    return [(y, lived_multiples(y), what_binds(y)[0]) for y in lives]


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_store_fills_before_the_child_walks", _fill)
    t("forgetting_is_free", _free)
    t("immortality_buys_nothing", _immortal)
    t("so_a_brain_is_a_filter_not_a_store", _filter)
    return all(o[1] for o in out), out


def _fill():
    y = fill_time_years()
    if not 0.1 < y < 10.0:
        raise ArithmeticError(f"the store fills in {y:.2f} years")
    return (f"{store_bits():.2e} bits of synapse against "
            f"{intake_bits_s():.0e} bit/s from one nerve fills in "
            f"{y:.2f} YEARS -- before the child can walk, and through "
            f"the eye alone. Whatever a brain is doing after that, it "
            f"is not filling up")


def _free():
    f = forgetting_cost_fraction(1.0)
    fast = forgetting_cost_fraction(1000.0)
    if f > 1e-4:
        raise ArithmeticError(f"forgetting costs {100*f:.2f}% of a budget")
    return (f"Landauer puts the floor under erasing the entire store "
            f"at {landauer_j():.2e} J. Clearing and refilling all of "
            f"memory once a second costs {100*f:.1e}% of an 82 W body, "
            f"and a thousand times a second {100*fast:.1e}%. Energy "
            f"does not constrain forgetting, so nothing is being kept "
            f"because it was expensive to drop")


def _immortal():
    rows = immortality_experiment()
    binds = {b for _y, _m, b in rows if _y >= 18.0}
    if binds != {"capacity"}:
        raise ArithmeticError(f"something other than capacity binds: {binds}")
    life = [m for y, m, _ in rows if y == 70.0][0]
    forever = [m for y, m, _ in rows if y == 1e6][0]
    return (f"switch death off and nothing improves. A 70-year life "
            f"already pours {life:.0f}x the store through one nerve; a "
            f"million years pours {forever:,.0f}x. Every multiple past "
            f"the first has to go somewhere and there is nowhere. THE "
            f"PROPOSAL FAILS, and it fails for a reason worth more "
            f"than it would have been worth: time was never the "
            f"constraint, so removing its limit changes nothing")


def _filter():
    y = fill_time_years()
    if y > 5.0:
        raise ArithmeticError("the store lasts long enough to be a store")
    return (f"a store that saturates at {y:.2f} years cannot be what a "
            f"brain is for -- it would be finished before it was any "
            f"use. What is left is SELECTION: the work is deciding "
            f"what not to keep, and an immortal learner is the same "
            f"learner discarding more. That also says what mapping a "
            f"brain while it learns would show. Not a store filling "
            f"up. A filter changing what it lets through")


if __name__ == "__main__":
    print(f"  store        {store_bits():.2e} bits = "
          f"{store_bits()/8/1e12:,.0f} TB")
    print(f"  intake       {intake_bits_s():.0e} bit/s through the eye")
    print(f"  fills in     {fill_time_years():.2f} years\n")
    print(f"  {'lived':>12}{'multiples of the store':>26}{'binds':>12}")
    for y, m, b in immortality_experiment():
        print(f"  {y:>10,.0f}y{m:>26,.0f}{b:>12}")
    print(f"\n  erase everything: {landauer_j():.2e} J "
          f"({100*forgetting_cost_fraction():.1e}% of an 82 W body)\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:38]}")
