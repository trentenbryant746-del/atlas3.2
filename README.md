# Atlas 3

**A question-answering system where every answer carries the check that
would catch it being wrong, and anything that cannot be checked is
refused rather than guessed.**

It runs in 14 MiB of memory, answers in 25 microseconds, imports in 16
milliseconds, uses the Python standard library and nothing else, and has
produced **zero wrong answers** across 5,902 evaluated prompts.

It also declines to answer twelve out of twelve ordinary
general-knowledge questions. Both of those facts are the same design
decision, and this README is mostly about why.

```python
from atlas import ask, why

ask("what day of the week is 2026-09-15")      # date algebra
ask("convert 100 km/h to meters per second")   # dimensional algebra
ask("Evaluate: ((3 + 4) × 5) - 6")             # compositional parse
ask("What element has atomic number 79?")      # expert, table round-trip
ask("which experts route chemistry")           # the Qwen expert map
ask("how many isotopes of element 130")        # the ladder over it
why("why is a quarter of the universe helium") # the whole derivation
```

---

## Summary

Atlas 3 is the third version of a system built on one idea: **answers
split by how they can fail, and that decides everything else.**

A `DERIVED` answer is reproducible from a rule, and a second independent
derivation checks it — so you can generate a million of them and risk
nothing. An `ASSERTED` answer is a claim about the world that nothing
internal can verify, so generating a new one does not produce an answer,
it **invents a fact**. Atlas refuses to do that.

Everything else follows. The system has four independent type systems
that refuse nonsense structurally, before any computation runs. It has a
cascade of layers ordered by how precisely each determines that it owns
a question, and every layer can decline. When it declines, it reports
the reason from every layer it tried, and — where it can — turns the
abstention into a **request** naming exactly what it would need.

Atlas 3 adds three things to Atlas 2: a map of all 10,240 experts inside
a 35-billion-parameter language model, addressed and checked without
ever opening the model's weights; the rungs above chemistry, from
nucleotide to organism, each gated by when its constituents can first
exist in the universe; and typed composition, which lets modules answer
questions together that none of them can answer alone.

---

## The numbers

Measured on this machine, not estimated.

| | |
|---|---|
| **Wrong answers, 5,737-record curriculum** | **0** |
| **Wrong answers, 165 held-out prompts** | **0** |
| Held-out prompts verified by recomputation | 165 / 165 |
| …of those, verified by a route sharing no code with the engine | 132 |
| Audited headline claims, each re-derived | 21 / 21 |
| Module self-checks | 62 |
| Cold import | **16 ms** |
| Per query | **25 µs** (40,271/sec, one core) |
| Peak memory | **14 MiB** |
| Dependencies | **0** — Python 3 standard library |
| Code | 68 files, 11,186 lines |
| Qwen experts mapped and checked | 10,240 |
| Routing events bound as compounds | 146,640 / 146,640 |
| Expert slice lengths re-derived from first principles | 30,720 / 30,720 |
| Packed-tensor boundaries with no gap or overlap | 30,600 |
| Addressable corpus | 1e9 tokens, 100 segments × 10M |

---

## Atlas 2 versus Atlas 3

Atlas 3 **contains Atlas 2 entire**. Every rule, every check, every
measurement is intact and still runs — 21/21 audited claims, 5,737/5,737
curriculum, all six original evals. Nothing was replaced. The table below
is what was *added*.

| | Atlas 2 | Atlas 3 |
|---|---|---|
| Answers | computed, each with an independent check | same, unchanged |
| Type systems | dimensional, conservation, causal, addressing | same, plus typed cross-module composition |
| Ladder | particle → atom → compound → mixture | …→ **nucleotide → codon → gene → genome → cell → organism** |
| Stellar death | a remnant **mass** | remnant **kind** + every element thrown off, per element, mass-conserved |
| Chandrasekhar limit | — | **derived** from ħ, c, G, mₕ: 1.435 M☉ vs accepted 1.4 |
| Nuclear equation of state | — | bounded by observation to 2.08–2.3 M☉, **refused inside it** |
| Other universes | — | constants as parameters; exponents re-measured, not asserted |
| Language models | — | 10,240 experts mapped, addressed, and checked |
| Corpus | 10M tokens, chunked | **1e9 tokens**, 100 segments, overlapping continuous grid |
| Open problems | — | a fixture that must come back **refused** |
| Held-out benchmark | 165 answered | 165 **verified**, 132 independently |
| Cross-module answers | written by hand | **found by search** over type signatures |

