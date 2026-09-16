"""
A verified index of generated code, addressable by provenance token.

Every emitted line carries `atlas:<id>`, and the id resolves to the IR node,
the operation, and the English that caused it -- in any backend. So the index
reads both ways: from a line of generated Ruby back to the intent, and from
an intent forward to every line in every language that implements it.

It is not unlimited. It is combinatorially large and, more usefully, every
entry is CROSS-VERIFIED: compiled to python and ruby, both run, traces
identical. An index of unverified code is a pile of text, which is the thing
the 640,000 proxy records already demonstrated.
"""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.ir import N, BACKENDS, cross_verify, index   # noqa: E402

STEPS = [(i, m, f"move {i} per tick, wrapping at {m}")
         for i in (1, 2, 3, 5, 7) for m in (4, 5, 7, 9, 11)]
GATES = [("> 3", "record only past the midpoint"),
         ("< 2", "record only near the start"),
         ("== 0", "record only on a wrap"),
         ("> 0", "record every non-zero position"),
         ("!= 1", "record everything except one")]
RUNS = [(8, "a short run"), (20, "a longer run"), (33, "a long run")]


def programs():
    for (inc, mod, sd), (cmp_, gd), (ticks, rd) in itertools.product(
            STEPS, GATES, RUNS):
        yield [
            N("let", "x", 0, origin="start at the origin"),
            N("loop", ticks,
              [N("add", "x", inc, mod, origin=sd),
               N("when", "x", cmp_, [N("emit", "x", origin=gd)], origin=gd)],
              origin=rd),
        ]


def build(limit=None, verify=True, novel_only=False):
    """novel_only keeps a program ONLY if its trace is new.

    Behavioural uniqueness is the thing worth growing. Counting programs
    overstates an index -- the first sweep produced 24 programs and 18
    distinct behaviours, so a quarter of it was the same game in different
    clothes. Growing on novelty makes the count mean something.
    """
    entries, tokens, failed = [], {}, []
    seen_traces = set()
    for i, prog in enumerate(programs()):
        if limit and i >= limit:
            break
        if verify:
            ok, srcs, traces, notes = cross_verify(prog)
        else:
            ok, srcs, traces = True, {n: b.emit(prog) for n, b in BACKENDS.items()}, {}
        if not ok:
            failed.append((i, notes))
            continue
        tr = traces.get("python", "")
        if novel_only:
            if tr in seen_traces:
                continue
            seen_traces.add(tr)
        idx = index(prog)
        tokens.update(idx)
        entries.append({"id": i, "tokens": sorted(idx),
                        "trace": traces.get("python", ""),
                        "langs": sorted(srcs),
                        "lines": {k: v.count(chr(10)) for k, v in srcs.items()}})
    return entries, tokens, failed


def lookup(token, tokens):
    return tokens.get(token)


DEFAULT_LIMIT = 40          # a 375-program sweep took 2.4 minutes by default


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                    help=f"programs to verify (default {DEFAULT_LIMIT}); "
                         f"0 means the whole sweep")
    ap.add_argument("--novel-only", action="store_true",
                    help="keep only behaviourally distinct programs")
    a = ap.parse_args()
    total = sum(1 for _ in programs())
    lim = a.limit or None
    if lim:
        print(f"verifying {lim} of {total} candidate programs "
              f"(--limit 0 for all)\n")
    entries, tokens, failed = build(limit=lim, novel_only=a.novel_only)
    print(f"generated  {len(entries)} programs, each cross-verified")
    print(f"failed     {len(failed)}")
    print(f"tokens     {len(tokens)} distinct provenance ids")
    print(f"languages  {sorted(BACKENDS)}")
    distinct = len({e['trace'] for e in entries})
    print(f"behaviours {distinct} distinct traces "
          f"({distinct}/{len(entries)} programs are behaviourally unique)")
    print()
    print("reading a token back to intent:")
    t = entries[0]["tokens"][0]
    for tok in entries[3]["tokens"][:3]:
        d = lookup(tok, tokens)
        print(f"  atlas:{tok}  {d['op']:<6} {str(d['args'])[:26]:<28} {d['origin']}")
    out = ROOT / "data" / "code-index.json"
    out.write_text(json.dumps(
        {"entries": entries,
         "tokens": {k: {"op": v["op"], "origin": v["origin"]}
                    for k, v in tokens.items()}}, indent=1))
    print(f"\nwrote {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
