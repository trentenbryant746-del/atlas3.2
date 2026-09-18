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

## 3.1.110 — telephone error, band pace, specialization depth

PROGRESS
- TELEPHONE = 0.10 per retelling, corrected by majority consensus.
  1 holder -> 10 items. 28 holders -> 8,688. The band IS the error
  correction, not the audience.
- craft.py: pace from the inverted pendulum. Band walks at the
  child, 0.707 of adult. Hazards per day, forage per km, so slowness
  concentrates problems 1.41x per km. 39x kept innovations per km
  over a lone adult, with the unmeasured solve rate cancelling.
- specialization depth derived: 2 specialties 13 deep, 9,332a. Set
  by fidelity and headcount, NOT by how many skills exist.
- chain 41 -> 43 links, 33 -> 35 derived.

REGRESSION FOUND AND FIXED
- retention("oral") charged for tellings not given and nothing for
  tellings given wrong. An entire failure mode of the mechanism was
  missing from the model of the mechanism. Cost: 4 items on the
  stock, but the LONE-teller case was wrong by 870x and had never
  been computed because holders was not a parameter.
- claims.py conflated oral CAPACITY (8,692, a coupon-collector
  inversion) with oral STOCK (8,688, capacity times fidelity). Same
  number to three figures, different quantities. Caught on the
  supersede, not by a check.

SUPERSEDED
- oral stock 8,692a -> 8,688a (telephone now charged).
- chain 41/33 -> 43/35.

STILL OPEN
- TELEPHONE = 0.10 is CHOSEN and the specialization optimum moves
  with it: at 0.01 the answer is 5 specialties, not 2. The
  QUALITATIVE result (a bottom exists, set by fidelity) survives any
  value; the 13-deep figure does not.
- LEG lengths are CHOSEN. The sqrt ratio is not.
- innovation.useful_fraction() = 1.1e-4 still unmeasured.

## 3.1.111 — literacy, disease, power

PROGRESS
- literacy.py: the exemplar IS the check. One copyist with three
  proofreads = 13 speakers. Buys 9 specialties instead of 2.
  Bootstraps orally, so 5 scribes or the script is lost. Spread is
  df/dt = r f^2 (1-f), NOT logistic: 4% -> 34% in 500 years.
- disease.py: crowd disease derived from settling, not assumed.
  Critical community 912; a band of 28 kills the pathogen. Cooking
  58x, wall 53 days of food a year.
- power.py: a granary's border is 909x shorter than the range's.
  Concentration still only 1.9x flat, 3.5x behind a wall. Writing
  extends a claim past its witnesses, which is inheritance.
- chain 43 -> 47 links, 35 -> 39 derived.

REGRESSION FOUND AND FIXED
- power._flat compared spare_per_head against bare zero and tripped
  on 1.1e-14 J. A correct check with an unstated tolerance on a
  difference of gigajoule terms. Now names the noise floor.
- literacy.spread was plain logistic on first write, saturating in
  200 years. Wrong mechanism: growth tracks the VALUE of the
  channel, which is f^2, not the number of teachers. Corrected to
  df/dt = r f^2 (1-f) and it now crawls for a millennium.

COINCIDENCE, LOGGED SO IT IS NOT MISTAKEN FOR A RESULT
- defensibility() = 909 and critical_community() = 912. Agree to
  0.3%, unrelated quantities (a perimeter ratio and a susceptible
  supply). Nothing connects them.

STILL OPEN
- PROOF_CATCH, WALL_ADVANTAGE, EDIBLE_FRACTION, SHELTER_GAIN_K,
  FIRE_EFFICIENCY all CHOSEN. Cooking's 58x survives any plausible
  value (it is two orders clear). The 3.5x walled concentration
  does not -- it is linear in WALL_ADVANTAGE.
- TELEPHONE = 0.10 still sets the specialization depth.
- innovation.useful_fraction() = 1.1e-4 still unmeasured.

## 3.1.112 — scarcity, inheritance drift, the technology loop

