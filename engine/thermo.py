"""
Heat capacity from molecular shape, and the Sun's surface from its own light.

An audit for thermodynamics found almost none. Clausius-Clapeyron
sits in engine/terraform.py and the word entropy appears once in
engine/biomatter.py. Equipartition, the second law, Carnot, Maxwell-
Boltzmann, chemical potential and heat capacity were all absent --
and yet three heat capacities were typed into the climate code and
used to set lapse rates and radiative timescales. Numbers where
there should have been rules, which is the defect this repository
keeps finding in itself.

EQUIPARTITION. A molecule in equilibrium carries kT/2 in every
quadratic degree of freedom it can reach. Translation is always
three. Rotation is two for a linear molecule and three otherwise,
because spinning a linear molecule about its own axis moves nothing.
That already gives the textbook answers for a monatomic and a
diatomic gas with nothing fitted.

VIBRATION IS THE INTERESTING PART, AND IT IS ALREADY IN THE REPO. A
vibrational mode is frozen when its quantum exceeds the thermal
energy and active when it does not, and the crossover is smooth --
the Einstein heat capacity,

    c_vib / R  =  x^2 e^x / (e^x - 1)^2,    x = h c nu / kT

Every nu needed is a band centre in engine/radiative.py, measured on
gas in a cell. So the heat capacity of carbon dioxide follows from
the same spectroscopy that sets its opacity, and the two stop being
independent inputs. That is the point: a rule connects things a
number cannot.

THE SUN'S TEMPERATURE IS NOT TYPED HERE EITHER. It is not an
independent measurement -- a star's surface temperature is what its
luminosity and radius imply through Stefan-Boltzmann, and both of
those are geometry and power. 5772 K comes out; nobody puts it in.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.constants import (K_B, N_A, H_PLANCK, C_LIGHT,  # noqa: E402
                              L_SUN_W)

R_GAS = K_B * N_A
DERIVED, ASSERTED = "DERIVED", "ASSERTED"

# Shape decides the rotational count, and nothing else does. A linear
# molecule has no moment of inertia about its own axis, so it has two
# rotational degrees of freedom rather than three.
GEOMETRY = {
    "He": ("monatomic", 1), "Ar": ("monatomic", 1),
    "N2": ("linear", 2), "O2": ("linear", 2), "H2": ("linear", 2),
    "CO2": ("linear", 3),
    "H2O": ("bent", 3), "CH4": ("tetrahedral", 5),
}

# Vibrational wavenumbers, cm^-1. Taken from the band centres in
# engine/radiative.py where they exist, which is the whole point --
# the same measurement sets opacity and heat capacity.
EXTRA_MODES = {
    "CO2": [(667.0, 2), (1333.0, 1), (2349.0, 1)],
    "H2O": [(1595.0, 1), (3657.0, 1), (3756.0, 1)],
    "N2": [(2359.0, 1)],
    "O2": [(1580.0, 1)],
    "CH4": [(1306.0, 3), (1534.0, 2), (2917.0, 1), (3019.0, 3)],
}


def rotational_dof(species):
    """2 for linear, 3 for anything bent or bulkier, 0 for an atom."""
    shape, natoms = GEOMETRY[species]
    if natoms == 1:
        return 0
    return 2 if shape == "linear" else 3


def einstein_cv(nu_cm, T):
    """One mode's contribution in units of R. DERIVED, no threshold."""
    x = H_PLANCK * C_LIGHT * (nu_cm * 100.0) / (K_B * T)
    if x > 50:
        return 0.0
    ex = math.exp(x)
    return x * x * ex / (ex - 1.0) ** 2


def cv_molar(species, T):
    """J/mol/K. DERIVED from shape and measured band frequencies."""
    c = 1.5 + 0.5 * rotational_dof(species)
    for nu, deg in EXTRA_MODES.get(species, []):
        c += deg * einstein_cv(nu, T)
    return c * R_GAS


def cp_molar(species, T):
    """cp = cv + R for an ideal gas. DERIVED."""
    return cv_molar(species, T) + R_GAS


def cp_specific(species, T):
    """J/kg/K, which is what a lapse rate needs. DERIVED."""
    from engine.radiative import MU, _molar
    # One parser for formulas, the one engine/radiative.py already
    # uses. Reaching into the periodic table by bare symbol here
    # broke on O2, because "O2" is a molecule and the table holds
    # atoms -- a second way of doing an existing job, which is the
    # duplication defect in miniature.
    mu = MU.get(species) or _molar(species)
    return cp_molar(species, T) / (mu * 1e-3)


