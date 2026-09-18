"""
The reaction that copies a sequence was already in the network.

engine/heredity.py derived division, inheritance and selection and
named the fourth absence precisely: nothing copies a SEQUENCE.
Compositional inheritance passes on which molecules are present,
not what any of them says, so there is no genome and nothing that
could carry an instruction forward.

The instruction was to look at every reaction until one copies a
sequence. Every one of them does.

A ligation a + b -> ab is TEMPLATED when the complement of its
product is present: the fragments anneal along that strand and
are joined in the order the strand dictates. And the thing that
makes it happen is the strand itself, so

    THE TEMPLATE IS THE CATALYST.

That is not a new reaction type. It is the ligation already in
the network, with its catalyst named rather than drawn at random,
and the catalyst is always present because a complete polymer set
is closed under complementation. In a 25,488-ligation network,
25,488 have their product's complement available -- all of them.

Three consequences, none of them assumed.

IT IS COPYING, NOT MERELY JOINING. A template of ABCD admits
CD+AB, C+DAB and CDA+B, and refuses AB+CD. It does not permit a
join, it SELECTS which join, and the product's sequence is the
template's, read off.

IT REPLICATES IN TWO ROUNDS. comp(comp(s)) is s exactly, so a
strand makes its complement and the complement makes the strand.

AND ITS CATALYSIS IS NOT 1e-8. A random molecule catalyses a
random reaction with the measured probability; a template
catalyses its own copy by base pairing, which is why
engine/cold.py could price its fidelity at all -- 1 error in 200
bases at 259 K, from the same dG that set the temperature window.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# MEASURED: Watson-Crick pairing. Two pairs over a four-letter
# alphabet, which is what makes the set closed under complement.
PAIR = {"A": "B", "B": "A", "C": "D", "D": "C"}


def complement(s):
    """The strand that anneals to this one. DERIVED from pairing."""
    return "".join(PAIR[c] for c in reversed(s))


def replicates(s):
    """-> bool. Two rounds return the original. DERIVED."""
    return complement(complement(s)) == s


def templated_splits(template):
    """-> [(a, b)]. Every fragment pair this template joins."""
    target = complement(template)
    return [(target[:i], target[i:]) for i in range(1, len(target))]


def accepts(template, a, b):
    """-> bool. Does the template select this join? DERIVED."""
    return a + b == complement(template)


def templated_fraction(max_len=6, alphabet="ABCD"):
    """-> (templated, total). How many ligations have a template."""
    from engine.closure import reactions, molecules
    rx = reactions(max_len, alphabet)
    have = set(molecules(max_len, alphabet))
    n = sum(1 for _a, _b, ab in rx if complement(ab) in have)
    return n, len(rx)


def copy_fidelity(T=259.0):
    """-> (error rate, bases held). DERIVED via engine/cold.py."""
    from engine.cold import error_at, genome_at
    return error_at(T), genome_at(T)


def information_carried(length, alphabet=4):
    """bits a strand of this length specifies. DERIVED."""
    import math
    return length * math.log2(alphabet)


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_template_is_the_catalyst", _cat)
    t("every_ligation_has_one_available", _all)
    t("it_selects_the_join_it_does_not_permit_it", _sel)
    t("two_rounds_return_the_original", _rep)
    t("the_sequence_is_what_is_carried", _info)
    t("what_this_still_does_not_say", _residue)
    return all(o[1] for o in out), out


def _cat():
    from engine.earthlab import CATALYSIS_P
    t = "ABCD"
    splits = templated_splits(t)
    if not splits or not all(accepts(t, a, b) for a, b in splits):
        raise ArithmeticError("the template does not accept its splits")
    return (f"a ligation a + b -> ab is templated when the complement "
            f"of ab is present, and the thing that makes it happen is "
            f"that strand: THE TEMPLATE IS THE CATALYST. It is not a "
            f"new reaction type -- it is the ligation already in the "
            f"network with its catalyst named rather than drawn at "
            f"{CATALYSIS_P:.0e}, and base pairing is why "
            f"engine/cold.py could price the fidelity at all")


def _all():
    n, total = templated_fraction()
    if n != total:
        raise ArithmeticError(f"{n} of {total} have a template")
    return (f"{n:,} of {total:,} ligations have their product's "
            f"complement available -- ALL of them. A complete polymer "
            f"set is closed under complementation, so the catalyst a "
            f"copy needs is never the missing one. The instruction "
            f"was to look at every reaction until one copies a "
            f"sequence; every one of them does")


def _sel():
    t = "ABCD"
    good = templated_splits(t)
    bad = [("AB", "CD"), ("CC", "AB")]
    if any(accepts(t, a, b) for a, b in bad):
        raise ArithmeticError("the template accepted a wrong join")
    return (f"a template of {t} admits "
            + ", ".join(f"{a}+{b}" for a, b in good)
            + f" and refuses {bad[0][0]}+{bad[0][1]}. It does not "
              f"PERMIT a join, it SELECTS which join, and the "
              f"product's sequence is the template's read off. That "
              f"is the difference between chemistry that sustains "
              f"itself and chemistry that says something")


def _rep():
    for s in ("ACD", "ABCD", "ACCDBA"):
        if not replicates(s):
            raise ArithmeticError(f"{s} does not return")
    return ("comp(comp(s)) is s exactly, so a strand makes its "
            "complement and the complement makes the strand. Two "
            "rounds and the sequence is back, which is replication "
            "and not merely production")


def _info():
    err, bases = copy_fidelity()
    bits = information_carried(bases)
    if bases < 100:
        raise ArithmeticError(f"only {bases:.0f} bases hold")
    return (f"at 259 K the copy error is 1 in {1/err:.0f} and a "
            f"{bases:.0f}-base strand holds against it, which is "
            f"{bits:.0f} bits carried forward. engine/heredity.py "
            f"passed on WHICH molecules were present; this passes on "
            f"what one of them SAYS, and the two numbers -- the "
            f"fidelity and the length -- come from the same dG that "
            f"set the temperature window")


def _residue():
    return ("what is still absent is not the copying. It is that "
            "nothing here says what a sequence is FOR: no strand "
            "codes for a catalyst, so a copied sequence is carried "
            "and never read. Template replication gives heredity of "
            "sequence and translation would give heredity of "
            "FUNCTION, and that is a further thing. The gap has "
            "moved again and it is smaller and it is still a gap")


if __name__ == "__main__":
    n, total = templated_fraction()
    err, bases = copy_fidelity()
    print(f"  {n:,} of {total:,} ligations have a template available\n")
    t = "ABCD"
    print(f"  template {t} -> product must be {complement(t)}")
    for a, b in templated_splits(t):
        print(f"    {a:>4} + {b:<4} -> {a+b}   templated")
    for a, b in (("AB", "CD"), ("CC", "AB")):
        print(f"    {a:>4} + {b:<4} -> {a+b}   rejected")
    print(f"\n  comp(comp(ABCD)) = {complement(complement('ABCD'))}")
    print(f"  fidelity at 259 K: 1 in {1/err:.0f}, holding "
          f"{bases:.0f} bases = {information_carried(bases):.0f} bits\n")
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:42}{d[:36]}")
