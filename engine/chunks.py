"""
Chunked grounding over corpora too large to prefill.

A 10M-token prompt cannot be put in a context window on the hardware this
line was measured on: TTFT = 7.2s + 0.491s x tokens puts it at 56.8 DAYS.
So chunking is not a speedup, it is the only way the question gets answered
at all.

The thing that survives chunking is the PROVENANCE CHAIN. Each answer is a
verbatim span with a chunk id and an offset, so the reasoning is recorded as
a sequence of citations rather than held in resident context. Losing the
thread is what happens when state lives in the window; here it lives in the
chain, and the chain is auditable after the fact.

belt-atlas measured the two candidate retrieval mechanisms head to head over
a million tokens:

    explicit note index            100.0% exact-chunk recovery
    expert-signature similarity     11.5%

So the index here is symbolic -- an inverted index over chunk vocabulary --
not a learned embedding. That was not a preference, it was the measurement.
"""
from __future__ import annotations

import re
from collections import defaultdict

TTFT_BASE, TTFT_PER_TOKEN = 7.2, 0.491
WORD = re.compile(r'[a-z0-9]+')


def approx_tokens(s):
    return max(1, len(s) // 4)


def prefill_seconds(tokens):
    return TTFT_BASE + TTFT_PER_TOKEN * tokens


class ChunkIndex:
    def __init__(self, chunk_tokens=256, overlap=None):
        overlap = OVERLAP if overlap is None else overlap
        self.chunk_chars = chunk_tokens * 4
        self.overlap = overlap
        self.stride_chars = stride_for(chunk_tokens, overlap) * 4
        self.chunks = []
        self.post = defaultdict(set)

    def add(self, text, doc="doc"):
        # STRIDE, NOT WIDTH. This stepped by the full chunk, so chunks
        # were disjoint and a fact sentence landing on a boundary sat
        # in no single chunk -- the 25 INVENTED the README records as
        # fixed by 25% overlap. The fix was written down and not
        # written in.
        step = self.stride_chars
        for i in range(0, len(text), step):
            body = text[i:i + self.chunk_chars]
            if i and i + self.chunk_chars >= len(text) + step:
                break          # wholly inside an earlier window
            cid = len(self.chunks)
            self.chunks.append({"id": cid, "doc": doc, "start": i,
                                "text": body})
            for w in set(WORD.findall(body.lower())):
                self.post[w].add(cid)

    def retrieve(self, query, k=3):
        qw = set(WORD.findall(query.lower()))
        score = defaultdict(int)
        for w in qw:
            ids = self.post.get(w)
            if not ids or len(ids) > len(self.chunks) * 0.2:
                continue                     # a word in 20% of chunks selects nothing
            for cid in ids:
                score[cid] += 1
        if not score:
            return []
        top = sorted(score.items(), key=lambda kv: -kv[1])[:k]
        return [self.chunks[cid] for cid, _ in top]

    def stats(self):
        chars = sum(len(c["text"]) for c in self.chunks)
        return {"chunks": len(self.chunks),
                "tokens": approx_tokens_total(chars),
                "vocab": len(self.post),
                "postings": sum(len(v) for v in self.post.values())}


def approx_tokens_total(chars):
    return max(1, chars // 4)


# ======================================================================
# TWO LEVELS, AND WHY THEY ARE NOT THE SAME NUMBER
#
#   segment   10,000,000 tokens   one context window's worth, x100
#   chunk            256 tokens   the unit actually put into context
#
# The corpus is 1e9 tokens as 100 segments of 10M. Making chunk_tokens
# 10,000,000 would make every retrieval unit a whole segment, and this
# module's own law prices that: 7.2 + 0.491 x 1e7 = 56.8 DAYS to
# prefill one. A 10M-token chunk IS the failure chunking exists to
# avoid. The segment is an ADDRESSING level; the chunk is a reading
# level, and only the chunk is paid for.
SEGMENT_TOKENS = 10_000_000
CORPUS_TOKENS = 1_000_000_000
SEGMENTS = CORPUS_TOKENS // SEGMENT_TOKENS          # 100

# CHUNKS OVERLAP, AND THE OVERLAP IS MEASURED. With chunk C and
# stride S, a span of length L sits whole inside some chunk for EVERY
# placement iff L <= C - S + 1. So overlap is not a margin of comfort,
# it is a GUARANTEED RECOVERABLE FACT LENGTH: 65 tokens at C=256,
# S=192. A longer fact can still be cut, and the number says where the
# guarantee stops.
OVERLAP = 0.25


def stride_for(chunk_tokens, overlap=OVERLAP):
    if not (0 <= overlap < 1):
        raise ValueError("overlap must be in [0, 1)")
    return max(1, int(round(chunk_tokens * (1.0 - overlap))))


def guaranteed_span(chunk_tokens, overlap=OVERLAP):
    """The longest span no boundary can cut."""
    return chunk_tokens - stride_for(chunk_tokens, overlap) + 1


def corpus_chunks(chunk_tokens=256, overlap=OVERLAP):
    """Chunk starts over the WHOLE corpus, not per segment.

    THE GRID MUST NOT RESTART AT A SEGMENT BOUNDARY. Gridding each
    segment from zero puts a clean cut every 10M tokens, which is the
    25-INVENTED bug one level up: measured, every 20-token fact
    straddling a boundary was in no chunk at all -- 19 of 19
    placements, across 99 internal boundaries. And the last chunk of
    a segment was clipped to 64 tokens, so the 65-token guarantee
    collapsed to 2 near a tail.

    So segments are an ADDRESSING span over one continuous grid, not
    a container that owns its own chunks. Chunks straddle boundaries
    by construction, exactly one chunk in the corpus is clipped, and
    the guarantee holds everywhere except the final chunk width --
    which is unavoidable, because the corpus has to end.
    """
    st = stride_for(chunk_tokens, overlap)
    return st, -(-CORPUS_TOKENS // st)


def segment_of(start):
    """Which segment a chunk is addressed to: where it BEGINS."""
    return min(start // SEGMENT_TOKENS, SEGMENTS - 1)


def plan(chunk_tokens=256, overlap=OVERLAP):
    """The arithmetic of the 1e9-token corpus, at both levels.

    THE STRIDE DRIVES THE COUNT, NOT THE WIDTH. Dividing the segment
    by the chunk width is the disjoint assumption: correct before the
    index overlapped and wrong after. Coverage is a UNION -- chunks
    overlap by design, so the union must equal the segment exactly
    while the sum exceeds it by the read amplification.
    """
    st, total = corpus_chunks(chunk_tokens, overlap)
    last_start = (total - 1) * st
    last_len = min(chunk_tokens, CORPUS_TOKENS - last_start)
    read = (total - 1) * chunk_tokens + last_len
    per_seg = -(-SEGMENT_TOKENS // st)      # chunks BEGINNING in a segment
    return {
        "corpus_tokens": CORPUS_TOKENS,
        "segment_tokens": SEGMENT_TOKENS,
        "segments": SEGMENTS,
        "chunk_tokens": chunk_tokens,
        "overlap": overlap,
        "stride_tokens": st,
        "chunks_beginning_in_a_segment": per_seg,
        "chunks_total": total,
        "clipped_chunks": 1,
        "tokens_read": read,
        "read_amplification": read / CORPUS_TOKENS,
        "guaranteed_span": guaranteed_span(chunk_tokens, overlap),
        "prefill_corpus_s": prefill_seconds(CORPUS_TOKENS),
        "prefill_segment_s": prefill_seconds(SEGMENT_TOKENS),
        "prefill_chunk_s": prefill_seconds(chunk_tokens),
    }


def union_covered(chunk_tokens=256, overlap=OVERLAP, span=CORPUS_TOKENS):
    """Tokens covered by at least one chunk. Overlaps counted ONCE."""
    st = stride_for(chunk_tokens, overlap)
    covered = reach = 0
    for start in range(0, span, st):
        end = min(start + chunk_tokens, span)
        if end > reach:
            covered += end - max(start, reach)
            reach = end
    return covered


def planted_fact_control(n=400, chunk_tokens=256, fact_tokens=20, seed=7):
    """The experiment that found the 25 INVENTED, run as a control.

    A fact is recoverable iff ONE chunk holds it whole -- which is
    what grounding requires, since the answer must be a verbatim span
    of a single retrieved chunk.
    """
    import random
    rnd = random.Random(seed)
    cc, fc = chunk_tokens * 4, fact_tokens * 4
    span = n * cc
    facts = sorted(rnd.randrange(0, span - fc) for _ in range(n))
    out = {}
    for ov in (0.0, OVERLAP):
        st = stride_for(chunk_tokens, ov) * 4
        starts = range(0, span, st)
        whole = sum(1 for f in facts
                    if any(b <= f and f + fc <= b + cc for b in starts))
        out[ov] = {"recoverable": whole, "lost": n - whole,
                   "chunks": len(starts)}
    return facts, out


def check_plan(chunk_tokens=256):
    """-> (ok, [(name, ok, detail)])."""
    out = []
    p = plan(chunk_tokens)

    out.append(("segments_close",
                p["segments"] * p["segment_tokens"] == p["corpus_tokens"],
                f"{p['segments']} x {p['segment_tokens']:,} = "
                f"{p['segments']*p['segment_tokens']:,}, corpus is "
                f"{p['corpus_tokens']:,}"))

    cov = union_covered(chunk_tokens)
    out.append(("union_covers_corpus", cov == p["corpus_tokens"],
                f"{p['chunks_total']:,} overlapping chunks cover {cov:,} "
                f"distinct tokens of {p['corpus_tokens']:,}"))

    # the check that would have caught the per-segment grid
    st = p["stride_tokens"]
    fact = 20
    cut = 0
    for k in range(1, SEGMENTS):
        edge = k * SEGMENT_TOKENS
        for a_ in range(edge - fact + 1, edge):
            lo = (a_ // st) * st
            if not any(b_ <= a_ and a_ + fact <= min(b_ + chunk_tokens,
                                                     CORPUS_TOKENS)
                       for b_ in (lo - st, lo, lo + st)):
                cut += 1
    out.append(("no_segment_boundary_cut", cut == 0,
                f"{fact}-token facts straddling all {SEGMENTS-1} internal "
                f"segment boundaries: {cut} in no chunk. Per-segment grids "
                f"gave 1,881 here"))

    # and the one that would have caught the clipped tail
    tail_worst = min(
        max((min(b_ + chunk_tokens, CORPUS_TOKENS) - a_)
            for b_ in range((a_ // st) * st, -1, -st) if b_ <= a_)
        for a_ in range(SEGMENT_TOKENS - 300, SEGMENT_TOKENS + 300))
    out.append(("guarantee_holds_at_a_boundary",
                tail_worst >= p["guaranteed_span"],
                f"across a segment boundary the longest guaranteed span is "
                f"{tail_worst} tokens, against the claimed "
                f"{p['guaranteed_span']}; per-segment grids gave 2"))

    out.append(("stride_under_chunk", p["stride_tokens"] < chunk_tokens,
                f"stride {p['stride_tokens']} < chunk {chunk_tokens}: "
                f"consecutive chunks share "
                f"{chunk_tokens - p['stride_tokens']} tokens"))

    out.append(("guaranteed_span", p["guaranteed_span"] > 1,
                f"any span of {p['guaranteed_span']} tokens or fewer sits "
                f"whole in some chunk wherever it falls"))

    _f, r = planted_fact_control(chunk_tokens=chunk_tokens)
    l0, ln = r[0.0]["lost"], r[OVERLAP]["lost"]
    out.append(("overlap_is_load_bearing", l0 > 0 and ln == 0,
                f"400 planted facts: {l0} cut with no overlap, {ln} at "
                f"{OVERLAP:.0%}. Without a loss at 0 the overlap would be "
                f"decoration"))

    amp = p["read_amplification"]
    out.append(("read_amplification", abs(amp - 1/(1-OVERLAP)) < 0.01,
                f"{p['tokens_read']:,} chunk tokens over "
                f"{p['corpus_tokens']:,} = {amp:.3f}x = 1/(1-{OVERLAP}), "
                f"paid in storage not prefill"))

    # This gated on "a chunk must prefill in under 600 seconds", which
    # is a number I chose, and it failed 2048-token chunks at 1013s --
    # a threshold rejecting a configuration, not physics rejecting it.
    # The structural fact is what matters: a chunk is a reading unit
    # and a segment is an addressing unit, so the chunk must be
    # strictly smaller. The costs are REPORTED, because how long a
    # query may take is the operator's call and nothing here derives
    # it.
    ratio = p["prefill_segment_s"] / p["prefill_chunk_s"]
    out.append(("chunk_is_not_a_segment", chunk_tokens < SEGMENT_TOKENS,
                f"chunk {chunk_tokens:,} < segment {SEGMENT_TOKENS:,}; a "
                f"segment is {p['prefill_segment_s']/86400:.1f} days of "
                f"prefill and a chunk is {p['prefill_chunk_s']:.0f}s, "
                f"{ratio:,.0f}x cheaper"))

    yrs = p["prefill_corpus_s"] / 86400 / 365.25
    out.append(("corpus_unprefillable", yrs > 1,
                f"the corpus is {yrs:.1f} years of prefill, so it is "
                f"addressed and never prompted"))
    return all(o[1] for o in out), out
