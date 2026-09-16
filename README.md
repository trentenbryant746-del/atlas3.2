# atlas2

A question-answering system where **every answer carries the check that
would catch it being wrong**, and anything that cannot be checked is
refused rather than guessed.

    from atlas import ask, why

    ask("what day of the week is 2026-09-15")      # date algebra
    ask("convert 100 km/h to meters per second")   # dimensional algebra
    ask("Evaluate: ((3 + 4) × 5) - 6")             # compositional parse
    ask("subtract 20 from 327")                    # rule via phrasing
    ask("What element has atomic number 79?")      # expert, table round-trip
    ask("...", index=idx)                          # grounded extraction

Every answer reports its mechanism, check kind, provenance and token cost.
Every refusal reports the reason from each layer that was tried.

---

## 1. The one idea

Answers split by **how they can fail**, and that decides everything else:

| kind | can be wrong if | generation |
|---|---|---|
| `DERIVED` | the rule is wrong — and the check catches that | unlimited |
| `DERIVED_UNCHECKED` | same, but nothing catches it | safe, flagged |
| `ASSERTED` | the *source* is wrong, and nothing internal can tell | **refused** |

A derived answer is reproducible from a rule. An asserted one is a claim.
Generating a million derived answers costs nothing and risks nothing;
generating one asserted answer **invents a fact**.

The predecessors each had only one kind and so could not see the line:
belt-atlas was entirely asserted (ceiling 70% on real questions, nothing
checkable); the Codex curriculum was entirely derived (inflated to 640,000
records that taught nothing).

### Check kinds

What varies between domains is not the rule form but **where the second
derivation comes from**:

    INVERSE     run it backwards            137 - 78 == 59
    IDENTITY    round-trip is the input     reverse(reverse(s)) == s
    REDUNDANT   a second algorithm          Zeller vs calendar arithmetic
    ENUMERATE   exhaust a finite space      syllogism over all models
    EXTERNAL    an outside validator        Godot / Python's own parser
    SPAN        verbatim in a source        grounded extraction
    NONE        no derivation exists        asserted; cite it

`eval/controls.py` sabotages every derived rule. All caught.

---

## 2. Four type systems

Each refuses a different kind of nonsense, **structurally** — before any
computation runs — and they are independent of each other.

| system | refuses | example |
|---|---|---|
| dimensional | unlike quantities | `add(length, time)` → None |
| conservation | unbalanced quantum numbers | lone proton, Q=+1 |
| causal (epoch) | effects before causes | gold before neutron-star mergers |
| addressing (keys) | questions outside a window | `capital of France` inside a code artifact |

Measured over every (element-pair × epoch) binding:

    dimensional   refuses    0 / 1680     (both are masses)
    conservation  refuses    0 / 1680     (both are neutral)
    EPOCH         refuses 1263 / 1680     (75%)

Epoch is not a refinement of the others — it refuses a space they cannot
touch. And the possibility space **opens over time**: 5% of element pairs
at BBN, 17% at stellar carbon, 65% at supernova, 100% after mergers.

---

## 3. The cascade

`atlas.py`. Ordered by **how precisely a layer determines that it owns the
question** — not by specificity.

    1  dates        "2026-09-15" is a valid subtraction to a number parser
    2  units        "100 km/h" contains a division sign
    3  experts      dna, periodic table, materials, seeded worlds
    3b game builder when asked to build one
    4  arithmetic   compositional, unbounded, EXACT
    5  nl rules     keywords + operand count — loose, so last
    6  grounded     extraction from supplied context
    7  abstain      with every layer's reason

**Terminal refusals.** "Not my question" continues the cascade; "your
question is malformed" stops it. Conflated, `convert 5 meters to kilograms`
was refused by units on dimension mismatch and then answered `500` by a
rule matching the words.

Both obvious orderings were measured and both failed:

    general arithmetic first  evaluated a span inside "Solve for x: -9x +
                              -6 = -348" and returned -348.   875/5737 wrong
    all rules first           NL layer saw 4 operands and "evaluate" in
                              "(3 + (4 × 5)) - 6", answered 29 not 17.
                              101/422 wrong

---

## 4. Learning

### Rule induction — `induce.py`, `induce2.py`

Bottom-up enumerative synthesis over a primitive basis, pruned by
**observational equivalence**: one representative per distinct value-vector
across the training examples.

    9 curriculum rules, induced from 6 examples each:  5683/5683 held-out
    8 operations absent from the corpus:               200/200 each

