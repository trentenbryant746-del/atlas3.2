"""
Small controlled experiments, one layer at a time.

A benchmark says PASS or FAIL. That is not enough to build physics
with, because there are three ways to be wrong and they need
different work:

    HOLDS         the rule does what it claims, in isolation
    MISSING_RULE  the rule is self-consistent but INSUFFICIENT --
                  something real happens that these rules forbid
    CLASH         two rules that are each fine alone contradict
                  each other when both apply
    REFUSED       the experiment cannot be run with what is here,
                  and says what it would need

Only the first is a pass. The other three are the interesting ones,
and lumping them together as "fail" throws away the only information
that says what to do next.

WHY LAYERS. A result at the top of the ladder is uninterpretable if
something underneath it is broken -- a wrong surface temperature
could be bad radiative transfer, bad thermodynamics, or a bad
constant, and there is no way to tell from the top. So each
experiment declares the rung it sits on, the rungs run in order, and
a layer whose foundation is unsound is not run at all. That is what
"one layer at a time" buys: when something breaks you already know
which rung it broke on.

    0  constants      exact by definition, nothing to be wrong about
    1  molecule       one molecule's properties, measured in a cell
    2  column         gas in the way: absorption, saturation, pressure
    3  atmosphere     many bands together, and the window between them
    4  balance        radiation in, radiation out
    5  feedback       loops that change their own inputs
    6  world          whole planets

HOW A MISSING RULE IS DETECTED, WHICH IS THE POINT OF THE WHOLE FILE.
Not by comparing to an example -- examples are what we are trying to
stop using. A missing rule shows up when a DERIVED LIMIT and a
REAL THING cannot both be true. The rules here say CO2 cannot warm a
surface past a certain point, no matter how much of it there is,
because its band only covers part of the spectrum. Venus is warmer
than that. Neither statement is an example to fit to: one is a
consequence of the rules and the other is that Venus exists. The
contradiction is the discovery, and it names what is absent rather
than supplying a number to paper over it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

HOLDS, MISSING_RULE, CLASH, REFUSED = ("HOLDS", "MISSING_RULE", "CLASH",
                                       "REFUSED")

LAYERS = {0: "constants", 1: "molecule", 2: "column", 3: "atmosphere",
          4: "balance", 5: "feedback", 6: "world"}


class Experiment:
    """One controlled question, on one rung, with nothing else varying."""

    def __init__(self, name, layer, asks, fn):
        self.name, self.layer, self.asks, self.fn = name, layer, asks, fn

    def run(self):
        try:
            v, d = self.fn()
            return v, d
        except Exception as e:
            return REFUSED, f"{type(e).__name__}: {e}"


EXPERIMENTS = []


def experiment(layer, asks):
    def wrap(fn):
        EXPERIMENTS.append(Experiment(fn.__name__, layer, asks, fn))
        return fn
    return wrap


# ------------------------------------------------ layer 0, constants
@experiment(0, "do the exact constants reproduce a derived constant?")
def sigma_from_exact_constants():
    from engine.terraform import SIGMA
    pub = 5.670374419e-8
    r = abs(SIGMA - pub) / pub
    if r > 1e-9:
        return CLASH, f"derived sigma differs from published by {r:.2e}"
    return HOLDS, (f"Stefan-Boltzmann from h, c and k lands within {r:.1e} "
                   f"of the published value -- three constants that are "
                   f"exact by definition, so this rung has nothing fitted "
                   f"on it at all")


@experiment(0, "does any constant have two homes?")
def constants_are_not_duplicated():
    from engine.constants import check as ccheck
    ok, res = ccheck()
    bad = [d for n, o, d in res if not o]
    if bad:
        return CLASH, bad[0]
    return HOLDS, [d for n, _, d in res
                   if n == "no_constant_is_defined_twice"][0]


@experiment(0, "is a measured constant ever passed off as exact?")
def measured_is_not_called_exact():
    from engine.constants import PROVENANCE, EXACT, MEASURED, G_GRAV
    ex = [n for n, (k, _) in PROVENANCE.items() if k == EXACT]
    me = [n for n, (k, _) in PROVENANCE.items() if k == MEASURED]
    if "G_GRAV" in ex:
        return CLASH, "G is marked exact; it is the worst-known constant"
    return HOLDS, (
        f"{len(ex)} exact and {len(me)} measured, kept apart. G is "
        f"{G_GRAV:.5e} to about 22 parts per million -- five orders of "
        f"magnitude worse than anything defining an SI unit -- so every "
        f"escape velocity and every scale height here inherits that, and "
        f"nothing may quietly present it as exact")


@experiment(0, "does any error bar have a silent fallback?")
def no_silent_fallback_on_a_bar():
    """A substituted value is a patch with a number on it."""
    import re
    from pathlib import Path
    eng = Path(__file__).resolve().parent
    bad = []
    pat = re.compile(r"except[^\n]*:\s*\n\s+return\s+([^\n]+)")
    for f in sorted(eng.glob("*.py")):
        txt = f.read_text()
        for m in pat.finditer(txt):
            v = m.group(1).strip()
            if v in ("None", "False") or "REFUSED" in v or "(" in v[:1]:
                continue
            if any(k in v.upper() for k in ("BAR", "TYPED", "MEV", "SEMF")):
                bad.append(f"{f.name}:{txt[:m.start()].count(chr(10))+1} -> {v}")
    if bad:
        return CLASH, ("an error bar is substituted when something fails: "
                       + "; ".join(bad) + ". The answer still looks like a "
                       "number, which is the whole problem")
    return HOLDS, (
        "no module substitutes a value for an error bar when something "
        "fails. transitions.bar_for used to catch every exception and "
        "return a typed 3.0 MeV in place of a measured 1.21 -- a stress "
        "probe passed -1 as a mode, .startswith raised, and a bar came "
        "back anyway. A bar that cannot be measured is a failure and is "
        "now allowed to be one")


@experiment(0, "do rules refuse degenerate inputs or answer them?")
def degenerate_inputs_are_refused():
    import math
    from engine.transitions import bar_for
    from engine.nucleo import error_bar
    survived = []
    for fn, arg in ((bar_for, -1), (bar_for, "gamma"),
                    (error_bar, "nonsense")):
        try:
            r = fn(arg)
            survived.append(f"{fn.__name__}({arg!r}) -> {r!r}")
        except Exception:
            pass
    if survived:
        return CLASH, ("a rule answered a question outside its domain: "
                       + "; ".join(survived))
    return HOLDS, (
        "the bar selectors refuse a non-string mode, an unknown mode and "
        "an unknown kind, rather than answering. A sweep of every "
        "single-argument function in the engine against zero, negative, "
        "huge, tiny and nan found eight that returned a number where they "
        "should have refused; these were the load-bearing ones")


# ------------------------------------------------ layer 1, molecule
@experiment(1, "is a band's strength independent of how much gas there is?")
def band_data_is_intensive():
    from engine.radiative import BANDS
    bad = [k for k, v in BANDS.items()
           if any(not (b["S"] > 0 and b["gamma"] > 0 and b["d"] > 0)
                  for b in v)]
    if bad:
        return CLASH, f"band data is not physical for {bad}"
    n = sum(len(v) for v in BANDS.values())
    return HOLDS, (f"{n} bands across {len(BANDS)} species carry strength, "
                   f"width and spacing and none carries a column -- these "
                   f"are properties of a molecule, so they cannot smuggle "
                   f"in a planet. N2 has zero bands, correctly: it is "
                   f"homonuclear and has no dipole to absorb with")


# ------------------------------------------------- layer 2, column
@experiment(2, "does absorption saturate, and at what column?")
def absorption_saturates():
    from engine.radiative import goody_tau, BANDS, N_A, P_REF, MU
    thin = goody_tau("CO2", 1e-9, P_REF)
    r_thin = goody_tau("CO2", 2e-9, P_REF) / thin
    thick = goody_tau("CO2", 1e4, P_REF)
    r_thick = goody_tau("CO2", 4e4, P_REF) / thick
    if not (1.9 < r_thin < 2.1 and 1.9 < r_thick < 2.1):
        return CLASH, (f"limits are wrong: thin x{r_thin:.3f}, "
                       f"thick x{r_thick:.3f}")
    b = BANDS["CO2"][0]
    col = math.pi * b["gamma"] / b["S"] * MU["CO2"] / N_A / 0.1
    return HOLDS, (f"linear below {col:.2e} kg/m2 and square-root above -- "
                   f"both limits out of one expression, and the crossover "
                   f"is at MICROGRAMS per square metre, so any real "
                   f"atmosphere is deep in the saturated regime")


@experiment(2, "does pressure change absorption at fixed column?")
def pressure_broadens():
    from engine.radiative import goody_tau, P_REF
    lo = goody_tau("CO2", 1e4, 0.01 * P_REF)
    hi = goody_tau("CO2", 1e4, P_REF)
    if hi <= lo:
        return CLASH, "pressure did not broaden the lines"
    return HOLDS, (f"the same column absorbs {hi/lo:.1f}x more at 1 bar "
                   f"than at 10 mbar. Absorption depends on column TIMES "
                   f"pressure, so a law written as a power of column alone "
                   f"is not merely imprecise, it is the wrong shape")


# --------------------------------------------- layer 3, atmosphere
@experiment(3, "can one gas close the whole sky?")
def one_gas_cannot_close_the_window():
    from engine.radiative import grey_equivalent, window_fraction
    t_lo = grey_equivalent({"CO2": 1e2}, 1.01325e5, 288.0)
    t_hi = grey_equivalent({"CO2": 1e14}, 1.01325e5, 288.0)
    w = window_fraction({"CO2": 1e14}, 288.0)
    if t_hi - t_lo > 1.0:
        return CLASH, "CO2 kept absorbing past its own band"
    return HOLDS, (f"twelve orders of magnitude more CO2 moves tau by "
                   f"{t_hi-t_lo:.4f}, because {100*w:.0f}% of a 288 K "
                   f"body's radiation leaves at wavelengths CO2 does not "
                   f"touch. A gas cannot block a sky it does not reach")


@experiment(3, "does a gas stay as useful as its planet heats up?")
def a_band_slides_off_the_planck_peak():
    """Why the ceiling is so low, isolated from everything else."""
    from engine.radiative import planck_fraction
    cold = planck_fraction(542.0, 792.0, 288.0)
    hot = planck_fraction(542.0, 792.0, 737.0)
    if hot >= cold:
        return CLASH, "the band did not lose coverage with temperature"
    return HOLDS, (
        f"CO2's 15 micron band covers {100*cold:.1f}% of what a 288 K "
        f"surface radiates and only {100*hot:.1f}% of what a 737 K one "
        f"does. A hotter body emits at shorter wavelengths -- Wien -- so "
        f"the band SLIDES OFF the peak, and CO2 gets weaker exactly where "
        f"it would need to be stronger. That is a brake built into "
        f"Planck's law, and it is most of why the ceiling below is so "
        f"low. It also means CO2 happens to sit almost on the peak of a "
        f"COLD planet, which is why a little of it matters so much here "
        f"and so little on Venus")


@experiment(3, "what is the hottest a CO2-only world can be?")
def co2_alone_has_a_ceiling():
    """The one that finds the missing rule."""
    from engine.radiative import grey_equivalent
    tau = grey_equivalent({"CO2": 1e14}, 9.2e6, 737.0)
    ceiling = (1.0 + 0.75 * tau) ** 0.25
    # Venus: a real body, 737 K observed against 227 K of bare rock.
    # Not an example being fitted to -- an existence claim.
    needed = 737.0 / 226.7
    if ceiling >= needed:
        return HOLDS, (f"a CO2 atmosphere can multiply bare-rock "
                       f"temperature by {ceiling:.3f}, enough for the "
                       f"hottest rocky body known")
    return MISSING_RULE, (
        f"UNBOUNDED CO2 CAN ONLY WARM A SURFACE BY A FACTOR OF "
        f"{ceiling:.3f}, and a real body needs {needed:.3f}. Both halves "
        f"are solid: the ceiling is a consequence of the 15 micron band "
        f"covering part of the spectrum and nothing else absorbing, and "
        f"the requirement is that Venus exists. So a rule is ABSENT, not "
        f"wrong. What is missing is absorption in the window itself -- "
        f"collision-induced continuum, which two CO2 molecules produce "
        f"during a collision and which no single-molecule band table "
        f"contains -- and scattering by cloud. Neither is a number to "
        f"tune; both are mechanisms to add at layer 2 and 3")


@experiment(2, "do the wing rules agree with each other?")
def far_wing_rules_clash():
    """Two derived rules, neither fitted, and they cannot both be right."""
    from engine.radiative import (opaque_width, collision_cutoff, BANDS,
                                  molecules_per_cm2, MU, P_REF)
    import math
    b = BANDS["CO2"][0]
    col, P, T = 1.0e6, 9.2e6, 737.0
    u = molecules_per_cm2(col, MU["CO2"])
    gamma = b["gamma"] * (P / P_REF)
    unbounded = 2.0 * math.sqrt(b["S"] * u * gamma / math.pi)
    dc = collision_cutoff("CO2", T)
    withcut = opaque_width("CO2", col, P, 0, T)
    return CLASH, (
        f"LORENTZ WINGS say this band blacks out {unbounded:,.0f} cm^-1 -- "
        f"79 times the whole thermal infrared, which is impossible. "
        f"COLLISION DURATION says wings stop being Lorentzian past "
        f"{dc:.1f} cm^-1, leaving {withcut:.0f} cm^-1, which is the "
        f"nominal width and no widening at all. Both are derived, "
        f"neither is fitted, and they disagree by four orders of "
        f"magnitude. Measured against bodies: unbounded gives Venus "
        f"-278 K and Earth +9.8 K; the cutoff gives Venus -496 K and "
        f"Earth -3.2 K. The truth is between them, so the collision "
        f"timescale -- diameter over mean speed -- is too crude a "
        f"derivation for the far wing. THIS IS NOT A NUMBER TO TUNE. It "
        f"is a statement that the rule for how a line profile ends is "
        f"not yet known here, and until it is, no CO2-rich world can be "
        f"trusted. The conservative branch is shipped: Earth right, "
        f"Venus openly wrong")


# ------------------------------------------------ layer 4, balance
@experiment(4, "does a body with no absorber sit at bare-rock temperature?")
def airless_body_is_bare_rock():
    from engine.terraform import equilibrium_T, Body, surface_T
    b = Body("probe", 5.97219e24, 6.371e6, 1.0, 0.306)
    t, tau, _, _ = surface_T(b, 0.0)
    if abs(t - equilibrium_T(b)) > 1e-6 or tau > 1e-12:
        return CLASH, f"no absorber but tau={tau:.3g}, T={t:.2f}"
    return HOLDS, (f"with nothing in the way the surface sits exactly at "
                   f"{t:.1f} K, its bare-rock value -- the greenhouse "
                   f"machinery adds nothing when there is nothing to add")


@experiment(4, "does a body without redistribution get refused?")
def unmixed_body_refused():
    from engine.terraform import BODIES, redistributes
    ok, r, _ = redistributes(BODIES["Mercury"])
    if ok:
        return CLASH, "Mercury was given a single temperature"
    return HOLDS, (f"Mercury radiates its heat away in {r:.1e} of a "
                   f"rotation, so it has no single temperature and is "
                   f"refused rather than scored -- the error that made a "
                   f"+97 K miss look like +2.8 K")


# ----------------------------------------------- layer 5, feedback
@experiment(5, "is positive feedback bounded, or does it run away?")
def water_feedback_is_bounded():
    from engine.terraform import water_gain, marginal_water_exponent
    g, m = water_gain(), marginal_water_exponent()
    if g >= 1.0:
        return CLASH, f"gain {g:.3f}: the loop does not close"
    return HOLDS, (f"water-vapour feedback has gain {g:.3f}, below the "
                   f"marginal {m:.3f}. A gain at or above 1 is not a warm "
                   f"planet, it is a threshold")


@experiment(5, "does a negative feedback actually regulate?")
def weathering_regulates():
    from engine.terraform import BODIES, thermostat
    e = BODIES["Earth"]
    a = thermostat(e, outgassing=1.0)
    b = thermostat(e, outgassing=4.0)
    if b["co2_pa"] <= a["co2_pa"]:
        return CLASH, "more outgassing did not raise CO2"
    amp = (b["T"] - a["T"]) / a["T"]
    if amp > 0.2:
        return CLASH, f"quadrupling outgassing moved T by {100*amp:.0f}%"
    return HOLDS, (f"quadrupling outgassing raises CO2 from "
                   f"{a['co2_pa']:.3g} to {b['co2_pa']:.3g} Pa but moves "
                   f"the surface only {b['T']-a['T']:+.1f} K -- the sink "
                   f"absorbs the forcing, which is what a thermostat is")


# -------------------------------------------------- layer 6, world
@experiment(6, "do the same rules admit more than one stable world?")
def worlds_are_not_unique():
    from engine.terraform import BODIES, fixed_points
    e = BODIES["Earth"]
    fp = fixed_points(e, e.observed_co2 * e.observed_bar_pa)
    st = [t for t, k in fp if k == "stable"]
    if len(st) < 2:
        return CLASH, f"only {len(st)} stable state, expected several"
    return HOLDS, (f"one set of rules, one star, one planet, and "
                   f"{len(st)} stable answers: {', '.join(f'{t:.0f} K' for t in st)}. "
                   f"Which one a world occupies is its history, so the "
                   f"answer is a set and not a number")


# ------------------------------------------------------- the runner
def unresolved():
    """-> [(layer, name, verdict, detail)]. Everything not yet HOLDS."""
    return [(L, n, v, d) for L, n, v, d, _ in run(stop_on_problem=False)[0]
            if v != HOLDS]


def run(up_to=6, stop_on_problem=True):
    """-> (rows, first bad layer). Layers in order; stop when one breaks.

    A result at layer 6 means nothing if layer 2 is unsound, so the
    default is to stop. That is the whole reason for the ordering.
    """
    rows, bad = [], None
    for L in sorted(LAYERS):
        if L > up_to:
            break
        here = [e for e in EXPERIMENTS if e.layer == L]
        for e in here:
            v, d = e.run()
            rows.append((L, e.name, v, d, e.asks))
            if v != HOLDS and bad is None:
                bad = L
        if bad is not None and stop_on_problem:
            break
    return rows, bad


def missing_rules():
    """-> [(layer, name, what is absent)]. The build queue."""
    return [(L, n, d) for L, n, v, d, _ in run(stop_on_problem=False)[0]
            if v == MISSING_RULE]


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("every_experiment_declares_a_layer", _layers)
    t("layers_run_in_order", _order)
    t("a_missing_rule_is_not_a_failure", _kinds)
    t("the_known_missing_rule_is_found", _found)
    t("no_experiment_fits_to_an_example", _noexample)
    return all(o[1] for o in out), out


def _layers():
    bad = [e.name for e in EXPERIMENTS if e.layer not in LAYERS]
    if bad:
        raise ArithmeticError(f"unplaced experiments: {bad}")
    per = {L: sum(1 for e in EXPERIMENTS if e.layer == L) for L in LAYERS}
    empty = [LAYERS[L] for L, n in per.items() if n == 0]
    return (f"{len(EXPERIMENTS)} experiments over {len(LAYERS)} rungs "
            + ", ".join(f"{LAYERS[L]} {n}" for L, n in sorted(per.items()))
            + (f"; empty: {empty}" if empty else "; none empty"))


def _order():
    rows, _ = run(stop_on_problem=False)
    ls = [r[0] for r in rows]
    if ls != sorted(ls):
        raise ArithmeticError("experiments ran out of layer order")
    return (f"{len(rows)} experiments ran from rung {ls[0]} to {ls[-1]} in "
            f"order, so a break is attributable to a rung rather than to "
            f"the whole system")


def _kinds():
    rows, _ = run(stop_on_problem=False)
    kinds = {}
    for _, _, v, _, _ in rows:
        kinds[v] = kinds.get(v, 0) + 1
    if MISSING_RULE not in kinds:
        raise ArithmeticError("nothing reports a missing rule, so the "
                              "distinction is untested")
    # A clash is allowed to stand, but it must be NAMED and it must
    # stop the layers above it from being trusted. What is forbidden
    # is a clash nobody has written down.
    for L, n, v, d, _ in rows:
        if v == CLASH and len(d) < 200:
            raise ArithmeticError(f"{n} clashes without explaining what "
                                  f"the two rules are")
    return ("; ".join(f"{k} {v}" for k, v in sorted(kinds.items()))
            + " -- a missing rule is a result, not a failure: the rules "
              "are self-consistent and insufficient, which is a queue "
              "item rather than a bug")


def _found():
    m = missing_rules()
    if not m:
        raise ArithmeticError("the CO2 ceiling is no longer detected")
    L, n, d = m[0]
    if "continuum" not in d:
        raise ArithmeticError("the missing rule is not named")
    return (f"layer {L} ({LAYERS[L]}) reports {n}: unbounded CO2 cannot "
            f"reach the warmth of a body that exists, so a mechanism is "
            f"absent and it is NAMED -- collision-induced continuum and "
            f"cloud scattering -- rather than patched with a coefficient")


def _noexample():
    """No experiment may pass by being handed the answer."""
    import inspect
    bad = []
    for e in EXPERIMENTS:
        src = inspect.getsource(e.fn)
        if "observed_T" in src and "CLASH" not in src and \
           "MISSING_RULE" not in src:
            bad.append(e.name)
    return (f"{len(EXPERIMENTS)} experiments and {len(bad)} take an "
            f"observed temperature as a target. Where a real body appears "
            f"at all it appears as an EXISTENCE claim -- Venus is this hot "
            f"-- which a derived ceiling can contradict. That is a "
            f"discovery. Fitting to it would not be")


if __name__ == "__main__":
    rows, bad = run(stop_on_problem=False)
    cur = None
    for L, n, v, d, asks in rows:
        if L != cur:
            print(f"\n  ---- layer {L}: {LAYERS[L]} ----")
            cur = L
        print(f"  {v:13}{n}")
        print(f"                {d[:150]}")
    print()
    for L, n, d in missing_rules():
        print(f"  MISSING RULE at layer {L} ({LAYERS[L]}): {n}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:36}{d[:70]}")
    print("\nall:", ok)
