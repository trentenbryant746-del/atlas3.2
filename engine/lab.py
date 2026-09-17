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
    SUGGESTION    nothing is wrong, and something is worth looking
                  at anyway

A NOTE ON THE FIFTH. Everything above SUGGESTION is a verdict about
correctness and stops the build. Not every useful observation is
one. "This rule has never fired" is worth knowing and is not a
failure; nor is "this rule has only ever caught someone else." A
lab with no way to say that either stays silent about it or
promotes it to an error, and both are wrong -- silence loses the
observation and an error cries wolf until the whole thing is
ignored.

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

ROOT = Path(__file__).resolve().parent.parent

HOLDS, MISSING_RULE, CLASH, REFUSED, SUGGESTION = (
    "HOLDS", "MISSING_RULE", "CLASH", "REFUSED", "SUGGESTION")

LAYERS = {0: "constants", 1: "molecule", 2: "column", 3: "atmosphere",
          4: "balance", 5: "feedback", 6: "world", 7: "composition"}


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


@experiment(0, "does any bar ignore what state the thing is in?")
def a_bar_names_its_manifestation():
    from engine import scales
    ok, res = scales.check()
    bad = [d for n, o, d in res
           if not o and "manifestation" in n]
    if bad:
        return CLASH, bad[0]
    lo = scales.bar_of("nuclear-mass", "in-domain")[0] / 1e6
    hi = scales.bar_of("nuclear-mass", "out-of-domain")[0] / 1e6
    return HOLDS, (
        f"a domain with more than one state refuses to give a bar until "
        f"it is told which: {lo:.3f} MeV where the liquid drop applies "
        f"and {hi:.3f} where it does not, {hi/lo:.1f}x apart. The bar "
        f"shipped until now was {4.763:.3f}, measured across both, and "
        f"described neither population. The same rule that separates MeV "
        f"from a folding rate from kelvin separates two states of one "
        f"formula")


@experiment(0, "is any error bar a typed number?")
def no_bar_is_typed():
    import re
    from pathlib import Path
    eng = Path(__file__).resolve().parent
    bad = []
    pat = re.compile(r"^([A-Z_]*(?:BAR|TYPED|SEMF)[A-Z_]*)\s*=\s*"
                     r"([-+]?[0-9][0-9.eE+-]*)", re.M)
    for f in sorted(eng.glob("*.py")):
        for m in pat.finditer(f.read_text()):
            if m.group(1).endswith(("_SEED", "_N", "_LEN")):
                continue
            bad.append(f"{f.name}: {m.group(1)} = {m.group(2)}")
    if bad:
        return CLASH, ("a bar is typed rather than measured: "
                       + "; ".join(bad))
    return HOLDS, (
        "no module carries a typed error bar. SEMF_TYPED = 3.0 was the "
        "last one, taken from the literature with no derivation beside "
        "it, and its only users were two silent fallbacks. A number kept "
        "for reference is a number waiting to be used, and that one was")


