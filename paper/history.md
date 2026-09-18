# Atlas — the documented history

Transcribed 2026-09-18 from the rules themselves. Nothing in this
document was typed by hand: every sentence was produced by the rule it
describes, so it cannot drift from what the system actually does.

## The chain

57 links from a nebula to a head. Each one names the rule that drives
it and the module the rule lives in. A link is DERIVED when something
here forces it, FORCED when it is both permitted and driven, CROSSES
when it is permitted and nothing drives it, and MISSING when it is a
gap that has been named rather than filled.

### 1. planck -> quark

*DERIVED* &nbsp; `epochs.EPOCHS`

quarks unbound; no hadrons (t = 1.0e-12 s)

### 2. quark -> hadron

*DERIVED* &nbsp; `epochs.EPOCHS`

quarks confine: protons and neutrons exist (t = 1.0e-06 s)

### 3. hadron -> lepton

*DERIVED* &nbsp; `epochs.EPOCHS`

neutrinos decouple; n/p ratio freezes (t = 1.0e+00 s)

### 4. lepton -> bbn

*DERIVED* &nbsp; `epochs.EPOCHS`

primordial nucleosynthesis: H, D, He3, He4, Li7 (t = 1.8e+02 s)

### 5. bbn -> the mass-5 and mass-8 gap

*DERIVED* &nbsp; `epochs.BBN_BARRIER`

25% helium and almost nothing heavier, because no stable nucleus at
mass 5 or 8, so the chain from He4 has no two-body bridge;

### 6. bbn -> recombination

*DERIVED* &nbsp; `epochs.EPOCHS`

atoms form; the universe goes transparent (t = 1.2e+13 s)

### 7. recombination -> first_stars

*DERIVED* &nbsp; `epochs.EPOCHS`

population III ignite: hydrogen burning (t = 6.3e+15 s)

### 8. first_stars -> stellar_c

*DERIVED* &nbsp; `epochs.EPOCHS`

triple-alpha: carbon, oxygen (t = 3.2e+16 s)

### 9. stellar_c -> supernova

*DERIVED* &nbsp; `epochs.EPOCHS`

elements to the iron peak, then r-process (t = 9.5e+16 s)

### 10. supernova -> ns_merger

*DERIVED* &nbsp; `epochs.EPOCHS`

heavy r-process: gold, platinum, uranium (t = 3.2e+17 s)

### 11. ns_merger -> a nebula with metals

*DERIVED* &nbsp; `abundance.channels`

every naturally occurring element has a production channel and the
heaviest stable one is named

### 12. a nebula -> a star and planets

*DERIVED* &nbsp; `genesis.composition`

condensation of minerals by temperature; Earth's iron comes out at
32.0% against a measured 32.1%

### 13. planets -> one in the band

*DERIVED* &nbsp; `evolve.habitable_band`

the carbonate-silicate thermostat puts the band at 1.000-1.901 AU,
derived from radiative transfer and not fitted to Earth

### 14. a warm ocean -> a cold brine

*DERIVED* &nbsp; `cold.temperature_for`

copying is discrimination, mu = exp(-dG/kT), so fidelity is a
temperature: the window runs 252-259 K, seven kelvin wide, bounded
below by the eutectic and above by sloppy copying

### 15. brine -> an autocatalytic set

*DERIVED* &nbsp; `closure.length_closing_derived`

a set closes when about half its reactions have a catalyst, p*M = 0.48,
which at four nucleotides needs polymers to 13 bases -- under the 20
earthlab derives for assembly

### 16. a closed set -> a bounded cell

*DERIVED* &nbsp; `earthlab.size_window`

closure needs 1.58 microns to hold the molecule types and diffusion
allows 47.5; the window is two rules meeting, not one measurement

### 17. a cell that could be -> chemistry that sustains itself

*DERIVED* &nbsp; `occurrence.closes_in_one`

the gate said yes or no and occurrence needed a rate. One compartment
at the closure floor holds 1e10 molecules, which is every polymer to 14
bases, and p*M = 3.58 against the 0.48 closure needs -- at the MEASURED
catalysis of 1e-8. An ocean is 8.1e34 such compartments

### 18. self-sustaining chemistry -> one that divides

*DERIVED* &nbsp; `heredity.divides_at`

two spheres of half the volume need 2^(1/3) times one sphere's area,
26% more; lipid is made in proportion to contents so area accrues as V
while a sphere needs V^(2/3). A vesicle divides exactly when it doubles
and nothing decides to

### 19. one that divides -> one that inherits

*DERIVED* &nbsp; `heredity.copies_per_type`

28 copies of each of 3.6e8 types, so a half-split misses one with
probability 2^-28. Heredity is what copy number does under a coin flip,
not a mechanism added

### 20. one that inherits -> one that is selected

*DERIVED* &nbsp; `heredity.lost_per_division`

1.39 types lost per division, and 10% of reactions have exactly one
catalyst, so about half of daughters cannot close. Variation and
differential survival, neither added and no mutation rate introduced

### 21. a selected lineage -> one that copies a sequence

*DERIVED* &nbsp; `template.templated_fraction`

a ligation is templated when its product's complement is present, and
THE TEMPLATE IS THE CATALYST. 25,488 of 25,488 ligations have one
available, because a complete polymer set is closed under
complementation. It selects the join rather than permitting it, and
comp(comp(s)) is s, so two rounds replicate

### 22. a copied sequence -> one that is read

*DERIVED* &nbsp; `code.affordable_code`

a code is the rule that closes reading, and it is not free: each
meaning costs an adaptor and every adaptor is a sequence. The modern
20-letter code needs 1,520 bases against the 200 fidelity allows -- it
does not fit. Five meanings do, so the first code was small and how
small is set by temperature

### 23. a small code -> a cell that is

*DERIVED* &nbsp; `frozen.cost_of_change`

a mapping is selected by the cost of CHANGING it: with 5 meanings over
100 codons one change breaks 100% of every sequence written so far, and
it is total from the first ones, before anything has had time to be
good. Something selects HAVING a code and is blind to WHICH, which is
why the real one looks arbitrary

### 24. LUCA -> eukaryote

*FORCED* &nbsp; `ancestry.steps + lineage.energy_per_gene_gain`

PERMITTED: CHOSEN | DRIVEN: a prokaryote makes ATP across its outer
membrane (area, r^2) and holds its genome in volume (r^3), so energy
per gene falls as 1/r -- a large prokaryote starves its own genome.
Internalising membranes multiplies area without touching volume and
buys 200x, which is what a mitochondrion is | HOW: omit a step of
phagocytosis: engulf, fail to digest

### 25. eukaryote -> multicellular

*FORCED* &nbsp; `ancestry.steps + biome.escalation_stops_at`

PERMITTED: MEASURED | DRIVEN: light is the only pressure in this
repository that rewards being LARGER: a rival eating your food takes a
share, one standing over you takes all of it, every day it stands there
| HOW: omit a step of division: divide, fail to separate

### 26. multicellular -> large-bodied

*FORCED* &nbsp; `ancestry.steps + biome.escalation_stops_at`

PERMITTED: MEASURED | DRIVEN: the same ratchet, and it does not stop at
the diffusion limit -- it stops where the cost of the structure exceeds
the light being fought over | HOW: the same, continued

### 27. large-bodied -> skeletal

*FORCED* &nbsp; `ancestry.steps + life.BONE_COMPRESSIVE`

PERMITTED: MEASURED | DRIVEN: past the size the ratchet drives you to,
a body on land cannot hold itself up without one; this is not an option
taken but a bill arriving | HOW: omit a step of mineral handling:
precipitate, fail to dissolve

### 28. skeletal -> land

*FORCED* &nbsp; `ancestry.steps + biome.surface_light`

PERMITTED: MEASURED | DRIVEN: land carries the same 236 W/m2 and,
before anything is there, no competitor at all -- an unexploited flow
is a pressure and engine/biome.py already prices what a competitor
costs | HOW: combine: the same body, a different medium

### 29. land -> endotherm

*FORCED* &nbsp; `ancestry.steps + shelter.coldest_survivable`

PERMITTED: MEASURED | DRIVEN: holding temperature buys the hours and
latitudes an ectotherm cannot work in, which is niche nobody is holding
| HOW: omit a step of thermal exchange: lose heat, fail to

### 30. endotherm -> large brain

*FORCED* &nbsp; `ancestry.steps + tools.pays_for_a_brain`

PERMITTED: MEASURED | DRIVEN: one femur of marrow is 70% of a forager's
day against the 14% a human brain costs over an ape's -- it pays 5.2x,
and engine/tools.py derives the flaked edge that opens it | HOW:
duplicate: neural tissue, and more of it

### 31. large brain -> us

*CROSSES* &nbsp; `ancestry.steps`

RECORDED

### 32. a large brain -> a filter, not a store

*DERIVED* &nbsp; `learning.fill_time_years`

4.7e+14 bits of synapse against one nerve's 1e7 bit/s fills in 1.49
years, before the child can walk, so the work is discarding

### 33. a filter -> recognition

*DERIVED* &nbsp; `recognize.sharp_fraction`

the sharp patch is 0.028% of the field and sweeping it takes 900 s, so
the periphery commits before evidence arrives

### 34. recognition -> one head

*DERIVED* &nbsp; `senses.inference_share`

the five senses between them reach 8 of the 13 constraints that bind on
a human, and they do not overlap -- which is why there are five. The
other 5 (allocation, fidelity, oxygen to tissue, provisioning, solvent)
emit no signal at all: provisioning is eighteen years ahead and
allocation is a fact about other people. 38% of what binds must be
MODELLED against 33% on a bacterium, and a model needs somewhere to
sit. That is what a head adds over an eye

### 35. one head -> several

*DERIVED* &nbsp; `civ.smallest_group`

a child costs 3.0 adult-years and one adult keeps no margin for a bad
season; 2 clear it, so company is arithmetic and not preference

### 36. several heads -> a shared corpus

*DERIVED* &nbsp; `school.grow`

speech carries 0.0122% of a lifetime's input and is worth it because it
is the part somebody already selected

### 37. a corpus -> an allocation rule

*DERIVED* &nbsp; `rank.rank_is_priced`

the absence was in the scenarios. N adults carry 1.9N children, and
below that line the order of serving changes nothing while above it
somebody does not eat. Rank is not a preference, it is an allocation
rule, and its price is discontinuous: zero below the carrying number
and a whole 82 W life above it

### 38. an allocation rule -> regard

*DERIVED* &nbsp; `regard.regard_is_worth`

who eats is who can take, and taking is reach and force -- the same
arithmetic that settles a predator. But between species the loser is
EATEN and 10% transfers, while within one species nothing transfers and
the contest produces no energy at all. A fight costs 4.2 MJ and a tenth
of a life, allocation needs settling 7,300 times in twenty years, and
remembering the outcome costs 1.4 microjoules. Regard is the contest
not held again, worth 2.7e19 times what it costs

### 39. regard -> transitivity

*DERIVED* &nbsp; `tradition.transitive_leverage`

regard is a remembered outcome, and outcomes compose. Observe the 27
adjacent links of a band of 28 and A>B, B>C forces A>C for all 378
pairs -- 14 facts per fact observed. engine/group.py was already
spending this (135 contests, not 378) without the rule being written
down. It is not universal: rock-paper-scissors composes to nothing, and
when an intransitive triple turns up the 378 contests come back, which
is why the exception is worth naming

### 40. transitivity -> a corpus that outlives its tellers

*DERIVED* &nbsp; `tradition.stock`

a generation adds a and keeps r, so the stock settles at a/(1-r) and
the whole question is r. An hour after dark for the 18-year
provisioning span is 78,840 tellings, and k ln k inverts to 8,692
items, so r = 0.99988 and the stock is 8692a. Epigenetics has a
two-generation half-life, r = 0.71, stock 3.4a. 2,546x apart:
epigenetics is an echo and cannot compound. Only the spoken channel
does, which is why the accumulation is cultural and not genetic

### 41. a corpus -> a band that walks at its slowest

*DERIVED* &nbsp; `craft.kept_innovations_ratio`

walking is an inverted pendulum, so speed goes as sqrt(g*L) and pace is
leg length and nothing else. A four-year-old walks 3.8 km/h against an
adult's 5.3, the band moves at the child, and the ratio is
sqrt(0.45/0.90) = 0.707 -- a square root, not a preference. Hazards are
charged by the DAY and forage is collected by the KILOMETRE, so going
slowly does not avoid problems, it concentrates them 1.41x per km. And
it brings 28 heads to them instead of one: 39x the kept innovations per
km, with the unmeasured per-head solve rate cancelling. Slowness is not
the price of company, it is the input

### 42. a slow band -> a discovery nobody made alone

*DERIVED* &nbsp; `tradition.settle_years`

one band waits 500 years for a one-in-500 accident. With 16 bands the
first hits at 31 years and coupon collector carries it to the rest in
22 more, so everyone holds it by year 53. Some bands get it first and
the tail is long, but it arrives. Discovery wants many bands and spread
wants few, so 1/(bp) + b ln b / 2 has a derivative and there is a band
count that settles fastest -- nobody chose 16

### 43. a discovery nobody made alone -> specialists

*DERIVED* &nbsp; `craft.best_depth`

oral tradition is a game of telephone: one retelling corrupts an item
with p=0.1, so a single line of transmission tops out at 10 items and
nothing accumulates. What saves it is that several people hold the same
item and the version that disagrees gets dropped -- 28 voters take the
consensus error to 5.6e-8. The band is not an audience for the corpus,
it is the error correction ON it. So splitting into specialties
multiplies breadth by s and divides the votes by s, and the trade
bottoms out at 2 specialties 13 deep carrying 9,332a -- against 280a if
each of the 28 specializes alone and every skill dies with its holder.
How specialized a band can be is transmission fidelity and headcount,
not how many useful skills exist

### 44. specialists -> a claim that carries its own check

*DERIVED* &nbsp; `literacy.equivalent_voices`

a speaker cannot compare their telling to anything -- the source is
gone as it is spoken, so the only correction available is other people,
and it takes 13 of them. A copyist has the original in front of them
and can read back: one pass takes a 0.1 slip to 0.01 (worth 5
speakers), three passes to 1e-4 (worth 13), from ONE person. Writing is
the first channel here where a claim carries the thing that would catch
it being wrong, and that buys 9 specialties instead of 2 with nobody
added. But it bootstraps orally -- you cannot learn to read from a book
you cannot read -- so it needs 5 holders or the script is lost in a few
generations, and its value goes as f^2 because it takes a writer AND a
reader, which is why it crawls for a thousand years before it pays

### 45. a written claim -> a crowd big enough to stay sick

*DERIVED* &nbsp; `disease.critical_community`

nothing so far gives anyone a reason to cook. A crowd disease needs one
fresh susceptible per 10-day infectious period or the chain breaks, and
births arrive at N/25 a year, so it cannot live below 912 people -- a
band of 28 burns through every host in a month and the pathogen dies
with them. Foragers have parasites, not epidemics. What makes 33 bands
sit together permanently is the 365-day grain harvest from
engine/accident.py, and settled ground carries 114x the shed load of a
camp left at 73 days. The pathogen is not an extra assumption, it is
the grain harvest seen from the other side

### 46. a crowd that is sick -> fire, washing and walls

*DERIVED* &nbsp; `disease.cooking_pays`

1e6 organisms a gram over 200 g against an ID50 of 1e4 is infection
with p=1.00; seven decades of killing takes it to 0.002. A bout is 7
days of fever at +26% BMR plus the food nobody went and got, 132 MJ,
against 2.3 MJ of wood to heat a kilo 65 K. 58x, and nobody had to
understand why. A wall is worth 526 MJ a year on thermoregulation alone
-- 53 days of food -- and the separation from your own ground comes
free. Each is adopted for a reason that is not hygiene and kept because
the people doing it are the ones still alive

### 47. a wall -> somebody who holds the store

*DERIVED* &nbsp; `power.concentration`

engine/group.py got a flat answer and it was right to: strength_share
is 1/n and spare_per_head is zero to 1e-14 J at every band size. A
forager is not egalitarian by disposition, there is simply no second
helping to withhold. What changes is geometry. A band of 28 eats 65 km2
with a 28.6 km border; a granary's border is 31 m -- 909x. You cannot
own a range and you can stand in the door of a barn. Strength is
headcount, so holding it still needs 15 of the 28 in on it, worth only
1.9x an equal share. The wall built for warmth takes that to 8 and
3.5x, and a written claim outlives its witnesses, which is what
inheritance is. A stock crosses a death; a flow cannot

### 48. a holder -> a specialist worth their scarcity

*DERIVED* &nbsp; `merit.pivotal`

the other source of power, and it is not the value of what you can do.
You are worth what the band cannot do without, which is value divided
by how many others hold the skill: 1 holder 100%, 5 holders 20%, 28
holders 4%. The skill's usefulness does not appear in that at all. And
engine/craft.py needs 5 holders or the skill dies in a few generations,
while its holder wants 1 -- 5x the power for a twelfth of the lifetime.
Neither is being unreasonable: the specialist's horizon is one life and
the skill's is generations. Lost crafts do not need a catastrophe, they
need someone who profited by not teaching

### 49. earned standing -> an heir who did not earn it

*DERIVED* &nbsp; `merit.mismatch`

under selection the holder is the best of 28, the expected max of 28
draws = sqrt(2 ln 28) = 2.58 sigma. Under inheritance the holder is
whoever was born, and ability regresses by half a generation while a
WRITTEN claim regresses by nothing: 1.29s, 0.65s, 0.08s by the fifth.
The holding is then 32x what the ability warrants. This is not
villainy, it is two different heritabilities. And it is not
deterministic either -- the heir is a draw, so P(heir >= founder) is 1
in 15 at one generation and 1 in 162 at five. A good king is a tail
probability with a number, and anything simulating this should draw
from that number rather than a knob

### 50. a settled order -> artifacts of many parts

*DERIVED* &nbsp; `intricacy.settle`

an artifact is a composition, so what a group can build is the subsets
of what it holds at once: 2^s - 1. Speech gives a band 2 specialties
and 3 possible things, and it is a FIXED POINT, not an early stage --
the corpus could hold 13 parts' worth but fidelity supports 2, and more
people means more mouths on the same one-lifetime-of-evenings ceiling.
Writing moves the binding constraint from fidelity, which nothing fixes
from inside, to how many can be spared from the fields, which yield
fixes. Iterating surplus -> scribes -> corpus -> specialties -> surplus
settles at 24 parts and 2e7 designs. It converges rather than running
away, because the corpus enters as a logarithm and the designs come out
as an exponent: doubling what is written buys one more part

### 51. artifacts of many parts -> villages that keep in touch

*DERIVED* &nbsp; `trade.knowledge_spread_years`

a porter eats the cargo. 30 kg at 32 km a day burning 14 MJ against
grain at 15 MJ/kg spends 0.058 kg per km of round trip, so a load
arrives as nothing at 516 km and has doubled in price at 258 km --
grain is not traded far because the cargo and the fuel are the same
substance. Technique weighs nothing AND the carrier still has it after
handing it over, which no other cargo does, so a region shares what it
knows long before it can share what it grows. And settling put
neighbours 5.2 km apart instead of 9, so they meet 22 times a year
instead of 2 and a discovery crosses 40 villages in 6.8 years instead
of 74. Forty villages in touch are 36,480 people: 12,160 specialties
against a village's 304, and 2.4x the output per worker from Wright's
law. Nobody built a city

### 52. a region in touch -> anyone actually better off

*DERIVED* &nbsp; `intricacy.per_capita_exponent`

this was carried as a GAP at 3.1.113 and the gap was an arithmetic
error: per-capita surplus was computed by subtracting mouths at N^1
from two terms that were ALREADY per worker, which made every invention
look as though it were being shared out and thinned. It is not. A loaf
feeds one person, so loaves per head is loaves/N; a technique for
making loaves is used by everyone who knows it, at once, and nobody has
less of it for that. The design stock is NOT divided, which is why the
knowledge terms carry no N underneath. It runs the other way too: an
invention costs one specialist's time whoever uses it and returns b to
each of N, so the worst one worth making needs only b > C/N -- more
people is more ideas AND more users per idea. The one genuinely rival
input is LAND, which does not grow, so supply at N^0.372 against a 0.30
land share leaves N^0.072. The crossover is a land share of 0.372:
while farming is more than 37% of output, technology rises and living
standards do not. The escape is not an invention, it is a share

### 53. a surplus -> a specialist who can afford the kit

*DERIVED* &nbsp; `capital.affordable_specialists`

everything above counted the specialties a channel could keep and
assumed anyone could take one up. A specialty is a toolkit and a
toolkit is other people's labour: a 23.5-part kit is 1,177 labour-days,
so a specialist costs 365 food-days of eating plus 118 of kit, and a
village of 912 keeps 368 of them rather than the 487 the food alone
allows. 24% of possible specialists are priced out by their own tools.
One person works one craft however rich they are, so surplus in fewer
hands than S/K sits idle and thinner than K buys no kit at all -- the
right spread is 368 of 912, and the walled holders of engine/power.py
sit below it. Concentration here is not only unfair, it is IDLE
CAPITAL, which is a cost the holders pay too

### 54. a gain per head -> a gain nobody actually receives

*DERIVED* &nbsp; `capital.income_stats`

the per-head figure is a MEAN and the distribution under it is skewed
by construction, before anyone is greedy. engine/merit.py pays a
specialist 1/k for a craft held by k people, and k is not the same for
every craft: at mean depth 3 the mean is 1.33x the median, the rarest
craft pays 4x the median on scarcity alone, and a walled holder
multiplies that to 14x. So 'everyone is 1.3x better off' is a sentence
no individual satisfies -- a few are near 14x, most are at or below the
median. Every per-head number on this chain is the first moment of a
skewed distribution and is not to be quoted alone

### 55. more that is known -> less that is new, and more of it

*DERIVED* &nbsp; `novelty.multiple`

designs are 2^s and s is log2(corpus), so the exponent and the
logarithm cancel and the space to be new in is LINEAR in population --
used up by being found, added to by people arriving, neither winning.
The steady state depends on the GROWTH rate and not the size: a
population that has stopped growing exhausts its design space however
large it is. But exhaustion is NOT what makes novelty per head fall
here -- at 3,244 designs a head, 99.7% of trials still land on
something new. The fall is the TEAM. A design of p parts needs p people
who between them hold p crafts, and p is a logarithm of what is already
known, so 912 -> 36,480 takes novelty per head to 0.80 while novel
designs in total rise 32x. Each person invents 20% less and the world
gets 32x more, both at once. It falls because knowing enough to add to
it costs more, not because there is less left

### 56. designs counted -> things that can be named

*DERIVED* &nbsp; `artifact.bootstrap`

a count is not a technology. Giving the 2^s designs actual objects --
16 physical capabilities, each grounded in a rule that already existed
for another reason, heat in the cooking bill and optics in the
diffraction limit that bounded an eye -- immediately showed that
composition depth is NOT the constraint. The prerequisite tree is 5
deep against a budget of 23.5, so on composition alone a literate
village reaches a governed engine. It does not. The gate is
TEMPERATURE: every step past cordage is a material you cannot have
until you reach the heat that makes it, and what you can reach depends
on what you have built. An open fire is 1100 K; a hearth and charcoal
buy 1400 and copper; bellows need a metal tuyere, which needs the
smelting the bellows were for, and that loop is why copper comes at
round 3 and steel at round 5. Six rounds from a hafted axe to a
governed engine, and nobody put the engine last -- combustion did

### 57. one gate -> whichever scalar is short

*DERIVED* &nbsp; `artifact.tolerance`

temperature stops moving at round 5 and 1750 K, and everything after it
-- vacuum, alloy, semiconductor, switching, inference -- is reachable
at exactly that heat and was not available for two centuries. The
scarce thing changed: not how hot you can get but how accurately you
can place matter, 1e-1 by hand through 1e-9 printed through a mask. The
same bootstrap shape holds and the same trap: setting the first rung
too high DEADLOCKED it, because a screw-cutting lathe is made of gears
and the first gears must therefore be filable by hand, exactly as the
first transistors were millimetre-scale before lithography existed. A
ladder needs a rung reachable from the ground. Asked to run two
centuries past now the model gives 29.4 -> 49.4 parts and an exponent,
and refuses to name anything, because a name for a primitive nobody has
made is a word with no rule under it

## The technology

21 physical capabilities, each grounded in a rule that already existed
for another reason. An artifact is a set of them used together. What
gates the sequence is not how many parts anyone can compose -- the tree
is only 9 deep against a budget of 29.4 -- but TEMPERATURE: every step
past cordage is a material you cannot have until you can reach the heat
that makes it.

### What can be reached, and how hot

An open wood fire is 1100 K. Each thing built raises it, and the things
that raise it need the things it makes:

- **a hearth that keeps it in** +150 K — needs containment
- **charcoal instead of wood** +150 K — needs containment, heat
- **bellows on a metal tuyere** +200 K — needs cordage, smelting
- **a regenerative flue** +150 K — needs smelting, gearing

### The bootstrap

**Round 1** — 1100 K

- **cordage** (300 K, needs nothing) — fibre twisted until it holds &nbsp; `tools.grip_gate`
- **edge** (300 K, needs nothing) — a worked face that cuts &nbsp; `tools.grip_gate`
- **heat** (600 K, needs nothing) — fire held at a temperature &nbsp; `disease.cook_cost_mj`
- **lever** (300 K, needs nothing) — a length trading force for distance &nbsp; `tools.torque`

**Round 2** — 1100 K

- **containment** (1000 K, needs heat) — fired clay that holds against a gradient &nbsp; `atoms.Pool`
- **mark** (300 K, needs edge) — a durable trace standing for a sound &nbsp; `literacy.copy_error`
- **rotation** (300 K, needs edge, lever) — a bearing and a round thing on it &nbsp; `biome.escalation_stops_at`

**Round 3** — 1400 K

- **breeding** (300 K, needs mark) — kept records of who bred with whom &nbsp; `heredity.copies_per_type`
- **smelting** (1350 K, needs heat, containment) — ore reduced past its melting point &nbsp; `arrhenius.rate`

**Round 4** — 1600 K

- **gearing** (1350 K, needs rotation, smelting) — teeth that carry a ratio &nbsp; `tools.torque`

**Round 5** — 1750 K

- **electricity** (1700 K, needs smelting, rotation) — charge moved on purpose &nbsp; `landauer.kT`
- **optics** (1700 K, needs heat, containment) — glass shaped to bend light &nbsp; `senses.diffraction_limit`
- **pressure** (1700 K, needs smelting, containment) — a vessel that holds against itself &nbsp; `eos.pressure`
- **spring** (1700 K, needs smelting) — steel: stored strain released on demand &nbsp; `eos.strain`

**Round 6** — 1750 K

- **regulation** (1700 K, needs gearing, spring) — a machine that corrects itself &nbsp; `control.feedback`
- **steam** (1700 K, needs pressure, heat) — heat turned into a stroke &nbsp; `carnot.efficiency`

**Round 7** — 1750 K

- **alloy** (1700 K, needs smelting, regulation) — composition held to a specification &nbsp; `atoms.Pool`
- **vacuum** (1700 K, needs pressure, regulation) — a volume with the air taken out &nbsp; `eos.pressure`

**Round 8** — 1750 K

- **semiconductor** (1700 K, needs vacuum, alloy) — a crystal pure enough to switch &nbsp; `landauer.kT`

**Round 9** — 1750 K

- **switching** (1700 K, needs semiconductor, electricity) — a gate that opens on a signal &nbsp; `landauer.kT`

**Round 10** — 1750 K

- **inference** (1700 K, needs switching, regulation) — statistics run at a scale no head holds &nbsp; `learning.store_bits`

### The things themselves

Names are vocabulary and derive nothing. Each is checked against the
derivation: a name whose parts never become reachable is an error, not
a prediction. The order is not a list anybody wrote.

- **round 1, 1100 K** — a bow (cordage + lever)
- **round 1, 1100 K** — a hafted axe (cordage + edge + lever)
- **round 2, 1100 K** — a cooking pot (containment + heat)
- **round 2, 1100 K** — a potter's wheel (lever + rotation)
- **round 2, 1100 K** — a sealed tablet, an account (containment + mark)
- **round 2, 1100 K** — a spindle (cordage + rotation)
- **round 3, 1400 K** — a bred crop line (breeding + mark)
- **round 3, 1400 K** — a metal blade (edge + smelting)
- **round 5, 1750 K** — spectacles, and then a lens ground to a number (mark + optics)
- **round 5, 1750 K** — a telescope on a mount (gearing + optics + rotation)
- **round 6, 1750 K** — a clock (gearing + regulation + spring)
- **round 6, 1750 K** — a dynamo under load (electricity + regulation + rotation)
- **round 6, 1750 K** — a machine that computes (electricity + mark + regulation)
- **round 6, 1750 K** — a signal read by machine (electricity + optics + regulation)
- **round 6, 1750 K** — a steam engine turning a shaft (gearing + rotation + steam)
- **round 6, 1750 K** — a governed engine (regulation + rotation + smelting + steam)
- **round 7, 1750 K** — a valve, and a signal amplified (electricity + regulation + vacuum)
- **round 9, 1750 K** — a transistor (semiconductor + switching)
- **round 9, 1750 K** — a stored-program computer (mark + regulation + switching)
- **round 10, 1750 K** — statistics run over a written corpus (inference + mark)
- **round 10, 1750 K** — a system that answers in sentences (inference + regulation + switching)

