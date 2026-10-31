"""
The tide pool.

A torus grid holding patches of two flavours, A and B. Smell tells the mote
which flavour a patch is and never which one is food: that polarity is drawn
fresh for every episode and announced only during the opening ticks, on one
sense channel, after which the channel goes quiet.

So there are exactly two ways to eat well.

    remember    hold the announcement for the rest of the episode
    taste       take a bite of something and read what it was

Tasting works, and it is meant to. It costs one mouthful of poison per
patch, and as difficulty rises poison hurts more while taste gets fainter,
so the margin between the two strategies widens on its own. Nothing here
rewards memory directly. Memory wins because biting things is expensive.

COMMON RANDOM NUMBERS. Every brain in a generation faces the same worlds
with the same sensor noise, pre-drawn per world rather than per animal. Two
brains being compared therefore differ by their behaviour and nothing else,
which cuts the variance of selection and is what makes a head-to-head
between an ancestor and a descendant mean anything.

FITNESS IS NET ENERGY, NOT FOOD EATEN. Scoring an animal on (food minus
poison) alone left metabolism out of fitness entirely: it could only matter
by killing you, so an animal with energy to spare carried twenty neurons
for free and brain size drifted wherever it liked. A calibration sweep over
the neuron cost found almost no effect on size for exactly this reason, and
a test asserting that a bigger brain costs something failed while the model
was, strictly speaking, correct. Score is now everything taken in minus
everything burnt -- food, poison, metabolism, the brain, and the cost of
moving -- which is the quantity selection should have been reading all
along.

A BRAIN COSTS SOMETHING TO RUN. Every hidden neuron a mote carries burns
NEURON_COST of energy per tick whether it is doing anything or not. Without
that charge a neuron was free, so hidden slots filled by neutral drift and
every lineage pinned at whatever ceiling the array size happened to impose
-- brain size measured N_MAX and nothing about the animal. With it, size is
an economic decision: the lineage buys exactly as much brain as the world
it is living in will pay for, which is the number worth plotting against
deep time.

EVERYTHING TIME-VARYING IS PRECOMPUTED. The cue schedule, the polarity
schedule and the patch drift are built as (steps, worlds) tables before a
single tick runs. That keeps the two backends -- the readable numpy one
below and the compiled one in fastsim.py -- structurally identical, so they
can be checked against each other instead of trusted.
"""
from __future__ import annotations

import numpy as np

from mote.brain import N_IN, N_MAX, Brains, step

F32 = np.float32

GRID = 20                  # cells across, wrapping both ways
STEPS = 100                # ticks in an episode
ANT_ANG = 0.7              # antenna half-angle, radians
ANT_R = 1.6                # antenna reach, cells
MAX_TURN = 0.7             # radians per tick
MAX_SPEED = 1.0            # cells per tick
FOOD_VALUE = 0.12          # energy in a full cell of the good flavour
START_ENERGY = 1.0
MAX_ENERGY = 3.0
MOVE_COST = 0.004          # per unit speed squared
NEURON_COST = 0.00005      # CALIBRATED by sweep, see mote/README.md
PATCH_SIGMA = 1.7
N_PATCH_A = 4


def dials(d: float) -> dict:
    """Difficulty d in [0, 1] -> the eight things that get harder.

    One knob, because the ratchet in evolve.py needs a single number it can
    push up when the population is coping and ease down when it is not.
    """
    d = float(np.clip(d, 0.0, 1.0))

    def lerp(lo, hi):
        return lo + (hi - lo) * d

    return {
        "d": d,
        "noise": lerp(0.01, 0.30),            # on every sense channel
        "poison_harm": lerp(0.15, 1.20),      # what a bad mouthful costs
        "announce": int(round(lerp(25, 3))),  # ticks the cue stays lit
        "n_patch_b": int(round(lerp(3, 7))),  # decoys outnumber food
        "base_cost": lerp(0.004, 0.012),      # metabolism per tick
        "taste_gain": lerp(0.90, 0.25),       # how legible a mouthful is
        "drift": lerp(0.0, 0.25),             # patches wander
        "flips": int(np.floor(lerp(0.0, 2.99))),  # polarity reversals mid-way
    }


def _cos32(v):
    """cos in double, rounded to float32 -- what the compiled kernel does.

    numpy evaluates np.cos on a float32 array in float32 and numba's
    math.cos evaluates in double and rounds, and the two disagree in the
    last bit. That was invisible until fitness started counting energy
    spent, which sums speed squared over a lifetime and carried the
    difference straight into the score. The double-then-round version is
    the more accurate of the two, so it is the definition.
    """
    return np.cos(v.astype(np.float64)).astype(F32)


def _sin32(v):
    return np.sin(v.astype(np.float64)).astype(F32)


