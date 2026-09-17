"""
One definition each. Nothing in this repo may define a constant twice.

A sweep for physical constants defined in more than one module found
four quantities carrying two or three independent definitions:

    atomic mass unit   AMU (terraform)      U_KG (cosmoschunks, halflife)
    Newton's constant  G_GRAV (terraform)   G_NEWTON (remnants)
    solar mass         M_SUN (remnants)     M_SUN_KG (cosmoschunks, halflife)
    alpha binding      B_ALPHA (transitions) B_ALPHA_MEV (nucleo)

EVERY ONE OF THEM AGREED. That is exactly what makes it worth fixing.
Nothing enforced the agreement, so it held by luck and by whoever
typed the second copy being careful. A later edit to one of them
would have produced two modules quietly disagreeing about the mass
of the Sun, and the answers would still have looked reasonable.

THE FIX IS A RULE, NOT A SYNC. Setting the copies equal is a patch:
it fixes today's values and leaves the mechanism that allowed the
divergence in place. The rule is that a physical constant has one
home, every module imports it, and a lab experiment fails if a
second definition appears anywhere. That cannot drift, because
drifting requires writing a duplicate and the duplicate is what is
forbidden.

TWO KINDS OF NUMBER LIVE HERE AND THEY ARE MARKED.

  EXACT     fixed by definition in the SI since 2019. The second, the
            metre, the kilogram, the kelvin and the mole are defined
            by fixing these, so they have no uncertainty at all and
            never will. Deriving one from the others is arithmetic.

  MEASURED  someone went and found out, and could be wrong. G is the
            worst-known constant in physics at about 22 parts per
            million -- five orders of magnitude worse than anything
            marked exact -- and any result resting on it inherits
            that.

A derived quantity is NOT stored here. If it can be computed it is
computed where it is used, so there is no second place for it to go
stale. That is why Stefan-Boltzmann is absent: it is 2 pi^5 k^4 /
15 h^3 c^2 and lives in the module that needs it.
"""
from __future__ import annotations

EXACT, MEASURED = "EXACT", "MEASURED"

# ------------------------------------------------- exact by definition
H_PLANCK = 6.62607015e-34      # J s      defines the kilogram
C_LIGHT = 299792458.0          # m/s      defines the metre
K_B = 1.380649e-23             # J/K      defines the kelvin
N_A = 6.02214076e23            # 1/mol    defines the mole
E_CHARGE = 1.602176634e-19     # C        defines the ampere
AU_M = 1.495978707e11          # m        defined exactly, IAU 2012

# ------------------------------------------------------------ measured
G_GRAV = 6.67430e-11           # m^3 kg^-1 s^-2   +/- 22 ppm, the worst
U_KG = 1.66053906660e-27       # kg               atomic mass unit
M_SUN_KG = 1.98847e30          # kg
L_SUN_W = 3.828e26             # W
YEAR_S = 3.155693e7            # s                Julian year
B_ALPHA_MEV = 28.296           # MeV              binding of helium-4

# Derived, not stored as data: hbar is h over two pi. It lived as a
# typed 1.054571817e-34 in engine/remnants.py, which is a second home
# for a number that can be computed -- the same defect as the four
# duplicated constants above, caught by the rule that forbids a typed
# error bar because "HBAR" contains "BAR".
import math as _math
HBAR = H_PLANCK / (2 * _math.pi)

PROVENANCE = {
    "H_PLANCK": (EXACT, "defines the kilogram"),
    "HBAR": (EXACT, "h over two pi; derived here, never stored"),
    "C_LIGHT": (EXACT, "defines the metre"),
    "K_B": (EXACT, "defines the kelvin"),
    "N_A": (EXACT, "defines the mole"),
    "E_CHARGE": (EXACT, "defines the ampere"),
    "AU_M": (EXACT, "defined exactly by the IAU in 2012"),
    "G_GRAV": (MEASURED, "+/- 22 ppm, the least well known constant "
                         "in physics; anything resting on it inherits that"),
    "U_KG": (MEASURED, "atomic mass unit, one twelfth of a carbon-12 atom"),
    "M_SUN_KG": (MEASURED, "solar mass"),
    "L_SUN_W": (MEASURED, "solar luminosity"),
    "YEAR_S": (MEASURED, "Julian year in seconds"),
    "B_ALPHA_MEV": (MEASURED, "binding energy of helium-4"),
}

# Names other modules historically used for these. A duplicate under
# any of them is the same clash wearing a different hat.
ALIASES = {
    "AMU": "U_KG", "G_NEWTON": "G_GRAV", "M_SUN": "M_SUN_KG",
    "B_ALPHA": "B_ALPHA_MEV", "L_SUN": "L_SUN_W", "AU": "AU_M",
}


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("every_constant_has_provenance", _prov)
    t("no_constant_is_defined_twice", _dupes)
    t("exact_constants_reproduce_derived_ones", _derive)
    return all(o[1] for o in out), out


def _prov():
    import sys as _s
    me = _s.modules[__name__]
    names = [n for n in dir(me)
             if n.isupper() and isinstance(getattr(me, n), float)]
    missing = [n for n in names if n not in PROVENANCE]
    if missing:
        raise ArithmeticError(f"no provenance for {missing}")
    ex = sum(1 for n in names if PROVENANCE[n][0] == EXACT)
    return (f"{len(names)} constants, {ex} exact by definition and "
            f"{len(names)-ex} measured, and every one says which -- an "
            f"exact constant has no error to propagate and a measured one "
            f"does, so the distinction has to survive into the answer")


def _dupes():
    """THE RULE: a constant has one home. Scans every engine module."""
    import re
    from pathlib import Path
    here = Path(__file__).resolve()
    owned = set(PROVENANCE) | set(ALIASES)
    pat = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=\s*[-+]?[0-9]", re.M)
    bad = []
    for f in sorted(here.parent.glob("*.py")):
        if f == here:
            continue
        for m in pat.finditer(f.read_text()):
            if m.group(1) in owned:
                bad.append(f"{m.group(1)} in {f.name}")
    if bad:
        raise ArithmeticError(
            "a physical constant is defined outside its one home: "
            + ", ".join(bad) + ". Setting the copies equal would be a "
            "patch; importing them is the fix, because a duplicate "
            "cannot drift if a duplicate cannot exist")
    return (f"{len(owned)} owned names including {len(ALIASES)} historical "
            f"aliases, and not one is redefined in any other engine "
            f"module. Four quantities used to carry two or three "
            f"definitions each -- all of them agreeing, which is what "
            f"made it dangerous")


def _derive():
    import math
    sigma = (2 * math.pi ** 5 * K_B ** 4) / (15 * H_PLANCK ** 3
                                             * C_LIGHT ** 2)
    r_gas = K_B * N_A
    ok = (abs(sigma - 5.670374419e-8) / 5.670374419e-8 < 1e-9
          and abs(r_gas - 8.31446261815324) < 1e-10)
    if not ok:
        raise ArithmeticError(f"sigma={sigma:.6e} R={r_gas:.9f}")
    return (f"Stefan-Boltzmann and the gas constant both fall out of the "
            f"exact four: sigma={sigma:.7e}, R={r_gas:.9f}. Neither is "
            f"stored here, because a number that can be computed has no "
            f"business having a second home to go stale in")


if __name__ == "__main__":
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:70]}")
    print("\nall:", ok)
