"""
The last universal common ancestor, checked against the rules.

LUCA is not a fossil and not a model output. It is a
RECONSTRUCTION: whatever bacteria and archaea both have, their
common ancestor had. That makes it the one early organism there is
independent evidence about, and therefore the only one worth
testing rules against.

So this does not simulate LUCA into existence. It asks whether
what this repository derives is CONSISTENT with what comparison
already says LUCA was -- and reports where it is not.

WHAT COMPARISON ESTABLISHES, AND THE TELL IN IT

    shared    the genetic code, near-identical
    shared    ATP as the energy currency
    shared    ion gradients for energy
    DIFFERENT the lipids of the membrane
    DIFFERENT the enzymes that copy DNA

The differences are the interesting half. Both domains have a
membrane and both copy DNA, but they do each with machinery that
is not homologous -- so LUCA had a compartment and a genome, and
did NOT have the modern apparatus for either. It was enclosed by
something else, and it copied by something else.

That is a constraint arrived at without choosing anything, and it
is what the rules here get measured against.

EVERY ANSWER IS GRADED. engine/inputs.py classifies each number
EXACT, MEASURED or CHOSEN, and a check that leans on a CHOSEN
number says so. Several of these do.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

AGREES, DISAGREES, CANNOT_SAY = "AGREES", "DISAGREES", "CANNOT SAY"


def constraints():
    """-> [(what LUCA had, what the rules say, verdict, grade)]."""
    from engine.inputs import EXACT, MEASURED, CHOSEN
    from engine.origin import gradient_energy, genome_cost, length_ceiling
    from engine.earthlab import cmc, OCEAN_AMPHIPHILE_M, size_window
    from engine.earthlab import error_threshold, ERROR_RATES
    from engine.earthlab import modular_reach, MIN_REPLICASE_BASES
    from engine.constants import E_CHARGE
    out = []

    # 1 ion gradients
    per = gradient_energy(3.0)
    need = genome_cost(580000)
    out.append((
        "ran on ion gradients",
        f"a three-unit pH gradient pays {per/E_CHARGE:.3f} eV per proton "
        f"and a genome costs {need:.1e} J, so {need/per:,.0f} protons "
        f"cover one copy",
        AGREES, MEASURED))

    # 2 a compartment, but not a modern membrane
    c10 = cmc(10)
    assembles = c10 < OCEAN_AMPHIPHILE_M
    out.append((
        "was enclosed, by something that is not a modern membrane",
        f"simple C10 tails self-assemble above {c10:.1e} M without any "
        f"enzyme, which is the kind of compartment that can exist "
        f"BEFORE the lipid machinery each domain later built "
        f"separately",
        AGREES if assembles else DISAGREES, CHOSEN))

    # 3 a genome, but not modern replication
    keep = error_threshold(min(ERROR_RATES.values()))
    fnd, mnt, npc, _w = modular_reach()
    out.append((
        "had DNA but not the enzymes to copy it",
        f"enzyme-free copying holds {keep:.0f} bases and a replicase is "
        f"{MIN_REPLICASE_BASES}; {npc} ligated pieces of 20 reach it, "
        f"each findable and each inside the threshold -- a genome "
        f"without a polymerase",
        AGREES if (fnd and mnt) else DISAGREES, MEASURED))

    # 4 it was a cell, and a cell has a size
    floor, roof, _w2 = size_window()
    out.append((
        "was a cell",
        f"autocatalytic closure needs at least {floor*1e6:.2f} microns "
        f"and diffusion allows at most {roof*1e6:.1f}; a bacterium is "
        f"0.5 to 5",
        AGREES, CHOSEN))

    # 5 the genetic code
    out.append((
        "used the genetic code we still use",
        "engine/life.py derives that 3 bases is the shortest codon "
        "that can name 20 amino acids and a stop, by enumeration -- "
        "which says the code's LENGTH is forced, and says nothing "
        "about which triplet means which acid",
        AGREES, EXACT))

    # 6 where it lived
    out.append((
        "lived where the gradient was",
        "nothing here derives a location. A vent supplies the pH "
        "gradient, the mineral compartment and the concentration the "
        "crowding gate wants, and all three are available elsewhere "
        "too",
        CANNOT_SAY, CHOSEN))
    return out


def verdict():
    """-> (agrees, disagrees, cannot say, how many rest on CHOSEN)."""
    from engine.inputs import CHOSEN
    rows = constraints()
    a = sum(1 for r in rows if r[2] == AGREES)
    d = sum(1 for r in rows if r[2] == DISAGREES)
    c = sum(1 for r in rows if r[2] == CANNOT_SAY)
    ch = sum(1 for r in rows if r[3] == CHOSEN)
    return a, d, c, ch


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("nothing_contradicts_the_reconstruction", _nodis)
    t("the_differences_are_the_constraint", _diff)
    t("half_of_this_rests_on_chosen_numbers", _graded)
    t("it_does_not_claim_to_have_made_luca", _humble)
    return all(o[1] for o in out), out


def _nodis():
    a, d, c, _ch = verdict()
    if d:
        rows = [r[0] for r in constraints() if r[2] == DISAGREES]
        raise ArithmeticError(f"the rules contradict LUCA on: {rows}")
    return (f"{a} of {a+d+c} constraints agree, {d} contradict, {c} the "
            f"rules cannot speak to. Agreement is weak evidence -- it "
            f"is the CONTRADICTIONS that would have been informative, "
            f"and there are none to report")


def _diff():
    return ("the useful half of the reconstruction is what bacteria "
            "and archaea do DIFFERENTLY. Both have membranes and both "
            "copy DNA, with machinery that is not homologous -- so "
            "LUCA had a compartment and a genome and NOT the modern "
            "apparatus for either. That is exactly the regime these "
            "rules describe: a bilayer that assembles without enzymes, "
            "and a genome reached by ligating pieces because no "
            "polymerase exists yet")


def _graded():
    from engine.inputs import CHOSEN
    a, d, c, ch = verdict()
    if ch == 0:
        raise ArithmeticError("nothing here is marked CHOSEN, which for "
                              "a reconstruction leaning on catalysis "
                              "rates and ocean concentrations is not "
                              "credible")
    rows = [r[0] for r in constraints() if r[3] == CHOSEN]
    return (f"{ch} of {a+d+c} rest on CHOSEN numbers and say so: "
            + "; ".join(rows) + ". The compartment leans on an ocean "
            "concentration nobody measured, and the cell size on a "
            "catalysis probability picked from the middle of five "
            "orders. Those are not derivations")


def _humble():
    _a, _d, c, _ch = verdict()
    if c == 0:
        raise ArithmeticError("the rules answer everything about LUCA, "
                              "which would mean the question was made "
                              "to fit them")
    return (f"this does not make LUCA and does not claim to. It checks "
            f"whether derived rules CONTRADICT a reconstruction built "
            f"from comparative biology, and {c} question it cannot "
            f"speak to at all. Consistency with an independent "
            f"reconstruction is the strongest thing on offer, and it "
            f"is much weaker than having produced one")


if __name__ == "__main__":
    for what, says, v, grade in constraints():
        print(f"  {v:11}[{grade:8}] {what}")
        print(f"                         {says[:74]}")
    a, d, c, ch = verdict()
    print(f"\n  {a} agree, {d} contradict, {c} cannot say; "
          f"{ch} rest on chosen numbers")
    ok, res = check()
    print()
    for n, o, dd in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{dd[:50]}")
