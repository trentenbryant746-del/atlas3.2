"""
Life with different chemistry, and what stays forced anyway.

engine/biomatter.py builds one biochemistry: four bases, twenty
residues, a phosphate backbone, water. Every number in it is ours.
Nothing in the derivations requires that -- codon_length() already
takes the alphabet size and the number of meanings as arguments,
and the epoch gate is whatever the backbone's elements demand. The
constants were the only thing tying the ladder to Earth.

So this makes the biochemistry a PARAMETER and re-runs the
derivations on it. A universe with six bases is not a variant of
our genetics; it is a different genetics, and the code length,
the redundancy and the information per site all move with it.

WHAT MOVES AND WHAT DOES NOT. That distinction is the whole point
of parameterising rather than just listing possibilities:

    moves     codon length, table size, spare codons, bits per
              site, the epoch a backbone can first exist
    forced    the codon must be long enough to name everything,
              and there is no arrangement where it is not. Four
              bases need three sites; six need two; two need five.
              The RULE is the same in every biochemistry and only
              its output changes.

WHICH BACKBONES ARE POSSIBLE IS NOT A MATTER OF TASTE. A backbone
element has to bond enough ways to chain, and it has to exist when
the life does. Both are already in the repo -- valences in
engine/transitions.py, origins in engine/epochs.py -- so a proposed
biochemistry is checked against them rather than accepted. Silicon
chains and is late; phosphorus chains and is late; helium does not
chain at all and is refused.

OURS IS ONE POINT IN THE SPACE, AND THE CHECK IS THAT IT COMES
BACK. Instantiating Earth biochemistry through the general
machinery must reproduce codon length 3, 64 codons, 43 spare and a
supernova gate -- the same numbers engine/biomatter.py gets by
hard-coding them. A generalisation that cannot return its own
special case has generalised the wrong thing.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import epochs as _ep, life                       # noqa: E402
from engine.experts import BY_SYM                            # noqa: E402
from engine.transitions import VALENCE                       # noqa: E402

DERIVED = "DERIVED"
Fact = life.Fact


@dataclass(frozen=True)
class Biochemistry:
    name: str
    bases: int              # alphabet size of the information polymer
    residues: int           # things the code must name
    stops: int              # plus this many control meanings
    backbone: tuple         # elements the backbone needs
    solvent: str = "H2O"

    def __str__(self):
        return (f"{self.name}: {self.bases} bases, {self.residues} "
                f"residues, backbone {'+'.join(self.backbone)}")


EARTH = Biochemistry("earth", 4, 20, 1, ("C", "H", "O", "N", "P"), "H2O")


def noble_z():
    """Closed-shell atomic numbers, from the shell capacities.

    The aufbau shells hold 2, 8, 8, 18, 18, 32 electrons, and an
    element is inert when the running total lands exactly on a
    closed shell. Those partial sums ARE the noble gases -- 2, 10,
    18, 36, 54, 86 -- so the set is computed rather than listed.
    """
    caps, tot, out = (2, 8, 8, 18, 18, 32), 0, []
    for c in caps:
        tot += c
        out.append(tot)
    return tuple(out)


def viable(bc):
    """-> (ok, why). Can this biochemistry exist at all?"""
    if bc.bases < 2:
        return False, (f"{bc.bases} base(s) cannot encode anything -- an "
                       f"alphabet of one carries no information")
    if bc.residues < 1:
        return False, "nothing to name"
    unknown = [e for e in bc.backbone if e not in BY_SYM]
    if unknown:
        return False, f"{unknown} are not elements"
    # THREE VERDICTS, BECAUSE TWO WERE NOT ENOUGH.
    #
    # The first version demanded every backbone element bond twice,
    # which refused Earth: hydrogen bonds once and is a cap, not a
    # link. The second treated absence from the valence table as
    # zero valence, which refused SILICON -- and silicon bonds four
    # ways. The table holds ten elements; it is not a census.
    #
    # Absence of data is not evidence of inertness. So: a noble gas
    # genuinely cannot bond and is refused; an element with a known
    # valence is judged on it; an element with no entry is REFUSED
    # FOR WANT OF DATA and says so, which is a different answer.
    inert = [e for e in bc.backbone if BY_SYM[e][0] in noble_z()]
    if inert:
        return False, (f"{inert} are noble gases -- closed shells, no "
                       f"bonds, so nothing can be built from them")
    unknown = [e for e in bc.backbone if e not in VALENCE]
    if unknown:
        return None, (f"no valence on record for {unknown}; the table "
                      f"holds {len(VALENCE)} elements and is not a "
                      f"census, so this is unknown rather than impossible")
    chains = [e for e in bc.backbone if VALENCE[e] >= 2]
    if not chains:
        return False, (f"nothing in {list(bc.backbone)} bonds more than "
                       f"once, so there is no chain -- only caps")
    missing = [e for e in bc.backbone if e not in _ep.ORIGIN]
    if missing:
        return False, f"no origin epoch recorded for {missing}"
    return True, (f"{chains} can chain and the rest cap; all have an "
                  f"epoch; {bc.bases} bases can name "
                  f"{bc.residues + bc.stops} meanings")


def code_length(bc):
    """The same rule as ours, run on a different alphabet."""
    ok, why = viable(bc)
    if ok is None:
        raise ValueError(f"cannot judge this biochemistry: {why}")
    if not ok:
        raise ValueError(why)
    k = life.codon_length(bc.bases, bc.residues, bc.stops)
    table = bc.bases ** k.value
    spare = table - (bc.residues + bc.stops)
    return Fact((k.value, table, spare), DERIVED, "ENUMERATE",
                f"{bc.bases}**{k.value} = {table} codes for "
                f"{bc.residues + bc.stops} meanings, {spare} spare -- "
                + ("redundant, as ours is" if spare else
                   "exactly enough, so no redundancy at all"))


def epoch_gate(bc):
    """When this biochemistry can first exist. From its own elements."""
    eras = {e: _ep.ORIGIN[e] for e in bc.backbone}
    era = max(eras.values(), key=lambda x: _ep.ORDER[x])
    late = sorted(e for e, v in eras.items() if v == era)
    return Fact(era, DERIVED, "EXTERNAL",
                f"{eras}; the latest is {late} at {era}, so nothing built "
                f"on this backbone exists before it")


def information(bc):
    """Bits per site, and per code word. DERIVED."""
    k = code_length(bc).value[0]
    per_site = math.log2(bc.bases)
    per_word = k * per_site
    used = math.log2(bc.residues + bc.stops)
    return Fact((per_site, per_word, per_word - used), DERIVED, "IDENTITY",
                f"{per_site:.3f} bits per site, {per_word:.3f} per code "
                f"word, and {per_word - used:.3f} of those are redundancy "
                f"rather than message")


def space(max_bases=8, residues=20, stops=1):
    """Every alphabet size, and what it forces. The rule does not move."""
    out = []
    for b in range(2, max_bases + 1):
        bc = Biochemistry(f"{b}-base", b, residues, stops,
                          EARTH.backbone, EARTH.solvent)
        k, table, spare = code_length(bc).value
        out.append((b, k, table, spare, math.log2(b) * k))
    return out


def backbones(candidates=("P", "S", "Si", "C", "N", "He", "Ne", "Fe")):
    """Which elements could carry a backbone, and when. DERIVED."""
    out = {}
    for e in candidates:
        bc = Biochemistry(f"{e}-backbone", 4, 20, 1, ("C", "H", "O", e))
        ok, why = viable(bc)
        out[e] = (ok, epoch_gate(bc).value if ok else None, why)
    return out


def verdicts(candidates=("P", "S", "Si", "C", "N", "He", "Ne", "Fe")):
    b = backbones(candidates)
    return {"chains": sorted(e for e, v in b.items() if v[0] is True),
            "inert": sorted(e for e, v in b.items() if v[0] is False),
            "unknown": sorted(e for e, v in b.items() if v[0] is None)}


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("earth_comes_back", _earth)
    t("alphabet_changes_the_code", _alpha)
    t("rule_is_the_same_everywhere", _rule)
    t("backbone_must_chain_and_exist", _back)
    t("refuses_the_impossible", _ref)
    return all(o[1] for o in out), out


def _earth():
    """The general machinery must return the special case."""
    from engine import biomatter
    k, table, spare = code_length(EARTH).value
    want_k = biomatter.codon_space().value[0]
    want_table = len(biomatter.CODE)
    if (k, table) != (want_k, want_table):
        raise ArithmeticError(f"earth through the general path gives "
                              f"{k}/{table}, hard-coded gives "
                              f"{want_k}/{want_table}")
    gate = epoch_gate(EARTH).value
    if gate != biomatter.dna_epoch().value:
        raise ArithmeticError(f"gate {gate} against "
                              f"{biomatter.dna_epoch().value}")
    return (f"earth biochemistry through the general machinery: codon "
            f"length {k}, {table} codes, {spare} spare, gated at {gate} "
            f"-- the same numbers biomatter.py gets by hard-coding them")


def _alpha():
    rows = space()
    by = {b: (k, table) for b, k, table, _s, _i in rows}
    if by[4][0] != 3:
        raise ArithmeticError("four bases did not give three sites")
    if by[6][0] >= by[4][0]:
        raise ArithmeticError("a bigger alphabet did not shorten the code")
    if by[2][0] <= by[4][0]:
        raise ArithmeticError("a smaller alphabet did not lengthen it")
    return ("; ".join(f"{b} bases -> {k} sites, {t} codes"
                      for b, k, t in [(b, v[0], v[1])
                                      for b, v in sorted(by.items())][:5])
            + " -- the alphabet moves the answer and the rule does not")


def _rule():
    """Every biochemistry must satisfy the same inequality."""
    bad = []
    for b, k, table, spare, _i in space():
        need = 20 + 1
        if table < need or (b ** (k - 1)) >= need:
            bad.append(b)
    if bad:
        raise ArithmeticError(f"the code is not minimal for {bad} bases")
    return ("for every alphabet from 2 to 8 the code is the SHORTEST that "
            "names all 21 meanings, and one site shorter never suffices -- "
            "one rule, different outputs")


def _back():
    v = verdicts()
    if set(v["inert"]) != {"He", "Ne"}:
        raise ArithmeticError(f"inert came out {v['inert']}, and the "
                              f"noble gases are derived from closed "
                              f"shells at {noble_z()}")
    if "P" not in v["chains"] or "S" not in v["chains"]:
        raise ArithmeticError(f"phosphorus or sulphur refused: {v}")
    # Silicon used to sit here for want of a table entry. It is
    # derived now, chains four ways, and has moved. Iron stays
    # unknown for a real reason: the d-block has several valences
    # and the main-group rule describes one.
    if set(v["unknown"]) != {"Fe"}:
        raise ArithmeticError(f"unknown came out {v['unknown']}")
    if "Si" not in v["chains"]:
        raise ArithmeticError("silicon should chain now that valence is "
                              "derived rather than looked up")
    b = backbones()
    gates = sorted({b[e][1] for e in v["chains"]})
    return (f"chains {v['chains']} gated at {gates}; inert {v['inert']}, "
            f"refused because {noble_z()} are closed shells derived from "
            f"the capacities 2-8-8-18-18-32; unknown {v['unknown']}, "
            f"refused for want of a valence rather than called impossible")


def _ref():
    cases = [(Biochemistry("one-base", 1, 20, 1, EARTH.backbone),
              "carries no information"),
             (Biochemistry("noble", 4, 20, 1, ("C", "H", "He")),
              "are noble gases"),
             (Biochemistry("caps only", 4, 20, 1, ("H", "F")),
              "there is no chain"),
             (Biochemistry("unmeasured", 4, 20, 1, ("C", "H", "Fe")),
              "no valence on record"),
             (Biochemistry("unreal", 4, 20, 1, ("C", "Zz")),
              "not elements")]
    for bc, want in cases:
        ok, why = viable(bc)
        if ok is True or want not in why:
            raise ArithmeticError(f"{bc.name}: ok={ok} why={why}")
    hard = sum(1 for bc, _w in cases if viable(bc)[0] is False)
    soft = sum(1 for bc, _w in cases if viable(bc)[0] is None)
    return (f"{hard} biochemistries refused as impossible and {soft} as "
            f"unjudgeable, each naming the rule -- and the two are "
            f"different answers, not one")


if __name__ == "__main__":
    print(f"  {EARTH}")
    print(f"    {code_length(EARTH)}")
    print(f"    {epoch_gate(EARTH)}")
    print(f"    {information(EARTH)}")
    print("\n  alphabet size against what it forces:")
    print(f"    {'bases':>6}{'sites':>7}{'codes':>8}{'spare':>7}{'bits':>8}")
    for b, k, table, spare, bits in space():
        print(f"    {b:>6}{k:>7}{table:>8}{spare:>7}{bits:>8.2f}")
    print("\n  backbone candidates:")
    for e, (ok, gate, why) in backbones().items():
        print(f"    {e:<4}{'yes' if ok else 'no ':<5}{gate or '':<12}"
              f"{why[:56]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{d[:86]}")
    print("\nall:", ok)
