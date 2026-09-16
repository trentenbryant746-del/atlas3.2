"""
Natural-language routing onto computing rules.

The graft. belt-atlas could route human phrasing but only ever returned a
stored string; atlas2 computes and self-checks but only recognises the
generator's exact wording. This routes human phrasing to a rule that computes.

Four lessons carried over from belt-atlas, each paid for:

  TRIGGERS COME FROM THE OPERATION, NOT FROM PROSE. Every wrong routing
  decision there was made on a generic word that was unique only because the
  corpus was small (`big`, `who`, `percent`). Triggers here are declared per
  rule and are words that NAME the operation.

  NO SYNONYM MAY DECIDE ALONE. There, synonyms were wired to one namespace's
  vocabulary and dragged every topic into it. Here a trigger proposes; arity
  and margin dispose.

  ARITY IS STRUCTURAL EVIDENCE. New here, and it is the strongest signal
  available: "add 3 and 4" yields two operands, so any 4-operand rule is
  excluded outright regardless of what words appear.

  DECLINE, DO NOT GUESS. Ambiguity and no-match stay distinct verdicts.
"""
from __future__ import annotations

import re
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rules.arith import BY_NAME, fmt                            # noqa: E402
from engine.route import (Result, ANSWERED, AMBIGUOUS,          # noqa: E402
                          UNCOVERED, CONTRADICTED)

# rule -> (arity, trigger words). Triggers name the operation.
TRIGGERS = {
    "add":      (2, {"add", "plus", "sum", "total", "combined", "altogether",
                     "more"}),
    "sub":      (2, {"subtract", "minus", "less", "difference", "take",
                     "remove", "left", "fewer"}),
    "mul":      (2, {"multiply", "times", "product", "multiplied"}),
    "div":      (2, {"divide", "divided", "quotient", "over", "split",
                     "share", "each"}),
    # `meters` REMOVED entirely. It was metres-to-centimetres, which is one
    # cell of the dimensional table engine/units.py already computes, so two
    # mechanisms answered one question -- and they disagreed on "100 km/h to
    # meters per second" (250/9 vs 10000). Deduplicating is the fix; ordering
    # around it would only hide which one is right.
    "pct":      (2, {"percent", "percentage", "increase", "raise", "grow",
                     "bigger", "%"}),
    "linear":   (3, {"solve", "x", "equation", "unknown"}),
    "fracadd":  (4, {"fraction", "fractions", "simplified", "simplify"}),
    "compound": (4, {"evaluate", "expression"}),
}

MARGIN = 0.0   # winner must beat runner-up by this many trigger hits

# Phrasings that REVERSE operand order. "subtract 20 from 327" yields [20,327]
# in text order but means 327-20. Binding by position produced -307 on two
# questions -- confident, wrong, and the most dangerous failure class there is.
# "into" is NOT here. It inverts after `divide` ("divide 5 into 20" = 4) but
# not after `split` ("split 20 into 5 shares" = 4, the other binding). The
# preposition does not decide it, the verb does -- treating "into" as always
# inverting turned a correct 155 into 1/155.
INVERTING = re.compile(r'\b(?:from|away from|out of|off of)\b', re.I)
DIVIDE_INTO = re.compile(r'\bdivide[sd]?\b[^.]*?\binto\b', re.I)
INVERTIBLE = {"sub", "div"}

# Markers that put a question OUTSIDE a rule's form even when the operation
# word and the operand count both fit. "solve for y: 3y squared + 2 = 50"
# has three operands and says "solve", so keyword+arity routed it to the
# linear rule and answered 16 for a quadratic. The strict regex in route.py
# rejected it -- that pattern was doing verification, not just matching, and
# this is what replaces the check the natural-language layer discarded.
DISQUALIFY = {
    "linear": {"squared", "cubed", "power", "sqrt", "root", "quadratic",
               "^", "²", "³"},
    "add": {"squared", "cubed", "power", "sqrt", "root"},
    "sub": {"squared", "cubed", "power", "sqrt", "root"},
    "mul": {"squared", "cubed", "power", "sqrt", "root"},
    "div": {"squared", "cubed", "power", "sqrt", "root"},
}

