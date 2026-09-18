"""What a skill is worth to the person who has it, and why that
stops tracking anything after a few generations.

engine/power.py got power from geometry -- a store is a point.
This is the other source: you are worth what the band cannot do
without you. That is not the VALUE of your skill, it is the value
divided by how many others have it, and how many others have it is
the number engine/craft.py needs to be large or the skill dies.

So the specialist and the band want opposite things about the same
number, and neither is being unreasonable.

Then inheritance breaks the link entirely. A claim copies exactly.
Ability does not. The gap between them is computable and it is the
whole of why there are bad kings -- no villainy required, just two
different heritabilities.
"""

import math

from engine.tradition import BAND, garbles
from engine.literacy import literacy_halflife, least_scribes

HERITABILITY = 0.50         # MEASURED-ish, parent-offspring on ability
FOUNDER_SIGMA = 2.58        # DERIVED below: best of a band
CLAIM_HERITABILITY = 1.0    # a written claim copies exactly


def pivotal(k):
    """Chance you are the one the band cannot replace. DERIVED."""
    return 1.0 / max(int(k), 1)


def specialist_power(value, k):
    """What a holder can extract. DERIVED."""
    return value * pivotal(k)


def secrecy_trade(value=1.0):
    """-> (k, power, half-life) for going it alone vs keeping it."""
    safe = least_scribes()
    return [(k, specialist_power(value, k), literacy_halflife(k))
            for k in (1, safe)]


# --- selection versus inheritance -----------------------------------
#
# Under selection the holder is the best of the band, which is the
# expected maximum of n draws -- about sqrt(2 ln n) sigma. Under
# inheritance the holder is whoever was born, and ability regresses
# by HERITABILITY every generation while the claim does not regress
# at all.


def best_of(n):
    """Expected max of n standard draws, in sigma. DERIVED."""
    return math.sqrt(2.0 * math.log(max(n, 2)))


def heir_ability(generations, founder=None):
    """-> (mean sigma, sd). DERIVED: regression to the mean."""
    f = best_of(BAND) if founder is None else founder
    r = HERITABILITY ** generations
    return f * r, math.sqrt(max(1.0 - r * r, 0.0))


def mismatch(generations):
    """Power held over ability warranted. DERIVED."""
    mean, _ = heir_ability(generations)
    return CLAIM_HERITABILITY / max(mean / best_of(BAND), 1e-12)


def heir_matches_founder(generations):
    """Chance the heir is as good as the one who earned it.

    This is the randomization: a competent king is not impossible,
    it is a tail probability, and it has a number.
    """
    f = best_of(BAND)
    mean, sd = heir_ability(generations)
    if sd <= 0:
        return 1.0 if mean >= f else 0.0
    z = (f - mean) / sd
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def one_in(generations):
    """-> int. One heir in how many is worthy. DERIVED."""
    p = heir_matches_founder(generations)
    return math.inf if p <= 0 else 1.0 / p


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_specialist_is_worth_their_scarcity_not_their_skill", _worth)
    t("the_secrecy_that_pays_is_the_secrecy_that_loses_it", _secret)
    t("inheritance_costs_two_and_a_half_sigma_of_competence", _cost)
    t("a_good_king_is_a_tail_probability_with_a_number", _king)
    return all(x for _, x, _ in res), res


def _worth():
    rows = [(k, pivotal(k)) for k in (1, 2, 5, 13, BAND)]
    if pivotal(1) <= pivotal(BAND):
        raise ArithmeticError("scarcity does not pay")
    return (f"you are worth what the band cannot do without, which "
            f"is the value of the skill divided by how many others "
            f"hold it: "
            + "; ".join(f"{k} holders -> {100*p:.0f}%" for k, p in rows)
            + f". The skill's value to the band does not appear in "
              f"that at all. A common skill of enormous worth buys "
              f"its holder nothing, and this is why the question "
              f"'how useful is it' is the wrong one")


def _secret():
    (k1, p1, h1), (k2, p2, h2) = secrecy_trade()
    if p1 <= p2 or h1 >= h2:
        raise ArithmeticError(f"{p1}/{h1} vs {p2}/{h2}")
    return (f"engine/craft.py needs {k2} holders or a skill is lost "
            f"in a few generations. Its holder wants {k1}. Going "
            f"alone is {p1/p2:.0f}x the power and {h2/h1:.0f}x "
            f"shorter a life for the skill -- {h1:.1f} generations "
            f"against {h2:.0f}. Neither party is being "
            f"unreasonable: the specialist's horizon is ONE LIFE "
            f"and the skill's survival is measured in generations, "
            f"so the individual optimum and the collective optimum "
            f"are different numbers for the same k. Lost crafts do "
            f"not need a catastrophe. They need someone who "
            f"profited by not teaching")


def _cost():
    sel = best_of(BAND)
    m5 = heir_ability(5)[0]
    if sel <= m5 * 2:
        raise ArithmeticError(f"{sel} vs {m5}")
    return (f"under selection the holder is the best of {BAND}, the "
            f"expected max of {BAND} draws = sqrt(2 ln {BAND}) = "
            f"{sel:.2f} sigma. Under inheritance the holder is "
            f"whoever was born, and ability regresses by "
            f"{HERITABILITY} a generation while a written claim "
            f"regresses by nothing: "
            + "; ".join(f"g{g} {heir_ability(g)[0]:.2f}s"
                        for g in (1, 2, 5, 10))
            + f". By the fifth generation the holding is "
              f"{mismatch(5):.0f}x what the ability warrants and the "
              f"heir is {m5:.2f} sigma -- indistinguishable from "
              f"anyone. Bad kings are two heritabilities, not bad "
              f"character")


def _king():
    rows = [(g, one_in(g)) for g in (1, 3, 5, 10)]
    if one_in(10) <= one_in(1):
        raise ArithmeticError("no drift")
    return (f"it is not impossible for an heir to deserve it, it is "
            f"a tail: the heir is drawn with mean "
            f"{HERITABILITY}^g x {best_of(BAND):.2f} and sd "
            f"sqrt(1-h^2g), so P(heir >= founder) is "
            + "; ".join(f"g{g} 1 in {n:.0f}" for g, n in rows)
            + f". That is the randomization -- a good king happens "
              f"at the rate chance allows and no faster, and the "
              f"rate is computable rather than chosen. Anything "
              f"drawing from this should draw from THIS, not from a "
              f"knob")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
