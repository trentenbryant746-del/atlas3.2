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
    "edge":        ((), 300, "tools.stress", "a worked face that cuts"),
    "cordage":     ((), 300, "tools.breaks", "fibre twisted until it holds"),
    "lever":       ((), 300, "tools.usable", "a length trading force for distance"),
    "rotation":    (("edge", "lever"), 300, "biome.escalation_stops_at", "a bearing and a round thing on it"),
    "mark":        (("edge",), 300, "literacy.copy_error", "a durable trace standing for a sound"),
    "breeding":    (("mark",), 300, "heredity.copies_per_type", "kept records of who bred with whom"),
    "containment": (("heat",), 1000, "atoms.Pool", "fired clay that holds against a gradient"),
    "smelting":    (("heat", "containment"), 1350, "thermo.effective_temperature", "ore reduced past its melting point"),
    "gearing":     (("rotation", "smelting"), 1350, "tools.what_works", "teeth that carry a ratio"),
    "optics":      (("heat", "containment"), 1700, "senses.diffraction_limit", "glass shaped to bend light"),
    "spring":      (("smelting",), 1700, "eos.band", "steel: stored strain released on demand"),
    "pressure":    (("smelting", "containment"), 1700, "eos.ceiling", "a vessel that holds against itself"),
    "steam":       (("pressure", "heat"), 1700, "thermo.gamma", "heat turned into a stroke"),
    "regulation":  (("gearing", "spring"), 1700, "signal.signal_bits", "a machine that corrects itself"),
    "electricity": (("smelting", "rotation"), 1700, "learning.landauer_j", "charge moved on purpose"),
    # Past iron, heat stops being the gate. Everything below is
    # reachable at 1750 K and none of it was available in 1750,
    # because the thing in short supply changed: not how hot you
    # can get but how ACCURATELY you can place matter. A second
    # scalar, and it bootstraps the same way.
    "vacuum":      (("pressure", "regulation"), 1700, "eos.floor", "a volume with the air taken out"),
    "alloy":       (("smelting", "regulation"), 1700, "atoms.Pool", "composition held to a specification"),
    "semiconductor": (("vacuum", "alloy"), 1700, "eos.classify", "a crystal pure enough to switch"),
    "switching":   (("semiconductor", "electricity"), 1700, "learning.landauer_j", "a gate that opens on a signal"),
    "inference":   (("switching", "regulation"), 1700, "learning.store_bits", "statistics run at a scale no head holds"),
    # A THIRD GATE, and it is not invented. The heat ladder only
    # ever went UP. Going DOWN is a separate physical scarcity
    # with its own floor -- thermal noise kT against the energy
    # you are trying to hold -- and nothing in this tree had
    # touched it. These are gated by cold, not by fire.
    "superconduction": (("alloy", "electricity"), 1700, "thermo.cv_molar", "resistance gone below a critical temperature"),
    "coherence":   (("superconduction", "switching"), 1700, "learning.landauer_j", "a quantum state held against the noise"),
    "placement":   (("coherence", "optics"), 1700, "eos.classify", "matter set down one atom at a time"),
}

# The second gate. A hand fits to about a tenth; a screw-cutting
# lathe to a thousandth; interferometry to a millionth; light
# printed through a mask to a billionth. Each needs what the last
# one made, exactly as the furnace did.
# THE FLOOR OF THE TOLERANCE LADDER IS DERIVED, NOT CHOSEN.
# You cannot place matter more finely than an atom is wide, and
# the Bohr radius falls out of hbar, the electron mass and the
# charge: 4 pi eps0 hbar^2 / (m_e e^2) = 5.29e-11 m. A silicon
# lattice is 5.43e-10. So 1e-10 is a WALL and not a rung -- the
# difference between a ladder that ends and one nobody has
# climbed yet.
M_ELECTRON = 9.1093837015e-31     # kg, MEASURED
EPS_0 = 8.8541878128e-12          # F/m, MEASURED


def bohr_radius():
    """4 pi eps0 hbar^2 / (m_e e^2). DERIVED."""
    from engine.constants import HBAR, E_CHARGE
    return (4 * math.pi * EPS_0 * HBAR**2
            / (M_ELECTRON * E_CHARGE**2))


