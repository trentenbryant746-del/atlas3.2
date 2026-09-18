"""What one head learns and another head keeps.

Three scales of the same move -- knowing something you did not
observe:

  TRANSITIVITY   across items.  A>B and B>C gives you A>C for free.
  COMPOUNDING    across time.   What the dead knew, without meeting them.
  DIFFUSION      across bands.  What the next valley found, without going.

Each one has a price and each price is a countable number of
retellings, so each one has a ceiling. The ceiling is the rule.
"""

import math

BAND = 28                   # engine/signal.affordable_group

# --- TRANSITIVITY ---------------------------------------------------
#
# engine/group.py already USES transitivity to price a dominance
# order (n log2 n contests, not n(n-1)/2). It was never stated as
# a rule. Stated: a relation R is transitive when aRb and bRc
# forces aRc. That is the whole of it, and what it buys is
# knowledge of pairs you never tested.
#
# It is not free and it is not universal. "Beats" is transitive in
# a band and NOT transitive in rock-paper-scissors, which is why
# an intransitive triple is worth naming when it appears.

TRANSITIVE = {
    "taller than": "geometry composes",
    "beats": "strength is one number, until it is not",
    "upstream of": "water runs one way",
    "ancestor of": "time runs one way",
    "ripens before": "the seasons are ordered",
}
INTRANSITIVE = {
    "mates with": "no ordering, only a matching",
    "is near": "a chain of neighbours is not a neighbour",
    "beats, in three weapons": "the classic cycle",
}


def known_from(observed, n):
    """Pairs you know after `observed` links of a chain of n. DERIVED."""
    if observed >= n - 1:
        return n * (n - 1) // 2
    # observed adjacent links leave observed+1 items comparable
    return (observed + 1) * observed // 2


def transitive_leverage(n):
    """Facts known per fact observed, over a full chain. DERIVED."""
    return (n * (n - 1) / 2) / (n - 1) if n > 1 else 1.0


# --- COMPOUNDING ----------------------------------------------------
#
# A generation adds `a` items and hands on a fraction `r`. The
# stock obeys S' = rS + a, whose fixed point is a/(1-r). So the
# whole question of whether understanding accumulates is the
# question of how close r is to one. Nothing else in the equation
# matters.
#
# Two channels carry it, and they are four orders apart.

TELL_SECONDS = 300.0        # one telling, CHOSEN, a short story
EVENING_SECONDS = 3600.0    # an hour after dark, CHOSEN
NIGHTS = 365.0
CHILDHOOD_YEARS = 18.0      # provisioning span, engine/comprehension

EPIGENETIC_LOCI = 100.0     # marks that survive the germline, MEASURED-ish
EPIGENETIC_HALFLIFE = 2.0   # generations to half, MEASURED-ish

# Oral tradition is a game of telephone and the previous version of
# this module pretended otherwise -- it charged only for tellings
# nobody got round to, and none for tellings that came out wrong.
#
# TELEPHONE is the chance one retelling corrupts one item. It is
# CHOSEN. What is NOT chosen is what saves it: several people hold
# the same item, and a corruption that one holder makes the others
# do not, so the version that disagrees with the rest is the one
# that gets dropped. Consensus over m holders is error correction,
# and it is the reason the band matters to the corpus.
TELEPHONE = 0.10            # CHOSEN, corruption per retelling


def _log_choose(m, i):
    return (math.lgamma(m + 1) - math.lgamma(i + 1)
            - math.lgamma(m - i + 1))


def _binom_pmf(m, i, e):
    """P(exactly i of m). Log space: math.comb overflows float
    above about a thousand holders, which is well inside the
    populations this is now asked about."""
    if e <= 0.0:
        return 1.0 if i == 0 else 0.0
    lp = _log_choose(m, i) + i * math.log(e) + (m - i) * math.log1p(-e)
    return math.exp(lp) if lp > -745.0 else 0.0


def _binom_tail(m, k, e):
    """P(at least k of m go wrong). Exact, no sampling."""
    tot = 0.0
    for i in range(k, m + 1):
        term = _binom_pmf(m, i, e)
        tot += term
        if term == 0.0 and i > k:
            break
    return tot


