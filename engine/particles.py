"""
Particles, conserved quantities, and deriving the table instead of storing it.

Dimensions were one type system. Conservation laws are another, independent
of it: charge, baryon number and lepton number are additive quantum numbers
that must balance across any binding. Adding them does not replace
dimensional typing, it intersects with it, and every extra conserved
quantity prunes further.

    particle      Q     B     L    mass (u)
    proton      +1    +1     0    1.007276
    neutron      0    +1     0    1.008665
    electron    -1     0    +1    0.000549

THE COMPRESSION CLAIM. A neutral atom is any bound state with Q = 0, and
its element is decided by its proton count alone. So the periodic table's
118 rows of (Z -> symbol) are not 118 facts about the world; they are one
binding rule plus 118 NAMES. The masses are genuinely empirical and stay
empirical. The STRUCTURE is derivable, and that difference is measurable:
predict each element's mass from its particle content and compare against
the tabulated value.

WHERE THIS STOPS. An element is a proton count. A compound is a fixed-ratio
binding with a formula. A MIXTURE -- silver ore, dirt -- is neither: no
fixed ratio, no formula, no binding rule. Dirt is not a compositional object
and no set of rules will make it one. The ladder is particles -> atoms ->
compounds, and it ends there.
"""
from __future__ import annotations

from dataclasses import dataclass

U = 1.0  # atomic mass units


from fractions import Fraction as Fr


@dataclass(frozen=True)
class Particle:
    name: str
    Q: int          # electric charge
    B: int          # baryon number
    L: int          # lepton number
    mass: float     # in u
    S: int = 0      # strangeness
    I3: Fr = Fr(0)  # third component of isospin
    spin: Fr = Fr(1, 2)

    @property
    def is_hadron(self):
        """made of quarks: a baryon (B != 0) or a meson (B = 0 but strange
        or isospin-carrying). Leptons are neither."""
        return self.B != 0 or self.S != 0

    def gell_mann_nishijima(self):
        """Q = I3 + (B+S)/2 -- for HADRONS. The relation describes quark
        content, so it says nothing about leptons and applying it to the
        electron reported a violation that was my error, not the data's.
        Returns None where the relation does not apply."""
        if not self.is_hadron:
            return None
        return self.Q == self.I3 + Fr(self.B + self.S, 2)


PROTON   = Particle("proton",   +1, +1, 0, 1.0072764666, 0, Fr(1, 2), Fr(1, 2))
NEUTRON  = Particle("neutron",    0, +1, 0, 1.0086649159, 0, Fr(-1, 2), Fr(1, 2))
ELECTRON = Particle("electron",  -1,  0, 1, 0.00054857991, 0, Fr(0), Fr(1, 2))
# strangeness is inert unless something carries it, so the basis grows
LAMBDA   = Particle("lambda0",    0, +1, 0, 1.1974,        -1, Fr(0), Fr(1, 2))
SIGMA_P  = Particle("sigma+",    +1, +1, 0, 1.2767,        -1, Fr(1), Fr(1, 2))
SIGMA_M  = Particle("sigma-",    -1, +1, 0, 1.2880,        -1, Fr(-1), Fr(1, 2))
XI_M     = Particle("xi-",       -1, +1, 0, 1.4166,        -2, Fr(-1, 2), Fr(1, 2))
KAON_P   = Particle("kaon+",     +1,  0, 0, 0.5302,        +1, Fr(1, 2), Fr(0))

BASIS = (PROTON, NEUTRON, ELECTRON)
HADRONS = (PROTON, NEUTRON, LAMBDA, SIGMA_P, SIGMA_M, XI_M, KAON_P)
ALL_PARTICLES = (PROTON, NEUTRON, ELECTRON, LAMBDA, SIGMA_P, SIGMA_M,
                 XI_M, KAON_P)


def bound_state(counts):
    """counts: {Particle: n} -> conserved totals.

    Q, B, L, S and I3 are ADDITIVE and simply sum. SPIN IS NOT -- angular
    momenta add as vectors, so a two-fermion state can be spin 0 or spin 1
    and the total is not determined by the parts. What IS determined is the
    STATISTICS: an odd number of fermions is a fermion, an even number is a
    boson. Reporting a summed spin would be wrong, so this reports the one
    thing that follows.
    """
    Q = sum(p.Q * n for p, n in counts.items())
    B = sum(p.B * n for p, n in counts.items())
    L = sum(p.L * n for p, n in counts.items())
    S = sum(p.S * n for p, n in counts.items())
    I3 = sum(p.I3 * n for p, n in counts.items())
    m = sum(p.mass * n for p, n in counts.items())
    nfermi = sum(n for p, n in counts.items() if p.spin.denominator == 2)
    return {"Q": Q, "B": B, "L": L, "S": S, "I3": I3, "mass_u": m,
            "statistics": "fermion" if nfermi % 2 else "boson"}


def is_neutral_atom(counts):
    """the binding rule: charge balances, and there is at least one baryon"""
    s = bound_state(counts)
    return s["Q"] == 0 and s["B"] >= 1


def atom(Z, N):
    """Z protons, N neutrons, Z electrons -- neutral by construction"""
    return {PROTON: Z, NEUTRON: N, ELECTRON: Z}


def predicted_mass(Z, N, binding_MeV_per_A=None):
    """sum of constituents. Without binding energy this is an OVERESTIMATE,
    and saying so is the point: the gap IS the nuclear binding energy."""
    return bound_state(atom(Z, N))["mass_u"]


# semi-empirical mass formula (Weizsacker) -- coefficients are MEASURED
A_V, A_S, A_C, A_A, A_P = 15.75, 17.8, 0.711, 23.7, 11.18       # MeV
MEV_PER_U = 931.494


def binding_energy_MeV(Z, N):
    A = Z + N
    if A <= 0:
        return 0.0
    term = (A_V * A
            - A_S * A ** (2 / 3)
            - A_C * Z * (Z - 1) / A ** (1 / 3)
            - A_A * (A - 2 * Z) ** 2 / A)
    if Z % 2 == 0 and N % 2 == 0:
        term += A_P / A ** 0.5
    elif Z % 2 == 1 and N % 2 == 1:
        term -= A_P / A ** 0.5
    return term


def mass_with_binding(Z, N):
    return predicted_mass(Z, N) - binding_energy_MeV(Z, N) / MEV_PER_U
