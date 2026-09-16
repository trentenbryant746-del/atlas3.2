# atlas2 — rules that compute, routing that declines

    from atlas import ask, why
    ask("what day of the week is 2026-09-15")        # date algebra
    ask("convert 100 km/h to meters per second")     # dimensional algebra
    ask("Evaluate: ((3 + 4) × 5) - 6")               # compositional parse
    ask("subtract 20 from 327")                      # rule via phrasing
    ask("...", index=idx)                            # grounded extraction

One entry point over every mechanism. Each answer carries its mechanism, its
check kind, its provenance and its token cost; each refusal carries the
reason from every layer that was tried.

    curriculum (5,737)          5737 correct, 0 wrong, 0 abstained
    novel arithmetic             422/422
    units and dates              all pass, compounds and chains included
    must-refuse                  7/7 refused
    cross-layer disagreement     0 over 1,512 probes

## Held-out benchmark from another project

`data/atlas-novel-sat-like.jsonl` -- 165 prompts, every one marked
`split: held_out_benchmark` and `training_eligible: false`, produced by the
Codex Atlas line and never seen by anything here.

    expected_tool                n  answered  abstained  verified
    arithmetic                  80        80          0        80
    time_measurement            12        12          0        12
    dna_structure               24         0         24
    material_ontology           16         0         16
    virtual_planet              12         0         12
    synthetic_galaxy            12         0         12
    periodic_table_reference     9         0          9

92 answered, all independently verified by recomputation; 73 abstained,
which is every prompt needing an expert this system does not have. Zero
wrong answers, and no expert was faked.

Expected answers in that file are SHA-256 hashes and the format is not
recoverable. The handoff README says not to infer answer content from a
hash, so verification here is by INDEPENDENT RECOMPUTATION instead --
stronger anyway, since it does not trust the benchmark either.

`time_measurement` was in the abstain column until the date algebra was
extended from days to INSTANTS. That is the recurring shape of progress
here: extending an algebra covered all twelve at once, where adding a family
would have covered one pattern.

## Six experts, each with the check its domain admits

    dna_structure     DERIVED       complement is its own inverse;
                                    GC content counted two ways
    periodic_table    ASSERTED      118 elements; empirical, so the check is
                                    a table round-trip and the answer cites
                                    IUPAC. Synthetics are flagged as most-
                                    stable-isotope, a different kind of value
    material_ontology DERIVED       formula asserted, molar mass computed
                                    from it; formulae round-trip or are refused
    virtual_planet    DERIVED       pure function of the seed, checked by
                                    determinism AND physical invariants --
                                    gravity is recomputed from radius and
                                    density rather than sampled
    synthetic_galaxy  DERIVED       same
    time_measurement  DERIVED       instants, added to the date algebra

    held-out benchmark: 165/165 answered, every one independently verified

Seeded worlds are where the system generates its own material and can still
verify it, because the world's only authority is its seed. The provenance
says so explicitly: "not a claim about any real planet."

## History, law and medicine

The proposal was that fundamental rules could build up to these. Half of that
is right and the half that is not cannot be fixed with more rules.

THE REASONING IS DERIVABLE, and already works:

    how many days between 2021-06-01 and 2024-05-01  -> 1065   date algebra
    what is 45 times 18                              -> 810    arithmetic
    convert 4500 mg to grams                         -> 9/2    dimensional

THE FACTS ARE NOT, and nothing entails them. The limitation period is three
years because a legislature wrote three. Westphalia is 1648 because it
happened then. A dose is 45 mg/kg because trials found that. Law is
STIPULATED, history is CONTINGENT, medicine is EMPIRICAL -- physics entails
none of them. Measured: 2.0% of belt-atlas's 350 stated facts had an answer
derivable from anything in the question, against 100% for arithmetic.

So `engine/gaps.py` makes the abstention into a REQUEST -- which is the
"generate possibilities that get satisfied" loop:

    asked      amoxicillin dose for otitis media in an 18 kg child
    atlas      NEEDS INPUT: a clinical parameter (empirical: established by
               trial, not derivation); then arithmetic once the rate is given
    supplied   45 mg/kg/day divided into 2          <- from a source
    derives    45 x 18 = 810 mg/day  ->  405 mg per dose  ->  0.405 g

Every arithmetic step is checked. The 45 mg/kg is a citation, and the system
never pretends to have derived it. That division of labour is the whole
value: it is wrong in a way you can see, or right in a way you can audit.

## Generating over asserted facts, inside the token window

For anything that cannot be derived, generation is restricted so it cannot
invent (`engine/epistemic.py`):

    the ANSWER must be a verbatim span of the source
    the QUESTION may use only vocabulary the source record contains
    the pair carries the source's epistemic tag

New phrasings, never new facts. Over belt-atlas's 350 sourced facts:

    507 pairs generated, 232/350 facts covered
    507/507 answer-verbatim AND question-in-window
    507/507 round-trip through the grounded extractor
    tags: EMPIRICAL 460, STIPULATED 28, CONTINGENT 19

The three asserted kinds are separated because they GO STALE differently: a
stipulated value changes by decree, a contingent one never changes but may be
misremembered, an empirical one is revised by better instruments. One
"ASSERTED" bucket cannot be audited; three can.

### What the window does not buy

FAITHFULNESS IS NOT USEFULNESS. The first version drew question words from
whatever the matched span contained and produced "what is the answer bryant
built" -- every token from the source, in-window, verbatim answer, and not a
question anybody would ask. The window constrains what may be said, not
whether saying it is worth anything. Both had to be fixed separately:

    frames chosen by attribute SHAPE   "how radius is earth" came from
                                       applying an adjectival frame to a noun
    interrogative and numeric keys     "what is the where of bend",
                                       "what is the 70 of speed"
    primary-statement preference       `earth.day` matched a sentence that
                                       mentions the day without stating it

THESE PAIRS ARE SAFE, NOT HARD. The questions are framed from the keys, and
key-derived questions were measured at ~100% retrieval against ~70% for
hand-written ones. So this corpus is good for checking that a system never
invents, and close to worthless for measuring whether it understands.

THE TAGGER IS CUE-BASED. Epistemic kind is assigned by regular expressions
over the text, unvalidated against any labelled set. 91% of this corpus lands
in EMPIRICAL, which is plausible for a corpus of physical constants and may
equally be the default branch absorbing everything. Treat the tags as a
starting partition, not a measurement.

## Ingesting from the open web

`engine/ingest.py`. Allowlisted hosts only, checked on the PARSED HOSTNAME --
a substring test would accept `https://evil.com/?q=.gov` and
`https://notgov.example`. Every answer carries url, retrieval date and a
content hash.

THE SOURCE TAGS ITSELF, where it can, and that is better evidence than the
cue-matching in engine/epistemic.py. NIST publishes both kinds on identically
formatted pages:

    speed of light   uncertainty "(exact)"        -> STIPULATED
    electron mass    uncertainty 2.8e-40 kg       -> EMPIRICAL

The stipulated/empirical split read off the authority's own annotation. The
metre is defined from c, so c is exact by decree; the electron mass is
measured, so it has a number after the plus-or-minus.

FETCHED TEXT IS DATA. Nothing in this path executes, routes or configures
anything from page content -- extraction only ever selects a verbatim span. A
page containing "ignore your rules" yields, at most, an answer quoting that
sentence with its URL.

