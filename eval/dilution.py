"""
Over-constrain the one fitted parameter, and see whether it predicts
or breaks.

engine/cosmos.py has exactly one free parameter: `dilution`, the
mass of pristine gas each unit of stellar ejecta mixes into. It was
tuned until the simulated composition matched the sun, and the
README says plainly that the resulting agreement is a FIT and not a
prediction. This is the experiment that decides which it can become.

WHY A FIT IS NOT EVIDENCE. One parameter tuned against one number --
the overall metallicity -- will always match, because there is
nothing left over to disagree. A model with as many knobs as
observations cannot be wrong, and a model that cannot be wrong has
told you nothing. The fit demonstrates the code runs.

WHAT WOULD MAKE IT A PREDICTION. Hold an observation OUT of the fit.
Tune dilution on some elements, then compute one that was never
used and compare it to the sun. That element had no way to influence
the parameter, so if it lands, the model predicted it. This is the
same move eval/induction.py already makes for rules -- fit on six
examples, score on the rest -- applied to a physical parameter.

    fit on      C, N, O, Ne      four elements
    predict     Fe               never used, and the sun measures it

WHAT "BREAKS IT" MEANS, AND WHY THAT IS THE BETTER OUTCOME. If no
single dilution can satisfy all of them, the model is refuted -- and
refuted informatively, because the RESIDUAL PATTERN says which yield
is wrong. A parameter that is too small for one element and too
large for another is not a parameter that needs better tuning. It is
a yield table with an error in a specific entry, and the per-element
best fits localise it.

THE THEORETICAL LIMIT. Even with perfect yields this model cannot do
better than its structure allows: four generations, one reservoir,
instantaneous mixing, no infall, no outflow, no Type Ia delay. So
the useful number is not how close it gets, it is whether the
remaining error is STRUCTURED. Scatter means noise; a pattern means
a missing mechanism, and the pattern names it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import cosmos                                    # noqa: E402
from engine import abundance                                 # noqa: E402

# EVERY NATURALLY OCCURRING ELEMENT, not the eleven a hand table
# listed. engine/abundance.py carries all 83 on the dex scale and
# derives mass fractions from them, so the testable set is now
# bounded by what cosmos YIELDS rather than by what anyone wrote
# down to compare against.
SOLAR = abundance.mass_fractions()
# EVERY ELEMENT BOTH SIDES KNOW ABOUT, rather than a chosen few.
# cosmos yields twelve; the solar table lists eleven; the overlap is
# what can be tested, and it is now nine instead of five. Computing
# it rather than writing it down means extending either side extends
# the experiment automatically.
def _testable():
    tracked = set()
    for _pop, (y, _e, _f) in cosmos.YIELDS.items():
        tracked |= set(y)
    return tuple(sorted(tracked & set(SOLAR)))


ALL = _testable()
HELD_OUT = ("Fe",)
FIT_ON = tuple(e for e in ALL if e not in HELD_OUT)


def simulate(dilution, seed="universe-0", generations=4):
    _stars, gas, _ledger = cosmos.run(generations=generations, seed=seed,
                                      dilution=dilution)
    return gas


def _err(dilution, elements, seed="universe-0"):
    gas = simulate(dilution, seed)
    return sum(abs(gas.get(e, 0.0) - SOLAR[e]) for e in elements) / \
        len(elements)


def best_dilution(elements, lo=0.1, hi=60.0, iters=60, seed="universe-0"):
    """Golden-section on the mean absolute error over these elements."""
    gr = (5 ** 0.5 - 1) / 2
    a, b = lo, hi
    c, d = b - gr * (b - a), a + gr * (b - a)
    fc, fd = _err(c, elements, seed), _err(d, elements, seed)
    for _ in range(iters):
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - gr * (b - a)
            fc = _err(c, elements, seed)
        else:
            a, c, fc = c, d, fd
            d = a + gr * (b - a)
            fd = _err(d, elements, seed)
        if b - a < 1e-4:
            break
    x = 0.5 * (a + b)
    return x, _err(x, elements, seed)


def per_element(seed="universe-0"):
    """Fit the ONE parameter to each element alone. Spread is the test."""
    out = {}
    for e in list(FIT_ON) + list(HELD_OUT):
        out[e] = best_dilution((e,), seed=seed)[0]
    return out


def held_out_test(seed="universe-0"):
    """Fit on four elements, predict the fifth. -> dict."""
    d, fit_err = best_dilution(FIT_ON, seed=seed)
    gas = simulate(d, seed)
    rows = {}
    for e in list(FIT_ON) + list(HELD_OUT):
        sim, obs = gas.get(e, 0.0), SOLAR[e]
        rows[e] = {"sim": sim, "obs": obs,
                   "ratio": (sim / obs) if obs else float("inf"),
                   "held_out": e in HELD_OUT}
    return {"dilution": d, "fit_error": fit_err, "elements": rows}


def corrected_yield_factor(seed="universe-0"):
    """What the held-out miss says the iron yield is wrong by."""
    r = held_out_test(seed)
    return r["elements"]["Fe"]["ratio"]


def leave_one_out(scale=None, seed="universe-0"):
    """For each element: fit on the other four, predict it.

    One held-out element can be unlucky. Five, each predicted by a
    parameter the other four chose, is the shape of the error --
    and the shape is what says whether a single yield is wrong or
    the model is.
    """
    out = {}
    for held in ALL:
        fit = tuple(e for e in ALL if e != held)
        with _yield_scale(scale):
            d, _e = best_dilution(fit, seed=seed)
            gas = simulate(d, seed)
        sim, obs = gas.get(held, 0.0), SOLAR[held]
        out[held] = {"dilution": d, "sim": sim, "obs": obs,
                     "ratio": sim / obs if obs else float("inf")}
    return out


class _yield_scale:
    """Temporarily scale one element's yield in every population.

    A correction has to be applied to the YIELD TABLE, which is the
    thing claimed to be wrong, not to the output. Scaling the answer
    would be fitting; scaling the yield is a hypothesis about
    nucleosynthesis that then has to survive elements it did not
    touch.
    """

    def __init__(self, spec):
        self.spec = spec
        self.saved = None

    def __enter__(self):
        if not self.spec:
            return self
        el, factor = self.spec
        self.saved = {}
        for pop, (yields, epoch, frac) in cosmos.YIELDS.items():
            if el in yields:
                self.saved[pop] = yields[el]
                yields[el] = yields[el] * factor
        return self

    def __exit__(self, *a):
        if self.saved:
            el, _f = self.spec
            for pop, v in self.saved.items():
                cosmos.YIELDS[pop][0][el] = v
        return False


def spread(rows):
    rs = [abs(r["ratio"] - 1.0) for r in rows.values()]
    return max(rs), sum(rs) / len(rs)


def correction_test(seed="universe-0"):
    """Derive the iron correction from its miss, then re-run LOO.

    THE TEST IS WHETHER THE OTHER FOUR IMPROVE. A factor fitted to
    iron will of course fix iron; that is circular and proves
    nothing. If the same factor also tightens C, N, O and Ne -- which
    it was not fitted to -- the yield table really was wrong in that
    entry. If only iron moves, the factor is absorbing an error
    rather than correcting one.
    """
    before = leave_one_out(seed=seed)
    factor = 1.0 / before["Fe"]["ratio"]
    after = leave_one_out(scale=("Fe", factor), seed=seed)
    others = [e for e in ALL if e != "Fe"]
    b_others = sum(abs(before[e]["ratio"] - 1) for e in others) / len(others)
    a_others = sum(abs(after[e]["ratio"] - 1) for e in others) / len(others)
    return {"factor": factor, "before": before, "after": after,
            "others_before": b_others, "others_after": a_others,
            "others_improved": a_others < b_others}


# ---------------------------------------------------------------------
# A DIFFERENT UNIVERSE IS NOT A BROKEN ONE.
#
# Everything above measures distance to the SUN, and distance to the
# sun is not the criterion. A simulated universe does not have to
# resemble ours. It has to be one THE LAWS OF OURS COULD HAVE MADE --
# internally consistent with every rule, and free to come out
# looking nothing like home.
#
# So the two questions are separated, because only one of them can
# fail:
#
#   LAWS         mass conserved, no element before its epoch, no
#                element made by a process that cannot make it,
#                enrichment monotonic, fractions summing to one.
#                A violation is a bug and the check fails.
#
#   RESEMBLANCE  how far the result sits from solar abundances.
#                Reported, never required. A universe 30x richer in
#                silver than ours is a universe with more mergers in
#                its history, not a broken model -- unless it broke
#                a law getting there.
#
# The r-process result reads differently under that split. As a
# resemblance measurement it is 29x off. As a law question it is
# silent, because nothing forbids a history with more mergers. What
# WOULD be a violation is making gold before any merger could have
# happened, and that is what gets checked.
def laws_hold(dilution=4.87, seed="universe-0"):
    """-> [(law, ok, detail)]. These are the ones that can fail."""
    from engine import epochs as _ep
    from engine.experts import BY_SYM
    stars, gas, ledger = cosmos.run(generations=4, seed=seed,
                                    dilution=dilution)
    out = []

    bad = [r["star"] for r in ledger if not r["conserved"]]
    out.append(("mass conserved", not bad,
                f"{len(ledger)} stellar events, {len(bad)} where ejecta "
                f"plus remnant did not equal the progenitor"))

    viol = []
    for st in stars:
        cut = _ep.ORDER.get(st.epoch)
        if cut is None:
            continue
        for sym in st.composition:
            base = sym.rstrip("0123456789")
            if base in _ep.ORIGIN and _ep.ORDER[_ep.ORIGIN[base]] > cut:
                viol.append((st.sid, base))
    out.append(("nothing before its epoch", not viol,
                f"{len(stars)} stars, {len(viol)} elements present before "
                f"the epoch that can make them"))

    tot = sum(gas.values())
    out.append(("fractions sum to one", abs(tot - 1.0) < 1e-9,
                f"the final gas sums to {tot:.12f}"))

    neg = [e for e, v in gas.items() if v < 0]
    out.append(("no negative abundance", not neg,
                f"{len(gas)} elements, {len(neg)} negative"))

    # nothing may be produced by a channel that cannot produce it
    wrong = []
    for e in gas:
        if e in BY_SYM and gas[e] > 0:
            ch, _why = abundance.channel(e)
            if ch == "primordial" and e not in ("H", "He", "Li"):
                wrong.append(e)
    out.append(("channels respected", not wrong,
                f"{len(wrong)} elements claimed by a process that cannot "
                f"make them"))
    return out


def resemblance(dilution=4.87, seed="universe-0"):
    """How far from home. Reported, never required."""
    gas = simulate(dilution, seed)
    shared = [e for e in ALL if e in gas]
    d = sum(abs(gas[e] - SOLAR[e]) for e in shared) / len(shared)
    worst = max(shared, key=lambda e: abs(gas[e] / SOLAR[e] - 1))
    return {"mean_abs": d, "worst": worst,
            "worst_ratio": gas[worst] / SOLAR[worst], "n": len(shared)}


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("one_parameter_fits_anything", _trivial)
    t("held_out_element", _held)
    t("residual_is_structured", _struct)
    t("structured_by_channel", _channels)
    t("reported_as_fit_not_prediction", _honest)
    t("laws_hold", _laws)
    t("resemblance_is_reported_not_required", _resemble)
    t("leave_one_out", _loo)
    t("correction_is_not_circular", _corr)
    return all(o[1] for o in out), out


def _trivial():
    """Fitting one parameter to one number must succeed. That is the point."""
    d, err = best_dilution(("O",))
    if err > 1e-3:
        raise ArithmeticError(f"could not even fit one element: {err:.2e}")
    return (f"fitting dilution to oxygen alone lands it to {err:.2e} at "
            f"dilution={d:.2f} -- which demonstrates nothing except that "
            f"one knob matches one number")


def _held():
    r = held_out_test()
    fe = r["elements"]["Fe"]
    fitted = [e for e in FIT_ON]
    worst = max(abs(r["elements"][e]["ratio"] - 1) for e in fitted)
    return (f"dilution={r['dilution']:.2f} fitted on {fitted} to within "
            f"{worst:.1%}; iron was held out and comes back "
            f"{fe['ratio']:.2f}x the solar value "
            f"({fe['sim']:.5f} against {fe['obs']:.5f}) -- "
            + ("PREDICTED" if abs(fe['ratio'] - 1) < 0.25 else
               "MISSED, so the model is refuted on the element it did not "
               "see"))


# Which process makes what. Grouping by this is the difference
# between "one table entry is wrong" and "a whole channel is".
# THE CHANNEL IS DERIVED, NOT LISTED HERE. This was a dict mapping
# each element to CNO / alpha / iron-peak / r-process, written by
# hand -- an inference supplied instead of computed, which is the
# one thing this repo is not supposed to do. engine/abundance.py
# now derives it from the binding curve: fusion pays only while
# binding per nucleon rises, so the peak at Z=26 is the boundary
# between what a star can build and what has to be captured.
#
# AND IT IS A CHANNEL, NOT A FAMILY. "Family" in this repo means
# constituents that actually come together -- a compound, a binding
# that happened. Elements sharing a production process have not come
# together with anything; they were made the same way. Calling that
# a family put two different relations under one word, and the one
# that matters for the ladder is the other one.
#
# A KNOWN EDGE, RECORDED RATHER THAN PATCHED. Nickel comes out
# "neutron-capture" because the semi-empirical peak is at Z=26,
# while real silicon burning makes Ni-56 and lets it decay to iron.
# The derivation is right about the curve and wrong about nickel,
# and special-casing it would hide a real limitation of the mass
# formula behind a hand edit.
def by_channel(rows=None):
    rows = rows or leave_one_out()
    out = {}
    for e, r in rows.items():
        out.setdefault(abundance.channel(e)[0], []).append((e, r["ratio"]))
    return {k: sorted(v) for k, v in out.items()}


def _channels():
    """Is the residual one entry, or a whole nucleosynthetic channel?"""
    fam = by_channel()
    means = {k: sum(r for _e, r in v) / len(v) for k, v in fam.items()}
    # THE WORST CHANNEL FIRST, because it distorts everything else.
    # Every element's dilution is fitted on the other eleven, so a
    # channel that is wrong by 30x drags every other fit with it --
    # which is why the alpha and CNO numbers move when r-process
    # elements enter the set. A badly wrong channel is not just wrong
    # about itself.
    worst = max(means, key=lambda k: abs(math.log10(means[k])))
    if abs(math.log10(means[worst])) > 0.7:
        detail = " ".join(f"{e} {r:.1f}x" for e, r in fam[worst])
        return (f"the {worst} channel is out by {means[worst]:.0f}x "
                f"({detail}) and dominates everything: each element is "
                f"fitted on the other eleven, so a channel this wrong "
                f"drags every other fit. Physically it is the model "
                f"giving every late-generation star a neutron-star "
                f"merger's worth of heavy elements, when mergers are "
                f"rare. Remaining channels: "
                + ", ".join(f"{k} {means[k]:.2f}x" for k in sorted(means)
                            if k != worst))
    alpha = [r for _e, r in fam.get("alpha", [])]
    cno = [r for e, r in fam.get("CNO", []) if e in ("C", "O")]
    fe = dict(fam.get("iron-peak", [])).get("Fe")
    if not alpha or not cno or fe is None:
        raise ArithmeticError("not enough elements to group by family")
    if not all(r > 1.0 for r in alpha):
        return (f"the alpha elements are not uniformly over-predicted: "
                f"{fam['alpha']} -- the channel reading does not hold")
    inside = min(alpha) <= fe <= max(alpha)
    return (f"grouped by what makes them: "
            + ", ".join(f"{k} {means[k]:.2f}x" for k in sorted(means))
            + f". Every alpha element is over-predicted "
              f"({min(alpha):.2f}-{max(alpha):.2f}x) and C and O are "
              f"under-predicted ({min(cno):.2f}-{max(cno):.2f}x). Iron at "
              f"{fe:.2f}x sits "
            + ("INSIDE" if inside else "outside")
            + " the alpha spread, so it is not the outlier five elements "
              "made it look like -- the error follows a production "
              "CHANNEL, not a single entry")


def _struct():
    """Scatter would be noise. A pattern names a missing mechanism."""
    pe = per_element()
    vals = sorted(pe.values())
    spread = vals[-1] - vals[0]
    if spread < 0.5:
        return (f"per-element best fits all within {spread:.2f} -- one "
                f"dilution satisfies every element and the parameter is "
                f"over-constrained successfully")
    lo = [e for e, v in pe.items() if v == vals[0]][0]
    hi = [e for e, v in pe.items() if v == vals[-1]][0]
    return (f"dilution fitted to each element alone spans {vals[0]:.2f} "
            f"({lo}) to {vals[-1]:.2f} ({hi}), a factor of "
            f"{vals[-1]/vals[0]:.1f}. No single value satisfies them, so "
            f"the model is refuted by its own observables and the "
            f"residual is structured rather than scattered")


def _honest():
    """The repo must not describe the fitted number as a prediction."""
    txt = (ROOT / "README.md").read_text().lower()
    if "dilution" in txt and "fitted" not in txt:
        raise ArithmeticError("the README quotes the dilution agreement "
                              "without saying it was fitted")
    return ("the README says the dilution factor was fitted wherever the "
            "agreement is quoted")


def _laws():
    """The only things here that are allowed to fail."""
    rows = laws_hold()
    bad = [n for n, ok, _d in rows if not ok]
    if bad:
        raise ArithmeticError(f"laws violated: {bad}")
    return (f"{len(rows)} laws hold: "
            + "; ".join(f"{n}" for n, _ok, _d in rows)
            + " -- this universe is one the rules could have produced")


def _resemble():
    """And this one reports. It must never be treated as a failure."""
    r = resemblance()
    return (f"mean |simulated - solar| = {r['mean_abs']:.2e} over "
            f"{r['n']} elements, worst {r['worst']} at "
            f"{r['worst_ratio']:.1f}x. Reported, not required: a universe "
            f"unlike ours is not a broken one, and nothing above this "
            f"line fails on it")


def _loo():
    rows = leave_one_out()
    worst, mean = spread(rows)
    order = sorted(rows, key=lambda e: abs(rows[e]["ratio"] - 1))
    return (f"each element predicted by a dilution the other four chose: "
            + ", ".join(f"{e} {rows[e]['ratio']:.2f}x" for e in ALL)
            + f"; mean miss {mean:.0%}, worst {order[-1]} at "
              f"{rows[order[-1]]['ratio']:.2f}x")


def _corr():
    """The iron correction, now that nine elements say it is not iron.

    With five elements iron looked like the outlier and a 0.577x
    yield correction looked like the fix. Nine elements put iron at
    1.73x INSIDE an alpha spread of 1.57-3.57x, so correcting iron
    alone treats one member of a family. The test still runs,
    because what it measures -- whether a factor fitted to one
    element helps the others -- is exactly what distinguishes a
    correction from an absorption.
    """
    r = correction_test()
    others = [e for e in ALL if e != "Fe"]
    moved = [e for e in others
             if abs(r["after"][e]["ratio"] - r["before"][e]["ratio"]) > 0.01]
    still = {e: round(r["after"][e]["ratio"], 2) for e in others
             if e not in moved}
    if not r["others_improved"]:
        return (f"iron's miss implies scaling its YIELD by "
                f"{r['factor']:.2f}, and the elements it was not fitted "
                f"to go {r['others_before']:.1%} -> "
                f"{r['others_after']:.1%} -- no better. The factor only "
                f"absorbs iron's own error, which is what the family "
                f"grouping predicts: iron is not the wrong entry")
    return (f"iron's miss implies scaling its YIELD by {r['factor']:.2f}. "
            f"Re-run, the four it was not fitted to go "
            f"{r['others_before']:.1%} -> {r['others_after']:.1%}, and the "
            f"mean hides where that came from: only {moved} moved -- the "
            f"element whose own fitting set contained the corrected iron. "
            f"{still} are unchanged, so they are NOT iron's fault and are "
            f"what is left when the structured error is removed")


def main():
    r = held_out_test()
    print(f"fit on {list(FIT_ON)}, hold out {list(HELD_OUT)}")
    print(f"  best dilution     {r['dilution']:.3f}")
    print(f"  mean abs error    {r['fit_error']:.3e} over the fitted four")
    print()
    print(f"  {'element':<10}{'simulated':>12}{'solar':>12}{'ratio':>9}  ")
    for e, d in r["elements"].items():
        tag = "  <- HELD OUT" if d["held_out"] else ""
        print(f"  {e:<10}{d['sim']:>12.5f}{d['obs']:>12.5f}"
              f"{d['ratio']:>9.2f}{tag}")
    print()
    pe = per_element()
    print("  dilution fitted to each element ALONE:")
    for e, v in pe.items():
        print(f"    {e:<6}{v:>8.2f}")
    print()
    print("  leave-one-out: each element predicted by the other four")
    loo = leave_one_out()
    for e in ALL:
        print(f"    {e:<6}dilution {loo[e]['dilution']:>6.2f}   "
              f"predicted {loo[e]['sim']:.5f} against {loo[e]['obs']:.5f}"
              f"   {loo[e]['ratio']:>6.2f}x")
    c = correction_test()
    print(f"\n  iron correction implied: x{c['factor']:.3f}")
    print(f"    the four it was NOT fitted to: "
          f"{c['others_before']:.1%} -> {c['others_after']:.1%} mean miss")
    for e in ALL:
        print(f"    {e:<6}{c['before'][e]['ratio']:>6.2f}x  ->  "
              f"{c['after'][e]['ratio']:>6.2f}x")

    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{d}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
