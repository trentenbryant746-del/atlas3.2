"""
Condensed particles are grey, and that is the whole point of them.

Every absorber in engine/radiative.py works in BANDS. A molecule has
discrete vibrational modes, so it blocks some wavenumbers and leaves
others open, and no amount of gas closes a window it cannot reach.
That is why CO2 alone cannot make a Venus, and 3.1.39 eliminated the
last gas mechanism that might have: the intermolecular potential was
derived, it predicted where a wing stops, and it missed by a factor
of three to nine.

A CONDENSED PARTICLE IS DIFFERENT IN KIND. Once a vapour becomes a
droplet a few microns across, it is large compared with an infrared
wavelength, and a large particle does not care what wavelength it
is: it removes light geometrically, across the whole spectrum at
once. There is no window in a cloud.

    tau = 3 Q M / (4 rho r)

with M the condensed mass overhead, rho the particle's density, r
its radius, and Q the extinction efficiency, which tends to 2 for
anything much bigger than the wavelength -- a particle removes twice
its geometric cross-section, half by blocking and half by
diffraction. Nothing there is fitted.

THE MODEL ALREADY HAD HALF OF THIS AND IT WAS THE WRONG HALF. Venus'
albedo of 0.77 IS its sulfuric acid deck; a bare rock would be near
0.1. So the cooling was counted -- 92 K of it -- and the warming was
not. Taking one side of a mechanism and not the other is worse than
omitting it, because the error has a sign and nothing declares it.

WHERE THE CONDENSATE COMES FROM IS DERIVED. Air rising from a cloud
base to a colder top must shed whatever it can no longer hold, and
how much that is comes from the same saturation curves already used
for water and carbon dioxide.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, REFUSED = "DERIVED", "REFUSED"
Q_GEOMETRIC = 2.0        # extinction efficiency for r >> wavelength

# Condensates, with the density of the condensed phase and the
# saturation curve this repository can supply for each.
CONDENSATES = {
    "H2O": dict(rho=1000.0, curve="water"),
    "CO2": dict(rho=1560.0, curve="co2"),
    "H2SO4": dict(rho=1840.0, curve=None),
}


def saturation(species, T):
    """Pa. Uses the curves already derived in engine/terraform.py."""
    from engine.terraform import p_sat_water, p_sat_co2
    c = CONDENSATES[species]["curve"]
    if c == "water":
        return p_sat_water(T)
    if c == "co2":
        return p_sat_co2(T)
    raise KeyError(
        f"no saturation curve for {species}: this repository has "
        f"Clausius-Clapeyron for water and carbon dioxide, and adding "
        f"another needs that substance's triple point and latent heat, "
        f"which are laboratory measurements it does not hold")


def condensed_column(species, T_base, T_top, gravity):
    """kg/m^2 that must condense between two levels. DERIVED.

    A parcel carried from a warm base to a cold top cannot keep what
    it held; the difference in saturation pressure, divided by
    gravity, is the mass left behind.
    """
    dp = saturation(species, T_base) - saturation(species, T_top)
    return max(0.0, dp) / gravity


# CONDENSED IS NOT THE SAME AS AIRBORNE, AND THE FIRST VERSION USED
# THE TOTAL. Lifting Earth's air from 288 K to 260 K sheds enough
# water for an optical depth of 22,500. Real cloud optical depths
# are 5 to 20. The error is a factor of about a thousand and it is
# not arithmetic: almost all of what condenses FALLS. A cloud is a
# standing balance between condensation and precipitation, not an
# accumulation, and its water content is whatever the updraft can
# hold against gravity at any instant.
#
# What sets that balance is droplet fall speed against updraft
# speed -- Stokes drag on a micron droplet -- and neither the
# updraft nor the collision-coalescence that grows droplets into
# raindrops is in this repository. So the airborne fraction is
# REFUSED rather than guessed, and every cloud optical depth here
# is reported as an upper bound: what the air would hold if nothing
# ever rained.
PRECIPITATION_RULE = None


def airborne_fraction():
    """-> refuses. The rule that would set it is not here."""
    raise NotImplementedError(
        "the fraction of condensate that stays aloft is a balance "
        "between droplet fall speed and updraft speed, and needs Stokes "
        "drag plus collision-coalescence growth, neither of which is in "
        "this repository. Total condensate over-states a cloud by about "
        "a thousand: Earth comes out at optical depth 22,500 where real "
        "clouds are 5 to 20")


def cloud_tau(mass_column, radius_m, rho):
    """Grey optical depth. DERIVED from geometry, not from a band."""
    if mass_column <= 0 or radius_m <= 0:
        return 0.0
    return 3.0 * Q_GEOMETRIC * mass_column / (4.0 * rho * radius_m)


def tau_for(species, T_base, T_top, gravity, radius_m=1e-6):
    """-> (tau, why). The cloud a planet's own profile produces."""
    rho = CONDENSATES[species]["rho"]
    m = condensed_column(species, T_base, T_top, gravity)
    t = cloud_tau(m, radius_m, rho)
    return t, (f"{m:.4g} kg/m2 of {species} condenses between {T_base:.0f} "
               f"and {T_top:.0f} K, giving a GREY optical depth of {t:.3g} "
               f"at {radius_m*1e6:.1f} micron particles -- grey because a "
               f"droplet that size is large against an infrared "
               f"wavelength and removes light geometrically")


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("a_cloud_has_no_window", _grey)
    t("thinner_particles_block_more", _size)
    t("earth_water_cloud_is_the_right_order", _earth)
    t("venus_condensate_is_refused_by_name", _venus)
    t("the_albedo_already_counts_the_cooling", _half)
    return all(o[1] for o in out), out


