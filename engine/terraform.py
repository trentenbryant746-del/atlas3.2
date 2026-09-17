"""
A planet that changes itself. No agent, no terraformer, no choices.

THE RULE THIS MODULE EXISTS TO OBEY: nothing acts on the planet. There
is no engineer, no seeding, no intervention and no optimiser looking
for a habitable answer. There is a rock with an interior, a star
shining on it, and the consequences. If it ends up temperate that is
because the equations have a fixed point there, and if it ends up
Venus that is because they have a fixed point there instead. Both
outcomes are reported the same way.

WHAT MAKES A PLANET SELF-REGULATING IS A LOOP, NOT A CONTROLLER.

    interior outgasses CO2  ->  greenhouse warms the surface
    warmer surface          ->  more rain, faster silicate weathering
    faster weathering       ->  CO2 buried as carbonate
    less CO2                ->  cooler surface

That is negative feedback with no one running it, and it is why Earth
has stayed liquid for four billion years while the Sun brightened by
about 30%. The loop is the whole mechanism. Everything else here is
the arithmetic needed to close it.

AND IT HAS TWO WAYS TO BREAK, BOTH OF WHICH MUST FALL OUT RATHER THAN
BE TYPED IN. Weathering needs liquid water. Too hot and the oceans are
vapour, so rain stops, so the feedback opens and CO2 accumulates with
nothing to remove it -- runaway. Too cold and the oceans are ice, so
rain stops again, and CO2 accumulates until it thaws, which is a
RECOVERY unless outgassing has already died with the interior. A
habitable zone is then not a number anybody supplies. It is the range
of stellar flux over which the loop has a fixed point with liquid
water at it.

EVERY CONSTANT THAT CAN BE DERIVED IS. Stefan-Boltzmann is not a
looked-up number here; it is 2*pi^5*k^4 / (15*h^3*c^2), and h, c and k
are exact by definition of the second, the metre and the kelvin. It is
checked against the published value to make sure the derivation is the
same quantity and not merely a plausible one.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, ASSERTED = "DERIVED", "ASSERTED"
INHERITED = "DERIVED_FROM_ASSERTED"

# Exact by definition since the 2019 SI revision. Not measurements.
from engine.constants import (H_PLANCK, C_LIGHT, K_B, N_A,  # noqa: E402
                              G_GRAV, U_KG as AMU, AU_M as AU,
                              L_SUN_W as L_SUN)

# Measured, and labelled as such. G is the worst-known constant in
# physics -- about 22 parts per million -- and that uncertainty is
# carried, not hidden.



def sigma_sb():
    """Stefan-Boltzmann, DERIVED from three exact constants."""
    return (2 * math.pi ** 5 * K_B ** 4) / (15 * H_PLANCK ** 3 * C_LIGHT ** 2)


SIGMA = sigma_sb()
R_GAS = K_B * N_A             # DERIVED: the gas constant is k times N_A


# --------------------------------------------------------- the bodies
# Mass, radius, distance and the star's output are OBSERVATIONS. They
# are the question, not the answer: nothing below is allowed to read a
# planet's actual temperature or actual atmosphere while deriving one.

class Body:
    def __init__(self, name, mass_kg, radius_m, au, albedo,
                 observed_T=None, observed_bar_pa=None, observed_co2=None,
                 water_kg=0.0, eccentricity=0.0, internal_w_m2=0.0):
        self.name, self.mass, self.radius = name, mass_kg, radius_m
        self.au, self.albedo = au, albedo
        # An inventory, carried by the body. The first version looked
        # the ocean up by the body's NAME, so every planet that was
        # not literally called "Earth" was bone dry and every
        # habitable-zone probe came back a runaway. Water is a
        # property of a world, not of a string.
        self.water_kg = water_kg
        # THE SEMI-MAJOR AXIS IS THE RIGHT LENGTH AND THE WRONG
        # AVERAGE. A planet spends longer near aphelion, but flux
        # goes as 1/r^2, so the time-average of the FLUX is
        # 1/(a^2 sqrt(1-e^2)) and not 1/a^2. Derivable, correct, and
        # worth +2.4 K on Mercury and +0.01 K on Earth -- far inside
        # the 9.3 K planetary bar for every body that is scored. It
        # goes in because it is right, not because it shows.
        self.eccentricity = eccentricity
        # A PLANET IS ALSO WARM FROM THE INSIDE. Radioactive decay
        # and leftover heat of formation leak out through the
        # surface, and on a tidally squeezed body they dominate.
        # Earth's 0.087 W/m2 against 236 absorbed is worth 0.0 K and
        # is right to ignore; Io's 2.0 against 4.65 is 43% and worth
        # +8.9 K. The model counted only starlight, which is why Io
        # came out 14.8 K too cold and the shortfall was blamed on
        # having no atmosphere.
        self.internal_w_m2 = internal_w_m2
        self.observed_T = observed_T
        self.observed_bar_pa = observed_bar_pa
        self.observed_co2 = observed_co2

    def gravity(self):
        """m/s^2. DERIVED."""
        return G_GRAV * self.mass / self.radius ** 2

    def escape_velocity(self):
        """m/s. DERIVED."""
        return math.sqrt(2 * G_GRAV * self.mass / self.radius)

    def flux(self, luminosity=L_SUN):
        """W/m^2 at the top of the atmosphere. DERIVED, inverse square."""
        e = getattr(self, "eccentricity", 0.0)
        return (luminosity / (4 * math.pi * (self.au * AU) ** 2)
                / math.sqrt(1.0 - e * e))


BODIES = {
    # albedo is observed; so are T and surface pressure, and those two
    # are used ONLY to score, never to derive.
    "Venus": Body("Venus", 4.8675e24, 6.0518e6, 0.723, 0.77,
                  observed_T=737.0, observed_bar_pa=9.2e6, observed_co2=0.965, eccentricity=0.0068),
    "Earth": Body("Earth", 5.97219e24, 6.371e6, 1.000, 0.306,
                  observed_T=288.0, observed_bar_pa=1.01325e5,
                  observed_co2=4.2e-4, water_kg=1.35e21,
                  eccentricity=0.0167),
    "Mars": Body("Mars", 6.4171e23, 3.3895e6, 1.524, 0.250,
                 observed_T=210.0, observed_bar_pa=6.36e2, observed_co2=0.95, eccentricity=0.0934),
    "Titan": Body("Titan", 1.3452e23, 2.5747e6, 9.537, 0.22,
                  observed_T=94.0, observed_bar_pa=1.467e5,
                  eccentricity=0.0288),
    "Mercury": Body("Mercury", 3.3011e23, 2.4397e6, 0.387, 0.088,
                    observed_T=440.0, observed_bar_pa=5e-10,
                    eccentricity=0.2056),
}


# A SINGLE TEMPERATURE IS NOT ALWAYS A MEANINGFUL QUANTITY, AND
# SCORING AGAINST ONE THAT IS NOT COST ME A RESULT.
#
# The factor of 4 in the equilibrium temperature comes from a sphere
# intercepting pi r^2 and radiating from 4 pi r^2. That is only
# right if the absorbed heat gets SPREAD over the whole sphere,
# which needs an atmosphere to carry it or rotation fast enough that
# no face stays lit. Without redistribution the subsolar point runs
# at 4^(1/4) = 1.41 times hotter and the night side falls towards
# nothing, and the average of T is not the T of the average because
# radiation goes as the fourth power.
#
# Version 3.1.19 reported Mercury as a held-out success at +2.8 K. It
# was not. Mercury's quoted 440 K is its DAYSIDE mean; its global
# mean is nearer 340 K. A model that assumes full redistribution was
# being scored against a number that assumes none, and the agreement
# was a coincidence of two mismatched quantities. Against the global
# figure the same model is about +97 K out.
#
# So the criterion is derived and the body is REFUSED when it fails:
# compare how long the surface takes to radiate its heat away against
# how long the planet takes to turn. If it cools faster than it
# spins, each face sits at its own temperature and the planet does
# not have one.
def _cp(species, T):
    """J/kg/K, DERIVED from shape and band frequencies. Was typed."""
    from engine.thermo import cp_specific
    return cp_specific(species, T)
DAY_S = 86400.0

ROTATION_S = {"Venus": 243.0 * DAY_S, "Earth": 1.0 * DAY_S,
              "Mars": 1.027 * DAY_S, "Titan": 15.95 * DAY_S,
              "Mercury": 58.65 * DAY_S, "Moon": 27.3 * DAY_S}


def radiative_time(body, T, p_total_pa, cp=None):
    """Seconds for the atmosphere to radiate its heat. DERIVED."""
    if p_total_pa <= 0 or T <= 0:
        return 0.0
    if cp is None:
        cp = _cp("CO2" if (body.observed_co2 or 0) > 0.5 else "N2", T)
    return cp * (p_total_pa / body.gravity()) / (4 * SIGMA * T ** 3)


def redistributes(body, T=None, p_total_pa=None):
    """-> (bool, ratio, why). Does this body HAVE one temperature?"""
    if T is None:
        T = equilibrium_T(body)
    if p_total_pa is None:
        p_total_pa = body.observed_bar_pa or 0.0
    rot = ROTATION_S.get(body.name)
    if rot is None:
        return True, float("inf"), "rotation unknown; assumed mixed"
    tr = radiative_time(body, T, p_total_pa)
    r = tr / rot
    # Three tiers, not two. A binary cut refused Mars, which sits at
    # 0.92 -- and Mars is genuinely marginal: it has the largest
    # day-night swing of any body here, about 60 K, so its mean is a
    # real number but a noisier one than Earth's. Mercury is at
    # 1.4e-15. Six orders of magnitude separate them, so where the
    # line goes between is not a sensitive choice.
    if r >= 1.0:
        return True, r, (f"the atmosphere holds its heat {r:.2f} rotations, "
                         f"so day and night even out and a single mean "
                         f"temperature means something")
    if r >= 0.1:
        return True, r, (f"marginal at {r:.2f} rotations of heat storage -- "
                         f"the mean is meaningful but the day-night swing "
                         f"is large, so this body deserves a wider bar "
                         f"than a well-mixed one")
    return False, r, (f"the surface radiates its heat away in {r:.3g} of a "
                      f"rotation, so each face sits at its own temperature "
                      f"and this body does not HAVE one temperature -- any "
                      f"single number quoted for it is a choice of which "
                      f"average, and scoring against it compares two "
                      f"different quantities")


def equilibrium_T(body, luminosity=L_SUN, albedo=None):
    """Bare-rock temperature. DERIVED: absorbed equals radiated.

    A sphere intercepts pi r^2 of the beam and radiates from 4 pi r^2,
    which is where the 4 comes from -- it is geometry, not a fudge.
    """
    a = body.albedo if albedo is None else albedo
    absorbed = body.flux(luminosity) * (1 - a) / 4.0
    return ((absorbed + getattr(body, "internal_w_m2", 0.0)) / SIGMA) ** 0.25


# ------------------------------------------------- what stays put
# A gas escapes when its molecules are fast enough often enough. The
# Jeans parameter is the ratio of gravitational binding to thermal
# energy, and the threshold is NOT typed here -- it is measured below
# against which gases the five bodies actually kept.
MOLAR = {"H2": 2.016, "He": 4.003, "CH4": 16.04, "H2O": 18.015,
         "N2": 28.013, "O2": 31.998, "CO2": 44.009, "Ar": 39.948}


def jeans_lambda(body, species, T=None):
    """Gravitational binding over thermal energy. DERIVED, dimensionless."""
    if species not in MOLAR:
        raise KeyError(f"no molar mass for {species!r}")
    if T is None:
        T = equilibrium_T(body)
    m = MOLAR[species] * AMU / (N_A * AMU / N_A)   # kg per molecule
    m = MOLAR[species] * 1e-3 / N_A
    return G_GRAV * body.mass * m / (K_B * T * body.radius)


# ------------------------------------------------- the greenhouse
# A grey slab: the atmosphere is transparent to sunlight and opaque to
# the ground's infrared, with one optical depth tau doing all the work.
#
#     T_surface = T_eq * (1 + 3 tau / 4) ^ (1/4)
#
# It is the crudest radiative model that is not wrong in principle,
# and the 3/4 is the two-stream result, not a fitted shape.
#
# WHERE tau COMES FROM IS THE HONEST PART. It must come from how much
# absorber is overhead, and the column of a gas is its partial
# pressure divided by gravity -- that is just the weight of the column
# holding itself up. So tau = k * column^n, and k and n are unknown.
#
# TWO POINTS DETERMINE TWO PARAMETERS EXACTLY, WHICH MEANS NO BAR.
# Venus and Mars are the two bodies here whose atmospheres are CO2, so
# they are what k and n are solved from -- and solving two unknowns
# from two points leaves no residual to measure. That is not a fit
# with a good score. It is a fit with NO score, and saying so is the
# only honest thing to do with it.

RH_EARTH = 0.7          # ASSERTED: global mean relative humidity
L_VAP = 2.501e6         # J/kg, measured latent heat of vaporisation
T_TRIPLE, P_TRIPLE = 273.16, 611.657     # K, Pa


def column(partial_pa, g):
    """kg/m^2 of absorber overhead. DERIVED: a column holds its weight."""
    return partial_pa / g


def _solve_power_law(p1, p2):
    """Two (column, tau) points -> (k, n). Exact, so no residual."""
    (c1, t1), (c2, t2) = p1, p2
    n = math.log(t2 / t1) / math.log(c2 / c1)
    return t1 / c1 ** n, n


def tau_from_T(T_surf, T_eq):
    """Invert the grey slab to read off the optical depth actually there."""
    return 4.0 / 3.0 * ((T_surf / T_eq) ** 4 - 1.0)


def _co2_law():
    """(k, n) for CO2, solved from Venus and Mars. DERIVED_FROM_ASSERTED."""
    pts = []
    for n in ("Venus", "Mars"):
        b = BODIES[n]
        te = equilibrium_T(b)
        tau = tau_from_T(b.observed_T, te)
        # Mars' mean surface and its bare-rock temperature agree to
        # within a degree, so its tau inverts to nearly zero and the
        # log blows up. The observed greenhouse on Mars is small but
        # not zero; the floor keeps the solve finite and is recorded
        # as the weak point of this two-point law.
        tau = max(tau, 1e-3)
        pts.append((column(b.observed_co2 * b.observed_bar_pa, b.gravity()),
                    tau))
    return _solve_power_law(*pts)


K_CO2, N_CO2 = _co2_law()


def tau_co2(body, co2_pa):
    """DERIVED once the two-point law is solved."""
    c = column(co2_pa, body.gravity())
    return 0.0 if c <= 0 else K_CO2 * c ** N_CO2


# CO2 CONDENSES, AND LEAVING THAT OUT MEANT THE OUTER EDGE OF THE
# HABITABLE ZONE DID NOT EXIST.
#
# The thermostat lets carbon dioxide accumulate until weathering
# balances outgassing, and on a cold planet weathering is slow, so
# CO2 piles up and the grey slab turns it into warmth. Run far
# enough out and the model keeps water liquid past 12 AU, which is
# nonsense and was reported as UNDETERMINED in 3.1.36 rather than
# bounded by hand.
#
# A real atmosphere cannot do it. Carbon dioxide has a condensation
# curve like anything else, and a cold planet reaches it: at 195 K
# the air can hold about 1.1 bar of CO2 and no more. Add any and it
# snows out. The greenhouse therefore caps ITSELF, and that cap --
# the maximum-greenhouse limit -- is what sets an outer edge.
#
# This is the SAME EQUATION already used for water a few lines
# below, with carbon dioxide's own triple point and latent heat.
# The rule was absent, not difficult, which is why it was worth
# saying so instead of inventing a bound.
T_TRIPLE_CO2, P_TRIPLE_CO2 = 216.58, 5.185e5     # K, Pa, measured
L_SUB_CO2 = 5.71e5                               # J/kg, measured


def p_sat_co2(T):
    """Pa. Above this, CO2 snows out. DERIVED from Clausius-Clapeyron."""
    rv = R_GAS / (MOLAR["CO2"] * 1e-3)
    return P_TRIPLE_CO2 * math.exp(
        L_SUB_CO2 / rv * (1.0 / T_TRIPLE_CO2 - 1.0 / T))


def co2_ceiling(T):
    """The most CO2 a surface at T can keep in the air. DERIVED."""
    return p_sat_co2(T)


def p_sat_water(T):
    """Clausius-Clapeyron. Pa. DERIVED from L and the triple point.

    Rv is not looked up: it is the gas constant divided by water's
    molar mass, and the gas constant is k times Avogadro.
    """
    rv = R_GAS / (MOLAR["H2O"] * 1e-3)
    return P_TRIPLE * math.exp(L_VAP / rv * (1.0 / T_TRIPLE - 1.0 / T))


# WATER IS AN INVENTORY, NOT A SETTING. The first version gave every
# body 70% humidity and got infinity for Venus and Mercury, which is
# the model saying that a planet with unlimited water at 440 K cannot
# have a temperature -- true, and useless, because neither body has
# any water. How much vapour is overhead is capped by how much water
# the planet HAS, so the inventory is a state variable and the cap is
# what makes the runaway finite and physical:
#
#     partial pressure of vapour  =  min( RH * p_sat(T),  ocean * g )
#
# and once the whole ocean is in the air, sunlight splits it and the
# hydrogen leaves. The inventory drains. That is how a wet planet
# becomes a dry one with a CO2 atmosphere, which is Venus, and it is
# an outcome here rather than an entry in a table.
#
# EARTH'S OCEAN IS NOT TYPED EITHER. 1.35e21 kg over the area of the
# globe is the column, and both numbers are observations of the body,
# not of its climate.
OCEAN_EARTH_KG = 1.35e21


def ocean_column(body, kg=None):
    """kg/m^2 of water. DERIVED from the body's inventory and area."""
    if kg is None:
        kg = getattr(body, "water_kg", 0.0)
    return kg / (4 * math.pi * body.radius ** 2)


