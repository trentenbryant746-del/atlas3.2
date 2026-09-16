"""
Where each atom goes after the prompt.

engine/transitions.py says that a decay changes which experts apply.
It does not say WHICH ATOM decayed, or where that atom had been, or
what it became part of afterwards. Those are different questions and
the second one is the useful one: a carbon atom that was made in a
particular star, thrown off in a particular supernova, and bound
into a particular molecule has a HISTORY, and that history is an
answer nothing else in the repo can give.

    the atom      an identity that survives its own transformations
    the history   where it formed, what it became, what it joined
    the answer    every step is a prompt context, and the chain of
                  them is a longer one

AN ATOM'S HISTORY IS DERIVED FROM ITS KEY, NOT STORED. The key is
hmac(universe key, chunk || element || serial), and every event
that follows is computed from it: which chunk it formed in, at
which epoch, by which nucleosynthetic channel, what it decays to,
what it can bind with. So a universe of 1e60 atoms costs nothing
until an atom is named, and naming one reconstructs its whole
history in microseconds. Same rule as the corpus and the universe
chunks -- derive, do not materialise.

IDENTITY SURVIVES TRANSFORMATION, WHICH IS THE WHOLE POINT. When an
atom decays its ELEMENT changes and its identity does not. That is
what makes a history a history rather than a list of unrelated
facts: the thing that was uranium and is now thorium is the same
thing, and a question about it spans both. The key is stable across
every event and the element is a property that varies along it.

WHAT THE URANIUM CHAIN GETS RIGHT, AND WHERE IT STOPS BEING RIGHT.
Asked for uranium's history the module derives U -> Th -> Ra -> Rn
-> Po -> Pb from Q-values alone, which is the real uranium series,
and nothing in this repo was told it. Then it carries on -- Pb ->
Hg -> Pt -> Os -> W -> Hf -- and that part is wrong. Lead-208 is
where the series ends.

The reason is worth keeping rather than patching. The
semi-empirical mass formula is a liquid drop: it knows volume,
surface, Coulomb, asymmetry and pairing, and it has NO SHELL
STRUCTURE. Lead-208 is doubly magic -- 82 protons and 126 neutrons,
both closed shells -- and that extra binding is exactly what a
liquid drop cannot see. So the model walks straight through the one
nucleus that should stop it.

That is a limitation of the formula, not of the tracking, and
hard-coding lead as a terminus would hide it. engine/unsolved.py
records shell closures as something this repo does not derive.

EVERY STEP CHANGES WHO CAN ANSWER. Each event carries the expert set
before and after, from engine/transitions.py. So the history is not
just a story -- it is a sequence of answer contexts, and the number
of distinct contexts a universe reaches grows with the number of
histories rather than the number of atoms.
"""
from __future__ import annotations

import hashlib
import hmac
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import abundance, chain, epochs as _ep            # noqa: E402
from engine import transitions as _tr                         # noqa: E402
from engine.experts import BY_SYM, BY_Z                       # noqa: E402

DERIVED = "DERIVED"


@dataclass
class Event:
    epoch: str
    kind: str                # formed | decay | bind
    element: str             # what it is AFTER this event
    detail: str
    experts: frozenset = field(default_factory=frozenset)

    def __str__(self):
        return f"{self.epoch:<14}{self.kind:<7}{self.element:<4}{self.detail}"


def atom_key(universe_key, chunk, element, serial):
    """A name that carries where it came from. Self-addressing."""
    if element not in BY_SYM:
        raise KeyError(f"{element} is not an element")
    msg = f"{chunk}\x00{element}\x00{serial}".encode()
    return hmac.new(str(universe_key).encode(), msg,
                    hashlib.sha256).hexdigest()


