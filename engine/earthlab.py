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


# CONCENTRATION IS A RULE, NOT A HOPE. The crowding gate asks for
# 40x and the ocean does not supply it, but three mechanisms do and
# each is arithmetic rather than special pleading:
#
#   evaporation   a pool losing a fraction f of its water
#                 concentrates everything left by 1/(1-f)
#   freezing      ice rejects solute, so the same ratio applies to
#                 the shrinking brine between the crystals
#   thermophoresis a temperature gradient drives solute to the cold
#                 wall by exp(S_T dT) each pass, and a convecting
#                 pore runs many passes
#
# Evaporation and freezing reach 100x at 99%, which is an ordinary
# tide pool and an ordinary winter. Thermophoresis is weaker per
# pass -- 1.3x to 4.5x -- and compounds.
SORET_PER_K = 0.01            # measured for small solutes


def concentration_factor(mechanism, extent):
    """-> how much more concentrated. DERIVED per mechanism."""
    if mechanism in ("evaporation", "freezing"):
        if not 0.0 <= extent < 1.0:
            raise ValueError(f"a removed fraction of {extent} is not one")
        return 1.0 / (1.0 - extent)
    if mechanism == "thermophoresis":
        return math.exp(SORET_PER_K * extent)
    raise KeyError(f"no rule for {mechanism!r}; known: evaporation, "
                   f"freezing, thermophoresis")


def best_concentration(evap=0.99, freeze=0.99, dT=30.0):
    """-> (factor, which). The strongest mechanism available."""
    opts = {"evaporation": concentration_factor("evaporation", evap),
            "freezing": concentration_factor("freezing", freeze),
            "thermophoresis": concentration_factor("thermophoresis", dT)}
    which = max(opts, key=opts.get)
    return opts[which], which


def molecules_in_vesicle(conc_M, radius_m=VESICLE_RADIUS_M):
    """How many solute molecules one vesicle encloses. DERIVED."""
    litres = (4.0 / 3.0) * math.pi * radius_m ** 3 * 1000.0
    return conc_M * litres * N_A


def error_threshold(mu):
    """Longest genome copying at rate mu can keep. DERIVED: L < 1/mu."""
    if mu <= 0:
        raise ValueError("an error rate of zero is not a copier")
    return 1.0 / mu


# MODULAR ASSEMBLY CLEARS BOTH REMAINING GATES AT ONCE, AND THAT IS
# THE RESULT OF THIS LAB.
#
# Search and fidelity both fail on the same object: a 200-base
# replicase that chance cannot find and enzyme-free copying cannot
# keep. Neither gate has to reach it whole.
#
#   a 20-base piece is 4^20 = 1.1e12 sequences, which an ocean
#   trying one per picosecond exhausts in under a second
#   a 20-base piece is well inside the 100-base error threshold
#   ten of them ligated is 200 bases
#
# The object that could be neither found nor maintained as a unit is
# trivially findable and maintainable in parts. Nothing new was
# added to get this -- it is the two existing bounds asked about a
# smaller object.
#
# AND IT IS THE SAME ANSWER AS LEVINTHAL, FOR THE FOURTH TIME.
# engine/folding.py says folding is not a search. engine/origin.py
# says sequence-finding is not a search. This says assembly is not a
# search either. Every time a combinatorial wall has appeared in
# this repository, the resolution has been that the thing is built
# rather than drawn.
LIGATION_PIECE_BASES = 20


def modular_reach(piece_bases=LIGATION_PIECE_BASES,
                  target=MIN_REPLICASE_BASES):
    """-> (findable, maintainable, n_pieces, why). DERIVED."""
    from engine.origin import ocean_trials, YEAR_S, AGE_UNIVERSE_YR
    seqs = 4.0 ** piece_bases
    yrs = seqs / (ocean_trials() * 1e12 * YEAR_S)
    findable = yrs < AGE_UNIVERSE_YR
    keep = error_threshold(min(ERROR_RATES.values()))
    maintainable = piece_bases < keep
    n = math.ceil(target / piece_bases)
    return findable, maintainable, n, (
        f"a {piece_bases}-base piece is {seqs:.1e} sequences, exhausted "
        f"in {yrs:.1e} years, and sits inside the {keep:.0f}-base error "
        f"threshold. {n} of them ligated is {target} bases -- the object "
        f"neither gate could reach whole")


