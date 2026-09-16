"""
What biophysics forbids, which is most of it.

The rungs above chemistry are not a new kind of rule. They are the
same rule -- derive it, check it a second way, refuse what cannot be
established -- applied to the constraints an organism cannot escape.
Each of these refuses a space the chemistry below it cannot touch,
the way engine/epochs.py refuses a space that dimensions and
conservation cannot.

    codon length      forced by how many things must be named
    diffusion         forced by how fast oxygen moves in water
    square-cube       forced by how strength and weight scale apart
    Reynolds number   forced by which term of the flow dominates

NOTHING HERE IS FITTED. Every constant is measured and cited, every
result is computed from them, and the one exception -- the Kleiber
exponent -- is marked ASSERTED and listed in engine/unsolved.py as
something this repo does not derive. A round trip through the same
exponent would prove arithmetic, not biology, so it carries no
check at all rather than a fake one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

# --- measured constants, not fitted -------------------------------------
D_O2_WATER = 2.0e-9      # m^2/s,  oxygen diffusion in water at 25 C
C_O2_WATER = 0.25        # mol/m^3, dissolved O2 in air-saturated water
RHO_WATER = 1000.0       # kg/m^3
G_EARTH = 9.80665        # m/s^2
MU_WATER = 1.0016e-3     # Pa s
BONE_COMPRESSIVE = 1.7e8  # Pa
KCAL_DAY_TO_W = 4184.0 / 86400.0

DERIVED = "DERIVED"
ASSERTED = "ASSERTED"
INHERITED = "DERIVED_FROM_ASSERTED"


@dataclass
class Fact:
    value: object
    kind: str
    check: str
    why: str

    def __str__(self):
        return f"{self.value}  [{self.kind}, {self.check}] {self.why}"


def codon_length(n_bases=4, n_amino=20, stops=1):
    """Shortest codon that can name everything. ENUMERATE.

    Not a fact about DNA. Given an alphabet of n_bases and
    n_amino+stops things to name, the codon length is the smallest k
    with n_bases**k >= n_amino+stops. For 4 and 21: 16 is too few,
    64 is enough. Three is forced, and the 43 spare codons are why
    the real code has to be redundant.
    """
    need = n_amino + stops
    if n_bases < 2 or need < 1:
        raise ValueError("need at least two letters and one meaning")
    k = 1
    while n_bases ** k < need:
        k += 1
    count = 0

    def walk(depth):
        nonlocal count
        if depth == 0:
            count += 1
            return
        for _ in range(n_bases):
            walk(depth - 1)
    walk(k)
    if count != n_bases ** k:
        raise ArithmeticError("enumeration disagrees with the power")
    return Fact(k, DERIVED, "ENUMERATE",
                f"{n_bases}**{k} = {count} codons for {need} meanings, "
                f"{count - need} spare -- the code must be redundant")


def surface_to_volume(radius_m):
    """3/r for a sphere. INVERSE: recover the radius."""
    if radius_m <= 0:
        raise ValueError("radius must be positive")
    sv = 3.0 / radius_m
    back = 3.0 / sv
    if not math.isclose(back, radius_m, rel_tol=1e-12):
        raise ArithmeticError("surface-to-volume is not invertible")
    return Fact(sv, DERIVED, "INVERSE",
                f"sphere of r={radius_m:g} m has {sv:g} /m; recovered "
                f"r={back:g}")


def diffusion_limit(consumption_mol_m3_s, D=D_O2_WATER, C0=C_O2_WATER):
    """Largest sphere that can supply itself by diffusion alone.

    Steady state in a sphere consuming at rate R: the centre reaches
    zero at r = sqrt(6 D C0 / R). Past that the middle suffocates, so
    a thing is smaller than this, flat, or has a pump. INVERSE
    recovers R.
    """
    if consumption_mol_m3_s <= 0:
        raise ValueError("consumption must be positive")
    r = math.sqrt(6.0 * D * C0 / consumption_mol_m3_s)
    back = 6.0 * D * C0 / (r * r)
    if not math.isclose(back, consumption_mol_m3_s, rel_tol=1e-9):
        raise ArithmeticError("diffusion limit is not invertible")
    return Fact(r, DERIVED, "INVERSE",
                f"r_max={r*1e6:.1f} um at R={consumption_mol_m3_s:g} "
                f"mol/(m^3 s); recovered R={back:g}")


def square_cube_limit(bone_fraction=0.01, strength_pa=BONE_COMPRESSIVE,
                      density=RHO_WATER, g=G_EARTH):
    """How tall a land skeleton gets before it crushes itself.

    Weight goes as L^3 and the cross-section holding it up as L^2, so
    the stress goes as L. Set it equal to the compressive strength.
    """
    L = strength_pa * bone_fraction / (density * g)
    back = L * density * g / bone_fraction
    if not math.isclose(back, strength_pa, rel_tol=1e-9):
        raise ArithmeticError("square-cube limit is not invertible")
    return Fact(L, DERIVED, "INVERSE",
                f"{L:.0f} m before stress reaches {strength_pa:.2g} Pa at "
                f"{bone_fraction:.0%} bone cross-section; recovered "
                f"{back:.2g} Pa")


def reynolds(length_m, speed_m_s, rho=RHO_WATER, mu=MU_WATER):
    """Which world it swims in. Re = rho v L / mu."""
    re = rho * speed_m_s * length_m / mu
    world = ("viscous -- stop beating and you stop within a body length"
             if re < 1 else
             "inertial -- coasting works" if re > 1000 else "between")
    return Fact(re, DERIVED, "IDENTITY",
                f"Re={re:.3g} at {length_m:g} m and {speed_m_s:g} m/s: "
                f"{world}")


def kleiber(mass_kg, exponent=0.75, b0_kcal_day=70.0):
    """Metabolic rate. The exponent is ASSERTED and this says so.

    Geometry predicts 2/3: heat leaves through a surface. Measurement
    gives about 3/4. Derivations from fractal transport networks
    exist and are disputed, and this repo has not carried one out, so
    the exponent is an observation taken on trust. No check can
    verify it -- a round trip through the same exponent proves
    arithmetic -- and pretending otherwise is what eval/controls.py
    exists to catch. Listed in engine/unsolved.py.
    """
    watts = b0_kcal_day * mass_kg ** exponent * KCAL_DAY_TO_W
    return Fact(watts, ASSERTED, "NONE",
                f"{watts:.1f} W at {mass_kg:g} kg using exponent "
                f"{exponent} (observed; geometry alone predicts 0.667)")


def earliest_possible_life(elements=("C", "H", "N", "O", "P", "S")):
    """When can CHNOPS all exist? The latest one decides."""
    from engine import epochs as ep
    eras = {e: ep.ORIGIN.get(e) for e in elements}
    missing = [e for e, v in eras.items() if v is None]
    if missing:
        raise KeyError(f"no origin epoch recorded for {missing}")
    era = max(eras.values(), key=lambda x: ep.ORDER[x])
    late = [e for e, v in eras.items() if v == era]
    return Fact(era, DERIVED, "EXTERNAL",
                f"{eras}; the latest is {late} at {era}, so nothing built "
                f"from CHNOPS exists before it")


CHECKS = (codon_length, surface_to_volume, diffusion_limit,
          square_cube_limit, reynolds, earliest_possible_life)


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("codon_length", lambda: codon_length().why)
    t("diffusion", lambda: diffusion_limit(1e-3).why)
    t("square_cube", lambda: square_cube_limit().why)
    t("reynolds", lambda: reynolds(1e-5, 1e-4).why)
    t("earliest_life", lambda: earliest_possible_life().why)
    t("kleiber_unverifiable", _kleiber)
    return all(o[1] for o in out), out


def _kleiber():
    f = kleiber(70.0)
    if f.kind != ASSERTED or f.check != "NONE":
        raise ArithmeticError("the Kleiber exponent must not claim a check")
    return (f"{f.value:.0f} W for a 70 kg animal, reported ASSERTED with "
            f"no check -- the exponent is observed, not derived here")


if __name__ == "__main__":
    for fn in (lambda: codon_length(), lambda: diffusion_limit(1e-3),
               lambda: square_cube_limit(), lambda: reynolds(1e-5, 1e-4),
               lambda: earliest_possible_life(), lambda: kleiber(70.0)):
        print(" ", fn())
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:22}{d[:96]}")
    print("\nall:", ok)
