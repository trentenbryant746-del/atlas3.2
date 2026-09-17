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

from engine.constants import N_A, K_B, H_PLANCK, C_LIGHT  # noqa: E402
P_REF = 1.01325e5          # Pa, the pressure line widths are quoted at

# Laboratory band data. Measured on gas in a cell, never on a sky.
#   nu0    band centre, cm^-1
#   width  band extent, cm^-1
#   S      band strength, cm^-1 / (molecule cm^-2)  [HITRAN integrated]
#   d      mean line spacing, cm^-1
#   gamma  Lorentz half-width at P_REF, cm^-1
#   mu     molar mass, g/mol
# A MOLECULE HAS MORE THAN ONE BAND, AND THE FIRST TABLE HAD ONE.
# That omission was found by the lab rather than by inspection: the
# layer-3 ceiling did not clear when the continuum was added, and
# tracing why pointed at a LOWER rung. A 737 K body radiates 60% of
# its energy between 1500 and 4000 cm^-1, and CO2's nu3 asymmetric
# stretch at 2349 cm^-1 -- its strongest band by an order of
# magnitude -- sits right there and was absent. Listing one band per
# molecule is not a simplification, it is a wrong molecule.
BANDS = {
    "CO2": [
        dict(nu0=667.0, width=250.0, S=9.0e-18, d=1.6, gamma=0.07,
             note="nu2 bend, 15 microns -- sits on the Planck peak of a "
                  "COLD planet, which is why a trace of CO2 matters here"),
        dict(nu0=2349.0, width=200.0, S=9.7e-17, d=1.5, gamma=0.08,
             note="nu3 asymmetric stretch, 4.3 microns -- CO2's strongest "
                  "band, ten times the bend, and it is where a HOT planet "
                  "radiates"),
        dict(nu0=3716.0, width=120.0, S=1.2e-18, d=1.5, gamma=0.08,
             note="combination band"),
        dict(nu0=960.0, width=90.0, S=3.0e-20, d=1.5, gamma=0.08,
             note="the weak 10 micron bands, in the window"),
    ],
    "H2O": [
        dict(nu0=250.0, width=500.0, S=6.0e-17, d=0.5, gamma=0.09,
             note="the pure rotation band -- water is bent and polar, so "
                  "it absorbs right down into the far infrared where a "
                  "cold planet radiates. CO2 cannot do this at all"),
        dict(nu0=1595.0, width=600.0, S=3.0e-17, d=0.8, gamma=0.09,
             note="nu2 bend, 6.3 microns"),
        dict(nu0=3700.0, width=400.0, S=2.0e-17, d=0.8, gamma=0.09,
             note="the nu1 and nu3 stretches"),
    ],
    "CH4": [
        dict(nu0=1306.0, width=300.0, S=1.1e-17, d=1.2, gamma=0.06,
             note="nu4 bend, 7.7 microns -- squarely in the window, which "
                  "is why a little methane does so much"),
        dict(nu0=3019.0, width=250.0, S=1.1e-17, d=1.2, gamma=0.06,
             note="nu3 stretch"),
    ],
    "N2": [],       # homonuclear: no dipole, NO bands at all, only CIA
}


# ---------------------------------------------- the continuum
# A LONE CO2 MOLECULE IS SYMMETRIC AND HAS NO DIPOLE. That is why its
# absorption lives in a few narrow bands and why the window between
# them stays open no matter how much gas is added. But two molecules
# in the act of colliding are briefly ONE distorted object with an
# induced dipole, and that transient pair absorbs where neither
# partner can alone. This is collision-induced absorption, and no
# table of single-molecule band strengths can contain it, because it
# is not a property of a molecule.
#
# THE DECISIVE FACT IS THAT IT IS A TWO-BODY PROCESS, SO IT GOES AS
# DENSITY SQUARED. The chance of finding a molecule is proportional
# to n; the chance of finding two together is proportional to n^2.
# Line absorption goes as n, this goes as n^2, and that single
# difference in exponent is why the continuum is nothing at one bar
# and everything at ninety. Nobody has to decide when it switches on.
#
#     tau_cia  =  k * (n/n0)^2 * L
#
# with k measured on gas in a cell, n0 the Loschmidt density, and L
# the path -- taken as the scale height, which is derived from the
# temperature, the molecular mass and the body's own gravity.
LOSCHMIDT = 2.6867811e25        # m^-3, exact by definition
CIA = {
    "CO2": dict(k=1.0e-8, lo=50.0, hi=550.0,
                note="CO2-CO2 induced dipole, measured in cm^-1 per "
                     "amagat squared; it fills the far-infrared window "
                     "that the 15 micron band leaves open"),
    "H2O": dict(k=4.0e-8, lo=800.0, hi=1200.0,
                note="the water continuum across the 8-12 micron window"),
    "N2": dict(k=1.0e-9, lo=50.0, hi=350.0,
               note="N2-N2, weak, but it is what warms Titan"),
}


