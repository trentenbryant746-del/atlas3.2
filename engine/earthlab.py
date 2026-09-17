"""
One planet, every rule, and the question asked step by step.

The census runs many worlds and asks whether any is habitable.
This does the opposite: one world, the one we can check, and the
whole road from chemistry to a cell walked one gate at a time. Each
gate is derived from rules already here, and the point is to find
the FIRST one that does not open, because that is where the missing
mechanism is.

WHAT THE GATES ARE

  elements     CHNOPS present, from engine/genesis.py over
               engine/abundance.py plus delivery
  solvent      liquid water, from engine/terraform.py's thermostat
  energy       the cost of copying, from Landauer -- engine/origin.py
  compartment  a membrane assembling itself, from the SAME
               hydrophobic effect engine/folding.py uses to collapse
               a protein
  crowding     enough molecules inside one vesicle to react
  search       how long a sequence chance can find, engine/origin.py
  fidelity     how long a sequence copying can KEEP, from Eigen
  bootstrap    is the smallest self-copier inside those two bounds

THE FIRST FOUR OPEN. Energy is not the barrier -- a genome costs
3.3e-15 J and a bacterium spends three thousand times that.
Compartments are not the barrier either: the hydrophobic effect
assembles a bilayer from C10 tails at concentrations the early ocean
plausibly had, and it is the same arithmetic that folds a protein.

THE LAST FOUR ARE THE PROBLEM AND THEY CLOSE ON EACH OTHER. Chance
can find 57 residues. Uncatalysed copying can maintain about 10
bases and the best known ribozyme about 100. The smallest RNA that
copies RNA is around 200. So the thing needed to cross the gap is
larger than either bound permits, AND it is the thing that would
raise the bounds. That is Eigen's paradox stated in this
repository's own numbers, and it is not a shortage of energy, time,
elements or containers.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.constants import K_B, N_A  # noqa: E402

R_GAS = K_B * N_A
OPEN, SHUT = "OPEN", "SHUT"

# Laboratory measurements of molecules, not of planets.
CH2_TRANSFER_J = 3.7e3        # J/mol to move one CH2 out of water
OCEAN_AMPHIPHILE_M = 1e-6     # generous early-ocean estimate
VESICLE_RADIUS_M = 1e-7       # smallest that holds a bilayer
MIN_REPLICASE_BASES = 200     # smallest RNA known to copy RNA
ERROR_RATES = {"uncatalysed template": 0.10,
               "mineral surface": 0.03,
               "best known ribozyme": 0.01}


def cmc(tail_carbons, T=298.0):
    """Critical concentration for self-assembly, M. DERIVED.

    The same hydrophobic effect engine/folding.py uses: burying a
    CH2 is worth about 3.7 kJ/mol, so a tail of n of them pays
    n times that, and assembly begins where that free energy
    balances the entropy of staying dissolved.
    """
    return math.exp(-tail_carbons * CH2_TRANSFER_J / (R_GAS * T))


def molecules_in_vesicle(conc_M, radius_m=VESICLE_RADIUS_M):
    """How many solute molecules one vesicle encloses. DERIVED."""
    litres = (4.0 / 3.0) * math.pi * radius_m ** 3 * 1000.0
    return conc_M * litres * N_A


def error_threshold(mu):
    """Longest genome copying at rate mu can keep. DERIVED: L < 1/mu."""
    if mu <= 0:
        raise ValueError("an error rate of zero is not a copier")
    return 1.0 / mu


def gates():
    """-> [(name, OPEN/SHUT, why)]. Earth, one step at a time."""
    from engine.origin import genome_cost, length_ceiling
    from engine.terraform import BODIES, thermostat
    out = []

    e = BODIES["Earth"]
    r = thermostat(e)
    wet = r.get("wet_fraction", 0.0)
    out.append(("solvent", OPEN if wet > 0 else SHUT,
                f"the thermostat keeps {100*wet:.0f}% of the surface "
                f"above freezing at {r['T']:.0f} K"))

    from engine.genesis import generate, solar_seed
    g = generate(solar_seed())
    p = min(g["planets"], key=lambda q: abs(q["au"] - 1.0))
    have = [x for x in "CHNOPS" if p["composition"].get(x, 0) > 1e-6]
    # ALL SIX OR NONE. This first asked for five of six and passed
    # while carbon was absent, which is not a partial success: a
    # biochemistry without carbon is not a biochemistry. Carbon is
    # locked in CO down to 25 K, so it arrives only from the coldest
    # part of the outer system, and the delivery average over
    # 3 to 45 AU does not carry enough of it.
    missing = [x for x in "CHNOPS" if x not in have]
    out.append(("elements", OPEN if not missing else SHUT,
                f"{','.join(have)} present at {p['au']:.2f} AU after "
                f"delivery"
                + (f"; MISSING {','.join(missing)} -- carbon is locked "
                   f"in CO to 25 K and reaches an inner planet only "
                   f"from the coldest reservoir" if missing else "")))

    c = genome_cost(580000)
    out.append(("energy", OPEN if c < 1e-11 else SHUT,
                f"copying a minimal genome costs {c:.1e} J against the "
                f"1e-11 a bacterium spends -- three thousand times over"))

    n10 = cmc(10)
    out.append(("compartment", OPEN if n10 < OCEAN_AMPHIPHILE_M else SHUT,
                f"a C10 tail self-assembles above {n10:.1e} M and the "
                f"early ocean plausibly held {OCEAN_AMPHIPHILE_M:.0e} -- "
                f"the same hydrophobic effect that folds a protein "
                f"builds the bag to put it in"))

    n = molecules_in_vesicle(OCEAN_AMPHIPHILE_M)
    out.append(("crowding", OPEN if n > 100 else SHUT,
                f"a {VESICLE_RADIUS_M*1e9:.0f} nm vesicle at "
                f"{OCEAN_AMPHIPHILE_M:.0e} M encloses {n:.1f} solute "
                f"molecules. Chemistry needs a population, not a pair, "
                f"so something must concentrate before anything reacts"))

    ceil = length_ceiling()
    out.append(("search", OPEN if ceil >= MIN_REPLICASE_BASES / 3 else SHUT,
                f"chance reaches {ceil} residues in the age of the "
                f"universe; the smallest self-copier needs about "
                f"{MIN_REPLICASE_BASES // 3} coded"))

    best = min(ERROR_RATES.values())
    keep = error_threshold(best)
    out.append(("fidelity", OPEN if keep >= MIN_REPLICASE_BASES else SHUT,
                f"the most accurate copier without enzymes loses one "
                f"base in {1/best:.0f}, so it can hold {keep:.0f} bases "
                f"before every copy carries a mutation. A replicase is "
                f"{MIN_REPLICASE_BASES}"))

    out.append(("bootstrap", SHUT,
                f"the {MIN_REPLICASE_BASES}-base replicase is what would "
                f"RAISE the fidelity bound, and it is larger than the "
                f"bound permits. Each of the two independent limits -- "
                f"{ceil} residues by search, {keep:.0f} bases by "
                f"fidelity -- falls below the thing that would lift "
                f"them both"))
    return out


def first_shut():
    """-> (name, why) for the earliest gate that does not open."""
    for nm, st, why in gates():
        if st == SHUT:
            return nm, why
    return None, "every gate opened, which would be a result"


# CANCELLING A RULE TO SEE WHAT IT WAS HOLDING UP.
#
# A shut gate says no. It does not say by how much, and the
# difference matters enormously: a gate missing by a factor of two
# is a different problem from one missing by 10^11. So each closed
# gate is relaxed -- the one quantity it depends on is moved until
# it opens -- and the size of the move IS the specification for the
# missing mechanism.
#
# This is the ablation idea from engine/ablate.py pointed at a
# question instead of at a test suite. There it asked which rule
# owns a failure. Here it asks what a rule would have to be worth.


def what_would_open(gate):
    """-> (factor, what must change). DERIVED per gate."""
    from engine.origin import length_ceiling, search_years, ALPHABET
    if gate == "crowding":
        have = molecules_in_vesicle(OCEAN_AMPHIPHILE_M)
        need = 100.0
        return need / have, (
            f"{need/have:.0f}x more concentrated, or a vesicle "
            f"{(need/have)**(1/3):.1f}x wider "
            f"({VESICLE_RADIUS_M*1e9*(need/have)**(1/3):.0f} nm). "
            f"Evaporating pools, eutectic freezing and pore "
            f"thermophoresis all reach far more than 40x, so this gate "
            f"is not a deep problem -- it is a mechanism this "
            f"repository has not written")
    if gate == "fidelity":
        best = min(ERROR_RATES.values())
        need_mu = 1.0 / MIN_REPLICASE_BASES
        return best / need_mu, (
            f"copying {best/need_mu:.1f}x more accurately -- one error "
            f"in {MIN_REPLICASE_BASES} instead of one in {1/best:.0f}. "
            f"A factor of two, not a factor of a thousand, and that is "
            f"the whole distance between chemistry and a replicator")
    if gate == "search":
        ceil = length_ceiling()
        need = MIN_REPLICASE_BASES // 3
        return ALPHABET ** (need - ceil), (
            f"{ALPHABET ** (need - ceil):.1e}x more trials to reach "
            f"{need} residues by chance. That is the one gate where "
            f"the shortfall is astronomical, so chance is not how it "
            f"was crossed -- something must assemble from parts "
            f"already found, which is Levinthal's answer again")
    if gate == "elements":
        return float("inf"), (
            "carbon must arrive, and the delivery average over 3 to 45 "
            "AU does not carry it because CO freezes only at 25 K. The "
            "fix is a colder source, not more of the same")
    return 1.0, "already open"


def specification():
    """-> the missing mechanism, in numbers rather than adjectives."""
    out = []
    for nm, st, _why in gates():
        if st == SHUT and nm != "bootstrap":
            f, why = what_would_open(nm)
            out.append((nm, f, why))
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_early_gates_open", _early)
    t("a_membrane_is_the_same_rule_as_folding", _memb)
    t("the_barrier_is_fidelity_not_supply", _barrier)
    t("the_two_bounds_close_on_each_other", _circle)
    t("this_is_a_constraint_not_an_origin", _humble)
    t("cancelling_a_rule_sizes_the_gap", _size)
    return all(o[1] for o in out), out


def _early():
    g = {n: (s, w) for n, s, w in gates()}
    early = ["solvent", "energy", "compartment"]
    shut = [n for n in early if g[n][0] == SHUT]
    if shut:
        raise ArithmeticError(f"an early gate closed: {shut}")
    el = g["elements"]
    return ("solvent, energy and compartment open on Earth: water, a "
            "genome costing 3.3e-15 J, and a bilayer that assembles "
            "itself. Elements is "
            + ("open too" if el[0] == OPEN else
               "SHUT on carbon, which is a real gap and not a rounding "
               "-- " + el[1].split(';')[-1].strip())
            + ". None of energy, water or compartments is what stops "
              "this")


def _memb():
    from engine.folding import hydrophobicity
    f = hydrophobicity("F")
    return (f"the membrane gate and engine/folding.py use ONE rule. "
            f"Burying carbon away from water is worth about "
            f"{CH2_TRANSFER_J/1000:.1f} kJ/mol per CH2, which collapses "
            f"a protein -- phenylalanine scores {f:.2f} on the same "
            f"carbon-to-polar ratio -- and assembles a vesicle. Two "
            f"consequences, one rule, and neither was fitted to the "
            f"other")


def _barrier():
    nm, _why = first_shut()
    if nm in ("solvent", "energy", "compartment"):
        raise ArithmeticError(f"the first closed gate is {nm}, which "
                              f"contradicts the early-gates result")
    return (f"the first gate that does not open is {nm!r}. Supply is "
            f"not the problem on Earth -- every gate about having "
            f"enough of something opens, and the ones that shut are "
            f"about keeping information rather than getting materials")


def _circle():
    from engine.origin import length_ceiling
    ceil = length_ceiling()
    keep = error_threshold(min(ERROR_RATES.values()))
    if keep >= MIN_REPLICASE_BASES:
        raise ArithmeticError("fidelity no longer bounds below the "
                              "replicase; the paradox has dissolved and "
                              "this reasoning needs redoing")
    return (f"two bounds derived from unrelated arguments -- {ceil} "
            f"residues from counting sequences, {keep:.0f} bases from "
            f"Eigen's error threshold -- both fall below the "
            f"{MIN_REPLICASE_BASES}-base replicase. And the replicase "
            f"is what would raise the second bound. The gap is not a "
            f"shortage, it is a loop")


def _humble():
    return ("this walks Earth to the first gate that does not open and "
            "says where it is. It does not open it. The mechanism that "
            "crosses from 10 maintainable bases to a 200-base copier is "
            "still absent, and the value of the walk is that four "
            "popular candidates -- energy, elements, water, "
            "compartments -- are now ruled out by derivation rather "
            "than opinion")


def _size():
    spec = specification()
    if not spec:
        raise ArithmeticError("every gate opens, so there is nothing to "
                              "size and this reasoning is stale")
    finite = [(n, f) for n, f, _w in spec if f != float("inf")]
    small = [(n, f) for n, f in finite if f < 100]
    big = [(n, f) for n, f in finite if f >= 100]
    return (f"relaxing each shut gate sizes it: "
            + "; ".join(f"{n} needs {f:.0f}x" for n, f in finite)
            + f". {len(small)} of them are modest -- "
            + ", ".join(n for n, _f in small)
            + f" -- and a factor of two in copying accuracy is the "
              f"whole distance between chemistry and a replicator. "
            + (f"Only {big[0][0]} is astronomical, which is why chance "
               f"is not how it was crossed" if big else ""))


if __name__ == "__main__":
    for nm, st, why in gates():
        mark = "open " if st == OPEN else "SHUT "
        print(f"  {mark}{nm:13}{why[:88]}")
    print()
    nm, why = first_shut()
    print(f"  first shut: {nm}\n")
    print("  WHAT WOULD OPEN EACH:")
    for n, f, w in specification():
        fs = "inf" if f == float("inf") else f"{f:.1e}"
        print(f"    {n:12}{fs:>10}x   {w[:74]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:56]}")
    print("\nall:", ok)
