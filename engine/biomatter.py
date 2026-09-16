"""
The ladder above chemistry: nucleotide, codon, gene, genome, cell,
organism. Every rung gated by when its constituents can exist.

engine/particles.py climbs particle -> atom -> compound and stops
where chemistry stops. This keeps going, under the same two rules
the rest of the repo runs on: every rung derives from the one below,
and nothing exists before its parts do.

    nucleotide   a compound with a formula, so its epoch is the
                 latest of its elements
    codon        three nucleotides; the 3 is DERIVED, not assumed
    gene         n codons, so 3n bases and 2 bits per base
    genome       n bases, with information content checked two ways
    cell         bounded below by the DNA it must hold and above by
                 what diffusion can feed
    organism     bounded by engine/life.py -- diffusion, the
                 square-cube law, and the epoch its atoms allow

WHAT PHOSPHORUS DECIDES. Every nucleotide carries a phosphate, and
phosphorus is Z=15, which engine/epochs.py puts in the supernova
band. So DNA -- and every organism built from it -- cannot exist
before supernovae, and that falls out of the periodic table rather
than being asserted anywhere. engine/life.earliest_possible_life()
reaches the same epoch from the element list; this reaches it from
the molecule, and the two agreeing is the check.

WHAT THE GENETIC CODE BUYS BACK. life.codon_length() derives the 3
from "4 bases must name 21 things", with the 20 and the 1 passed in
as DEFAULT ARGUMENTS. With the code table present those two numbers
are COUNTED instead of assumed, fed back, and must still give 3 with
4**3 equal to the number of entries. A derivation whose inputs come
from data it did not use is a second route, not a restatement.

THE CHECK WORTH HAVING. A genome's information content is derivable
two ways -- 2 bits per base because there are four, and the Shannon
entropy of the actual base counts. They agree only at uniform
composition, and nothing real is uniform, so the rule reports the
GAP rather than demanding they match. The gap is GC bias, and it is
biology rather than error.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import epochs as _ep                             # noqa: E402
from engine import life                                      # noqa: E402
from engine.experts import FORMULA, BY_SYM                   # noqa: E402

DERIVED, ASSERTED = "DERIVED", "ASSERTED"
Fact = life.Fact

# ASSERTED: measured structures of the four DNA nucleoside
# monophosphates. Physics does not entail them; everything above
# them is derived from these formulas.
NUCLEOTIDES = {
    "dAMP": "C10H14N5O6P",
    "dCMP": "C9H14N3O7P",
    "dGMP": "C10H14N5O7P",
    "dTMP": "C10H15N2O8P",
}
NUC_SOURCE = "structures of the deoxyribonucleoside monophosphates"
BASES = "ACGT"

# ASSERTED: the standard genetic code, on DNA sense codons so it
# composes with engine/experts.py's DNA handling without a
# transcription step. '*' is stop.
CODE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}
CODE_SOURCE = "standard genetic code, NCBI translation table 1"

# ASSERTED: B-form DNA geometry, measured.
BP_RISE_M = 0.34e-9
HELIX_DIAM_M = 2.0e-9
DNA_GEOM_SOURCE = "B-form DNA fibre diffraction"


def _elements(formula):
    out = {}
    for sym, n in FORMULA.findall(formula):
        if not sym:
            continue
        if sym not in BY_SYM:
            raise ValueError(f"{sym!r} is not an element")
        out[sym] = out.get(sym, 0) + int(n or 1)
    if not out:
        raise ValueError("no elements in formula")
    return out


# ------------------------------------------------------------ nucleotide
def nucleotide_epoch(name="dAMP"):
    """When can this nucleotide exist? Straight from its formula."""
    if name not in NUCLEOTIDES:
        raise ValueError(f"no formula on record for {name!r}; have "
                         f"{sorted(NUCLEOTIDES)}")
    f = NUCLEOTIDES[name]
    els = _elements(f)
    eras = {e: _ep.ORIGIN.get(e) for e in els}
    missing = [e for e, v in eras.items() if v is None]
    if missing:
        raise KeyError(f"no origin epoch for {missing}")
    era = max(eras.values(), key=lambda x: _ep.ORDER[x])
    late = sorted(e for e, v in eras.items() if v == era)
    return Fact(era, DERIVED, "EXTERNAL",
                f"{name} = {f}; its elements appear {eras}, and the latest "
                f"is {late} at {era}")


def dna_epoch():
    """DNA needs all four, so the latest of the four decides."""
    eras = {n: nucleotide_epoch(n).value for n in NUCLEOTIDES}
    era = max(eras.values(), key=lambda x: _ep.ORDER[x])
    return Fact(era, DERIVED, "EXTERNAL",
                f"all four nucleotides are needed; {eras} -> {era}")


# ----------------------------------------------------------------- codon
def code_shape():
    """Count what life.codon_length() otherwise takes as arguments."""
    meanings = set(CODE.values())
    aminos = sorted(m for m in meanings if m != "*")
    stops = sorted(c for c, m in CODE.items() if m == "*")
    bases = sorted({b for c in CODE for b in c})
    k = life.codon_length(len(bases), len(aminos), 1)
    if k.value != 3:
        raise ArithmeticError(f"the counted table forces k={k.value}")
    if len(bases) ** k.value != len(CODE):
        raise ArithmeticError(f"{len(bases)}**{k.value} != {len(CODE)}")
    return Fact((len(bases), len(aminos), len(stops), len(CODE)),
                DERIVED, "REDUNDANT",
                f"{len(bases)} bases and {len(aminos)} amino acids counted "
                f"out of the table still force a codon length of "
                f"{k.value}, and {len(bases)}**{k.value} = {len(CODE)} is "
                f"exactly the number of entries; 1 stop meaning across "
                f"{len(stops)} codons")


def codon_space():
    """64, with the 3 derived rather than assumed."""
    k = life.codon_length().value
    n = 4 ** k
    return Fact((k, n), DERIVED, "ENUMERATE",
                f"{k} bases per codon (4**2 < 21 <= 4**3), so {n} codons")


# ------------------------------------------------------------ gene, genome
def gene(codons):
    """A gene is codons; bases and bits follow. INVERSE on the bases."""
    if codons < 1:
        raise ValueError("a gene has at least one codon")
    k = life.codon_length().value
    bases = codons * k
    if bases // k != codons:
        raise ArithmeticError("codon count is not recoverable")
    bits = bases * math.log2(4)
    return Fact((bases, bits), DERIVED, "INVERSE",
                f"{codons} codons = {bases} bases = {bits:.0f} bits at 2 "
                f"per base; codons recover as {bases // k}")


def _entropy(ps):
    tot = sum(ps)
    if not math.isclose(tot, 1.0, rel_tol=1e-9):
        raise ArithmeticError(f"probabilities sum to {tot}, not 1")
    return -sum(p * math.log2(p) for p in ps if p > 0)


def genome_information(base_counts):
    """Two routes to a genome's information, and the gap between them."""
    total = sum(base_counts.values())
    if total < 1:
        raise ValueError("no bases")
    unknown = sorted(set(base_counts) - set(BASES))
    if unknown:
        raise ValueError(f"not DNA bases: {unknown}")
    naive = total * 2.0
    h = _entropy([c / total for c in base_counts.values()])
    actual = total * h
    # REDUNDANT check with teeth: uniform counts must make them equal
    u = _entropy([0.25] * 4)
    if not math.isclose(u, 2.0, rel_tol=1e-12):
        raise ArithmeticError("entropy of a uniform base is not 2 bits")
    gc = sum(base_counts.get(b, 0) for b in "GC") / total
    return Fact((naive, actual), DERIVED, "REDUNDANT",
                f"{total:,} bases: {naive:,.0f} bits at 2 per base, "
                f"{actual:,.0f} at the measured entropy ({h:.4f}/base); "
                f"GC {gc:.1%}, and the {naive-actual:,.0f}-bit gap IS that "
                f"bias, not an error")


