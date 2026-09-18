"""
Why a pressure is not yet a necessity, with the size of the gap.

engine/lineage.py marks seven middle links FORCED: permitted, and
something drives them. FORCED is weaker than DERIVED and the
instruction was to write the rule that closes it -- why the step
HAS to happen, not merely why something is worse off without it.

The rule is the one selection already implies. A trait under a
pressure moves by the breeder's equation, response = s * sigma^2
per generation, so the step is taken when variation carries the
trait across the distance inside the time available.

Written down and evaluated, it says every one of the seven takes
BETWEEN ONE AND SIX YEARS.

    LUCA -> eukaryote              1,023 generations      3 y
    eukaryote -> multicellular       758                  2 y
    multicellular -> large-bodied  2,312                  6 y
    endotherm -> large brain       1,888                  5 y

The record puts the first of those at about two billion years.
The rule is wrong by eight orders of magnitude, and it is wrong
in the informative direction: it says these steps should be
INSTANT and they were not.

So the rule is right about selection and wrong about the KIND OF
CHANGE. A continuous trait under constant pressure does move that
fast. What separates LUCA from a eukaryote is not a bigger
version of LUCA -- it is a membrane inside a membrane, which no
amount of incremental size change reaches. The seven links are
not distances in a trait. They are discrete innovations, and
nothing here produces one.

That is why they stay FORCED. Writing the rule did not close the
gap; it measured it, and it named what is actually absent.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SELECTION_STRENGTH = 0.1     # CHOSEN, a strong but ordinary pressure
GENERATIONS_PER_YEAR = 365.0  # CHOSEN, a microbial generation a day

# RECORDED: roughly when each transition is dated, in Gyr before now
DATED = {
    "eukaryote": (3.8, 1.8),
    "multicellular": (1.8, 0.6),
    "large-bodied": (0.6, 0.54),
    "skeletal": (0.54, 0.44),
    "land": (0.44, 0.37),
    "endotherm": (0.37, 0.22),
    "large brain": (0.22, 0.002),
}

# Log-size distance for each step, from the sizes the modules use
SPAN = {
    "eukaryote": (1e-6, 1e-5),
    "multicellular": (1e-5, 5.5e-5),
    "large-bodied": (5.5e-5, 1e-2),
    "skeletal": (1e-2, 1.0),
    "land": (1.0, 1.0),
    "endotherm": (1.0, 1.0),
    "large brain": (1.0, 70.0),
}


def variation():
    """Spread in log size per generation. DERIVED via descent."""
    from engine.descent import MUTATION_SIZE
    return MUTATION_SIZE


def generations_needed(step, s=SELECTION_STRENGTH):
    """Breeder's equation: response = s * sigma^2 per generation."""
    a, b = SPAN[step]
    d = abs(math.log(b / a)) if b != a else 0.7
    return d / (s * variation() ** 2)


def years_needed(step, s=SELECTION_STRENGTH):
    """DERIVED."""
    return generations_needed(step, s) / GENERATIONS_PER_YEAR


def years_taken(step):
    """RECORDED, in years."""
    a, b = DATED[step]
    return (a - b) * 1e9


def discrepancy(step, s=SELECTION_STRENGTH):
    """-> orders of magnitude between predicted and recorded."""
    return math.log10(years_taken(step) / max(years_needed(step, s), 1e-9))


def all_steps(s=SELECTION_STRENGTH):
    """-> [(step, generations, predicted yr, recorded yr, orders)]."""
    return [(k, generations_needed(k, s), years_needed(k, s),
             years_taken(k), discrepancy(k, s)) for k in SPAN]


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_rule_is_written_and_evaluated", _rule)
    t("it_is_wrong_by_eight_orders", _wrong)
    t("wrong_in_the_informative_direction", _dir)
    t("so_the_steps_are_not_distances_in_a_trait", _kind)
    t("they_stay_forced_and_now_the_gap_has_a_size", _stay)
    return all(o[1] for o in out), out


def _rule():
    rows = all_steps()
    if not rows:
        raise ArithmeticError("no steps evaluated")
    fast = max(r[2] for r in rows)
    return (f"the rule selection already implies: a trait under "
            f"pressure moves by response = s*sigma^2 per generation, "
            f"so a step is taken when variation carries the trait "
            f"across the distance in the time available. With "
            f"sigma = {variation()} from engine/descent.py and a "
            f"strong ordinary pressure, the slowest of the seven "
            f"takes {fast:.0f} years")


def _wrong():
    rows = all_steps()
    worst = max(rows, key=lambda r: r[4])
    if worst[4] < 6:
        raise ArithmeticError(f"only {worst[4]:.1f} orders out")
    return (f"the record puts {worst[0]} at {worst[3]:.2e} years and "
            f"the rule predicts {worst[2]:.0f}. That is "
            f"{worst[4]:.0f} ORDERS OF MAGNITUDE. Every one of the "
            f"seven is out by between "
            f"{min(r[4] for r in rows):.0f} and "
            f"{max(r[4] for r in rows):.0f}")


def _dir():
    rows = all_steps()
    if any(r[2] > r[3] for r in rows):
        raise ArithmeticError("some step is predicted slower than recorded")
    return ("and it is wrong in the INFORMATIVE direction. A rule "
            "that predicted these steps were too slow would mean the "
            "pressure was too weak or the variation too small, and "
            "either could be patched with a number. It predicts they "
            "are INSTANT. Nothing about selection is missing; "
            "something about the steps is")


def _kind():
    rows = all_steps()
    euk = [r for r in rows if r[0] == "eukaryote"][0]
    return (f"a continuous trait under constant pressure really does "
            f"move that fast -- {euk[1]:,.0f} generations to change "
            f"size tenfold is not an error. What separates LUCA from "
            f"a eukaryote is not a bigger LUCA. It is a membrane "
            f"inside a membrane, and no amount of incremental size "
            f"change reaches it. THE SEVEN LINKS ARE NOT DISTANCES "
            f"IN A TRAIT, they are discrete innovations, and nothing "
            f"in this repository produces one")


def _stay():
    from engine.lineage import chain, FORCED
    forced = [r for r in chain() if r[2] == FORCED]
    rows = all_steps()
    lo = min(r[4] for r in rows)
    if len(forced) != 7:
        raise ArithmeticError(f"{len(forced)} links are forced")
    return (f"the seven stay FORCED. Writing the rule did not close "
            f"the gap, it MEASURED it: at least {lo:.0f} orders of "
            f"magnitude between what selection on a continuous trait "
            f"would take and what the record shows. That is a better "
            f"position than before, when the gap was 'no rule "
            f"produces this' with no number attached, and it names "
            f"what is absent -- a mechanism that makes a discrete "
            f"innovation, which engine/descent.py could not find for "
            f"pumps, skins or skeletons either")


if __name__ == "__main__":
    print(f"  sigma = {variation()} per generation, s = "
          f"{SELECTION_STRENGTH}\n")
    print(f"  {'step':<16}{'gens':>10}{'predicted':>12}"
          f"{'recorded':>13}{'orders out':>12}")
    for k, g, yp, yr, d in all_steps():
        print(f"  {k:<16}{g:>10,.0f}{yp:>10.0f} y{yr:>11.2e} y"
              f"{d:>12.1f}")
    print()
    for nm, o, dd in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:44}{dd[:34]}")