### What ingestion buys, and what it does not

It raises COVERAGE OF ASSERTED FACTS, which was the measured bottleneck:
2.0% of stated facts were derivable from their questions, so the rest have to
come from somewhere. A fetched page is a citation.

It does not make the system learn. No amount of prose induces a new
primitive, and nothing in the 2.0% figure moves because a fact arrived over
HTTPS instead of from a file. More sources means more questions answerable
with provenance; it does not mean better reasoning.

.gov AND .edu ARE A PROVENANCE FILTER, NOT A TRUTH FILTER. `.edu` includes
student pages, personal sites and course notes; `.gov` includes superseded
and archived material. The allowlist establishes who is speaking, which is
exactly what a citation is for, and not whether they are right.

## Games: English in, a running game out

`engine/games.py`. belt-atlas established the shape -- picks in, code out, a
round-trip back to picks proving the compression was real. Its check was
Godot's parser, which proves the text is legal, not that the game works. The
check here EXECUTES:

    parses                      ast.parse accepts it
    round-trips to the picks    re-reading the source recovers them
    runs headless               N deterministic ticks, no exception
    invariants held every tick  position in bounds, score <= goals, hp <= max
    reproducible from the seed  same seed, byte-identical trace

All five sabotaged; all five caught. Three of them are things a parser
cannot see.

### The English layer is the ceiling, and it is measurable

Stress-tested, and the result is stark:

    "20x10 grid, collect 5 coins, 3 enemies"    4 decisions from 9 words
    "a hard game"                               0 decisions
    "a relaxing puzzle, help a lost cat home"   0 decisions from 13 words
    "like Pac-Man but the ghosts cooperate"     0 decisions
    "make it fun"                               0 decisions

Every one of those produced a game that RUNS -- and for four of five it was
the identical default game, silently. So the builder now separates two
things that were being conflated:

    ok                 the generated game passes all five checks
    matches_request    anything in the description became a decision

and reports what it could not use, by kind:

    AESTHETIC    fun, hard, relaxing. Not derivable. Fun is EMPIRICAL --
                 established by putting the thing in front of people, in
                 exactly the way a dose is empirical and a statute is
                 stipulated. No number of cues turns "relaxing" into a grid
                 size, because the mapping does not exist to be learned.
    REFERENTIAL  "like Pac-Man". Needs the referenced game described. This
                 one IS fixable -- it is a fetch, and the ingest path exists.
    NARRATIVE    a lost cat finding home. The pick language has no slot for
                 theme. Fixable by extending the language, which is work,
                 not a barrier.

Two of the three are engineering. The first is not, and adding a "fun" pick
would be inventing a number.

The system can generate the possibility space and verify every point in it
runs. Which point is worth shipping is measured, never computed.

## One IR, several backends, and the backends check each other

`engine/ir.py`. Generating GDScript directly ties output to one engine and
leaves the check at whatever that engine's parser says. An IR fixes both:

    picks -> IR -> {python, ruby, gdscript}

and buys a check no single-target generator can have. Two backends are two
INDEPENDENT IMPLEMENTATIONS of one specification. Compile, run both, require
byte-identical traces:

    python   6|5|4|6|5|4|6|5|4
    ruby     6|5|4|6|5|4|6|5|4      agree
    gdscript emitted, NOT executed -- Godot is not installed, so it is
             labelled unverified rather than counted as passing

Negative control: an off-by-one injected into the ruby backend alone.

    python   6|5|4|6|5|4|6|5|4
    ruby     6|4|7|5|6|4|7|5|6|4    CAUGHT

A codegen bug now has to survive one backend's syntax AND the other's
semantics, and they were written separately.

## Godot, and the third executable backend

Godot 4.7.2-stable downloaded and SHA-512 verified -- the same version
belt-atlas's validate.py hardcodes. GDScript is emitted as a SceneTree
script, which Godot runs directly with `--headless --script`, so it needed
no project scaffold and became EXECUTABLE rather than merely emitted.

    python    6|5|4|6|5|4|6|5|4
    ruby      6|5|4|6|5|4|6|5|4
    gdscript  6|5|4|6|5|4|6|5|4     all three agree

    negative control, gdscript sabotaged alone:
    gdscript  6|4|7|5|6|4|7|5|6|4   CAUGHT

Traces are delimited `<<T>>...<<E>>` in every backend, because a runtime
prints what it likes -- Godot emits a version banner before the program
says anything, and an undelimited comparison was fooled by it.

`EXECUTABLE` is computed from whether the runtime is actually on the
machine. A backend with no runtime is reported as unverified, never counted
as passing.

## The visual is a fourth representation, not a picture

`engine/visualize.py`. Atlas's own vocabulary maps straight onto the IR --
particles are operands, atoms are ADD/MUL/NEG/INV, a compound is the tree,
routes are its edges -- and a tree is the one thing a game engine is
unambiguously good at drawing.

So an induced compound is rendered as a .tscn whose node NAMES are the
provenance tokens. The same id then labels the shape on screen, the Python
line, the Ruby line and the GDScript line.

AND GODOT READS IT BACK. A picture that cannot be recovered is a picture,
not a representation. Godot loads the generated scene headlessly, walks the
node tree, prints what it finds, and the recovered structure must equal the
expression that produced it:

    induced   ((x2*(x0+x1))+-(x3))
    rendered  8 atoms
    readback  8 atoms round-tripped through Godot        ok
    control   one metadata label corrupted               CAUGHT

Same rule belt-atlas's compress.py applied to code, now applied to a scene.

GODOT EARNED ITS PLACE IMMEDIATELY by rejecting my own script:

    Parse Error: Cannot infer the type of "root" variable because the
    value doesn't have a set type.

`load()` returns Variant, so `:=` cannot infer. A third-party parser with
no stake in my code found that in the first run.

## Compression, drawn

`engine/dag.py`. The 9->4 primitive result was a number in a report. It is
also a SHAPE: when compounds reduce to the same primitives they share
subtrees, and sharing is what a DAG draws and a tree cannot.

    9 induced compounds
    tree nodes if drawn separately   50
    DAG nodes after hash-consing     29
    ratio                            1.72x
    reconstruction verified          every original rebuilt from the DAG and
                                     behaviourally identical on 200 inputs

A DAG that cannot rebuild its inputs is a smaller picture, not a
compression. The sharing is also informative rather than decorative:

    d1   x0    used by all 9 rules
    d8   100   shared by meters and pct -- both scale by a hundred
    d6   1/    shared by div and fracadd

Rendered to Godot and read back: 29 atoms out, 29 atoms in, structures
identical. Godot reports a shared atom as `d0:x1:add,compound,div,linear,
mul,pct,sub` -- the shape on screen knows which seven rules use it.

## Composed experts, and what the percentage actually measures

`engine/compose.py`. "An expert with a certain percentage of everything in
it" cannot mean a blend -- there is no 30% of ADD, and averaging two rules
gives a rule that answers neither question. What is well defined is
COVERAGE of the shared atom vocabulary:

    shared vocabulary            9 atoms
    composed experts             10, each behaviourally distinct
    coverage                     44% - 78%, mean 54%

Kept only if behaviourally novel, the same rule the code index uses.

WHAT THESE ARE NOT. `-(((1/(-(x2*x0))+x1)+x2))` is a valid computation,
genuinely novel, and nobody asks it anything. An expert is a function PLUS
a family of questions it answers, and composition supplies only the first
half. The possibility space is generatable and verifiable; which points in
it are experts depends on questions, and questions come from outside.