# ------------------------------------------------------------------ cell
def dna_volume(bp):
    """A genome as a B-DNA cylinder. INVERSE on the base pairs."""
    if bp < 1:
        raise ValueError("a genome has at least one base pair")
    v = math.pi * (HELIX_DIAM_M / 2) ** 2 * (bp * BP_RISE_M)
    back = v / (math.pi * (HELIX_DIAM_M / 2) ** 2 * BP_RISE_M)
    if not math.isclose(back, bp, rel_tol=1e-9):
        raise ArithmeticError("genome volume is not invertible")
    return Fact(v, DERIVED, "INVERSE",
                f"{bp:,} bp in a {HELIX_DIAM_M*1e9:.1f} nm cylinder rising "
                f"{BP_RISE_M*1e9:.2f} nm each = {v*1e27:,.0f} nm^3; "
                f"recovered {back:,.0f} bp")


def cell_window(bp, consumption=1e-3):
    """-> (floor, ceiling). Which bound actually binds.

    The floor is the sphere that just contains the DNA at packing
    fraction 1 -- physically unreachable, and chosen for exactly that
    reason: it is a bound nothing can argue with, where a realistic
    one would need a number this repo does not derive. The ceiling is
    what diffusion can feed.
    """
    v = dna_volume(bp).value
    lo = (v / (4 / 3 * math.pi)) ** (1 / 3)
    hi = life.diffusion_limit(consumption).value
    if hi <= lo:
        raise ArithmeticError(
            f"no viable size: floor {lo*1e9:.1f} nm exceeds ceiling "
            f"{hi*1e9:.1f} nm")
    return Fact((lo, hi), DERIVED, "SPAN",
                f"{bp:,} bp: r between {lo*1e9:.1f} nm and {hi*1e6:.1f} um, "
                f"a factor of {hi/lo:,.0f}. The floor is "
                f"{math.log10(hi/lo):.1f} orders below the ceiling, so "
                f"diffusion decides a cell's size and the genome does not")


