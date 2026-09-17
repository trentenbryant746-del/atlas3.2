"""
Solar abundances for every naturally occurring element, and the
pattern that catches a typo in them.

engine/mixtures.OBSERVED listed eleven elements, so the dilution
experiment could be over-constrained at most eleven ways, and in
practice nine. That was a limit of a table, and it produced a wrong
conclusion once already: with five elements iron looked like the
bad yield, and with nine it turned out to be an entire
nucleosynthetic channel. A table that small can misinform.

So this holds all 83 elements that occur naturally in measurable
quantity -- hydrogen through uranium, minus technetium and
promethium, which have no stable isotope and are essentially absent,
and minus the man-made elements above uranium, which are not part of
any universe this repo simulates.

ASSERTED IN DEX, DERIVED IN MASS. Abundances are quoted the way
astronomers measure them: A(X) = log10(N_X / N_H) + 12, so hydrogen
is 12 by definition. Those numbers are the assertion, with a source.
The mass fractions everything else uses are DERIVED from them with
the atomic weights already in engine/experts.py -- so the conversion
is arithmetic this repo does rather than a second table to get
wrong.

THE CHECK THAT CATCHES TYPOS: ODDO-HARKINS. Elements with an even
atomic number are more abundant than their odd neighbours, usually
by a factor of a few to ten. The reason is nuclear: even-Z nuclei
pair their protons and are more tightly bound, so nucleosynthesis
favours them and they survive better. It holds across the whole
table with a handful of known exceptions, so a mistyped value shows
up as an element breaking a rule it has no business breaking.

That is the point of including it. A large asserted table is a
liability -- 83 numbers, and any of them could be wrong. Oddo-Harkins
is a pattern the data must satisfy for reasons independent of the
values, which makes it a check rather than a restatement. So is the
overall decline with Z, and so is the iron peak standing above its
neighbours.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.experts import BY_SYM, BY_Z                      # noqa: E402

ASSERTED, DERIVED = "ASSERTED", "DERIVED"

# ASSERTED: photospheric abundances on the astronomical dex scale,
# A(X) = log10(N_X/N_H) + 12. Meteoritic values where the photosphere
# does not give a reliable line. Source below.
DEX = {
    "H": 12.00, "He": 10.93, "Li": 1.05, "Be": 1.38, "B": 2.70,
    "C": 8.43, "N": 7.83, "O": 8.69, "F": 4.56, "Ne": 7.93,
    "Na": 6.24, "Mg": 7.60, "Al": 6.45, "Si": 7.51, "P": 5.41,
    "S": 7.12, "Cl": 5.50, "Ar": 6.40, "K": 5.03, "Ca": 6.34,
    "Sc": 3.15, "Ti": 4.95, "V": 3.93, "Cr": 5.64, "Mn": 5.43,
    "Fe": 7.50, "Co": 4.99, "Ni": 6.22, "Cu": 4.19, "Zn": 4.56,
    "Ga": 3.04, "Ge": 3.65, "As": 2.30, "Se": 3.34, "Br": 2.54,
    "Kr": 3.25, "Rb": 2.52, "Sr": 2.87, "Y": 2.21, "Zr": 2.58,
    "Nb": 1.46, "Mo": 1.88, "Ru": 1.75, "Rh": 0.91, "Pd": 1.57,
    "Ag": 0.94, "Cd": 1.71, "In": 0.80, "Sn": 2.04, "Sb": 1.01,
    "Te": 2.18, "I": 1.55, "Xe": 2.24, "Cs": 1.08, "Ba": 2.18,
    "La": 1.10, "Ce": 1.58, "Pr": 0.72, "Nd": 1.42, "Sm": 0.96,
    "Eu": 0.52, "Gd": 1.07, "Tb": 0.30, "Dy": 1.10, "Ho": 0.48,
    "Er": 0.92, "Tm": 0.10, "Yb": 0.84, "Lu": 0.10, "Hf": 0.85,
    "Ta": -0.12, "W": 0.85, "Re": 0.26, "Os": 1.40, "Ir": 1.38,
    "Pt": 1.62, "Au": 0.92, "Hg": 1.17, "Tl": 0.90, "Pb": 1.75,
    "Bi": 0.65, "Th": 0.02, "U": -0.54,
}
DEX_SOURCE = ("solar photospheric and meteoritic abundances, Asplund "
              "et al. compilation, on the A(X) = log10(N_X/N_H) + 12 scale")

# WHICH ELEMENTS NATURE MAKES, DERIVED FROM THE TABLE THAT ALREADY
# KNOWS. This was two hand-written entries and the number 92, typed
# by me -- an inference supplied instead of computed. engine/experts
# already records UNSTABLE, the set of atomic numbers with no stable
# isotope, and everything needed follows from it:
#
#   man-made boundary   the smallest Z from which EVERY heavier
#                       element is unstable. Below it nature still
#                       manages something; at and above it, nothing
#                       survives long enough to be found.
#   heaviest stable     the largest Z not in UNSTABLE below that.
#   trace by decay      unstable, but lying BETWEEN the heaviest
#                       stable element and the heaviest primordial
#                       one -- so a uranium or thorium chain passes
#                       through it and keeps replenishing it.
#   truly absent        unstable and BELOW the heaviest stable
#                       element, so no long-lived parent decays into
#                       it and nothing keeps it topped up.
#
# That last distinction is the interesting one and it comes out of
# position alone: technetium and promethium are absent because
# nothing upstream makes them, while polonium through actinium exist
# in traces because they sit on the way down from uranium.
def _boundary():
    from engine.experts import UNSTABLE, PT
    top = len(PT)
    z = top
    while z > 1 and (z - 1) in UNSTABLE:
        z -= 1
    return z - 1


def heaviest_stable():
    from engine.experts import UNSTABLE
    b = _boundary()
    return max(z for z in range(1, b + 1) if z not in UNSTABLE)


def without_stable_isotope():
    """-> {symbol: why}. Everything the table marks unstable below 93."""
    from engine.experts import UNSTABLE, BY_Z
    b = _boundary()
    return {BY_Z[z][0]: f"Z={z} has no stable isotope"
            for z in sorted(UNSTABLE) if z <= b}


def trace_by_decay():
    """REFUSED. The table cannot tell trace-present from truly absent.

    This tried to derive the split by position: an unstable element
    between the heaviest stable one and the heaviest primordial one
    is fed by a uranium or thorium chain, and one below has no
    parent. The derivation runs and returns nothing, because the
    premise is false in the source data.

    engine/experts.UNSTABLE means "has no stable isotope", and that
    is not the same property. Uranium and thorium have no stable
    isotope and are nevertheless primordial -- their half-lives are
    comparable to the age of the Earth, so they are still here. The
    table does not mark them unstable, which makes the heaviest
    stable element come out as Z=92 and collapses the window to
    nothing.

    So the split is not derivable from what this repo records, and
    polonium through actinium are reported as "no stable isotope"
    rather than as trace-present, which is the weaker claim the data
    supports. What would settle it is HALF-LIVES:
    engine/isotopes.HALF_LIVES exists for exactly this and is empty.
    An element is primordial if some isotope's half-life is a
    reasonable fraction of the age of the Earth, and trace if a
    long-lived parent decays through it.

    PARTIALLY WITHDRAWN. engine/halflife.py now loads measured
    half-lives and does exactly that, and it resolves some of it:
    radium and radon come out trace on alpha steps alone, and
    technetium comes out absent with the search run to completion.
    What is still refused is the rest -- actinium, astatine,
    francium, polonium, promethium -- because reaching them needs
    beta steps whose Q-values are 0.02 to 2.3 MeV, under the mass
    formula's own 3 MeV resolution. The refusal is narrower and its
    reason is now specific.
    """
    try:
        from engine import halflife
        return {k: v[1] for k, v in halflife.trace_or_absent().items()
                if v[0] == "trace"}
    except Exception:
        return {}


ABSENT_REASON = ("no stable isotope; whether an element is genuinely "
                 "absent or present in traces from a decay chain needs "
                 "half-lives, which engine/isotopes.HALF_LIVES would hold "
                 "and does not")


def absent_naturally():
    return without_stable_isotope()


ABSENT = absent_naturally()
MAN_MADE_ABOVE = _boundary()


def naturally_occurring():
    """Every element a universe makes on its own. DERIVED from the table."""
    out = []
    for z in range(1, MAN_MADE_ABOVE + 1):
        sym = BY_Z[z][0]
        if sym in ABSENT:
            continue
        out.append(sym)
    return out


def mass_fractions():
    """dex -> mass fraction. DERIVED, using the repo's atomic weights."""
    num = {}
    for sym, a in DEX.items():
        if sym not in BY_SYM:
            raise KeyError(f"{sym} is not in the periodic table")
        weight = BY_SYM[sym][1][2]
        num[sym] = 10.0 ** (a - 12.0) * weight     # relative to hydrogen
    total = sum(num.values())
    return {s: v / total for s, v in num.items()}