## Typed atoms: binding rules make compounds mean something

`engine/bind.py`. The composed experts were meaningless because they were
UNTYPED -- nothing stopped `x2*x0` from multiplying a duration by a count.
units.py had already solved this for conversion, refusing metres to
kilograms on dimension exponents before any arithmetic runs. The same move
applies to the atom basis:

    ADD  : T x T -> T        only like to like
    MUL  : A x B -> A*B      dimensions multiply
    INV  : A     -> A^-1
    SQRT : A^2k  -> A^k      only of an even-powered dimension

A binding that violates a signature is not a low-scoring compound, it is
not a compound. Measured on a two-seed basis grown to size 9:

    bindings attempted              146,946
    refused by type                  49,588   (34%)
    elements formed                  97,360
    of those, dimensionally a TIME      328   (0.3%)

    -> a dimension-directed search tests 328 instead of ~147,000, a 448x
       reduction, and the SMALLEST survivor is the law:

           (a * sqrt(a/mu))          = a^1.5 / sqrt(mu)
           sqrt(a*(a*(a*1/mu)))      = sqrt(a^3/mu)

### The type signature is the prompt

An element's construction IS its reasoning chain, and its signature states
what question it answers:

    element  (a*sqrt((a*1/(mu))))       type (0,0,1) = time, 7 atoms
      1. take a          4. take the reciprocal of that
      2. take a          5. multiply those two
      3. take mu         6. take the square root of that
                         7. multiply those two

    inputs  a = length, mu = gravitational parameter
    output  time
    prompt  "given a length and a gravitational parameter, find a time"

328 elements answer that prompt. The shortest is Kepler's law. So a typed
element is a multi-step reasoning problem whose answer, derivation and
provenance all come from the same object.

MEANINGLESS ATOMS BIND ANYWAY, which is the point. `mu` alone says little.
Bound into sqrt(a^3/mu) it is what makes the dimensions balance. Meaning is
a property of the binding, not of the atom.

## Particles: conservation laws are a second type system

`engine/particles.py`. Dimensions were one type system. Conserved quantum
numbers are another, independent of it -- charge, baryon number and lepton
number are additive and must balance across any binding.

    particle      Q     B     L    mass (u)
    proton      +1    +1     0    1.0072765
    neutron      0    +1     0    1.0086649
    electron    -1     0    +1    0.0005486

    refused: a lone proton (Q=+1), a lone electron (Q=-1),
             2 protons + 1 electron (Q=+1)

### What compresses, and what does not

THE STRUCTURE COMPRESSES. A neutral atom is any bound state with Q=0, and
its element is its proton count. The table's 118 rows of Z -> symbol are one
binding rule plus 118 NAMES, not 118 facts about the world.

THE MASSES COMPRESS, CONDITIONALLY. Given (Z, N), atomic mass derives from
3 particle masses plus the 5 measured Weizsacker coefficients -- 8 numbers:

    element     predicted   tabulated    error
    oxygen         15.997      15.999     0.0%
    iron           55.932      55.845     0.2%
    gold          196.961     196.970     0.0%
    uranium       238.037     238.030     0.0%

    median error with the true isotope:  0.22%

THE ISOTOPE DOES NOT COMPRESS. Deriving N by maximising binding energy per
nucleon fails outright -- median error 5.66%, and it gives hydrogen N=2
(tritium) and oxygen N=10. Which isotope is abundant is empirical.

    CORRECTION. An earlier run of this reported "84 tabulated masses
    reproduced to ~1% from 8 numbers". The numbers printed directly above
    that line said median 4.1% and 15/84 within 1%. The claim was false and
    the measurement in the same output disproved it. The error was the
    isotope derivation, not the mass formula, and separating the two is what
    showed it. A second label in that run called the liquid-drop model "poor"
    for light nuclei; light is 0.15% and heavy is 0.29%, so that was wrong too.

### Spin, isospin, strangeness -- and what each one is worth

Strangeness is inert unless something carries it, so the basis grew:
lambda0, sigma+/-, xi-, kaon+. Then the quantum numbers can be CHECKED
rather than merely stored, by Gell-Mann-Nishijima, Q = I3 + (B+S)/2:

    7/7 hadrons satisfy it
    1 lepton, where the relation does not apply
    a fabricated particle with Q=+2, B=1, S=0, I3=0 -> CAUGHT

The first run reported the ELECTRON as violating it. That was my error, not
the data's: the relation describes quark content, so it says nothing about
leptons. Scoping the check is part of the check.

SPIN DOES NOT SIMPLY ADD. Q, B, L, S and I3 are additive and sum. Angular
momentum is a vector, so two spin-1/2 particles give total 0 OR 1 and the
parts do not determine it. What IS determined is the statistics -- odd
number of fermions is a fermion, even is a boson:

    hydrogen-1  (2 fermions)  boson
    deuterium   (3 fermions)  fermion
    helium-4    (6 fermions)  boson     -- which is why it goes superfluid

Reporting a summed spin would have been wrong, so it reports what follows.

### Biogenic elements: two questions, two answers

    most abundant by MASS   oxygen   ~65% of a human
    most abundant by COUNT  hydrogen ~62% of the atoms

Both true, and conflating them is the classic error. Both are stored and
the query must say which. CHNOPS and the five DNA elements (C H N O P,
phosphorus from the backbone) are registered for the structures to come.

### Mixtures -- a correction

I claimed the ladder stopped at compounds: that dirt and ore "are not
compositional objects and no set of rules will make them one". That was
wrong. A mixture is compositional under a different rule:

    compound   fixed integer ratio    H2O      exact, a formula
    mixture    real fractions         dirt     sum(f) = 1, plus a seed

Sum-to-one is a conservation law exactly like charge balance, and just as
checkable. What a mixture lacks is not composition but a CANONICAL
composition -- two handfuls of dirt differ -- so the representation carries
a seed, and the seed is the watermark. Same seed, same mixture, verified.

REPRODUCIBLE IS NOT REALISTIC, and they are kept apart. A generated `star`
came out 24% oxygen; a real one is ~74% hydrogen. So measured compositions
live in `OBSERVED` with citations and generated ones never mix with them:

    sun          H 73.5%, He 24.8%, O 0.8%   Asplund et al.
    earth-crust  O 46.1%, Si 28.2%, Al 8.2%  standard reference
    generated    H 21%, Fe 21%, He 21%       reproducible, and not a star

The sum-to-one check then caught the solar table summing to 0.9972 -- seven
listed elements and a truncated tail. The remainder is now explicit;
loosening the tolerance would have hidden a truncated table instead of
naming it.

## Nucleosynthesis: the universe, recomputed from the rules

`engine/nucleo.py`. Nothing here is a stored astrophysical fact. Every
result is computed from the particle masses and the Weizsacker coefficients
already in the repo, then compared against the observed value.

CONSERVATION BEFORE ENERGY. A reaction is balanced for charge, baryon
number and lepton number before any energy is computed:

    ok       4p -> He4 + 2e+ + 2nu
    ok       p + p -> D + e+ + nu
    ok       3 He4 -> C12
    REFUSED  4p -> He4          (leptons unaccounted; not a reaction)

