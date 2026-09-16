"""
Compression made visible: hash-cons the atoms and draw what is shared.

The 9->4 primitive result was a number in a report. It is also a SHAPE: when
several compounds reduce to the same primitives, they share subtrees, and
sharing is exactly what a DAG draws and a tree cannot.

Hash-consing gives the measurement and the picture at once. Every distinct
subexpression becomes one node; identical subexpressions across different
rules collapse onto it. Then

    tree nodes   what you would draw if every compound were separate
    dag nodes    what is actually there once sharing is taken out
    ratio        the compression, verified by RECONSTRUCTION rather than
                 asserted -- every original expression is rebuilt from the
                 DAG and must evaluate identically on random inputs

A DAG that cannot rebuild its inputs is a smaller picture, not a
compression. That distinction is the whole discipline.
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.induce import Expr, ev                              # noqa: E402


def key_of(e):
    """structural key -- identical structure gets one node"""
    if e.op == "leaf":
        i, c = e.kids
        return ("leaf", i, c)
    return (e.op,) + tuple(key_of(k) for k in e.kids if isinstance(k, Expr))


class DAG:
    def __init__(self):
        self.nodes = {}        # key -> id
        self.meta = {}         # id -> (op, label, [child ids], [owners])
        self.roots = {}        # rule name -> id

    def add(self, e, owner):
        k = key_of(e)
        if k in self.nodes:
            nid = self.nodes[k]
            if owner not in self.meta[nid][3]:
                self.meta[nid][3].append(owner)
            return nid
        kids = [self.add(c, owner) for c in e.kids if isinstance(c, Expr)]
        nid = f"d{len(self.nodes)}"
        self.nodes[k] = nid
        self.meta[nid] = (e.op, _label(e), kids, [owner])
        return nid

    def insert(self, name, e):
        self.roots[name] = self.add(e, name)

    def tree_size(self, e):
        n = 1
        for c in e.kids if e.op != "leaf" else ():
            if isinstance(c, Expr):
                n += self.tree_size(c)
        return n

    def rebuild(self, nid):
        op, label, kids, _ = self.meta[nid]
        if op == "leaf":
            for k, v in self.nodes.items():
                if v == nid:
                    _, i, c = k
                    e = Expr("leaf", (), label, 1)
                    e.kids = (i, c)
                    return e
        subs = [self.rebuild(k) for k in kids]
        e = Expr(op, tuple(subs), label, 1 + sum(s.size for s in subs))
        return e

    def shared(self):
        return {nid: m for nid, m in self.meta.items() if len(m[3]) > 1}


def _label(e):
    if e.op == "leaf":
        i, c = e.kids
        return f"x{i}" if c is None else str(c)
    return {"add": "+", "mul": "x", "neg": "-", "inv": "1/"}[e.op]


def verify_reconstruction(dag, originals, arity_of, trials=200, seed=3):
    """every original must be rebuildable from the DAG and behave identically"""
    rng = random.Random(seed)
    bad = []
    for name, e in originals.items():
        rebuilt = dag.rebuild(dag.roots[name])
        ar = arity_of[name]
        for _ in range(trials):
            args = [rng.randint(-20, 20) or 3 for _ in range(ar)]
            try:
                a = ev(e, args)
            except ZeroDivisionError:
                continue
            try:
                b = ev(rebuilt, args)
            except ZeroDivisionError:
                bad.append((name, args, "rebuilt divides by zero"))
                break
            if a != b:
                bad.append((name, args, f"{a} != {b}"))
                break
    return not bad, bad


def scene(dag, title="compression"):
    """a .tscn of the DAG. Shared atoms are drawn once and named by owners."""
    L = ["[gd_scene load_steps=1 format=3]", "",
         f'[node name="{title}" type="Node2D"]', ""]
    depth = {}

    def d(nid):
        if nid in depth:
            return depth[nid]
        kids = dag.meta[nid][2]
        depth[nid] = 0 if not kids else 1 + max(d(k) for k in kids)
        return depth[nid]

    for nid in dag.meta:
        d(nid)
    rows = {}
    for nid, dd in depth.items():
        rows.setdefault(dd, []).append(nid)
    for dd, ids in rows.items():
        for i, nid in enumerate(ids):
            op, label, kids, owners = dag.meta[nid]
            L.append(f'[node name="{nid}_{op}" type="Node2D" parent="."]')
            L.append(f'position = Vector2({(i - len(ids)/2) * 150:.1f}, {-dd*130})')
            L.append(f'metadata/token = "{nid}"')
            L.append(f'metadata/label = "{label}"')
            L.append(f'metadata/owners = "{",".join(sorted(owners))}"')
            L.append(f'metadata/shared = "{len(owners)}"')
            L.append("")
    return "\n".join(L)
