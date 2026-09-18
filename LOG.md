# Log — regressions and progressions

Running record of what broke, what fixed it, and what moved forward.
Ordered newest first. Every entry here is also in `README.md` at its
version, and every withdrawn number is in `eval/claims.py:SUPERSEDED`
with a written reason.

**Standing counts:** 47 published claims · 14 superseded · 9 checks
inverted rather than deleted · 19 open `MISSING_RULE`s · 406 module
checks across 63 modules · suite 7.3 s warm.

---

## Regressions — found, and how

Grouped by what caught them, because that is the useful axis.

### Caught by an automated check

| what | detail |
|---|---|
| `id(body)` as a cache key | CPython reused a freed address; a published outer edge moved 1.899 → 1.984 AU. **Claims checker.** |
| duplicate constants | Two quantities redefined minutes after the rule forbidding it was written. **The rule caught its own author, twice.** |
| self-grepping checks | Five checks matched a literal they themselves contained, so could never fail. **Meta-check over every module.** |
| infinite recursion | `rules_that_have_never_fired` called `run()`. **Lab.** |
| stale published numbers | Five separate occasions. **Claims checker.** |
| frozen-fingerprint tampering | Editing the ledger raises `SOLID PREFIX BROKE`. **Root store.** |

### Caught by comparison against a known value

| what | detail |
|---|---|
| pumping power ×10⁶ | ml vs m³; gave 6,528% of a human energy budget against a known 1–2 W heart. |
| Kleiber double conversion | The returned `Fact` said "53.9 W" in its own metadata and I converted anyway, shrinking every animal's bill 20×. |
| Mercury "+2.8 K" | Compared a redistributed prediction to a dayside mean. Real error +97 K. Withdrawn. |
| tool count 26 vs 21 | Typed into the README by hand instead of read from the check. No claim was registered to catch it; one is now. |

### Caught by deriving something previously asserted

| what | detail |
|---|---|
| Kleiber applied to a tree trunk | An animal rule on a plant: a trunk is 4% alive at 100 m. Pricing dead heartwood as breathing made a 155-tonne tree cost 1.3 MW. |
| crown tied to height | Made tallness pay for itself with no competitor — it assumed the conclusion. Rule **inverted and kept**. |
| `ENGINE_GAIN` as a learning rate | 1.2%/yr took 450 years to reach a ceiling because it was told to crawl. Efficiency is a material property. |
| a saturated `reach` cap | A cap I chose was already saturated before the variable under test was added, so the experiment measured the cap. |
| calibration 10⁵ too small | Made a corpus grow 0.007 units in six centuries, hiding every limit behind arithmetic that never moved. |
| sign inversion, Arrhenius | Reported cold as *harmful* to persistence. The higher barrier slows more on cooling. |
| food ceiling guessed | 3.5 TW out of the air gave 81 billion people, which is nobody's estimate. |

### Caught by cross-referencing an earlier release

| what | detail |
|---|---|
| "119 functions are dead code" | **66 of them are referenced in Atlas 2.** The tree had grown past the call site, not the rule. Split into lineage / dispatched / stranded: 66 / 32 / 22. |

### Structural errors in my own verification

| what | detail |
|---|---|
| hand-written dependency spine | Eleven stages typed by hand. Replaced with AST derivation, which immediately found two bugs. |
| `_defs` walking function bodies | Bisection locals (`lo`, `mid`, `hi`) appeared as *rules* in a dependency root. |
| linear keying of a DAG | Keyed nodes on their position in one walk; sharing collapsed to 6 of 115. A node's own fingerprint is the key. |
| `ENACTED` made exclusive | Required that nothing be both enacted and input-graded. They are orthogonal axes. **The check failed on its own registry in one run, correctly.** |
| a check pinned to a rule name | Asserted `atoms.standing_crop` was stranded; a later version wired it, so the check failed *because what it watched got fixed*. Now tests the ordering. |
| a condition always true | The Carnot branch fired in year zero of every run once engines started at the ceiling. A condition that is always true is not a finding. |
| audit asserting a count | `len(EXECUTABLE) == 3` made a machine without an optional runtime report failure while working. The claim is that backends *agree*. |

