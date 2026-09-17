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
# THE RULE, GIVEN RATHER THAN THE ANSWER.
#
#   1  kinetic theory       viscosity = (1/3) rho vbar lambda
#   2  Stokes               drag balances weight -> terminal velocity
#   3  residence            a droplet lives cloud-depth / fall-speed
#   4  standing balance     what is aloft is what condenses in one
#                           residence time, not what has ever condensed
#
# Nothing in that is a measurement of a cloud. The viscosity comes
# out 1.21e-5 Pa s against a measured 1.81e-5 -- simple kinetic
# theory, 33% low, which is what it is worth -- and the chain then
# brings Earth from an optical depth of 22,500 to about 8. The
# factor of a thousand was precipitation, exactly as the refusal
# said.
def air_viscosity(T, P=1.01325e5, diameter=3.7e-10, mu_amu=29.0):
    """Pa s. DERIVED from kinetic theory, not looked up."""
    from engine.constants import K_B, U_KG
    n = P / (K_B * T)
    lam = 1.0 / (math.sqrt(2) * math.pi * diameter * diameter * n)
    m = mu_amu * U_KG
    vbar = math.sqrt(8 * K_B * T / (math.pi * m))
    return (1.0 / 3.0) * n * m * vbar * lam


def terminal_velocity(radius_m, rho_drop, gravity, T, P=1.01325e5):
    """m/s. DERIVED: Stokes drag against weight."""
    return (2.0 * rho_drop * gravity * radius_m * radius_m
            / (9.0 * air_viscosity(T, P)))


def condensation_gradient(species, T, gravity, lapse=6.5e-3,
                          P=1.01325e5):
    """d(mixing ratio)/dz. DERIVED from the species' OWN curve.

    This was a hardcoded 2e-6, which is water's value, and passing
    it to sulfuric acid silently gave H2SO4 water's condensation
    behaviour -- the refusal vanished and Venus appeared to work. A
    shared default is how one substance's properties leak into
    another.
    """
    dT = 0.1
    ps_hi = saturation(species, T)
    ps_lo = saturation(species, T - dT)
    dps_dT = (ps_hi - ps_lo) / dT
    from engine.radiative import MU, _molar
    mu = MU.get(species) or _molar(species)
    eps = mu / 28.96
    return max(0.0, eps * dps_dT / P * lapse)


def standing_water_path(species, radius_m, rho_drop, gravity, T,
                        updraft=1.0, depth=3000.0, P=1.01325e5):
    """kg/m^2 aloft at any instant. DERIVED from the balance.

    A cloud is not an accumulation. It holds whatever condenses
    during the time a droplet takes to fall out of it, and no more.
    """
    from engine.constants import K_B, U_KG
    rho_air = P * 29.0 * U_KG / (K_B * T)
    dq_dz = condensation_gradient(species, T, gravity, P=P)
    vt = terminal_velocity(radius_m, rho_drop, gravity, T, P)
    if vt <= 0:
        return 0.0
    return rho_air * updraft * dq_dz * (depth / vt)


def airborne_fraction(species, T_base, T_top, gravity, radius_m,
                      **kw):
    """-> what fraction of the condensate is actually up there."""
    rho = CONDENSATES[species]["rho"]
    total = condensed_column(species, T_base, T_top, gravity)
    aloft = standing_water_path(species, radius_m, rho, gravity,
                                T_base, **kw)
    return min(1.0, aloft / total) if total > 0 else 0.0


def cloud_tau(mass_column, radius_m, rho):
    """Grey optical depth. DERIVED from geometry, not from a band."""
    if mass_column <= 0 or radius_m <= 0:
        return 0.0
    return 3.0 * Q_GEOMETRIC * mass_column / (4.0 * rho * radius_m)


def tau_for(species, T_base, T_top, gravity, radius_m=1e-6,
            standing=True):
    """-> (tau, why). The cloud a planet's own profile produces."""
    rho = CONDENSATES[species]["rho"]
    if standing:
        m = standing_water_path(species, radius_m, rho, gravity, T_base)
    else:
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
    if False:
        raise ArithmeticError(f"tau={t:.2f} is no longer an over-estimate; "
                              f"if precipitation was added this bound is "
                              f"stale")
    bound, _ = tau_for("H2O", 288.0, 260.0, e.gravity(), 2e-5,
                       standing=False)
    t20, _ = tau_for("H2O", 288.0, 260.0, e.gravity(), 2e-5)
    eta = air_viscosity(288.0)
    if not 1.0 < t20 < 40.0:
        raise ArithmeticError(f"the standing balance gives tau={t20:.1f}")
    return (f"kinetic theory gives air a viscosity of {eta:.2e} Pa s "
            f"against a measured 1.81e-05, Stokes then gives a 20 micron "
            f"droplet a fall speed, and the standing balance gives "
            f"tau={t20:.1f} where total condensate gave {bound:,.0f}. "
            f"Real Earth clouds are 5 to 20. The missing factor of a "
            f"thousand WAS precipitation, and the rule recovered it "
            f"without any cloud being measured")


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
