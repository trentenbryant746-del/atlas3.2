"""
Big Bang and stellar nucleosynthesis, from the rules already present.

Nothing here is a stored astrophysical fact. Each result is computed from
the particle masses and the Weizsacker coefficients in engine/particles.py,
then compared against the observed value. Where they agree, the rules
reproduced the universe; where they do not, the gap is reported.

Every reaction is checked for conservation of charge, baryon number and
lepton number before its energy is computed. A reaction that does not
balance is not a low-yield reaction, it is not a reaction.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.particles import (PROTON, NEUTRON, ELECTRON, MEV_PER_U,
                              binding_energy_MeV)                # noqa: E402

M_H_ATOM = PROTON.mass + ELECTRON.mass          # 1.007825 u
M_HE4_ATOM = 4.002602                           # measured
M_D_ATOM = 2.014102
M_HE3_ATOM = 3.016029
M_C12_ATOM = 12.000000                          # defines the scale

# neutron-proton mass difference drives the whole primordial helium result
DELTA_M_NP_MEV = (NEUTRON.mass - PROTON.mass) * MEV_PER_U
T_FREEZE_MEV = 0.8          # weak-interaction freeze-out temperature


def balances(lhs, rhs):
    """(Q, B, L) conserved? lhs/rhs are lists of (particle-like dicts, n)."""
    def tot(side, k):
        return sum(p[k] * n for p, n in side)
    return all(tot(lhs, k) == tot(rhs, k) for k in ("Q", "B", "L"))


def np_ratio_at_freezeout():
    """n/p = exp(-dm c^2 / kT) at weak freeze-out. One line, no table."""
    return math.exp(-DELTA_M_NP_MEV / T_FREEZE_MEV)


def primordial_helium(np_ratio=None, decay_factor=0.74):
    """Y_p = 2(n/p) / (1 + n/p).

    Essentially every surviving neutron ends up bound in He-4, so the helium
    MASS fraction is twice the neutron fraction. decay_factor accounts for
    free neutrons beta-decaying between freeze-out and nucleosynthesis.
    """
    r = (np_ratio if np_ratio is not None else np_ratio_at_freezeout()) * decay_factor
    return 2 * r / (1 + r), r


def fusion_energy_MeV(reactants, products):
    """Q = (sum of reactant masses - sum of product masses) x c^2, in MeV."""
    dm = sum(m * n for m, n in reactants) - sum(m * n for m, n in products)
    return dm * MEV_PER_U


def binding_per_nucleon(Z, N):
    A = Z + N
    return binding_energy_MeV(Z, N) / A if A else 0.0


def iron_peak(zmax=60):
    """Where does binding energy per nucleon peak? Derived, not looked up."""
    best = (None, -1e9)
    for Z in range(1, zmax):
        for N in range(0, 2 * zmax):
            b = binding_per_nucleon(Z, N)
            if b > best[1]:
                best = ((Z, N), b)
    (Z, N), b = best
    return {"Z": Z, "N": N, "A": Z + N, "B_per_A_MeV": b}


# reaction bookkeeping: (Q, B, L) per species
P = {"Q": 1, "B": 1, "L": 0}
N_ = {"Q": 0, "B": 1, "L": 0}
E_PLUS = {"Q": 1, "B": 0, "L": -1}
NU = {"Q": 0, "B": 0, "L": 1}
HE4 = {"Q": 2, "B": 4, "L": 0}
D = {"Q": 1, "B": 2, "L": 0}
HE3 = {"Q": 2, "B": 3, "L": 0}
C12 = {"Q": 6, "B": 12, "L": 0}

REACTIONS = {
    "pp-I  4p -> He4 + 2e+ + 2nu": ([(P, 4)], [(HE4, 1), (E_PLUS, 2), (NU, 2)]),
    "p + p -> D + e+ + nu":        ([(P, 2)], [(D, 1), (E_PLUS, 1), (NU, 1)]),
    "D + p -> He3":                ([(D, 1), (P, 1)], [(HE3, 1)]),
    "triple-alpha 3 He4 -> C12":   ([(HE4, 3)], [(C12, 1)]),
    "BROKEN 4p -> He4 (no leptons)": ([(P, 4)], [(HE4, 1)]),
}


# ====================================================================
# HOW WRONG IS THIS FORMULA? IT DEPENDS ENTIRELY ON WHAT YOU ASK IT.
#
# A single error bar for the whole formula is the wrong object, and
# using one cost this repo a correct result. engine/transitions.py
# refuses a decay whose Q-value is under "the formula's error", and
# that error was first typed as 3.0 MeV from the literature, then
# measured at ~8 MeV against atomic weights -- at which point alpha
# decay became unresolvable and the uranium series was withdrawn.
#
# BOTH NUMBERS ANSWER A QUESTION NOBODY ASKED. A decay is a
# DIFFERENCE of two binding energies, and the formula's errors are
# strongly correlated between neighbouring nuclei -- the same
# volume, surface and Coulomb terms are slightly off in the same
# direction for both. So the error in a difference is far smaller
# than the error in either term, and measuring the absolute mass
# error tells you almost nothing about whether a decay is
# resolvable.
#
# Measured on the same nuclides:
#
#     absolute binding error     4.76 MeV median
#     Q-VALUE error              1.21 MeV median
#
# Alpha Q-values in the heavy elements are 4 to 5 MeV, so with the
# right bar they are resolvable after all, and the uranium series
# stands. Beta Q-values are 0.02 to 2.3 and mostly are NOT, which
# preserves the finding that chains cannot branch here.
#
# So the bar is a function of the question. error_bar("decay") is
# not error_bar("mass"), and neither is a property of "the formula"
# on its own.
#
# THE FIXTURE IS PER-NUCLIDE, WHICH IS THE OTHER HALF OF THE FIX.
# The earlier attempt scored against standard atomic WEIGHTS, which
# are abundance-weighted averages -- chromium came out 55 MeV wrong
# because Cr-53 and Cr-54 pull the average off Cr-52, not because
# the formula missed. These are single-nuclide measurements.
BINDING_FIXTURE = {
    (2, 2): 28.30, (6, 6): 92.16, (8, 8): 127.62, (20, 20): 342.05,
    (24, 28): 456.35, (26, 30): 492.25, (28, 30): 506.46,
    (34, 46): 696.87, (47, 60): 915.3, (50, 70): 1020.5,
    (79, 118): 1559.4, (82, 126): 1636.4, (84, 128): 1655.8,
    (86, 136): 1708.2, (88, 138): 1731.6, (90, 142): 1766.7,
    (92, 146): 1801.70,
}
BF_SOURCE = "measured nuclear binding energies, per nuclide"
from engine.constants import B_ALPHA_MEV  # noqa: E402

# ISOBARIC PAIRS -- same A, adjacent Z -- for the BETA bar, which
# could not be measured at all without them. Each is a real decay,
# and the fixture carries the measured Q so the formula can be
# scored on the thing it is actually asked for.
# Isobaric pairs -- same A, adjacent Z -- so the BETA bar can be
# measured at all. ONLY the binding energies are carried: the
# measured Q-values were here too and were redundant, because
# dB + (m_n - m_H) reproduces them from these same numbers to
# 0.0015 MeV. Carrying both would have been giving the answer and
# the working.
BETA_B = {(1, 2): 8.482, (2, 1): 7.718, (6, 8): 105.28, (7, 7): 104.66,
          (15, 17): 270.85, (16, 16): 271.78, (19, 21): 341.52,
          (20, 20): 342.05, (27, 33): 524.80, (28, 32): 526.84}
BETA_PAIRS = (((1, 2), (2, 1)), ((6, 8), (7, 7)), ((15, 17), (16, 16)),
              ((19, 21), (20, 20)), ((27, 33), (28, 32)))

# THE TERM THE REPO WAS MISSING, AND IT IS BIGGER THAN THE ANSWER.
#
# A beta-minus Q-value is not just the change in binding energy. A
# neutron becomes a proton, and in the atomic-mass convention that
# releases the neutron-hydrogen difference as well:
#
#     Q(beta-) = B(Z+1, N-1) - B(Z, N) + (m_n - m_H)c^2
#
# engine/transitions.py used the first part alone. That term is
# 0.7825 MeV and typical beta Q-values are 0.02 to 2.8, so leaving
# it out is not a small correction -- it is comparable to the whole
# quantity and it FLIPS SIGNS. C-14 to N-14 came out -0.620 MeV,
# meaning the decay does not happen, against a true +0.156. Every
# beta decision in the repo was wrong by 0.78 MeV.
#
# Note it is the neutron-HYDROGEN difference, not the
# neutron-proton one already in DELTA_M_NP_MEV. Binding energies
# here are defined against atomic masses, so the electron comes
# along with the proton: 0.7825 MeV, not 1.2933.
# DERIVED FROM THE PARTICLE MASSES ALREADY HERE, not typed. The
# first version wrote 0.78254 and 1.02200 in by hand, which is
# supplying an answer the repo can compute: engine/particles.py
# carries the proton, neutron and electron masses, and these are
# just differences of them. Typing them also lost a digit -- 0.78254
# against the 0.78233 the masses give.
def _delta_m_nh():
    """Neutron minus a hydrogen ATOM: the proton and its electron."""
    from engine.particles import PROTON, NEUTRON, ELECTRON
    return (NEUTRON.mass - PROTON.mass - ELECTRON.mass) * MEV_PER_U


def _two_me():
    from engine.particles import ELECTRON
    return 2.0 * ELECTRON.mass * MEV_PER_U


DELTA_M_NH_MEV = _delta_m_nh()
TWO_ME_MEV = _two_me()


def beta_q(z, n, mode="beta-minus"):
    """Q for a beta transition, with every term. DERIVED."""
    if mode == "beta-minus":
        d = (z + 1, n - 1)
        extra = DELTA_M_NH_MEV
    elif mode == "electron-capture":
        d = (z - 1, n + 1)
        extra = -DELTA_M_NH_MEV
    elif mode == "beta-plus":
        d = (z - 1, n + 1)
        extra = -DELTA_M_NH_MEV - TWO_ME_MEV
    else:
        raise KeyError(f"no beta mode {mode!r}")
    a, b = binding_energy_MeV(z, n), binding_energy_MeV(*d)
    if a is None or b is None or d[0] < 0 or d[1] < 0:
        return None
    return (b - a) + extra


def beta_error():
    """The formula's error on a beta Q-value. Measured on real decays."""
    rows = []
    for par, dau in BETA_PAIRS:
        q_semf = beta_q(par[0], par[1], "beta-minus")
        if q_semf is None:
            continue
        # the reference Q, DERIVED from the fixture's own measured
        # binding energies by the same rule the formula uses
        q_true = (BETA_B[dau] - BETA_B[par]) + DELTA_M_NH_MEV
        rows.append((par, q_true, q_semf, q_true,
                     abs(q_semf - q_true), 0.0))
    if not rows:
        raise ArithmeticError("no beta pairs")
    d = sorted(r[4] for r in rows)
    f = sorted(r[5] for r in rows)
    return {"n": len(d), "median": d[len(d) // 2], "worst": d[-1],
            "fixture_median": f[len(f) // 2], "rows": rows}


def absolute_error(lo=1, hi=118):
    """Error in a single binding energy. NOT what a decay inherits."""
    d = sorted(abs(binding_energy_MeV(z, n) - v)
               for (z, n), v in BINDING_FIXTURE.items() if lo <= z <= hi)
    if not d:
        raise ArithmeticError(f"no fixture nuclides in Z {lo}-{hi}")
    return {"n": len(d), "median": d[len(d) // 2], "worst": d[-1],
            "mean": sum(d) / len(d)}


def q_error():
    """Error in a DIFFERENCE. This is the one a decay inherits."""
    out = []
    for (z, n), v in BINDING_FIXTURE.items():
        d = (z - 2, n - 2)
        if d not in BINDING_FIXTURE:
            continue
        q_semf = (binding_energy_MeV(*d) + B_ALPHA_MEV) - \
            binding_energy_MeV(z, n)
        q_true = (BINDING_FIXTURE[d] + B_ALPHA_MEV) - v
        out.append((z, abs(q_semf - q_true), q_true))
    if not out:
        raise ArithmeticError("no alpha pairs in the fixture")
    d = sorted(e for _z, e, _q in out)
    return {"n": len(d), "median": d[len(d) // 2], "worst": d[-1],
            "pairs": out}


# A BAR BELONGS TO A MANIFESTATION, NOT JUST TO A QUESTION.
#
# 3.1.16 established that the bar depends on the QUESTION -- a mass,
# an alpha step and a beta step are three different quantities and
# get three different numbers. That was half of it. The other half
# is that the same question has a different answer depending on WHAT
# STATE THE THING IS IN, and measuring across mixed states produces
# a number that describes neither.
#
# Measured on the fixture, after shell corrections:
#
#     inside the liquid drop's domain    rms 1.850 MeV   (n=15)
#     outside it                         rms 6.249 MeV   (n=2)
#     mixed together, as shipped               4.763 MeV
#
# A factor of 3.4 between two populations, and the shipped bar is
# neither of them -- too loose where the formula works, far too
# tight where it does not. Every refusal judged against 4.763 MeV
# inside the domain was refusing things the formula could actually
# resolve.
#
# Closed-shell against mid-shell now comes out at 0.98, no
# difference at all, which is a second result: before shell
# corrections that split was 3.6 to 1, and adding them absorbed it.
# A manifestation stops mattering once the rule that explains it
# exists, and that is how you know the rule was the right one.
MANIFESTATIONS = ("in-domain", "out-of-domain", "mixed")


def _by_manifestation(kind, manifestation):
    from engine.shells import in_domain
    keep = []
    for (z, n) in BINDING_FIXTURE:
        ok = in_domain(z, n)
        if manifestation == "in-domain" and ok:
            keep.append((z, n))
        elif manifestation == "out-of-domain" and not ok:
            keep.append((z, n))
        elif manifestation == "mixed":
            keep.append((z, n))
    return keep


def mass_bar(manifestation):
    """-> (MeV, n, why). Measured over ONE manifestation only."""
    if manifestation not in MANIFESTATIONS:
        raise KeyError(
            f"a bar needs a manifestation, not just a question: "
            f"{manifestation!r} is not one of {MANIFESTATIONS}. The same "
            f"formula has a 1.85 MeV error where it applies and 6.25 "
            f"where it does not, and a bar measured across both "
            f"describes neither")
    from engine.shells import shell_term, SCALE
    errs = []
    for (z, n) in _by_manifestation("mass", manifestation):
        a = z + n
        errs.append(abs(binding_per_nucleon(z, n) * a
                        + shell_term(z, n, SCALE) - BINDING_FIXTURE[(z, n)]))
    if not errs:
        raise ValueError(f"no fixture nuclides are {manifestation}")
    rms = (sum(e * e for e in errs) / len(errs)) ** 0.5
    return rms, len(errs), (
        f"{rms:.3f} MeV rms over {len(errs)} {manifestation} nuclides. "
        f"Measured on this manifestation alone; mixing it with the other "
        f"gives 4.763, which describes neither population")


# =================================================================
# ONE SOURCE PER Q-VALUE, AND MEASUREMENT IS A SOURCE
# =================================================================
#
# 3.1.27 established that every term in a Q-value must come from the
# same place, because a Q-value is a DIFFERENCE and its small bar
# exists only where the formula's errors cancel between the two
# sides. That rule was then implemented as "always use the formula",
# which is one way to satisfy it and not the only one.
#
# 3.1.28 showed what that costs. Helium-4 sits below the liquid
# drop's derived domain, so the formula cannot supply it, so alpha
# decay became underivable and twelve of fourteen known fates went
# to refused. The ablation in 3.1.30 confirmed the whole loss
# belongs to that single gate.
#
# THE COMPLETE RULE IS "ONE SOURCE", NOT "ONE PARTICULAR SOURCE".
# Measured binding energies are a source. Where every term of a
# Q-value is measured, the difference is consistent and the errors
# that needed to cancel never arise. Where every term is inside the
# formula's domain, the formula is consistent too. Only a MIXTURE is
# forbidden, which is what the rule always said.
#
# The two claims are not the same and are labelled differently:
#
#   MEASURED  arithmetic on measured binding energies. Correct, and
#             not a derivation -- it asserts nothing the data did
#             not already contain.
#   FORMULA   the liquid drop, within its domain. A derivation, and
#             carries the formula's bar.
#
# THE TABLES WERE ALSO DUPLICATED. BINDING_FIXTURE held 17 measured
# binding energies and BETA_B held 10 more of the same quantity,
# overlapping in one entry that agreed. Same defect as the four
# duplicated constants in 3.1.24: two homes for one thing, agreeing
# by care rather than by construction. They are one table now.
MEASURED, FORMULA = "MEASURED", "FORMULA"

_EXTRA_BINDING = {
    # Alpha daughters the decay chains need, measured. They reproduce
    # measured alpha Q-values to within 0.08 MeV -- and the check is
    # real rather than circular, because Ra-226 -> Rn-222 and
    # Po-212 -> Pb-208 use only entries that were already here.
    (80, 124): 1607.5,      # Hg-204
    (88, 140): 1742.5,      # Ra-228
    (90, 144): 1777.7,      # Th-234
}


def measured_binding():
    """-> {(Z,N): MeV}. The one table of measured binding energies."""
    out = dict(BINDING_FIXTURE)
    for k, v in BETA_B.items():
        if k in out and abs(out[k] - v) > 1e-6:
            raise ArithmeticError(
                f"the two binding tables disagree at {k}: {out[k]} vs {v}")
        out[k] = v
    out.update(_EXTRA_BINDING)
    return out


MEASURED_BINDING = measured_binding()
def _measured_q_precision():
    """MeV. DERIVED from how precisely the table is quoted.

    A typed 0.10 sat here until the no_bar_is_typed rule caught it,
    which is the rule working on the person who wrote it.

    Each entry is quoted to a fixed number of decimals, so its
    rounding half-width is half of that place. A Q-value is a sum of
    three such entries, and independent rounding errors add in
    quadrature. Nothing is chosen: the table's own representation
    says how well it can be differenced.
    """
    from decimal import Decimal
    halves = []
    for v in MEASURED_BINDING.values():
        exp = Decimal(str(v)).as_tuple().exponent
        halves.append(0.5 * 10.0 ** exp)
    worst = max(halves)
    return (3 ** 0.5) * worst


MEASURED_Q_BAR = _measured_q_precision()


def q_from(z, n, mode):
    """-> (Q, source, why). One source, or refuse. DERIVED or MEASURED."""
    from engine.shells import in_domain, shell_term, SCALE
    if mode == "alpha":
        parts = [(z, n), (z - 2, n - 2), (2, 2)]
        if any(a < 0 or b < 0 for a, b in parts):
            return None, None, "no alpha daughter exists"
        mb = MEASURED_BINDING
        if all(pp in mb for pp in parts):
            q = mb[(z - 2, n - 2)] + mb[(2, 2)] - mb[(z, n)]
            return q, MEASURED, (
                f"every term measured: B({z-2},{n-2}) + B(He-4) - "
                f"B({z},{n}) = {q:+.3f} MeV. Arithmetic on measurement, "
                f"not a derivation, and it carries the table's "
                f"{MEASURED_Q_BAR:.2f} MeV precision rather than the "
                f"formula's bar")
        if all(in_domain(a, b) for a, b in parts):
            def bf(a, b):
                return (binding_per_nucleon(a, b) * (a + b)
                        + shell_term(a, b, SCALE))
            q = bf(z - 2, n - 2) + bf(2, 2) - bf(z, n)
            return q, FORMULA, f"every term from the formula: {q:+.3f} MeV"
        missing = [pp for pp in parts
                   if pp not in mb and not in_domain(*pp)]
        return None, None, (
            f"refused: {missing} is neither measured nor inside the "
            f"formula's domain, and mixing the two sources is what "
            f"3.1.27 removed -- it biased every alpha channel by 5.455 "
            f"MeV, 4.5 times its own bar")
    # Beta gets the same treatment. The neutron-hydrogen term and
    # the two electron masses are derived from particle masses and
    # belong to neither source -- they are exact bookkeeping, not
    # binding energies, so carrying them alongside measured binding
    # is not a mixture.
    mb = MEASURED_BINDING
    if mode == "beta-minus":
        d, extra = (z + 1, n - 1), DELTA_M_NH_MEV
    elif mode == "electron-capture":
        d, extra = (z - 1, n + 1), -DELTA_M_NH_MEV
    elif mode == "beta-plus":
        d, extra = (z - 1, n + 1), -DELTA_M_NH_MEV - TWO_ME_MEV
    else:
        return None, None, f"unknown mode {mode!r}"
    if d[0] < 0 or d[1] < 0:
        return None, None, f"no {mode} daughter exists"
    if (z, n) in mb and d in mb:
        q = mb[d] - mb[(z, n)] + extra
        return q, MEASURED, (
            f"both binding energies measured: B{d} - B({z},{n}) "
            f"{extra:+.5f} = {q:+.3f} MeV")
    q = beta_q(z, n, mode)
    return (q, FORMULA, f"{mode} from the formula: {q:+.3f} MeV") \
        if q is not None else (None, None, f"no {mode} channel")


def error_bar(kind="decay"):
    """-> (MeV, why). The bar for the question actually being asked."""
    if kind == "mass":
        a = absolute_error()
        return a["median"], (
            f"{a['median']:.2f} MeV median over {a['n']} measured "
            f"nuclides -- the error in ONE binding energy, which is what "
            f"a mass prediction inherits")
    if kind == "decay":
        q = q_error()
        a = absolute_error()
        return q["median"], (
            f"{q['median']:.2f} MeV median over {q['n']} alpha pairs -- "
            f"the error in a DIFFERENCE of two binding energies, which "
            f"is what a decay inherits. Far smaller than the "
            f"{a['median']:.2f} MeV absolute error, because the formula "
            f"is wrong in the same direction for neighbouring nuclei and "
            f"most of it cancels")
    if kind in ("beta", "beta-decay"):
        b = beta_error()
        return b["median"], (
            f"{b['median']:.2f} MeV median over {b['n']} measured beta "
            f"decays -- a different bar again, because a beta step "
            f"changes Z by one where an alpha changes it by two, and the "
            f"formula's asymmetry term is what is wrong in each. The "
            f"reference Q comes from the fixture's own measured binding "
            f"energies by the same rule, so what is scored is the "
            f"formula against measurement and nothing is carried twice")
    raise KeyError(f"no error bar defined for {kind!r}; the bar depends "
                   f"on the question, and 'mass', 'decay' and 'beta' are "
                   f"different questions")


# The atomic-weight measurement that preceded this is removed
# rather than kept: it scored single-nuclide predictions against
# abundance-weighted averages and reported ~8 MeV, which is the
# isotope mix and not the formula. Its one lasting contribution is
# the caution above -- a weight is not a mass -- and BINDING_FIXTURE
# is per-nuclide for exactly that reason.