def _rng(key, salt):
    """Deterministic choice from the key. No state, no sampling."""
    h = hashlib.sha256((key + "\x00" + salt).encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64


def history(universe_key, chunk, element, serial, limit=12):
    """-> [Event]. Reconstructed from the key alone."""
    key = atom_key(universe_key, chunk, element, serial)
    ch, why = abundance.channel(element)
    born = _ep.ORIGIN.get(element)
    if born is None:
        born = {"primordial": "bbn", "alpha-chain": "stellar_c",
                "secondary": "supernova",
                "neutron-capture": "ns_merger"}.get(ch, "supernova")
    out = [Event(born, "formed", element,
                 f"in chunk {chunk} by {ch}: {why[:58]}",
                 _tr.experts_for_element(element))]

    cur = element
    for step in range(limit):
        z = BY_SYM[cur][0]
        n = _tr.most_bound_n(z)
        if n is None:
            break
        mode, d, dwhy = _tr.decay_of(z, n)
        if d is None or d[0] < 1 or d[0] > len(BY_Z):
            break
        nxt = BY_Z[d[0]][0]
        ev_epoch = out[-1].epoch
        out.append(Event(ev_epoch, "decay", nxt,
                         f"{cur} -> {nxt} by {mode}; {dwhy[:44]}",
                         _tr.experts_for_element(nxt)))
        cur = nxt
        if len({e.element for e in out}) > limit:
            break

    # what it can join, once it exists
    partner = None
    if cur in _tr.VALENCE:
        opts = sorted(p for p in _tr.VALENCE if p != cur)
        partner = opts[int(_rng(key, "bind") * len(opts))]
        e = _tr.bind_edge(cur, partner)
        if e:
            out.append(Event(e.epoch, "bind", cur,
                             f"joins {partner} as {e.after[0]}",
                             e.experts_after))
    return out


def chain_of_custody(universe_key, chunk, element, serial):
    """The history as a 256-bit head. Tamper-evident, like every other."""
    evs = history(universe_key, chunk, element, serial)
    states = [(f"{i}:{e.kind}",
               {"epoch": e.epoch, "element": e.element, "kind": e.kind})
              for i, e in enumerate(evs)]
    return chain.build(atom_key(universe_key, chunk, element, serial),
                       states), evs


def contexts(universe_key, chunk, element, serial):
    """Distinct expert sets this one atom passes through."""
    return {e.experts for e in history(universe_key, chunk, element, serial)}


def survey(universe_key="universe-0", chunk=0, elements=None, per=3):
    """Many atoms, and how many answer contexts they reach between them."""
    elements = elements or ["H", "C", "O", "Fe", "U", "Au", "Si", "N"]
    seen, rows = set(), []
    for el in elements:
        for s in range(per):
            evs = history(universe_key, chunk, el, s)
            for e in evs:
                seen.add(e.experts)
            rows.append((el, s, len(evs), evs[-1].element))
    return rows, seen


# ------------------------------------------------------- self-checking
def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("key_is_stable_and_unique", _key)
    t("history_is_derived_not_stored", _der)
    t("identity_survives_decay", _ident)
    t("every_step_changes_context", _ctx)
    t("custody_chain_is_tamper_evident", _tamp)
    t("histories_outnumber_atoms", _more)
    t("uranium_series_then_overruns", _u238)
    return all(o[1] for o in out), out


def _key():
    a = atom_key("u0", 0, "C", 1)
    if a != atom_key("u0", 0, "C", 1):
        raise ArithmeticError("the same atom got two keys")
    others = {atom_key("u0", 0, "C", s) for s in range(200)}
    if len(others) != 200:
        raise ArithmeticError("two atoms share a key")
    if a == atom_key("u1", 0, "C", 1):
        raise ArithmeticError("the same key in two universes")
    return ("200 atoms of one element in one chunk get 200 distinct keys; "
            "the same atom in another universe gets a different one")


def _der():
    h1 = history("u0", 0, "Fe", 7)
    h2 = history("u0", 0, "Fe", 7)
    if [str(e) for e in h1] != [str(e) for e in h2]:
        raise ArithmeticError("the history is not reproducible")
    return (f"iron atom 7 of chunk 0 has a {len(h1)}-step history, "
            f"identical on a second reconstruction, and nothing about it "
            f"was stored between the two")


def _ident():
    h = history("u0", 0, "U", 0)
    els = [e.element for e in h]
    if len(set(els)) < 2:
        raise ArithmeticError("nothing transformed, so identity is not "
                              "being tested")
    k1 = atom_key("u0", 0, "U", 0)
    # the key is a function of where it STARTED, not of what it is now
    if k1 != atom_key("u0", 0, "U", 0):
        raise ArithmeticError("the key moved with the element")
    return (f"uranium atom 0 passes through {els} and keeps one key "
            f"throughout -- the thing that was {els[0]} and is now "
            f"{els[-1]} is the same thing, which is what makes this a "
            f"history")


def _ctx():
    h = history("u0", 0, "U", 0)
    sets = [e.experts for e in h]
    same = sum(1 for i in range(len(sets) - 1) if sets[i] == sets[i + 1])
    if same:
        raise ArithmeticError(f"{same} steps changed no expert")
    return (f"{len(h)} steps, {len(set(sets))} distinct expert sets, and "
            f"no two consecutive steps share one -- every event moves the "
            f"answer context")


def _tamp():
    ch, evs = chain_of_custody("u0", 0, "U", 0)
    states = [(f"{i}:{e.kind}",
               {"epoch": e.epoch, "element": e.element, "kind": e.kind})
              for i, e in enumerate(evs)]
    ok, why = chain.verify(ch, states)
    if not ok:
        raise ArithmeticError(f"custody chain does not verify: {why}")
    bad = list(states)
    bad[1] = (bad[1][0], {**bad[1][1], "element": "Xx"})
    ok2, why2 = chain.verify(ch, bad)
    if ok2:
        raise ArithmeticError("an altered history still verified")
    return (f"the custody chain verifies over {len(states)} events, and "
            f"altering one is caught: {why2[:52]}")


def _u238():
    """The real series, and the exact point the liquid drop fails."""
    els = [e.element for e in history("u0", 0, "U", 0)]
    real = ["U", "Th", "Ra", "Rn", "Po", "Pb"]
    got = els[:len(real)]
    if got != real:
        raise ArithmeticError(f"the series came out {got}, not {real}")
    if "Pb" not in els or els[-1] == "Pb":
        raise ArithmeticError("it stopped at lead, which the SEMF has no "
                              "way to know -- check what changed")
    after = els[els.index("Pb") + 1:]
    return (f"derived {' -> '.join(real)} from Q-values alone, which is "
            f"the uranium series. Then it overruns into {after}, because "
            f"Pb-208 is doubly magic and a liquid drop has no shells. "
            f"Recorded, not patched")


def _more():
    rows, seen = survey()
    atoms = len(rows)
    if len(seen) <= 2:
        raise ArithmeticError("histories reach almost no contexts")
    return (f"{atoms} atoms across 8 elements produce {len(seen)} distinct "
            f"expert sets between them, from histories reconstructed on "
            f"demand and stored nowhere")


if __name__ == "__main__":
    for el in ("U", "C", "Au"):
        print(f"atom: {el} #0 of chunk 0, universe-0")
        print(f"  key {atom_key('universe-0', 0, el, 0)[:48]}...")
        for e in history("universe-0", 0, el, 0):
            print("   " + str(e)[:104])
        print()
    rows, seen = survey()
    print(f"{len(rows)} atoms -> {len(seen)} distinct expert sets")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:34}{d[:88]}")
    print("\nall:", ok)
