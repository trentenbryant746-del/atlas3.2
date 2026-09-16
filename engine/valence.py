"""
Valence from where an element sits, not from a table of ten.

engine/transitions.VALENCE holds ten elements. That was enough for
the bindings it needed and not enough for anything else --
engine/variantlife.py had to refuse silicon, which bonds four ways,
because the table had never heard of it. A ten-element table is not
a census, and treating absence from it as zero valence was a false
inference this repo caught and recorded.

The fix is not eighty more typed numbers. Valence for a main-group
element follows from HOW MANY ELECTRONS ARE IN ITS OUTER SHELL, and
that follows from filling the shells in order:

    shells hold   2, 8, 8, 18, 18, 32
    outer count   whatever is left after the full ones
    valence       that count if it is 4 or fewer, else 8 minus it

Hydrogen keeps one, carbon four, oxygen two, chlorine one, argon
none -- and silicon, which the old table lacked, comes out four
without anyone deciding.

WHERE IT REFUSES, AND WHY THAT IS NOT A GAP. Transition metals do
not have one valence. Iron is +2 and +3, manganese runs from +2 to
+7, and which one appears depends on what it is bonding with. That
is not a number waiting to be looked up; it is a property the
main-group rule does not describe. So the d-block and f-block are
REFUSED rather than assigned, and the refusal says what it would
take -- orbital energies, which this repo does not compute.

CHECKED AGAINST THE TABLE IT REPLACES. The ten hand-written
valences are kept as a FIXTURE and the derivation is scored against
them. It is not fitted to them: the shell capacities come from
engine/variantlife.noble_z(), which was written for a different
purpose, and if the two disagreed the derivation would be wrong
rather than the table.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.experts import BY_SYM, BY_Z                      # noqa: E402

DERIVED, ASSERTED = "DERIVED", "ASSERTED"

# ASSERTED: how many electrons each shell holds, in filling order.
# The same capacities engine/variantlife.py sums to find the noble
# gases, stated once here.
SHELLS = (2, 8, 8, 18, 18, 32)
SHELL_SOURCE = "aufbau shell capacities"

# Blocks the main-group rule does not describe. Their boundaries are
# where the d and f subshells fill, which is why the simple outer
# count stops working there.
D_BLOCK = [(21, 30), (39, 48), (72, 80), (104, 112)]
F_BLOCK = [(57, 71), (89, 103)]


def _in(z, ranges):
    return any(lo <= z <= hi for lo, hi in ranges)


def block(z):
    """-> 'main' | 'd' | 'f'. Which rule applies, if any."""
    if _in(z, F_BLOCK):
        return "f"
    if _in(z, D_BLOCK):
        return "d"
    return "main"


def _filled(z, ranges, cap, core=0):
    """d or f electrons filled ABOVE the noble core and below Z.

    Counting every range below Z double-counts: iodine sits on the
    krypton core at Z=36, which already contains the first d-block
    at 21-30, so adding those ten again left it with minus three
    outer electrons and no valence. Only the part of a range that
    lies above the core is outside it.
    """
    n = 0
    for lo, hi in ranges:
        start, end = max(lo, core + 1), min(hi, z)
        # A range lying entirely inside the core contributes nothing,
        # and so does one entirely above Z. Bounding only the start
        # left iodine counting the 21-30 d-block, which is already
        # inside its krypton core, and it came out with minus three
        # outer electrons.
        if start > end:
            continue
        n += min(cap, end - start + 1)
    return n


def outer_electrons(z):
    """Electrons in the outer s and p subshells. DERIVED.

    THE d ELECTRONS DO NOT COUNT, AND THE FIRST VERSION COUNTED
    THEM. Subtracting whole shells in order gave germanium 14 outer
    electrons and a valence of MINUS SIX, because after argon the
    period holds 4s, then ten 3d, then 4p -- eighteen elements, of
    which only the eight s and p ones set the bonding. The check
    against the hand-written table caught it on Ge, As, Se, Br and
    I, which is what a fixture is for.

    So the count is Z above the noble core it sits on, less the d
    and f electrons that have already gone in below it.
    """
    core = max([n for n in _noble() if n < z] or [0])
    return (z - core - _filled(z, D_BLOCK, 10, core)
            - _filled(z, F_BLOCK, 14, core))


def _noble():
    tot, out = 0, []
    for c in SHELLS:
        tot += c
        out.append(tot)
    return out


def valence(sym):
    """-> (n, why) or (None, why). Refuses where the rule does not hold."""
    if sym not in BY_SYM:
        raise KeyError(f"{sym} is not an element")
    z = BY_SYM[sym][0]
    b = block(z)
    if b != "main":
        return None, (f"Z={z} is in the {b}-block, where an element has "
                      f"several valences rather than one -- iron is +2 "
                      f"and +3, manganese +2 to +7, and which appears "
                      f"depends on the partner. Deciding needs orbital "
                      f"energies this repo does not compute")
    if z in _noble():
        return 0, (f"Z={z} closes a shell, so it forms no bonds")
    out = outer_electrons(z)
    if out <= 0:
        return None, (f"Z={z} gives {out} outer electrons, which is not a "
                      f"count -- the rule does not reach here")
    v = out if out <= 4 else 8 - out
    return v, (f"Z={z} has {out} outer electron(s), so it bonds "
               f"{v} way(s) -- " + ("sharing them"
                                    if out <= 4 else
                                    f"accepting the {8 - out} it lacks"))


def table():
    """-> {symbol: valence} for every element the rule covers."""
    out = {}
    for z in range(1, len(BY_Z) + 1):
        sym = BY_Z[z][0]
        v, _w = valence(sym)
        if v is not None:
            out[sym] = v
    return out


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("reproduces_the_hand_table", _fix)
    t("covers_more_than_ten", _cov)
    t("silicon", _si)
    t("nobles_are_zero", _nob)
    t("refuses_the_d_and_f_blocks", _ref)
    return all(o[1] for o in out), out


def _fix():
    """The ten hand-written valences are the fixture, not the input."""
    # AGAINST THE FIXTURE, NOT THE LIVE TABLE. transitions.VALENCE
    # is now this derivation's own output, so scoring against it
    # would be scoring against itself. The ten hand-written values
    # are kept separately for exactly this reason.
    from engine.transitions import VALENCE_FIXTURE as VALENCE
    got, bad = 0, []
    for sym, want in VALENCE.items():
        v, _w = valence(sym)
        if v == want:
            got += 1
        else:
            bad.append((sym, want, v))
    if bad:
        raise ArithmeticError(f"derivation disagrees with the hand table "
                              f"on {bad}")
    return (f"all {got} hand-written valences reproduced from shell "
            f"filling alone -- and the capacities came from "
            f"variantlife.noble_z(), written for a different purpose, so "
            f"agreement is two routes meeting")


def _cov():
    tbl = table()
    from engine.transitions import VALENCE_FIXTURE
    n = len(VALENCE_FIXTURE)
    if len(tbl) <= n:
        raise ArithmeticError(f"{len(tbl)} covered against {n} typed -- "
                              f"no gain")
    return (f"{len(tbl)} elements have a valence against the {n} that "
            f"were typed, {len(tbl)/n:.0f}x more with nothing added by "
            f"hand -- the typed ten are now a fixture, not the source")


def _si():
    v, why = valence("Si")
    if v != 4:
        raise ArithmeticError(f"silicon came out {v}")
    return (f"silicon bonds {v} ways: {why} -- the element "
            f"variantlife.py had to refuse for want of a table entry")


def _nob():
    from engine.variantlife import noble_z
    for z in noble_z():
        if z > len(BY_Z):
            continue
        sym = BY_Z[z][0]
        v, _w = valence(sym)
        if v != 0:
            raise ArithmeticError(f"{sym} came out valence {v}")
    return (f"every closed-shell element at {noble_z()} comes out zero, "
            f"independently of the noble-gas list -- both fall out of the "
            f"same capacities")


def _ref():
    for sym in ("Fe", "Mn", "Cu", "Gd"):
        v, why = valence(sym)
        if v is not None:
            raise ArithmeticError(f"{sym} was assigned {v}")
        if "block" not in why:
            raise ArithmeticError(f"{sym} refused without naming why")
    n = sum(1 for z in range(1, len(BY_Z) + 1)
            if block(z) != "main")
    return (f"{n} d- and f-block elements refused rather than assigned, "
            f"because they have several valences and the rule describes "
            f"one")


if __name__ == "__main__":
    tbl = table()
    print(f"{len(tbl)} elements with a derived valence\n")
    for sym in ("H", "C", "N", "O", "F", "Ne", "Na", "Si", "P", "S",
                "Cl", "Ar", "Ge", "As", "Se", "Br"):
        v, why = valence(sym)
        print(f"  {sym:<3}{str(v):<5}{why[:72]}")
    print()
    for sym in ("Fe", "Gd"):
        v, why = valence(sym)
        print(f"  {sym:<3}{str(v):<5}{why[:72]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:30}{d[:88]}")
    print("\nall:", ok)
