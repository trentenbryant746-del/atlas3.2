"""
Division, heredity and selection, none of them added.

engine/occurrence.py closed the first of four things a cell is:
chemistry that sustains itself. It said plainly that the other
three were absent -- nothing copies a sequence forward, nothing
divides, nothing selects -- and that the gap had moved rather
than shut.

All three fall out of numbers already derived. No mutation rate
is introduced, no division timer, no fitness function.

DIVISION IS GEOMETRY. A sphere of volume V needs area
(36 pi)^(1/3) V^(2/3). Two spheres of V/2 need 2^(1/3) times
that -- 26% more. Metabolism makes lipid in proportion to
CONTENTS, so membrane accrues as V while the sphere requires
only V^(2/3), and the excess arrives on its own. A vesicle
therefore divides exactly when it doubles, because doubling is
where the excess reaches 26%. Nothing decides to divide.

HEREDITY IS COPY NUMBER. A compartment at the closure floor
holds 1e10 molecules over 3.6e8 types, so 28 copies of each. A
random half-split misses a given type with probability 2^-28,
which is 3.9e-9, so essentially every type is transmitted.

AND SELECTION IS THE REMAINDER. 3.6e8 types at 3.9e-9 each is
1.39 TYPES LOST PER DIVISION. Heredity is high-fidelity and not
perfect, and the imperfection is not a parameter -- it is what
28 copies and a coin-flip split produce. Closure then either
survives the loss or does not, so there is variation and there
is differential survival, and nothing was added to get either.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SPLIT_AREA_RATIO = 2.0 ** (1.0 / 3.0)     # EXACT: two half-spheres


def area_for(volume):
    """Area a sphere of this volume needs. EXACT geometry."""
    return (36.0 * math.pi) ** (1.0 / 3.0) * volume ** (2.0 / 3.0)


def excess_membrane(volume_ratio):
    """-> ratio. Membrane made over membrane a sphere needs. DERIVED.

    Lipid is made in proportion to contents, so area accrues as V
    while the sphere needs V^(2/3).
    """
    return volume_ratio / (volume_ratio ** (2.0 / 3.0))


def divides_at():
    """-> volume ratio. Where excess reaches what two spheres need."""
    v = 1.0
    while excess_membrane(v) < SPLIT_AREA_RATIO and v < 100.0:
        v *= 1.0001
    return v


def copies_per_type(radius_m=None):
    """-> (copies, molecules, types). DERIVED via engine/occurrence.py."""
    from engine.occurrence import (molecules_held, types_up_to,
                                   longest_complete_polymer)
    held = molecules_held(radius_m)
    L = longest_complete_polymer(radius_m)
    M = types_up_to(L)
    return held / M, held, M


def lost_per_division(radius_m=None):
    """-> (types lost, per-type probability). DERIVED.

    A random half-split misses a type when all its copies land on
    one side: 2^-n for n copies. No mutation rate is introduced.
    """
    n, _held, M = copies_per_type(radius_m)
    p = 2.0 ** (-n)
    return M * p, p


def sole_catalyst_fraction():
    """-> fraction of reactions with exactly one catalyst. DERIVED.

    Catalysts per reaction is Poisson with mean p*M, so P(exactly
    one) = lam e^-lam. Losing that molecule type stops the
    reaction; losing any other does not.
    """
    from engine.occurrence import closes_in_one
    _ok, lam, _L = closes_in_one()
    return lam * math.exp(-lam), lam


def daughter_fails(radius_m=None):
    """-> probability a division produces a non-viable daughter."""
    lost, _p = lost_per_division(radius_m)
    sole, _lam = sole_catalyst_fraction()
    from engine.occurrence import closes_in_one
    _ok, lam, _L = closes_in_one()
    # each lost type catalysed about lam reactions; it is load
    # bearing where it was the only catalyst
    return min(1.0, lost * lam * sole)


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("division_is_geometry_and_nothing_decides_it", _div)
    t("heredity_is_copy_number", _her)
    t("selection_is_what_copy_number_leaves_over", _sel)
    t("no_mutation_rate_was_introduced", _nomut)
    t("three_of_four_now_and_the_fourth_is_named", _four)
    return all(o[1] for o in out), out


def _div():
    v = divides_at()
    if abs(v - 2.0) > 0.05:
        raise ArithmeticError(f"division at {v:.3f}x volume, not 2x")
    return (f"two spheres of half the volume need {SPLIT_AREA_RATIO:.4f} "
            f"times one sphere's area -- {100*(SPLIT_AREA_RATIO-1):.1f}% "
            f"more. Lipid is made in proportion to contents, so area "
            f"accrues as V while the sphere needs V^(2/3), and the "
            f"excess reaches that at a volume ratio of {v:.2f}. A "
            f"vesicle DIVIDES EXACTLY WHEN IT DOUBLES, and nothing "
            f"decides to: no timer, no trigger, no rule beyond a "
            f"sphere's area")


def _her():
    n, held, M = copies_per_type()
    _lost, p = lost_per_division()
    if p > 1e-6:
        raise ArithmeticError(f"a type is lost with p={p:.2e}")
    return (f"a compartment at the closure floor holds {held:.1e} "
            f"molecules over {M:,} types, so {n:.1f} copies each. A "
            f"random half-split misses a given type only when every "
            f"copy lands on one side, 2^-{n:.0f} = {p:.1e}. Heredity "
            f"is not a mechanism added here -- it is what copy number "
            f"does under a coin flip")


def _sel():
    lost, _p = lost_per_division()
    sole, lam = sole_catalyst_fraction()
    fail = daughter_fails()
    if lost < 0.1 or lost > 100:
        raise ArithmeticError(f"{lost:.2f} types lost per division")
    return (f"{lost:.2f} TYPES ARE LOST PER DIVISION. Heredity is "
            f"high-fidelity and not perfect, and the imperfection is "
            f"not a parameter -- it is what 28 copies and a coin flip "
            f"produce. Catalysts per reaction is Poisson with mean "
            f"{lam:.2f}, so {100*sole:.1f}% of reactions have exactly "
            f"one, and losing that type stops them. About "
            f"{100*fail:.0f}% of divisions yield a daughter that "
            f"cannot close. Variation and differential survival, "
            f"neither of them added")


def _nomut():
    import ast
    src = (ROOT / "engine" / "heredity.py").read_text()
    tree = ast.parse(src)
    names = {n.targets[0].id for n in ast.walk(tree)
             if isinstance(n, ast.Assign) and n.targets
             and isinstance(n.targets[0], ast.Name)}
    bad = {x for x in names if "MUT" in x.upper() or "RATE" in x.upper()}
    if bad:
        raise ArithmeticError(f"a rate was introduced: {bad}")
    return (f"this file defines one constant, 2^(1/3), and it is "
            f"exact geometry. No mutation rate, no division timer, no "
            f"fitness function. Everything else is read from "
            f"engine/occurrence.py, which read it from "
            f"engine/closure.py and engine/earthlab.py. A number "
            f"introduced to make a mechanism work is the mechanism "
            f"not working")


def _four():
    from engine.occurrence import closes_in_one
    ok, _pm, _L = closes_in_one()
    v, (lost, _p) = divides_at(), lost_per_division()
    if not ok:
        raise ArithmeticError("the chemistry no longer closes")
    return (f"engine/occurrence.py closed the first of four -- "
            f"chemistry that sustains itself -- and named the other "
            f"three absent. Division is geometry ({v:.1f}x volume), "
            f"heredity is copy number, and selection is the "
            f"{lost:.2f} types a split leaves behind. THE FOURTH IS "
            f"STILL MISSING and it is the one that was always "
            f"hardest: nothing here copies a SEQUENCE. Compositional "
            f"inheritance passes on which molecules are present, not "
            f"what any of them says, so there is no genome and "
            f"nothing that could carry an instruction forward")


if __name__ == "__main__":
    n, held, M = copies_per_type()
    lost, p = lost_per_division()
    sole, lam = sole_catalyst_fraction()
    print(f"  division at {divides_at():.2f}x volume "
          f"({100*(SPLIT_AREA_RATIO-1):.1f}% excess membrane)\n")
    print(f"  {held:.1e} molecules / {M:,} types = {n:.1f} copies each")
    print(f"  a type is missed with p = 2^-{n:.0f} = {p:.1e}")
    print(f"  so {lost:.2f} types lost per division\n")
    print(f"  catalysts per reaction: Poisson mean {lam:.2f}")
    print(f"  reactions with exactly one: {100*sole:.1f}%")
    print(f"  daughters that cannot close: {100*daughter_fails():.0f}%\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:44}{d[:34]}")