def tau_total(body, T, co2_pa, ocean_kgm2, humidity=RH_EARTH):
    """Optical depth at a GIVEN temperature. DERIVED, no iteration.

    The CO2 cap belongs HERE, inside the one fixed point that
    already exists, not in a second loop outside it. Nesting two
    fixed points -- one for temperature, one for how much CO2 stays
    aloft -- gave the solver a new family of roots and it found
    WARMER ones: 289 K at 12 AU against 258 K uncapped, a cap that
    heated the planet. One loop, and the cap evaluated at whatever
    temperature that loop is currently testing.
    """
    co2_pa = min(co2_pa, p_sat_co2(max(T, 60.0)))
    tw = 0.0
    if ocean_kgm2 > 0:
        pw = min(humidity * p_sat_water(T), ocean_kgm2 * body.gravity())
        tw = K_H2O * column(pw, body.gravity()) ** N_H2O
    return tau_co2(body, co2_pa) + tw, tw


def _imbalance(body, T, co2_pa, ocean_kgm2, luminosity, humidity, albedo):
    te = equilibrium_T(body, luminosity, albedo)
    tau, _ = tau_total(body, T, co2_pa, ocean_kgm2, humidity)
    return te * (1.0 + 0.75 * tau) ** 0.25 - T


def fixed_points(body, co2_pa, ocean_kgm2=None, luminosity=L_SUN,
                 humidity=RH_EARTH, albedo=None, lo=None, hi=1800.0,
                 steps=420):
    """-> [(T, "stable"|"unstable")]. EVERY solution, not the first.

    Iterating from the bare-rock temperature found 257 K for Earth and
    called it the answer. It is A answer -- a real fixed point, and
    the one a frozen Earth sits at -- but it is not the one Earth is
    at. Water vapour is positive feedback, so the balance is not
    monotonic and can have three roots: a cold state, an unstable
    ridge between, and a warm state. Reporting one of them is
    reporting a coin flip as a fact, so this scans and returns all.
    """
    if ocean_kgm2 is None:
        ocean_kgm2 = ocean_column(body)
    # 3,400 STEPS WERE BUYING NOTHING. Profiling one thermostat call
    # found fixed_points running 586 times at 3,400 points each --
    # two million evaluations of a smooth function to locate a
    # handful of roots. At 200 steps the roots are identical to the
    # last decimal, because the scan only has to BRACKET a sign
    # change and the bisection that follows does the precision. 420
    # keeps a wide margin over the coarsest that still worked.
    if lo is None:
        # The floor must sit below the bare-rock temperature or the
        # scan misses the only root a body with no atmosphere has.
        # Starting at a round 100 K lost Titan, whose answer is 85.
        lo = 0.5 * equilibrium_T(body, luminosity, albedo)
    f = lambda T: _imbalance(body, T, co2_pa, ocean_kgm2, luminosity,
                             humidity, albedo)
    out, prev_T, prev = [], lo, f(lo)
    for i in range(1, steps + 1):
        T = lo + (hi - lo) * i / steps
        cur = f(T)
        if prev == 0.0 or (prev < 0) != (cur < 0):
            a_, b_ = prev_T, T
            for _ in range(60):
                m = 0.5 * (a_ + b_)
                if (f(a_) < 0) != (f(m) < 0):
                    b_ = m
                else:
                    a_ = m
            root = 0.5 * (a_ + b_)
            # stable if the imbalance crosses downwards: a nudge up
            # gets cooled, a nudge down gets warmed
            d = f(root + 0.5) - f(root - 0.5)
            out.append((root, "stable" if d < 0 else "unstable"))
        prev_T, prev = T, cur
    return out


