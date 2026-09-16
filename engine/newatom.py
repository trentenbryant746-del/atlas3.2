"""
Discovering that the basis is short, and what is missing from it.

The search found Kepler only because `sqrt` was handed to it. Without that
atom the search returns nothing -- and returns exactly the same nothing when
there is genuinely no law to find. Those are different situations and the
system could not tell them apart.

    Z -> atomic mass      no closed-form law exists       correct to fail
    a -> orbital period   a law exists, basis cannot say it

Distinguishing them takes two independent questions:

    IS IT LEARNABLE?   does ANY smooth function predict held-out points?
                       If a flexible fit generalises, a relationship is
                       there regardless of whether the basis can write it.
    IS IT EXPRESSIBLE?  does any expression over the current atoms fit?

    learnable + expressible   -> found, nothing missing
    learnable + NOT           -> THE BASIS IS SHORT. Characterise what is
                                 missing and propose it.
    not learnable             -> no law. Do not invent an atom to fit noise.

CHARACTERISING THE GAP. The shape of the residual says which operation is
absent, and the classic diagnostics are enough to name it:

    log y vs log x linear   power law      propose x^k
    log y vs x linear       exponential    propose exp
    y vs log x linear       logarithmic    propose log

A proposal is not accepted on the strength of a straight line. It is added
to the basis, the search is re-run, and it counts only if the law is then
found AND survives held-out validation. An atom that does not make anything
findable is not an atom, it is a parameter.
"""
from __future__ import annotations

import math
import statistics


