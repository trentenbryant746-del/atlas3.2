"""
The same world as world.py, compiled, and checked against it.

Deep time is only affordable because of this file. The vectorised reference
spends its generation inside numpy call overhead -- the arrays are a few
hundred elements wide, so every tick is ninety numpy calls each doing a
microsecond of real work. Rewriting the tick as one scalar loop per animal
removes all of it and, more importantly, lets the brain exploit its own
sparsity: a genome with four live neurons does sixteen multiply-adds, not
the 1,600 a dense 40x40 matrix would charge it.

    reference, numpy        ~19 ms per generation
    this, 4 threads          ~2 ms per generation

Two rules this file lives under.

ARITHMETIC IN FLOAT32, LIKE THE REFERENCE, and every constant arrives
already cast. This matters more than ordinary rounding hygiene: a brain
that crosses a decision boundary one tick earlier eats something it
otherwise would not, and the two backends would then tell different
stories rather than the same story to different precision.

HOW CLOSELY THEY AGREE, MEASURED. Across difficulties and seeds, the two
backends produce bit-identical BEHAVIOUR -- the same food eaten, the same
poison eaten, the same number of mouthfuls, the same animals dead at the
same tick. The energy ledger agrees to about one float32 ULP per tick,
which reaches 1.5e-8 of a score of order 0.1 by the end of an episode.

That last ULP was chased and not caught. numba evaluates a float32
expression through double internally and rounds on store, and matching
numpy exactly would mean matching its operation grouping and its
intermediate precision at every step; explicit casts at each stage and
replicating numpy left-to-right grouping both failed to close it. Since
energy is itself a sense channel, the backends could in principle diverge
chaotically from that ULP rather than merely differ by it -- so the test
asserts identical behaviour and a 1e-6 score tolerance, not equality, and
world.py remains the definition of the game.
"""
from __future__ import annotations

import math

import numpy as np

from mote.brain import N_IN, N_MAX
from mote import world as _w
from mote.world import (ANT_ANG, ANT_R, FOOD_VALUE, GRID, MAX_ENERGY,
                        MAX_SPEED, MAX_TURN, MOVE_COST, START_ENERGY, STEPS)

F32 = np.float32

try:
    from numba import njit, prange
    AVAILABLE = True
except Exception:                                  # pragma: no cover
    AVAILABLE = False

    def njit(*a, **k):
        def wrap(fn):
            return fn
        return wrap
    prange = range


@njit(cache=True, parallel=True, fastmath=False, nogil=True)
def _kernel(Wm, beff, src, n_src, tgt, n_tgt,
            A, B, x, y, th, energy, alive, gained, lost, spent, bites,
            h, nh, noise, cue_ts, pol_ts, drift_x, drift_y, brain_cost,
            n_worlds, grid, steps, ant_r, ca, sa, max_turn, max_speed,
            food_value, harm, taste_gain, base_cost, move_cost,
            max_energy, start_energy):
    f = x.shape[0]
    gg = grid * grid
    zero = F32(0.0)
    one = F32(1.0)
    half_speed = F32(F32(0.5) * max_speed)

    for a in prange(f):
        bi = a // n_worlds
        wi = a - bi * n_worlds
        off = a * gg
        ns = n_src[bi]
        nt = n_tgt[bi]
        # the fixed part of the metabolic bill, summed in the same order as
        # the reference: a three-term sum inside the tick loop rounded
        # differently and the two backends stopped agreeing bit for bit
        bc = base_cost + brain_cost[bi]

        for t in range(steps):
            al = alive[a]
            alf = one if al else zero
            ox = drift_x[t]
            oy = drift_y[t]
            ct = F32(math.cos(th[a]))
            st = F32(math.sin(th[a]))

            cxh = (int(math.floor(x[a])) + ox) % grid
            cyh = (int(math.floor(y[a])) + oy) % grid
            here = off + cyh * grid + cxh

            a_here = A[here]
            b_here = B[here]
            if pol_ts[t, wi] > zero:
                good = a_here
                bad = b_here
            else:
                good = b_here
                bad = a_here

            # --- the senses ----------------------------------------
            s0 = zero
            s1 = zero
            s2 = zero
            s3 = zero
            for k in range(2):
                ds = sa if k == 0 else -sa
                ax = x[a] + ant_r * (ct * ca - st * ds)
                ay = y[a] + ant_r * (st * ca + ct * ds)
                ix = (int(math.floor(ax)) + ox) % grid
                iy = (int(math.floor(ay)) + oy) % grid
                j = off + iy * grid + ix
                if k == 0:
                    s0 = A[j]
                    s2 = B[j]
                else:
                    s1 = A[j]
                    s3 = B[j]

            sv0 = (s0 + noise[t, wi, 0]) * alf
            sv1 = (s1 + noise[t, wi, 1]) * alf
            sv2 = (s2 + noise[t, wi, 2]) * alf
            sv3 = (s3 + noise[t, wi, 3]) * alf
            sv4 = (taste_gain * (good - bad) + noise[t, wi, 4]) * alf
            sv5 = (energy[a] - start_energy + noise[t, wi, 5]) * alf
            sv6 = (cue_ts[t, wi] + noise[t, wi, 6]) * alf
            sv7 = (one + noise[t, wi, 7]) * alf

            # --- the brain, over live nodes only -------------------
            for ii in range(nt):
                i = tgt[bi, ii]
                acc = beff[bi, i]
                for jj in range(ns):
                    j = src[bi, jj]
                    acc += Wm[bi, i, j] * h[a, j]
                nh[a, i] = acc / (one + abs(acc))
            for ii in range(nt):
                i = tgt[bi, ii]
                h[a, i] = nh[a, i]
            h[a, 0] = sv0
            h[a, 1] = sv1
            h[a, 2] = sv2
            h[a, 3] = sv3
            h[a, 4] = sv4
            h[a, 5] = sv5
            h[a, 6] = sv6
            h[a, 7] = sv7

            out_turn = h[a, N_IN]
            out_thrust = h[a, N_IN + 1]

            # --- eat whatever is underfoot -------------------------
            if al and (a_here + b_here) > F32(0.01):
                gained[a] += food_value * good
                lost[a] += harm * bad
                bites[a] += one
                A[here] = zero
                B[here] = zero
                dE = food_value * good - harm * bad
            else:
                dE = zero

            # --- move, and pay for it ------------------------------
            th[a] += out_turn * max_turn * alf
            speed = (out_thrust + one) * half_speed * alf
            x[a] += speed * F32(math.cos(th[a]))
            y[a] += speed * F32(math.sin(th[a]))

            burn = (bc + move_cost * speed * speed) * alf
            spent[a] += burn
            e = energy[a] + dE - burn
            if e < F32(-0.1):
                e = F32(-0.1)
            elif e > max_energy:
                e = max_energy
            energy[a] = e
            if e <= zero:
                alive[a] = False


