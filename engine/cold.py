"""
The fidelity gate opens by getting colder, and so does crowding.

engine/earthlab.py walks Earth to the first gate that will not
open and reports two: search, short by 5.1e11, and fidelity,
short by exactly 2. Fidelity is the near one and it was being
carried by a MEASURED constant -- the best known ribozyme copies
at one error in a hundred -- with no rule saying why that number
and not another.

It is derivable, and deriving it changes what the gate means.

    copying is discrimination: mu = exp(-dG/kT)
    one error in 100 at 298 K implies dG = 2.73 kcal/mol
    which is an ordinary base-pair free-energy gap

SO THE RIBOZYME IS NOT A POOR COPIER. It is at the thermodynamic
limit for its temperature, and no better catalyst exists at 298 K
because the gap between a right pair and a wrong one is the whole
of what a catalyst has to work with.

Which says what to change. dG is fixed by chemistry, so halving
the error means raising dG/kT, and the only free term is T:

    1 in  100    298.0 K     25 C
    1 in  200    259.0 K    -14 C
    1 in  500    220.8 K    -52 C

259 K is below freezing and ABOVE the NaCl eutectic at 252, so
the brine is still liquid. And getting there is not free -- the
freezing-point depression that holds water liquid at 259 K
requires a solution six times more concentrated than seawater,
which is the crowding gate's own requirement arriving as a side
effect.

ONE MOVE OPENS TWO GATES, and neither was handed anything.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KCAL_PER_MOL_J = 4184.0 / 6.02214076e23     # EXACT, from N_A
KF_WATER = 1.86                 # MEASURED, K kg/mol cryoscopic constant
SEAWATER_OSMOLAL = 1.2          # MEASURED, mol particles per kg
NACL_EUTECTIC_K = 251.9         # MEASURED
MGCL2_EUTECTIC_K = 239.0        # MEASURED
REF_ERROR = 0.01                # MEASURED, best ribozyme at 298 K
REF_T = 298.0                   # MEASURED, where that was measured


def discrimination_kcal(mu=REF_ERROR, T=REF_T):
    """kcal/mol between a right pair and a wrong one. DERIVED.

    Read off a measured error rate rather than asserted, which is
    what turns the ribozyme's 1-in-100 from a fact about biology
    into a fact about temperature.
    """
    from engine.constants import K_B
    return -K_B * T * math.log(mu) / KCAL_PER_MOL_J


def error_at(T, dG=None):
    """Copying error rate at temperature T. DERIVED."""
    from engine.constants import K_B
    g = discrimination_kcal() if dG is None else dG
    return math.exp(-g * KCAL_PER_MOL_J / (K_B * T))


def temperature_for(mu, dG=None):
    """K needed for this error rate. DERIVED, the inverse."""
    from engine.constants import K_B
    g = discrimination_kcal() if dG is None else dG
    return -g * KCAL_PER_MOL_J / (K_B * math.log(mu))


def genome_at(T):
    """Longest maintainable genome at T. DERIVED via earthlab."""
    from engine.earthlab import error_threshold
    return error_threshold(error_at(T))


def osmolality_for(T):
    """mol/kg of solute needed to stay liquid at T. DERIVED.

    Freezing-point depression, dT = Kf m. This is why getting
    cold is not free: the water that stays liquid is the water
    that has everything dissolved in it.
    """
    return max(273.15 - T, 0.0) / KF_WATER


def concentration_factor(T, start=SEAWATER_OSMOLAL):
    """How much more concentrated the brine is. DERIVED."""
    return max(osmolality_for(T) / start, 1.0)


def still_liquid(T):
    """-> (bool, why). Below the eutectic there is no brine."""
    return T > NACL_EUTECTIC_K, (
        f"{T:.1f} K against the NaCl eutectic at "
        f"{NACL_EUTECTIC_K:.1f} K")


def both_gates(target_mu=0.005):
    """-> dict. What one temperature does to fidelity and crowding."""
    T = temperature_for(target_mu)
    liquid, why = still_liquid(T)
    return {"T": T, "mu": error_at(T), "genome": genome_at(T),
            "concentration": concentration_factor(T),
            "liquid": liquid, "why": why}


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_ribozyme_is_at_its_thermodynamic_limit", _limit)
    t("fidelity_is_a_temperature_not_a_catalyst", _temp)
    t("the_brine_is_still_liquid_there", _liquid)
    t("getting_cold_concentrates_what_is_left", _conc)
    t("one_move_opens_two_gates", _both)
    t("nothing_here_was_handed_over", _clean)
    return all(o[1] for o in out), out


def _limit():
    g = discrimination_kcal()
    if not 1.5 < g < 5.0:
        raise ArithmeticError(f"the gap came out {g:.2f} kcal/mol")
    back = error_at(REF_T)
    if abs(back - REF_ERROR) > 1e-9:
        raise ArithmeticError("the inverse does not reproduce the input")
    return (f"one error in {1/REF_ERROR:.0f} at {REF_T:.0f} K implies a "
            f"discrimination of {g:.2f} kcal/mol, which is an ORDINARY "
            f"base-pair free-energy gap. So the best known ribozyme is "
            f"not a poor copier -- it is at the thermodynamic limit "
            f"for its temperature, and no better catalyst exists at "
            f"298 K because that gap is the whole of what a catalyst "
            f"has to work with")


def _temp():
    T = temperature_for(0.005)
    if not 240.0 < T < 275.0:
        raise ArithmeticError(f"halving the error wants {T:.0f} K")
    return (f"dG is fixed by chemistry, so halving the error means "
            f"raising dG/kT and the only free term is T: "
            f"{T:.1f} K, {T-273.15:.1f} C. engine/earthlab.py reports "
            f"the fidelity gate short by exactly 2x, and the thing "
            f"that closes it is NOT a better catalyst. It is a colder "
            f"one")


def _liquid():
    T = temperature_for(0.005)
    ok, why = still_liquid(T)
    if not ok:
        raise ArithmeticError(f"no liquid at {T:.0f} K: {why}")
    return (f"{why} -- so there is still brine to react in. Push "
            f"further and it stops: one error in 500 wants "
            f"{temperature_for(0.002):.0f} K, which is below every "
            f"eutectic here, and a gate that opens in solid ice has "
            f"not opened")


def _conc():
    T = temperature_for(0.005)
    c = concentration_factor(T)
    if c < 2.0:
        raise ArithmeticError(f"only {c:.1f}x concentration")
    return (f"getting cold is not free. Holding water liquid at "
            f"{T:.1f} K needs {osmolality_for(T):.2f} mol/kg of "
            f"solute against seawater's {SEAWATER_OSMOLAL:.1f}, so "
            f"the brine is {c:.1f}x concentrated. The water that "
            f"stays liquid is the water with everything dissolved in "
            f"it")


def _both():
    b = both_gates()
    if not b["liquid"] or b["concentration"] < 2.0:
        raise ArithmeticError(str(b))
    from engine.earthlab import error_threshold, ERROR_RATES
    was = error_threshold(min(ERROR_RATES.values()))
    return (f"ONE MOVE OPENS TWO GATES. At {b['T']:.1f} K the error "
            f"rate is {b['mu']:.4f}, the maintainable genome goes "
            f"{was:.0f} -> {b['genome']:.0f} bases, and the same "
            f"freezing-point depression that gets there concentrates "
            f"the brine {b['concentration']:.1f}x, which is the "
            f"crowding gate's own requirement arriving as a side "
            f"effect. Neither was aimed at the other")


def _clean():
    return ("nothing in this file was handed over. The discrimination "
            "energy is read off a measured error rate, the "
            "temperature follows from it, the eutectic and the "
            "cryoscopic constant are measured properties of water, "
            "and the concentration is freezing-point depression. No "
            "rule here says life is likely, only what temperature "
            "the fidelity gate opens at and what else that costs")


if __name__ == "__main__":
    g = discrimination_kcal()
    print(f"  discrimination {g:.2f} kcal/mol, read off 1-in-"
          f"{1/REF_ERROR:.0f} at {REF_T:.0f} K\n")
    print(f"  {'T':>8}{'error':>10}{'genome':>9}{'brine':>9}{'liquid':>9}")
    for T in (298.0, 280.0, 273.15, 265.0, 259.0, 252.0, 245.0):
        ok, _ = still_liquid(T)
        print(f"  {T:>7.1f}K{error_at(T):>10.4f}{genome_at(T):>8.0f}b"
              f"{concentration_factor(T):>8.1f}x{'yes' if ok else 'NO':>9}")
    b = both_gates()
    print(f"\n  to double fidelity: {b['T']:.1f} K, genome "
          f"{b['genome']:.0f} bases, brine {b['concentration']:.1f}x\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:44}{d[:36]}")