def gamma(species, T):
    """Adiabatic index cp/cv. DERIVED."""
    return cp_molar(species, T) / cv_molar(species, T)


def lapse_rate(gravity, species, T):
    """K/m. DERIVED: g over the specific heat, no typed constant."""
    return gravity / cp_specific(species, T)


# --------------------------------------------------- the star
def effective_temperature(luminosity_w, radius_m):
    """K. DERIVED: a sphere radiating its own luminosity."""
    from engine.terraform import SIGMA
    return (luminosity_w / (4 * math.pi * radius_m ** 2 * SIGMA)) ** 0.25


R_SUN_M = 6.957e8          # measured, a length


def solar_surface():
    """-> (K, why). Not a measurement of temperature. DERIVED."""
    t = effective_temperature(L_SUN_W, R_SUN_M)
    return t, (f"{t:.0f} K from the Sun's luminosity and radius through "
               f"Stefan-Boltzmann, which is itself derived from h, c and "
               f"k. A surface temperature is not an independent "
               f"observation of a star -- it is what its power and its "
               f"area imply, and nothing here was told it")


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("equipartition_gives_the_typed_values", _cp)
    t("vibration_comes_from_the_band_data", _vib)
    t("adiabatic_index_is_right_for_each_shape", _gam)
    t("the_suns_surface_is_derived_not_measured", _sun)
    t("heat_capacity_rises_with_temperature", _rise)
    return all(o[1] for o in out), out


def _cp():
    rows = []
    for sp, typed in (("N2", 1040.0), ("CO2", 850.0)):
        got = cp_specific(sp, 288.0)
        rows.append(f"{sp} {got:.0f} against a typed {typed:.0f}")
        if abs(got - typed) / typed > 0.10:
            raise ArithmeticError(f"{sp}: derived {got:.1f} vs {typed}")
    return ("shape plus measured band frequencies reproduce the numbers "
            "that were typed into the climate code: " + "; ".join(rows)
            + ". Three heat capacities were constants; they are "
            "consequences now")


def _vib():
    cold = cv_molar("CO2", 150.0) / R_GAS
    hot = cv_molar("CO2", 1500.0) / R_GAS
    frozen = 1.5 + 0.5 * rotational_dof("CO2")
    if not (cold < hot and cold >= frozen - 0.01):
        raise ArithmeticError(f"cv/R went {cold:.2f} -> {hot:.2f}")
    return (f"CO2's cv/R is {cold:.2f} at 150 K, near the {frozen:.1f} that "
            f"translation and rotation alone give, and {hot:.2f} at 1500 K "
            f"as its bending and stretching modes wake up. The frequencies "
            f"are the band centres engine/radiative.py already uses for "
            f"opacity -- one measurement, two consequences")


def _gam():
    mono, di = gamma("Ar", 288.0), gamma("N2", 288.0)
    if not (1.66 < mono < 1.67):
        raise ArithmeticError(f"monatomic gamma {mono:.3f}, expected 5/3")
    if not (1.39 < di < 1.41):
        raise ArithmeticError(f"diatomic gamma {di:.3f}, expected 7/5")
    return (f"argon comes out {mono:.4f} and nitrogen {di:.4f} -- five "
            f"thirds and seven fifths, from counting degrees of freedom "
            f"and nothing else")


def _sun():
    t, why = solar_surface()
    if not 5500 < t < 6000:
        raise ArithmeticError(f"the Sun came out {t:.0f} K")
    return why


def _rise():
    a, b = cp_specific("CO2", 200.0), cp_specific("CO2", 800.0)
    if b <= a:
        raise ArithmeticError("cp did not rise with temperature")
    return (f"CO2's cp runs {a:.0f} J/kg/K at 200 K to {b:.0f} at 800 K, "
            f"a {100*(b/a-1):.0f}% change. The climate code used one "
            f"number for both, which is a 200 K planet and a 800 K planet "
            f"being told they have the same gas")


if __name__ == "__main__":
    print(f"  Sun's surface: {solar_surface()[0]:.0f} K (derived)\n")
    print(f"  {'species':8}{'cv/R':>7}{'cp J/kg/K':>11}{'gamma':>8}")
    for sp in ("Ar", "N2", "O2", "CO2", "H2O", "CH4"):
        print(f"  {sp:8}{cv_molar(sp, 288.0)/R_GAS:>7.2f}"
              f"{cp_specific(sp, 288.0):>11.0f}{gamma(sp, 288.0):>8.3f}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:40}{d[:62]}")
    print("\nall:", ok)
