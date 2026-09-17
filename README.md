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

## Two rules that govern everything below

**1. A claim is only as good as its worst input.**

Every number in this repository is one of three things, and the kind
decides what may be said about any result depending on it:

    EXACT      fixed by definition. No error, ever.
    MEASURED   someone went and found out. Carries their error.
    CHOSEN     nobody measured it and nothing derives it. It was
               picked so a model would run.

A CHOSEN number is not forbidden — a model that refuses every
unmeasured quantity does nothing at all. **Citing a result that rests
on one as though it were derived is forbidden.** `engine/inputs.py`
classifies all 33 and grades every registered claim by its weakest
input. Currently **18 are CHOSEN**, and the results resting on them say
so wherever they appear. The planet results — habitable band, Earth's
composition, the biosignature — rest on nothing chosen. Several biology
results do.

**2. There is no prediction here. There are rules and their
consequences.**

Nothing is scored, fitted to an answer, or estimated with a confidence.
Where a number is compared against reality it is a *consequence being
checked*, not a guess being graded. `engine/folding.py` refuses to
predict a protein structure and says AlphaFold does that with 93
million learned parameters. `engine/newatom.py` uses a flexible fit
**only as a diagnostic** for whether a law exists at all, never as an
answer — *"an atom that does not make anything findable is not an atom,
it is a parameter."*

The chain is recorded rather than asserted. `engine/provenance.py`
hash-links an atom from a universe seed through the epoch that made it
and every decay since, and `engine/planetlab.py` carries it up to a
folding residue:

    seed          universe hash d59bc58bc3456775c6831abc...
    stellar_c     formed: alpha-chain, Z=6 even and below the peak
    stellar_c     decay: C -> N by beta-minus, Q=0.16 MeV
    abundance     C is 2.36e-03 of baryonic mass
    valence       C bonds 4 ways, from shell filling
    residue       G is C2H5NO2 -- 2 atoms of C in it
    fold          G scores 0.667 on carbon-to-polar

Nothing in it is computed for the occasion. That is what makes it a
root rather than a story.

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

### Every 3.1 release, and what each one added

Each row is a commit in this repository and a section further down. The
pattern is worth reading as a whole: roughly a third of these releases
**overturn an earlier one**, and those are the load-bearing entries.

| ver | what changed | what it cost or exposed |
|---|---|---|
| 3.1.1 | Lane-Emden constant derived | one assertion off the list |
| 3.1.2 | dilution factor over-constrained | it broke, and named the yield |
| 3.1.3 | nine elements | **overturned 3.1.2** |
| 3.1.4 | all 83 naturally occurring elements | the r-process broke |
| 3.1.5 | channel derived, "family" dropped | laws separated from resemblance |
| 3.1.6 | audit of what was still handwritten | derived two, refused a third |
| 3.1.7 | proteins | limits of what benchmark hashes give up |
| 3.1.8 | atoms breaking/binding as transitions | a keyed commitment |
| 3.1.9 | universes chunked | density stopped being bounded by a list |
| 3.1.10 | folding by exhaustive enumeration | Levinthal is about *when* you are |
| 3.1.11 | atom provenance | benchmark answer format recovered |
| 3.1.12 | measured half-lives, 165/165 byte-exact | three wrong chain walks |
| 3.1.13 | biochemistry as a parameter | Earth returns as a special case |
| 3.1.14 | error bar asserted, and says so | valence derived, 10 → 50 elements |
| 3.1.15 | error bar **measured** | withdrew the uranium series |
| 3.1.16 | the bar depends on the question | **the withdrawal withdrawn** |
| 3.1.17 | beta decay, a missing term | 3 of 14 confidently wrong |
| 3.1.18 | a bar belongs to a domain | folding's bar is a *rate*, not an energy |
| 3.1.19 | a planet that terraforms itself | no agent; faint young Sun resolved |
| 3.1.20 | — | **withdrew the Mercury result** |
| 3.1.21 | optical depth from molecules | no planet consulted; Earth −15.4 K |
| 3.1.22 | the lab: controlled experiments | HOLDS / MISSING_RULE / CLASH / REFUSED |
| 3.1.23 | four missing rules and one clash | Earth −3.2 K; Venus openly wrong |
| 3.1.24 | never patch: one home per constant | four quantities had 2–3 definitions |
| 3.1.25 | stress-test every rule | a silent fallback substituting a bar |

Four rows are retractions: 3.1.3, 3.1.15, 3.1.16 and 3.1.20. Three of
those retract something *this repository itself* had published, and 3.1.16
retracts a retraction. That is the intended failure mode.

## What Atlas is not

Stated before the numbers, because the numbers invite a reading that
would be false.

**Atlas does not run the language model, and cannot.** There is no
inference here of any kind:

- It produces **no logits and no tokens**. There is no forward pass.
- **No weights are stored, regenerated or distilled.** What
  `expert-tensor-map.json` holds is `expert_slice_offset` — a byte
  position inside the GGUF — and a length. Pointers, not values. Grep
  the tree: no module so much as mentions `ffn_gate_exps` except to
  record where it sits.
- There is **no routed-expert computation**, because there is nothing
  to compute with. The map says *which* experts fired on recorded
  prompts and *where* their weights live; it cannot evaluate them.
- The **25 µs** figure is Atlas answering its own rule-based questions.
  It is not model inference and is not comparable to one.
- The **1e9-token corpus is addressed, never attended.** Chunks are
  retrieved by a symbolic inverted index and grounded by verbatim span.
  No attention is computed over it. That is the whole point — putting
  10M tokens in a context window costs 56.8 days by this repo's own
  measured prefill law.

**So the 175× is not model compression.** It is the ratio of (map +
rules) to (model file), and the map cannot reconstruct the model.
Delete the 21 GB GGUF and you can no longer run Qwen at all; what you
keep answers questions *about* its routing, not questions it would
answer.

The honest description is the weaker one: **Atlas indexes and ladders a
model it never executes.** If you want the stronger claim — a compact
executable implementation with routed expert computation and outputs
compared against the original — none of that exists here, and building
it would be a different project that starts by reading weights this one
deliberately never opens.

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


---

# Atlas 3.1 — changes since 3

Atlas 3 is frozen as the artifact of its version. Everything below is
new in 3.1, documented as it lands.

## 3.1.1 — The Lane-Emden constant stops being asserted

**What was wrong with it.** `engine/remnants.chandrasekhar()` computes
the white-dwarf ceiling from measured constants and one number that was
not measured and not derived:

```
M_Ch = C · (ħc/G)^(3/2) / (μₑ mₕ)²        C = 3.0984
```

ħ, c, G and mₕ are measurements this repo cites. **C came from a table.**
It is the structure of a star that holds itself up by degenerate electron
pressure, and structure is the solution of a differential equation nobody
here was solving. It was listed in `engine/unsolved.py` among the five
things this repo asserts and does not derive, with the entry saying
exactly what would close it: *"solving the Lane-Emden equation
numerically in this repo."*

That is now done, so the entry comes off the list.

**The equation.** A self-gravitating sphere whose pressure goes as
ρ^(1+1/n) obeys, in dimensionless form:

```
(1/ξ²) d/dξ (ξ² dθ/dξ) + θⁿ = 0        θ(0) = 1,  θ′(0) = 0
```

n = 3 is the relativistic degenerate case, which is why it is the one the
Chandrasekhar mass needs. At n = 3 there is no closed-form solution — it
is integrated. What the mass needs is a single number from it,

```
ω₃ = −ξ₁² θ′(ξ₁)
```

at the first zero ξ₁, after which `C = (√(3π)/2)·ω₃`, and the √(3π)/2 is
algebra rather than structure.

**Two things the method had to get right.**

*The singularity at the origin.* The 2/ξ term is undefined at ξ = 0, so
the integration does not start there. The series solution near the
origin, θ = 1 − ξ²/6 + nξ⁴/120, steps off the singularity, and plain RK4
runs from there. The step-off distance is not tuned: halving the step
must not move the answer, and a check requires it.

*Finding the surface.* The first version interpolated linearly across the
step that brackets the zero. That left n = 0 wrong by 1.8e-6 — small, and
**larger than the 1e-6 the closed forms are checked against**. Loosening
that tolerance would have been tuning the test to the method. Instead the
root is polished by Newton, taking each trial step with the same RK4 from
the last good state, so the surface is found by *integrating to it*
rather than by drawing a line across it. n = 0 now lands 2.2e-12 from
exact.

**Three checks, and the second is the one that matters.**

| check | what it does |
|---|---|
| `step_independent` | halving the step moves ξ₁ by 1.4e-10 and ω by 8.6e-11 — the answer is about the equation, not the integrator |
| `closed_forms` | n = 0 and n = 1 have exact solutions, so the same integrator is scored against algebra it cannot influence |
| `reproduces_the_assertion` | the derived C must reproduce the number that was asserted |

**The control caught the control.** n = 0 has θ = 1 − ξ²/6, so ξ₁ = √6 and
ω₀ = −ξ₁²θ′(ξ₁) = 2√6. I had written √6 in the reference table. The check
failed — **against itself, not against the integrator**, which had already
matched ξ₁ to ten figures and reproduced the literature's n = 3 values of
6.89685 and 2.01824 to six. A positive control that can only ever indict
the thing under test is not much of a control; this one indicted the
reference value, which is the other outcome it exists to produce.

**Result.**

```
n=0    ξ₁ = 2.449490   ω = 4.898979      exact 2.449490, 4.898979
n=1    ξ₁ = 3.141593   ω = 3.141593      exact π, π
n=3    ξ₁ = 6.896849   ω = 2.018236      literature 6.89685, 2.01824

C  = √(3π)/2 · ω₃ = 3.09797     asserted was 3.0984, 1.4e-04 apart
M_Ch = 1.4353 M☉                accepted 1.4
```

The asserted 3.0984 was right, and is now unnecessary. It stays in the
source as a fallback and as the thing the derivation is scored against,
but it is no longer what the Chandrasekhar mass is built on.
`chandrasekhar()` now reports **DERIVED** where it reported
DERIVED_FROM_ASSERTED, and `unsolved.py` carries a `CLOSED_BY_US` entry
with a check that fails if it ever silently reverts — because an entry
that simply vanishes from a list of open problems leaves no evidence it
was ever open.

**Four remain** on the asserted list: the Kleiber exponent, the fitted
dilution factor, the initial-final mass relation, and the held-out answer
format.


## 3.1.2 — The dilution factor, over-constrained

`engine/cosmos.py` has exactly one free parameter: `dilution`, the mass
of pristine gas each unit of stellar ejecta mixes into. It was tuned
until the simulated composition matched the sun, and the repo has always
said the resulting agreement is a **fit**, not a prediction. This is the
experiment that decides which it can become.

### Why a fit is not evidence

One parameter tuned against one number will always match, because there
is nothing left over to disagree with. Measured here, deliberately:
fitting dilution to oxygen alone lands it to **1.7e-08**. That number
looks spectacular and demonstrates nothing except that one knob matches
one number. A model with as many knobs as observations cannot be wrong,
and a model that cannot be wrong has told you nothing.

### What "more observables" means

Observations the *same single parameter* must satisfy **without being
re-tuned**. The cheapest version, and the one run here: hold an element
out of the fit entirely, then compute it. It had no way to influence the
parameter, so if it lands, the model predicted it. Same move
`eval/induction.py` already makes for rules — fit on six examples, score
on the rest — applied to a physical parameter.

### Leave-one-out: each element predicted by the other four

```
element   dilution   predicted      solar     ratio
C           4.87      0.00241      0.00290     0.83x
N           4.87      0.00100      0.00090     1.11x
O           6.19      0.00600      0.00770     0.78x
Ne          4.87      0.00154      0.00120     1.28x
Fe          4.87      0.00277      0.00160     1.73x
```

**It breaks, and it breaks informatively.** Iron, predicted by a
parameter four other elements chose, comes back **1.73× the solar value**.
Fitting dilution to each element *alone* shows the same thing from the
other side: C 4.04, N 5.43, O 4.87, Ne 6.19, **Fe 8.44**. Iron sits
outside the others.

That is not a parameter that needs better tuning. A parameter too small
for one element and too large for another is a **yield table with an
error in a specific entry**, and the per-element fits localise it.

### Fixing it, without the fix being circular

A factor fitted to iron will of course fix iron. So the correction is
applied to the **yield table** — a hypothesis about nucleosynthesis —
and then judged on the elements it was *not* fitted to.

```
iron yield x0.577          the four it was NOT fitted to: 19.5% -> 14.0%

C    0.83x  ->  0.83x
N    1.11x  ->  1.11x
O    0.78x  ->  1.00x
Ne   1.28x  ->  1.28x
Fe   1.73x  ->  1.00x
```

The mean improves, and **the mean hides where it came from**. Only oxygen
moved — the one element whose own fitting set contained the corrected
iron, so its fit had been contaminated by the bad entry. C, N and Ne are
unchanged. The check now says so explicitly rather than reporting the
19.5% → 14.0% and letting it read as a broad improvement.

So the result splits cleanly in two:

- **Iron's error is a yield error**, worth 0.577×, and removing it also
  removes the contamination it was causing in other elements' fits.
- **C at 0.83×, N at 1.11×, Ne at 1.28× are not iron's fault.** They are
  what is left once the structured error is gone.

### The theoretical limit

That residual is the point. This model has four generations, one
reservoir, instantaneous mixing, no infall, no outflow and no Type Ia
delay. Even with perfect yields it cannot do better than its structure
allows, so the useful question is not how close it gets but whether the
remaining error is **structured or scatter**.

At ~17–28% per element with no ordering by mass or by nucleosynthetic
family, C/N/Ne look like the structure rather than like more bad
entries. Closing that needs a mechanism, not a number: a Type Ia delay
time, or infall, or a second reservoir.

**The dilution factor stays on the asserted list.** It is still fitted.
What changed is that it is now fitted *and over-constrained*, the
over-constraint refutes it on a held-out element, and the refusal is
specific enough to name which yield is wrong and by how much.


## 3.1.3 — Nine elements overturn 3.1.2

The dilution experiment tested five elements because that was the
overlap between what `cosmos.py` yields and what the solar table listed
— a limit of the table, not of the physics. `cosmos` tracks twelve. The
table listed seven. Mg, Si, S and Ca were being yielded and had nothing
to compare against.

They are now in the table, taken out of `other` rather than added on top
so the total is unchanged and the sum-to-one check still has something
to catch. The testable set is **computed** from the overlap rather than
written down, so extending either side extends the experiment.

**Five → nine, and the conclusion inverts.**

```
                         held-out ratio
CNO        C 0.75x   N 1.11x   O 0.57x          mean 0.81x
Ne         Ne 1.28x                             mean 1.28x
alpha      Mg 1.96x  Si 2.22x  S 1.57x  Ca 3.57x  mean 2.33x
iron-peak  Fe 1.73x                             mean 1.73x
```

In 3.1.2 I concluded the iron yield was wrong by 0.577×. **That was an
artifact of having five elements.** With nine, iron at 1.73× sits
*inside* an alpha spread of 1.57–3.57×. It is not an outlier and it is
not the error.

The real pattern is a whole nucleosynthetic channel: **every alpha
element is over-predicted and C and O are under-predicted.** The model
over-produces what massive stars make in hydrostatic burning and
under-produces what dredge-up and winds return. Per-element fitted
dilutions now span 4.04 (C) to 17.14 (Ca) — a factor of 4.2, where five
elements suggested 2.1.

The iron correction test still runs, and now returns the opposite
verdict for the right reason: scaling iron's yield by 0.577× moves only
C and O, leaving Ca, Mg, S, Si, N, Ne untouched. A factor fitted to one
member of a family does not fix the family.

**What this says about the limit.** The residual is not scatter and not
a bad table entry. It is channel-structured, which points at mechanism:
no Type Ia delay, so iron-peak and alpha arrive together when in reality
Ia iron comes billions of years later; and one scaling for all
massive-star yields, so alpha and CNO cannot move apart. Both are
structural absences, and neither is closable by a number.

This is what "more observables" buys. Five could not tell a bad entry
from a bad channel. Nine can, and it says the earlier answer was wrong.


## 3.1.4 — Every naturally occurring element, and what it exposed

Nine was not the number of elements. It was the size of the overlap
between two small tables, and it had already produced one wrong answer.

`engine/abundance.py` now carries **all 83 naturally occurring elements**
— hydrogen through uranium, minus technetium and promethium, which have
no stable isotope, and minus everything above uranium, which is
man-made and not part of any universe simulated here. The seven trace
decay products between bismuth and thorium are recorded as absent with
the reason rather than left as a hole.

**Asserted in dex, derived in mass.** Abundances are quoted the way they
are measured: A(X) = log₁₀(N_X/N_H) + 12. Those are the assertion. Mass
fractions are **derived** from them using the atomic weights already in
the periodic table, so the conversion is arithmetic this repo performs
rather than a second table to get wrong.

**Eighty-three asserted numbers is a liability, so they are checked
against patterns they must satisfy for reasons independent of their
values:**

| check | result |
|---|---|
| Oddo-Harkins — even Z beats its odd neighbours, because paired protons bind tighter | **39 of 39, no exceptions** |
| abundance falls with Z | 0.088 dex per proton, ~8× per ten elements |
| the iron peak stands above Ti–Zn | **534× above their mean** — the binding-energy peak showing up in a table of counts |
| X, Y, Z derived from the dex values | **0.7374 / 0.2492 / 0.0134** against accepted 0.7381 / 0.2485 / 0.0134 |

That last row is the strongest evidence the table is not mistyped: three
numbers derived from all 83 entries, landing on an independently known
result to about 0.1%.

### The dilution test, now on twelve elements

```
CNO        C 0.77x   N 1.10x   O 0.74x               mean 0.87x
Ne         Ne 0.91x                                  mean 0.91x
alpha      Mg 1.35x  Si 1.63x  S 1.17x  Ca 2.67x     mean 1.70x
iron-peak  Fe 1.62x                                  mean 1.62x
r-process  Ag 47.8x  Au 5.5x   U 32.7x               mean 28.7x
```

**The r-process channel is out by ~30×**, and that is not a subtlety —
it is the model handing every late-generation star a neutron-star
merger's worth of silver, gold and uranium, when mergers are rare
events. Per-element fitted dilutions now span 4.97 (C) to 60.0 (Ag), a
factor of 12.

And it exposed something methodological worth keeping: **a badly wrong
channel is not only wrong about itself.** Every element's dilution is
fitted on the other eleven, so a channel off by 30× drags every other
fit with it — which is why the alpha and CNO numbers moved when the
r-process elements entered the set. The check now reports the dominant
channel first and the rest separately.

### Three conclusions, each one overturning the last

- **five elements** → "the iron yield is wrong by 0.577×"
- **nine elements** → wrong; iron sits inside the alpha spread, the error
  is a whole channel
- **twelve elements** → the alpha story is real but second-order; the
  r-process is out by 30× and was distorting everything else

Each was the best available reading of the data at hand, and each was
overturned by more of it. That is the argument for carrying all 83
rather than the handful someone needed at the time.


## 3.1.5 — Laws must hold; resemblance need not

Two corrections, and the second one changes what the dilution
experiment was even measuring.

### "Family" was the wrong word, and it was also an inference I typed

`eval/dilution.py` carried a `FAMILY` dict assigning each element to
CNO, alpha, iron-peak or r-process. Two things wrong with that.

**It was supplied rather than derived** — the exact thing this repo is
built not to do. It now follows from the binding curve `engine/nucleo.py`
already computes. Fusion releases energy only while binding per nucleon
rises, so the peak is a hard boundary:

```
Z <= 3           primordial        epochs.ORIGIN puts it at bbn
Z >  Z_peak      neutron-capture   fusing here COSTS energy, so no
                                   star builds it; it must be captured
even, 6..Z_peak  alpha-chain       reachable from carbon by alphas
otherwise        secondary         odd and below the peak, made from
                                   seed nuclei rather than built up
```

The peak is derived at Z=26 with 8.865 MeV per nucleon, and a check
confirms nothing below exceeds it and everything sampled above falls
short — so "fusion stops here" is a measured property of the curve, not
a rule about iron. 83 elements sort into 3 primordial, 11 alpha-chain,
12 secondary, 57 neutron-capture, and no element beyond the peak is
called fusible.

*A known edge, recorded rather than patched:* nickel comes out
neutron-capture because the semi-empirical peak sits at Z=26, while real
silicon burning makes Ni-56 and lets it decay to iron. The derivation is
right about the curve and wrong about nickel. Special-casing it would
hide a real limitation of the mass formula behind a hand edit.

**And "family" belongs to something else.** In this repo a family is
constituents that *actually come together* — a compound, a binding that
happened. Elements sharing a production process have not come together
with anything; they were made the same way. Two different relations
under one word, and the one that matters for the ladder is the other
one. It is `channel` now.

### A different universe is not a broken one

Everything the dilution experiment measured was distance to the sun —
and **distance to the sun is not the criterion.** A simulated universe
does not have to resemble ours. It has to be one the laws of ours could
have produced: internally consistent with every rule, and free to come
out looking nothing like home.

So the two questions are now separated, because **only one of them can
fail**:

