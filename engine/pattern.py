"""
Induce the PATTERN, not just the computation.

The sharpest limit of engine/induce.py was that a human still wrote the regex:
which spans of text are operands, and which questions a rule is about. This
removes that. Given raw (prompt, answer) pairs and nothing else, it recovers
the templates by anti-unification and emits the capture pattern.

Method, all of it mechanical:

  TOKENISE   split each prompt into words and numeric literals.
  SHAPE      replace every numeric literal with a hole. The shape is the
             token sequence that remains -- a behavioural fingerprint for
             surface form, the same trick observational equivalence plays
             for values.
  CLUSTER    prompts sharing a shape are instances of one template.
  ANTI-UNIFY within a cluster, positions that vary across instances become
             capture groups; positions that never vary become literal text.
             A position that is constant across every instance is part of
             the template even if it is a number ("100 centimetres").
  EMIT       build a regex from the alignment.

The one prior kept: a numeric literal is a CANDIDATE hole. That is much
weaker than supplying the rule, but it is not nothing, and it is why this
recovers arithmetic templates and would not recover "reverse the string X"
without extending the candidate set to quoted spans.
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TOKEN = re.compile(r'-?\d+|[^\s\d-]+|-')
NUMBER = re.compile(r'^-?\d+$')


def tokenise(s):
    return TOKEN.findall(s)


def shape(s):
    return tuple("§" if NUMBER.match(t) else t for t in tokenise(s))


def cluster(prompts):
    """-> {shape: [prompt, ...]}"""
    g = defaultdict(list)
    for p in prompts:
        g[shape(p)].append(p)
    return g


def anti_unify(prompts):
    """Positions that vary become holes; positions that never vary are literal.

    A numeric position constant across EVERY instance is part of the template,
    not an operand -- "1 meter = 100 centimetres" must not become a parameter.
    """
    toks = [tokenise(p) for p in prompts]
    n = len(toks[0])
    holes = []
    for i in range(n):
        vals = {t[i] for t in toks}
        if len(vals) > 1:
            holes.append(i)
    return toks[0], holes


def build_regex(template_tokens, holes):
    out = []
    for i, t in enumerate(template_tokens):
        if i in holes:
            out.append(r'\s*(-?\d+)\s*')
        else:
            out.append(re.escape(t))
    # tokens were split on whitespace boundaries we no longer know; allow any
    pat = r'\s*'.join(x for x in out)
    return re.compile(pat.replace(r'\s*\s*', r'\s*'))


def induce_patterns(prompts, min_support=20):
    """-> [(regex, n_instances, example, hole_count)]"""
    out = []
    for shp, group in cluster(prompts).items():
        if len(group) < min_support:
            continue
        tmpl, holes = anti_unify(group)
        if not holes:
            continue
        out.append({
            "regex": build_regex(tmpl, holes),
            "n": len(group),
            "example": group[0],
            "arity": len(holes),
            "shape": " ".join(shp),
        })
    return sorted(out, key=lambda d: -d["n"])