STELLAR FUSION, from mass defect alone:

    4 H  -> He4    26.73 MeV   accepted 26.73    error 0.01%
    3 He4 -> C12    7.271 MeV  accepted  7.275   error 0.1%

BIG BANG NUCLEOSYNTHESIS. The whole primordial helium abundance follows
from the neutron-proton mass difference:

    dm(n-p)              1.293 MeV      from the particle masses
    n/p = exp(-dm/kT)    0.199          at freeze-out
    after beta decay     0.147          ~ 1 neutron per 6.8 protons
    Y_p = 2r/(1+r)       0.256          observed 0.245

    sensitivity to the one free parameter:
       T_freeze 0.75 MeV -> Y_p 0.233     0.80 -> 0.256     0.85 -> 0.278

    I chose 0.80 as a round standard value. Most of the 4.6% error is that
    choice, not the derivation -- which is a thing worth knowing before
    quoting the agreement as a success.

WHY FUSION STOPS AT IRON, derived rather than looked up:

    derived peak   Z=26  A=58   B/A 8.865 MeV
    actual peak    Fe-56 / Ni-62, B/A ~ 8.79 MeV

It gets the ELEMENT right and the isotope wrong by two neutrons. The
Weizsacker formula is a liquid drop with no shell closures, and the real
peak is set by exactly those. A known limit of the model, surfaced by the
derivation instead of hidden by it.

## Time: a fourth type system, and the one that dominates

`engine/epochs.py`. Dimensions prune by physical quantity. Conservation
prunes by quantum number. Both are TIMELESS. Epoch prunes by causality, and
it is independent of the other two: carbon at t = 3 minutes is
dimensionally fine and perfectly charge-neutral, and it cannot exist,
because triple-alpha needs stars and there are none yet.

Measured over every (element-pair x epoch) binding:

    type system                    refuses   passes
    dimensional (both masses)            0     1680
    conservation (both neutral)          0     1680
    EPOCH (causality)                 1263      417

Epoch refuses 75% of a space the other two cannot touch. It is an
independent constraint, not a refinement of them.

THE POSSIBILITY SPACE OPENS OVER TIME:

    bbn             5% of element pairs possible
    recombination   5%
    first_stars     7%
    stellar_c      17%
    supernova      65%
    ns_merger     100%

### The Big Bang is not a variety generator

It runs about twenty minutes and produces FIVE nuclides:

    H 0.75, He4 0.25, D 2.5e-5, He3 1e-5, Li7 5e-10

and then stops, because there is no stable nucleus at mass 5 or mass 8. The
chain upward from helium has no two-body bridge, and crossing it needs a
three-body collision at stellar densities on stellar timescales. Everything
past lithium waits.

So complexity is a function of TIME, not of the bang. Which is exactly why a
time layer buys something: without it, the model would happily bind gold at
t = 3 minutes.

### Context tokens are timelines

A compound's context token is the ordered list of when its constituents
became possible. DNA's five elements:

    H@bbn         t = 1.8e+02 s
    C@stellar_c   t = 3.2e+16 s
    N@stellar_c   t = 3.2e+16 s
    O@stellar_c   t = 3.2e+16 s
    P@supernova   t = 9.5e+16 s

Fourteen orders of magnitude of cosmic time in one molecule -- hydrogen from
the first three minutes, phosphorus from exploding stars billions of years
later.

## A universe you can audit

`engine/cosmos.py`. Not a cosmological simulation -- that is a
supercomputer problem. The point is that every gram is ACCOUNTED FOR, so
the model can be checked instead of admired.

    mass conservation      ejecta + remnant = progenitor    12/12 events
    monotonic enrichment   metallicity never falls           true
    epoch compliance       no element predates engine/epochs  0 violations
    convergence            measured against OBSERVED solar abundances

A star's provenance is its prompt -- which generation, from whose ejecta,
carrying which elements produced when:

    generation 3 popI star g3s2, 28.96 solar masses, Z=0.2810,
    from ['g2s0','g2s1'], earliest constituent epoch bbn

### The convergence test caught a real modelling error

The first run passed every internal check and still produced a universe
28% metals against a solar 1.7% -- an order of magnitude too enriched. The
internal checks could not see it; only comparison with the real sky could.

The cause was DILUTION. The model fed 100% of each generation's ejecta into
the next, when real ejecta disperses into a far larger reservoir of gas
that never formed stars.

    dilution   final Z        H   mean |diff| vs solar
           0    0.3610   0.3890            0.1051
           5    0.0161   0.7339            0.0006
          20    0.0040   0.7460            0.0037

    element    simulated     solar        diff
    H            0.73392   0.73460    -0.00068
    O            0.00606   0.00770    -0.00164
    Fe           0.00258   0.00160    +0.00098
    Ne           0.00121   0.00120    +0.00001

### What is fitted and what is not

THE DILUTION FACTOR WAS FITTED to the solar data. One free parameter tuned
against six element constraints, so the agreement is a fit and not a
prediction, and quoting 0.0006 as a success without saying so would be
dishonest.

What was NOT fitted: the yield table, the generation structure, the
conservation laws. So the informative part is the RESIDUAL PATTERN --
oxygen consistently low, iron consistently high, and no value of the single
scale parameter removes either. That is a signature of the yields being
wrong in a specific direction, which is a finding rather than a failure.

## Fixing the shape of a generator

A generator is a distribution, and a distribution has a SUPPORT -- the set
of values it can emit -- and a shape within it. The seed picks a point
inside the support. It cannot move the support.

`seeded_mixture` drew N components from [1.0, 1.4] and normalised, so every
component is pinned near 1/N:

    N=3    any component confined to [0.263, 0.412]
    N=7    any component confined to [0.106, 0.189]     solar H = 0.735
    N=10   any component confined to [0.074, 0.135]

Solar hydrogen is not improbable here, it is ARITHMETICALLY UNREACHABLE.
2^256 = 1.16e77 draws (not 1e277 -- that would be 2^920) changes nothing,
because every draw lands in the same interval.

THE FIX IS TO SEED THE INPUTS AND DERIVE THE OUTPUTS.

    broken   seed -> composition            the seed IS the answer
    fixed    seed -> initial conditions -> physics -> composition

cosmos.py already worked the second way: its seed sets stellar masses and
composition falls out of yields plus mass conservation. Hydrogen lands near
0.73 because BBN made 75% of it and four stellar generations burn little of
it away -- no anchoring to solar values anywhere.

### Correct support with zero diversity is also a failure

Running 400 seeded universes through the derived generator gave

    H fraction   sd 0.00000     every universe bit-identical

The yields were fixed per population, so stellar mass varied and changed
nothing. Correct location, no variance -- the opposite failure from a
generator that misses the target entirely, and just as useless.

Real yields depend strongly on progenitor mass: massive stars make the
alpha elements, lower-mass stars contribute carbon and nitrogen by
dredge-up. With that scaling:

    H fraction   0.7295 - 0.7367   sd 0.00137    solar 0.7346
    metallicity  0.0133 - 0.0205   sd 0.00137    solar 0.0166
    400/400 within 5% of solar, mass conserved in every one

Both properties at once: the support contains the target, and the seeds
genuinely differ. Diversity from initial conditions, location from physics.

## A universe history in 256 bits