```
LAWS         mass conserved                12 events, 0 violations
             nothing before its epoch      12 stars, 0 violations
             fractions sum to one          1.000000000000
             no negative abundance         14 elements, 0 negative
             channels respected            0 claimed by an impossible process

RESEMBLANCE  mean |simulated - solar|      4.80e-04 over 12 elements
             worst                         Ag at 63x
```

The r-process result reads completely differently under that split. As a
resemblance measurement it is ~30× off. **As a law question it is
silent**, because nothing forbids a history with more neutron-star
mergers than ours had. A universe richer in silver is a universe with a
different history, not a broken model.

What *would* be a violation is making gold before any merger could have
happened — and that is what `nothing before its epoch` checks, across
every star in every generation.

This does not retract 3.1.2 through 3.1.4. The r-process is still
over-produced by 30× relative to the sun, the channel structure is still
real, and if the goal were to reproduce *our* universe those would be
failures. The change is that the goal is not that, so they are
measurements rather than verdicts — and the things that genuinely cannot
be violated are now checked separately and named.


## 3.1.6 — Auditing what was still handwritten

You asked me to look for anything else I had typed in rather than
derived. I audited every module-level literal in the eleven modules
added since Atlas 2.

**Most are correct as they stand**, and the distinction matters:

- **Measured constants** — ħ, c, G, mₕ, oxygen diffusivity, bone
  compressive strength, B-DNA geometry, the 83 solar abundances, the
  four pulsar and merger observations, the genetic code, the nucleotide
  formulas. These are measurements of the world. Asserting them with a
  source is right; deriving them is not possible.
- **Definitions** — the Q4_K/Q5_K/Q6_K superblock sizes, the rung names,
  the registries of which functions to run. Naming is not inference.

**Two were inferences I had typed**, and both are now derived:

```
MAN_MADE_ABOVE = 92      ->  the smallest Z from which EVERY heavier
                             element is unstable, read off the periodic
                             table's own UNSTABLE set
ABSENT = {Tc, Pm}        ->  every element at or below that boundary
                             with no stable isotope, same source
```

The boundary derives to 92 exactly, and the check confirms nothing above
it is stable and 92 itself is not.

### And the derivation that failed, kept as a refusal

I also tried to derive the *reason* each element is missing: an unstable
element between the heaviest stable one and the heaviest primordial one
should be fed by a uranium or thorium chain and present in traces, while
one below has no parent and is genuinely absent.

**It runs and returns nothing**, because the premise is false in the
source data. `experts.UNSTABLE` means *"has no stable isotope"* — and
that is not the same property. Uranium and thorium have no stable
isotope and are primordial anyway; their half-lives are comparable to
the age of the Earth. The table does not mark them unstable, so the
heaviest stable element comes out as Z=92 and the window collapses.

So `trace_by_decay()` **refuses**, and says what would settle it:
half-lives. An element is primordial if some isotope survives a
reasonable fraction of the age of the Earth, and trace if a long-lived
parent decays through it. `engine/isotopes.HALF_LIVES` exists for
exactly this and is empty. Both are one measurement away, and neither is
guessed.

Protactinium falls in the same gap — no stable isotope, not marked
unstable, no abundance — and the coverage check names it rather than
rounding it away.

**This is the better outcome than the handwritten version.** The typed
`ABSENT = {Tc, Pm}` was confidently wrong about six elements: polonium
through actinium are not absent, they are trace-present, and I had
silently excluded them. The derivation cannot tell those apart either —
but it says so.


## 3.1.7 — Proteins, and what the benchmark hashes will and will not give up

### The protein rung

`engine/biomatter.py` now runs nucleotide → codon → gene → **protein** →
genome → cell → organism. 13/13 checks.

```
ATGTGTGGATAA  ->  MCG, stop at codon 4
MCG           ->  C10H19N3O4S2, 309.399 g/mol, epoch supernova
              ->  8 possible genes, 3.0 bits lost in translation
```

**Mass two ways, and the atoms arbitrate.** A chain of n residues is the
n free amino acids minus n−1 waters, one per peptide bond. Route one
weighs each acid and subtracts the waters; route two builds the
polymer's atom counts and weighs that once. They share the atomic
weights and nothing else — different operation order, different rounding
path — and they agree to 0.0e+00 on a 20-residue chain. The atom route
also supports a check mass cannot: the chain must hold **exactly three
fewer atoms per bond** than its parts.

**All 64 codons translated singly rebuild the table**, and the
degeneracies partition all 64 exactly — so the map is onto and not
one-to-one, which is why `back_translation_count` enumerates the
preimages and then **refuses** to name a gene. Three residues already
have 8.

**Sulphur sets the epoch.** Cysteine and methionine carry S at Z=16, so
any chain containing either waits for supernovae. Everything else is
CHNO and earlier. Same mechanism as DNA and phosphorus, reached from a
different molecule.

Refusals: a sequence that is not a whole number of codons, a base
outside ACGT, a codon absent from the table, a residue with no formula.
Each raises with the reason that makes it malformed.

### Can the held-out answer format be recovered? Measured, not guessed

Two things are now established rather than assumed.

**The hash is a function of the answer, and injective.** Over 40 distinct
computed arithmetic answers: zero values map to two hashes, zero hashes
are shared by two values. So recomputation is right about what the
answers are — 137 + 11 really is 148 — and the only unknown is the
serialisation.

**And the serialisation is not any obvious one.** Searched and failed:

```
251 template forms       prefixes, suffixes, JSON, repr, float formats,
                         UTF-16, int-to-bytes, double-SHA, HMAC with
                         eight plausible keys — tested against six pairs
                         simultaneously
2,200,000 integers       sha256 of every bare integer string from
                         -200,000 to 2,000,000 — no expected hash is one
1,742,015 affixes        every constant prefix or suffix up to 3
                         printable characters, plus 1-char both sides
```

So whatever wraps the answer is longer than three characters, or a
different encoding, or the answer text is prose rather than a number.

**Ways to make it recoverable, cheapest first:**

1. **Ask the publisher for the serialisation.** One line unlocks all 165
   permanently. Everything else is a workaround for not having it.
2. **Publish answers beside hashes** in future benchmark files. The hash
   is worth keeping — it is what makes the file tamper-evident — but a
   commitment nobody can open is a commitment nobody can check.
3. **Release a key after evaluation.** Keep answers hidden while the
   benchmark is live by hashing `key + answer`, then publish the key.
   Verifiable *and* recoverable, in that order.
4. **Publish a Merkle root plus per-item openings.** Same property with
   finer grain: each answer can be opened individually without revealing
   the rest.
5. **Widen the brute force.** Well-posed now — find constant `F` with
   `sha256(F(answer))` matching — but the space past three characters is
   large and it is guessing at someone else's convention.

Meanwhile the hashes already earn their keep without being opened:
prompts sharing a hash must share an answer, which is **46 equivalence
classes over 98 prompts**, and Atlas gives one answer in every class.
That is a wording-invariance test taken from the benchmark's own
commitments without ever learning what the answers are.


## 3.1.8 — Atoms breaking and binding, and a commitment that can be opened

### Transitions: where the answer set changes

The ladder was static — an element sat at a rung and stayed there. Atoms
do not. `engine/transitions.py` tracks both things they actually do, as
**events in time that change which experts can answer**.

```
decay  Re -> Ta at supernova    +[element:Ta]  -[element:Re]
bind   C+H -> CH4 at stellar_c  +[compound, formula:CH4]
```

A transition is a **continuation of a prompt that needs a different set
of experts than the one before it**. That is the reason to track them:
each edge is a place where the answer set changes, so the reachable
contexts grow with the edges rather than with the atoms. Measured: **27
atoms take part, and the transitions between them reach 53 distinct
expert sets.**

Nothing here is a decay table. Which way a nuclide goes is the sign of
its Q-value — the products are more bound in total, or they are not —
and for alpha the escaping particle's own 28.3 MeV counts toward it.
Taking each element's **best-bound** isotope: 44 come out stable, 27
undetermined, 21 decay with a determined mode.

**It refuses inside its own error bar.** Q is a difference of two
semi-empirical binding energies and the formula is good to a few MeV, so
when |Q| is smaller than that the *sign* is not determined — and the
sign is the whole prediction. 49 nuclides land there and get
`undetermined` rather than a confident guess.

Binding is computed, not listed: valences close at the lowest common
multiple, giving H2O, CH4, H3N and CO2 from arithmetic. And every edge
carries a time — stamped with the later of its inputs' epochs, with a
check that none runs before something it needs.

**Rendered and read back in Godot**, the fourth verification level: 36
transitions emitted as a scene, walked headlessly, and every one
recovered with its kind, epoch and expert counts intact.

*Two checks failed first and were right to.* The first version gave
every element the same generic tags, so most transitions changed nothing
— 39 answer sets from 92 atoms, fewer contexts than nodes. The fix was
not a longer tag list: **an atom is itself an expert**, so `element:Z` is
in the set by construction and a decay necessarily changes it. And the
first version scanned isotopes upward and took the first with a
determined decay, which reported 91 of 92 elements as beta-plus
emitters — an artifact of the scan, not physics. An element's
representative is the isotope that binds best.

### A commitment that can actually be opened

`eval/commit.py`. The held-out benchmark commits to its answers with a
bare SHA-256, which hides them and also makes them **unrecoverable
forever** — this repo measured exactly how unrecoverable. A commitment
nobody can open is a commitment nobody can check.

```
commit   h = hmac-sha256(key, answer)     publish h only
hide     the key stays out of the repo and out of the system
open     publish the key; every answer becomes checkable
```

While the key is withheld this is exactly as hidden as a bare hash —
verified: none of the published commitments matches the plain SHA-256 of
its own answer. Once released, everything reopens, which the bare-hash
version cannot do at any price. And because the hashes were published
first, it also proves the answers were not chosen after seeing results.

**HMAC rather than `sha256(key + answer)`**, deliberately. SHA-256 leaks
enough internal state that publishing `sha256(m)` lets someone compute
`sha256(m || x)` for a chosen `x`. HMAC exists for exactly this and is
used instead of hand-rolling the concatenation.

**The system never sees the key.** It is in no module, it is not written
to the repo, and a check greps the tree to confirm the name appears
nowhere but the implementation — and confirms it was unset in the
environment the test ran in. It arrives at verification time and nothing
stores it.


## 3.1.9 — Universes in chunks, so they can hold enough matter

`engine/cosmos.py` runs four generations of three stars: twelve stars,
251 solar masses, about 1e56 atoms. That is a model of a mechanism, not
a universe — and it cannot be made denser by adding stars to a list,
because the list is what it costs.

`engine/cosmoschunks.py` partitions a universe the way `engine/chunks.py`
partitions a corpus too large to prefill. Each chunk is an independent
region with its own derived seed; the universe is the ordered set.

### Density comes from counting, not from storing

A chunk holds a mass and a composition. The atom count follows:

```
N(element) = M_chunk × f(element) / (A × u)
```

So a chunk contains 2e59 atoms whether or not anyone writes them down.
Same rule the 1e9-token corpus runs on — derive, do not materialise —
applied to matter instead of text.

```
            10 chunks  ->  1.949e+60 atoms,  2.041e+03 Msun
         1,000 chunks  ->  1.949e+62 atoms,  2.041e+05 Msun
     1,000,000 chunks  ->  1.949e+65 atoms,  2.041e+08 Msun
 1,000,000,000 chunks  ->  1.949e+68 atoms,  2.041e+11 Msun
```

The last line is reported **without running it**. One chunk is enough to
know the rest, because the partition rule is identical in each and the
seed only changes which star masses come up — so the density of a
universe is a multiplication rather than a simulation. A check confirms
the projection is linear in chunk count to within one part in a million.

### Consistent across universes, and measurably so

A chunking is only worth anything if chunk *k* of one universe means the
same thing as chunk *k* of another. The partition rule is fixed and
derived, never sampled: **chunk k's seed is `hmac(universe key, k)`** —
reproducible from the key alone, independent of its neighbours, and
different in every universe.

Across three universes at five chunks each:

```
same chunk count            5, 5, 5
laws hold in every chunk    15 chunks, all mass conserved
heads differ                3 distinct heads from 3 keys
comparable scale            total mass varies under 50%
same elements present       identical element set in every one
```

Same structure, different history — which is the pair of properties
that makes two universes comparable at all rather than merely different.

### Every chunk is keyed, and the keys chain

A chunk key is `hmac(universe key, index)`, and the chunk digests link
into one 256-bit head for the whole universe — `engine/chain.py`'s
discipline applied to space as well as time. Hand back a chunk key and
that chunk alone regenerates and matches the head, with nothing else
rebuilt. A key from a different universe is **refused** rather than
matched to the same index.


## 3.1.10 — Folding by enumeration, and a paradox that is about time

### Every fold, not a search

Structure prediction is refused and names what does it instead: AlphaFold,
about 93 million learned parameters, with no rule to extract.

What is not refused is **enumeration**. For a short chain on a lattice the
set of folds is finite, so `engine/folding.py` walks all of them, scores
each, and reports the minimum. No heuristic, no sampling — the answer is
not the best fold found, it is the best fold there is.

```
FFFFWWFF     543 folds, best -27.00,  8 at the minimum
GGGGSSGG     543 folds, best  -1.50,  4 at the minimum
FGFGFGFG     543 folds, best  -6.00, 38 at the minimum
MCGFWAIL     543 folds, best -12.25,  2 at the minimum
```

Degeneracy is reported rather than one fold picked. FGFGFGFG has **38
distinct folds tied at the ground state** — which is a fact about that
sequence, not an ambiguity to resolve.

### Hydrophobicity derived, and the threshold that failed

The usual lattice model sorts residues into H and P, which needs a cutoff
someone chooses. This takes the ratio of carbon to polar atoms straight
out of the formulas already in `biomatter.py` — glycine 0.67, phenylalanine
3.00 — and uses it **continuously**.

Trying to split it failed honestly and is recorded: the largest gap in the
sorted ratios falls between tyrosine (2.25) and tryptophan (2.75), which
would make **only F and W hydrophobic** and put lysine among them. That
split is wrong, and the continuous form does not need it.

**Hydrophobic collapse, plainly:** oily things stick together in water,
the way oil beads up in a pan. Some residues are oily and some are not, so
a chain in water tucks its oily parts inward and leaves the rest facing
out. That tucking *is* the fold. Measured here: FFFFWWFF reaches −27.00
and GGGGSSGG only −1.50 over the *same 543 shapes* — same geometry, very
different cost, depending only on what the chain is made of.

### Levinthal is about our universe's age, not about arithmetic

```
 10 residues   5.90e+04 states   1.87e-15 yr   possible now
 50 residues   7.18e+23 states   2.27e+04 yr   possible now
100 residues   5.15e+47 states   1.63e+28 yr   NOT possible now
```

A 100-residue chain has 3¹⁰⁰ conformations; trying them at a picosecond
each takes **1.63e28 years**, which is 1.2e18 times the age of this
universe. So folding here cannot be a search, and real proteins fold in
milliseconds.

**But heat death is around 1e100 years.** That is 6e71 times longer than
an exhaustive fold needs. The search is impossible in a 13.8-billion-year
universe and comfortable in one allowed to run to heat death — so
Levinthal is a statement about *when you are*, not about proteins. That
is exactly the kind of difference between universes this project exists
to notice, and the check asserts both halves: the paradox must reproduce
now, and must dissolve by heat death.

### How many learned parameters, for the record

```
Qwen3.6-35B-A3B    35,000,000,000 learned
AlphaFold2            ~93,000,000 learned
Atlas 3.1                       0 learned
                            1,081 written down, by hand, all visible
```

Every number the system holds is a module-level constant in 13,922 lines
across 74 files — 32 million times fewer numbers than Qwen, and each one
either a measurement with a source, a definition, or a fixture to score
against. None was fitted, and none was learned.


## 3.1.11 — Atom provenance, and the benchmark format recovered

### Where each atom goes after the prompt

`engine/transitions.py` said a decay changes which experts apply. It did
not say *which atom* decayed, where it had been, or what it joined
afterwards. `engine/provenance.py` answers that.

```
atom: U #0 of chunk 0, universe-0
  key 6c2f...
   ns_merger  formed U   in chunk 0 by neutron-capture
   ns_merger  decay  Th  U -> Th by alpha; Q=4.27 MeV
   ns_merger  decay  Ra  Th -> Ra by alpha
   ns_merger  decay  Rn  Ra -> Rn by alpha
   ns_merger  decay  Po  Rn -> Po by alpha
   ns_merger  decay  Pb  Po -> Pb by alpha
```

**That is the real uranium series, derived from Q-values alone.** Nothing
in this repo was told it.

A history is **derived from the key, not stored**. The key is
`hmac(universe key, chunk‖element‖serial)`, and every event follows from
it — so a universe of 1e60 atoms costs nothing until an atom is named,
and naming one reconstructs its whole history in microseconds. 200 atoms
of one element in one chunk get 200 distinct keys; the same atom in
another universe gets a different one.

**Identity survives transformation**, which is the point. When the atom
decays its element changes and its key does not — the thing that was
uranium and is now lead is the same thing, so a question about it spans
both. And **every step changes the answer context**: 11 steps, 11
distinct expert sets, no two consecutive ones alike. The custody chain
is hash-chained, verifies over all 11 events, and an altered history is
caught at the first divergence.

**And where it stops being right, recorded rather than patched.** The
chain carries on past lead — Pb → Hg → Pt → Os → W → Hf — and that part
is wrong. Lead-208 ends the series. The semi-empirical mass formula is a
liquid drop: volume, surface, Coulomb, asymmetry, pairing, and **no shell
structure**. Pb-208 is doubly magic, 82 protons and 126 neutrons both
closed, and that extra binding is exactly what a liquid drop cannot see.
So the model walks straight through the one nucleus that should stop it.
Hard-coding lead as a terminus would hide a real limitation; shell
closures are now in `engine/unsolved.py` with what would close them.

### The benchmark format, recovered

The 165 held-out answers looked permanently unrecoverable — 251 template
forms, 2.2 million bare integers, 1.74 million constant affixes, all
missing. **The reason was not cryptography.**

```
sha256('148')                                                   no
sha256('Plan: add 137 and 11. Check: 148 - 11 = 137.\nAnswer: 148')  YES
```

The answer was never the number. It is the controller's full
plan-and-check string, and no amount of prefix searching finds a
56-character sentence containing the working.

Two recipes, from `build-atlas-novel-benchmark.py`:

```
id                      sha256("ATLAS-NOVEL-BENCHMARK-1\0" + prompt)   165/165
expected_answer_sha256  sha256(answer)                                  plain
```

`EVE-ROUTE-1`, the namespace in the handoff's key file, matches **0/165**
on either field — it belongs to the routing subsystem, not this
benchmark. The namespace *pattern* was the clue; the namespace itself was
the wrong one.

**So the arithmetic third is no longer verified by recomputation — it is
verified against the file's own published commitment, byte for byte:**

```
arithmetic                80  exact 80  mismatch 0
dna_structure             24  no rule yet
material_ontology         16  no rule yet
time_measurement          12  no rule yet
periodic_table_reference   9  no rule yet
virtual_planet            12  no rule yet
synthetic_galaxy          12  no rule yet
```

The remaining 85 need each tool's answer string reconstructed from the
same source, which is mechanical now that the scheme is known.

And the design lesson for `eval/commit.py` sharpens. A bare hash of a
*number* is brute-forceable in seconds; a bare hash of *prose* is not,
**by accident rather than by design**. Neither is a commitment. Security
by unguessable formatting is not security — it is an obstacle that
happens to have held for a while.


## 3.1.13 — Variant biochemistry: what moves and what stays forced

`engine/biomatter.py` builds one biochemistry — four bases, twenty
residues, a phosphate backbone, water. Every number in it is ours, and
nothing in the derivations required that: `codon_length()` already took
the alphabet size as an argument, and the epoch gate is whatever the
backbone's elements demand. **The constants were the only thing tying
the ladder to Earth.**

`engine/variantlife.py` makes the biochemistry a parameter and re-runs
the derivations.

```
 bases  sites   codes  spare    bits
     2      5      32     11    5.00
     3      3      27      6    4.75
     4      3      64     43    6.00     <- ours
     5      2      25      4    4.64
     6      2      36     15    5.17
     8      2      64     43    6.00
```

**What moves:** code length, table size, spare codons, bits per site.
Six bases need only two positions; two bases need five. **What is
forced:** the code must be the shortest that names everything, and one
site shorter never suffices — checked for every alphabet from 2 to 8.
One rule, different outputs.

Our 43 spare codons are not a fact about life. They are what four bases
and twenty-one meanings *leave over*, and a five-base biochemistry would
have four.

### Earth has to come back, or the generalisation is wrong

The strongest check here: instantiate Earth through the general
machinery and it must reproduce **codon length 3, 64 codes, 43 spare,
supernova gate** — exactly what `biomatter.py` gets by hard-coding them.
A generalisation that cannot return its own special case has generalised
the wrong thing.

### Three verdicts on a backbone, because two were not enough

```
chains   C, N, P, S    gated at stellar_c and supernova
inert    He, Ne        closed shells -- refused
unknown  Si, Fe        no valence on record -- refused, differently
```