# An operator SYMBOL names its operation as plainly as a word does.
SYMBOL = [("add", re.compile(r'\d\s*\+\s*-?\d')),
          ("sub", re.compile(r'\d\s*-\s*\d')),
          ("mul", re.compile(r'\d\s*[×*x]\s*-?\d')),
          ("div", re.compile(r'\d\s*[÷]\s*-?\d'))]

_NUM = re.compile(r'-?\d+')
_FRACPAIR = re.compile(r'(-?\d+)\s*/\s*(-?\d+)')


def operands(q: str):
    return [int(x) for x in _NUM.findall(q)]


def words(q: str):
    out = set(re.findall(r'[a-z%]+', q.lower()))
    out |= {c for c in q if c in "^²³"}
    return out


def symbol_ops(q: str):
    """operations named by an operator symbol between two operands"""
    return {name for name, pat in SYMBOL if pat.search(q)}


def route_nl(question: str) -> Result:
    """Human phrasing -> a rule that computes the answer."""
    qw = words(question)
    nums = operands(question)

    # structural pre-filter: a rule whose arity the question cannot supply
    # is excluded before any word is considered.
    viable = {name: trig for name, (ar, trig) in TRIGGERS.items()
              if ar == len(nums)}
    if not viable:
        return Result(UNCOVERED,
                      why=f"{len(nums)} operands match no rule's arity")

    # fraction addition is the only rule taking two a/b pairs
    if len(_FRACPAIR.findall(question)) == 2 and "fracadd" in viable:
        viable = {"fracadd": viable["fracadd"]}

    # a question carrying a marker outside the rule's form is not viable,
    # however well the operation word and operand count fit
    viable = {n: t for n, t in viable.items()
              if not (qw & DISQUALIFY.get(n, set()))}
    if not viable:
        return Result(UNCOVERED,
                      why="question is outside every matching rule's form")

    syms = symbol_ops(question)
    scored = sorted(((len(qw & trig) + (2 if name in syms else 0), name)
                     for name, trig in viable.items()), reverse=True)
    top, name = scored[0]
    if top == 0:
        return Result(UNCOVERED, why="no operation word recognised")
    runner = scored[1][0] if len(scored) > 1 else 0
    if top - runner <= MARGIN and len(scored) > 1 and runner == top:
        tied = sorted(n for s, n in scored if s == top)
        return Result(AMBIGUOUS, why=f"operation unclear between {tied}")

    rule = BY_NAME[name]
    if name in INVERTIBLE and (INVERTING.search(question)
                               or DIVIDE_INTO.search(question)):
        nums = [nums[1], nums[0]] + nums[2:]      # "X from Y" means Y - X
    try:
        produced = rule.answer(nums)
    except ZeroDivisionError:
        return Result(UNCOVERED, rule=name, subject=rule.subject,
                      why="division by zero: outside the rule's domain")
    if not rule.verify(nums, produced):
        return Result(CONTRADICTED, answer=produced, rule=name,
                      subject=rule.subject, args=nums,
                      why="the rule's check disagreed with its own compute")
    return Result(ANSWERED, answer=produced, rule=name, subject=rule.subject,
                  args=nums,
                  why=f"triggers {sorted(qw & viable[name])} -> '{name}', "
                      f"{len(nums)} operands, check agreed")


if __name__ == "__main__":
    for q in (sys.argv[1:] or [
            "what's 59 plus 78?",
            "add 59 and 78",
            "how much is 427 times 76",
            "what do i get if i divide 11470 by 74",
            "convert 602 meters to centimeters",
            "a quantity is 640, increase it by 20 percent",
            "solve for x: -9x + -6 = -348",
            "what is 10/19 + 9/4 as a simplified fraction",
            "who wrote Hamlet",
            "what is 5 and 7"]):
        r = route_nl(q)
        print(f'  "{q}"')
        print(f"     {r.verdict:<13} {r.answer if r.answer is not None else ''}")
        print(f"     {r.why}")
