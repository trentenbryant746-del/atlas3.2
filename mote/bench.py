"""
The frozen benchmark. The only place improvement is allowed to be claimed.

The training world in evolve.py moves: it hardens when the population
copes. That is what keeps a million generations interesting and it also
destroys the meaning of a fitness score, because a 0.4 earned at d=0.1 and
a 0.4 earned at d=0.9 are not the same animal and the number cannot tell
you which you have.

So every claim in this project comes from here instead, under three rules.

    FIXED      the seeds and the difficulties below are constants. They
               were chosen once, before any long run, and a run that
               looked bad is not grounds for changing them.
    BLIND      nothing in this module is visible to selection. Lineage
               never calls it. It cannot be optimised against.
    SHARED     a fossil and its descendant are scored inside the SAME
               episode object, so they meet the same worlds, the same
               patch layout and the same sensor noise. A head-to-head
               here differs by behaviour and by nothing else.

WHAT THE LESIONS ARE FOR. Knowing a mote got better is not knowing what it
got better at. Two strategies earn a living in this world -- remember the
announcement, or bite something and find out -- and a score cannot tell
them apart. Breaking the cue can.

    intact     the announcement is true
    none       there is no announcement at all
    lying      the announcement is reversed, in half the worlds

A mote that navigates by memory is wrecked by `lying` and hurt by `none`.
A mote that taste-tests does not notice either. The gap between intact and
lying is therefore a measure of how much of the animal's competence is
memory, and it is reported next to every score.
"""
from __future__ import annotations

import numpy as np

from mote.brain import Brains
from mote.world import Episode

# Chosen once. Changing these numbers invalidates every run ever recorded
# against them, which is the point of writing them down here.
BENCH_SEEDS = (90001, 90002, 90003, 90004, 90005, 90006, 90007, 90008)
BENCH_LEVELS = (0.0, 0.33, 0.66, 1.0)
LESION_LEVEL = 0.66
CEILING_GRID = tuple(round(0.1 * i, 2) for i in range(11))
CEILING_PASS = 0.15        # a score that counts as "making a living"

_CACHE: dict = {}


def _episodes(d, cue_mode="intact", noise_scale=1.0):
    """Cached, so the same worlds are reused for every fossil in a report."""
    key = (round(d, 4), cue_mode, round(noise_scale, 3))
    if key not in _CACHE:
        _CACHE[key] = [Episode(seed=s, n_worlds=4, d=d, cue_mode=cue_mode,
                               noise_scale=noise_scale) for s in BENCH_SEEDS]
    return _CACHE[key]


def _score(brains: Brains, d, cue_mode="intact", noise_scale=1.0):
    """-> (P,) mean normalised score over every frozen world at this level."""
    tot = None
    for ep in _episodes(d, cue_mode, noise_scale):
        s, _ = ep.run(brains)
        m = s.mean(1)
        tot = m if tot is None else tot + m
    return tot / len(BENCH_SEEDS)


def frozen(brains: Brains) -> dict:
    """Score every genome at every frozen level. -> {level: (P,) array}."""
    out = {d: _score(brains, d) for d in BENCH_LEVELS}
    out["overall"] = np.mean([out[d] for d in BENCH_LEVELS], axis=0)
    return out


def ceiling(brains: Brains) -> np.ndarray:
    """The hardest difficulty each genome still makes a living in.

    Scanned bottom-up and stopped at the first failure, so this is the
    width of the band a mote can survive across, not its single best level.
    """
    p = brains.size
    out = np.zeros(p)
    passed = np.ones(p, dtype=bool)
    for d in CEILING_GRID:
        ok = _score(brains, d) >= CEILING_PASS
        passed &= ok
        out[passed] = d
    return out


def lesions(brains: Brains, d=LESION_LEVEL) -> dict:
    """How much of the competence is memory, and how much is tasting."""
    intact = _score(brains, d, "intact")
    none = _score(brains, d, "none")
    lying = _score(brains, d, "lying")
    noisy = _score(brains, d, "intact", noise_scale=2.0)
    denom = np.maximum(np.abs(intact), 0.02)
    return {
        "intact": intact, "none": none, "lying": lying, "noisy": noisy,
        "cue_worth": intact - none,          # what the announcement is worth
        "lie_damage": intact - lying,        # what believing it costs
        "memory_index": (intact - lying) / denom,
        "noise_robustness": noisy / denom,
    }


def head_to_head(a: Brains, b: Brains, d=LESION_LEVEL, worlds=None) -> dict:
    """Two genomes, the same worlds, tick for tick.

    Both are run inside one Episode, so neither gets a kinder patch layout
    or a quieter sensor than the other.
    """
    pair = Brains.concat([a.take([0]), b.take([0])])
    seeds = BENCH_SEEDS if worlds is None else worlds
    wins_a = wins_b = ties = 0
    sa = sb = 0.0
    n = 0
    for s in seeds:
        ep = Episode(seed=s, n_worlds=4, d=d)
        sc, _ = ep.run(pair)
        for w in range(sc.shape[1]):
            n += 1
            sa += float(sc[0, w])
            sb += float(sc[1, w])
            if sc[0, w] > sc[1, w] + 1e-6:
                wins_a += 1
            elif sc[1, w] > sc[0, w] + 1e-6:
                wins_b += 1
            else:
                ties += 1
    return {"d": d, "episodes": n, "score_a": sa / n, "score_b": sb / n,
            "wins_a": wins_a, "wins_b": wins_b, "ties": ties,
            "win_rate_b": wins_b / n}