Two failures got it there, both worth keeping:

**It refused Earth.** The first rule demanded every backbone element bond
at least twice. Hydrogen bonds once — it is a *cap*, not a link, and a
backbone needs both. Fixed by requiring that at least one element chain
rather than all of them.

**Then it refused silicon.** The second treated absence from the valence
table as zero valence. Silicon bonds four ways; the table holds ten
elements and is not a census. **Absence of data is not evidence of
inertness.** So the verdicts split three ways: a noble gas genuinely
cannot bond and is refused; an element with a known valence is judged on
it; an element with no entry is refused *for want of data* and says so.

And the noble gases are derived, not listed. The aufbau shells hold
2, 8, 8, 18, 18, 32 electrons, so the running totals — **2, 10, 18, 36,
54, 86** — are exactly the closed-shell elements. Computed from the
capacities rather than typed out.

### What this buys

A universe with different chemistry now grows different life through the
same rules, and the rules say which chemistries are possible before
anything is simulated. Combined with 3.1.5's laws-versus-resemblance
split, a biochemistry unlike ours is not a broken one — it is a different
point in a space the ladder can already walk.


## 3.1.14 — Two things that were typed in, checked

You asked whether the mass formula's 3 MeV was something we set. It was.
And you were right that a ten-element valence table is too small.

### The error bar is asserted, and cannot currently be measured here

`SEMF_MeV = 3.0` is typed. It is the threshold every decay refusal turns
on, so a wrong value silently changes what the repo will and will not
say — which makes it worth knowing exactly what kind of number it is.

I tried to measure it and the attempt failed instructively. Scoring the
formula against the periodic table's atomic weights gives a **median
residual of 80 MeV**, which looks catastrophic and is an artefact: a
standard atomic weight is the **abundance-weighted average over an
element's isotopes**, not the mass of any one nuclide. For iron the
formula predicts 55.935 u — Fe-56 to three decimals — while the
tabulated weight is 55.845 because Fe-54 pulls it down. Comparing a
single-nuclide prediction to a multi-isotope average measures the
isotope mix, not the formula.

So it stays asserted, with the source named, and it is now on the
`unsolved.py` list with what would close it: **per-isotope masses**,
which this repo does not carry. Six things are on that list now.

### Valence, derived instead of typed

`engine/valence.py`. Not eighty more numbers — the same shell capacities
that gave the noble gases:

```
shells hold   2, 8, 8, 18, 18, 32
outer count   Z above its noble core, less the d and f already filled
valence       that count if 4 or fewer, else 8 minus it
```

**50 elements instead of 10**, and silicon — the element `variantlife.py`
had to refuse — comes out bonding four ways without anyone deciding.

The ten hand-written valences are kept as a **fixture**, and the
derivation is scored against them rather than fitted to them. That
fixture earned its keep twice:

**Germanium came out −6.** Subtracting whole shells in order counted the
ten 3d electrons as outer ones. After argon the period holds 4s, then
ten 3d, then 4p — eighteen elements, of which only the eight s and p
ones set the bonding.

**Then iodine came out with no valence at all.** Bounding the d-block
count at the start but not the end meant iodine counted the 21–30
d-block, which is *already inside* its krypton core.

Both were caught by ten numbers a person wrote down, which is what a
fixture is for.

**And where it refuses:** 68 d- and f-block elements are **not**
assigned. Iron is +2 and +3, manganese runs +2 to +7, and which appears
depends on the partner. That is not a number waiting to be looked up —
it is a property the main-group rule does not describe, so it says so
and names what it would take.

### A latent bug the wider table reached

Feeding 50 valences into `transitions.bind_edge` crashed with a division
by zero. While the table held ten hand-picked elements **every entry
bonded**, so nothing ever guarded against a valence of zero — and two
noble gases give `gcd(0, 0)`.

A zero valence is not a small one. The bug had been there since the
module was written and only a table wide enough to contain an inert
element could reach it.


## 3.1.15 — The error bar measured, and a result withdrawn

You said it should guess and then be checked. It can, and the check
changed the answer.

### Measuring it: mono-isotopic elements

The formula predicts isotope masses. What was missing was something to
compare against — and there is one. **Some elements have only one
isotope**, so their standard atomic weight *is* that nuclide's mass and
the average has a single term.

Which elements those are does not need asserting either. A
mono-isotopic weight sits close to a whole number (aluminium 26.9815)
while a mixture lands between them (chlorine 35.45, copper 63.55). The
model picks its own comparison set.

```
16 elements (Z >= 8)    median 7.97 MeV   mean 19.27   worst 56.26
typed value                     3.00 MeV
```

Light nuclei are worst — hydrogen is out by 25 MeV, because a liquid
drop is a poor model of four nucleons, so they are excluded and named.

### What the measurement costs

**Real alpha Q-values in the heavy elements are 4–5 MeV. The measured
error bar is 8.** So a formula honest about its own error **cannot
resolve alpha decay at all**, and every chain collapses to
*undetermined*.

That includes the uranium series. 3.1.11 reported that the module
derives U → Th → Ra → Rn → Po → Pb from Q-values alone, which it did —
**at a 3.0 MeV bar taken from the literature and never checked here.**
When the bar was measured it turned out optimistic by more than double.

**That series is withdrawn as a result.** It was not a derivation
surviving a test; it was an artefact of an under-estimated error. The
check now requires the opposite — that nothing be claimed at the
measured bar — and records that the typed value still produces it.

Same for 3.1.12's trace/absent split: radium and radon resolved as
trace on alpha steps, and those steps are now unresolvable. Everything
unstable is undetermined.

### Why the measured value is the default anyway

Refusing is correct when the error bar says you cannot tell. Keeping
3.0 because it gives the nicer answer is choosing the number that
flatters the model, which is the one thing this project is built not to
do.

Both values are available and the consequence of each is visible in the
source. The measurement is an **upper bound** — the near-integer test
admits chromium and molybdenum, which are not mono-isotopic — so the
true error sits between 3 and 8 MeV.

And that sharpens the unsolved entry rather than closing it. It is no
longer *"measure the error bar"*. It is **"decide whether this model can
see alpha decay at all"**, and it needs per-isotope masses to settle.


## 3.1.16 — One error bar was the wrong object

You said each field should have its own rules, and that folding and decay
should not share a number. That is exactly what was wrong, and fixing it
restored a result I had withdrawn.

### The bar depends on the question

A single "error of the mass formula" answers a question nobody asked.
**A decay is a difference of two binding energies**, and the formula's
errors are strongly correlated between neighbouring nuclei — the same
volume, surface and Coulomb terms are slightly off in the same direction
for both. Most of it cancels.

Measured on the same seventeen nuclides:

```
absolute binding error    4.76 MeV median      what a MASS prediction inherits
Q-value error             1.21 MeV median      what a DECAY inherits
```

Alpha Q-values in the heavy elements are 4–5 MeV. Against 4.76 they are
invisible; against 1.21 they are comfortable. Same formula, same data,
opposite conclusion — because the first number was measuring the wrong
thing.

`error_bar("mass")` and `error_bar("decay")` are now different
functions, and asking for a bar without saying which question raises
rather than guessing.

### The withdrawal is itself withdrawn

3.1.15 withdrew the uranium series on an 8 MeV bar. **That withdrawal
was right given the number it had and wrong about the number.** The
series is back:

```
U -> Th -> Ra -> Rn -> Po -> Pb        at a 1.21 MeV measured bar
```

Not on the literature's 3.0, and not on an absolute error that does not
apply — on a bar measured here, on differences, which is what a decay
actually inherits.

Both corrections were right in sequence and the second needed the first
to have happened. Measuring 8 MeV was what made it obvious the quantity
was wrong.

### And the fixture had to change too

The earlier measurement scored predictions against standard atomic
**weights**, which are abundance-weighted averages. Chromium came out 55
MeV wrong because Cr-53 and Cr-54 pull the average off Cr-52 — not
because the formula missed. `BINDING_FIXTURE` is **per-nuclide**
measured binding energies for exactly that reason.

### What it buys, beyond the series

```
Po  trace          At  trace          Ra  trace       Rn  trace
Ac  undetermined   Fr  undetermined   Pm  undetermined
Tc  absent
```

Polonium and astatine now resolve as trace, which they are. And the
finding that chains cannot branch **survives**: beta Q-values are 0.02
to 2.3 MeV and straddle the 1.21 bar, so Ac, Fr and Pm stay
undetermined. The unsolved entry narrows from "can it see decay at all"
to **"can it see beta decay"** — and names what is missing: the alpha
bar rests on four pairs in the fixture, and the beta bar on none.


## 3.1.17 — Beta decay: a missing term bigger than the answer

Making it see beta decay turned up something worse than a missing
capability.

### The term that flips signs

A beta-minus Q-value is not the change in binding energy alone. A
neutron becomes a proton, and against atomic masses that releases the
neutron–hydrogen difference too:

```
Q(beta-) = B(Z+1, N-1) - B(Z, N) + (m_n - m_H)c^2
```

**That term was missing.** It is 0.78 MeV and typical beta Q-values run
0.02 to 2.8, so leaving it out is not a small correction — **it flips
signs**. C-14 → N-14 came out at −0.620 MeV, meaning no decay, against
a measured +0.156. Every beta decision the module had ever made was
wrong by 0.78 MeV.

And the term is **derived, not typed**. `engine/particles.py` already
carries the proton, neutron and electron masses; the neutron–hydrogen
difference is just `n − (p + e)`. My first version wrote `0.78254` in by
hand and even that was wrong in the fifth digit — the masses give
0.78233.

### A third bar, because a beta step is not an alpha step

```
mass    4.763 MeV      error in ONE binding energy
alpha   1.208 MeV      error in a difference two protons apart
beta    1.061 MeV      error in a difference one proton apart
```

Measured on five real decays, with the reference Q **derived from the
fixture's own binding energies** by the same rule — the measured
Q-values were carried too at first, which was giving the answer and the
working.

### And then: stable is not the same as unresolvable

The rule reported anything with no positive Q as *stable*. But a mode
whose computed Q is negative and **smaller than the bar** has an
undetermined sign — the formula cannot tell decay from stability there.
That is now separated.

### What it actually gets right, measured

Arguing about the bar is cheap. Scoring it is not:

```
14 decays with known fates:   8 right   3 refused   3 WRONG
  C-14    is beta-minus,  said stable
  K-40    is beta-minus,  said beta-plus
  Pb-208  is stable,      said alpha
```

**The three wrong ones are the number that matters**, and all three are
*outside* their own error bars — the formula is confident and mistaken,
not uncertain. A wider bar would convert them to refusals rather than
fix them.

Pb-208 is the informative one: doubly magic, 82 protons and 126
neutrons, extra-bound in a way a liquid drop cannot see. The same
blindness that makes the uranium chain overrun past lead makes lead
itself look unstable.

So the unsolved entry changes from *"can it see beta decay"* — it can —
to **"three decays it gets confidently wrong"**, with shell corrections
named as what would fix two of them.

### 3.1.18 — a bar is a property of a domain, and not always an energy

`engine/nucleo.py` measures three error bars because a mass, an alpha step
and a beta step are three questions about one formula. This version takes
that further, because the three are all still nuclear. A protein is not a
nucleus:

    nuclear binding        ~8 MeV per nucleon
    chemical bond          ~4 eV
    hydrogen bond          ~0.2 eV
    thermal noise at 310 K  0.0267 eV

Eight and a half orders of magnitude. The 1.208 MeV alpha bar is forty
million thermal quanta, so applying it to a fold would refuse every fold
there is; a folding bar applied to nuclei would accept every decay
including the ones that do not happen. Neither error is subtle, and both
come from treating "the error bar" as one thing.

`engine/scales.py` holds one bar per domain with the unit it is in, and
refuses for a domain that has not established one — which is the honest
state of chemical bonds here, since `engine/valence.py` counts bonds and
never weighs them. Thermal noise is DERIVED: kT from Boltzmann's constant
and the elementary charge, both exact by definition since the 2019 SI
revision. Nothing in it is fitted.

**The finding is that folding's bar is not an energy at all.** The nuclear
bars are residuals against MEASUREMENT — the formula says a binding energy,
a real nuclide has one, the spread over many nuclides is the bar. There is
no measured energy for a fold of `CGCG` on a square lattice, because no
such object exists. So the bar is measured MODEL AGAINST MODEL: how often
an exact minimum survives a change the chemistry does not settle. Sulfur is
that change — Pauling puts S at 2.58 and C at 2.55, no difference at all —
so the baseline counts S as polar and the variant counts it as greasy, and
only cysteine and methionine move.

    55 of 96 sequences keep the same minimising fold.
    43% of exact minima are the model's choice, not the sequence's.

    nuclear    bar in MeV     residual against a measurement
    folding    bar as a RATE  disagreement with another model

Different classes of thing do not merely get different numbers. They get
different KINDS of bar, because what there is to be wrong about differs.
`units_never_mix` enforces it: a rate and an energy are different claims
and the unit is what keeps them from being compared.

**Two wrong measurements on the way, both kept.** The first ran over
alternating sequences and got 14 of 14 surviving. A square lattice is
bipartite, so every contact joins an odd index to an even one; in `ABABAB`
every contact is A·B and the energy is one constant times a contact count,
which no reweighting can reorder. Those sequences were unflippable BY
CONSTRUCTION and a perfect score over them measured nothing. It is now a
check, `alternating_cannot_be_flipped`.

The second looked for a threshold. Ten flipped sequences all had small gap
fractions, suggesting a fold separated by enough of the spectrum would be
safe — the same shape as the nuclear bar, where a Q-value outside 1.208 MeV
resolves. Over 375 sequences it did not hold: survival runs 53% in the
lowest band to 81% in the highest, with a flip as high as 0.224. The
correlation is real, weak, and not a threshold. The hypothesis is recorded
as overturned.

**And a bug the bar found.** Reporting degeneracy made every short sequence
a two-way tie. Those were never two folds — `walks()` fixes the first step,
which removes the fourfold rotation but not reflection across it, so every
fold was being counted with its mirror image. Mirrors have identical energy
by construction and can never be told apart by any energy at all, so
counting them as a tie makes the model look undecided about something it
was never asked. `canonical()` quotients by reflection; `FGFGFGFG` goes
from 38 tying folds to 19, and `fold()` and `ground_set()` now give one
answer instead of two.

    engine/scales.py    6/6      registry, kT derived, units never mix
    engine/folding.py  11/11     was 7; +mirror, +scale-free, +parity, +bar
    eval/audit.py      21/21
    eval/heldout.py   165/165    byte-exact
    eval/benchmark.py  ALL PASS  5,737 correct, 0 wrong

### Known weak points, deferred to Atlas 3.3

**Two tracks, and they are different releases.** Atlas **3.2** is where
every rule is made consistent with every other rule -- the lab sweep,
the clashes resolved, the missing rules found and added. Atlas **3.3**
is packaging and infrastructure, which is what the items below are.

Raised in outside review and confirmed here. None of them affects a
machine that has the full tree, which is why they are deferred rather
than fixed now. They are recorded so that nobody has to rediscover them.

**1. `eval/audit.py` fails on a machine without Godot, and should not.**
`engine/ir.py:183` degrades correctly — `EXECUTABLE` drops `gdscript`
when Godot is absent — but `eval/audit.py:135` asserts `len(EXECUTABLE)
== 3`. So a clean Linux or Windows box reports 20/21 while the system is
working. This contradicts "runs on any computer" and is the one item
here that is a real bug. The claim being audited is that the executable
backends AGREE, not that there are three of them; two agreeing is still
cross-verification.

**2. No packaging, and the checks are not discoverable.** There is no
`pyproject.toml` and no `setup.py`. There are 10 scripts in `eval/` and a
`check()` in every engine module — over 200 self-checks — but nothing a
standard runner finds on its own, so a reviewer has to be told where to
look. That matters when independent peer review is a stated goal.

**3. `ui/server.py` is a local demonstration and is not hardened.**
Stdlib `HTTPServer`, no authentication, no persistence, and
`traceback.format_exc()[-800:]` in the error body at line 114. Fine on
localhost, not fit to face a network. It should say so and bind
accordingly.

**4. `tools/get_godot.py` only carries the macOS URL.** It does detect
the platform and does honour `ATLAS_GODOT`, so the escape hatch exists;
the download table is just incomplete. Minor, and only visible once (1)
is fixed.

**Not defects.** Coverage is narrow and the natural-language layer is
regexes and overlap scoring. Both are accurate descriptions and both
limit RECALL, not PRECISION: the system abstains where it cannot derive,
and the number that must be zero is wrong answers, not abstentions
(5,737 correct, 0 wrong). This is not a general question-answering
system and nothing here should be read as claiming it is. The Qwen
artefacts are also sometimes assumed to be external; they are not, they
are six files totalling 223 MB tracked in this repository, and a fresh
clone gets them.

### 3.1.19 — a planet that terraforms itself, with nothing doing it

`engine/terraform.py`. The rule the module exists to obey: **nothing acts
on the planet.** No engineer, no seeding, no intervention, no optimiser
hunting for a habitable answer. There is a rock with a hot interior, a
star shining on it, and the consequences. `nothing_acts_on_the_planet`
enforces it structurally — 41 functions and not one takes a target, a
goal or a set point.

What makes a world self-regulating is a loop, not a controller:

    interior outgasses CO2   ->  greenhouse warms the surface
    warmer surface           ->  more rain, faster silicate weathering
    faster weathering        ->  CO2 buried as carbonate
    less CO2                 ->  cooler surface

**Derived, not looked up.** Stefan-Boltzmann is `2π⁵k⁴/15h³c²`, agreeing
with the published value to one part in 10⁹, built from three constants
that are exact by definition. The gas constant is `k·N_A`. The
temperature dependence of weathering is `R·T²/Ea` with Ea measured on
basalt in a beaker — 14.37 K per e-fold, where the climate literature
quotes 13.7. None of those came from a climate table.

**Earth's own existence fixes the water-vapour physics.** The first
version reused CO2's optical-depth exponent (1.185, superlinear) for
water and Earth came out *unstable* at 288 K — a tipping point, not a
home. The clash was in the rule: absorption growing faster than absorber
is a runaway with no brake. So the exponent was derived instead from an
observation that is not a temperature — Earth has stayed liquid for four
billion years, and a state that persists is a stable one. Setting the
feedback gain to 1 gives the largest exponent Earth could have and still
be here:

    n_marginal = 0.5387   ->  absorption MUST saturate

That conclusion comes out of the planet still being here, not out of a
spectroscopy table. At n = 1/2 the gain is 0.928: stable, and close to
the edge.

**Results that were not fitted.** Venus, Earth and Mars were spent on the
three parameters and are calibration, not prediction. What is left:

    Mercury   437.2 K vs 440 observed   +2.8 K   airless, so no greenhouse
    Titan      84.7 K vs  94 observed   -9.3 K   too cold, and names methane
    inner edge of the habitable zone at 0.999 AU, where the oceans go to
      vapour, rain stops, the sink closes and CO2 accumulates unopposed
    faint young Sun: at 0.7 L_sun Earth with today's CO2 sits at 237 K,
      frozen solid. Let the loop run and CO2 climbs to 1.06 bar and the
      surface is liquid again — the paradox answered by the feedback

**Earth has two stable states.** Same sunlight, same equations: 288 K and
798 K, with an unstable ridge at 298 K between them. Which one a planet
occupies is history, not physics, so `states()` returns the set. A model
that returns one number there is picking a branch and calling it a fact.

**Four wrong versions, all kept as checks.** Iterating from the bare-rock
temperature found 257 K for Earth and called it the answer — a real fixed
point, just not Earth's. Giving every body 70% humidity returned infinity
for Venus and Mercury, which is the model correctly saying a planet with
unlimited water at 440 K has no temperature; water became an inventory.
Bisecting the carbon balance declared Earth a runaway, because the curve
crosses zero twice — frozen and boiled both stop the rain — and a method
assuming one crossing sees neither. And `ocean_column` looked the ocean up
by `body.name`, so every habitable-zone probe was bone dry and every
distance ran away; `water_is_a_property_not_a_name` is the regression.

**Weathering is integrated over latitude, not switched.** The hard
freezing cutoff parked every planet past 1 AU at exactly 273.0 K — the
thermostat drove the mean onto the switch and sat there. A world averaging
260 K still has a warm equator and it still rains there. With the bands
integrated, Earth reports 82% of its surface above freezing, which is
right, and which the switch was hiding.

**A third kind of error bar.** `engine/scales.py` now holds three:

    nuclear            MeV   residual against measurement, many nuclides
    planetary-climate  K     residual against measurement, TWO bodies
    protein-fold       rate  against another model; nothing was measured

6.9 K over Mercury and Titan is a residual in kelvin like the nuclear
bars, over a sample far too small to behave like one. Reporting it
without saying so would be the most misleading of the three.

**Stated limits.** The grey slab has no Rayleigh scattering and no CO2
condensation, so thick atmospheres are over-warmed and the outer edge runs
past 2.8 AU where real models stop near 1.7. And it puts Earth 0.1% inside
the runaway threshold, which is too tight — the gain of 0.928 is the grey
model exaggerating water feedback. Both are left standing rather than
tuned away.

    engine/terraform.py  13/13     engine/scales.py    6/6
    eval/audit.py        21/21     eval/heldout.py   165/165 byte-exact
    eval/benchmark.py    ALL PASS  5,737 correct, 0 wrong

