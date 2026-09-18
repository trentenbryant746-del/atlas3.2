# Fingerprint-gated claim verification in a scientific codebase

**A report on one system, with fault-injection results and a list of
what it got wrong.**

Trenten Bryant · `github.com/trentenbryant746-del/atlas3.1`

---

## 1. The claim

This is an engineering report, not a discovery. The claim is narrow:

> In a codebase that publishes results as numbered claims, gating each
> claim's re-verification on a **content-addressed fingerprint of its
> transitive rule dependencies** (i) cuts continuous verification cost
> by roughly four orders of magnitude, (ii) is sound under fault
> injection, and (iii) exposes a cheap structural diagnostic —
> *root depth* — that separates results the rules derive from results
> the rules merely do arithmetic over.

The fingerprinting mechanism itself is old. Nix, Bazel and ccache have
content-addressed dependency graphs; Snakemake and DVC have staleness
tracking for pipelines. What I have not found is the same mechanism
applied at the granularity of a **published scientific claim**, with a
provenance type attached to every input, and with the resulting graph
used as a *diagnostic* rather than only a cache key. Whether that
combination is worth anything is the question I would like help with.

**I am not claiming the domain results are correct.** The substrate is
a rule-based physics and chemistry model; parts of it are well
constrained and parts rest on values I picked. The system's job is to
make the difference legible and machine-checkable. Section 8 is
explicit about where it does not.

---

## 2. Why this arose

The codebase is 33,600 lines across 107 modules. It publishes 47
numbered claims — things like *"the habitable band runs 0.999–1.899
AU"* or *"the fidelity gate opens at 259 K"* — each one a value, a
function that recomputes it, and an expected result.

Two failure modes kept recurring, and neither is caught by tests:

**Stale published numbers.** A rule changes, a number in the write-up
does not. This happened five times before it was automated away. Once,
a README figure ("26 of 28 configurations pay") was simply *typed by
hand* while the code said 21 — no test could catch it because no test
knew the README existed.

**Results that look derived but are not.** A function can consume a
constant, do arithmetic, and return a number with the surface form of a
derivation. One module priced whether a tool "pays for itself" and
returned confident numbers; it stood on exactly one constant and
itself.

Full re-verification is the obvious answer and it cost 77 seconds,
70 of them in the claim checker, which was re-deriving results nothing
could have changed. At that price it stops being run.

---

## 3. Mechanism

### 3.1 Every input carries an epistemic kind

135 registered inputs, each typed:

| kind | meaning | count |
|---|---|---|
| `EXACT` | fixed by definition | 6 |
| `MEASURED` | someone went and found out | 80 |
| `CHOSEN` | nobody measured it; picked so a model would run | 47 |
| `RECORDED` | happened once, contingently | 2 |
| `ENACTED` | happened in a *run*, not in the world | 14 results |

A claim is graded by its **worst** input. `CHOSEN` is not forbidden —
a model that refuses every unmeasured quantity does nothing — but
citing a `CHOSEN`-backed result as derived is. 48 claims carry an input
list; the checker enforces the grading.

`ENACTED` was added late and is the one I would defend hardest. A
simulation output is not `MEASURED` (nobody observed it) and not
`CHOSEN` (nobody picked it). Calling a sweep result "13.9% of universes
carry a toolmaker" *measured* claims a survey of universes. Calling it
*chosen* says somebody picked 13.9. It needed its own word.

### 3.2 The dependency spine is read, not written

`engine/spine.py` recovers a claim's dependency graph by walking the
AST: what a function calls, what those call, out through imports
(including function-local imports, which this codebase uses heavily),
to a fixpoint. Each node is fingerprinted over **its own source text
and its dependencies' fingerprints**, so one 16-byte value commits to
the entire chain beneath a claim.

Hashing *source* rather than *values* is deliberate: a rule can be
rewritten and still return the same number today. Hashing the answer
would miss that.

An earlier version of this walked a **hand-written** list of eleven
stages. That list said what I believed the dependencies were. It could
not say what they were, it silently omitted anything forgotten, and
every new question meant more typing. Deriving it found two bugs
immediately (§6).

Whole-graph cost: **1,772 rules fingerprinted in 26 s, 43 MB, reloaded
in 0.15 ms.**

### 3.3 A worked example

The claim *"the light race stops at 11.4 m"* resolves to
`biome.escalation_stops_at`. Its recovered chain is 19 nodes:

    biome.CROWN_M2                  ca5764695a26eead
    biome.PHOTOSYNTHETIC_EFFICIENCY 217528a4dcab6c8d
    biome.RESP_PER_KG               39b61f615b4ee755
    biome.XYLEM_TENSION             dc824fecba318d96
    life.G_EARTH                    0693c9a2035a7e0e
    life.RHO_WATER                  e957a0e4e29a957f
    biome.hydraulic_ceiling         f9c540e277ba9178
    ... 11 more
    biome.escalation_stops_at       1d7e6a21f337415b   <- the claim

