# What actually catches errors in scientific code?

**A labelled corpus of 25 faults from one codebase, each tagged with
the mechanism that found it — including 7 in the checking apparatus
itself.**

Trenten Bryant · `github.com/trentenbryant746-del/atlas3.1`

---

## 1. The claim

> Scientific codebases fail in characteristic ways, and there is very
> little labelled data about *what catches the failures*. This is a
> corpus of 25 dated faults from one 33,600-line scientific codebase,
> each annotated in-source with its cause and the mechanism that
> detected it, partitioned into five categories. **Seven of the 25 are
> faults in the verification machinery itself.**

The corpus is the contribution. The infrastructure that makes it
affordable to record — a fingerprint-gated claim ledger, §6 — is
method, and I do not claim it is novel.

**I am not claiming the domain results are correct.** The substrate is
a rule-based physics and chemistry model. 47 of its 135 registered
inputs are values I picked. The system's job is to make that
distinction machine-checkable, and §8 says where it fails.

---

## 2. Why this data is scarce

Empirical software engineering has bug corpora — Defects4J, BugSwarm,
ManyBugs — and they are mined from version control after the fact.
That gives the *fix*. It rarely gives the *cause*, and it almost never
gives **what caught it**, because the commit that fixes a bug does not
usually record how the bug surfaced.

For scientific code the gap is worse:

- Researchers fix and move on; the error is not a publishable object.
- A wrong number that is never noticed produces no commit at all.
- Nobody publishes the bugs in their own test suite. Admitting a check
  was wrong is admitting the checked results were unverified.

So the question *"which mechanisms actually find errors in scientific
software — types, assertions, cross-validation, dimensional analysis,
independent reimplementation?"* is mostly answered by intuition. This
is 25 data points, and they are not distributed the way I expected.

---

## 3. The corpus

Every entry is annotated at its site in source and in `LOG.md`, with
the version it was found at.

| category | n |
|---|---|
| deriving something previously asserted | 7 |
| **faults in the verification machinery itself** | **7** |
| an automated check fired | 6 |
| comparison against an externally known value | 4 |
| cross-referencing an earlier release of the same system | 1 |

### 3.1 Deriving something previously asserted (7)

The largest category, and the one I did not anticipate. These are
faults that no test could have caught, because the code was
self-consistent — it was *answering with a number somebody typed in*.

- **An animal scaling law applied to a plant.** Metabolic cost priced
  a tree trunk with Kleiber's law. A trunk is ~4% living tissue at
  100 m; pricing dead heartwood as respiring made a 155-tonne tree
  cost 1.3 MW. Found only by deriving the cost from buckling mechanics.
- **A model that assumed its own conclusion.** Crown area was set
  proportional to height, so height paid for itself with no competitor
  present. The result looked like a derivation of tree height and was
  a restatement of the input.
- **A learning rate standing in for physics.** Engine efficiency
  improved 1.2%/year and reached a thermodynamic ceiling after 450
  years — because it was told to crawl, not because anything resisted.
- **A chosen cap that was already saturated.** A ceiling I picked was
  binding *before* the variable under test was introduced, so the
  experiment measured the cap. Adding the variable changed nothing and
  the null result was an artifact.
- **A calibration constant 10⁵ too small**, which made a quantity grow
  0.007 units in six centuries and hid every limit behind arithmetic
  that never moved.
- **A sign inversion in an Arrhenius ratio**, reporting a temperature
  effect backwards.
- **A guessed ceiling** producing a population bound nobody would
  endorse.

### 3.2 Faults in the verification machinery (7)

The category I would most want reviewed, because these are the ones
that make every other result provisional while they are live.

- **Five checks that grepped for a string literal they themselves
  contained**, and so could never fail. Found by a meta-check scanning
  every module.
- **A dependency graph keyed as if it were a chain.** Nodes were keyed
  by position in one traversal; the graph is a DAG, so a rule reached
  by two routes got two keys and sharing collapsed from ~100 to 6.
- **A hand-written dependency list.** Eleven stages typed by hand. It
  said what I *believed* the dependencies were; replacing it with AST
  derivation immediately exposed two further bugs.
- **An AST walk that descended into function bodies**, so loop-local
  variables (`lo`, `mid`, `hi` from a bisection) appeared as *rules* in
  a published claim's dependency root.