### 3.1.20 — a correction: Mercury was never a held-out success

3.1.19 reported Mercury at **+2.8 K** as a free win — a body with no
atmosphere showing no greenhouse. That result does not hold and is
withdrawn.

The equilibrium temperature's factor of 4 comes from a sphere
intercepting `πr²` and radiating from `4πr²`. That is only right if the
absorbed heat is **spread over the whole sphere**, which needs an
atmosphere to carry it or rotation fast enough that no face stays lit.
Mercury has neither. Its quoted 440 K is the **dayside** mean; the global
mean is nearer 340 K. A model assuming full redistribution was being
scored against a number assuming none, and the two happened to land 3 K
apart. Against the right quantity the same model is about **+97 K** out.

The tell was the Moon. Every airless body came out too cold — Io −14.8 K,
Callisto −19.3 K, Europa −9.5 K — except the Moon, which came out
**+18.3 K too hot**. A greenhouse that is missing makes you too cold, never
too hot, so the asymmetry meant the formula was being misapplied rather
than the physics being incomplete.

**So the criterion is derived and the body is refused when it fails.**
Compare how long the surface takes to radiate its heat away against how
long the planet takes to turn:

    Titan     573      well mixed
    Earth      32.2    well mixed
    Venus      18.8    well mixed
    Mars        0.92   MARGINAL -- the largest day-night swing here, ~60 K
    Mercury     1.4e-15  refused: it does not have one temperature

Six orders of magnitude separate Mars from Mercury, so where the line
falls between them is not a sensitive choice. A body below it does not
*have* a mean temperature — any single number quoted for it is a choice
of which average, and scoring against it compares two different
quantities.

**The bar gets worse and more honest.** Venus, Earth and Mars were spent
on the three parameters. Every airless body is now refused. That leaves
the solar system with **one** usable test:

    planetary-climate bar   9.3 K, over a sample of ONE (Titan)

Which is the strongest possible argument for what comes next. There are
no more test points to be had here, so validation has to stop being
"does it match our planets" and become **"does our solar system fall out
of the space of internally consistent worlds."**

### 3.1.21 — optical depth from molecules, with no planet consulted

`engine/terraform.py` solved its absorption law *from* Venus and Mars and
then used it to talk about Venus and Mars. That is circular, and a law
read off three planets cannot be evidence about planets. `engine/radiative.py`
replaces it with radiative transfer over laboratory band data — strengths,
line widths, line spacings, all measured on gas in a cell.
`no_planet_appears_in_this_file` parses the imports to enforce it.

**The square-root exponent is now a consequence, not a choice.** 3.1.19
picked n = 1/2 inside a bound derived from Earth still existing. Here it
falls out of the shape of a collision-broadened line: the wings of a
Lorentz profile drop as an inverse square, so once the line centre is
black, further gas widens the opaque core as the square root of the
column. Earth is not mentioned.

**And pressure broadening appears, which the fitted law could not see.**
Collisions set the line width, so absorption goes as `sqrt(column ×
pressure)`, not as a pure power of column. The same column absorbs 10×
more at 1 bar than at 10 mbar. A fit to column alone buries that in the
exponent and is then right only where it was fitted.

**Two wrong versions, both kept.** The first averaged optical depths
weighted by spectral coverage and gave Earth τ = 230 and a surface of
**922 K**. That is a category error, not an approximation: a band opaque
across a quarter of the spectrum does not make the sky a quarter of
infinitely opaque — it blocks that quarter, and the rest leaves through
the window untouched. Bands now combine in transmittance and convert
back at the end. The second was the check itself: two versions of
`no_planet_appears_in_this_file` failed by grepping their own source and
matching the strings they contained. It parses the AST now.

**The unfitted result, with nothing told to it:**

    body    T_eq    tau   predicted  observed    error
    Earth   254.0  0.435    272.6      288       -15.4 K
    Mars    209.8  0.307    221.0      210       +11.0 K
    Titan    84.7  0.000     84.7       94        -9.3 K
    Venus   226.7  0.067    229.5      737      -507.5 K

Earth recovers 19 K of its 34 K greenhouse from molecular constants alone.
Mars lands 11 K high. Both are honest numbers in a way the fitted version's
exact agreement never was.

**Venus is the finding.** Missing by 507 K is not noise, and the model says
exactly why: CO₂'s 15 µm band covers **26%** of what a 288 K surface
radiates, so raising CO₂ by *ten orders of magnitude* moves τ by 0.0000.
One gas cannot close a sky it does not reach. Venus is real, so the rules
here are incomplete in a specific, named way — collision-induced continuum
absorption in the window, and sulfuric-acid cloud scattering. The model did
not fudge its way to Venus; it reported that Venus is impossible under the
rules it has been given, which is the correct response and tells us which
rule to add next.

    engine/radiative.py  7/7     engine/terraform.py  14/14
    eval/audit.py       21/21    eval/heldout.py     165/165 byte-exact

### 3.1.22 — a lab: small controlled experiments, one rung at a time

A benchmark says PASS or FAIL. That is not enough to build physics with,
because there are three ways to be wrong and they need different work.
`engine/lab.py` separates them:

    HOLDS         the rule does what it claims, in isolation
    MISSING_RULE  self-consistent but INSUFFICIENT -- something real
                  happens that these rules forbid
    CLASH         two rules, each fine alone, contradict each other
    REFUSED       cannot be run with what is here, and says what it needs

Only the first is a pass. Lumping the other three together as "fail"
throws away the only information that says what to do next.

**Why layers.** A wrong surface temperature could be bad radiative
transfer, bad thermodynamics, or a bad constant, and from the top there
is no way to tell. So each experiment declares its rung, the rungs run in
order, and a layer whose foundation is unsound is not run at all:

    0 constants   1 molecule   2 column   3 atmosphere
    4 balance     5 feedback   6 world

12 experiments, 11 HOLD, **1 MISSING_RULE**, 0 CLASH.

**How a missing rule is found — not by comparing to an example.** It
shows up when a *derived limit* and a *real thing* cannot both be true.
The rules say unbounded CO₂ can multiply a bare-rock temperature by at
most **1.012**. Venus requires **3.251**. Neither statement is an example
being fitted to: one is a consequence of the rules, the other is that
Venus exists. The contradiction is the discovery, and it names what is
absent — collision-induced continuum absorption, which two CO₂ molecules
produce during a collision and which no single-molecule band table can
contain, plus cloud scattering.

**And isolating it found a second mechanism.** A controlled experiment at
layer 3 asked only whether a gas stays as useful as its planet heats up:

    CO2's 15 micron band covers  26.1% of a 288 K body's emission
                                  6.5% of a 737 K body's emission

A hotter body emits at shorter wavelengths, so the band **slides off the
Planck peak**. CO₂ gets weaker exactly where it would need to be
stronger — a brake built into Planck's law, and most of why the ceiling
is so low. It also means CO₂ sits almost exactly on the peak of a *cold*
planet, which is why a trace of it matters so much here and so little on
Venus. That was not visible from the top; it took an experiment with
nothing else varying.

    engine/lab.py  5/5 checks, 12 experiments over 7 rungs

### 3.1.23 — the lab as method: four missing rules and one clash

**Labs are part of this research, not scaffolding for it.** `engine/lab.py`
is meant to be picked apart. Every experiment declares its rung, states
the question it asks in one line, varies one thing, and returns a verdict
with its reasoning attached. `python3 -m engine.lab` prints all of them.
Five meta-checks verify the lab itself: that every experiment is placed on
a rung, that rungs run in order, that the four verdicts are distinguished,
that the known missing rule is still detected, and that **no experiment
takes an observed temperature as a target**.

That last one is the discipline. Where a real body appears, it appears as
an *existence claim* — Venus is this hot — which a derived ceiling can
contradict. That contradiction is a discovery. Fitting to it would not be.

**Being wrong is the most useful outcome available.** A wrong answer is
fixable with a rule, and a rule is permanent. The more rules there are the
more chances they have to contradict each other, and a contradiction
between two derived rules is *information about which one isn't a law of
nature*. That is why CLASH is a first-class verdict here and not a bug
report. The aim is not to get the right number; it is to run out of
contradictions.

**What one evening of this produced.** The layer-3 ceiling refused to
clear, and each fix exposed the next absence:

    1  CONTINUUM ABSORPTION.  A lone CO2 molecule is symmetric and has
       no dipole. Two colliding briefly do. It is a two-body process so
       it goes as density SQUARED -- which is why it is nothing at one
       bar and everything at ninety, with nobody deciding when it
       switches on. Doubling density multiplies it by 4.000.

    2  THE BAND TABLE WAS A WRONG MOLECULE.  One band per species. A
       737 K body radiates 60% of its energy between 1500-4000 cm-1,
       where CO2's nu3 stretch at 2349 -- its strongest, ten times the
       bend -- was simply absent. Found by tracing a layer-3 symptom
       down to layer 1.

    3  BANDS WIDEN, THEY DO NOT ONLY SATURATE.  A Lorentz wing absorbs
       as gamma/dnu^2, so with enough gas even a far wing goes black,
       and the opaque width grows as sqrt(column x pressure). This is
       how a window closes: no new substance, the same inverse-square
       wing asked a different question.

    4  AND THE WING HAS AN END.  Unbounded, rule 3 claimed Venus'
       15 micron band blacks out 315,694 cm-1 -- 79x the whole thermal
       infrared. The impact approximation behind the Lorentz profile
       treats collisions as instantaneous; they are not, and past
       dnu_c = 1/(2 pi c tau_collision) real wings fall faster.

**And rules 3 and 4 clash, which is the honest finding.**

    Lorentz wings, unbounded  ->  315,694 cm-1 opaque. Impossible.
                                  Venus -278 K, Earth +9.8 K
    Collision cutoff, 9.6 cm-1 -> no widening at all.
                                  Venus -496 K, Earth  -3.2 K

Both are derived. Neither is fitted. They disagree by four orders of
magnitude, and the truth is between them — so *diameter over mean speed*
is too crude a derivation for where a line profile ends. This is not a
number to tune. It is a statement that a rule is not yet known, and until
it is, no CO₂-rich world can be trusted. The conservative branch ships:
Earth right, Venus openly wrong. A CLASH is allowed to stand, but the lab
requires it to be named.

**Where the unfitted model stands.** Nothing in `engine/radiative.py`
reads a planet; the import list is parsed to enforce it.

    Earth    -3.2 K       from lab molecular constants alone
    Titan    -8.9 K       missing haze
    Mars    +12.5 K
    Venus  -495.6 K       blocked on the clash above

Earth's 34 K greenhouse reproduced to 3 K with no planetary input is the
result. Venus missing by 496 K is the *other* result, and it points at a
specific unknown rather than asking for a coefficient.

**Coming in Atlas 3.3:** the summary graph will show what each of Atlas 1,
2, 3, 3.1 and 3.2 does, alongside the fixes deferred there.

    engine/lab.py  5/5 meta-checks; 13 experiments, 11 HOLDS,
                   1 CLASH, 1 MISSING_RULE, both named

### 3.1.24 — never patch: one home per constant, enforced

**The rule.** A failure is the most useful thing this project produces,
because a failure converts into a rule and a rule is permanent. A patch
converts a failure into silence. So nothing here is fixed by adjusting a
value; it is fixed by changing a rule, or it is left standing and named.

The first sweep of *all* rules — not just the climate ones — went looking
for physical constants defined in more than one module. It found four
quantities carrying two or three independent definitions:

    atomic mass unit   AMU (terraform)       U_KG (cosmoschunks, halflife)
    Newton's constant  G_GRAV (terraform)    G_NEWTON (remnants)
    solar mass         M_SUN (remnants)      M_SUN_KG (cosmoschunks, halflife)
    alpha binding      B_ALPHA (transitions) B_ALPHA_MEV (nucleo)

**Every one of them agreed, which is what made it worth fixing.** Nothing
enforced the agreement — it held because whoever typed the second copy was
careful. One later edit and two modules would have quietly disagreed about
the mass of the Sun, and every answer would still have looked reasonable.
This is precisely a rule that looks right and isn't.

Setting the copies equal would be a patch: it fixes today's values and
leaves the mechanism intact. The fix is `engine/constants.py` — one home,
every module imports, and a lab experiment at layer 0 fails if a second
definition appears anywhere, under its own name or any historical alias.
**A duplicate cannot drift if a duplicate cannot exist.**

**And the sweep forced a second distinction.** Constants are now marked
EXACT or MEASURED, and a layer-0 experiment fails if a measured one is
presented as exact. Six are exact by definition — they *define* the
kilogram, metre, kelvin, mole, ampere and the astronomical unit, so they
have no uncertainty and never will. Six are measured. G is the worst-known
constant in physics at ~22 parts per million, five orders of magnitude
worse than anything defining an SI unit, and every escape velocity and
scale height in the repo inherits that. Nothing may hide it.

Derived quantities are deliberately **not** stored. Stefan-Boltzmann is
absent from the constants file because it is `2π⁵k⁴/15h³c²` — a number that
can be computed has no business having a second home to go stale in.

    engine/constants.py  3/3     lab: 15 experiments, 13 HOLDS,
    5,737 correct, 0 wrong       1 CLASH, 1 MISSING_RULE, both named
    audit 21/21                  heldout 165/165 byte-exact

**Toward 3.2: lab every rule.** This sweep covered constants. The same
treatment is owed to unit consistency, to dimensional agreement across
module boundaries, and to every place two modules compute a quantity that
ought to match. The expectation is that it uproots things that currently
look right.

### 3.1.25 — stress-testing every rule, not just the new ones

The constants sweep was one pass over one kind of rule. This is the
start of the full stress test, and it found the "never patch" principle
being violated by code already in the repo.

**A silent fallback is a patch with a number on it.** `transitions.bar_for`
selected the error bar for a decay mode, and ended:

    except Exception:
        return SEMF_TYPED        # 3.0 MeV, typed

Any failure at all — a bad import, a renamed kind, a mode that was not a
string — was swallowed, and a **typed 3.0 MeV was substituted for a
measured 1.21**. The answer still looked like a number. That is the whole
problem: a wrong bar makes decays look resolvable or unresolvable and
nothing says why. Two of these existed. Both are gone; a bar that cannot
be measured is now a failure and is allowed to be one.

**How it was found: probe every rule with inputs it should refuse.** A
sweep of every single-argument function in the engine against zero,
negative, huge, tiny and NaN found **eight** that returned a number where
they should have refused. `bar_for(-1)` returned 3.0 — calling
`.startswith` on an integer raised, the bare `except` ate it, and a bar
came back anyway.

**A second find, same shape as the constants.** `radiative.MU` held four
typed molar masses, and `CIA` held them again. The periodic table already
in the repo derives all of them. They agreed to three decimal places,
which is exactly how a typed table survives long enough to go wrong.
`MU` is now computed from `engine/experts.py`'s table, and the duplicates
in `CIA` are deleted.

**Both are now rules, at layer 0, so they cannot come back:**

    no_silent_fallback_on_a_bar    scans every module for an exception
                                   handler that substitutes a bar value
    degenerate_inputs_are_refused  the bar selectors must refuse a
                                   non-string mode, an unknown mode and
                                   an unknown kind

    lab   17 experiments, 15 HOLDS, 1 CLASH, 1 MISSING_RULE
    5,737 correct, 0 wrong    audit 21/21    heldout 165/165 byte-exact

**Still owed before 3.2.** Dimensional agreement across module
boundaries; every place two modules compute a quantity that ought to
match; monotonicity of each rule in its own arguments; and the
convective-adjustment rule that the missing-rule analysis points to.

### 3.1.26 — using every rule at once

Everything so far tested rules **in isolation**, which is what a lab is
for. But a rule can be individually correct and still contradict another
one the moment both apply. Layer 7 of the lab holds the constraints that
do not exist inside any single module.

**One atom, straight up the ladder, eight rules in sequence:**

    periodic table   C = 12.011 u
    nucleo SEMF      C-12 at 7.468 MeV per nucleon
    transitions      stable
    valence          4, from shell filling
    abundance        2.36e-03 by mass
    provenance       formed in stellar carbon burning
    radiative        CO2 at 44.009 g/mol, 4 infrared bands
    folding          glycine C:polar 0.667

No contradiction anywhere along it.

**Two modules disagree by 0.092%, and they are both right.** The table
gives carbon 12.011 u; carbon-12 is 12.0 exactly. `engine/radiative.py`
builds CO₂ from the bulk average because it weighs a *gas*, a mixture of
isotopes. `engine/nucleo.py` uses per-nuclide masses because it binds a
*nucleus*, one isotope. A rule that forced them to agree would be wrong —
and an earlier version of this repo measured binding against atomic
weights and produced an 80 MeV artefact doing exactly that. The
difference is now a check, so it has to survive.

**Two derivations meet that were never arranged to.** Valence from aufbau
shell occupancy gives C 4, N 3, O 2, H 1, S 2. The residue and molecule
formulas, counted atom by atom from real compounds, need exactly those.
Those come from opposite directions and nothing connects them.

**And nothing is built from an element that does not exist.** Six
elements are used across the IR molecules, every amino-acid residue and
the CHNOPS life gate; all are in the naturally-occurring set and none is
among the eight `engine/abundance.py` derives as absent. A molecule made
of technetium would be chemistry with no supply chain.

**The layer count found its own bug.** `run()` defaulted to `up_to=6`.
Adding layer 7 meant four composition experiments ran, passed, and were
never reported — a bound written as a literal instead of as the thing it
bounds goes stale the first time the thing changes. It now reads
`max(LAYERS)`.

    lab   21 experiments over 8 rungs: 19 HOLDS, 1 CLASH, 1 MISSING_RULE

### 3.1.27 — shell corrections, and a right answer for the wrong reason

**The magic numbers are derived, not typed.** A list of 2, 8, 20, 28, 50,
82, 126 would be exactly the kind of table this project keeps removing.
`engine/shells.py` gets them from a potential instead:

    E / hbar omega = (N + 3/2) - kappa[ 2 l.s + mu( l^2 - <l^2>_N ) ]

A harmonic oscillator alone gives 2, 8, 20, 40, 70, 112 — the first three
right and then wrong for ever. Spin-orbit coupling pulls the aligned
`j = l+1/2` orbital down far enough to join the shell below, and the l²
term accounts for a real nucleus flattening towards its surface. **Only
4.2% of the (κ, μ) plane reproduces all seven closures** — 51 of 1,209
grid points, κ in 0.028–0.045 and μ in 0.28–0.75, which is where the
Nilsson model's own values sit. Seven integers pinning two continuous
parameters into 4% of a plane.

It also predicts **40**, which was not in the target list and is real —
the N=40 sub-shell closure shows in zirconium-90 and calcium-48. A
derivation that produced only what it was aimed at would be weaker.

**Then the shell corrections exposed something much worse.** Every alpha
Q-value in the repository was built as

    Q = B_semf(daughter) + B_MEASURED(helium-4) - B_semf(parent)

taking one of three terms from a different source. The SEMF gives
helium-4 22.841 MeV; the measured value is 28.296. **Every alpha channel
carried a +5.455 MeV bias — 4.5× its own error bar.**

And it breaks precisely the argument 3.1.16 rests on. A Q-value is a
*difference*, and its bar is 1.21 MeV instead of the 4.76 MeV absolute
mass error **only because the formula's errors cancel between the two
sides**. Take one term from elsewhere and the cancellation is gone, so
the bar no longer describes the quantity it is applied to.

**That bias was doing real work.** The SEMF under-predicts heavy alpha
Q-values by 5–11 MeV, and the borrowed helium supplied most of it. Two
errors in opposite directions, partly cancelling:

    as shipped (mixed sources)         8 right, 3 WRONG, 3 refused
    consistent sources                 4 right, 3 WRONG, 7 refused
    consistent + derived shells        4 right, 2 WRONG, 8 refused

Four of the eight "right" answers were right for the wrong reason and
are now correctly refused as unresolvable. **Wrong went from 3 to 2** —
polonium-212 stopped being called stable, because its daughter lead-208
sits on a double closure a smooth formula cannot see. Wrong is the number
that must reach zero, and it fell.

**The uranium series is withdrawn a third time.** 3.1.15 withdrew it on
the wrong bar. 3.1.16 withdrew that withdrawal, correctly. Both were
right. Now U-238's alpha Q comes out **−0.024 MeV against a measured
+4.27**, the channel never opens, and the chain walks into beta decays
that do not happen. The earlier reasoning survives intact; what changed
is that the derivation rested on an inconsistency rather than on the bar.
The gap is named: the liquid drop is ~4.3 MeV short on that step even
with shells.

**Restoring the mixed source would have kept the score.** That is the
definition of a patch — keeping a broken mechanism because it produces
right answers — and it is why the score is allowed to fall.

    engine/shells.py 6/6   lab 22 experiments   5,737 correct, 0 wrong
    audit 21/21            heldout 165/165 byte-exact

### 3.1.28 — filling the liquid-drop gap: a domain, not a number