def metallicity():
    """Z: everything heavier than helium, by mass. DERIVED."""
    mf = mass_fractions()
    return sum(v for s, v in mf.items() if s not in ("H", "He"))


# ------------------------------------- which process made it, DERIVED
# THE CHANNEL IS NOT A TABLE I WROTE. An earlier version of the
# dilution experiment carried a FAMILY dict assigning each element
# to CNO, alpha, iron-peak or r-process, and that was an inference
# typed in by hand -- exactly the thing this repo is supposed to
# derive and then confirm, rather than supply.
#
# It follows from the binding curve engine/nucleo.py already
# computes. Fusion releases energy only while binding per nucleon is
# rising, so the peak is a hard boundary:
#
#   Z <= 3            made in the Big Bang; epochs.ORIGIN says so
#   Z >  Z_peak       fusion COSTS energy here, so no star makes it
#                     by fusing -- it has to be neutron capture
#   even, 6..Z_peak   reachable from carbon by adding alpha
#                     particles, which is the alpha chain
#   otherwise         a secondary product, made from seed nuclei
#                     rather than built up directly
#
# Every branch is a consequence of the curve and of parity. The only
# thing asserted is the arithmetic of what an alpha particle is.
_PEAK = None


def peak_z():
    """Where fusion stops paying, from engine/nucleo.py. DERIVED."""
    global _PEAK
    if _PEAK is None:
        from engine.nucleo import iron_peak
        _PEAK = iron_peak()["Z"]
    return _PEAK


