"""
Grammar rules tied to the system's own rules: parse and mean at once.

grammar2 parsed, then a dimensional filter ran over the finished parses and
removed 14% of them. That is the wrong order. If the semantic action is
PART of the rule, an ill-typed combination is never built, its subtree
never grows, and the ambiguity explosion is cut off at the root instead of
mopped up at the end.

Every rule is therefore a pair:

    (catA, catB) -> (catC, action)

where `action(semA, semB)` returns a meaning or **None**. None kills that
branch mid-parse. The semantics are the types already in the repo --
dimensions from engine/bind.py, entities, and expert calls -- so the parse
does not produce a tree that then needs interpreting. IT PRODUCES A CALL.

    "what is the mass of earth"  ->  Query(attr='mass', entity='earth',
                                           dim=(0,1,0))

which is exactly the recognition problem -- which expert, which arguments --
solved compositionally rather than by matching a template.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

DET, N, ADJ, P, V, WH, NUM, NP, PP, VP, S, Q = (
    "DET N ADJ P V WH NUM NP PP VP S Q".split())

LENGTH, MASS, TIME, DIMLESS = (1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)


@dataclass(frozen=True)
class Sem:
    """a meaning: an attribute, an entity, a relation, or a finished query"""
    kind: str                 # attr | entity | rel | query | op | det
    name: str = ""
    dim: tuple | None = None
    args: tuple = ()

    def __repr__(self):
        if self.kind == "query":
            return f"Query({self.name} of {self.args[0].name if self.args else '?'})"
        return f"{self.kind}:{self.name}"


ATTRS = {"mass": MASS, "weight": MASS, "radius": LENGTH, "distance": LENGTH,
         "length": LENGTH, "width": LENGTH, "period": TIME, "year": TIME,
         "day": TIME, "time": TIME, "age": TIME, "gravity": (1, 0, -2),
         "speed": (1, 0, -1), "density": (-3, 1, 0), "number": DIMLESS}
ENTITIES = {"earth", "mars", "venus", "mercury", "jupiter", "saturn",
            "uranus", "neptune", "pluto", "sun", "moon", "gold", "water",
            "carbon", "iron", "star", "planet", "atom", "orbit"}

LEX = {}
for a, d in ATTRS.items():
    LEX.setdefault(a, []).append((N, Sem("attr", a, d)))
for e in ENTITIES:
    LEX.setdefault(e, []).append((N, Sem("entity", e)))
for w in "the a an this that".split():
    LEX[w] = [(DET, Sem("det", w))]
for w in "of for in".split():
    LEX[w] = [(P, Sem("rel", w))]
for w in "is are was were".split():
    LEX[w] = [(V, Sem("op", "be"))]
for w in "what how which".split():
    LEX[w] = [(WH, Sem("op", "ask"))]
for w in "heavy large old fast dense".split():
    LEX[w] = [(ADJ, Sem("attr", w, None))]


# ---- rules, each with the action that must succeed ---------------------
def r_det_n(a, b):
    """a determiner does not change the meaning, it just closes the phrase"""
    return b


def r_p_np(a, b):
    """`of earth` is a relation to an ENTITY. `of the year` is not."""
    if b.kind != "entity":
        return None
    return Sem("rel", a.name, args=(b,))


def r_n_pp(a, b):
    """attach a relation to an ATTRIBUTE -- this is where typing bites.
    `distance of earth` is fine; `distance of mass` is not, because an
    attribute cannot be the object of a possessive relation here."""
    if a.kind != "attr":
        return None
    if not b.args or b.args[0].kind != "entity":
        return None
    return Sem("query", a.name, a.dim, args=b.args)


def r_v_np(a, b):
    return Sem("query", b.name, b.dim, args=b.args) if b.kind == "query" else None


def r_wh_vp(a, b):
    return b if b.kind == "query" else None


def r_np_pp(a, b):
    """attach a further relation to an already-complete query.

    Syntactically free -- this is the rule that creates the Catalan
    explosion. Semantically it must say something: a second `of` phrase on
    a finished query is only meaningful if it refines the same entity, and
    most attachment sites do not, so most branches die here.
    """
    if a.kind != "query":
        return None
    if not b.args or b.args[0].kind != "entity":
        return None
    if a.args and b.args[0].name == a.args[0].name:
        return None                    # "of earth of earth"
    return None                        # no refinement relation is defined


def r_s_pp(a, b):
    """same, on a finished sentence"""
    return None


RULES = {
    (DET, N): (N, r_det_n),
    (NP, PP): (NP, r_np_pp),
    (S, PP): (S, r_s_pp),
    (VP, PP): (VP, r_np_pp),
    (DET, NP): (NP, r_det_n),
    (N, PP): (NP, r_n_pp),
    (P, N): (PP, r_p_np),
    (P, NP): (PP, r_p_np),
    (V, NP): (VP, r_v_np),
    (WH, VP): (S, r_wh_vp),
}


@dataclass(frozen=True)
class Node:
    cat: str
    sem: Sem
    text: str


def parse(sentence, apply_semantics=True):
    """-> (roots, unknown). With semantics off, it is grammar2's behaviour."""
    toks = sentence.split()
    cells, unknown = [], []
    for t in toks:
        e = LEX.get(t.lower().strip("?.,"))
        if not e:
            unknown.append(t)
        cells.append([Node(c, s, t) for c, s in (e or [])])
    if unknown:
        return [], unknown
    n = len(cells)
    tbl = {(i, 1): list(cells[i]) for i in range(n)}
    for span in range(2, n + 1):
        for i in range(n - span + 1):
            here = []
            for k in range(1, span):
                for a in tbl.get((i, k), []):
                    for b in tbl.get((i + k, span - k), []):
                        hit = RULES.get((a.cat, b.cat))
                        if not hit:
                            continue
                        cat, act = hit
                        if apply_semantics:
                            sem = act(a.sem, b.sem)
                            if sem is None:
                                continue          # branch dies here
                        else:
                            sem = a.sem
                        here.append(Node(cat, sem, f"{a.text} {b.text}"))
            tbl[(i, span)] = here
    return [r for r in tbl.get((0, n), []) if r.cat in (S, NP, VP)], []