def scale_height(T, mu_g_mol, gravity):
    """m. DERIVED: kT over the weight of one molecule."""
    m = mu_g_mol * 1e-3 / N_A
    return K_B * T / (m * gravity)


def cia_tau(species, partial_pa, T, gravity):
    """Continuum optical depth. DERIVED, and quadratic in density."""
    if species not in CIA or partial_pa <= 0:
        return 0.0
    c = CIA[species]
    n = partial_pa / (K_B * T)                 # molecules per m^3
    amagat = n / LOSCHMIDT
    L_cm = scale_height(T, MU[species], gravity) * 100.0
    return c["k"] * amagat ** 2 * L_cm


def molecules_per_cm2(column_kg_m2, mu_g_mol):
    """Column in molecules/cm^2. DERIVED from a mass and a molar mass."""
    return column_kg_m2 * 0.1 / mu_g_mol * N_A


def _molar(formula):
    """g/mol from the periodic table. DERIVED, not typed.

    These were four typed numbers, and a stress sweep caught them for
    the same reason the duplicated constants were caught: a quantity
    that can be computed had a second home. They agreed to three
    decimal places, which is exactly how a typed table survives long
    enough to go wrong.
    """
    from engine.experts import PT
    w = {sym: m for sym, _name, m in PT}
    tot, i = 0.0, 0
    while i < len(formula):
        j = i + 1
        while j < len(formula) and formula[j].islower():
            j += 1
        sym = formula[i:j]
        k = j
        while k < len(formula) and formula[k].isdigit():
            k += 1
        tot += w[sym] * int(formula[j:k] or 1)
        i = k
    return tot


FORMULAE = {"CO2": "CO2", "H2O": "H2O", "CH4": "CH4", "N2": "N2"}
MU = {k: _molar(v) for k, v in FORMULAE.items()}


# A BAND DOES NOT ONLY SATURATE, IT WIDENS -- AND THAT IS WHAT CLOSES
# A WINDOW. The third missing rule, and the lab found it the same way
# as the other two: adding the continuum did not clear the ceiling,
# adding the absent bands did not clear it either, and what was left
# was that every band here had a FIXED spectral extent.
#
# It cannot be fixed. A Lorentz line's wing absorbs as gamma/(dnu)^2,
# so the further out you look the weaker it is -- but with enough gas
# even a weak wing is opaque. The wing goes black out to wherever
#
#     S * u * gamma / (pi * dnu^2)  =  1     ->   dnu = sqrt(S u gamma/pi)
#
# and that grows without limit as the square root of column times
# pressure. On a thin atmosphere it is nothing and the nominal band
# width is right. At ninety bars the wings of neighbouring bands
# reach across the gaps between them, merge, and THE WINDOW STOPS
# EXISTING. No new substance is required and no coefficient is
# tuned: it is the same inverse-square wing that gave the square-root
# law, read at a different question.
# AND THE WING HAS AN END, WHICH IS THE FOURTH MISSING RULE.
# Unbounded widening said Venus' 15 micron band blacks out 315,694
# cm^-1 -- seventy-nine times the whole thermal infrared -- and it
# widened Earth's water rotation band to 1,671 cm^-1 and overshot
# Earth by +9.8 K. A band cannot be wider than the spectrum, so the
# rule was incomplete in both directions at once.
#
# The Lorentz profile comes from the IMPACT APPROXIMATION, which
# treats a collision as instantaneous. A collision is not
# instantaneous; it lasts about as long as one molecule takes to pass
# another. By the uncertainty relation that finite duration blurs
# frequencies only out to
#
#     dnu_c  =  1 / (2 pi c tau_collision),   tau = diameter / speed
#
# and beyond that detuning the approximation fails and real wings
# fall off FASTER than Lorentz. Both quantities are molecular:
# diameter from the gas, speed from sqrt(8kT/pi m). Nothing here is
# a planet and nothing is a fitted cutoff.
DIAMETER_M = {"CO2": 3.3e-10, "H2O": 2.65e-10, "CH4": 3.8e-10,
              "N2": 3.64e-10}
C_CM = 2.99792458e10


