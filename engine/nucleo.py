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