def channel(sym):
    """-> (name, why). What process can have made this element."""
    if sym not in BY_SYM:
        raise KeyError(f"{sym} is not an element")
    z = BY_SYM[sym][0]
    pk = peak_z()
    from engine import epochs as _ep
    if sym in _ep.ORIGIN and _ep.ORIGIN[sym] == "bbn":
        return "primordial", (f"epochs.ORIGIN puts {sym} at bbn, so it "
                              f"predates any star")
    if z <= 3:
        return "primordial", f"Z={z} is light enough to be made in the bang"
    if z > pk:
        return "neutron-capture", (
            f"Z={z} is past the binding peak at Z={pk}, so fusing up to it "
            f"absorbs energy instead of releasing it -- no star builds it "
            f"by fusion, and it must be captured onto a seed")
    if z % 2 == 0 and z >= 6:
        return "alpha-chain", (
            f"Z={z} is even and at or below the peak, so it is reachable "
            f"from carbon by adding alpha particles")
    return "secondary", (
        f"Z={z} is odd and below the peak, so it is not on the alpha "
        f"chain -- it is made from seed nuclei rather than built up")


def channels():
    """-> {channel: [symbols]} over everything with an abundance."""
    out = {}
    for sym in DEX:
        out.setdefault(channel(sym)[0], []).append(sym)
    return {k: sorted(v, key=lambda s: BY_SYM[s][0]) for k, v in out.items()}


# ------------------------------------------------- checks on the table
def oddo_harkins(tol=0):
    """-> (violations, tested). Even Z should beat its odd neighbours."""
    bad, tested = [], 0
    for sym, a in sorted(DEX.items(), key=lambda kv: BY_SYM[kv[0]][0]):
        z = BY_SYM[sym][0]
        if z % 2 == 1 or z < 6:
            continue
        nb = [BY_Z[z + d][0] for d in (-1, 1)
              if 1 <= z + d <= MAN_MADE_ABOVE and BY_Z[z + d][0] in DEX]
        if not nb:
            continue
        tested += 1
        for n in nb:
            if DEX[n] > a + tol:
                bad.append((sym, z, a, n, DEX[n]))
    return bad, tested


