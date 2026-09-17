"""
What nobody knows, held on the record so the system can be checked
against it.

A system that derives answers from rules will, if the rules are
wrong or the pattern-matching is loose, eventually produce an answer
to something nobody has solved. That is not a discovery. It is
almost always a bug -- a regex that matched, a rule applied outside
its domain, a number invented to fill a slot.

So the open problems are a FIXTURE, and the expected result is
ABSTENTION. Every entry here must come back refused. If one ever
comes back answered, that is a flag to investigate, and this module
says so rather than celebrating:

    an answer here means one of two things, and the first is far
    more likely: something is broken, or something is interesting

THE SECOND CATEGORY IS THE ONE THAT MATTERS MORE. Alongside the
famous open problems are the things THIS REPO does not derive and
knows it does not derive -- the Kleiber exponent, the Lane-Emden
constant, the fitted dilution factor, the nuclear equation of
state. Those are not unknown to science; they are unknown to us,
and the distinction is worth keeping because they fail differently.
A famous conjecture will never be closed by anything here. An
asserted constant might be, by someone doing the derivation, and
then it should move out of this list.

INTERNAL CONSISTENCY IS THE OTHER HALF. Where the repo's rules
touch an open problem, they must not silently resolve it. The TOV
band is the worked example: engine/remnants.py refuses inside it,
and engine/eos.py narrows it from observations without ever
claiming to have derived the equation of state. That is the shape
every entry here should have -- bounded where data bounds it,
refused where it does not.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# (question, field, why it is open, what would close it)
OPEN_TO_SCIENCE = (
    ("Is the Riemann hypothesis true?", "mathematics",
     "unproven since 1859; the zeros are verified numerically to great "
     "height, which is evidence and not proof",
     "a proof, or a counterexample zero off the critical line"),
    ("Does P equal NP?", "mathematics",
     "no separation and no collapse is known",
     "a proof either way"),
    ("Does the Collatz sequence reach 1 for every positive integer?",
     "mathematics",
     "verified far past 2^68 by computation; no proof of termination",
     "a proof, or a divergent or cyclic starting value"),
    ("Is every even number greater than 2 the sum of two primes?",
     "mathematics", "Goldbach; verified to 4e18, unproven",
     "a proof, or an even number with no such pair"),
    ("Do smooth solutions to the Navier-Stokes equations always exist?",
     "mathematics", "existence and smoothness in three dimensions is open",
     "a proof, or a solution that blows up in finite time"),
    ("What is the equation of state of matter at nuclear density?",
     "physics",
     "not known; it decides the neutron-star maximum mass. This repo "
     "BOUNDS it in engine/eos.py rather than deriving it",
     "heavier confirmed pulsars, tighter tidal deformability"),
    ("How is gravity quantised?", "physics",
     "no tested theory of quantum gravity",
     "an experiment at the Planck scale, which is far out of reach"),
    ("What is dark matter made of?", "physics",
     "inferred gravitationally, never detected directly",
     "a direct detection, or a modified-gravity theory that fits all "
     "the same observations"),
    ("Why is there more matter than antimatter?", "physics",
     "the Standard Model's CP violation is far too small to explain it",
     "a new source of CP violation"),
    ("Does the Kleiber 3/4 exponent follow from anything?", "biology",
     "geometry predicts 2/3 and measurement gives about 3/4; fractal "
     "transport derivations exist and are disputed",
     "a derivation this repo carries out, rather than an assertion"),
)

# The repo's own. Not unknown to science -- unknown to US, and each
# could move out of this list by someone doing the work.
# CLOSED. Kept with the date, because an entry that simply vanishes
# from a list of open problems leaves no evidence it was ever open.
CLOSED_BY_US = (
    ("Lane-Emden n=3 constant",
     "was: engine/remnants.py asserted C = 3.0984 from a table",
     "engine/polytrope.py integrates the Lane-Emden equation to its "
     "first zero and derives omega_3 = 2.01824, giving C = 3.09797 -- "
     "1.4e-04 from the value that was asserted. The Chandrasekhar mass "
     "is now DERIVED rather than DERIVED_FROM_ASSERTED"),
)


OPEN_TO_US = (
    ("Kleiber exponent", "engine/life.py; asserted 0.75, and life.kleiber() carries check=NONE rather than a fake one",
     "a fractal-transport derivation, carried out here"),
    ("cosmos dilution factor", "engine/cosmos.py; FITTED to solar data",
     "more observables -- alpha-element ratios, age-metallicity -- "
     "turning the fit into a prediction or breaking it"),
    ("initial-final mass relation", "engine/remnants.py; asserted anchors",
     "stellar-evolution modelling, which this repo does not do"),
    ("whether the mass formula can see BETA decay",
     "ALPHA IS SETTLED: the Q-value error is 1.21 MeV measured on "
     "differences, against alpha Q-values of 4-5, so alpha decay "
     "resolves. Beta Q-values are 0.02 to 2.3 MeV and straddle the "
     "bar, so chains still cannot branch and Ac, Fr and Pm stay "
     "undetermined",
     "more measured binding energies, particularly beta pairs "
     "(Z, Z+1 at the same A). The alpha bar rests on four pairs in "
     "BINDING_FIXTURE and the beta bar on none at all -- it is "
     "currently inferred from the alpha one"),
    ("nuclear shell closures",
     "engine/nucleo.py is a liquid drop with no shell structure, so "
     "the magic numbers are invisible to it -- provenance.py walks "
     "straight through doubly-magic Pb-208, which really ends the "
     "uranium series",
     "a shell-model correction term, or measured binding energies to "
     "score the liquid drop against"),
    ("the answer format of the held-out benchmark",
     "data/atlas-novel-sat-like.jsonl; SHA-256 only",
     "the publisher releasing the serialisation, so the hashes become "
     "checkable instead of only comparable"),
)


def ask_all(ask_fn=None):
    """Put every open question to the system. All must abstain."""
    if ask_fn is None:
        import atlas
        ask_fn = atlas.ask
    out = []
    for q, field, why, closes in OPEN_TO_SCIENCE:
        a = ask_fn(q)
        answered = bool(a)
        out.append({"question": q, "field": field, "answered": answered,
                    "value": getattr(a, "value", None),
                    "why_open": why, "would_close": closes})
    return out


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("abstains_on_the_unsolved", _abstain)
    t("bounded_where_data_bounds", _bounded)
    t("our_own_gaps_listed", _ours)
    t("closed_stay_closed", _closed)
    return all(o[1] for o in out), out


def _abstain():
    rs = ask_all()
    answered = [r for r in rs if r["answered"]]
    if answered:
        raise ArithmeticError(
            "ANSWERED AN OPEN PROBLEM -- investigate before believing it: "
            + "; ".join(f"{r['question'][:40]}... -> {r['value']}"
                        for r in answered))
    return (f"{len(rs)} open problems, all {len(rs)} refused. An answer "
            f"here would be a bug far more often than a discovery, so "
            f"this failing is a flag to investigate, not a result")


def _bounded():
    """Where data bounds an open problem, the repo must use the bound."""
    from engine import eos, remnants
    lo, hi = eos.band().value
    if not (lo < hi):
        raise ArithmeticError("the EOS band is empty")
    inside = remnants.classify((lo + hi) / 2).value
    if inside != "undetermined":
        raise ArithmeticError(
            f"the midpoint of the open band was resolved to {inside} -- "
            f"the repo silently closed an open problem")
    below = remnants.classify(lo - 0.1).value
    return (f"the one open problem the repo touches is bounded to "
            f"{lo}-{hi} by observation and still refused inside it, while "
            f"{lo - 0.1:.2f} resolves to {below}. Bounded where data "
            f"bounds it, refused where it does not")


def _closed():
    """Anything claimed closed must actually be derived now."""
    from engine import polytrope, remnants
    c = polytrope.chandrasekhar_constant().value
    _v, how = remnants.lane_emden_c()
    if how != "DERIVED":
        raise ArithmeticError("the polytrope constant is still asserted")
    if remnants.chandrasekhar().kind != "DERIVED":
        raise ArithmeticError("the Chandrasekhar mass still inherits an "
                              "assertion")
    return (f"{len(CLOSED_BY_US)} closed: the polytrope constant is "
            f"{c:.5f}, integrated rather than looked up, and the "
            f"Chandrasekhar mass built on it is now DERIVED")


def _ours():
    if len(OPEN_TO_US) < 3:
        raise ArithmeticError("too few of our own gaps recorded to be honest")
    names = ", ".join(n for n, _w, _c in OPEN_TO_US)
    return (f"{len(OPEN_TO_US)} things this repo asserts and does not "
            f"derive, each with what would close it: {names}")


if __name__ == "__main__":
    print("OPEN TO SCIENCE -- every one must come back refused")
    for r in ask_all():
        mark = "ANSWERED <- INVESTIGATE" if r["answered"] else "refused"
        print(f"  {mark:<24}{r['question'][:56]}")
    print("\nOPEN TO US -- asserted here, and what would close it")
    for n, w, c in OPEN_TO_US:
        print(f"  {n:<34}{w}")
        print(f"  {'':<34}closes if: {c}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:26}{d}")
    print("\nall:", ok)