PROGRESS
- merit.py: power is value/holders, and the skill's usefulness does
  not enter. Collides with craft.py's 5-holder survival floor: 5x
  power for a twelfth of the lifetime. Lost crafts are an incentive
  problem, not an accident.
- hereditary drift derived: selection gives 2.58 sigma, inheritance
  gives 0.08 by g5, holding is 32x the ability. Randomization is a
  real tail: 1 in 15 at g1, 1 in 162 at g5.
- intricacy.py: designs = 2^s - 1. Speech is a FIXED POINT at 2
  specialties, not an early stage. Writing moves the binding
  constraint from fidelity (unfixable from inside) to spare labour
  (fixable by yield). Loop settles at 24 parts, 10.1x yield.
- chain 47 -> 50 links, 39 -> 42 derived.

REGRESSION FOUND AND FIXED
- literacy.spread had no floor and no ceiling. f^2 alone put one
  literate in 912 at 20,000 years to saturation. Added the
  administrative floor (1/BAND, derived from power.py) and the food
  ceiling (spare labour from the surplus). Shape was right, both
  ends missing. Published 34%@500y -> 10%.
- tradition.garbles overflowed float via math.comb above ~1000
  holders. Never triggered while everything was band-sized; the
  moment populations became villages it raised OverflowError.
  Rewritten in log space with lgamma. The check caught it by
  crashing, which is the correct failure.

STILL OPEN
- YIELD_PER_SKILL = 1.10 is CHOSEN and the fixed point is sensitive
  to it: the 24-part settle moves with it. The CONVERGENCE does not
  -- log corpus against exponential designs holds at any value.
- SURPLUS_RATIO, COPIES_PER_YEAR, COPY_LIFE_YEARS, PROOF_CATCH,
  WALL_ADVANTAGE all CHOSEN.
- HERITABILITY = 0.5 sets the 32x; the DIRECTION (claim perfect,
  ability regressing) does not depend on the value.
- innovation.useful_fraction() = 1.1e-4 still unmeasured.

## 3.1.113 — trade, network scale, and a named gap

PROGRESS
- trade.py: a porter eats the cargo. Grain doubles in price at 258
  km, arrives as nothing at 516. Knowledge is the ONLY cargo with
  no range limit and no loss on transfer.
- settling put villages 5.2 km apart vs a band's 9 km: 22 meetings
  a year instead of 2, diffusion across 40 villages in 6.8 years
  instead of 74.
- network of 40 villages = 36,480 reachable people: 12,160
  specialties vs 304, 2.4x output per worker (Wright). Loop fixed
  point 24.3 -> 29.7 parts.
- chain 50 -> 52 links.

GAP OPENED, DELIBERATELY
- per-capita surplus scales as N^-0.628. Total output rises
  everywhere in the module and NONE of it lands per head. Supply
  exponents sum to 0.372 against mouths at 1.0.
- Registered as the chain's first MISSING link since 3.1.95:
  "a region in touch -> anyone actually better off".
- intricacy._malthus is INVERTED: it fails if the loop ever makes
  anyone richer, because that would mean an assumption had been
  smuggled in. The correct output of the model as built is
  stagnation, and saying so is the result.

STILL OPEN
- the Malthus gap above. Nothing on this chain closes it.
- LEARNING_RATE 0.85 is MEASURED but PORTER_KG, WALK_HOURS,
  PORTER_MJ_DAY, FARM_EDIBLE are CHOSEN. The 258 km doubling moves
  with them; the EXISTENCE of a finite range does not -- it follows
  from cargo and fuel being the same substance.
- YIELD_PER_SKILL 1.10 sets both the fixed point and half the
  Malthus exponent. At 1.6 the exponent would still be negative.
- innovation.useful_fraction() = 1.1e-4 still unmeasured.

## 3.1.114 — non-rivalry, the food cap, tools, and the mean

