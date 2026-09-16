"""
One narrator for every derivation, with re-execution as the fidelity check.

explain.py narrated arithmetic expression trees and checked itself by
replaying the narrated steps. Everything else in the repo -- primordial
helium, stellar enrichment, the iron peak, rule induction -- produced
numbers and no account of how they were reached.

The generalisation is a DERIVATION RECORD: an ordered list of steps, each
carrying what was done, on what, why it follows, and how to recompute it.
Then one narrator turns any record into English, and fidelity is checked
the same way explain.py checks itself -- by re-running the narrated steps
and comparing to the stated result.

An explanation that cannot be re-executed is prose. This repo does not
ship prose as evidence.

Each step also declares its own kind, so a chain can be MIXED -- most real
derivations are -- and the narration says exactly which links are computed
and which are quoted:

    DERIVED   follows from the step before it
    ASSERTED  a measured constant or a sourced fact, with a citation
    DEFINED   true by definition or convention
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

DERIVED, ASSERTED, DEFINED = "DERIVED", "ASSERTED", "DEFINED"


@dataclass
class Step:
    what: str                      # plain-English action
    value: object                  # the result of this step
    because: str = ""              # why it follows
    kind: str = DERIVED
    source: str = ""               # required when ASSERTED
    recompute: Callable | None = None   # () -> value, for the fidelity check
    unit: str = ""

    def check(self, tol=1e-9):
        if self.recompute is None:
            return None
        got = self.recompute()
        if isinstance(got, float) and isinstance(self.value, float):
            return abs(got - self.value) <= max(tol, abs(self.value) * 1e-9)
        return got == self.value


@dataclass
class Derivation:
    question: str
    steps: list = field(default_factory=list)
    result: object = None
    compared_to: object = None
    comparison: str = ""

    def add(self, *a, **k):
        self.steps.append(Step(*a, **k))
        return self.steps[-1]

    def verify(self):
        """re-run every step that can be re-run"""
        out = []
        for s in self.steps:
            out.append((s.what, s.check()))
        checked = [o for o in out if o[1] is not None]
        return all(ok for _n, ok in checked), out

    def narrate(self, width=74):
        L = [self.question, ""]
        for i, s in enumerate(self.steps, 1):
            val = s.value
            if isinstance(val, float):
                val = f"{val:.6g}"
            tag = {DERIVED: "", ASSERTED: "  [measured]",
                   DEFINED: "  [by definition]"}[s.kind]
            L.append(f"{i}. {s.what}")
            L.append(f"   = {val}{' ' + s.unit if s.unit else ''}{tag}")
            if s.because:
                L.append(f"   because {s.because}")
            if s.kind == ASSERTED and s.source:
                L.append(f"   source: {s.source}")
        L.append("")
        res = self.result
        if isinstance(res, float):
            res = f"{res:.6g}"
        L.append(f"Answer: {res}")
        if self.compared_to is not None:
            L.append(f"Observed: {self.compared_to}   ({self.comparison})")
        ok, detail = self.verify()
        n = sum(1 for _x, c in detail if c is not None)
        L.append("")
        L.append(f"Every step re-executed: {sum(1 for _x, c in detail if c)}"
                 f"/{n} reproduce their stated value."
                 if n else "No step is independently re-executable.")
        if not ok:
            for nm, c in detail:
                if c is False:
                    L.append(f"  UNFAITHFUL: {nm}")
        return "\n".join(L)


def kinds(deriv):
    """how much of a chain is computed and how much is quoted"""
    d = {}
    for s in deriv.steps:
        d[s.kind] = d.get(s.kind, 0) + 1
    return d
