"""The things themselves, so that the technology can be read.

engine/intricacy.py counts designs as 2**s and never says what
any of them IS. A count is not a technology. This gives the
count its objects.

A PRIMITIVE is a physical capability, and each one here is
grounded in a rule that already exists somewhere on the chain --
heat in the cooking bill, edge and lever in the grip and tool
rules, optics in the diffraction limit that bounded an eye. An
ARTIFACT is a set of primitives used together.

What is DERIVED: which primitives exist, in what order (a
primitive that needs others cannot come first), how many parts an
artifact may have at a given specialty count, and therefore which
artifacts are reachable when.

What is VOCABULARY: the names. KNOWN_AS is a dictionary from a
set of primitives to the word we use for it. It derives nothing
and is not allowed to -- it is there so a person can read the
output and recognise a steam engine when the parts arrive. Every
name in it is checked against the derivation: a name whose parts
are not reachable is an error, not a prediction.
"""

import itertools
import math

# COMPOSITION DEPTH IS NOT THE CONSTRAINT, and finding that out
# is most of what this module is for. The prerequisite tree below
# is five deep; engine/intricacy.py affords 23.5 parts in a
# village. On composition alone a literate village reaches a
# governed engine, which is plainly false, so something physical
# has to be doing the gating instead -- and it is TEMPERATURE.
#
# Every step past cordage is a material you cannot have until you
# can reach the heat that makes it. Fired clay wants 1000 K,
# copper 1350, iron and glass and steel 1700. And what you can
# reach depends on what you have already built: a hearth keeps the
# heat in, bellows force the air, charcoal burns hotter than wood.
# So the tech tree is a bootstrap on a single scalar, and the
# order comes out of combustion rather than out of a list.
#
# Each entry: (needs, temperature K, grounding rule, words).
PRIMITIVES = {
    "heat":        ((), 600, "disease.cook_cost_mj", "fire held at a temperature"),
    "edge":        ((), 300, "tools.grip_gate", "a worked face that cuts"),
    "cordage":     ((), 300, "tools.grip_gate", "fibre twisted until it holds"),
    "lever":       ((), 300, "tools.torque", "a length trading force for distance"),
    "rotation":    (("edge", "lever"), 300, "biome.escalation_stops_at", "a bearing and a round thing on it"),
    "mark":        (("edge",), 300, "literacy.copy_error", "a durable trace standing for a sound"),
    "breeding":    (("mark",), 300, "heredity.copies_per_type", "kept records of who bred with whom"),
    "containment": (("heat",), 1000, "atoms.Pool", "fired clay that holds against a gradient"),
    "smelting":    (("heat", "containment"), 1350, "arrhenius.rate", "ore reduced past its melting point"),
    "gearing":     (("rotation", "smelting"), 1350, "tools.torque", "teeth that carry a ratio"),
    "optics":      (("heat", "containment"), 1700, "senses.diffraction_limit", "glass shaped to bend light"),
    "spring":      (("smelting",), 1700, "eos.strain", "steel: stored strain released on demand"),
    "pressure":    (("smelting", "containment"), 1700, "eos.pressure", "a vessel that holds against itself"),
    "steam":       (("pressure", "heat"), 1700, "carnot.efficiency", "heat turned into a stroke"),
    "regulation":  (("gearing", "spring"), 1700, "control.feedback", "a machine that corrects itself"),
    "electricity": (("smelting", "rotation"), 1700, "landauer.kT", "charge moved on purpose"),
}

# What a wood fire in the open reaches, and what each built thing
# adds by keeping heat in, forcing air through, or burning hotter.
# MEASURED-ish, and the gains need the primitives that make them.
BASE_K = 1100
# Staged, because they do not all arrive together. Bellows need a
# metal tuyere at the hot end, which needs the smelting the
# bellows were for -- so the cheap gains buy copper, and copper
# buys the gains that reach iron. That loop is why bronze precedes
# iron by a long way and it is not put in by hand.
GAINS = {
    "a hearth that keeps it in": (("containment",), 150),
    "charcoal instead of wood": (("containment", "heat"), 150),
    "bellows on a metal tuyere": (("cordage", "smelting"), 200),
    "a regenerative flue": (("smelting", "gearing"), 150),
}