def cell_ok(radius_m, bp, consumption=1e-3):
    """-> (ok, rule, why). A cell that cannot exist, and which rule says."""
    if radius_m <= 0:
        return False, "geometry", "a radius is positive"
    lo, hi = cell_window(bp, consumption).value
    if radius_m < lo:
        return (False, "containment",
                f"r={radius_m*1e9:.1f} nm cannot hold {bp:,} bp, which need "
                f"at least {lo*1e9:.1f} nm")
    if radius_m > hi:
        return (False, "diffusion",
                f"r={radius_m*1e6:.1f} um is past the {hi*1e6:.1f} um "
                f"diffusion can feed -- the middle suffocates")
    return True, "none", (f"r={radius_m*1e6:.3f} um is inside the window "
                          f"for {bp:,} bp")


# -------------------------------------------------------------- organism
def organism_bounds(consumption=1e-3):
    """Everything the biophysics permits, assembled."""
    d = life.diffusion_limit(consumption)
    sq = life.square_cube_limit()
    era = dna_epoch().value
    return Fact((d.value, sq.value, era), DERIVED, "EXTERNAL",
                f"anything relying on diffusion stays under "
                f"{d.value*1e3:.2f} mm; a land skeleton crushes itself past "
                f"{sq.value:.0f} m; and none of it before {era}, because "
                f"DNA needs phosphorus")


# -------------------------------------------------------- self-checking
def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("nucleotide_epoch", lambda: nucleotide_epoch().why)
    t("two_routes_to_life", _two)
    t("code_shape", lambda: code_shape().why)
    t("gene_inverse", lambda: gene(300).why)
    t("genome_two_ways", _info)
    t("cell_window", lambda: cell_window(4_600_000).why)
    t("cell_refuses", _cell)
    t("organism_bounds", lambda: organism_bounds().why)
    t("epoch_gating", _gate)
    return all(o[1] for o in out), out


def _two():
    a = life.earliest_possible_life().value
    b = dna_epoch().value
    if a != b:
        raise ArithmeticError(f"element route says {a}, molecule route {b}")
    return (f"the element list and the nucleotide formulas both give "
            f"{a} -- two routes, written apart, agreeing")


def _info():
    uniform = genome_information({"A": 250, "C": 250, "G": 250, "T": 250})
    n, a = uniform.value
    if not math.isclose(n, a, rel_tol=1e-9):
        raise ArithmeticError("uniform bases must make the routes agree")
    skew = genome_information({"A": 400, "C": 100, "G": 100, "T": 400})
    n2, a2 = skew.value
    if a2 >= n2:
        raise ArithmeticError("a skewed genome must carry LESS information")
    return (f"uniform: both routes give {n:.0f} bits. Skewed 80/20: "
            f"{n2:.0f} naive against {a2:.0f} measured, a "
            f"{n2-a2:.0f}-bit gap that IS the composition bias")


def _cell():
    hi = cell_window(4_600_000).value[1]
    cases = [((50e-9, 4_600_000), "containment"),
             ((hi * 10, 4_600_000), "diffusion"),
             ((-1.0, 1000), "geometry")]
    for (r, bp), want in cases:
        ok, rule, _why = cell_ok(r, bp)
        if ok or rule != want:
            raise ArithmeticError(f"r={r:g} bp={bp} expected {want}, "
                                  f"got ok={ok} rule={rule}")
    ok, rule, _w = cell_ok(1e-6, 4_600_000)
    if not ok:
        raise ArithmeticError(f"a 1 um bacterium was rejected by {rule}")
    return (f"{len(cases)} impossible cells refused by "
            f"{[c[1] for c in cases]}, and a 1 um cell with a bacterial "
            f"genome accepted")


def _gate():
    """Nothing on this ladder may predate its constituents."""
    era = dna_epoch().value
    idx = _ep.ORDER[era]
    for n in NUCLEOTIDES:
        if _ep.ORDER[nucleotide_epoch(n).value] > idx:
            raise ArithmeticError(f"{n} postdates DNA itself")
    earlier = [e for e in _ep.ORDER if _ep.ORDER[e] < idx]
    return (f"DNA is gated at {era} (index {idx}); all four nucleotides "
            f"are at or before it, and the {len(earlier)} earlier epochs "
            f"cannot hold any of this ladder")


if __name__ == "__main__":
    for f in (nucleotide_epoch(), dna_epoch(), code_shape(), codon_space(),
              gene(300), genome_information({"A": 897, "C": 603,
                                             "G": 601, "T": 899}),
              dna_volume(4_600_000), cell_window(4_600_000),
              organism_bounds()):
        print(" ", f)
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:20}{d[:100]}")
    print("\nall:", ok)