### What Atlas 2 could already do

**The derived/asserted split.** `eval/controls.py` sabotages every
derived rule and all of them catch it; the one asserted rule correctly
reports itself as *unverifiable* rather than quietly passing.

**Four type systems, each refusing a space the others cannot touch.**
Measured over every element-pair × epoch binding: dimensions refuse 0 of
1,680 (both are masses), conservation refuses 0 (both are neutral),
**epoch refuses 1,263**. Causality is not a refinement of the other two.

**Rule induction.** Nine curriculum rules induced from six examples each,
5,683/5,683 held-out. Eight operations absent from the corpus, 200/200
each. Two induced rules came out *better* than the hand-written ones.

**Compositional parsing over three algebras** — arithmetic, units, dates
— so unseen forms need no examples: 2,807/2,807 novel arithmetic forms,
266 distinct unit pairs where the corpus had one, date chains nobody
enumerated.

**Grounded extraction** with three verdicts: answered with a verbatim
span and its offset, ungrounded, or `INVENTED` — an answer that is *not*
in the source. That third verdict paid for itself immediately: it caught
25 fact sentences cut by a chunk boundary that a system without it would
have reported as 100% correct.

**Four executable backends** — Python, Ruby, GDScript, and a register
machine — compiled from one IR and required to produce byte-identical
traces, with negative controls that are caught.

### What Atlas 3 adds

**The Qwen expert map.** All 10,240 experts of a 35B-parameter
mixture-of-experts model, addressed as `(time, expert)` — the layer *is*
the time coordinate, because a token's context is built up layer by
layer. Expert 147 at layer 3 and expert 147 at layer 31 are different
experts, and time is what separates them.

The map is checked without opening a single weight: a Q4_K superblock is
144 bytes per 256 weights, Q5_K is 176, Q6_K is 210, so every slice
length follows from its shape and quantization. **All 30,720 reproduce**,
and within each of the 120 packed tensors the 256 slices abut exactly —
no gap, no overlap, across 30,600 boundaries.

**A ladder over the experts.** Element is an expert id, isotope is that
element at one time, compound is the eight bound together at one time,
material is forty compounds. The binding number is read from the model's
own header, not chosen: all 146,640 routing events bind, cardinality 8
throughout, and a compound may bind only isotopes of its own time —
routing at layer 3 cannot reach an expert of layer 31, because that
expert has not been computed yet.

**Life above chemistry.** Phosphorus decides it: every nucleotide carries
a phosphate, phosphorus is Z=15, and the nucleosynthesis bands put it in
the supernova era — so DNA, and every organism built from it, cannot
predate supernovae. That falls out of the periodic table rather than
being asserted. Two routes reach it independently and agree.

The codon length is *derived*: four bases must name 21 things, 4² = 16 is
too few, 4³ = 64 is enough, so three is forced and the 43 spare codons
are why the real code must be redundant. And with the genetic code table
present, the "20 amino acids and 1 stop" that derivation takes as
arguments are **counted out of the table** instead of assumed, fed back,
and still give 3.

**Stellar remnants, as physics rather than lookup.** One rule at every
mass: a star builds a degenerate core, and what holds that core up
decides what it becomes. Electrons below the Chandrasekhar mass, neutrons
above it, nothing known above the TOV limit. A one-solar-mass star leaves
a white dwarf because its core never reaches M_Ch — not because of
anything about which stars happen to be in a simulation.

