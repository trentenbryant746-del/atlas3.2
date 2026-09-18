"""
Permission is not occurrence, and the distance is arithmetic.

engine/lineage.py marks one link MISSING: every gate opens and
nothing makes a cell. That gap was real and it was also
unmeasured, which is a different failing -- a gate answers YES or
NO and occurrence needs a RATE, and nobody had multiplied the
three numbers that turn one into the other.

    how many compartments a world runs
    how many distinct molecules each holds
    whether that is enough for closure

engine/closure.py derived the last of those: a set closes when
about half its reactions have a catalyst, p*M = 0.481, where M is
the number of molecule TYPES present. The word types is doing the
work and had been read as molecules.

    up to 10 bases     1,398,100 types    p*M = 0.014
    up to 12 bases    22,369,620          p*M = 0.224
    up to 13 bases    89,478,484          p*M = 0.895   <- closes
    up to 14 bases   357,913,940          p*M = 3.579

A compartment at the closure floor -- 1.58 microns, which
engine/earthlab.py derives from how many molecule types must sit
together to catalyse their own repair -- holds about 1e10
molecules at crowded concentration. Seeing every type up to 13
bases takes 1.6e9 draws, so one compartment contains all of them
with an order of magnitude to spare.

AND AN OCEAN HOLDS 8.1e34 SUCH COMPARTMENTS. The gap does not
close narrowly.

What this does NOT say is in _residue(). A closed reaction
network is chemistry that sustains itself; it is not heredity,
not a boundary that divides, and not descent. Those are three
further things and none of them is derived here.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OCEAN_KG = 1.35e21              # MEASURED
WATER_DENSITY = 1000.0          # MEASURED
CROWD_FACTOR = 100.0            # from earthlab: evaporation or sea ice


def compartments(radius_m=None):
    """How many cell-sized volumes an ocean is. DERIVED."""
    from engine.earthlab import size_window
    r = radius_m or size_window()[0]
    return (OCEAN_KG / WATER_DENSITY) / (4.0 / 3.0 * math.pi * r ** 3)


def types_up_to(L, k=4):
    """Distinct polymers up to length L. EXACT count."""
    return sum(k ** i for i in range(1, L + 1))


def draws_to_see_all(n_types):
    """Molecules needed to contain every type. DERIVED: coupon collector."""
    return n_types * math.log(max(n_types, 2))


def molecules_held(radius_m=None):
    """Molecules in one compartment at crowded concentration. DERIVED."""
    from engine.earthlab import (molecules_in_vesicle, CROWDED_M,
                                 size_window)
    r = radius_m or size_window()[0]
    n = molecules_in_vesicle(CROWDED_M * CROWD_FACTOR, r)
    return float(getattr(n, "value", n))


def longest_complete_polymer(radius_m=None, k=4):
    """Longest length whose every sequence fits in one compartment."""
    held = molecules_held(radius_m)
    L = 1
    while draws_to_see_all(types_up_to(L + 1, k)) <= held and L < 40:
        L += 1
    return L


def closes_in_one(radius_m=None, k=4):
    """-> (bool, p*M, L). Does a single compartment close? DERIVED."""
    from engine.closure import CATALYSTS_PER_REACTION
    from engine.earthlab import CATALYSIS_P
    L = longest_complete_polymer(radius_m, k)
    M = types_up_to(L, k)
    return (CATALYSIS_P * M >= CATALYSTS_PER_REACTION,
            CATALYSIS_P * M, L)


def expected_occurrences(radius_m=None, k=4):
    """-> float. Compartments times whether each one closes. DERIVED."""
    ok, _pm, _L = closes_in_one(radius_m, k)
    return compartments(radius_m) * (1.0 if ok else 0.0)


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("types_not_molecules_was_the_confusion", _types)
    t("one_compartment_holds_every_short_polymer", _one)
    t("a_single_compartment_closes", _closes)
    t("the_gap_does_not_close_narrowly", _many)
    t("what_this_does_not_say", _residue)
    return all(o[1] for o in out), out


def _types():
    from engine.earthlab import CATALYSIS_P
    from engine.closure import CATALYSTS_PER_REACTION
    rows = [(L, types_up_to(L), CATALYSIS_P * types_up_to(L))
            for L in (10, 12, 13, 14)]
    crossing = next(L for L, _M, pm in rows
                    if pm >= CATALYSTS_PER_REACTION)
    if crossing != 13:
        raise ArithmeticError(f"closure crosses at {crossing} bases")
    return (f"p*M = {CATALYSTS_PER_REACTION} is about molecule TYPES "
            f"and had been read as molecules. Up to 12 bases gives "
            f"{rows[1][1]:,} types and p*M = {rows[1][2]:.3f}, short. "
            f"Up to {crossing} gives {rows[2][1]:,} and "
            f"{rows[2][2]:.3f}, which is over. One word was carrying "
            f"the whole question")


def _one():
    held = molecules_held()
    L = longest_complete_polymer()
    need = draws_to_see_all(types_up_to(L))
    if held < need:
        raise ArithmeticError(f"{held:.1e} molecules for {need:.1e} needed")
    from engine.earthlab import size_window
    return (f"a compartment at the closure floor "
            f"({1e6*size_window()[0]:.2f} microns) holds "
            f"{held:.1e} molecules at crowded concentration. Seeing "
            f"every polymer up to {L} bases takes {need:.1e} draws by "
            f"coupon collector, so ONE compartment contains all of "
            f"them with {held/need:.0f}x to spare")


def _closes():
    ok, pm, L = closes_in_one()
    from engine.closure import CATALYSTS_PER_REACTION
    if not ok:
        raise ArithmeticError(f"p*M = {pm:.3f}, short of "
                              f"{CATALYSTS_PER_REACTION}")
    return (f"one compartment holds every polymer to {L} bases, which "
            f"is p*M = {pm:.3f} against the {CATALYSTS_PER_REACTION} "
            f"closure needs. IT CLOSES. Not because catalysis is "
            f"better than measured -- it is the measured 1e-8 -- but "
            f"because the number of distinct molecules in a "
            f"cell-sized volume is large and p*M scales with it")


def _many():
    n = compartments()
    e = expected_occurrences()
    if e < 1e20:
        raise ArithmeticError(f"only {e:.1e} expected")
    return (f"an ocean is {n:.2e} compartments at that size, and each "
            f"one closes, so the expected count is {e:.2e}. THE GAP "
            f"DOES NOT CLOSE NARROWLY. engine/lineage.py marked this "
            f"link MISSING because a gate says yes or no and "
            f"occurrence needs a rate; the rate was three numbers "
            f"already derived and never multiplied")


def _residue():
    return ("a closed reaction network is chemistry that sustains "
            "itself. It is NOT heredity -- nothing here copies a "
            "sequence forward. It is NOT a boundary that divides, so "
            "no lineage. And it is NOT descent, so nothing selects. "
            "Three further things, none derived here, and calling "
            "this 'a cell' would be the same error as calling an "
            "open gate an occurrence. What closed is the first of "
            "four, and the other three are now the named gap")


if __name__ == "__main__":
    from engine.earthlab import CATALYSIS_P, size_window
    from engine.closure import CATALYSTS_PER_REACTION
    print(f"  closure needs p*M >= {CATALYSTS_PER_REACTION}, "
          f"catalysis is {CATALYSIS_P:.0e}\n")
    print(f"  {'up to':>8}{'types':>16}{'p*M':>10}")
    for L in (10, 11, 12, 13, 14):
        M = types_up_to(L)
        print(f"  {L:>6} b{M:>16,}{CATALYSIS_P*M:>10.3f}"
              + ("   <- closes" if CATALYSIS_P * M >= CATALYSTS_PER_REACTION
                 and CATALYSIS_P * types_up_to(L - 1) < CATALYSTS_PER_REACTION
                 else ""))
    ok, pm, L = closes_in_one()
    print(f"\n  one {1e6*size_window()[0]:.2f} um compartment holds "
          f"{molecules_held():.1e} molecules")
    print(f"  -> every polymer to {L} bases, p*M = {pm:.3f}, closes: {ok}")
    print(f"  an ocean is {compartments():.2e} of them\n")
    for n, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:36]}")
