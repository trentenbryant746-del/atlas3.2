"""How complicated a thing can get, and what stops it.

An artifact is a composition of skills -- a hafted axe is stone
working AND cordage AND wood. So the artifacts a population can
build are the subsets of the skills it holds SIMULTANEOUSLY, and
that is 2**s, which means intricacy is exponential in
specialization and specialization is what the channel allows.

That gives a loop, and the loop is the point:

    a surplus       lets people stop farming
    -> scribes      let the corpus hold more
    -> specialties  let artifacts compose more parts
    -> technology   raises the surplus
    -> back to the top

engine/literacy.py already found the two ends of it: writing is
floored by the granary needing an account and CEILED by the food
that can feed a non-farmer. So the question is whether the loop
climbs or sits, and that is a fixed point, not an opinion.
"""

import math

from engine.tradition import BAND, oral_capacity
from engine.craft import best_depth
from engine.literacy import copy_error, spread, ADMIN_DEMAND
from engine.trade import LEARNING_RATE

YIELD_PER_SKILL = 1.10      # CHOSEN, what one craft adds to output
COPY_LIFE_YEARS = 100.0     # MEASURED-ish, a written surface
COPIES_PER_YEAR = 250.0     # CHOSEN, a working scribe
VILLAGE = 912.0             # engine/disease.critical_community


def designs(s):
    """Distinct artifacts from s skills held at once. DERIVED."""
    return 2.0 ** s - 1.0


def parts_afforded(corpus):
    """Most parts an artifact can have if every design is kept."""
    return math.log2(max(corpus, 1.0) + 1.0)


def written_corpus(scribes):
    """Distinct items a scribal class can keep alive. DERIVED.

    A written surface rots, so the corpus is not what was ever
    written -- it is what can be recopied before it goes.
    """
    return scribes * COPIES_PER_YEAR * COPY_LIFE_YEARS


def yield_ratio(s):
    """Output over subsistence at s specialties. DERIVED."""
    return YIELD_PER_SKILL ** s


def spare_fraction(s):
    """Who can be fed without farming. DERIVED."""
    r = yield_ratio(s)
    return (r - 1.0) / r


def turn(s, n=VILLAGE, passes=2, years=2000.0, market=None):
    """One pass round the loop. -> next s. DERIVED."""
    from engine.trade import productivity
    gain = 1.0 if market is None else productivity(market)
    r = yield_ratio(s) * gain
    ceil = max((r - 1.0) / r, ADMIN_DEMAND)
    f = spread(1.0 / n, years, ceiling=ceil)
    corpus = written_corpus(f * n)
    by_channel = best_depth(int(n), copy_error(passes))[1]
    return min(by_channel, parts_afforded(corpus)), f, corpus


def settle(n=VILLAGE, passes=2, rounds=40, market=None):
    """Fixed point of the loop. DERIVED, not searched."""
    s = 2.0
    for _ in range(rounds):
        s = turn(s, n, passes, market=market)[0]
    return s


def settle_network(villages=40, passes=2):
    """The same loop with a region in touch. DERIVED."""
    mkt = villages * VILLAGE
    return settle(n=mkt, passes=passes, market=mkt)


# --- and whether any of it makes anyone better off ------------------
#
# Everything above raises TOTAL output. Per head is a different
# question and it has a different answer, so it gets its own
# arithmetic rather than being assumed to follow.


def malthus_exponent():
    """How per-capita surplus scales with population. DERIVED.

    Two things rise with N and one rises faster than both.

      Wright      output/worker as N**(-log2(LEARNING_RATE))
      skills      s ~ log2(N), so yield as N**log2(YIELD_PER_SKILL)
      mouths      food needed as N**1

    Add the exponents on the supply side and subtract the demand
    side. Above zero the place gets richer per head; below, it
    does not, whatever the technology is doing.
    """
    wright = -math.log2(LEARNING_RATE)
    skills = math.log2(YIELD_PER_SKILL)
    return wright + skills - 1.0


def oral_fixed_point():
    """Where the loop sits with no writing at all. DERIVED."""
    by_channel = best_depth(BAND)[1]
    return min(by_channel, parts_afforded(oral_capacity()))


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("intricacy_is_exponential_in_specialization", _exp)
    t("speech_is_a_stable_trap_and_not_a_slow_climb", _trap)
    t("writing_moves_the_binding_constraint_to_people", _bind)
    t("the_loop_closes_on_a_number_and_it_is_not_infinity", _fix)
    t("a_region_in_touch_beats_a_village_that_is_not", _region)
    t("INVERTED_the_loop_does_not_escape_malthus", _malthus)
    return all(x for _, x, _ in res), res


def _exp():
    a, b = best_depth(BAND)[1], best_depth(BAND, copy_error(2))[1]
    if designs(b) <= designs(a):
        raise ArithmeticError(f"{a} {b}")
    return (f"an artifact is a composition -- a hafted axe is stone "
            f"AND cordage AND wood -- so what a group can build is "
            f"the subsets of what it holds at once: 2^s - 1. A band "
            f"of {BAND} speaking holds {a} specialties and can "
            f"therefore build {designs(a):.0f} distinct things. "
            f"Writing takes it to {b}, and {designs(b):.0f}. "
            f"{designs(b)/designs(a):.0f}x from the same people. "
            f"Intricacy is exponential in specialization and "
            f"specialization is linear in the channel, which is why "
            f"the channel is worth more than it looks")