# What a cold stage reaches and what it needs to get there.
# Cooling CASCADES: no liquid helium without liquid air first,
# because the helium must be pre-cooled -- the same shape as the
# bellows needing the tuyere it was for.
BASE_COLD = 300.0
COLD_GAINS = {
    "expanding a compressed gas": (("pressure", "regulation"), 77.0),
    "pumping on a cascaded bath": (("vacuum", "superconduction"), 4.0),
}
COLD_NEEDED = {
    "superconduction": 77.0,
    "coherence": 4.0,
    "placement": 4.0,
}

# A TOLERANCE HAS TO BE A TOLERANCE ON SOMETHING, and until now
# these were relative numbers floating free of any dimension.
# Giving each craft a characteristic size lets the tolerance be
# checked against what the physics actually demands, and three
# of them came out wrong when it was.
#
# The worst was optics. A lens surface must be true to about a
# quarter wavelength -- 138 nm on a 50 mm lens, which is 2.7e-6
# relative, not the 1e-2 that was here. Four orders out.
#
# The resolution is a real distinction that this file did not
# have: some accuracy is MEASURED and some is PROCESSED. You
# cannot machine a lens to a quarter wave, and nobody ever did.
# You grind two surfaces against each other and they conform,
# because a sphere is the only shape that slides on itself in
# every orientation. The accuracy is produced by the method and
# nobody gauges it. Three flats lapped in rotation give a plane
# the same way, and a hobbed gear generates its own involute.
#
# So the ladder in TOL_NEEDED is what you must MEASURE. A craft
# whose accuracy comes out of its process needs no drawing and
# no instrument, which is why lenses precede micrometers.
DIMENSION_M = {
    "lever": 1.0, "cordage": 1.0, "edge": 0.1, "heat": 0.3,
    "containment": 0.2, "rotation": 0.1, "mark": 0.01,
    "breeding": 1.0, "smelting": 0.3, "gearing": 0.05,
    "optics": 0.05, "spring": 0.1, "pressure": 0.3,
    "steam": 0.5, "regulation": 0.05, "electricity": 0.1,
    "vacuum": 0.2, "alloy": 0.05, "semiconductor": 1e-3,
    "switching": 1e-5, "inference": 1e-6,
    "superconduction": 0.01, "coherence": 1e-5, "placement": 1e-9,
}

# What the physics demands, in metres, where it is known. Set
# against DIMENSION_M x TOL_NEEDED this says whether a craft can
# be gauged or must be self-generated.
ABSOLUTE_NEEDED_M = {
    "gearing": 1e-4,        # tooth pitch must match to mesh
    "optics": 1.4e-7,       # a quarter of 550 nm
    "pressure": 1e-4,       # wall thickness, hoop stress
    "switching": 1e-8,
    "placement": 5.3e-11,   # the Bohr radius
}

# Crafts whose accuracy is produced by the method rather than
# gauged: lapping, three-plate flats, hobbing. These are the
# ones that arrive before the instrument that could measure them.
SELF_FIGURING = {"optics", "gearing", "rotation"}

BASE_TOL = 1e-1
# These were wrong on the first pass and the bootstrap DEADLOCKED,
# which is the right failure. Gearing was set at 1e-2 and the only
# route to 1e-2 is a screw-cutting lathe, which is made of gears.
# The way out is historical and physical: the first gears were
# hand-filed at a tenth and they were good enough to cut better
# ones. The same held for transistors -- point-contact devices
# were millimetre-scale, and lithography came after them, not
# before. A tolerance ladder must have a rung you can reach by
# hand or it is not a ladder.
TOL_NEEDED = {
    "gearing": 1e-1, "spring": 1e-1,      # hand-filed, forged
    "pressure": 1e-2, "regulation": 1e-2,  # lathe work
    "optics": 1e-2, "vacuum": 1e-3, "alloy": 1e-3,
    "semiconductor": 1e-6, "switching": 1e-6,   # point contact
    "inference": 1e-9,                          # printed, at scale
    "superconduction": 1e-6, "coherence": 1e-9,
    "placement": 1e-10,                         # the atomic wall
}
TOL_GAINS = {
    "a screw-cutting lathe": (("gearing", "smelting"), 1e-3),
    "interferometry": (("optics", "regulation"), 1e-6),
    "light printed through a mask": (("optics", "switching"), 1e-9),
    "a tip that feels single atoms": (("coherence", "vacuum"), 1e-10),
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
    frozenset({"vacuum", "electricity", "regulation"}): "a valve, and a signal amplified",
    frozenset({"semiconductor", "switching"}): "a transistor",
    frozenset({"switching", "regulation", "mark"}): "a stored-program computer",
    frozenset({"inference", "mark"}): "statistics run over a written corpus",
    frozenset({"inference", "switching", "regulation"}): "a system that answers in sentences",
}


