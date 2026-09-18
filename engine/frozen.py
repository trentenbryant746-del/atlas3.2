"""
Why the code we have looks arbitrary: changing it is lethal at once.

engine/code.py closed reading and left one gap: the rule says a
code CAN be afforded and how wide, and any assignment of
subsequences to catalysts works equally well, so nothing selects
one mapping over another. That absence is what makes the real
code look like an accident.

It is not an absence. A mapping is selected by the cost of
CHANGING it, and that cost is computable.

Change one codon's meaning and every sequence containing that
codon now says something else. With a genome of 200 bases at two
bases a codon, 100 codons are encoded, and the chance a given
sequence avoids the changed one is (1 - 1/m)^100:

    4 meanings    one change breaks 100.0% of sequences
    5             100.0%
    20             99.4%
    64             79.3%

SO THE FIRST MAPPING TO ARISE IS THE ONE THAT IS KEPT, and not
because it is good. The cost of change is total from the very
first sequences, before anything has had time to be good. A
narrow code is worse in this respect than a wide one -- with few
meanings every sequence uses every codon -- which is exactly the
situation engine/code.py says the first code was in.

That is the whole of the selection, and it selects for NOTHING
about the mapping itself. What it explains is why the mapping
looks arbitrary: it is arbitrary, and it is frozen.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def codons_encoded(T=259.0):
    """How many codons a maintainable genome holds. DERIVED."""
    from engine.cold import genome_at
    from engine.code import affordable_code
    n, w, _left = affordable_code(T)
    return int(genome_at(T) / w), n, w


def breaks_fraction(meanings, codons):
    """Share of sequences a single meaning-change ruins. DERIVED."""
    return 1.0 - (1.0 - 1.0 / max(meanings, 2)) ** codons


def cost_of_change(T=259.0, meanings=None):
    """-> (fraction broken, codons, meanings). DERIVED."""
    codons, n, _w = codons_encoded(T)
    m = meanings or n
    return breaks_fraction(m, codons), codons, m


def frozen_at(T=259.0, threshold=0.5):
    """-> (bool, why). Is the mapping locked? DERIVED."""
    frac, codons, m = cost_of_change(T)
    return frac >= threshold, (
        f"{m} meanings over {codons} codons, so one change breaks "
        f"{100*frac:.1f}% of every sequence written so far")


def narrow_is_worse():
    """-> [(meanings, fraction)]. A small code freezes harder."""
    codons, _n, _w = codons_encoded()
    return [(m, breaks_fraction(m, codons)) for m in (4, 5, 20, 64)]


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("a_mapping_is_selected_by_the_cost_of_changing_it", _sel)
    t("the_cost_is_total_from_the_first_sequences", _total)
    t("a_narrow_code_freezes_harder", _narrow)
    t("so_the_mapping_is_arbitrary_and_that_is_derived", _arb)
    return all(o[1] for o in out), out


def _sel():
    locked, why = frozen_at()
    if not locked:
        raise ArithmeticError(f"not frozen: {why}")
    return (f"engine/code.py left this open: any assignment of "
            f"subsequences to catalysts works equally well, so "
            f"nothing selects one. Something does -- the cost of "
            f"CHANGING it. {why}. A mapping is not chosen for being "
            f"good, it is kept because changing it is lethal")


def _total():
    frac, codons, m = cost_of_change()
    if frac < 0.99:
        raise ArithmeticError(f"only {100*frac:.1f}% broken")
    return (f"with {m} meanings over {codons} codons a single change "
            f"breaks {100*frac:.2f}% of sequences. That is total, and "
            f"it is total FROM THE FIRST SEQUENCES -- before anything "
            f"has had time to be good. So the first mapping to arise "
            f"is the one kept, and its merit never enters")


def _narrow():
    rows = narrow_is_worse()
    if rows[0][1] <= rows[-1][1]:
        raise ArithmeticError("a wide code freezes harder")
    return (f"a NARROW code freezes harder: "
            + ", ".join(f"{m} meanings {100*f:.1f}%" for m, f in rows)
            + f". With few meanings every sequence uses every codon, "
              f"so nothing survives a change -- and engine/code.py "
              f"says the first code had five meanings, which is the "
              f"worst case for escaping it")


def _arb():
    frac, _c, _m = cost_of_change()
    return (f"the selection is real and it selects for NOTHING about "
            f"the mapping. It is indifferent between assignments and "
            f"locks whichever arrived, at {100*frac:.1f}% cost to "
            f"change. So the answer to why the code looks arbitrary "
            f"is that it IS arbitrary, and the arbitrariness is now "
            f"derived rather than left as a gap. The gap said "
            f"'nothing selects a mapping'; the truth is that "
            f"something selects HAVING one and is blind to WHICH")


if __name__ == "__main__":
    codons, n, w = codons_encoded()
    print(f"  genome holds {codons} codons of {w} bases, "
          f"{n} meanings affordable\n")
    print(f"  {'meanings':>10}{'one change breaks':>20}")
    for m, f in narrow_is_worse():
        print(f"  {m:>10}{100*f:>19.2f}%")
    locked, why = frozen_at()
    print(f"\n  frozen: {locked} -- {why}\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:48}{d[:30]}")