def collision_cutoff(species, T):
    """cm^-1 past which wings are sub-Lorentzian. DERIVED.

    This used to be a diameter over a mean speed, which is a guess
    with units on it. engine/potential.py now derives the
    intermolecular potential from polarizability and ionisation
    energy and integrates an actual trajectory through it, which is
    slower near the turning point where the kinetic energy has gone
    into the field. The collision lasts 1.19 times longer than the
    crude estimate said.
    """
    try:
        from engine.potential import wing_cutoff, MOLECULES
        if species in MOLECULES:
            return wing_cutoff(species, T)
    except Exception:
        raise
    m = MU[species] * 1e-3 / N_A
    v = math.sqrt(8 * K_B * T / (math.pi * m))
    return 1.0 / (2 * math.pi * C_CM * DIAMETER_M[species] / v)


def opaque_width(species, column_kg_m2, pressure_pa, band=0, T=288.0):
    """cm^-1 of spectrum this band actually blacks out. DERIVED."""
    bl = BANDS[species]
    if not bl or column_kg_m2 <= 0:
        return 0.0
    b = bl[band]
    u = molecules_per_cm2(column_kg_m2, MU[species])
    gamma = b["gamma"] * (pressure_pa / P_REF)
    if u <= 0 or gamma <= 0:
        return b["width"]
    dc = collision_cutoff(species, T)
    amp = b["S"] * u * gamma / math.pi

    def kappa(d):
        k = amp / (d * d)
        if d > dc:
            k *= math.exp(-(d - dc) / dc)
        return k

    if kappa(b["width"] / 2) < 1.0:
        return b["width"]
    lo, hi = b["width"] / 2, b["width"] / 2
    for _ in range(200):
        hi *= 1.3
        if kappa(hi) < 1.0:
            break
    for _ in range(80):
        mid = math.sqrt(lo * hi)
        if kappa(mid) >= 1.0:
            lo = mid
        else:
            hi = mid
    return max(b["width"], 2.0 * lo)


def goody_tau(species, column_kg_m2, pressure_pa, band=0):
    """One band's optical depth. DERIVED from laboratory data alone.

    Weak-line and strong-line limits both fall out of the one form;
    nothing switches between them and nothing was fitted.
    """
    bl = BANDS[species]
    if not bl:
        return 0.0
    b = bl[band]
    u = molecules_per_cm2(column_kg_m2, MU[species])
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


# A GUARD AGAINST log(0) BECAME A CEILING ON PHYSICS.
#
# Transmittance was clamped at 1e-12 before taking its logarithm, to
# avoid log(0). That is an ordinary numerical precaution and it
# quietly capped optical depth at -ln(1e-12) = 27.6. Venus needs
# 147.6. So no atmosphere this module could describe was ever
# allowed to be as opaque as Venus actually is, whatever the band
# data said -- and the layer-3 MISSING_RULE was measuring the clamp
# as much as the chemistry.
#
# The floor is now set by the smallest positive number a float can
# hold, which is a property of the arithmetic rather than a choice,
# and it puts the ceiling near 700 -- far above anything a planet
# does. A check asserts the ceiling stays well clear of what the
# bodies in the table require, so this cannot silently come back.
import sys as _sys

TAU_MAX = -math.log(_sys.float_info.min)


def _to_tau(transmittance):
    """-> optical depth. Floored by float precision, not by a choice."""
    t = min(max(transmittance, _sys.float_info.min), 1.0)
    return -math.log(t)


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
        for i, b in enumerate(BANDS[sp]):
            w = opaque_width(sp, col, pressure_pa, i, T)
            f = planck_fraction(max(1.0, b["nu0"] - w / 2),
                                b["nu0"] + w / 2, T)
            tot_f += f
            trans += f * math.exp(
                -min(goody_tau(sp, col, pressure_pa, i), 700.0))
    if tot_f > 1.0:                 # bands overlap; share the spectrum
        trans /= tot_f
        tot_f = 1.0
    trans += (1.0 - tot_f)
    return _to_tau(trans)


def _spectral_bins(n=400, lo=1.0, hi=4000.0):
    step = (hi - lo) / n
    return [(lo + i * step, lo + (i + 1) * step) for i in range(n)], step