`engine/chain.py`. Each expansion step is digested and linked to the one
before:

    link[0] = H(seed)
    link[n] = H(link[n-1] || canonical(state[n]))

    seed             37d3b3d5e8487aa2...
    bbn              d801e554be0a1de8...
    gen0             710272a1cd7b66ed...
    gen3             e30b97887b2d6e9d...
    now              23fdebf307ffe900...
    HEAD             23fdebf307ffe900212dea2c3a0b286c...

YOU DO NOT NEED 1056 BITS, and that is the point of chaining rather than
concatenating. A digest per epoch grows with the number of epochs; a chain
stays 256 bits for a history of any length, and it buys what concatenation
does not:

    IDENTITY     one 256-bit head names an entire Big-Bang-to-now history
    INTEGRITY    altering any epoch changes the head
    MEMBERSHIP   an epoch can be proved to belong to a head by replaying
                 from its link, without re-running the physics

    tamper with gen1's metallicity -> verify False,
                "first divergence at epoch 'gen1'"

Same discipline as belt-atlas's seal.py, which chained file hashes in
sorted order -- applied to time instead of to a directory.

### Where the ladder ends

    particles -> atoms      binding rule: charge balances
    atoms     -> compounds  fixed ratio, a formula, a molar mass
    compounds -> mixtures   NO RULE

    compounds -> mixtures   sum(fractions) = 1, plus a seed

Corrected above: mixtures DO have a binding rule, it is just weaker than a
formula. The ladder runs particles -> atoms -> compounds -> mixtures, and
planets, stars and ore are the last rung rather than beyond it.

## Testing the composed experts against data

`engine/discover_law.py`. A composed expert has no questions from people,
but DATA can ask it one: does it reproduce a relationship that actually
holds? That turns an arbitrary function into a candidate law.

Run against belt-atlas's planetary facts, seeded with the atoms
+, x, -, 1/, sqrt, square:

    search space   489 expressions over one variable
    train          5 bodies
    held out       3 bodies

    fit training AND held-out:  mul(x0, sqrt(x0))     =  a x sqrt(a)  =  a^1.5

That is Kepler's Third Law, recovered from the corpus's own numbers and
validated on three planets it never saw.

### The failed search was the more useful one

The first attempt fit nothing, and the reason was not the search:

    body       a (AU)   stored   T yrs predicted   stored/predicted
    mercury     0.387       88             0.241             365.52
    venus       0.723      225             0.615             365.99
    mars        1.524      687             1.881             365.16
    jupiter     5.204     11.9            11.872               1.00
    saturn      9.583     29.4            29.666               0.99

belt-atlas stores `.year` in DAYS for the inner planets and YEARS for the
outer ones, and nothing in the net records which. Testing rules against data
found a defect in the data. That is the most useful thing a failed fit can
do, and no amount of reading the corpus had turned it up.

### Does a bigger atom vocabulary help? Measured, not assumed

I asserted that more atoms buys reach and costs precision. The first half is
true and the second is not, which only showed up on measuring it.

    basis              exprs   shuffled fits   ALSO survive held-out
    4  (+ x - 1/)        171            0.0%                    0.0%
    6  (+ sqrt sq)       489            0.7%                    0.7%
    9  (+ log exp cube) 1,596           0.7%                    0.7%
                                          (300 shuffles each)

Four atoms cannot express a^1.5 at any size, so Kepler is unreachable -- the
basis, not the data, was the limit. Six can. Going to nine TRIPLES the search
space and does not move the false-discovery rate, because a chance fit on
five points almost never survives three held-out ones. Held-out validation
absorbs the cost of a larger vocabulary.

An earlier run reported 5%. That was one hit in twenty trials -- noise. Twenty
shuffles cannot distinguish 5% from 15%, and quoting it as a rate was wrong.

So: add atoms. The thing that limits discovery here is the data, not the
vocabulary.

### And the periodic table does not need more rows

All 118 elements are present. Searching Z -> atomic mass finds NOTHING at
2%, 5% or 10% tolerance, and that is correct: mass/Z drifts from 1.01 at
hydrogen to 2.53 at lead. It is a trend, not a closed-form law, and the
search declined to fit it rather than inventing one. The abstention property
operating at the level of discovery.

More COLUMNS would help only where a closed-form relationship exists between
them. Most periodic trends are not closed form -- which is precisely why the
periodic table is a table.

## Finding its own atoms

`engine/newatom.py`. The search found Kepler only because `sqrt` was handed
to it. Without that atom it returns nothing -- and returns exactly the same
nothing when there is no law to find. Telling those apart is the whole
problem.

Three signals, because no single one separates all three cases:

    dataset            n    form        R^2    |resid|   sign runs / expected
    Kepler a->T        8    power   0.999999      0.15%      3 / 4.5  random
    Z -> atomic mass  84    linear  0.997578      2.41%     17 / 42.5 systematic
    pure noise        29    log     0.145075     44.82%     13 / 15.0 random

    R^2         separates noise from structure; a trend scores ~1 too
    residual    separates a law (0.15%) from a trend (2.41%)
    sign runs   a trend's residual keeps its sign -- 17 runs where 42 are
                expected means the FORM is wrong, not just noisy

Then the shape of the residual names the missing operation, and the
proposal is VERIFIED by adding it and re-searching:

    dataset         verdict                       atom    verification
    Kepler a->T     BASIS SHORT (verified)        x^1.5   size 3:  1 fit,  1 held-out
    Z->atomic mass  TREND, NOT A LAW              -
    pure noise      NO LAW                        -
    y = 3x+7        EXPRESSIBLE, BUDGET TOO SMALL -
    y = 2e^(x/2)    BASIS SHORT (verified)        exp     size 7:  4 fit,  4 held-out
    y = 4ln(x)+1    BASIS SHORT (verified)        log     size 9: 56 fit, 56 held-out

An atom that does not make the law findable is reported as PROPOSAL
UNVERIFIED, not as a discovery.

### Four failures on the way, all mine

    split by position     training on the inner planets and predicting the
                          outer ones extrapolates a power law across three
                          decades. It reported 32% error and concluded "no
                          law" about Kepler's third law.
    density, not lawfulness  leave-one-out interpolation then called Kepler
                          (8 points over 2 decades) unlearnable and the
                          periodic table (84 points spaced by 1) a law --
                          exactly backwards. It was measuring how densely
                          sampled the data was.
    runs test on zero     a numerically exact fit has no residual to test.
                          The signs are floating-point dust, they clump, and
                          y = 3x + 7 was read as "systematically wrong".
    wrong prediction space  residual_profile only reconstructed the power
                          form, so an exponential was scored against a
                          straight line and misreported as a trend.

THE SIZE BUDGET HAS NOW BITTEN THREE TIMES -- Kepler at 6, the typed
element search at 6, this verification at 3. Every time the method was
right and the cap was the limit, so the verification budget is now DERIVED:
the search retries at growing sizes because a new atom needs room for the
scale and offset wrapped around it.

### Guarding against finding laws in noise

Searching hundreds of expressions against eight points WILL produce fits by
chance, so:

    held-out    the winner must hold on bodies excluded from the fit
    shuffled    with the targets randomly permuted, the same search still
                found "a law" in 5% of 20 trials

5% is not zero. A single held-out survivor is evidence, not proof, and the
control is what makes that statement quantitative rather than hopeful.

### What was supplied

