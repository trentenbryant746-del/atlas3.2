"""
Schooling, and what understanding is actually limited by.

engine/revolution.py found that handing over instructions costs
almost nothing -- a whole trade is 0.0003% of a brain. That is
true of ONE transfer and says nothing about a society's whole
stock of understanding, which is a different object with a
different limit.

Three numbers settle most of it.

WHAT ONE PERSON CAN HOLD. Forty thousand waking hours of being
taught, at the 39 bit/s engine/civ.py measured, is 5.6e9 bits --
about four trades. Not four thousand. A human is a small vessel
and the ceiling is the channel, not the storage: engine/learning.py
already showed the store fills in 1.49 years and the rest is
discarding.

WHAT A SOCIETY CAN HOLD. The corpus cannot exceed the number of
people holding it times what each holds, so a body of knowledge
needs a POPULATION to exist in. Today's corpus needs about
750,000 specialists as a floor -- that is not a claim about
universities, it is division.

WHAT IT COSTS. A person being schooled is not producing.
Eighteen years out of a fifty-year working life is 36% of it,
which is a larger standing tax than all the infrastructure in
engine/revolution.py put together.

And then the thing worth running: understanding grows, and the
question is what stops it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

LIFE_LEARN_HOURS = 40000.0    # CHOSEN, generous waking hours of teaching
WORKING_LIFE_YR = 50.0        # MEASURED
SPECIALIST_FRACTION = 0.01    # CHOSEN, share of people who can specialise
# CALIBRATED, not chosen. A Roman city held about 30 trades and
# 1800 Europe about 3,000 -- 1,800 years apart at a population of
# order 100 million with a percent specialising. That pair fixes
# the rate at 1.7e-8 trades per specialist-watt-year. The first
# value here was a guess of 2e-13, five orders of magnitude small,
# which made the corpus grow by 0.007 trades in six centuries and
# hid every limit behind an arithmetic that never moved.
DISCOVERY_PER_SURPLUS = 1.70e-8

# RECORDED: rough size of the shared corpus, in trade-equivalents
CORPUS = {"a village craft": 3, "a Roman city": 30,
          "1800 Europe": 3000, "today": 3_000_000}


def one_lifetime_bits(hours=LIFE_LEARN_HOURS):
    """Bits a person can be handed in a life. DERIVED via engine/civ.py."""
    from engine.civ import SPEECH_BITS_S
    return SPEECH_BITS_S * hours * 3600.0


def trades_per_person(hours=LIFE_LEARN_HOURS):
    """How many trades one head holds. DERIVED."""
    from engine.revolution import teaching_bits
    return one_lifetime_bits(hours) / teaching_bits()


def specialists_for(corpus_trades):
    """Minimum people needed to hold a corpus at all. DERIVED."""
    return max(corpus_trades / trades_per_person(), 1.0)


def holdable(pop, fraction=SPECIALIST_FRACTION):
    """Largest corpus a population can carry. DERIVED."""
    return pop * fraction * trades_per_person()


def schooling_tax(years):
    """Fraction of a working life spent not working. DERIVED."""
    return min(years / WORKING_LIFE_YR, 1.0)


def years_to_learn(corpus_trades, n_specialists):
    """Years one specialist needs. DERIVED.

    The first version divided the corpus by the MINIMUM people
    who could hold it, which by construction gives each of them a
    full head -- four trades, fifty years, a whole working life,
    for every corpus at every population. The tax was then 100%,
    the surplus zero, and nothing ever grew. How many specialists
    there are is set by the POPULATION, not by the minimum, and
    with more of them each learns a smaller share.
    """
    from engine.revolution import APPRENTICE_HOURS
    share = corpus_trades / max(n_specialists, 1.0)
    share = min(share, trades_per_person())
    return share * APPRENTICE_HOURS / (LIFE_LEARN_HOURS / WORKING_LIFE_YR)


def grow(pop, years=600, corpus0=30.0, fraction=SPECIALIST_FRACTION):
    """-> [(year, corpus, specialists, tax)]. Understanding, forward.

    Discovery needs people with surplus time; holding needs people
    at all. Both are population, which is why this cannot be run
    apart from engine/revolution.py.
    """
    from engine.civ import FORAGER_W
    c, out = corpus0, []
    cap = holdable(pop, fraction)
    for y in range(years + 1):
        need = specialists_for(c)
        tax = schooling_tax(years_to_learn(c, pop * fraction))
        surplus = pop * FORAGER_W * (1.0 - tax) * fraction
        c = min(c + surplus * DISCOVERY_PER_SURPLUS, cap)
        out.append((y, c, need, tax))
    return out


def what_limits(pop, fraction=SPECIALIST_FRACTION):
    """-> (name, why). DERIVED. Holding, or the tax, or neither."""
    h = grow(pop, fraction=fraction)
    last = h[-1]
    cap = holdable(pop, fraction)
    if last[1] >= cap * 0.999:
        return "holding", (
            f"the corpus reached {last[1]:,.0f} trades, which is every "
            f"trade {pop*fraction:,.0f} specialists can carry at "
            f"{trades_per_person():.1f} each")
    if last[3] >= 0.95:
        return "schooling", (
            f"a specialist needs "
            f"{years_to_learn(last[1], pop*fraction):,.0f} years of "
            f"schooling, which is a whole working life")
    return "neither yet", (
        f"corpus {last[1]:,.0f} of a holdable {cap:,.0f}, tax "
        f"{100*last[3]:.0f}%")


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("a_head_holds_about_four_trades", _head)
    t("a_corpus_needs_a_population_to_exist_in", _hold)
    t("schooling_is_the_largest_tax_here", _tax)
    t("understanding_grows_and_then_stops", _grow)
    t("what_stops_it_is_population", _pop)
    t("no_rule_prices_a_shared_foundation", _nofoundation)
    return all(o[1] for o in out), out


def _head():
    n = trades_per_person()
    if not 1.0 < n < 100.0:
        raise ArithmeticError(f"one head holds {n:.1f} trades")
    return (f"{LIFE_LEARN_HOURS:,.0f} waking hours of being taught at "
            f"39 bit/s is {one_lifetime_bits():.2e} bits -- about "
            f"{n:.0f} trades, not four thousand. A human is a small "
            f"vessel and the ceiling is the CHANNEL, not the storage: "
            f"engine/learning.py already showed the store fills in "
            f"1.49 years and the rest of a life is discarding")


def _hold():
    now = specialists_for(CORPUS["today"])
    rome = specialists_for(CORPUS["a Roman city"])
    if now <= rome:
        raise ArithmeticError("a bigger corpus needs fewer people")
    return (f"a corpus cannot exceed the people holding it times what "
            f"each holds, so knowledge needs a POPULATION to exist "
            f"in. A Roman city's {CORPUS['a Roman city']} trades need "
            f"{rome:.0f} specialists; today's {CORPUS['today']:,} need "
            f"{now:,.0f}. That is not a claim about universities, it "
            f"is division")


def _tax():
    from engine.revolution import INFRASTRUCTURE, infrastructure_cost
    school = schooling_tax(18.0)
    infra = infrastructure_cost(tuple(INFRASTRUCTURE))
    if school <= infra:
        raise ArithmeticError(f"schooling {school:.2f} vs infra {infra:.2f}")
    return (f"eighteen years out of a {WORKING_LIFE_YR:.0f}-year "
            f"working life is {100*school:.0f}% of it -- a larger "
            f"standing tax than every road, grid and aqueduct in "
            f"engine/revolution.py put together, which come to "
            f"{100*infra:.0f}%. A person being schooled is not "
            f"producing, and that is the whole cost of understanding")


def _grow():
    h = grow(60e6, years=3000)
    if h[-1][1] <= h[0][1] * 10:
        raise ArithmeticError(f"the corpus only reached {h[-1][1]:.0f}")
    return (f"60 million people take a corpus from {h[0][1]:.0f} trades "
            f"to {h[-1][1]:,.0f} over {h[-1][0]:,} years. That rate is "
            f"CALIBRATED against a recorded pair -- a Roman city at "
            f"30 trades and 1800 Europe at 3,000 -- rather than "
            f"picked, which the first version's guess was, at five "
            f"orders of magnitude too small")


def _pop():
    """CORRECTED. Holding does not bind and I had assumed it would."""
    rows = [(p, grow(p, years=3000)[-1][1], holdable(p))
            for p in (60e6, 1e9, 8e9)]
    if any(c >= cap * 0.01 for _p, c, cap in rows):
        raise ArithmeticError("holding came within a percent after all")
    slope = rows[2][1] / rows[0][1]
    if not 50 < slope < 500:
        raise ArithmeticError(f"the corpus scaled {slope:.0f}x")
    return (f"HOLDING NEVER BINDS, and the check that said it would "
            f"was wrong. At 8 billion the corpus reaches "
            f"{rows[2][1]:,.0f} trades of a holdable "
            f"{rows[2][2]:,.0f} -- three orders of headroom. What "
            f"limits understanding is the DISCOVERY RATE, which is "
            f"proportional to people with surplus: {slope:.0f}x the "
            f"corpus for {8e9/60e6:.0f}x the population. So "
            f"understanding is limited by population, and population "
            f"in engine/revolution.py is limited by phosphorus. The "
            f"chain closes on a mineral, but through the rate and "
            f"not through the holding")


def _nofoundation():
    """MISSING_RULE, named not tuned."""
    mine = years_to_learn(CORPUS["today"], 8e9 * SPECIALIST_FRACTION)
    real = 18.0                         # RECORDED, years of schooling
    if mine > real:
        raise ArithmeticError(f"the model already asks {mine:.0f} years")
    return (f"MISSING_RULE. This says a specialist today needs "
            f"{mine:.1f} years of schooling and the recorded figure "
            f"is about {real:.0f} -- short by {real/max(mine,0.01):.0f}x. "
            f"The reason is visible: dividing a corpus by its "
            f"specialists assumes they share NOTHING, and real ones "
            f"share an enormous common base -- language, numeracy, "
            f"how to read, what a machine is -- before any of them "
            f"specialises at all. No rule here prices a foundation "
            f"every specialist must hold, so the schooling cost is "
            f"understated and the number was NOT adjusted to hide it")


if __name__ == "__main__":
    print(f"  one head holds {trades_per_person():.1f} trades "
          f"({one_lifetime_bits():.2e} bits)\n")
    print(f"  {'corpus':<20}{'trades':>12}{'specialists':>14}")
    for k, v in CORPUS.items():
        print(f"  {k:<20}{v:>12,}{specialists_for(v):>14,.0f}")
    print()
    print(f"  {'population':>12}{'corpus in 3000 yr':>20}{'holdable':>16}")
    for pop in (60e6, 1e9, 8e9):
        print(f"  {pop/1e6:>10,.0f}M{grow(pop, years=3000)[-1][1]:>20,.0f}"
              f"{holdable(pop):>16,.0f}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:38]}")
