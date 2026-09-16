"""
Meet-in-the-middle synthesis. Same result, found from both ends.

induce.py enumerates until an expression's value vector EQUALS the target,
so a size-9 rule requires building every expression up to size 9 -- 147,202
candidates at size 8 alone.

Here, every time an expression E with vector V is stored, we also ask what
its COMPLEMENT would have to be:

    for ADD:  we need W such that V + W = T   ->  W = T - V
    for MUL:  we need W such that V * W = T   ->  W = T / V

Both are computable because the basis is a field. If any already-known
expression has vector W, then ADD(E, W) or MUL(E, W) reproduces the target,
and we have found a size-(|E|+|W|+1) solution WITHOUT ever enumerating that
size. The search meets in the middle.

Cost: one extra hash lookup per stored expression. The table is already
built, so the complement check is essentially free.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.induce import Expr, leaf, ev, CONSTS                # noqa: E402


def synthesize_mim(examples, max_size=9, node_cap=3_000_000):
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

    seen = {}                       # value vector -> smallest expression
    by_size = {1: []}
    for i in range(arity):
        by_size[1].append(leaf(f"x{i}", idx=i))
    for c in CONSTS:
        by_size[1].append(leaf(str(c), const=c))

    def complement_hit(e, v):
        """is there a known W making ADD(e,W) or MUL(e,W) equal the target?"""
        w_add = tuple(t - x for t, x in zip(targets, v))
        if w_add in seen:
            o = seen[w_add]
            return Expr("add", (e, o), f"({e.txt}+{o.txt})", e.size + o.size + 1)
        try:
            if all(x != 0 for x in v):
                w_mul = tuple(Fraction(t) / x for t, x in zip(targets, v))
                if w_mul in seen:
                    o = seen[w_mul]
                    return Expr("mul", (e, o),
                                f"({e.txt}*{o.txt})", e.size + o.size + 1)
        except ZeroDivisionError:
            pass
        return None

    def store(e):
        v = vec(e)
        if v is None:
            return None, False
        if v == targets:
            return e, True
        hit = complement_hit(e, v)
        if hit is not None:
            return hit, True
        if v in seen:
            return None, False
        seen[v] = e
        return None, True           # stored, keep for growth

    for e in by_size[1]:
        found, _ = store(e)
        if found:
            return found, {"nodes": 0, "classes": len(seen), "via": "leaf"}

    nodes = 0
    for size in range(2, max_size + 1):
        cur = []
        for sub in by_size.get(size - 1, []):
            for op, sym in (("neg", "-"), ("inv", "1/")):
                e = Expr(op, (sub,), f"{sym}({sub.txt})", size)
                nodes += 1
                found, kept = store(e)
                if found:
                    return found, {"nodes": nodes, "classes": len(seen),
                                   "via": f"size {size} + complement"}
                if kept:
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
                        found, kept = store(e)
                        if found:
                            return found, {"nodes": nodes,
                                           "classes": len(seen),
                                           "via": f"size {size} + complement"}
                        if kept:
                            cur.append(e)
                if nodes > node_cap:
                    break
        by_size[size] = cur
        if nodes > node_cap:
            break
    return None, {"nodes": nodes, "classes": len(seen), "via": "exhausted"}