The `sqrt` atom was seeded deliberately -- a^1.5 is unreachable from
+, x, -, 1/ alone, so without it the search cannot represent Kepler at any
size. Seeding the atom vocabulary is the design, not a shortcut, but the
result is "found the law GIVEN the right atoms", not "found the atoms".
And the unit normalisation was done by hand after the failure diagnosed it.

## Subject keys backed by a source

`engine/subjects.py`. `history:` was unregistered, which was correct and was
also the gap. A subject expert is not code -- it is a key, a source and a
citation.

    history: when was the constitutional convention called
    -> "The Constitutional Convention was called for May 14, 1787, but a
        quorum was not present until May 25."
       CONTINGENT -- dated events: they happened as they happened
       source: archives.gov/founding-docs/constitution-q-and-a, offset 0

    history: what caused the french revolution
    -> abstains: one source registered and it does not answer this

The tag is not decoration. Nothing derives 1787. The system is not reasoning
about history, it is quoting a source about history and naming the source.
Those are different claims and only the second one is true here.

## Keys: explicit addressing into one expert's window

`engine/keys.py`. The cascade INFERS which expert owns a question, and
inference is where the losses are: measured, free English reached ~70%
where a canonical key reached ~100%. A key removes the inference.

    NAMED     `chem: molar mass of water`  -- names the expert outright
    ARTIFACT  a block of Python source     -- the artifact IS the key, and
              its own identifiers become the window

The artifact form is the interesting one. Handing over a file opens a window
whose vocabulary is that file, so an answer cannot wander into another
subject -- the failure that produced `jupiter.spot` for "how wide is the
planet". Asked something outside the window, it abstains:

    window (4): ['clamp', 'lower', 'upper', 'value']
    "what does clamp return when value is below lower"  -> answered
    "what is the capital of France"                     -> abstains

An unknown key abstains and lists what it knows. `history:` is not a
registered expert, so it says so rather than guessing which one was meant.

## The code index

`engine/codeindex.py`. Every emitted line carries `atlas:<id>`; the id
resolves to the IR node, the operation and the English that caused it, in
any backend. The index reads both directions -- from a line of generated
Ruby back to the intent, and from an intent forward to every line in every
language implementing it.

    120 programs, every one cross-verified in THREE languages, 0 failed
    84 behaviourally distinct  (70% novel; 36 duplicates discarded)
    103 distinct provenance tokens

Growth is driven by BEHAVIOURAL NOVELTY, not program count. A program whose
trace already exists is discarded however different its source looks --
counting programs overstates an index, counting distinct behaviours does
not.

    atlas:a440b0946  add   ('x', 3, 7)   move three per tick, wrapping at seven
    atlas:ab6e99440  emit  ('x',)        record only near the start

Not unlimited -- combinatorially large, and every entry cross-verified. An
index of UNVERIFIED code is a pile of text, which is what the 640,000 proxy
records already were.

That 18/24 is worth noticing: a quarter of the generated programs are
behavioural duplicates wearing different surfaces. Counting programs
overstates the index; counting distinct traces does not.

## What the rest of the extra data is

Surveyed all 100+ JSONL corpora in the handoff. By the criterion that
decides learnability -- is the answer a function of the question? --

    REAL PAIRS        reasoning-curriculum 5,737 (already induced),
                      chemistry-core 64, python-core 5
    ROUTING ONLY      ~180,000 records whose answers are SHA-256 only.
                      They teach WHICH EXPERT, not what to say -- recognition
                      data, which is this system's weakest layer.
    NO PAIRS AT ALL   ~1.9M growth/proxy records: ids, hashes and seeds, with
                      one constant answer_rule string across 120,000 scanned.
                      Nothing to learn; the count is evidence a generator ran.

So "all the extra expert data" is mostly not answer data. The part worth
having is the routing labels and the held-out benchmark above.

## Wiring, and the three bugs only wiring can have

Integration has a failure mode no component test can see: two layers that
both answer, differently. `eval/integration.py` hunts for it. First run:
877 failures.

TERMINAL REFUSALS. "Not my question" and "your question is malformed" are
different outcomes and only the first may continue the cascade. Conflated,
"convert 5 meters to kilograms" was refused by the units layer on dimension
mismatch and then answered 500 by a rule that matched on the words `convert`
and `meters`. A vaguer layer must not overturn a determination a sharper one
already made.

ORDER BY PRECISION OF OWNERSHIP, not by specificity. Both obvious orderings
were measured and both failed:

    general arithmetic first  evaluated a span inside "Solve for x: -9x + -6
                              = -348" and returned -348.   875/5737 wrong
    all rules first           the NL layer saw four operands and the word
                              `evaluate` in "(3 + (4 × 5)) - 6", applied the
                              compound shape, answered 29 not 17. 101/422 wrong

Exact mechanisms -- named patterns, parsing, dimensional algebra -- rank
above heuristic ones whatever their generality.

DEDUPLICATE RATHER THAN ORDER AROUND. The NL `meters` rule and the units
layer both answered conversions and disagreed on "100 km/h to meters per
second" (250/9 vs 10000). Ordering hid it; deleting the rule fixed it. Two
mechanisms for one question is a defect even when the cascade picks right.


Greenfield. Takes the half that worked from each predecessor.

| | belt-atlas | Codex atlas | atlas2 |
|---|---|---|---|
| answers | stored strings | computed | **computed** |
| verifier | none | the domain is arithmetic | **per-rule independent check** |
| routing | two-stage, IDF-aware | none | **subject-first, can decline** |
| abstention | margin (fails on real questions) | none | **verdicts with reasons** |
| eval | 3 gates, negative controls | honest README | **3 gates + refusal control** |
| ceiling | 70% on real questions | 100% in-template, unmeasured out | see below |

## What it does

A question is matched to a **rule**, not a row. The rule *derives* the answer
and then derives it a second way; the two must agree. Four verdicts, kept
distinct because collapsing them is what made the predecessor undiagnosable:

    ANSWERED      one rule matched and its check agreed
    AMBIGUOUS     several matched — the question is underspecified
    UNCOVERED     none matched — outside competence
    CONTRADICTED  a rule disagreed with itself

`CONTRADICTED` cannot exist in a lookup table. Only a rule that derives an
answer two ways can catch itself being wrong.

## Measured

    in-template     5737/5737 answers recomputed and matched  (100.00%)
    held-out        9 rules removed one at a time, 5737 questions asked
                    → 5737 declined, 0 wrong answers
    refusal control 8 out-of-domain questions → 8 refused
    compression     9 surface rules → 4 primitives (ADD, MUL, NEG, INV),
                    reproducing all 5737 records; crippled basis fails 1894

## What these numbers do and do not mean

**In-template 100% proves nothing.** The rules and the corpus share a
generator — I wrote the same arithmetic that produced the data. Reported only
to show the harness runs.

**Held-out shows graceful degradation, not generalization.** Removing a rule
makes its questions *unanswerable*, and the system declines all 5737 instead
of guessing — which is the property belt-atlas lacked, where a missing fact
produced a confident wrong neighbour. But an absent rule is not an *induced*
rule. Nothing here learns the 10th template from the other 9.

**The compression result is real**, verified on every record with a negative
control. It says the corpus's information content is 4 operations plus 9
surface patterns plus operand samples — not 5737 facts, and not 640,000.

## The natural-language graft