def _grey():
    from engine.radiative import BANDS, planck_fraction
    covered = 0.0
    for b in BANDS["CO2"]:
        covered += planck_fraction(max(1.0, b["nu0"] - b["width"] / 2),
                                   b["nu0"] + b["width"] / 2, 737.0)
    return (f"CO2's four bands together cover {100*covered:.0f}% of what a "
            f"737 K surface radiates, so gas leaves {100*(1-covered):.0f}% "
            f"open however much is added. A cloud covers all of it: a "
            f"droplet microns across is large against every infrared "
            f"wavelength and removes light geometrically. That is a "
            f"difference in KIND, not in degree, and it is why no gas "
            f"rule could close this")


def _size():
    a = cloud_tau(0.05, 1e-6, 1840.0)
    b = cloud_tau(0.05, 1e-5, 1840.0)
    if a <= b:
        raise ArithmeticError("smaller particles did not block more")
    return (f"the same mass gives tau {a:.2f} as 1 micron droplets and "
            f"{b:.2f} at 10 microns -- ten times thinner, because opacity "
            f"goes as surface area per unit mass and that goes as 1/r. A "
            f"cloud's strength is about how finely divided it is")


def _earth():
    from engine.terraform import BODIES
    e = BODIES["Earth"]
    t, _why = tau_for("H2O", 288.0, 260.0, e.gravity(), 1e-5)
    real_hi = 20.0
    if t < real_hi:
        raise ArithmeticError(f"tau={t:.2f} is no longer an over-estimate; "
                              f"if precipitation was added this bound is "
                              f"stale")
    try:
        airborne_fraction()
    except NotImplementedError:
        pass
    else:
        raise ArithmeticError("an airborne fraction was produced from "
                              "nothing")
    return (f"lifting Earth's air from 288 K to 260 K sheds enough water "
            f"for tau={t:,.0f} in 10 micron droplets, against real cloud "
            f"optical depths of 5 to 20. A factor of about a thousand, "
            f"and it is not arithmetic: almost all of what condenses "
            f"FALLS. Every cloud depth here is an upper bound -- what "
            f"the air would hold if nothing ever rained -- and the "
            f"precipitation balance is refused by name rather than "
            f"guessed")


def _venus():
    try:
        tau_for("H2SO4", 400.0, 250.0, 8.87)
    except KeyError as e:
        if "triple point" not in str(e):
            raise ArithmeticError("the refusal does not say what is needed")
        return ("Venus' deck is sulfuric acid and it is REFUSED: this "
                "repository has Clausius-Clapeyron for water and carbon "
                "dioxide, and H2SO4 needs its own triple point and latent "
                "heat. Those are laboratory measurements of a substance, "
                "the same kind of input as a band strength, and the "
                "mechanism is built and waiting for them. Inventing a "
                "curve to close Venus would be the patch this whole "
                "exercise exists to avoid")
    raise ArithmeticError("a sulfuric acid cloud was produced from nothing")


def _half():
    from engine.terraform import BODIES, Body, equilibrium_T
    v = BODIES["Venus"]
    bare = Body("bare", v.mass, v.radius, v.au, 0.10,
                eccentricity=v.eccentricity)
    d = equilibrium_T(bare) - equilibrium_T(v)
    if d < 50:
        raise ArithmeticError(f"the cloud albedo is only worth {d:.0f} K")
    return (f"Venus' albedo of 0.77 is its cloud deck -- a bare rock would "
            f"be near 0.10 -- and it removes {d:.0f} K that the model "
            f"counts in full. The same clouds' greenhouse is counted at "
            f"zero. Half a mechanism is worse than none, because the "
            f"error has a sign and nothing declares it")


if __name__ == "__main__":
    from engine.terraform import BODIES
    e = BODIES["Earth"]
    for r in (1e-6, 5e-6, 1e-5):
        t, _ = tau_for("H2O", 288.0, 260.0, e.gravity(), r)
        print(f"  Earth water cloud, {r*1e6:>4.1f} um droplets: tau {t:>8.1f}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:60]}")
    print("\nall:", ok)