Two came out better than the hand-written versions — `fracadd` as
`a/b + c/d` rather than `(ad+cb)/(bd)`.

**Meet-in-the-middle** (`induce2.py`) looks for the complement of each
stored expression instead of enumerating to the answer:

    rule       bottom-up   meet-in-middle   speedup
    pct            7.8s           0.0s        1415x
    fracadd       36.4s           0.0s        3041x
    compound      37.9s           0.1s         749x

### Pattern induction — `pattern.py`, `discover.py`

Recovers templates from raw text by anti-unification, then composes with
rule induction:

    5,737 unlabelled (prompt, answer) pairs
      -> 9 templates recovered, 5737/5737 coverage, no cross-matching
      -> 9 complete rules
      -> 5683/5683 held-out

No regexes, labels or rule names supplied.

### Finding new atoms — `newatom.py`

The search found Kepler only because `sqrt` was handed to it, and returns
the same nothing when no law exists. Three signals separate the cases:

    dataset            R^2      |resid|   sign runs / expected
    Kepler        0.999999        0.15%      3 / 4.5   random
    Z -> mass     0.997578        2.41%     17 / 42.5  systematic
    noise         0.145           44.8%     13 / 15    random

R² separates noise; the **residual** separates law from trend; the **run
count** shows whether the form is systematically wrong.

    Kepler         BASIS SHORT (verified)   x^1.5   size 3:  1 fit,  1 held-out
    Z->mass        TREND, NOT A LAW
    noise          NO LAW
    y = 3x+7       EXPRESSIBLE, BUDGET TOO SMALL
    y = 2e^(x/2)   BASIS SHORT (verified)   exp     size 7:  4 fit,  4 held-out
    y = 4ln(x)+1   BASIS SHORT (verified)   log     size 9: 56 fit, 56 held-out

A proposed atom is added to the basis and the search re-run. One that does
not make the law findable is `PROPOSAL UNVERIFIED`, not a discovery.

### Grammar — `grammar.py`

Recognition without templates. Language is compositional the way chemistry
is, so the grammar is written exactly like the dimensional typing:

    bind("add", length, time)  -> None    dimensions disagree
    combine(DET, VERB)         -> None    categories disagree

    42 words, 17 rules, unbounded sentences
    8/8 grammatical parsed, 3/3 ungrammatical refused

Syntax is compositional and this handles it. **Reference is not** — parsing
"what is the statute of limitations in California" yields a correct tree
and no answer.

### How far more rules get you — measured

`grammar2.py` scales it to **209 words, 49 rules**. Coverage and ambiguity
were tracked as the rule set grew:

    rules   coverage   precision   mean ambiguity   max
       12     0 / 10      7 / 7            0.0       0
       19     4 / 10      7 / 7            1.2       2
       26     4 / 10      7 / 7            2.5       5
       34    10 / 10      7 / 7            2.5       5
       41    10 / 10      7 / 7            3.3       9
       49    10 / 10      7 / 7            3.3       9

**Coverage saturates at 34 rules. Ambiguity keeps climbing after it.**
Past that point a new rule buys parses, not understanding.

And ambiguity does not grow gently. Prepositional attachment, all words in
the lexicon:

    1 PP      3 parses
    2 PPs     9
    3 PPs    28
    4 PPs    90
    5 PPs   297

That is the Catalan explosion, and **no amount of rule-writing fixes it,
because every one of those parses is grammatical.** Choosing among them is
not a grammar problem.

Applying the dimensional type system to the parses — `the distance of the
year` is grammatical and dimensionally absurd — prunes **42 of 297, 14%**.
Real, and nowhere near enough. Resolving the rest needs either full
semantics or statistics over actual usage, which is the wall every
hand-written grammar has hit.

SO: write rules until coverage saturates, then stop. For this lexicon that
was ~34. The next gain is not a fiftieth rule.

### Tying each grammar rule to the system's own rules — `grammar3.py`

The fiftieth rule is not the next gain. Putting the SEMANTICS INSIDE the
rule is. Every rule becomes a pair:

    (catA, catB) -> (catC, action)

and `action(semA, semB)` returns a meaning or **None**. None kills that
branch mid-parse, so an ill-typed combination never grows a subtree.