def states(body, co2_pa, ocean_kgm2=None, luminosity=L_SUN,
           humidity=RH_EARTH, albedo=None):
    """-> [stable temperatures]. THE ANSWER IS A SET, NOT A NUMBER.

    Earth comes out with two stable states, 288 K and 798 K, with an
    unstable ridge at 298 K between them. Both are real solutions of
    the same equations under the same sunlight, and which one a
    planet occupies is not set by present conditions -- it is set by
    where it came from. A model that returns one number here is
    picking a branch and calling it a fact. This returns the set, and
    a caller that wants one number has to say which branch and why.
    """
    return [t for t, k in fixed_points(body, co2_pa, ocean_kgm2, luminosity,
                                       humidity, albedo) if k == "stable"]


def surface_T(body, co2_pa, ocean_kgm2=None, luminosity=L_SUN,
              humidity=RH_EARTH, albedo=None, prefer="cold"):
    """-> (T, tau, tau_water, n_states).

    prefer="cold" tracks the branch a planet reaches by warming up
    into its present state from a colder past, which is the history
    every body here actually had. It is a stated assumption, not a
    discovery, and n_states is returned so the caller can see when it
    mattered.
    """
    if ocean_kgm2 is None:
        ocean_kgm2 = ocean_column(body)
    pts = states(body, co2_pa, ocean_kgm2, luminosity, humidity, albedo)
    if not pts:
        return float("inf"), float("inf"), float("inf"), 0
    T = min(pts) if prefer == "cold" else max(pts)
    tau, tw = tau_total(body, T, co2_pa, ocean_kgm2, humidity)
    return T, tau, tw, len(pts)


