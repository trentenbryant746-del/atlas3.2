"""
Every fold enumerated, and Levinthal's paradox answered by counting.

A protein's structure cannot be predicted here. AlphaFold does that
with about 93 million learned parameters, and there is no rule to
extract from them -- running it would be importing the thing this
repo exists not to be. So structure prediction is refused.

What is NOT refused is enumeration. For a short chain on a lattice
the set of folds is FINITE and can be walked exhaustively, scored,
and the minimum found -- no search heuristic, no sampling, no
model. Every fold is visited, so the answer is not the best one
found but the best one there is.

HYDROPHOBICITY IS DERIVED, AND NOT THRESHOLDED. The usual lattice
model sorts residues into H and P, which needs a cutoff somebody
chooses. This takes the ratio of carbon to polar atoms straight out
of the formulas already in engine/biomatter.py -- glycine 0.67,
phenylalanine 3.00 -- and uses it CONTINUOUSLY as the interaction
weight. Trying to split it failed honestly: the largest gap in the
sorted ratios falls between tyrosine and tryptophan, which would
make only F and W hydrophobic. That split is wrong and the
continuous form does not need it.

    contact energy = -h(i) * h(j) for residues adjacent in space
                     and not adjacent in the chain

Two greasy residues touching lowers the energy; a greasy one
touching a polar one lowers it less. That is hydrophobic collapse,
and it is the whole force in this model.

LEVINTHAL, WITH THE NUMBERS RUN. A 100-residue chain with three
choices per bond has 3^100 = 5.2e47 conformations. At one
picosecond each, trying them all takes 1.6e28 years, and the
universe is 1.4e10 years old -- so folding cannot be a search, and
real proteins fold in milliseconds. That is the paradox.

It is a paradox about OUR universe's age, not about arithmetic.
Heat death is around 1e100 years, so a universe allowed to run that
far has 1e72 times more time than an exhaustive fold needs. The
search is impossible here and comfortable there, which is a real
difference between universes rather than a fact about proteins --
and it is the kind of thing this project exists to notice.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.biomatter import RESIDUES, _elements                # noqa: E402

DERIVED, ASSERTED = "DERIVED", "ASSERTED"
PICOSECOND = 1e-12
YEAR_S = 3.155693e7
AGE_UNIVERSE_YR = 1.38e10
HEAT_DEATH_YR = 1e100        # from engine/epochs.py's far-future era


def hydrophobicity(aa):
    """Carbon against polar atoms, from the formula. DERIVED, continuous."""
    if aa not in RESIDUES:
        raise KeyError(f"no formula for residue {aa!r}")
    e = _elements(RESIDUES[aa])
    polar = e.get("N", 0) + e.get("O", 0) + e.get("S", 0)
    if polar == 0:
        raise ArithmeticError(f"{aa} has no polar atoms")
    return e.get("C", 0) / polar


def scale():
    return {aa: hydrophobicity(aa) for aa in RESIDUES}


# ------------------------------------------------------- the lattice
STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def walks(n):
    """Every self-avoiding walk of n sites on the square lattice.

    Exhaustive. The first step is fixed to one direction, which
    removes the fourfold rotation without removing any distinct
    fold -- and the count is checked against the unreduced walk.
    """
    if n < 1:
        raise ValueError("a chain has at least one residue")
    if n == 1:
        yield ((0, 0),)
        return
    start = [(0, 0), (1, 0)]

    def go(path, seen):
        if len(path) == n:
            yield tuple(path)
            return
        x, y = path[-1]
        for dx, dy in STEPS:
            p = (x + dx, y + dy)
            if p in seen:
                continue
            seen.add(p)
            path.append(p)
            yield from go(path, seen)
            path.pop()
            seen.remove(p)
    yield from go(list(start), set(start))


def energy(seq, path):
    """Hydrophobic contacts. Adjacent in space, not in the chain."""
    h = [hydrophobicity(a) for a in seq]
    pos = {p: i for i, p in enumerate(path)}
    e = 0.0
    for i, (x, y) in enumerate(path):
        for dx, dy in STEPS:
            j = pos.get((x + dx, y + dy))
            if j is None or j <= i + 1:
                continue
            e -= h[i] * h[j]
    return e


def fold(seq):
    """-> (best energy, degeneracy, count). Every fold, not a sample."""
    if len(seq) > 14:
        raise ValueError(
            f"{len(seq)} residues is past what can be enumerated here; "
            f"the walk count grows about 2.6x per residue and this "
            f"refuses rather than sampling")
    best, deg, total = None, 0, 0
    for w in walks(len(seq)):
        total += 1
        e = energy(seq, w)
        if best is None or e < best - 1e-12:
            best, deg = e, 1
        elif abs(e - best) <= 1e-12:
            deg += 1
    return best, deg, total


def levinthal(n=100, per_state=PICOSECOND, branches=3):
    """-> dict. The paradox, and which universes it is a paradox in."""
    states = branches ** n
    seconds = states * per_state
    years = seconds / YEAR_S
    return {"residues": n, "states": states, "years": years,
            "vs_age_of_universe": years / AGE_UNIVERSE_YR,
            "vs_heat_death": years / HEAT_DEATH_YR,
            "possible_now": years < AGE_UNIVERSE_YR,
            "possible_by_heat_death": years < HEAT_DEATH_YR}


def predict_structure(seq):
    """REFUSED. Enumeration is not prediction."""
    raise NotImplementedError(
        f"no structure is predicted for a {len(seq)}-residue chain. This "
        f"enumerates every fold of a short chain on a lattice and reports "
        f"the minimum, which is exact and is not a structure: a lattice "
        f"is not a protein and there are no side chains, no solvent and "
        f"no backbone angles in it. Structure prediction is AlphaFold's, "
        f"with about 93 million learned parameters and no rule to take")


# ------------------------------------------------------- self-checking
def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("hydrophobicity_derived", _hyd)
    t("walks_are_self_avoiding", _saw)
    t("enumeration_is_exhaustive", _exh)
    t("collapse_lowers_energy", _coll)
    t("degeneracy_reported", _deg)
    t("levinthal", _lev)
    t("refuses_to_predict", _ref)
    return all(o[1] for o in out), out


def _hyd():
    s = scale()
    lo = min(s, key=lambda a: s[a])
    hi = max(s, key=lambda a: s[a])
    # the ordering is the claim; scored against nothing, reported as is
    return (f"{len(s)} residues scored from the formulas alone: {lo} at "
            f"{s[lo]:.2f} up to {hi} at {s[hi]:.2f}. Continuous, because "
            f"the largest gap in the sorted ratios falls between Y and W "
            f"and splitting there would call only F and W hydrophobic")


def _saw():
    bad = 0
    for n in (5, 7, 9):
        for w in walks(n):
            if len(set(w)) != len(w):
                bad += 1
    if bad:
        raise ArithmeticError(f"{bad} walks revisit a site")
    return "every walk at n=5, 7 and 9 visits each site exactly once"


def _exh():
    """The reduced count times the symmetry must equal the full count."""
    def full(n):
        if n == 1:
            return 1
        tot = 0
        for d in STEPS:
            start = [(0, 0), d]

            def go(path, seen):
                nonlocal tot
                if len(path) == n:
                    tot += 1
                    return
                x, y = path[-1]
                for dx, dy in STEPS:
                    p = (x + dx, y + dy)
                    if p in seen:
                        continue
                    seen.add(p); path.append(p)
                    go(path, seen)
                    path.pop(); seen.remove(p)
            go(list(start), set(start))
        return tot
    rows = []
    for n in (4, 6, 8):
        r = sum(1 for _ in walks(n))
        f = full(n)
        if f != 4 * r:
            raise ArithmeticError(f"n={n}: {f} full against 4x{r} reduced")
        rows.append(f"n={n}: {r} reduced, {f} full")
    return ("fixing the first step removes exactly the fourfold rotation "
            "and nothing else -- " + "; ".join(rows))


def _coll():
    """A greasy chain must fold tighter than a polar one."""
    greasy = fold("FFFFWWFF")
    polar = fold("GGGGSSGG")
    if greasy[0] >= polar[0]:
        raise ArithmeticError(f"greasy {greasy[0]:.2f} did not beat polar "
                              f"{polar[0]:.2f}")
    return (f"FFFFWWFF reaches {greasy[0]:.2f} and GGGGSSGG only "
            f"{polar[0]:.2f} over the same {greasy[2]} folds -- the same "
            f"shape costs different energy depending on what is in it, "
            f"which is hydrophobic collapse and the only force here")


def _deg():
    e, deg, tot = fold("FGFGFGFG")
    if deg < 1:
        raise ArithmeticError("no minimum found")
    return (f"FGFGFGFG: {tot} folds enumerated, best energy {e:.2f}, and "
            f"{deg} distinct folds reach it -- a degenerate ground state, "
            f"reported rather than one of them picked")


def _lev():
    a = levinthal(100)
    if a["possible_now"]:
        raise ArithmeticError("the paradox did not reproduce")
    if not a["possible_by_heat_death"]:
        raise ArithmeticError("even heat death is not long enough, which "
                              "contradicts the arithmetic")
    return (f"100 residues, {a['states']:.2e} conformations, "
            f"{a['years']:.2e} years to try them all -- "
            f"{a['vs_age_of_universe']:.1e}x the age of this universe, so "
            f"folding cannot be a search here; but "
            f"{1/a['vs_heat_death']:.1e}x LESS than the time to heat "
            f"death, so a universe run that far could afford it")


def _ref():
    try:
        predict_structure("MCGFWA")
    except NotImplementedError as e:
        if "93 million" not in str(e):
            raise ArithmeticError("the refusal does not say what does it")
        return ("structure prediction is refused and names what does it "
                "instead -- enumeration on a lattice is exact and is not "
                "a structure")
    raise ArithmeticError("a structure was predicted")


if __name__ == "__main__":
    s = scale()
    print("hydrophobicity, derived from the formulas (C : polar atoms)")
    for aa in sorted(s, key=lambda a: -s[a])[:5]:
        print(f"  {aa} {s[aa]:.2f}")
    print("  ...")
    for aa in sorted(s, key=lambda a: s[a])[:3]:
        print(f"  {aa} {s[aa]:.2f}")
    print()
    for seq in ("FFFFWWFF", "GGGGSSGG", "FGFGFGFG", "MCGFWAIL"):
        e, deg, tot = fold(seq)
        print(f"  {seq}  {tot:>6} folds, best {e:8.2f}, "
              f"{deg} at the minimum")
    print()
    for n in (10, 50, 100):
        L = levinthal(n)
        print(f"  {n:>4} residues: {L['states']:.2e} states, "
              f"{L['years']:.2e} yr  now={L['possible_now']} "
              f"by-heat-death={L['possible_by_heat_death']}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:28}{d[:92]}")
    print("\nall:", ok)
