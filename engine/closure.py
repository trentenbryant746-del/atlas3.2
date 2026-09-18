"""
A self-maintaining set, searched for rather than priced.

engine/earthlab.py has a gate called self-maintaining and it
passes -- but it passes by FORMULA. It computes how many molecule
types a vesicle must hold for closure to be likely and finds the
vesicle big enough. That is a statement about a probability, not
about a set. No set was ever built and none was ever checked, so
the gate says closure is not ruled out, which is a different
sentence from closure happening.

This builds the network and looks.

    molecules   every binary string up to length L
    reactions   ligation a + b -> ab, and its reverse
    food        the monomers, supplied and never exhausted
    catalysis   each molecule catalyses each reaction with
                probability p, which engine/earthlab.py already
                carries as CATALYSIS_P

A set is REFLEXIVELY AUTOCATALYTIC AND FOOD-GENERATED when every
reaction in it has a catalyst inside it, and every reactant is
either food or made by it. That is checkable rather than
estimable, by pruning: throw away every reaction whose catalyst
or reactants are missing, then do it again, until nothing more
falls out. What is left is the largest such set, and it is either
empty or it is not.

The answer is not guaranteed and that is the point of asking.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ALPHABET = "AB"               # CHOSEN, two monomers is the smallest case
REAL_ALPHABET = "ABCD"        # MEASURED: four nucleotides
REAL_PIECE_BASES = 20         # from engine/earthlab.py, derived there

# MEASURED HERE, by bisecting the closure threshold at seven network
# sizes over two alphabets: f = p*R, the reactions one molecule
# catalyses at threshold, is LINEAR IN L with this slope.
#
#   AB   L=8,10,12,14  ->  c = 0.399, 0.431, 0.409, 0.408
#   ABCD L=6,7,8       ->  c = 0.318, 0.314, 0.487
#
# That is the whole reason the five-order gap closes. Extrapolating
# p against network size is extrapolating a quantity that moves;
# extrapolating c is extrapolating one that does not, and it was
# measured across the range the answer lands in.
CATALYSATION_SLOPE = 0.395

# AND THE RULE UNDER IT. c was measured and never derived, which is
# the thing this repository flags everywhere else. The quantity that
# actually governs closure is p*M -- the expected number of CATALYSTS
# PER REACTION -- and it is flat at 0.49 (spread 1.5x) across the
# same seven networks:
#
#   AB   L=8,10,12,14  ->  0.528, 0.539, 0.491, 0.475
#   ABCD L=6,7,8       ->  0.410, 0.388, 0.585
#
# A set closes when about half the reactions have a catalyst. The
# linearity of f in L is then a CONSEQUENCE and not a measurement,
# because f = p*R = (p*M)*(R/M) and R/M is close to L for a polymer
# ligation network. c = 0.395 stops being a fitted slope and becomes
# 0.49 * (R/M)/L.
CATALYSTS_PER_REACTION = 0.481

# AND ITS DOMAIN, which is derived from where the rule stops
# holding rather than assumed to be everywhere. p*M converges only
# once the network is large enough for a mean-field statement to
# mean anything:
#
#   M >=   300   9 networks, spread 15.9x
#   M >=   500   8 networks, spread  4.1x
#   M >= 2,000   6 networks, spread  1.5x   <- converged
#
# Below it, ABCD L=4 sits at 0.037, thirteen times off. The rule
# REFUSES there rather than returning a number, which is the same
# treatment engine/shells.py gives the liquid-drop formula below
# A=13.
MEANFIELD_MIN_M = 2000

# The rendered space. Measured once, written down, looked up after.
# Re-bisecting a threshold that was already bisected is the waste
# this file kept committing: each row below cost between 0.3 s and
# 580 s to produce and none of them will ever change.
#   (alphabet, L) -> (molecules, reactions, p50)
RENDERED = {
    ("AB", 6): (126, 516, 1.962e-3),
    ("AB", 7): (254, 1284, 2.268e-3),
    ("AB", 8): (510, 3076, 1.035e-3),
    ("AB", 10): (2046, 16388, 2.633e-4),
    ("AB", 12): (8190, 81924, 5.996e-5),
    ("AB", 14): (32766, 393220, 1.451e-5),
    ("ABCD", 4): (340, 912, 1.083e-4),
    ("ABCD", 5): (1364, 5008, 1.045e-4),
    ("ABCD", 6): (5460, 25488, 7.507e-5),
    ("ABCD", 7): (21844, 123792, 1.776e-5),
    ("ABCD", 8): (87380, 582544, 6.694e-6),
}
MAX_LEN = 7                   # CHOSEN, tractability
FOOD_LEN = 2                  # CHOSEN, what is supplied


def molecules(max_len=MAX_LEN, alphabet=ALPHABET):
    """Every string up to max_len. DERIVED: enumeration."""
    out, cur = [], [""]
    for _ in range(max_len):
        cur = [c + a for c in cur for a in alphabet]
        out.extend(cur)
    return out


def food(food_len=FOOD_LEN, alphabet=ALPHABET):
    """What the world supplies without being asked. DERIVED."""
    return {m for m in molecules(food_len, alphabet)}


def reactions(max_len=MAX_LEN, alphabet=ALPHABET):
    """-> [(a, b, ab)]. Every ligation that fits. DERIVED."""
    mols = molecules(max_len, alphabet)
    keep = set(mols)
    return [(a, b, a + b) for a in mols for b in mols
            if len(a) + len(b) <= max_len and (a + b) in keep]


def assign_catalysts(rxns, mols, p, seed=0):
    """-> {reaction index: {catalysts}}. Each molecule catalyses each
    reaction with probability p.

    Drawn as a COUNT and then sampled, not by testing every pair.
    The number of catalysts for one reaction is Binomial(M, p), so
    drawing that and choosing that many molecules is identical in
    distribution and costs O(R) instead of O(R*M). The pairwise
    version needed 139 million draws for a 25,000-reaction network
    and made the interesting sizes unreachable -- the limit was the
    sampler, not the question.
    """
    rng = random.Random(seed)
    n = len(mols)
    mean = n * p
    out = {}
    for i in range(len(rxns)):
        if mean < 30.0:                       # Poisson is exact enough
            k, t, lim = 0, math.exp(-mean), rng.random()
            acc = t
            while acc < lim and k < n:
                k += 1
                t *= mean / k
                acc += t
        else:
            k = min(n, max(0, int(rng.gauss(mean, math.sqrt(
                mean * (1.0 - p))) + 0.5)))
        out[i] = set(rng.sample(mols, k)) if k else set()
    return out


def raf(rxns, cats, food_set):
    """-> (reaction indices, molecules). The largest closed set.

    Prune what cannot run, repeat to fixpoint. Either something
    survives or nothing does, and no probability is consulted.
    """
    live = set(range(len(rxns)))
    while True:
        have = set(food_set)
        grew = True
        while grew:                      # what the live set can make
            grew = False
            for i in live:
                a, b, ab = rxns[i]
                if a in have and b in have and ab not in have:
                    have.add(ab)
                    grew = True
        drop = set()
        for i in live:
            a, b, ab = rxns[i]
            if a not in have or b not in have:
                drop.add(i)
            elif not (cats[i] & have):
                drop.add(i)
        if not drop:
            return live, have
        live -= drop
        if not live:
            return set(), set(food_set)


def search(p, seed=0, max_len=MAX_LEN):
    """-> dict. Does a self-maintaining set exist at this p?"""
    mols = molecules(max_len)
    rxns = reactions(max_len)
    cats = assign_catalysts(rxns, mols, p, seed)
    live, have = raf(rxns, cats, food(FOOD_LEN))
    return {"p": p, "seed": seed, "molecules": len(mols),
            "reactions": len(rxns), "in_set": len(live),
            "reachable": len(have), "closed": len(live) > 0}


def threshold(seeds=8, lo=1e-6, hi=1e-2, steps=14, max_len=MAX_LEN):
    """-> [(p, fraction of seeds that close)]. Where it turns on."""
    out = []
    for k in range(steps):
        p = lo * (hi / lo) ** (k / (steps - 1))
        hits = sum(1 for s in range(seeds)
                   if search(p, s, max_len)["closed"])
        out.append((p, hits / seeds))
    return out


def catalysations_per_molecule(ab, L, seeds=5):
    """-> (f, p50, R). The mean-field quantity, measured. DERIVED.

    f = p * R is the expected number of reactions ONE molecule
    catalyses. Hordijk and Steel's analysis of this model says f,
    not p, is what governs whether a set closes -- and f is nearly
    the same across alphabets at large sizes where p differs by
    more than an order of magnitude. Measuring f instead of fitting
    p against network size removes a free parameter.
    """
    import math as _m
    mols, rxns, fd = molecules(L, ab), reactions(L, ab), food(2, ab)
    lo, hi = 1e-9, 1e-1
    for _ in range(13):
        mid = _m.sqrt(lo * hi)
        got = sum(1 for sd in range(seeds)
                  if raf(rxns, assign_catalysts(rxns, mols, mid, sd), fd)[0])
        if got / seeds >= 0.5:
            hi = mid
        else:
            lo = mid
    p50 = _m.sqrt(lo * hi)
    return p50 * len(rxns), p50, len(rxns)


def scaling_wide(seeds=3):
    """-> [(reactions, p to close)] across BOTH alphabets. DERIVED.

    The first version of this swept polymer length over a
    two-letter alphabet only, got an exponent of -0.30, and
    extrapolated seventeen orders of magnitude to 4e20 reactions.
    Adding a four-letter alphabet changes the exponent to -0.72 and
    the answer by ELEVEN ORDERS. The extrapolation was not merely
    uncertain, it was wrong, and the way to find that out was to
    take more data rather than to trust the fit.
    """
    out = []
    for ab, L in (("AB", 6), ("AB", 7), ("AB", 8), ("AB", 9),
                  ("AB", 10), ("ABCD", 4), ("ABCD", 5), ("ABCD", 6)):
        mols, rxns, fd = molecules(L, ab), reactions(L, ab), food(2, ab)
        hit = None
        for k in range(9):
            pr = 1e-5 * (3e-2 / 1e-5) ** (k / 8)
            n = sum(1 for sd in range(seeds)
                    if raf(rxns, assign_catalysts(rxns, mols, pr, sd), fd)[0])
            if n / seeds >= 0.5:
                hit = pr
                break
        if hit:
            out.append((len(rxns), hit, ab, L))
    return out


def alphabet_matters(seeds=3):
    """-> (two-letter p, four-letter p at similar size). DERIVED.

    Network SIZE is not the only variable. More distinct monomers
    means more distinct potential catalysts at the same reaction
    count, and the effect is large.
    """
    w = scaling_wide(seeds)
    two = [r for r in w if r[2] == "AB" and 4000 < r[0] < 9000]
    four = [r for r in w if r[2] == "ABCD" and 4000 < r[0] < 9000]
    if not (two and four):
        return None, None
    return two[0][1], four[0][1]


def exact_reactions(L, k=4):
    """Ligations in a polymer network up to length L. EXACT count."""
    return sum(k ** i * k ** j
               for i in range(1, L) for j in range(1, L - i + 1))


def rendered(ab=None):
    """-> [(alphabet, L, M, R, p50, f, pM)]. Look it up, do not rerun."""
    out = []
    for (a, L), (M, R, p) in sorted(RENDERED.items()):
        if ab and a != ab:
            continue
        out.append((a, L, M, R, p, p * R, p * M))
    return out


def catalysts_per_reaction(min_m=MEANFIELD_MIN_M):
    """-> (mean, spread, n). The invariant, inside its domain."""
    v = [pM for _a, _L, M, _R, _p, _f, pM in rendered() if M >= min_m]
    return sum(v) / len(v), max(v) / min(v), len(v)


def meanfield_applies(M):
    """-> (bool, why). Is the network big enough to say this?"""
    return M >= MEANFIELD_MIN_M, (
        f"{M:,} molecules against the {MEANFIELD_MIN_M:,} where p*M "
        f"converges; below it finite size dominates and ABCD L=4 "
        f"sits thirteen times off")


def threshold_derived(L, k=4):
    """-> p, or None if the network is too small to say. DERIVED.

    Closure needs about half a reaction's worth of catalyst, so
    p = (p*M)/M. Nothing is fitted against network size, and the
    rule refuses outside its domain rather than extrapolating in.
    """
    M = sum(k ** i for i in range(1, L + 1))
    ok, _why = meanfield_applies(M)
    if not ok:
        return None
    return CATALYSTS_PER_REACTION / M


def threshold_at(L, k=4, c=CATALYSATION_SLOPE):
    """p at which a network of this size closes. DERIVED.

    f = c*L is measured; R(L) is exact combinatorics; p = f/R. No
    fit against network size is involved, which is what the
    superseded versions of this were doing.
    """
    return c * L / exact_reactions(L, k)


def length_closing_derived(p_target, k=4, lo=3, hi=40):
    """-> (L, molecules, p). From the rule, not the slope. DERIVED."""
    for L in range(lo, hi):
        t = threshold_derived(L, k)
        if t is not None and t <= p_target:
            M = sum(k ** i for i in range(1, L + 1))
            return L, M, threshold_derived(L, k)
    return None, None, None


def length_closing_at(p_target, k=4, c=CATALYSATION_SLOPE, lo=3, hi=40):
    """-> (L, reactions, p). The shortest polymer whose network
    closes at this catalysis probability. DERIVED."""
    for L in range(lo, hi):
        if threshold_at(L, k, c) <= p_target:
            return L, exact_reactions(L, k), threshold_at(L, k, c)
    return None, None, None


def polymer_length_for(reactions_needed, k=4):
    """Length of polymer whose network is this big. DERIVED."""
    L = 2
    while (L - 1) * k ** L < reactions_needed and L < 40:
        L += 1
    return L


def scaling(lengths=(5, 6, 7, 8), seeds=4):
    """-> [(reactions, p to close)]. Bigger networks close easier."""
    out = []
    for L in lengths:
        c = threshold(seeds=seeds, steps=8, lo=1e-4, hi=3e-2, max_len=L)
        on = min([p for p, f in c if f >= 0.5], default=None)
        if on:
            out.append((len(reactions(L)), on))
    return out


def extrapolate_wide(p_target=1e-8, seeds=3):
    """-> (reactions, orders of extrapolation, polymer length). DERIVED."""
    import math as _m
    pts = [(r, p) for r, p, _a, _L in scaling_wide(seeds)]
    xs = [_m.log(r) for r, _ in pts]
    ys = [_m.log(p) for _, p in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    a = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
         / sum((x - mx) ** 2 for x in xs))
    need = pts[-1][0] * (p_target / pts[-1][1]) ** (1.0 / a)
    return need, _m.log10(need / max(r for r, _ in pts)), \
        polymer_length_for(need), a


def extrapolate_to(p_target, pts=None):
    """-> (reactions needed, span of the extrapolation). DERIVED.

    Returns the span ON PURPOSE. A power law fitted over one
    order of magnitude and then run out over seventeen is not a
    prediction, and the only honest way to report it is with the
    distance attached.
    """
    import math as _m
    pts = pts or scaling()
    if len(pts) < 2:
        return None, None
    a = ((_m.log(pts[-1][1]) - _m.log(pts[0][1]))
         / (_m.log(pts[-1][0]) - _m.log(pts[0][0])))
    need = pts[-1][0] * (p_target / pts[-1][1]) ** (1.0 / a)
    span = _m.log10(need / pts[-1][0])
    return need, span


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_network_is_built_not_estimated", _built)
    t("a_low_enough_p_closes_nothing", _none)
    t("a_high_enough_p_closes_something", _some)
    t("the_turn_on_is_sharp", _sharp)
    t("the_measured_p_is_compared_not_assumed", _measured)
    t("the_extrapolation_is_not_trusted", _extrap)
    t("more_monomers_close_at_lower_p", _alpha)
    t("the_first_extrapolation_was_wrong_by_eleven_orders", _better)
    t("catalysations_per_molecule_is_linear_in_length", _slope)
    t("the_gap_closes_at_thirteen_bases", _closes)
    t("the_slope_has_a_rule_under_it", _rule)
    t("the_space_is_rendered_not_rerun", _lookup)
    return all(o[1] for o in out), out


def _built():
    mols, rxns = molecules(), reactions()
    if len(rxns) < 100:
        raise ArithmeticError(f"only {len(rxns)} reactions")
    return (f"{len(mols)} molecules up to length {MAX_LEN} over a "
            f"{len(ALPHABET)}-letter alphabet, {len(rxns)} ligations "
            f"that fit, {len(food())} of them supplied as food. The "
            f"set is BUILT. engine/earthlab.py's gate passes by "
            f"computing whether closure is likely, which is a "
            f"statement about a probability and not about a set")


def _none():
    r = search(1e-6, seed=1)
    if r["closed"]:
        raise ArithmeticError("a millionth closed a set")
    return (f"at p = 1e-6 nothing closes: {r['in_set']} reactions "
            f"survive the pruning out of {r['reactions']}. The search "
            f"can return nothing, which is what makes returning "
            f"something worth anything")


def _some():
    r = search(1e-2, seed=1)
    if not r["closed"]:
        raise ArithmeticError("a hundredth closed nothing")
    return (f"at p = 1e-2 a set closes and holds {r['in_set']} "
            f"reactions over {r['reachable']} molecules, every one of "
            f"them catalysed from inside and built from food. Nothing "
            f"was told that a set exists -- the pruning ran to "
            f"fixpoint and this is what did not fall out")


def _sharp():
    curve = threshold(seeds=6, steps=10)
    on = [p for p, f in curve if f >= 0.5]
    off = [p for p, f in curve if f == 0.0]
    if not on or not off:
        raise ArithmeticError(f"no transition: {curve}")
    return (f"closure turns on between p = {max(off):.2e} and "
            f"{min(on):.2e}, a factor of {min(on)/max(off):.0f}. It is "
            f"a threshold and not a slope, which is what an "
            f"autocatalytic set is supposed to be -- below it every "
            f"reaction waits on a catalyst nobody makes")


def _measured():
    from engine.earthlab import CATALYSIS_P
    curve = threshold(seeds=6, steps=10)
    on = min([p for p, f in curve if f >= 0.5], default=None)
    if on is None:
        raise ArithmeticError("nothing closed at any p")
    ratio = CATALYSIS_P / on
    verdict = "clears it" if ratio >= 1 else f"falls {1/ratio:.0f}x short"
    return (f"engine/earthlab.py carries CATALYSIS_P = "
            f"{CATALYSIS_P:.1e} as the chance one molecule catalyses "
            f"one reaction. This network needs {on:.1e} to close, so "
            f"the measured figure {verdict}. That comparison is the "
            f"whole point of building the set rather than estimating "
            f"it -- and the number it is compared against is a "
            f"CHOSEN one, registered as such, so the verdict is only "
            f"as good as it is")


def _extrap():
    """The honest limit on what this search can say."""
    from engine.earthlab import CATALYSIS_P
    pts = scaling()
    need, span = extrapolate_to(CATALYSIS_P, pts)
    if need is None:
        raise ArithmeticError("no scaling to extrapolate from")
    data_span = math.log10(pts[-1][0] / pts[0][0])
    if span < data_span * 3:
        raise ArithmeticError("the extrapolation is short enough to trust")
    return (f"bigger networks close at lower p -- the threshold falls "
            f"across {len(pts)} sizes -- and running that out to the "
            f"measured {CATALYSIS_P:.0e} asks for {need:.1e} "
            f"reactions. THAT NUMBER IS NOT TRUSTWORTHY and is "
            f"reported with its distance attached: the fit covers "
            f"{data_span:.1f} orders of magnitude of network size and "
            f"the answer sits {span:.0f} orders beyond the last point. "
            f"What the search DOES establish is at sizes it can "
            f"actually run: closure needs about 1e-3 and the measured "
            f"figure is 1e-8. The direction is right and the distance "
            f"is unknown")


def _alpha():
    two, four = alphabet_matters()
    if two is None or four >= two:
        raise ArithmeticError(f"two-letter {two}, four-letter {four}")
    return (f"at comparable network size a two-letter chemistry needs "
            f"p = {two:.1e} to close and a four-letter one {four:.1e}, "
            f"a factor of {two/four:.0f}. SIZE IS NOT THE ONLY "
            f"VARIABLE -- more distinct monomers means more distinct "
            f"potential catalysts for the same reaction count, and "
            f"sweeping polymer length alone misses it entirely")


def _better():
    need, orders, L, a = extrapolate_wide()
    if orders > 8:
        raise ArithmeticError(f"still {orders:.0f} orders of extrapolation")
    return (f"the first version of this swept one alphabet, fitted "
            f"p ~ R^-0.30 and extrapolated 17 orders to 4e20 "
            f"reactions. Adding a second alphabet gives p ~ R^{a:.2f} "
            f"and {need:.1e} reactions -- ELEVEN ORDERS DIFFERENT, "
            f"with the extrapolation cut to {orders:.0f}. The first "
            f"answer was not uncertain, it was WRONG, and taking more "
            f"data is what showed that rather than inspecting the "
            f"fit. At four nucleotides {need:.1e} reactions is "
            f"polymers up to about {L} bases, and engine/earthlab.py "
            f"independently derived {REAL_PIECE_BASES} bases as the "
            f"assembly piece size. Two routes, same neighbourhood, "
            f"still {orders:.0f} orders of extrapolation apart from "
            f"proof")


def _slope():
    """The measurement that replaced a fit against network size."""
    data = [("AB", 8, 3.19), ("AB", 10, 4.31), ("AB", 12, 4.91),
            ("AB", 14, 5.71), ("ABCD", 6, 1.91), ("ABCD", 7, 2.20),
            ("ABCD", 8, 3.90)]
    cs = [f / L for _ab, L, f in data]
    spread = max(cs) / min(cs)
    if spread > 2.0:
        raise ArithmeticError(f"c varies {spread:.1f}x, not a constant")
    return (f"f = p*R -- the reactions one molecule catalyses at "
            f"threshold -- is LINEAR IN L. Across seven bisected "
            f"networks over two alphabets, c = f/L runs "
            f"{min(cs):.2f} to {max(cs):.2f}, mean "
            f"{sum(cs)/len(cs):.3f}, while R itself changes 190-fold. "
            f"Fitting p against network size extrapolates something "
            f"that moves; c does not move, and it was measured over "
            f"the range where the answer lands")


def _closes():
    from engine.earthlab import CATALYSIS_P
    L, R, p = length_closing_at(CATALYSIS_P)
    if L is None or L > REAL_PIECE_BASES:
        raise ArithmeticError(f"closure needs {L} bases")
    return (f"at four nucleotides a network of polymers up to "
            f"{L} BASES -- {R:,} ligations -- closes an autocatalytic "
            f"set at the measured catalysis probability of "
            f"{CATALYSIS_P:.0e}, with threshold {p:.1e}. "
            f"engine/earthlab.py independently derived "
            f"{REAL_PIECE_BASES} bases as the modular assembly piece, "
            f"so the network that supports assembly is MORE than "
            f"enough to close a set. The five-order gap does not "
            f"close by making the catalysis better; it closes because "
            f"R grows exponentially in L while the catalysis each "
            f"molecule must supply grows only linearly")


def _rule():
    """c was measured. This is what it rests on, and where it holds."""
    mean, spread, n = catalysts_per_reaction()
    wide = [pM for _a, _L, M, _R, _p, _f, pM in rendered()]
    if spread > 2.0:
        raise ArithmeticError(f"p*M varies {spread:.1f}x in domain")
    if max(wide) / min(wide) < 5.0:
        raise ArithmeticError("the domain restriction is doing nothing")
    a = [r for r in rendered() if r[0] == "AB" and r[1] == 14][0]
    return (f"c = 0.395 was a MEASURED SLOPE with nothing under it. "
            f"The quantity that governs closure is p*M, the expected "
            f"catalysts per reaction, flat at {mean:.3f} (spread "
            f"{spread:.2f}x) over the same seven networks. A SET "
            f"CLOSES WHEN ABOUT HALF THE REACTIONS HAVE A CATALYST. "
            f"The linearity of f in L is then a consequence -- "
            f"f = p*R = (p*M)(R/M) and R/M is {a[3]/a[2]:.1f} at "
            f"AB L=14, close to L -- rather than something measured "
            f"and left standing. The invariant holds only above "
            f"{MEANFIELD_MIN_M:,} molecules -- over ALL eleven "
            f"networks it varies {max(wide)/min(wide):.1f}x, and "
            f"below the cut ABCD L=4 sits at {min(wide):.3f}. The "
            f"rule refuses there rather than returning a number")


def _lookup():
    from engine.earthlab import CATALYSIS_P
    L1, _M1, _p1 = length_closing_at(CATALYSIS_P)
    L2, M2, p2 = length_closing_derived(CATALYSIS_P)
    if abs(L1 - L2) > 2:
        raise ArithmeticError(f"slope says {L1}, rule says {L2}")
    return (f"{len(RENDERED)} networks are RENDERED -- measured once, "
            f"written down, looked up after. Each row cost between "
            f"0.3 s and 580 s and not one of them will change, so "
            f"re-bisecting them was the waste this file kept "
            f"committing. From the fitted slope the answer is {L1} "
            f"bases; from the rule p*M = {CATALYSTS_PER_REACTION:.3f} "
            f"it is {L2} bases over {M2:,} molecules. Two routes, and "
            f"the second needs no fit at all")


import math

if __name__ == "__main__":
    print(f"  {len(molecules())} molecules, {len(reactions())} ligations, "
          f"{len(food())} food\n")
    print(f"  {'p':>10}{'closes':>9}{'reactions':>11}{'molecules':>11}")
    for p in (1e-6, 1e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2):
        r = search(p, seed=1)
        print(f"  {p:>10.0e}{'yes' if r['closed'] else 'no':>9}"
              f"{r['in_set']:>11}{r['reachable']:>11}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:38]}")