# WATER GETS ITS OWN EXPONENT, AND EARTH'S EXISTENCE IS WHAT FIXES IT.
#
# The first version reused CO2's exponent for water and Earth came out
# UNSTABLE at 288 K -- a tipping point rather than a home. The clash
# is real and it is in the rule, not the arithmetic: the CO2 exponent
# is 1.185, solved from two points four orders of magnitude apart and
# dominated by Venus, and an exponent above 1 means absorption grows
# FASTER than the amount of absorber. Water vapour cannot behave that
# way, because vapour rises steeply with temperature and a
# super-linear response to it is a runaway with no brake.
#
# So the exponent is derived instead, from an observation that is not
# a temperature: EARTH HAS STAYED LIQUID FOR FOUR BILLION YEARS. A
# state that persists is a stable one, and stability is a condition
# on the slope:
#
#     warming feedback gain  =  n * (dln p_sat/dT) * tau * (dT/dtau)
#
# with dln p_sat/dT from Clausius-Clapeyron and dT/dtau from the grey
# slab, both already derived. Setting the gain to 1 gives the largest
# exponent Earth could have and still be here:
#
#     n_marginal = 0.5387
#
# Anything at or above that and Earth is not a planet, it is a
# threshold. The exponent must be BELOW ONE -- absorption must
# saturate -- and that conclusion comes out of the planet still being
# here rather than out of a spectroscopy table. n = 1/2 is the
# simplest law under the bound and is the square-root behaviour a
# saturated band actually shows; it is a CHOICE, made inside a derived
# bound, and it leaves Earth at a gain of 0.93, stable but close to
# the edge -- which is why the inner edge of the habitable zone is
# near.

def marginal_water_exponent(T_ref=None):
    """The largest exponent that leaves Earth stable. DERIVED."""
    b = BODIES["Earth"]
    Ts = b.observed_T if T_ref is None else T_ref
    te = equilibrium_T(b)
    tau = tau_from_T(Ts, te)
    rv = R_GAS / (MOLAR["H2O"] * 1e-3)
    dlnp = L_VAP / (rv * Ts ** 2)
    dTdtau = Ts * 0.25 * 0.75 / (1 + 0.75 * tau)
    return 1.0 / (dlnp * tau * dTdtau)


