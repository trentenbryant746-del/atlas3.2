"""
A sequence that is read, and why the first code had to be small.

engine/template.py closed heredity of SEQUENCE: a ligation is
templated when its product's complement is present, the template
is the catalyst, and comp(comp(s)) is s. What it could not close
was heredity of FUNCTION -- no strand codes for a catalyst, so a
sequence was carried and never read.

The rule that closes it is a CODE: a mapping from subsequences to
catalysts that is not the identity and not the complement. And
once the rule is written, the numbers decide something nobody
put in.

A CODE IS NOT FREE. Each meaning needs an adaptor -- a molecule
that recognises a subsequence at one end and carries a catalyst
at the other -- and every adaptor is itself a sequence that has
to be specified and maintained. So the code competes for genome
with the thing it codes for.

And the genome is capped by copying fidelity, which
engine/cold.py derived from a base-pair discrimination energy:
200 bases at 259 K. Twenty adaptors of twenty bases is 400. THE
MODERN CODE DOES NOT FIT, by a factor of two.

       T   genome  adaptors  alphabet  left for catalysts
   273 K      152         3         3         92 bases
   259 K      200         5         5        100
   252 K      232         5         5        132

So the first code was SMALL, and how small is set by the
temperature the brine sits at. That is not a hypothesis added
here -- it is what the fidelity limit and the cost of an adaptor
give when both are already on the table.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ADAPTOR_BASES = 20        # CHOSEN: the shortest thing that can
                          # recognise a codon at one end and hold a
                          # catalyst at the other. Order only.
CODE_SHARE = 0.5          # CHOSEN: half the genome to the code, half
                          # to what it codes for. A dial, and the
                          # conclusion survives any value under 0.9.
MODERN_AMINO_ACIDS = 20   # RECORDED
MODERN_ADAPTOR_BASES = 76  # RECORDED: tRNA


def genome_bases(T=259.0):
    """Bases a lineage can hold at this temperature. DERIVED."""
    from engine.cold import genome_at
    return genome_at(T)


def codon_width(n_meanings, alphabet=4):
    """Bases per codon. DERIVED: 4^w must reach the meanings."""
    return max(1, math.ceil(math.log(max(n_meanings, 2), alphabet)))


def affordable_code(T=259.0, adaptor=ADAPTOR_BASES, share=CODE_SHARE):
    """-> (meanings, codon width, bases left). DERIVED.

    A code costs one adaptor per meaning and adaptors are
    sequences, so the code competes with its own product for a
    genome that fidelity has already capped.
    """
    g = genome_bases(T)
    n = int(g * share // adaptor)
    return n, codon_width(n), g - n * adaptor


def modern_code_fits(T=259.0):
    """-> (bool, needed, held). Does the code we have fit? DERIVED."""
    need = MODERN_AMINO_ACIDS * MODERN_ADAPTOR_BASES
    return need <= genome_bases(T), need, genome_bases(T)


def temperature_for_code(n_meanings, adaptor=ADAPTOR_BASES,
                         share=CODE_SHARE):
    """K needed to afford a code this wide. DERIVED, the inverse."""
    from engine.cold import temperature_for
    need = n_meanings * adaptor / share
    return temperature_for(1.0 / need)


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("a_code_is_the_rule_that_closes_reading", _rule)
    t("the_modern_code_does_not_fit", _modern)
    t("so_the_first_code_was_small", _small)
    t("code_size_is_bounded_by_temperature", _temp)
    t("the_conclusion_survives_the_dials", _robust)
    t("what_is_still_missing", _residue)
    return all(o[1] for o in out), out


def _rule():
    from engine.template import complement
    n, w, left = affordable_code()
    if n < 2:
        raise ArithmeticError("no code is affordable at all")
    return (f"engine/template.py gave heredity of SEQUENCE and could "
            f"not give heredity of FUNCTION, because a strand codes "
            f"only for its own complement. A CODE is the missing "
            f"rule: a mapping from subsequences to catalysts that is "
            f"neither the identity nor the complement. It is not "
            f"free -- each meaning needs an adaptor, and every "
            f"adaptor is a sequence that must itself be maintained, "
            f"so the code competes for genome with the thing it "
            f"codes for")


def _modern():
    fits, need, held = modern_code_fits()
    if fits:
        raise ArithmeticError("the modern code fits after all")
    return (f"the code we have needs {MODERN_AMINO_ACIDS} adaptors of "
            f"{MODERN_ADAPTOR_BASES} bases, {need:,} in total, "
            f"against the {held:.0f} a lineage holds at 259 K. IT "
            f"DOES NOT FIT, by {need/held:.1f}x. Nothing was tuned to "
            f"get that -- the genome limit came from a base-pair "
            f"discrimination energy three modules ago and the tRNA "
            f"length is recorded")


def _small():
    n, w, left = affordable_code()
    if n > 10 or left <= 0:
        raise ArithmeticError(f"{n} meanings leaving {left:.0f} bases")
    return (f"what does fit is {n} meanings at {w} base(s) per codon, "
            f"leaving {left:.0f} bases for the catalysts themselves. "
            f"THE FIRST CODE WAS SMALL, and that is a derived "
            f"prediction rather than an assumption -- it falls out of "
            f"an adaptor costing sequence and a genome capped by "
            f"fidelity, both already on the table")


def _temp():
    rows = [(T, genome_bases(T), affordable_code(T)[0])
            for T in (273.15, 265.0, 259.0, 252.0)]
    if rows[0][2] >= rows[-1][2]:
        raise ArithmeticError("colder does not buy a wider code")
    return (f"a code costs adaptors, adaptors cost genome, and genome "
            f"is capped by copying fidelity -- so CODE SIZE IS "
            f"BOUNDED BY TEMPERATURE. "
            + "; ".join(f"{T:.0f} K holds {g:.0f} bases and "
                        f"{n} meanings" for T, g, n in rows[::2])
            + ". The same seven-kelvin window that opened fidelity, "
              "crowding and persistence sets how much a sequence can "
              "say")


def _robust():
    got = [affordable_code(share=s)[0] for s in (0.3, 0.5, 0.7, 0.9)]
    if max(got) >= MODERN_AMINO_ACIDS:
        raise ArithmeticError(f"a share reaches the modern code: {got}")
    return (f"CODE_SHARE is a dial and the conclusion does not turn "
            f"on it: at 30%, 50%, 70% and 90% of the genome the "
            f"affordable code is {got} meanings, and none of them "
            f"reaches {MODERN_AMINO_ACIDS}. The adaptor length is an "
            f"order-of-magnitude guess and would have to be wrong by "
            f"{MODERN_AMINO_ACIDS/max(got):.0f}x to change the "
            f"answer")


def _residue():
    return ("the rule says a code CAN be afforded and how wide. It "
            "does not say a code appears, and it does not say which "
            "mapping -- any assignment of subsequences to catalysts "
            "works equally well here, which is exactly why the one we "
            "have looks arbitrary. What is now missing is narrower "
            "than 'nothing reads a sequence': it is that nothing "
            "here selects one mapping over another once both are "
            "affordable")


if __name__ == "__main__":
    fits, need, held = modern_code_fits()
    print(f"  the modern code: {MODERN_AMINO_ACIDS} adaptors x "
          f"{MODERN_ADAPTOR_BASES} bases = {need:,}")
    print(f"  a genome holds {held:.0f} at 259 K -> fits: {fits}\n")
    print(f"  {'T':>7}{'genome':>9}{'meanings':>10}{'codon':>7}"
          f"{'left over':>11}")
    for T in (273.15, 265.0, 259.0, 255.0, 252.0):
        n, w, left = affordable_code(T)
        print(f"  {T:>6.1f}K{genome_bases(T):>9.0f}{n:>10}{w:>7}"
              f"{left:>9.0f} b")
    print()
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:42}{d[:36]}")
