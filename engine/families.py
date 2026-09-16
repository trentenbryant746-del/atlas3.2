"""
Generate new families instead of waiting to observe them.

The system could only recognise templates it had instances of, which caps
coverage at whatever the corpus happened to contain -- nine. But a family is
just (surface form, operand slots, program), and the program space is the
basis we already have. So enumerate programs, render each as a surface form,
sample operands, and compute answers. The family exists before anyone asks a
question in it.

Every generated family is VERIFIED BY INDUCING IT BACK. Take the examples the
family produced, run the synthesiser on them, and check the recovered program
agrees with the original on fresh inputs. This catches the two ways a
generated family can be junk:

  DEGENERATE   the surface does not determine the operands, so different
               questions render identically and no program can fit.
  COLLAPSED    the program is extensionally equal to a simpler one already
               generated -- "(x0+x0)" is not a new family, it is 2*x0.

A family that cannot be induced back from its own examples is discarded, not
shipped. Generating unusable families is exactly the 640,000-proxy-record
failure in another costume.
"""
from __future__ import annotations

import random
import sys
from fractions import Fraction
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.induce import Expr, leaf, ev, CONSTS                # noqa: E402
from engine.induce2 import synthesize_mim                       # noqa: E402

VARS = ["a", "b", "c", "d"]


def enumerate_programs(arity, max_size, cap=4000):
    """distinct-behaviour programs over `arity` variables, by size"""
    # ONE generator. Re-seeding per element made every variable in a row
    # take the same value, so x0 and x1 were observationally identical, dedup
    # deleted x1, and no program using both variables could ever be built.
    # The enumerator returned zero families and looked like a logic bug.
    _rng = random.Random(97)
    probe = [[_rng.choice([-9, -7, -4, -3, -2, 2, 3, 5, 6, 8, 11])
              for _ in range(arity)] for _ in range(12)]

    def vec(e):
        out = []
        for p in probe:
            try:
                out.append(ev(e, p))
            except (ZeroDivisionError, OverflowError, ValueError):
                return None
        return tuple(out)

    by_size = {1: [leaf(f"x{i}", idx=i) for i in range(arity)]
                  + [leaf(str(c), const=c) for c in CONSTS]}
    seen, keep = {}, []
    for e in by_size[1]:
        v = vec(e)
        if v is not None and v not in seen:
            seen[v] = e
    for size in range(2, max_size + 1):
        cur = []
        for sub in by_size.get(size - 1, []):
            for op, sym in (("neg", "-"), ("inv", "1/")):
                e = Expr(op, (sub,), f"{sym}({sub.txt})", size)
                v = vec(e)
                if v is None or v in seen:
                    continue
                seen[v] = e; cur.append(e)
        for la in range(1, size):
            lb = size - 1 - la
            if lb < 1:
                continue
            for x in by_size.get(la, []):
                for y in by_size.get(lb, []):
                    for op, sym in (("add", "+"), ("mul", "*")):
                        e = Expr(op, (x, y), f"({x.txt}{sym}{y.txt})", size)
                        v = vec(e)
                        if v is None or v in seen:
                            continue
                        seen[v] = e; cur.append(e)
        by_size[size] = cur
        keep.extend(cur)
        if len(keep) > cap:
            break
    # only programs that actually USE every variable are real n-ary families
    return [e for e in keep
            if all(f"x{i}" in e.txt for i in range(arity))]


def infix(e):
    """render a program as ordinary arithmetic notation"""
    if e.op == "leaf":
        i, c = e.kids
        return VARS[i] if c is None else str(c)
    if e.op == "neg":
        return f"-{infix(e.kids[0])}"
    if e.op == "inv":
        return f"1/({infix(e.kids[0])})"
    a, b = infix(e.kids[0]), infix(e.kids[1])
    return f"({a} + {b})" if e.op == "add" else f"({a} × {b})"


def render(e, arity):
    """surface template with {0}..{n} slots"""
    s = infix(e)
    for i in range(arity):
        s = s.replace(VARS[i], "{%d}" % i)
    return f"Evaluate: {s}. Show a brief check."


def make_family(e, arity, n_examples=12, rng=None):
    rng = rng or random.Random(0)
    tmpl = render(e, arity)
    exs = []
    tries = 0
    while len(exs) < n_examples and tries < n_examples * 20:
        tries += 1
        args = [rng.randint(-40, 40) for _ in range(arity)]
        try:
            val = ev(e, args)
        except (ZeroDivisionError, OverflowError, ValueError):
            continue
        exs.append((args, val, tmpl.format(*args)))
    return {"program": e, "arity": arity, "template": tmpl, "examples": exs}


def verify_family(fam, probes=300, seed=11):
    """induce the family back from its own examples; must agree on fresh input"""
    exs = fam["examples"]
    if len(exs) < 6:
        return False, "too few valid examples"
    train = [(a, v) for a, v, _ in exs[:6]]
    rec, _st = synthesize_mim(train, max_size=max(9, fam["program"].size))
    if rec is None:
        return False, "not re-inducible from its own examples"
    rng = random.Random(seed)
    agree = checked = 0
    for _ in range(probes):
        args = [rng.randint(-50, 50) for _ in range(fam["arity"])]
        try:
            a = ev(fam["program"], args)
            b = ev(rec, args)
        except (ZeroDivisionError, OverflowError, ValueError):
            continue
        checked += 1
        agree += (a == b)
    if checked == 0:
        return False, "no defined probes"
    return agree == checked, f"recovered {rec}, agreed {agree}/{checked}"