The gap was 5–11 MeV on heavy alpha steps. It turned out to be **one
nucleus**, not a trend. Alpha Q is `B(daughter) + B(helium-4) −
B(parent)`, and the SEMF gives helium-4 22.841 MeV against a measured
28.296. Parent and daughter differ by four nucleons so their per-nucleon
errors largely cancel; helium's cancels against nothing and lands in
**every** alpha channel.

**The obvious guess was a missing curvature term, and it is wrong.** The
Weizsäcker expansion runs volume ~A, surface ~A^(2/3), curvature ~A^(1/3),
and the formula stops after two. If the residual were the truncated third
term it would scale as A^(-2/3) per nucleon and the ratio would be
constant. Measured across the fixture it runs **−3.44 at A=4 to +2.10 at
A=238 and changes sign** — light nuclei under-bound, heavy ones
over-bound. One term cannot do both, so the hypothesis is discarded
rather than fitted.

**What is true is that the formula has a domain, and it says so itself.**
Rather than assert a floor, compare the formula against its own measured
4.763 MeV mass bar:

    A = 4    off by 5.46 MeV   OUTSIDE its own bar
    A = 12   off by 6.95 MeV   OUTSIDE its own bar
    A = 16   off by 1.65 MeV   inside
    A >= 13  inside, everywhere in the fixture

Both nuclei that break it are alpha-clustered — helium-4 is one alpha,
carbon-12 behaves as three — which is quantum structure a fluid drop
cannot represent. The boundary is **derived from the formula's own error**,
not typed. This is the shape the request asked for: a rule, not a number.

**The consequence is severe and is stated rather than hidden.** Every
alpha Q-value needs helium-4, helium-4 is outside the domain, so **alpha
decay cannot be derived here at all**.

    mixed sources (3.1.26)        8 right, 3 WRONG,  3 refused
    consistent + shells (3.1.27)  4 right, 2 WRONG,  8 refused
    + derived domain (3.1.28)     1 right, 1 WRONG, 12 refused

Wrong is the number that must reach zero and it is now **1** — K-40, a
beta case. One right out of fourteen is the price, and it is the correct
price: the other thirteen are things this formula cannot resolve.

**Refusing a channel is not the same as closing it, and getting that
wrong put the count back up.** When alpha went dark, polonium-212 came
back "stable" — no computable channel raises its binding — which asserts
the alpha channel is *shut*, the one thing not known about it. The same
error made `halflife` report radium, radon, polonium and astatine as
**absent**, when every chain that feeds them is an alpha series and they
are demonstrably here. Unreachable by a walk that cannot walk is not
absent. Both now return undetermined.

**A recurring bug, now a rule.** Three checks have failed by grepping
their own source and matching text they themselves contain — two in
`engine/radiative.py`, one in the lab experiment testing for the very
string its comment explained. `checks_do_not_grep_themselves` forbids it:
test the arithmetic, or parse the AST.

**Still owed:** 12 module-level constants have no derivation or
provenance beside them, including `RH_EARTH = 0.7`, `D_CONTRAST = 45.0`,
`M_REF = 18.0` and `SEMF_TYPED = 3.0`.

    lab 23 experiments, 21 HOLDS, 1 CLASH, 1 MISSING_RULE
    5,737 correct, 0 wrong   audit 21/21   heldout 165/165 byte-exact

### 3.1.29 — a bar belongs to a manifestation, and that is now a rule

3.1.18 established that a bar belongs to a **domain** — MeV for nuclei,
a survival rate for folding, kelvin for climate — and that they must
never be compared. 3.1.16 established that it belongs to a **question** —
mass, alpha and beta are three different numbers. This is the third and
last piece: it belongs to a **manifestation**, the state the thing is
actually in. And it is a rule now, not a convention.

Measured on the fixture, after shell corrections:

    inside the liquid drop's domain    rms 1.850 MeV   (n=15)
    outside it                         rms 6.249 MeV   (n=2)
    mixed together, as shipped               4.763 MeV

**A factor of 3.4, and the shipped bar is neither of them** — too loose
where the formula works, far too tight where it does not. Every refusal
judged against 4.763 MeV inside the domain was refusing things the
formula could resolve.

So `engine/scales.py` now **refuses to hand out a bar** for a domain with
more than one state until it is told which:

    scales.bar_of("nuclear-mass")                -> ValueError
    scales.bar_of("nuclear-mass", "in-domain")   -> 1.850 MeV

Asking for "the bar" is not a well-formed question where states exist.

**A second result, and it is the encouraging one.** Closed-shell against
mid-shell now measures **0.98** — no difference at all. Before shell
corrections that split was 3.6 to 1. Adding the rule *absorbed* the
manifestation. **A manifestation stops mattering once the rule that
explains it exists**, which is how you know the rule was the right one
rather than a curve through the points.

**The last typed bar is gone.** `SEMF_TYPED = 3.0` came from the
literature with no derivation beside it. Its only users were two silent
fallbacks removed in 3.1.25 and a message quoting it. A number kept for
reference is a number waiting to be used, and that one was.
`no_bar_is_typed` forbids the category.

**And that rule found something by being wrong.** It flagged
`HBAR = 1.054571817e-34` in `engine/remnants.py` — a false positive,
since ħ is not an error bar, my pattern just matched the letters. But ħ
is h/2π: a **derivable quantity with a second home**, the same defect as
the four duplicated constants in 3.1.24. It is now computed in
`engine/constants.py` and imported. The pattern matches whole words now.

    lab 25 experiments, 23 HOLDS, 1 CLASH, 1 MISSING_RULE
    5,737 correct, 0 wrong   audit 21/21   heldout 165/165 byte-exact

### 3.1.30 — all rules at once, then one at a time

A lab tests a rule in isolation, which is how you learn whether the rule
is sound. It cannot tell you which rule is responsible when everything is
switched on and the answer is still wrong — and by then the rules
interact, so reading the code will not tell you either.

`engine/ablate.py` makes the procedure a mechanism:

    1  run with every rule on. If it passes, stop.
    2  if it fails, run again with each rule removed in turn.
    3  a rule whose REMOVAL changes the outcome is implicated.
    4  a rule whose removal changes nothing is not the problem,
       however plausible it looked.
    5  what is left is a specific failure with a specific owner,
       and that is what a narrower rule gets written for.

**Run on the decay target it immediately reversed a conclusion.**

> **SUPERSEDED — the numbers in this section are history.** 3.1.31
> changed the rule being measured and the same command now prints
> 8 right, 0 wrong, 6 refused. The table below was correct when
> written and describes a system that no longer exists. Registered in
> `eval/claims.py` so it cannot be mistaken for a current result.

    all rules on                          1 right, 1 WRONG, 12 refused
    without shell-corrections             1 right, 1 WRONG, 12 refused
    without liquid-drop-domain            4 right, 2 WRONG,  8 refused
    without one-source-per-Q              1 right, 1 WRONG, 12 refused

Read alone, that says the domain rule is the whole story and the other
two do nothing — that shell corrections and the helium-4 consistency
fix, both of which cost real work, are irrelevant.

**That reading is wrong, and pairs show why.**

    without shell-corrections + domain            4 right, 3 WRONG,  7 refused
    without domain + one-source-per-Q             8 right, 2 WRONG,  4 refused

Both "inert" rules matter the moment the domain rule is lifted too. They
were not irrelevant; they were **downstream of a closed gate**. The
domain rule shuts the alpha channel entirely, so neither had any input
to act on. A rule behind a closed gate looks irrelevant however
important it is, and single ablation reports it as not implicated.

**This also reproduces the 3.1.27 finding mechanically.** Lifting the
domain *and* the source consistency gives 8 right — the old headline
number — because the +5.455 MeV helium bias returns and cancels the
liquid drop's deficit on heavy alpha steps. Two errors, one good-looking
answer. Ablation separates them by construction: remove one and the
other appears.

**And it answers the question asked of 3.1.29 directly.** The
manifestation rule did not resolve the decay scoring, and the ablation
says why in one line: the 12 refusals belong entirely to
`liquid-drop-domain`. Tightening a bar cannot help a channel that cannot
be computed at all. Three hypotheses have now been rejected this way —
a curvature term, a tighter mass bar, a climate manifestation split —
and each cost work that an ablation would have saved.

    engine/ablate.py 4/4   lab 26 experiments, 23 HOLDS, 1 CLASH,
                           1 MISSING_RULE, 1 REFUSED

### 3.1.31 — one source per Q-value, and measurement is a source

The ablation named a single owner for the whole decay loss:
`liquid-drop-domain`, and behind it helium-4. This is the narrower rule
it asked for.

**3.1.27's rule was right and its implementation was one case of it.**
"Every term in a Q-value from the same source" got built as "always use
the formula". That is *a* way to satisfy it, not the only one — and it
cost everything, because helium-4 is below the formula's domain, so
alpha became underivable and twelve of fourteen fates went to refused.

Measured binding energies are a source too. Where every term is
measured, the difference is consistent and the cancellation the small
bar depends on never has to happen. Only a **mixture** was ever the
problem.

    MEASURED  arithmetic on measured binding energies. Correct, and
              not a derivation -- it asserts nothing the data did not
              already contain.
    FORMULA   the liquid drop inside its domain. A derivation, and it
              carries the formula's bar.

**The result is the baseline, reached honestly:**

    3.1.26  mixed sources        8 right, 3 WRONG,  3 refused
    3.1.28  formula only         1 right, 1 WRONG, 12 refused
    3.1.31  one source, either   8 right, 0 WRONG,  6 refused

Eight right is the old headline number. **Zero wrong is new** — the
number this project says must reach zero, and it has. The old eight
included three wrong answers and rested on a +5.455 MeV bias cancelling
a 5–11 MeV deficit; these eight rest on consistent arithmetic, and each
of the six refusals has a named cause.

**The bar follows the source, which is another manifestation.** A
Q-value read off measured binding carries the table's precision; one
from the liquid drop carries 1.21 MeV. Applying the formula's bar to a
measured difference would refuse decays known to a tenth of an MeV.

**Tritium is refused, and that is correct.** Its beta Q is 18.6 keV,
below the table's own precision. The model declining to call it is the
right answer, not a gap.

**A third duplicated table.** `BINDING_FIXTURE` held 17 measured binding
energies and `BETA_B` held 10 more of the same quantity, overlapping in
one entry that agreed — the same defect as the four duplicated constants
in 3.1.24 and ħ in 3.1.29. One table now, 29 nuclides, with the three
alpha daughters the chains needed. They reproduce measured alpha
Q-values to within 0.08 MeV, and the check is real rather than circular:
two of the five pairs use only entries that were already there.

**And the typed-bar rule caught its own author.** `MEASURED_Q_BAR = 0.10`
was typed by hand an hour after `no_bar_is_typed` was written to forbid
exactly that. It is now derived from how precisely the table is
quoted — each entry's rounding half-width, three of them in quadrature —
which gives **0.0866 MeV**, and nothing is chosen.

    5,737 correct, 0 wrong   audit 21/21   heldout 165/165 byte-exact
    lab 26 experiments: 23 HOLDS, 1 CLASH, 1 MISSING_RULE, 1 REFUSED

### 3.1.32 — every published number, recomputed

A number written into this README is a claim the repository is still
making. Nothing here was checking them: the benchmark checks the code
against itself, the audit checks it against its own invariants, and
neither reads the document.

**It had already gone wrong once.** 3.1.30 published an ablation table
reading 1 right, 1 wrong, 12 refused. 3.1.31 changed the rule being
measured, and the same command now prints 8, 0, 6. The table was correct
when written and is false as a present-tense claim, and only a reader who
ran the code would have known.

`eval/claims.py` registers each load-bearing published number with the
computation that produced it:

    3.1.31  decay score 8 right, 0 wrong, 6 refused          ok
    3.1.27  magic numbers 2,8,20,28,40,50,82,126             ok
    3.1.27  4.2% of the (kappa, mu) plane                    ok
    3.1.21  Stefan-Boltzmann to 3.25e-11                     ok
    3.1.28  liquid drop refused below A=13                   ok
    3.1.29  mass bar 1.850 in domain, 6.249 outside          ok
    3.1.31  measured-Q precision 0.0866 MeV                  ok
    3.1.31  unified binding table, 29 nuclides               ok
    3.1.18  folding survival rate 0.573                      ok
    3.1.23  unfitted climate: Earth -3.2, Venus -495.6       ok
    3.1.31  lab 23 HOLDS / 1 CLASH / 1 MISSING / 1 REFUSED   ok

**Eleven of eleven still reproduce.** A claim that stops reproducing has
two honest repairs — correct the document, or mark the number as
superseded history. Leaving it is not one of them.

Three numbers are now recorded as **history rather than current**, each
saying what replaced it: 3.1.30's ablation table, 3.1.26's eight-right
(which rested on two cancelling errors), and 3.1.19's Mercury result. The
3.1.30 section carries an inline superseded notice so it cannot be read
as a live result.

**Full soundness sweep, everything at once:**

    engine modules        166/166 checks across 26 modules
    lab                   26 experiments: 23 HOLDS, 1 CLASH,
                          1 MISSING_RULE, 1 REFUSED
    published claims      11/11 reproduce
    curriculum            5,737 correct, 0 WRONG, 0 abstained
    held-out              165/165 byte-exact, 132 by an independent route
    wording               46 answers with several phrasings, 0 disagreeing
    audit                 21/21
    decay                 8 right, 0 WRONG, 6 refused

The two open items are unchanged and both are named: the far-wing
**CLASH** at layer 2, and the CO₂ ceiling **MISSING_RULE** at layer 3.
Neither is hidden and neither is patched.

### 3.1.33 — the clash and the missing rule, examined

Three hypotheses tested against the two open items before building any
of them. The ablation discipline from 3.1.30 paid for itself.

**1. Convection does not fix Venus.** The grey radiative profile is
never super-adiabatic at these optical depths — Venus at τ=21 has a
radiative lapse of 7.3 K/km against a 10.4 K/km adiabat, so convection
never triggers and the tropopause comes out at zero height. At the
shipped τ of 0.38 convection gives **227 K**, which is worse than doing
nothing. It only helps at τ≈21, which requires the wing branch of the
clash, so the two were never independent. Rejected before building.

**2. A `log(0)` guard had become a ceiling on physics.** Transmittance
was clamped at 1e-12 before taking a logarithm, which caps optical depth
at −ln(1e-12) = **27.6**. Venus needs **147.6**. No atmosphere this
module could describe was allowed to be as opaque as Venus actually is.
The floor is now the smallest positive float, putting the ceiling near
700, and a check keeps it clear of what any body needs. It was not
binding at the shipped cutoff — but it silently capped the
unbounded-wing branch, which is why scanning that branch saturated at
−278 K and looked like a physical result.

**3. Overlapping absorbers add optical depth; they do not average
transmittance.** This was a real modelling error. The old code summed
each band's Planck-weighted transmittance and renormalised when
coverage exceeded the spectrum — treating two absorbers in the same
place as alternatives rather than as both being in the way. A weak band
could dilute a strong one, and CO₂'s tiny 10 µm feature kept leaking
photons its enormous 15 µm and 4.3 µm bands had already stopped. Venus
saturating at τ=21.08 under ten-million-fold wing widening was not
physics; it was a weighted average unable to exceed its largest term.

Beer-Lambert is per wavenumber, so the model is now per wavenumber: bin
the spectrum, add every absorber's τ in each bin, transmit there, and
Planck-weight. Overlap is automatic and nothing is renormalised.

**And fixing it made Earth worse, which is the honest outcome.**

    before overlap fix   Earth -3.2 K   Venus -495.6 K
    after                Earth +12.3 K  Venus -495.6 K

Earth's water bands overlap heavily, so the old averaging under-counted
them — the −3.2 K agreement was partly the bug. Venus is unchanged
because at the shipped wing cutoff its bands are too narrow to overlap
at all. **Removing an error exposed another**, for the fourth time this
session.

**The claims checker earned itself one commit after being written.** It
flagged `3.1.23 unfitted climate: Earth -3.2 K` as no longer
reproducing, within minutes of the change. The old figure is now
recorded as superseded with the reason.

**Both open items stand, better understood.** The layer-2 CLASH and the
layer-3 MISSING_RULE are unresolved, and two of the three plausible
routes to them are now closed by measurement rather than opinion.

    radiative 10/10   lab 26 experiments   5,737 correct, 0 wrong
    published claims 11/11   audit 21/21   heldout 165/165

### 3.1.34 — thermodynamics existed as numbers, not rules

Asked directly whether this repository had thermodynamics, the audit
said almost none: Clausius-Clapeyron in `engine/terraform.py`, the word
entropy once in `engine/biomatter.py`. **Absent:** equipartition, the
second law, Carnot, Maxwell-Boltzmann, chemical potential, heat
capacity. And yet three heat capacities were typed into the climate code
and used to set lapse rates and radiative timescales.

`engine/thermo.py` derives them. A molecule carries kT/2 per reachable
quadratic degree of freedom; rotation is two for a linear molecule and
three otherwise, because spinning a linear molecule about its own axis
moves nothing.

**The vibrational part was already in the repository.** A mode is frozen
when its quantum exceeds the thermal energy and active when it does not,
smoothly, by the Einstein heat capacity — and every frequency needed is
a band centre in `engine/radiative.py`, measured on gas in a cell. So
**the heat capacity of CO₂ follows from the same spectroscopy that sets
its opacity**, and the two stop being independent inputs. That is what a
rule does and a number cannot.

    Ar    gamma 1.6667   five thirds, from counting alone
    N2    gamma 1.3998   seven fifths
    CO2   cp 833 J/kg/K against a typed 850

**And the typed value was wrong in a way that mattered.** CO₂'s cp runs
**735 J/kg/K at 200 K to 1167 at 800 K, a 59% change**. The climate code
used one number for Mars at 210 K and Venus at 737 K — the same gas
asserted to behave identically on two planets 500 K apart.

**The Sun's surface is derived, not measured.** A star's effective
temperature is not an independent observation: it is what its luminosity
and radius imply through Stefan-Boltzmann, itself derived from h, c and
k. **5772 K** comes out; nothing put it in.

**Is the distance from the Sun proper?** The semi-major axis is the right
length and the wrong average. A planet spends longer near aphelion but
flux goes as 1/r², so the time-averaged flux is `L/(4πa²√(1−e²))`. The
correction is **+2.4 K on Mercury, +0.23 K on Mars, +0.01 K on Earth** —
inside the 9.3 K planetary bar for every body that is scored. It is in
because it is right, not because it shows.

    thermo 5/5   terraform 14/14   5,737 correct, 0 wrong
    published claims 11/11   audit 21/21   heldout 165/165

### 3.1.35 — generated forward from a cloud, with our planets held out

**The seed is not the planets, and that is the whole design decision.**
It is tempting to "seed our solar system" by writing down Mercury
through Neptune and letting the rules act on them. That gives the answer
away: any later agreement restates the input. The rules must *generate*
planets, so the planets cannot be seeded.

What is seeded is the cloud they came from — **four numbers**:

    nebula mass        how much material collapsed
    metallicity        the fraction that is not hydrogen or helium
    angular momentum   how far the disk spreads
    a random draw      for what is genuinely stochastic

Everything after is derived: star mass from the collapse, luminosity
from mass, disk temperature from luminosity, where each substance can
condense, how much solid sits at each radius, what a body there can
sweep up. `the_seed_contains_no_planet` enforces it.

**The first derived structure is right, and nothing about any planet
was used to get it.** Water ice condenses below 170 K, which for the
Sun's luminosity is **2.68 AU**:

      ice line                             |                       2.68 AU
      actual       M       V   E     M     C     J     S      U   N
      generated   R      R     R     R   R    G    G     G   G    G
                0.3                                          35 AU

The asteroid belt runs 2.1–3.3 AU. Mars is at 1.52, Jupiter at 5.20.
The rock/ice boundary falls between them. Rocky bodies form inside it
and giants outside, and that ordering is a consequence of one
temperature profile.

**Nine of ten generated orbits land within 35% of a real body** — 0.99
AU against Earth, 1.53 against Mars, 5.55 against Jupiter, 9.29 against
Saturn. The spacing came from a seeded random walk, so that is partly
the draw. What is not the draw is which side of the ice line each one
falls on.

**The masses are wrong and the check says so.** Six of nine are out by
more than 3×, up to 489,000× in the asteroid belt. Isolation mass gives
what a body can sweep from its own feeding zone, and Mercury and Mars
are far *lighter* than that — a known open problem in planet formation,
not an arithmetic error here. **The structure derives and the masses do
not**, and `masses_are_wrong_and_say_so` fails if that ever quietly
starts passing.

**Why this replaces hand-written experiments.** The lab's 26 experiments
each construct a scenario I thought of in advance; the rules do not
compound, they are exercised one at a time in artificial isolation. A
generated system is one state that every rule acts on at once, so
interactions appear without being anticipated. This is the first piece:
cloud to planet. Planet to life is next, and the Sun's own evolution —
birth to red giant — moves the ice line across the system while it runs.

    genesis 6/6   5,737 correct, 0 wrong   published claims 11/11

### 3.1.36 — the system run forward in time

`engine/genesis.py` builds a system once, at one moment, which is not
how any of it happens. A star brightens across its main sequence, so
the distance at which water survives moves outward the whole time.
Checking a system at a single instant answers a question nobody asked.