Same syntax in both columns; the only difference is when the check runs:

    sentence                                          syntax   +sem  pruned
    what is the distance of earth                          2      2      0%
    what is the distance of earth of mars                  9      0    100%
    ... of the star                                       34      0    100%
    ... of the sun                                       157      0    100%
    ... of the moon                                      788      0    100%

    post-filtering after the parse (grammar2)   prunes  14%
    checking inside the rule     (grammar3)     prunes 100%

Same information, different moment. Filtering afterwards must build all
788 parses first; checking inside the rule kills the branch before it can
combine, so **the explosion never happens.**

AND THE PARSE IS NO LONGER A TREE. It is a call:

    "what is the mass of earth"  ->  Query(mass of earth), dim (0,1,0)

Legitimate questions still yield two syntactic derivations — and both
denote the SAME call, so the sentence is semantically unambiguous even
where the parser found two trees.

This is the recognition problem — which expert, which arguments — solved
compositionally rather than by matching a template. It does not touch the
derived/asserted boundary: the call is built, and the expert still has to
know the fact.

---

### English all the way through — `english.py`

The two halves existed and were not joined: grammar3 turned a question
into a call and nothing routed it; explain.py narrated a derivation and
only knew arithmetic. Joined, one English sentence now produces the call
it was understood as, the answer, the check that was applied, the
provenance, and all of it back in English.

The point is not that it speaks English. It is that **the explanation says
which of the two ways the answer is right**, and a reader can tell them
apart without reading any code:

    Q: convert 6371 km to meters
       [DERIVED] check: INVERSE + REDUNDANT
       The answer is 6371000.
       This is DERIVED, not quoted: computed from the scale factors, and
       the dimensions had to match before any arithmetic ran.
       Two checks were applied. Converting the result back returns the
       input exactly, and routing through SI base units by a separate
       path gives the same number. If either disagreed you would get
       nothing instead of this.

    Q: what is the radius of earth
       [ASSERTED] check: SPAN-IN-SOURCE
       The answer is R 6371 km.
       This is an ASSERTED fact, not a derived one: nothing computes the
       radius of earth, so it is quoted from a source.
       The source says: "Earth's mean radius is 6,371 km..."
       The check is SPAN-IN-SOURCE -- the answer appears verbatim in the
       source, which verifies faithfulness, not truth.

Both answers are correct. Only one of them is *checkable*, and the
explanation is where that becomes visible to a person rather than to a
test suite.

    what is the mass of the year   -> "I could not read that as a question
                                       about a quantity."
    what is the flurb of earth     -> "I do not know the word 'flurb'."

### Every derivation in English — `narrate.py`, `accounts.py`

`explain.py` narrated arithmetic and checked itself by replaying the
narrated steps. Everything else produced numbers and no account. The
generalisation is a DERIVATION RECORD: an ordered list of steps, each
carrying what was done, why it follows, whether it is measured or derived,
and a closure that recomputes it.

One narrator renders any record. Fidelity is checked the same way — by
re-running the narrated steps:

    Why is a quarter of the universe helium?

    1. take the neutron mass          = 1.00866 u   [measured]  CODATA/NIST
    2. take the proton mass           = 1.00728 u   [measured]  CODATA/NIST
    3. subtract them, in energy units = 1.29333 MeV
       because the neutron is heavier, and that difference is the whole
       reason protons outnumber neutrons
    4. take the weak freeze-out temperature = 0.8 MeV  [measured]
       source: the result is sensitive to it (0.75 gives 0.233, 0.85 gives 0.278)
    5. form the ratio exp(-dm/kT)     = 0.19856
    6. allow for neutron decay        = 0.146934
    7. convert to a mass fraction     = 0.256221
       because every surviving neutron ends up in helium-4 and brings a
       proton with it, so the helium mass is twice the neutron mass

    Answer: 0.256221   Observed: 0.245   (error 4.6%)
    Every step re-executed: 7/7 reproduce their stated value.

Each step declares its own kind, so a MIXED chain says exactly which links
are computed and which are quoted — primordial helium is 4 derived steps on
3 measured ones.

    negative control: corrupt any narrated value and the step is reported
    UNFAITHFUL. Caught in all three accounts.

An explanation that cannot be re-executed is prose, and prose is not
evidence.

Wired into the English layer, so a "why" question returns the derivation:

    why is a quarter of the universe helium   -> the chain above
    why does fusion stop at iron              -> the iron-peak search
    why does fusion release 26.7 MeV          -> the mass-defect chain

Routing picks the LONGEST matching cue and abstains on a genuine tie --
"why does fusion stop at iron" contains both "fusion" and "iron", and
table order answered it with the wrong derivation until specificity
decided it.