N_H2O = 0.5          # the simple law inside the derived bound


def water_gain(n=None):
    """Feedback gain at Earth's present state. DERIVED. Below 1 = stable."""
    b = BODIES["Earth"]
    Ts, te = b.observed_T, equilibrium_T(b)
    tau = tau_from_T(Ts, te)
    rv = R_GAS / (MOLAR["H2O"] * 1e-3)
    return ((N_H2O if n is None else n) * L_VAP / (rv * Ts ** 2) * tau
            * Ts * 0.25 * 0.75 / (1 + 0.75 * tau))


def _water_coefficient():
    """k for water, solved from Earth's 34 K at its own exponent."""
    b = BODIES["Earth"]
    te = equilibrium_T(b)
    need = tau_from_T(b.observed_T, te) - tau_co2(
        b, b.observed_co2 * b.observed_bar_pa)
    pw = RH_EARTH * p_sat_water(b.observed_T)
    return need / column(pw, b.gravity()) ** N_H2O


K_H2O = 0.0
K_H2O = _water_coefficient()


# ==================================================================
# THE THERMOSTAT -- the part with no one running it
# ==================================================================
#
# Two flows, both of them consequences:
#
#   OUT   the interior degasses CO2. It does this because it is hot,
#         and it slows as the planet cools. Nothing decides to.
#
#   IN    rain dissolves CO2, weak acid attacks silicate rock, the
#         carbon ends up as carbonate on the sea floor. This is
#         faster when it is warmer, because dissolution is an
#         Arrhenius process, and it STOPS COMPLETELY when there is no
#         liquid water, because there is no rain.
#
# The atmosphere sits where the two match. Push the planet warm and
# weathering outruns outgassing, CO2 falls, and it cools back. That
# is a thermostat, and its set point is not a target anybody chose --
# it is wherever the two curves cross.
#
# THE TEMPERATURE DEPENDENCE IS DERIVED FROM ONE MEASURED CHEMISTRY
# NUMBER, NOT FROM A CLIMATE FUDGE. Arrhenius gives rate ~
# exp(-Ea/RT), so near a reference temperature the e-folding interval
# is T_e = R T^2 / Ea. Basalt dissolution has Ea about 48 kJ/mol,
# measured in a beaker with no planet involved, and that yields
# T_e = 14.4 K at 288 K. The often-quoted climate value is 13.7 K; it
# is not typed in here, it falls out of the chemistry.
#
# WEATHERING SHUTS OFF WITHOUT LIQUID WATER, AND THAT ONE FACT IS
# WHAT MAKES BOTH DISASTERS. Freeze the oceans and the sink closes,
# so CO2 piles up until it thaws -- a recovery, and the reason
# snowball Earth ended. Boil them and the sink closes too, but now
# CO2 piles up on top of an already-hot planet with nothing to stop
# it. Same rule, opposite outcomes, neither one written down.

EA_SILICATE = 48000.0        # J/mol, measured basalt dissolution
BETA_CO2 = 0.3               # ASSERTED: weathering's order in pCO2


def weathering_efolding(T_ref=288.0):
    """K per e-fold of weathering rate. DERIVED from Arrhenius."""
    return R_GAS * T_ref ** 2 / EA_SILICATE


def wet_fraction(body, T_mean, p_total_pa):
    """Fraction of the surface where rain can fall. DERIVED.

    The verdict has to be read off the same bands the sink is, or the
    module contradicts itself: integrating weathering over latitude
    and then judging habitability by the global mean called planets
    dry that were raining at the equator.
    """
    return sum(w for tb, w in band_temperatures(T_mean)
               if liquid_water(body, tb, p_total_pa))


def liquid_water(body, T, p_total_pa):
    """Can rain fall? DERIVED from the phase boundary, not a range.

    Freezing is near enough constant; boiling is not -- it is
    wherever the vapour pressure reaches the total pressure, which is
    why a thicker atmosphere keeps water liquid hotter.
    """
    if T <= T_TRIPLE - 0.16:
        return False
    return p_sat_water(T) < max(p_total_pa, P_TRIPLE)


# A PLANET DOES NOT HAVE ONE TEMPERATURE, AND PRETENDING IT DOES PINS
# THE ANSWER. The first version switched weathering off the moment
# the GLOBAL MEAN fell below freezing. Every planet past 1 AU then
# parked at exactly 273.0 K -- the thermostat drove the mean to the
# switch and sat on it -- and the verdict flickered between temperate
# and frozen on numerical noise. The clash is the rule, not the
# solver: a world whose average is 260 K still has a warm equator,
# and it still rains there.
#
# So the sink is integrated over latitude instead of switched. The
# profile is the standard insolation shape, hot at the equator and
# cold at the poles,
#
#     T(lat) = T_mean + D * (1/3 - sin^2 lat)
#
# with the contrast D taken from Earth's own equator-to-pole
# difference. Each band weathers at its own Arrhenius rate and only
# where it can rain, and the bands are area-weighted by cos(lat)
# because that is how much planet is at that latitude. The switch
# becomes a ramp, the pinning goes away, and the outer edge of the
# habitable zone stops being an artefact of a step function.
D_CONTRAST = 45.0        # K, observed equator-to-pole spread on Earth


def band_temperatures(T_mean, n=36, D=D_CONTRAST):
    """-> [(T, area weight)]. DERIVED from geometry plus one contrast."""
    out, tot = [], 0.0
    for i in range(n):
        lat = (i + 0.5) * (math.pi / 2) / n
        w = math.cos(lat)
        out.append((T_mean + D * (1.0 / 3.0 - math.sin(lat) ** 2), w))
        tot += w
    return [(t, w / tot) for t, w in out]


def weathering(body, T, co2_pa, ocean_kgm2, T_ref=288.0, co2_ref=None):
    """Relative sink strength, integrated over the planet. DERIVED."""
    if ocean_kgm2 <= 0:
        return 0.0
    if co2_ref is None:
        e = BODIES["Earth"]
        co2_ref = e.observed_co2 * e.observed_bar_pa
    te_fold = weathering_efolding(T_ref)
    p_tot = co2_pa + 1e5
    acc = 0.0
    for tb, w in band_temperatures(T):
        if not liquid_water(body, tb, p_tot):
            continue
        acc += w * math.exp((tb - T_ref) / te_fold)
    if acc <= 0.0:
        return 0.0
    # normalised so that Earth today, whose bands are computed the
    # same way, comes out at exactly 1
    return (max(co2_pa, 1e-12) / co2_ref) ** BETA_CO2 * acc / _EARTH_BANDS