# A WING FALLS OFF. IT IS NOT A WIDER BOX.
#
# opaque_width() answers "how far out is this band still opaque",
# and the previous version used that as the edge of a rectangle,
# assigning the BAND-CENTRE optical depth to every wavenumber inside
# it. A band with tau of ten billion and a wing reaching 100,000
# cm^-1 therefore had tau of ten billion everywhere across it.
#
# The result was a switch. Below a wing cutoff of about 29 cm^-1
# Venus came out 479 K too cold; above 96 cm^-1 it came out 349 K
# too hot, with nothing in between. Real absorption does not behave
# like that, and neither does a Lorentz profile: the whole content
# of a wing is that it WEAKENS with distance from the line centre,
#
#     tau(nu)  =  S u / pi  *  gamma / ((nu - nu0)^2 + gamma^2)
#
# so a widened band is a tall narrow core with long thin shoulders,
# and adding gas raises the shoulders gradually rather than
# switching the sky from open to shut.
def line_tau(species, column_kg_m2, pressure_pa, band, nu_cm, T=288.0):
    """Optical depth AT a wavenumber. DERIVED from the line shape."""
    bl = BANDS[species]
    if not bl or column_kg_m2 <= 0:
        return 0.0
    b = bl[band]
    u = molecules_per_cm2(column_kg_m2, MU[species])
    gamma = b["gamma"] * (pressure_pa / P_REF)
    if u <= 0 or gamma <= 0:
        return 0.0
    d = abs(nu_cm - b["nu0"])
    half = b["width"] / 2.0
    # inside the nominal band the lines are dense: the Goody band
    # model already averages over them, so use it there.
    if d <= half:
        return goody_tau(species, column_kg_m2, pressure_pa, band)
    # outside it, one Lorentz wing, cut off where a collision's
    # finite duration ends the impact approximation
    dd = d - half
    k = (b["S"] * u / math.pi) * gamma / (dd * dd + gamma * gamma)
    dc = collision_cutoff(species, T)
    if dd > dc:
        k *= math.exp(-(dd - dc) / dc)
    return k


def grey_equivalent_full(mix_pa, T, gravity, p_total_pa, nbins=400):
    """-> tau. Bands and continuum on a SPECTRAL GRID.

    OVERLAPPING ABSORBERS ADD THEIR OPTICAL DEPTHS; THEY DO NOT
    AVERAGE THEIR TRANSMITTANCES. The previous version summed each
    band's Planck-weighted transmittance and, when the coverage
    exceeded the whole spectrum, divided by the total to renormalise.
    That treats two absorbers in the same place as alternatives
    rather than as both being in the way, and it let a WEAK band
    dilute a strong one: CO2's tiny 10 micron feature kept leaking
    photons that its enormous 15 micron and 4.3 micron bands had
    already stopped.
    
    The symptom was that Venus's optical depth saturated at 21.08 no
    matter how far the wings were allowed to spread -- ten million
    times the derived cutoff changed nothing. That looked like
    physics saying CO2 cannot make a Venus. It was arithmetic saying
    a weighted average cannot exceed its largest term.
    
    Beer-Lambert is per wavenumber, so the fix is to be per
    wavenumber: bin the spectrum, add every absorber's tau in each
    bin, transmit exp(-tau) there, and Planck-weight the result.
    Overlap is then automatic and nothing needs renormalising.
    """
    bins, step = _spectral_bins(nbins)
    tau_bin = [0.0] * len(bins)
    for sp, pp in sorted(mix_pa.items()):
        if pp <= 0:
            continue
        if sp in BANDS:
            col = pp / gravity
            for i, b in enumerate(BANDS[sp]):
                for k, (blo, bhi) in enumerate(bins):
                    tau_bin[k] += line_tau(sp, col, p_total_pa, i,
                                           0.5 * (blo + bhi), T)
        if sp in CIA:
            c = CIA[sp]
            tau = cia_tau(sp, pp, T, gravity)
            for k, (blo, bhi) in enumerate(bins):
                if bhi > c["lo"] and blo < c["hi"]:
                    tau_bin[k] += tau
    num = den = 0.0
    for k, (blo, bhi) in enumerate(bins):
        f = planck_fraction(blo, bhi, T)
        den += f
        num += f * math.exp(-min(tau_bin[k], 700.0))
    if den <= 0:
        return 0.0
    return _to_tau(num / den)


def window_fraction(mix, T):
    """How much of the outgoing spectrum no gas here can touch."""
    f = 0.0
    for sp, col in mix.items():
        if col > 0 and sp in BANDS:
            for b in BANDS[sp]:
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
    t("continuum_is_quadratic_in_density", _cia)
    t("bands_widen_under_pressure", _widen)
    t("no_numerical_ceiling_on_opacity", _ceiling)
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
    bd = BANDS["CO2"][0]
    u_sat = math.pi * bd["gamma"] / bd["S"]
    col_sat = u_sat * MU["CO2"] / N_A / 0.1
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
    tau = grey_equivalent({"CO2": 1e9}, P_REF, 288.0)
    f = window_fraction({"CO2": 1e9}, 288.0)
    expect = -math.log(max(f, 1e-12))
    if abs(tau - expect) > 0.6:
        raise ArithmeticError(f"an infinitely opaque CO2 band gave "
                              f"tau={tau:.3f}, expected {expect:.3f}")
    return (f"a CO2 column of 1e9 kg/m2 -- opaque past any doubt -- gives "
            f"tau={tau:.3f}, not infinity, because {100*f:.0f}% of the "
            f"spectrum is left open between its bands. Averaging "
            f"depths instead of transmittances gave Earth tau=230 and a "
            f"surface of 922 K")