- **An epistemic type defined as exclusive when it is orthogonal.** A
  new kind, `ENACTED` (a result that happened in a *run*), was checked
  as mutually exclusive with input-grading. It is not — one says what
  the answer is *about*, the other how good its inputs were. **The
  check failed on its own registry on first execution, correctly.**
- **A check pinned to a rule name**, which failed *because the thing it
  watched got repaired*. Checks must assert invariants, not
  memberships.
- **A branch condition that became always-true** after a related
  change, so it reported a stop that had not happened. A condition
  that cannot be false is not a finding.

### 3.3 An automated check fired (6)

- A cache keyed on `id(body)`; CPython reused a freed address and moved
  a published value. Caught by the claim checker.
- A duplicate-constant rule **caught its own author twice**, within
  minutes of being written.
- Infinite recursion in a lab rule that invoked its own runner.
- Stale published numbers, on five separate occasions.
- Ledger tampering: editing a stored fingerprint raises
  `SOLID PREFIX BROKE at <node>`.

### 3.4 Comparison against an externally known value (4)

- **Unit error, factor 10⁶.** Circulatory power in ml vs m³ gave 6,528%
  of a human energy budget against a known 1–2 W heart.
- **Double unit conversion.** A returned value object stated "53.9 W"
  in its own metadata; the caller converted anyway, shrinking every
  result 20×. *The information needed to prevent this was present and
  unread* — an argument for machine-checked units, not a stronger
  convention.
- A prediction compared against the wrong observable (a redistributed
  mean vs a dayside measurement): apparent error +2.8 K, real error
  +97 K.
- A figure typed into the write-up by hand (26) while the code said 21.
  No test could see it; the write-up was not in the dependency graph.

### 3.5 Cross-referencing an earlier release (1)

One entry, and it corrected a claim I had already published: an
analysis reported 119 functions as dead code. Checking against the
previous major version showed **66 were referenced there.** The tree
had grown past the call site, not past the rule. The correct partition
is lineage 66 / runtime-dispatched 32 / genuinely stranded 22.

---

## 4. What the distribution suggests

Tentatively, from 25 points in one codebase:

**Tests were not the main mechanism.** Only 6 of 25 were caught by an
automated check. The largest category (7) required *re-deriving a
quantity that had been asserted* — work no test suite performs,
because the code was self-consistent and every test passed.

**Self-consistency is the dominant failure mode.** A function that
consumes a typed-in constant and returns a number has the surface form
of a derivation and no test can tell the difference.

**Checking apparatus fails at roughly the rate of the code it
checks** (7 vs 18). I have not seen this quantified elsewhere and
would not have guessed parity.

**External anchoring is disproportionately valuable.** 4 faults were
caught purely by comparing against a value from outside the system,
and two were order-of-magnitude unit errors that no internal
consistency check would ever surface.

---

## 5. The practice that produces the record

The corpus exists because of two conventions, which are cheap and
which I would defend independently of any tooling.

**Inverted checks.** When a check's premise turns out false, the check
is *flipped and kept*, carrying its own history, rather than deleted.
Nine checks in five modules currently read "INVERTED, kept" followed by
what they used to assert and why that was wrong. Deleting them would
have erased nine data points.

**Supersession with written reasons.** 14 published numbers have been
withdrawn, each with a paragraph explaining *why*, not merely that.
Several were withdrawn while remaining arithmetically correct — the
question they answered was wrong, which is a distinct failure and one
that a pass/fail suite cannot express.

---

## 6. Method: making continuous verification cheap

Recording errors requires noticing them, which requires re-checking
often, which has to be affordable.

47 numbered claims, each a value plus a function that recomputes it.
Full re-verification cost 77 s, 70 of them re-deriving results nothing
could have changed.

`engine/spine.py` recovers each claim's dependency graph from the AST —
what a function calls, what those call, out through imports, to a
fixpoint — and fingerprints each node over **its own source text and
its dependencies' fingerprints**. One 16-byte value therefore commits
to the whole chain beneath a claim. Hashing *source* rather than
*values* matters: a rule can be rewritten and still return the same
number today.

    biome.PHOTOSYNTHETIC_EFFICIENCY  217528a4dcab6c8d
    life.RHO_WATER                   e957a0e4e29a957f
    biome.hydraulic_ceiling          f9c540e277ba9178
    ... 15 more
    biome.escalation_stops_at        1d7e6a21f337415b   <- the claim