def brain_cost(brains):
    """-> (P,) float32 energy per tick charged for carrying this brain.

    Both backends call this rather than each computing it. They did compute
    it separately, with one multiplying NEURON_COST into an int64 array and
    rounding afterwards and the other multiplying in float32 throughout,
    and the last bit of difference was enough to cost the two backends
    their bit-exact agreement.
    """
    return (NEURON_COST * brains.n_hidden().astype(F32)).astype(F32)


def _patches(rng, n_worlds, n, sigma=PATCH_SIGMA):
    """-> (n_worlds, GRID, GRID) of summed gaussian bumps on a torus."""
    ax = np.arange(GRID, dtype=F32)
    c = (rng.random((2, n_worlds, n)).astype(F32) * GRID)
    dx = np.abs(ax[None, None, :] - c[0][:, :, None])        # (worlds, n, GRID)
    dy = np.abs(ax[None, None, :] - c[1][:, :, None])
    np.minimum(dx, GRID - dx, out=dx)                        # wrap
    np.minimum(dy, GRID - dy, out=dy)
    g = np.exp(-(dy[:, :, :, None] ** 2 + dx[:, :, None, :] ** 2)
               / (2 * sigma ** 2)).sum(1).astype(F32)
    np.clip(g, 0.0, 1.0, out=g)
    g[g < 0.05] = 0.0
    return g


