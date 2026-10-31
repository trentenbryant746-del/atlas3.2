"""
What has to be true for any number in a report to mean anything.

The load-bearing one is test_batching_does_not_change_a_score. Every claim
in this project compares a genome from generation 0 against a genome from
generation a million, and the report scores all hundred-odd fossils in one
batched call for speed. If a genome's score depended on who it was batched
with, every one of those comparisons would be meaningless.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from mote import bench, fastsim                                  # noqa: E402
from mote.brain import HID0, N_IN, Brains                        # noqa: E402
from mote.deeptime import fossil_gens                            # noqa: E402
from mote.evolve import Lineage                                  # noqa: E402
from mote.world import Episode                                   # noqa: E402


def _aged(n=24, seed=0, rounds=8):
    rng = np.random.default_rng(seed)
    b = Brains.seed_population(n, rng)
    for _ in range(rounds):
        b.mutate(rng)
    return b


def test_backends_agree():
    """fastsim.py is an optimisation, not a second opinion.

    BEHAVIOUR must be bit-identical -- same food eaten, same poison eaten,
    same mouthfuls, same animals dead. The energy LEDGER is allowed about a
    float32 ULP per tick, because numba evaluates float32 expressions
    through double and rounds on store; see the note in fastsim.py for what
    was tried. 1e-6 is roughly a hundred times the observed gap and far
    below anything a claim in this project rests on.
    """
    if not fastsim.AVAILABLE:
        return
    for d in (0.0, 0.25, 0.5, 0.75, 1.0):
        for seed in (4242, 77):
            b = _aged(16, seed=int(d * 100) + seed)
            ep = Episode(seed=seed, n_worlds=3, d=d)
            a, ea = ep.run(b, backend="ref")
            f, ef = ep.run(b, backend="fast")
            for k in ("gained", "lost", "bites", "alive"):
                assert np.array_equal(ea[k], ef[k]), (
                    f"backends behaved differently at d={d}: {k}")
            assert np.abs(a - f).max() < 1e-6, f"ledger drift at d={d}"


def test_batching_does_not_change_a_score():
    b = _aged(12, seed=7)
    ep = Episode(seed=555, n_worlds=4, d=0.5)
    together, _ = ep.run(b)
    for i in (0, 5, 11):
        alone, _ = Episode(seed=555, n_worlds=4, d=0.5).run(b.take([i]))
        assert np.allclose(alone[0], together[i], atol=0, rtol=0), (
            f"genome {i} scored differently alone than in a batch")


def test_episode_is_deterministic():
    b = _aged(8, seed=3)
    one, _ = Episode(seed=99, n_worlds=3, d=0.4).run(b)
    two, _ = Episode(seed=99, n_worlds=3, d=0.4).run(b)
    assert np.array_equal(one, two)


def test_identical_brains_get_identical_worlds():
    """Common random numbers: a duplicate genome must tie with itself."""
    b = _aged(1, seed=11)
    pair = Brains.concat([b.take([0]), b.take([0])])
    s, _ = Episode(seed=1234, n_worlds=4, d=0.6).run(pair)
    assert np.array_equal(s[0], s[1])


def test_mutation_keeps_the_genome_legal():
    rng = np.random.default_rng(1)
    b = Brains.seed_population(32, rng)
    for _ in range(40):
        b.mutate(rng)
        assert not b.conn_on[:, :N_IN, :].any(), "wired into an input node"
        assert b.node_on[:, :HID0].all(), "a sense or muscle was switched off"
        assert (b.n_hidden() >= 1).all(), "a brain lost its last neuron"
        assert np.isfinite(b.W).all() and np.isfinite(b.b).all()
        assert (b.sigma > 0).all()


def test_a_bigger_brain_costs_something():
    """A neuron switched on with zero weights is behaviourally silent, so any
    difference it makes is the metabolic charge and nothing else.

    Two traps here, both hit while writing this test.

    The weights have to be zeroed explicitly, exactly as Brains.mutate does
    when it grows a neuron: seed_population scatters conn_on across slots
    that are switched OFF, so merely enabling a slot revives latent random
    wiring and the comparison stops being about metabolism.

    And TOTAL spend is not monotone in brain size, because a heavier brain
    drains faster, dies sooner, and can therefore burn less over a shorter
    life -- and score better for the same reason, having eaten less poison
    on the way. The invariant is the per-tick charge, and total spend only
    among animals that lived equally long.
    """
    from mote.world import brain_cost

    rng = np.random.default_rng(5)
    small = Brains.seed_population(1, rng, hidden_on=2)
    big = small.take([0])
    free = np.nonzero(~big.node_on[0, HID0:])[0][:8]
    slots = HID0 + free
    big.node_on[0, slots] = True
    big.W[0, slots, :] = 0.0                    # silent on arrival
    big.W[0, :, slots] = 0.0

    assert big.n_hidden()[0] == small.n_hidden()[0] + 8
    assert brain_cost(big)[0] > brain_cost(small)[0], "the charge is not levied"

    pair = Brains.concat([small, big])
    ep = Episode(seed=31337, n_worlds=8, d=0.0)
    _s, ex = ep.run(pair)
    survived = [w for w in range(ep.n)
                if ex["spent"][0, w] > 0 and ex["spent"][1, w] > 0]
    assert survived, "no world to compare in"
    full = [w for w in survived
            if abs(float(ex["spent"][0, w]) - float(ex["spent"][1, w])) > 0]
    assert full, "the extra neurons changed nothing at all"
    assert any(ex["spent"][1, w] > ex["spent"][0, w] for w in full), (
        "extra neurons were never more expensive in any world")


def test_brain_cost_is_monotone():
    from mote.world import brain_cost
    rng = np.random.default_rng(2)
    b = Brains.seed_population(6, rng)
    for i in range(6):
        b.node_on[i, HID0:HID0 + i + 1] = True
        b.node_on[i, HID0 + i + 1:] = False
    c = brain_cost(b)
    assert np.all(np.diff(c) > 0), f"charge not monotone in neurons: {c}"


def test_lesions_do_what_they_say():
    none = Episode(seed=8, n_worlds=3, d=0.66, cue_mode="none")
    assert np.all(none.cue_ts == 0.0)
    intact = Episode(seed=8, n_worlds=3, d=0.66)
    assert np.any(intact.cue_ts != 0.0)
    lying = Episode(seed=8, n_worlds=3, d=0.66, cue_mode="lying")
    lit = intact.cue_ts != 0.0
    assert np.any(lying.cue_ts[lit] != intact.cue_ts[lit]), "the lie told truth"
    assert np.array_equal(intact.A0, lying.A0), "lesion changed the world too"


def test_difficulty_is_monotone_where_it_claims_to_be():
    from mote.world import dials
    easy, hard = dials(0.0), dials(1.0)
    assert hard["noise"] > easy["noise"]
    assert hard["poison_harm"] > easy["poison_harm"]
    assert hard["announce"] < easy["announce"]
    assert hard["taste_gain"] < easy["taste_gain"]
    assert hard["flips"] >= easy["flips"]


def test_ratchet_follows_competence_not_a_clock():
    """d must be able to fall, or it is a schedule wearing a disguise."""
    lin = Lineage(pop=24, worlds=2, seed=2, d0=0.5)
    lin.topq_ema = 0.0                            # a starving population
    for _ in range(12):
        lin.generation(want_sizes=False)
    assert lin.d < 0.5, "the world never relented for a failing population"


def test_benchmark_is_frozen():
    """Same genome, two calls, and a fresh cache in between."""
    b = _aged(4, seed=21)
    first = bench.frozen(b)["overall"].copy()
    bench._CACHE.clear()
    assert np.allclose(first, bench.frozen(b)["overall"], atol=1e-6)


def test_fossil_schedule():
    for total in (0, 1, 1000, 1_000_000):
        g = fossil_gens(total)
        assert g == sorted(set(g))
        assert g[0] == 0 and g[-1] <= total or total == 0


def main():
    fns = [(k, v) for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    bad = 0
    for name, fn in fns:
        try:
            fn()
            print(f"  PASS  {name}")
        except AssertionError as e:
            bad += 1
            print(f"  FAIL  {name}: {e}")
        except Exception as e:
            bad += 1
            print(f"  ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n  {len(fns)-bad}/{len(fns)} passed")
    return bad


if __name__ == "__main__":
    raise SystemExit(1 if main() else 0)
