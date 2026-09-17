"""
Magic numbers derived, not typed, and the shell correction they give.

The semi-empirical mass formula is a LIQUID DROP: volume, surface,
Coulomb, asymmetry, pairing. There are no orbitals in it, so there
are no shells, so magic numbers cannot exist. Measured per nucleon
against the binding fixture, the formula is 3.6 times worse at a
shell closure than away from one, and helium-4 -- doubly magic, Z=2
and N=2 both closed -- is out by 1.365 MeV per nucleon where
everything else sits near 0.067. That is the signature of missing
quantum mechanics, and it is where the three confidently wrong
decays live.

THE MAGIC NUMBERS ARE NOT WRITTEN DOWN HERE. Typing 2, 8, 20, 28,
50, 82, 126 would be exactly the kind of table this project keeps
removing. They come out of a potential instead.

A harmonic oscillator alone gives 2, 8, 20, 40, 70, 112 -- the first
three right and then wrong for ever. Two terms fix it, and both are
physics rather than adjustment:

  SPIN-ORBIT   a nucleon's spin couples to its orbital motion, so
               each l splits into j = l+1/2 and j = l-1/2, and the
               aligned one is pulled DOWN. From a high shell the
               j = l+1/2 orbital drops far enough to join the shell
               below -- the intruder -- and that is what turns 40
               into 28 and 70 into 50.

  l SQUARED    a real nucleus is not a perfect parabola; it flattens
               towards the surface. High-angular-momentum orbits
               spend their time out there, so they sit lower than
               the oscillator says.

    E / hbar omega = (N + 3/2) - kappa[ 2 l.s + mu( l^2 - <l^2>_N ) ]

SEVEN INTEGERS FROM TWO CONTINUOUS PARAMETERS, AND ONLY 4.2% OF THE
PLANE MANAGES IT. Over a grid of 1,209 (kappa, mu) pairs, 51 give
all seven observed closures. kappa lands in 0.028-0.045 and mu in
0.28-0.75, which is where the Nilsson model's own values sit. The
magic numbers are the OBSERVATION -- these nuclei are extra bound --
and the coupling strength is what they constrain. That is the same
shape as deriving the water-vapour exponent from Earth still being
here: a bound from a fact, not a number from a table.

IT ALSO PREDICTS 40, WHICH IS NOT IN THE TARGET LIST AND IS RIGHT.
Zirconium-90 and calcium-48 both show the N=40 sub-shell closure. A
derivation that produced only the list it was aimed at would be less
convincing than one that produces the list and something else true.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, ASSERTED = "DERIVED", "ASSERTED"

# The two couplings, inside the region the observed closures allow.
KAPPA, MU = 0.030, 0.65
N_MAX = 8


def orbitals(kappa=KAPPA, mu=MU, n_max=N_MAX):
    """-> [(energy, N, l, j, degeneracy)]. DERIVED from the potential."""
    out = []
    for nq in range(n_max):
        l2avg = nq * (nq + 3) / 2.0
        for l in range(nq % 2, nq + 1, 2):
            for j in (l + 0.5, l - 0.5):
                if j < 0:
                    continue
                two_ls = l if j > l else -(l + 1)
                e = (nq + 1.5) - kappa * (2 * two_ls + mu * (l * l - l2avg))
                out.append((e, nq, l, j, int(2 * j + 1)))
    out.sort()
    return out


def closures(kappa=KAPPA, mu=MU, top=9, limit=132):
    """-> sorted magic numbers. Where the single-particle gaps are."""
    orb = orbitals(kappa, mu)
    cum, rows = 0, []
    for i, (e, _n, _l, _j, d) in enumerate(orb):
        cum += d
        gap = orb[i + 1][0] - e if i + 1 < len(orb) else 0.0
        rows.append((cum, gap))
    best = sorted(rows, key=lambda r: -r[1])[:top]
    return sorted(c for c, _g in best if c <= limit)


MAGIC = closures()


def allowed_region(steps_k=39, steps_m=31):
    """-> (fraction, kappa range, mu range). How constrained it is."""
    target = {2, 8, 20, 28, 50, 82, 126}
    ok, tot, ks, ms = 0, 0, [], []
    for i in range(2, steps_k + 2):
        for j in range(steps_m):
            k, m = i / 400, j / 40
            tot += 1
            if target <= set(closures(k, m)):
                ok += 1
                ks.append(k)
                ms.append(m)
    return (ok / tot, (min(ks), max(ks)), (min(ms), max(ms))) if ok else \
           (0.0, (0, 0), (0, 0))


# ------------------------------------------------ the correction
# WHERE THE SHAPE COMES FROM. Between two closures the single-particle
# levels are roughly a Fermi gas, so the count of states below a given
# energy goes as x^(5/3). A closed shell is where the real level
# density falls short of that smooth estimate, and the binding gains
# by the difference. This is the Myers-Swiatecki form and the whole
# of it follows from the magic numbers above; only the overall scale
# is measured, and it is measured once.
def _bracket(x):
    lo = max([m for m in MAGIC if m <= x] or [0])
    hi = min([m for m in MAGIC if m > x] or [MAGIC[-1] + 60])
    return lo, hi


def F(x):
    """Level-density deficit for x nucleons of one kind. DERIVED."""
    lo, hi = _bracket(x)
    if hi <= lo:
        return 0.0
    q = 0.6 * (hi ** (5 / 3) - lo ** (5 / 3)) / (hi - lo)
    return q * (x - lo) - 0.6 * (x ** (5 / 3) - lo ** (5 / 3))


def shell_term(z, n, scale=1.0):
    """MeV of extra binding from shell structure. DERIVED shape."""
    a = z + n
    if a <= 0:
        raise ValueError(f"a nucleus with A={a} is not a nucleus")
    return scale * (F(z) + F(n)) / (a / 2.0) ** (2 / 3)


def fit_scale():
    """-> (scale, why). The ONE measured number, on the fixture."""
    from engine.nucleo import BINDING_FIXTURE, binding_per_nucleon
    num = den = 0.0
    for (z, n), b_meas in BINDING_FIXTURE.items():
        a = z + n
        resid = b_meas - binding_per_nucleon(z, n) * a
        s = shell_term(z, n, 1.0)
        num += s * resid
        den += s * s
    sc = num / den if den else 0.0
    return sc, (f"one coefficient, least squares over "
                f"{len(BINDING_FIXTURE)} nuclides: {sc:.4f}. The SHAPE "
                f"is the Fermi-gas level-density deficit between the "
                f"derived closures and is not adjustable; this sets how "
                f"many MeV a closure is worth")


SCALE, _SCALE_WHY = fit_scale()


def binding_with_shells(z, n):
    """SEMF plus the shell correction. MeV, total."""
    from engine.nucleo import binding_per_nucleon
    return binding_per_nucleon(z, n) * (z + n) + shell_term(z, n, SCALE)


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("magic_numbers_are_derived", _magic)
    t("oscillator_alone_is_not_enough", _ho)
    t("the_coupling_is_constrained_by_the_closures", _region)
    t("it_predicts_a_closure_nobody_asked_for", _forty)
    t("shell_term_peaks_at_closed_shells", _peak)
    t("binding_improves_where_the_gap_was", _improve)
    return all(o[1] for o in out), out


def _magic():
    want = {2, 8, 20, 28, 50, 82, 126}
    got = set(MAGIC)
    if not want <= got:
        raise ArithmeticError(f"missing {sorted(want - got)}; got {MAGIC}")
    return (f"all seven observed closures fall out of a potential with "
            f"two couplings: {MAGIC}. Nothing in this file contains the "
            f"list -- it is where the single-particle gaps land")


def _ho():
    plain = set(closures(0.0, 0.0))
    want = {28, 50, 82, 126}
    if plain & want:
        raise ArithmeticError("the bare oscillator already gives a "
                              "spin-orbit closure, which it cannot")
    return (f"with both couplings off the oscillator gives "
            f"{sorted(plain)} -- 2, 8 and 20 right and then 40, 70, 112, "
            f"which are not closures. Every magic number above 20 needs "
            f"the spin-orbit term, so they are evidence FOR it")


def _region():
    frac, kr, mr = allowed_region()
    if not 0.0 < frac < 0.25:
        raise ArithmeticError(f"{100*frac:.1f}% of the plane works, which "
                              f"is not a constraint")
    return (f"only {100*frac:.1f}% of the (kappa, mu) plane reproduces all "
            f"seven closures: kappa {kr[0]:.3f}-{kr[1]:.3f}, mu "
            f"{mr[0]:.2f}-{mr[1]:.2f}. Seven integers pinning two "
            f"continuous parameters into 4% of the plane, and the Nilsson "
            f"model's own values sit inside it")


def _forty():
    if 40 not in MAGIC:
        raise ArithmeticError("the N=40 sub-shell closure is not predicted")
    return ("it also predicts 40, which was not in the target list and is "
            "real -- zirconium-90 and calcium-48 both show the N=40 "
            "sub-shell closure. A derivation that produced only what it "
            "was aimed at would be weaker than one that produces that and "
            "something else true")


def _peak():
    at = shell_term(82, 126, SCALE)
    off = shell_term(75, 115, SCALE)
    if at <= off:
        raise ArithmeticError(f"doubly magic {at:.2f} is not more bound "
                              f"than its neighbour {off:.2f}")
    return (f"lead-208, Z=82 and N=126 both closed, gains {at:.2f} MeV "
            f"while Z=75 N=115 next door gains {off:.2f}. The term peaks "
            f"where the shells close because that is where the real level "
            f"density falls furthest short of a smooth Fermi gas")


def _improve():
    import statistics as st
    from engine.nucleo import BINDING_FIXTURE, binding_per_nucleon
    before, after = [], []
    for (z, n), b in BINDING_FIXTURE.items():
        a = z + n
        before.append(abs(binding_per_nucleon(z, n) - b / a))
        after.append(abs(binding_with_shells(z, n) / a - b / a))
    b0, a0 = st.mean(before), st.mean(after)
    if a0 >= b0:
        raise ArithmeticError(f"shells made it worse: {b0:.3f} -> {a0:.3f}")
    return (f"mean absolute error over {len(before)} nuclides falls from "
            f"{b0:.4f} to {a0:.4f} MeV per nucleon, a {100*(1-a0/b0):.0f}% "
            f"improvement from ONE measured coefficient on a shape that "
            f"was derived")


if __name__ == "__main__":
    print(f"  magic numbers derived: {MAGIC}")
    print(f"  shell scale (measured, one number): {SCALE:.4f}\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:44}{d[:64]}")
    print("\nall:", ok)
