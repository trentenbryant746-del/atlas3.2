"""
Time as a fourth type system: nothing binds before its parts exist.

Dimensions prune by physical quantity. Conservation prunes by quantum
number. Both are timeless. EPOCH prunes by causality, and it is independent
of the other two: carbon is dimensionally fine and perfectly charge-neutral
at t = 3 minutes, and it cannot exist, because the triple-alpha process
needs stars and there are none yet.

So every element carries the earliest epoch at which it can exist, and a
binding is refused when any constituent postdates it. That is a CONTEXT
TOKEN in the literal sense: the token says when, and a compound's timeline
is the ordered list of its constituents' epochs.

WHY THE BIG BANG IS NOT A VARIETY GENERATOR. It runs for about twenty
minutes and produces five nuclides. There is no stable mass-5 or mass-8
nucleus, so the chain from helium upward has no bridge, and by the time
three-body collisions could cross it the universe is too cool and too
sparse. Everything past lithium waits on stellar timescales. Complexity is
a function of time, not of the bang -- which is the whole reason a time
layer buys anything.
"""
from __future__ import annotations

from dataclasses import dataclass

# (label, t after the Big Bang in seconds, what the epoch does)
EPOCHS = [
    ("planck",        1e-43, "quantum gravity; no structure survives"),
    ("quark",         1e-12, "quarks unbound; no hadrons"),
    ("hadron",        1e-6,  "quarks confine: protons and neutrons exist"),
    ("lepton",        1.0,   "neutrinos decouple; n/p ratio freezes"),
    ("bbn",           180.0, "primordial nucleosynthesis: H, D, He3, He4, Li7"),
    ("recombination", 1.2e13, "atoms form; the universe goes transparent"),
    ("first_stars",   6.3e15, "population III ignite: hydrogen burning"),
    ("stellar_c",     3.2e16, "triple-alpha: carbon, oxygen"),
    ("supernova",     9.5e16, "elements to the iron peak, then r-process"),
    ("ns_merger",     3.2e17, "heavy r-process: gold, platinum, uranium"),
]
T_OF = {name: t for name, t, _ in EPOCHS}
ORDER = {name: i for i, (name, _, _) in enumerate(EPOCHS)}

# earliest epoch at which each species can exist
ORIGIN = {
    "proton": "hadron", "neutron": "hadron", "electron": "lepton",
    "H": "bbn", "D": "bbn", "He3": "bbn", "He4": "bbn", "Li7": "bbn",
    "Be": "first_stars",
    "C": "stellar_c", "N": "stellar_c", "O": "stellar_c",
    "Ne": "supernova", "Mg": "supernova", "Si": "supernova",
    "S": "supernova", "Ca": "supernova", "Fe": "supernova", "Ni": "supernova",
    "Ag": "ns_merger", "Au": "ns_merger", "Pt": "ns_merger", "U": "ns_merger",
    "P": "supernova",
}

# BBN's actual output. Five nuclides, and the reason it stops.
BBN_YIELD = {"H": 0.75, "He4": 0.25, "D": 2.5e-5, "He3": 1e-5, "Li7": 5e-10}
BBN_BARRIER = ("no stable nucleus at mass 5 or 8, so the chain from He4 has "
               "no two-body bridge; three-body (triple-alpha) needs stellar "
               "densities and timescales")


@dataclass
class Dated:
    label: str
    epoch: str

    @property
    def t(self):
        return T_OF[self.epoch]


def earliest(species):
    return ORIGIN.get(species)


def can_bind(parts, at_epoch):
    """-> (ok, reason). Causality: every constituent must already exist."""
    if at_epoch not in ORDER:
        return False, f"unknown epoch {at_epoch!r}"
    late = [(p, ORIGIN[p]) for p in parts
            if p in ORIGIN and ORDER[ORIGIN[p]] > ORDER[at_epoch]]
    if late:
        p, e = late[0]
        return False, (f"{p} does not exist until {e} "
                       f"(t={T_OF[e]:.1e}s); asked at {at_epoch} "
                       f"(t={T_OF[at_epoch]:.1e}s)")
    unknown = [p for p in parts if p not in ORIGIN]
    if unknown:
        return False, f"no origin epoch on record for {unknown}"
    return True, f"all constituents exist by {at_epoch}"


def timeline(parts):
    """the context token: an ordered list of when each part became possible"""
    known = [(p, ORIGIN[p]) for p in parts if p in ORIGIN]
    known.sort(key=lambda kv: ORDER[kv[1]])
    return [f"{p}@{e}(t={T_OF[e]:.1e}s)" for p, e in known]
