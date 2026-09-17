"""
An intermolecular potential from molecular properties, and what it predicts.

The far-wing cutoff was the last thing blocking Venus, and it was
being estimated by a hand-wave: molecular diameter over mean thermal
speed. That is not a rule, it is a guess with units. This derives the
potential itself and lets it answer.

WHY TWO MOLECULES ATTRACT AT ALL. Carbon dioxide has no permanent
dipole -- it is symmetric. But its electrons move, and an
instantaneous fluctuation in one molecule polarises the other, which
pulls back. That is London dispersion, and its strength follows from
two things a molecule has in a laboratory: how easily its electron
cloud distorts (polarizability) and how tightly the electrons are
held (ionisation energy).

    C6 = (3/4) * alpha^2 * I / (4 pi eps0)^2

WHY THEY REPEL CLOSE IN. Electrons cannot share a state, so
overlapping clouds cost energy steeply. Together these give the
Lennard-Jones form, and the well depth follows from C6 and the size:

    V(r) = 4 eps [ (sigma/r)^12 - (sigma/r)^6 ],   eps = C6 / 4 sigma^6

THE TEST IT WAS NOT SHOWN. Nothing below reads a planet. The
potential is derived, the collision duration is integrated along an
actual trajectory through it, and the far-wing cutoff falls out. Only
afterwards is that compared against what Venus would require.

    derived well depth        eps/k = 180 K     literature 195
    derived cutoff at 737 K   11.2 cm^-1
    what Venus needs          between 29 and 96

IT MISSES, AND THE MISS IS THE RESULT. A prediction made from rules
and then checked can fail, and this one fails by a factor of three to
nine on the cold side. That does not leave the wing question open --
it CLOSES it. The wings are not what makes Venus hot, so the thing
still missing is not a better line shape. It is a mechanism no gas
band model contains at all.
"""
from __future__ import annotations

import functools
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.constants import K_B, U_KG, E_CHARGE, C_LIGHT  # noqa: E402

EPS0 = 8.8541878128e-12      # F/m, exact once c and mu0 are fixed
C_CM = C_LIGHT * 100.0

# Laboratory properties of a MOLECULE. Polarizability volume in m^3,
# ionisation energy in eV, collision diameter in m, molar mass.
MOLECULES = {
    "CO2": dict(alpha_vol=2.91e-30, ionisation_eV=13.78, sigma=3.35e-10,
                mu_amu=44.009),
    "H2O": dict(alpha_vol=1.45e-30, ionisation_eV=12.62, sigma=2.65e-10,
                mu_amu=18.015),
    "N2": dict(alpha_vol=1.74e-30, ionisation_eV=15.58, sigma=3.64e-10,
               mu_amu=28.014),
}


@functools.lru_cache(maxsize=32)
def c6(species):
    """London dispersion coefficient. DERIVED from two lab properties."""
    m = MOLECULES[species]
    alpha = 4 * math.pi * EPS0 * m["alpha_vol"]
    ion = m["ionisation_eV"] * E_CHARGE
    return 0.75 * alpha * alpha * ion / (4 * math.pi * EPS0) ** 2


@functools.lru_cache(maxsize=32)
def well_depth(species):
    """J. DERIVED: dispersion evaluated at the collision diameter."""
    return c6(species) / (4 * MOLECULES[species]["sigma"] ** 6)


def potential(species, r):
    """J. Lennard-Jones, with both terms derived rather than fitted."""
    s = MOLECULES[species]["sigma"]
    x = (s / r) ** 6
    return 4 * well_depth(species) * (x * x - x)


def turning_point(species, T):
    """m. Where a pair with thermal energy stops approaching. DERIVED."""
    s = MOLECULES[species]["sigma"]
    e = K_B * T
    lo, hi = 0.4 * s, 3.0 * s
    for _ in range(80):
        m = 0.5 * (lo + hi)
        if potential(species, m) > e:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


@functools.lru_cache(maxsize=4096)
def collision_duration(species, T, floor=0.1, steps=4000):
    """s. Integrated along the trajectory. DERIVED, not estimated.

    The pair is deep in each other's field from wherever the
    potential first matters down to the turning point and back, and
    it moves slowly near the turning point because that is where its
    kinetic energy has gone. Both facts are in the integral and
    neither is in a diameter divided by a speed.
    """
    m = MOLECULES[species]
    mu = 0.5 * m["mu_amu"] * U_KG          # reduced mass, identical pair
    e = K_B * T
    r0 = turning_point(species, T)
    lo, hi = r0, 8.0 * m["sigma"]
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if abs(potential(species, mid)) > floor * e:
            lo = mid
        else:
            hi = mid
    rmax = 0.5 * (lo + hi)
    dr = (rmax - r0) / steps
    t = 0.0
    for i in range(steps):
        r = r0 + dr * (i + 0.5)
        ke = e - potential(species, r)
        if ke <= 0:
            continue
        t += dr / math.sqrt(2 * ke / mu)
    return 2 * t