**What drives it is derived.** Fusing four hydrogen into one helium
raises the core's mean molecular weight, so it must burn hotter to hold
itself up. Lifetime is fuel over burn rate, `t ~ M^-2.5`; luminosity
follows from the mass-luminosity relation already in `genesis.py`.

    t Gyr  L/Lsun  ice AU   inner edge
      0.0    0.71    2.27      0.84
      4.2    0.97    2.63      0.98        <- now
      9.4    1.73    3.52      1.31
     10.4    5.40    6.23      2.32   post main sequence
     12.5   81.43   24.19      9.01

**The faint young Sun appears unprompted** — 0.71 of present output at
formation, from fuel and burn rate alone. That is the reason the
carbonate thermostat in `engine/terraform.py` has to exist, arriving
here as a consequence rather than an input.

**Habitability turns out to be a *when*.** The band's inner edge sweeps
0.84 → 1.31 AU across the main sequence while nothing about the planets
changes. The generated world at 0.99 AU is inside it early and too hot
after about 5 Gyr — roughly a billion years from now, before the star
leaves the main sequence at all.

**The band edges were typed and should not have been.** An inner edge of
1.10 and outer of 0.36 in Earth-flux units were written straight in,
while `engine/terraform.py` already *derives* the inner edge by running
its thermostat outward until the oceans vapourise and the sink closes.
Two modules, one quantity, the newer typing what the older computes.
They are now measured once from the thermostat — **0.999 AU** — and
moved by `sqrt(L)`, which is exact because habitability follows flux.

**And the outer edge is refused, which found the next missing rule.**
The thermostat keeps water liquid past 12 AU, because it lets CO₂ pile
up without limit and the grey slab turns any optical depth into warmth.
A real atmosphere cannot: below about 195 K **carbon dioxide condenses**,
snowing out and capping its own greenhouse. That is what actually sets
an outer edge, and Clausius-Clapeyron for CO₂ is the same equation
already used for water here — so the rule is absent rather than hard.
Until it exists the outer edge is UNDETERMINED. Inventing a bound would
be a patch, and the check fails if an outer edge ever appears without
the rule.

    evolve 6/6   5,737 correct, 0 wrong   published claims 11/11

### 3.1.37 — CO₂ condenses, and the outer edge closes

3.1.36 refused to give an outer edge to the habitable zone: the
thermostat kept water liquid past 12 AU because it let CO₂ accumulate
without limit. The refusal named the missing rule, and this is it.

**A cold planet cannot hold unlimited CO₂ — it snows out.** Carbon
dioxide has a condensation curve like anything else, and it is the same
Clausius-Clapeyron already used for water, with CO₂'s own triple point
and latent heat of sublimation:

    at 150 K an atmosphere holds   0.011 bar of CO2
    at 195 K                       1.107 bar
    at 250 K                      33.490 bar

So the greenhouse caps **itself**. That is the maximum-greenhouse limit,
and it is what sets an outer edge.

**Derived result:**

    inner edge   0.999 AU   where rain stops and the CO2 sink closes
    outer edge   1.898 AU   where CO2 condenses out of the air

Published maximum-greenhouse estimates put the outer edge at **1.67–1.77
AU**. This lands within 8–14%, with nothing fitted — the curve comes from
CO₂'s measured triple point and latent heat, both laboratory quantities.

**And the first implementation was wrong in a way worth recording.** I
put the cap in its own iteration outside the temperature solve, nesting
two fixed points. The solver found a new family of roots and picked
*warmer* ones — **289 K at 12 AU against 258 K uncapped, a cap that
heated the planet.** An ablation caught it: comparing with and without
showed the cap making things hotter, which no condensation rule can do.
Moving it inside the one fixed point that already existed fixed it.

    2.0 AU   182 K, frozen        (was 259.7 K, 22% liquid)
    6.0 AU   104 K, frozen        (was 258.5 K, 13% liquid)

Earth is untouched at 288.0 K and 42.56 Pa — the cap is 165 bar there
and never binds.

**Three gaps became two.** The far-wing CLASH and the CO₂ ceiling
MISSING_RULE remain. This one closed because 3.1.36 refused to invent a
bound: a refusal that names what is absent is what makes the next rule
findable, and inventing an outer edge would have hidden it permanently.

    evolve 6/6   terraform 14/14   5,737 correct, 0 wrong
    published claims 12/12   audit 21/21

### 3.1.38 — a wing falls off, and the clash becomes a threshold

Both open items attacked. Neither closed, and both are now understood
well enough to say what would close them.

**A wing is not a wider box.** `opaque_width()` answers how far out a
band is still opaque, and the code used that as the edge of a
*rectangle*, giving the band-centre optical depth to every wavenumber
inside it. A band with τ of ten billion and a wing reaching 100,000 cm⁻¹
therefore had τ of ten billion everywhere across it. The whole content
of a wing is that it weakens with distance:

    tau(nu) = S u / pi * gamma / ((nu - nu0)^2 + gamma^2)

**I suspected double-counting and was wrong.** A band is hundreds of
lines, so treating its far wing as one Lorentz line carrying the whole
band strength looked like an overestimate. Measured against the explicit
sum over lines, the ratio is 0.82 at 300 cm⁻¹ and 1.00 by 3,000 — the
one-line form is right. The hypothesis cost a measurement and was
discarded.

**The correct shape makes agreement worse, and that is the honest
outcome.** Earth moves from +12.3 K to +21.3 K. Its τ comes out 1.596
where 0.869 is needed — **over by 1.84×**, which is a factor of two in
`S`, `d` or `gamma`. Those band parameters were entered by hand as
laboratory values, and a factor of two is exactly what that
uncertainty permits. Better physics, worse number, cause named.

**The clash is a percolation threshold, and its sharpness is real.**
CO₂'s bands sit at 667, 960, 2349 and 3716 cm⁻¹, so the gaps are about
1,370 cm⁻¹ wide. A wing that reaches half a gap closes the sky **all at
once**:

    wing cutoff 29 cm-1    Venus 471 K too cold
    wing cutoff 96 cm-1    Venus 250 K too hot

Nothing in between. Venus does not need *more absorber* — it needs the
wings to stop in exactly the right place, and **fitting the cutoff to
land Venus between those two is precisely what is not allowed.**

**So the layer-3 missing rule now depends entirely on the layer-2
clash**, and the clash needs something this repository does not have.
The collision-duration derivation — molecular diameter over mean thermal
speed — gives 9.6 cm⁻¹ where the literature's sub-Lorentzian cutoffs are
nearer 100. The relevant timescale is the duration of the *strong* part
of the interaction, not of the whole encounter, and deriving that needs
an intermolecular potential. That is the next rule, and it is named.

**A check had to be allowed to move with its own finding.**
`the_known_missing_rule_is_found` required the word "continuum" —
written in 3.1.23, when continuum absorption *was* the named absence.
It was added in 3.1.33, and the absence moved. A check that insists on
yesterday's answer fails the moment its own finding is acted on.

    lab 26 experiments: 23 HOLDS, 1 CLASH, 1 MISSING_RULE, 1 REFUSED
    radiative 10/10   5,737 correct, 0 wrong   published claims 12/12

### 3.1.39 — an intermolecular potential, and a prediction that misses

The far-wing cutoff was the last thing blocking Venus, and it was
being estimated by a hand-wave: molecular diameter over mean thermal
speed. That is not a rule, it is a guess with units on it.

**The potential is derived from two laboratory properties of a
molecule.** CO₂ has no permanent dipole — it is symmetric — but its
electrons move, and a fluctuation in one molecule polarises the other,
which pulls back. That is London dispersion, and its strength follows
from how easily the cloud distorts and how tightly the electrons are
held:

    C6 = (3/4) alpha^2 I / (4 pi eps0)^2
    V(r) = 4 eps [(sigma/r)^12 - (sigma/r)^6],   eps = C6 / 4 sigma^6

    derived well depths   CO2 180 K   N2 44 K   H2O 167 K
    literature            CO2 195 K   N2 95 K   H2O 356 K

**The collision duration is integrated, not estimated.** A pair crawls
near the turning point, where its kinetic energy has gone into the
field. Integrating the trajectory gives a collision **1.19× longer**
than diameter-over-speed said, and the temperature dependence — 4.2
cm⁻¹ at 200 K to 14.6 at 1000 K — is a consequence of the trajectory
rather than a parameter.

**Then it was allowed to guess, and it missed.**

    derived cutoff at 737 K      11.2 cm-1
    what Venus would require     between 29 and 96

A factor of three to nine, on the cold side. `nothing_here_reads_a_planet`
parses the imports: the prediction was made from molecular properties
and compared to Venus only afterwards.

**The miss is the result, because it closes the question.** A guess that
fails eliminates its hypothesis. Widening wings are not what makes Venus
hot, so the thing still missing is not a better line shape — and the
layer-2 **CLASH is resolved**, because both of its branches were
hand-waves and neither survives a derivation.

**The absence has a new name.** 3.1.23 blamed missing continuum
absorption and it was added. 3.1.38 blamed the line shape. 3.1.39
eliminated the line shape. What remains is a mechanism no gas model
contains at all: Venus is wrapped in a sulfuric acid cloud deck, and a
condensed aerosol absorbs and scatters across the **whole spectrum**
instead of in bands. That is a different rung, not a refinement of this
one.

**And it compounds, which is the point.** One chain, no hand-written
scenario at any step:

    polarizability + ionisation energy
      -> London C6            1.402e-77 J m^6
      -> well depth           180 K
      -> collision duration   4.724e-13 s
      -> wing cutoff          11.2 cm-1
      -> opaque band width    331 cm-1
      -> Venus optical depth  0.599
      -> habitable band       0.999 - 1.898 AU
      -> ice line             2.68 AU
      -> worlds with a window 3

    lab 26: 24 HOLDS, 0 CLASH, 1 MISSING_RULE, 1 REFUSED
    potential 5/5   5,737 correct, 0 wrong   claims 14/14   audit 21/21

### 3.1.40 — clouds, composition, and heat from below

**A condensed particle is different in kind from a gas.** Every absorber
so far works in bands, because a molecule has discrete vibrational
modes — which is why CO₂ alone cannot make a Venus and why 3.1.39's
derived potential eliminated the last gas mechanism. A droplet microns
across is large against every infrared wavelength and removes light
**geometrically**, `tau = 3 Q M / (4 rho r)`, with no window anywhere.
CO₂'s four bands cover 17% of a 737 K spectrum; a cloud covers all of it.

**The model already had half of this, and it was the wrong half.**
Venus' albedo of 0.77 *is* its sulfuric acid deck — a bare rock would be
near 0.10 — so the model counted the clouds removing **92 K** and gave
back none of their greenhouse. Taking one side of a mechanism is worse
than omitting it, because the error has a sign and nothing declares it.

**Venus is refused by name.** H₂SO₄ needs its own triple point and
latent heat, laboratory measurements this repository does not hold. The
mechanism is built and waiting for them; inventing a curve to close
Venus would be the patch this whole exercise exists to avoid.

**And the first cloud estimate was wrong by a thousand.** Lifting
Earth's air from 288 K to 260 K sheds enough water for optical depth
**22,500**, against a real 5–20. Not arithmetic: almost all of what
condenses **falls**. A cloud is a standing balance between condensation
and precipitation, needing Stokes drag and collision-coalescence, and
neither is here. Every cloud depth is now reported as an upper bound —
what the air would hold if nothing ever rained — with the balance
refused rather than guessed.

**Planets now have a composition instead of a label.** They previously
carried a mass, a temperature and the string `"rocky"`. Composition
follows from the elemental inventory in `abundance.py` and the disk
temperature — but **minerals must condense, not elements.** Keyed on
elements, oxygen condenses at 180 K and so was absent from a 280 K
planet, while Earth is 30% oxygen. It does not arrive as ice at 1 AU; it
arrives bound in silicates.

              derived   Earth
      Fe         34.9    32.1
      O          28.8    30.1
      Si         12.6    15.1
      Mg         19.1    13.9
      Ni          1.9     1.8
      Al          1.5     1.4

From solar abundances and laboratory condensation temperatures, no
planet consulted. The composition is flat across the rocky zone, so this
does **not** reproduce Mercury's iron enrichment, which needs mantle
stripping rather than equilibrium condensation.

**A planet is also warm from inside.** The balance counted only
starlight. Earth's 0.087 W/m² against 236 absorbed is worth 0.0 K and
was right to ignore — but Io's 2.0 against 4.65 is **43%, worth +8.9 K**,
and Io was coming out 14.8 K too cold with the shortfall blamed on
having no atmosphere. Tidal heat was the answer and it was never in the
sum.

    clouds 5/5   genesis 8/8   terraform 14/14
    5,737 correct, 0 wrong   claims 14/14   audit 21/21

### 3.1.41 — two rules given, one works and one does not

Asked for **rules** rather than answers: a rule for finding a
saturation curve, and a rule for the precipitation balance. Both were
built and run. One holds and one fails, and the failure is as useful.

**The saturation-curve rule fails, and the reason is structural.**
The chain exists and every link is real:

    polarizability + ionisation -> London C6
    permanent dipole            -> Debye and Keesom terms
    total C6 / 4 sigma^6        -> well depth eps
    kT_c = 1.31 eps             -> critical temperature
    T_b = 0.6 T_c               -> boiling point
    Trouton, dS_vap ~ 88        -> latent heat
    Clausius-Clapeyron          -> the curve

Run on substances whose answers are known it gives critical
temperatures of 235 K for CO₂ (real 304), 1578 K for water (647) and
195 K for H₂SO₄ (925). **It is not close enough to be useful, and the
sensitivity says it never will be:** ε goes as σ⁻⁶, so 10% on the
collision diameter is 77% on the well depth, and Clausius-Clapeyron
then *exponentiates* that into orders of magnitude on vapour pressure.
A factor of 10⁻⁹ in saturation pressure is not a curve, it is noise.

So Venus stays refused, but the refusal is now quantitative: H₂SO₄
needs a **measured** triple point and latent heat, and the reason a
derivation cannot substitute is written down.

**The precipitation rule works.** Four steps, no cloud measured:

    kinetic theory     viscosity = (1/3) rho vbar lambda
    Stokes             drag balances weight -> terminal velocity
    residence          a droplet lives cloud-depth / fall-speed
    standing balance   what is aloft is what condenses in ONE
                       residence time, not what ever condensed

Air viscosity comes out **1.21e-5 Pa s against a measured 1.81e-5** —
simple kinetic theory, 33% low, which is what it is worth. Then:

    droplet size   standing tau      total-condensate bound
       5 um            1083                  45,087
      10 um             135                  22,544
      20 um              17                  11,272
      50 um               1.1                 4,509

Real Earth cloud optical depth is **5 to 20**. The missing factor of a
thousand *was* precipitation, recovered from rules with nothing
measured. Droplet radius is the one remaining input, and it is named:
it is set by condensation-nucleus counts, not by anything derivable
here.

**And a shared default leaked one substance into another.** The
condensation gradient was a hardcoded `2e-6` — water's value — so
passing sulfuric acid through it silently gave H₂SO₄ water's behaviour
and the Venus refusal *vanished*. The gradient now comes from each
substance's own saturation curve, which restores the refusal. A shared
default is how one thing's properties become another's without anyone
writing it down.

    clouds 5/5   5,737 correct, 0 wrong   claims 14/14   audit 21/21

### 3.1.42 — the leak audit, and measuring before optimising

**A principle, stated because it changed how this session ran:** when a
measurement is off, do not reach for the number. Ask whether the rules
have enough context. Every real fix in this repository has been a rule
added, not a value adjusted.

**The sulfuric-acid leak was not unique, and is now a rule.** A function
that takes a species or a body and *defaults* a physical quantity is a
place where one thing silently wears another's properties. An AST sweep
of every engine module found six live cases beyond the original:

    condensation_gradient(lapse=0.0065)   Earth's moist adiabat
    condensation_gradient(P=101325)       Earth's surface pressure
    standing_water_path(depth=3000)       Earth's cloud layer
    standing_water_path(P=101325)         Earth's pressure
    opaque_width(T=288)                   Earth's temperature
    cv_molar / cp_molar / gamma (T=288)   Earth's temperature

The temperature ones mattered most: CO₂'s heat capacity varies **59%**
between 200 K and 800 K, so a caller who forgot `T` gave Venus Earth's
gas. All are now required arguments or derived from the body in hand.
`no_shared_physical_default` enforces it, exempting only names ending
`_ref`, which are stated normalisation points rather than properties of
the body.

**Cloud depth got the same treatment and is now honest about being a
bound.** Replacing Earth's 3,000 m with the scale height puts Earth at
optical depth 69 against a real 5–20 — about three times too deep,
which is exactly the ratio of a scale height to a real cloud layer.
Kept as a bound that at least scales with the body, with the missing
rule named: the lifting condensation level and the level of neutral
buoyancy.

**Chunking the band search made it seven times slower.** Eight threads
took **174 seconds against 24 serial**. Python holds one interpreter
lock, so CPU-bound threads take turns rather than run, and the chunked
search does 40 solves where bisection does 28. Slower work, done slower.

**Profiling found the actual cost.** One thermostat call ran
`fixed_points` **586 times, each scanning 3,400 points** — two million
evaluations of a smooth function to bracket a handful of roots. At 200
steps the roots are identical to the last decimal, because the scan only
has to find a sign change and the bisection after it does the precision.

    thermostat      6.43s -> 0.67s     9.6x
    band search    ~24s   -> 12.7s
    terraform      31.4s  ->  5.8s

The outer edge moved by 0.001 AU, inside the bisection tolerance, and
the claims checker caught that too.

    lab 27: 25 HOLDS, 0 CLASH, 1 MISSING_RULE, 1 REFUSED
    5,737 correct, 0 wrong   claims 14/14   audit 21/21

### 3.1.43 — forty worlds, none alive, and the census says why

`engine/census.py` runs the whole chain over many seeds and looks for
life. Three conditions, each already computed by some other module for
its own reasons: liquid water from the thermostat, CHNOPS from
condensation over solar abundances, and a long enough window from the
moving habitable band. None was built for this, so agreement between
them would mean something.

**40 systems, 192 worlds, 0 alive** — and the point is that it says why
instead of shrugging.

**First pass: C, H, N, P and S missing from every world.** The mineral
table had iron, silicates and ice and no carrier for any biogenic
element. The rules were not wrong; there were not enough of them. Added
apatite for phosphorus, and fixed sulfur — troilite condenses at 704 K
but metallic iron had taken all the iron at 1334, so sulfur starved. In
a real nebula FeS *sulfurises metal that already condensed* rather than
competing for it.

**Second pass caught an overcorrection.** Graphite at 626 K gave a
planet at 1 AU **36.9% carbon**, where Earth is 0.03%. The absent rule
is CO stability: oxygen outnumbers carbon in a solar nebula, CO is the
most tightly bound molecule available, and essentially every carbon
atom ends up in one — staying gaseous until about 25 K. An inner planet
gets no carbon at all, and that is correct.

The composition is much better for it:

              derived   Earth
      Fe         32.0    32.1
      Ni          1.8     1.8
      Al          1.4     1.4
      P           0.1     0.1
      O          26.6    30.1
      Mg         17.5    13.9
      Si         11.6    15.1
      S           7.7     2.9

**And the remaining failure is one rule, named exactly.** What is
missing on all 192 worlds is **C, H and N** — the same three, and they
are the three volatiles that cannot condense where rocky planets form.
Carbon is locked in CO until 25 K, water needs 170 K, ammonia 131. A
rocky world builds itself from iron, silicates and phosphate and gets
none of them. Earth has all three.

So the missing rule is **volatile delivery**: bodies that formed beyond
the ice line, scattered inward. Equilibrium condensation cannot make a
wet, carbon-bearing Earth and was never going to — and running forty
systems at once is what made that unmistakable. One world would have
looked like a bug.

**On parallelism.** Seeds are independent, so the census runs in
separate *processes* — separate interpreters, separate locks, ten cores
actually working. 40 systems in 20 seconds. This is what threads could
not do for the band search in 3.1.42, and the difference is that these
jobs share nothing.

    census 2/2   genesis 8/8   5,737 correct, 0 wrong   claims 14/14

### 3.1.44 — volatiles arrive, and eight worlds come alive

**C, H and N do not condense where rocky planets form.** Carbon stays in
CO to 25 K, water needs 170, ammonia 131. The census found all three
missing from 192 of 192 worlds, so the rule is delivery, and every piece
of it derives:

    reservoir     what condensed beyond the ice line -- 185 Earth
                  masses, from the surface density already integrated
    scattering    giant planets throw a fraction inward
    focusing      a planet catches more than its disc, 1 + (v_esc/v_enc)^2
    persistence   a scattered body crosses once per orbit for as long
                  as it survives, so capture ACCUMULATES

**The last one is what a single-crossing estimate misses by three
thousand:** one pass delivers 6.6e-8 Earth masses of water, and Earth's
ocean is 2.3e-4.

**The source is a range, not a point.** Drawing delivered material from
just outside the ice line brings water and ammonia and *no carbon* —
CO needs 25 K, far colder than 3 AU. Comets come from the whole outer
system, and only its cold end carries carbon.

