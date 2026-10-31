"""
The little guy's brain.

A tiny fully-recurrent network, stored for a whole population at once so
that one generation is a handful of numpy calls rather than a Python loop
over individuals.

The state vector has N_MAX slots, laid out like this:

    [0 .. N_IN)            input nodes, overwritten by the senses each step
    [N_IN .. HID0)         output nodes, read as turn and thrust
    [HID0 .. N_MAX)        hidden slots, each either ON or OFF

Nothing is ever resized. A brain "grows" by switching a hidden slot on and
"shrinks" by switching it off, which keeps the entire population in one
rectangular array -- the only reason deep time is affordable here.

W[p, i, j] is the weight from node j to node i in genome p, so the update is

    pre = W @ h + b ;  h = squash(pre) ;  h[inputs] = senses

THE SQUASH IS v / (1 + |v|), NOT tanh. Same sigmoid shape, same (-1, 1)
range, and no transcendental: with four of them per tick per animal, tanh
was a third of the whole cost of deep time. Nothing in the model wants the
particular curvature of tanh, so it buys nothing and is not worth an hour
of wall clock per million generations.

Connections into input nodes are permanently off: those rows get overwritten
by the senses, so a weight there would be a gene that cannot be expressed.
"""
from __future__ import annotations

import numpy as np

# --- the sense channels, in order ---------------------------------------
#   0  flavour-A density, left antenna
#   1  flavour-A density, right antenna
#   2  flavour-B density, left antenna
#   3  flavour-B density, right antenna
#   4  taste of the cell underfoot: signed, and you have already eaten it
#   5  own energy, centred on the starting level
#   6  the cue: +1 if A is food this episode, -1 if B is, 0 once it stops
#   7  constant 1.0
N_IN = 8
N_OUT = 2                  # turn, thrust
HID0 = N_IN + N_OUT
N_MAX = 40
N_HID = N_MAX - HID0       # 30 hidden slots

F32 = np.float32


