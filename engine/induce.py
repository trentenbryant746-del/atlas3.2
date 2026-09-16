"""
Induce a rule from examples. Nobody tells it the operation.

Bottom-up enumerative synthesis over the primitive basis that eval/compress.py
verified (ADD, MUL, NEG, INV) plus the operands and a few constants. Build
expressions by size; keep one representative per distinct VALUE VECTOR across
the training examples (observational equivalence), which collapses the search
enormously because most expressions are behaviourally identical. Stop when an
expression reproduces every training answer.

Two expressions, not one. After the first solution is found the search keeps
going for a STRUCTURALLY DIFFERENT expression with the same value vector. If
one exists, the pair becomes derive + check -- a REDUNDANT verification that
nobody wrote. If none exists, the induced rule is honestly reported as
unchecked, because a check that is a copy of the thing it checks is not a
check. That is the substring-match mistake in another costume.

What this does NOT do: invent primitives, invent check KINDS, or induce
anything outside arithmetic composition. It searches a basis it was handed.
"""
from __future__ import annotations

import itertools
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CONSTS = [1, 2, 100]


class Expr:
    __slots__ = ("op", "kids", "size", "txt")

    def __init__(self, op, kids, txt, size):
        self.op, self.kids, self.txt, self.size = op, kids, txt, size

    def __repr__(self):
        return self.txt


def leaf(name, idx=None, const=None):
    # one leaf op for both operands and constants -- distinguishing them by
    # op name meant ev() fell through to the binary branch for constants
    e = Expr("leaf", (), name, 1)
    e.kids = (idx, const)
    return e


def ev(e, args):
    if e.op == "leaf":
        i, c = e.kids
        return Fraction(args[i]) if c is None else Fraction(c)
    if e.op == "neg":
        return -ev(e.kids[0], args)
    if e.op == "inv":
        v = ev(e.kids[0], args)
        if v == 0:
            raise ZeroDivisionError
        return Fraction(1, 1) / v
    a = ev(e.kids[0], args)
    b = ev(e.kids[1], args)
    return a + b if e.op == "add" else a * b


def synthesize(examples, max_size=7, want_two=True, node_cap=120000):
    """examples: [(args, target Fraction)]. -> (derive, check|None, stats)"""
    argss = [a for a, _ in examples]
    targets = tuple(t for _, t in examples)
    arity = len(argss[0])

    def vec(e):
        out = []
        for a in argss:
            try:
                out.append(ev(e, a))
            except ZeroDivisionError:
                return None
            except (OverflowError, ValueError):
                return None
        return tuple(out)

    by_size = {1: []}
    seen = {}
    for i in range(arity):
        by_size[1].append(leaf(f"x{i}", idx=i))
    for c in CONSTS:
        by_size[1].append(leaf(str(c), const=c))
    for e in by_size[1]:
        v = vec(e)
        if v is not None and v not in seen:
            seen[v] = e

    found, alt, nodes = None, None, 0
    for e in by_size[1]:
        if vec(e) == targets and found is None:
            found = e

    for size in range(2, max_size + 1):
        cur = []
        # unary
        for sub in by_size.get(size - 1, []):
            for op, sym in (("neg", "-"), ("inv", "1/")):
                e = Expr(op, (sub,), f"{sym}({sub.txt})", size)
                v = vec(e)
                nodes += 1
                if v is None:
                    continue
                if v == targets:
                    if found is None:
                        found = e
                    elif alt is None and _structurally_different(found, e):
                        alt = e
                if v in seen:
                    continue
                seen[v] = e
                cur.append(e)
        # binary
        for la in range(1, size):
            lb = size - 1 - la
            if lb < 1:
                continue
            for x in by_size.get(la, []):
                for y in by_size.get(lb, []):
                    for op, sym in (("add", "+"), ("mul", "*")):
                        e = Expr(op, (x, y), f"({x.txt}{sym}{y.txt})", size)
                        v = vec(e)
                        nodes += 1
                        if v is None:
                            continue
                        if v == targets:
                            if found is None:
                                found = e
                            elif alt is None and _structurally_different(found, e):
                                alt = e
                        if v in seen:
                            continue
                        seen[v] = e
                        cur.append(e)
                    if nodes > node_cap:
                        break
        by_size[size] = cur
        if found is not None and (alt is not None or not want_two):
            break
        if nodes > node_cap:
            break
    return found, alt, {"nodes": nodes, "classes": len(seen)}


def _subtrees(e):
    yield e.txt
    if e.op in ("neg", "inv"):
        yield from _subtrees(e.kids[0])
    elif e.op in ("add", "mul"):
        yield from _subtrees(e.kids[0])
        yield from _subtrees(e.kids[1])


def _ops(e):
    from collections import Counter
    c = Counter()

    def walk(n):
        if n.op != "leaf":
            c[n.op] += 1
        for k in (n.kids if n.op != "leaf" else ()):
            if isinstance(k, Expr):
                walk(k)
    walk(e)
    return c


def _structurally_different(a, b) -> bool:
    """A second derivation, not a rewrite of the first.

    The first version accepted -(-(x0+x1)) as an independent check on
    (x0+x1). Double negation is the same derivation wearing a hat, and a
    check that contains the thing it checks proves nothing -- the same
    mistake as validating an answer by finding it inside itself.

    So: neither may contain the other as a subexpression, and their operator
    multisets must differ.
    """
    if a.txt == b.txt:
        return False
    if a.txt in set(_subtrees(b)) or b.txt in set(_subtrees(a)):
        return False
    return _ops(a) != _ops(b)


def as_fn(e):
    return lambda *args: ev(e, list(args))