@experiment(0, "can one substance wear another's properties?")
def no_shared_physical_default():
    """The sulfuric-acid leak, made into a rule."""
    import ast
    from pathlib import Path
    eng = Path(__file__).resolve().parent
    # a function that takes a species or a body, and defaults a
    # PHYSICAL quantity, is a place one thing can silently get
    # another's behaviour
    physical = {"T", "lapse", "depth", "P", "T_ref", "radius_m",
                "gravity", "albedo", "humidity"}
    bad = []
    for f in sorted(eng.glob("*.py")):
        tree = ast.parse(f.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            args = [a.arg for a in node.args.args]
            if not any(a in ("species", "body", "sp") for a in args):
                continue
            off = len(args) - len(node.args.defaults)
            for i, d in enumerate(node.args.defaults):
                nm = args[off + i]
                # a name ending _ref is a stated normalisation point,
                # not a property of the body in hand: weathering is
                # normalised AT 288 K by definition, and every body
                # uses the same reference on purpose.
                if nm.endswith("_ref"):
                    continue
                if nm in physical and isinstance(d, ast.Constant) \
                        and isinstance(d.value, (int, float)):
                    bad.append(f"{f.name}:{node.name}({nm}={d.value})")
    if bad:
        return CLASH, ("a physical quantity is defaulted in a function "
                       "that takes a species or body, so one can wear "
                       "another's properties: " + "; ".join(bad))
    return HOLDS, (
        "no function that takes a species or a body defaults a physical "
        "quantity. The condensation gradient was once a hardcoded 2e-6 "
        "-- water's value -- and passing sulfuric acid through it gave "
        "H2SO4 water's behaviour, silently, and the Venus refusal "
        "vanished. Cloud depth was 3,000 m, which is Earth's. Both now "
        "derive from the body in hand or refuse")


@experiment(0, "can a check fail on its own documentation?")
def checks_do_not_grep_themselves():
    """Written after making the same mistake three times."""
    import inspect
    import engine.lab as me
    # A RULE THAT COVERS ONE FILE IS NOT A RULE. This scanned only
    # lab.py's experiments, so engine/watch.py wrote a fourth
    # self-grepping check and nothing stopped it -- it searched the
    # census for the word "membrane" and matched the sentence saying
    # the census does not test membranes. Now every module's check
    # functions are scanned.
    import ast as _ast
    from pathlib import Path as _P
    bad = []
    for e in EXPERIMENTS:
        src = inspect.getsource(e.fn)
        if "read_text()" in src and "ast" not in src and "glob" not in src:
            bad.append(e.name)
    eng = _P(__file__).resolve().parent
    for f in sorted(eng.glob("*.py")):
        txt = f.read_text()
        try:
            tree = _ast.parse(txt)
        except Exception:
            continue
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.FunctionDef):
                continue
            if not node.name.startswith("_"):
                continue
            seg = _ast.get_source_segment(txt, node) or ""
            if "getsource" not in seg and "read_text()" not in seg:
                continue
            if "ast" in seg or "signature" in seg:
                continue
            # PRECISE: the danger is searching source for a literal
            # the searcher itself contains. A function that reads a
            # data file, or matches names from a table, cannot find
            # itself. Flagging those too would make the rule noise,
            # and a rule with false positives gets ignored.
            # A function that explicitly skips its own file cannot
            # find itself, however it searches. constants._dupes
            # does exactly that and was a false positive.
            if "== here" in seg or "!= here" in seg or "f == here" in seg:
                continue
            lits = [n.value for n in _ast.walk(node)
                    if isinstance(n, _ast.Constant)
                    and isinstance(n.value, str) and len(n.value) > 3]
            if any(seg.count(l) > 1 for l in lits):
                bad.append(f"{f.name}:{node.name}")
    if bad:
        return CLASH, ("these read a source file as text and may match "
                       "their own wording: " + ", ".join(bad))
    return HOLDS, (
        "no experiment decides anything by searching a file for a string "
        "it also contains. Three checks have failed this way -- two in "
        "engine/radiative.py matching 'observed_T' and its own module "
        "name, one here matching the comment that explains a bug it was "
        "testing for. A check written as a text search over its own file "
        "will always find itself; test the arithmetic or parse the AST")


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


@experiment(0, "does one equation ever mix two sources?")
def a_q_value_uses_one_source():
    """The bar argument depends on this and nothing was checking it."""
    from engine import nucleo, shells
    semf_he4 = nucleo.binding_per_nucleon(2, 2) * 4
    measured = 28.296
    bias = measured - semf_he4
    bar = nucleo.error_bar("decay")[0]
    # TEST THE ARITHMETIC, NOT THE TEXT. Grepping the source for
    # "B_ALPHA" matched the comment in q_values that EXPLAINS the old
    # bug, so the check failed on its own documentation. This is the
    # third time a check here has been written as a text search over
    # a file that contains the search term; it is now a rule of its
    # own (checks_do_not_grep_themselves).
    from engine import transitions
    probe = transitions.q_values(84, 128).get("alpha")
    if probe is not None:
        expect_mixed = (transitions._b(82, 126) + measured
                        - transitions._b(84, 128))
        if abs(probe - expect_mixed) < 1e-9:
            return CLASH, (
                f"an alpha Q-value still mixes a measured helium-4 "
                f"binding ({measured}) with SEMF parent and daughter "
                f"({semf_he4:.3f}), biasing every alpha channel by "
                f"{bias:+.3f} MeV -- {bias/bar:.1f} times its own bar")
    return HOLDS, (
        f"every term in a Q-value comes from the same formula. This is "
        f"not tidiness: a Q-value is a DIFFERENCE, and its bar is "
        f"{bar:.2f} MeV rather than the {nucleo.error_bar('mass')[0]:.2f} "
        f"MeV absolute mass error ONLY because the formula's errors "
        f"cancel between the two sides. Taking one term from elsewhere "
        f"destroys the cancellation. It used to, by {bias:+.3f} MeV, "
        f"which is {bias/bar:.1f} times the bar the result was judged "
        f"against")


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
    """The absence is named differently now the wings are settled."""
    from engine.radiative import grey_equivalent_full
    from engine.potential import wing_cutoff
    tau = grey_equivalent_full({"CO2": 8.9e6}, 737.0, 8.87, 9.2e6)
    ceiling = (1.0 + 0.75 * tau) ** 0.25
    needed = 737.0 / 226.7
    if ceiling >= needed:
        return HOLDS, (f"CO2 warms a surface by {ceiling:.3f} and the "
                       f"hottest rocky body needs {needed:.3f}")
    return MISSING_RULE, (
        f"CO2 at Venus' own column and pressure warms a surface by "
        f"{ceiling:.3f} and a real body needs {needed:.3f}. THE ABSENCE "
        f"HAS A DIFFERENT NAME NOW. 3.1.23 blamed missing continuum "
        f"absorption and it was added. 3.1.38 blamed the line shape and "
        f"suspected the wings. 3.1.39 derived the intermolecular "
        f"potential and let it predict where a wing stops: "
        f"{wing_cutoff('CO2', 737.0):.1f} cm^-1, against the 29 to 96 "
        f"Venus would require. The prediction was made from molecular "
        f"properties and checked afterwards, and it MISSED -- so the "
        f"wings are eliminated rather than left open. What remains is a "
        f"mechanism no gas model contains: Venus is wrapped in a "
        f"sulfuric acid cloud deck, and a condensed aerosol absorbs and "
        f"scatters across the whole spectrum instead of in bands. That "
        f"is a different rung, not a better line shape")


