# mote

A very small animal with a very small brain, evolved for as long as a
laptop will sit still. One generation is one lifetime, so a million
generations is a million years at the default one year per generation, and
nothing is quietly multiplied to make the number bigger.

```
python -m mote demo                    # ~20k years, start to finish, ~3 min
python -m mote run --gens 1000000      # the long one
python -m mote report runs/deep        # score the fossils, write the charts
python -m mote watch runs/deep         # ancestor vs descendant, same world
python -m mote selftest                # 11 checks on the model itself
```

Requires numpy. numba is optional and makes it ~8x faster; without it the
reference implementation runs and gives the same answers.

## The animal

A fully-recurrent network of at most 40 nodes: 8 senses, 2 muscles, and up
to 30 hidden slots that are individually switched on or off by mutation. A
newborn lineage starts with **two** hidden neurons.

Mutation changes weights, adds and removes connections, and adds and
removes neurons. The mutation step size is itself a gene, so a lineage
tunes how boldly it searches rather than being told. New wiring arrives at
**weight zero** — expressed and inherited but behaviourally silent until
ordinary weight mutation finds a use for it. Without that, every structural
mutation was an immediate insult to a working brain and selection pruned
the population back to the floor every time.

Every hidden neuron burns energy each tick whether it is doing anything or
not, so brain size is an economic decision rather than a free parameter.

## The world

A wrapping 20x20 grid with patches of two flavours, A and B. Smell tells
the mote which flavour a patch is and **never** which one is food: that
polarity is drawn fresh each episode and announced only during the opening
ticks, on one sense channel, which then goes quiet. At higher difficulty
the polarity also reverses mid-life.

So there are exactly two ways to make a living:

- **remember** the announcement for the rest of the episode, or
- **taste** something and find out, at the price of a mouthful of poison.

Tasting works, and it is meant to. As difficulty rises poison hurts more
and taste gets fainter, so the margin between the two strategies widens on
its own. Nothing in the model rewards memory directly — memory wins because
biting things is expensive.

**Fitness is net energy over a lifetime**: everything taken in, minus
everything burnt on poison, metabolism, brain and movement. Scoring food
eaten alone left metabolism out of fitness entirely, so an animal with
energy to spare carried twenty neurons for free.

**Difficulty is not a schedule.** One number `d` rises when the top
quartile is eating well and falls when it is starving, so the world tracks
the population's competence instead of running out. A lineage that
collapses is handed easier worlds rather than going extinct.

## How improvement is measured

The training world moves, so a training score of 0.4 at `d=0.1` and a 0.4
at `d=0.9` are not the same animal and the number cannot tell you which you
have. Every claim therefore comes from `bench.py`, which is

- **fixed** — the seeds and difficulties are constants, chosen once, before
  any long run;
- **blind** — nothing in it is visible to selection, and `Lineage` never
  calls it;
- **shared** — a fossil and its descendant are scored inside the *same*
  episode, meeting the same patch layouts and the same sensor noise, so a
  head-to-head differs by behaviour and nothing else.

Three lesions then say *what* was learned, which a score cannot. The cue is
run intact, absent, and **lying**. A mote that navigates by memory is
wrecked when the cue lies; one that taste-tests never notices. The gap
between the two is reported as a memory index next to every score.

## What is chosen, and what is measured

Numbers that were picked rather than derived, and what each one does:

| name | value | how it was set |
|---|---|---|
| `NEURON_COST` | see `world.py` | calibrated by sweep; see below |
| `RATCHET_UP` / `DOWN` | 0.24 / 0.14 | calibrated against the score a population actually reaches |
| `FOOD_VALUE`, `MOVE_COST`, grid size, episode length | — | chosen, and not tuned against any result |
| `p_grow` / `p_shrink` | equal | deliberately symmetric, see below |

Two of these were wrong first, in ways worth recording:

- **Structural mutation rates were per connection slot, not per genome.**
  Every brain gained twenty-three connections per generation and the wiring
  saturated inside twenty generations, leaving selection nothing to choose
  between.
- **`p_grow` was 2.5x `p_shrink`.** Brains then grew because the mutation
  rates made them grow, which measures the author and not the animal. Equal
  rates make size something selection decides.
- **`RATCHET_UP` was 0.30**, which a population plateauing near 0.26 never
  once tripped: `d` sat at zero for six thousand generations while the
  world stayed on its easiest setting. A ratchet whose band does not
  straddle what the animal can reach is decoration.

## Two backends, and how closely they agree

`world.py` is the definition: readable, vectorised, slow. `fastsim.py` is
the same world compiled, and it is what makes deep time affordable
(~2 ms per generation against ~19 ms). It is not trusted — `selftest`
runs both on the same genomes and the same worlds.

Across difficulties and seeds the two produce **bit-identical behaviour**:
the same food eaten, the same poison eaten, the same mouthfuls, the same
animals dead at the same tick. The energy ledger agrees to about one
float32 ULP per tick, reaching 1.5e-8 of a score of order 0.1 by the end of
an episode. That last bit was chased and not caught: numba evaluates
float32 expressions through double and rounds on store, and explicit casts
at every stage and replicating numpy's left-to-right grouping both failed
to close it. The test asserts identical behaviour and a 1e-6 score
tolerance rather than equality, and says so.

## What this is not

It is not a language model, and it does not get smarter by reading
anything. It is a few hundred numbers under selection pressure in a
foraging task, and the only thing it can become better at is making a
living in that task. "A million years" is a unit conversion from
generations at a stated generation time, not a claim to have simulated
geology, ecology, or anything else that happens over a million years.

A million generations of selection on one population in one task is also
not a long time in any evolutionary sense. Nothing here speciates, nothing
competes with anything else alive, and the world cannot be changed by the
things living in it.