def _lin_fit(xs, ys):
    """least squares slope, intercept, and R^2"""
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return 0.0, my, 0.0
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    inter = my - slope * mx
    ss_res = sum((y - (slope * x + inter)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot else 0.0
    return slope, inter, r2


def residual_profile(train, kind, param):
    """after the best parametric form is removed, what is left?

    A LAW leaves residuals that are tiny and randomly signed. A TREND leaves
    residuals that are larger and keep their sign in long runs, because the
    form is systematically wrong rather than noisily so. The Wald-Wolfowitz
    run count makes that quantitative: k independent signs give about
    (k+1)/2 runs, and far fewer means structure remains.
    """
    xs = [x[0] for x, _ in train]
    ys = [y for _, y in train]
    # the prediction must be built in the SAME space the form was fitted in.
    # Only `power` was handled, so an exponential was scored against a
    # straight line, left a huge systematic residual, and was misreported
    # as a trend. Every form now reconstructs its own prediction.
    pos = all(x > 0 for x in xs) and all(y > 0 for y in ys)
    if kind == "power" and pos:
        sl, ic, _ = _lin_fit([math.log(x) for x in xs], [math.log(y) for y in ys])
        pred = [math.exp(ic) * x ** sl for x in xs]
    elif kind == "exponential" and all(y > 0 for y in ys):
        sl, ic, _ = _lin_fit(xs, [math.log(y) for y in ys])
        pred = [math.exp(ic) * math.exp(sl * x) for x in xs]
    elif kind == "logarithmic" and all(x > 0 for x in xs):
        sl, ic, _ = _lin_fit([math.log(x) for x in xs], ys)
        pred = [sl * math.log(x) + ic for x in xs]
    else:
        sl, ic, _ = _lin_fit(xs, ys)
        pred = [sl * x + ic for x in xs]
    res = [(y - pp) / y for y, pp in zip(ys, pred) if y]
    if not res:
        return 1.0, 0, 1.0
    signs = [1 if r > 0 else -1 for r in res]
    runs = 1 + sum(1 for i in range(1, len(signs)) if signs[i] != signs[i - 1])
    return statistics.median(abs(r) for r in res), runs, (len(signs) + 1) / 2


def classify(train, r2_min=0.98, resid_max=0.01, runs_ratio_min=0.5):
    """-> ('LAW'|'TREND'|'NO STRUCTURE', evidence)

    Three signals, because no one of them separates all three cases:
      R^2            separates noise from structure, but a trend scores ~1 too
      residual size  separates a law (0.15%) from a trend (2.41%)
      sign runs      a trend's residual keeps its sign; 17 runs where 42 are
                     expected is a systematically wrong form
    """
    (kind, param, r2), _all = characterise(train)
    if r2 < r2_min:
        return "NO STRUCTURE", {"r2": r2, "kind": kind}
    med, runs, exp = residual_profile(train, kind, param)
    # A numerically exact fit has no residual to run a runs-test on. The
    # signs are floating-point dust, they clump, and the test read
    # y = 3x + 7 -- a perfect linear fit -- as "systematically wrong".
    if med < 1e-9:
        return "LAW", {"r2": r2, "kind": kind, "param": param, "resid": med,
                       "runs": runs, "expected_runs": exp, "exact": True}
    ratio = runs / exp if exp else 1.0
    if med <= resid_max and ratio >= runs_ratio_min:
        return "LAW", {"r2": r2, "kind": kind, "param": param,
                       "resid": med, "runs": runs, "expected_runs": exp}
    return "TREND", {"r2": r2, "kind": kind, "param": param,
                     "resid": med, "runs": runs, "expected_runs": exp}


def characterise(train):
    """-> (kind, parameter, r2). Which operation would close the gap."""
    xs = [x[0] for x, _ in train]
    ys = [y for _, y in train]
    cands = []
    if all(x > 0 for x in xs) and all(y > 0 for y in ys):
        k, _b, r2 = _lin_fit([math.log(x) for x in xs], [math.log(y) for y in ys])
        cands.append(("power", k, r2))
        k2, _b2, r22 = _lin_fit(xs, [math.log(y) for y in ys])
        cands.append(("exponential", k2, r22))
        k3, _b3, r23 = _lin_fit([math.log(x) for x in xs], ys)
        cands.append(("logarithmic", k3, r23))
    k4, _b4, r24 = _lin_fit(xs, ys)
    cands.append(("linear", k4, r24))
    cands.sort(key=lambda c: -c[2])
    return cands[0], cands


def propose(kind, param):
    """-> (name, unary fn) the atom to add, or None"""
    if kind == "power":
        k = round(param * 4) / 4          # snap to a quarter power
        if abs(k - 1.0) < 1e-9:
            return None
        return (f"x^{k}", lambda a, k=k: a ** k if a >= 0 or float(k).is_integer() else None)
    if kind == "exponential":
        return ("exp", lambda a: math.exp(a) if a < 60 else None)
    if kind == "logarithmic":
        return ("log", lambda a: math.log(a) if a > 0 else None)
    return None


def diagnose(train, held, search_fn, tol=0.02, verify_with=None):
    """the whole decision, with the verification of any proposal"""
    hits = search_fn(train, held)
    if hits:
        return {"verdict": "EXPRESSIBLE", "found": hits[0][0], "proposal": None}

    kindv, ev = classify(train)
    if kindv == "NO STRUCTURE":
        return {"verdict": "NO LAW", "why": f"best R^2 only {ev['r2']:.3f}",
                "proposal": None, "evidence": ev}
    if kindv == "TREND":
        return {"verdict": "TREND, NOT A LAW", "proposal": None, "evidence": ev,
                "why": (f"residual {ev['resid']:.2%} in {ev['runs']} sign runs "
                        f"where {ev['expected_runs']:.0f} are expected -- the "
                        f"form is systematically wrong, so no single atom "
                        f"closes it")}
    prop = propose(ev["kind"], ev["param"])
    if prop is not None and verify_with is not None:
        # VERIFY THE PROPOSAL. An atom that does not make the law findable
        # is not a discovery. The budget is DERIVED, not fixed: a new atom
        # needs room for the scale and offset wrapped around it, so the
        # search is retried at growing sizes. A fixed cap has bitten three
        # times in this repo -- each time the method was right and the
        # budget was the limit.
        name, fn = prop
        ok_at = None
        for size in (3, 5, 7, 9, 11):
            hits = verify_with(train, held, name, fn, size)
            if hits:
                ok_at = (size, len(hits), sum(1 for _, h in hits if h))
                break
        ev["verified"] = ok_at
        if ok_at is None:
            return {"verdict": "PROPOSAL UNVERIFIED", "proposal": prop,
                    "evidence": ev,
                    "why": (f"proposed {name!r} from the residual shape, but "
                            f"adding it did not make the law findable up to "
                            f"size 11 -- the shape may be coincidental")}
    if prop is None:
        # the form is a law AND the basis already has the operations for it,
        # so nothing is missing from the vocabulary -- the SEARCH could not
        # reach it. That is a budget problem, not a discovery.
        return {"verdict": "EXPRESSIBLE, SEARCH BUDGET TOO SMALL",
                "proposal": None, "evidence": ev,
                "why": (f"{ev['kind']} form with residual {ev['resid']:.2%} "
                        f"needs no new atom; raise max_size or the constant "
                        f"set instead")}
    v = ev.get("verified")
    return {"verdict": "BASIS SHORT (verified)" if v else "BASIS SHORT",
            "proposal": prop, "evidence": ev,
            "kind": ev["kind"], "param": ev["param"], "r2": ev["r2"],
            "why": (f"residual {ev['resid']:.2%}, {ev['runs']} sign runs vs "
                    f"{ev['expected_runs']:.0f} expected -- random, so the "
                    f"form is right and only the operation is missing")}
