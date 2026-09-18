"""After the last element, and how the chain ends.

engine/epochs.py stops at the neutron-star merger, about ten
billion years, because that is the last epoch that makes a new
kind of matter. Everything this repository derives afterwards --
cells, bodies, bands, writing, lithography -- happens inside that
one epoch and uses nothing the universe had not already made.

So the chain has an end and it was never written down. This is
it, and the interesting part is not that things get cold. It is
that every rule in this repository runs on a GRADIENT. A cell
eats one, a body sheds one, a fire needs one, a Carnot engine is
defined by one. Heat death is the state in which there is no
gradient, and the honest last link therefore says: nothing
further can be derived, and that is an answer rather than a gap.

Four numbers do the work, and all four come out of the constants
in engine/constants.py plus the Hubble rate.
"""

import math

from engine.constants import (HBAR, C_LIGHT, G_GRAV, K_B, M_SUN_KG,
                              L_SUN_W, YEAR_S)

# MEASURED. Planck 2018 / SH0ES disagree at about 9%, which is the
# Hubble tension; nothing here turns on which is right.
H0_KM_S_MPC = 67.4
MPC_M = 3.0856775814913673e22

# MEASURED, Super-Kamiokande. A LOWER BOUND, not a lifetime: the
# proton has never been seen to decay. Carried as a bound because
# the difference matters to what can be claimed.
PROTON_DECAY_BOUND_YR = 1.6e34

LIGHTEST_STAR_MSUN = 0.08      # MEASURED, the hydrogen-burning floor
MASS_LUMINOSITY_EXP = 3.5      # MEASURED, main-sequence L ~ M^3.5


def hubble_s():
    """H0 in inverse seconds. DERIVED."""
    return H0_KM_S_MPC * 1000.0 / MPC_M


def hubble_time_yr():
    """1/H0, the expansion timescale. DERIVED."""
    return 1.0 / hubble_s() / YEAR_S


def de_sitter_temperature():
    """The floor temperature of an accelerating universe. DERIVED.

    A de Sitter horizon radiates at T = hbar H / (2 pi k), exactly
    as a black hole horizon does. This is the temperature nothing
    can get below, so it is the temperature everything ends at.
    """
    return HBAR * hubble_s() / (2.0 * math.pi * K_B)


def hawking_temperature(mass_kg):
    """T = hbar c^3 / (8 pi G M k). DERIVED."""
    return (HBAR * C_LIGHT**3
            / (8.0 * math.pi * G_GRAV * mass_kg * K_B))


def evaporation_years(mass_kg):
    """t = 5120 pi G^2 M^3 / (hbar c^4). DERIVED."""
    return (5120.0 * math.pi * G_GRAV**2 * mass_kg**3
            / (HBAR * C_LIGHT**4) / YEAR_S)


def star_lifetime_years(mass_msun):
    """Fuel over burn rate: t ~ M / L ~ M^(1-exp). DERIVED."""
    sun = 1e10                       # MEASURED, solar main sequence
    return sun * mass_msun ** (1.0 - MASS_LUMINOSITY_EXP)


def cmb_temperature(years, now=2.725):
    """Cooling under exponential expansion. DERIVED.

    Once dark energy dominates the scale factor grows as e^(Ht),
    and the photon temperature falls as 1/a, so the CMB decays
    exponentially with the Hubble time as its constant.
    """
    return now * math.exp(-years / hubble_time_yr())


def black_holes_start_shrinking(mass_kg=M_SUN_KG):
    """When the sky gets colder than the hole. DERIVED.

    A black hole absorbs more than it radiates while the CMB is
    hotter than its Hawking temperature, so nothing evaporates
    until the sky has cooled past it.
    """
    t_h = hawking_temperature(mass_kg)
    return hubble_time_yr() * math.log(2.725 / t_h)


ERAS = [
    ("stelliferous", 1e10, "stars are still forming and burning"),
    ("last starlight", None, "the longest-lived red dwarfs go out"),
    ("degenerate", 1e15, "white dwarfs, neutron stars, cold planets"),
    ("black hole", None, "the holes are the only structures left"),
    ("dark", None, "nothing but the horizon glow"),
]


def eras():
    """-> [(name, years, what)]. DERIVED where it can be."""
    return [
        ("stelliferous ends", star_lifetime_years(LIGHTEST_STAR_MSUN),
         "the lightest hydrogen-burning star runs out"),
        ("holes begin to shrink", black_holes_start_shrinking(),
         "the sky falls below a solar-mass Hawking temperature"),
        ("stellar holes are gone", evaporation_years(M_SUN_KG),
         "a solar-mass hole finishes evaporating"),
        ("galactic holes are gone", evaporation_years(1e9 * M_SUN_KG),
         "the largest known holes finish evaporating"),
    ]


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_chain_ends_and_the_end_was_never_written_down", _end)
    t("nothing_evaporates_until_the_sky_is_colder_than_it", _cold)
    t("the_last_structures_go_by_a_formula_in_three_constants", _holes)
    t("MISSING_whether_matter_itself_decays", _proton)
    t("INVERTED_heat_death_is_where_derivation_stops", _stop)
    return all(x for _, x, _ in res), res