Nobody declared that this claim depends on `life.RHO_WATER`; it does,
through `hydraulic_ceiling`, and the walk found it. Change
`RHO_WATER` and the terminal fingerprint changes, because each node
hashes its dependencies' hashes. Two claims sharing history share
their node fingerprints **exactly** — so consistency between them
stops being something a test asserts and becomes something the bytes
are.

That property is what makes the skip sound. It is also the whole
mechanism; there is nothing else in it.

### 3.4 Claims are skipped, not recomputed

An unchanged fingerprint is a *proof* that recomputation returns what
it returned last time. The checker stores `{claim → (fingerprint,
verdict)}` and skips on a match.

---

## 4. A second use: searches that can return nothing

The same graph exposed a distinction I had been eliding. A gate in the
codebase asked whether a self-maintaining chemical set could exist and
**passed** — by computing whether closure was *likely* under a
probability model. That is a statement about a probability, not about
a set. No set had been built and none checked.

Replacing it with a search changed the answer. `engine/closure.py`
enumerates 254 molecules and 1,284 ligation reactions, assigns
catalysts at probability *p*, and prunes reactions lacking a catalyst
or reactants to a fixpoint — what survives is the maximal closed set,
or nothing.

| p | closes | reactions | molecules |
|---|---|---|---|
| 1e-4 | no | 0 | 6 |
| 1e-3 | no | 0 | 6 |
| 3e-3 | yes | 431 | 221 |
| 1e-2 | yes | 1,171 | 254 |

Sharp threshold, and **the search can return nothing** — which is what
makes returning something mean anything. The measured catalysis
probability in the codebase is 1e-8, five orders below the threshold at
searchable network sizes. Extrapolating the size-scaling to 1e-8 asks
for ~1e20 reactions; that figure is reported **with its distance
attached** (1.2 orders of data, 17 orders of extrapolation) because it
is not trustworthy.

The general point is small but I think real: a check that computes a
*likelihood of existence* and a check that *searches for an instance*
have the same surface form and different epistemic content, and root
depth distinguishes them cheaply.

## 5. Benchmark

Measured on a 10-core M-series laptop, Python 3.9, no dependencies.

| | cold | warm |
|---|---|---|
| claim checker, 47 claims | 70.9 s | **0.0 s** (47/47 skipped) |
| full suite | 77 s | **7.3 s** |
| whole-repo fingerprint | 26.0 s | 0.15 ms |

The residual 7.3 s is interpreter startup and one text-chunking corpus,
not claim verification.

Also in the suite: 406 self-check assertions across 63 modules, 5,737
curriculum items, 165 held-out items. **Caveat in §8: the curriculum is
self-generated, so "0 wrong" is weak evidence and I do not lean on it.**

---

## 6. Fault injection

The benchmark is worthless if the gate is unsound — a fast wrong answer
is worse than a slow right one. Each fault is injected into source, the
caches cleared, and the checker run.

### 6.1 Recall — does a real fault get caught?

| injected fault | claims recomputed | claims failed |
|---|---|---|
| photosynthetic efficiency +5% | 7 / 47 | 3 |
| bone compressive strength +12% | 9 / 47 | 3 |
| ribozyme error rate +20% | 4 / 47 | 4 |
| gravitational constant +0.1% | 6 / 47 | 4 |

**4 of 4 faults detected.** None triggered a full recompute; each
recomputed only its dependent subset.

### 6.2 Precision — does an irrelevant edit stay quiet?

| edit | claims recomputed |
|---|---|
| whitespace in an unrelated docstring | 0 / 47 |
| render resolution (no claim depends on it) | 0 / 47 |
| a constant used by one claim only | **1** / 47 |

### 6.3 Tampering with the ledger

Editing a stored fingerprint and re-running with `verify=True` raises
`SOLID PREFIX BROKE at 'biome.surface_light'` — a frozen node that
recomputes to a different hash is the one error the store exists to
raise.

### 6.4 Root depth as a groundedness diagnostic

Depth of a claim's dependency graph:

    radiative.grey_equivalent_full     37 nodes
    biome.escalation_stops_at          19
    nucleo.mass_bar                    15
    ontogeny.provisioning_debt         11
    atoms.limiting_element              6
    ontogeny.tool_search                2      <- flagged

`tool_search` reached **one constant and itself**. It was arithmetic
wearing the shape of an answer. Rebuilding it so the result derived
from material strengths already in the codebase moved it to **13 nodes**
and changed the answer. This is the diagnostic working, and it is the
part I am least sure generalises — see §8.

---

## 7. What it got wrong

A verification claim is only interesting alongside the error record.
The repository contains **14 superseded published numbers**, each with
a written reason, and **9 checks that were inverted rather than deleted
when their premise turned out false**. In-source markers: 25
"an earlier version", 9 "was wrong", 3 "CORRECTED", 19 open
`MISSING_RULE`s.