---

## Progressions

| version | what moved |
|---|---|
| 3.1.88 | Four deferred defects fixed. Persistence added as a gate. Self-maintaining set **searched for** rather than priced — and the search returns a refusal with a number: measured catalysis is 5 orders below threshold. |
| 3.1.87 | Fidelity shown to be a **temperature, not a catalyst**. The best ribozyme is at its thermodynamic limit for 298 K. Seven-kelvin window. |
| 3.1.83 | Verification cost 77 s → 7.3 s via fingerprint gating, **soundness demonstrated by fault injection** rather than asserted. |
| 3.1.82 | Root depth 2 → 13 for a claim that was arithmetic wearing the shape of a derivation. |
| 3.1.78 | `ENACTED` added as a fifth epistemic kind. |
| 3.1.75 | Whole dependency graph held in 43 MB, enabling repository-wide questions a partial walk could not ask. |
| 3.1.72 | Dependency spine moved from **hand-written to AST-derived**. Nuclear, atmospheric and biological questions all acquired roots with no wiring. |
| 3.1.69 | Matter conservation enforced across every life module; `O2_PER_C` stopped being `32/12` typed by hand. |
| 3.1.63 | Claims graded by their worst input. |

---

## Set aside

**3.1.79–3.1.86, the human line** — civilisation, empire, industrial
revolution, schooling. Retained and still checked, but not the
direction of work. What carried over: `ENACTED`, fingerprint-gated
claims, and the habit of marking what was handed over rather than
derived.

## Open

- 19 `MISSING_RULE`s, including: nothing purges a deleterious mutation;
  nothing prices a shared educational foundation; a trophic level is
  treated as a species rather than a guild.
- Venus CO₂ ceiling — needs an H₂SO₄ saturation curve; the derivation
  chain fails because ε ∝ σ⁻⁶ exponentiates through Clausius–Clapeyron.
- Climate manifestations REFUSED — four bodies, one blocked.
- No comparison against Nix / Bazel / DVC / Snakemake. **This is the
  most important open item** and it bounds the paper's claim.

## 3.1.109 — senses, transitivity, compounding, diffusion

PROGRESS
- senses.py extended past eyes: five senses, non-overlapping, reach
  8 of the 13 human constraints. 5 reach none and must be inferred.
  38% inferred on a human, 33% on a bacterium — the derived role of
  a brain over a sense organ.
- tradition.py: transitivity stated as a rule (14 facts per fact),
  WITH its counterexamples held rather than assumed away.
- compounding derived, not assumed: oral r=0.99988 (8692a) vs
  epigenetic r=0.71 (3.4a). 2,546x. Culture compounds, genes echo.
- diffusion: 16 bands is the optimum band count and nobody chose it.
- chain 37 -> 41 links, 29 -> 33 derived. Still 0 gaps, 1 crossing.

REGRESSION FOUND AND FIXED
- lineage._gaps read only MISSING, so it tripped on "the chain
  claims to be complete" while a CROSSES link sat unexplained. An
  inverted check that could not see half its own evidence. Now
  counts crossings as named gaps and still fails if both hit zero.
- accident's farming/alcohol discrimination was 13 days against a
  73-day threshold — too thin to publish alone. Diffusion supplies
  an independent 6x cut (182-day rendezvous gap). Kept both.

SUPERSEDED
- "37 links, 29 derived" -> 41/33. Not wrong, short. One of the four
  new links closed an unstated jump (recognition -> one head) rather
  than extending the end.

STILL OPEN
- innovation.useful_fraction() = 1.1e-4 unmeasured, still carries
  the hominin timing.
- tradition's TELL_SECONDS, EVENING_SECONDS and MEETINGS_PER_YEAR
  are CHOSEN. The 2,546x gap survives any plausible choice; the
  8,692 figure does not.