def declines_with_z():
    """Heavier is rarer, over the table as a whole. DERIVED trend."""
    pts = [(BY_SYM[s][0], a) for s, a in DEX.items()]
    n = len(pts)
    mx = sum(z for z, _a in pts) / n
    my = sum(a for _z, a in pts) / n
    num = sum((z - mx) * (a - my) for z, a in pts)
    den = sum((z - mx) ** 2 for z, _a in pts)
    return num / den


def iron_peak_stands_out():
    """Fe must exceed its neighbours by a wide margin. DERIVED."""
    fe = DEX["Fe"]
    nb = [DEX[BY_Z[z][0]] for z in range(22, 32)
          if BY_Z[z][0] in DEX and BY_Z[z][0] != "Fe"]
    return fe - max(nb), fe - (sum(nb) / len(nb))


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("coverage", _cov)
    t("oddo_harkins", _oh)
    t("declines_with_z", _decl)
    t("iron_peak", _fe)
    t("metallicity", _met)
    t("natural_boundary_derived", _nat)
    t("channels_are_derived", _chan)
    t("fusion_stops_at_the_peak", _stop)
    t("the_trace_refusal_is_exercised", _stranded)
    return all(o[1] for o in out), out


def _cov():
    nat = set(naturally_occurring())
    have = set(DEX)
    missing = sorted(nat - have, key=lambda s: BY_SYM[s][0])
    extra = sorted(have - nat)
    if extra:
        raise ArithmeticError(f"abundances for non-natural elements: {extra}")
    return (f"{len(have)} elements with abundances; {len(nat)} occur "
            f"naturally up to Z={MAN_MADE_ABOVE} by the derived boundary; "
            f"{len(missing)} without a value ({missing}) -- protactinium, "
            f"which has no stable isotope and is not marked unstable by "
            f"the periodic table, so it falls in the same gap "
            f"trace_by_decay() refuses to resolve")


def _oh():
    bad, tested = oddo_harkins()
    rate = 1 - len(bad) / tested if tested else 0
    if rate < 0.85:
        raise ArithmeticError(
            f"Oddo-Harkins holds for only {rate:.0%} of {tested} even-Z "
            f"elements -- the table is probably mistyped: {bad[:5]}")
    ex = ", ".join(f"{s} under {n}" for s, _z, _a, n, _an in bad[:4])
    return (f"even-Z beats its odd neighbours for {tested - len(bad)} of "
            f"{tested} tested ({rate:.0%}); exceptions {ex or 'none'}. A "
            f"pattern the values must satisfy for nuclear reasons, so a "
            f"mistyped abundance breaks it")


def _decl():
    slope = declines_with_z()
    if slope >= 0:
        raise ArithmeticError(f"abundance does not fall with Z: {slope:+.4f}")
    return (f"abundance falls {abs(slope):.3f} dex per proton across the "
            f"table -- about {10 ** (abs(slope) * 10):.0f}x per ten "
            f"elements")


def _fe():
    over_max, over_mean = iron_peak_stands_out()
    if over_max <= 0:
        raise ArithmeticError("iron does not stand above its neighbours")
    return (f"iron sits {over_max:.2f} dex above the next most abundant of "
            f"Ti-Zn and {over_mean:.2f} above their mean -- a factor of "
            f"{10 ** over_mean:.0f}, which is the binding-energy peak "
            f"showing up in a table of counts")