`engine/nl.py` routes human phrasing to the same computing rules. Triggers
name the operation; **arity is structural evidence** (a question yielding two
operands excludes every four-operand rule outright, whatever words appear);
margin and disqualifiers decide the rest.

    hand-written natural questions   40/40   (IN-SAMPLE, see below)
    must-refuse questions            10/10 refused
    canonical generator prompts    5737/5737 (not tuned on)

Three real bugs, each a distinct class, found by planting traps:

  OPERAND ORDER  "subtract 20 from 327" binds [20,327] in text order and
  computed -307. Confident, wrong, the worst class. Inversion is now
  verb-sensitive: "from/out of/off of" invert, and "into" inverts only after
  `divide` -- "split 20 into 5 shares" is the other binding.

  THE STRICT PATTERN WAS DOING VERIFICATION. "solve for y: 3y squared + 2 =
  50" has three operands and says "solve", so keyword+arity answered 16 for a
  quadratic. route.py's regex rejected it. Replacing a pattern with keywords
  discards a check you did not know you had; DISQUALIFY restores it.

  SYMBOLS NAME OPERATIONS. "59 + 78 = ?" was declined until operator symbols
  counted as triggers.

**The 40/40 is in-sample and close to worthless as a generalization estimate.**
I wrote those questions and then fixed the router against them. The 5737/5737
is honest but easy -- those prompts are generator-formatted and regular.
Unseen human phrasing remains unmeasured.

Known unresolved: "divide A into B" is genuinely ambiguous in English and the
system picks the long-division reading rather than abstaining.

## The rule is not about maths

Arithmetic was only the domain the corpus happened to contain. The form is
about ANSWER GENERATION: pattern, derive, derive again differently, agree.
What changes between domains is where the second derivation comes from.

    kind        domain              rule           second derivation
    INVERSE     temperature         f_to_c         convert back
    IDENTITY    text                reverse        reverse twice == input
    REDUNDANT   dates               weekday        Zeller vs calendar arithmetic
    ENUMERATE   categorical logic   syllogism      exhaust a finite universe
    EXTERNAL    code                py_syntax      the real Python parser
    NONE        stated fact         earth_radius   none exists

`eval/controls.py` sabotages every DERIVED rule; all five checks caught it.
The ASSERTED rule reports as unverifiable rather than quietly passing.

## Which answers are safe to generate

This is what the taxonomy is for, and it is the honest answer to "generate
astronomically many pairs":

    DERIVED   unlimited. Each pair is verified as it is made. 10,000
              generated, 10,000 verified, 0 failures. But the volume carries
              no new information -- it compresses back to the 5 rules plus
              parameter samples. The count is evidence the generator ran,
              not evidence of knowledge.

    ASSERTED  zero. Refused by policy. No derivation exists, so producing a
              new pair does not generate an answer, it invents a fact.

belt-atlas was entirely ASSERTED, which is why nothing in it could be checked
and why its real-question ceiling was 70%. The Codex curriculum was entirely
DERIVED, which is why it could be scaled to 640,000 records that taught
nothing. Neither project could see the distinction because neither contained
both kinds.

## Rule induction

`engine/induce.py` derives a rule from examples with no knowledge of the
operation. Bottom-up enumerative synthesis over the verified basis (ADD, MUL,
NEG, INV) plus constants, pruned by observational equivalence -- one
representative per distinct value-vector across the training examples, which
collapses the space enormously.

Every curriculum rule, induced from 6 examples, evaluated on the rest:

    rule       train  held-out  correct     acc   induced
    add            6       393      393  100.0%   (x0+x1)
    sub            6       394      394  100.0%   (x0+-(x1))
    mul            6       392      392  100.0%   (x0*x1)
    div            6       392      392  100.0%   (x0*1/(x1))
    meters         6       611      611  100.0%   (x0*100)
    pct            6       186      186  100.0%   (x0+(x0*(x1*1/(100))))
    linear         6       661      661  100.0%   (1/(x0)*(x2+-(x1)))
    fracadd        6       660      660  100.0%   ((x0*1/(x1))+(x2*1/(x3)))
    compound       6      1994     1994  100.0%   (-(x3)+(x2*(x0+x1)))
    TOTAL                 5683     5683  100.0%

Two beat the hand-written versions: fracadd came out as a/b + c/d rather than
(ad+cb)/(bd), and linear as (c-b)*(1/a).

Not memorisation -- eight operations absent from the curriculum, 200 held-out
each, all 200/200:

    triple then add 7    (1+((x0+2)*(1+2)))          built 3 and 7 from constants
    2a - 3b              -((x1+(2*(x1+-(x0)))))
    (a-b)/(a+b)          (1/((x0+x1))*(x0+-(x1)))
    average, a^2, 1/a+1/b, a*b*c, percent-of         all found

`engine/learn.py` closes the loop: examples -> induced expression -> a Rule
the router can use. A never-seen operation becomes answerable in one step.

### What induction does not do

  BASIS-BOUND      it searches ADD/MUL/NEG/INV and constants {1,2,100}. It
                   cannot reach powers, roots, or modulo, and it cannot
                   induce the reverse/weekday/syllogism/py_syntax rules at
                   all -- those are not arithmetic compositions.
  DERIVE ONLY      a rule is pattern + derive + check. This induces DERIVE.
                   Which spans of text are the operands, and which questions
                   the rule is even about, are still written by a human. The
                   system learns the computation, not the recognition.
  EXPONENTIAL      cost grows with expression size. fracadd at size 9 took
                   36s; size 12 is out of reach.
  THE INDUCED CHECK IS NOT A PROOF. Both expressions are fitted to the same
                   examples, so they agree on training by construction. Their
                   disagreement on new input detects OVERFITTING, not
                   incorrectness.

### A kind the induction work exposed

An induced rule with no second expression was being labelled ASSERTED, which
was wrong and would have banned generating from it. A computation exists; it
simply has no redundant confirmation. Three kinds, not two:

    DERIVED            computed and independently checked. Generate freely.
    DERIVED_UNCHECKED  computed, no second derivation. Generating is safe --
                       the pair is reproducible -- but it cannot catch itself
                       being wrong.
    ASSERTED           no computation exists. Generation refused.

## The pipeline, end to end

    raw (prompt, answer) pairs
      -> pattern.py     anti-unify surface forms       -> template + operands
      -> induce2.py     meet-in-the-middle synthesis   -> shortest program
      -> distinguish.py rivals + generated counterexamples -> determined?
      -> route/nl.py    recognition and abstention
      -> kinds.py       execute + independent check
      -> explain.py     English derivation, round-trip verified

Nothing in that chain is hand-written per rule. What is supplied: the
primitive basis, and the prior that a numeric literal is a candidate operand.

## Measured

    induced programs                9
    expression sizes                3 - 9
    candidates built (bottom-up)    116,596 - 945,994
    candidates built (meet-in-mid)  144 - 1,202          507x - 3041x faster
    pruned by observational equiv.  73.4%
    training constraints per rule   6
    recognition                     9/9 templates, 5737/5737 prompts,
                                    no cross-matching between clusters
    held-out execution              5683/5683   100.00%
    counterexample survival         9/9 DETERMINED over 800 probes each
    explanation fidelity            5683/5683   100.00%

## Three qualifications, and what was done about them

SMALLEST-FIRST IS A BIAS, NOT A GUARANTEE. A short accidental program can fit
a small dataset. Addressed by keeping held-out evaluation separate from
induction and by generating counterexamples; not by trusting brevity.