class Brains:
    """A population of genomes as five rectangular arrays."""

    __slots__ = ("W", "b", "node_on", "conn_on", "sigma")

    def __init__(self, W, b, node_on, conn_on, sigma):
        self.W = W                  # (P, N, N) float32
        self.b = b                  # (P, N)    float32
        self.node_on = node_on      # (P, N)    bool
        self.conn_on = conn_on      # (P, N, N) bool
        self.sigma = sigma          # (P,)      float32, self-adapting

    # -- construction ----------------------------------------------------
    @property
    def size(self) -> int:
        return self.W.shape[0]

    @staticmethod
    def seed_population(p: int, rng, hidden_on: int = 2, density: float = 0.35,
                        sigma: float = 0.08):
        """The ancestor: `hidden_on` hidden neurons and a sparse wiring."""
        W = (rng.standard_normal((p, N_MAX, N_MAX)) * 0.5).astype(F32)
        b = (rng.standard_normal((p, N_MAX)) * 0.1).astype(F32)

        node_on = np.zeros((p, N_MAX), dtype=bool)
        node_on[:, :HID0] = True                      # senses and muscles always
        node_on[:, HID0:HID0 + hidden_on] = True

        conn_on = rng.random((p, N_MAX, N_MAX)) < density
        conn_on[:, :N_IN, :] = False                  # input rows are overwritten
        return Brains(W, b, node_on, conn_on,
                      np.full(p, sigma, dtype=F32))

    def take(self, idx) -> "Brains":
        """A new population made of the genomes at `idx` (copies)."""
        return Brains(self.W[idx].copy(), self.b[idx].copy(),
                      self.node_on[idx].copy(), self.conn_on[idx].copy(),
                      self.sigma[idx].copy())

    # -- the forward pass ------------------------------------------------
    def wiring(self):
        """-> (WT, beff) with every mask already folded in.

        Done once per generation, not once per step: the masks only change
        when the genomes do.
        """
        m = self.node_on
        W = self.W * self.conn_on
        W *= m[:, :, None]          # target node off -> it receives nothing
        W *= m[:, None, :]          # source node off -> it sends nothing
        WT = np.ascontiguousarray(W.swapaxes(1, 2))
        return WT, (self.b * m).astype(F32)

    def n_hidden(self):
        """Live hidden neurons per genome. Cheap: the full sizes() scans the
        (pop, 40, 40) connection array, and the energy budget needs this
        every generation."""
        return self.node_on[:, HID0:].sum(1)

    def sizes(self):
        """-> (hidden neurons on, live connections) per genome."""
        hid = self.node_on[:, HID0:].sum(1)
        m = self.node_on
        live = (self.conn_on & m[:, :, None] & m[:, None, :]).sum((1, 2))
        return hid, live

    # -- variation -------------------------------------------------------
    def mutate(self, rng, p_conn=0.03, p_drop=0.02, p_grow=0.006,
               p_shrink=0.006, tau=0.12):
        """In place. Weights, wiring, and the mutation rate itself.

        TWO THINGS HERE WERE WRONG THE FIRST TIME AND BOTH MATTERED.

        The structural rates were per SLOT, not per genome. At 0.03 a slot
        across 784 slots every genome gained twenty-three connections per
        generation and the wiring saturated inside twenty generations --
        every brain fully connected, no structure left for selection to
        choose between.

        And a new connection arrived carrying a random weight, which makes
        every structural mutation an immediate behavioural insult. A brain
        one neuron larger was always worse at first, so selection pruned
        and the population shrank to the floor. New wiring now arrives at
        weight ZERO: expressed, inherited, and behaviourally silent until
        ordinary weight mutation finds a use for it. That is the whole
        reason a lineage here can get bigger instead of only better tuned.

        AND THE RATES ARE SYMMETRIC ON PURPOSE. p_grow was 0.010 against a
        p_shrink of 0.004, so brains grew two and a half times more readily
        than they shrank and every lineage drifted to the array ceiling.
        That measured my rates, not the animal. Equal rates make size a
        thing selection decides: growth has to earn its metabolism.
        """
        p = self.size

        # the step size is a gene too, so the lineage tunes how boldly it
        # searches instead of being told
        self.sigma *= np.exp(tau * rng.standard_normal(p)).astype(F32)
        np.clip(self.sigma, 0.005, 0.6, out=self.sigma)

        # weights: only where there is a connection to carry one. The dense
        # version drew 100k normals a generation to use 3k of them.
        gi, ti, si = np.nonzero(self.conn_on)
        if gi.size:
            self.W[gi, ti, si] += (rng.standard_normal(gi.size).astype(F32)
                                   * self.sigma[gi])
        self.b += (rng.standard_normal((p, N_MAX)).astype(F32)
                   * self.sigma[:, None] * 0.5)

        # --- structural, one event per genome at most ------------------
        on = self.node_on
        for r in np.nonzero(rng.random(p) < p_conn)[0]:       # gain a wire
            tgt = np.nonzero(on[r])[0]
            tgt = tgt[tgt >= N_IN]
            src = np.nonzero(on[r])[0]
            i, j = tgt[rng.integers(len(tgt))], src[rng.integers(len(src))]
            self.conn_on[r, i, j] = True
            self.W[r, i, j] = 0.0                             # silent on arrival

        for r in np.nonzero(rng.random(p) < p_drop)[0]:       # lose a wire
            live = np.nonzero(self.conn_on[r])
            if live[0].size:
                k = rng.integers(live[0].size)
                self.conn_on[r, live[0][k], live[1][k]] = False

        for r in np.nonzero(rng.random(p) < p_grow)[0]:       # gain a neuron
            free = np.nonzero(~on[r, HID0:])[0]
            if free.size:
                slot = HID0 + free[0]
                self.node_on[r, slot] = True
                # wired in, but at zero: it changes nothing until it earns it
                src = np.nonzero(self.node_on[r])[0]
                self.conn_on[r, slot, src[rng.integers(len(src))]] = True
                outs = src[src >= N_IN]
                self.conn_on[r, outs[rng.integers(len(outs))], slot] = True
                self.W[r, slot, :] = 0.0
                self.W[r, :, slot] = 0.0

        for r in np.nonzero(rng.random(p) < p_shrink)[0]:     # lose a neuron
            live = np.nonzero(self.node_on[r, HID0:])[0]
            if live.size > 1:
                self.node_on[r, HID0 + live[rng.integers(live.size)]] = False

    @staticmethod
    def concat(parts):
        return Brains(np.concatenate([p.W for p in parts]),
                      np.concatenate([p.b for p in parts]),
                      np.concatenate([p.node_on for p in parts]),
                      np.concatenate([p.conn_on for p in parts]),
                      np.concatenate([p.sigma for p in parts]))

    # -- the fossil record ----------------------------------------------
    def save(self, path):
        np.savez_compressed(path, W=self.W, b=self.b, node_on=self.node_on,
                            conn_on=self.conn_on, sigma=self.sigma)

    @staticmethod
    def load(path) -> "Brains":
        d = np.load(path)
        return Brains(d["W"], d["b"], d["node_on"], d["conn_on"], d["sigma"])


def step(h, WT, beff, senses):
    """One tick of every brain in the population at once.

    h: (P, B, N) -- P genomes each living in B worlds.
    """
    pre = h @ WT
    pre += beff[:, None, :]
    den = np.abs(pre)
    den += 1.0
    pre /= den                      # squash(v) = v / (1 + |v|)
    pre[:, :, :N_IN] = senses
    return pre