def garbles(holders, e=TELEPHONE):
    """P(the consensus itself is wrong) per generation. DERIVED.

    Majority rules, and an even split is a coin. With one holder
    there is no consensus and the error passes straight through.
    """
    m = int(holders)
    if m <= 1:
        return e
    wrong = _binom_tail(m, m // 2 + 1, e)
    if m % 2 == 0:                        # a tie is settled by chance
        wrong += 0.5 * _binom_pmf(m, m // 2, e)
    return wrong


def tellings_per_childhood():
    """How many stories a child can sit through. DERIVED."""
    return (EVENING_SECONDS / TELL_SECONDS) * NIGHTS * CHILDHOOD_YEARS


def oral_capacity():
    """Items an oral tradition can carry. Coupon collector. DERIVED."""
    budget = tellings_per_childhood()
    k = 2.0
    for _ in range(200):                      # invert k ln k, no sweep
        k = budget / max(math.log(k), 1e-9)
    return k


def retention(channel, holders=BAND):
    """Fraction of the stock that survives one generation. DERIVED.

    Two independent losses, so they multiply: what nobody got
    round to retelling, and what got retold wrong and stuck.
    """
    if channel == "epigenetic":
        return 0.5 ** (1.0 / EPIGENETIC_HALFLIFE)
    if channel == "oral":
        untold = 1.0 - 1.0 / oral_capacity()
        return untold * (1.0 - garbles(holders))
    raise KeyError(channel)


def stock(channel, added_per_generation=1.0, holders=BAND):
    """Equilibrium understanding held. a/(1-r). DERIVED."""
    r = retention(channel, holders)
    return added_per_generation / (1.0 - r)


# --- DIFFUSION ------------------------------------------------------
#
# An accident does not have to happen to you. With b bands each
# with a per-year chance p, the FIRST discovery arrives b times
# sooner -- and then has to travel, which costs b ln b meetings.
#
# The two pull opposite ways, so there is a number of bands that
# finds and spreads a thing fastest. Fewer and nobody finds it;
# more and it never gets round.

MEETINGS_PER_YEAR = 2.0    # CHOSEN: two rendezvous a year


def first_discovery_years(b, p):
    """When the first band hits it. DERIVED."""
    return 1.0 / (b * p)


def spread_years(b, meetings=MEETINGS_PER_YEAR):
    """Coupon collector over bands. DERIVED."""
    return (b * math.log(b)) / meetings if b > 1 else 0.0


def settle_years(b, p):
    """First discovery plus spread to all. DERIVED."""
    return first_discovery_years(b, p) + spread_years(b)


def best_band_count(p, meetings=MEETINGS_PER_YEAR):
    """b where d/db of settle time is zero. DERIVED, no sweep."""
    # -1/(b^2 p) + (ln b + 1)/meetings = 0
    b = 2.0
    for _ in range(300):
        b = math.sqrt(meetings / (p * (math.log(b) + 1.0)))
    return b


def everyone_eventually(b, p, years):
    """Does it reach every band inside `years`? DERIVED."""
    return settle_years(b, p) <= years


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("transitivity_is_the_rule_that_buys_unobserved_pairs", _trans)
    t("an_intransitive_relation_buys_nothing", _intrans)
    t("oral_tradition_compounds_and_epigenetics_cannot", _compound)
    t("a_discovery_settles_across_bands_not_within_one", _diffuse)
    t("there_is_a_band_count_that_settles_fastest", _best)
    t("the_telephone_is_what_the_band_corrects", _phone)
    return all(x for _, x, _ in res), res


def _trans():
    n = BAND
    lev = transitive_leverage(n)
    if lev < 2:
        raise ArithmeticError(f"leverage {lev}")
    return (f"observe the {n-1} adjacent links of a chain of {n} and "
            f"transitivity hands you all {n*(n-1)//2} orderings -- "
            f"{lev:.1f} facts per fact. engine/group.py was already "
            f"spending this ({n} log2 {n} = "
            f"{n*math.log2(n):.0f} contests, not "
            f"{n*(n-1)//2}) without the rule being written down. "
            f"Transitive: {', '.join(sorted(TRANSITIVE)[:3])}")


def _intrans():
    if not INTRANSITIVE:
        raise ArithmeticError("no counterexample held")
    bad = "beats, in three weapons"
    return (f"the rule is not universal and the exceptions are the "
            f"interesting ones. {len(INTRANSITIVE)} relations here "
            f"compose to nothing: {sorted(INTRANSITIVE)}. '{bad}' -- "
            f"{INTRANSITIVE[bad]} -- means a dominance order can fail "
            f"to exist, and then the {BAND*(BAND-1)//2} contests come "
            f"back. An intransitive triple is worth naming when it "
            f"turns up, because it is the rule breaking, not noise")


def _phone():
    alone, band = stock("oral", holders=1), stock("oral", holders=BAND)
    g1, gb = garbles(1), garbles(BAND)
    if alone > band / 100:
        raise ArithmeticError(f"alone {alone}, band {band}")
    return (f"one retelling corrupts an item with p={TELEPHONE}, so a "
            f"single line of transmission loses {100*g1:.0f}% a "
            f"generation and its corpus tops out at {alone:.1f}a -- a "
            f"game of telephone, and nothing accumulates. {BAND} "
            f"holders vote, a corruption one makes the others do "
            f"not, and the consensus goes wrong with p={gb:.2e}. The "
            f"stock is {band:.0f}a, {band/alone:.0f}x. The band is "
            f"not an audience for the corpus, it is the error "
            f"correction ON the corpus, and without it oral "
            f"tradition carries about ten things")


def _compound():
    cap, oral, epi = oral_capacity(), stock("oral"), stock("epigenetic")
    if epi > 10 or oral < 100:
        raise ArithmeticError(f"oral {oral}, epi {epi}")
    return (f"a generation adds a and keeps r, so the stock settles "
            f"at a/(1-r) and the whole question is r. Oral: an hour "
            f"after dark for {CHILDHOOD_YEARS:.0f} years is "
            f"{tellings_per_childhood():.0f} tellings, and k ln k "
            f"inverts to {cap:.0f} items, so r = "
            f"{retention('oral'):.5f} and the stock is {oral:.0f}a. "
            f"Epigenetic: {EPIGENETIC_HALFLIFE:.0f}-generation "
            f"half-life gives r = {retention('epigenetic'):.2f} and "
            f"{epi:.1f}a, and the telephone costs "
            f"{garbles(BAND):.1e} on top. That is {oral/epi:.0f}x. "
            f"Epigenetics does "
            f"not compound -- it is a two-generation echo. Oral "
            f"tradition compounds, and that is the only channel that "
            f"does, which is why the accumulation is cultural")


def _diffuse():
    p, b = 1.0 / 500, 40          # one band, one chance in 500 years
    alone, many = first_discovery_years(1, p), settle_years(b, p)
    if many >= alone:
        raise ArithmeticError(f"{many} vs {alone}")
    return (f"one band waits {alone:.0f} years for a one-in-"
            f"{1/p:.0f} accident. {b} bands: the first hits at "
            f"{first_discovery_years(b, p):.0f} years and it travels "
            f"to the rest in {spread_years(b):.0f} more, so everyone "
            f"holds it by year {many:.0f} -- {alone/many:.0f}x sooner "
            f"than any one band could manage. Some bands get it "
            f"first; the coupon-collector tail is why the last one "
            f"waits so much longer than the median, and why it still "
            f"arrives")


def _best():
    p = 1.0 / 500
    b = best_band_count(p)
    here, fewer, more = settle_years(b, p), settle_years(b/4, p), settle_years(b*4, p)
    if here > fewer or here > more:
        raise ArithmeticError(f"{fewer} / {here} / {more}")
    return (f"discovery wants many bands and spread wants few, so "
            f"the sum has a floor: {b:.0f} bands settle a one-in-"
            f"{1/p:.0f} accident in {here:.0f} years, against "
            f"{fewer:.0f} at {b/4:.0f} bands and {more:.0f} at "
            f"{b*4:.0f}. Too few and nobody finds it, too many and it "
            f"never gets round. The optimum is not chosen -- it falls "
            f"out of 1/(bp) + b ln b / {MEETINGS_PER_YEAR:.0f} having "
            f"a derivative")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print(("  all hold" if ok else "  broken"))