OBSERVATIONAL DEDUPLICATION IS EXACT ONLY OVER THE EXAMPLES TESTED. Confirmed
empirically rather than argued: bottom-up and meet-in-the-middle returned
DIFFERENT programs for `pct` from identical data, because they stored
different representatives of the same value class. distinguish.py now keeps
the shortest candidate per OPERATOR SIGNATURE and separates survivors with
generated inputs. Partiality is not counted as disagreement -- 1/(1/x) equals
x everywhere it is defined, and treating that as a rival made all five basic
operations look underdetermined.

SIX EXAMPLES ARE SUFFICIENT FOR THIS FAMILY, NOT UNIVERSALLY. Now a
measurement rather than an assumption: all 9 families are DETERMINED, meaning
every rival program fitting the 6 examples agrees with every other across 800
generated inputs. A different corpus would have to be measured again.

## Beyond observed families

Two fixes for "it only recognises families it has seen".

GENERATE FAMILIES (`engine/families.py`). A family is just (surface form,
operand slots, program), and the program space is the basis. Enumerate
distinct-behaviour programs, render each as notation, sample operands,
compute answers -- the family exists before anyone asks a question in it.

    119 families generated, 119 verified by re-induction (100%)

Verification matters more than the count: each family is induced BACK from
its own examples and the recovered program must agree with the original on
fresh inputs. That rejects families whose surface does not determine the
operands, and families extensionally equal to a simpler one. Shipping
unverified generated families would be the 640,000-proxy-record failure
wearing a different hat.

PARSE COMPOSITIONALLY (`engine/parse.py`). Generation still yields a finite
list. But arithmetic is compositional -- an unseen form is built from parts
already known -- so parsing the structure removes the family requirement
entirely. Templates become unbounded and examples-per-template become zero.

    novel forms, never observed, no examples:  2807/2807  100.00%
    declined 0, wrong 0, nesting depth 2-5, 1,848 distinct surface templates

Two independent implementations -- recursive descent plus Python's own ast
over Fractions, different parsers and different evaluators. Agreement is a
REDUNDANT check; disagreement returns nothing.

### Testing the boundary instead of asserting it

I claimed dates and stated facts were outside this. Two of those three were
wrong, and each turned out to compose over its own algebra rather than over
arithmetic.

UNITS (`engine/units.py`). A unit is a scale factor plus a dimension vector,
so a table of ~28 units generates every pair and an unbounded set of compound
units nobody enumerated.

    266/266 correct across 266 distinct unit pairs   (the corpus had 1)
    490 cross-dimension questions refused
    km/h -> m/s, kg*m/s2 -> g*cm/s2, m/s2 -> km/h2   none of them listed

The dimension vector IS the abstention rule, and it costs nothing. Metres to
kilograms is not a hard question, it is a malformed one, and the exponents
disagree before any arithmetic runs.

DATES (`engine/dates.py`). Dates and durations form a torsor: date-date is a
duration, date+duration is a date, and those compose.

    3200/3200 correct
    including chains never enumerated: "what day of the week is 90 days
    after 100 days before 2026-09-15"
    date + date refused on TYPE, not by a rule saying so

STATED FACTS. These genuinely resist, and now it is measured rather than
assumed. Over belt-atlas's 350 facts:

    questions containing any number          13   3.7%
    answers containing a number             195  55.7%
    both -- the only ones that could derive    7   2.0%

For the arithmetic corpus that last figure is 100%. Here the answer carries
information the question does not, which is the definition of an asserted
fact. There is nothing for induction to be a function OF, retrieval is the
only available mechanism, and that is why belt-atlas capped at 70%.

### Moving the last row too: grounding

A stated fact is not a function of the question. A stated fact WITH ITS
SOURCE IN CONTEXT is, and the function is extraction -- so the answer becomes
checkable after all. What is verified is FAITHFULNESS, not truth: the rule
cannot tell you 6,371 km is correct, only a source can. It can tell you the
answer is a verbatim span of the supplied text and exactly where.

That yields the verdict a retrieval system cannot produce about itself:

    ANSWERED     verbatim span, offset recorded as provenance
    UNGROUNDED   nothing in the context answers it -- decline
    INVENTED     an answer was produced that is NOT in the context

Retrieve-then-ground over belt-atlas's 350 facts -- the responder picks the
row, grounding verifies the span:

    span-verified and correct   235
    WRONG                         0
    declined                    115

67.1% looks like belt-atlas's 70%, and it is a different 67%. That number
contained confident wrong answers; this one contains none. Grounding converts
wrong answers into declines, which is the trade worth making.

THE BILL. Grounding is paid in prefill, priced with belt-atlas's measured law
(TTFT = 7.2s + 0.491s x tokens, R^2 = 0.9975):

    whole net in context   12,686 tokens   6,236s  (104 min)
    retrieved gloss only       28 tokens      21s
    ratio                                    297x cheaper

Which is the argument for retrieval and grounding together rather than either
alone: retrieval narrows the context, grounding verifies the extraction, and
the token bill scales with the retrieved span instead of the corpus.

### Corpora too large to prefill

Grounding also answers what to do with a prompt that cannot be a prompt. At
the measured rate a 10M-token context costs

    7.2 + 0.491 x 10,002,398 = 4,911,185s = 56.8 DAYS

so chunking is not an optimisation, it is the difference between answerable
and not. Measured on a real 40 MB / 10M-token corpus with 400 planted facts:

                    whole prompt        chunked + grounded
    prefill         56.8 days           477 s
    retrieval       --                  0.10 ms
    context/query   10,002,398 tokens   956 tokens
    verified        --                  400/400, 0 invented
                                        ~8,900x cheaper

What survives chunking is the PROVENANCE CHAIN. Every answer is a verbatim
span with a chunk id and an offset, so the reasoning is a sequence of
citations rather than state held in a window. Losing the thread is what
happens when the thread lives in resident context; here it lives in the
chain and can be audited afterwards.

The index is symbolic, and that was measured rather than preferred. Over a
million tokens belt-atlas compared the two candidates head to head:

    explicit note index            100.0% exact-chunk recovery
    expert-signature similarity     11.5%

THE INVENTED VERDICT PAID FOR ITSELF. The first run returned 25 INVENTED of
400. Not noise: 25 fact sentences were cut by a chunk boundary, so no single
chunk contained the span. 25% overlap took it to 400/400 for 24% more
context. A system without that verdict would have returned 25 unsupported
answers and reported 100%.

### Where the boundary actually sits

Not "compositional vs not" but WHETHER THE ANSWER IS A FUNCTION OF THE
QUESTION. Arithmetic, units and dates all are, over three different algebras.
Stated facts are not -- until the source is in context, at which point they
become extractive and the extraction is checkable. What no machinery here can
establish is whether the source is RIGHT. Faithfulness is verifiable; truth
is a citation.

## Not done

- **Rule induction.** The open question: derive a missing rule from the others.
  Until that works, "generated prompts are naturally right" holds only inside
  the templates someone already wrote.
- **Natural-language questions.** Every prompt here is generator-formatted.
  belt-atlas measured the gap between derived and real phrasings at 98% vs
  70%; nothing here has faced a real one.

## Layout

    rules/arith.py     rule table: pattern + compute + independent check
    engine/route.py    routing and the four verdicts
    eval/gate.py       in-template, held-out, refusal control
    eval/compress.py   the primitive-basis claim, with a negative control
