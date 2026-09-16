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