def _window():
    tau_small = grey_equivalent({"CO2": 1e2}, P_REF, 288.0)
    tau_huge = grey_equivalent({"CO2": 1e12}, P_REF, 288.0)
    if tau_huge - tau_small > 1.0:
        raise ArithmeticError("ten orders more CO2 still moved tau a lot; "
                              "the band is not saturating")
    w = window_fraction({"CO2": 1e12}, 288.0)
    if w < 0.3:
        raise ArithmeticError(f"only {w:.2f} of the spectrum left open")
    return (f"raising CO2 by ten orders of magnitude moves tau by "
            f"{tau_huge-tau_small:.4f}, because {100*w:.0f}% of a 288 K "
            f"body's radiation comes out at wavelengths CO2 does not "
            f"absorb. One gas cannot close a sky it does not reach, and "
            f"this is why CO2 alone cannot make a Venus")


def _cia():
    """The exponent is the whole content of the continuum."""
    a = cia_tau("CO2", 1e5, 300.0, 9.0)
    b = cia_tau("CO2", 2e5, 300.0, 9.0)
    r = b / a
    if not 3.8 < r < 4.2:
        raise ArithmeticError(f"doubling density scaled the continuum by "
                              f"{r:.3f}; a two-body process must give 4")
    thin = cia_tau("CO2", 42.6, 288.0, 9.82)
    thick = cia_tau("CO2", 8.9e6, 737.0, 8.87)
    return (f"doubling the density multiplies the continuum by {r:.3f}, "
            f"because two molecules must meet and the chance of that goes "
            f"as n squared. At a CO2 partial pressure of 43 Pa it is "
            f"{thin:.2e} and at 89 bar it is {thick:.1f} -- {thick/thin:.1e} "
            f"times larger, from the exponent alone. Nothing decides when "
            f"the continuum switches on")


def _widen():
    thin = opaque_width("CO2", 4.34, 1.01325e5, 0, 288.0)
    thick = opaque_width("CO2", 1.0e6, 9.2e6, 0, 737.0)
    nominal = BANDS["CO2"][0]["width"]
    if thin > nominal * 1.5:
        raise ArithmeticError(f"a thin atmosphere already widened to {thin}")
    if thick <= thin:
        raise ArithmeticError("pressure did not widen the band")
    return (f"CO2's 15 micron band blacks out {thin:.0f} cm^-1 at Earth-like "
            f"column and pressure -- its nominal {nominal:.0f} -- and "
            f"{thick:.3g} cm^-1 at a hundred bars. The wings go as "
            f"gamma/dnu^2, so with enough gas even a far wing is opaque, "
            f"and the opaque width grows as sqrt(column x pressure) "
            f"far -- but only out to where a collision's finite duration "
            f"stops the impact approximation working, at "
            f"{collision_cutoff('CO2', 737.0):.1f} cm^-1, past which real "
            f"wings fall faster than Lorentz. Unbounded, the same rule "
            f"claimed 315,694 cm^-1, which is 79 times the whole thermal "
            f"infrared")


def _ceiling():
    need_venus = (4.0 / 3.0) * ((737.0 / 226.7) ** 4 - 1.0)
    if TAU_MAX < 2 * need_venus:
        raise ArithmeticError(
            f"optical depth is capped at {TAU_MAX:.1f} and the most "
            f"opaque body known needs {need_venus:.1f}; a guard against "
            f"log(0) is acting as a physical limit")
    return (f"optical depth can reach {TAU_MAX:.0f}, set by the smallest "
            f"positive float rather than by a chosen constant. The most "
            f"opaque atmosphere in the table needs {need_venus:.1f}. A "
            f"1e-12 clamp used to cap it at 27.6, below what Venus is. "
            f"It was not binding at the shipped wing cutoff, where tau is "
            f"0.382 -- but it silently capped the unbounded-wing branch, "
            f"which is why a scan of that branch saturated at -278 K and "
            f"looked like physics")


if __name__ == "__main__":
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:72]}")
    print("\nall:", ok)


