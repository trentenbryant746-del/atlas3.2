"""
Selection, and the ratchet that keeps the world from being solved.

A fixed world is mastered and then nothing more happens: the population
sits at its ceiling and a million further generations buy nothing. So the
world here tracks the population. Difficulty is one number d in [0, 1], and
after every generation

    the top quartile is eating well     ->  d rises a little
    the top quartile is starving        ->  d falls a little
    in between                          ->  d holds

which makes d a *measurement* rather than a schedule: it settles wherever
the population's competence is, and watching it climb over deep time is
watching the animal get better at something, not watching a curriculum run
out. Nobody has to guess the right difficulty, and a lineage that collapses
is given easier worlds instead of dying out.

THE COST OF THE RATCHET is that raw fitness stops meaning anything across
eras -- a score of 0.4 at d=0.2 and a score of 0.4 at d=0.9 are not the
same animal. Every number used to claim improvement in this project
therefore comes from bench.py, which holds its worlds fixed forever and is
never allowed to influence selection.
"""
from __future__ import annotations

import numpy as np

from mote.brain import N_MAX, Brains
from mote.world import Episode

F32 = np.float32

RATCHET_UP = 0.15          # top-quartile score above which the world hardens
RATCHET_DOWN = 0.08        # and below which it relents
RATCHET_STEP = 0.003
RATCHET_MEMORY = 0.02      # EMA weight on the signal the ratchet reads


class Lineage:
    """One evolving population, plus the world that is tracking it."""

    def __init__(self, pop=128, worlds=3, seed=0, d0=0.0, ratchet=True,
                 elite=2, tourney=3, p_cross=0.45, extinct_every=0,
                 extinct_keep=0.10):
        self.rng = np.random.default_rng(seed)
        self.seed = seed
        self.pop = pop
        self.worlds = worlds
        self.d = float(d0)
        self.ratchet = ratchet
        self.elite = elite
        self.tourney = tourney
        self.p_cross = p_cross
        self.extinct_every = extinct_every
        self.extinct_keep = extinct_keep
        self.gen = 0
        self.brains = Brains.seed_population(pop, self.rng)
        self.extinctions = 0
        self._fit = None
        # Three worlds is a noisy read on a genome, so the raw top-quartile
        # score swung 0.13 to 0.43 between neighbouring generations and the
        # ratchet spent its time chasing that instead of tracking
        # competence. It reads an EMA with a ~35 generation half-life.
        self.topq_ema = None

    # -- selection -------------------------------------------------------
    def _tournament(self, fit, n):
        """Indices of n winners of k-way tournaments, sampled with repeats."""
        picks = self.rng.integers(0, self.pop, size=(n, self.tourney))
        return picks[np.arange(n), np.argmax(fit[picks], axis=1)]

    def generation(self, want_sizes=True):
        """Evaluate, select, breed, and let the world react. -> stats dict.

        The next generation is built with ONE copy of the genome arrays.
        The obvious version -- take the elites, take the clones, crossover
        the rest, concatenate -- copied (pop, 28, 28) four times over and
        cost more than simulating the generation did.
        """
        ep = Episode(seed=(self.seed * 1_000_003 + self.gen),
                     n_worlds=self.worlds, d=self.d)
        score, extras = ep.run(self.brains)
        fit = score.mean(1)
        self._fit = fit

        order = np.argsort(-fit)
        topq = float(fit[order[:max(1, self.pop // 4)]].mean())

        stats = {
            "gen": self.gen, "d": self.d,
            "best": float(fit[order[0]]), "mean": float(fit.mean()),
            "topq": topq, "median": float(np.median(fit)),
            "sigma": float(self.brains.sigma.mean()),
            "alive": float(extras["alive"].mean()),
            "bites": float(extras["bites"].mean()),
            "extinctions": self.extinctions,
        }
        if want_sizes:
            hid, conns = self.brains.sizes()
            stats["hidden"] = float(hid.mean())
            stats["conns"] = float(conns.mean())

        # -- the next generation ----------------------------------------
        n_elite = min(self.elite, self.pop)
        n_child = self.pop - n_elite
        bottleneck = (self.extinct_every and self.gen
                      and self.gen % self.extinct_every == 0)

        parents = np.empty(self.pop, dtype=np.intp)
        parents[:n_elite] = order[:n_elite]
        if bottleneck:
            # only the top sliver survives, and the refill searches harder
            n_surv = max(2, int(self.pop * self.extinct_keep))
            parents[n_elite:] = order[self.rng.integers(0, n_surv, size=n_child)]
            self.extinctions += 1
        else:
            parents[n_elite:] = self._tournament(fit, n_child)

        nxt = self.brains.take(parents)
        if bottleneck:
            nxt.sigma[n_elite:] *= 2.0
        else:
            n_x = int(n_child * self.p_cross)
            if n_x:
                pb = self._tournament(fit, n_x)
                sl = slice(n_elite, n_elite + n_x)
                m = self.rng.random((n_x, N_MAX, N_MAX)) < 0.5
                nxt.W[sl] = np.where(m, nxt.W[sl], self.brains.W[pb])
                mb = self.rng.random((n_x, N_MAX)) < 0.5
                nxt.b[sl] = np.where(mb, nxt.b[sl], self.brains.b[pb])
                nxt.sigma[sl] = np.sqrt(nxt.sigma[sl] * self.brains.sigma[pb])

        nxt.mutate(self.rng)
        for arr, src in ((nxt.W, self.brains.W), (nxt.b, self.brains.b),
                         (nxt.node_on, self.brains.node_on),
                         (nxt.conn_on, self.brains.conn_on),
                         (nxt.sigma, self.brains.sigma)):
            arr[:n_elite] = src[order[:n_elite]]        # elites pass unchanged
        self.brains = nxt

        self.topq_ema = topq if self.topq_ema is None else (
            (1 - RATCHET_MEMORY) * self.topq_ema + RATCHET_MEMORY * topq)
        stats["topq_ema"] = self.topq_ema
        if self.ratchet:
            topq = self.topq_ema
            if topq > RATCHET_UP:
                self.d = min(1.0, self.d + RATCHET_STEP)
            elif topq < RATCHET_DOWN:
                self.d = max(0.0, self.d - RATCHET_STEP)

        self.gen += 1
        return stats

    # -- what to keep ----------------------------------------------------
    def champion(self) -> Brains:
        """The single best genome of the generation just evaluated.

        Evaluates if nothing has been evaluated yet, so a freshly built
        lineage still returns its best ancestor rather than genome zero.
        """
        if self._fit is None:
            ep = Episode(seed=self.seed * 1_000_003, n_worlds=self.worlds, d=self.d)
            self._fit, _ = ep.run(self.brains)
            self._fit = self._fit.mean(1)
        return self.brains.take([int(np.argmax(self._fit))])
