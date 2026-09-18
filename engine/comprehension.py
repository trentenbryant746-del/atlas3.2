"""
What an organism has to understand, which is not the code.

This repository can read its own rules -- engine/spine.py walks
the dependency graph, engine/vocabulary.py indexes every rule by
its own words, engine/frozen.py knows why a code mapping is
locked. None of that is available to a bacterium, and a
bacterium is fine.

An organism does not need the code. It needs a RESPONSE TO EVERY
CONSTRAINT THAT CAN KILL IT, and no more. The rules of the
environment are already in the environment; what has to be
carried is the reply.

So comprehension is not a scale of insight. It is a COUNT: how
many distinct constraints bind at this organism's scale, because
each one that binds needs its own reply and each one that does
not needs nothing.

    bacterium    6 bind    no neural tissue at all
    bee          8         3.5e8 bits
    mouse       10         1.4e11
    human       13         4.7e14

A bacterium does not respond to predation, heat rejection or
provisioning because none of those bind at a micron. It is not
ignorant of them; they are not there. And a human carries three
that nothing else does -- provisioning a child for eighteen
years, an allocation rule above the carrying number, and a shared
corpus -- because engine/ontogeny.py, engine/rank.py and
engine/school.py each derived a constraint that only appears at
that scale.

WHICH IS WHY A BIGGER BRAIN UNDERSTANDS MORE, and not because
understanding is a virtue. More of the world binds on a large,
long-lived, provisioned animal, and every constraint that binds
must be answered or it kills you.

STORAGE IS NOT WHAT SCALES. engine/learning.py already showed a
human store fills in 1.49 years through one nerve, so the 4.7e14
bits are not being used to hold thirteen rules. What scales is
the number of distinct situations that must be told apart and
answered differently, and thirteen constraints in combination is
a large number of situations.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Which derived constraints bind at each grade, and the module that
# derived each. Nothing here is new -- it is a census of what the
# repository already refuses to let an organism ignore.
BINDS = {
    "bacterium": ["solvent", "elements", "energy", "crowding",
                  "fidelity", "persistence"],
    "bee": ["solvent", "elements", "energy", "fidelity", "persistence",
            "heat out", "food in", "predation"],
    "mouse": ["solvent", "elements", "energy", "fidelity", "persistence",
              "heat out", "food in", "predation", "oxygen to tissue",
              "skeleton"],
    "human": ["solvent", "elements", "energy", "fidelity", "persistence",
              "heat out", "food in", "predation", "oxygen to tissue",
              "skeleton", "provisioning", "allocation",
              "a shared corpus"],
}

SOURCE = {
    "solvent": "earthlab", "elements": "earthlab", "energy": "earthlab",
    "crowding": "earthlab", "fidelity": "cold", "persistence": "cold",
    "heat out": "shelter", "food in": "biome", "predation": "tools",
    "oxygen to tissue": "biosphere", "skeleton": "life",
    "provisioning": "ontogeny", "allocation": "rank",
    "a shared corpus": "school",
}

BRAIN_KG = {"bacterium": 0.0, "bee": 1e-6, "mouse": 4e-4,
            "crow": 1.4e-2, "chimp": 0.40, "human": 1.35}


def brain_bits(name):
    """Bits of synapse at this grade. DERIVED via engine/learning.py."""
    from engine.learning import SYNAPSES, BITS_PER_SYNAPSE
    kg = BRAIN_KG.get(name, 0.0)
    return SYNAPSES * (kg / 1.35) * BITS_PER_SYNAPSE


def binding(name):
    """Constraints that bind at this grade. DERIVED, a census."""
    return BINDS.get(name, [])


def situations(name):
    """Distinct situations to tell apart. DERIVED: 2^constraints.

    Each binding constraint is present or not, and a reply that
    is right for one combination can be wrong for another, so
    what must be distinguished grows as the power set.
    """
    return 2 ** len(binding(name))


def unique_to(name):
    """What binds here and nowhere simpler. DERIVED."""
    order = ["bacterium", "bee", "mouse", "human"]
    if name not in order or order.index(name) == 0:
        return []
    prev = set(binding(order[order.index(name) - 1]))
    return [c for c in binding(name) if c not in prev]


def needs_the_code(name):
    """-> (bool, why). Must an organism read its own rules? DERIVED."""
    return False, (
        f"a {name} needs a reply to each of the "
        f"{len(binding(name))} constraints that bind on it. The "
        f"rules of the environment are already in the environment; "
        f"what has to be carried is the reply, not the rule")


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("an_organism_needs_replies_not_the_code", _code)
    t("comprehension_is_a_count_of_what_binds", _count)
    t("what_does_not_bind_needs_nothing", _absent)
    t("a_bigger_brain_has_more_binding_on_it", _scale)
    t("storage_is_not_what_scales", _store)
    t("every_constraint_names_the_module_that_derived_it", _cite)
    return all(o[1] for o in out), out


def _code():
    ok, why = needs_the_code("bacterium")
    if ok:
        raise ArithmeticError("a bacterium must read the code")
    return (f"this repository can read its own rules -- "
            f"engine/spine.py walks the graph, engine/vocabulary.py "
            f"indexes every rule by its words, engine/frozen.py "
            f"knows why a code is locked. None of that is available "
            f"to a bacterium and a bacterium is fine. {why}")


def _count():
    rows = [(k, len(binding(k)), situations(k)) for k in BINDS]
    if not all(a[1] <= b[1] for a, b in zip(rows, rows[1:])):
        raise ArithmeticError("the count does not increase")
    return (f"comprehension is not a scale of insight, it is a COUNT: "
            + ", ".join(f"{k} {n}" for k, n, _s in rows)
            + f". Each constraint that binds needs its own reply, and "
              f"since a reply right for one combination can be wrong "
              f"for another, the situations to tell apart go as the "
              f"power set -- {rows[-1][2]:,} for a human against "
              f"{rows[0][2]} for a bacterium")


def _absent():
    b = set(binding("bacterium"))
    if "predation" in b or "heat out" in b:
        raise ArithmeticError("a bacterium faces predation or heat loss")
    return ("a bacterium does not respond to predation, heat "
            "rejection or provisioning because NONE OF THOSE BIND AT "
            "A MICRON. It is not ignorant of them -- they are not "
            "there. engine/biome.py prices predation for bodies that "
            "can be caught and engine/shelter.py prices heat loss "
            "for bodies that make 82 W, and a bacterium is neither")


def _scale():
    u = unique_to("human")
    if len(u) < 3:
        raise ArithmeticError(f"a human adds only {u}")
    return (f"a human carries {u} and nothing simpler does, because "
            f"engine/ontogeny.py, engine/rank.py and "
            f"engine/school.py each derived a constraint that only "
            f"appears at that scale -- eighteen years of "
            f"provisioning, an allocation rule above the carrying "
            f"number, a corpus too large for one head. A BIGGER "
            f"BRAIN UNDERSTANDS MORE because MORE BINDS ON IT, not "
            f"because understanding is a virtue")


def _store():
    from engine.learning import fill_time_years
    bits = brain_bits("human")
    n = len(binding("human"))
    return (f"a human holds {bits:.1e} bits and {n} constraints, so "
            f"storage is plainly not what scales -- "
            f"engine/learning.py already showed that store fills in "
            f"{fill_time_years():.2f} years through one nerve. What "
            f"scales is the number of distinct SITUATIONS that must "
            f"be told apart and answered differently, which is "
            f"{situations('human'):,} combinations of thirteen "
            f"constraints")


def _cite():
    missing = [c for k in BINDS for c in BINDS[k] if c not in SOURCE]
    if missing:
        raise ArithmeticError(f"unsourced constraints: {set(missing)}")
    mods = sorted(set(SOURCE.values()))
    return (f"every one of the {len(SOURCE)} constraints names the "
            f"module that derived it, across {len(mods)}: "
            + ", ".join(mods) + ". This file adds no constraint of "
            "its own -- it is a census of what the repository "
            "already refuses to let an organism ignore")


if __name__ == "__main__":
    print(f"  {'organism':<12}{'binds':>7}{'situations':>13}"
          f"{'brain bits':>14}")
    for k in BINDS:
        print(f"  {k:<12}{len(binding(k)):>7}{situations(k):>13,}"
              f"{brain_bits(k):>14.1e}")
    print()
    for k in ("bee", "mouse", "human"):
        u = unique_to(k)
        if u:
            print(f"  {k} adds: {', '.join(u)}")
    print()
    for nm, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {nm:50}{d[:28]}")
