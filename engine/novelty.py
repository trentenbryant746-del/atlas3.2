"""Why there is always something new and always less of it.

Two facts that look contradictory and are not.

  A design space gets USED UP. Once a combination has been found
  it is not novel again, so the chance a trial lands on something
  new falls as the explored fraction rises.

  A design space also GROWS. engine/intricacy.py has designs at
  2**s with s ~ log2(corpus) and corpus ~ N, so the space itself
  is proportional to population. More people is a bigger space to
  be new in, not merely more people looking.

Put together they give a steady state rather than exhaustion --
and the steady state depends on the GROWTH rate of population,
not its size, which is the part that is not obvious.

Then the separate effect that actually makes novelty per person
fall: a design of p parts needs someone who holds all p, and
nobody holds many. So inventing takes a TEAM, the team grows with
intricacy, and intricacy grows with the log of the corpus.
"""

import math

from engine.intricacy import (settle, settle_network, parts_afforded,
                              written_corpus, VILLAGE)
from engine.literacy import spread

TRIALS_PER_HEAD_YEAR = 0.01   # CHOSEN, attempts at something new
SPECIALTIES_PER_HEAD = 1.0    # one craft each, engine/craft.py
POP_GROWTH = 0.001            # MEASURED-ish, pre-industrial, per year


def space(n):
    """Designs that exist to be found at population n. DERIVED.

    corpus ~ n, s = log2(corpus), designs = 2**s = corpus. The
    exponent and the logarithm cancel, so the space is LINEAR in
    population -- which is why it can be both used up and never
    used up.
    """
    f = spread(1.0 / max(n, 2.0), 2000.0)
    return written_corpus(f * n)


def explored_fraction(growth=POP_GROWTH, trials=TRIALS_PER_HEAD_YEAR):
    """Steady-state share of the space already found. DERIVED.

    da/dt = (trials/c)(1-a) - a*growth, where c is space per head.
    Setting it to zero: a* = trials / (trials + c*growth).
    """
    c = space(VILLAGE) / VILLAGE
    return trials / (trials + c * growth)


def novel_fraction(growth=POP_GROWTH, trials=TRIALS_PER_HEAD_YEAR):
    """Share of trials that land on something new. DERIVED."""
    return 1.0 - explored_fraction(growth, trials)


def team_size(n):
    """People needed to hold every part of one new design. DERIVED."""
    parts = parts_afforded(space(n))
    return max(1.0, parts / SPECIALTIES_PER_HEAD)


def novel_per_head(n, growth=POP_GROWTH):
    """New designs per person per year. DERIVED."""
    return TRIALS_PER_HEAD_YEAR * novel_fraction(growth) / team_size(n)


def novel_total(n, growth=POP_GROWTH):
    """New designs a year, whole population. DERIVED."""
    return n * novel_per_head(n, growth)


def multiple(n1, n2, growth=POP_GROWTH):
    """-> (per-head ratio, total ratio). DERIVED.

    The number asked for: what happens to novelty when the
    population goes from n1 to n2.
    """
    return (novel_per_head(n2, growth) / novel_per_head(n1, growth),
            novel_total(n2, growth) / novel_total(n1, growth))


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_space_grows_as_fast_as_it_is_used_up", _space)
    t("novelty_survives_on_growth_not_on_size", _growth)
    t("a_new_design_needs_a_team_and_the_team_grows", _team)
    t("per_head_novelty_falls_as_one_over_log_population", _mult)
    return all(x for _, x, _ in res), res


def _space():
    a, b = space(VILLAGE), space(40 * VILLAGE)
    if not 0.5 < (b / a) / 40.0 < 2.0:
        raise ArithmeticError(f"space is not linear in n: {b/a}")
    return (f"designs are 2**s and s is log2(corpus), so the "
            f"exponent and the logarithm cancel and the space is "
            f"LINEAR in population: {a:.3g} designs at "
            f"{VILLAGE:.0f} people, {b:.3g} at "
            f"{40*VILLAGE:.0f}, a factor of {b/a:.0f} for a factor "
            f"of 40. That is why a design space can be both used "
            f"up and never used up -- finding things removes them "
            f"from it, and arriving people add to it, and neither "
            f"process wins outright")


def _growth():
    live, dead = novel_fraction(POP_GROWTH), novel_fraction(1e-9)
    fast = novel_fraction(0.02)
    if not (dead < live < fast):
        raise ArithmeticError(f"{dead} {live} {fast}")
    return (f"a* = trials/(trials + space-per-head x growth), so "
            f"the novel share of trials is "
            f"{100*live:.1f}% at {POP_GROWTH:.3f}/yr growth, "
            f"{100*fast:.1f}% at 0.02, and {100*dead:.3f}% at "
            f"none. A population that has stopped growing exhausts "
            f"its design space however LARGE it is -- size sets how "
            f"many trials happen, growth sets whether there is "
            f"anywhere left to put them. That is not obvious and it "
            f"is the whole content of the steady state")


def _team():
    tv, tn = team_size(VILLAGE), team_size(40 * VILLAGE)
    if tn <= tv:
        raise ArithmeticError(f"{tv} {tn}")
    return (f"a design of p parts needs someone holding all p, and "
            f"engine/craft.py says a person holds about "
            f"{SPECIALTIES_PER_HEAD:.0f}. So it takes a team, and "
            f"the team is the part count: {tv:.1f} people in a "
            f"village of {VILLAGE:.0f}, {tn:.1f} in a network of "
            f"{40*VILLAGE:.0f}. Intricacy grows with the log of the "
            f"corpus and the corpus grows with population, so the "
            f"cost of ONE new thing rises with how much is already "
            f"known. Nobody is getting worse at this")


def _mult():
    per, tot = multiple(VILLAGE, 40 * VILLAGE)
    n1, n2 = VILLAGE, 40 * VILLAGE
    t1, t2 = team_size(n1), team_size(n2)
    naive = math.log2(n1) / math.log2(n2)
    if per >= 1.0 or tot <= 1.0:
        raise ArithmeticError(f"{per} {tot}")
    return (f"the multiple. {n1:.0f} -> {n2:.0f} people, "
            f"{n2/n1:.0f}x: novelty per head falls to {per:.2f} "
            f"and novel designs in TOTAL rise {tot:.0f}x. Each "
            f"person invents {100*(1-per):.0f}% less and the world "
            f"gets {tot:.0f}x more, both at once. The ratio is "
            f"log2(corpus1)/log2(corpus2) = {t1:.1f}/{t2:.1f} = "
            f"{per:.2f}, NOT log2(n1)/log2(n2) = {naive:.2f} -- the "
            f"corpus is bigger than the population because literacy "
            f"and recopying multiply it, and using the population "
            f"there would overstate the fall by "
            f"{100*(per-naive)/per:.0f}%. And note which mechanism "
            f"did the work: exhaustion did NOT. At "
            f"{space(n1)/n1:.0f} designs per head against "
            f"{TRIALS_PER_HEAD_YEAR} trials a year, "
            f"{100*novel_fraction():.1f}% of trials still land on "
            f"something new -- nobody is running out. The entire "
            f"decline is the TEAM: a design of p parts needs p "
            f"people who between them hold p crafts, and p is a "
            f"logarithm of what is already known. Novelty per head "
            f"falls because knowing enough to add to it costs more, "
            f"not because there is less left")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