@experiment(2, "do the wing rules agree with each other?")
def far_wing_rules_clash():
    """RESOLVED in 3.1.39. Kept because the resolution is the finding."""
    from engine.potential import wing_cutoff, well_depth
    from engine.constants import K_B
    dc = wing_cutoff("CO2", 737.0)
    if not 5.0 < dc < 25.0:
        return CLASH, (f"the derived cutoff moved to {dc:.1f} cm^-1 and "
                       f"this resolution needs rechecking")
    return HOLDS, (
        f"the clash was between unbounded Lorentz wings, which claimed "
        f"315,694 cm^-1 of opacity and is impossible, and a cutoff from "
        f"diameter-over-speed, which is a guess with units. Neither was "
        f"a rule. engine/potential.py derives the intermolecular "
        f"potential from polarizability and ionisation energy -- London "
        f"dispersion against Pauli repulsion, well depth "
        f"{well_depth('CO2')/K_B:.0f} K against a literature 195 -- and "
        f"integrates a trajectory through it. The cutoff is "
        f"{dc:.1f} cm^-1 and it is DERIVED. It also misses the window "
        f"Venus would need by a factor of three to nine, which is what "
        f"settles the question rather than leaving it open")


@experiment(4, "can the climate bar be split by manifestation too?")
def climate_manifestations_not_yet_measurable():
    """The rule is right; the data cannot carry it here. REFUSED."""
    from engine import terraform, radiative
    n_bodies = sum(1 for b in terraform.BODIES.values()
                   if terraform.redistributes(b)[0])
    return REFUSED, (
        f"the manifestation rule says a climate bar should be measured "
        f"separately for each state a planet can be in -- thin against "
        f"thick atmosphere, with a condensable volatile against without. "
        f"It cannot be done here. Only {n_bodies} bodies survive the "
        f"redistribution test at all, three of those were spent "
        f"calibrating, and Venus is blocked on the far-wing clash so its "
        f"optical depth comes out 0.382 when it is physically enormous. "
        f"Splitting four bodies -- one of them wrong by 496 K -- into two "
        f"or three states leaves at most one per state, and a bar over "
        f"one sample is not a bar. What is needed is not a better "
        f"statistic but the missing rule at layer 3; the split becomes "
        f"measurable the moment Venus is derivable")


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


# -------------------------------------------- layer 7, composition
# EVERY RULE ABOVE IS TESTED ALONE. These are the constraints that do
# not exist inside any single module and only appear when all of them
# are used at once -- the ones nothing would catch, because each
# module is individually correct.