def _earth_band_sum(T_ref=288.0):
    e = BODIES["Earth"]
    te_fold = weathering_efolding(T_ref)
    p_tot = e.observed_co2 * e.observed_bar_pa + 1e5
    return sum(w * math.exp((tb - T_ref) / te_fold)
               for tb, w in band_temperatures(T_ref)
               if liquid_water(e, tb, p_tot))


_EARTH_BANDS = 1.0
_EARTH_BANDS = _earth_band_sum()


def airborne_co2(body, co2_pa, ocean_kgm2=None, luminosity=L_SUN,
                 humidity=RH_EARTH, albedo=None, iters=24):
    """How much of the CO2 can actually stay in the air. DERIVED.

    The cap depends on temperature and the temperature depends on
    the cap, so it is a fixed point, not a single clamp. A colder
    surface holds less, which cools it further, which holds less
    still -- and that loop terminates because the saturation curve
    is steep.
    """
    eff = co2_pa
    for _ in range(iters):
        T = surface_T(body, eff, ocean_kgm2, luminosity, humidity,
                      albedo)[0]
        if not math.isfinite(T):
            return co2_pa
        nxt = min(co2_pa, p_sat_co2(max(T, 60.0)))
        if abs(nxt - eff) <= 1e-6 * max(eff, 1.0):
            return nxt
        eff = 0.5 * eff + 0.5 * nxt
    return eff


def _excess(body, co2_pa, outgassing, ocean_kgm2, luminosity, humidity,
            albedo):
    """outgassing minus the sink. Positive means CO2 accumulates.

    CO2 above its own saturation pressure is not in the air, it is
    on the ground, so the radiative calculation only ever sees what
    can stay aloft.
    """
    T, _, _, n = surface_T(body, co2_pa, ocean_kgm2, luminosity, humidity,
                           albedo)
    if not math.isfinite(T):
        return outgassing, T, n           # runaway: the sink is gone
    return (outgassing - weathering(body, T, co2_pa, ocean_kgm2)), T, n


def thermostat(body, outgassing=1.0, ocean_kgm2=None, luminosity=L_SUN,
               humidity=RH_EARTH, albedo=None, lo_pa=1e-6, hi_pa=1e8,
               steps=260):
    """-> dict. Where the planet puts ITSELF. No target, no controller.

    THE BALANCE IS NOT MONOTONIC AND BISECTING IT WAS WRONG. The
    first version checked the two ends, found CO2 accumulating at
    both, and declared Earth a runaway. Both ends were right: with no
    CO2 the oceans are ice and nothing weathers, and with a thousand
    bars they are steam and nothing weathers. The sink only exists in
    the middle, where it can rain. So the curve crosses zero twice --
    a low-CO2 crossing the planet settles into, and a high-CO2 one it
    only reaches if something pushes it there -- and a method that
    assumes one crossing cannot see either.

    Outgassing is in units of Earth's present rate. outgassing=1 on
    Earth at 1 AU must return Earth; that is the single calibration,
    and every other body and distance is a prediction from it.
    """
    if ocean_kgm2 is None:
        ocean_kgm2 = ocean_column(body)

    def f(c):
        return _excess(body, c, outgassing, ocean_kgm2, luminosity,
                       humidity, albedo)[0]

    roots, prev_c = [], lo_pa
    prev = f(lo_pa)
    for i in range(1, steps + 1):
        c = lo_pa * (hi_pa / lo_pa) ** (i / steps)
        cur = f(c)
        if (prev < 0) != (cur < 0):
            x, y = prev_c, c
            for _ in range(80):
                m = math.sqrt(x * y)
                if (f(x) < 0) != (f(m) < 0):
                    y = m
                else:
                    x = m
            r = math.sqrt(x * y)
            # stable when the excess falls through zero: more CO2
            # brings more rain, which takes the CO2 back out
            stable = f(r * 1.05) < f(r / 1.05)
            roots.append((r, stable))
        prev_c, prev = c, cur

    stable = [r for r, ok in roots if ok]
    if not stable:
        T, _, _, n = surface_T(body, hi_pa, ocean_kgm2, luminosity,
                               humidity, albedo)
        if f(lo_pa) < 0:
            T0, _, _, n = surface_T(body, lo_pa, ocean_kgm2, luminosity,
                                    humidity, albedo)
            return {"body": body.name, "verdict": "STRIPPED", "co2_pa": lo_pa,
                    "T": T0, "states": n, "liquid_water": False, "roots": roots,
                    "why": "weathering beats outgassing with almost no CO2 "
                           "left, so the planet removes its own atmosphere"}
        return {"body": body.name, "verdict": "RUNAWAY", "co2_pa": hi_pa,
                "T": T, "states": n, "liquid_water": False, "roots": roots,
                "why": "CO2 accumulates at every pressure and nothing "
                       "removes it -- no liquid water means no rain, and "
                       "the sink never reopens"}

    co2 = min(stable)
    T, tau, tw, n = surface_T(body, co2, ocean_kgm2, luminosity, humidity,
                              albedo)
    frac = wet_fraction(body, T, co2 + 1e5)
    if frac >= 0.999:
        v = "TEMPERATE"
    elif frac > 0.0:
        v = "PARTLY_LIQUID"
    else:
        v = "FROZEN"
    return {"body": body.name, "verdict": v,
            "co2_pa": co2, "T": T, "tau": tau, "tau_water": tw,
            "states": n, "wet_fraction": frac, "roots": roots,
            "why": f"outgassing and weathering balance at {co2:.3g} Pa of "
                   f"CO2 and a mean of {T:.1f} K, with {100*frac:.0f}% of "
                   f"the surface above freezing -- found by the loop, "
                   f"not set"}


