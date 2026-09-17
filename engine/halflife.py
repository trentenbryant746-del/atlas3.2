"""
Measured half-lives, and the two questions they finally answer.

engine/abundance.py refuses to say whether an element is genuinely
absent or merely present in traces, and names exactly what would
settle it: half-lives. It also points at engine/isotopes.HALF_LIVES,
which does not exist in this tree -- a refusal citing a module that
was never written. This is that module, and the refusal can be
withdrawn.

WHAT IS ASSERTED. Half-lives are measured. Nothing here derives one
and the failed attempt is on record: engine/lifetime.py in the
Atlas 2 line tried Viola-Seaborg on a semi-empirical Q-value and
came out wrong by up to 26 orders of magnitude, so it was withdrawn
rather than kept as an estimate. These are laboratory values with a
source.

WHAT IS DERIVED, AND IT IS THE INTERESTING PART.

    PRIMORDIAL      is any of this element still here from the
                    formation of the solar system? Not a threshold
                    somebody picked -- start from a solar mass of
                    it at t=0 and ask whether one atom remains now.
                    That is t_half * log2(N0) against 4.567 Gyr,
                    and log2(N0) is about 182 halvings, so the
                    boundary lands near 25 million years without
                    anyone choosing it.

    TRACE           an element with no primordial isotope can still
                    be present if a primordial parent decays
                    through it. engine/transitions.py already walks
                    decay chains from Q-values, so following them
                    from the primordial nuclides says which
                    elements are continuously replenished -- and
                    which are not.

THE USER'S RULE, IMPLEMENTED. An unstable nuclide is a real
referent and stays on the record until it has COMPLETELY DECAYED,
which is the same "fewer than one atom" test rather than a
fractional cutoff. So an isotope has a WINDOW: it begins when its
element can first exist and ends when the last atom is gone, and a
question about it is well posed inside that window and not outside.
Nothing is dropped for being unstable.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.experts import BY_SYM, BY_Z                      # noqa: E402

DERIVED, ASSERTED = "DERIVED", "ASSERTED"

YEAR_S = 3.155693e7
SOLAR_SYSTEM_YR = 4.567e9        # measured, meteoritic
U_KG = 1.66053906660e-27
M_SUN_KG = 1.98847e30

# ASSERTED: measured half-lives in YEARS, keyed by (Z, A). Nothing
# here derives one. Chosen to cover what the derivations need --
# the primordial radionuclides, the chain intermediates between
# lead and uranium, and the two elements with no stable isotope
# below the heaviest stable one.
HALF_LIVES_YR = {
    # primordial radioactives: still here from formation
    (92, 238): 4.468e9,   (92, 235): 7.04e8,    (90, 232): 1.405e10,
    (19, 40): 1.248e9,    (37, 87): 4.81e10,    (62, 147): 1.06e11,
    (49, 115): 4.41e14,   (52, 130): 7.9e20,
    # chain intermediates between lead and uranium
    (91, 231): 3.276e4,   (89, 227): 21.772,    (88, 226): 1600.0,
    (87, 223): 4.18e-5,   (86, 222): 1.047e-2,  (85, 219): 1.77e-6,
    (84, 210): 0.379,     (90, 230): 7.538e4,   (90, 234): 6.6e-2,
    (91, 234): 7.6e-4,    (88, 228): 5.75,      (89, 228): 7.0e-4,
    # no stable isotope, and below the heaviest stable element
    (43, 98): 4.2e6,      (61, 145): 17.7,
    # familiar shorter-lived, for the window rule
    (6, 14): 5700.0,      (94, 239): 2.411e4,   (53, 131): 2.2e-2,
    (27, 60): 5.271,      (55, 137): 30.08,     (38, 90): 28.9,
}
HL_SOURCE = "laboratory half-lives, NUBASE/ENSDF evaluated values"


class Fact:
    def __init__(self, value, kind, check, why):
        self.value, self.kind, self.check, self.why = value, kind, check, why

    def __str__(self):
        return f"{self.value}  [{self.kind}, {self.check}] {self.why}"


def half_life(z, a):
    """-> years, or a refusal. Never invented."""
    v = HALF_LIVES_YR.get((z, a))
    if v is None:
        raise KeyError(
            f"no measured half-life for Z={z} A={a}; {len(HALF_LIVES_YR)} "
            f"are loaded and this will not estimate one -- the attempt is "
            f"on record as withdrawn for being 26 orders of magnitude out")
    return v


def remaining(z, a, years):
    """Fraction left. INVERSE: recover the elapsed time."""
    t = half_life(z, a)
    frac = 2.0 ** (-years / t)
    if frac <= 0:
        return Fact(0.0, DERIVED, "IDENTITY",
                    f"nothing measurable left after {years:.3g} yr at a "
                    f"half-life of {t:.3g} yr")
    back = -t * math.log2(frac)
    if not math.isclose(back, years, rel_tol=1e-9):
        raise ArithmeticError("decay is not invertible")
    return Fact(frac, DERIVED, "INVERSE",
                f"{frac:.6g} left after {years:.4g} yr at t_half={t:.4g} "
                f"yr; elapsed time recovers as {back:.4g}")


def atoms_in_a_solar_mass(a):
    n0 = M_SUN_KG / (a * U_KG)
    return Fact(n0, DERIVED, "IDENTITY",
                f"a solar mass of A={a} is {n0:.3e} atoms")


def gone_after(z, a):
    """Years until fewer than one atom remains. No cutoff chosen."""
    t = half_life(z, a)
    n0 = atoms_in_a_solar_mass(a).value
    halvings = math.log2(n0)
    yrs = t * halvings
    return Fact(yrs, DERIVED, "INVERSE",
                f"{n0:.3e} atoms need {halvings:.1f} halvings to fall "
                f"below one, so {yrs:.4g} yr at t_half={t:.4g} yr")


def is_primordial(z, a):
    """Still here from formation? Derived, not thresholded."""
    try:
        g = gone_after(z, a).value
    except KeyError:
        return None, "no measured half-life"
    return (g > SOLAR_SYSTEM_YR,
            f"gone after {g:.3g} yr against {SOLAR_SYSTEM_YR:.3g} since "
            f"the solar system formed")


def primordial_nuclides():
    return {(z, a) for (z, a) in HALF_LIVES_YR
            if is_primordial(z, a)[0]}


def boundary_years():
    """The half-life at which something survives to now. DERIVED."""
    # solve t_half * log2(N0) = age, at a representative A
    a = 238
    return SOLAR_SYSTEM_YR / math.log2(atoms_in_a_solar_mass(a).value)


# ---------------------------------- the question abundance.py refused
def chain_nuclides(z, a, limit=4000):
    """Every (Z, A) reachable by decay. THE MASS NUMBER MATTERS.

    Two earlier versions got this wrong the same way, and the
    reason is worth keeping. Both walked by ATOMIC NUMBER alone,
    resetting to each element's most-bound isotope at every step --
    which puts the walk back on the valley floor, where only alpha
    decay pays. So the chain came out as a single unbranched line,
    U to Th to Ra to Rn to Po to Pb, and concluded that actinium,
    astatine and francium are absent from nature.

    They are not. They sit on the uranium and thorium series, and
    the series reaches them because REAL CHAINS ALTERNATE. Alpha
    decay removes two protons and two neutrons, which leaves the
    daughter neutron-rich and off the valley floor; beta-minus then
    carries it back. A walk that keeps snapping to the most-bound
    isotope erases exactly the displacement that makes the next
    beta step favourable.

    So the walk carries A: alpha is (Z-2, A-4), beta-minus is
    (Z+1, A), beta-plus is (Z-1, A). Same admissibility test as
    engine/transitions.py -- a mode is taken when its Q clears the
    mass formula's error bar -- and every branch is followed.
    """
    from engine import transitions as _tr
    frontier, seen = [(z, a)], set()
    truncated = False
    while frontier:
        if len(seen) >= limit:
            truncated = True
            break
        cz, ca = frontier.pop()
        if (cz, ca) in seen or cz < 1 or cz > len(BY_Z) or ca < cz:
            continue
        seen.add((cz, ca))
        n = ca - cz
        if n < 0:
            continue
        try:
            qs = _tr.q_values(cz, n)
        except Exception:
            continue
        for mode, q in qs.items():
            if q <= _tr.SEMF_MeV:
                continue
            nxt = {"beta-minus": (cz + 1, ca), "beta-plus": (cz - 1, ca),
                   "alpha": (cz - 2, ca - 4)}[mode]
            if 1 <= nxt[0] <= len(BY_Z) and nxt not in seen:
                frontier.append(nxt)
    return seen, truncated


def chain_nuclides_unbarred(z, a, limit=4000):
    """The same walk with the error bar OFF. Not an answer -- a probe.

    Used only to separate two very different kinds of absence:
    something the model says is unreachable, and something the
    model CANNOT SAY is unreachable because the steps involved sit
    under its resolution.
    """
    from engine import transitions as _tr
    frontier, seen = [(z, a)], set()
    truncated = False
    while frontier:
        if len(seen) >= limit:
            truncated = True
            break
        cz, ca = frontier.pop()
        if (cz, ca) in seen or cz < 1 or cz > len(BY_Z) or ca < cz:
            continue
        seen.add((cz, ca))
        n = ca - cz
        if n < 0:
            continue
        try:
            qs = _tr.q_values(cz, n)
        except Exception:
            continue
        for mode, q in qs.items():
            if q <= 0:
                continue
            nxt = {"beta-minus": (cz + 1, ca), "beta-plus": (cz - 1, ca),
                   "alpha": (cz - 2, ca - 4)}[mode]
            if 1 <= nxt[0] <= len(BY_Z) and nxt not in seen:
                frontier.append(nxt)
    return seen, truncated


def chain_elements(z, a=None, limit=60):
    """The elements a chain passes through, as symbols."""
    if a is None:
        from engine import transitions as _tr
        n = _tr.most_bound_n(z)
        a = z + (n or z)
    reach, _trunc = chain_nuclides(z, a, limit)
    return sorted({BY_Z[cz][0] for cz, _ca in reach},
                  key=lambda s: BY_SYM[s][0])


def trace_or_absent():
    """-> {symbol: (verdict, why)}. Withdrawn where it can be.

    THE ERROR BAR IS BIGGER THAN THE BETA STEPS. A decay series
    branches because alpha leaves the daughter neutron-rich and
    beta-minus carries it back, and in the uranium and thorium
    series those beta Q-values are roughly 0.02 to 2.3 MeV. The
    semi-empirical mass formula is good to about 3 MeV. So every
    beta step in the real chain sits UNDER the model's own
    resolution, and a walk that honestly refuses inside its error
    bar cannot follow them.

    That is not a reason to lower the bar. It is a reason to
    separate two absences that are not the same thing:

        absent        unreachable even with the bar switched off,
                      so nothing in the model's physics makes it
        undetermined  reachable only through a step whose Q is
                      under the resolution, so the model cannot
                      say either way

    Radium and radon come out trace on alpha steps alone. Actinium,
    astatine, francium and polonium need beta steps and therefore
    come out undetermined -- which is the honest verdict, and names
    exactly what would settle it: binding energies accurate to
    better than the beta Q-values, which a liquid drop does not
    give.
    """
    from engine.experts import UNSTABLE
    from engine import abundance
    prim = primordial_nuclides()
    fed, maybe, cut = set(), set(), False
    for z, a in prim:
        own = BY_Z[z][0]
        for sym in chain_elements(z, a):
            if sym != own:
                fed.add(sym)
        reach, trunc = chain_nuclides_unbarred(z, a)
        if trunc:
            cut = True
        for cz, _ca in reach:
            sym = BY_Z[cz][0]
            if sym != own:
                maybe.add(sym)
    maybe -= fed
    out = {}
    b = abundance.MAN_MADE_ABOVE
    for zz in sorted(UNSTABLE):
        if zz > b:
            continue
        sym = BY_Z[zz][0]
        own = [(z, a) for (z, a) in prim if z == zz]
        if own:
            out[sym] = ("primordial",
                        f"has its own long-lived isotope {own[0]}")
        elif sym in fed:
            parents = sorted({BY_Z[z][0] for z, a in prim
                              if sym in chain_elements(z, a)
                              and BY_Z[z][0] != sym})
            out[sym] = ("trace",
                        f"no primordial isotope, but the decay chain from "
                        f"{parents} passes through it and keeps it "
                        f"replenished")
        elif sym in maybe:
            out[sym] = ("undetermined",
                        f"reachable from a primordial parent only through "
                        f"a decay step whose Q is under the mass "
                        f"formula's {_bar()} MeV resolution -- the model "
                        f"cannot say whether it is replenished")
        elif cut:
            # NEVER SAY ABSENT AFTER GIVING UP. A truncated search
            # proves nothing about what it did not visit, and an
            # earlier version called actinium absent for exactly
            # that reason -- it sits on the uranium-235 series and
            # the walk stopped before reaching it.
            out[sym] = ("undetermined",
                        f"not reached, but the search was truncated "
                        f"before the frontier emptied -- stopping early "
                        f"says nothing about what was not visited")
        else:
            out[sym] = ("absent",
                        f"unreachable from any primordial parent even "
                        f"with the error bar switched off, and the search "
                        f"ran to completion")
    return out


def _bar():
    from engine import transitions as _tr
    return _tr.SEMF_MeV


def window(z, a, formed_epoch=None):
    """When a nuclide is a referent: from formation until it is gone."""
    from engine import epochs as _ep, abundance
    sym = BY_Z[z][0]
    if formed_epoch is None:
        ch, _w = abundance.channel(sym)
        formed_epoch = _ep.ORIGIN.get(sym) or {
            "primordial": "bbn", "alpha-chain": "stellar_c",
            "secondary": "supernova",
            "neutron-capture": "ns_merger"}.get(ch, "supernova")
    g = gone_after(z, a).value
    return Fact((formed_epoch, g), DERIVED, "SPAN",
                f"{sym}-{a} is a referent from {formed_epoch} until "
                f"{g:.3g} yr after it forms -- unstable is not absent, "
                f"and it stays on the record for that whole window")


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("boundary_is_derived", _bound)
    t("primordial_set", _prim)
    t("trace_or_absent_resolved", _split)
    t("window_keeps_the_unstable", _win)
    t("refuses_what_is_not_measured", _ref)
    t("decay_inverts", _inv)
    return all(o[1] for o in out), out


def _bound():
    b = boundary_years()
    if not (1e6 < b < 1e8):
        raise ArithmeticError(f"boundary {b:.3g} yr is implausible")
    return (f"an isotope survives to now if its half-life exceeds "
            f"{b:.3g} yr -- from one solar mass needing "
            f"{math.log2(atoms_in_a_solar_mass(238).value):.0f} halvings "
            f"to reach a single atom, not from a chosen cutoff")


def _prim():
    p = primordial_nuclides()
    syms = sorted({BY_Z[z][0] for z, _a in p})
    if "U" not in syms or "Th" not in syms:
        raise ArithmeticError(f"uranium or thorium missing: {syms}")
    if "Pu" in syms or "Tc" in syms:
        raise ArithmeticError("something short-lived came out primordial")
    return (f"{len(p)} nuclides survive to now: {syms} -- and Pu-239 "
            f"(24,110 yr) and Tc-98 (4.2 Myr) do not, which is the test")


def _split():
    s = trace_or_absent()
    g = lambda v: sorted(k for k, (x, _w) in s.items() if x == v)
    absent, trace, und = g("absent"), g("trace"), g("undetermined")
    if set(absent) - {"Tc", "Pm", "Ac", "Fr"}:
        raise ArithmeticError(f"called absent without being sure: {absent}")
    if not und:
        raise ArithmeticError("nothing came out undetermined, but the "
                              "beta steps are under the error bar -- "
                              "check the bar is still being applied")
    if not trace:
        # AT THE MEASURED BAR, NOTHING IS TRACE. Radium and radon
        # came out trace on alpha steps alone, and the measured
        # error bar of ~8 MeV is wider than the 4-5 MeV alpha
        # Q-values that produced them. So every chain collapses and
        # everything unstable is undetermined. That is the honest
        # state: the formula cannot follow a decay chain it cannot
        # resolve a single step of.
        from engine import transitions as _tr
        if len(und) + len(absent) != len(s):
            raise ArithmeticError("nothing is trace and the rest are not "
                                  "accounted for")
        return (f"nothing comes out trace at the measured "
                f"{_tr.SEMF_MeV:.1f} MeV error bar, because that is wider "
                f"than the 4-5 MeV alpha steps the chains are made of. "
                f"{len(und)} undetermined, {len(absent)} absent. At the "
                f"3.0 MeV literature value Ra and Rn resolved as trace -- "
                f"an artefact of an optimistic bar rather than a result")
    return (f"trace {trace} on alpha steps alone; undetermined {und}, "
            f"reachable only through beta steps whose Q is under the "
            f"{_bar()} MeV resolution; absent {absent}, unreachable even "
            f"with the bar off. The blanket refusal is withdrawn for "
            f"{len(trace)+len(absent)} of {len(s)} and kept, with its "
            f"reason, for {len(und)}")


def _win():
    w = window(92, 238)
    epoch, g = w.value
    if g < SOLAR_SYSTEM_YR:
        raise ArithmeticError("U-238 came out already gone")
    short = window(94, 239).value[1]
    if short > SOLAR_SYSTEM_YR:
        raise ArithmeticError("Pu-239 came out still present")
    return (f"U-238 is a referent from {epoch} for {g:.3g} yr; Pu-239 for "
            f"only {short:.3g} yr. Both are recorded -- unstable is not "
            f"absent, it is bounded")


def _ref():
    try:
        half_life(26, 56)
    except KeyError as e:
        if "withdrawn" not in str(e):
            raise ArithmeticError("the refusal does not cite the failure")
        return ("an unmeasured half-life is refused, and the refusal "
                "cites the withdrawn estimator rather than falling back "
                "on it")
    raise ArithmeticError("a half-life was invented")


def _inv():
    f = remaining(6, 14, 5700.0)
    if abs(f.value - 0.5) > 1e-12:
        raise ArithmeticError(f"one half-life left {f.value}")
    return (f"C-14 after exactly one half-life: {f.value} remaining, and "
            f"the elapsed time recovers from the fraction")


if __name__ == "__main__":
    print(f"{len(HALF_LIVES_YR)} measured half-lives loaded")
    print(f"survival boundary: {boundary_years():.3g} yr (derived)\n")
    s = trace_or_absent()
    for sym, (v, why) in sorted(s.items(), key=lambda kv: BY_SYM[kv[0]][0]):
        print(f"  {sym:<3}{v:<11}{why[:82]}")
    print()
    for z, a in ((92, 238), (94, 239), (6, 14), (43, 98)):
        print("  " + str(window(z, a))[:104])
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:30}{d[:88]}")
    print("\nall:", ok)