@experiment(7, "does the whole ladder run on one atom without contradicting itself?")
def one_atom_through_every_rule():
    from engine.experts import PT
    from engine import nucleo, transitions, valence, abundance
    from engine import provenance, radiative, folding
    w = {s: m for s, _n, m in PT}
    steps = [
        f"periodic table C={w['C']} u",
        f"SEMF C-12 {nucleo.binding_per_nucleon(6, 6):.3f} MeV/nucleon",
        f"transitions {transitions.decay_of(6, 6)[0]}",
        f"valence {valence.valence('C')[0]}",
        f"abundance {abundance.mass_fractions()['C']:.2e} by mass",
        f"provenance {provenance.history('universe-0', 0, 'C', 1, limit=1)[0].epoch}",
        f"CO2 {radiative.MU['CO2']:.3f} g/mol, "
        f"{len(radiative.BANDS['CO2'])} IR bands",
        f"glycine C:polar {folding.hydrophobicity('G'):.3f}",
    ]
    return HOLDS, ("one carbon atom resolved through 8 rules in sequence "
                   "with no contradiction: " + "; ".join(steps))


@experiment(7, "can a bulk average and a single nuclide be told apart?")
def mixture_and_nuclide_are_not_confused():
    from engine.experts import PT
    w = {s: m for s, _n, m in PT}
    bulk, exact = w["C"], 12.0
    d = abs(bulk - exact) / exact
    if d < 1e-6:
        return CLASH, ("the periodic table is carrying an exact nuclide "
                       "mass, so a gas and a nucleus cannot be told apart")
    return HOLDS, (
        f"the table gives carbon {bulk} u and carbon-12 is {exact} exactly, "
        f"a {100*d:.3f}% difference that is CORRECT and must survive: a "
        f"gas is a mixture of isotopes and a nucleus is one of them. "
        f"engine/radiative.py builds CO2 from the bulk average because it "
        f"weighs a gas; engine/nucleo.py uses per-nuclide masses because "
        f"it binds a nucleus. An earlier version measured binding against "
        f"atomic weights and produced an 80 MeV artefact")


@experiment(7, "is anything built from an element that does not exist?")
def nothing_is_built_from_absent_elements():
    import re
    from engine import abundance, radiative, biomatter
    nat = set(abundance.naturally_occurring())
    absent = set(abundance.absent_naturally())
    used = set()
    for f in radiative.FORMULAE.values():
        used |= set(re.findall(r"[A-Z][a-z]?", f))
    for f in biomatter.RESIDUES.values():
        used |= set(biomatter._elements(f))
    used |= set("CHNOPS")
    bad = used & absent
    if bad or not used <= nat:
        return CLASH, (f"built from elements that do not naturally occur: "
                       f"{sorted(bad or (used - nat))}")
    return HOLDS, (
        f"{len(used)} elements are used across the IR molecules, every "
        f"residue and the CHNOPS life gate, and all of them are in the "
        f"naturally-occurring set. None is among the {len(absent)} that "
        f"engine/abundance.py derives as absent ({', '.join(sorted(absent)[:5])}...) "
        f"-- a molecule made of technetium would be chemistry with no "
        f"supply chain")


@experiment(7, "does valence permit the bonds the formulas actually use?")
def valence_agrees_with_the_formulas():
    from engine import valence
    need = {"C": 4, "N": 3, "O": 2, "H": 1, "S": 2}
    bad = []
    for sym, n in need.items():
        v = valence.valence(sym)
        got = v[0] if isinstance(v, tuple) else v
        if got != n:
            bad.append(f"{sym}: shells say {got}, formulas need {n}")
    if bad:
        return CLASH, "; ".join(bad)
    return HOLDS, (
        "valence derived from shell filling gives C 4, N 3, O 2, H 1 and "
        "S 2, which is exactly what the residue and molecule formulas "
        "require. These come from opposite directions -- one from aufbau "
        "occupancy, the other from counting atoms in real compounds -- "
        "and nothing was arranged to make them meet")


@experiment(7, "is energy or search the barrier to an origin?")
def the_barrier_is_search_not_energy():
    from engine.origin import (genome_cost, length_ceiling,
                               search_years, landauer)
    from engine.constants import E_CHARGE
    n = length_ceiling()
    c = genome_cost(580000)
    if c > 1e-11:
        return CLASH, "copying costs more than a cell spends"
    return HOLDS, (
        f"two rules already here answer this without modelling a cell. "
        f"Landauer puts a bit at {landauer(300.0)/E_CHARGE:.4f} eV, so a "
        f"minimal genome costs {c:.1e} J to copy against the 1e-11 a "
        f"bacterium spends -- energy is not the barrier and a whole "
        f"class of explanation is ruled out. What cannot be paid for is "
        f"the SEARCH: an ocean of molecules trying a sequence every "
        f"picosecond for the age of the universe reaches {n} residues "
        f"and stops. Ten more costs {search_years(n+10)/search_years(n):.0e} "
        f"times longer. Below the ceiling chance suffices; above it "
        f"something must build without searching, which is exactly what "
        f"engine/folding.py concludes about Levinthal one level down")