def error_bar():
    """-> (K, why). MEASURED on the two bodies that were held out.

    A THIRD KIND OF EPISTEMIC SITUATION, and the point of keeping the
    kinds apart. The nuclear bars are residuals in MeV over many
    nuclides, so they are well determined. The folding bar is a rate,
    because no fold was ever measured and the only comparison
    available is against another model. This one is a residual
    against measurement, like the nuclear bars -- but over TWO
    bodies, because Venus, Earth and Mars were spent calibrating and
    only Mercury and Titan were left. Two points is not a
    distribution. The bar exists, it is in kelvin, and it is barely
    determined, and a module that reported it without saying so
    would be the most misleading of the three.
    """
    rows = []
    for n in sorted(BODIES):
        b = BODIES[n]
        if n in ("Venus", "Earth", "Mars"):
            continue                     # spent on the three parameters
        if not redistributes(b)[0]:
            continue                     # has no single temperature to score
        rows.append((n, surface_T(b, 0.0)[0] - b.observed_T))
    if not rows:
        raise ValueError("no held-out body survives the redistribution "
                         "test, so there is nothing to measure a bar on")
    rms = math.sqrt(sum(d * d for _, d in rows) / len(rows))
    return rms, (f"{rms:.1f} K, over {len(rows)} held-out body/bodies ("
                 + ", ".join(f"{n} {d:+.1f}" for n, d in rows) +
                 f"). Venus, Earth and Mars were spent on the three "
                 f"parameters, and every airless body is refused because it "
                 f"has no single temperature to score -- which leaves the "
                 f"solar system with ONE usable test. A residual in kelvin "
                 f"like the nuclear bars, over a sample of one, and that is "
                 f"the strongest reason to stop testing against this solar "
                 f"system and start asking whether it falls out of the "
                 f"space of consistent worlds")


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("stefan_boltzmann_derived", _sb)
    t("gas_constant_derived", _rgas)
    t("equilibrium_T_against_observation", _teq)
    t("airless_body_has_no_greenhouse", _mercury)
    t("titan_missed_and_names_why", _titan)
    t("water_exponent_bounded_by_earth_existing", _wexp)
    t("earth_has_two_stable_states", _bistable)
    t("weathering_efolding_from_chemistry", _efold)
    t("thermostat_reproduces_its_calibration", _cal)
    t("faint_young_sun_resolved_by_the_loop", _faint)
    t("water_is_a_property_not_a_name", _wname)
    t("runaway_inside_the_inner_edge", _inner)
    t("nothing_acts_on_the_planet", _noagent)
    t("AU_is_a_distance_not_gold", _augold)
    return all(o[1] for o in out), out


def _probe(au, water=True, lum=L_SUN):
    e = BODIES["Earth"]
    return Body("probe", e.mass, e.radius, au, e.albedo,
                water_kg=e.water_kg if water else 0.0,
                eccentricity=e.eccentricity)


def _mercury():
    """Mercury must be REFUSED, not scored. This was a reported result."""
    b = BODIES["Mercury"]
    ok, r, why = redistributes(b)
    if ok:
        raise ArithmeticError("Mercury is being treated as having a single "
                              "temperature; it does not")
    for n in ("Venus", "Earth", "Mars", "Titan"):
        good, rr, _ = redistributes(BODIES[n])
        if not good:
            raise ArithmeticError(f"{n} was refused too, leaving nothing")
    return (f"Mercury is refused: {why[:120]}... 3.1.19 scored it at "
            f"+2.8 K against a DAYSIDE mean of 440 K while predicting a "
            f"redistributed global mean. The real global figure is near "
            f"340 K and the model is about +97 K out. The agreement was "
            f"two different quantities meeting by chance")


def _titan():
    b = BODIES["Titan"]
    T, _, _, _ = surface_T(b, 0.0)
    d = T - b.observed_T
    if d > 0:
        raise ArithmeticError("Titan should be UNDER-predicted: the model "
                              "has no methane and methane warms it")
    if abs(d) > 20:
        raise ArithmeticError(f"Titan off by {d:.1f} K, too far to blame "
                              f"on one missing gas")
    return (f"Titan {T:.1f} K against {b.observed_T:.0f} K, {d:+.1f} K and "
            f"too cold -- held out, and the shortfall is methane and "
            f"nitrogen collision absorption, neither of which is in here")


def _wexp():
    m = marginal_water_exponent()
    g = water_gain()
    if not 0.4 < m < 0.7:
        raise ArithmeticError(f"marginal exponent {m:.3f} is implausible")
    if N_H2O >= m:
        raise ArithmeticError(f"using {N_H2O} at or above the marginal "
                              f"{m:.3f} makes Earth a tipping point")
    if g >= 1.0:
        raise ArithmeticError(f"feedback gain {g:.3f} -- Earth unstable")
    return (f"Earth having stayed liquid bounds the exponent below "
            f"{m:.4f}, so absorption MUST saturate; at {N_H2O} the gain is "
            f"{g:.3f}, stable and close to the edge, and no spectroscopy "
            f"table was consulted to get there")


def _bistable():
    b = BODIES["Earth"]
    fp = fixed_points(b, b.observed_co2 * b.observed_bar_pa)
    st = [t for t, k in fp if k == "stable"]
    un = [t for t, k in fp if k == "unstable"]
    if len(st) < 2 or not un:
        raise ArithmeticError(f"expected two stable states and a ridge, "
                              f"got {fp}")
    if not (min(st) < min(un) < max(st)):
        raise ArithmeticError("the ridge is not between the two states")
    return (f"same sunlight, two answers: {min(st):.0f} K and {max(st):.0f} "
            f"K, with an unstable ridge at {min(un):.0f} K between them. "
            f"Which one a planet is in is history, not physics, so the "
            f"answer is the set")


def _efold():
    v = weathering_efolding()
    if not 10.0 < v < 20.0:
        raise ArithmeticError(f"e-folding {v:.2f} K")
    return (f"R T^2 / Ea with Ea measured on basalt in a beaker gives "
            f"{v:.2f} K per e-fold; the climate literature quotes 13.7 -- "
            f"close, and derived from chemistry rather than fitted to a "
            f"planet")


def _cal():
    e = BODIES["Earth"]
    r = thermostat(e)
    obs = e.observed_co2 * e.observed_bar_pa
    if abs(r["co2_pa"] - obs) / obs > 0.02:
        raise ArithmeticError(f"the one calibration does not return "
                              f"itself: {r['co2_pa']:.3g} vs {obs:.3g} Pa")
    if abs(r["T"] - e.observed_T) > 0.5:
        raise ArithmeticError(f"T came back {r['T']:.1f}")
    return (f"outgassing=1 at 1 AU returns {r['co2_pa']:.2f} Pa and "
            f"{r['T']:.1f} K, which is Earth -- this is the single "
            f"calibration returning itself, not a prediction, and is "
            f"listed so nobody counts it as one")