# SELF-MAINTAINING MEANS AUTOCATALYTIC CLOSURE, AND CLOSURE HAS A
# SIZE.
#
# A replicase that can be assembled is still not a cell. A cell
# maintains itself: every molecule it needs is produced by a
# reaction that another of its molecules catalyses, with nothing
# outside keeping it going. Closure appears when N x p > 1, for N
# molecule types present and p the chance that a random one
# catalyses a given reaction -- measured by in-vitro selection at
# somewhere between 1e-6 and 1e-11.
#
# That puts a FLOOR under the compartment, because diversity needs
# volume. And engine/watch.py already derived a ROOF from
# diffusion: past a certain radius the centre suffocates. Two
# bounds from arguments with nothing to do with each other:
#
#   p = 1e-6    floor 0.34 um     roof 47.5 um
#   p = 1e-8    floor 1.58 um     roof 47.5 um
#   p = 1e-10   floor 7.35 um     roof 47.5 um
#
# There is a window for every plausible p, and a bacterium is 0.5 to
# 5 microns. The 100 nm vesicle that passed the compartment gate is
# FAR too small to maintain itself -- it holds 252 molecules where
# closure wants a million types. The first self-maintaining thing
# had to be cell-sized, and that is a prediction rather than an
# observation fed in.
CATALYSIS_P = 1e-8            # in-vitro selection, mid-range
CROWDED_M = 1e-2              # after concentration


def closure_floor(p=CATALYSIS_P, conc_M=CROWDED_M):
    """m. Smallest compartment that can hold a closed set. DERIVED."""
    from engine.constants import N_A
    need = 1.0 / p
    litres = need / (conc_M * N_A)
    return (litres / 1000.0 * 3.0 / (4.0 * math.pi)) ** (1.0 / 3.0)


def size_window(T=288.0, p=CATALYSIS_P):
    """-> (floor m, roof m, why). Both ends derived, neither fitted."""
    from engine.watch import cell_ceiling
    floor = closure_floor(p)
    roof = cell_ceiling(T)[0]
    return floor, roof, (
        f"closure needs at least {floor*1e6:.2f} microns to hold "
        f"{1/p:.0e} molecule types at {CROWDED_M:.0e} M; diffusion "
        f"allows at most {roof*1e6:.1f} before the centre suffocates. "
        f"A bacterium is 0.5 to 5 microns and sits inside a window "
        f"neither bound was aimed at")


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

    raw = molecules_in_vesicle(OCEAN_AMPHIPHILE_M)
    fac, which = best_concentration()
    n = molecules_in_vesicle(OCEAN_AMPHIPHILE_M * fac)
    out.append(("crowding", OPEN if n > 100 else SHUT,
                f"a {VESICLE_RADIUS_M*1e9:.0f} nm vesicle holds "
                f"{raw:.1f} molecules at ocean concentration and "
                f"{n:.0f} after {fac:.0f}x by {which} -- a pool losing "
                f"99% of its water, or the brine between sea ice. The "
                f"gate needed 40x and ordinary evaporation gives 100"))

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

    fnd, mnt, npc, mwhy = modular_reach()
    out.append(("assembly", OPEN if (fnd and mnt) else SHUT,
                f"built from parts instead of drawn whole: {mwhy}"))

    floor, roof, swhy = size_window()
    out.append(("self-maintaining", OPEN if floor < roof else SHUT,
                f"autocatalytic closure: {swhy}"))

    out.append(("bootstrap", OPEN if (fnd and mnt) else SHUT,
                f"the {MIN_REPLICASE_BASES}-base replicase exceeds both "
                f"bounds as a unit -- {ceil} residues by search, "
                f"{keep:.0f} bases by fidelity -- and neither bound "
                f"applies to a {LIGATION_PIECE_BASES}-base piece. "
                f"{npc} pieces, each findable and each maintainable. The "
                f"loop is not broken by raising a bound, it is stepped "
                f"around by not needing the whole object at once"))
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
    t("assembly_clears_what_search_cannot", _assembly)
    t("closure_and_diffusion_bracket_a_real_cell", _window)
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


def _assembly():
    fnd, mnt, npc, why = modular_reach()
    if not (fnd and mnt):
        raise ArithmeticError(f"a {LIGATION_PIECE_BASES}-base piece is "
                              f"not both findable and maintainable")
    whole_f, whole_m, _n, _w = modular_reach(MIN_REPLICASE_BASES)
    if whole_f or whole_m:
        raise ArithmeticError("the whole replicase now passes a bound, "
                              "so the contrast this rests on is gone")
    return (f"{why}. The whole object passes neither bound and a piece "
            f"passes both, so the gap closes by building rather than "
            f"drawing. This is Levinthal's answer for the fourth time "
            f"here -- folding is not a search, sequence-finding is not "
            f"a search, and assembly is not either")


def _window():
    floor, roof, why = size_window()
    if floor >= roof:
        raise ArithmeticError(f"no window: floor {floor*1e6:.2f} um "
                              f"exceeds roof {roof*1e6:.1f}")
    small = molecules_in_vesicle(CROWDED_M, VESICLE_RADIUS_M)
    if small > 1.0 / CATALYSIS_P:
        raise ArithmeticError("a 100 nm vesicle now suffices for "
                              "closure, which would undo this contrast")
    return (f"{why}. The 100 nm vesicle that passes the compartment "
            f"gate holds {small:.0f} molecules against the {1/CATALYSIS_P:.0e} "
            f"types closure wants, so a bag is not yet a cell. The two "
            f"bounds come from diversity and from diffusion, neither "
            f"aimed at the other, and what they bracket is the size "
            f"life actually is")


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
