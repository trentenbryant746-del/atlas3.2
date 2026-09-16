"""
A much larger grammar, and the measurement that says when to stop.

Adding rules raises coverage. It also raises AMBIGUITY -- the number of
distinct parses a sentence admits -- and ambiguity grows faster than
coverage does. That is the wall every hand-written grammar has hit, and it
is measurable here rather than something to be warned about.

So this tracks three curves as the rule set grows:

    coverage    grammatical sentences that parse
    precision   ungrammatical sentences still refused
    ambiguity   mean parses per sentence

A grammar that parses everything, including nonsense, in fifty ways has not
understood English. It has stopped discriminating.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# ---- categories --------------------------------------------------------
CATS = ("DET N ADJ ADV V AUX P CONJ PRON WH NUM REL "
        "NP VP PP AP S SBAR Q").split()
globals().update({c: c for c in CATS})

LEXICON = {}


def add(words, cat):
    for w in words.split():
        LEXICON.setdefault(w, set()).add(cat)


add("what which how who where when why whose", WH)
add("is are was were be been being am", V)
add("does do did has have had can could will would should may might must", AUX)
add("the a an this that these those its his her their my your our", DET)
add("of in to for from with by on at into onto over under between through "
    "about across against during without within", P)
add("and or but nor so yet", CONJ)
add("it he she they we you i him her them us me", PRON)
add("that which who whom whose", REL)
add("very quite rather extremely nearly almost approximately roughly", ADV)
add("many much far old heavy light large small big long short high low deep "
    "wide narrow fast slow hot cold dense bright dark new ancient stable "
    "radioactive neutral charged simple complex", ADJ)
add("mass radius gravity period distance density temperature charge spin "
    "element atom star planet moon galaxy sequence formula compound mixture "
    "proton neutron electron isotope nucleus orbit year day second metre "
    "meter gram kilogram litre number value answer result rule law force "
    "energy speed weight length width height volume area time", N)
add("earth mars venus mercury jupiter saturn uranus neptune pluto sun moon "
    "gold silver iron carbon oxygen hydrogen helium water ice quartz", N)
add("calculate compute find convert evaluate measure solve determine give "
    "show tell explain map generate produce contains equals means", V)

RULES = {
    # noun phrases
    (DET, N): NP, (DET, AP): NP, (ADJ, N): N, (ADJ, AP): AP, (N, N): N,
    (NUM, N): NP, (PRON,): NP,
    (AP, N): N,
    (NP, PP): NP, (N, PP): NP, (NP, SBAR): NP,
    (NP, CONJ_NP := "NP_CONJ"): NP,
    # adjective phrases
    (ADV, ADJ): AP, (ADJ,): AP,
    # prepositional
    (P, NP): PP, (P, N): PP, (P, PRON): PP,
    # verb phrases
    (V, NP): VP, (V, N): VP, (V, PP): VP, (V, AP): VP, (V, PRON): VP,
    (AUX, VP): VP, (AUX, V): VP, (VP, PP): VP, (VP, NP): VP,
    (ADV, VP): VP, (VP, ADV): VP,
    # questions and sentences
    (WH, VP): S, (WH, NP): S, (WH, N): S, (WH, AP): Q, (WH, ADJ): Q,
    (Q, VP): S, (Q, NP): S, (Q, V): S,
    (NP, VP): S, (PRON, VP): S, (S, PP): S,
    (AUX, S): S, (V, S): S,
    # subordinate / relative
    (REL, VP): SBAR, (REL, S): SBAR, (SBAR, PP): SBAR,
    # coordination
    (NP, "NP_CONJ"): NP, (CONJ, NP): "NP_CONJ",
    (S, "S_CONJ"): S, (CONJ, S): "S_CONJ",
    (VP, "VP_CONJ"): VP, (CONJ, VP): "VP_CONJ",
}


@dataclass(frozen=True)
class Node:
    cat: str
    text: str
    kids: tuple = ()


def lex(tok):
    t = tok.lower().strip("?.,;:!")
    if re.fullmatch(r'-?\d+(\.\d+)?', t):
        return [Node(NUM, t)]
    cats = LEXICON.get(t)
    return [Node(c, t) for c in cats] if cats else None


def parse_all(sentence, rules=None, cap=400):
    """-> (list of root nodes, unknown tokens). Every parse, not the first."""
    rules = rules if rules is not None else RULES
    toks = sentence.split()
    cells, unknown = [], []
    for t in toks:
        ns = lex(t)
        if ns is None:
            unknown.append(t)
        cells.append(ns or [])
    if unknown:
        return [], unknown
    n = len(cells)
    table = {(i, 1): list(cells[i]) for i in range(n)}
    # unary closure
    for i in range(n):
        for a in list(table[(i, 1)]):
            c = rules.get((a.cat,))
            if c and not any(x.cat == c for x in table[(i, 1)]):
                table[(i, 1)].append(Node(c, a.text, (a,)))
    for span in range(2, n + 1):
        for i in range(n - span + 1):
            here = []
            for k in range(1, span):
                for a in table.get((i, k), []):
                    for b in table.get((i + k, span - k), []):
                        c = rules.get((a.cat, b.cat))
                        if c:
                            here.append(Node(c, f"{a.text} {b.text}", (a, b)))
                            if len(here) > cap:
                                break
            table[(i, span)] = here
    roots = table.get((0, n), [])
    return [r for r in roots if r.cat in (S, Q, NP, VP)], []


def distinct_parses(sentence, rules=None):
    roots, unk = parse_all(sentence, rules)
    if unk:
        return None, unk
    return len(roots), []