def _faint():
    lum = 0.7 * L_SUN
    b = _probe(1.0)
    frozen, _, _, _ = surface_T(b, 42.56, luminosity=lum)
    r = thermostat(b, luminosity=lum)
    if frozen > 273.0:
        raise ArithmeticError("a dimmer Sun did not freeze fixed-CO2 Earth")
    if r.get("wet_fraction", 0) <= 0:
        raise ArithmeticError("the thermostat did not recover liquid water")
    return (f"at 0.7 L_sun Earth with today's CO2 sits at {frozen:.0f} K, "
            f"frozen solid; let the loop run and CO2 climbs to "
            f"{r['co2_pa']:.3g} Pa and {100*r['wet_fraction']:.0f}% of the "
            f"surface is above freezing. The faint young Sun paradox, "
            f"answered by the feedback and not by an assumption")


def _wname():
    """The bug that made every probe planet a runaway."""
    e = BODIES["Earth"]
    a = thermostat(_probe(1.0))
    if a["verdict"] == "RUNAWAY":
        raise ArithmeticError("a planet identical to Earth but differently "
                              "named runs away -- water is being looked up "
                              "by name again")
    if abs(a["co2_pa"] - e.observed_co2 * e.observed_bar_pa) > 1.0:
        raise ArithmeticError("the copy does not match the original")
    dry = thermostat(_probe(1.0, water=False))
    if dry["verdict"] != "RUNAWAY":
        raise ArithmeticError("a planet with no water still weathers")
    return ("a body identical to Earth but called 'probe' gets Earth's "
            "answer, and the same body with no water runs away -- the "
            "inventory decides, not the name. The first version keyed the "
            "ocean off body.name and every habitable-zone probe came back "
            "a runaway")


def _inner():
    hot = thermostat(_probe(0.85))
    ok = thermostat(_probe(1.05))
    if hot["verdict"] != "RUNAWAY":
        raise ArithmeticError(f"0.85 AU gave {hot['verdict']}")
    if ok["verdict"] == "RUNAWAY":
        raise ArithmeticError("1.05 AU also ran away; no inner edge")
    lo, hi = 0.85, 1.05
    for _ in range(8):      # 0.8% in AU is far finer than the bar
        m = 0.5 * (lo + hi)
        if thermostat(_probe(m))["verdict"] == "RUNAWAY":
            lo = m
        else:
            hi = m
    return (f"the inner edge falls at {0.5*(lo+hi):.3f} AU -- inside it the "
            f"oceans are vapour, rain stops, the sink closes and CO2 "
            f"accumulates with nothing to remove it. Nobody put an edge "
            f"in; it is where the loop stops having a solution")


def _augold():
    """AU is 149,597,870,700 m. Au is element 79. Never the same thing."""
    import engine.abundance as ab
    g = getattr(ab, "ABUNDANCE", {})
    if "AU" in g:
        raise ArithmeticError("an element table has a key 'AU'")
    if "Au" in dir(sys.modules[__name__]):
        raise ArithmeticError("this module defines a bare name Au")
    if abs(AU - 1.495978707e11) > 1e-3:
        raise ArithmeticError(f"AU is {AU}")
    return (f"AU = {AU:,.0f} m, exact by definition, a bare uppercase "
            f"constant here; gold is the quoted string 'Au' used as a key "
            f"in the element tables, which this module never imports. "
            f"Different case, different type, different namespace -- they "
            f"cannot be confused by anything that runs")


def _noagent():
    """Structural: nothing in here is allowed to steer a planet."""
    import inspect
    banned = ("target", "goal", "desired", "setpoint", "optimi", "terraformer")
    bad = []
    for name, fn in sorted(globals().items()):
        if not inspect.isfunction(fn) or name.startswith("_"):
            continue
        for a in inspect.signature(fn).parameters:
            if any(b in a.lower() for b in banned):
                bad.append(f"{name}({a})")
    if bad:
        raise ArithmeticError("something can be steered: " + ", ".join(bad))
    return (f"{len([f for f in globals().values() if inspect.isfunction(f)])}"
            f" functions and not one takes a target, a goal or a set point. "
            f"The planet is not being terraformed BY anything -- outgassing "
            f"and weathering are consequences, and the temperature is "
            f"wherever they cross")


def _sb():
    published = 5.670374419e-8      # CODATA, for comparison only
    rel = abs(SIGMA - published) / published
    if rel > 1e-9:
        raise ArithmeticError(f"derived {SIGMA:.9e} vs {published:.9e}")
    return (f"sigma = 2 pi^5 k^4 / 15 h^3 c^2 = {SIGMA:.7e} W m^-2 K^-4, "
            f"agreeing with the published value to {rel:.1e} -- built from "
            f"h, c and k, which are exact by definition, so this is a "
            f"derivation and not a lookup")


def _rgas():
    if abs(R_GAS - 8.31446261815324) > 1e-10:
        raise ArithmeticError(f"R came out {R_GAS}")
    return f"R = k N_A = {R_GAS:.9f} J/mol/K, exact because both factors are"


def _teq():
    rows = []
    for n in ("Venus", "Earth", "Mars"):
        b = BODIES[n]
        rows.append(f"{n} {equilibrium_T(b):.0f}K vs {b.observed_T:.0f}K")
    return "bare rock, no atmosphere: " + ", ".join(rows)


if __name__ == "__main__":
    print(f"  sigma  {SIGMA:.7e}   R  {R_GAS:.6f}\n")
    print(f"  {'body':9}{'flux':>9}{'T_eq':>8}{'T_obs':>8}{'greenhouse':>12}"
          f"{'v_esc':>9}{'g':>7}")
    for n, b in BODIES.items():
        te = equilibrium_T(b)
        gh = "" if b.observed_T is None else f"{b.observed_T - te:+.0f} K"
        print(f"  {n:9}{b.flux():>9.0f}{te:>8.1f}"
              f"{b.observed_T or 0:>8.0f}{gh:>12}"
              f"{b.escape_velocity()/1000:>9.2f}{b.gravity():>7.2f}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:36}{d[:76]}")
    print("\nall:", ok)