## 5. Physics

Nothing below is a stored astrophysical fact. Each is computed from the
particle masses and Weizsäcker coefficients in `particles.py`.

    4 H -> He4               26.73 MeV    accepted 26.73    error 0.01%
    3 He4 -> C12              7.271 MeV   accepted  7.275   error 0.1%
    primordial helium Y_p     0.256       observed  0.245
    iron peak                 Z=26 A=58   actual Fe-56 / Ni-62
    atomic masses given (Z,N) median error 0.22% from 8 numbers

**Gell-Mann-Nishijima** `Q = I3 + (B+S)/2` holds for 7/7 hadrons; leptons
are marked not-applicable; a fabricated particle is caught.

**Spin does not add.** Q, B, L, S, I3 are additive. Angular momentum is a
vector, so only the *statistics* follows: hydrogen-1 boson, deuterium
fermion, helium-4 boson — which is why helium-4 goes superfluid.

### Cosmology — `cosmos.py`

    mass conservation      ejecta + remnant = progenitor    every event
    monotonic enrichment   metallicity never falls          true
    epoch compliance       no element predates its epoch    0 violations
    convergence            distance to observed solar        0.0012

400 seeded universes: H spans 0.7295–0.7367 (solar 0.7346), metallicity
0.0133–0.0205 (solar 0.0166), all within 5%.

**The dilution factor was fitted**, so that agreement is a fit. What was
*not* fitted is the yield table — so the informative part is the residual:
oxygen low, iron high, consistently. Fitting dilution on each element alone
gives 4.0–5.5 for five of them and **8.0 for iron**, which localises the
error to the iron yield; scaling it by 0.62 unifies them.

---

## 6. Generation

### Games — `games.py`

English → picks → a runnable game, checked by **execution**:

    parses · round-trips to the picks · runs headless ·
    invariants every tick · reproducible from the seed

All five sabotaged, all five caught.

**The English layer is the ceiling**, measured: `"20x10 grid, collect 5
coins"` yields 4 decisions; `"a relaxing puzzle where you help a lost cat
find its way home"` yields **0**, and silently produced the default game
until `matches_request` was separated from `ok`. Unmet intent is reported
by kind — aesthetic (not derivable: fun is empirical), referential (fixable
by a fetch), narrative (fixable by extending the pick language).

### Code — `ir.py`, `codeindex.py`

One IR, three **executable** backends, and they check each other:

    python    6|5|4|6|5|4|6|5|4
    ruby      6|5|4|6|5|4|6|5|4
    gdscript  6|5|4|6|5|4|6|5|4      agree

    negative control, gdscript sabotaged alone:
    gdscript  6|4|7|5|6|4|7|5|6|4    CAUGHT

Every emitted line carries `atlas:<id>`; the same token labels the
corresponding line in all three languages and the shape in a Godot scene.

Growth is driven by **behavioural novelty**, not program count — a program
whose trace already exists is discarded however different its source.

### Generating over asserted facts — `epistemic.py`

Restricted so it cannot invent: the answer must be a verbatim span, the
question may use only the source's vocabulary.

    507 pairs, 507/507 answer-verbatim and question-in-window,
    507/507 round-trip through the grounded extractor

**Faithfulness is not usefulness.** The first version produced *"what is
the answer bryant built"* — every token from the source, and not a question.

---

## 7. Grounding and scale

A fact alone is not a function of the question. A fact **with its source in
context** is, and the function is extraction. What becomes checkable is
*faithfulness*, not truth.

    ANSWERED     verbatim span, offset recorded
    UNGROUNDED   nothing in the context answers it
    INVENTED     an answer NOT in the context

Over belt-atlas's 350 facts, retrieve-then-ground gives **235 correct, 0
wrong, 115 declined** — the same headline as its 70%, with none of the
confident wrong answers.

### 10M tokens

    whole prompt      10,002,398 tokens  ->  56.8 DAYS prefill
    chunked+grounded         956 tokens  ->  477 s      (~8,900x)
    retrieval                               0.10 ms
    verified                                400/400, 0 invented

The first run returned 25 INVENTED — **25 fact sentences cut by a chunk
boundary**. 25% overlap took it to 400/400. The verdict diagnosed its own
fix.

### Web ingestion — `ingest.py`

Allowlisted hosts, checked on the **parsed hostname** (a substring test
accepts `evil.com/?q=.gov`). Every answer carries url, date and hash.