**The efficiency is wrong by three orders and is labelled, not tuned.**
The chain delivers ~3,000 oceans to a world at 1 AU where Earth has one
on the surface and perhaps ten in the mantle. The cause is assuming a
scattered body stays on a crossing orbit for its whole dynamical life;
most are ejected, fall in, or are parked in a resonance long before.
The missing rule is the dynamical lifetime **distribution**. Tuning the
two coefficients until Earth came out right would be the patch this
project refuses — the mechanism is shown to work by a wide margin, and
the efficiency is named as unresolved.

**Eight of 293 worlds now pass all three conditions**, and deconstructing
them gives a result nobody put in:

     star     AU    M/Me   window        Z
     0.54   0.35    2.59     23.3   0.0297
     0.52   0.35    0.77     29.3   0.0135
     0.51   0.35    0.28     35.7   0.0070
     0.54   0.50    3.50     47.4   0.0305

**Every living world orbits a star of 0.51–0.54 solar masses**, out of a
population spanning 0.51 to 1.57. Metallicity runs the entire range and
is irrelevant. A small star burns slowly — lifetime goes as M⁻²·⁵ — so
its habitable band lingers over one orbit for tens of billions of years
instead of a few. Nothing was told to prefer small stars. It fell out of
running many and looking, which is what the census is for.

    census 3/3   genesis 8/8   5,737 correct, 0 wrong   claims 14/14

### 3.1.45 — caching keyed on the dependency closure, and four worlds watched

**The suite reruns in 32 seconds instead of 3 minutes 11.** `eval/cache.py`
keys each result on a hash — but of the **transitive closure**, not the
file. `engine/terraform.py` imports `engine/constants.py`, so editing a
constant must invalidate terraform even though terraform's own bytes did
not change. Hashing the file alone would keep serving the old answer,
and a stale PASS is a lie that looks like work.

    terraform reaches 10 engine modules; touching constants.py changes
    its key. Touching terraform.py leaves folding.py alone.

Eval scripts key on the whole engine, because a script that exercises
it end to end can be changed by anything in it — coarse and correct
beats fast and wrong. `--verify` ignores the cache entirely and reruns
everything, which is what a release does. Speed is for the edit loop.

**And the four worlds, followed instead of counted.**

    star 0.54 Msun, main sequence 47 Gyr
    world at 0.59 AU, 3.82 Earth masses
      0.0 Gyr   frozen
     14.0 Gyr   enters the band
     51.2 Gyr   too hot  [post main sequence]
      temperate for 32.6 Gyr

    star 0.52 Msun, main sequence 50 Gyr
    world at 0.35 AU, 0.77 Earth masses
      0.0 Gyr   enters the band
     35.1 Gyr   too hot
      temperate for 30.1 Gyr

**They are not the same story, and a census total cannot tell them
apart.** The worlds at 0.35 AU are warm from the beginning and lose it
as the star brightens. The ones at 0.55–0.59 AU start **frozen**, wait
14 to 15 billion years for the star to warm enough to reach them, and
then hold it for 33 to 35 Gyr — several times the present age of the
universe. One kind of world is running out of time; the other has not
started yet.

Every one ends the same way: **too hot**, as the band sweeps outward
past it. None freezes at the end. The failure mode of a habitable world
around a small star is its star brightening, not dying.

    watch 2/2   cache 4/4   suite 3:11 -> 0:32 warm
    5,737 correct, 0 wrong   claims 14/14   audit 21/21

### 3.1.46 — habitable is not inhabited

**No. Nothing made a cell, and calling it "life" was wrong.** The census
tested liquid water, the presence of CHNOPS, and a long enough window.
Not one line of that is about a membrane, replication, or metabolism.
The word was doing work it had not earned, and it is now `habitable`
everywhere — a statement about a *place*, not about anything living in
it. `habitable_is_not_inhabited` checks structurally that the census
sets no key claiming otherwise.

**The step from chemistry to a self-copying compartment is
abiogenesis, and this repository does not derive it.** It is absent,
not implied.

**What can be asked from rules already present is whether a cell could
persist**, and how big. `engine/life.py` derives the diffusion limit —
a sphere consuming oxygen supplies its own centre only out to
`sqrt(6 D C0 / R)`, past which the middle suffocates — and diffusion
scales with temperature over viscosity, so the ceiling moves with
climate:

    275 K   39.5 micron ceiling
    310 K   64.9 micron ceiling

    world at 0.35 AU   262 K, 30% wet   ceiling 33.0 um
    world at 0.57 AU   260 K, 22% wet   ceiling 32.0 um

Those are colder worlds than Earth, so they permit only smaller cells.
It is a statement about what *could* persist, not about anything that
did.

**And as for the rule the habitable worlds revealed — there was none to
add.** "Every habitable world orbits a 0.51–0.54 M☉ star" is not a new
rule; it is a *consequence* of two already present, the mass-luminosity
relation and lifetime going as M⁻²·⁵. A small star's band lingers over
one orbit for tens of billions of years. That the census found it
without being told is the point: the rules were sufficient, and the
run made the consequence visible.

**A fourth self-grepping check, and the rule that should have caught
it.** `habitable_is_not_inhabited` first searched `census.py` for the
word "membrane" and matched the sentence explaining that the census
does *not* test membranes. `checks_do_not_grep_themselves` existed
precisely to forbid this — but scanned only `lab.py`. **A rule that
covers one file is not a rule.** It now scans every module, and was
made precise: it flags a function only when it searches source for a
string literal it itself contains, so a function reading a data file
or skipping its own file is not caught. A rule with false positives
gets ignored.

    watch 4/4   census 3/3   cache 4/4   suite 0:32 warm
    5,737 correct, 0 wrong   claims 14/14   audit 21/21

### 3.1.47 — a lab on the origin, and the barrier is not what it looks like

Back to a lab, because the question is small enough to isolate: what
can be said about abiogenesis from rules already here, without
inventing biology?

**Energy is not the barrier, and that rules out a whole class of
explanation.** Copying information has a floor — Landauer, `kT ln 2`
per bit, **0.0179 eV** at 300 K. A minimal 580,000-base genome is 1.16
million bits and costs **3.3 × 10⁻¹⁵ J** to copy. A three-unit pH
gradient pays 0.179 eV per proton, so **116,398 protons** cover a whole
genome — a hydrothermal system moves that in moments. A real bacterium
spends about 10⁻¹¹ J, **three thousand times the floor**. Nothing is
stopped by the bill.

**What cannot be paid for is the search.**

     residues    sequences    years to search
           40     1.1e+52          4.3e-13
           50     1.1e+65          4.4e+00
           57     1.4e+74          5.6e+09
           70     1.2e+91          4.6e+26
          100     1.3e+130         4.9e+65

Fill an ocean with 8.1 × 10⁴⁴ peptide-scale molecules, let each try a
new sequence every picosecond, and run it for the age of the universe.
**Chance reaches 57 residues and stops.** Ten more residues costs 10¹⁷
times longer — 20ⁿ does not bend, so the ceiling is a cliff.

**So the missing mechanism has a shape.** Below 57 residues, exhaustive
search needs no explanation. Above it, something must reach long
sequences *without trying them* — selection on intermediates, or
assembly from parts already found. That is the same answer
`engine/folding.py` gives to Levinthal's paradox one level down:
folding is not a search, and neither is this.

**And naming the shape of a mechanism is not deriving it.**
`this_does_not_claim_abiogenesis` says so explicitly. What the lab
produced is a *constraint* — a number where there was a hand-wave, and
one whole explanation eliminated. The origin itself is still absent.

**And the constants rule caught its own author again.** `engine/origin.py`
redefined `YEAR_S` ten minutes after being written, and
`constants_are_not_duplicated` flagged it — the second time a rule here
has caught the person who wrote it, after `MEASURED_Q_BAR` in 3.1.31.
Both were typed by hand shortly after the rule forbidding exactly that
went in. A rule that only catches other people's mistakes is not being
tested.

    origin 5/5   lab 28 experiments   5,737 correct, 0 wrong
    claims 16/16   audit 21/21

### 3.1.48 — a fifth verdict, and measuring instead of compiling

**SUGGESTION.** The lab could only say pass, clash, missing or refused,
and not every useful observation is a verdict about correctness. "This
rule has never fired" is worth knowing and is not a failure. With no way
to say it, a lab either stays silent — losing the observation — or
promotes it to an error and cries wolf until the whole thing is ignored.
A SUGGESTION stops nothing and blocks no layer.

The first one implements exactly the point that prompted it:

    3 of 29 rules have returned something other than HOLDS at least
    once and are demonstrably live. The other 26 have only ever
    passed, which is not a defect and is not evidence either -- a
    rule that cannot fail looks exactly like one that has not yet
    had cause to.

The record starts when recording started, so the rules that fired
*before* this existed — the sulfuric-acid leak, `MEASURED_Q_BAR`,
`YEAR_S` — show as never having fired, and the count understates. Said
plainly rather than quietly corrected.

**And it recursed on its first run.** An experiment that inspects the
whole lab called `run()`, which runs every experiment including that
one, until the stack gave out. An experiment cannot take a reading of
the lab it is part of; the *runner* writes the history and the
experiment only reads it.

**On compiling to C: the measurement said not to.** Profiling one
thermostat call found `gravity()` evaluated **1,309,539 times** — a
constant of two numbers fixed when the body was made — and
`equilibrium_T` recomputed 436,514 times inside a loop it does not
depend on. Cython would have made a needless division fast. Memoising
one and hoisting the other:

    thermostat    6.43s -> 0.67s -> 0.478s
    band search    24s  -> 12.7s -> 9.1s

That is the second time on this question that measuring first beat the
obvious answer; the first was threads, which made it seven times slower.
Compilation is still available and is now worth less, because what was
left is arithmetic that has to happen.

    lab 29 experiments: 26 HOLDS, 1 SUGGESTION, 1 MISSING_RULE, 1 REFUSED
    5,737 correct, 0 wrong   claims 16/16   audit 21/21

### 3.1.49 — Earth alone, walked gate by gate

The census asks many worlds one question. This asks one world every
question, in order, and stops at the first gate that does not open —
because that is where the missing mechanism is. Every gate is derived
from rules already here; nothing was added to make a point.

    open   solvent      82% of the surface above freezing at 288 K
    SHUT   elements     H,N,O,P,S present -- MISSING C
    open   energy       a genome costs 3.3e-15 J; a bacterium spends 1e-11
    open   compartment  C10 tails assemble above 3.3e-07 M
    SHUT   crowding     a 100 nm vesicle holds 2.5 solute molecules
    SHUT   search       chance reaches 57 residues; ~66 are needed
    SHUT   fidelity     best enzyme-free copying keeps 100 bases
    SHUT   bootstrap    the 200-base replicase exceeds both bounds

**Three of the four things usually called hard are not the problem.**
Water, energy and compartments all open. Energy by three orders of
magnitude. And the compartment gate turned out to be the **same rule**
as protein folding — burying a CH₂ away from water is worth 3.7 kJ/mol,
which collapses a chain and assembles a bilayer. Two consequences, one
rule, neither fitted to the other.

**The elements gate was passing on a technicality and now does not.**
It asked for five of six and opened while **carbon was absent**. That is
not a partial success — a biochemistry without carbon is not a
biochemistry. Carbon is locked in CO down to 25 K, so it reaches an
inner planet only from the coldest reservoir, and the delivery average
over 3–45 AU does not carry enough. All six or none.

**A 100 nm vesicle at 10⁻⁶ M encloses 2.5 molecules.** Chemistry needs a
population, not a pair. Something must concentrate before anything can
react, and that mechanism — drying pools, ice eutectics, vent pores —
is absent here.

**And the last two bounds close on each other.** Chance can *find* 57
residues. The most accurate enzyme-free copying can *keep* 100 bases.
The smallest RNA that copies RNA is 200. Two limits from unrelated
arguments both fall below the one thing that would raise them — because
the replicase is what would improve the fidelity that would permit the
replicase. **The gap is not a shortage, it is a loop.**

This walks Earth to the first closed gate and names it. It does not open
it. What the walk is worth is that four popular explanations are now
ruled out by derivation rather than opinion.

    earthlab 5/5   lab 29 experiments   5,737 correct, 0 wrong

### 3.1.50 — cancelling a rule to size what it was holding up

**A shut gate says no. It does not say by how much**, and the difference
matters enormously: a gate missing by a factor of two is a different
problem from one missing by 10¹¹. So each closed gate is relaxed — the
one quantity it depends on is moved until it opens — and **the size of
the move is the specification for the missing mechanism.**

    elements        inf x    carbon must arrive; CO freezes only at 25 K,
                             so the fix is a colder source, not more
    crowding        40 x     or a vesicle 3.4x wider (341 nm)
    search      5.1e+11 x    more trials to reach 66 residues by chance
    fidelity       2.0 x     one error in 200 instead of one in 100

**Two of the four are modest.** Crowding needs 40× — evaporating pools,
eutectic freezing and pore thermophoresis all reach far more than that,
so it is not a deep problem, only a mechanism not yet written. And
**fidelity needs a factor of two.** One error in 200 instead of one in
100 is the entire distance between chemistry and a replicator.

**One is astronomical, and that is the informative one.** Search is short
by 5.1 × 10¹¹, which is not a gap anything closes by trying harder. So
chance is not how it was crossed — something must assemble from parts
already found. That is Levinthal's answer for the third time in this
repository: folding is not a search, sequence-finding is not a search,
and neither is this.

**The loop audit, now standing.** Profiling a spectral pass found
`c6()` — the London dispersion coefficient, a pure function of two
constants — called **10,749,440 times**, with `well_depth` and
`potential` behind it. None of that is physics; it is one answer
recomputed. Memoised:

    spectral pass   ~1.3s -> 0.039s

That is the third time here that the fix was not running a loop rather
than running it faster, after `gravity()` at 1.3 million calls and
`fixed_points` at 3,400 steps that 200 would do. **Before making a loop
faster, check whether it needs to run.**

    earthlab 6/6   5,737 correct, 0 wrong   claims 16/16   audit 21/21

### 3.1.51 — reuse the exact answer, never the average

Caching the thermostat cuts the Earth lab from 0.52 s to 0.007 s and
the band search roughly in half. Two things about how, because both
matter more than the speed.

**Averaging past scans would not be a cache, it would be a new and
wrong number.** A mean over runs that differ describes none of them,
and this repository has been bitten by exactly that twice: measuring
binding energies against abundance-weighted atomic weights produced an
**80 MeV artefact**, and measuring an error bar across two
manifestations gave **4.763 MeV where the two populations are 1.850 and
6.249**. Exact reuse of an identical computation is safe. Averaging is
how you get a plausible number that nothing can check.

**And the first cache was wrong in a way worth keeping.** It keyed on
`id(body)`. The habitable-band search builds a probe planet per
iteration and drops it immediately, CPython reuses the freed address,
and **a new world at a new orbit was handed a dead one's climate.** The
outer edge moved from **1.899 to 1.984 AU**.

It announced itself only because a published number changed — which is
what `eval/claims.py` exists for. A key must be what the answer depends
on: mass, radius, orbit, albedo, eccentricity, internal heat.
`a_cache_keys_on_what_it_depends_on` now forbids the pattern.

    thermostat    0.483s cold, 0.00001s warm
    earthlab      0.52s -> 0.007s
    terraform     8.2s -> 3.9s      lab 30.0s -> 4.7s

    lab 30 experiments: 27 HOLDS, 1 SUGGESTION, 1 MISSING_RULE, 1 REFUSED
    5,737 correct, 0 wrong   claims 16/16   audit 21/21

### 3.1.52 — every supply gate opens, and a finding is withdrawn

**Concentration is a rule, and it clears crowding easily.** A pool
losing 99% of its water concentrates what remains 100×; ice rejecting
solute does the same to the brine between crystals; thermophoresis in a
pore adds 1.3–4.5× per pass and compounds. The gate needed **40×**. A
100 nm vesicle goes from 2.5 molecules to 252.

**Carbon arrives once the source reaches the CO line.** Delivery was
sampling 3–45 AU, which spans 170 K down to 41 — and CO condenses at
**25 K, which for this star is 124 AU**. Every sample was too warm, so
delivery carried water and ammonia and no carbon. Comets are not a belt
but a range, and only the cold end carries carbon. Extending the source
opens the elements gate: **C, H, N, O, P, S all present.**

**All five supply gates now open, and everything still shut is about
information:**

    open   solvent      elements   energy   compartment   crowding
    SHUT   search       fidelity

**And one mechanism clears both.** Search and fidelity fail on the same
object — a 200-base replicase that chance cannot find and enzyme-free
copying cannot keep. Neither gate has to reach it whole:

    a 20-base piece is 1.1e12 sequences, exhausted in under a second
    a 20-base piece is well inside the 100-base error threshold
    ten of them ligated is 200 bases

The object that could be neither found nor maintained as a unit is
trivially both in parts. Nothing was added to get this — it is the two
existing bounds asked about a smaller object. **This is Levinthal's
answer for the fourth time here:** folding is not a search,
sequence-finding is not a search, and assembly is not either. Every
combinatorial wall in this repository has resolved the same way — the
thing is built, not drawn.

**3.1.44 is withdrawn.** It reported that every habitable world orbits a
0.51–0.54 M☉ star. That held *only while carbon could not reach an inner
planet*: with the source stopping at 45 AU, the only worlds scraping any
carbon were those around dim stars whose ice line sits close in. With
the source extended, **101 of 234 worlds are habitable and span every
stellar mass, every metallicity, and orbits from 0.35 to 3.7 AU.** The
correlation was the shape of a missing rule, not a fact about small
stars.

    earthlab 7/7   census 3/3   5,737 correct, 0 wrong   audit 21/21

### 3.1.53 — self-maintaining has a size, and it is the size of a cell

A replicase that can be assembled is still not a cell. A cell
**maintains itself**: every molecule it needs is produced by a reaction
another of its molecules catalyses, with nothing outside keeping it
going. That is autocatalytic closure, and closure appears when
`N × p > 1` — N molecule types present, p the chance a random one
catalyses a given reaction, measured by in-vitro selection at somewhere
between 10⁻⁶ and 10⁻¹¹.

**Diversity needs volume, so closure puts a FLOOR under the
compartment.** And `engine/watch.py` already derived a **ROOF** from
diffusion — past a certain radius a sphere cannot supply its own centre.
Two bounds from arguments with nothing to do with each other:

    p = 1e-6     floor 0.34 um     roof 47.5 um
    p = 1e-8     floor 1.58 um     roof 47.5 um
    p = 1e-10    floor 7.35 um     roof 47.5 um

**There is a window for every plausible p, and a bacterium is 0.5 to 5
microns.** Neither bound was aimed at the other and neither was fitted
to a cell. What they bracket is the size life actually is.

**And it says the 100 nm vesicle is not a candidate.** The bag that
passes the compartment gate holds 25,225 molecules against the 10⁸ types
closure wants. A bag is not a cell, and the first self-maintaining thing
had to be cell-sized — which is a prediction, not an observation fed in.

    open   solvent  elements  energy  compartment  crowding
    open   assembly  self-maintaining  bootstrap
    SHUT   search    fidelity            (both bypassed by assembly)

**Godot is present** — 4.7.2, already wired as a third executable
backend in `engine/ir.py`. Worth being exact about what it can do for
speed: rendering does not reduce computation, and moving the chemistry
into GDScript would be a rewrite, not an offload. What it *is* good for
is the thing atlas2 used it for — a **second execution path**, so a
result that agrees across Python, Ruby and GDScript is one no single
interpreter's quirk produced. That is verification, not throughput.

    earthlab 8/8   5,737 correct, 0 wrong   claims 16/16   audit 21/21

### 3.1.54 — cells on Earth, and the one place compiling was right

**Cells introduced, at the size the lab derived** — between the
closure floor and the diffusion roof, not sized to fit the experiment.
The question stops being whether a world permits life and becomes what
life does to the world.

**Oxygen is sink-limited, not production-limited.** A modern biosphere
makes Earth's whole oxygen atmosphere in **4,144 years**. The reduced
crust swallows 38 atmospheres' worth first, so a planet can
photosynthesise for ages and still read as anoxic. The curve is a
threshold, not a ramp: nothing, then everything.

**And the air was already wired to the surface.** Methane is one of
three gases in the band table, so once oxygen cuts its lifetime from
10,000 years to 10, the climate follows with nothing added to connect
them:

    t Gyr   sink     O2   CH4 ppm   T surf
     0.00     0%   0.00    1000.0    315.6
     0.23   100%   1.00       1.8    313.7   <-- -1.9 K

**A biosphere that makes oxygen cools its own planet**, which is not
something it was asked to do, and Earth's first glaciation follows its
first oxygen.

**The delay is wrong by 147× and is left wrong.** The model puts first
oxygen at 0.0075 Gyr; Earth took about 1.1. The *shape* is right —
sink first, then accumulation — and the inputs are not: early
productivity was a fraction of modern, and the sink is not only iron
but the whole reduced crust plus what volcanism keeps adding. Neither
is derived here, so neither is tuned.

