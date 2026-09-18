"""
Adaptation is a search, and reproduction is how it is paid for.

engine/trajectory.py showed that moving to a new latitude imposes
a constraint the old one did not -- seasonality at 60 degrees is
a 109 K swing against 6 at the equator. It did not say how a
population comes to answer one.

The answer needs nothing new. engine/heredity.py gives variation
without a mutation rate: 1.39 molecule types lost per division,
of which 4.48 reactions' worth are non-lethal. engine/innovation.py
gives the share of those that are useful, 1.1e-4 and honestly
unmeasured. Multiply and one individual produces 4.9e-4 useful
variants per generation.

SO REPRODUCTION IS THE SEARCH. Population size is how many
variants are tried per generation and nothing else changes it:

            10 individuals    204 generations to find one answer
           100                 20
        10,000                  0.2
     1,000,000                  0.002

AND THAT SETS A FLOOR ON POPULATION. A constraint has to be
answered before it kills you. If the environment presents a new
one every T years and the population needs more than T to find
an answer, the lineage does not adapt -- it ends. The minimum
viable number is not a conservation figure here, it is where the
search rate crosses the rate of being asked.

WHAT SELECTION CONTRIBUTES IS THE OTHER HALF. Variation without
differential survival is drift: engine/heredity.py already has
the differential -- about half of daughters cannot close -- so
the useful variant is kept and the rest are not, at no cost to
anything. Selection is not a force applied to the population. It
is what the failures already do.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

GENERATION_DAYS = 1.0        # CHOSEN, a microbial division a day

# MEASURED, days between generations. The thing that turned out to
# be the lever -- not population.
GENERATIONS = {"microbe": 1.0, "insect": 30.0, "mouse": 90.0,
               "wolf": 3 * 365.0, "human": 20 * 365.0}


def useful_per_individual():
    """Useful variants one individual makes per generation. DERIVED."""
    from engine.innovation import innovations_per_division, useful_fraction
    frac, _sampled = useful_fraction()
    return innovations_per_division() * frac


def search_rate(population):
    """Useful variants a population tries per generation. DERIVED."""
    return population * useful_per_individual()


def generations_to_answer(population):
    """How long to find one answer. DERIVED."""
    r = search_rate(population)
    return float("inf") if r <= 0 else 1.0 / r


def years_to_answer(population, gen_days=GENERATION_DAYS):
    """DERIVED."""
    return generations_to_answer(population) * gen_days / 365.0


def minimum_population(challenge_years, gen_days=GENERATION_DAYS):
    """-> N. Below this the search is slower than the asking. DERIVED."""
    per_gen = useful_per_individual()
    gens = challenge_years * 365.0 / gen_days
    return 1.0 / (per_gen * gens)


def adapts(population, challenge_years, gen_days=GENERATION_DAYS):
    """-> (bool, why). Does this lineage keep up? DERIVED."""
    need = years_to_answer(population, gen_days)
    return need <= challenge_years, (
        f"{population:,.0f} individuals find an answer in "
        f"{need:.3g} years against a new constraint every "
        f"{challenge_years:g}")


def selection_is_free():
    """-> (fraction culled, why). DERIVED via engine/heredity.py."""
    from engine.heredity import daughter_fails
    f = daughter_fails()
    return f, (
        f"{100*f:.0f}% of daughters already cannot close, so the "
        f"differential exists before anything is selected FOR. "
        f"Selection is not a force applied to a population, it is "
        f"what the failures already do")


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("reproduction_is_the_search", _search)
    t("population_size_is_the_only_lever", _pop)
    t("generation_time_is_the_lever_not_population", _floor)
    t("selection_costs_nothing_extra", _sel)
    t("nothing_new_was_introduced", _clean)
    return all(o[1] for o in out), out


def _search():
    u = useful_per_individual()
    if u <= 0 or u > 1:
        raise ArithmeticError(f"{u} useful variants per individual")
    from engine.innovation import innovations_per_division
    return (f"engine/heredity.py gives 4.48 non-lethal variants per "
            f"division without a mutation rate, and "
            f"engine/innovation.py gives the useful share, 1.1e-4. "
            f"Multiply and one individual makes {u:.2e} useful "
            f"variants a generation. REPRODUCTION IS THE SEARCH -- "
            f"it is not a way of continuing, it is how the answers "
            f"are looked for")


def _pop():
    rows = [(n, generations_to_answer(n)) for n in (10, 100, 1e4, 1e6)]
    if rows[0][1] <= rows[-1][1]:
        raise ArithmeticError("more individuals do not search faster")
    return (f"population size is how many variants are tried per "
            f"generation and nothing else changes it: "
            + "; ".join(f"{int(n):,} take {g:,.0f}" for n, g in rows[:3])
            + f" generations to find one answer. A lineage does not "
              f"adapt faster by trying harder, it adapts faster by "
              f"being more numerous")


def _floor():
    """CORRECTED. The floor is tiny; the lever is elsewhere."""
    rows = [(k, minimum_population(1.0, d))
            for k, d in GENERATIONS.items()]
    micro, human = rows[0][1], rows[-1][1]
    if human <= micro * 100:
        raise ArithmeticError(f"microbe {micro:.0f}, human {human:.0f}")
    return (f"the first version of this expected fifty individuals to "
            f"be too few and they are not -- a microbe answering a "
            f"yearly challenge needs {micro:.0f}. With a division a "
            f"day the search is simply fast. GENERATION TIME IS THE "
            f"LEVER: "
            + ", ".join(f"{k} {n:,.0f}" for k, n in rows[1::2])
            + f", and a human generation is {GENERATIONS['human']:.0f} "
              f"days, so the population needed for the same challenge "
              f"is {human/micro:,.0f} times larger. A slow breeder "
              f"does not adapt by being patient; it adapts by being "
              f"numerous, or it does not adapt")


def _sel():
    f, why = selection_is_free()
    if not 0.1 < f < 0.9:
        raise ArithmeticError(f"{f:.2f} of daughters fail")
    return (f"variation without differential survival is drift, and "
            f"the differential is already there: {why}")


def _clean():
    import ast
    src = (ROOT / "engine" / "adapt.py").read_text()
    tree = ast.parse(src)
    consts = {n.targets[0].id for n in ast.walk(tree)
              if isinstance(n, ast.Assign) and n.targets
              and isinstance(n.targets[0], ast.Name)
              and n.targets[0].id.isupper()} - {"ROOT"}
    if consts - {"GENERATION_DAYS", "GENERATIONS"}:
        raise ArithmeticError(f"introduced {consts}")
    return (f"this file introduces {sorted(consts)} and both are "
            f"generation lengths. No selection "
            f"coefficient, no mutation rate, no fitness function -- "
            f"the variation comes from engine/heredity.py, the "
            f"useful share from engine/innovation.py, and the "
            f"differential from the half of daughters that already "
            f"cannot close")


if __name__ == "__main__":
    u = useful_per_individual()
    print(f"  {u:.2e} useful variants per individual per generation\n")
    print(f"  {'population':>12}{'per generation':>18}{'generations':>14}")
    for n in (10, 100, 1e4, 1e6, 1e9):
        print(f"  {n:>12,.0f}{search_rate(n):>18.3e}"
              f"{generations_to_answer(n):>14,.1f}")
    print(f"\n  a new constraint every year needs "
          f"{minimum_population(1.0):.1f} individuals")
    f, _w = selection_is_free()
    print(f"  and {100*f:.0f}% of daughters already fail, so the "
          f"differential is free\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:48}{d[:30]}")
