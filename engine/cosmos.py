"""
A universe you can audit: matter tracked from the Big Bang forward.

The point is not a cosmological simulation -- a real one is a supercomputer
problem. The point is that every gram is ACCOUNTED FOR, so the model can be
checked rather than admired:

    mass conservation     ejecta + remnant = progenitor, every generation
    monotonic enrichment  metallicity never decreases down a lineage
    epoch compliance      no element appears before engine/epochs.py allows
    convergence           the simulated composition is compared against the
                          OBSERVED solar abundances, and the distance is
                          reported rather than asserted to be small

A star's provenance is its prompt: which generation, from whose ejecta,
carrying which elements produced when. That chain is the complex object,
not the star's parameters.

SEEDED IS NOT REALISTIC -- the same caution as mixtures. Structure here is
reproducible from a seed; whether it resembles the real sky is a separate
question, answered by the convergence measurement and not by the seed.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field

from engine.epochs import ORIGIN, ORDER, T_OF

PRIMORDIAL = {"H": 0.75, "He4": 0.25}

# fraction of a star's mass returned as each element, by generation type.
# Massive Pop III stars make the alpha elements; later generations add
# iron-peak from Ia supernovae; r-process needs compact-object mergers.
YIELDS = {
    "popIII": ({"C": 0.020, "O": 0.055, "Ne": 0.010, "Mg": 0.007,
                "Si": 0.006, "S": 0.003, "Ca": 0.001, "Fe": 0.004},
               "stellar_c", 0.45),
    "popII":  ({"C": 0.015, "N": 0.004, "O": 0.040, "Ne": 0.008,
                "Mg": 0.006, "Si": 0.007, "S": 0.003, "Ca": 0.001,
                "Fe": 0.011}, "supernova", 0.35),
    "popI":   ({"C": 0.012, "N": 0.005, "O": 0.030, "Ne": 0.006,
                "Mg": 0.005, "Si": 0.006, "S": 0.002, "Ca": 0.001,
                "Fe": 0.013, "Ag": 2e-7, "Au": 4e-8, "U": 1e-8},
               "ns_merger", 0.30),
}


@dataclass
class Star:
    sid: str
    generation: int
    pop: str
    mass: float
    composition: dict
    parents: list = field(default_factory=list)
    epoch: str = "first_stars"

    def metallicity(self):
        """Z: mass fraction in anything heavier than helium"""
        return sum(v for k, v in self.composition.items()
                   if k not in ("H", "He4", "He3", "D", "Li7"))

    def token(self):
        body = "|".join(f"{k}:{self.composition[k]:.8f}"
                        for k in sorted(self.composition))
        return hashlib.sha256(f"{self.sid}|{body}".encode()).hexdigest()[:12]

    def prompt(self):
        """the star's provenance chain, which is the complex object"""
        return (f"generation {self.generation} {self.pop} star {self.sid}, "
                f"{self.mass:.2f} solar masses, Z={self.metallicity():.4f}, "
                f"from {self.parents or ['primordial gas']}, "
                f"earliest constituent epoch "
                f"{min((ORIGIN[e] for e in self.composition if e in ORIGIN), key=lambda e: ORDER[e])}")


def normalise(d):
    t = sum(d.values())
    return {k: v / t for k, v in d.items() if v > 0}


# How a yield scales with progenitor mass. Massive stars make the alpha
# elements in hydrostatic burning; lower-mass stars contribute carbon and
# nitrogen through dredge-up. Fixed per-population yields made every star of
# a generation identical, so 400 seeded universes came out bit-identical --
# correct location, zero diversity, which is the opposite failure from a
# generator whose support misses the target entirely.
MASS_SCALING = {
    "O": 1.0, "Ne": 1.0, "Mg": 1.0, "Si": 0.8, "S": 0.8, "Ca": 0.6,  # alpha
    "C": -0.6, "N": -0.8,                                            # dredge-up
    "Fe": 0.3, "Ag": 0.5, "Au": 0.5, "U": 0.5,
}
M_REF = 18.0          # solar masses


def scaled_yield(el, base, mass):
    """base * (M/M_ref)^k, k from MASS_SCALING. k>0 rises with mass."""
    k = MASS_SCALING.get(el, 0.0)
    return base * (mass / M_REF) ** k


def evolve(star):
    """-> (ejecta composition, ejected mass, remnant mass). Mass is conserved."""
    yields, epoch, eject_frac = YIELDS[star.pop]
    ejected = star.mass * eject_frac
    remnant = star.mass - ejected
    out = dict(star.composition)
    made = 0.0
    for el, frac in yields.items():
        f = scaled_yield(el, frac, star.mass)
        out[el] = out.get(el, 0.0) + f
        made += f
    # what the star fused came out of its hydrogen
    out["H"] = max(0.0, out.get("H", 0.0) - made)
    return normalise(out), ejected, remnant, epoch


def run(generations=4, seed="universe-0", stars_per_gen=3, dilution=0.0):
    """dilution: mass of pristine gas each unit of ejecta mixes into.

    Without it the model feeds 100% of a generation's ejecta into the next,
    and over-enriches wildly -- the first run reached Z = 0.28 against a
    solar 0.017, more than an order of magnitude too metal-rich. Real ejecta
    disperses into a far larger reservoir that never formed stars, and only
    a few percent of gas is converted per generation. Omitting that was the
    error; the convergence measurement is what caught it.
    """
    gas = dict(PRIMORDIAL)
    pops = ["popIII", "popII", "popI", "popI"]
    all_stars, ledger = [], []
    prev = []
    for g in range(generations):
        pop = pops[min(g, len(pops) - 1)]
        gen = []
        for i in range(stars_per_gen):
            h = hashlib.sha256(f"{seed}|{g}|{i}".encode()).digest()
            mass = 8.0 + (int.from_bytes(h[:4], "big") / 2**32) * 22.0
            s = Star(sid=f"g{g}s{i}", generation=g, pop=pop, mass=mass,
                     composition=dict(gas),
                     parents=[p.sid for p in prev[:2]],
                     epoch=YIELDS[pop][1])
            ej, em, rm, ep = evolve(s)
            ledger.append({"star": s.sid, "progenitor_mass": s.mass,
                           "ejected": em, "remnant": rm,
                           "conserved": abs((em + rm) - s.mass) < 1e-9})
            gen.append((s, ej, em))
            all_stars.append(s)
        # next generation's gas: mass-weighted mean of this generation's ejecta
        tot = sum(em for _, _, em in gen)
        mixed = {}
        for _, ej, em in gen:
            for k, v in ej.items():
                mixed[k] = mixed.get(k, 0.0) + v * em / tot
        if dilution > 0:
            # ejecta (mass 1) mixes into `dilution` masses of pristine gas
            blended = {}
            for k in set(mixed) | set(PRIMORDIAL):
                blended[k] = (mixed.get(k, 0.0) * 1.0
                              + PRIMORDIAL.get(k, 0.0) * dilution) / (1 + dilution)
            mixed = blended
        gas = normalise(mixed)
        prev = [s for s, _, _ in gen]
    return all_stars, gas, ledger


def distance_to(observed, simulated):
    """mean absolute difference over the elements both record"""
    keys = set(observed) & set(simulated)
    if not keys:
        return None, 0
    return sum(abs(observed[k] - simulated[k]) for k in keys) / len(keys), len(keys)