### What would move it further

The fixed point converges because the corpus enters as a logarithm, so
trying harder buys nothing. Only a changed term moves it:

- **as it stands** — +0.0 parts, per-capita exponent +0.072
- **a printing press** — +6.6 parts, per-capita exponent +0.072
- **power that is not land** — +0.0 parts, per-capita exponent +0.322
- **proofread twice more** — +0.0 parts, per-capita exponent +0.072
- **ten times the people** — +3.3 parts, per-capita exponent +0.072

## The rules, and what each one says

557 of 557 rules hold across 91 modules.

Every check below is a rule that produced its own sentence. An INVERTED
check is one that fails when the result looks too good -- it is there
to catch the system flattering itself.

### engine/ablate.py

All rules at once. When that fails, remove one at a time and see.

**ablation_restores_every_rule** — holds

every switch is put back: (8, 0, 6) before and after a full sweep. An
ablation that leaked would poison every result measured after it

**every_rule_is_attributable** — holds

target decay with all rules on: 8 right, 0 wrong, 6 refused.
shell-corrections: removing it changes nothing here -- not implicated,
however plausible; liquid-drop-domain: shifts right against refused
without changing how many are wrong; one-source-per-Q: removing it
changes nothing here -- not implicated, however plausible

**errors_that_cancel_are_visible** — holds

removing the helium-4 consistency alone changes nothing, which reads as
'it does not matter' and is wrong. It is inert only because the domain
rule shuts the alpha channel and leaves it no input. Lift both and the
outcome moves to (12, 0, 2) from (8, 0, 6) -- the +5.455 MeV bias
reappears and partly cancels the liquid drop's deficit on heavy alpha
steps. A rule behind a closed gate looks irrelevant however important
it is, which is why single ablation is not enough

**a_masked_rule_is_found_by_pairs** — holds

2 rules look inert on their own (one-source-per-Q, shell-corrections)
and 2 of them matter once a second rule is lifted too
(one-source-per-Q, shell-corrections). Single ablation would have
reported them as not implicated and the diagnosis would have been wrong

### engine/abundance.py

Solar abundances for every naturally occurring element, and the pattern
that catches a typo in them.

**coverage** — holds

83 elements with abundances; 84 occur naturally up to Z=92 by the
derived boundary; 1 without a value (['Pa']) -- protactinium, which has
no stable isotope and is not marked unstable by the periodic table, so
it falls in the same gap trace_by_decay() refuses to resolve

**oddo_harkins** — holds

even-Z beats its odd neighbours for 39 of 39 tested (100%); exceptions
none. A pattern the values must satisfy for nuclear reasons, so a
mistyped abundance breaks it

**declines_with_z** — holds

abundance falls 0.088 dex per proton across the table -- about 8x per
ten elements

**iron_peak** — holds

iron sits 1.28 dex above the next most abundant of Ti-Zn and 2.73 above
their mean -- a factor of 534, which is the binding-energy peak showing
up in a table of counts

**metallicity** — holds

X=0.7374 Y=0.2492 Z=0.0134, derived from the dex table and the repo's
atomic weights; accepted solar is about X=0.7381 Y=0.2485 Z=0.0134

**natural_boundary_derived** — holds

everything above Z=92 is man-made, derived: it is the smallest Z from
which every heavier element is unstable. 8 elements at or below it have
no stable isotope (['Ac', 'At', 'Fr', 'Pm', 'Po', 'Ra', 'Rn', 'Tc']).
Whether each is truly absent or present in traces is REFUSED -- see
trace_by_decay(); the table records 'no stable isotope', which uranium
also satisfies while being primordial

**channels_are_derived** — holds

alpha-chain 11, neutron-capture 57, primordial 3, secondary 12; the
split is the binding peak at Z=26, derived in engine/nucleo.py and not
written down here

**fusion_stops_at_the_peak** — holds

binding per nucleon tops out at 8.865 MeV at Z=26; nothing below
exceeds it and everything sampled above falls short, so 'fusion stops
here' is a measured property of the curve rather than a rule about iron

**the_trace_refusal_is_exercised** — holds

its docstring opens with REFUSED and it returns FINDINGS -- 1 of them,
e.g. Ra: no primordial isotope, but the decay chain from ['Th'] passes
through it and. The refusal is real but partial: position alone cannot
split trace from absent, and yet the decay chains settle some cases
outright. Nothing called this, so nobody had noticed the docstring
describes only half of what the function does

### engine/accident.py

Accidental discovery, and why a store makes you stop moving.

**all_discovery_here_is_already_accidental** — holds

engine/innovation.py makes 4.48 non-lethal variants per division of
which 1.1e-04 are useful, and NOTHING IN THAT SEEKS ANYTHING -- a
variant is a step omitted, duplicated or combined, produced whether or
not it helps. All discovery here was already accidental and it had not
been said. What a pressure does is decide which accidents are KEPT, not
which are made

**a_store_is_what_makes_you_stationary** — holds

alcohol, grain and dried meat are the same object: calories held
against later. A store cannot be carried, so leaving one costs 3.1 GJ
for a year's worth while moving gains 0.61 GJ. STATIONARY IS NOT A
CHOICE, IT IS THE STORE

**which_accident_does_not_matter** — holds

I expected the stores to be interchangeable and they are not. The
threshold is 73 days: fermented fruit holds 60 and does NOT settle, a
grain harvest holds 365 and does. So the arithmetic picks FARMING over
alcohol -- by 13 days, on a store duration that is a chosen number. The
discrimination is real and it is NOT robust: fermented fruit keeping
three months instead of two reverses it, and that is worth more than a
confident answer would have been

**the_threshold_is_about_a_month** — holds

moving stops paying at 73 days of stored food. Below that the journey
is worth more than the store; above it the store is worth more than the
journey. One number, and the only chosen input is what following the
food gains

**and_it_is_the_group_benefit_seen_twice** — holds

engine/group.py needed a benefit growing linearly in n and could not
find one: defence saturates and energy is per-head neutral. A STORE IS
ONE. It is defended by the group that holds it and a larger store is
worth more to defend, so settling and grouping are the same arithmetic
seen twice -- which is why they appear together in the record rather
than one causing the other

**only_a_store_that_survives_the_trip_spreads** — holds

settling alone discriminates by 13 days against a 73-day threshold,
which is thin. Diffusion is the second cut and it is not thin: bands
meet every 182 days, so a store that rots first never leaves the
valley. ['a grain harvest'] survive the trip, by a factor of 6.1x over
the rest. Fermented fruit settles a band and dies with it; grain
settles a band AND travels. Two independent rules, same answer, and the
weaker one is no longer carrying it alone

### engine/adapt.py

Adaptation is a search, and reproduction is how it is paid for.

**reproduction_is_the_search** — holds

engine/heredity.py gives 4.48 non-lethal variants per division without
a mutation rate, and engine/innovation.py gives the useful share,
1.1e-4. Multiply and one individual makes 4.90e-04 useful variants a
generation. REPRODUCTION IS THE SEARCH -- it is not a way of
continuing, it is how the answers are looked for

**population_size_is_the_only_lever** — holds

population size is how many variants are tried per generation and
nothing else changes it: 10 take 204; 100 take 20; 10,000 take 0
generations to find one answer. A lineage does not adapt faster by
trying harder, it adapts faster by being more numerous

**generation_time_is_the_lever_not_population** — holds

the first version of this expected fifty individuals to be too few and
they are not -- a microbe answering a yearly challenge needs 6. With a
division a day the search is simply fast. GENERATION TIME IS THE LEVER:
insect 168, wolf 6,119, and a human generation is 7300 days, so the
population needed for the same challenge is 7,300 times larger. A slow
breeder does not adapt by being patient; it adapts by being numerous,
or it does not adapt

**selection_costs_nothing_extra** — holds

variation without differential survival is drift, and the differential
is already there: 50% of daughters already cannot close, so the
differential exists before anything is selected FOR. Selection is not a
force applied to a population, it is what the failures already do

**nothing_new_was_introduced** — holds

this file introduces ['GENERATIONS', 'GENERATION_DAYS'] and both are
generation lengths. No selection coefficient, no mutation rate, no
fitness function -- the variation comes from engine/heredity.py, the
useful share from engine/innovation.py, and the differential from the
half of daughters that already cannot close

### engine/ancestry.py

LUCA to us, every step graded, and the gaps left visible.

**nothing_in_the_chain_is_forbidden** — holds

8 transitions from LUCA to us: none forbidden, 0 silent, 1 that CROSS
into recorded history, 1 resting on chosen numbers. The chain does not
stop where physics does -- it changes kind, which is what this system
has always done when a question stops being one sort of thing

**insulation_is_a_precondition_not_a_refinement** — holds

a 70 kg body makes 82 W and loses 99 through bare skin, and the ratio
never reaches one at ANY size -- it climbs from 0.33 at a gram to 0.83
at 70 kg and stops. So warm-bloodedness is not something a body can
simply do; insulation comes first or the heat leaves faster than it
arrives. Every endotherm has it

**a_brain_has_a_hard_ceiling** — holds

neural tissue runs about 10 times average, so a brain at 10% of body
mass would consume 100% of the entire budget. A human brain is 2% and
takes 20%. There is a wall a factor of five away, and it is the reason
a brain is expensive rather than merely large

**the_chain_says_allowed_never_happened** — holds

every row says ALLOWED or CROSSES, never HAPPENED. A transition needs a
mechanism producing the variation being selected, and engine/descent.py
showed there is none here -- seeded life stays microbial and predation
does not move it. The last step CROSSES rather than stopping: which
large-brained endotherm carried on is recorded, not derived, and a
chain reaching history changes kind the same way the cascade changes
layer when arithmetic becomes a date

### engine/artifact.py

The things themselves, so that the technology can be read.

**a_primitive_cannot_precede_what_it_is_made_of** — holds

21 primitives, each grounded in a rule that already existed for another
reason -- heat in the cooking bill, optics in the diffraction limit
that bounded an eye, steam in Carnot. A primitive that needs others
cannot come first, so the order is forced: depth 0 is ['cordage',
'edge', 'heat', 'lever'], and the deepest is inference at 8. Nobody
sequenced this; the prerequisites did

**the_count_of_designs_now_has_objects_under_it** — holds

engine/intricacy.py counted 2**s designs and never said what one WAS.
Giving them objects found that composition depth is NOT the constraint:
the prerequisite tree is 9 deep and a village affords 23.5 parts, so on
composition alone a literate village reaches a governed engine. It does
not, and the thing stopping it is TEMPERATURE. Every step past cordage
is a material you cannot have until you can reach the heat that makes
it, and the bootstrap takes 10 rounds from 1100 K to 1750 K. The count
now has objects under it and the objects have a metallurgy

**every_name_is_checked_against_the_derivation** — holds

21 names, and they derive NOTHING -- they are vocabulary so the output
can be read. Every one is checked against the derivation and a name
whose parts never become reachable is an error, not a prediction. They
arrive where the bootstrap puts them: r1 a bow; r1 a hafted axe; r2 a
cooking pot; r2 a potter's wheel; r2 a sealed tablet, an account ...
and a system that answers in sentences at r10

**our_own_age_arrives_last_and_not_by_being_listed** — holds

nothing here is late because it was listed last. Copper is round 3 and
steel 5, and the gap is a LOOP: bellows need a metal tuyere and the
tuyere needs the smelting the bellows were for, so the cheap gains buy
copper at 1400 K and copper buys the gains that reach 1750 K. The same
shape repeats in tolerance: the first gears were hand-filed at a tenth
and were good enough to cut better ones, and point-contact transistors
were millimetre-scale before lithography existed. Setting either rung
too high DEADLOCKED the bootstrap on the first attempt, which is the
correct failure -- a ladder needs a rung you can reach by hand. 6
things are in hand by round 2 (a bow); 4 wait for round 9 or later,
ending at a system that answers in sentences

**the_gate_changes_and_heat_stops_mattering** — holds

temperature stops moving at round 5 (1750 K) and the bootstrap runs to
10. Everything after that is reachable at the same heat and was not
available for two centuries, because the scarce thing CHANGED: not how
hot you can get but how accurately you can place matter. Tolerance goes
1e-03 -> 1e-09 over those rounds. A model with one gate would have put
a transistor next to a steam engine. The gate is not a constant of the
system, it is whichever scalar is currently short, and noticing that it
had moved is the only reason the later rounds exist

**INVERTED_the_future_gets_numbers_and_no_nouns** — holds

asked to run 200 years past now, the model answers with two numbers and
no nouns. Parts: 29.4 -> 49.4, and the whole of that gain is a corpus
copied at 1e6 a scribe-year rather than 250 -- a millionfold corpus is
20 more parts, because the corpus is a logarithm and that never stops
being true. Per-capita exponent: 0.072 -> 0.352 as the land share goes
to 0.02. What it will NOT do is name the artifacts. Every primitive
here is a material or an effect somebody has made and every name in
KNOWN_AS is a thing that exists; a name for a primitive nobody has made
would be a word with no rule under it, and this check fails if one
appears. The forecast is 6.6 parts and a share, and anyone wanting more
than that is asking for fiction

### engine/atoms.py

Nothing is created and nothing is destroyed, including when it dies.

**death_returns_every_atom** — holds

built 400 kg of body from a 1000 kg pool, killed it, and the pool is
1000 kg again to nine decimals. Death is a deposit. Every module before
this one let a thing die and did not say where it went

**a_world_cannot_grow_what_it_lacks** — holds

strip the phosphorus to a ten-thousandth and 500 kg cannot be built,
and the refusal NAMES phosphorus. Not 'growth failed' -- which atom ran
out

**the_limiting_element_is_derived** — holds

given that reservoir, P runs out first and caps biomass at 116 kg. Life
is not capped by sunlight here. It is capped by the scarcest atom, and
which atom that is was derived from the recipe, not chosen

**wood_is_not_flesh** — holds

a kilo of wood holds 1.26 times the carbon of a kilo of flesh and NO
nitrogen at all, which is why a trunk is cheap to build and a leaf is
not. Cellulose is not Redfield, and no function here can reach for the
wrong one by accident -- it is an argument, not a default buried in the
body

**burial_is_the_only_leak_and_it_is_named** — holds

bury one percent and TWO books disagree, which is the point. Total
matter is still 1000.000000 kg -- nothing was destroyed and the check
would scream if it had been. Circulating matter is 996.00 kg, down 4.0.
A leak is not a cycle. Coal, oil and chalk are that one percent, and so
is the oxygen it left behind

**a_tree_is_made_of_air** — holds

the 11.4 m tree engine/biome.py says the light race stops at weighs 26
kg dry and holds 12 kg of carbon -- 969 moles of CO2 pulled out of the
air. The height was derived from watts; the matter to build it is a
separate bill and it is now itemised

**every_life_rule_accounts_for_matter** — holds

10 living modules checked: 3 route matter through this file and 7 are
exempt WITH A REASON WRITTEN DOWN, not by omission. A new life module
that grows or kills anything fails this until it says what its bodies
are made of

**eating_moves_atoms_and_makes_none** — holds

a 100 kg prey yields 80 kg of predator and 20 kg to the ground, and
those add to 100. The 80% that is not assimilated does not evaporate --
it is returned free, which is what feeds the decomposers that no module
has yet

**standing_crop_is_exercised** — holds

a world recycling every 10 years holds 116 kg of biomass at once,
capped by P. This was written the day the atom ledger went in and
nothing ever called it

### engine/biomatter.py

The ladder above chemistry: nucleotide, codon, gene, genome, cell,
organism. Every rung gated by when its constituents can exist.

**nucleotide_epoch** — holds

dAMP = C10H14N5O6P; its elements appear {'C': 'stellar_c', 'H': 'bbn',
'N': 'stellar_c', 'O': 'stellar_c', 'P': 'supernova'}, and the latest
is ['P'] at supernova

**two_routes_to_life** — holds

the element list and the nucleotide formulas both give supernova -- two
routes, written apart, agreeing

**code_shape** — holds

4 bases and 20 amino acids counted out of the table still force a codon
length of 3, and 4**3 = 64 is exactly the number of entries; 1 stop
meaning across 3 codons

**gene_inverse** — holds

300 codons = 900 bases = 1800 bits at 2 per base; codons recover as 300

**genome_two_ways** — holds

uniform: both routes give 2000 bits. Skewed 80/20: 2000 naive against
1722 measured, a 278-bit gap that IS the composition bias

**cell_window** — holds

4,600,000 bp: r between 105.5 nm and 1732.1 um, a factor of 16,423. The
floor is 4.2 orders below the ceiling, so diffusion decides a cell's
size and the genome does not

**cell_refuses** — holds

3 impossible cells refused by ['containment', 'diffusion', 'geometry'],
and a 1 um cell with a bacterial genome accepted

**organism_bounds** — holds

anything relying on diffusion stays under 1.73 mm; a land skeleton
crushes itself past 173 m; and none of it before supernova, because DNA
needs phosphorus

**epoch_gating** — holds

DNA is gated at supernova (index 8); all four nucleotides are at or
before it, and the 8 earlier epochs cannot hold any of this ladder

**translation** — holds

all 64 codons translated singly rebuild the table; ATGTGTGGATAA -> MCG,
stop reached True

**protein_mass_two_ways** — holds

every residue weighed alone, and all 20 as one chain: 2395.742 g/mol
for C107H159N29O30S2, by two routes agreeing

**translation_loses_information** — holds

MCG has 8 possible genes; the degeneracies partition all 64 codons
exactly, so the map is onto and not one-to-one and the gene is not
recoverable

**protein_refuses** — holds

4 malformed inputs refused, each with the reason that makes it
malformed

**codon_and_epoch_are_exercised** — holds