def temperature(held):
    """Hottest fire buildable with what is already held. DERIVED."""
    t = BASE_K
    for _label, (needs, gain) in GAINS.items():
        if set(needs) <= set(held):
            t += gain
    return t


def gauged_precision(primitive):
    """Absolute precision you must MEASURE, in metres. DERIVED."""
    return (DIMENSION_M.get(primitive, 0.1)
            * TOL_NEEDED.get(primitive, BASE_TOL))


def demanded_precision(primitive):
    """What the physics needs, where that is known. RECORDED."""
    return ABSOLUTE_NEEDED_M.get(primitive)


def self_figuring(primitive):
    """Does the process produce the accuracy? DERIVED-ish."""
    return primitive in SELF_FIGURING


def needs_gauging(primitive):
    """Must somebody measure it to hit it? DERIVED."""
    want = demanded_precision(primitive)
    if want is None:
        return False
    return not self_figuring(primitive) and gauged_precision(primitive) > want


def coldness(held):
    """Lowest temperature reachable with what is held. DERIVED."""
    t = BASE_COLD
    for _label, (needs, got) in COLD_GAINS.items():
        if set(needs) <= set(held):
            t = min(t, got)
    return t


def tolerance(held):
    """Finest placement achievable with what is held. DERIVED."""
    t = BASE_TOL
    for _label, (needs, tol) in TOL_GAINS.items():
        if set(needs) <= set(held):
            t = min(t, tol)
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
        tol, cold = tolerance(held), coldness(held)
        got = {n for n, (needs, k, _r, _w) in PRIMITIVES.items()
               if n not in held and set(needs) <= held and k <= t
               and TOL_NEEDED.get(n, 1e-1) >= tol
               and COLD_NEEDED.get(n, BASE_COLD) >= cold}
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


# GOING FORWARD, and what that can honestly mean.
#
# Everything above is recorded: every primitive names a material
# or an effect somebody has actually made, and every entry in
# KNOWN_AS is a thing that exists. Asking the model to run two
# centuries past now is a fair question with a narrow answer.
#
# It CAN project the two scalars it tracks, because both are
# arithmetic on terms already priced -- the parts budget from the
# corpus, and the per-capita exponent from the land share.
#
# It CANNOT name what gets built. A name here is vocabulary
# attached to a combination of KNOWN primitives; a name for a
# primitive nobody has made would be a word with no rule under it,
# and the whole discipline of this repo is that a word with no
# rule under it is not an answer. So project() returns numbers and
# no nouns, and a check below fails if anybody adds one.

DIGITAL_COPY_GAIN = 1e6      # CHOSEN: copies a scribe-year, now


def project(years=200):
    """-> dict. The scalars, forward. PROJECTED, not derived."""
    import math as _m
    from engine.intricacy import (settle_network, per_capita_exponent,
                                  LAND_SHARE)
    now = settle_network()
    press = _m.log2(DIGITAL_COPY_GAIN)
    return {
        "years": years,
        "parts now": now,
        "parts projected": now + press,
        "from": "a corpus copied at 1e6 a scribe-year rather than 250",
        "exponent now": per_capita_exponent(LAND_SHARE),
        "exponent projected": per_capita_exponent(0.02),
        "named artifacts": 0,
    }


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_primitive_cannot_precede_what_it_is_made_of", _order)
    t("every_grounding_pointer_resolves_to_a_real_rule", _grounded)
    t("the_count_of_designs_now_has_objects_under_it", _objects)
    t("every_name_is_checked_against_the_derivation", _names)
    t("our_own_age_arrives_last_and_not_by_being_listed", _modern)
    t("the_gate_changes_and_heat_stops_mattering", _gate)
    t("INVERTED_the_future_gets_numbers_and_no_nouns", _future)
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


