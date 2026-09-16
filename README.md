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