class Episode:
    """One batch of worlds, identical for every brain that runs in it.

    cue_mode is the lesion handle: "intact" announces the truth, "none"
    never announces, "lying" announces the reverse in half the worlds. A
    brain that navigates by memory of the cue is wrecked by "lying"; a
    brain that taste-tests does not notice. That is how the report tells
    the two strategies apart.
    """

    def __init__(self, seed, n_worlds, d, cue_mode="intact", noise_scale=1.0):
        self.n = n_worlds
        self.dial = dials(d)
        self.cue_mode = cue_mode
        rng = np.random.default_rng(seed)

        self.A0 = _patches(rng, n_worlds, N_PATCH_A)
        self.B0 = _patches(rng, n_worlds, self.dial["n_patch_b"])
        self.pol0 = np.where(rng.random(n_worlds) < 0.5, 1.0, -1.0).astype(F32)
        self.x0 = (rng.random(n_worlds) * GRID).astype(F32)
        self.y0 = (rng.random(n_worlds) * GRID).astype(F32)
        self.th0 = (rng.random(n_worlds) * 2 * np.pi).astype(F32)
        self.noise = (rng.standard_normal((STEPS, n_worlds, N_IN))
                      * self.dial["noise"] * noise_scale).astype(F32)
        lie = np.where(rng.random(n_worlds) < 0.5, -1.0, 1.0).astype(F32)

        flips = (np.sort(rng.choice(np.arange(STEPS // 4, STEPS - 12),
                                    size=self.dial["flips"], replace=False))
                 if self.dial["flips"] else np.zeros(0, dtype=int))
        self.flip_at = flips

        # --- the schedules, built once --------------------------------
        ann = self.dial["announce"]
        lit = np.zeros(STEPS, dtype=bool)
        lit[:ann] = True
        for fs in flips:                      # a brief re-announcement
            lit[fs:fs + max(3, ann // 3)] = True

        # polarity at tick t is pol0 flipped once per flip that has happened
        n_flipped = np.searchsorted(flips, np.arange(STEPS), side="right")
        sign = np.where(n_flipped % 2 == 0, 1.0, -1.0).astype(F32)
        self.pol_ts = (self.pol0[None, :] * sign[:, None]).astype(F32)
        shown = self.pol_ts * (lie[None, :] if cue_mode == "lying" else 1.0)
        self.cue_ts = np.where(lit[:, None] & (cue_mode != "none"),
                               shown, 0.0).astype(F32)

        dr = self.dial["drift"]
        ts = np.arange(STEPS)
        self.drift_x = np.round(dr * ts * 0.5).astype(np.intp) % GRID
        self.drift_y = np.round(dr * ts * 0.3).astype(np.intp) % GRID

        # the normalising constant: the energy in the food that was there to
        # be had, under the polarity the episode opened with. Floored because
        # it is a denominator and a world with no food at all would otherwise
        # score every animal at infinity.
        good0 = np.where(self.pol0[:, None, None] > 0, self.A0, self.B0)
        self.available = np.maximum(FOOD_VALUE * good0.sum((1, 2)),
                                    1e-3).astype(F32)

    # -----------------------------------------------------------------
    def run(self, brains: Brains, trace=None, backend="auto"):
        """-> (scores (P, n_worlds) normalised, extras dict)."""
        if backend == "auto":
            from mote import fastsim
            backend = "fast" if (fastsim.AVAILABLE and trace is None) else "ref"
        if backend == "fast":
            from mote import fastsim
            return fastsim.run(self, brains)
        return self._run_ref(brains, trace)

    def _run_ref(self, brains: Brains, trace=None):
        """The reference implementation: readable, vectorised, slow.

        fastsim.py must agree with this. It is not dead code -- it is what
        the compiled kernel is checked against, and the only version worth
        reading to find out what the world actually does.
        """
        p, w = brains.size, self.n
        f = p * w
        gg = GRID * GRID
        WT, beff = brains.wiring()

        A = np.tile(self.A0, (p, 1, 1)).reshape(-1)   # flat; animal = b*w + i
        B = np.tile(self.B0, (p, 1, 1)).reshape(-1)
        x = np.tile(self.x0, p).copy()
        y = np.tile(self.y0, p).copy()
        th = np.tile(self.th0, p).copy()
        energy = np.full(f, START_ENERGY, dtype=F32)
        alive = np.ones(f, dtype=bool)
        gained = np.zeros(f, dtype=F32)
        lost = np.zeros(f, dtype=F32)
        spent = np.zeros(f, dtype=F32)
        bites = np.zeros(f, dtype=F32)

        h = np.zeros((p, w, N_MAX), dtype=F32)
        senses = np.zeros((f, N_IN), dtype=F32)
        s3 = senses.reshape(p, w, N_IN)               # a view, for broadcasting
        base_off = (np.arange(f) * gg).astype(np.intp)
        ca, sa = F32(np.cos(ANT_ANG)), F32(np.sin(ANT_ANG))
        harm = F32(self.dial["poison_harm"])
        tg = F32(self.dial["taste_gain"])
        base = F32(self.dial["base_cost"]) + np.repeat(brain_cost(brains), w)
        frames = [] if trace is not None else None

        for t in range(STEPS):
            pol_mask = np.repeat(self.pol_ts[t] > 0, 1)
            pol_mask = np.tile(pol_mask, p)
            ox, oy = self.drift_x[t], self.drift_y[t]
            ct, st = _cos32(th), _sin32(th)

            def cell(px, py):
                return base_off + (((np.floor(py).astype(np.intp) + oy) % GRID)
                                   * GRID
                                   + ((np.floor(px).astype(np.intp) + ox) % GRID))

            here = cell(x, y)
            for k, ds in ((0, sa), (1, -sa)):
                idx = cell(x + ANT_R * (ct * ca - st * ds),
                           y + ANT_R * (st * ca + ct * ds))
                senses[:, k] = A[idx]
                senses[:, 2 + k] = B[idx]

            a_here, b_here = A[here], B[here]
            good = np.where(pol_mask, a_here, b_here)
            bad = np.where(pol_mask, b_here, a_here)

            senses[:, 4] = tg * (good - bad)
            senses[:, 5] = energy - START_ENERGY
            s3[:, :, 6] = self.cue_ts[t]                 # (w,) over p
            senses[:, 7] = 1.0
            s3 += self.noise[t]
            senses *= alive[:, None]

            h = step(h, WT, beff, s3)
            out = h[:, :, N_IN:N_IN + 2].reshape(f, 2)

            act = alive & ((a_here + b_here) > 0.01)
            gained += np.where(act, FOOD_VALUE * good, 0.0)
            lost += np.where(act, harm * bad, 0.0)
            bites += act
            eaten = here[act]
            A[eaten] = 0.0
            B[eaten] = 0.0

            th = th + out[:, 0] * MAX_TURN * alive
            speed = (out[:, 1] + 1.0) * (0.5 * MAX_SPEED) * alive
            x = x + speed * _cos32(th)
            y = y + speed * _sin32(th)

            burn = (base + MOVE_COST * speed * speed) * alive
            spent += burn
            energy = energy + np.where(act, FOOD_VALUE * good - harm * bad, 0.0)
            energy = energy - burn
            np.clip(energy, -0.1, MAX_ENERGY, out=energy)
            alive &= energy > 0.0

            if frames is not None:
                bi, wi = trace
                j = bi * w + wi
                frames.append({
                    "t": t, "x": float(x[j]) , "y": float(y[j]),
                    "th": float(th[j]), "energy": float(energy[j]),
                    "alive": bool(alive[j]), "cue": float(self.cue_ts[t][wi]),
                    "pol": float(self.pol_ts[t][wi]), "ate": bool(act[j]),
                    "good": float(good[j]), "bad": float(bad[j]),
                    "ox": int(ox), "oy": int(oy),
                    "A": A[base_off[j]:base_off[j] + gg].reshape(GRID, GRID).copy(),
                    "B": B[base_off[j]:base_off[j] + gg].reshape(GRID, GRID).copy()})

        return self._finish(gained, lost, spent, bites, alive, p, w, frames)

    def _finish(self, gained, lost, spent, bites, alive, p, w, frames=None):
        """Score is net energy over a lifetime, as a fraction of the food
        that was there to be had."""
        net = (gained - lost - spent).reshape(p, w)
        score = net / self.available[None, :]
        return score.astype(F32), {
            "gained": gained.reshape(p, w) / self.available[None, :],
            "lost": lost.reshape(p, w) / self.available[None, :],
            "spent": spent.reshape(p, w) / self.available[None, :],
            "bites": bites.reshape(p, w),
            "alive": alive.reshape(p, w).mean(1),
            "frames": frames,
        }