def _nat():
    """The boundary and the gaps must come from the table, not from me."""
    from engine.experts import UNSTABLE, BY_Z
    b, hs = MAN_MADE_ABOVE, heaviest_stable()
    if any(z not in UNSTABLE for z in range(b + 1, len(BY_Z) + 1)):
        raise ArithmeticError(f"something above Z={b} is stable, so it is "
                              f"not the man-made boundary")
    if b in UNSTABLE:
        raise ArithmeticError(f"Z={b} is itself unstable")
    gone = ABSENT
    # every element with an abundance must be one nature actually makes
    for sym in DEX:
        z = BY_SYM[sym][0]
        if z > b:
            raise ArithmeticError(f"{sym} is past the man-made boundary")
        if sym in gone:
            raise ArithmeticError(f"{sym} has an abundance but nothing "
                                  f"replenishes it")
    return (f"everything above Z={b} is man-made, derived: it is the "
            f"smallest Z from which every heavier element is unstable. "
            f"{len(gone)} elements at or below it have no stable isotope "
            f"({sorted(gone)}). Whether each is truly absent or present "
            f"in traces is REFUSED -- see trace_by_decay(); the table "
            f"records 'no stable isotope', which uranium also satisfies "
            f"while being primordial")


def _chan():
    ch = channels()
    pk = peak_z()
    # The classifier must put things where physics does, and the
    # test of that is not a list of expected answers -- it is that
    # no element beyond the peak is called fusible and none below it
    # is called captured.
    for sym in ch.get("neutron-capture", []):
        if BY_SYM[sym][0] <= pk:
            raise ArithmeticError(f"{sym} is at or below the peak and was "
                                  f"called neutron-capture")
    for name in ("alpha-chain", "secondary"):
        for sym in ch.get(name, []):
            if BY_SYM[sym][0] > pk:
                raise ArithmeticError(f"{sym} is past the peak and was "
                                      f"called {name}")
    return (", ".join(f"{k} {len(v)}" for k, v in sorted(ch.items()))
            + f"; the split is the binding peak at Z={pk}, derived in "
              f"engine/nucleo.py and not written down here")


def _stop():
    """The boundary has to be real: binding must fall past the peak."""
    from engine.nucleo import binding_per_nucleon
    pk = peak_z()

    def best(z):
        return max(binding_per_nucleon(z, n) for n in range(0, 3 * z + 4))
    top = best(pk)
    rising = [z for z in range(6, pk) if best(z) > top]
    falling = all(best(z) < top for z in range(pk + 1, 93, 6))
    if rising or not falling:
        raise ArithmeticError(f"the peak is not a peak: {rising} exceed it")
    return (f"binding per nucleon tops out at {top:.3f} MeV at Z={pk}; "
            f"nothing below exceeds it and everything sampled above falls "
            f"short, so 'fusion stops here' is a measured property of the "
            f"curve rather than a rule about iron")


def _met():
    z = metallicity()
    if not (0.008 < z < 0.025):
        raise ArithmeticError(f"metallicity {z:.4f} is nowhere near solar")
    mf = mass_fractions()
    return (f"X={mf['H']:.4f} Y={mf['He']:.4f} Z={z:.4f}, derived from the "
            f"dex table and the repo's atomic weights; accepted solar is "
            f"about X=0.7381 Y=0.2485 Z=0.0134")



def _stranded():
    """Wires trace_by_decay, which is a REFUSAL nobody called."""
    r = trace_by_decay()
    if not isinstance(r, dict) or not r:
        raise ArithmeticError(f"expected findings, got {type(r).__name__}")
    k = sorted(r)[0]
    return (f"its docstring opens with REFUSED and it returns "
            f"FINDINGS -- {len(r)} of them, e.g. {k}: {r[k][:76]}. "
            f"The refusal is real but partial: position alone cannot "
            f"split trace from absent, and yet the decay chains "
            f"settle some cases outright. Nothing called this, so "
            f"nobody had noticed the docstring describes only half "
            f"of what the function does")

if __name__ == "__main__":
    mf = mass_fractions()
    print(f"{len(DEX)} naturally occurring elements with solar abundances")
    print(f"X={mf['H']:.4f}  Y={mf['He']:.4f}  Z={metallicity():.4f}")
    print()
    top = sorted(mf.items(), key=lambda kv: -kv[1])[:12]
    print("  most abundant by mass:")
    for s, v in top:
        print(f"    {s:<4}{v:.6f}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:18}{d[:110]}")
    print("\nall:", ok)
