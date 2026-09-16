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

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import cosmos                                    # noqa: E402
from engine.mixtures import OBSERVED                         # noqa: E402

SOLAR = OBSERVED["sun"][0]
# EVERY ELEMENT BOTH SIDES KNOW ABOUT, rather than a chosen few.
# cosmos yields twelve; the solar table lists eleven; the overlap is
# what can be tested, and it is now nine instead of five. Computing
# it rather than writing it down means extending either side extends
# the experiment automatically.
def _testable():
    tracked = set()
    for _pop, (y, _e, _f) in cosmos.YIELDS.items():
        tracked |= set(y)
    return tuple(sorted(tracked & (set(SOLAR) - {"other"})))


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
    t("structured_by_family", _families)
    t("reported_as_fit_not_prediction", _honest)
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
FAMILY = {"C": "CNO", "N": "CNO", "O": "CNO",
          "Ne": "Ne",
          "Mg": "alpha", "Si": "alpha", "S": "alpha", "Ca": "alpha",
          "Fe": "iron-peak"}


def by_family(rows=None):
    rows = rows or leave_one_out()
    out = {}
    for e, r in rows.items():
        out.setdefault(FAMILY.get(e, "?"), []).append((e, r["ratio"]))
    return {k: sorted(v) for k, v in out.items()}


def _families():
    """Is the residual one entry, or a whole nucleosynthetic channel?"""
    fam = by_family()
    means = {k: sum(r for _e, r in v) / len(v) for k, v in fam.items()}
    alpha = [r for _e, r in fam.get("alpha", [])]
    cno = [r for e, r in fam.get("CNO", []) if e in ("C", "O")]
    fe = dict(fam.get("iron-peak", [])).get("Fe")
    if not alpha or not cno or fe is None:
        raise ArithmeticError("not enough elements to group by family")
    if not all(r > 1.0 for r in alpha):
        return (f"the alpha elements are not uniformly over-predicted: "
                f"{fam['alpha']} -- the family reading does not hold")
    inside = min(alpha) <= fe <= max(alpha)
    return (f"grouped by what makes them: "
            + ", ".join(f"{k} {means[k]:.2f}x" for k in sorted(means))
            + f". Every alpha element is over-predicted "
              f"({min(alpha):.2f}-{max(alpha):.2f}x) and C and O are "
              f"under-predicted ({min(cno):.2f}-{max(cno):.2f}x). Iron at "
              f"{fe:.2f}x sits "
            + ("INSIDE" if inside else "outside")
            + " the alpha spread, so it is not the outlier five elements "
              "made it look like -- the error is a CHANNEL, not an entry")


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