# VOCABULARY ONLY. Names for combinations, so the output reads.
# Deriving nothing; checked against the derivation, never driving it.
KNOWN_AS = {
    frozenset({"edge", "cordage", "lever"}): "a hafted axe",
    frozenset({"heat", "containment"}): "a cooking pot",
    frozenset({"cordage", "lever"}): "a bow",
    frozenset({"rotation", "lever"}): "a potter's wheel",
    frozenset({"rotation", "cordage"}): "a spindle",
    frozenset({"mark", "containment"}): "a sealed tablet, an account",
    frozenset({"smelting", "edge"}): "a metal blade",
    frozenset({"breeding", "mark"}): "a bred crop line",
    frozenset({"optics", "mark"}): "spectacles, and then a lens ground to a number",
    frozenset({"optics", "rotation", "gearing"}): "a telescope on a mount",
    frozenset({"gearing", "spring", "regulation"}): "a clock",
    frozenset({"steam", "rotation", "gearing"}): "a steam engine turning a shaft",
    frozenset({"steam", "rotation", "smelting", "regulation"}): "a governed engine",
    frozenset({"electricity", "rotation", "regulation"}): "a dynamo under load",
    frozenset({"electricity", "optics", "regulation"}): "a signal read by machine",
    frozenset({"electricity", "regulation", "mark"}): "a machine that computes",
}


def temperature(held):
    """Hottest fire buildable with what is already held. DERIVED."""
    t = BASE_K
    for _label, (needs, gain) in GAINS.items():
        if set(needs) <= set(held):
            t += gain
    return t


def bootstrap():
    """-> [(round, temperature, newly reachable)]. DERIVED.

    Start with an open fire. Make what that allows. That raises
    the fire. Repeat until nothing new appears. Nobody sequences
    this -- the fixed point does.
    """
    held, rounds = set(), []
    while True:
        t = temperature(held)
        got = {n for n, (needs, k, _r, _w) in PRIMITIVES.items()
               if n not in held and set(needs) <= held and k <= t}
        if not got:
            return rounds
        held |= got
        rounds.append((len(rounds) + 1, t, sorted(got)))


def held_by_round(r):
    """Everything in hand after r rounds of the bootstrap."""
    out = set()
    for i, _t, got in bootstrap():
        if i <= r:
            out |= set(got)
    return out


def depth(name, seen=None):
    """Longest chain of prerequisites under a primitive. DERIVED."""
    seen = seen or set()
    if name in seen:
        raise ValueError(f"cycle at {name}")
    needs = PRIMITIVES[name][0]
    if not needs:
        return 0
    return 1 + max(depth(n, seen | {name}) for n in needs)


def order():
    """Primitives in the order they can appear. DERIVED."""
    return sorted(PRIMITIVES, key=lambda n: (depth(n), n))


def available(parts_budget, rounds=None):
    """Primitives in reach: hot enough AND affordable to compose."""
    hot = held_by_round(len(bootstrap()) if rounds is None else rounds)
    return [n for n in order()
            if n in hot and depth(n) + 1 <= parts_budget]


def reachable(parts_budget):
    """Artifacts buildable at that budget. DERIVED."""
    prims = available(parts_budget)
    cap = int(min(parts_budget, len(prims)))
    return sum(math.comb(len(prims), k) for k in range(1, cap + 1))


def named_at(parts_budget):
    """-> [(name, parts)]. Recognisable things now in reach."""
    prims = set(available(parts_budget))
    out = []
    for combo, name in KNOWN_AS.items():
        if combo <= prims and len(combo) <= parts_budget:
            out.append((name, sorted(combo)))
    return sorted(out, key=lambda r: (len(r[1]), r[0]))


def first_round(combo):
    """Bootstrap round at which every part is in hand. DERIVED."""
    for i, _t, _g in bootstrap():
        if set(combo) <= held_by_round(i):
            return i
    return None


def first_possible(combo):
    """Smallest parts budget that admits this artifact. DERIVED."""
    need = max(depth(c) + 1 for c in combo)
    return max(need, len(combo))