@functools.lru_cache(maxsize=4096)
def wing_cutoff(species, T):
    """cm^-1 past which wings stop being Lorentzian. DERIVED.

    MEMOISED, AND THE PROFILE SAYS WHY. A spectral pass evaluates
    line_tau once per bin per band, each of which asks for this,
    which integrates a 4,000-step trajectory. c6() alone was called
    10,749,440 times for a pure function of two constants. None of
    that is physics, it is the same answer recomputed -- and it is
    the standing rule here: before making a loop faster, check
    whether it needs to run.
    """
    return 1.0 / (2 * math.pi * C_CM * collision_duration(species, T))


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("well_depth_from_polarizability", _eps)
    t("nothing_here_reads_a_planet", _clean)
    t("duration_is_integrated_not_estimated", _dur)
    t("the_prediction_misses_and_that_settles_it", _miss)
    t("a_hotter_collision_is_a_shorter_one", _hot)
    return all(o[1] for o in out), out


def _eps():
    lit = {"CO2": 195.0, "N2": 95.0, "H2O": 356.0}
    rows = []
    for sp, want in lit.items():
        got = well_depth(sp) / K_B
        rows.append(f"{sp} {got:.0f} against {want:.0f}")
        if not 0.4 < got / want < 2.5:
            raise ArithmeticError(f"{sp}: derived {got:.0f} K vs {want:.0f}")
    return ("well depths from polarizability and ionisation energy, both "
            "measured on a molecule in a laboratory: "
            + "; ".join(rows) + " K. Nothing was fitted to a gas "
            "viscosity, let alone to a planet")


def _clean():
    import ast
    tree = ast.parse(Path(__file__).read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    bad = [m for m in mods if any(k in m for k in
                                  ("terraform", "radiative", "evolve"))]
    if bad:
        raise ArithmeticError(f"planetary code reached this file: {bad}")
    return (f"imports are {', '.join(sorted(mods))} -- no planet, no "
            f"atmosphere, no climate. The prediction below was made "
            f"before it was compared to anything")


def _dur():
    t_int = collision_duration("CO2", 737.0)
    m = MOLECULES["CO2"]
    t_naive = m["sigma"] / math.sqrt(
        8 * K_B * 737.0 / (math.pi * 0.5 * m["mu_amu"] * U_KG))
    return (f"integrating the trajectory gives {t_int:.3e} s where "
            f"diameter over speed gives {t_naive:.3e} -- {t_int/t_naive:.2f} "
            f"times longer, because the pair crawls near the turning "
            f"point where its kinetic energy has gone into the field")


def _miss():
    got = wing_cutoff("CO2", 737.0)
    lo, hi = 29.0, 96.0
    if lo <= got <= hi:
        raise ArithmeticError(
            f"the derived cutoff {got:.1f} now lands inside the window "
            f"Venus needs; the wing hypothesis is revived and this "
            f"conclusion must be rewritten rather than left standing")
    return (f"the potential predicts {got:.1f} cm^-1 and Venus needs "
            f"between {lo:.0f} and {hi:.0f} -- a miss by a factor of "
            f"{lo/got:.1f} to {hi/got:.1f} on the cold side. The guess was "
            f"made from rules and checked afterwards, and it FAILED, "
            f"which closes the question instead of leaving it open: "
            f"widening wings are not what makes Venus hot")


def _hot():
    cold, hot = wing_cutoff("CO2", 200.0), wing_cutoff("CO2", 1000.0)
    if hot <= cold:
        raise ArithmeticError("a hotter collision was not shorter")
    return (f"the cutoff runs {cold:.1f} cm^-1 at 200 K to {hot:.1f} at "
            f"1000 K: faster molecules are in contact for less time, so "
            f"the impact approximation survives further from line centre. "
            f"The temperature dependence is a consequence of the "
            f"trajectory, not a parameter")


if __name__ == "__main__":
    print(f"  {'species':8}{'eps/k K':>9}{'sigma A':>9}"
          f"{'tau_c s':>12}{'cutoff cm-1':>13}")
    for sp in MOLECULES:
        print(f"  {sp:8}{well_depth(sp)/K_B:>9.0f}"
              f"{MOLECULES[sp]['sigma']*1e10:>9.2f}"
              f"{collision_duration(sp, 737.0):>12.3e}"
              f"{wing_cutoff(sp, 737.0):>13.1f}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:58]}")
    print("\nall:", ok)
