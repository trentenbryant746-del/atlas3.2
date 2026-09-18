"""You cannot specialize in something you cannot afford the tools for.

engine/craft.py counted the specialties a channel can KEEP and
engine/intricacy.py counted the designs they make possible. Both
assumed anyone could take one up. They cannot. A specialty is a
toolkit, a toolkit is other people's labour, and other people's
labour has to be bought out of a surplus that is not evenly held.

So two separate ceilings sit on top of the fidelity one:

  WHAT THE PLACE CAN AFFORD   total surplus / cost per specialist
  WHO CAN COMMAND A KIT       nobody buys a kit out of a share
                              too thin to cover it

They pull opposite ways on concentration and meet at a number.

And then the thing that everything above gets wrong by reporting
a single figure: the gain per head is a MEAN, and the distribution
it averages is skewed by construction. Scarcity pays 1/k, and k is
not the same for every craft. The mean is not what a typical
person gets, and the difference is computable rather than
rhetorical.
"""

import math

from engine.tradition import BAND
from engine.intricacy import settle, settle_network, spare_fraction, VILLAGE
from engine.trade import unit_cost
from engine.power import concentration, WALL_ADVANTAGE

DAYS_PER_PART = 50.0        # CHOSEN, labour-days to make one part
TOOL_LIFE_YEARS = 10.0
EAT_DAYS_YEAR = 365.0


def toolkit_days(parts, market):
    """Labour-days in one specialist's kit. DERIVED.

    Wright's law is already paid here: a bigger market makes the
    kit cheaper as well as making the specialty possible.
    """
    return parts * DAYS_PER_PART * unit_cost(market)


def specialist_cost(parts, market):
    """Food-days to keep one specialist for a year. DERIVED."""
    return EAT_DAYS_YEAR + toolkit_days(parts, market) / TOOL_LIFE_YEARS


def surplus_days(n, parts):
    """The food that can support non-farmers. DERIVED."""
    return n * EAT_DAYS_YEAR * spare_fraction(parts)


def affordable_specialists(n, parts, market=None):
    """How many the place can keep. DERIVED."""
    m = n if market is None else market
    return surplus_days(n, parts) / specialist_cost(parts, m)


def tooling_loss(n, parts, market=None):
    """Specialists lost to the price of kit alone. DERIVED."""
    m = n if market is None else market
    free = surplus_days(n, parts) / EAT_DAYS_YEAR
    return (free - affordable_specialists(n, parts, m)) / free


def best_spread(n, parts, market=None):
    """Holders the surplus should be split among. DERIVED.

    One person works one specialty however rich they are, so
    surplus concentrated in fewer hands than S/K sits idle; split
    thinner than that and no single share buys a kit. The optimum
    is not a preference, it is S/K.
    """
    return affordable_specialists(n, parts, market)


# --- and the average is not anybody ---------------------------------
#
# engine/merit.py: a specialist takes 1/k, where k is how many
# others hold the craft. Rare crafts pay many times what common
# ones do, so income is 1/k weighted by the k people standing at
# each depth -- which is right-skewed before anyone is greedy.
# Then engine/power.py's holders multiply the top of it.


def _shares(mean_depth):
    """-> [(income, headcount)]. Depths spread about the mean."""
    kmax = max(2, int(round(2 * mean_depth - 1)))
    return [(1.0 / k, float(k)) for k in range(1, kmax + 1)]


def income_stats(mean_depth, wall=WALL_ADVANTAGE):
    """-> (mean, median, top, top_over_median). DERIVED."""
    rows = sorted(_shares(mean_depth), reverse=True)
    heads = sum(h for _, h in rows)
    mean = sum(i * h for i, h in rows) / heads
    seen, median = 0.0, rows[-1][0]
    for inc, h in rows:
        seen += h
        if seen >= heads / 2.0:
            median = inc
            break
    top = rows[0][0] * concentration(BAND, wall)
    return mean, median, top, top / median


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_specialty_is_a_toolkit_and_a_toolkit_is_bought", _kit)
    t("intricacy_makes_its_own_tools_dearer", _dearer)
    t("concentration_has_a_right_answer_and_it_is_S_over_K", _spread)
    t("INVERTED_the_average_gain_is_nobodys_gain", _mean)
    return all(x for _, x, _ in res), res


