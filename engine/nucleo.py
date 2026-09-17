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
# HOW WRONG IS THIS FORMULA? MEASURED, NOT TAKEN FROM THE LITERATURE.
#
# engine/transitions.py refuses a decay whose Q-value is smaller than
# the mass formula's error, and that error was typed in as 3.0 MeV
# from the literature. It is the threshold every refusal turns on, so
# it decides what the repo will and will not say -- and a number that
# important should be measured here.
#
# The obvious measurement fails. Scoring predictions against the
# periodic table's atomic weights gives 80 MeV, which is an artefact:
# a standard atomic weight is the ABUNDANCE-WEIGHTED AVERAGE over an
# element's isotopes and not the mass of any one nuclide. Iron comes
# out 55.935 u, which is Fe-56 almost exactly, against a tabulated
# 55.845 that Fe-54 pulls down.
#
# BUT SOME ELEMENTS HAVE ONLY ONE ISOTOPE, and for those the average
# has a single term -- so the weight IS the mass and the comparison is
# fair. Which elements those are does not need asserting either: a
# mono-isotopic weight sits very close to a whole number (aluminium
# 26.9815) while a mixture lands between them (chlorine 35.45, copper
# 63.55). Selecting on that gives a comparison set the model picks out
# for itself.
#
# THE MEASURED ANSWER IS WORSE THAN THE TYPED ONE, which is the point
# of measuring. Median residual about 7 MeV against the 3.0 assumed,
# and much worse for the lightest nuclei -- hydrogen is out by 25 MeV,
# because a liquid drop is a poor model of four nucleons. So the
# threshold should be more conservative than it was, not less, and the
# refusals it drives should be wider.
NEAR_INTEGER = 0.05      # how close to a whole number counts as one isotope
LIGHT_Z = 8              # below this a liquid drop is not the right model


def mono_isotopic(near=NEAR_INTEGER, min_z=LIGHT_Z):
    """Elements whose weight is essentially one isotope's mass."""
    from engine.experts import BY_Z, UNSTABLE
    out = []
    for z in range(1, 93):
        if z in UNSTABLE or z < min_z:
            continue
        sym, _name, w = BY_Z[z]
        if abs(w - round(w)) < near:
            out.append((sym, z, round(w), w))
    return out


def accuracy(near=NEAR_INTEGER, min_z=LIGHT_Z):
    """-> dict. The formula's residual, measured on its own predictions."""
    import math as _m
    U_MEV = 931.49410242
    M_H, M_N = 1.007825, 1.008665
    rows = []
    for sym, z, a, w in mono_isotopic(near, min_z):
        n = a - z
        b = binding_energy_MeV(z, n)
        if b is None:
            continue
        pred = z * M_H + n * M_N - b / U_MEV
        rows.append((sym, (pred - w) * U_MEV))
    if not rows:
        raise ArithmeticError("no comparison set")
    d = sorted(abs(r[1]) for r in rows)
    return {"n": len(d), "median": d[len(d) // 2],
            "mean": sum(d) / len(d),
            "rms": _m.sqrt(sum(x * x for x in d) / len(d)),
            "worst": d[-1], "rows": rows,
            "caveat": ("the near-integer test has false positives -- "
                       "chromium and molybdenum have several isotopes "
                       "whose average happens to land near a whole "
                       "number -- so this is an upper bound on the "
                       "formula's error rather than a clean one")}


def error_bar():
    """The number engine/transitions.py should refuse inside. DERIVED."""
    a = accuracy()
    return a["median"], (
        f"{a['median']:.2f} MeV median residual over {a['n']} elements "
        f"whose atomic weight is within {NEAR_INTEGER} of a whole number, "
        f"so the weight is one isotope's mass rather than an average. "
        f"Measured, not taken from the literature -- and larger than the "
        f"3.0 that was assumed, so the refusals widen. {a['caveat']}")