REGRESSION FOUND AND FIXED — the big one
- the "Malthus gap" of 3.1.113 was MY ARITHMETIC, not the world.
  per-capita exponent subtracted mouths at N^1 from two terms that
  were already per-worker. Every invention was counted as though
  divided among its users. A design is non-rival: not divided.
  Corrected N^-0.628 -> N^0.072, crossover at a 0.372 land share.
  A gap I opened deliberately and loudly turned out to be a bug,
  which is the strongest argument for opening them loudly.
- yield_ratio compounded over EVERY specialty to 40x subsistence.
  A potter does not raise grain yield. Capped at FOOD_SKILLS = 8:
  2.14x, 53% sparable. Knock-on: every downstream number moved.

PROGRESS
- non-rivalry stated as a rule with its converse: an invention
  costs C once and returns b to each of N, so the threshold worth
  inventing is C/N and falls with population.
- capital.py: a specialty is a toolkit. 24% of possible specialists
  priced out. Optimum concentration is S/K = 368 of 912; walled
  holders sit below it, so concentration is IDLE CAPITAL.
- intricacy would price people out of their own crafts in a village
  that did not trade; Wright's law on the network reverses it.
- income_stats INVERTED: fails if mean ever equals median. Mean
  1.33x median, top 14x median. Per-head figures are first moments.
- chain 52 -> 54 links, gap closed, 46 derived.

STILL OPEN
- LAND_SHARE 0.30 is MEASURED-ish and sets the sign of the escape.
  The CROSSOVER (0.372) is derived and does not depend on it.
- DAYS_PER_PART 50, TOOL_LIFE_YEARS 10, FOOD_SKILLS 8 all CHOSEN.
  The 24% tooling loss moves with them; its EXISTENCE does not.
- income_stats models depth spread as uniform 1..2k-1. The repo has
  no measured distribution of craft depths. The skew is real, the
  14x is a shape assumption.
- innovation.useful_fraction() = 1.1e-4 still unmeasured.

## 3.1.115 — novelty, and transcription

PROGRESS
- novelty.py: design space is LINEAR in population (2^s with
  s=log2(corpus) cancels), so it is used up and refilled at once.
  Steady state depends on population GROWTH, not size: no growth
  exhausts the space at any size.
- the multiple: novelty per head 0.80, total 32x, going 912 ->
  36,480. Each person invents 20% less, the world gets 32x more.
- mechanism named honestly: exhaustion does NOT do it (99.7% of
  trials still novel). The TEAM does -- p parts need p holders and
  p is log(corpus).
- tools/transcribe.py: the whole record as one readable document,
  every sentence produced by the rule it describes. 5,429 lines.

REGRESSION FOUND AND FIXED — by transcription, not by a claim
- ecology.competition_prevents_the_collapse was TRUE WHEN WRITTEN
  and false since descent.py's unbounded-fitness bug was fixed.
  With the closure floor in place a solo lineage holds at 1.76 um;
  there is no collapse. Competition takes the median DOWN to 0.64
  and produces a RANGE. Restated, not patched.
- power._claim demanded 5x reach, calibrated against an uncapped
  literacy spread. The food ceiling dropped it to 3.4x. Headcount
  was the wrong measure for a claim about outliving; now measured
  across generations.

GAP IN THE VERIFICATION ITSELF, NAMED
- 550 module checks exist against 81 claims. The fingerprint gate
  only recomputes CLAIMS, so a check no claim depends on can fail
  silently for versions. Both bugs above were red and unobserved.
- Transcription is the only full sweep. It is deliberate, not
  automatic, because running 90 modules is exactly the CPU spike
  that is not wanted on every change.

CORRECTED IN PASSING
- the novelty ratio is log2(corpus1)/log2(corpus2) = 0.80, not
  log2(n1)/log2(n2) = 0.65. Using population overstates it 19%.

STILL OPEN
- TRIALS_PER_HEAD_YEAR 0.01, POP_GROWTH 0.001, SPECIALTIES_PER_HEAD
  1.0 all CHOSEN. The 0.80 multiple depends only on the corpus
  logarithms; the 99.7% novel fraction depends heavily on trials.
- innovation.useful_fraction() = 1.1e-4 still unmeasured.
