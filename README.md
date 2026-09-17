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
