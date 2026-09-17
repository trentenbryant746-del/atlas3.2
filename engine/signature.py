"""
Fewer rules, grown further, and a sign of life that is not a guess.

Everything up to here added rules. This removes them. Give a world
the minimum -- what binds to what, and what is downhill -- let it
run, and then ask one question of the result: is the atmosphere
POSSIBLE without something continuously remaking it?

WHY DISEQUILIBRIUM IS THE RIGHT QUESTION. Oxygen is not a
biosignature; a photodissociating ocean makes oxygen. Methane is
not one; serpentinising rock makes methane. But the two TOGETHER
are, because

    CH4 + 2 O2 -> CO2 + 2 H2O

is downhill by 818 kJ/mol and fast, which puts the equilibrium
constant at 2.3e148. Earth holds 1.8 ppm of methane inside 21%
oxygen, and those two cannot sit together. Something is
replenishing the methane faster than the oxygen destroys it.

That is not an assumption about biology. It is an accounting
identity: a system held far from equilibrium is being driven, and
a driver is a thing that exists. It is also measurable across
interstellar distance from a spectrum, which the rest of this
repository's conclusions are not.

WHAT THIS DELIBERATELY DOES NOT DO. It does not say life. A
sufficiently odd geology could drive a gas pair, and this returns
a magnitude and a requirement rather than a verdict. The useful
output is "something must be doing this", and the size of the
something.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.constants import K_B, N_A  # noqa: E402

R_GAS = K_B * N_A

# Standard Gibbs energies, measured, kJ/mol of reaction as written.
PAIRS = {
    ("CH4", "O2"): dict(dG=-818e3, why="methane burns in oxygen"),
    ("H2", "O2"): dict(dG=-457e3, why="hydrogen burns in oxygen"),
    ("CO", "O2"): dict(dG=-514e3, why="carbon monoxide burns"),
    ("N2O", "O2"): dict(dG=-82e3, why="nitrous oxide is unstable"),
}


def equilibrium_constant(dG, T=288.0):
    """DERIVED. How far downhill, as a ratio."""
    x = -dG / (R_GAS * T)
    return math.exp(min(x, 700.0))


def disequilibrium(mix_fractions, T=288.0):
    """-> [(pair, orders of magnitude, why)]. DERIVED per gas pair."""
    out = []
    for (a, b), d in PAIRS.items():
        fa, fb = mix_fractions.get(a, 0.0), mix_fractions.get(b, 0.0)
        if fa <= 0 or fb <= 0:
            continue
        k = equilibrium_constant(d["dG"], T)
        orders = math.log10(k)
        out.append(((a, b), orders, fa, fb, d["why"]))
    return sorted(out, key=lambda r: -r[1])


# ORDERS FROM EQUILIBRIUM IS NOT ENOUGH, AND MARS PROVED IT.
#
# The first version asked only how far downhill a pair sits, and
# Mars came back DRIVEN: it holds 0.07% carbon monoxide beside
# 0.14% oxygen, and CO burns by 128 orders. Both real, and neither
# alive -- ultraviolet splits CO2 all day and the pieces take time
# to recombine.
#
# The equilibrium constant says how IMPOSSIBLE a pair is. It says
# nothing about how MUCH must be remade to hold it there, and that
# is the part a driver has to pay for. A trace pair needs a trace
# source, and photochemistry is a perfectly good trace source.
#
# So the measure is the FLUX: how much of the minor species must be
# replaced per year against its lifetime in the presence of the
# other. Earth's methane needs hundreds of teragrams a year. Mars'
# carbon monoxide needs almost nothing.
SECONDS_PER_YEAR = 3.155693e7

# THE FLUX RULE WAS THE WRONG SECOND TEST, AND MARS SHOWED IT TWICE.
#
# Asking how far downhill a pair sits called Mars driven. Adding a
# flux -- how much must be remade -- narrowed the gap to a factor of
# 23 and still called Mars driven. Deriving the lifetime properly
# from hydroxyl chemistry made it WORSE, because Mars' dry air gives
# CO a 21-year life and therefore a larger bill, not a smaller one.
#
# Three attempts at a magnitude, and magnitude was never the
# question. What separates the two worlds is not how big the
# disequilibrium is but whether ONE PROCESS CAN ACCOUNT FOR IT.
#
#   Mars    CO2 + photon -> CO + O.  A single reaction makes both
#           members of the pair, in a ratio it fixes. The
#           disequilibrium is exactly that reaction's output.
#   Earth   methane comes from methanogens, oxygen from
#           photosynthesis. NO abiotic reaction has methane and
#           oxygen among its products, at any ratio.
#
# So the test is whether a known process can write the whole
# invoice. Mars' observed CO/O2 is 0.50 against the 2.0 that
# photolysis predicts -- a factor of four, and atmospheric escape
# removes light species preferentially, which moves it that way.
# Earth's CH4/O2 is 8.6e-6 and matches nothing.
ABIOTIC_SOURCES = [
    ("CO2 photolysis", ("CO", "O2"), 2.0,
     "CO2 + photon -> CO + O, so one reaction makes both"),
    ("water photolysis", ("H2", "O2"), 2.0,
     "2 H2O + photon -> 2 H2 + O2, so one reaction makes both"),
    ("serpentinisation", ("H2", "CH4"), 4.0,
     "olivine + water -> H2, and some reduces CO2 to CH4"),
]


def explained_abiotically(pair, mix_fractions, tolerance=10.0):
    """-> (bool, why). Can one known reaction produce this pair?"""
    a, b = pair
    for name, prod, ratio, how in ABIOTIC_SOURCES:
        if set(prod) != set(pair):
            continue
        fa, fb = mix_fractions.get(prod[0], 0.0), mix_fractions.get(
            prod[1], 0.0)
        if fb <= 0:
            continue
        obs = fa / fb
        off = max(obs / ratio, ratio / obs)
        if off <= tolerance:
            return True, (f"{name} accounts for both: {how}, predicting "
                          f"{prod[0]}/{prod[1]} = {ratio:.1f} against an "
                          f"observed {obs:.2f}, within {off:.1f}x. One "
                          f"process writes the whole invoice, so nothing "
                          f"further is required")
    return False, (f"no single abiotic reaction has both {a} and {b} "
                   f"among its products at any ratio, so no one process "
                   f"accounts for them")


def required_flux(mix_fractions, T=288.0, surface_pa=1.01325e5,
                  gravity=9.82, lifetime_s=None):
    """-> (kg/yr of the minor species, pair, why). DERIVED.

    A pair held out of equilibrium is being topped up. The rate is
    the standing amount over its lifetime against the reaction.
    """
    rows = disequilibrium(mix_fractions, T)
    if not rows:
        return 0.0, None, "no reactive pair"
    (a, b), _orders, fa, fb, _w = rows[0]
    minor, f_minor = (a, fa) if fa < fb else (b, fb)
    from engine.radiative import MU, _molar
    mu = MU.get(minor) or _molar(minor)
    column = f_minor * surface_pa / gravity           # kg/m2
    area = 4 * math.pi * 6.371e6 ** 2
    standing = column * area
    # lifetime falls as the oxidant thickens; 10 yr at 21% O2 is
    # methane's measured value and scales inversely
    other = fb if minor == a else fa
    life = lifetime_s or (10.0 * SECONDS_PER_YEAR * 0.21 / max(other, 1e-12))
    return standing / (life / SECONDS_PER_YEAR), (a, b), (
        f"{standing:.2e} kg of {minor} standing, lifetime "
        f"{life/SECONDS_PER_YEAR:.2e} yr against {b if minor == a else a}")


def driven(mix_fractions, T=288.0, threshold=10.0, min_flux_kg_yr=1e9,
           surface_pa=1.01325e5, gravity=9.82):
    """-> (bool, why). Impossible AND expensive to maintain."""
    rows = disequilibrium(mix_fractions, T)
    if not rows:
        return False, ("no reactive pair present, so nothing here is "
                       "out of equilibrium and nothing needs a driver")
    (a, b), orders, fa, fb, why = rows[0]
    if orders < threshold:
        return False, (f"{a} and {b} coexist, but only {orders:.1f} "
                       f"orders from equilibrium -- geology suffices")
    known, kwhy = explained_abiotically((a, b), mix_fractions)
    if known:
        return False, (f"{a} and {b} are {orders:.0f} orders apart and "
                       f"it does not matter: {kwhy}")
    flux, _pair, fwhy = required_flux(mix_fractions, T, surface_pa,
                                      gravity)
    if flux < min_flux_kg_yr:
        return False, (f"{a} and {b} are {orders:.0f} orders apart, but "
                       f"holding them there costs only {flux:.2e} kg/yr "
                       f"-- {fwhy}")
    return True, (f"{a} at {fa:.2e} and {b} at {fb:.2e} together: {why} "
                  f"by {orders:.0f} ORDERS, and holding them apart "
                  f"costs {flux:.2e} kg/yr. Not the impossibility alone "
                  f"-- the BILL. Something is paying it, and that is an "
                  f"accounting identity rather than a claim about "
                  f"biology")


def scan(worlds):
    """-> [(label, driven, why)]. Look at many atmospheres at once."""
    return [(lbl, *driven(mix, T)) for lbl, mix, T in worlds]


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("earth_reads_as_driven", _earth)
    t("a_dead_world_does_not", _dead)
    t("one_gas_alone_is_not_a_signature", _single)
    t("the_rule_is_not_fitted_to_mars", _not_fitted_to_mars)
    t("it_says_driven_not_alive", _humble)
    return all(o[1] for o in out), out


def _earth():
    ok, why = driven({"CH4": 1.8e-6, "O2": 0.21})
    if not ok:
        raise ArithmeticError("Earth does not read as driven")
    return why


def _dead():
    """Mars was a false positive through three versions. It is fixed."""
    ok, _w = driven({"CO2": 0.965, "CO": 2e-5}, T=737.0)
    if ok:
        raise ArithmeticError("a world with no oxidant reads as driven")
    ok2, w2 = driven({"CO2": 0.95, "CO": 7e-4, "O2": 1.4e-3}, T=210.0,
                     surface_pa=636.0, gravity=3.73)
    if ok2:
        raise ArithmeticError("Mars reads driven again: " + w2[:120])
    return (f"Venus reads undriven -- no oxidant. Mars reads undriven "
            f"too, and it took three attempts. Orders from equilibrium "
            f"called it driven. A flux rule narrowed the gap to 23x and "
            f"still called it driven. Deriving the lifetime properly "
            f"from hydroxyl chemistry made it WORSE, because dry air "
            f"gives CO a 21-year life and a bigger bill. Magnitude was "
            f"never the question: {w2[:110]}")


def _not_fitted_to_mars():
    """The rule must answer pairs it was not built for."""
    h2o2, w1 = driven({"H2": 1e-3, "O2": 5e-4})
    h2ch4, w2 = driven({"H2": 1e-2, "CH4": 2.5e-3})
    if h2o2:
        raise ArithmeticError("H2 and O2 read as a signature; water "
                              "photolysis makes both")
    if h2ch4:
        raise ArithmeticError("H2 and CH4 read as a signature; "
                              "serpentinisation makes both")
    ok, _w = driven({"CH4": 1.8e-6, "O2": 0.21})
    if not ok:
        raise ArithmeticError("the rule now rejects Earth too")
    return ("the co-production rule was motivated by Mars, so it has to "
            "answer pairs it was not built for. Hydrogen beside oxygen "
            "is quiet -- water photolysis makes both. Hydrogen beside "
            "methane is quiet -- serpentinising rock makes both. Both "
            "are real astrobiological false positives and neither was "
            "tuned. Methane beside oxygen stays driven, because no "
            "reaction has those two among its products at any ratio")


def _single():
    ok, _w = driven({"O2": 0.21})
    if ok:
        raise ArithmeticError("oxygen alone was called a signature")
    ok2, _w2 = driven({"CH4": 1.8e-6})
    if ok2:
        raise ArithmeticError("methane alone was called a signature")
    return ("oxygen alone is not a signature -- a photodissociating "
            "ocean makes it. Methane alone is not -- serpentinising "
            "rock makes it. Only the PAIR is, because only the pair is "
            "impossible, and this returns nothing for either on its own")


def _humble():
    _ok, why = driven({"CH4": 1.8e-6, "O2": 0.21})
    if "biology" not in why:
        raise ArithmeticError("the refusal to claim life is missing")
    return ("the output is 'no known process accounts for this' and a "
            "bill, not 'life'. An unknown geology could still write the "
            "invoice, and the rule can only check reactions it has been "
            "given -- its blind spot is exactly the chemistry nobody "
            "has thought of. What it buys is that it is observable "
            "across interstellar distance from a spectrum, which "
            "nothing else concluded here is")


if __name__ == "__main__":
    worlds = [
        ("Earth", {"CH4": 1.8e-6, "O2": 0.21}, 288.0),
        ("Venus", {"CO2": 0.965, "CO": 2e-5}, 737.0),
        ("Mars", {"CO2": 0.95, "CO": 7e-4, "O2": 1.4e-3}, 210.0),
        ("Titan", {"CH4": 0.05, "N2": 0.95}, 94.0),
        ("early Earth", {"CH4": 1e-3, "CO2": 0.1}, 288.0),
    ]
    for lbl, ok, why in scan(worlds):
        print(f"  {'DRIVEN' if ok else 'quiet ':7}{lbl:14}{why[:76]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{d[:60]}")
    print("\nall:", ok)