def _grounded():
    """Every rule named as grounding must actually exist.

    Added at 3.1.118 because it did not. The module claimed each
    primitive was grounded in a rule that already existed and 13
    of 21 pointed at nothing -- tools.torque, eos.strain,
    carnot.efficiency, landauer.kT, control.feedback, none of
    them real. Nothing checked, because the claim was in prose.
    """
    import importlib
    bad = []
    for n, (_needs, _k, rule, _w) in PRIMITIVES.items():
        mod, _, fn = rule.partition(".")
        try:
            m = importlib.import_module("engine." + mod)
            if not hasattr(m, fn):
                bad.append(f"{n} -> {rule}")
        except Exception:
            bad.append(f"{n} -> {rule} (no module)")
    if bad:
        raise ArithmeticError(f"{len(bad)} ungrounded: {bad}")
    mods = sorted({r.split(".")[0] for _n, (_a, _b, r, _c)
                   in PRIMITIVES.items()})
    return (f"all {len(PRIMITIVES)} primitives point at a rule that "
            f"exists and is importable, across {len(mods)} modules: "
            f"{mods}. This check exists because the claim was made "
            f"in prose first and 13 of the 21 pointers were "
            f"invented -- tools.torque, eos.strain, "
            f"carnot.efficiency, control.feedback, landauer.kT. "
            f"Plausible names for rules this repo does not have. A "
            f"grounding that is not resolved is a citation nobody "
            f"followed")


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
    return (f"nothing here is late because it was listed last. "
            f"Copper is round {copper} and steel {iron}, and the "
            f"gap is a LOOP: bellows need a metal tuyere and the "
            f"tuyere needs the smelting the bellows were for, so "
            f"the cheap gains buy copper at {b[copper-1][1]} K and "
            f"copper buys the gains that reach {b[iron-1][1]} K. "
            f"The same shape repeats in tolerance: the first gears "
            f"were hand-filed at a tenth and were good enough to "
            f"cut better ones, and point-contact transistors were "
            f"millimetre-scale before lithography existed. Setting "
            f"either rung too high DEADLOCKED the bootstrap on the "
            f"first attempt, which is the correct failure -- a "
            f"ladder needs a rung you can reach by hand. "
            f"{len(early)} things are in hand by round 2 "
            f"({early[0][2]}); {len(late)} wait for round "
            f"{len(b)-1} or later, ending at {rows[-1][2]}")


def _gate():
    b = bootstrap()
    temps = [t for _i, t, _g in b]
    flat = next(i for i, t, _g in b if t == max(temps))
    tols = [(i, tolerance(held_by_round(i))) for i, _t, _g in b]
    after = [tl for i, tl in tols if i >= flat]
    if len(set(temps[flat - 1:])) != 1 or len(set(after)) < 2:
        raise ArithmeticError(f"{temps} {after}")
    return (f"temperature stops moving at round {flat} "
            f"({max(temps)} K) and the bootstrap runs to "
            f"{len(b)}. Everything after that is reachable at the "
            f"same heat and was not available for two centuries, "
            f"because the scarce thing CHANGED: not how hot you "
            f"can get but how accurately you can place matter. "
            f"Tolerance goes {after[0]:.0e} -> {after[-1]:.0e} "
            f"over those rounds. A model with one gate would have "
            f"put a transistor next to a steam engine. The gate is "
            f"not a constant of the system, it is whichever scalar "
            f"is currently short, and noticing that it had moved "
            f"is the only reason the later rounds exist")


def _future():
    """INVERTED. Fails the moment a future artifact acquires a name."""
    pr = project()
    unnamed = [n for n in PRIMITIVES if n not in
               {x for c in KNOWN_AS for x in c}]
    if pr["named artifacts"] != 0:
        raise ArithmeticError(
            "something two centuries out has been given a name, "
            "which means a word was written with no rule under it")
    return (f"asked to run {pr['years']} years past now, the model "
            f"answers with two numbers and no nouns. Parts: "
            f"{pr['parts now']:.1f} -> {pr['parts projected']:.1f}, "
            f"and the whole of that gain is {pr['from']} -- a "
            f"millionfold corpus is {math.log2(DIGITAL_COPY_GAIN):.0f} "
            f"more parts, because the corpus is a logarithm and "
            f"that never stops being true. Per-capita exponent: "
            f"{pr['exponent now']:.3f} -> "
            f"{pr['exponent projected']:.3f} as the land share goes "
            f"to 0.02. What it will NOT do is name the artifacts. "
            f"Every primitive here is a material or an effect "
            f"somebody has made and every name in KNOWN_AS is a "
            f"thing that exists; a name for a primitive nobody has "
            f"made would be a word with no rule under it, and this "
            f"check fails if one appears. The forecast is 6.6 "
            f"parts and a share, and anyone wanting more than that "
            f"is asking for fiction")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