codon_space returns the PAIR (3, 64), not the 64 its name suggests --
the triplet is derived from 4**2 < 21 <= 4**3, and a chain holding M or
C waits for supernovae: supernova [DERIVED, EXTERNAL] this chain
contains ['C', 'H', 'N', 'O'. Neither had a caller

### engine/biome.py

Plants, the things that eat them, and a test for intelligence.

**light_is_winner_take_all** — holds

at leaf area index 4 only 13.5% of light reaches below, at 8 only 1.8%.
A rival eating your food takes a SHARE; a rival growing above you takes
it ALL, and keeps taking it every day it stands there. That is the
first winner-take-all pressure here, and the only one whose reward
grows with being larger

**height_is_worthless_without_a_rival** — holds

INVERTED, kept. This rule first said height has an optimum and it is
tall, and it passed at 92 m -- because the crown was set to a tenth of
the height, so tallness paid for itself with nobody to outgrow. It
assumed the conclusion. Cut that tie and a plant alone stays at the
floor (0.05 m): sunlight does not get brighter further up. Height is
worth nothing on its own and 11 m against a rival. The pressure is the
neighbour, not the sun

**light_ratchets_size_upward** — holds

0.05 m -> 11 m, a 229-fold climb that stops where the trunk costs as
much as the light being fought over, well under the 204 m cavitation
ceiling. Every other pressure here pushed size DOWN --
engine/descent.py collapsed a lineage to 0.1 um and predation could not
stop it at 99% mortality. Light is the first that pushes UP, because a
rival eating your food takes a share and a rival standing over you
takes all of it

**the_food_chain_has_a_derivable_length** — holds

236 W/m2 reaches the ground, plants fix 2.36, and each level passes
about 10% up -- so the chain runs 4 levels before there is nothing left
to be. Food chains are short because the arithmetic is exponential, not
because anyone decided

**each_trophic_level_is_smaller_in_total** — holds

producers hold 2.36 W/m2 and top predators 2.36e-03, a 1000-fold drop
over three steps, so the same 10 kg body needs 8.07e-06 km2 as a grazer
and 0.00807 as a hunter. Predators are rare because the arithmetic
makes them rare, not because anything said so

**a_predator_needs_ground_not_a_square_metre** — holds

MISSING_RULE. A 40 kg carnivore needs 0.0023 km2 to cover 54 W, and a
175 kg one at the top 0.069 km2. Real wolf packs hold 100-1000 km2 --
43808 times more. The derivation is a floor and reality sits far above
it, which is the right direction but not an explanation. What is absent
is that A TROPHIC LEVEL IS A GUILD, NOT A SPECIES: the tenth that
passes upward is split across every carnivore, most of it invertebrate,
and one wolf takes a sliver. No rule here partitions a level among its
occupants, so the number is not being fixed by hand

**a_brain_must_pay_for_itself** — holds

a brain at 2% of mass costs 20% of the budget, so it must raise intake
by MORE than a fifth or it is dead weight. A 15% gain does not cover
it; a 50% gain does. That is the same test circulation passed at 0.01%
-- and a brain is two thousand times more expensive than a heart

**intelligence_is_not_claimed** — holds

nothing here says a brain appeared, and nothing says tools were made.
The question asked is whether thinking EARNS its keep, which has a
number in it, and the answer is that it only does above a large intake
gain. Whether any lineage found one is not something these rules can
reach -- it needs the mechanism that generates variation, which
engine/descent.py showed is absent

**the_shading_and_prey_rules_are_exercised** — holds

under a 5 m canopy, clearing it beats staying short (under a 5.0 m
canopy a short plant nets 0.314 W; clearing it net), and a 40 kg
predator stands on 17 prey of 20 kg. Both rules were written and
neither had a caller

### engine/biosphere.py

Cells introduced to Earth, and the planet watched while they work.

**oxygen_is_sink_limited_not_production_limited** — holds

a modern biosphere makes Earth's whole oxygen atmosphere in 4,149
years, so production is not the constraint. The reduced crust can
swallow 117 atmospheres first, and does -- which is why a planet can
photosynthesise for ages and still read as anoxic

**the_sink_delays_oxygen** — holds

free oxygen first appears at 0.0075 Gyr, after 1 of 14 sampled steps
spent filling the crust. The curve is a threshold, not a ramp: nothing,
then everything

**oxygen_shortens_methanes_life** — holds

methane lasts 10,000 years in an anoxic atmosphere and 10 once oxygen
is free -- 1,000 times shorter. A biosphere that makes oxygen therefore
DESTROYS a greenhouse gas, and cooling a planet is not something life
was asked to do

**the_delay_is_wrong_and_says_so** — holds

the model puts first oxygen at 0.0075 Gyr and Earth took about 1.1 --
wrong by 146 times, and left wrong. The SHAPE is right: sink first,
then accumulation. The inputs are not. Early productivity was a small
fraction of modern and the sink is not only iron but the whole reduced
crust plus whatever volcanism keeps adding. Neither is derived here, so
neither is tuned

**cells_are_the_size_the_lab_derived** — holds

the cells introduced here are 1.58 to 47.5 microns, which is the window
engine/earthlab.py derives from autocatalytic closure below and oxygen
diffusion above. They were not sized to fit this experiment

**life_cools_its_own_planet** — holds

an anoxic Earth at 1000 ppm methane sits at 315.6 K; once oxygen cuts
methane to 1.8 ppm it sits at 313.7 -- 1.9 K colder. Nothing was added
to connect them: methane was already a band in engine/radiative.py and
the climate was already downstream of the bands. A biosphere that makes
oxygen COOLS ITS OWN PLANET, which is not something it was asked to do,
and Earth's first glaciation follows its first oxygen

**oxygen_alone_cannot_thicken_a_body** — holds

at present oxygen a body can be 54.8 microns thick without circulation,
and at FIVE times present only 122.5 -- 2.24x for 5x the air, because
diffusion goes as the square root. Thickness is not bought from the
atmosphere. It is bought with a pump

**prime_earth_reaches_animals_but_not_by_air** — holds

Earth run at its best -- full productivity, a tenth the reduced sink --
reaches 100% of present oxygen. That opens aerobic metabolism and a
thin body, and it does NOT open a thick one. Adding circulation opens
it immediately at the same oxygen. So the step to a large animal is not
an atmosphere, it is an organ, and no amount of prime conditions
substitutes

**circulation_is_cheap_and_that_is_derivable** — holds

Poiseuille against Kleiber: pumping costs 0.60% at 1e-06 kg, 0.11% at
0.001 kg, 0.02% at 1 kg, 0.01% at 70 kg, 0.00% at 10000 kg. Affordable
everywhere and cheaper as bodies grow, because demand rises as
mass^0.75 and resistance falls as r^-4. Circulation is not a barrier
that had to be crossed -- it is the cheap answer to a problem that
becomes unavoidable at 55 microns

**but_the_organ_itself_is_not_derived** — holds

that a pump PAYS FOR ITSELF does not say how a lineage builds one, and
there is no rule here for that. The derivable claim is narrower than
'circulation is derivable': nothing forbids it, and the economics
favour it at exactly the size diffusion fails. The organ is still an
absence, and a smaller one than it looked

**the_uv_shield_is_made_of_the_thing_it_protects** — holds

ozone is made from oxygen, so a planet cannot shield its land before
its air is breathable -- the same molecule does both. It saturates
quickly: 1.9e-03 of the damaging band reaches the ground at 0.5% of
present oxygen and 2.4e-09 at 5%. The shield is not the hard part of
coming ashore

**every_remaining_gate_is_architecture** — holds

on prime Earth the environmental gates open (uv shield, gas exchange)
and the shut ones are water retention, support -- a skin and a
skeleton. Adding them opens everything at the same oxygen. THIS IS THE
THIRD TIME: a thick body needed a pump, land needs a cuticle and bones,
and not one of them is something a planet supplies. Every barrier left
in this simulation is architecture

### engine/bridge.py

Modules answer together by TYPE, which is how bind.py already works.

**crosses_modules** — holds

a 25 solar-mass star -> black_hole via core_mass -> classify_remnant;
chemistry -> 9,502,720 bytes via subject_experts -> expert_bytes across
2 modules

**no_path_refuses** — holds

asked for an impossible chain: refused -- no chain from subject to
seconds_after_bang across 16 capabi...

**composition_beats_parts** — holds

4 answers need two or more modules chained; none of them is written
down anywhere, they exist because the types line up

### engine/capital.py

You cannot specialize in something you cannot afford the tools for.

**a_specialty_is_a_toolkit_and_a_toolkit_is_bought** — holds

a 23.5-part kit is 1177 labour-days at 50 a part, so keeping one
specialist for a year costs 365 food-days of eating plus 118 of kit =
483. A village of 912 with 53% sparable supports 368 of them, not the
487 the food alone would allow. 24% of the possible specialists are
lost to the price of their tools, and no rule above this one saw that
cost

**intricacy_makes_its_own_tools_dearer** — holds

intricacy is a headwind on itself: more parts is a dearer kit, 23.5
parts at 1177 days against 29.4 parts at... 620. It went DOWN, because
Wright's law on a 40x market cuts unit cost to 0.42 and that beats the
1.25x rise in part count. So the network does not merely allow more
specialties, it makes each one cheaper to enter -- the two gains are
separate and they happen to point the same way. In a village that did
NOT trade, rising intricacy would price people out of their own crafts

**concentration_has_a_right_answer_and_it_is_S_over_K** — holds

one person works one specialty however rich they are. Surplus held in
fewer hands than S/K sits idle; split thinner than K and no share buys
a kit. So the right number of holders is 368 of 912 -- 40% -- and it is
arithmetic, not a politics. engine/power.py's walled holders take 3.5x
an equal share, which puts the working surplus in about 29% of hands:
below the optimum, so kit goes unbought that the place could afford.
Concentration is not only unfair here, it is IDLE CAPITAL, and that is
a cost the holders pay too

**INVERTED_the_average_gain_is_nobodys_gain** — holds

engine/intricacy.py reports a gain per head and that figure is a MEAN.
Income is 1/k for a craft held by k people, and k is not the same for
every craft, so the distribution is skewed before anyone is greedy: at
mean depth 3 the mean is 0.333 and the median 0.250, 1.33x apart. The
rare craft pays 4.0x the median on scarcity alone, and a walled holder
multiplies it again to 14.0x. So 'everyone is 1.3x better off' is a
statement no individual satisfies -- some are near 14x, most are at or
under the median, and the mean sits above the median by construction.
Any per-head number from this chain is the first moment of a skewed
distribution and should be quoted with the other two

### engine/census.py

Many worlds generated, and a search through them for HABITABILITY.

**many_worlds_run_and_differ** — holds

24 systems from 18 distinct stellar masses, 115 rocky or icy worlds
between them, each run from a four-number seed through condensation,
atmosphere, thermostat and a moving habitable band

**the_census_says_why_not** — holds

47 of 115 worlds pass all three conditions. Deconstruct them: the
result is what they share

**habitable_worlds_share_something_real** — holds

47 of 115 worlds are habitable (41%) and they share NOTHING: stellar
mass 0.54-1.54 against a population of 0.54-1.54, the whole range. That
withdraws 3.1.44, which reported every habitable world orbiting a
0.51-0.54 solar mass star. It did -- when carbon could not reach an
inner planet, and only dim stars with close-in ice lines delivered any.
The correlation was the shape of a missing rule, not a fact about small
stars, and extending the comet source to the CO line at 124 AU
dissolved it

### engine/civ.py

Play god once, then look at the bill.

**language_is_almost_nothing_as_a_pipe** — holds

vision delivers 1e7 bit/s and speech 39 -- 256,410 times narrower.
Everything anyone says to you in seventy years is 5.74e+10 bits,
0.0122% of what a brain holds. If language carried civilisation by
VOLUME it would be the worst tool ever adopted

**what_it_carries_is_the_selection** — holds

a brain saturates at 1.49 years and spends the rest discarding, so what
it owns that is expensive is its SELECTION, not its contents. Speech is
the only channel that moves a selection between heads without the
second head paying to derive it. 0.0122% is enough because it is the
0.0122% somebody already chose

**connection_did_not_have_to_be_given** — holds

a child costs 16.4 W of provisioning plus 34 W of its own body, 51 W of
a forager's 97. one adult keeps 46 W spare against 48 W of slack needed
to survive a bad season. CONNECTION DID NOT HAVE TO BE GIVEN -- it was
already implied by a module written four versions ago and nobody had
looked. It is not a preference on top of the physics, it is the physics

**the_group_size_is_derived_not_chosen** — holds

2 adults is the smallest that carries one child with slack for a bad
season: 46 W spare alone against 143 W at 2. Nobody picked a band size
-- it is where the surplus crosses the margin

**what_was_given_is_marked_as_given** — holds

two things were handed over and both are named: a channel between
brains; adults pool what they bring in. Everything else in this file is
derived or refused, and the point of playing god once is that the bill
afterwards is legible -- connection came back DERIVED, which means the
gift was not needed for it

**some_wants_derive_and_some_do_not** — holds

of 5 appetites, 3 derive from rules already here -- connection, food,
shelter -- one is partly derived, and 1 does not: status, because
nothing prices rank. No rule makes one adult's share depend on
another's regard, so if status is real it is MISSING and not derived,
and that is a different sentence from 'people want status'

### engine/closure.py

A self-maintaining set, searched for rather than priced.

**the_network_is_built_not_estimated** — holds

254 molecules up to length 7 over a 2-letter alphabet, 1284 ligations
that fit, 6 of them supplied as food. The set is BUILT.
engine/earthlab.py's gate passes by computing whether closure is
likely, which is a statement about a probability and not about a set

**a_low_enough_p_closes_nothing** — holds

at p = 1e-6 nothing closes: 0 reactions survive the pruning out of
582544. The search can return nothing, which is what makes returning
something worth anything

**a_high_enough_p_closes_something** — holds

at p = 1e-2 a set closes and holds 431 reactions over 221 molecules,
every one of them catalysed from inside and built from food. Nothing
was told that a set exists -- the pruning ran to fixpoint and this is
what did not fall out

**the_turn_on_is_sharp** — holds

closure turns on between p = 2.27e-03 and 6.69e-06, a factor of 0. It
is a threshold and not a slope, which is what an autocatalytic set is
supposed to be -- below it every reaction waits on a catalyst nobody
makes

**the_measured_p_is_compared_not_assumed** — holds

engine/earthlab.py carries CATALYSIS_P = 1.0e-08 as the chance one
molecule catalyses one reaction. This network needs 6.7e-06 to close,
so the measured figure falls 669x short. That comparison is the whole
point of building the set rather than estimating it -- and the number
it is compared against is a CHOSEN one, registered as such, so the
verdict is only as good as it is

**the_extrapolation_is_not_trusted** — holds

INVERTED, kept. This asserted that the extrapolation was NOT to be
trusted, and it was right: 17 orders beyond 1.2 orders of data, on a
fit against network size. Widening the alphabet and bisecting properly
cut it to 3 orders over 3.1 of data, and then the rule p*M = 0.481
removed the fit altogether -- 13 bases with nothing extrapolated at
all. The check fails now BY HAVING BEEN FIXED, which is the only way a
distrust claim should ever fail

**more_monomers_close_at_lower_p** — holds

at the closest comparable sizes -- 1,284 and 912 reactions -- a
two-letter chemistry needs p = 2.3e-03 to close and a four-letter one
1.1e-04, a factor of 21. SIZE IS NOT THE ONLY VARIABLE -- more distinct
monomers means more distinct potential catalysts for the same reaction
count, and sweeping polymer length alone misses it entirely

**the_first_extrapolation_was_wrong_by_eleven_orders** — holds

the first version of this swept one alphabet, fitted p ~ R^-0.30 and
extrapolated 17 orders to 4e20 reactions. Adding a second alphabet
gives p ~ R^-0.70 and 6.3e+09 reactions -- ELEVEN ORDERS DIFFERENT,
with the extrapolation cut to 4. The first answer was not uncertain, it
was WRONG, and taking more data is what showed that rather than
inspecting the fit. At four nucleotides 6.3e+09 reactions is polymers
up to about 15 bases, and engine/earthlab.py independently derived 20
bases as the assembly piece size. Two routes, same neighbourhood, still
4 orders of extrapolation apart from proof

**catalysations_per_molecule_is_linear_in_length** — holds

f = p*R -- the reactions one molecule catalyses at threshold -- is
LINEAR IN L. Across seven bisected networks over two alphabets, c = f/L
runs 0.31 to 0.49, mean 0.395, while R itself changes 190-fold. Fitting
p against network size extrapolates something that moves; c does not
move, and it was measured over the range where the answer lands

**the_gap_closes_at_thirteen_bases** — holds

at four nucleotides a network of polymers up to 13 BASES --
1,043,915,664 ligations -- closes an autocatalytic set at the measured
catalysis probability of 1e-08, with threshold 4.9e-09.
engine/earthlab.py independently derived 20 bases as the modular
assembly piece, so the network that supports assembly is MORE than
enough to close a set. The five-order gap does not close by making the
catalysis better; it closes because R grows exponentially in L while
the catalysis each molecule must supply grows only linearly

**the_slope_has_a_rule_under_it** — holds

c = 0.395 was a MEASURED SLOPE with nothing under it. The quantity that
governs closure is p*M, the expected catalysts per reaction, flat at
0.481 (spread 1.51x) over the same seven networks. A SET CLOSES WHEN
ABOUT HALF THE REACTIONS HAVE A CATALYST. The linearity of f in L is
then a consequence -- f = p*R = (p*M)(R/M) and R/M is 12.0 at AB L=14,
close to L -- rather than something measured and left standing. The
invariant holds only above 2,000 molecules -- over ALL eleven networks
it varies 15.9x, and below the cut ABCD L=4 sits at 0.037. The rule
refuses there rather than returning a number

**the_space_is_rendered_not_rerun** — holds

11 networks are RENDERED -- measured once, written down, looked up
after. Each row cost between 0.3 s and 580 s and not one of them will
change, so re-bisecting them was the waste this file kept committing.
From the fitted slope the answer is 13 bases; from the rule p*M = 0.481
it is 13 bases over 89,478,484 molecules. Two routes, and the second
needs no fit at all

### engine/clouds.py

Condensed particles are grey, and that is the whole point of them.

**a_cloud_has_no_window** — holds

CO2's four bands together cover 17% of what a 737 K surface radiates,
so gas leaves 83% open however much is added. A cloud covers all of it:
a droplet microns across is large against every infrared wavelength and
removes light geometrically. That is a difference in KIND, not in
degree, and it is why no gas rule could close this

**thinner_particles_block_more** — holds

the same mass gives tau 40.76 as 1 micron droplets and 4.08 at 10
microns -- ten times thinner, because opacity goes as surface area per
unit mass and that goes as 1/r. A cloud's strength is about how finely
divided it is

**earth_water_cloud_is_the_right_order** — holds

kinetic theory gives air a viscosity of 1.21e-05 Pa s against a
measured 1.81e-05, Stokes gives a 20 micron droplet its fall speed, and
the standing balance gives tau=69 where total condensate gave 11,272.
Real Earth clouds are 5 to 20, so the factor of a thousand was
precipitation and what is left is about three -- which is the scale
height 8.4 km standing in for a cloud layer of 1 to 3. Two inputs
remain and both are named: droplet radius, set by nucleus counts, and
cloud depth, set by the lifting condensation level

**venus_condensate_is_refused_by_name** — holds

Venus' deck is sulfuric acid and it is REFUSED: this repository has
Clausius-Clapeyron for water and carbon dioxide, and H2SO4 needs its
own triple point and latent heat. Those are laboratory measurements of
a substance, the same kind of input as a band strength, and the
mechanism is built and waiting for them. Inventing a curve to close
Venus would be the patch this whole exercise exists to avoid

**the_albedo_already_counts_the_cooling** — holds

Venus' albedo of 0.77 is its cloud deck -- a bare rock would be near
0.10 -- and it removes 92 K that the model counts in full. The same
clouds' greenhouse is counted at zero. Half a mechanism is worse than
none, because the error has a sign and nothing declares it

### engine/code.py

A sequence that is read, and why the first code had to be small.

**a_code_is_the_rule_that_closes_reading** — holds

engine/template.py gave heredity of SEQUENCE and could not give
heredity of FUNCTION, because a strand codes only for its own
complement. A CODE is the missing rule: a mapping from subsequences to
catalysts that is neither the identity nor the complement. It is not
free -- each meaning needs an adaptor, and every adaptor is a sequence
that must itself be maintained, so the code competes for genome with
the thing it codes for

**the_modern_code_does_not_fit** — holds

the code we have needs 20 adaptors of 76 bases, 1,520 in total, against
the 200 a lineage holds at 259 K. IT DOES NOT FIT, by 7.6x. Nothing was
tuned to get that -- the genome limit came from a base-pair
discrimination energy three modules ago and the tRNA length is recorded

**so_the_first_code_was_small** — holds

what does fit is 5 meanings at 2 base(s) per codon, leaving 100 bases
for the catalysts themselves. THE FIRST CODE WAS SMALL, and that is a
derived prediction rather than an assumption -- it falls out of an
adaptor costing sequence and a genome capped by fidelity, both already
on the table

**code_size_is_bounded_by_temperature** — holds

a code costs adaptors, adaptors cost genome, and genome is capped by
copying fidelity -- so CODE SIZE IS BOUNDED BY TEMPERATURE. 273 K holds
152 bases and 3 meanings; 259 K holds 200 bases and 5 meanings. The
same seven-kelvin window that opened fidelity, crowding and persistence
sets how much a sequence can say

**the_conclusion_survives_the_dials** — holds

CODE_SHARE is a dial and the conclusion does not turn on it: at 30%,
50%, 70% and 90% of the genome the affordable code is [3, 5, 7, 9]
meanings, and none of them reaches 20. The adaptor length is an
order-of-magnitude guess and would have to be wrong by 2x to change the
answer

**what_is_still_missing** — holds

the rule says a code CAN be afforded and how wide. It does not say a
code appears, and it does not say which mapping -- any assignment of
subsequences to catalysts works equally well here, which is exactly why
the one we have looks arbitrary. What is now missing is narrower than
'nothing reads a sequence': it is that nothing here selects one mapping
over another once both are affordable

### engine/cold.py

The fidelity gate opens by getting colder, and so does crowding.

**the_ribozyme_is_at_its_thermodynamic_limit** — holds

one error in 100 at 298 K implies a discrimination of 2.73 kcal/mol,
which is an ORDINARY base-pair free-energy gap. So the best known
ribozyme is not a poor copier -- it is at the thermodynamic limit for
its temperature, and no better catalyst exists at 298 K because that
gap is the whole of what a catalyst has to work with

**fidelity_is_a_temperature_not_a_catalyst** — holds

dG is fixed by chemistry, so halving the error means raising dG/kT and
the only free term is T: 259.0 K, -14.1 C. engine/earthlab.py reports
the fidelity gate short by exactly 2x, and the thing that closes it is
NOT a better catalyst. It is a colder one

**the_brine_is_still_liquid_there** — holds

259.0 K against the NaCl eutectic at 251.9 K -- so there is still brine
to react in. Push further and it stops: one error in 500 wants 221 K,
which is below every eutectic here, and a gate that opens in solid ice
has not opened

**getting_cold_concentrates_what_is_left** — holds

getting cold is not free. Holding water liquid at 259.0 K needs 7.60
mol/kg of solute against seawater's 1.2, so the brine is 6.3x
concentrated. The water that stays liquid is the water with everything
dissolved in it

**cold_slows_breaking_more_than_building** — holds

breaking a phosphodiester bond has a 100 kJ/mol barrier and building
one about 60, so cooling slows BREAKING more. At 259 K building beats
breaking 11.4x better than at 298 and a bond lasts 9,574 years against
22. a 200-base strand loses 0.0145 bonds a year at 259 K, and building
beats breaking 11.4x better than at 298 K. Had the two barriers been
equal this would be 1.00 at every temperature -- I wrote the sign
backwards first and it said cold made things worse

**one_move_opens_three_gates** — holds

ONE MOVE OPENS THREE GATES. At 259.0 K the error rate is 0.0050, the
maintainable genome goes 100 -> 200 bases, and the same freezing-point
depression that gets there concentrates the brine 6.3x, which is the
crowding gate's own requirement arriving as a side effect -- and a bond
lasts 9,549 years instead of 22, because breaking has the higher
barrier. Fidelity, crowding and persistence, and none of the three was
aimed at the others

**nothing_here_was_handed_over** — holds

nothing in this file was handed over. The discrimination energy is read
off a measured error rate, the temperature follows from it, the
eutectic and the cryoscopic constant are measured properties of water,
and the concentration is freezing-point depression. No rule here says
life is likely, only what temperature the fidelity gate opens at and
what else that costs

### engine/comprehension.py

What an organism has to understand, which is not the code.

**an_organism_needs_replies_not_the_code** — holds

this repository can read its own rules -- engine/spine.py walks the
graph, engine/vocabulary.py indexes every rule by its words,
engine/frozen.py knows why a code is locked. None of that is available
to a bacterium and a bacterium is fine. a bacterium needs a reply to
each of the 6 constraints that bind on it. The rules of the environment
are already in the environment; what has to be carried is the reply,
not the rule

**comprehension_is_a_count_of_what_binds** — holds

comprehension is not a scale of insight, it is a COUNT: bacterium 6,
bee 8, mouse 10, human 13. Each constraint that binds needs its own
reply, and since a reply right for one combination can be wrong for
another, the situations to tell apart go as the power set -- 8,192 for
a human against 64 for a bacterium

**what_does_not_bind_needs_nothing** — holds

a bacterium does not respond to predation, heat rejection or
provisioning because NONE OF THOSE BIND AT A MICRON. It is not ignorant
of them -- they are not there. engine/biome.py prices predation for
bodies that can be caught and engine/shelter.py prices heat loss for
bodies that make 82 W, and a bacterium is neither

**a_bigger_brain_has_more_binding_on_it** — holds

a human carries ['provisioning', 'allocation', 'a shared corpus'] and
nothing simpler does, because engine/ontogeny.py, engine/rank.py and
engine/school.py each derived a constraint that only appears at that
scale -- eighteen years of provisioning, an allocation rule above the
carrying number, a corpus too large for one head. A BIGGER BRAIN
UNDERSTANDS MORE because MORE BINDS ON IT, not because understanding is
a virtue

**storage_is_not_what_scales** — holds

a human holds 4.7e+14 bits and 13 constraints, so storage is plainly
not what scales -- engine/learning.py already showed that store fills
in 1.49 years through one nerve. What scales is the number of distinct
SITUATIONS that must be told apart and answered differently, which is
8,192 combinations of thirteen constraints

**every_constraint_names_the_module_that_derived_it** — holds

every one of the 14 constraints names the module that derived it,
across 10: biome, biosphere, cold, earthlab, life, ontogeny, rank,
school, shelter, tools. This file adds no constraint of its own -- it
is a census of what the repository already refuses to let an organism
ignore

### engine/constants.py

One definition each. Nothing in this repo may define a constant twice.

**every_constant_has_provenance** — holds

13 constants, 7 exact by definition and 6 measured, and every one says
which -- an exact constant has no error to propagate and a measured one
does, so the distinction has to survive into the answer

**no_constant_is_defined_twice** — holds

19 owned names including 6 historical aliases, and not one is redefined
in any other engine module. Four quantities used to carry two or three
definitions each -- all of them agreeing, which is what made it
dangerous

**exact_constants_reproduce_derived_ones** — holds

Stefan-Boltzmann and the gas constant both fall out of the exact four:
sigma=5.6703744e-08, R=8.314462618. Neither is stored here, because a
number that can be computed has no business having a second home to go
stale in

### engine/cosmoschunks.py

A universe in chunks, so it can hold as much matter as it needs to.

**density_is_counted** — holds

8 chunks, 1,831 solar masses, 1.748e+60 atoms -- 2.185e+59 per chunk,
counted from mass and composition and stored nowhere

**mass_conserved_across_chunks** — holds

8 chunks sum to 1,830.64 solar masses exactly, and every one conserves
mass internally

**chunk_proves_itself** — holds

chunk 3 regenerated from its key alone and matches link
4de267f962cc5947...; a key from another universe is refused rather than
matched to the same index

**consistent_across_universes** — holds

same chunk count; laws hold in every chunk; heads differ; comparable
scale; same elements present

**scales_without_running** — holds

one chunk holds 1.949e+59 atoms, so a million hold 1.949e+65 across
2.041e+08 solar masses -- reported without running them, because the
rule is the same in each

### engine/craft.py

Why a band is slow, and what the slowness buys.

**a_band_walks_at_its_shortest_legs** — holds

walking is an inverted pendulum, so speed goes as sqrt(g*L) and pace is
leg length and nothing else. Adult 1.49 m/s (5.3 km/h), four-year-old
1.05 m/s (3.8 km/h). The band moves at the child, so the ratio is
sqrt(0.45/0.90) = 0.707 -- a square root, not a preference, and the
18-year provisioning span of engine/comprehension is why a child is
there at all

**slowness_is_what_supplies_the_problems** — holds

hazards are charged by the day and forage is collected by the
kilometre, so a band at 0.707 of adult pace meets 1.41x the trouble per
km -- slowness does not avoid problems, it concentrates them. And it
brings 28 heads to them instead of one, so kept innovations per km run
39x a lone adult. The per-head solve rate cancels: (1-(1-q)^m)/q -> m.
Slowness is not the price of company, it is the input to the only thing
here that accumulates

**specialization_is_bounded_by_the_telephone** — holds

s specialties means BAND/s holders each, and those holders were the
votes correcting the telephone. Breadth multiplies by s, fidelity
divides by it. The trade bottoms out at 13 holders and 2 specialties,
carrying 9332a -- against 8688a if all 28 hold one corpus, and 280a if
all 28 specialize alone, where every skill dies with the one who knows
it. 33x. How specialized a band can be is not set by how many useful
skills exist

**more_skills_needs_a_bigger_band_or_a_better_channel** — holds

to hold 6 skills instead of 2, either the band grows to 90 (15 deep) or
the channel improves: drop the telephone from 0.1 to 0.01 and the same
28 people carry 5 specialties at 5 deep. Specialization depth is
transmission fidelity and headcount, in that order. Writing is the
second lever and it is the cheap one, which is the whole reason it is
worth inventing

### engine/descent.py

Seed the smallest thing that can live, supply the planet, and let go.

**the_seed_has_no_traits** — holds

the seed is a single sphere of 1.58 microns -- the closure floor
engine/earthlab.py derives -- with no circulation, no skin, no skeleton
and no instruction to acquire any

**nothing_rewards_complexity** — holds

fitness is energy per gram from Kleiber and nothing else. At the same
size, carrying circulation scores 0% WORSE -- a trait is pure overhead
until a wall makes it necessary. Nothing here is scored against being
large or complex

**size_holds_at_the_closure_floor** — holds

the lineage holds at 1.76 microns against a closure floor of 1.58, from
1.75 at the seed. It neither grows nor collapses. This rule has been
INVERTED TWICE: it first asserted growth, then collapse to 0.1 microns,
and both were artifacts -- the second of an objective that diverged as
mass fell. The floor is not a clamp now, it is engine/earthlab.py's
closure size, derived from how many molecule types a compartment must
hold to catalyse its own repair

**what_emerges_was_not_supplied** — holds

after 4000 generations the population carries no trait above half, from
a seed that had none and a fitness that charges for every one. Whatever
is there was kept by the walls, not supplied

**intake_bounds_size_from_above** — holds

intake goes as mass^(2/3) and cost as mass^0.75, so they cross at a
radius of 17.0 cm. Above it a body burns more than its surface can
supply. The first run had no intake rule, bigness was free, and the
population grew to EIGHTY-ONE METRES before hitting a land skeleton's
ceiling while swimming -- which is how the absence announced itself

**nothing_selects_for_size_in_either_direction** — holds

size drifts 0.8% over the whole run, so nothing selects for size IN
EITHER DIRECTION once closure bounds it from below. The earlier version
of this asserted only that nothing favours being large, which was half
the statement -- and the missing half was doing real damage, because
fitness as surplus per gram favoured being small without limit and that
was read as a biological result rather than an unbounded objective

**encounter_rate_is_no_refuge** — holds

encounter rate is 6.75e+01 per second at every prey size tested -- it
varies by 1.0000x across four orders of magnitude. Density goes as
r^-3, cross-section as r^2, speed as r, and the product is r^0. Being
large is no refuge from being FOUND, and each meal is bigger, so the
obvious mechanism is not the mechanism

**a_second_organism_reverses_it** — holds

predation was the named missing category and adding it did not do what
I expected. Alone the population settles at 1.76 microns; with a
separate predator lineage the prey settles at 1.77 and the predator at
5.09, a ratio of 2.9 which is just PREDATOR_RATIO. The hunter tracks
its prey down to the floor. Pushed to 99% of deaths from predation the
prey reaches 0.13 microns and no further: growing to escape costs more
than being eaten, because surplus per gram goes as mass^(-1/3) and that
is a steep hill against a BOUNDED risk. Two organisms were not enough

**shrinking_does_not_delete_matter** — holds

300 bodies built and killed and the pool is 1.000000 kg, unchanged.
This lineage collapses from 1.58 um to 0.1 um and the matter it sheds
is now accounted rather than forgotten

**the_collapse_was_an_unbounded_objective** — holds

the collapse to 0.1 microns is GONE, and it was never the energy
balance. fitness returned surplus PER GRAM, a*m^(-1/3) - b*m^(-1/4),
which diverges as mass falls -- 3.3e6 at 1.58 microns and 5.5e8 a
hundredth of the way down. The lineage was descending an unbounded
objective into max(r, 1e-7), a typed clamp. Consulting
engine/earthlab.py's closure floor bounds it: below 1.58 microns a
compartment cannot hold the molecule types to catalyse its own repair,
so surplus buys nothing. The lineage now holds at 1.76 microns, and the
break-even at 2.04e+01 kg is the ceiling it never approaches

### engine/disease.py

Why anyone would bother to cook, wash, or build a wall.

**a_band_is_too_small_to_hold_a_crowd_disease** — holds

a crowd disease with a 10-day infectious period needs one fresh
susceptible per period or the chain breaks, and births arrive at N/25 a
year -- so it cannot live below 912 people. A band of 28 burns through
every host in a month and the pathogen goes extinct with them. It takes
33 bands in permanent contact. Foragers do not have epidemics; they
have parasites and whatever the animals gave them

**settling_is_what_invents_the_disease** — holds

engine/accident.py found that only a 365-day store beats the 73-day
threshold for staying put. Staying put is the whole mechanism: shedding
accumulates toward a steady state over 365 days, and a band that leaves
at 73 days never gets near it. Settled ground carries 114x the load of
a camp, and the aggregation that a year's grain allows finally clears
the 912 floor. The pathogen is not an extra assumption. It is the grain
harvest, seen from the other side

**cooking_pays_for_itself_fifty_times_over** — holds

raw: 1e+06/g over 200 g against an ID50 of 1e+04 is infection with
p=1.000. 7 decades of killing takes it to p=0.0020. A bout is 7 days of
fever at +26% BMR plus the food you did not go and get: 132 MJ. Heating
a kilo 65 K on a 10% efficient fire costs 2.3 MJ of wood. 58x. Nobody
had to understand why

**a_wall_pays_before_anyone_mentions_disease** — holds

a wall is worth 526 MJ a year in thermoregulation alone -- 5 W/K across
10 K for 8 hours, 365 nights -- which is 53 days of food. It pays on
heat before anyone mentions disease, and the separation from your own
ground comes free with it. That is the shape of all three: the hygienic
thing is adopted for a reason that is not hygiene, and keeps being done
because the people who do it are the ones still alive

**every_answer_to_it_is_a_skill_and_the_band_is_full** — holds

fire, washing and walls are 3 skills, and each has to be held and
handed on like any other. engine/craft.py says a band of 28 bottoms out
at 2 specialties before fidelity eats the breadth -- it cannot hold the
answers to the problem that settling created. Written, the same 28 hold
9. So the disease does not just follow the grain; it puts the load on
the channel, and the channel was already at its ceiling. That is a
pressure, not a gap

### engine/earthlab.py

One planet, every rule, and the question asked step by step.

**the_early_gates_open** — holds

solvent, energy and compartment open on Earth: water, a genome costing
3.3e-15 J, and a bilayer that assembles itself. Elements is open too.
None of energy, water or compartments is what stops this

**a_membrane_is_the_same_rule_as_folding** — holds

the membrane gate and engine/folding.py use ONE rule. Burying carbon
away from water is worth about 3.7 kJ/mol per CH2, which collapses a
protein -- phenylalanine scores 3.00 on the same carbon-to-polar ratio
-- and assembles a vesicle. Two consequences, one rule, and neither was
fitted to the other

**the_barrier_is_fidelity_not_supply** — holds

the first gate that does not open is 'search'. Supply is not the
problem on Earth -- every gate about having enough of something opens,
and the ones that shut are about keeping information rather than
getting materials

**the_two_bounds_close_on_each_other** — holds

two bounds derived from unrelated arguments -- 57 residues from
counting sequences, 100 bases from Eigen's error threshold -- both fall
below the 200-base replicase. And the replicase is what would raise the
second bound. The gap is not a shortage, it is a loop

**this_is_a_constraint_not_an_origin** — holds

this walks Earth to the first gate that does not open and says where it
is. It does not open it. The mechanism that crosses from 10
maintainable bases to a 200-base copier is still absent, and the value
of the walk is that four popular candidates -- energy, elements, water,
compartments -- are now ruled out by derivation rather than opinion

**cancelling_a_rule_sizes_the_gap** — holds

relaxing each shut gate sizes it: search needs 512000000000x; fidelity
needs 2x; persistence needs 1x. 2 of them are modest -- fidelity,
persistence -- and a factor of two in copying accuracy is the whole
distance between chemistry and a replicator. Only search is
astronomical, which is why chance is not how it was crossed

**assembly_clears_what_search_cannot** — holds

a 20-base piece is 1.1e+12 sequences, exhausted in 4.3e-53 years, and
sits inside the 100-base error threshold. 10 of them ligated is 200
bases -- the object neither gate could reach whole. The whole object
passes neither bound and a piece passes both, so the gap closes by
building rather than drawing. This is Levinthal's answer for the fourth
time here -- folding is not a search, sequence-finding is not a search,
and assembly is not either

**closure_and_diffusion_bracket_a_real_cell** — holds

closure needs at least 1.58 microns to hold 1e+08 molecule types at
1e-02 M; diffusion allows at most 47.5 before the centre suffocates. A
bacterium is 0.5 to 5 microns and sits inside a window neither bound
was aimed at. The 100 nm vesicle that passes the compartment gate holds
25225 molecules against the 1e+08 types closure wants, so a bag is not
yet a cell. The two bounds come from diversity and from diffusion,
neither aimed at the other, and what they bracket is the size life
actually is

**fidelity_opens_in_a_seven_kelvin_window** — holds

fidelity is SHUT at 298 K, OPEN at 255, and SHUT again at 245 -- a
window 7 K wide between 252 K, where the brine freezes, and 259 K,
where copying gets too sloppy to hold a replicase. It is not a
threshold, it is a WINDOW, and Earth has one. Inside it only ['search']
stays shut, which engine/earthlab.py's own assembly gate is the route
around

### engine/ecology.py

Many species, one finite world, and the causes of death made explicit.

**every_death_cause_is_an_existing_rule** — holds

7 causes of death and six of them are rules written for other reasons:
starvation from the intake balance, suffocation from the diffusion
limit, desiccation from the vapour deficit, crushing from square-cube,
freezing from the liquid-water line, predation from a size ratio. Only
'crowded out' is new

**competition_is_the_only_compounding_cost** — holds

predation is bounded -- a thing dies once -- while metabolic advantage
compounds every generation, and engine/descent.py showed a bounded cost
cannot beat a compounding return even at 99% of deaths. A RIVAL is
different: it takes a share of the intake every generation for ever.
That is the only cost here with the same shape as the advantage it
opposes, which is why competition and not predation was the missing
piece

**what_many_species_do_that_one_could_not** — holds

9 snapshots: median size 1.50 to 0.64 microns, spread 6.8x to 36.6x
across species. Commonest death is 'crowded out' at 75. Size still does
not climb, and now the reason is explicit in the death ledger rather
than inferred

**competition_makes_a_range_not_a_size** — holds

one lineage on its own settles at 1.76 microns, held there by the
closure floor. Add rivals and the median goes DOWN to 0.64 --
competition does not drive size up and it does not hold it up either.
What it produces is a RANGE: species span 37x smallest to largest, and
the median sits low because the smallest niche is the most crowded and
the cheapest to occupy. Almost every death is 'crowded out' (75). The
earlier version of this rule said competition prevented a collapse; the
collapse was a bug in engine/descent.py and fixing it there left this
rule asserting something no longer true

**bodies_are_made_of_atoms_that_return** — holds

every body in the run was built from a pool and returned to it, 11.000
kg in and 11.000 kg out. Before this, species died and the matter
simply stopped being mentioned

### engine/empire.py

A code of law and an empire, handed over, then audited.

**an_empire_is_bounded_by_its_signal_speed** — holds

a centre that cannot answer before a crisis finishes does not govern
the place, so the radius is 50 km/day times half a 90-day window: 2,250
km, reaching 15,739,694 km2 or 3.1% of Earth. Not a question about
ambition

**the_derived_span_lands_on_rome** — holds

Rome to Hadrian's Wall is 1,900 km and Rome to the Euphrates 2,500. The
derived radius is 2,250 km and lands between them, out of a courier
speed and a crisis window and nothing else. This is the one place in
the whole human chain where a number here meets something that actually
happened

**honesty_is_a_condition_on_the_channel** — holds

speech is worth its cost only because it carries a selection the
receiver need not check. Above 4.7% lies, the channel tolerates 4.7%
lies and this... -- everything must be verified and verifying costs
what deriving would have, so you pay the telling AND the thinking. DO
NOT BEAR FALSE WITNESS is not an ethical premise here, it is the
condition under which speech stays cheaper than thought

**most_of_the_code_does_not_derive** — holds

of 10 injunctions, 3 derive from rules already here (do not bear false
witness, do not kill, honour your parents), two are partial, and 5 do
not derive at all. The code was HANDED OVER and most of it stayed
handed over. What is worth saying is not that the rest is wrong -- it
is that nothing here prices belief, rank or rest, so those are absences
and not refutations

**faster_signals_make_bigger_empires** — holds

a runner at 40 km/day governs 1,800 km and an optical telegraph at 800
governs 36,000, which is 100% of the planet. The size of the largest
possible empire is a fact about signalling and moves when signalling
does -- it predicts that global empires cannot precede fast signals,
and they did not

### engine/eos.py

The nuclear equation of state: not known, but bounded, and the bounding
is a derivation.

**band_from_data** — holds

the maximum is between 2.08 and 2.3 solar masses -- 0.22 wide, against
the 0.70 the module refused in before the observations were consulted

**narrower_than_asserted** — holds

the asserted band was 2.2-2.9 (0.70 wide); observations give 2.08-2.3
(0.22 wide), 69% narrower and from data

**probe_refutes** — holds

a proposed maximum of 1.8 is refuted by 3 observed pulsars; one of 2.6
is refuted by 1 merger constraint(s). The data excludes, it does not
derive

**still_refuses_inside** — holds

2.15 solar masses is still undetermined, and the refusal now names what
would settle it

**observations_consistent** — holds

4 observations, floor 2.08 <= ceiling 2.3, so no observed neutron star
is heavier than the collapse constraint allows

### engine/evolve.py

The system run forward in time, and every planet checked at each step.

**the_star_brightens_with_age** — holds

the star runs 0.71 to 1.73 Lsun across its 10.0 Gyr main sequence,
because fusing four hydrogen into one helium raises the core's mean
molecular weight and it must burn hotter to hold itself up

**the_habitable_band_moves_outward** — holds

the ice line sweeps 2.27 -> 3.52 AU and the band's inner edge 0.84 ->
1.31 AU across the main sequence. The outer edge is undetermined until
CO2 condensation exists. A planet does not sit in a zone; the zone
moves across it, and here the leading edge sweeps 55% outward while
nothing about the planets changes

**habitability_is_a_when_not_a_where** — holds

3 generated worlds spend time inside the band's inner edge, and 1 leave
it before the star does: 0.99 AU is too hot after 4.2 Gyr. Asking
whether a planet is habitable without saying WHEN is not a well-formed
question. The outer edge is refused, so these windows are open-ended on
the cold side

**a_heavier_star_dies_sooner** — holds

a half-solar star lasts 57 Gyr and a two-solar one 1.77 -- 32 times
shorter for four times the fuel, because luminosity climbs as the 3.5
power of mass. Big stars are not where you look for old life

**the_faint_young_sun_appears_unprompted** — holds

the star begins at 0.71 of its present output with nothing asked of it
-- the faint young Sun falls out of fuel and burn rate, and is the
reason the carbonate thermostat in engine/terraform.py has to exist

**band_edges_come_from_the_thermostat** — holds

the band is 0.999 to 1.899 AU, both edges run out of the thermostat
rather than typed as flux thresholds. The inner is where rain stops and
the CO2 sink closes; the outer is where CO2 CONDENSES and caps its own
greenhouse. Published maximum-greenhouse estimates put the outer edge
at 1.67-1.77 AU. It was UNDETERMINED in 3.1.36 and refused rather than
bounded by hand, which is what made the missing rule findable

### engine/folding.py

Every fold enumerated, and Levinthal's paradox answered by counting.

**hydrophobicity_derived** — holds

20 residues scored from the formulas alone: G at 0.67 up to F at 3.00.
Continuous, because the largest gap in the sorted ratios falls between
Y and W and splitting there would call only F and W hydrophobic

**walks_are_self_avoiding** — holds

every walk at n=5, 7 and 9 visits each site exactly once

**enumeration_is_exhaustive** — holds

fixing the first step removes exactly the fourfold rotation and nothing
else -- n=4: 9 reduced, 36 full; n=6: 71 reduced, 284 full; n=8: 543
reduced, 2172 full

**collapse_lowers_energy** — holds

FFFFWWFF reaches -27.00 and GGGGSSGG only -1.50 over the same 543 folds
-- the same shape costs different energy depending on what is in it,
which is hydrophobic collapse and the only force here

**degeneracy_reported** — holds

FGFGFGFG: 543 folds enumerated, best energy -6.00, and 19 distinct
folds reach it -- a degenerate ground state, reported rather than one
of them picked

**levinthal** — holds

100 residues, 5.15e+47 conformations, 1.63e+28 years to try them all --
1.2e+18x the age of this universe, so folding cannot be a search here;
but 6.1e+71x LESS than the time to heat death, so a universe run that
far could afford it

**refuses_to_predict** — holds

structure prediction is refused and names what does it instead --
enumeration on a lattice is exact and is not a structure

**mirror_images_are_one_fold** — holds

FGFG's two minima are one fold and its reflection -- walks() fixes the
first step, which kills rotation but not mirroring, and quotienting by
it turns a false 2-way tie into one fold

**answer_is_scale_free** — holds

multiplying every weight by 7.3 leaves the fold identical and scales
the energy by 7.3 squared, as a product of two weights must -- the
hydrophobicity ratio carries no units and the answer does not read a
scale that is not there

**alternating_cannot_be_flipped** — holds

a square lattice is bipartite so every contact joins an odd index to an
even one; in ABABAB every contact is A-B and the energy is one constant
times a count, which no reweighting can reorder -- the first bar
measured only such sequences and its perfect 14 of 14 was measuring
nothing

**bar_is_a_rate_and_is_measured** — holds

55 of 96 sequences keep the same minimising fold when sulfur is counted
as greasy rather than polar, a call the electronegativities do not make
(S 2.58, C 2.55). 43% of exact minima are the model's choice, not the
sequence's. This is the folding bar and it is a rate, because there is
no measured fold to take a residual against

### engine/frozen.py

Why the code we have looks arbitrary: changing it is lethal at once.

**a_mapping_is_selected_by_the_cost_of_changing_it** — holds

engine/code.py left this open: any assignment of subsequences to
catalysts works equally well, so nothing selects one. Something does --
the cost of CHANGING it. 5 meanings over 100 codons, so one change
breaks 100.0% of every sequence written so far. A mapping is not chosen
for being good, it is kept because changing it is lethal

**the_cost_is_total_from_the_first_sequences** — holds

with 5 meanings over 100 codons a single change breaks 100.00% of
sequences. That is total, and it is total FROM THE FIRST SEQUENCES --
before anything has had time to be good. So the first mapping to arise
is the one kept, and its merit never enters

**a_narrow_code_freezes_harder** — holds

a NARROW code freezes harder: 4 meanings 100.0%, 5 meanings 100.0%, 20
meanings 99.4%, 64 meanings 79.3%. With few meanings every sequence
uses every codon, so nothing survives a change -- and engine/code.py
says the first code had five meanings, which is the worst case for
escaping it

**so_the_mapping_is_arbitrary_and_that_is_derived** — holds

the selection is real and it selects for NOTHING about the mapping. It
is indifferent between assignments and locks whichever arrived, at
100.0% cost to change. So the answer to why the code looks arbitrary is
that it IS arbitrary, and the arbitrariness is now derived rather than
left as a gap. The gap said 'nothing selects a mapping'; the truth is
that something selects HAVING one and is blind to WHICH

### engine/generate.py

Generate every universe the rules allow. Ask questions afterwards.

**the_generator_is_not_told_the_question** — holds

_facts records 20 quantities and contains no target, no success
condition and no early exit. A search that knows what it wants can stop
at a promising branch, pick a grid that brackets the expected answer,
or read an absent result as a bug in itself. A generator that does not
know cannot do any of those

**the_space_generates_once** — holds

10,584 universes over 6 axes in 0.1 s, 0 failing. Every row carries
every quantity the rules yield at that point, whether or not anything
has asked. That is the entire cost, paid once

**questions_are_lookups_afterwards** — holds

a three-condition question -- in the band, brine still liquid, a body
able to shed its own heat -- returns 864 universes in 46 ms.
engine/multiverse.py answered a narrower version of this by sweeping
seeds and took 22 s per 20,000 worlds

**it_answers_things_nobody_asked** — holds

nobody asked for the overlap between worlds that can hold a 200-base
genome (3024) and the quarter of worlds with the highest tree ceiling,
above 355 m (2646), and the store answers it anyway: 756. The
quantities were recorded because the rules produced them, not because a
question wanted them, which is what makes a later question cheap

**the_store_knows_when_a_rule_moved** — holds

the store is keyed on 9be8c86937dfa4e5, a hash over the fingerprints of
every rule that fed it, through engine/spine.py. A row goes stale
exactly when a rule beneath it changes and not otherwise -- so this is
not a cache that has to be remembered about, it is one that knows

### engine/genesis.py

A system generated forward from a nebula. Our planets are the test,
never the input.

**the_seed_contains_no_planet** — holds

the seed is 4 numbers -- nebula_mass, metallicity, spread_au, draw --
and none of them is a planet. Our planets are compared against at the
end and never consulted on the way; a seed that contained them would
make any agreement a restatement of the input

**ice_line_falls_in_the_asteroid_belt** — holds

water ice can first condense at 2.68 AU, from the star's luminosity
alone. The asteroid belt runs 2.1 to 3.3 AU, Mars is at 1.52 and
Jupiter at 5.20 -- the rock/ice boundary falls between them and no
planet was used to put it there

**rocky_inside_icy_outside** — holds

5 rocky positions inside 2.68 AU and 5 icy ones outside, with no
interleaving. The ordering is a consequence of one temperature profile

**a_dimmer_star_moves_everything_in** — holds

a 0.6 Msun star puts the ice line at 1.08 AU and a 1.2 Msun star at
3.62. The habitable structure of a system moves with its star, which is
the kind of thing a table of our planets could never say

**planets_have_a_composition_not_a_label** — holds

a planet at 280 K condenses to Fe 32%, O 27%, Si 12%, Mg 18% against
Earth's measured 32, 30, 15, 14. From solar abundances and laboratory
condensation temperatures, with no planet consulted -- 'rocky' was a
string and this is not

**oxygen_arrives_bound_in_silicates** — holds

oxygen is 27% of a 280 K planet even though water ice needs 170 K. It
arrives BOUND IN SILICATES, and an element-keyed condensation table
left it out entirely -- wrong by a third of the planet

**positions_land_near_real_planets** — holds

9 of 10 generated orbits fall within 35% of a real body, worst 30% --
including 0.99 AU against Earth and 1.53 against Mars. The spacing came
from a seeded random walk, so this is partly the draw; what is NOT the
draw is that rocky bodies land inside the ice line and giants outside
it

**masses_are_wrong_and_say_so** — holds

6 of 9 masses are out by more than 3x, up to 489421x. Isolation mass
says how much a body can sweep from its own feeding zone; Mercury and
Mars are far LIGHTER than that, which is a known open problem in planet
formation rather than an arithmetic error here. The structure derives
and the masses do not, and saying so is the result

### engine/group.py

Why survival is in groups, how big, and why strength loses to knowing.

**energy_does_not_set_the_size** — holds

a child costs 51 W and an adult nets 97, so 1.9 adults carry one child
at every scale and the spare per head is zero for a group of two and
zero for sixty-four. Adding people neither gains nor loses per head, so
ENERGY DOES NOT SET THE SIZE -- whatever does must not scale linearly

**transitivity_is_what_allows_a_group_at_all** — holds

every pair in a group must be settled once, which is 10,296 contests at
n=144. But a rank order is TRANSITIVE -- if A beats B and B beats C
nobody fights A and C -- so it sorts in 1,032, a factor of 10.
Transitivity is what lets a group be larger than a handful at all, and
it is the same memory engine/regard.py priced at 1.4 microjoules

**the_derived_optimum_is_a_family_not_a_band** — holds

defence saturates as base/n and contests grow, so the optimum is n = 3.
THAT IS A FAMILY, NOT A BAND. Real groups are twenty to a hundred and
fifty, so this is not the whole story and the number is reported as it
comes out rather than adjusted toward the record

**strength_is_zero_sum_and_understanding_is_not** — holds

both get you fed and they are not symmetric. engine/regard.py showed
nothing transfers within a species, so STRENGTH moves a share between
heads and leaves the total alone -- 50% of it at two and 2% at fifty.
UNDERSTANDING answers a constraint, which opens what was closed, and
adds for everyone. Strength is zero-sum and understanding is not, so
the larger the group the worse that trade is for strength

**the_missing_benefit_is_named_not_fitted** — holds

CLOSED. The optimum here is 3 because every rank contest was charged as
a fight. engine/signal.py found that a display settles it when the
asymmetry is visible, five million times cheaper, and with nine in ten
settled that way the affordable group is 28 -- inside the real 20 to
150. And engine/accident.py supplied the linear benefit that was
missing: a store is defended by the group holding it and a larger store
is worth more to defend

### engine/halflife.py

Measured half-lives, and the two questions they finally answer.

**boundary_is_derived** — holds

an isotope survives to now if its half-life exceeds 2.51e+07 yr -- from
one solar mass needing 182 halvings to reach a single atom, not from a
chosen cutoff

**primordial_set** — holds

8 nuclides survive to now: ['In', 'K', 'Rb', 'Sm', 'Te', 'Th', 'U'] --
and Pu-239 (24,110 yr) and Tc-98 (4.2 Myr) do not, which is the test

**trace_or_absent_resolved** — holds

trace ['Ra'] on alpha steps alone; undetermined ['Ac', 'At', 'Fr',
'Pm', 'Po', 'Rn', 'Tc'], reachable only through beta steps whose Q is
under the 1.2083696436986884 MeV resolution; absent [], unreachable
even with the bar off. The blanket refusal is withdrawn for 1 of 8 and
kept, with its reason, for 7

**window_keeps_the_unstable** — holds

U-238 is a referent from ns_merger for 8.12e+11 yr; Pu-239 for only
4.38e+06 yr. Both are recorded -- unstable is not absent, it is bounded

**refuses_what_is_not_measured** — holds

an unmeasured half-life is refused, and the refusal cites the withdrawn
estimator rather than falling back on it

**decay_inverts** — holds

C-14 after exactly one half-life: 0.5 remaining, and the elapsed time
recovers from the fraction

### engine/heredity.py

Division, heredity and selection, none of them added.

**division_is_geometry_and_nothing_decides_it** — holds

two spheres of half the volume need 1.2599 times one sphere's area --
26.0% more. Lipid is made in proportion to contents, so area accrues as
V while the sphere needs V^(2/3), and the excess reaches that at a
volume ratio of 2.00. A vesicle DIVIDES EXACTLY WHEN IT DOUBLES, and
nothing decides to: no timer, no trigger, no rule beyond a sphere's
area

**heredity_is_copy_number** — holds

a compartment at the closure floor holds 1.0e+10 molecules over
357,913,940 types, so 27.9 copies each. A random half-split misses a
given type only when every copy lands on one side, 2^-28 = 3.9e-09.
Heredity is not a mechanism added here -- it is what copy number does
under a coin flip

**selection_is_what_copy_number_leaves_over** — holds

1.39 TYPES ARE LOST PER DIVISION. Heredity is high-fidelity and not
perfect, and the imperfection is not a parameter -- it is what 28
copies and a coin flip produce. Catalysts per reaction is Poisson with
mean 3.58, so 10.0% of reactions have exactly one, and losing that type
stops them. About 50% of divisions yield a daughter that cannot close.
Variation and differential survival, neither of them added

**no_mutation_rate_was_introduced** — holds

this file defines one constant, 2^(1/3), and it is exact geometry. No
mutation rate, no division timer, no fitness function. Everything else
is read from engine/occurrence.py, which read it from engine/closure.py
and engine/earthlab.py. A number introduced to make a mechanism work is
the mechanism not working

**three_of_four_now_and_the_fourth_is_named** — holds

engine/occurrence.py closed the first of four -- chemistry that
sustains itself -- and named the other three absent. Division is
geometry (2.0x volume), heredity is copy number, and selection is the
1.39 types a split leaves behind. THE FOURTH IS STILL MISSING and it is
the one that was always hardest: nothing here copies a SEQUENCE.
Compositional inheritance passes on which molecules are present, not
what any of them says, so there is no genome and nothing that could
carry an instruction forward

### engine/human.py

The last step, and what it costs to take it.

**the_gut_trade_was_the_wrong_question** — holds

INVERTED, kept. The sum is still right -- 12.8 W freed against 11.1 W
spent -- and it answers nothing, because it prices an ADULT STANDING
STILL, as though a brain were a running cost some organ must offset. A
brain is built, out of food, in childhood, by someone else.
engine/ontogeny.py runs the life instead of the snapshot: a newborn's
brain is 109% of everything its own body can make, and the 3.0
adult-years a child costs were never inside one body to be found by
rearranging its organs

**cooking_alone_does_not_explain_the_gut** — holds

MISSING_RULE, and NARROWED. This used to say cooking fails to pay for
the brain; engine/ontogeny.py showed the brain was never waiting on the
gut. What is left is still real and now stands on its own: the human
gut IS smaller, and nothing here explains how far. Walk brain and diet
up together and the climb LOSES ground the whole way, 0.00 W to -3.48
W. It only breaks even at a 61% diet improvement, and cooking is
measured at 35% -- short by a factor of 1.73 -- and 2.18 against the
76% the recorded gut implies. So cooking alone does not pay for a human
brain. COOKING_GAIN was NOT raised to close this. What is absent is
whatever else made the food cheaper: meat is denser per gram, pounding
and cutting digest food outside the body, and sharing spreads a bad
day. None of those has a rule here, and the gap says how big they have
to be together

**the_two_routes_to_the_gut_are_compared** — holds

CLASH, and both sides are kept. Route one takes the RECORDED ape and
human gut fractions and finds the trade works: 12.8 W freed against
11.1 W spent. Route two models the gut from diet quality and finds it
does not. They disagree because the recorded human gut implies a diet
76% better than raw forage and nothing here supplies more than 35%. The
trade is real; the reason the gut could shrink that far is not derived.
Neither number was moved to make them agree

**a_tool_must_feed_the_head_that_made_it** — holds

the extra brain over an ape's costs 13.6% of the budget. A tool
returning 5% does not pay for it; one returning 30% does. Cooking is
measured at about 35%. So tool use is affordable here -- which is not
the same as saying anything made one

**a_human_is_made_of_atoms_and_returns_them** — holds

a 70 kg human is O 34.1 kg, C 24.7 kg, H 5.1 kg and the rest, built
from a pool and returned to it whole. The same rule that catches a
forest growing out of nothing catches a person

**nothing_here_says_it_happened** — holds

every row here says CAN, never DID. The gut can pay for the brain, the
climb can be walked in increments, a tool can return more than it
costs. What no rule in this repository reaches is why this lineage and
not the other large-brained land endotherms -- engine/ancestry.py marks
that step RECORDED and it stays RECORDED. The path is shown to be open.
It is not shown to have been taken

**the_ramp_test_is_exercised** — holds

is_a_ramp() returns False, losing ground at step 1 of twenty. It is the
predicate behind the cooking MISSING_RULE and it had no caller of its
own

### engine/industry.py

Sixty million people, every material they ask for, and the answer.

**an_industrial_revolution_is_burial_run_backwards** — holds

engine/atoms.py already kept two books and called the gap between them
coal and oil, before anything here intended to burn any. Land
photosynthesis runs 352 TW and buries 352 GW-equivalent a year, which
over 300 Myr is 3.33e+27 J. An industrial revolution is not a new kind
of energy -- IT IS THE BURIAL ACCOUNT RUN BACKWARDS

**free_materials_do_not_lift_the_ceiling** — holds

a boiler at 480 K allows 39.0% and no material raises it past 54.7%,
because water is not liquid above 647 K. Newcomen managed about 0.5%
against a 21% ceiling, so the gap was never a shortage of iron.
Spawning every material asked for moves NOTHING here: Carnot does not
read the parts list, only the temperature

**sixty_million_is_not_enough_to_matter** — holds

60 million at 1000 W each draw 60 GW against 352 GW buried a year, a
ratio of 0.17. A Roman industrial revolution would have been INSIDE THE
FLOW -- machinery, not a revolution, and not the thing that word now
means. Their whole muscle output is 5.8 GW, so a thousand watts each is
already a tenfold change in their lives and still invisible to the
planet

**what_we_actually_do_is_the_striking_number** — holds

we draw 18 TW against 352 GW of burial, so EVERY YEAR WE BURN ABOUT 51
YEARS OF ACCUMULATION. That number, and not any invention, is what
separates an industrial revolution from a lot of machinery -- and it
came out of a burial rate this repository wrote down to explain why a
leak is not a cycle

**the_stock_is_finite_and_that_is_arithmetic** — holds

3.33e+27 J at 18 TW lasts 5,865,517 years. That is arithmetic and not a
warning -- a stock divided by a rate. Whether the estimate of what is
recoverable matches what was buried is a question this file cannot
answer, and the burial fraction it rests on is CHOSEN

### engine/inherit.py

Is the DNA good enough to say how tall or how strong? No.

**the_dna_here_cannot_say_how_tall** — holds

engine/biomatter.py holds the four nucleotides by formula, the standard
code and B-form geometry. engine/descent.py holds a radius and three
named traits. NEITHER FILE MENTIONS THE OTHER -- there is chemistry at
one end, a label at the other, and no map between. So no, the DNA
cannot attribute height, and it is not a close no

**muscle_is_derived_from_stress_and_area** — holds

the 400 N blow engine/tools.py needs to crack a bone wants 1600 N of
muscle across 53 cm2 at 3e+05 Pa. That is an arm, and no gene had to be
invented -- the number was already implied by a module that only wanted
a hammer

**height_is_bounded_and_not_determined** — holds

at 2.6 m the ankle carries 0.7% of bone's strength, so everything from
1.2 to 2.6 m stands. So height is BOUNDED and free inside the bound,
which is a real answer rather than a shrug: these rules constrain the
trait and do not determine it, so it has to be given and the giving is
visible

**health_is_a_load_with_no_purge** — holds

1.5 harmful mutations a generation reach 75 in fifty with nothing
removing them. no rule in this repository purges a deleterious
mutation. engine/civ.py found the same hole from the other side when
sex came back PARTLY DERIVED -- the NEED for repair follows from the
error threshold and the mechanism does not. The ratchet is named in two
modules now and turned by neither

**preferable_needs_a_measure_of_better** — holds

the assigned genome is 1.80 m and 60 cm2, and it is marked GIVEN in 2
of 5 traits. 'Preferable' needs a measure of better and no rule here
supplies one: 1.6 m runs at 72 W and 2.1 m at 132 W, 84% more, every
second, forever. Taller is not fitter, it is hungrier, so the
preference is somebody's and is labelled as somebody's

**the_assigned_genome_faces_the_same_gates** — holds

the assigned genome makes 450 N, above the 400 N a bone needs, so it
opens one -- and it eats 93 W against 82 W for a 70 kg body, 14% more
forever. BEING GIVEN A GENOME EXEMPTS IT FROM NOTHING. The preference
bought a capability and was charged for it by rules that never heard of
it

### engine/innovation.py

Discrete innovation: the same absence in three places, named.

**every_innovation_is_omit_duplicate_or_combine** — holds

6 supposed innovations, and not one is a new process: 4 are an existing
process with a step OMITTED, one is two things COMBINED, one is a
tissue DUPLICATED. engine/tools.py is the one that closed and it closed
by combination -- a hand and a stone, both already there. Nothing is
created, which makes the space countable where 'a new thing appears'
never was

**the_rate_falls_out_of_heredity** — holds

engine/heredity.py has 1.39 types lost per division, each catalysing
3.58 reactions, 10% of them sole-catalysed. So 0.50 lethal losses per
division and 4.48 NON-LETHAL ones -- a process running with a step
omitted and still closing, which is what an innovation is. Nothing was
added to get that rate

**single_omissions_are_not_the_barrier** — holds

every single-step omission in a 1e+05-reaction cell is sampled in 61
years at 4.5 per division. SINGLE OMISSIONS ARE NOT THE BARRIER, which
is the thing worth learning here -- the wait is not in finding one, it
is in needing several at once

**the_coordination_number_is_derived_now** — holds

k IS DERIVED NOW: 3.58, the Poisson mean p*M that engine/closure.py
measured, because losing one molecule type removes every reaction it
catalysed and that is how many. A coordinated change of that size is
not a conjunction to wait for, it is what ONE loss already is. The
fitted value was 3, so the fit had been reading this number off the
answer. What the derivation does NOT explain is the timing: types are
sampled in 2.2e+05 years against a record of 2e9, leaving a factor of
9,135. That is now a named unmeasured quantity -- the share of viable
omissions that are also USEFUL, about 1.1e-04 -- rather than a
parameter tuned to hide it

**the_taxonomy_is_falsifiable** — holds

the taxonomy is a claim and can be wrong: if an innovation turns up
that is not a step omitted, a thing duplicated or two things combined,
this file is false and the countability goes with it. That is the point
of writing it as six named cases rather than a principle. It also
predicts where to look -- an innovation should always have a PARENT
PROCESS, and if one has none then something here is creating rather
than recombining

### engine/inputs.py

Every number, and which of three things it is.

**every_number_is_classified** — holds

145 numbers classified: 49 CHOSEN, 6 EXACT, 88 MEASURED, 2 RECORDED. An
audit found 28 with no label at all, and calling them all 'measured'
would have been the generous answer rather than the true one

**chosen_numbers_are_admitted** — holds

49 numbers are CHOSEN -- picked so a model would run, with nobody
having measured them. The worst is descent.INTAKE_COEFFICIENT, which
carried the comment 'sets where supply and demand cross'. That is a
knob with a note on it, and pretending otherwise is how a fit becomes a
finding

**results_are_graded_by_worst_input** — holds

29 of 53 registered claims rest on nothing chosen. 19 do rest on chosen
inputs and must say so wherever they appear: the cell size window
1.58-47.5 um; life cools its own planet by 1.9 K; the light race stops
at 11 m; the food chain runs 4 levels; an empire reaches 2250 km at
courier speed; we burn 51 years of burial every year; 10,584 universes
generated blind, queried in 45 ms; a set closes above p=1e-3, measured
is 1e-8; holding never binds; discovery rate does; infrastructure taxes
8% and shortens the clock; every gift shortens the phosphorus clock;
the channel tolerates 4.7% lies; the assigned genome costs 11% more
forever; a person is nameable to 289 m; a shelter pays back in 4.6
nights; a brain fills in 1.49 years; seeded life stays microbial;
competition prevents the collapse; predation does not reverse the
collapse

**the_planet_chain_rests_on_nothing_chosen** — holds

the planet results -- the habitable band, Earth's composition, the
biosignature -- rest on no chosen input. The BIOLOGY results do. That
split is the honest state: the physics derives and the evolutionary
modelling has dials in it

**history_is_a_kind_not_a_gap** — holds

4 contingent facts registered, each one unrepeatable and each one
checkable -- Chicxulub against an iridium layer, endosymbiosis against
every eukaryote genome, the Great Oxidation against sediment isotopes.
engine/ancestry.py went SILENT on its last step and I read that as a
hole in the physics. It is not. It is a fact of a kind that had no
slot, and a chain reaching it should CHANGE KIND rather than stop --
the same way the cascade changes layer when a question stops being
arithmetic and starts being a date

**a_run_is_not_a_measurement** — holds

15 results are ENACTED -- they happened in a run. Not EXACT, nobody
defined them; not MEASURED, nobody observed them; not CHOSEN, nobody
picked them; and not RECORDED, which means it happened in the world.
They are history of a world that was never anywhere. 8 of them ALSO
carry an input grade, and that is not a contradiction -- the grade says
how good the numbers going in were and this says what the answer is
about. Every one is on the human side, which is why the kind was
needed: physics answers what CAN happen and this answers what DID. An
ENACTED result may be cited for what these rules do and never for what
the world contains

### engine/intricacy.py

How complicated a thing can get, and what stops it.

**intricacy_is_exponential_in_specialization** — holds

an artifact is a composition -- a hafted axe is stone AND cordage AND
wood -- so what a group can build is the subsets of what it holds at
once: 2^s - 1. A band of 28 speaking holds 2 specialties and can
therefore build 3 distinct things. Writing takes it to 9, and 511. 170x
from the same people. Intricacy is exponential in specialization and
specialization is linear in the channel, which is why the channel is
worth more than it looks

**speech_is_a_stable_trap_and_not_a_slow_climb** — holds

speech is not a slow version of writing, it is a fixed point. The
corpus could hold 13.1 parts' worth of designs, but fidelity only
supports 2 specialties, so the binding constraint is the channel and
NOTHING the band does relieves it -- more people means more mouths on
the same 8692-item ceiling, and the ceiling is one lifetime of
evenings. An oral society is not early. It is at equilibrium, and it
will sit there indefinitely unless something changes the transmission

**writing_moves_the_binding_constraint_to_people** — holds

in a village of 912 the written channel would support 304 specialties,
but 13% literacy gives 118 scribes, a corpus of 2958445 items that can
be recopied before they rot, and only 21.5 parts of design. The binding
constraint has MOVED: speech was limited by fidelity, which nothing
could fix from inside; writing is limited by how many people can be
spared from the fields, which yield can fix. That is the difference
between a trap and a loop

**the_loop_closes_on_a_number_and_it_is_not_infinity** — holds

iterating surplus -> scribes -> corpus -> specialties -> surplus
settles at 23.5 parts, 12163632 designs, a 2.14x yield and 53% of
people off the land -- against 2 and 3 for speech. It converges rather
than running away, because the corpus enters the intricacy as a
LOGARITHM while the designs come out as an exponent: doubling what is
written buys one more part. So the loop climbs and then crawls, and
every further step costs twice the last. That is a fixed point, not a
takeoff, and anything claiming a takeoff has to say which term it
changed

**a_region_in_touch_beats_a_village_that_is_not** — holds

a village alone settles at 23.5 parts. Forty villages in touch -- 36480
people inside a 16 km radius, reachable because knowledge is the one
cargo with no range limit -- settle at 29.4 parts and 7.33e+08 designs,
with 2.4x the output per worker from Wright's law alone. Nobody built a
city. The gain a city is credited with comes from the size of the
corpus's audience, not from standing close together

**a_design_is_not_divided_among_its_users** — holds

a loaf feeds one person, so 1000 loaves among 36480 people is 0.027
each. A technique for making loaves is used by everyone who knows it,
at once, and nobody has less of it for that -- 1000 techniques is 1000
each. The design stock is NOT divided, which is why the knowledge terms
carry no N in the denominator. It runs the other way too: an invention
costs one specialist's time whoever uses it, so the worst one worth
making needs b > C/N, which falls from 1.10e-03 in a village to
2.74e-05 in the network. More people is more ideas AND more users per
idea, and those are two different gains

**the_escape_is_land_share_against_non_rivalry** — holds

the only genuinely rival input is LAND, and it does not grow. Supply
gives N**0.372 (Wright 0.234 + skills 0.138, neither divided by
anyone), fixed land drags by its share, so surplus per head goes as
N**0.072 at a 0.30 land share -- growing the network 40x leaves each
person 1.30x better off. But at a 0.50 share it is N**-0.128 and nobody
gains. The crossover is a land share of 0.372, and that is a
FALSIFIABLE line: while farming is more than 37% of output, technology
rises and living standards do not; below it they move together. The
escape is not an invention, it is a share

**only_two_of_the_four_levers_are_worth_pulling** — holds

the fixed point converges because the corpus enters as a logarithm, so
trying harder buys nothing -- every further part costs twice the last.
Only a changed TERM moves it, and of four: a printing press +6.6 parts,
exponent 0.072; power that is not land +0.0 parts, exponent 0.322;
proofread twice more +0.0 parts, exponent 0.072; ten times the people
+3.3 parts, exponent 0.072. A press is worth 6.6 parts because a
hundred impressions where there was one is a hundredfold corpus and the
corpus is a logarithm -- the same reason ten times the people is worth
only 3.3. Power that is not land buys no parts at all and instead takes
the per-capita exponent from 0.072 to 0.322, which is the only one of
the four that makes anybody better off. Proofreading buys nothing: the
channel stopped binding at 3.1.112 and pushing on a constraint that is
not binding is the commonest way to waste an effort

### engine/lab.py

Small controlled experiments, one layer at a time.

**every_experiment_declares_a_layer** — holds

30 experiments over 8 rungs constants 12, molecule 1, column 3,
atmosphere 3, balance 3, feedback 2, world 1, composition 5; none empty

**layers_run_in_order** — holds

30 experiments ran from rung 0 to 7 in order, so a break is
attributable to a rung rather than to the whole system

**a_missing_rule_is_not_a_failure** — holds

HOLDS 27; MISSING_RULE 1; REFUSED 1; SUGGESTION 1 -- a missing rule is
a result, not a failure: the rules are self-consistent and
insufficient, which is a queue item rather than a bug

**the_known_missing_rule_is_found** — holds

layer 3 (atmosphere) reports co2_alone_has_a_ceiling: unbounded CO2
cannot reach the warmth of a body that exists, so a mechanism is absent
and it is NAMED -- collision-induced continuum and cloud scattering --
rather than patched with a coefficient

**no_experiment_fits_to_an_example** — holds

30 experiments and 0 take an observed temperature as a target. Where a
real body appears at all it appears as an EXISTENCE claim -- Venus is
this hot -- which a derived ceiling can contradict. That is a
discovery. Fitting to it would not be

### engine/learning.py

Turn off death and see what actually binds.

**the_store_fills_before_the_child_walks** — holds

4.70e+14 bits of synapse against 1e+07 bit/s from one nerve fills in
1.49 YEARS -- before the child can walk, and through the eye alone.
Whatever a brain is doing after that, it is not filling up

**forgetting_is_free** — holds

Landauer puts the floor under erasing the entire store at 1.39e-06 J.
Clearing and refilling all of memory once a second costs 1.7e-06% of an
82 W body, and a thousand times a second 1.7e-03%. Energy does not
constrain forgetting, so nothing is being kept because it was expensive
to drop

**immortality_buys_nothing** — holds

switch death off and nothing improves. A 70-year life already pours 47x
the store through one nerve; a million years pours 671,438x. Every
multiple past the first has to go somewhere and there is nowhere. THE
PROPOSAL FAILS, and it fails for a reason worth more than it would have
been worth: time was never the constraint, so removing its limit
changes nothing

**so_a_brain_is_a_filter_not_a_store** — holds

a store that saturates at 1.49 years cannot be what a brain is for --
it would be finished before it was any use. What is left is SELECTION:
the work is deciding what not to keep, and an immortal learner is the
same learner discarding more. That also says what mapping a brain while
it learns would show. Not a store filling up. A filter changing what it
lets through

### engine/life.py

What biophysics forbids, which is most of it.

**codon_length** — holds

4**3 = 64 codons for 21 meanings, 43 spare -- the code must be
redundant

**diffusion** — holds

r_max=1732.1 um at R=0.001 mol/(m^3 s); recovered R=0.001

**square_cube** — holds

173 m before stress reaches 1.7e+08 Pa at 1% bone cross-section;
recovered 1.7e+08 Pa

**reynolds** — holds

Re=0.000998 at 1e-05 m and 0.0001 m/s: viscous -- stop beating and you
stop within a body length

**earliest_life** — holds

{'C': 'stellar_c', 'H': 'bbn', 'N': 'stellar_c', 'O': 'stellar_c', 'P':
'supernova', 'S': 'supernova'}; the latest is ['P', 'S'] at supernova,
so nothing built from CHNOPS exists before it

**kleiber_unverifiable** — holds

82 W for a 70 kg animal, reported ASSERTED with no check -- the
exponent is observed, not derived here

### engine/lineage.py

Nebula to human, one chain, every link named.

**the_chain_runs_end_to_end** — holds

57 links from a nebula to what a head does, in order and in one list:
CROSSES 1, DERIVED 49, FORCED 7. engine/planetlab.py,
engine/earthlab.py and engine/ancestry.py each walked part of this and
none handed off, so the chain the repository is for was the one thing
nobody could read

**permission_is_not_pressure** — holds

7 of the middle links are FORCED and 0 remain merely ALLOWED. The
difference is the one the chain was missing: a permission says a step
is payable, a pressure says something is worse off not taking it, and
only the second produces anything. Most of the pressures were already
derived and never cited -- engine/biome.py holds the only one here that
rewards being larger, and no link referred to it. The eukaryote's is
new: ATP scales with membrane AREA and genome with VOLUME, so energy
per gene falls as 1/r until membranes go inside, which buys 200x

**every_link_names_its_rule** — holds

57 of 57 links name the rule and module that produce them; the 0 that
do not are exactly the 0 marked MISSING, whose whole content is that no
rule produces them

**the_gaps_are_named_and_counted** — holds

57 links, 0 gaps, 1 crossings. Crossings: large brain -> us. A crossing
is permitted and undriven -- the gates open and nothing makes it
happen, so permission is not occurrence and the distance between them
is not measured anywhere here

**competition_is_a_theorem_not_a_run** — holds

how many species coexist is bounded by how many limiting resources
there are, because at equilibrium each needs one it is best at and two
sharing a best cannot both stay. That is a statement about RANK.
engine/ecology.py answered the same question by running 600 generations
of 12 species; the bound needed no population at all

**abundance_falls_as_the_three_quarter_power** — holds

one body costs b*m^(3/4), so on a fixed energy share abundance goes as
m^(-3/4): a gram-sized animal is 31623 times commoner than a
tonne-sized one, which is 1e+06^0.75 exactly. Population energy use is
then the SAME at every size -- a field holds few large and many small
animals and nothing chose that, Kleiber did

**nothing_here_simulates** — holds

this file calls no run, sweep, census or generate. Every link is a rule
proved elsewhere and cited, and the three ecological statements are
theorems -- exclusion is about rank, energetic equivalence is Kleiber
divided through. README rule 3: a search means the rule has not been
found

### engine/literacy.py

Writing is a skill, and at first almost nobody has it.

**the_exemplar_is_the_check_and_that_is_the_advantage** — holds

a speaker cannot compare their telling to anything -- the source is
gone as it is spoken, so the only correction is other people. A copyist
has the original in front of them. One read-back at 0.9 catch takes a
0.1 slip to 0.010, worth 5 speakers; two passes 0.0010, worth 9; three,
worth 13 -- the whole specialization depth of a band, from one person.
Writing is the first channel here where a claim carries the thing that
would catch it being wrong

**writing_buys_the_specialties_the_band_could_not_hold** — holds

engine/craft.py bottomed out at 2 specialties 13 deep, because every
specialty steals voices from the consensus that was correcting the
telephone. A checked copy does not need voices. At 0.0010 the same 28
people hold 9 specialties 3 deep -- 4.5x the skills, with nobody added.
This is the lever craft.py named and did not price

**a_script_with_too_few_scribes_is_lost** — holds

you cannot learn to read from a book you cannot read, so literacy
bootstraps through the LOSSY channel and is subject to the same
consensus arithmetic as any other skill. One scribe: half-life 6.6
generations. Three: 24. It takes 5 holders to keep a script 40
generations (81 half-life), and a band of 28 that spares 5 for writing
has spent a fifth of itself on a skill that feeds nobody. A script is
not lost to catastrophe. It is lost to being held by too few people

**writing_is_worth_the_square_of_who_can_read** — holds

a written item needs a writer AND a reader, so peer value goes as f**2,
not f. But f**2 has no floor, and one literate in 912 on peer value
alone takes 20,000 years to go anywhere -- which is wrong. The floor is
the granary: a store needs an account and that is worth something
whoever else can read, so 3.6% of people (one scribe per holding) is
demanded whatever happens. This is why the earliest writing anywhere is
an inventory. The ceiling is food: a scribe does not farm, so literacy
stops at 13%, the share a 1.15x surplus can spare. Between them: 0y
0.1%; 200y 4.4%; 500y 8.6%; 2000y 13.0%. Value multiplies 1617x over
the first 200 years and 2.3x over the last 1500, and then it STOPS --
not because everyone can read but because nobody else can be spared
from the fields. Mass literacy is not waiting on a better alphabet, it
is waiting on yield

### engine/luca.py

The last universal common ancestor, checked against the rules.

**nothing_contradicts_the_reconstruction** — holds

5 of 6 constraints agree, 0 contradict, 1 the rules cannot speak to.
Agreement is weak evidence -- it is the CONTRADICTIONS that would have
been informative, and there are none to report

**the_differences_are_the_constraint** — holds

the useful half of the reconstruction is what bacteria and archaea do
DIFFERENTLY. Both have membranes and both copy DNA, with machinery that
is not homologous -- so LUCA had a compartment and a genome and NOT the
modern apparatus for either. That is exactly the regime these rules
describe: a bilayer that assembles without enzymes, and a genome
reached by ligating pieces because no polymerase exists yet

**half_of_this_rests_on_chosen_numbers** — holds

3 of 6 rest on CHOSEN numbers and say so: was enclosed, by something
that is not a modern membrane; was a cell; lived where the gradient
was. The compartment leans on an ocean concentration nobody measured,
and the cell size on a catalysis probability picked from the middle of
five orders. Those are not derivations

**it_does_not_claim_to_have_made_luca** — holds

this does not make LUCA and does not claim to. It checks whether
derived rules CONTRADICT a reconstruction built from comparative
biology, and 1 question it cannot speak to at all. Consistency with an
independent reconstruction is the strongest thing on offer, and it is
much weaker than having produced one

### engine/merit.py

What a skill is worth to the person who has it, and why that stops
tracking anything after a few generations.

**a_specialist_is_worth_their_scarcity_not_their_skill** — holds

you are worth what the band cannot do without, which is the value of
the skill divided by how many others hold it: 1 holders -> 100%; 2
holders -> 50%; 5 holders -> 20%; 13 holders -> 8%; 28 holders -> 4%.
The skill's value to the band does not appear in that at all. A common
skill of enormous worth buys its holder nothing, and this is why the
question 'how useful is it' is the wrong one

**the_secrecy_that_pays_is_the_secrecy_that_loses_it** — holds

engine/craft.py needs 5 holders or a skill is lost in a few
generations. Its holder wants 1. Going alone is 5x the power and 12x
shorter a life for the skill -- 6.6 generations against 81. Neither
party is being unreasonable: the specialist's horizon is ONE LIFE and
the skill's survival is measured in generations, so the individual
optimum and the collective optimum are different numbers for the same
k. Lost crafts do not need a catastrophe. They need someone who
profited by not teaching

**inheritance_costs_two_and_a_half_sigma_of_competence** — holds

under selection the holder is the best of 28, the expected max of 28
draws = sqrt(2 ln 28) = 2.58 sigma. Under inheritance the holder is
whoever was born, and ability regresses by 0.5 a generation while a
written claim regresses by nothing: g1 1.29s; g2 0.65s; g5 0.08s; g10
0.00s. By the fifth generation the holding is 32x what the ability
warrants and the heir is 0.08 sigma -- indistinguishable from anyone.
Bad kings are two heritabilities, not bad character

**a_good_king_is_a_tail_probability_with_a_number** — holds

it is not impossible for an heir to deserve it, it is a tail: the heir
is drawn with mean 0.5^g x 2.58 and sd sqrt(1-h^2g), so P(heir >=
founder) is g1 1 in 15; g3 1 in 88; g5 1 in 162; g10 1 in 202. That is
the randomization -- a good king happens at the rate chance allows and
no faster, and the rate is computable rather than chosen. Anything
drawing from this should draw from THIS, not from a knob

### engine/multiverse.py

Every universe that could hold a human, and why the rest cannot.

**gravity_is_what_varies_and_it_reaches_far** — holds

a 0.1-Earth world pulls 3.4 m/s2 and lets a tree reach 588 m; a
10-Earth world pulls 28.3 and caps it at 71. Same sap, same cavitation
pressure, 8.3x the height -- because rho g h is the only thing between
them. Gravity is what varies between worlds and it reaches all the way
to whether a forest is possible

**a_refusal_is_a_measurement_not_a_verdict** — holds

a world with three of six elements and 0.2 Gyr in the band fails 3
gates, and the first reads 'CHNOPS present: 3 elements against 6 --
missing ['N', 'P', 'S']'. Not 'uninhabitable'. Which quantity, against
which, by how much. A universe missing bone strength by 1.1x is a
different fact from one with no carbon, and a count flattens them
together

**some_universes_carry_a_toolmaker** — holds

252 worlds on a deterministic grid, 180 passing every gate. What
refuses, and how often: heat can leave the body 72. This used to SWEEP
-- ten processes, generated seeds, 15 s for 120 worlds -- to learn
which gates bind. A gate is an inequality in orbit, mass and
temperature; only composition needs a seed and only CHNOPS reads it.
The sweep was random and partial, this is complete over the grid

**the_human_gates_do_bind_once_they_are_asked** — holds

over the whole grid, ['heat can leave the body'] refuse and NO
mechanical gate does. Heat alone refuses 1 of 6 temperatures: a bare 82
W body sheds only down to 32 C and the habitable band is a criterion
for liquid water on a PLANET. Everything crossing the body boundary is
a gate; strengths that do not vary between worlds are not

**ram_was_not_the_limit_cores_were** — holds

a budget of 8192 MB was given to make this faster and it was never what
was scarce. This check used to SWEEP 120 worlds across ten processes to
measure the memory those processes took -- it was measuring its own
instrument. 252 worlds now evaluate in one process with no allocation
worth naming, because a deterministic grid needs no workers. The cost
was never RAM and never arithmetic; it was spawning pools to sample a
space that could be enumerated

**a_narrow_sweep_asks_the_better_question** — holds

fragility used to mean regenerating universes around a seed. The
sensitive quantity is main-sequence lifetime against the window life
needs: at one solar mass it is 10.0 Gyr and it falls under 2 Gyr by
beyond +30%. On the other side, 1 of 6 surface temperatures refuse a
bare body outright. Both are closed-form -- no seed, no generator, no
pool

### engine/novelty.py

Why there is always something new and always less of it.

**the_space_grows_as_fast_as_it_is_used_up** — holds

designs are 2**s and s is log2(corpus), so the exponent and the
logarithm cancel and the space is LINEAR in population: 2.96e+06
designs at 912 people, 1.18e+08 at 36480, a factor of 40 for a factor
of 40. That is why a design space can be both used up and never used up
-- finding things removes them from it, and arriving people add to it,
and neither process wins outright

**novelty_survives_on_growth_not_on_size** — holds

a* = trials/(trials + space-per-head x growth), so the novel share of
trials is 99.7% at 0.001/yr growth, 100.0% at 0.02, and 0.032% at none.
A population that has stopped growing exhausts its design space however
LARGE it is -- size sets how many trials happen, growth sets whether
there is anywhere left to put them. That is not obvious and it is the
whole content of the steady state

**a_new_design_needs_a_team_and_the_team_grows** — holds

a design of p parts needs someone holding all p, and engine/craft.py
says a person holds about 1. So it takes a team, and the team is the
part count: 21.5 people in a village of 912, 26.8 in a network of
36480. Intricacy grows with the log of the corpus and the corpus grows
with population, so the cost of ONE new thing rises with how much is
already known. Nobody is getting worse at this

**per_head_novelty_falls_as_one_over_log_population** — holds

the multiple. 912 -> 36480 people, 40x: novelty per head falls to 0.80
and novel designs in TOTAL rise 32x. Each person invents 20% less and
the world gets 32x more, both at once. The ratio is
log2(corpus1)/log2(corpus2) = 21.5/26.8 = 0.80, NOT log2(n1)/log2(n2) =
0.65 -- the corpus is bigger than the population because literacy and
recopying multiply it, and using the population there would overstate
the fall by 19%. And note which mechanism did the work: exhaustion did
NOT. At 3244 designs per head against 0.01 trials a year, 99.7% of
trials still land on something new -- nobody is running out. The entire
decline is the TEAM: a design of p parts needs p people who between
them hold p crafts, and p is a logarithm of what is already known.
Novelty per head falls because knowing enough to add to it costs more,
not because there is less left

### engine/occurrence.py

Permission is not occurrence, and the distance is arithmetic.

**types_not_molecules_was_the_confusion** — holds

p*M = 0.481 is about molecule TYPES and had been read as molecules. Up
to 12 bases gives 22,369,620 types and p*M = 0.224, short. Up to 13
gives 89,478,484 and 0.895, which is over. One word was carrying the
whole question

**one_compartment_holds_every_short_polymer** — holds

a compartment at the closure floor (1.58 microns) holds 1.0e+10
molecules at crowded concentration. Seeing every polymer up to 14 bases
takes 7.0e+09 draws by coupon collector, so ONE compartment contains
all of them with 1x to spare

**a_single_compartment_closes** — holds

one compartment holds every polymer to 14 bases, which is p*M = 3.579
against the 0.481 closure needs. IT CLOSES. Not because catalysis is
better than measured -- it is the measured 1e-8 -- but because the
number of distinct molecules in a cell-sized volume is large and p*M
scales with it

**the_gap_does_not_close_narrowly** — holds

an ocean is 8.13e+34 compartments at that size, and each one closes, so
the expected count is 8.13e+34. THE GAP DOES NOT CLOSE NARROWLY.
engine/lineage.py marked this link MISSING because a gate says yes or
no and occurrence needs a rate; the rate was three numbers already
derived and never multiplied

**what_this_does_not_say** — holds

a closed reaction network is chemistry that sustains itself. It is NOT
heredity -- nothing here copies a sequence forward. It is NOT a
boundary that divides, so no lineage. And it is NOT descent, so nothing
selects. Three further things, none derived here, and calling this 'a
cell' would be the same error as calling an open gate an occurrence.
What closed is the first of four, and the other three are now the named
gap

### engine/ontogeny.py

Child to adult, and who actually pays.

**an_infant_cannot_feed_its_own_head** — holds

a newborn's 380 g brain is 109% of everything a 3.5 kg body can make --
over one hundred, so it is not tight, it is impossible. The adult sits
at 21%. Provisioning is therefore a PRECONDITION and not an advantage,
the same shape as insulation in engine/ancestry.py, which also never
balances at any size

**growth_stops_where_the_brain_is_dearest** — holds

body growth bottoms out at age 5 at 1.50 kg/yr, down from 8.0 in the
first half year, and the brain is still taking 71% of the budget right
there. Two curves were entered separately and the minimum of one lands
in the expensive phase of the other. The child does not shrink an organ
to afford its head -- IT STOPS GROWING

**the_provisioning_debt_is_a_number** — holds

9,294 MJ of brain above an ape's share, birth to eighteen -- 3.0
adult-years of a forager's whole surplus, per child. That is what
somebody else has to hand over. engine/human.py tried to find this
inside one adult body by shrinking the gut; it was never in there

**a_child_is_built_from_what_it_eats** — holds

birth to adult is 60.5 kg of body and 0.97 kg of brain, every atom of
it drawn from a pool and the pool still balancing. The food does not
merely fuel the child, IT IS THE CHILD -- which is the thing a
watts-only account could not say

**a_brain_is_not_made_of_plankton** — holds

a 1.35 kg brain is C 0.88 kg, P 0.057 kg and the rest. Per kilo it
holds 4.9 times the phosphorus of Redfield tissue, because it is built
of phospholipid rather than protein. Wood got cellulose and a brain
gets this; no recipe here is a default anyone can fall into

**tools_can_be_priced_and_cannot_be_produced** — holds

SEARCHED, not assumed. 20 combinations of brain size and intake gain;
16 of them pay, the cheapest at a 18% gain on a 0.40 kg brain. So a
tool is AFFORDABLE across most of the space. Zero were MADE. Nothing in
this repository generates a tool, a technique or any other piece of
architecture -- engine/descent.py found the same hole for pumps, skins
and skeletons, which can all be priced and none produced. That is one
absence, not two, and it is now met from a second direction

### engine/origin.py

What a lab can say about the origin of life without inventing biology.

**copying_is_cheap** — holds

Landauer puts one bit at 0.0179 eV, so a 580,000-base genome costs
3.33e-15 J to copy. A real bacterium spends about 1e-11 J, 3,003 times
more. Energy is not what stops anything

**a_gradient_pays_for_it_easily** — holds

a three-unit pH gradient pays 0.179 eV per proton, so 116,398 protons
cover a whole minimal genome. A hydrothermal system moves that in
moments -- the bill is not the problem and saying so rules out a whole
class of explanation

**search_has_a_length_ceiling** — holds

with an ocean of 8.1e+44 molecules each trying a sequence every
picosecond for the age of the universe, chance reaches 57 residues and
no further. Below that, exhaustive search needs no explanation; above
it, something must build long chains WITHOUT trying them, which is
Levinthal's answer one level up

**the_ceiling_is_sharp** — holds

at 57 residues the search takes 5.6e+09 years and at 67 it takes
5.8e+22 -- 1e+13 times longer for ten more. Twenty to the power of n
does not bend, so the ceiling is a cliff and a mechanism either clears
it or does not

**this_does_not_claim_abiogenesis** — holds

what this shows is a constraint, not an origin. It says energy is not
the barrier and that chance stops at about 57 residues, so the missing
mechanism must reach longer sequences without searching -- selection on
intermediates, or assembly from parts already found. NAMING THE SHAPE
OF A MECHANISM IS NOT DERIVING IT, and this repository still does not
derive abiogenesis

### engine/planetlab.py

One planet, start to land creatures, fast. Provisional rules allowed.

**the_planet_chain_runs_fast** — holds

seed to land creature in 0.05 seconds over 14 steps. The full suite is
minutes and almost none of it is about making a planet

**it_reaches_land_creatures** — holds

every step from a four-number seed to a land animal opens: 14 of 14.
Given a pump, a skin and a skeleton -- which this repository can price
but not produce -- nothing in the physics forbids the outcome

**provisional_rules_are_listed_not_hidden** — holds

0 provisional rules in use. The list is the audit -- nothing marked
PROVISIONAL may be cited as a result, and eval/claims.py is not told
about any of it. The point is to find which rules are load-bearing
before spending effort deriving them

**the_root_runs_from_a_seed_to_a_residue** — holds

7 linked stages from a universe hash to a protein residue: seed ->
stellar_c -> stellar_c -> abundance -> valence -> residue -> fold.
engine/provenance.py already hash-linked the atomic part so it can be
checked rather than believed; this reads the existing records upward
through valence, formula and hydrophobicity. Nothing new is computed,
which is what makes it a root

### engine/polytrope.py

Solving the Lane-Emden equation, so one asserted constant stops being
asserted.

**closed_forms** — holds

closed forms verified by substitution, then compared to the integrator:
n=0 residual 0.0e+00, xi_1 agrees to 2.2e-12, omega to 7.0e-12; n=1
residual 4.1e-11, xi_1 agrees to 3.3e-12, omega to 9.8e-12

**step_independent** — holds

halving the step moves xi_1 by 1.4e-10 and omega by 8.6e-11 -- the
answer is about the equation, not the integrator

**reproduces_the_assertion** — holds

derived 3.09797 against the 3.0984 that was asserted, 1.38e-04 apart --
the table value was right and is now unnecessary

**chandrasekhar_still_right** — holds

the Chandrasekhar mass built on the DERIVED constant is 1.4353 solar
masses, against an accepted 1.4

**omega_is_exercised** — holds

the Lane-Emden n=3 mass integral is 2.01824, a number this module could
produce and nothing asked for

### engine/potential.py

An intermolecular potential from molecular properties, and what it
predicts.

**well_depth_from_polarizability** — holds

well depths from polarizability and ionisation energy, both measured on
a molecule in a laboratory: CO2 180 against 195; N2 44 against 95; H2O
167 against 356 K. Nothing was fitted to a gas viscosity, let alone to
a planet

**nothing_here_reads_a_planet** — holds

imports are __future__, ast, engine.constants, functools, math,
pathlib, sys -- no planet, no atmosphere, no climate. The prediction
below was made before it was compared to anything

**duration_is_integrated_not_estimated** — holds

integrating the trajectory gives 4.724e-13 s where diameter over speed
gives 3.978e-13 -- 1.19 times longer, because the pair crawls near the
turning point where its kinetic energy has gone into the field

**the_prediction_misses_and_that_settles_it** — holds

the potential predicts 11.2 cm^-1 and Venus needs between 29 and 96 --
a miss by a factor of 2.6 to 8.5 on the cold side. The guess was made
from rules and checked afterwards, and it FAILED, which closes the
question instead of leaving it open: widening wings are not what makes
Venus hot

**a_hotter_collision_is_a_shorter_one** — holds

the cutoff runs 4.2 cm^-1 at 200 K to 14.6 at 1000 K: faster molecules
are in contact for less time, so the impact approximation survives
further from line centre. The temperature dependence is a consequence
of the trajectory, not a parameter

### engine/pov.py

What it looks like from in there.

**the_image_comes_from_the_rules** — holds

pov.png is written from stdlib alone -- PNG is a zlib stream and four
headers. Acuity comes from engine/senses.py, the fovea and the naming
range from engine/recognize.py, the falloff from cone density. The
picture is a CLAIM and can be wrong, which is the only reason it is
worth drawing

**the_sharp_patch_is_drawn_to_scale** — holds

the red box is 2 degrees of 120 -- 17 px across in a 1000 px frame,
0.06% of it. Everything outside is drawn at the resolution the eye has
there

**acuity_blurs_it_does_not_grey_it** — holds

blur radius goes from 0.1 px at the centre to 1.6 px at 50 degrees out,
a factor of 23. The first version faded the edges to GREY, which is not
what an eye does -- acuity does not desaturate, it leaves things
UNRESOLVED, and those are different pictures

**distance_decides_what_is_named** — holds

the same 1.7 m person is NAMED at 19 m and only a shape at 400 m,
because engine/recognize.py puts the limit at 289 m. An earlier scene
placed the far one at 240 m and this check failed, correctly: 240 is
inside 289, so they were nameable and I had assumed otherwise

### engine/power.py

Who holds what, and why nobody could hold anything before.

**a_forager_cannot_be_rich_and_it_is_not_about_virtue** — holds

engine/group.py already ran this and got a flat answer:
strength_share(28) = 0.0357 = 1/28, and spare_per_head is zero to
1.1e-14 J at 3, 10 and 28 -- float noise on a difference of gigajoule
terms, not a crumb. Nothing is over. A forager is not egalitarian by
disposition, they are egalitarian because a carcass is worthless in a
week and there is no second helping to withhold. Power needs a surplus
AND somewhere to keep it, and engine/accident.py's grain harvest is the
first thing on this chain that is both

**a_store_is_a_point_and_a_range_is_an_area** — holds

a band of 28 eats 65 km2 of country -- 116 W each against 0.5 W/m2 of
production at an edible fraction of 1e-04 -- and its border is 28.6 km.
A granary's border is 31 m. 909x. You cannot own a range and you can
stand in the door of a barn. That is why wealth appears when people
stop moving, and it is geometry, not a change of heart

**power_is_shared_wider_than_anyone_holding_it_wants** — holds

strength is headcount, so a holder needs enough backing to match
everyone they exclude: g >= (28-1)/2, which is 15 people in on it and
13 out. Each insider commands 7% against an equal 4% -- 1.9x, and no
more. The first concentration is not a chief with everything, it is
half the band with slightly more, because the arithmetic will not carry
a chief yet

**a_wall_concentrates_power_and_was_built_for_warmth** — holds

engine/disease.py built the wall for 526 MJ a year of thermoregulation
and the separation came free. It is not free here. One defender behind
it matches 3, so the backing needed drops from 15 to 8 and each
insider's share goes 1.9x -> 3.5x. The building that was worth 53 days
of food for being warm turns out to decide who eats. Nobody chose that
when they built it, which is the point -- it is the same shape as
cooking, adopted for one reason and kept for another

**writing_is_what_makes_a_claim_outlive_its_witnesses** — holds

spoken, a claim binds whoever heard it and dies with the last witness:
179 people, once. Written, it binds anyone who can read it, including
people not yet born -- 377 readers in each of 10 generations is 3767
bindings and still going, 21x. The multiple is not the headcount, which
literacy's food ceiling caps at 8%; it is that the denominator is a
lifetime for one and nothing for the other. A claim that outlives its
holder is what inheritance IS. A stock crosses a death; a flow cannot,
and so does a ledger

### engine/provenance.py

Where each atom goes after the prompt.

**key_is_stable_and_unique** — holds

200 atoms of one element in one chunk get 200 distinct keys; the same
atom in another universe gets a different one

**history_is_derived_not_stored** — holds

iron atom 7 of chunk 0 has a 1-step history, identical on a second
reconstruction, and nothing about it was stored between the two

**identity_survives_decay** — holds

uranium atom 0 passes through ['U', 'Pa', 'Th', 'Ac', 'Ra'] and keeps
one key throughout -- the thing that was U and is now Ra is the same
thing, which is what makes this a history

**every_step_changes_context** — holds

5 steps, 5 distinct expert sets, and no two consecutive steps share one
-- every event moves the answer context

**custody_chain_is_tamper_evident** — holds

the custody chain verifies over 5 events, and altering one is caught:
first divergence at epoch '1:decay'

**histories_outnumber_atoms** — holds

24 atoms across 8 elements produce 14 distinct expert sets between
them, from histories reconstructed on demand and stored nowhere

**uranium_series_then_overruns** — holds

WITHDRAWN: U-238's alpha Q comes out -0.024 MeV against a measured
+4.27, so the channel never opens and the walk gives U->Pa->Th->Ac->Ra
instead of U->Th->Ra->Rn->Po->Pb. The previous derivation worked
because a measured helium-4 binding was mixed into an otherwise-SEMF
Q-value, adding +5.455 MeV -- 4.5 times the alpha bar -- which
cancelled most of the formula's 5-to-11 MeV deficit on heavy alpha
steps. Right answer, wrong reason, and the reason is gone

**the_context_set_is_exercised** — holds

a single carbon atom passes through 2 distinct expert sets on its way
from a universe seed, and that count is now checked instead of merely
available

### engine/qwenaccounts.py

Answers that need Qwen AND the rest of the repo, each half checked.

**touched per token** — holds

8 steps, 3 re-executed and reproduced; two independent routes to the
sparsity; they agree to 1.71e-04

**experts against the file** — holds

4 steps, 2 re-executed and reproduced; 19,568,525,312 of 22,134,528,992
bytes = 88.4% of the file is expert weights

**subject cost** — holds

4 steps, 2 re-executed and reproduced; 5 experts, 9,502,720 bytes,
0.0486% of all expert weight

### engine/qwenmap.py

All 10,240 Qwen experts mapped into Atlas, with the layer as time.

**slot_count** — holds

256 experts x 40 time points = 10,240; the map holds exactly that many

**keys_distinct** — holds

10,240 distinct 256-bit keys for 10,240 experts

**slice_arithmetic** — holds

30,720 slice lengths re-derived from shape and quantization alone, 0
differ

**tiling** — holds

120 packed tensors, 30,600 internal boundaries, 0 gaps or overlaps

**every_time_full** — holds

all 40 time points hold 256 experts; subject classification 100%-100%
across them, so the signal is not localised to one time

**no_interpolation** — holds

asked for per-expert subjects at a time where none were exported, it
refuses rather than interpolating

### engine/qwenmatter.py

The Qwen experts as matter: elements, isotopes, compounds, materials.

**isotopes_per_element** — holds

all 256 elements have exactly 40 isotopes = 10,240 on the ladder

**every_compound_binds** — holds

146,640 of 146,640 routing events bind as compounds; cardinality 8
throughout, from the header

**time_compliance** — holds

1,173,120 constituents, every one an isotope of its own compound's time
-- no compound reaches forward to a layer not computed yet

**abundance_conserved** — holds

1,173,120 element occurrences = 146,640 compounds x 8; 256 distinct
elements, most abundant is 130 at 9,669

**materials_complete** — holds

3,666 materials, each exactly 40 compounds -- one per time, no gaps

**sequence_round_trip** — holds

40 sites, {8} elements each, alphabet 256; the sequence rebuilds its
material exactly

**refuses_impossible** — holds

5 impossible compounds refused, each naming its own rule

**occupancy** — holds

9,944 of 10,240 isotopes occupied (97.1%); 296 exist in the model and
were never routed to in this capture, and stay on the table as
unoccupied

### engine/radiative.py

Optical depth from molecules, with no planet consulted.

**no_planet_appears_in_this_file** — holds

imports parsed, not grepped: __future__, ast, engine.constants,
engine.experts, engine.potential, engine.radiative, math, pathlib,
planck, sys -- no body table, no observed temperature, no planetary
composition. Band strengths, line widths and spacings are measurements
of gas in a cell, so a law built from them is evidence ABOUT planets
rather than a restatement of three

**weak_line_limit_is_linear** — holds

doubling CO2 multiplies tau by 1.9999 only below about 1.79e-05 kg/m2
of column; above that the lines are black at the centre and it goes as
the square root. CO2 saturates at a column of MICROGRAMS per square
metre, which is why adding it to an atmosphere that already has some
buys so much less than the first trace did

**strong_line_limit_is_square_root** — holds

quadrupling a thick CO2 column multiplies tau by 2.0000, so tau goes as
the SQUARE ROOT of column. The exponent of 1/2 that terraform.py chose
inside a bound is here a consequence of a Lorentz line's inverse-square
wings, and no planet was asked

**pressure_broadening_increases_absorption** — holds

the same column absorbs 10.00x more at 1 bar than at 10 mbar, because
collisions widen the lines. Absorption goes as sqrt(column x PRESSURE),
and a law fitted to a pure power of column cannot represent that -- it
buries the pressure dependence in the exponent

**planck_fractions_sum_to_one** — holds

the full band integrates to 1.0000, and CO2's 15 micron band covers
26.1% of what a 288 K surface radiates -- so even an infinitely opaque
CO2 band leaves the other 74% to escape through the window

**bands_combine_in_transmittance** — holds

a CO2 column of 1e9 kg/m2 -- opaque past any doubt -- gives tau=0.454,
not infinity, because 67% of the spectrum is left open between its
bands. Averaging depths instead of transmittances gave Earth tau=230
and a surface of 922 K

**an_opaque_band_cannot_close_the_window** — holds

raising CO2 by ten orders of magnitude moves tau by 0.1638, because 67%
of a 288 K body's radiation comes out at wavelengths CO2 does not
absorb. One gas cannot close a sky it does not reach, and this is why
CO2 alone cannot make a Venus

**continuum_is_quadratic_in_density** — holds

doubling the density multiplies the continuum by 4.000, because two
molecules must meet and the chance of that goes as n squared. At a CO2
partial pressure of 43 Pa it is 8.81e-10 and at 89 bar it is 16.6 --
1.9e+10 times larger, from the exponent alone. Nothing decides when the
continuum switches on

**compiled_and_python_paths_agree** — holds

the compiled and Python Planck integrators agree to 1.0e-15 over 9
band-and-temperature combinations. The Python one is kept as a second
implementation, not as dead code -- a disagreement between them would
be a finding

**bands_widen_under_pressure** — holds

CO2's 15 micron band blacks out 250 cm^-1 at Earth-like column and
pressure -- its nominal 250 -- and 331 cm^-1 at a hundred bars. The
wings go as gamma/dnu^2, so with enough gas even a far wing is opaque,
and the opaque width grows as sqrt(column x pressure) far -- but only
out to where a collision's finite duration stops the impact
approximation working, at 11.2 cm^-1, past which real wings fall faster
than Lorentz. Unbounded, the same rule claimed 315,694 cm^-1, which is
79 times the whole thermal infrared

**no_numerical_ceiling_on_opacity** — holds

optical depth can reach 708, set by the smallest positive float rather
than by a chosen constant. The most opaque atmosphere in the table
needs 147.6. A 1e-12 clamp used to cap it at 27.6, below what Venus is.
It was not binding at the shipped wing cutoff, where tau is 0.382 --
but it silently capped the unbounded-wing branch, which is why a scan
of that branch saturated at -278 K and looked like physics

### engine/rank.py

When rank has a price, and what the price is.

**the_absence_was_in_the_scenarios** — holds

engine/civ.py and engine/empire.py both reported that nothing prices
rank. Every group they priced had a surplus -- 2 adults with 1 child
keep 143 W spare -- and where there is enough for everyone the order of
serving does not matter. The absence was in the SCENARIOS, not in the
rules

**rank_is_an_allocation_rule_not_a_preference** — holds

rank is not a preference somebody has. It is an ALLOCATION RULE, and an
allocation rule has no work to do until there is a shortfall. That is
why asking 'what makes people want status' found nothing: the question
was about wanting, and the answer is about who does not eat

**the_carrying_number_is_derived** — holds

a forager nets 97 W and a child costs 51 W of provisioning and body, so
N adults carry 1.9N children: 3.8 for two, 5.7 for three. Nothing was
chosen -- both numbers come from engine/civ.py and engine/ontogeny.py

**the_price_is_discontinuous_and_is_a_life** — holds

for two adults the price of rank is zero at 3 family sizes and 82 W at
4 children. IT IS DISCONTINUOUS. Below the carrying number rank is
worth nothing; above it, what the low-ranked person loses is not a
share of the shortfall, it is their whole metabolism. The step appears
exactly at the carrying number and nowhere else

**what_this_still_does_not_say** — holds

this prices rank and does not produce one. It says a group above its
carrying number must have an allocation rule and that the rule is worth
a life to be high in -- it does not say which rule, any more than
engine/frozen.py says which code mapping. And it says nothing about
regard, which is what the word status usually means: what is derived is
who eats, not who is admired, and whether those are the same thing is
not a question these rules can reach

### engine/reach.py

Why a pressure is not yet a necessity, with the size of the gap.

**the_rule_is_written_and_evaluated** — holds

the rule selection already implies: a trait under pressure moves by
response = s*sigma^2 per generation, so a step is taken when variation
carries the trait across the distance in the time available. With sigma
= 0.15 from engine/descent.py and a strong ordinary pressure, the
slowest of the seven takes 6 years

**it_is_wrong_by_eight_orders** — holds

the record puts eukaryote at 2.00e+09 years and the rule predicts 3.
That is 9 ORDERS OF MAGNITUDE. Every one of the seven is out by between
7 and 9

**wrong_in_the_informative_direction** — holds

and it is wrong in the INFORMATIVE direction. A rule that predicted
these steps were too slow would mean the pressure was too weak or the
variation too small, and either could be patched with a number. It
predicts they are INSTANT. Nothing about selection is missing;
something about the steps is

**so_the_steps_are_not_distances_in_a_trait** — holds

a continuous trait under constant pressure really does move that fast
-- 1,023 generations to change size tenfold is not an error. What
separates LUCA from a eukaryote is not a bigger LUCA. It is a membrane
inside a membrane, and no amount of incremental size change reaches it.
THE SEVEN LINKS ARE NOT DISTANCES IN A TRAIT, they are discrete
innovations, and nothing in this repository produces one

**they_stay_forced_and_now_the_gap_has_a_size** — holds

the seven stay FORCED. Writing the rule did not close the gap, it
MEASURED it: at least 7 orders of magnitude between what selection on a
continuous trait would take and what the record shows. That is a better
position than before, when the gap was 'no rule produces this' with no
number attached, and it names what is absent -- a mechanism that makes
a discrete innovation, which engine/descent.py could not find for
pumps, skins or skeletons either

### engine/recognize.py

Watching it recognise something, and why that cannot be a search.

**the_sharp_part_is_almost_none_of_it** — holds

at 1.01 arcmin the whole field holds 5.07e+07 resolvable cells and the
sharp patch 1.41e+04 -- 0.028% of it. Almost everything an animal can
see, it cannot see WELL, at any instant

**recognition_cannot_be_a_search** — holds

foveating the field takes 900 s at 4 saccades a second, which is
fifteen minutes, and nobody spends fifteen minutes recognising a tree.
So the periphery has to choose where the fovea goes BEFORE anything is
identified -- the answer is partly committed before the evidence is in.
That is not a theory of brains, it is what is left when exhaustive
search is priced

**it_is_a_reduction_of_ten_million_to_one** — holds

a retina delivers 1e7 bit/s. 'Is it food' is 1 bit, a 1.0e+07-fold
reduction; naming one of thirty thousand words is 14.9 bits, still
6.7e+05-fold. Everything between those numbers is discarded on purpose,
every second, and engine/learning.py says discarding is free

**the_range_falls_out_of_the_acuity** — holds

naming a thing needs about 20 cells across it, so a 1.7 m person is
nameable to 289 m, a 10 cm fruit to 17 m and a 5 mm insect to 0.8 m.
One acuity number sets all three, and the foraging range and the social
range are the same measurement wearing different clothes

**two_routes_reach_the_same_filter** — holds

engine/learning.py concluded a brain is a filter because its store
fills in 1.49 years. This concludes it because the sharp patch would
take 900 s to sweep. THE ARGUMENTS SHARE NOTHING -- one is capacity
over a lifetime, the other geometry within a second, and neither module
reads the other's numbers to reach it. Two routes to one answer is the
strongest thing available here short of a measurement

### engine/regard.py

What prices regard: the contest you do not have to hold again.

**who_eats_is_who_can_take** — holds

allocation is the trophic rule applied inside a level: who eats is who
can take. And taking was already derived -- 450 N from 60 cm2 of
muscle, 2.50 m of reach with a haft against 0.75 bare. The same two
quantities engine/tools.py used to settle a predator settle this, and
nothing new was needed to say who wins

**but_the_loser_is_not_eaten_and_that_is_the_difference** — holds

but it is NOT the same rule. Between species the loser is eaten and 10%
of the energy transfers -- that is what a trophic level is. Within one
species the loser is not eaten and NOTHING TRANSFERS. The contest
produces no energy at all, and that difference is where regard comes
from

**a_contest_produces_nothing_and_costs_both** — holds

a real fight costs 4.2 MJ and a 10% chance of 5.2 GJ of life, and
allocation must be settled about 7,300 times over twenty years.
Fighting each one costs 37.8 TJ, which is unaffordable by orders of
magnitude

**regard_is_the_contest_not_held_again** — holds

remembering the outcome is free: engine/learning.py puts erasing an
ENTIRE brain at 1.4e-06 J, against 3.8e+13 J of fighting every decision
-- a ratio of 2.7e+19. REGARD IS THE MEMORY OF A SETTLED CONTEST, and
what it is worth is every contest it prevents. That is why rank looks
like a social fact and prices out as a physical one

**what_this_still_does_not_say** — holds

what is still not derived is which contests are ever held. This says a
settled order is worth enormously more than fighting, and it does not
say how the first order is set or when it is re-opened -- the same
shape as engine/frozen.py, which says a code is locked and is blind to
which one. Something selects HAVING a rank order and is indifferent to
WHO is where, so rank is arbitrary in the way the genetic code is
arbitrary

### engine/remnants.py

What a star leaves behind, and what it throws off, both recorded.

**chandrasekhar** — holds

1.435 solar masses derived from hbar, c, G, m_H; accepted 1.4, so the
derivation is 2.5% out

**classification** — holds

4 remnants classified: ['black_hole', 'neutron_star', 'white_dwarf']

**refuses_the_unknown_band** — holds

3 remnants inside the observational band 2.08-2.3 refused; either side
of it decided. The asserted 2.2-2.9 is superseded and kept only as a
fallback

**progenitor_rule** — holds

birth mass decides it through the core and the two degeneracy limits:
1->white, 2->white, 5->white, 8->white, 10->neutron, 15->neutron,
20->neutron, 25->black, 40->black, 80->black

**composition_matters** — holds

a 5.0 solar-mass remnant is a black_hole at mu_e=2 and a white_dwarf at
mu_e=1 -- M_Ch is 1.44 against 5.74. Same universe, and the composition
decides it

**scaling_exponents** — holds

measured by doubling each constant: hbar +1.5, c +1.5, G -1.5, mu_e
-2.0 -- the analytic exponents, re-measured not asserted

**other_universes** — holds

ours M_Ch=1.435; strong gravity M_Ch=0.063; weak gravity M_Ch=32.481;
large hbar M_Ch=11.484; and in weak gravity a 5 solar-mass remnant is a
white dwarf, which in ours is a black hole

**every_death_recorded** — holds

12 stellar deaths, every one carrying a remnant kind ['black_hole'] and
12 carrying an ejecta breakdown

**ejecta_conserved** — holds

12 events: remnant + ejecta = progenitor in every one, and the
per-element masses sum to the ejected mass (88.50 solar masses total)

### engine/revolution.py

Sixty million people, handed the machines, run forward.

**it_runs_and_the_population_moves** — holds

60M in year 0 to 13.89 billion by year 400, with energy per person
going 120 W to 119 W. Nothing in the loop says how big it gets -- each
year comes out of rules derived elsewhere

**they_were_not_making_engines** — holds

THEY WERE NOT MAKING ENGINES. An earlier version raised efficiency 1.2%
a year and took 450 years to reach the ceiling -- because it was told
to crawl, not because anything resisted. Efficiency is derived now:
pressure sets temperature and temperature sets Carnot, so cast iron
gives 21.4% and every-material-granted gives 54.7% AT ONCE, in year
zero, and never moves again

**giving_it_what_it_needs_moves_the_wall** — holds

the food ceiling was the wall, so the nitrogen to grow more food was
handed over. It moves the ceiling by 1.86x -- 34.3B to 63.6B -- and
that is EXACTLY the nitrogen ratio, because crop carbon is capped by
crop nitrogen at Redfield. It does not remove the wall. It moves it

**a_second_way_to_fail_changes_the_answer** — holds

before this, 'stopped by food' was the only verdict the loop COULD
return -- population grows to the ceiling and sits there, so moving the
ceiling changed the number and never the answer. Phosphorus is a stock,
not a rate, and it gives the run a second way to fail. All three now
end on PHOSPHORUS, and EVERY GIFT SHORTENS THE CLOCK: 1411 years given
nothing, 998 with nitrogen, 698 with synthetic food on top. More people
eat the constraint faster

**instructions_are_almost_free_to_hand_over** — holds

a whole trade, apprenticed over 10,000 hours at 39 bit/s, is 1.40e+09
bits -- 0.00030% of a brain. KNOWLEDGE IS ALMOST FREE TO HAND OVER: no
materials, no loss on copying, and engine/civ.py already showed the
channel carries a selection rather than a volume. So giving them the
instructions changes nothing about what binds, and that is the finding
rather than a disappointment

**infrastructure_is_a_tax_not_a_gift** — holds

every road and pipe decays and is rebuilt out of the same surplus that
feeds people, so infrastructure is not a gift, IT IS A STANDING TAX: 8%
of output forever, buying 42% more reach. Net it carries 63.6B to 69.9B
-- and SHORTENS the phosphorus clock from 998 years to 957, because the
extra people eat the constraint faster. Every gift so far has done this

**a_chosen_cap_was_hiding_the_effect** — holds

the reach multiplier used to be capped at 3.6, a number I picked, and
it was SATURATED before infrastructure was added -- so adding roads and
grids and sanitation changed nothing at all, and the cap rather than
the physics was giving the answer. The ceiling comes from the flow now:
if every watt of land photosynthesis were eaten it feeds 2,707 billion,
and at the largest run here they use 8% of it. The flow was never what
was binding

**something_stops_it_and_it_is_named** — holds

at 300 years nothing has stopped it and the run says so. By 2000 the
answer is PHOSPHORUS: rock phosphate ran out, and unlike the food
ceiling this is a stock rather than a rate -- it does not cap a
population, it ends one. An earlier version reported Carnot here, which
was true of the engines and false of the run -- and once engines
started at the ceiling it fired in year zero of everything, so it is
gone. A condition that is always true is not a finding

**the_stock_is_barely_touched** — holds

after 1200 years they have used 0.006% of the buried carbon. The coal
was never the limit at this scale, which is what engine/industry.py
said before anything was run -- and the run agreeing with the argument
is worth more than either alone

**this_is_a_run_not_an_argument** — holds

engine/industry.py priced the constraints and concluded a Roman
industrial revolution stays inside the flow. That was an argument and
it was read as a run. This is the run: same rules, plus time, and
nothing about the outcome written into the loop. It is ENACTED --
history of a world that was never anywhere -- and citable for what
these rules do and not for what happened

### engine/roots.py

Follow the root. Do not re-run the world.

**the_prefix_is_shared_not_repeated** — holds

10 questions, 126 stages between them, and only 111 were computed -- 15
came off a prefix another question had already solidified. Every
question after the first pays only for where it leaves the others

**a_solid_prefix_cannot_change_quietly** — holds

edited one frozen node and the recompute caught it: SOLID PREFIX BROKE
at biome.surface_light: frozen 0000000000000000 now fingerprints
99b18288... The past cannot be changed quietly, because every
fingerprint downstream commits to it

**a_different_universe_shares_no_prefix** — holds

move gravity in the twelfth place and the universe id goes
eede9f7bddffc659 -> 53a8cbed0dbf8220, so nothing frozen carries over. A
different world does not get to reuse this one's past, and that is not
caution -- they are not answers to the same question

**a_break_is_located_not_just_reported** — holds

rewrote one constant in engine/biome.py and 5 node fingerprints moved,
beginning at biome.PHOTOSYNTHETIC_EFFICIENCY, with 3 of 10 questions
standing on them. A suite says something failed. A root says WHICH
RULES moved and WHAT RESTS ON THEM, and the questions it leaves alone
are untouched -- nuclear and atmospheric did not flinch at a change to
photosynthesis

**following_beats_running_everything** — holds

10 questions, 6.73 ms warm against 17.3 s for the full suite on a warm
cache -- 2,571x. The suite re-establishes the past on every question.
This establishes it once, because the past does not move. Roots get
longer and deeper as modules are added and the cost stays at the tip

### engine/scales.py

Every domain has its own energy scale, and therefore its own bar.

**scales_span_orders** — holds

8.5 orders of magnitude from planetary-climate at 2.60e-02 eV to
nuclear-mass at 8.00e+06 -- a bar from one is meaningless in the other

**thermal_is_derived** — holds

kT is 0.0257 eV at 298 K and 0.0267 at 310 K, from two constants that
are exact by definition -- no measurement, no fit

**no_domain_borrows_another** — holds

4 domains have a bar and none is borrowed; the tightest nuclear one is
3.97e+07 times thermal noise, so using it on a fold would refuse every
fold there is

**folding_bar_is_a_rate_not_an_energy** — holds

folding's bar is 0.57 as a survival rate and refuses to be an energy --
43% of its exact minima move when a choice the chemistry does not
settle is made the other way

**nuclear_bars_are_measured** — holds

measured, not typed: mass 4.76 MeV, alpha 1.21 MeV, beta 1.06 MeV --
three questions about one formula, three answers

**units_never_mix** — holds

K: planetary-climate; eV: nuclear-alpha, nuclear-beta, nuclear-mass,
thermal; survival rate: protein-fold -- three kinds of claim. A
residual in MeV over many nuclides, a residual in K over two bodies,
and a rate against another model where nothing was ever measured. The
unit is what stops them being compared

**a_bar_names_its_manifestation** — holds

nuclear-mass refuses to give a bar until it is told which state: 1.850
MeV where the liquid drop applies and 6.249 where it does not, a factor
of 3.4. The shipped 4.763 was measured across both and is neither --
too loose where the formula works, far too tight where it does not.
Closed-shell against mid-shell, by contrast, now comes out 0.98: adding
shell corrections ABSORBED that manifestation, which is how you know
the rule was right

### engine/school.py

Schooling, and what understanding is actually limited by.

**a_head_holds_about_four_trades** — holds

40,000 waking hours of being taught at 39 bit/s is 5.62e+09 bits --
about 4 trades, not four thousand. A human is a small vessel and the
ceiling is the CHANNEL, not the storage: engine/learning.py already
showed the store fills in 1.49 years and the rest of a life is
discarding

**a_corpus_needs_a_population_to_exist_in** — holds

a corpus cannot exceed the people holding it times what each holds, so
knowledge needs a POPULATION to exist in. A Roman city's 30 trades need
8 specialists; today's 3,000,000 need 750,000. That is not a claim
about universities, it is division

**schooling_is_the_largest_tax_here** — holds

eighteen years out of a 50-year working life is 36% of it -- a larger
standing tax than every road, grid and aqueduct in engine/revolution.py
put together, which come to 8%. A person being schooled is not
producing, and that is the whole cost of understanding

**understanding_grows_and_then_stops** — holds

60 million people take a corpus from 31 trades to 2,997 over 3,000
years. That rate is CALIBRATED against a recorded pair -- a Roman city
at 30 trades and 1800 Europe at 3,000 -- rather than picked, which the
first version's guess was, at five orders of magnitude too small

**what_stops_it_is_population** — holds

HOLDING NEVER BINDS, and the check that said it would was wrong. At 8
billion the corpus reaches 395,677 trades of a holdable 320,000,000 --
three orders of headroom. What limits understanding is the DISCOVERY
RATE, which is proportional to people with surplus: 132x the corpus for
133x the population. So understanding is limited by population, and
population in engine/revolution.py is limited by phosphorus. The chain
closes on a mineral, but through the rate and not through the holding

**no_rule_prices_a_shared_foundation** — holds

MISSING_RULE. This says a specialist today needs 0.5 years of schooling
and the recorded figure is about 18 -- short by 38x. The reason is
visible: dividing a corpus by its specialists assumes they share
NOTHING, and real ones share an enormous common base -- language,
numeracy, how to read, what a machine is -- before any of them
specialises at all. No rule here prices a foundation every specialist
must hold, so the schooling cost is understated and the number was NOT
adjusted to hide it

### engine/senses.py

A body that can look around, and what it would take to fail.

**the_eye_sits_at_its_own_diffraction_limit** — holds

diffraction at a 3 mm pupil allows 0.77 arcmin and cone spacing samples
1.01 -- 1.31x apart, against a measured 1.00. Three routes, none told
about the others. A retina finer than the optics samples blur; optics
sharper than the retina paint detail nothing reads. Neither is wasted
on the other and nothing here arranged that

**space_is_two_eyes_and_it_runs_out** — holds

depth error goes as z^2, so 6.4 cm of baseline resolves 0.19 mm at
arm's length, 7.6 cm at ten metres, and nothing past 1320 m where the
error equals the distance. Seeing space is two eyes and a subtraction,
and where it stops is b over the disparity threshold -- not a fact
about brains

**a_hook_grip_cannot_strike** — holds

striking needs 25 N held. A thumb-opposed grip holds 40 and passes at
1.6x; a hook grip holds 12.5 and FAILS at 0.50x. engine/tools.py
assumed a hand without checking, and the hand is the reason a flake is
not a tool for most animals that could reach one

**four_limbs_on_the_ground_carry_nothing** — holds

INVERTED, kept. This first counted TOTAL limbs and had a biped with
none free, because it read 'two-legged' as 'owns two limbs'. A human
and a horse both own four. Count what touches the ground and a
quadruped has 0 free and a biped 2 -- that is the entire thing
bipedalism buys, and the earlier reading had it exactly backwards

**a_failure_names_its_mechanism** — holds

take the thumb away and the report is not 'failed'. It is: grip (hook):
FAILS: 12.5 N against 25 needed, 0.5x -- friction mu=0.5 on a 25 N grip
against a 1 kg stone reaching 5 m/s... A verdict is the least useful
part of a failure. The quantity that fell short, the one it lost to and
the factor between them is what says whether it nearly worked or is not
that kind of thing

**five_senses_reach_eight_of_thirteen** — holds

the five senses between them reach 8 of the 13 constraints that bind on
a human, and they do not overlap -- which is why there are five. Smell
is the only one that reads the PAST, since a track is a chemical record
of something gone; hearing the only one that reads round a corner;
taste the only one that acts after commitment, which is why it is wired
to disgust. Bandwidth spans 1e+02 to 1e+07 bit/s and the narrowest is
not the least useful

**the_rest_is_inferred_and_that_is_the_brain** — holds

5 constraints reach NO sense: ['allocation', 'fidelity', 'oxygen to
tissue', 'provisioning', 'solvent']. Provisioning is eighteen years
ahead and allocation is a fact about other people -- neither has a
signal to detect, so both must be MODELLED. That is 38% of what binds
on a human against 33% on a bacterium, and it is what a brain adds over
a sense organ. Senses bound comprehension from below; inference is the
rest

### engine/shells.py

Magic numbers derived, not typed, and the shell correction they give.

**magic_numbers_are_derived** — holds

all seven observed closures fall out of a potential with two couplings:
[2, 8, 20, 28, 40, 50, 82, 126]. Nothing in this file contains the list
-- it is where the single-particle gaps land

**oscillator_alone_is_not_enough** — holds

with both couplings off the oscillator gives [2, 4, 8, 10, 20, 40, 70,
112] -- 2, 8 and 20 right and then 40, 70, 112, which are not closures.
Every magic number above 20 needs the spin-orbit term, so they are
evidence FOR it

**the_coupling_is_constrained_by_the_closures** — holds

only 4.2% of the (kappa, mu) plane reproduces all seven closures: kappa
0.028-0.045, mu 0.28-0.75. Seven integers pinning two continuous
parameters into 4% of the plane, and the Nilsson model's own values sit
inside it

**it_predicts_a_closure_nobody_asked_for** — holds

it also predicts 40, which was not in the target list and is real --
zirconium-90 and calcium-48 both show the N=40 sub-shell closure. A
derivation that produced only what it was aimed at would be weaker than
one that produces that and something else true

**shell_term_peaks_at_closed_shells** — holds

lead-208, Z=82 and N=126 both closed, gains -0.00 MeV while Z=75 N=115
next door gains -8.96. The term peaks where the shells close because
that is where the real level density falls furthest short of a smooth
Fermi gas

**binding_improves_where_the_gap_was** — holds

mean absolute error over 17 nuclides falls from 0.1383 to 0.1351 MeV
per nucleon, a 2% improvement from ONE measured coefficient on a shape
that was derived

**the_liquid_drop_knows_where_it_ends** — holds

the formula is refused below A=13, derived by asking where it exceeds
its OWN measured mass bar rather than by asserting a floor. Helium-4 is
out by 5.46 MeV and carbon-12 by 6.95; both are alpha-clustered. Every
alpha Q-value needs helium-4, so alpha decay is not derivable here and
is refused

**curvature_was_tested_and_rejected** — holds

a missing curvature term would make this ratio constant; it runs -3.44
to +2.10 and changes sign, so light nuclei are under-bound and heavy
ones over-bound and one term cannot do both. Hypothesis discarded, not
fitted

**the_one_measured_number_is_exercised** — holds

the single fitted number here is -4.6955 and it is NEGATIVE -- a
deficit, not a scale, whatever its name says. Wiring it was how that
surfaced: nothing had called it, so nothing had ever had to know its
sign. He-4 also gets told why it is out of domain

### engine/shelter.py

When a shelter pays, and what makes one a home.

**worn_insulation_runs_out** — holds

a 82 W body over 1.8 m2 balances only 4.6 K below core bare, so naked
it is stranded above 32 C -- a tropical animal by arithmetic. Every
worn layer helps and they run out at 19 C

**cold_is_construction_not_hardiness** — holds

at -10 C, worn insulation bottoms out at 19 C and the air is -10 C. A
brush shelter reaches -14 C and an earth lodge -64 C. Everything below
about 19 C is not endurance or hardiness, IT IS CONSTRUCTION, and the
line between them is a subtraction

**a_home_is_tenure_not_architecture** — holds

brush shelter pays back in 4.6 nights and was kept 30. One night is a
loss; thirty is the best return available. The STRUCTURE IS IDENTICAL
-- nothing about it changed. So the difference between a shelter and a
home is not architecture, it is tenure, and tenure has a threshold at
4.6 nights. That also says a home cannot appear in a lineage that does
not stay put, whatever it is able to build

**this_extends_a_rule_it_does_not_contradict_it** — holds

engine/ancestry.py was CALLED, not quoted: can_stay_warm(70 kg, bare)
returns False. It made insulation a precondition at 288 K. This agrees
and says why: bare balances only down to 32 C, which is above 15 C, so
at the temperature it tested the answer had to be no. The new rule
EXTENDS the old one past worn insulation instead of overturning it, and
if it had disagreed at 288 K this check would have said so

**the_world_filter_is_exercised** — holds

of two worlds carrying people, 50% sit beyond 1 AU and get less light,
so construction is not optional there. The rule existed with no caller

### engine/signal.py

Communication, and why it appears long before language.

**a_signal_is_a_contest_not_held** — holds

engine/group.py found each member must settle rank about log n times --
seven at a band of 144 -- and engine/regard.py prices one fight at 5.2
GJ, so seven is most of a lifetime's risk. A SIGNAL IS A CONTEST NOT
HELD, exactly as regard is a contest not repeated. Not a courtesy and
not a precursor of language -- the cheapest way to settle something
that has to be settled

**it_works_when_the_asymmetry_is_visible** — holds

reach and force are visible before contact: 600 N against 300 N settles
without a blow, and so does 1.75 m of haft against a bare arm. An even
match does not -- there is nothing to read, so it has to be fought. The
signal carries information only where information exists

**display_is_millions_of_times_cheaper** — holds

a fight is 5.2 GJ and a display 970 J, a factor of 5.3e+06. That ratio
is why signalling is everywhere an organism has rank to settle, which
is everywhere there is a group -- long before anything language-shaped

**capacity_scales_with_what_must_be_distinguished** — holds

a signal separates the situations its sender needs separated, and
engine/comprehension.py counts those as 2^constraints -- so the bits
needed are one per constraint: bacterium 6, bee 8, mouse 10, human 13.
COMMUNICATION GROWS WITH UNDERSTANDING rather than alongside it,
because what must be said is what must be told apart

**and_it_is_what_lets_a_group_be_large** — holds

engine/group.py got an optimum of 3 -- a family, not a band -- because
it charged every rank contest as a fight. With nine in ten settled by
display the affordable group is 28. Signalling is not a refinement on
group living, IT IS WHAT MAKES A GROUP BIGGER THAN A FAMILY POSSIBLE

### engine/signature.py

Fewer rules, grown further, and a sign of life that is not a guess.

**earth_reads_as_driven** — holds

CH4 at 1.80e-06 and O2 at 2.10e-01 together: methane burns in oxygen by
148 ORDERS, and holding them apart costs 9.47e+11 kg/yr. Not the
impossibility alone -- the BILL. Something is paying it, and that is an
accounting identity rather than a claim about biology

**a_dead_world_does_not** — holds

Venus reads undriven -- no oxidant. Mars reads undriven too, and it
took three attempts. Orders from equilibrium called it driven. A flux
rule narrowed the gap to 23x and still called it driven. Deriving the
lifetime properly from hydroxyl chemistry made it WORSE, because dry
air gives CO a 21-year life and a bigger bill. Magnitude was never the
question: CO and O2 are 128 orders apart and it does not matter: CO2
photolysis accounts for both: CO2 + photon -> CO +

**one_gas_alone_is_not_a_signature** — holds

oxygen alone is not a signature -- a photodissociating ocean makes it.
Methane alone is not -- serpentinising rock makes it. Only the PAIR is,
because only the pair is impossible, and this returns nothing for
either on its own

**the_rule_is_not_fitted_to_mars** — holds

the co-production rule was motivated by Mars, so it has to answer pairs
it was not built for. Hydrogen beside oxygen is quiet -- water
photolysis makes both. Hydrogen beside methane is quiet --
serpentinising rock makes both. Both are real astrobiological false
positives and neither was tuned. Methane beside oxygen stays driven,
because no reaction has those two among its products at any ratio

**it_says_driven_not_alive** — holds

the output is 'no known process accounts for this' and a bill, not
'life'. An unknown geology could still write the invoice, and the rule
can only check reactions it has been given -- its blind spot is exactly
the chemistry nobody has thought of. What it buys is that it is
observable across interstellar distance from a spectrum, which nothing
else concluded here is

### engine/template.py

The reaction that copies a sequence was already in the network.

**the_template_is_the_catalyst** — holds

a ligation a + b -> ab is templated when the complement of ab is
present, and the thing that makes it happen is that strand: THE
TEMPLATE IS THE CATALYST. It is not a new reaction type -- it is the
ligation already in the network with its catalyst named rather than
drawn at 1e-08, and base pairing is why engine/cold.py could price the
fidelity at all

**every_ligation_has_one_available** — holds

25,488 of 25,488 ligations have their product's complement available --
ALL of them. A complete polymer set is closed under complementation, so
the catalyst a copy needs is never the missing one. The instruction was
to look at every reaction until one copies a sequence; every one of
them does

**it_selects_the_join_it_does_not_permit_it** — holds

a template of ABCD admits C+DAB, CD+AB, CDA+B and refuses AB+CD. It
does not PERMIT a join, it SELECTS which join, and the product's
sequence is the template's read off. That is the difference between
chemistry that sustains itself and chemistry that says something

**two_rounds_return_the_original** — holds

comp(comp(s)) is s exactly, so a strand makes its complement and the
complement makes the strand. Two rounds and the sequence is back, which
is replication and not merely production

**the_sequence_is_what_is_carried** — holds

at 259 K the copy error is 1 in 200 and a 200-base strand holds against
it, which is 400 bits carried forward. engine/heredity.py passed on
WHICH molecules were present; this passes on what one of them SAYS, and
the two numbers -- the fidelity and the length -- come from the same dG
that set the temperature window

**what_this_still_does_not_say** — holds

what is still absent is not the copying. It is that nothing here says
what a sequence is FOR: no strand codes for a catalyst, so a copied
sequence is carried and never read. Template replication gives heredity
of sequence and translation would give heredity of FUNCTION, and that
is a further thing. The gap has moved again and it is smaller and it is
still a gap

### engine/terraform.py

A planet that changes itself. No agent, no terraformer, no choices.

**stefan_boltzmann_derived** — holds

sigma = 2 pi^5 k^4 / 15 h^3 c^2 = 5.6703744e-08 W m^-2 K^-4, agreeing
with the published value to 3.3e-11 -- built from h, c and k, which are
exact by definition, so this is a derivation and not a lookup

**gas_constant_derived** — holds

R = k N_A = 8.314462618 J/mol/K, exact because both factors are

**equilibrium_T_against_observation** — holds

bare rock, no atmosphere: Venus 227K vs 737K, Earth 254K vs 288K, Mars
210K vs 210K

**airless_body_has_no_greenhouse** — holds

Mercury is refused: the surface radiates its heat away in 1.45e-15 of a
rotation, so each face sits at its own temperature and this body doe...
3.1.19 scored it at +2.8 K against a DAYSIDE mean of 440 K while
predicting a redistributed global mean. The real global figure is near
340 K and the model is about +97 K out. The agreement was two different
quantities meeting by chance

**titan_missed_and_names_why** — holds

Titan 84.7 K against 94 K, -9.3 K and too cold -- held out, and the
shortfall is methane and nitrogen collision absorption, neither of
which is in here

**water_exponent_bounded_by_earth_existing** — holds

Earth having stayed liquid bounds the exponent below 0.5388, so
absorption MUST saturate; at 0.5 the gain is 0.928, stable and close to
the edge, and no spectroscopy table was consulted to get there

**earth_has_two_stable_states** — holds

same sunlight, two answers: 288 K and 798 K, with an unstable ridge at
298 K between them. Which one a planet is in is history, not physics,
so the answer is the set

**weathering_efolding_from_chemistry** — holds

R T^2 / Ea with Ea measured on basalt in a beaker gives 14.37 K per
e-fold; the climate literature quotes 13.7 -- close, and derived from
chemistry rather than fitted to a planet

**thermostat_reproduces_its_calibration** — holds

outgassing=1 at 1 AU returns 42.56 Pa and 288.0 K, which is Earth --
this is the single calibration returning itself, not a prediction, and
is listed so nobody counts it as one

**faint_young_sun_resolved_by_the_loop** — holds

at 0.7 L_sun Earth with today's CO2 sits at 237 K, frozen solid; let
the loop run and CO2 climbs to 1.45e+05 Pa and 30% of the surface is
above freezing. The faint young Sun paradox, answered by the feedback
and not by an assumption

**water_is_a_property_not_a_name** — holds

a body identical to Earth but called 'probe' gets Earth's answer, and
the same body with no water runs away -- the inventory decides, not the
name. The first version keyed the ocean off body.name and every
habitable-zone probe came back a runaway

**runaway_inside_the_inner_edge** — holds

the inner edge falls at 0.999 AU -- inside it the oceans are vapour,
rain stops, the sink closes and CO2 accumulates with nothing to remove
it. Nobody put an edge in; it is where the loop stops having a solution

**nothing_acts_on_the_planet** — holds

50 functions and not one takes a target, a goal or a set point. The
planet is not being terraformed BY anything -- outgassing and
weathering are consequences, and the temperature is wherever they cross

**AU_is_a_distance_not_gold** — holds

AU = 149,597,870,700 m, exact by definition, a bare uppercase constant
here; gold is the quoted string 'Au' used as a key in the element
tables, which this module never imports. Different case, different
type, different namespace -- they cannot be confused by anything that
runs

**escape_and_ceiling_are_exercised** — holds

Earth binds N2 at lambda=829.7 and H2 at 59.7, a factor of 14 -- which
is why there is nitrogen up there and no hydrogen. The CO2 ceiling at
288 K is 1.65e+07 Pa and 1 bar offered leaves 1e+05 airborne. All three
of these were written and never called; they work, and now something
fails if they stop

### engine/thermo.py

Heat capacity from molecular shape, and the Sun's surface from its own
light.

**equipartition_gives_the_typed_values** — holds

shape plus measured band frequencies reproduce the numbers that were
typed into the climate code: N2 1039 against a typed 1040; CO2 833
against a typed 850. Three heat capacities were constants; they are
consequences now

**vibration_comes_from_the_band_data** — holds

CO2's cv/R is 2.64 at 150 K, near the 2.5 that translation and rotation
alone give, and 5.97 at 1500 K as its bending and stretching modes wake
up. The frequencies are the band centres engine/radiative.py already
uses for opacity -- one measurement, two consequences

**adiabatic_index_is_right_for_each_shape** — holds

argon comes out 1.6667 and nitrogen 1.3998 -- five thirds and seven
fifths, from counting degrees of freedom and nothing else

**the_suns_surface_is_derived_not_measured** — holds

5772 K from the Sun's luminosity and radius through Stefan-Boltzmann,
which is itself derived from h, c and k. A surface temperature is not
an independent observation of a star -- it is what its power and its
area imply, and nothing here was told it

**heat_capacity_rises_with_temperature** — holds

CO2's cp runs 735 J/kg/K at 200 K to 1167 at 800 K, a 59% change. The
climate code used one number for both, which is a 200 K planet and a
800 K planet being told they have the same gas

### engine/tools.py

A tool, produced rather than priced.

**a_body_cannot_open_a_bone** — holds

the hardest thing a body has spreads 400 N over 2e-05 m2 and reaches
2.00e+07 Pa against bone's 1.7e+08 -- short by 8x. The calories inside
a femur are unreachable to the animal that killed it. That is the
barrier, and it is a material property, not a lack of wit

**picking_up_a_rock_is_not_enough** — holds

an unworked cobble reaches 4.0e+06 Pa and still fails by 42x. A flaked
edge reaches 4.0e+08 and goes through. PICKING UP A ROCK IS NOT ENOUGH
-- the edge has to be made small, and the only variable is contact
area. That is the line between using an object and making a tool and it
is 100x of area, nothing else

**the_material_selects_itself** — holds

limestone, wood fail before bone does; flint, granite, obsidian do not.
A tool that breaks before its target is not a tool, so the rock chooses
itself out of whatever is lying there. Nobody told these rules to
prefer flint over wood, and for a DIFFERENT job -- reach -- wood wins,
because the test is never the material, it is the material against the
target

**the_intake_gain_is_derived_not_chosen** — holds

one femur a day is 70% of a forager's intake, against the 14% a human
brain costs over an ape's. It pays with 5.2x over. And this number was
NOT chosen -- engine/ontogeny.py had to be handed a gain to test
against; this one comes out of how much marrow is in a femur and how
much energy is in marrow

**no_access_means_no_calories** — holds

take the flaked edge away and the gain goes to exactly zero, not to
something smaller. The calories do not become partly available when the
bone stays shut. An earlier version multiplied marrow constants whether
or not anything could open it, which is pricing wearing the clothes of
producing

**a_spear_is_geometry** — holds

an arm reaches 0.75 m and a large predator strikes at 1.0, so bare you
are always inside its range and it is never inside yours. Haft 1.75 m
of wood and reach goes to 2.5, a 1.50 m margin, dropping predation risk
from 0.40 to 0.16. No courage, no tactics -- the whole of it is which
of two numbers is larger

**this_produces_a_tool_it_does_not_price_one** — holds

3 surface-and-material combinations open a bone and every one was
DERIVED: the force a body makes, the area it lands on, and strengths
already in engine/life.py. Nothing here was handed a tool or told one
existed. This is the first piece of architecture this repository has
produced rather than priced -- and it worked only because a tool is the
one kind that is NOT GROWN. A pump must be built by a body and
inherited. A stone is already lying there. The hole in
engine/descent.py is still open for everything that has to be built

**the_breaks_predicate_is_exercised** — holds

breaks() says False for a fist and True for a flaked edge, which is the
whole of this module in one predicate -- and nothing called it until
now

### engine/trade.py

What can be carried how far, and what that does to production.

**a_porter_eats_the_cargo_and_that_sets_the_range** — holds

a porter carries 30 kg and walks 32 km a day, burning 14 MJ against
grain at 15 MJ/kg -- so a round trip spends 0.058 kg of the load per
km. The load arrives as nothing at 516 km and has doubled in price at
258 km. Grain is not traded far because it cannot be: the cargo and the
fuel are the same substance, and that is a fact about food, not about
markets

**knowledge_is_the_only_cargo_with_no_range_limit** — holds

at 2000 km grain delivers 0 kg and pays: False. Value density sorts
everything -- salt and obsidian go where grain cannot. But technique
weighs nothing AND the carrier still has it after handing it over,
which no other cargo does. It is the only thing on this chain with no
range limit and no loss on transfer, so a region can share what it
knows long before it can share what it grows. Knowledge trade precedes
goods trade for a reason in physics

**settling_puts_neighbours_a_field_apart_not_a_migration** — holds

a village of 912 cultivates 21 km2, so settlements sit 5.2 km apart --
against the 9 km a forager band needed. Neighbours are a morning away,
not a migration, so they meet 22 times a year instead of 2, and a
discovery crosses 40 villages in 6.8 years instead of 74. The same
settling that made everyone sick made everyone 11x quicker to hear
about it

**a_network_specializes_like_a_town_nobody_built** — holds

40 villages of 912 inside a 16 km radius are 36480 people who can reach
each other. One village supports 304 specialties; the network supports
12160. And unit cost falls 0.85 per doubling of volume, so serving 40x
the market is 5.3 doublings and 2.4x the output per worker. Nobody
built a town. The specialization a city is usually credited with is
available to a region that merely keeps in touch, because the binding
quantity was never how close people stand -- it was how many the corpus
reaches

### engine/tradition.py

What one head learns and another head keeps.

**transitivity_is_the_rule_that_buys_unobserved_pairs** — holds

observe the 27 adjacent links of a chain of 28 and transitivity hands
you all 378 orderings -- 14.0 facts per fact. engine/group.py was
already spending this (28 log2 28 = 135 contests, not 378) without the
rule being written down. Transitive: ancestor of, beats, ripens before

**an_intransitive_relation_buys_nothing** — holds

the rule is not universal and the exceptions are the interesting ones.
3 relations here compose to nothing: ['beats, in three weapons', 'is
near', 'mates with']. 'beats, in three weapons' -- the classic cycle --
means a dominance order can fail to exist, and then the 378 contests
come back. An intransitive triple is worth naming when it turns up,
because it is the rule breaking, not noise

**oral_tradition_compounds_and_epigenetics_cannot** — holds

a generation adds a and keeps r, so the stock settles at a/(1-r) and
the whole question is r. Oral: an hour after dark for 18 years is 78840
tellings, and k ln k inverts to 8692 items, so r = 0.99988 and the
stock is 8688a. Epigenetic: 2-generation half-life gives r = 0.71 and
3.4a, and the telephone costs 5.6e-08 on top. That is 2545x.
Epigenetics does not compound -- it is a two-generation echo. Oral
tradition compounds, and that is the only channel that does, which is
why the accumulation is cultural

**a_discovery_settles_across_bands_not_within_one** — holds

one band waits 500 years for a one-in-500 accident. 40 bands: the first
hits at 12 years and it travels to the rest in 74 more, so everyone
holds it by year 86 -- 6x sooner than any one band could manage. Some
bands get it first; the coupon-collector tail is why the last one waits
so much longer than the median, and why it still arrives

**there_is_a_band_count_that_settles_fastest** — holds

discovery wants many bands and spread wants few, so the sum has a
floor: 16 bands settle a one-in-500 accident in 53 years, against 126
at 4 bands and 143 at 65. Too few and nobody finds it, too many and it
never gets round. The optimum is not chosen -- it falls out of 1/(bp) +
b ln b / 2 having a derivative

**the_telephone_is_what_the_band_corrects** — holds

one retelling corrupts an item with p=0.1, so a single line of
transmission loses 10% a generation and its corpus tops out at 10.0a --
a game of telephone, and nothing accumulates. 28 holders vote, a
corruption one makes the others do not, and the consensus goes wrong
with p=5.63e-08. The stock is 8688a, 870x. The band is not an audience
for the corpus, it is the error correction ON the corpus, and without
it oral tradition carries about ten things

### engine/trajectory.py

Three ladders that gate each other, first ancestor to us.

**the_habitat_ladder_is_gated_on_the_tool_ladder** — holds

3 grades are worn as found and 3 need material worked. Everything
colder than 6 C is on the far side of a tool, so THE HABITAT LADDER IS
GATED ON THE TOOL LADDER -- and the gate is not asserted here, it is
the same stress threshold engine/tools.py used for a bone

**one_threshold_decides_both** — holds

bone yields at 1.7e+08 Pa and hide and wood give way to the same
concentrated stress. A fist cannot reach it, an unworked cobble cannot,
a flaked edge can. ONE NUMBER decides whether a bone opens and whether
a shelter can be built, which is why the two ladders move together
rather than being made to

**habitat_opens_latitude_and_latitude_is_land** — holds

insolation falls as cos(lat) and Stefan-Boltzmann makes temperature
fall as its fourth root, so a body surviving 19 C reaches 27d and 45%
of land while one surviving -64 C reaches 77d and 97%. No meridional
heat transport is modelled, which understates the high latitudes and is
marked rather than corrected

**latitude_imposes_a_constraint_the_equator_does_not** — holds

obliquity moves the sub-solar point, so the swing between summer and
winter is 6.4 K at the equator and 109.3 K at 60 degrees. That imposes
seasonality: food is not available year round... -- a constraint
nothing at the equator faces, which is how a habitat hands back a rule

**so_the_loop_closes** — holds

UNDERSTANDING BUYS TOOLS, TOOLS BUY HABITAT, HABITAT IMPOSES
UNDERSTANDING. A flaked edge opens 97% of land against 45% without one;
the land it opens is seasonal; seasonality is a constraint that must be
answered; and engine/comprehension.py counts what binds, 6 on a microbe
and 13 on us. The loop is three modules written for three other
reasons, meeting at one stress threshold and one cosine

**this_does_not_produce_the_flake** — holds

this shows the ladders gate each other and does NOT produce the flake.
engine/innovation.py holds that: a step is an existing process with a
part omitted, duplicated or combined, the non-lethal variants arrive at
4.48 per division, and the share of them that are USEFUL is 1e-4 and
unmeasured. Everything here is conditional on the first edge, and the
first edge is still the thing nothing derives

### engine/transitions.py

What an atom becomes, and who can answer once it has.

**decay_is_derived** — holds

taking each element's BEST-BOUND isotope: 1 come out stable, 78
undetermined inside the error bar, and 13 decay with a determined mode
{'beta-minus': 3, 'beta-plus': 10} -- all from the sign of Q

**refuses_inside_the_error_bar** — holds

84 nuclides whose best Q lands inside the 1.2083696436986884 MeV the
mass formula is good to, refused rather than guessed -- the sign is the
answer and it is not determined there

**binding_is_computed** — holds

valence closure computes ['CH4', 'CO2', 'H2O', 'H3N'] -- water,
methane, ammonia and carbon dioxide, from lowest common multiples
rather than a table

**edges_run_forward** — holds

every transition is stamped with the later of its inputs' epochs, and
none runs before something it needs

**experts_actually_change** — holds

58 of 58 transitions change which experts apply; e.g. Be+C -> Be2C
gains ['compound', 'formula:Be2C']

**answer_sets_exceed_atoms** — holds

22 atoms take part, and the transitions between them reach 113 distinct
expert sets -- more answer contexts than there are atoms, which is the
point of tracking the edges

**chains_terminate** — holds

U-238 followed 2 steps to undetermined: Z92 -> Z90

**scored_against_known_fates** — holds

over 14 decays whose fate is known: 8 right, 0 WRONG, 6 refused.
Nothing confidently wrong.

**the_resolution_floor_is_exercised** — holds

a 5 MeV Q is resolvable and a 0.1 keV one is not: Q=0.00 MeV against a
measured error of 1.21; smaller than the formula's own erro. The
formula's own bar decides what it is allowed to have an opinion about,
and this rule says so -- it had no caller until now

### engine/unsolved.py

What nobody knows, held on the record so the system can be checked
against it.

**abstains_on_the_unsolved** — holds

10 open problems, all 10 refused. An answer here would be a bug far
more often than a discovery, so this failing is a flag to investigate,
not a result

**bounded_where_data_bounds** — holds

the one open problem the repo touches is bounded to 2.08-2.3 by
observation and still refused inside it, while 1.98 resolves to
neutron_star. Bounded where data bounds it, refused where it does not

**our_own_gaps_listed** — holds

6 things this repo asserts and does not derive, each with what would
close it: Kleiber exponent, cosmos dilution factor, initial-final mass
relation, three decays the formula gets confidently wrong, nuclear
shell closures, the answer format of the held-out benchmark

**closed_stay_closed** — holds

1 closed: the polytrope constant is 3.09797, integrated rather than
looked up, and the Chandrasekhar mass built on it is now DERIVED

### engine/valence.py

Valence from where an element sits, not from a table of ten.

**reproduces_the_hand_table** — holds

all 10 hand-written valences reproduced from shell filling alone -- and
the capacities came from variantlife.noble_z(), written for a different
purpose, so agreement is two routes meeting

**covers_more_than_ten** — holds

50 elements have a valence against the 10 that were typed, 5x more with
nothing added by hand -- the typed ten are now a fixture, not the
source

**silicon** — holds

silicon bonds 4 ways: Z=14 has 4 outer electron(s), so it bonds 4
way(s) -- sharing them -- the element variantlife.py had to refuse for
want of a table entry

**nobles_are_zero** — holds

every closed-shell element at (2, 10, 18, 36, 54, 86) comes out zero,
independently of the noble-gas list -- both fall out of the same
capacities

**refuses_the_d_and_f_blocks** — holds

68 d- and f-block elements refused rather than assigned, because they
have several valences and the rule describes one

### engine/variantlife.py

Life with different chemistry, and what stays forced anyway.

**earth_comes_back** — holds

earth biochemistry through the general machinery: codon length 3, 64
codes, 43 spare, gated at supernova -- the same numbers biomatter.py
gets by hard-coding them

**alphabet_changes_the_code** — holds

2 bases -> 5 sites, 32 codes; 3 bases -> 3 sites, 27 codes; 4 bases ->
3 sites, 64 codes; 5 bases -> 2 sites, 25 codes; 6 bases -> 2 sites, 36
codes -- the alphabet moves the answer and the rule does not

**rule_is_the_same_everywhere** — holds

for every alphabet from 2 to 8 the code is the SHORTEST that names all
21 meanings, and one site shorter never suffices -- one rule, different
outputs

**backbone_must_chain_and_exist** — holds

chains ['C', 'N', 'P', 'S', 'Si'] gated at ['stellar_c', 'supernova'];
inert ['He', 'Ne'], refused because (2, 10, 18, 36, 54, 86) are closed
shells derived from the capacities 2-8-8-18-18-32; unknown ['Fe'],
refused for want of a valence rather than called impossible

**refuses_the_impossible** — holds

4 biochemistries refused as impossible and 1 as unjudgeable, each
naming the rule -- and the two are different answers, not one

### engine/vocabulary.py

Every rule, reachable by its own words.

**the_english_path_was_broken_and_is_fixed** — holds

engine/english.py parses that into mass(carbon) and says what it
understood. It raised ModuleNotFoundError until now, from a bare
`import responder_shim` at line 181 that resolved only when run from
inside engine/. The one mechanism here for asking in words was down,
and nothing tested it, so ninety versions of hand-written searches were
written past it

**every_rule_is_reachable_by_its_own_words** — holds

656 rules across 127 modules, indexed under 3,380 distinct terms,
against the 350 facts the Atlas 2 shim carried. The gap was never
machinery -- it was that 3.1's rules had never been given their words

**a_question_is_a_lookup_not_a_search** — holds

'how cold before copying is accurate enough' resolves to
evolve.habitability_is_a_when_not_a_where in 4 ms -- holds: 3 generated
worlds spend time inside the band's inner edge, and 1 leave i. Nothing
was searched. The words are the index and the rule's own sentence is
the answer

**nothing_in_the_index_was_written_by_hand** — holds

656 of 656 entries carry terms taken from the rule's own name and
docstring, and the answer is the sentence its check() already emitted.
No lexicon was written by hand, so a rule added tomorrow is reachable
tomorrow

**only_what_moved_is_recomputed** — holds

127 modules untouched, 0 rechecked, in 56 ms. An earlier version of
this SWEPT -- ran every check and compared 512 sentences, 180 seconds
to re-derive answers nothing could have changed. That is the mistake
eval/claims.py had already fixed with fingerprints, committed again
three files later. A rule's fingerprint commits to its whole chain, so
you do not re-verify; you fix the rule when you notice it is wrong and
only what stands on it recomputes

### engine/watch.py

Four habitable worlds, followed step by step, and what happens to them.

**habitable_worlds_can_be_followed** — holds

star 1.17 Msun, main sequence 7 Gyr | world at 1.53 AU, 12.50 Earth
masses, 6694 oceans delivered | elements: C,H,N,O,P,S

**a_window_has_a_beginning_and_an_end** — holds

the first habitable world is temperate from 0.0 to 4.8 Gyr and loses it
before the run ends. A window has a beginning and an end, and which one
a world is in is not something a census total can say

**habitable_is_not_inhabited** — holds

the census decides on ['habitable', 'has_water', 'window_gyr',
'elements'] -- water, elements and time, which describe a PLACE. It
sets no key about a membrane, replication, metabolism or division,
because nothing here derives the step from chemistry to a self-copying
compartment. That step is abiogenesis and it is absent, not implied.
Habitable is the strongest word the evidence carries

**a_cell_ceiling_moves_with_climate** — holds

the diffusion ceiling runs 39.5 microns at 275 K to 64.9 at 310 K,
because diffusion scales with temperature over viscosity and water
thins steeply. A cold habitable world permits only smaller cells --
which is a statement about what could persist, not about anything that
did

## The published numbers

84 of 84 reproduce. A claim is tied to a fingerprint over the rule that
produced it and everything that rule depends on, so an unchanged
fingerprint is a proof that recomputing would return the same thing.

- `3.1.92` 10,584 universes generated blind; 864 pass three filters — reproduces (`(True, 10584, 864)`)
- `3.1.108` a display is 1e6x cheaper and takes the band 3 -> 28 — reproduces (`(7, 3, 28, 13)`)
- `3.1.108` settling needs 73 days of store; only a harvest clears it — reproduces (`(73, 1, 'a grain harvest')`)
- `3.1.109` five senses reach 8 of 13 constraints; 38% must be inferred — reproduces (`(8, 5, 38, 33)`)
- `3.1.109` oral capacity is 8,692 items; epigenetics holds 3.4a — reproduces (`(14.0, 8692, 3.4, 16, 53)`)
- `3.1.110` a lone teller keeps 10 items; 28 voters keep 8,688 — reproduces (`(10.0, 8688, 5.6e-08)`)
- `3.1.110` a band walks at 0.707 adult pace and innovates 39x per km — reproduces (`(1.41, 39, 13, 2, 9332, 280, 90)`)
- `3.1.111` one checked copy is worth 13 speakers; 5 scribes keep a script — reproduces (`(5, 13, 9, 5, 10)`)
- `3.1.111` a crowd disease needs 912 people; cooking pays 58x — reproduces (`(912, 33, 132, 58, 526)`)
- `3.1.111` a granary is 909x cheaper to hold than the range it replaced — reproduces (`(909, 15, 1.9, 8, 3.5)`)
- `3.1.112` a 5th-generation heir holds 32x what their ability warrants — reproduces (`(20, 2.58, 0.08, 32, 15, 162)`)
- `3.1.114` speech is a fixed point at 2 specialties; the loop settles at 23.5 — reproduces (`(2, 3, 23.5, 12163632, 53)`)
- `3.1.113` grain dies at 516 km; knowledge has no range limit — reproduces (`(516, 258, 5.2, 6.8, 2.4)`)
- `3.1.114` ideas are non-rival: escape turns on a 0.372 land share — reproduces (`(0.372, 0.072, -0.128, 0.372, 23.5, 29.4)`)
- `3.1.114` 24% of possible specialists are priced out by their tools — reproduces (`(1177, 368, 24, 1.33, 14.0)`)
- `3.1.115` novelty per head falls to 0.80 while the total rises 32x — reproduces (`(0.8, 32, 21.5, 26.8, 99.7, 0.032)`)
- `3.1.117` two gates: heat stops at round 5, tolerance runs to 10 — reproduces (`(21, 10, 1750, 3, 5, 9, 10)`)
- `3.1.117` 7 of 10 derived numbers match the record within 3x — reproduces (`(7, 1, 2, 6)`)
- `3.1.116` a press is worth 6.6 parts; proofreading is worth nothing — reproduces (`(6.6, 0.322, 0.0, 3.3)`)
- `3.1.107` the derived group is 3; transitivity saves 10x on contests — reproduces (`(3, 10, 0.0, 0.02)`)
- `3.1.106` a microbe needs 6 to adapt yearly, a human 40,792 — reproduces (`(6, 40792, 0.5)`)
- `3.1.105` 3 grades worn, 3 need a tool; the edge opens 97% of land — reproduces (`(3, 3, 97, True, 109)`)
- `3.1.104` comprehension is a count: 6 binds on a microbe, 13 on us — reproduces (`(6, 13, 8192, 3)`)
- `3.1.103` regard is worth 1e19 times what it costs to hold — reproduces (`(True, 7300, 19)`)
- `3.1.102` the code freezes at 100% cost; rank steps at 3.8 children — reproduces (`(100.0, 100, True)`)
- `3.1.102` rank is worth zero then 82 W at the carrying number — reproduces (`(3.8, False, True, 82)`)
- `3.1.101` innovation is omit/duplicate/combine at 4.48 per division — reproduces (`(6, 4, 4.48, 3)`)
- `3.1.100` the modern code needs 1520 bases and 200 are held — reproduces (`(5, 2, False, 1520)`)
- `3.1.100` selection on a trait is 7-9 orders too fast — reproduces (`(7, 7.0, 8.9)`)
- `3.1.99` every ligation is templated; the template is the catalyst — reproduces (`(True, 25488, True, True, 200)`)
- `3.1.98` divides at 2x volume, 28 copies, 1.39 types lost — reproduces (`(2.0, 28, 1.39, 10.0)`)
- `3.1.96` one compartment closes at 14 bases; an ocean is 1e35 — reproduces (`(True, 14, 13, 35)`)
- `3.1.117` Big Bang to a head in 57 links: 49 derived, 7 forced, 0 gaps — reproduces (`(57, 49, 7, 0, 1)`)
- `3.1.95` abundance falls as mass^-3/4 exactly — reproduces (`1.0`)
- `3.1.94` the lineage holds at the 1.58 um closure floor — reproduces (`(1.58, True, True)`)
- `3.1.91` closure is 0.48 catalysts per reaction, above 2000 molecules — reproduces (`(0.48, True, 13, True)`)
- `3.1.90` closure at measured catalysis needs a 13-mer, under 20 — reproduces (`(13, True, 0.395)`)
- `3.1.88` a set closes above 1e-3; the measured p is 1e-8 — reproduces (`(False, True, True)`)
- `3.1.88` cold buys 11x on build/break and 436x on lifetime — reproduces (`(11.4, 436)`)
- `3.1.88` three gates shut at 298 K, one at 255 — reproduces (`(2.73, 259.0, ['fidelity', 'persistence', 'search'], ['search'])`)
- `3.1.86` a head holds 4 trades; today needs 750k; holding never binds — reproduces (`(4.0, 750000, True)`)
- `3.1.85` four gifts, four shorter clocks: 1411, 998, 957, 695 — reproduces (`((1411, 998, 957, 695), True, 8)`)
- `3.1.82` steam caps at 54.7%; Rome 0.17x burial, we run 51x — reproduces (`(54.7, 0.17, 51, True)`)
- `3.1.81` empire 2250 km, 4.7% lies tolerated, 3 of 10 derive — reproduces (`(2250, 4.7, 3)`)
- `3.1.80` muscle for a 400 N blow is 53 cm2; bone picks no height — reproduces (`(53, False)`)
- `3.1.79` speech is 256410x narrower than sight, 0.0122% of a brain — reproduces (`(256410, 0.0122)`)
- `3.1.79` two adults are the smallest viable group — reproduces (`(2, False)`)
- `3.1.79` the fovea is 0.028% of the field; 900 s to sweep — reproduces (`(0.028, 900, 289)`)
- `3.1.78` heat rejection binds; toolmakers fall under 20% — reproduces (`(True, True)`)
- `3.1.77` Earth is fragile in spread, one-sided in mass, free in Z — reproduces (`(True, True, True)`)
- `3.1.76` worn insulation runs out at 19 C, a lodge reaches -64 — reproduces (`(19, -64)`)
- `3.1.76` a brush shelter pays back in 4.6 nights — reproduces (`4.6`)
- `3.1.76` unreferenced rules are mostly lineage, not dead code — reproduces (`(True, True)`)
- `3.1.74` the eye: diffraction 0.77 arcmin, sampling 1.01 — reproduces (`(0.77, 1.01)`)
- `3.1.74` stereo reaches 1320 m and 0.19 mm at arm's length — reproduces (`(1320, 0.19)`)
- `3.1.74` a brain fills in 1.49 years; a life pours 47x through — reproduces (`(1.49, 47)`)
- `3.1.73` a body is 8x short of bone; a flaked edge goes through — reproduces (`(False, 8, True)`)
- `3.1.73` marrow pays for a brain 5.2x over — reproduces (`(True, 5.2)`)
- `3.1.73` the tool root went from 2 nodes to 13 — reproduces (`13`)
- `3.1.73` 16 of 20 tool configurations pay, on DERIVED gains — reproduces (`(16, 20)`)
- `3.1.73` the tool root is 13 nodes deep against 37 for radiative — reproduces (`(13, 37)`)
- `3.1.70` a newborn's brain is 109% of its own budget — reproduces (`109`)
- `3.1.70` growth bottoms at age 5 where the brain is 71% — reproduces (`(5.0, 1.5, 71)`)
- `3.1.70` the provisioning debt is 3.0 adult-years per child — reproduces (`3.0`)
- `3.1.69` cooking short 1.73x on break-even, 2.18x on the gut — reproduces (`(1.73, 2.18, 76)`)
- `3.1.69` death conserves total matter and burial breaks the cycle — reproduces (`(True, True)`)
- `3.1.68` the light race stops at 11.4 m, and at 0.05 m alone — reproduces (`(11.4, 0.05)`)
- `3.1.68` height scales as crown^0.4: 6, 11, 26, 64, 161 m — reproduces (`(6, 11, 26, 64, 161)`)
- `3.1.68` 4 trophic levels under a 204 m cavitation ceiling — reproduces (`(4, 204)`)
- `3.1.31` decay score is 8 right, 0 wrong, 6 refused — reproduces (`(8, 0, 6)`)
- `3.1.27` the derived magic numbers — reproduces (`(2, 8, 20, 28, 40, 50, 82, 126)`)
- `3.1.27` 4.2% of the (kappa, mu) plane gives all seven closures — reproduces (`4.2`)
- `3.1.21` Stefan-Boltzmann agrees to 3.25e-11 — reproduces (`3.25e-11`)
- `3.1.28` the liquid drop is refused below A=13 — reproduces (`13`)
- `3.1.29` mass bar 1.850 in domain, 6.249 outside — reproduces (`(1.85, 6.249)`)
- `3.1.31` measured-Q precision derived as 0.0866 MeV — reproduces (`0.0866`)
- `3.1.31` the unified binding table holds 29 nuclides — reproduces (`29`)
- `3.1.18` folding survival rate 0.573 — reproduces (`0.5729`)
- `3.1.39` unfitted climate: Earth +21.0 K, Venus -488.3 K — reproduces (`(21.0, -488.3)`)
- `3.1.42` habitable band derived 0.999 - 1.899 AU — reproduces (`(0.999, 1.899)`)
- `3.1.60` lab: 27 HOLDS, 0 CLASH, 1 MISSING_RULE, 1 REFUSED, 1 SUGGESTION — reproduces (`(27, 0, 1, 1)`)
- `3.1.47` chance reaches 57 residues and stops — reproduces (`57`)
- `3.1.39` derived CO2 wing cutoff 11.2 cm-1 at 737 K — reproduces (`11.2`)
- `3.1.39` derived CO2 well depth 180 K — reproduces (`180`)

## What was published and later withdrawn

28 numbers were published here and are wrong. They are kept with the
reason, because a record that only holds the surviving answers is not a
record.

### `3.1.116` temperature gates the tech tree, 16 primitives in 6 rounds

true as far as it went and it did not go far enough. Heat stops moving
at round 5 and everything after -- vacuum, alloy, semiconductor,
switching, inference -- is reachable at the same 1750 K and was not
available for two centuries, because the scarce scalar CHANGED to how
accurately matter can be placed. 21 primitives in 10 rounds, with
tolerance going 1e-3 to 1e-9 after the heat stops. The gate is not a
constant of the system, it is whichever scalar is short

### `3.1.68` competition prevents the size collapse, 1.76 vs 0.64

TRUE WHEN WRITTEN and false now, through no fault of its own.
engine/descent.py ran an unbounded fitness objective and a solo lineage
walked down to 0.1 micron; competition looked like the thing holding
size up. That bug was fixed at source with the 1.58-micron closure
floor from engine/earthlab.py, so a solo lineage now settles at 1.76
and there is no collapse to prevent. Competition in fact takes the
median DOWN to 0.64 and what it produces is a RANGE, 5x+ across
species. Found by transcription, not by a claim -- nothing was watching
this rule

### `3.1.113` per-capita surplus scales as N^-0.628, the loop cannot escape

WRONG, and wrong by my arithmetic rather than by the world. The
exponent subtracted mouths at N^1 from two terms that were already PER
WORKER -- Wright's law gives output per worker and yield_ratio is a
ratio to subsistence -- so every invention was counted as though it
were divided among its users and thinned. A design is not divided: a
loaf feeds one person, a technique for making loaves is used by
everyone at once. The only rival input is land. Corrected: N^0.072 at a
0.30 land share, with the crossover at 0.372

### `3.1.112` the loop settles at 24.3 parts, 10.13x yield, 90% off the land

yield_ratio compounded YIELD_PER_SKILL over EVERY specialty and reached
40x subsistence in the network case, which no agrarian economy has ever
managed -- a potter does not raise the grain yield. Only the eight
crafts that touch a field do. Capped: 2.14x yield, 53% sparable, and
past FOOD_SKILLS further specialization buys designs rather than
calories, which is why living standards cannot be read off the food
surplus once anyone is specialized at all

### `3.1.112` Big Bang to a head in 50 links, 0 gaps

3.1.113 adds trade and, with it, the first MISSING link the chain has
carried in a while: total output rises everywhere and per-capita
surplus falls as N^-0.628. Zero gaps was accurate and was also the
chain not yet having asked whether any of it made anyone better off

### `3.1.111` literacy reaches 34% in 500 years from one in 28

spread() was value-driven on f**2 alone, which has no floor -- one
literate in a village of 912 took 20,000 years to go anywhere, which is
plainly wrong. Two terms were missing: an administrative FLOOR (a store
needs an account, worth something whoever else can read, so 1/BAND =
3.6% is demanded regardless) and a food CEILING (a scribe does not
farm, so literacy stops at the share a surplus can spare, 13% at
1.15x). The shape was right and both ends were missing

### `3.1.111` Big Bang to a head in 47 links: 39 derived

three added at 3.1.112: power from scarcity rather than geometry, the
decoupling of an inherited claim from a regressing ability, and the
technology loop

### `3.1.110` Big Bang to a head in 43 links: 35 derived

four added at 3.1.111 -- writing as a skill that bootstraps orally and
can be lost, crowd disease derived from the grain harvest rather than
assumed, the three hygienic answers, and the concentration of a store.
None of them extends the end; they all hang off settling, which was
already there

### `3.1.109` the oral stock is 8,692a (capacity and stock conflated)

8,692 charged only for tellings nobody got round to and nothing for
tellings that came out WRONG. Oral tradition is a game of telephone and
the module pretended it was not. Charging p=0.1 per retelling,
corrected by 28-voice consensus, gives 8,688a -- a four-item
correction, which is the point: the band was already doing the error
correction, the module just had not said so. A LONE teller keeps 10

### `3.1.109` Big Bang to a head in 41 links: 33 derived

two links added at 3.1.110. Pace was missing entirely -- the band walks
at its slowest member, which concentrates problems per km rather than
avoiding them, and that is where the innovation pressure comes from.
Specialists followed from the telephone once it was charged for

### `3.1.95` Big Bang to a head in 37 links: 29 derived, 7 forced

four links were added at 3.1.109 and one of them closed a jump rather
than extending the end: recognition -> one head was an unstated step,
and engine/senses.py now drives it (five senses reach 8 of 13
constraints, so 5 must be modelled). The other three extend regard into
transitivity, oral tradition and diffusion across bands. 37 was never
wrong, it was short

### `3.1.61` seeded life collapses to 0.10 microns

withdrawn in 3.1.94. IT WAS AN UNBOUNDED OBJECTIVE, not a biological
result. fitness() returned surplus PER GRAM -- a*m^(-1/3) - b*m^(-1/4)
-- which diverges as mass falls: 3.3e6 at 1.58 microns and 5.5e8 a
hundredth of the way down. The lineage was descending that without
limit into max(r, 1e-7), a clamp with nothing behind it, and the
resting place was therefore the clamp rather than any rule. The
function's own docstring said 'bigger is cheaper per gram by Kleiber
and harder to feed by geometry, and where they cross is a size', which
is true of surplus and false of surplus per gram. engine/earthlab.py
had already derived the missing bound -- 1.58 microns, below which a
compartment cannot hold the molecule types to catalyse its own repair
-- and descent never consulted it. With closure in place the lineage
neither collapses nor grows; it holds at 1.78 microns

### `3.1.89` wider sweep: p ~ R^-0.72, a 15-mer, 5 orders of gap

withdrawn in 3.1.90. The number was close and the METHOD was still
wrong: it fitted the threshold p against network size and extrapolated,
which extrapolates a quantity that moves. Bisecting the threshold at
seven sizes over two alphabets shows that f = p*R, the reactions one
molecule catalyses at threshold, is LINEAR IN L with slope 0.395 -- and
c = f/L holds between 0.31 and 0.49 while R changes 190-fold. Since R
grows exponentially in L and the catalysis each molecule must supply
grows only linearly, p = cL/R(L) is a derivation rather than a fit, and
it lands at 13 bases rather than 15. This is the third value published
for this quantity; the first two were 1e20 reactions and 6.4e9

### `3.1.88` extrapolating closure to 1e-8 asks for 1e20 reactions

withdrawn in 3.1.89, and not for being uncertain -- for being WRONG BY
ELEVEN ORDERS OF MAGNITUDE. It fitted p ~ R^-0.30 by sweeping polymer
length over a two-letter alphabet, which varies network size and holds
monomer diversity fixed. Adding a four-letter alphabet gives p ~
R^-0.72 and 6.4e9 reactions. The published number carried its
extrapolation distance (17 orders) attached, which is why it was not
trusted, but labelling an extrapolation as untrustworthy is not the
same as checking it. Taking more data is. At four nucleotides the new
figure is polymers up to about 15 bases, and earthlab derived 20 bases
independently as the assembly piece size

### `3.1.87` two gates shut at 298 K: fidelity and search

withdrawn in 3.1.88 by ADDING A GATE, not by any number moving. Nothing
was asking whether a replicase survives long enough to be copied, and a
strand cut faster than it is rebuilt is not a replicase. Persistence is
now a gate, it is SHUT at 298 K, and it opens by 273 -- so the list at
298 is three and the list at 255 is still one. A claim about which
gates are shut is only as complete as the set of gates

### `3.1.84` every gift shortens the clock: 1809, 1201, 708 years

withdrawn in 3.1.85, and the finding survived the correction that
killed the numbers. The reach multiplier was capped at 3.6, a figure I
picked, and it turned out to be SATURATED before infrastructure was
added -- so the cap and not the physics was setting the ceiling, and
adding roads and grids changed nothing at all. The ceiling now comes
from the flow: every watt of land photosynthesis feeds 2,707 billion.
The years move to 1411, 998, 957, 695 and every gift still shortens the
clock

### `3.1.83` the run reaches 24B and stops on food, not coal

withdrawn in 3.1.84. 24 billion is still what the flow feeds, but
'stopped by food' was the only verdict that loop COULD return --
population grows to the ceiling and sits there, so moving the ceiling
changed the number and never the answer. Phosphorus is a stock rather
than a rate and gives the run a second way to fail, and with it in
place all three scenarios end on PHOSPHORUS instead. The old claim was
not wrong about the number; it was a claim about a model with one wall

### `3.1.72` the tool root is 2 nodes deep, the shallowest asked

withdrawn in 3.1.73 BY BEING FIXED, which is the only way a depth claim
can be withdrawn. Two nodes meant the question stood on one constant
and itself -- a tool was being priced, never produced. engine/tools.py
derives it instead: a blow is a force over an area, bone yields at a
pressure engine/life.py already knew, and a fist misses by 8x while a
flaked edge goes through. The root now runs 13 nodes and reaches
life.BONE_COMPRESSIVE. The old number was right when it was published
and the point of publishing it was to make it wrong

### `3.1.72` 21 of 28 tool configurations pay

withdrawn in 3.1.73, and not because it was miscounted -- it was, at
3.1.70, where 26 was written into the README by hand instead of read
from the check, which is why both tool numbers are registered now. It
is withdrawn because the SPACE changed. Those 28 combinations crossed
four brain sizes with seven intake gains somebody picked out of the
air, and the answer meant no more than the list did. engine/tools.py
derives the gain from how much marrow is in a femur, how much energy is
in marrow, and whether anything can open the bone at all -- so the
gains are computed and there are five, not seven. 16 of 20 pay. The
count went down and the number is worth more

### `3.1.69` the gut pays for the brain, 12.8 W against 11.1 W

withdrawn in 3.1.70, and the arithmetic was never wrong -- the QUESTION
was. It priced an adult standing still, where a brain is a running cost
that some other organ must offset. A brain is not run, it is BUILT, out
of food, in childhood, by someone who is not paying for it. Run the
life instead of the snapshot and a newborn's brain is 109% of
everything its own body can make, so provisioning is a precondition and
not a trade; and body growth falls to its slowest at age five with the
brain still at 71%, so the child does not shrink an organ, it stops
growing. The 3.0 adult-years a child costs was never inside one adult
body to be found by rearranging its organs

### `3.1.44` every habitable world orbits a 0.51-0.54 Msun star

withdrawn in 3.1.52. That held only while carbon could not reach an
inner planet: the delivery source stopped at 45 AU and CO condenses at
124, so the only worlds scraping enough carbon were those around dim
stars with close-in ice lines. With the source extended, 101 of 234
worlds are habitable and span every stellar mass. The correlation was
the shape of a gap

### `3.1.37` habitable band outer edge 1.898 AU

3.1.42 coarsened the root scan from 3,400 points to 420 after profiling
showed it bought nothing; the outer edge moved by 0.001 AU, which is
inside the bisection tolerance

### `3.1.31` lab reported 1 CLASH

resolved in 3.1.39: the far-wing clash was between two hand-waves, and
deriving the intermolecular potential replaced both with a computed
11.2 cm-1

### `3.1.33` unfitted climate: Earth +12.3 K

3.1.38 replaced the box-shaped wing with a real Lorentz profile that
falls off with distance from line centre. The correct shape absorbs
more, and Earth moved to +21.3 K -- worse agreement from better
physics, with the excess traced to hand-entered band parameters being
out by about a factor of two

### `3.1.23` unfitted climate: Earth -3.2 K

3.1.33 fixed spectral overlap so overlapping bands add optical depth
instead of averaging transmittance. Earth's water bands overlap
heavily, so the old averaging under-counted them and the -3.2 K
agreement was partly the bug. It now reads +12.3 K

### `3.1.30` ablation read 1 right, 1 wrong, 12 refused

3.1.31 changed the rule being measured; it now reads 8, 0, 6. The table
was correct when written and describes a system that no longer exists

### `3.1.26` 8 right, 3 wrong, 3 refused

those eight rested on a +5.455 MeV source inconsistency cancelling the
liquid drop's deficit; superseded by 3.1.31, which reaches eight with
zero wrong

### `3.1.19` Mercury held out at +2.8 K

withdrawn in 3.1.20: it compared a redistributed prediction against a
dayside observation
