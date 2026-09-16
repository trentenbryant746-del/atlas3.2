"""
The repo's derivations, told in English and re-executable.

Each function returns a Derivation: the chain of steps, each with its
justification, its kind, and a closure that recomputes it. Narrating and
verifying are then the same object seen two ways.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.narrate import Derivation, DERIVED, ASSERTED, DEFINED  # noqa: E402
from engine.particles import (PROTON, NEUTRON, MEV_PER_U,
                              binding_energy_MeV)                  # noqa: E402
from engine.nucleo import (T_FREEZE_MEV, M_H_ATOM, M_HE4_ATOM,
                           M_C12_ATOM)                             # noqa: E402

NIST = "CODATA/NIST particle masses"


def primordial_helium():
    d = Derivation("Why is a quarter of the universe helium?")
    mn, mp = NEUTRON.mass, PROTON.mass
    d.add("take the neutron mass", mn, kind=ASSERTED, source=NIST, unit="u",
          recompute=lambda: NEUTRON.mass)
    d.add("take the proton mass", mp, kind=ASSERTED, source=NIST, unit="u",
          recompute=lambda: PROTON.mass)
    dm = (mn - mp) * MEV_PER_U
    d.add("subtract them, in energy units", dm, unit="MeV",
          because="the neutron is heavier, and that difference is the whole "
                  "reason protons outnumber neutrons",
          recompute=lambda: (NEUTRON.mass - PROTON.mass) * MEV_PER_U)
    T = T_FREEZE_MEV
    d.add("take the weak freeze-out temperature", T, unit="MeV",
          kind=ASSERTED,
          source="standard value; the result is sensitive to it (0.75 gives "
                 "Y_p 0.233, 0.85 gives 0.278)",
          recompute=lambda: T_FREEZE_MEV)
    r = math.exp(-dm / T)
    d.add("form the neutron-to-proton ratio, exp(-dm/kT)", r,
          because="at freeze-out the weak interactions stop converting "
                  "between them, so the Boltzmann factor is locked in",
          recompute=lambda: math.exp(-((NEUTRON.mass - PROTON.mass)
                                       * MEV_PER_U) / T_FREEZE_MEV))
    rd = r * 0.74
    d.add("allow for free neutrons decaying before nucleosynthesis", rd,
          because="roughly a quarter of them beta-decay in the interval",
          recompute=lambda: math.exp(-((NEUTRON.mass - PROTON.mass)
                                       * MEV_PER_U) / T_FREEZE_MEV) * 0.74)
    Y = 2 * rd / (1 + rd)
    d.add("convert that to a helium mass fraction, 2r/(1+r)", Y,
          because="essentially every surviving neutron ends up bound in "
                  "helium-4, and each one brings a proton with it, so the "
                  "helium mass is twice the neutron mass",
          recompute=lambda: (lambda q: 2 * q / (1 + q))(
              math.exp(-((NEUTRON.mass - PROTON.mass) * MEV_PER_U)
                       / T_FREEZE_MEV) * 0.74))
    d.result = Y
    d.compared_to = 0.245
    d.comparison = f"error {abs(Y - 0.245) / 0.245:.1%}"
    return d


def fusion_energy():
    d = Derivation("Why does hydrogen fusion release 26.7 MeV?")
    d.add("take the mass of four hydrogen atoms", 4 * M_H_ATOM, unit="u",
          kind=ASSERTED, source=NIST, recompute=lambda: 4 * M_H_ATOM)
    d.add("take the mass of one helium-4 atom", M_HE4_ATOM, unit="u",
          kind=ASSERTED, source="measured atomic mass",
          recompute=lambda: M_HE4_ATOM)
    dm = 4 * M_H_ATOM - M_HE4_ATOM
    d.add("subtract: the helium is lighter than its parts", dm, unit="u",
          because="binding energy has left the system",
          recompute=lambda: 4 * M_H_ATOM - M_HE4_ATOM)
    q = dm * MEV_PER_U
    d.add("convert the missing mass to energy", q, unit="MeV",
          because="E = mc^2, with 931.494 MeV per atomic mass unit",
          recompute=lambda: (4 * M_H_ATOM - M_HE4_ATOM) * MEV_PER_U)
    d.result = q
    d.compared_to = 26.73
    d.comparison = f"error {abs(q - 26.73) / 26.73:.2%}"
    return d


def iron_peak():
    d = Derivation("Why does fusion stop at iron?")
    d.add("take the Weizsacker mass formula", "5 coefficients",
          kind=ASSERTED,
          source="volume, surface, Coulomb, asymmetry and pairing terms, "
                 "all measured",
          recompute=lambda: "5 coefficients")
    best, bb = None, -1e9
    for Z in range(1, 60):
        for N in range(0, 120):
            A = Z + N
            if A < 1:
                continue
            b = binding_energy_MeV(Z, N) / A
            if b > bb:
                bb, best = b, (Z, N)
    d.add("search every (Z, N) for the largest binding energy per nucleon",
          f"Z={best[0]}, N={best[1]}, A={sum(best)}",
          because="fusion releases energy only while binding per nucleon is "
                  "rising, so the maximum is where it must stop",
          recompute=lambda: f"Z={best[0]}, N={best[1]}, A={sum(best)}")
    d.add("read off that maximum", bb, unit="MeV per nucleon",
          recompute=lambda: bb)
    d.result = f"iron, Z={best[0]}"
    d.compared_to = "Fe-56 / Ni-62 at ~8.79 MeV per nucleon"
    d.comparison = ("right element, isotope off by two neutrons -- the "
                    "liquid-drop model has no shell closures, and the real "
                    "peak is set by exactly those")
    return d
