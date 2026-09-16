"""
What a rule is, independent of domain.

    pattern   recognises a question and binds its parameters
    derive    produces the answer
    check     produces it AGAIN, by a different route
    kind      whether a check exists at all

Arithmetic was only the domain that happened to be in the corpus. The form is
about ANSWER GENERATION. What changes between domains is not the shape of the
rule, it is where the second derivation comes from:

  INVERSE      run the operation backwards.      137-78 == 59
  IDENTITY     round-trip returns the input.     reverse(reverse(s)) == s
  REDUNDANT    a second, unrelated algorithm.    Zeller vs date arithmetic
  ENUMERATE    check every case exhaustively.    syllogism over all models
  EXTERNAL     an outside validator rules on it. Godot parses the GDScript
  NONE         no derivation exists.             "Earth's radius is 6371 km"

The last one is the important one, and it is why the two predecessor projects
could not be merged naively. belt-atlas was entirely NONE: every answer was a
claim someone wrote down, checkable only against its source. atlas2 was
entirely derivable. A general answer generator needs both and must never
confuse them, because they fail differently:

    DERIVED   can be wrong only if the rule is wrong -- and the check catches
              that. Safe to generate at any volume.
    ASSERTED  can be wrong if the SOURCE is wrong, and nothing internal can
              tell. Never safe to generate; only to attribute.

Generating a million DERIVED answers costs nothing and risks nothing.
Generating one ASSERTED answer invents a fact.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

INVERSE, IDENTITY, REDUNDANT, ENUMERATE, EXTERNAL, NONE = (
    "INVERSE", "IDENTITY", "REDUNDANT", "ENUMERATE", "EXTERNAL", "NONE")

DERIVED = "DERIVED"                      # derived, and independently checked
DERIVED_UNCHECKED = "DERIVED_UNCHECKED"  # derived, no second derivation found
ASSERTED = "ASSERTED"                    # no derivation exists at all

# The middle kind was missing and it mattered. An INDUCED rule with no
# alternate expression is not an asserted fact -- a computation exists, it
# simply has no redundant confirmation. Collapsing it into ASSERTED would
# have banned generating from it, which is wrong: it derives, so every pair
# it makes is reproducible. It just cannot catch itself being wrong.


@dataclass
class Rule:
    name: str
    subject: str
    pattern: re.Pattern
    derive: Callable
    check: Callable | None = None
    check_kind: str = NONE
    source: str | None = None          # required when kind is ASSERTED
    fmt: Callable = str

    derivable: bool = True     # False only for facts with no computation

    @property
    def kind(self) -> str:
        if not self.derivable:
            return ASSERTED
        return DERIVED if self.check is not None else DERIVED_UNCHECKED

    def bind(self, q: str):
        m = self.pattern.search(q)
        if not m:
            return None
        return [g for g in m.groups()]

    def answer(self, args):
        return self.fmt(self.derive(*args))

    def verify(self, args, produced) -> bool | None:
        """True/False when checkable, None when the rule is ASSERTED."""
        if self.check is None:
            return None
        try:
            return self.fmt(self.check(*args)) == produced
        except Exception:
            return False

    def describe(self) -> str:
        if self.kind == ASSERTED:
            return f"{self.name}: ASSERTED, source={self.source}"
        if self.kind == DERIVED_UNCHECKED:
            return (f"{self.name}: DERIVED but UNCHECKED "
                    f"-- generating from it is safe, trusting it is not")
        return f"{self.name}: DERIVED, checked by {self.check_kind}"
