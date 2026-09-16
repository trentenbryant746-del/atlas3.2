"""
Keep rival programs; separate them with generated counterexamples.

Observational deduplication is exact only over the examples tested. Two
programs with the same training value vector can disagree everywhere else,
and keeping one representative silently discards the other -- possibly the
one that generalises. Demonstrated, not hypothesised: meet-in-the-middle and
bottom-up search returned DIFFERENT programs for `pct` from identical data,
because they stored different representatives of the same class.

So: retain the shortest candidate per OPERATOR SIGNATURE rather than one per
value vector, then manufacture inputs that force them apart.

    AGREE EVERYWHERE   the rivals are extensionally equal on the generated
                       domain. The induction is determined; pick the shortest.
    DISAGREE           the training examples did not pin the rule. This is
                       the honest outcome and it is actionable: the
                       counterexample is exactly the next example to label.

A single surviving class is evidence, not proof -- the generated domain is
finite. But an induction that survives thousands of adversarial inputs is a
different object from one that fit six points.
"""
from __future__ import annotations

import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.induce import Expr, leaf, ev, CONSTS                # noqa: E402


def signature(e):
    """multiset of operators -- a structural fingerprint, not a value one"""
    c = Counter()

    def walk(n):
        if n.op != "leaf":
            c[n.op] += 1
            for k in n.kids:
                if isinstance(k, Expr):
                    walk(k)
    walk(e)
    return tuple(sorted(c.items()))


def all_solutions(examples, max_size=9, node_cap=2_000_000, max_keep=40):
    """every program fitting the examples, one per operator signature"""
    argss = [a for a, _ in examples]
    targets = tuple(t for _, t in examples)
    arity = len(argss[0])

    def vec(e):
        out = []
        for a in argss:
            try:
                out.append(ev(e, a))
            except (ZeroDivisionError, OverflowError, ValueError):
                return None
        return tuple(out)

    sols = {}
    seen = {}
    by_size = {1: []}
    for i in range(arity):
        by_size[1].append(leaf(f"x{i}", idx=i))
    for c in CONSTS:
        by_size[1].append(leaf(str(c), const=c))

    def consider(e):
        v = vec(e)
        if v is None:
            return False
        if v == targets:
            s = signature(e)
            if s not in sols:
                sols[s] = e
        if v in seen:
            return False
        seen[v] = e
        return True

    for e in by_size[1]:
        consider(e)
    nodes = 0
    for size in range(2, max_size + 1):
        cur = []
        for sub in by_size.get(size - 1, []):
            for op, sym in (("neg", "-"), ("inv", "1/")):
                e = Expr(op, (sub,), f"{sym}({sub.txt})", size)
                nodes += 1
                if consider(e):
                    cur.append(e)
        for la in range(1, size):
            lb = size - 1 - la
            if lb < 1:
                continue
            for x in by_size.get(la, []):
                for y in by_size.get(lb, []):
                    for op, sym in (("add", "+"), ("mul", "*")):
                        e = Expr(op, (x, y), f"({x.txt}{sym}{y.txt})", size)
                        nodes += 1
                        if consider(e):
                            cur.append(e)
                if nodes > node_cap:
                    break
        by_size[size] = cur
        if len(sols) >= max_keep or nodes > node_cap:
            break
    return list(sols.values()), {"nodes": nodes, "signatures": len(sols)}


UNDEF = object()


def counterexamples(cands, arity, n=2000, lo=-60, hi=60, seed=5):
    """-> (classes, first_real_disagreement, partiality)

    Two candidates CONFLICT only where both are defined and disagree.
    1/(1/(x)) equals x everywhere except x=0, where it is undefined -- that
    is a smaller DOMAIN, not a different rule, and the first version of this
    counted it as underdetermination on all five basic operations. Partiality
    is reported separately and the more total candidate is preferred.
    """
    rng = random.Random(seed)
    probes = [[rng.randint(lo, hi) for _ in range(arity)] for _ in range(n)]

    vals = []
    for c in cands:
        row = []
        for p in probes:
            try:
                row.append(ev(c, p))
            except (ZeroDivisionError, OverflowError, ValueError):
                row.append(UNDEF)
        vals.append(row)

    def conflict(i, j):
        for k in range(len(probes)):
            a, b = vals[i][k], vals[j][k]
            if a is not UNDEF and b is not UNDEF and a != b:
                return k
        return None

    # group by "no conflict with the class representative"
    classes, reps, first = [], [], None
    for i in range(len(cands)):
        placed = False
        for ci, r in enumerate(reps):
            k = conflict(i, r)
            if k is None:
                classes[ci].append(cands[i])
                placed = True
                break
            elif first is None:
                first = (probes[k],
                         {cands[i].txt: vals[i][k], cands[r].txt: vals[r][k]})
        if not placed:
            classes.append([cands[i]])
            reps.append(i)

    partial = sum(1 for row in vals if any(v is UNDEF for v in row))
    # within a class prefer the most total, then the shortest
    for ci, grp in enumerate(classes):
        grp.sort(key=lambda c: (sum(1 for p in probes
                                    if _undefined(c, p)), c.size))
    return classes, first, partial


def _undefined(c, p):
    try:
        ev(c, p)
        return False
    except (ZeroDivisionError, OverflowError, ValueError):
        return True
