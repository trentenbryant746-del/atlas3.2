# The three Atlases

Each version is a whole system, not a patch on the one before. This
records what each was, what it could do, and the measurement that
made the next one necessary.

---

## Atlas 1 — belt-atlas

A retrieval system over a hand-built net of stated facts.

    answers      stored strings
    verifier     none
    routing      two-stage, IDF-aware
    abstention   a confidence margin
    ceiling      70% on hand-written questions

**What it established.** Flat IDF inverts topic salience: the more
facts about a topic, the less that topic's own name identifies it.
`earth`, in 62 rows, scored the floor. Accuracy FELL as the net grew
from 171 to 350 rows — structural, not tuning.

**What killed it.** Everything in it was ASSERTED, so nothing could
be checked, and the margin that bought precision on derived queries
*declined* on real ones — 79% at one threshold, 50% at another. A
confidently wrong answer stays confident. There was no mechanism
that could ever have caught it.

**The trap it left behind, and it is the most valuable thing it
produced:** derived evaluations do not predict real questions, and
across three scorer variants they disagreed *in sign*. Optimising a
big cheap eval can move the real number the wrong way.

---

## Atlas 2

A question-answering system where every answer carries the check
that would catch it being wrong, and anything uncheckable is
refused.

    answers      computed
    verifier     an independent second derivation, per rule
    routing      a cascade ordered by precision of ownership
    abstention   verdicts with the reason from every layer tried
    measured     5,737/5,737 curriculum, 165/165 held-out, 21/21 audit

**The one idea.** Answers split by how they can fail, and that
decides everything:

| kind | wrong if | generation |
|---|---|---|
| `DERIVED` | the rule is wrong, and the check catches it | unlimited |
| `DERIVED_UNCHECKED` | same, but nothing catches it | safe, flagged |
| `ASSERTED` | the source is wrong, and nothing internal can tell | **refused** |

Generating a million derived answers risks nothing. Generating one
asserted answer invents a fact.

**Four type systems**, each refusing a space the others cannot
touch — dimensional, conservation, causal (epoch), addressing. Over
every element-pair × epoch binding: dimensions refuse 0 of 1680,
conservation 0, **epoch 1263**.

**What it could not do.** It stopped where chemistry stopped. No
life, no remnants, no model of its own reasoning, and a corpus
bounded by what one context could hold.

---

## Atlas 3

Atlas 2 entire — every rule, every check, every measurement intact —
plus the Qwen expert map and everything that composes with it.

    Atlas 2's numbers, unchanged   21/21, 5737/5737, 165/165, 6/6 evals
    experts mapped                 10,240, layer as the time coordinate
    module checks                  62 across 10 new modules
    held-out                       165 VERIFIED, 132 independently
    corpus                         1e9 tokens, 100 segments of 10M

### What is new

**`qwenmap`** — 10,240 Qwen experts addressed as `(time, expert)`,
the layer being the time coordinate because a token's context is
built up layer by layer. Checked by re-deriving all 30,720 slice
lengths from shape and quantization, and by the 256 slices of each
packed tensor tiling with no gap across 30,600 boundaries.

**`qwenmatter`** — the ladder over them. Element is an expert id,
isotope is that element at one time, compound is the eight bound at
one time, material is forty compounds. The binding number is read
from the GGUF header, not chosen: all 146,640 routing events bind.

**`remnants`, `eos`** — what a star leaves and throws off. The
Chandrasekhar mass derived from ħ, c, G and mₕ at 1.435 M☉ against
an accepted 1.4. Where the nuclear equation of state is unknown the
rule refuses, and `eos` narrows the band from 2.2–2.9 to 2.08–2.3
using observed pulsars and GW170817 — 69% narrower, and from data.

**`life`, `biomatter`** — the rungs above chemistry, each gated by
when its constituents exist. Phosphorus decides it: DNA cannot
predate supernovae, and that falls out of the periodic table.

**`bridge`** — `bind.py` one level up. 16 typed capabilities across
8 modules, chains found by search rather than written.

**`unsolved`** — open problems as a fixture that must come back
refused. It found a real bug on its first run.

**`chunks`** — 1e9 tokens as 100 segments of 10M, with overlapping
chunks on one continuous grid.

### What Atlas 3 still does not do

No neural network anywhere: stdlib only, no torch, no gradients, no
embeddings, no matmul, and the 21 GB GGUF is never opened. The
expert map is offsets, not weights.

Five things this repo asserts and does not derive are listed in
`engine/unsolved.py` with what would close each: the Kleiber
exponent, the Lane-Emden constant, the fitted dilution factor, the
initial-final mass relation, and the held-out answer format.
