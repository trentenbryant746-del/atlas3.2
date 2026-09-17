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

import functools
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
    best, tied, total = None, set(), 0
    for w in walks(len(seq)):
        total += 1
        e = energy(seq, w)
        if best is None or e < best - 1e-12:
            best, tied = e, {canonical(w)}
        elif abs(e - best) <= 1e-12:
            tied.add(canonical(w))
    # canonical() first, THEN count: a fold and its reflection have
    # identical energy by construction, so counting them separately
    # reports a tie the model was never asked to break.
    return best, len(tied), total


# --------------------------------------------- what a fold's bar IS
#
# engine/nucleo.py measures its bars against MEASUREMENT: the mass
# formula predicts a binding energy, a real nuclide has one, and the
# residual over many nuclides is the bar. Folding has no such thing
# to compare to. There is no measured energy for a fold of FGFGFGFG
# on a square lattice because no such object exists. Borrowing the
# nuclear bar would be absurd -- 1.2 MeV is forty million thermal
# quanta, so every fold would pass -- and inventing a folding number
# in eV would be making one up, which is the one thing refused here.
#
# SO THE BAR IS MEASURED MODEL AGAINST MODEL. Where there is nothing
# to be right about, the question that remains is whether the answer
# SURVIVES A DEFENSIBLE CHANGE TO THE MODEL. It is a weaker claim
# than the nuclear bar and is labelled as one, but it is measured
# rather than typed, and it catches the real failure: a minimum that
# only exists because of an arbitrary choice upstream.
#
# The change used is sulfur. Counting S as polar is a coin flip --
# Pauling electronegativity puts sulfur at 2.58 and carbon at 2.55,
# which is no difference at all, so a thioether is about as greasy as
# a hydrocarbon. The baseline counts S with N and O; the variant
# counts it with C. Nothing else moves, and only cysteine and
# methionine change weight.
#
# AND THE ANSWER MUST BE SCALE-FREE. The hydrophobicity ratio has no
# units, so multiplying every weight by a constant is not a different
# model, it is the same model in different money. If the ground fold
# moved under that, the enumeration would be reading a scale that is
# not there. It is checked, and it does not.

S_POLAR, S_GREASY = "S-polar", "S-greasy"


def canonical(path):
    """A fold and its mirror image are ONE fold.

    walks() fixes the first step, which removes the fourfold rotation
    -- _exh() measures that it removes exactly fourfold and no more.
    It does NOT remove reflection across that step's axis, and the
    first run of determinacy() was reporting every short sequence as
    a two-way tie because of it. Those were never two folds. They
    were one fold and its reflection, which have identical energy by
    construction and so can never be told apart by any energy at all.
    Counting them as a tie makes the model look undecided about
    something it was never asked.
    """
    m = tuple((x, -y) for x, y in path)
    return min(tuple(path), m)


def hydrophobicity_v(aa, variant=S_POLAR):
    """Hydrophobicity under a stated variant of the model."""
    if aa not in RESIDUES:
        raise KeyError(f"no formula for residue {aa!r}")
    e = _elements(RESIDUES[aa])
    c, s = e.get("C", 0), e.get("S", 0)
    if variant == S_POLAR:
        num, polar = c, e.get("N", 0) + e.get("O", 0) + s
    elif variant == S_GREASY:
        num, polar = c + s, e.get("N", 0) + e.get("O", 0)
    else:
        raise ValueError(f"unknown variant {variant!r}; "
                         f"known: {S_POLAR}, {S_GREASY}")
    if polar == 0:
        raise ArithmeticError(f"{aa} has no polar atoms under {variant}")
    return num / polar


def energy_v(seq, path, h):
    """Contact energy given an explicit weight table."""
    pos = {p: i for i, p in enumerate(path)}
    e = 0.0
    for i, (x, y) in enumerate(path):
        for dx, dy in STEPS:
            j = pos.get((x + dx, y + dy))
            if j is None or j <= i + 1:
                continue
            e -= h[seq[i]] * h[seq[j]]
    return e


def ground_set(seq, variant=S_POLAR, gain=1.0):
    """-> (frozenset of minimising folds, E0, E1, spread, total).

    The fold SET, not one fold, because ties are the model saying it
    cannot choose and that has to survive into the answer.
    """
    h = {aa: hydrophobicity_v(aa, variant) * gain for aa in set(seq)}
    lo, hi, best, total = None, None, [], 0
    for w in walks(len(seq)):
        total += 1
        e = energy_v(seq, w, h)
        if lo is None or e < lo - 1e-12:
            lo, best = e, [canonical(w)]
        elif abs(e - lo) <= 1e-12:
            best.append(canonical(w))
        if hi is None or e > hi:
            hi = e
    nxt = None
    for w in walks(len(seq)):
        e = energy_v(seq, w, h)
        if e > lo + 1e-12 and (nxt is None or e < nxt):
            nxt = e
    return frozenset(best), lo, nxt, (hi - lo), total