**On Cython: it was right exactly once, and it earned that by
measurement.** Four earlier speed attempts did not need a compiler —
threads made the band search **seven times slower**, a 3,400-step scan
gave identical answers at 200, `gravity()` ran 1,309,539 times for a
constant, and `c6()` 10,749,440 times for a pure function. All four
were fixed by *not doing the work*, and a compiler would only have made
needless work fast.

Planck's law is different: **2,475,200 evaluations per biosphere run**,
every one a different number something downstream uses. Nothing to
hoist, nothing to cache. That is when compiling is worth reaching for.

    spectral pass    0.039s -> 0.0156s
    biosphere        61.4s  -> 6.0s

**The Python version stays beside it**, and the two are checked against
each other — they agree to 1e-16 across nine band-and-temperature
combinations. The compiled path is a *second implementation*, not a
replacement, so a disagreement between them would be a finding.

    biosphere 6/6   radiative 11/11   5,737 correct, 0 wrong

### 3.1.55 — prime Earth, and why a big animal is an organ not an atmosphere

Earth run at every advantage the rules allow — full productivity, a
tenth the reduced sink — reaches **100% of present oxygen**. Then the
question is what a body can be.

    without circulation          with circulation
      open  aerobic                open  aerobic
      open  thin body              open  thin body
      SHUT  thick body             open  thick body
      SHUT  large on land          open  large on land

**Oxygen is the usual answer and it is not the whole one.** Tissue
thickness without a transport system is the same diffusion limit
`engine/life.py` derives for one cell, and it goes as the **square root**
of oxygen:

    0.5% of present O2      3.8 um of tissue
    100%                   54.8 um
    500%                  119.5 um

**Five times the oxygen buys 2.2 times the thickness.** A body cannot be
made thick by enriching the air. Fifty-five microns is a sheet a few
cells deep — and that is exactly what the earliest multicellular fossils
are: fronds and quilts, thin in one dimension.

**So the step to a large animal is not an atmosphere, it is an organ.**
Adding circulation opens a thick body immediately, at the *same* oxygen
that could not open it before. No amount of prime conditions
substitutes, and the model says so by leaving the gate shut however
favourably Earth is run.

Above that the constraint changes again: once thick bodies exist the
square-cube law binds instead, at **173 m** before a land skeleton
reaches bone's compressive strength at 1% cross-section.

**What this run says, deconstructed:** a planet can be given every
advantage and still not produce a large organism, because the missing
thing is not a resource. Three of the four gates here are about supply
and open on prime Earth. The one that stays shut is about
*architecture*, and architecture is not something a planet provides.

    biosphere 8/8   5,737 correct, 0 wrong   claims 16/16   audit 21/21

### 3.1.56 — circulation is derivable, and it is cheap

**Yes, and the answer makes the gap smaller than it looked.** A pump
moves fluid against viscous resistance; Poiseuille gives what a flow
costs and `engine/life.py`'s Kleiber relation gives how much flow a
body of a given mass needs. Blood carries about 4 × 10⁶ joules of
oxygen per cubic metre.

      1 ug     0.60% of the metabolic budget
      1 g      0.11%
      1 kg     0.02%
     70 kg     0.01%     (a real heart is 1-2%, with a branching
                          tree this single-vessel model omits)

**Pumping is affordable at every size and gets cheaper as bodies grow**,
because demand rises as mass^0.75 while a wider vessel's resistance
falls as r⁻⁴. So circulation was never a barrier that had to be
crossed. It is the cheap answer to a problem that becomes unavoidable
at about 55 microns — below that a pump is pure cost, above it there is
no alternative.

**What is not derived is the organ.** That a pump pays for itself does
not say how a lineage builds one, and there is no rule here for that.
The honest claim is narrower than "circulation is derivable": *nothing
forbids it, and the economics favour it at exactly the size diffusion
fails.* The absence is real and much smaller than it appeared.

**A unit error worth recording.** The first pass had pumping costing
**6,528% of a human's budget** — I mixed millilitres and cubic metres
in blood's oxygen capacity, a factor of a thousand. It was caught by
comparing against a known quantity: a real heart is 1–2 W of a 100 W
budget, and 5,355 W is not. Checking a derivation against something
measured is what stops a unit slip becoming a conclusion.

**On the CPU, plainly:** the suite has not got faster *for you* because
`--verify` bypasses the cache by design, and because every edit to an
engine module invalidates everything downstream of it. Both are correct
behaviour and both mean the runs you have seen were cold. The caching
is real — a warm run is 32 seconds against 3 minutes 11 — but it only
shows when the tree is not being edited.

    biosphere 10/10

### 3.1.57 — land, and the pattern that has now repeated three times

Four things change when a body leaves water, and **only one is a
planetary condition.**

    open  uv shield        ozone 300 DU passes 3.1e-39 of the damaging band
    SHUT  water retention  air pulls 850 Pa against a body wet inside
    SHUT  support          buoyancy gone; the skeleton carries everything
    open  gas exchange     air holds ~30x more oxygen per volume than water

**The UV shield is made of the thing it protects.** Ozone comes from
oxygen, so a planet cannot shield its land before its air is
breathable — the same molecule does both. And it saturates fast: at
0.5% of present oxygen two parts in a thousand reach the ground, at 5%
four parts in a billion. Coming ashore was never blocked by ultraviolet
for long.

**Gas exchange gets *easier*.** Air carries about thirty times more
oxygen per volume than water. It is the one thing land simplifies.

**And the two that stay shut are a skin and a skeleton.** Adding them
opens everything, at the same oxygen that could not open them before.

**That is the third time in a row:**

    a thick body     needed a pump
    a large animal   needed circulation
    land             needs a cuticle and bones

Not one of them is something a planet supplies. Every environmental
gate this simulation can state now opens on Earth, and **every barrier
left is architecture.**

**Which is the honest end of this line of work.** The rules can say
what conditions permit a land vertebrate, and they do: oxygen,
shielding, a size window between closure and diffusion, a pump costing
0.01% of budget, a skeleton good to 173 m. They cannot produce one. The
missing mechanism is whatever generates architecture — variation and
selection — and this repository has no rule for it. That is a single
named absence standing behind three separate gates, which is a better
position than three unrelated mysteries.

    biosphere 12/12

### 3.1.58 — seeded, released, and it stays microbial

The instruction was to seed the smallest thing that can live, supply
the planet, give it only the rules under which it lives or dies, and
let go. `engine/descent.py` does that. The seed is one 1.58-micron
sphere — the closure floor — with **no traits and no instruction to
acquire any**. Traits appear by accident, cost metabolism, and pay
nothing unless a wall makes them necessary.

**It ran twice and both runs were wrong in opposite directions, which
is how the missing rule announced itself.**

**First run: eighty-one metres.** Kleiber gives the *cost* of being big
— mass^0.75, so cost per gram falls — and I had given no *intake*.
Bigness was free, circulation fixed at 100% within 333 generations, and
the population grew until it hit the only wall left: a land skeleton's
173 m ceiling, applied absurdly to something swimming.

**Second run: it collapses to the floor.** A body feeds through a
*surface*, so intake goes as mass^(2/3) while cost goes as mass^0.75.
Adding that bounds size from above — the curves cross at 23 cm — but it
also makes surplus energy per gram scale as **mass^(-1/3)**:

     radius    intake W      cost W     surplus/g
      0.10u    2.34e-10    6.48e-12     5.43e+07
     10.00u    2.34e-06    2.05e-07     5.09e+05
   1000.00u    2.34e-02    6.48e-03     4.04e+03

**Smaller is always fitter, and that is not a bug.** Life on Earth was
microbial for three billion years. Nothing about metabolism favours
being large.

**So what selects for size is not in this repository, and now I can
name the category.** Predation and competition are **interactions
between organisms**, and every rule here is one body against physics —
diffusion, Kleiber, square-cube, desiccation, Poiseuille. That is a
different kind of absence from a missing measurement like H₂SO₄'s
vapour curve. It is a missing *kind of rule*.

**A check was inverted rather than deleted.** `size_grows_until_a_wall`
asserted that size grows, and passed — on the model where bigness was
free. The intake rule falsified it. It now asserts that size *shrinks*,
which is what the rules say and what Earth did, and it carries the
history of having claimed the opposite.

    descent 6/6

### 3.1.59 — fewer rules, and a sign of life that could be checked

Every conclusion in this repository so far is about worlds nobody can
visit. This is the first that could be **measured across interstellar
distance from a spectrum**.

**Oxygen is not a biosignature** — a photodissociating ocean makes it.
**Methane is not** — serpentinising rock makes it. The two *together*
are, because `CH4 + 2 O2 -> CO2 + 2 H2O` is downhill by 818 kJ/mol,
putting the equilibrium constant at **2.3 × 10¹⁴⁸**. Earth holds 1.8 ppm
methane inside 21% oxygen. Those cannot sit together; something is
remaking the methane faster than the oxygen destroys it. That is an
accounting identity, not an assumption about biology.

**And the first version was wrong in a way Mars exposed.** Asking only
how far downhill a pair sits, Mars came back **DRIVEN** — it holds 0.07%
carbon monoxide beside 0.14% photochemical oxygen, genuinely 128 orders
from equilibrium, and it is not alive. Ultraviolet splits CO₂ all day.

The equilibrium constant says how *impossible* a pair is. It says
nothing about how *much* must be remade to hold it there, and that is
what a driver pays for. So the measure became a **flux**:

    Earth   9.47e+11 kg/yr of methane must be replaced
    Mars    4.06e+10 kg/yr of carbon monoxide

**That narrowed the gap from 20 orders to a factor of 23, and did not
close it. Mars still reads driven, and it is left that way.** Lowering
the threshold until Mars drops out would be fitting to the answer. What
is actually missing is a real lifetime rule — CO on Mars survives
centuries on slow hydroxyl chemistry, not the inverse-oxygen scaling
used here — and naming that is worth more than a tuned constant.

**What this deliberately does not say is "life."** It returns *something
must be doing this* and a bill. A sufficiently odd geology can drive a
gas pair, Mars demonstrates it, and the false positive is reported
rather than hidden.

    signature 4/4

### 3.1.60 — Mars fixed, and magnitude was never the question

The biosignature detector called Mars **driven**, and Mars is dead.
That was the one wrong answer left in the repository, and it took
three attempts because the first two asked the wrong thing.

    orders from equilibrium     Mars driven at 128 orders
    + a flux rule               gap narrowed to 23x, still driven
    + a derived OH lifetime     WORSE -- dry air gives CO a 21-year
                                life, so a bigger bill, not smaller

**Deriving the lifetime properly made it worse**, which is the clue.
Every attempt was measuring *how large* the disequilibrium is, and
size was never what separates the two worlds.

**What separates them is whether one process can write the whole
invoice.**

    Mars    CO2 + photon -> CO + O.  A single reaction makes BOTH
            members of the pair, in a ratio it fixes. Observed
            CO/O2 is 0.50 against a predicted 2.0 -- a factor of
            four, and escape removes light species preferentially.
    Earth   methane from methanogens, oxygen from photosynthesis.
            No abiotic reaction has both among its products at ANY
            ratio.

**The rule was motivated by Mars, so it has to answer pairs it was not
built for** — otherwise it is fitting with extra steps. It does:
hydrogen beside oxygen reads quiet (water photolysis makes both),
hydrogen beside methane reads quiet (serpentinisation makes both).
Both are real astrobiological false positives, neither was tuned, and
methane beside oxygen stays driven.

**And the honest limit is sharper now.** The detector can only check
reactions it has been given, so its blind spot is precisely the
chemistry nobody has thought of. It returns *no known process accounts
for this* — which is a weaker and more defensible claim than "life."

    signature 5/5   0 wrong answers in the repository

### 3.1.61 — the second organism, and it was not enough

`engine/descent.py` showed that under one-body-against-physics rules
life stays microbial: surplus energy per gram goes as mass^(-1/3), so
smaller always wins. **Predation was the named missing category. It was
added, and it did not work.**

**An encounter-rate refuge was the obvious mechanism and it is not
one.** If large prey were rarer, a hunter would starve looking for
them. But the scalings cancel *exactly*: density goes as r⁻³,
cross-section as r², swimming speed as r, and the product is r⁰. A
predator meets the same number of meals per second whatever size its
prey are, and each meal is bigger. **Being large is no refuge from
being found.**

**Predation inside one population is self-cancelling.** A size
threshold — anything three times your radius can eat you — changed
nothing, because selection drives everyone to the floor together and
once the population is uniform nobody is three times anybody. *A
predator that shrinks with its prey is not a predator.* The second
organism has to be a separate lineage or the pressure dissolves into
the thing it is applying pressure to.

**With two lineages it still fails, and the failure is clean:**

    pressure    prey um    predator um
        0.40      0.100          0.311
        0.80      0.108          0.351
        0.95      0.114          0.324
        0.99      0.130          0.366

The hunter tracks its prey down to the floor and sits at exactly
`PREDATOR_RATIO`. Pushed to **99% of all deaths from predation** the
prey reaches 0.13 microns and stops. Growing to escape costs more than
being eaten, because surplus per gram goes as mass^(-1/3) — a steep
hill against a *bounded* risk. The pressure was measured rather than
tuned upward until it worked.

**So two organisms were not enough**, and that is worth more than a
rigged success. What a bounded risk cannot do, an unbounded one might:
predation caps at losing everything once, while metabolic advantage
compounds every generation. Whatever selects for size has to beat a
compounding return, and a fixed chance of death does not.

    descent 8/8

### 3.1.62 — one planet, half a second, and the root was already there

**Checking everything takes minutes and almost none of it is about
making a planet.** `engine/planetlab.py` runs only the planet chain —
seed to land creature — and it takes **0.53 seconds**, which makes the
loop worth using.

    star                  1.00 Msun, ice line 2.68 AU
    planet                0.99 AU, 3.45 Earth masses, Fe 32% O 27%
    elements              C,H,N,O,P,S after 2961 oceans delivered
    climate               288 K, 82% above freezing, CO2 43 Pa
    cells                 viable between 1.58 and 47.5 microns
    oxygen                reaches 100% of present
    body/aerobic          open      land/uv shield        open
    body/thin body        open      land/water retention  open
    body/thick body       open      land/support          open
    body/large on land    open      land/gas exchange     open

**Provisional rules were offered and none were needed.** The lab allows
undevised rules marked PROVISIONAL, listed rather than hidden, with
what would promote each — nothing marked PROVISIONAL may be cited as a
result and `eval/claims.py` is never told about it. The count is
**zero**. Every step from a four-number nebula seed to a land animal is
already derived.

**And you were right that the root already exists.**
`engine/provenance.py` has been recording atoms from a universe seed
hash through the epoch that made them and every decay since,
hash-linked so the chain can be *checked* rather than believed. It
stopped at atoms. Carrying it up costs nothing new:

    seed          universe hash d59bc58bc3456775c6831abc...
    stellar_c     formed: alpha-chain, Z=6 is even and below the peak
    stellar_c     decay: C -> N by beta-minus, Q=0.16 MeV
    abundance     C is 2.36e-03 of baryonic mass
    valence       C bonds 4 ways, from shell filling
    residue       G is C2H5NO2 -- 2 atoms of C in it
    fold          G scores 0.667 on carbon-to-polar

Seven linked stages from a hash to a folding residue, and **nothing in
it is computed for the occasion** — it is the existing records read in
order, which is what makes it a root rather than a story.

    planetlab 4/4   0.53s for the whole planet chain

### 3.1.63 — a claim is only as good as its worst input

**The challenge was right and it is worse than a word choice.** This
repository claims to derive rather than predict. An audit of the
modules added most recently found **28 typed numbers with no label at
all**, and several are not measurements. `INTAKE_COEFFICIENT` carried
the comment *"sets where supply and demand cross"* — a knob with a note
on it.

`engine/inputs.py` classifies every one into three kinds, chosen
honestly rather than generously:

    EXACT      2   fixed by definition
    MEASURED  13   someone went and found out
    CHOSEN    18   nobody measured it, nothing derives it, it was
                   picked so a model would run

**A CHOSEN number is not forbidden** — a model that refuses every
unmeasured quantity does nothing. What is forbidden is *citing* a
result that rests on one as though it were derived. So claims are
graded by their weakest input:

    EXACT     the habitable band 0.999-1.899 AU
    EXACT     Earth composition Fe 32.0%
    EXACT     Earth reads as driven and Mars does not
    MEASURED  the 57-residue search ceiling
    CHOSEN    the cell size window 1.58-47.5 um
    CHOSEN    life cools its own planet by 1.9 K
    CHOSEN    seeded life stays microbial
    CHOSEN    predation does not reverse the collapse

**That split is the honest state, and it is not flattering to the
recent work.** The planet results — band, composition, biosignature —
rest on nothing chosen. **The biology results do.** "Seeded life stays
microbial" depends on `INTAKE_COEFFICIENT` and `TRAIT_COST`, both
picked. "Predation does not reverse the collapse" depends on three
chosen numbers. Those two were reported as findings and they are
parameter-dependent conclusions.

**This is the same discipline as the error bars, one level down.**
3.1.18 said a bar belongs to a domain; 3.1.29 said it belongs to a
manifestation. This says a *claim* belongs to its weakest input, which
is the rule those two were special cases of.

    inputs 4/4   18 of 33 numbers are CHOSEN and now say so

### 3.1.64 — the earliest ancestor, checked rather than produced

LUCA is not a fossil and not a model output. It is a
**reconstruction**: whatever bacteria and archaea both have, their
common ancestor had. That makes it the one early organism there is
independent evidence about, and the only one worth testing rules
against.

So `engine/luca.py` does not simulate it into existence. It asks
whether what this repository derives **contradicts** what comparison
already establishes.

    AGREES     [MEASURED] ran on ion gradients
    AGREES     [CHOSEN  ] was enclosed, by something not a modern membrane
    AGREES     [MEASURED] had DNA but not the enzymes to copy it
    AGREES     [CHOSEN  ] was a cell
    AGREES     [EXACT   ] used the genetic code we still use
    CANNOT SAY [CHOSEN  ] lived where the gradient was

**Five agree, none contradict, one the rules cannot speak to.**

**The useful half of the reconstruction is what the two domains do
*differently*.** Both have membranes and both copy DNA — with
machinery that is *not homologous*. So LUCA had a compartment and a
genome and **not** the modern apparatus for either. It was enclosed by
something else and copied by something else.

That is precisely the regime these rules describe: a bilayer that
assembles from C10 tails with no enzyme, and a 200-base replicase
reached by ligating ten 20-base pieces because no polymerase exists
yet. Neither was built to match LUCA.

**Three of the six rest on CHOSEN numbers and say so.** The
compartment leans on an ocean concentration nobody measured; the cell
size on a catalysis probability picked from the middle of five orders
of magnitude. Those are not derivations and are not cited as such.

**And agreement is weak evidence.** It is the contradictions that
would have been informative, and there are none to report — which is
a much weaker statement than having produced an ancestor. The rules
are consistent with the earliest organism we have evidence for. They
did not make it.

    luca 4/4   5 agree, 0 contradict, 1 cannot say

### 3.1.65 — LUCA to us, and the gaps made legible by contrast

The argument for running the chain even where it is weak: **a complete
chain makes its own gaps legible.** A step resting on nothing chosen
sits next to one resting on three picked numbers, and the contrast
says where the work is.

    ALLOWED  [CHOSEN  ] LUCA -> eukaryote
    ALLOWED  [MEASURED] eukaryote -> multicellular
    ALLOWED  [MEASURED] multicellular -> large-bodied
    ALLOWED  [MEASURED] large-bodied -> skeletal
    ALLOWED  [MEASURED] skeletal -> land
    ALLOWED  [MEASURED] land -> endotherm
    ALLOWED  [MEASURED] endotherm -> large brain
    SILENT   [CHOSEN  ] large brain -> us

**Nothing in the chain is forbidden. Two steps rest on chosen numbers
and one the rules cannot speak to at all.**

**Two things turned out more derivable than expected.**

**Insulation is a precondition, not a refinement.** A warm body makes
heat through its volume and loses it through its surface. A 70 kg body
makes 82 W and loses **99 W** through bare skin — and the ratio never
reaches one at *any* size, climbing from 0.33 at a gram to 0.83 at 70
kg and stopping. Warm-bloodedness is not something a body can simply
do. Fur comes first or the heat leaves faster than it arrives, and
every endotherm has it.

**A brain has a hard ceiling five times away.** Neural tissue runs
about ten times the metabolic cost of average tissue, so a brain at 10%
of body mass would consume **100% of the entire energy budget**. A human
brain is 2% and takes 20%. That is why a brain is expensive rather than
merely large.

**Every row says ALLOWED or SILENT, never HAPPENED.** Each transition
needs a mechanism producing the variation being selected, and
`engine/descent.py` established there is none here — seeded life stays
microbial, and predation does not move it. The last step is silent
outright: **nothing distinguishes one large-brained land endotherm from
another**, because at that point the rules stop being physics and start
being history, and this repository has no history.

**So the two missing parts are now sharply framed.** One is a mechanism
that generates architecture. The other is contingency — the reason it
was us and not some other large-brained endotherm. The first might be
derivable. The second is not the same kind of question.

    ancestry 4/4   8 transitions, 0 forbidden, 1 silent
