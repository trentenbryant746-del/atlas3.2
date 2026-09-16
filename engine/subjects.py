"""
Subject keys backed by a fetched source.

`history:` was not a registered expert, so the key layer abstained and listed
what it knew -- correct, and also the whole gap. A subject expert is not code;
it is a KEY plus a SOURCE plus a citation. Registering one means putting a
retrieved document behind the key and answering only from it.

    history: when was the constitutional convention called
      -> a verbatim span of archives.gov, with url, date and epistemic tag

The epistemic tag is CONTINGENT and that is not decoration. Nothing derives
1787. The system is not reasoning about history; it is quoting a source about
history and saying which source. Those are different claims and only one of
them is true here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SRC = ROOT / "data" / "sources"


def registry():
    out = {}
    for meta in sorted(SRC.glob("*.meta.json")):
        m = json.loads(meta.read_text())
        body = meta.with_name(meta.name.replace(".meta.json", ".txt"))
        if body.exists():
            out.setdefault(m["key"], []).append({**m, "text": body.read_text()})
    return out


def ask_subject(key, question):
    """-> (answer, citation) or (None, reason). Only from registered sources."""
    from engine.grounded import extract, ANSWERED
    reg = registry()
    if key not in reg:
        return None, (f"no source registered for {key!r}; "
                      f"registered subjects: {sorted(reg)}")
    best = None
    for s in reg[key]:
        g = extract(question, s["text"])
        if g.verdict == ANSWERED:
            best = (g, s)
            break
    if not best:
        return None, (f"{key!r} has {sum(len(v) for v in reg.values())} "
                      f"source(s) and none of them answers this")
    g, s = best
    return g.answer, (f"{s['epistemic']} -- {s['why']}\n"
                      f"    source: {s['url']} (retrieved {s['retrieved']}), "
                      f"span at offset {g.offset}")