def determinacy(seq):
    """-> dict. Is this minimum real, or an artefact of the model?

    Three scale-free facts, none of which needs an energy unit:
      degeneracy   how many folds tie. More than one and the model
                   has not chosen; that is exact, not a bar.
      gap_frac     (E1 - E0) / (Emax - E0). What fraction of the
                   model's whole range separates the winner. Invariant
                   under rescaling, which the arbitrary units demand.
      survives     whether the same fold set wins when sulfur moves.
    """
    g0, e0, e1, spread, total = ground_set(seq, S_POLAR)
    g1, *_ = ground_set(seq, S_GREASY)
    gap = None if e1 is None or spread <= 0 else (e1 - e0) / spread
    survives = (g0 == g1)
    if len(g0) > 1:
        v, why = ("UNDETERMINED",
                  f"{len(g0)} folds tie at the minimum, so the model has "
                  f"not picked one -- that is the model speaking, not a "
                  f"measurement error, and no bar makes it go away")
    elif not survives:
        v, why = ("UNDETERMINED",
                  f"the minimum is unique but it MOVES when sulfur is "
                  f"counted as greasy instead of polar, a change the "
                  f"chemistry does not decide -- so this fold is a "
                  f"property of the choice, not of the sequence")
    else:
        v, why = ("DETERMINED_IN_MODEL",
                  f"one fold of {total}, and the same one under both "
                  f"sulfur conventions; still a 2D lattice answer, which "
                  f"is not a claim about a real protein")
    return {"sequence": seq, "verdict": v, "why": why,
            "degeneracy": len(g0), "E0": e0, "E1": e1,
            "gap_frac": gap, "survives_variant": survives,
            "walks": total}


# THE BAR IS A RATE, NOT AN ENERGY, AND THAT IS THE FINDING.
#
# The first attempt measured this over alternating sequences and got
# 14 of 14 surviving -- a perfect score that meant nothing. On a
# square lattice a contact needs |i - j| odd, so in ABABAB every
# contact is A-B and the energy is one constant times the contact
# count. Rescaling one residue cannot reorder a spectrum that is a
# scaled integer count. Those sequences were unflippable BY
# CONSTRUCTION and measuring on them measured nothing.
#
# The second attempt looked for a threshold. Ten flipped sequences
# all had small gap fractions, which suggested that a fold separated
# by enough of the spectrum would be safe -- the same shape as the
# nuclear bar, where a Q-value outside 1.208 MeV is resolvable. Over
# 375 sequences it did not hold: survival runs 53% in the lowest
# band to 81% in the highest, with a flip as high as 0.224. The
# correlation is real and weak, and it is not a threshold. Recorded
# because a negative result that overturns a hypothesis is worth as
# much as the hypothesis was.
#
# What is left is a plain rate, and it is the honest bar:
#
#   nuclear    bar in MeV       against MEASUREMENT
#   folding    bar as a RATE    against ANOTHER MODEL
#
# Different classes of thing do not merely get different numbers.
# They get different KINDS of bar, because what there is to be wrong
# about differs. A nucleus has a mass somebody weighed. A fold of
# CGCG on a square lattice does not exist, so the only question that
# can be asked is how often the answer is the model's rather than
# the sequence's -- and the answer is that about a third of the time
# it is the model's.

BAR_SEED, BAR_N, BAR_LEN = 11, 96, 8
BAR_ALPHABET = "GACMFSWL"


def bar_sample(seed=BAR_SEED, n=BAR_N, length=BAR_LEN):
    """Sequences carrying C or M -- the only residues sulfur moves.

    Seeded, so the bar is the same number on every machine, and
    filtered to sequences the variant can actually reach.
    """
    import random
    r = random.Random(seed)
    out = []
    while len(out) < n:
        q = "".join(r.choice(BAR_ALPHABET) for _ in range(length))
        if any(c in q for c in "CM"):
            out.append(q)
    return out


