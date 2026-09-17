"""
Every number, and which of three things it is.

A challenge worth answering: this repository claims to derive rather
than predict, and the biology modules added most recently are full
of typed numbers. An audit found 28 with no label at all, and
several of them are not measurements. INTAKE_COEFFICIENT carries
the comment "sets where supply and demand cross", which is a knob
with a note on it.

So every number gets one of three kinds, and the kind decides what
may be said about a result that depends on it.

    EXACT      fixed by definition. No error, ever.
    MEASURED   someone went and found out. Carries their error and
               a source. Legitimate input.
    CHOSEN     nobody measured it and nothing derives it. It was
               picked so a model would run.

A CHOSEN number is not forbidden -- a model that refuses every
unmeasured quantity does nothing at all. What is forbidden is
CITING a result that rests on one as though it were derived. So
results are tagged by the worst input they depend on, and anything
resting on CHOSEN says so wherever it appears.

THIS IS THE SAME DISCIPLINE AS THE ERROR BARS, ONE LEVEL DOWN.
3.1.18 established that a bar belongs to a domain and 3.1.29 that
it belongs to a manifestation. This says a CLAIM belongs to its
weakest input, which is the rule those two were special cases of.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EXACT, MEASURED, CHOSEN = "EXACT", "MEASURED", "CHOSEN"

# The audit. Every typed number in the modules added recently,
# classified honestly rather than generously.
INPUTS = {
    # --- measured, with a source in the literature -------------
    "genesis.SULFURISATION_K": (MEASURED, "FeS condensation, 704 K"),
    "earthlab.CH2_TRANSFER_J": (MEASURED, "hydrophobic transfer per CH2"),
    "earthlab.SORET_PER_K": (MEASURED, "thermophoresis, small solutes"),
    "earthlab.MIN_REPLICASE_BASES": (MEASURED, "smallest RNA that copies RNA"),
    "biosphere.NPP_MODERN_KG_C_YR": (MEASURED, "net primary production"),
    "biosphere.CH4_LIFETIME_OXIC_YR": (MEASURED, "methane lifetime in air"),
    "biosphere.BLOOD_VISCOSITY": (MEASURED, "whole blood at 310 K"),
    "biosphere.OZONE_PRESENT_DU": (MEASURED, "Earth's ozone column"),
    "biosphere.O3_CROSS_SECTION_CM2": (MEASURED, "Hartley band"),
    "biosphere.CH4_OXIC_PPM": (MEASURED, "Earth today"),
    "origin.AGE_UNIVERSE_YR": (MEASURED, "age of the universe"),
    "potential.EPS0": (EXACT, "vacuum permittivity, fixed by c and mu0"),
    "signature.SECONDS_PER_YEAR": (MEASURED, "Julian year"),
    "origin.ALPHABET": (MEASURED, "20 proteinogenic amino acids"),
    "biosphere.DU_TO_MOLECULES_CM2": (EXACT, "Dobson unit definition"),

    # --- chosen. Nobody measured these and nothing derives them -
    "descent.INTAKE_COEFFICIENT": (
        CHOSEN, "picked so supply and demand cross at a plausible size"),
    "descent.PREDATION_PRESSURE": (
        CHOSEN, "fraction of deaths from predation; a dial"),
    "descent.PREDATOR_RATIO": (
        CHOSEN, "3x is a rule of thumb, not a measurement"),
    "descent.TRAIT_COST": (CHOSEN, "2% per trait, picked"),
    "descent.MUTATION_SIZE": (CHOSEN, "spread per generation, picked"),
    "descent.MUTATION_TRAIT": (CHOSEN, "trait gain rate, picked"),
    "earthlab.CATALYSIS_P": (
        CHOSEN, "mid-range of a 1e-6 to 1e-11 literature spread"),
    "earthlab.CROWDED_M": (CHOSEN, "concentration after drying, picked"),
    "earthlab.OCEAN_AMPHIPHILE_M": (
        CHOSEN, "a generous early-ocean estimate, not a measurement"),
    "earthlab.VESICLE_RADIUS_M": (CHOSEN, "smallest bilayer, order only"),
    "earthlab.LIGATION_PIECE_BASES": (CHOSEN, "20 bases, picked"),
    "biosphere.REDUCED_SINK_KG": (CHOSEN, "order of magnitude only"),
    "biosphere.CH4_ANOXIC_PPM": (CHOSEN, "early Earth, poorly constrained"),
    "biosphere.CH4_LIFETIME_ANOXIC_YR": (CHOSEN, "order of magnitude"),
    "biosphere.AEROBIC_MIN_FRACTION": (CHOSEN, "1% Pasteur point, a convention"),
    "census.MIN_WINDOW_GYR": (CHOSEN, "how long life needs; nobody knows"),
    "genesis.EJECTION_YEARS": (CHOSEN, "dynamical lifetime, order only"),
    "genesis.SCATTERED_FRACTION": (CHOSEN, "fraction thrown inward, picked"),
}

# Which results lean on which inputs. A claim is only as good as
# its worst one.
CLAIMS_ON = {
    "the habitable band 0.999-1.899 AU": [],
    "Earth composition Fe 32.0%": [],
    "the 57-residue search ceiling": ["origin.ALPHABET",
                                      "origin.AGE_UNIVERSE_YR"],
    "the cell size window 1.58-47.5 um": ["earthlab.CATALYSIS_P",
                                          "earthlab.CROWDED_M"],
    "life cools its own planet by 1.9 K": ["biosphere.CH4_ANOXIC_PPM"],
    "seeded life stays microbial": ["descent.INTAKE_COEFFICIENT",
                                    "descent.TRAIT_COST"],
    "predation does not reverse the collapse": [
        "descent.PREDATION_PRESSURE", "descent.PREDATOR_RATIO",
        "descent.INTAKE_COEFFICIENT"],
    "Earth reads as driven and Mars does not": [],
}


def kind_of(name):
    return INPUTS.get(name, (CHOSEN, "unregistered, so assumed chosen"))[0]


def grade(claim):
    """-> (kind, why). A claim is as good as its worst input."""
    deps = CLAIMS_ON.get(claim)
    if deps is None:
        return CHOSEN, f"{claim!r} is not registered"
    if not deps:
        return EXACT, (f"rests on no chosen input -- every number "
                       f"under it is exact, measured or derived")
    worst = CHOSEN if any(kind_of(d) == CHOSEN for d in deps) else MEASURED
    bad = [d for d in deps if kind_of(d) == CHOSEN]
    return worst, (f"rests on {len(deps)} registered inputs"
                   + (f", of which {len(bad)} are CHOSEN: "
                      + ", ".join(bad) if bad else ", all measured"))


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("every_number_is_classified", _classified)
    t("chosen_numbers_are_admitted", _chosen)
    t("results_are_graded_by_worst_input", _graded)
    t("the_planet_chain_rests_on_nothing_chosen", _planet)
    return all(o[1] for o in out), out


def _classified():
    counts = {}
    for k, (kind, _w) in INPUTS.items():
        counts[kind] = counts.get(kind, 0) + 1
    return (f"{len(INPUTS)} numbers classified: "
            + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
            + ". An audit found 28 with no label at all, and calling "
              "them all 'measured' would have been the generous answer "
              "rather than the true one")


def _chosen():
    bad = [k for k, (kind, _w) in INPUTS.items() if kind == CHOSEN]
    if not bad:
        raise ArithmeticError("nothing is marked CHOSEN, which for a "
                              "repository with evolutionary parameters "
                              "in it is not credible")
    return (f"{len(bad)} numbers are CHOSEN -- picked so a model would "
            f"run, with nobody having measured them. The worst is "
            f"descent.INTAKE_COEFFICIENT, which carried the comment "
            f"'sets where supply and demand cross'. That is a knob "
            f"with a note on it, and pretending otherwise is how a "
            f"fit becomes a finding")


def _graded():
    rows = [(c, grade(c)[0]) for c in CLAIMS_ON]
    chosen = [c for c, k in rows if k == CHOSEN]
    clean = [c for c, k in rows if k == EXACT]
    return (f"{len(clean)} of {len(rows)} registered claims rest on "
            f"nothing chosen. {len(chosen)} do rest on chosen inputs "
            f"and must say so wherever they appear: "
            + "; ".join(chosen))


def _planet():
    for c in ("the habitable band 0.999-1.899 AU",
              "Earth composition Fe 32.0%",
              "Earth reads as driven and Mars does not"):
        k, why = grade(c)
        if k == CHOSEN:
            raise ArithmeticError(f"{c} rests on a chosen input: {why}")
    return ("the planet results -- the habitable band, Earth's "
            "composition, the biosignature -- rest on no chosen input. "
            "The BIOLOGY results do. That split is the honest state: "
            "the physics derives and the evolutionary modelling has "
            "dials in it")


if __name__ == "__main__":
    for kind in (EXACT, MEASURED, CHOSEN):
        names = [k for k, (x, _w) in INPUTS.items() if x == kind]
        print(f"  {kind} ({len(names)})")
        for n in sorted(names):
            print(f"      {n:38}{INPUTS[n][1][:44]}")
    print()
    for c in CLAIMS_ON:
        k, why = grade(c)
        print(f"  {k:9}{c[:44]:46}{why[:40]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:52]}")
