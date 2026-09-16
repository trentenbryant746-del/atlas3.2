"""
Search the composed-expert space against observed data.

A composed expert has no questions from people, but data can ask it one:
does it reproduce a relationship that actually holds? That turns an
arbitrary function into a candidate LAW, and turns "test all of them out"
into something with a pass/fail.

Two hazards, both handled rather than hoped away:

  MIXED UNITS       belt-atlas stores planetary `year` in DAYS for the inner
                    planets and YEARS for the outer ones, with nothing
                    recording which. The first search fit nothing, and the
                    reason was the corpus, not the search. Testing rules
                    against data found a data defect -- which is the most
                    useful thing a failed fit can do.
  MULTIPLE TESTING  searching thousands of expressions against eight points
                    WILL turn up fits by chance. So: fit on a subset, and
                    require the winner to hold on bodies it never saw. A
                    shuffled-target control measures how often the search
                    finds "a law" in noise.
"""
from __future__ import annotations

import itertools
import math
import random

# atoms, now including a root -- a^1.5 is unreachable from +,x,-,1/ alone
OPS1 = {"neg": lambda a: -a,
        "inv": lambda a: (1.0 / a) if a else None,
        "sqrt": lambda a: math.sqrt(a) if a >= 0 else None,
        "sq": lambda a: a * a}
OPS2 = {"add": lambda a, b: a + b,
        "mul": lambda a, b: a * b}


def enumerate_exprs(nvars, max_size=4, consts=(1.0, 2.0)):
    """(label, fn) over the seeded atom vocabulary"""
    pool = [(f"x{i}", (lambda i: (lambda v: v[i]))(i)) for i in range(nvars)]
    pool += [(str(c), (lambda c: (lambda v: c))(c)) for c in consts]
    by = {1: pool}
    seen = set(l for l, _ in pool)
    for size in range(2, max_size + 1):
        cur = []
        for lbl, fn in by.get(size - 1, []):
            for op, f in OPS1.items():
                nl = f"{op}({lbl})"
                if nl in seen:
                    continue
                seen.add(nl)
                cur.append((nl, (lambda f, fn: (lambda v: _ap1(f, fn, v)))(f, fn)))
        for la in range(1, size):
            lb = size - 1 - la
            if lb < 1:
                continue
            for l1, f1 in by.get(la, []):
                for l2, f2 in by.get(lb, []):
                    for op, f in OPS2.items():
                        nl = f"{op}({l1},{l2})"
                        if nl in seen:
                            continue
                        seen.add(nl)
                        cur.append((nl, (lambda f, f1, f2:
                                         (lambda v: _ap2(f, f1, f2, v)))(f, f1, f2)))
        by[size] = cur
    return [e for s in sorted(by) for e in by[s]]


def _ap1(f, fn, v):
    a = fn(v)
    return None if a is None else f(a)


def _ap2(f, f1, f2, v):
    a, b = f1(v), f2(v)
    return None if a is None or b is None else f(a, b)


def fits(fn, rows, tol=0.02):
    for xs, y in rows:
        try:
            got = fn(xs)
        except (ValueError, ZeroDivisionError, OverflowError):
            return False
        if got is None or not math.isfinite(got):
            return False
        if y == 0:
            if abs(got) > tol:
                return False
        elif abs(got - y) / abs(y) > tol:
            return False
    return True


def search(train, held, nvars, max_size=4, tol=0.02):
    """-> (label, fits_held) for every expression fitting TRAIN"""
    hits = []
    for lbl, fn in enumerate_exprs(nvars, max_size):
        if fits(fn, train, tol):
            hits.append((lbl, fits(fn, held, tol)))
    return hits


def chance_rate(train, held, nvars, max_size=4, tol=0.02, trials=20, seed=1):
    """how often does the search find a 'law' when the target is shuffled?"""
    rng = random.Random(seed)
    found = 0
    for _ in range(trials):
        ys = [y for _, y in train]
        rng.shuffle(ys)
        shuf = [(xs, y) for (xs, _), y in zip(train, ys)]
        if search(shuf, held, nvars, max_size, tol):
            found += 1
    return found / trials