The source often tags itself: NIST marks the speed of light `(exact)` →
STIPULATED, and gives the electron mass an uncertainty → EMPIRICAL.

Fetched text is **data**. Nothing executes or routes from page content.

---

## 8. Everything measured

    curriculum answered correctly          5737 / 5737
    induction held-out                     5683 / 5683
    external held-out benchmark             165 / 165
    must-refuse                               6 / 6
    periodic table                          118 elements
    Gell-Mann-Nishijima                       7 / 7 hadrons
    4H->He4                               26.73 MeV (0.01%)
    iron peak element                      Z = 26
    mass conserved, every universe          true
    universes genuinely differ              true
    distance to solar                      0.0012
    chain verify / tamper detect            true / true
    three backends agree                    true
    grammar                                 8/8 parsed, 3/3 refused

`python3 eval/audit.py` re-derives all of these and fails on disagreement.
**21/21 verified.**

---

## 9. What is still true at the edges

**Fitted, not predicted.** The dilution factor. More observables — α-element
ratios, age-metallicity — would turn it into a prediction or break it.

**Seeded is not realistic.** A generator's *support* is set by its form, not
its seed count. `seeded_mixture` confines every component near 1/N, so
solar hydrogen (0.735) is not improbable there, it is **arithmetically
unreachable** — 2²⁵⁶ = 1.16e77 draws changes nothing. The fix is to seed the
**inputs** and derive the outputs, which `cosmos.py` does.

**Recognition is partial.** Compositional domains are unbounded. The grammar
extends that to syntax. Reference still needs a source.

**Fun is empirical.** The game builder makes things that run. Whether anyone
wants them is measured, never computed.

**Faithfulness is verifiable; truth is a citation.** The system can prove an
answer is a verbatim span of its source. Whether the source is right is
outside anything here.

---

## 10. The UI

    python3 ui/server.py          then open http://localhost:8765

Two panes, no dependencies. **Ask** anything on the left: the answer comes
back tagged with its kind (DERIVED / ASSERTED / DERIVATION / ABSTAINED),
the check that was applied, and the full English account where there is
one. **Godot generation** on the right renders an induced compound as the
atom tree, each node labelled with its provenance token — the same id that
labels the corresponding line of Python, Ruby and GDScript.

Two buttons run the real thing rather than a picture of it:

    Run Godot round-trip    loads the generated .tscn in headless Godot and
                            checks the recovered structure matches
    Check three backends    compiles the IR to python, ruby and gdscript,
                            runs all three, and requires identical traces

## 11. Running it

    python3 eval/audit.py            all 21 headline claims, re-derived
    python3 eval/integration.py      every corpus + cross-layer disagreement
    python3 eval/gate.py             the 5,737-record curriculum
    python3 eval/controls.py         sabotage every check
    python3 eval/compress.py         the 9 -> 4 primitive claim
    python3 eval/induction.py        leave-one-out rule induction
    python3 engine/discover.py       raw pairs -> complete rules
    python3 engine/codeindex.py      cross-verified code index (--limit 0 for all)
    python3 engine/generate.py       generation governed by check kind

### Setup

    python3 tools/get_godot.py       fetch + verify Godot 4.7.2  (optional)
    python3 eval/audit.py            expect 21/21

Python 3 only; no packages. Two optional runtimes each ADD a verification
path and are degraded-gracefully if absent:

    ruby    second executable backend for cross-verification
    godot   third executable backend + the scene round-trip

WHY GODOT IS NOT IN THE REPO. The macOS build is 162.7 MB and **GitHub
rejects any file over 100 MB outright** -- not a warning, a refused push.
Git LFS would accept it and then put a 163 MB pull on every clone against
a bandwidth quota, for a platform-specific artefact that goes stale.

`tools/get_godot.py` pins the version and its SHA-512 instead, so one
command gives you byte-for-byte the build that produced every gdscript
number here. A hash mismatch deletes the download and exits non-zero
rather than proceeding.

    python3 tools/get_godot.py           fetch, verify, unpack to vendor/
    python3 tools/get_godot.py --check   report what is present
    python3 tools/get_godot.py --where   print the binary path

It searches `ATLAS_GODOT`, `vendor/`, `/Applications`, then `~/Downloads`,
so an existing install is found and not re-downloaded. Without Godot,
GDScript is emitted and reported as unverified rather than counted as
passing, and every other check still runs.

`README-log.md` holds the development narrative — every measurement in
order, including the failures and what each one corrected.