def _indices(brains):
    """Live-node index tables, padded, one row per genome."""
    on = brains.node_on
    p = on.shape[0]
    src = np.argsort(~on, axis=1, kind="stable").astype(np.intp)
    n_src = on.sum(1).astype(np.intp)
    tgt_mask = on.copy()
    tgt_mask[:, :N_IN] = False
    tgt = np.argsort(~tgt_mask, axis=1, kind="stable").astype(np.intp)
    n_tgt = tgt_mask.sum(1).astype(np.intp)
    return src, n_src, tgt, n_tgt


def run(ep, brains):
    """Same contract as Episode._run_ref, minus the trace."""
    p, w = brains.size, ep.n
    f = p * w
    gg = GRID * GRID

    m = brains.node_on
    Wm = (brains.W * brains.conn_on).astype(F32)
    Wm *= m[:, :, None]
    Wm *= m[:, None, :]
    beff = (brains.b * m).astype(F32)
    src, n_src, tgt, n_tgt = _indices(brains)
    # through the module, not a bound copy, so a calibration sweep can move
    # NEURON_COST and have both backends see it
    bcost = _w.brain_cost(brains)

    A = np.tile(ep.A0, (p, 1, 1)).reshape(-1).astype(F32)
    B = np.tile(ep.B0, (p, 1, 1)).reshape(-1).astype(F32)
    x = np.tile(ep.x0, p).astype(F32)
    y = np.tile(ep.y0, p).astype(F32)
    th = np.tile(ep.th0, p).astype(F32)
    energy = np.full(f, START_ENERGY, dtype=F32)
    alive = np.ones(f, dtype=np.bool_)
    gained = np.zeros(f, dtype=F32)
    lost = np.zeros(f, dtype=F32)
    spent = np.zeros(f, dtype=F32)
    bites = np.zeros(f, dtype=F32)
    h = np.zeros((f, N_MAX), dtype=F32)
    nh = np.zeros((f, N_MAX), dtype=F32)

    _kernel(Wm, beff, src, n_src, tgt, n_tgt,
            A, B, x, y, th, energy, alive, gained, lost, spent, bites,
            h, nh, ep.noise, ep.cue_ts, ep.pol_ts,
            ep.drift_x.astype(np.intp), ep.drift_y.astype(np.intp), bcost,
            w, GRID, STEPS, F32(ANT_R), F32(np.cos(ANT_ANG)),
            F32(np.sin(ANT_ANG)), F32(MAX_TURN), F32(MAX_SPEED),
            F32(FOOD_VALUE), F32(ep.dial["poison_harm"]),
            F32(ep.dial["taste_gain"]), F32(ep.dial["base_cost"]),
            F32(MOVE_COST), F32(MAX_ENERGY), F32(START_ENERGY))

    return ep._finish(gained, lost, spent, bites, alive, p, w)
