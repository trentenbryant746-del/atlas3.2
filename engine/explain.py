"""
Expression tree -> English derivation, with fidelity checked by round-trip.

An explanation that does not correspond to the computation is worse than no
explanation, so this does not simply render prose. Each step is emitted as a
(operation, operands, result-name) triple, the prose is generated FROM those
triples, and the triples are then re-executed. If re-executing the narrated
steps does not reproduce the program's own answer, the explanation is
rejected rather than shown.

Same discipline as belt-atlas/tools/compress.py: a representation claim is
only real if the representation reproduces the original.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.induce import Expr, ev                              # noqa: E402

WORD = {"add": "Add", "mul": "Multiply", "neg": "Negate", "inv": "Invert"}


def linearise(e, names, steps):
    """post-order -> a list of (op, [operand names], out name)"""
    if e.op == "leaf":
        i, c = e.kids
        return names[i] if c is None else str(c)
    kids = [linearise(k, names, steps) for k in e.kids if isinstance(k, Expr)]
    out = f"t{len(steps) + 1}"
    steps.append((e.op, kids, out))
    return out


def narrate(e, names):
    steps = []
    final = linearise(e, names, steps)
    lines = []
    for i, (op, kids, out) in enumerate(steps, 1):
        if op == "add":
            a, b = kids
            if b.startswith("-") or b.startswith("t") and False:
                pass
            lines.append(f"{i}. Add {a} and {b} -> {out}")
        elif op == "mul":
            a, b = kids
            lines.append(f"{i}. Multiply {a} by {b} -> {out}")
        elif op == "neg":
            lines.append(f"{i}. Negate {kids[0]} -> {out}")
        elif op == "inv":
            lines.append(f"{i}. Take the reciprocal of {kids[0]} -> {out}")
    lines.append(f"Answer: {final}")
    return lines, steps, final


def replay(steps, final, names, args):
    """execute the NARRATED steps -- not the tree -- and return the answer"""
    env = {n: Fraction(v) for n, v in zip(names, args)}

    def val(tok):
        if tok in env:
            return env[tok]
        return Fraction(int(tok))

    for op, kids, out in steps:
        if op == "add":
            env[out] = val(kids[0]) + val(kids[1])
        elif op == "mul":
            env[out] = val(kids[0]) * val(kids[1])
        elif op == "neg":
            env[out] = -val(kids[0])
        elif op == "inv":
            v = val(kids[0])
            if v == 0:
                raise ZeroDivisionError
            env[out] = Fraction(1, 1) / v
    return val(final)


def explain(e, names, args):
    """-> (lines, faithful: bool). faithful=False means do not show it."""
    lines, steps, final = narrate(e, names)
    try:
        want = ev(e, args)
        got = replay(steps, final, names, args)
        faithful = (want == got)
    except ZeroDivisionError:
        faithful = False
    return lines, faithful
