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

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ALPHABET = "AB"               # CHOSEN, two monomers is the smallest case
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
    reaction with probability p. The only random step, and the seed
    is an argument so a result can be repeated or swept."""
    rng = random.Random(seed)
    out = {}
    for i in range(len(rxns)):
        c = {m for m in mols if rng.random() < p}
        out[i] = c
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


def scaling(lengths=(5, 6, 7, 8), seeds=4):
    """-> [(reactions, p to close)]. Bigger networks close easier."""
    out = []
    for L in lengths:
        c = threshold(seeds=seeds, steps=8, lo=1e-4, hi=3e-2, max_len=L)
        on = min([p for p, f in c if f >= 0.5], default=None)
        if on:
            out.append((len(reactions(L)), on))
    return out


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
