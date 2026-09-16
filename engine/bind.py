"""
Typed atoms, binding rules, and the elements they make.

The composed experts were meaningless because they were UNTYPED. Nothing
stopped `x2*x0` from multiplying a duration by a count and adding a ratio to
the result -- a valid computation over Fractions and nonsense as a quantity.

units.py already solved this for conversion: metres to kilograms is refused
because the dimension exponents disagree, before any arithmetic runs. The
same move applies to the atom basis. Give every atom a TYPE SIGNATURE and
composition stops being free:

    ADD : T x T -> T          you may only add like to like
    MUL : A x B -> A*B        dimensions multiply
    INV : A     -> A^-1
    SQRT: A^2k  -> A^k        only of an even-powered dimension

A binding that violates a signature is not a low-scoring compound, it is not
a compound at all. What survives is an ELEMENT: a multi-step compound whose
type signature states what it means, carrying the provenance chain that says
how it was built.

MEANINGLESS ATOMS BIND ANYWAY, which is the point. A bare dimensionless
constant means nothing alone; bound into `time = sqrt(dist^3 / mu)` it is
the thing that makes the equation balance. Meaning is a property of the
binding, not of the atom.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass

# dimension exponents over (length, mass, time)
DIMLESS = (0, 0, 0)


def dmul(a, b):
    return tuple(x + y for x, y in zip(a, b))


def dinv(a):
    return tuple(-x for x in a)


def dsqrt(a):
    if any(x % 2 for x in a):
        return None                   # sqrt of an odd-powered dimension
    return tuple(x // 2 for x in a)


@dataclass(frozen=True)
class Typed:
    label: str
    dim: tuple
    size: int = 1

    def __repr__(self):
        return f"{self.label}:{self.dim}"


def bind(op, a, b=None):
    """-> Typed or None. None means the binding is not permitted."""
    if op == "add":
        if a.dim != b.dim:
            return None               # cannot add unlike quantities
        return Typed(f"({a.label}+{b.label})", a.dim, a.size + b.size + 1)
    if op == "mul":
        return Typed(f"({a.label}*{b.label})", dmul(a.dim, b.dim),
                     a.size + b.size + 1)
    if op == "inv":
        return Typed(f"1/({a.label})", dinv(a.dim), a.size + 1)
    if op == "sqrt":
        d = dsqrt(a.dim)
        if d is None:
            return None
        return Typed(f"sqrt({a.label})", d, a.size + 1)
    if op == "neg":
        return Typed(f"-({a.label})", a.dim, a.size + 1)
    raise ValueError(op)


UNARY = ("inv", "sqrt", "neg")
BINARY = ("add", "mul")


def grow(seeds, max_size=5, cap=20000):
    """-> (elements, attempted, refused). Elements are typed compounds."""
    pool = list(seeds)
    seen = {s.label for s in pool}
    attempted = refused = 0
    by_size = {1: list(pool)}
    for size in range(2, max_size + 1):
        cur = []
        for a in by_size.get(size - 1, []):
            for op in UNARY:
                attempted += 1
                t = bind(op, a)
                if t is None:
                    refused += 1
                    continue
                if t.label in seen:
                    continue
                seen.add(t.label)
                cur.append(t)
        for la in range(1, size):
            lb = size - 1 - la
            if lb < 1:
                continue
            for a in by_size.get(la, []):
                for b in by_size.get(lb, []):
                    for op in BINARY:
                        attempted += 1
                        t = bind(op, a, b)
                        if t is None:
                            refused += 1
                            continue
                        if t.label in seen:
                            continue
                        seen.add(t.label)
                        cur.append(t)
                        if len(cur) > cap:
                            break
        by_size[size] = cur
        pool += cur
    return pool, attempted, refused


def elements_of_dim(pool, dim):
    return [t for t in pool if t.dim == dim]
