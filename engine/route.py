"""
Route a question to a rule, or decline it.

Verdicts, kept distinct because collapsing them is what made belt-atlas
undiagnosable: best_row() returned None both for "no coverage" and for
"too much coverage", and the harness scored them identically.

    ANSWERED     exactly one rule matched, and its independent check agreed
    AMBIGUOUS    several rules matched -- the question is underspecified
    UNCOVERED    no rule matched -- outside the system's competence
    CONTRADICTED a rule matched but its check disagreed with its own compute

CONTRADICTED is the one that matters most and the one neither source project
had. It cannot be produced by a lookup table: only a rule that derives an
answer two ways can catch itself being wrong.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rules.arith import RULES                                   # noqa: E402

ANSWERED = "ANSWERED"
AMBIGUOUS = "AMBIGUOUS"
UNCOVERED = "UNCOVERED"
CONTRADICTED = "CONTRADICTED"


@dataclass
class Result:
    verdict: str
    answer: str | None = None
    rule: str | None = None
    subject: str | None = None
    args: list | None = None
    why: str = ""

    def __bool__(self):
        return self.verdict == ANSWERED


def route(question: str) -> Result:
    hits = []
    for r in RULES:
        args = r.match(question)
        if args is not None:
            hits.append((r, args))

    if not hits:
        return Result(UNCOVERED, why="no rule pattern matches this question")

    if len(hits) > 1:
        names = sorted(r.name for r, _ in hits)
        return Result(AMBIGUOUS, rule=None,
                      why=f"{len(names)} rules match: {names}")

    rule, args = hits[0]
    try:
        produced = rule.answer(args)
    except ZeroDivisionError:
        return Result(UNCOVERED, rule=rule.name, subject=rule.subject,
                      why="division by zero: outside the rule's domain")

    if not rule.verify(args, produced):
        return Result(CONTRADICTED, answer=produced, rule=rule.name,
                      subject=rule.subject, args=args,
                      why="the rule's independent check disagreed with itself")

    return Result(ANSWERED, answer=produced, rule=rule.name,
                  subject=rule.subject, args=args,
                  why=f"rule '{rule.name}' on {args}, check agreed")


def explain(question: str) -> str:
    r = route(question)
    lines = [f'  "{question}"', f"  verdict {r.verdict}"]
    if r.rule:
        lines.append(f"  rule    {r.rule}  ({r.subject})")
    if r.answer is not None:
        lines.append(f"  answer  {r.answer}")
    lines.append(f"  why     {r.why}")
    return "\n".join(lines)


if __name__ == "__main__":
    qs = sys.argv[1:] or [
        "Calculate 59 + 78. Show a brief check.",
        "Evaluate: (100 + 27) × -9 - 96. Show a brief check.",
        "Calculate 10/19 + 9/4. Give the simplified fraction and a brief check.",
        "Calculate 5 ÷ 0. Show a brief check.",
        "What is the capital of France?",
        "Integrate x^2 dx.",
    ]
    for q in qs:
        print(explain(q)); print()
