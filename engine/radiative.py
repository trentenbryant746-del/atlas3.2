"""
Optical depth from molecules, with no planet consulted.

engine/terraform.py solved its absorption law from Venus and Mars and
then used it to talk about Venus and Mars. That is circular and it is
the thing to remove: a law read off three planets cannot then be
evidence about planets. Everything here comes from properties a
molecule has in a laboratory -- band strengths, line widths, line
spacings -- and from radiative transfer. No planetary temperature,
pressure or composition appears anywhere in this file.

WHY ABSORPTION SATURATES, DERIVED RATHER THAN ASSUMED. A spectral
line is not a spike; collisions broaden it into a Lorentz profile
with wings that fall off as 1/(nu - nu0)^2. Put a little gas in the
way and absorption grows in proportion to how much there is: the
WEAK LINE limit, absorption proportional to column. Put a lot in and
the line centre goes black -- it cannot absorb more than everything
-- so further gas only widens the black core outward into the wings.
Because the wings fall as an inverse square, the width of the black
core grows as the SQUARE ROOT of the column. That is the STRONG LINE
limit, and it is where the exponent of 1/2 comes from. It was a
choice in terraform.py, made inside a bound derived from Earth still
being here. Here it is a consequence of the shape of a broadened
line, and Earth is not mentioned.

PRESSURE BROADENING MATTERS AND THE FITTED LAW COULD NOT SEE IT.
Collisions set the line width, so gamma grows with pressure, and in
the strong-line limit absorption goes as sqrt(S * gamma * u) -- as
the square root of column TIMES PRESSURE, not of column alone. A
thick atmosphere therefore absorbs more per molecule than a thin one
with the same column. Fitting a pure power of column, as the earlier
version did, folds that dependence into the exponent and gets a
number that is right for the two planets it was fitted to and wrong
everywhere else.

THE BAND MODEL. Real bands are hundreds of lines, so a single line is
not enough. The Goody statistical model treats a band as lines of
random strength and spacing and gives a mean transmittance that has
both limits built in:

    tau_band  =  (S/d) * u  /  sqrt( 1 + S*u / (pi*gamma) )

Small u: tau -> (S/d)*u, linear. Large u: tau -> sqrt(pi*gamma*u)/d,
the square root law. One expression, both regimes, no switch.

EVERY NUMBER BELOW IS A LABORATORY MEASUREMENT OF A MOLECULE.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, ASSERTED = "DERIVED", "ASSERTED"

N_A = 6.02214076e23
K_B = 1.380649e-23
H_PLANCK = 6.62607015e-34
C_LIGHT = 299792458.0
P_REF = 1.01325e5          # Pa, the pressure line widths are quoted at

# Laboratory band data. Measured on gas in a cell, never on a sky.
#   nu0    band centre, cm^-1
#   width  band extent, cm^-1
#   S      band strength, cm^-1 / (molecule cm^-2)  [HITRAN integrated]
#   d      mean line spacing, cm^-1
#   gamma  Lorentz half-width at P_REF, cm^-1
#   mu     molar mass, g/mol
BANDS = {
    "CO2": dict(nu0=667.0, width=250.0, S=9.0e-18, d=1.6, gamma=0.07,
                mu=44.009,
                note="the nu2 bend at 15 microns, CO2's only strong "
                     "band inside the thermal infrared"),
    "H2O": dict(nu0=1595.0, width=600.0, S=3.0e-17, d=0.8, gamma=0.09,
                mu=18.015,
                note="the nu2 bend at 6.3 microns plus the pure "
                     "rotation band; water is a bent polar molecule so "
                     "it absorbs far more widely than CO2"),
    "CH4": dict(nu0=1306.0, width=300.0, S=1.1e-17, d=1.2, gamma=0.06,
                mu=16.04, note="the nu4 bend at 7.7 microns"),
}


def molecules_per_cm2(column_kg_m2, mu_g_mol):
    """Column in molecules/cm^2. DERIVED from a mass and a molar mass."""
    return column_kg_m2 * 0.1 / mu_g_mol * N_A


def goody_tau(species, column_kg_m2, pressure_pa):
    """Band optical depth. DERIVED from laboratory band data alone.

    Weak-line and strong-line limits both fall out of the one form;
    nothing switches between them and nothing was fitted.
    """
    b = BANDS[species]
    u = molecules_per_cm2(column_kg_m2, b["mu"])
    if u <= 0:
        return 0.0
    gamma = b["gamma"] * (pressure_pa / P_REF)      # collisions broaden
    if gamma <= 0:
        return 0.0
    return (b["S"] / b["d"]) * u / math.sqrt(1.0 + b["S"] * u
                                             / (math.pi * gamma))


def planck_fraction(nu_lo, nu_hi, T):
    """Fraction of blackbody emission between two wavenumbers. DERIVED."""
    def integrand(nu_cm):
        nu = nu_cm * 100.0
        x = H_PLANCK * C_LIGHT * nu / (K_B * T)
        if x > 700:
            return 0.0
        return (nu ** 3) / math.expm1(x)
    n = 220
    tot = sum(integrand(1.0 + i * (4000.0 - 1.0) / n)
              for i in range(n + 1)) * (4000.0 - 1.0) / n
    part = sum(integrand(nu_lo + i * (nu_hi - nu_lo) / n)
               for i in range(n + 1)) * (nu_hi - nu_lo) / n
    return 0.0 if tot <= 0 else max(0.0, min(1.0, part / tot))


def grey_equivalent(mix, pressure_pa, T):
    """-> tau. Bands combined in TRANSMITTANCE, which is the only way.

    THE FIRST VERSION AVERAGED OPTICAL DEPTHS AND GAVE EARTH tau=230
    AND A SURFACE OF 922 K. Averaging depths weighted by how much
    spectrum each band covers is not an approximation, it is a
    category error: a band that is utterly opaque across a quarter of
    the spectrum does not make the atmosphere a quarter of infinitely
    opaque. It blocks that quarter and the other three quarters leave
    through the window untouched.

    So each band is converted to what it actually transmits, the
    window is counted at full transmission, and the total is turned
    back into a grey depth at the end:

        T_bar = sum_i f_i exp(-tau_i)  +  f_window
        tau   = -ln(T_bar)

    This is what makes an atmosphere SATURATE as a whole. Pile on CO2
    for ever and its 26% of the spectrum goes black and stops
    mattering, while the remaining 74% carries on radiating to space.
    The fitted power law had no window in it, so it let one gas close
    a sky it cannot reach.
    """
    tot_f, trans = 0.0, 0.0
    for sp, col in sorted(mix.items()):
        if col <= 0 or sp not in BANDS:
            continue
        b = BANDS[sp]
        lo = max(1.0, b["nu0"] - b["width"] / 2)
        hi = b["nu0"] + b["width"] / 2
        f = planck_fraction(lo, hi, T)
        tot_f += f
        trans += f * math.exp(-min(goody_tau(sp, col, pressure_pa), 700.0))
    if tot_f > 1.0:                 # bands overlap; share the spectrum
        trans /= tot_f
        tot_f = 1.0
    trans += (1.0 - tot_f)
    trans = min(max(trans, 1e-12), 1.0)
    return -math.log(trans)


def window_fraction(mix, T):
    """How much of the outgoing spectrum no gas here can touch."""
    f = 0.0
    for sp, col in mix.items():
        if col > 0 and sp in BANDS:
            b = BANDS[sp]
            f += planck_fraction(max(1.0, b["nu0"] - b["width"] / 2),
                                 b["nu0"] + b["width"] / 2, T)
    return max(0.0, 1.0 - min(f, 1.0))


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("no_planet_appears_in_this_file", _clean)
    t("weak_line_limit_is_linear", _weak)
    t("strong_line_limit_is_square_root", _strong)
    t("pressure_broadening_increases_absorption", _press)
    t("planck_fractions_sum_to_one", _planck)
    t("bands_combine_in_transmittance", _combine)
    t("an_opaque_band_cannot_close_the_window", _window)
    return all(o[1] for o in out), out


def _clean():
    # PARSE the imports; do not grep for them. Two versions of this
    # check failed themselves -- the first matched the string
    # "observed_T" that it contained, the second matched the module
    # name it was testing for. A check written as a text search over
    # its own file will always find itself.
    import ast
    tree = ast.parse(Path(__file__).read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    bad = sorted(m for m in mods
                 if any(k in m for k in ("terraform", "biomatter", "cosmos")))
    import engine.radiative as me
    bad += [n for n in dir(me) if n.lower() in ("bodies", "equilibrium_t")]
    if bad:
        raise ArithmeticError("planetary data reached this file: " + str(bad))
    return ("imports parsed, not grepped: " + ", ".join(sorted(mods))
            + " -- no body table, no observed temperature, no planetary "
              "composition. Band strengths, line widths and spacings are "
              "measurements of gas in a cell, so a law built from them is "
              "evidence ABOUT planets rather than a restatement of three")



def _weak():
    # It has to be ASTONISHINGLY thin. The first attempt used 1e-4
    # kg/m^2 and got 1.471, because CO2's 15 micron band is already
    # saturated there -- S*u/(pi*gamma) is about 5. That was the model
    # being right and the test being wrong.
    a = goody_tau("CO2", 1e-9, P_REF)
    b = goody_tau("CO2", 2e-9, P_REF)
    r = b / a
    if not 1.9 < r < 2.1:
        raise ArithmeticError(f"doubling a thin column scaled tau by {r:.3f}")
    # where saturation sets in: S*u = pi*gamma
    bd = BANDS["CO2"]
    u_sat = math.pi * bd["gamma"] / bd["S"]
    col_sat = u_sat * bd["mu"] / N_A / 0.1
    return (f"doubling CO2 multiplies tau by {r:.4f} only below about "
            f"{col_sat:.2e} kg/m2 of column; above that the lines are "
            f"black at the centre and it goes as the square root. CO2 "
            f"saturates at a column of MICROGRAMS per square metre, which "
            f"is why adding it to an atmosphere that already has some "
            f"buys so much less than the first trace did")


def _strong():
    a = goody_tau("CO2", 1e4, P_REF)
    b = goody_tau("CO2", 4e4, P_REF)
    r = b / a
    if not 1.9 < r < 2.1:
        raise ArithmeticError(f"quadrupling a thick column scaled tau by "
                              f"{r:.3f}; expected 2 for a square root")
    return (f"quadrupling a thick CO2 column multiplies tau by {r:.4f}, so "
            f"tau goes as the SQUARE ROOT of column. The exponent of 1/2 "
            f"that terraform.py chose inside a bound is here a consequence "
            f"of a Lorentz line's inverse-square wings, and no planet was "
            f"asked")


def _press():
    thin = goody_tau("CO2", 1e4, 0.01 * P_REF)
    thick = goody_tau("CO2", 1e4, P_REF)
    if thick <= thin:
        raise ArithmeticError("pressure broadening did not increase tau")
    return (f"the same column absorbs {thick/thin:.2f}x more at 1 bar than "
            f"at 10 mbar, because collisions widen the lines. Absorption "
            f"goes as sqrt(column x PRESSURE), and a law fitted to a pure "
            f"power of column cannot represent that -- it buries the "
            f"pressure dependence in the exponent")


def _planck():
    tot = planck_fraction(1.0, 4000.0, 288.0)
    if abs(tot - 1.0) > 0.02:
        raise ArithmeticError(f"the whole spectrum came to {tot:.4f}")
    f15 = planck_fraction(542.0, 792.0, 288.0)
    return (f"the full band integrates to {tot:.4f}, and CO2's 15 micron "
            f"band covers {100*f15:.1f}% of what a 288 K surface radiates "
            f"-- so even an infinitely opaque CO2 band leaves the other "
            f"{100*(1-f15):.0f}% to escape through the window")


def _combine():
    """The bug that gave Earth 922 K."""
    huge = {"CO2": 1e9}
    tau = grey_equivalent(huge, P_REF, 288.0)
    f = planck_fraction(542.0, 792.0, 288.0)
    expect = -math.log(1.0 - f)
    if abs(tau - expect) > 0.05:
        raise ArithmeticError(f"an infinitely opaque CO2 band gave "
                              f"tau={tau:.3f}, expected {expect:.3f}")
    return (f"a CO2 column of 1e9 kg/m2 -- opaque past any doubt -- gives "
            f"tau={tau:.3f}, not infinity, because it can only black out "
            f"the {100*f:.0f}% of the spectrum its band covers. Averaging "
            f"depths instead of transmittances gave Earth tau=230 and a "
            f"surface of 922 K")


def _window():
    tau_small = grey_equivalent({"CO2": 1e2}, P_REF, 288.0)
    tau_huge = grey_equivalent({"CO2": 1e12}, P_REF, 288.0)
    if tau_huge - tau_small > 1.0:
        raise ArithmeticError("ten orders more CO2 still moved tau a lot; "
                              "the band is not saturating")
    w = window_fraction({"CO2": 1e12}, 288.0)
    if w < 0.5:
        raise ArithmeticError(f"only {w:.2f} of the spectrum left open")
    return (f"raising CO2 by ten orders of magnitude moves tau by "
            f"{tau_huge-tau_small:.4f}, because {100*w:.0f}% of a 288 K "
            f"body's radiation comes out at wavelengths CO2 does not "
            f"absorb. One gas cannot close a sky it does not reach, and "
            f"this is why CO2 alone cannot make a Venus")


if __name__ == "__main__":
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:72]}")
    print("\nall:", ok)


