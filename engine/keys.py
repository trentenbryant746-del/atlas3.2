"""
Keys: explicit addressing into one expert's window.

The cascade infers which expert owns a question, and inference is where the
losses are -- measured, free English reached ~70% while a canonical key
reached ~100%. A KEY removes the inference. It names the expert, and it
narrows the admissible answer to that expert's window before anything is
computed.

Two forms, because two things can serve as an address:

  NAMED     `chem: molar mass of water`   -- a prefix naming the expert
  ARTIFACT  a block of Python source      -- the artifact IS the key; its own
            identifiers become the window, so answers about it must be drawn
            from it and not from anywhere else

The second is the more interesting one. Handing the system a file opens a
window whose vocabulary is that file, and a question answered inside that
window cannot wander into another subject -- the failure that produced
`jupiter.spot` for "how wide is the planet".

An unknown key ABSTAINS and lists what it does know. Guessing which expert
was meant is the thing keys exist to stop.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

KEY = re.compile(r'^\s*([a-z][a-z0-9_]{1,15})\s*:\s*(.+)$', re.I | re.S)

# expert -> (what it answers, how its window is defined)
REGISTRY = {
    "arith":   "compositional arithmetic; window is the expression itself",
    "unit":    "dimensional conversion; window is the unit table",
    "date":    "dates, instants and durations; window is the calendar",
    "dna":     "sequence complement and GC content; window is ACGT",
    "chem":    "formulae and molar mass; window is the periodic table",
    "element": "the periodic table; window is 118 elements",
    "planet":  "seeded worlds; window is the seed",
    "galaxy":  "seeded galaxies; window is the seed",
    "game":    "game construction; window is the pick language",
    "code":    "code over the IR; window is the supplied source",
    "fact":    "grounded extraction; window is the supplied source text",
}


def looks_like_python(text):
    if not re.search(r'\b(def|class|import|return|lambda)\b', text):
        return False
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


def source_window(text):
    """identifiers an artifact makes askable -- and nothing else"""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return set()
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.update(a.arg for a in n.args.args)
        elif isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
    return names


def parse_key(prompt):
    """-> (expert, body, window, why). expert None means no key was given."""
    if looks_like_python(prompt):
        return ("code", prompt, source_window(prompt),
                "artifact key: the supplied Python source defines the window")
    m = KEY.match(prompt)
    if not m:
        return (None, prompt, None, "no key given; the cascade must infer")
    name, body = m.group(1).lower(), m.group(2).strip()
    if name not in REGISTRY:
        return ("?", body, None,
                f"unknown key {name!r}; known keys are {sorted(REGISTRY)}")
    return (name, body, None, f"key {name!r}: {REGISTRY[name]}")


def answer_in_window(question, window, source_text):
    """answer using ONLY what the window admits"""
    from engine.grounded import extract, ANSWERED
    asked = set(re.findall(r'[A-Za-z_][A-Za-z0-9_]*', question))
    outside = {w for w in asked
               if w in source_text or w in window} and None
    known = asked & window
    if not known:
        return None, (f"nothing in the question names anything the window "
                      f"contains; window holds {len(window)} identifiers")
    g = extract(question, source_text)
    if g.verdict != ANSWERED:
        return None, g.why
    return g.answer, f"within the artifact window, matched on {sorted(known)[:3]}"