def _trap():
    s = oral_fixed_point()
    cap = parts_afforded(oral_capacity())
    chan = best_depth(BAND)[1]
    if s != chan or cap <= chan:
        raise ArithmeticError(f"{s} {cap} {chan}")
    return (f"speech is not a slow version of writing, it is a "
            f"fixed point. The corpus could hold {cap:.1f} parts' "
            f"worth of designs, but fidelity only supports {chan} "
            f"specialties, so the binding constraint is the channel "
            f"and NOTHING the band does relieves it -- more people "
            f"means more mouths on the same {oral_capacity():.0f}-"
            f"item ceiling, and the ceiling is one lifetime of "
            f"evenings. An oral society is not early. It is at "
            f"equilibrium, and it will sit there indefinitely "
            f"unless something changes the transmission")


def _bind():
    n = VILLAGE
    chan = best_depth(int(n), copy_error(2))[1]
    f = spread(1.0 / n, 2000.0)
    corpus = written_corpus(f * n)
    cap = parts_afforded(corpus)
    if chan <= cap:
        raise ArithmeticError(f"channel {chan} still binds under {cap}")
    return (f"in a village of {n:.0f} the written channel would "
            f"support {chan} specialties, but {100*f:.0f}% literacy "
            f"gives {f*n:.0f} scribes, a corpus of "
            f"{corpus:.0f} items that can be recopied before they "
            f"rot, and only {cap:.1f} parts of design. The binding "
            f"constraint has MOVED: speech was limited by fidelity, "
            f"which nothing could fix from inside; writing is "
            f"limited by how many people can be spared from the "
            f"fields, which yield can fix. That is the difference "
            f"between a trap and a loop")


def _fix():
    s = settle()
    oral = oral_fixed_point()
    r, sp = yield_ratio(s), spare_fraction(s)
    if s <= oral or not math.isfinite(s):
        raise ArithmeticError(f"{s} vs {oral}")
    return (f"iterating surplus -> scribes -> corpus -> specialties "
            f"-> surplus settles at {s:.1f} parts, "
            f"{designs(s):.0f} designs, a {r:.2f}x yield and "
            f"{100*sp:.0f}% of people off the land -- against {oral} "
            f"and {designs(oral):.0f} for speech. It converges "
            f"rather than running away, because the corpus enters "
            f"the intricacy as a LOGARITHM while the designs come "
            f"out as an exponent: doubling what is written buys one "
            f"more part. So the loop climbs and then crawls, and "
            f"every further step costs twice the last. That is a "
            f"fixed point, not a takeoff, and anything claiming a "
            f"takeoff has to say which term it changed")


def _region():
    from engine.trade import productivity
    one, many = settle(), settle_network()
    mkt = 40 * VILLAGE
    if many <= one:
        raise ArithmeticError(f"{one} {many}")
    return (f"a village alone settles at {one:.1f} parts. Forty "
            f"villages in touch -- {mkt:.0f} people inside a 16 km "
            f"radius, reachable because knowledge is the one cargo "
            f"with no range limit -- settle at {many:.1f} parts and "
            f"{designs(many):.3g} designs, with "
            f"{productivity(mkt):.1f}x the output per worker from "
            f"Wright's law alone. Nobody built a city. The gain a "
            f"city is credited with comes from the size of the "
            f"corpus's audience, not from standing close together")


def _malthus():
    """INVERTED. Fails if the loop quietly makes anyone richer.

    Every other check here reports a rise. This one asks whether
    any of it lands per head, and the answer is no -- which has
    to be stated, not left for a reader to assume otherwise.
    """
    e = malthus_exponent()
    if e >= 0:
        raise ArithmeticError(
            f"per-capita surplus scales as N**{e:.3f}: the loop "
            f"escapes, and something has been assumed that should "
            f"have been derived")
    n1, n2 = VILLAGE, 40 * VILLAGE
    return (f"total output rises the whole way up this module. Per "
            f"HEAD it does not. Wright gives N**"
            f"{-math.log2(LEARNING_RATE):.3f} and skills give "
            f"N**{math.log2(YIELD_PER_SKILL):.3f} against mouths at "
            f"N**1, so surplus per person goes as "
            f"N**{e:.3f} -- growing the network {n2/n1:.0f}x leaves "
            f"each person {(n2/n1)**e:.2f}x as well off. The model "
            f"produces exactly the world it should: rising "
            f"population, rising technology, flat living standards. "
            f"Escape needs the supply exponents to clear 1.0 and "
            f"they sum to {e+1:.3f}. NOTHING ON THIS CHAIN CLOSES "
            f"THAT GAP. It is named here rather than hidden in a "
            f"total that keeps going up")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
