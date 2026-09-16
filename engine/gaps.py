"""
When the system cannot answer, say exactly what it would need.

"Give it the fundamental rules of how the world works and it can build up to
history, law and medicine" contains one true half and one false half, and
they separate cleanly:

  THE REASONING IN THOSE DOMAINS IS DERIVABLE.
    Is a filing within a limitation period? -- date algebra.
    What is the dose at 45 mg/kg for 18 kg, divided twice daily? -- arithmetic.
    How many years between two events? -- date algebra.

  THE FACTS ARE NOT, AND NO FUNDAMENTAL RULE ENTAILS THEM.
    The limitation period is three years because a legislature wrote three.
    Westphalia is 1648 because it happened in 1648.
    The dose is 45 mg/kg because trials found that, not because physics says so.

Law is STIPULATED, history is CONTINGENT, medicine is EMPIRICAL. Physics does
not entail any of them. Measured on belt-atlas's 350 stated facts, 2.0% had
an answer derivable from anything in the question; for the arithmetic corpus
that figure is 100%.

So the useful move is not to derive the facts. It is to SPLIT the question,
compute the derivable part, and name the asserted part precisely enough that
a source -- or a person -- can supply it. That is what this does: the
abstention becomes a request.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# things whose value must come from outside, with the reason it must
ASSERTED_MARKERS = [
    (re.compile(r'\b(treaty|war|revolution|battle|founded|signed|born|died)\b', re.I),
     "a historical date", "contingent: it happened when it happened"),
    (re.compile(r'\b(statute of limitations|deadline|filing period|notice period)\b', re.I),
     "a statutory period", "stipulated: whatever the legislature enacted"),
    (re.compile(r'\b(dose|dosage|mg/kg|contraindicat|half-life)\b', re.I),
     "a clinical parameter", "empirical: established by trial, not derivation"),
    (re.compile(r'\b(capital|population|currency|border)\b', re.I),
     "a geographic or civic fact", "contingent: set by people and subject to change"),
]


def unknown_terms(question):
    """proper nouns and quoted names -- candidates for things to be supplied"""
    caps = re.findall(r'\b([A-Z][a-z]{2,}(?:\s+(?:of|the|de)\s+)?(?:[A-Z][a-z]+)*)',
                      question)
    stop = {"What", "How", "When", "Which", "Where", "Who", "Is", "If", "The"}
    return [c.strip() for c in caps if c.split()[0] not in stop]


def analyse(question, ask_fn):
    """-> dict describing what is derivable and what must be supplied"""
    a = ask_fn(question)
    if a:
        return {"status": "answered", "answer": a.value,
                "mechanism": a.mechanism}

    needs = []
    for pat, what, why in ASSERTED_MARKERS:
        if pat.search(question):
            needs.append({"kind": what, "because": why})
    terms = unknown_terms(question)

    # would the question become derivable if the asserted parts were given?
    derivable_if = []
    if re.search(r'\b(how (many|long)|between|after|before|duration|years?|days?)\b',
                 question, re.I):
        derivable_if.append("date algebra, once the dates are supplied")
    if re.search(r'\b(per|each|total|times|divided|rate|mg/kg|dose)\b', question, re.I):
        derivable_if.append("arithmetic, once the rate and quantity are supplied")
    if re.search(r'\b(convert|in (grams|kg|ml|litres|liters|mg))\b', question, re.I):
        derivable_if.append("dimensional algebra, once the units are supplied")

    return {"status": "needs_input", "needs": needs, "terms": terms,
            "derivable_if": derivable_if,
            "request": _request(needs, terms, derivable_if)}


def _request(needs, terms, derivable_if):
    if not needs and not terms:
        return "no expert covers this and nothing identifiable is missing"
    bits = []
    if terms:
        bits.append("supply values for: " + ", ".join(dict.fromkeys(terms)[:4]
                    if isinstance(terms, dict) else list(dict.fromkeys(terms))[:4]))
    for n in needs:
        bits.append(f"{n['kind']} ({n['because']})")
    tail = ("; then " + " and ".join(derivable_if)) if derivable_if else ""
    return "; ".join(bits) + tail
