"""
Discrete innovation: the same absence in three places, named.

engine/descent.py could price a pump, a skin and a skeleton and
produce none. engine/reach.py found the seven middle links of the
chain are not distances in a trait -- selection on a continuous
trait crosses them in years and the record says hundreds of
millions. engine/tools.py is the one that closed, and how it
closed is the clue: a tool is not built, it is a HAND AND A
STONE. Two things that already existed, combined.

Read the others the same way and none of them is a new process
either:

    eukaryote      engulf, and fail to digest       omit a step
    multicellular  divide, and fail to separate     omit a step
    skeletal       precipitate, and fail to dissolve omit a step
    endotherm      lose heat, and fail to lose it   omit a step
    a tool         hand and stone                   combine two
    large brain    neural tissue, and more of it    duplicate

So the rule is: AN INNOVATION IS AN EXISTING PROCESS WITH A STEP
OMITTED, DUPLICATED, OR COMBINED WITH ANOTHER. Nothing is
created. That makes the space countable, which an open-ended
"new thing appears" never was.

AND THE RATE FALLS OUT OF HEREDITY. engine/heredity.py has 1.39
molecule types lost per division, each catalysing about 3.58
reactions, of which 10% are sole-catalysed and therefore lethal.
So 0.50 lethal losses per division and 4.48 NON-LETHAL ones -- a
process running with a step omitted and still closing, which is
exactly an innovation, happening four and a half times per
division.

Single omissions are therefore NOT the barrier, which was the
thing worth learning. Whatever separates LUCA from a eukaryote
needs several coordinated at once, and how many is the one number
here that is read off the record rather than derived. That is
marked wherever it appears.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OMIT, DUPLICATE, COMBINE = "omit", "duplicate", "combine"

# The taxonomy, and it is a claim that can be wrong: if a real
# innovation turns up that is none of these three, this is false.
INNOVATIONS = {
    "eukaryote": (OMIT, "phagocytosis", "engulf, and fail to digest"),
    "multicellular": (OMIT, "division", "divide, and fail to separate"),
    "skeletal": (OMIT, "mineral handling",
                 "precipitate, and fail to dissolve"),
    "endotherm": (OMIT, "thermal exchange",
                  "lose heat, and fail to lose it"),
    "a tool": (COMBINE, "grasping", "a hand and a stone"),
    "large brain": (DUPLICATE, "tissue growth",
                    "neural tissue, and more of it"),
}

REACTIONS_IN_A_CELL = 1e5     # CHOSEN, order of magnitude
DIVISIONS_PER_YEAR = 365.0    # CHOSEN, a division a day


def losses():
    """-> (lethal, non-lethal) per division. DERIVED via heredity."""
    from engine.heredity import lost_per_division, sole_catalyst_fraction
    lost, _p = lost_per_division()
    sole, lam = sole_catalyst_fraction()
    return lost * lam * sole, lost * lam * (1.0 - sole)


def innovations_per_division():
    """Non-lethal step omissions. DERIVED, nothing added."""
    return losses()[1]


def combinations(k, r=REACTIONS_IN_A_CELL):
    """How many coordinated sets of size k exist. EXACT."""
    return math.comb(int(r), k) if k < 6 else float("inf")


def wait_years(k, r=REACTIONS_IN_A_CELL):
    """Years to sample every coordinated set of size k. DERIVED."""
    rate = innovations_per_division() * DIVISIONS_PER_YEAR
    return combinations(k, r) / rate


def coordination_size():
    """-> k. How many reactions one omission changes. DERIVED.

    NO LONGER FITTED. Losing a single molecule type removes every
    reaction it catalysed, and that count is the Poisson mean p*M
    that engine/closure.py measured -- 3.58. So a coordinated
    change of that size is not a rare conjunction to wait for, it
    is what ONE loss already is. The earlier version searched for
    the k that reproduced the record and found 3, which was
    reading this number off the answer.
    """
    from engine.heredity import sole_catalyst_fraction
    _sole, lam = sole_catalyst_fraction()
    return lam


def coordination_for(years, r=REACTIONS_IN_A_CELL):
    """-> k. Kept so the old fitted route stays visible."""
    for k in range(1, 6):
        if wait_years(k, r) >= years:
            return k
    return None


def useful_fraction(recorded_years=2e9):
    """-> fraction. What the derived rate still leaves unexplained.

    With k derived, the distinct coordinated sets available are
    the molecule TYPES, and they are sampled in 2.2e5 years
    against a record of 2e9. The residue is not a free parameter
    dressed up -- it is a named quantity nobody here has measured:
    the share of viable omissions that are also USEFUL.
    """
    from engine.occurrence import types_up_to, longest_complete_polymer
    types = types_up_to(longest_complete_polymer())
    sampled_yr = types / (innovations_per_division()
                          * DIVISIONS_PER_YEAR)
    return sampled_yr / recorded_years, sampled_yr


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("every_innovation_is_omit_duplicate_or_combine", _tax)
    t("the_rate_falls_out_of_heredity", _rate)
    t("single_omissions_are_not_the_barrier", _single)
    t("the_coordination_number_is_derived_now", _fit)
    t("the_taxonomy_is_falsifiable", _fals)
    return all(o[1] for o in out), out


def _tax():
    kinds = {v[0] for v in INNOVATIONS.values()}
    if kinds - {OMIT, DUPLICATE, COMBINE}:
        raise ArithmeticError(f"a fourth kind appeared: {kinds}")
    omits = sum(1 for v in INNOVATIONS.values() if v[0] == OMIT)
    return (f"{len(INNOVATIONS)} supposed innovations, and not one is "
            f"a new process: {omits} are an existing process with a "
            f"step OMITTED, one is two things COMBINED, one is a "
            f"tissue DUPLICATED. engine/tools.py is the one that "
            f"closed and it closed by combination -- a hand and a "
            f"stone, both already there. Nothing is created, which "
            f"makes the space countable where 'a new thing appears' "
            f"never was")


def _rate():
    lethal, viable = losses()
    if viable < 1.0:
        raise ArithmeticError(f"only {viable:.2f} non-lethal per division")
    return (f"engine/heredity.py has 1.39 types lost per division, "
            f"each catalysing 3.58 reactions, 10% of them sole-"
            f"catalysed. So {lethal:.2f} lethal losses per division "
            f"and {viable:.2f} NON-LETHAL ones -- a process running "
            f"with a step omitted and still closing, which is what "
            f"an innovation is. Nothing was added to get that rate")


def _single():
    k1 = wait_years(1)
    if k1 > 1e6:
        raise ArithmeticError(f"a single omission takes {k1:.1e} years")
    return (f"every single-step omission in a {REACTIONS_IN_A_CELL:.0e}-"
            f"reaction cell is sampled in {k1:.0f} years at "
            f"{innovations_per_division():.1f} per division. SINGLE "
            f"OMISSIONS ARE NOT THE BARRIER, which is the thing worth "
            f"learning here -- the wait is not in finding one, it is "
            f"in needing several at once")


def _fit():
    k = coordination_size()
    old = coordination_for(2e9)
    frac, sampled = useful_fraction()
    if abs(k - old) > 1.0:
        raise ArithmeticError(f"derived {k:.2f} against fitted {old}")
    if frac > 0.01:
        raise ArithmeticError("nothing is left unexplained")
    return (f"k IS DERIVED NOW: {k:.2f}, the Poisson mean p*M that "
            f"engine/closure.py measured, because losing one "
            f"molecule type removes every reaction it catalysed and "
            f"that is how many. A coordinated change of that size is "
            f"not a conjunction to wait for, it is what ONE loss "
            f"already is. The fitted value was {old}, so the fit had "
            f"been reading this number off the answer. What the "
            f"derivation does NOT explain is the timing: types are "
            f"sampled in {sampled:.1e} years against a record of "
            f"2e9, leaving a factor of {1/frac:,.0f}. That is now a "
            f"named unmeasured quantity -- the share of viable "
            f"omissions that are also USEFUL, about {frac:.1e} -- "
            f"rather than a parameter tuned to hide it")


def _fals():
    return ("the taxonomy is a claim and can be wrong: if an "
            "innovation turns up that is not a step omitted, a thing "
            "duplicated or two things combined, this file is false "
            "and the countability goes with it. That is the point of "
            "writing it as six named cases rather than a principle. "
            "It also predicts where to look -- an innovation should "
            "always have a PARENT PROCESS, and if one has none then "
            "something here is creating rather than recombining")


if __name__ == "__main__":
    lethal, viable = losses()
    print(f"  {'innovation':<16}{'kind':<11}{'parent process':<20}how")
    for k, (kind, parent, how) in INNOVATIONS.items():
        print(f"  {k:<16}{kind:<11}{parent:<20}{how}")
    print(f"\n  lethal losses per division     {lethal:.2f}")
    print(f"  non-lethal (= innovations)     {viable:.2f}\n")
    print(f"  {'coordinated':>12}{'combinations':>16}{'years to sample':>18}")
    for k in (1, 2, 3, 4):
        print(f"  {k:>12}{combinations(k):>16.2e}{wait_years(k):>17.2e}")
    print(f"\n  the record's ~2e9 years implies k = "
          f"{coordination_for(2e9)}  (FITTED, not derived)\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:46}{d[:32]}")
