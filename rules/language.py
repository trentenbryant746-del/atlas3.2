"""
Rules that take or produce English, rather than only digits.

Atlas abstained on "spell the number 1247 in words" and on "what number is
one thousand two hundred forty-seven". Neither is a fact to look up and
neither needed a knowledge base -- both are compositions, and both carry a
real check, so refusing them was a gap in the LANGUAGE layer and not a
principled refusal.

WHY THERE IS A SECOND RULE CLASS HERE. rules/arith.py's Rule coerces every
captured group with int(), which is right for everything it holds and makes
an English operand impossible to express. TextRule is the same interface
with that one coercion removed. It is not a parallel hierarchy -- route.py
calls match/answer/verify and neither class knows about the other.

Both rules below are IDENTITY in rules/kinds.py's sense: the answer is
produced one way and confirmed by converting it back the other way, which
is a different algorithm rather than the same one restated.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rules.arith import Rule, fmt                                # noqa: E402
from engine.numwords import read, say                            # noqa: E402


@dataclass
class TextRule:
    """rules/arith.py's Rule without the int() on every group.

    `guard` exists because binding is part of recognition. "what number is
    eleventy seven" matches the pattern and is not a numeral, and the first
    version let that through to compute(), where read() raised ValueError
    straight out of route() and took the whole cascade down -- worse than
    either answering or refusing. A group that will not parse means this
    rule does not OWN the question, so match() returns None and the
    cascade carries on to the next layer.
    """
    name: str
    subject: str
    pattern: re.Pattern
    compute: Callable
    check: Callable | None = None
    guard: Callable | None = None

    def match(self, q: str):
        m = self.pattern.search(q)
        if not m:
            return None
        args = list(m.groups())
        if self.guard is not None and not self.guard(*args):
            return None
        return args

    def answer(self, args):
        return fmt(self.compute(*args))

    def verify(self, args, produced: str) -> bool:
        if self.check is None:
            return True
        try:
            return fmt(self.check(*args)) == produced
        except Exception:
            return False


def _spell(n: int) -> str:
    return say(n)


def _spell_check(n: int):
    """IDENTITY: the words are right only if they read back as the number."""
    words = say(n)
    return words if read(words) == int(n) else None


def _reads(words: str) -> bool:
    """Whether this text is a numeral at all -- asked before binding."""
    try:
        read(words)
        return True
    except Exception:
        return False


def _read(words: str) -> int:
    return read(words)


def _read_check(words: str):
    """IDENTITY, the other way about: re-spelling must reproduce the words."""
    n = read(words)
    return n if read(say(n)) == n else None


RULES = [
    # the optional prefix keeps this ONE rule: two patterns for "spell 12 in
    # words" and "12 in words" would both match the longer phrasing, and
    # route.py returns AMBIGUOUS when two rules match rather than guessing
    Rule("spell", "language.numeral",
         re.compile(r'(?:(?:spell|write|say)(?:\s+(?:out|the\s+number))?\s+)?'
                    r'(-?\d+)\s+in\s+words', re.I),
         _spell, check=_spell_check),
    TextRule("readnum", "language.numeral",
             re.compile(r'(?:what\s+number\s+is|read|parse)\s+'
                        r'((?:negative\s+|minus\s+)?[a-z]+(?:[\s-]+(?:and\s+)?'
                        r'[a-z]+)*)', re.I),
             _read, check=_read_check, guard=_reads),
]