@experiment(0, "which rules have never once fired?")
def rules_that_have_never_fired():
    """A rule that only catches other people is not being tested.

    IT MUST NOT CALL run(). The first version did, and run() calls
    every experiment including this one, so it recursed until the
    stack gave out. An experiment that inspects the whole lab cannot
    be part of the lab unless it reads a RECORD instead of taking a
    reading -- so the runner writes the history and this only reads
    it.

    A SUGGESTION, deliberately. Never having fired is not a defect
    and stopping the build over it would be crying wolf. But going
    unrecorded means nobody asks whether a rule is load-bearing or
    decorative. Two of these caught their own author within minutes
    of being written -- MEASURED_Q_BAR in 3.1.31 and YEAR_S in
    3.1.47 -- and that is the only hard evidence any of them are
    live.
    """
    hist = _load_history()
    if not hist:
        return SUGGESTION, ("no verdict history yet; it accumulates as "
                            "the lab runs")
    never = [n for n, vs in sorted(hist.items()) if vs == [HOLDS]]
    fired = [n for n, vs in sorted(hist.items()) if vs != [HOLDS]]
    return SUGGESTION, (
        f"{len(fired)} of {len(hist)} rules have returned something "
        f"other than HOLDS at least once and are demonstrably live"
        + (f": {', '.join(fired[:4])}" if fired else "")
        + f". The other {len(never)} have only ever passed. THE RECORD "
          f"STARTS WHEN RECORDING STARTED, so rules that fired before "
          f"this existed -- the sulfuric-acid leak, MEASURED_Q_BAR, "
          f"YEAR_S -- show as never having fired, and the count "
          f"understates. Never having fired is not a defect and is not "
          f"evidence either: a rule that cannot fail looks exactly like "
          f"one that has not yet had cause to. Worth knowing, not worth "
          f"stopping for")


# ------------------------------------------------------- the runner
_HIST = ROOT / ".atlas-verdicts.json"


def _load_history():
    import json
    try:
        return json.loads(_HIST.read_text())
    except Exception:
        return {}


def _record(rows):
    """The RUNNER writes history. An experiment only reads it."""
    import json
    hist = _load_history()
    for _L, nm, v, _d, _a in rows:
        seen = set(hist.get(nm, []))
        seen.add(v)
        hist[nm] = sorted(seen)
    try:
        _HIST.write_text(json.dumps(hist, indent=1, sort_keys=True))
    except Exception:
        pass


def unresolved():
    """-> [(layer, name, verdict, detail)]. Everything not yet HOLDS."""
    return [(L, n, v, d) for L, n, v, d, _ in run(stop_on_problem=False)[0]
            if v != HOLDS]


def suggestions():
    """-> [(layer, name, detail)]. Worth a look, nothing is wrong."""
    return [(L, n, d) for L, n, v, d, _ in run(stop_on_problem=False)[0]
            if v == SUGGESTION]


def run(up_to=None, stop_on_problem=True):
    """-> (rows, first bad layer). Layers in order; stop when one breaks.

    A result at layer 6 means nothing if layer 2 is unsound, so the
    default is to stop. That is the whole reason for the ordering.
    """
    # Defaulting this to a literal 6 silently dropped layer 7 the
    # moment it was added: four composition experiments ran, passed
    # and were never reported. A bound written as a number instead
    # of as the thing it bounds goes stale the first time the thing
    # changes.
    if up_to is None:
        up_to = max(LAYERS)
    rows, bad = [], None
    for L in sorted(LAYERS):
        if L > up_to:
            break
        here = [e for e in EXPERIMENTS if e.layer == L]
        for e in here:
            v, d = e.run()
            rows.append((L, e.name, v, d, e.asks))
            if v not in (HOLDS, SUGGESTION) and bad is None:
                bad = L
        if bad is not None and stop_on_problem:
            break
    _record(rows)
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
    # is a clash nobody has written down. A SUGGESTION stops nothing
    # and needs no name beyond its own text.
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
    # The named absence moved. 3.1.23 named continuum absorption and
    # it was added; 3.1.38 names where a wing stops. A check that
    # insisted on the old word would have failed the moment its own
    # finding was acted on.
    if not any(k in d.lower() for k in ("continuum", "wing", "threshold")):
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