def _kit():
    p, mkt = settle(), VILLAGE
    kit, cost = toolkit_days(p, mkt), specialist_cost(p, mkt)
    loss = tooling_loss(VILLAGE, p)
    if loss <= 0:
        raise ArithmeticError(f"{loss}")
    return (f"a {p:.1f}-part kit is "
            f"{kit:.0f} labour-days at {DAYS_PER_PART:.0f} a part, "
            f"so keeping one specialist for a year costs "
            f"{EAT_DAYS_YEAR:.0f} food-days of eating plus "
            f"{kit/TOOL_LIFE_YEARS:.0f} of kit = {cost:.0f}. A "
            f"village of {VILLAGE:.0f} with "
            f"{100*spare_fraction(p):.0f}% sparable supports "
            f"{affordable_specialists(VILLAGE, p):.0f} of them, not "
            f"the {surplus_days(VILLAGE, p)/EAT_DAYS_YEAR:.0f} the "
            f"food alone would allow. {100*loss:.0f}% of the "
            f"possible specialists are lost to the price of their "
            f"tools, and no rule above this one saw that cost")


def _dearer():
    pv, pn = settle(), settle_network()
    mkt = 40 * VILLAGE
    kv, kn = toolkit_days(pv, VILLAGE), toolkit_days(pn, mkt)
    if kn >= kv:
        raise ArithmeticError(f"{kv} {kn}")
    return (f"intricacy is a headwind on itself: more parts is a "
            f"dearer kit, {pv:.1f} parts at {kv:.0f} days against "
            f"{pn:.1f} parts at... {kn:.0f}. It went DOWN, because "
            f"Wright's law on a {mkt/VILLAGE:.0f}x market cuts unit "
            f"cost to {unit_cost(mkt):.2f} and that beats the "
            f"{pn/pv:.2f}x rise in part count. So the network does "
            f"not merely allow more specialties, it makes each one "
            f"cheaper to enter -- the two gains are separate and "
            f"they happen to point the same way. In a village that "
            f"did NOT trade, rising intricacy would price people "
            f"out of their own crafts")


def _spread():
    p = settle()
    g = best_spread(VILLAGE, p)
    idle = concentration(BAND, WALL_ADVANTAGE)
    if g <= 0 or g >= VILLAGE:
        raise ArithmeticError(f"{g}")
    return (f"one person works one specialty however rich they "
            f"are. Surplus held in fewer hands than S/K sits idle; "
            f"split thinner than K and no share buys a kit. So the "
            f"right number of holders is {g:.0f} of "
            f"{VILLAGE:.0f} -- {100*g/VILLAGE:.0f}% -- and it is "
            f"arithmetic, not a politics. engine/power.py's walled "
            f"holders take {idle:.1f}x an equal share, which puts "
            f"the working surplus in about "
            f"{100/idle:.0f}% of hands: below the optimum, so kit "
            f"goes unbought that the place could afford. "
            f"Concentration is not only unfair here, it is "
            f"IDLE CAPITAL, and that is a cost the holders pay too")


def _mean():
    """INVERTED. Fails if the mean ever represents the median."""
    p = settle_network()
    depth = 3.0
    mean, med, top, ratio = income_stats(depth)
    if abs(mean - med) < 0.05 * med:
        raise ArithmeticError(
            f"mean {mean:.3f} and median {med:.3f} agree -- the "
            f"distribution has been flattened somewhere")
    return (f"engine/intricacy.py reports a gain per head and that "
            f"figure is a MEAN. Income is 1/k for a craft held by "
            f"k people, and k is not the same for every craft, so "
            f"the distribution is skewed before anyone is greedy: "
            f"at mean depth {depth:.0f} the mean is {mean:.3f} and "
            f"the median {med:.3f}, {mean/med:.2f}x apart. The rare "
            f"craft pays {1/med:.1f}x the median on scarcity alone, "
            f"and a walled holder multiplies it again to "
            f"{ratio:.1f}x. So 'everyone is 1.3x better off' is a "
            f"statement no individual satisfies -- some are near "
            f"{ratio:.0f}x, most are at or under the median, and "
            f"the mean sits above the median by construction. Any "
            f"per-head number from this chain is the first moment "
            f"of a skewed distribution and should be quoted with "
            f"the other two")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
