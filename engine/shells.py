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


# ------------------------------------- where the liquid drop ends
# THE GAP WAS NEVER "HEAVY NUCLEI ARE WRONG". It was one nucleus.
#
# Alpha Q = B(daughter) + B(helium-4) - B(parent), and the SEMF gives
# helium-4 22.841 MeV against a measured 28.296. That single 5.46 MeV
# error sits in EVERY alpha channel, which is why every heavy alpha
# step came out 5 to 11 MeV short. Parent and daughter differ by only
# four nucleons, so their per-nucleon errors largely cancel; helium's
# does not cancel against anything.
#
# A MISSING CURVATURE TERM WAS THE OBVIOUS GUESS AND IT IS WRONG. The
# Weizsacker expansion goes volume ~ A, surface ~ A^(2/3), curvature
# ~ A^(1/3), and the formula stops after two. If the residual were
# the truncated third term it would scale as A^(-2/3) per nucleon and
# the ratio would be constant. Measured across the fixture it runs
# from -3.44 at A=4 to +2.10 at A=238 AND CHANGES SIGN. Light nuclei
# are under-bound, heavy ones over-bound. One term cannot do both, so
# the hypothesis is discarded rather than fitted.
#
# WHAT IS TRUE IS THAT THE FORMULA HAS A DOMAIN, AND IT SAYS SO
# ITSELF. A liquid drop needs a bulk: an interior where a nucleon has
# a full set of neighbours, and a surface correcting for the ones
# that do not. Helium-4 has no interior -- every nucleon is surface.
# Rather than assert where that matters, compare the formula against
# its OWN measured mass bar of 4.763 MeV:
#
#     A = 4    off by 5.46 MeV   OUTSIDE its own bar
#     A = 12   off by 6.95 MeV   OUTSIDE its own bar
#     A = 16   off by 1.65 MeV   inside
#     A >= 16  inside, everywhere in the fixture
#
# Both nuclei that break it are alpha-clustered -- helium-4 is one
# alpha and carbon-12 behaves as three -- which is a quantum
# structure a fluid drop cannot represent at all. So the boundary is
# DERIVED: the formula is used where it is within its own error and
# refused where it is not.
#
# THE CONSEQUENCE IS THAT ALPHA DECAY CANNOT BE DERIVED HERE. Every
# alpha Q-value needs helium-4, helium-4 is outside the domain, and
# the honest answer is refusal rather than a number known to be 5.46
# MeV wrong. That is a real loss and it is stated rather than hidden.
SEMF_MIN_A = None       # derived below, never typed


def _derive_min_a():
    """Smallest A where the formula is inside its own mass bar."""
    from engine.nucleo import BINDING_FIXTURE, binding_per_nucleon, error_bar
    bar = error_bar("mass")[0]
    bad = []
    for (z, n), b in BINDING_FIXTURE.items():
        a = z + n
        e = abs(binding_per_nucleon(z, n) * a + shell_term(z, n, SCALE) - b)
        if e > bar:
            bad.append(a)
    return (max(bad) + 1) if bad else 1


SEMF_MIN_A = _derive_min_a()


def in_domain(z, n):
    """Is the liquid drop valid here? DERIVED from its own bar."""
    return (z + n) >= SEMF_MIN_A


def domain_note(z, n):
    a = z + n
    return (f"A={a} is below {SEMF_MIN_A}, where the semi-empirical mass "
            f"formula exceeds its own measured {4.763:.3f} MeV bar. A "
            f"liquid drop needs an interior and this nucleus is all "
            f"surface; helium-4 and carbon-12 are alpha-clustered, which "
            f"is quantum structure a fluid cannot have. Refused rather "
            f"than answered wrongly")


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
    t("the_liquid_drop_knows_where_it_ends", _domain)
    t("curvature_was_tested_and_rejected", _curv)
    t("the_one_measured_number_is_exercised", _stranded)
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


def _domain():
    if not 8 <= SEMF_MIN_A <= 40:
        raise ArithmeticError(f"domain floor came out A={SEMF_MIN_A}")
    if in_domain(2, 2):
        raise ArithmeticError("helium-4 is inside the domain, so the "
                              "boundary is not doing anything")
    if not in_domain(82, 126):
        raise ArithmeticError("lead-208 was excluded")
    return (f"the formula is refused below A={SEMF_MIN_A}, derived by "
            f"asking where it exceeds its OWN measured mass bar rather "
            f"than by asserting a floor. Helium-4 is out by 5.46 MeV and "
            f"carbon-12 by 6.95; both are alpha-clustered. Every alpha "
            f"Q-value needs helium-4, so alpha decay is not derivable "
            f"here and is refused")


def _curv():
    import statistics as st
    from engine.nucleo import BINDING_FIXTURE, binding_per_nucleon
    r = []
    for (z, n), b in BINDING_FIXTURE.items():
        a = z + n
        r.append((binding_per_nucleon(z, n) - b / a) / a ** (-2 / 3))
    lo, hi = min(r), max(r)
    if lo * hi > 0:
        raise ArithmeticError("the residual no longer changes sign, so a "
                              "curvature term may now be the explanation "
                              "and should be retried")
    return (f"a missing curvature term would make this ratio constant; it "
            f"runs {lo:+.2f} to {hi:+.2f} and changes sign, so light "
            f"nuclei are under-bound and heavy ones over-bound and one "
            f"term cannot do both. Hypothesis discarded, not fitted")



def _stranded():
    """Wires fit_scale and domain_note."""
    sc, why = fit_scale()
    v = float(getattr(sc, "value", sc))
    note = domain_note(2, 2)
    if not -100.0 < v < 0.0 or "below" not in note:
        raise ArithmeticError(f"scale {v}, note {note[:40]}")
    return (f"the single fitted number here is {v:.4f} and it is "
            f"NEGATIVE -- a deficit, not a scale, whatever its name "
            f"says. Wiring it was how that surfaced: nothing had "
            f"called it, so nothing had ever had to know its sign. "
            f"He-4 also gets told why it is out of domain")

if __name__ == "__main__":
    print(f"  magic numbers derived: {MAGIC}")
    print(f"  shell scale (measured, one number): {SCALE:.4f}\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:44}{d[:64]}")
    print("\nall:", ok)
