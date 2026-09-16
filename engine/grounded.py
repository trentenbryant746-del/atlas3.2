"""
GROUNDED: turn an asserted fact into a checkable extraction.

An asserted fact is not a function of the question, which is why nothing
internal could verify it and why retrieval capped belt-atlas at 70%. Put the
SOURCE IN CONTEXT and that changes: the answer becomes a function of
(question, context), and the function is extraction.

What becomes checkable is FAITHFULNESS, not truth. The rule cannot tell you
Earth's radius is really 6371 km -- only a source can. It can tell you the
answer is a verbatim span of the supplied text, and exactly where. That is
the check that catches invention, which is the failure mode that matters when
generating.

    ANSWERED     the answer is a verbatim span, offset recorded
    UNGROUNDED   nothing in the context answers it -- decline
    INVENTED     an answer was produced that is NOT in the context.
                 The one verdict a retrieval system cannot produce about
                 itself, and the reason this is worth the tokens.

The cost is prefill, and it is not free. belt-atlas measured it on the target
hardware: TTFT = 7.2s + 0.491s x prompt_tokens (R^2 = 0.9975). Grounding is
a token bill, so `budget()` prices it rather than waving at it.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

ANSWERED, UNGROUNDED, INVENTED = "ANSWERED", "UNGROUNDED", "INVENTED"

# measured on belt-atlas hardware, not assumed
TTFT_BASE = 7.2
TTFT_PER_TOKEN = 0.491


@dataclass
class Grounded:
    verdict: str
    answer: str | None = None
    offset: int | None = None
    source: str | None = None
    why: str = ""


def approx_tokens(s: str) -> int:
    return max(1, len(s) // 4)


def budget(context: str) -> dict:
    n = approx_tokens(context)
    return {"tokens": n,
            "prefill_seconds": round(TTFT_BASE + TTFT_PER_TOKEN * n, 1)}


def _norm(s):
    return re.sub(r'\s+', ' ', s.strip().lower())


def answer_from(question: str, context: str, candidate: str) -> Grounded:
    """Verify a proposed answer is a verbatim span of the context."""
    if not candidate or not candidate.strip():
        return Grounded(UNGROUNDED, why="no candidate answer")
    hay, needle = _norm(context), _norm(candidate)
    i = hay.find(needle)
    if i < 0:
        return Grounded(INVENTED, answer=candidate,
                        why="answer does not occur in the supplied context")
    return Grounded(ANSWERED, answer=candidate, offset=i, source=context[:60],
                    why=f"verbatim span at offset {i} of {len(context)} chars")


def extract(question: str, context: str) -> Grounded:
    """Deterministic extraction: the sentence of the context that shares the
    most content words with the question. No model, no scoring beyond overlap.
    """
    qw = set(re.findall(r'[a-z0-9]+', question.lower())) - {
        "what", "is", "the", "how", "a", "an", "of", "are", "do", "does"}
    if not qw:
        return Grounded(UNGROUNDED, why="question has no content words")
    # A question asking for a QUANTITY wants the sentence with the quantity
    # in it. Scoring on content-word overlap alone answered "what is the
    # numerical value of the speed of light" with the title sentence "Speed
    # of light in vacuum." -- a verbatim span, faithful, and not the answer.
    wants_number = bool(re.search(
        r'\b(value|how many|how much|how far|how long|how old|how deep|'
        r'how tall|how fast|mass|length|number|uncertainty|rate)\b',
        question, re.I))
    best, score = None, 0.0
    for sent in re.split(r'(?<=[.!?])\s+', context):
        sw = set(re.findall(r'[a-z0-9]+', sent.lower()))
        ov = float(len(qw & sw))
        if ov == 0:
            continue
        if wants_number and re.search(r'\d', sent):
            ov += 1.5
        if ov > score:
            best, score = sent.strip(), ov
    if not best or score == 0:
        return Grounded(UNGROUNDED,
                        why="no sentence in context shares a content word")
    return answer_from(question, context, best)
