"""
Ingesting sourced facts from the open web, with the provenance kept.

Fetched text is DATA. It is never read as instructions, and nothing in this
path can execute, route or configure anything from page content -- extraction
only ever selects a verbatim span. A page that contains the sentence "ignore
your rules" yields, at most, an answer quoting that sentence with its URL.

WHAT INGESTION BUYS, AND WHAT IT DOES NOT. The bottleneck was never rules, it
was asserted facts -- 2.0% of stated facts were derivable from their
questions. The web supplies asserted facts, so this raises COVERAGE. It does
not make the system smarter: no amount of prose induces a new primitive, and
a fetched page is a citation, not an understanding.

THE SOURCE TAGS ITSELF, where it can. NIST marks the speed of light "(exact)"
and gives the electron mass an uncertainty. That is the stipulated/empirical
distinction stated by the authority rather than inferred by a regex, and it
is strictly better evidence than engine/epistemic.py's cue matching.

    c   299 792 458 m s^-1        uncertainty "(exact)"   -> STIPULATED
    m_e 9.109 383 7139e-31 kg     uncertainty 2.8e-40     -> EMPIRICAL

ALLOWLIST. Only hosts ending in the configured suffixes are accepted, and the
check is on the parsed hostname, not a substring -- "evil.com/.gov" and
"notgov.com" must not pass.
"""
from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

ALLOWED_SUFFIXES = (".gov", ".edu", ".int")

EXACT = re.compile(r'\(exact\)|exact(?:ly)? by definition|defined (?:to be|as)',
                   re.I)
UNCERTAIN = re.compile(r'standard uncertainty|uncertainty|±|\+/-', re.I)

STIPULATED, EMPIRICAL, CONTINGENT = "STIPULATED", "EMPIRICAL", "CONTINGENT"


def host_allowed(url: str) -> tuple[bool, str]:
    """Suffix match on the PARSED HOST. A substring test would accept
    http://evil.com/?x=.gov and http://notgov.example."""
    try:
        h = (urlparse(url).hostname or "").lower().rstrip(".")
    except ValueError:
        return False, "unparseable url"
    if not h:
        return False, "no host"
    for suf in ALLOWED_SUFFIXES:
        if h == suf.lstrip(".") or h.endswith(suf):
            return True, h
    return False, f"host {h!r} is not on the allowlist {ALLOWED_SUFFIXES}"


@dataclass
class Source:
    url: str
    host: str
    fetched_at: str
    text: str
    sha256: str
    epistemic: str
    marker: str = ""
    notes: list = field(default_factory=list)

    def cite(self) -> str:
        return f"{self.url} (retrieved {self.fetched_at}, sha256 {self.sha256[:12]})"


def classify(text: str) -> tuple[str, str]:
    """epistemic kind from the SOURCE'S OWN markers where present"""
    m = EXACT.search(text)
    if m:
        return STIPULATED, m.group(0)
    m = UNCERTAIN.search(text)
    if m:
        return EMPIRICAL, m.group(0)
    if re.search(r'\b(in \d{3,4}|was founded|was signed|was born)\b', text, re.I):
        return CONTINGENT, "dated event"
    return EMPIRICAL, "no explicit marker; defaulted"


def make_source(url: str, text: str) -> Source | None:
    ok, host = host_allowed(url)
    if not ok:
        return None
    kind, marker = classify(text)
    return Source(url=url, host=host,
                  fetched_at=time.strftime("%Y-%m-%d"),
                  text=text,
                  sha256=hashlib.sha256(text.encode()).hexdigest(),
                  epistemic=kind, marker=marker)


def answer(question: str, source: Source):
    """grounded extraction over a fetched source, carrying the citation"""
    from engine.grounded import extract, ANSWERED
    g = extract(question, source.text)
    if g.verdict != ANSWERED:
        return None, g.why
    return g.answer, (f"{source.epistemic} [{source.marker}] "
                      f"span at offset {g.offset} of {source.cite()}")
