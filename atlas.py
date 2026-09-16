"""
atlas -- one entry point over every mechanism in this repo.

    from atlas import ask
    ask("what day of the week is 2026-09-15")
    ask("convert 100 km/h to meters per second")
    ask("Evaluate: ((3 + 4) × 5) - 6")
    ask("whats 59 plus 78")
    ask("what is the calibration constant for unit zq0007", index=idx)

THE CASCADE, and why it is in this order.

  1 DATES      before arithmetic, because "2026-09-15" is a valid subtraction
               to a parser that only knows numbers. The more specific reader
               must be asked first or the general one silently eats its input.
  2 UNITS      before arithmetic, for the same reason: "100 km/h" contains a
               division sign and "5 m + 3 m" contains a plus.
  3 RULES      exact pattern match on named families.
  4 ARITHMETIC compositional and unbounded, and EXACT.
  5 NL RULES   the same rules via human phrasing -- keywords plus operand
               count, which is loose evidence, so it goes last.

The ordering rule is not "specific before general", it is ORDER BY HOW
PRECISELY A LAYER DETERMINES THAT IT OWNS THE QUESTION. Both orderings were
measured and both failed differently:

  general arithmetic first   it evaluated a span inside "Solve for x: -9x +
                             -6 = -348" and returned -348. 875/5737 wrong.
  all rules first            the NL layer matched "(3 + (4 × 5)) - 6" on four
                             operands and the word `evaluate`, applied the
                             compound shape and answered 29 instead of 17.
                             101/422 novel forms wrong.

Exact mechanisms -- named patterns, parsing -- rank above heuristic ones
whatever their generality.
  6 GROUNDED   extraction from supplied context, span-verified. Last because
               a derived answer beats an extracted one whenever both exist:
               derivation checks itself, extraction only checks faithfulness.
  7 ABSTAIN    with every layer's reason, so a refusal is diagnosable.

TERMINAL REFUSALS. A layer has two ways to decline and they are not the same.
"Not my question" continues the cascade. "Your question is malformed" stops
it, because a vaguer layer must not overturn a determination a more specific
one already made. Conflating them answered "convert 5 meters to kilograms"
with 500: the units layer refused it on dimension mismatch, and the
natural-language rule layer then matched on the words `convert` and `meters`
and applied metres-to-centimetres.

Ordering is the whole content of an integration. Each layer is asked only
after every more-specific layer has declined.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from engine import dates as _dates                              # noqa: E402
from engine import units as _units                              # noqa: E402
from engine import parse as _parse                              # noqa: E402
from engine import route as _route                              # noqa: E402
from engine import nl as _nl                                    # noqa: E402
from engine import experts as _experts
from engine import games as _games
from engine import grounded as _grounded                        # noqa: E402
from engine.explain import explain as _explain                  # noqa: E402

ANSWERED, ABSTAINED, CONTRADICTED = "ANSWERED", "ABSTAINED", "CONTRADICTED"


@dataclass
class Answer:
    verdict: str
    value: object = None
    mechanism: str | None = None
    check: str | None = None
    provenance: str | None = None
    cost_tokens: int = 0
    trace: list = field(default_factory=list)

    def __bool__(self):
        return self.verdict == ANSWERED

    def __str__(self):
        if self.verdict != ANSWERED:
            return f"[{self.verdict}] " + "; ".join(self.trace[-3:])
        return (f"{self.value}   ({self.mechanism}, checked by {self.check}"
                + (f", {self.provenance}" if self.provenance else "") + ")")


def _fmt(v):
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    return str(v)


def ask(question: str, context: str | None = None, index=None) -> Answer:
    trace = []

    # 1 -- dates
    v, why = _dates.solve(question)
    if v is not None:
        return Answer(ANSWERED, v, "date algebra", "INVERSE + REDUNDANT",
                      why, trace=trace)
    if _dates.terminal(why):
        return Answer(ABSTAINED, None, "date algebra", None, why, trace=trace + [
            f"dates REFUSED (terminal): {why}"])
    trace.append(f"dates: {why}")

    # 2 -- units
    v, why = _units.convert(question)
    if v is not None:
        return Answer(ANSWERED, _fmt(v), "dimensional algebra",
                      "INVERSE + REDUNDANT", why, trace=trace)
    if _units.terminal(why):
        return Answer(ABSTAINED, None, "dimensional algebra", None, why,
                      trace=trace + [f"units REFUSED (terminal): {why}"])
    trace.append(f"units: {why}")

    # 3 -- strict rule match (specific beats general)
    r = _route.route(question)
    if r.verdict == _route.ANSWERED:
        return Answer(ANSWERED, r.answer, f"rule '{r.rule}'", "rule check",
                      r.why, trace=trace)
    if r.verdict == _route.CONTRADICTED:
        return Answer(CONTRADICTED, r.answer, f"rule '{r.rule}'", None,
                      r.why, trace=trace)
    trace.append(f"rules: {r.why}")

    # 3b -- named experts (dna, periodic table, materials, seeded worlds)
    st, val, exp, chk, prov = _experts.route_expert(question)
    if st == _experts.ANSWERED:
        return Answer(ANSWERED, val, f"expert '{exp}'", chk, prov, trace=trace)
    if st == _experts.REFUSED:
        return Answer(ABSTAINED, None, f"expert '{exp}'", None, prov,
                      trace=trace + [f"expert REFUSED (terminal): {prov}"])
    trace.append(f"experts: {prov}")

    # 3c -- game construction, when asked to build one
    if re.search(r'\b(make|build|generate|create)\b.{0,40}\bgame\b',
                 question, re.I):
        g = _games.make(question)
        if not g["ok"]:
            return Answer(ABSTAINED, None, "game builder", None,
                          "generated game failed its own checks", trace=trace)
        note = ("" if g["matches_request"] else
                "  [RUNS BUT DOES NOT MATCH THE REQUEST: " +
                "; ".join(f"{k} {w}" for k, w, _ in g["understood"]["unmet"]) + "]")
        return Answer(ANSWERED, g["source"], "game builder",
                      "PARSE+ROUNDTRIP+RUN+INVARIANTS+DETERMINISM",
                      f"{g['understood']['picks_from_text']} decisions from the "
                      f"description, {g['lines_out']} lines{note}", trace=trace)

    # 4 -- compositional arithmetic: EXACT, so it outranks heuristics
    v, why = _parse.recognise(question)
    if v is not None:
        return Answer(ANSWERED, _fmt(v), "compositional parse", "REDUNDANT",
                      f"span {why!r}", trace=trace)
    if _parse.terminal(why):
        return Answer(ABSTAINED, None, "compositional parse", None, why,
                      trace=trace + [f"arithmetic REFUSED (terminal): {why}"])
    trace.append(f"arithmetic: {why}")

    # 5 -- rules via natural phrasing: loose evidence, so last
    r = _nl.route_nl(question)
    if r.verdict == _route.ANSWERED:
        return Answer(ANSWERED, r.answer, f"rule '{r.rule}' (nl)",
                      "rule check", r.why, trace=trace)
    if r.verdict == _route.CONTRADICTED:
        return Answer(CONTRADICTED, r.answer, f"rule '{r.rule}' (nl)", None,
                      r.why, trace=trace)
    trace.append(f"nl: {r.why}")

    # 6 -- grounded extraction, only if a source was supplied
    if index is not None and context is None:
        hits = index.retrieve(question, k=3)
        context = " ".join(h["text"] for h in hits) if hits else None
        if context is None:
            trace.append("grounded: nothing retrieved")
    if context:
        g = _grounded.extract(question, context)
        cost = _grounded.approx_tokens(context)
        if g.verdict == _grounded.ANSWERED:
            return Answer(ANSWERED, g.answer, "grounded extraction",
                          "SPAN-IN-SOURCE", f"offset {g.offset}", cost, trace)
        if g.verdict == _grounded.INVENTED:
            return Answer(CONTRADICTED, g.answer, "grounded extraction",
                          "SPAN-IN-SOURCE", g.why, cost, trace)
        trace.append(f"grounded: {g.why}")

    return Answer(ABSTAINED, None, None, None, None, 0, trace)


def why(question, context=None, index=None) -> str:
    a = ask(question, context, index)
    out = [f'  "{question}"', f"  verdict    {a.verdict}"]
    if a.value is not None:
        out.append(f"  answer     {a.value}")
    if a.mechanism:
        out.append(f"  mechanism  {a.mechanism}")
    if a.check:
        out.append(f"  check      {a.check}")
    if a.provenance:
        out.append(f"  provenance {a.provenance}")
    if a.cost_tokens:
        out.append(f"  cost       {a.cost_tokens} context tokens")
    if a.verdict != ANSWERED:
        for t in a.trace:
            out.append(f"     tried  {t}")
    return "\n".join(out)