@functools.lru_cache(maxsize=8)
def model_bar(seed=BAR_SEED, n=BAR_N, length=BAR_LEN):
    """-> (survival rate, why). MEASURED, not typed, not in eV.

    Cached because it is seeded and deterministic: the same sample
    gives the same rate, and engine/scales.py asks for it on every
    registry build.
    """
    kept = [determinacy(q)["survives_variant"]
            for q in bar_sample(seed, n, length)]
    f = sum(kept) / len(kept)
    return f, (f"{sum(kept)} of {len(kept)} sequences keep the same "
               f"minimising fold when sulfur is counted as greasy rather "
               f"than polar, a call the electronegativities do not make "
               f"(S 2.58, C 2.55). {100*(1-f):.0f}% of exact minima are "
               f"the model's choice, not the sequence's. This is the "
               f"folding bar and it is a rate, because there is no "
               f"measured fold to take a residual against")


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
    t("mirror_images_are_one_fold", _mirror)
    t("answer_is_scale_free", _scalefree)
    t("alternating_cannot_be_flipped", _parity)
    t("bar_is_a_rate_and_is_measured", _bar)
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


def _mirror():
    """Reflection is not degeneracy, and the first run said it was."""
    raw = {}
    for w in walks(4):
        raw.setdefault(round(energy("FGFG", w), 9), []).append(tuple(w))
    lo = min(raw)
    pair = raw[lo]
    if len(pair) != 2:
        raise ArithmeticError(f"expected the mirror pair, got {len(pair)}")
    a, b = pair
    if tuple((x, -y) for x, y in a) != b and \
       tuple((x, -y) for x, y in b) != a:
        raise ArithmeticError("the two minima are not each other's mirror")
    if len({canonical(w) for w in pair}) != 1:
        raise ArithmeticError("canonical() failed to merge a mirror pair")
    g, *_ = ground_set("FGFG")
    if len(g) != 1:
        raise ArithmeticError(f"FGFG still reports {len(g)} folds")
    return ("FGFG's two minima are one fold and its reflection -- walks() "
            "fixes the first step, which kills rotation but not mirroring, "
            "and quotienting by it turns a false 2-way tie into one fold")


def _scalefree():
    """The units are arbitrary, so the answer must not depend on them."""
    for q in ("FCGMFCGM", "MGGMGGMG", "CGCLCLSC"):
        a, ea, *_ = ground_set(q, gain=1.0)
        b, eb, *_ = ground_set(q, gain=7.3)
        if a != b:
            raise ArithmeticError(f"{q} changed fold when every weight was "
                                  f"multiplied by the same constant")
        if abs(eb - ea * 7.3 ** 2) > 1e-9 * abs(eb):
            raise ArithmeticError(f"{q} energy did not scale as a product")
    return ("multiplying every weight by 7.3 leaves the fold identical and "
            "scales the energy by 7.3 squared, as a product of two weights "
            "must -- the hydrophobicity ratio carries no units and the "
            "answer does not read a scale that is not there")


def _parity():
    """Why the first bar measured 14 of 14 and meant nothing."""
    for w in walks(8):
        for i, pi in enumerate(w):
            for dx, dy in STEPS:
                j = {p: k for k, p in enumerate(w)}.get(
                    (pi[0] + dx, pi[1] + dy))
                if j is not None and abs(j - i) % 2 == 0:
                    raise ArithmeticError(
                        f"a contact between {i} and {j} breaks the lattice's "
                        f"bipartite parity")
        break
    alt = "CGCGCGCG"
    a, *_ = ground_set(alt, S_POLAR)
    b, *_ = ground_set(alt, S_GREASY)
    if a != b:
        raise ArithmeticError("an alternating sequence flipped, which the "
                              "parity argument says is impossible")
    return ("a square lattice is bipartite so every contact joins an odd "
            "index to an even one; in ABABAB every contact is A-B and the "
            "energy is one constant times a count, which no reweighting "
            "can reorder -- the first bar measured only such sequences and "
            "its perfect 14 of 14 was measuring nothing")


def _bar():
    f, why = model_bar()
    if not 0.0 < f < 1.0:
        raise ArithmeticError(f"a survival rate of {f} is not a measurement")
    if f > 0.95:
        raise ArithmeticError(f"{f:.2f} survival means the variant barely "
                              f"bites and the bar is not testing anything")
    sample = bar_sample()
    if len(set(sample)) < len(sample) * 0.9:
        raise ArithmeticError("the bar sample repeats itself")
    if not all(any(c in q for c in "CM") for q in sample):
        raise ArithmeticError("the sample contains sequences the variant "
                              "cannot reach, which would inflate the rate")
    return why