**Where physics does not know, Atlas refuses — and bounds.** The nuclear
equation of state is an open problem. Atlas cannot derive it, so it
refuses, but it narrows the band **from data**: a 2.08 M☉ pulsar that
exists refutes every softer equation of state, and GW170817's collapsed
remnant caps it near 2.3. The band goes from 0.70 wide to 0.22 — 69%
narrower — and inside it the answer stays *undetermined*, with the
refusal naming what would settle it.

**Other universes.** The Chandrasekhar mass is a function of ħ, c, G and
composition, so it moves with them. Exponents re-measured rather than
asserted: ħ +1.5, c +1.5, G −1.5, μₑ −2.0. A 5 M☉ remnant is a black hole
in our universe and a white dwarf in one with an eighth our gravity. Same
rule, different universe.

**Typed composition.** 16 capabilities across 8 modules, and chains are
**found by search, not written**:

```
nucleotide=dAMP   → seconds_after_bang = 9.5e+16
genome_bp=4600000 → surface_to_volume  = 2.84e+07   (three modules)
progenitor=25 M☉  → remnant_kind       = black_hole
subject=chemistry → total_bytes        = 9,502,720
```

Nobody wrote those. They exist because the type signatures line up, and
adding one capability adds every chain it completes. Where no path
exists, it abstains with a reason.

**A register of what nobody knows.** Ten open problems — Riemann, P vs
NP, Collatz, Goldbach, Navier–Stokes, the nuclear EOS, quantum gravity,
dark matter, baryon asymmetry, the Kleiber exponent — held as a fixture
where **the expected result is abstention**. An answer there is a bug far
more often than a discovery.

It found one on its first run. *"Does the Kleiber 3/4 exponent follow from
anything?"* came back **3/4** — the compositional parser had grabbed the
substring. The fix wasn't a hand-written blocklist: removing the
arithmetic span from all 5,902 prompts that must keep answering leaves
exactly twenty framing words, and anything outside that means the
sentence is about something else.

---

## Compared to a frontier model

This is not a claim that Atlas beats a large language model at answering
questions. It does not, and the honest numbers cut both ways.

**Where a frontier model wins, decisively:** coverage. Ask Atlas twelve
ordinary general-knowledge questions — the capital of France, who wrote
Hamlet, why the Roman Empire fell — and it answers **zero of twelve**. A
frontier model answers all twelve, and mostly correctly. Atlas has no
opinion about anything it cannot derive or ground in a supplied source.

**Where the difference is extreme, on the axes Atlas optimises:**

| | Atlas 3 | Qwen3.6-35B-A3B (the model mapped here) |
|---|---|---|
| Artifact size | 120 MiB | 20.6 GiB — **175× larger** |
| Working memory | **14 MiB** | ~21 GB to load — **1,500× more** |
| Accelerator | none | GPU or a large-memory machine |
| Latency | **25 µs** | seconds; prefill is 7.2 s + 0.491 s/token |
| Determinism | byte-identical, always | sampled |
| Wrong answers on its own evals | **0 of 5,902** | not characterisable this way |
| Says "I don't know" | with the reason from every layer | rarely, and not reliably |
| Can you check an answer? | **yes — it ships the check** | no |
| Dependencies | **0** | a deep stack |

The prefill law makes the corpus point concrete. Putting 10 million
tokens in a context window costs **56.8 days** on the reference machine.
Atlas addresses 1e9 tokens as 100 segments and reads ~956 tokens per
query — about 477 s — because chunking here is not an optimisation, it is
the difference between answerable and not.

**The real distinction is the failure mode.** A language model's wrong
answer looks exactly like its right answer. That is not a flaw in any
particular model; it is what a probability distribution over tokens
produces. Atlas's failure mode is an abstention that names which layer
declined and why. The system is built so that the *only* thing it can do
badly is decline too often.

So the comparison is not better or worse. It is: **if you need an answer
you can audit, and you would rather have nothing than something plausible
and wrong, the numbers above are the trade.**

And a genuine, measured result on the model itself: Atlas maps all 10,240
of its experts — identity, address, timing, co-activation, byte ranges —
in **120 MiB with the weights deleted**, verified by re-deriving 30,720
slice lengths and 30,600 tensor boundaries. Every check still passes with
the 21 GB file made unreadable.