def catalogue():
    """-> [(round, temp, name, parts)]. In arrival order. DERIVED."""
    temps = {i: t for i, t, _g in bootstrap()}
    rows = []
    for combo, name in KNOWN_AS.items():
        r = first_round(combo)
        if r is None:
            continue
        rows.append((r, temps[r], name, sorted(combo)))
    return sorted(rows, key=lambda x: (x[0], len(x[3]), x[2]))


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_primitive_cannot_precede_what_it_is_made_of", _order)
    t("the_count_of_designs_now_has_objects_under_it", _objects)
    t("every_name_is_checked_against_the_derivation", _names)
    t("our_own_age_arrives_last_and_not_by_being_listed", _modern)
    return all(x for _, x, _ in res), res


def _order():
    o = order()
    for name in PRIMITIVES:
        for need in PRIMITIVES[name][0]:
            if o.index(need) >= o.index(name):
                raise ArithmeticError(f"{name} before {need}")
    d = {n: depth(n) for n in o}
    return (f"{len(PRIMITIVES)} primitives, each grounded in a rule "
            f"that already existed for another reason -- heat in the "
            f"cooking bill, optics in the diffraction limit that "
            f"bounded an eye, steam in Carnot. A primitive that "
            f"needs others cannot come first, so the order is "
            f"forced: depth 0 is "
            f"{[n for n in o if d[n]==0]}, and the deepest is "
            f"{max(d, key=d.get)} at {max(d.values())}. Nobody "
            f"sequenced this; the prerequisites did")


def _objects():
    from engine.intricacy import settle
    v = settle()
    rounds = bootstrap()
    deep = max(depth(n) for n in PRIMITIVES) + 1
    if deep >= v:
        raise ArithmeticError(f"composition {deep} vs budget {v}")
    return (f"engine/intricacy.py counted 2**s designs and never "
            f"said what one WAS. Giving them objects found that "
            f"composition depth is NOT the constraint: the "
            f"prerequisite tree is {deep} deep and a village "
            f"affords {v:.1f} parts, so on composition alone a "
            f"literate village reaches a governed engine. It does "
            f"not, and the thing stopping it is TEMPERATURE. "
            f"Every step past cordage is a material you cannot "
            f"have until you can reach the heat that makes it, and "
            f"the bootstrap takes {len(rounds)} rounds from "
            f"{rounds[0][1]} K to {rounds[-1][1]} K. The count now "
            f"has objects under it and the objects have a "
            f"metallurgy")


def _names():
    bad = [n for c, n in KNOWN_AS.items()
           if not set(c) <= set(PRIMITIVES)]
    unreachable = [n for c, n in KNOWN_AS.items() if first_round(c) is None]
    if bad or unreachable:
        raise ArithmeticError(f"named but underivable: {bad + unreachable}")
    rows = catalogue()
    return (f"{len(KNOWN_AS)} names, and they derive NOTHING -- "
            f"they are vocabulary so the output can be read. Every "
            f"one is checked against the derivation and a name "
            f"whose parts never become reachable is an error, not "
            f"a prediction. They arrive where the bootstrap puts "
            f"them: "
            + "; ".join(f"r{r} {nm}" for r, _t, nm, _p in rows[:5])
            + f" ... and {rows[-1][2]} at r{rows[-1][0]}")


def _modern():
    rows, b = catalogue(), bootstrap()
    early = [r for r in rows if r[0] <= 2]
    late = [r for r in rows if r[0] >= len(b) - 1]
    copper = next(i for i, _t, g in b if "smelting" in g)
    iron = next(i for i, _t, g in b if "spring" in g)
    if iron <= copper or not late:
        raise ArithmeticError(f"{copper} {iron}")
    return (f"the recognisable modern things are not late because "
            f"anyone listed them last. Copper arrives at round "
            f"{copper} and steel at {iron}, and the gap is a LOOP: "
            f"bellows need a metal tuyere at the hot end, and the "
            f"tuyere needs the smelting the bellows were for. So "
            f"the cheap gains -- a hearth, charcoal -- buy copper "
            f"at {b[copper-1][1]} K, and copper buys the gains that "
            f"reach {b[iron-1][1]} K and iron. {len(early)} things "
            f"are in hand by round 2 ({early[0][2]}); "
            f"{len(late)} wait for round {len(b)-1} or later, "
            f"including {rows[-1][2]}. Nobody put a steam engine "
            f"after a cooking pot -- combustion did")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