Nobody declared that this claim depends on `life.RHO_WATER`. It does,
transitively, and the walk found it. An unchanged fingerprint is a
proof the answer cannot have moved.

| | cold | warm |
|---|---|---|
| 47-claim ledger | 70.9 s | **0.0 s** (47/47 skipped) |
| full suite | 77 s | **7.3 s** |
| whole-repo fingerprint (1,772 rules) | 26.0 s | 0.15 ms |

**This mechanism is not novel.** Nix, Bazel and ccache hash build
inputs; DVC and Snakemake track pipeline staleness. The only
differences here are that the unit is a *published claim* rather than a
build artifact, and that the graph is also read as a diagnostic (§7.4).
Whether either difference matters is an open question (§8.2).

### 6.1 Provenance typing

135 inputs, each typed `EXACT` (6), `MEASURED` (80), `CHOSEN` (47) or
`RECORDED` (2); results additionally `ENACTED` (14) when they are the
output of a *run* rather than an observation. Claims are graded by
their worst input, and citing a `CHOSEN`-backed result as derived is
refused.

---

## 7. Does the gate actually work?

A fast wrong answer is worse than a slow right one, so the gate was
tested by fault injection rather than assumed.

**Recall** — faults injected into source, caches cleared, ledger rerun:

| injected fault | recomputed | failed |
|---|---|---|
| photosynthetic efficiency +5% | 7 / 47 | 3 |
| bone compressive strength +12% | 9 / 47 | 3 |
| ribozyme error rate +20% | 4 / 47 | 4 |
| gravitational constant +0.1% | 6 / 47 | 4 |

4 of 4 detected; none triggered a full recompute.

**Precision** — edits that should change nothing:

| edit | recomputed |
|---|---|
| whitespace in an unrelated docstring | 0 / 47 |
| render resolution (no claim depends on it) | 0 / 47 |
| a constant used by exactly one claim | 1 / 47 |

### 7.4 Root depth

A by-product: the depth of a claim's dependency graph separates
results the rules *derive* from results that are arithmetic over a
constant.

    radiative.grey_equivalent_full     37 nodes
    nucleo.mass_bar                    15
    atoms.limiting_element              6
    <a "does a tool pay for itself" claim>  2   <- flagged

Two nodes: one constant and itself. Rebuilding it to derive from
material strengths already present moved it to 13 and changed the
answer. **This caught one real case. One case is an anecdote**, and it
is gameable — inlining shortens a root, a pass-through lengthens one.

---

## 8. Limitations

1. **One codebase, one author, no external replication.** The
   distribution in §4 is 25 points from a system I wrote; my blind
   spots are in the data twice — once as faults, once as faults I
   failed to record.
2. **No comparison against Nix, Bazel, DVC or Snakemake.** Not run.
   This bounds §6 entirely, and "use Bazel" is a legitimate response.
3. **Survivorship.** The corpus contains faults that were *found*.
   Faults still present are by definition absent, and I have no
   estimate of the ratio.
4. **The curriculum is self-generated.** 5,737 items at 0 wrong is
   consistency, not accuracy. I do not lean on it.
5. **Root depth is a heuristic on one case.**
6. **Source-hashing is conservative** — a comment inside a dependent
   function forces recomputation.
7. **The domain content is unreviewed.** 47 of 135 inputs are `CHOSEN`;
   19 `MISSING_RULE`s are open. Labelling is not validation.
8. **Static analysis misses dynamic dispatch** — 32 functions resolved
   by name at runtime are invisible to the walk. Reported, not hidden.

---

## 9. What I am asking

1. **Is a labelled fault corpus with catching-mechanism annotations
   useful to anyone?** If empirical SE or RSE people already have this,
   I would like to be pointed at it.
2. **Is the parity in §4 — verification machinery failing about as
   often as the code it verifies — known?** It surprised me and I have
   not found it quantified.
3. **Does the claim-granularity framing add anything over a build
   system?** I have not run the comparison and would rather be told it
   is unnecessary.

**Reproduction.** Stock Python 3.9, no dependencies, no network.

    python3 -m eval.benchmark    # full suite, ~7 s warm / ~77 s cold
    python3 -m eval.claims       # the 47-claim ledger
    pytest                       # discovers all 406 module checks
    python3 -m engine.spine      # dependency graph and root depths

`LOG.md` is the corpus. Fault-injection scripts are ~30 lines and
available on request.

I would rather be told this is a solved problem than continue not
knowing.