---

## It runs on any computer

There is no GPU, no accelerator, no network call, no model to download,
no package to install, and no build step.

```bash
git clone <this repo> && cd atlas3
python3 tools/get_qwen.py     # assemble + verify the expert data
python3 eval/benchmark.py     # everything, in one command
```

**Python 3 and nothing else.** No torch, no numpy, no tensorflow, no
sklearn. The whole tree imports only the standard library, and that is
enforced rather than claimed — there is no neural network anywhere in it,
no gradients, no embeddings, no matrix multiply.

At **14 MiB peak** it fits in the memory of a Raspberry Pi Zero with room
to spare, and at 25 µs per query one core serves 40,000 questions a
second. A decade-old laptop runs the full benchmark. The bottleneck on
any modern machine is reading the file from disk.

Two optional runtimes each *add* a verification path and degrade
gracefully if absent:

- **ruby** — a second executable backend for cross-verification
- **godot** — a third backend, plus the scene round-trip

Without them, GDScript is emitted and reported as *unverified* rather
than counted as passing, and every other check still runs. Godot is
pinned by version and SHA-512 (`tools/get_godot.py`); the 21 GB language
model is pinned by SHA-256 and **not carried**, because nothing here
opens it.

---

## What Atlas 3 does not do

Stated plainly, because a system that reports its limits is the whole
point.

- **It answers almost nothing by general knowledge.** 0 of 12 ordinary
  questions. Facts must be derivable, or supplied in context where it can
  verify the answer is a verbatim span.
- **It does not learn.** Rule induction derives a *computation* from
  examples; which spans are operands and which questions a rule is about
  are still written by a person.
- **Faithfulness is verifiable; truth is a citation.** Atlas can prove an
  answer appears verbatim in its source. Whether the source is right is
  outside anything here.
- **Five things it asserts and does not derive** are listed in
  `engine/unsolved.py` with what would close each: the Kleiber exponent,
  the Lane-Emden constant, the fitted dilution factor, the initial-final
  mass relation, and the held-out answer format.
- **The cosmological dilution factor was fitted**, so that agreement is a
  fit and not a prediction, and the README says so where it is quoted.

---

## Running it

```bash
python3 eval/benchmark.py        # everything: 21 claims, corpora, modules
python3 eval/audit.py            # the 21 headline claims, re-derived
python3 eval/heldout.py          # the 165, recomputed independently
python3 eval/integration.py      # every corpus + cross-layer disagreement
python3 eval/controls.py         # sabotage every check
python3 engine/unsolved.py       # the open problems; all must refuse
python3 engine/bridge.py         # typed chains across modules
python3 engine/biomatter.py      # the life ladder
python3 engine/qwenmatter.py     # the expert ladder
python3 ui/server.py             # then open http://localhost:8765
```

## Layout

```
atlas.py            one entry point; the cascade and its ordering
rules/              rule tables: pattern + compute + independent check
engine/             80 modules — see VERSIONS.md for what each version added
  parse units dates       three algebras, compositional
  route nl keys grammar3  recognition, and declining to recognise
  particles nucleo epochs cosmos   physics from constants
  life biomatter          the rungs above chemistry
  remnants eos            stellar death, and where physics does not know
  qwenmap qwenmatter      10,240 experts, addressed and laddered
  bridge                  typed composition across modules
  unsolved                what nobody knows, as a fixture
  ir codeindex visualize  four backends, and a scene that reads back
eval/               the gates; benchmark.py runs all of them
data/qwen/          the expert map, pinned in MANIFEST.json
tools/              get_qwen.py, get_godot.py — pin, fetch, verify, refuse
VERSIONS.md         Atlas 1, 2 and 3: what each was and what forced the next
README-log.md       the development narrative, including every failure
```

`README-log.md` holds the measurement-by-measurement history, including
the results that were wrong and what corrected them. It is longer than
this file and more useful if you want to know whether to believe any of
it.
