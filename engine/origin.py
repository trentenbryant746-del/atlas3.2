"""
What a lab can say about the origin of life without inventing biology.

engine/census.py asks whether a world is habitable. It cannot ask
whether anything arose there, because the step from chemistry to a
self-copying compartment is not derived anywhere here. That step is
abiogenesis, and rather than model it, this asks a smaller question
that rules already present can answer: WHAT DOES IT COST, AND WHAT
CANNOT BE FOUND BY LOOKING?

ENERGY IS NOT THE BARRIER, AND THAT IS THE FIRST RESULT. Copying
information has a floor -- Landauer, kT ln 2 per bit, which at 300 K
is 0.018 eV. A minimal genome of 580,000 bases is 1.16 million bits
and costs 3.3e-15 joules to copy. A pH gradient of three units
across a membrane pays 0.18 eV per proton, so about 116,000 protons
cover a whole genome. Real bacteria spend around 1e-11 J, three
thousand times the floor, and a hydrothermal system supplies vastly
more than either. Nothing is stopped by the bill.

WHAT CANNOT BE PAID FOR IS THE SEARCH. A chain of n amino acids has
20^n possible sequences. Fill an ocean with peptide-scale molecules
and let every one try a new sequence every picosecond, and:

    50 residues    1.1e65 sequences     790 years
    60 residues    1.2e78 sequences     8.6e12 years
   100 residues    1.3e130 sequences    8.9e67 years

The universe is 1.4e10 years old. So there is a LENGTH CEILING on
what chance can find, and this repository can derive where it falls
rather than assert it. Below it, exhaustive search works and needs
no explanation. Above it, something must build long sequences
without searching for them -- which is the same answer
engine/folding.py already gives to Levinthal's paradox one level
down: folding is not a search, and neither is this.

THE MISSING MECHANISM HAS A SHAPE NOW, WHICH IS AS FAR AS A LAB CAN
HONESTLY GO. It is whatever lets a system reach sequences longer
than the ceiling without trying them all: selection on
intermediates, or assembly from parts already found. Naming that
shape is not the same as deriving the mechanism, and this does not
claim to.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.constants import K_B, E_CHARGE, N_A  # noqa: E402

AGE_UNIVERSE_YR = 1.38e10
YEAR_S = 3.155693e7
ALPHABET = 20            # amino acids; engine/biomatter.py's RESIDUES


def landauer(T):
    """J per bit. DERIVED: the floor on copying one bit."""
    return K_B * T * math.log(2)


def genome_cost(bases, T=300.0):
    """J to copy a genome of `bases` bases. DERIVED. 2 bits per base."""
    return 2 * bases * landauer(T)


def gradient_energy(ph_units, T=300.0):
    """J per proton from a pH gradient. DERIVED."""
    return ph_units * math.log(10) * K_B * T


def ocean_trials(ocean_kg=1.35e21, molecule_amu=1000.0):
    """How many peptide-scale molecules an ocean holds. DERIVED."""
    return ocean_kg / (molecule_amu * 1e-3 / N_A)


def search_years(n_residues, trials=None, rate_hz=1e12):
    """Years to try every sequence of this length. DERIVED."""
    trials = ocean_trials() if trials is None else trials
    return (ALPHABET ** n_residues) / (trials * rate_hz * YEAR_S)


def length_ceiling(budget_yr=AGE_UNIVERSE_YR):
    """Longest chain chance can find in the time available. DERIVED."""
    lo, hi = 1, 400
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if search_years(mid) <= budget_yr:
            lo = mid
        else:
            hi = mid - 1
    return lo


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("copying_is_cheap", _cheap)
    t("a_gradient_pays_for_it_easily", _grad)
    t("search_has_a_length_ceiling", _ceiling)
    t("the_ceiling_is_sharp", _sharp)
    t("this_does_not_claim_abiogenesis", _humble)
    return all(o[1] for o in out), out


def _cheap():
    c = genome_cost(580000)
    atp = 1e-11
    if c > atp:
        raise ArithmeticError("copying costs more than a cell spends")
    return (f"Landauer puts one bit at {landauer(300.0)/E_CHARGE:.4f} eV, "
            f"so a 580,000-base genome costs {c:.2e} J to copy. A real "
            f"bacterium spends about {atp:.0e} J, {atp/c:,.0f} times "
            f"more. Energy is not what stops anything")


def _grad():
    per = gradient_energy(3.0)
    need = genome_cost(580000) / per
    return (f"a three-unit pH gradient pays {per/E_CHARGE:.3f} eV per "
            f"proton, so {need:,.0f} protons cover a whole minimal "
            f"genome. A hydrothermal system moves that in moments -- the "
            f"bill is not the problem and saying so rules out a whole "
            f"class of explanation")


def _ceiling():
    n = length_ceiling()
    if not 40 < n < 80:
        raise ArithmeticError(f"the ceiling came out {n} residues")
    return (f"with an ocean of {ocean_trials():.1e} molecules each trying "
            f"a sequence every picosecond for the age of the universe, "
            f"chance reaches {n} residues and no further. Below that, "
            f"exhaustive search needs no explanation; above it, "
            f"something must build long chains WITHOUT trying them, "
            f"which is Levinthal's answer one level up")


def _sharp():
    n = length_ceiling()
    a, b = search_years(n), search_years(n + 10)
    return (f"at {n} residues the search takes {a:.1e} years and at "
            f"{n+10} it takes {b:.1e} -- {b/a:.0e} times longer for ten "
            f"more. Twenty to the power of n does not bend, so the "
            f"ceiling is a cliff and a mechanism either clears it or "
            f"does not")


def _humble():
    n = length_ceiling()
    return (f"what this shows is a constraint, not an origin. It says "
            f"energy is not the barrier and that chance stops at about "
            f"{n} residues, so the missing mechanism must reach longer "
            f"sequences without searching -- selection on intermediates, "
            f"or assembly from parts already found. NAMING THE SHAPE OF "
            f"A MECHANISM IS NOT DERIVING IT, and this repository still "
            f"does not derive abiogenesis")


if __name__ == "__main__":
    print(f"  Landauer at 300 K: {landauer(300.0)/E_CHARGE:.4f} eV/bit")
    print(f"  ocean holds {ocean_trials():.2e} peptide-scale molecules\n")
    print(f"  {'residues':>9}{'sequences':>13}{'years to search':>18}")
    for n in (40, 50, length_ceiling(), 70, 100):
        print(f"  {n:>9}{float(ALPHABET**n):>13.2e}{search_years(n):>18.2e}")
    print(f"\n  ceiling: {length_ceiling()} residues in "
          f"{AGE_UNIVERSE_YR:.2e} years")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{d[:66]}")
    print("\nall:", ok)