**Regressions — mine, caught by the system or by review:**

- A cache keyed on `id(body)`; CPython reused a freed address and moved
  a published result. Caught by the claims checker.
- Two unit errors: pumping power off by 10⁶ (ml vs m³), and a double
  conversion of a value whose own metadata said "53.9 W".
- A sign inversion in an Arrhenius ratio that reported cold as harmful.
- Five self-checks that grepped for a literal they themselves
  contained, and so could never fail.
- A duplicate-constant rule that caught **its own author twice**, within
  minutes of being written.
- A `reach` cap I chose, saturated before the variable under test was
  added — so the experiment measured the cap, not the physics.
- A calibration constant five orders of magnitude off, which made a
  quantity grow 0.007 units in six centuries and hid every limit.
- A claim that 119 unreferenced functions were dead code. Cross-checking
  against an earlier release showed **66 were referenced there** — the
  tree had grown past the call site, not the rule.

**Progressions:**

- Verification cost 77 s → 7.3 s, soundness demonstrated rather than
  asserted.
- The dependency spine moved from hand-written to AST-derived; nuclear,
  atmospheric and biological questions all acquired roots with no
  wiring.
- `ENACTED` added, separating simulation output from measurement.
- Four long-deferred defects fixed, including one real portability bug
  (an audit asserting a backend *count* rather than backend
  *agreement*, so a machine missing an optional runtime reported
  failure while working correctly).

---

## 8. Limitations

Stated plainly, because they bound the claim.

1. **Single codebase, single author, no external replication.** Every
   number here comes from one system that I wrote. The mechanism might
   be overfitted to its own substrate.
2. **No comparison against existing tools.** I have not benchmarked
   this against DVC, Snakemake, `noWorkflow`, or a Nix-based pipeline.
   That comparison is the obvious next experiment and I have not run
   it. It is possible the honest conclusion is "use Bazel."
3. **The curriculum is self-generated.** 5,737 items with 0 wrong
   answers is consistency, not accuracy. I do not treat it as
   validation.
4. **Root depth is a heuristic and is gameable.** Inlining a constant
   shortens a root; adding a pass-through lengthens one. It caught a
   real case, and I cannot show it generalises.
5. **Source-hashing is conservative.** A comment change inside a
   function body changes the fingerprint and forces recomputation.
   Precision in §6.2 held only because the edits were outside dependent
   functions.
6. **The domain content is not peer-reviewed.** 47 of 135 inputs are
   `CHOSEN`. Results resting on them are labelled, but labelling is not
   validation, and a domain expert would likely find real errors. The
   `MISSING_RULE` count is 19 and I expect it to rise.
7. **Python, AST-level, dynamic dispatch invisible.** 32 functions
   dispatched by name at runtime are unreachable to a static walk. The
   system reports this rather than hiding it, but it is a hole.

---

## 9. Related work, and what I am asking

**Where I think this sits.** Content-addressed dependency graphs are
standard: Nix and Bazel hash build inputs, ccache hashes preprocessed
source, Snakemake and DVC track pipeline staleness, and `noWorkflow`
and similar capture provenance from Python execution traces. Two
things here are not in that set, and I am unsure either is worth
anything:

- the unit is a **published claim** rather than a build artifact or a
  pipeline stage, so the ledger maps 1:1 onto the numbers that appear
  in a write-up, which is where staleness actually hurts;
- the graph is used as a **diagnostic** (root depth, §6.4) and not only
  as a cache key.

Provenance systems typically record *how* a value was produced. This
additionally types *what kind of thing* each input is, and refuses to
let a `CHOSEN`-backed number be cited as derived. I do not know whether
that is a real distinction or bookkeeping.

I would value an opinion on three things:

1. **Is the claim-granularity framing worth pursuing, or is this
   reinventing a build system?** I genuinely do not know, and the
   benchmark in §4 does not answer it without the comparison in §8.2.
2. **Is root depth a real diagnostic or a coincidence?** It caught one
   case. One case is an anecdote.
3. **Does the epistemic typing carry weight outside this codebase?**
   `ENACTED` in particular felt necessary here; I cannot tell whether
   that is general or local.

**Reproduction.** Stock Python 3.9, no dependencies, no network.

    git clone <repo> && cd atlas3.1
    python3 -m eval.benchmark      # full suite, ~7 s warm / ~77 s cold
    python3 -m eval.claims         # the 47-claim ledger
    pytest                         # discovers all 406 module checks
    python3 -m engine.spine        # dependency graph and root depths
    python3 -m engine.closure      # the RAF search of §4

Fault injection is three dozen lines: patch a constant in source, clear
the AST caches, re-run the ledger, restore. I can supply the exact
scripts that produced §6.1–6.2.

I would rather be told this is a solved problem than continue not
knowing.