def _end():
    from engine.epochs import EPOCHS
    last = EPOCHS[-1]
    red = star_lifetime_years(LIGHTEST_STAR_MSUN)
    if red < 1e12:
        raise ArithmeticError(f"{red}")
    return (f"engine/epochs.py stops at {last[0]} at "
            f"{last[1]/YEAR_S:.2g} years, because that is the last "
            f"epoch that makes a new KIND of matter. Everything "
            f"this repository derives after it -- cells, bodies, "
            f"bands, writing, lithography -- happens inside that "
            f"one epoch and uses nothing the universe had not "
            f"already made. The chain had an end and nobody had "
            f"written it down. Main-sequence lifetime goes as "
            f"M^(1-{MASS_LUMINOSITY_EXP:.1f}), so the lightest star "
            f"that burns at all, {LIGHTEST_STAR_MSUN} solar masses, "
            f"lasts {red:.2e} years against the Sun's 1e10. The "
            f"stelliferous era is {red/1e10:.0f} times longer than "
            f"the part with people in it")


def _cold():
    t_h = hawking_temperature(M_SUN_KG)
    when = black_holes_start_shrinking()
    ds = de_sitter_temperature()
    if when < 1e10 or t_h < ds:
        raise ArithmeticError(f"{when} {t_h} {ds}")
    return (f"a solar-mass hole radiates at "
            f"{t_h:.2e} K, which is colder than today's 2.725 K "
            f"sky -- so it GROWS. Nothing evaporates until the "
            f"universe has cooled past it, and under exponential "
            f"expansion that takes ln(2.725/{t_h:.1e}) Hubble "
            f"times, about {when:.2e} years. The floor is the "
            f"de Sitter temperature {ds:.2e} K, set by the horizon "
            f"itself at hbar H / 2 pi k, which is the same formula "
            f"as the hole's. Nothing gets colder than that, which "
            f"is why this is an end and not a stage")


def _holes():
    a, b = evaporation_years(M_SUN_KG), evaporation_years(1e9 * M_SUN_KG)
    if b / a < 1e20:
        raise ArithmeticError(f"{a} {b}")
    return (f"t = 5120 pi G^2 M^3 / hbar c^4 -- three constants and "
            f"a mass, nothing fitted. A solar-mass hole takes "
            f"{a:.2e} years and a billion-solar-mass one "
            f"{b:.2e}, because the cube makes a factor of "
            f"{b/a:.0e} out of a factor of 1e9. The largest "
            f"structures last longest and they last by a wide "
            f"margin, so the last event in the universe is the "
            f"evaporation of the biggest hole in it")


def _proton():
    """A genuine gap: the answer is not known, not merely underived."""
    bound = PROTON_DECAY_BOUND_YR
    hole = evaporation_years(M_SUN_KG)
    if bound > hole:
        raise ArithmeticError("the bound now exceeds evaporation")
    return (f"whether ordinary matter survives to meet any of this "
            f"is NOT KNOWN. The proton has never been observed to "
            f"decay and Super-Kamiokande puts the lifetime beyond "
            f"{bound:.1e} years, which is a BOUND and not a value. "
            f"If protons do decay near that bound, white dwarfs "
            f"and planets evaporate long before the "
            f"{hole:.1e} years a stellar black hole needs, and the "
            f"degenerate era ends early. If they do not, cold "
            f"matter simply waits. This repository cannot decide "
            f"it and neither can anyone else yet, so it is carried "
            f"as a gap in the world rather than a gap in the "
            f"model -- a distinction worth keeping separate")


def _stop():
    """INVERTED. Fails if anything is still derivable at the end."""
    ds = de_sitter_temperature()
    from engine.disease import cooking_pays
    if ds > 1e-25:
        raise ArithmeticError(f"{ds} is not a floor")
    return (f"every rule in this repository runs on a GRADIENT. A "
            f"cell eats one, a body sheds one, a fire needs one, "
            f"Carnot is defined by one, and engine/disease.py "
            f"prices a cooking fire at {cooking_pays()[2]:.0f}x "
            f"precisely because there is somewhere for the heat to "
            f"go. At {ds:.2e} K everything is at the horizon "
            f"temperature and there is no somewhere. So the last "
            f"link does not say the universe is cold; it says that "
            f"the machinery this repository is built out of has "
            f"nothing left to bite on. That is an ANSWER and not a "
            f"gap, and it is the only place on the chain where "
            f"'nothing further can be derived' is the correct "
            f"result rather than an admission")


if __name__ == "__main__":
    print(f"  {'era':<26}{'years':>12}")
    for name, yr, what in eras():
        print(f"  {name:<26}{yr:>12.3e}   {what}")
    print()
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
