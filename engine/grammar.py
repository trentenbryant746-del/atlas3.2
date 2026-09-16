"""
Language as a typed binding system -- the same machine as engine/bind.py.

The family approach caps recognition at templates that have been observed.
But language is compositional in the same way chemistry is: morphemes bind
into words, words into phrases, phrases into sentences, and the rules are
finite while the sentences are not. So the grammar is written exactly like
the dimensional typing, and it refuses ungrammatical bindings the way
dimensions refuse metres plus kilograms.

    bind("add", length, time)   -> None   the dimensions disagree
    bind("np",  det, verb)      -> None   the categories disagree

Same structure, different type lattice. No templates anywhere: a sentence
never seen before parses if its parts type-check.

WHAT THIS DOES AND DOES NOT SOLVE, because they are different problems.

  SYNTAX IS COMPOSITIONAL and this handles it. An unbounded set of
  sentences from a finite set of rules, which is exactly the property that
  made arithmetic parsing beat family matching.

  REFERENCE IS NOT. Parsing "what is the statute of limitations in
  California" perfectly yields a correct tree and no answer, because the
  answer is an asserted fact that no amount of grammar derives. The parse
  tells you WHICH EXPERT and WHICH ARGUMENTS -- which is precisely the
  recognition problem -- and then the expert still has to know the thing.

So a grammar removes the "only families it has seen" limit for RECOGNITION.
It does not remove the derived/asserted boundary, and nothing will.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# categories, the way dimensions are exponent vectors
DET, N, ADJ, V, P, NP, PP, VP, S, NUM, Q = (
    "DET", "N", "ADJ", "V", "P", "NP", "PP", "VP", "S", "NUM", "Q")

LEXICON = {
    "what": Q, "how": Q, "which": Q,
    "is": V, "are": V, "does": V, "has": V, "have": V, "find": V,
    "the": DET, "a": DET, "an": DET, "of": P, "in": P, "to": P, "for": P,
    "many": ADJ, "much": ADJ, "far": ADJ, "old": ADJ, "heavy": ADJ,
    "mass": N, "radius": N, "gravity": N, "period": N, "distance": N,
    "element": N, "atom": N, "star": N, "planet": N, "sequence": N,
    "days": N, "grams": N, "metres": N, "meters": N, "seconds": N,
    "earth": N, "mars": N, "moon": N, "gold": N, "water": N, "carbon": N,
}

# binding rules: (left, right) -> result. Finite; the sentences are not.
RULES = {
    (DET, N): NP, (ADJ, N): N, (N, N): N,
    (NP, PP): NP, (N, PP): NP,
    (P, NP): PP, (P, N): PP,
    (V, NP): VP, (V, N): VP, (VP, PP): VP,
    (Q, VP): S, (Q, NP): S, (NP, VP): S, (S, PP): S, (Q, N): S,
    (NUM, N): NP,
    (Q, ADJ): Q,          # "how far", "how many" -- a complex question word
}


@dataclass(frozen=True)
class Node:
    cat: str
    text: str
    kids: tuple = ()


def lex(tok):
    t = tok.lower().strip("?.,")
    if re.fullmatch(r'-?\d+(\.\d+)?', t):
        return Node(NUM, t)
    c = LEXICON.get(t)
    return Node(c, t) if c else None


def combine(a, b):
    """the binding rule. None means these categories do not bind."""
    c = RULES.get((a.cat, b.cat))
    return Node(c, f"{a.text} {b.text}", (a, b)) if c else None


def parse(sentence):
    """CYK over the rule table -> (root Node or None, unknown tokens)"""
    toks = sentence.split()
    cells, unknown = [], []
    for t in toks:
        n = lex(t)
        if n is None:
            unknown.append(t)
        cells.append([n] if n else [])
    if unknown:
        return None, unknown
    n = len(cells)
    table = {(i, 1): list(cells[i]) for i in range(n)}
    for span in range(2, n + 1):
        for i in range(n - span + 1):
            here = []
            for k in range(1, span):
                for a in table.get((i, k), []):
                    for b in table.get((i + k, span - k), []):
                        c = combine(a, b)
                        if c and not any(x.cat == c.cat for x in here):
                            here.append(c)
            table[(i, span)] = here
    roots = table.get((0, n), [])
    best = next((r for r in roots if r.cat == S), None) or (roots[0] if roots else None)
    return best, []


def tree(node, depth=0):
    pad = "  " * depth
    if not node.kids:
        return [f"{pad}{node.cat:<4} {node.text}"]
    out = [f"{pad}{node.cat:<4} {node.text}"]
    for k in node.kids:
        out += tree(k, depth + 1)
    return out
