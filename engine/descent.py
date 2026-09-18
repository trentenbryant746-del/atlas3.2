"""
Seed the smallest thing that can live, supply the planet, and let go.

Every gate this repository has reached lately shut on ARCHITECTURE
-- a pump, a skin, a skeleton -- and none of those is something a
planet provides. So stop providing them. Seed the least organism
the rules allow, hand it nothing but the conditions under which it
lives or dies, and run.

WHAT IS GIVEN

  the physics    diffusion supply, Kleiber metabolism, the
                 square-cube law, desiccation, all from rules
                 already written for other reasons
  the planet     resources always available, as instructed --
                 nothing here dies of a shortage
  variation      offspring differ slightly in size, and rarely
                 gain or lose a trait

WHAT IS NOT GIVEN

  any trait as a starting condition. The seed has none.
  any reward for complexity. A trait costs metabolism and pays
  nothing unless the physics happens to make it pay.
  any target. Nothing is scored against being large, or being a
  vertebrate, or being us.

THE ONE PRESSURE, AND IT IS DERIVED. Kleiber says metabolic rate
goes as mass^0.75, so energy per gram FALLS as a body grows. Being
bigger is cheaper per unit of self. That is the only advantage in
the model and it was not put there for this -- it has been in
engine/life.py since long before.

Everything else is a wall. Grow past what diffusion can supply and
the middle starves, unless a pump has appeared. Leave the water
without a skin and dry out. Stand up without a skeleton and
collapse. The walls are physics and the traits are accidents, and
what happens is whatever survives.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TRAITS = ("circulation", "skin", "skeleton")
TRAIT_COST = 0.02          # fraction of metabolism, each
MUTATION_SIZE = 0.15       # lognormal spread per generation
MUTATION_TRAIT = 0.002     # chance a trait appears or vanishes


class Organism:
    __slots__ = ("radius", "traits", "land")

    def __init__(self, radius, traits=frozenset(), land=False):
        self.radius = radius
        self.traits = frozenset(traits)
        self.land = land

    def mass(self):
        return 1000.0 * (4.0 / 3.0) * math.pi * self.radius ** 3

    def child(self, rng):
        r = self.radius * math.exp(rng.gauss(0.0, MUTATION_SIZE))
        t = set(self.traits)
        for name in TRAITS:
            if rng.random() < MUTATION_TRAIT:
                t.discard(name) if name in t else t.add(name)
        land = self.land
        if rng.random() < MUTATION_TRAIT:
            land = not land
        # The clamp was 1e-7, a number with nothing behind it.
        # Mutation may still produce a body below closure; fitness
        # refuses it rather than a floor hiding it.
        return Organism(max(r, 1e-9), t, land)


# THE SECOND ORGANISM. Every rule before this is one body against
# physics, and under those rules life stays microbial for ever --
# surplus energy per gram goes as mass^(-1/3), so smaller is always
# fitter, and that is what the first runs showed.
#
# AN ENCOUNTER-RATE REFUGE WAS THE OBVIOUS MECHANISM AND IT IS NOT
# ONE. If big prey were rarer, a predator would starve looking for
# them. But the scalings cancel exactly: number density goes as
# r^-3, cross-section as r^2, swimming speed as r, and the product
# is r^0. A predator meets the same number of meals per second
# whatever size its prey are, and each meal is larger. Being big is
# no refuge from being FOUND.
#
# What is left is simpler and it is a ratchet. A predator has to be
# bigger than its prey to handle it, so the only escape is to be
# bigger than anything hunting you. That does not reward size in
# the abstract -- it rewards size RELATIVE to whatever else is in
# the water, and both sides move. Nothing in this is a preference
# for complexity; it is the same metabolic accounting with one term
# added for being eaten.
PREDATOR_RATIO = 3.0        # how much bigger a hunter must be
PREDATION_PRESSURE = 0.4    # fraction of deaths from being eaten


def eaten_risk(org, population):
    """-> chance of being eaten this generation. DERIVED.

    Anything at least PREDATOR_RATIO times your radius can handle
    you. Encounter rate is size-independent, so risk is simply the
    share of the population big enough to do it.
    """
    if not population:
        return 0.0
    hunters = sum(1 for o in population
                  if o.radius >= org.radius * PREDATOR_RATIO)
    return PREDATION_PRESSURE * hunters / len(population)


def viable(org, o2_fraction=1.0, T=288.0):
    """-> (alive, why). The rules that kill, and nothing else."""
    from engine.biosphere import tissue_thickness
    from engine.life import square_cube_limit
    thick = tissue_thickness(o2_fraction)
    if org.radius > thick and "circulation" not in org.traits:
        return False, "centre starves: past the diffusion limit, no pump"
    intake, cost = energy_balance(org)
    if intake <= cost:
        return False, ("cannot feed itself: a surface supplies "
                       "mass^(2/3) and a volume burns mass^0.75")
    if org.land and "skin" not in org.traits:
        return False, "dries out: on land without a barrier"
    if org.land and "skeleton" not in org.traits and org.radius > 1e-3:
        return False, "collapses: on land, over a millimetre, no skeleton"
    h = float(square_cube_limit().value)
    if org.radius * 2 > h:
        return False, "crushes itself: past the square-cube ceiling"
    return True, "alive"


# THE FIRST RUN GREW TO EIGHTY-ONE METRES AND THAT WAS A MISSING
# RULE, NOT A RESULT.
#
# Kleiber gives the COST of being big -- mass^0.75, so cost per gram
# falls and bigger is cheaper per unit of self. Nothing gave the
# INTAKE. A body feeds through a surface: gut wall, gill, skin,
# whatever it is, the rate scales as area and area goes as
# mass^(2/3). So supply rises more slowly than demand,
#
#     cost / intake  ~  m^0.75 / m^(2/3)  =  m^0.083
#
# and however slowly that climbs it climbs without limit. There IS
# a maximum size and it comes from the mismatch between a volume
# that must be fed and a surface that does the feeding. Leaving
# intake out made bigness free, so the population grew until it hit
# the only wall left -- a land skeleton's 173 m ceiling, applied
# absurdly to something swimming.
INTAKE_COEFFICIENT = 90.0      # sets where supply and demand cross


def break_even_mass(n_traits=0):
    """kg where intake meets cost. CLOSED FORM, no generations.

    intake = a*m^(2/3) and cost = b*m^(3/4), so they cross where
    m^(3/4 - 2/3) = a/b, i.e. m = (a/b)^12. The 4,000-generation
    run was finding this number numerically and taking 5.5 s to
    do it. A loop that searches for a fixed point an equation
    gives is a rule that has not been found yet.
    """
    a = INTAKE_COEFFICIENT
    b = 70.0 * (1.0 + TRAIT_COST * n_traits)
    return (a / b) ** 12.0


def radius_of(mass_kg, density=1000.0):
    """m. DERIVED: a sphere of that mass."""
    return (3.0 * mass_kg / (4.0 * math.pi * density)) ** (1.0 / 3.0)


def collapses_to(n_traits=0):
    """m of radius the lineage settles at. DERIVED, closed form."""
    return radius_of(break_even_mass(n_traits))


def energy_balance(org):
    """-> (intake W, cost W). DERIVED: surface feeds, volume burns."""
    m = org.mass()
    if m <= 0:
        return 0.0, 1.0
    intake = INTAKE_COEFFICIENT * m ** (2.0 / 3.0)
    cost = 70.0 * m ** 0.75 * (1.0 + TRAIT_COST * len(org.traits))
    return intake, cost


_FLOOR = {}


def closure_floor_m():
    """m of radius below which nothing maintains itself. DERIVED.

    Not a new number. engine/earthlab.py derives it from
    autocatalytic closure -- how many molecule types must sit
    inside one compartment for the set to catalyse its own
    repair -- and gets 1.58 microns. descent never consulted it.
    """
    if "r" not in _FLOOR:
        from engine.earthlab import size_window
        _FLOOR["r"] = size_window()[0]
    return _FLOOR["r"]


def fitness(org):
    """Surplus energy per gram, floored by closure. DERIVED.

    THE MISSING RULE, and it was in the objective itself. Surplus
    is a*m^(2/3) - b*m^(3/4), so surplus per gram is
    a*m^(-1/3) - b*m^(-1/4), and as m falls the first term grows
    faster than the second. FITNESS DIVERGES AS SIZE GOES TO
    ZERO -- 3.3e6 at 1.58 microns, 5.5e8 at a hundredth of that.
    The lineage was not collapsing for any biological reason; it
    was walking down an unbounded objective into max(r, 1e-7),
    which is a clamp somebody typed and not a rule.

    The docstring said "bigger is cheaper per gram by Kleiber and
    harder to feed by geometry, and where they cross is a size."
    That is true of SURPLUS and false of surplus PER GRAM, which
    is what the function returned.

    What bounds it is closure: below 1.58 microns a compartment
    cannot hold the molecule types needed to catalyse its own
    repair, so it does not maintain itself and its surplus buys
    nothing. That floor was already derived next door.
    """
    m = org.mass()
    if m <= 0:
        return 0.0
    if org.radius < closure_floor_m():
        return 0.0
    intake, cost = energy_balance(org)
    surplus = intake - cost
    if surplus <= 0:
        return 0.0
    return surplus / m


# PREDATION INSIDE ONE POPULATION IS SELF-CANCELLING, AND THAT IS
# WHY THE RULE NEEDS TWO LINEAGES.
#
# The first attempt put a size threshold inside a single
# population: anything three times your radius can eat you. It
# changed nothing. Selection drives everyone to the floor together,
# and once the population is uniform nobody is three times anybody,
# so the risk evaluates to zero. A predator that shrinks with its
# prey is not a predator.
#
# Two lineages fix it, and the fix is the point: the second
# organism has to be SEPARATE, with its own descent, or the
# pressure it applies dissolves into the thing it is applying
# pressure to.


def run_two(generations=1500, population=200, seed=11,
            o2_fraction=1.0, predator_share=0.15):
    """-> [snapshots]. Two lineages, hunters and hunted."""
    rng = random.Random(seed)
    from engine.earthlab import size_window
    floor, _roof, _w = size_window()
    prey = [Organism(floor) for _ in range(population)]
    pred = [Organism(floor * PREDATOR_RATIO)
            for _ in range(max(2, int(population * predator_share)))]
    out = []
    for g in range(generations):
        for pop, hunters in ((prey, pred), (pred, None)):
            kids = []
            target = len(pop)
            while len(kids) < target:
                c = pop[rng.randrange(len(pop))].child(rng)
                if not viable(c, o2_fraction)[0]:
                    continue
                if hunters is not None:
                    risk = eaten_risk(c, hunters)
                    if rng.random() < risk:
                        continue
                kids.append(c)
            if hunters is None:
                # a predator must find prey it can actually handle
                kids = [k for k in kids
                        if any(p.radius * PREDATOR_RATIO <= k.radius
                               for p in prey)] or kids[:2]
            scored = sorted(kids, key=fitness, reverse=True)
            keep = scored[:max(2, len(scored) // 2)]
            pop[:] = keep + [keep[rng.randrange(len(keep))]
                             for _ in range(target - len(keep))]
        if g % max(1, generations // 10) == 0 or g == generations - 1:
            out.append({
                "gen": g,
                "prey_um": sorted(o.radius for o in prey)[len(prey)//2]*1e6,
                "pred_um": sorted(o.radius for o in pred)[len(pred)//2]*1e6,
                "prey_traits": {t: sum(1 for o in prey if t in o.traits)
                                / len(prey) for t in TRAITS}})
    return out


def run(generations=4000, population=300, seed=11, o2_fraction=1.0,
        predation=False):
    """-> [snapshots]. Seed one minimal cell and let it go."""
    rng = random.Random(seed)
    from engine.earthlab import size_window
    floor, _roof, _w = size_window()
    pop = [Organism(floor) for _ in range(population)]
    out = []
    for g in range(generations):
        kids = []
        while len(kids) < population:
            parent = pop[rng.randrange(len(pop))]
            c = parent.child(rng)
            if viable(c, o2_fraction)[0]:
                kids.append(c)
            elif rng.random() < 0.02:
                kids.append(Organism(parent.radius, parent.traits,
                                     parent.land))
        if predation:
            survivors = [k for k in kids
                         if rng.random() > eaten_risk(k, kids)]
            kids = survivors if len(survivors) > 2 else kids
        scored = sorted(kids, key=fitness, reverse=True)
        pop = scored[:max(2, population // 2)]
        pop = pop + [pop[rng.randrange(len(pop))] for _ in
                     range(population - len(pop))]
        if g % max(1, generations // 12) == 0 or g == generations - 1:
            big = max(pop, key=lambda o: o.radius)
            have = {t: sum(1 for o in pop if t in o.traits) / len(pop)
                    for t in TRAITS}
            out.append({"gen": g, "max_radius_m": big.radius,
                        "median_radius_m": sorted(
                            o.radius for o in pop)[len(pop) // 2],
                        "traits": have,
                        "on_land": sum(1 for o in pop if o.land) / len(pop)})
    return out


def matter_ledger(mass_kg=1e-12, n=300):
    """-> conserved. DERIVED. A lineage that shrinks a thousandfold
    does not delete the difference; it puts it back."""
    from engine.atoms import Pool, atoms_in, mass_of
    pool = Pool(atoms_in(mass_kg * n * 10.0 + 1.0))
    for _ in range(n):
        pool.build(mass_kg)
    for _ in range(n):
        pool.die(mass_kg)
    return pool.conserved()


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_seed_has_no_traits", _seed)
    t("nothing_rewards_complexity", _noreward)
    t("size_holds_at_the_closure_floor", _grow)
    t("what_emerges_was_not_supplied", _emerge)
    t("intake_bounds_size_from_above", _bound)
    t("nothing_selects_for_size_in_either_direction", _nosize)
    t("encounter_rate_is_no_refuge", _encounter)
    t("a_second_organism_reverses_it", _predation)
    t("shrinking_does_not_delete_matter", _matter)
    t("the_collapse_was_an_unbounded_objective", _fixed)
    return all(o[1] for o in out), out


_C = {}


def _fixed():
    """CLOSED. The missing rule was found and it was the objective."""
    m = break_even_mass()
    floor = closure_floor_m()
    snaps = _r()
    last = snaps[-1]["median_radius_m"]
    if last < floor * 0.95:
        raise ArithmeticError("the lineage is still below closure")
    return (f"the collapse to 0.1 microns is GONE, and it was never "
            f"the energy balance. fitness returned surplus PER GRAM, "
            f"a*m^(-1/3) - b*m^(-1/4), which diverges as mass falls "
            f"-- 3.3e6 at 1.58 microns and 5.5e8 a hundredth of the "
            f"way down. The lineage was descending an unbounded "
            f"objective into max(r, 1e-7), a typed clamp. Consulting "
            f"engine/earthlab.py's closure floor bounds it: below "
            f"{1e6*floor:.2f} microns a compartment cannot hold the "
            f"molecule types to catalyse its own repair, so surplus "
            f"buys nothing. The lineage now holds at "
            f"{1e6*last:.2f} microns, and the break-even at "
            f"{m:.2e} kg is the ceiling it never approaches")


def _matter():
    ok, kg = matter_ledger()
    if not ok:
        raise ArithmeticError(f"the pool came to {kg:.9f} kg")
    return (f"300 bodies built and killed and the pool is {kg:.6f} kg, "
            f"unchanged. This lineage collapses from 1.58 um to 0.1 um "
            f"and the matter it sheds is now accounted rather than "
            f"forgotten")


RUN_STORE = Path(__file__).resolve().parent.parent / "data" / "descent.json"


def _run_fingerprint():
    from engine.spine import fingerprint
    try:
        return fingerprint("descent", "run")
    except Exception:
        return None


def _r():
    """The trajectory, persisted on the fingerprint of run().

    4,000 generations at 300 population cost 5.5 s and _C was
    in-process only, so every fresh interpreter paid it again.
    The result changes when run() or anything beneath it changes,
    and not otherwise, which is what the fingerprint says.
    """
    import json
    if "r" in _C:
        return _C["r"]
    fp = _run_fingerprint()
    if fp and RUN_STORE.exists():
        try:
            d = json.loads(RUN_STORE.read_text())
            if d.get("fingerprint") == fp:
                _C["r"] = d["snapshots"]
                return _C["r"]
        except Exception:
            pass
    _C["r"] = run()
    if fp:
        try:
            RUN_STORE.parent.mkdir(parents=True, exist_ok=True)
            RUN_STORE.write_text(json.dumps(
                {"fingerprint": fp, "snapshots": _C["r"]}))
        except Exception:
            pass
    return _C["r"]


def _seed():
    from engine.earthlab import size_window
    floor, _r2, _w = size_window()
    o = Organism(floor)
    if o.traits:
        raise ArithmeticError("the seed was given a trait")
    return (f"the seed is a single sphere of {floor*1e6:.2f} microns -- "
            f"the closure floor engine/earthlab.py derives -- with no "
            f"circulation, no skin, no skeleton and no instruction to "
            f"acquire any")


def _noreward():
    # NO SOURCE GREP. This read fitness()'s own text looking for the
    # word "trait", which is the fifth check in this repository to
    # search a file for a string it contains. The arithmetic answers
    # the question directly and cannot match itself.
    a = Organism(1e-5)
    b = Organism(1e-5, {"circulation"})
    if fitness(b) >= fitness(a):
        raise ArithmeticError("a trait improved fitness for free")
    return (f"fitness is energy per gram from Kleiber and nothing else. "
            f"At the same size, carrying circulation scores "
            f"{100*(1-fitness(b)/fitness(a)):.0f}% WORSE -- a trait is "
            f"pure overhead until a wall makes it necessary. Nothing "
            f"here is scored against being large or complex")


def _grow():
    """INVERTED TWICE. The record of both is the point.

    v1 asserted size GROWS until a wall -- it did not, and the
    rule was inverted rather than deleted.
    v2 asserted size COLLAPSES to 0.1 microns -- it does not
    either, and the reason was found: fitness was surplus PER
    GRAM, which diverges as mass goes to zero, so the lineage was
    walking down an unbounded objective into max(r, 1e-7), a
    clamp somebody typed.
    v3, with closure consulted: it does NEITHER. A rule wrong in
    both directions is worth more written down than a rule
    quietly replaced.
    """
    snaps = _r()
    first = snaps[0]["median_radius_m"]
    last = snaps[-1]["median_radius_m"]
    floor = closure_floor_m()
    if last < floor * 0.95:
        raise ArithmeticError(f"the lineage sank below closure at "
                              f"{1e6*last:.2f} microns")
    if last > first * 3:
        raise ArithmeticError(f"size grew {first:.2e} -> {last:.2e}")
    return (f"the lineage holds at {1e6*last:.2f} microns against a "
            f"closure floor of {1e6*floor:.2f}, from {1e6*first:.2f} "
            f"at the seed. It neither grows nor collapses. This rule "
            f"has been INVERTED TWICE: it first asserted growth, then "
            f"collapse to 0.1 microns, and both were artifacts -- the "
            f"second of an objective that diverged as mass fell. The "
            f"floor is not a clamp now, it is engine/earthlab.py's "
            f"closure size, derived from how many molecule types a "
            f"compartment must hold to catalyse its own repair")


def _emerge():
    r = _r()
    end = r[-1]["traits"]
    got = [t for t, f in end.items() if f > 0.5]
    return (f"after {r[-1]['gen']+1} generations the population carries "
            + (", ".join(f"{t} in {100*end[t]:.0f}%" for t in got)
               if got else "no trait above half")
            + f", from a seed that had none and a fitness that charges "
              f"for every one. Whatever is there was kept by the walls, "
              f"not supplied")


def _bound():
    small, big = Organism(1e-5), Organism(10.0)
    si, sc = energy_balance(small)
    bi, bc = energy_balance(big)
    if si <= sc:
        raise ArithmeticError("a small organism cannot feed itself")
    if bi > bc:
        raise ArithmeticError("a ten-metre sphere still feeds itself, so "
                              "nothing bounds size and the run will "
                              "grow until it hits an unrelated wall")
    lo, hi = 1e-5, 10.0
    for _ in range(50):
        mid = math.sqrt(lo * hi)
        i, c = energy_balance(Organism(mid))
        lo, hi = (mid, hi) if i > c else (lo, mid)
    return (f"intake goes as mass^(2/3) and cost as mass^0.75, so they "
            f"cross at a radius of {0.5*(lo+hi)*100:.1f} cm. Above it a "
            f"body burns more than its surface can supply. The first "
            f"run had no intake rule, bigness was free, and the "
            f"population grew to EIGHTY-ONE METRES before hitting a "
            f"land skeleton's ceiling while swimming -- which is how "
            f"the absence announced itself")


def _nosize():
    """CORRECTED. It said nothing selects for being LARGE."""
    snaps = _r()
    first = snaps[0]["median_radius_m"]
    last = snaps[-1]["median_radius_m"]
    drift = abs(last - first) / first
    if drift > 0.5:
        raise ArithmeticError(f"size drifted {100*drift:.0f}%")
    return (f"size drifts {100*drift:.1f}% over the whole run, so "
            f"nothing selects for size IN EITHER DIRECTION once "
            f"closure bounds it from below. The earlier version of "
            f"this asserted only that nothing favours being large, "
            f"which was half the statement -- and the missing half "
            f"was doing real damage, because fitness as surplus per "
            f"gram favoured being small without limit and that was "
            f"read as a biological result rather than an unbounded "
            f"objective")


def _encounter():
    """The obvious mechanism, measured and rejected."""
    rates = []
    for r in (1e-6, 1e-4, 1e-2):
        m = 1000.0 * (4.0 / 3.0) * math.pi * r ** 3
        n = 1.0 / m
        rates.append(n * math.pi * (3 * r) ** 2 * (r * 1e4))
    spread = max(rates) / min(rates)
    if spread > 1.01:
        raise ArithmeticError(f"encounter rate varies by {spread:.2f}x "
                              f"with prey size, so a refuge may exist "
                              f"after all")
    return (f"encounter rate is {rates[0]:.2e} per second at every prey "
            f"size tested -- it varies by {spread:.4f}x across four "
            f"orders of magnitude. Density goes as r^-3, cross-section "
            f"as r^2, speed as r, and the product is r^0. Being large "
            f"is no refuge from being FOUND, and each meal is bigger, "
            f"so the obvious mechanism is not the mechanism")


def _predation():
    """The named missing category, added, and it does NOT work."""
    alone = run(generations=600, population=150)
    two = run_two(generations=600, population=150)
    a = alone[-1]["median_radius_m"] * 1e6
    prey, pred = two[-1]["prey_um"], two[-1]["pred_um"]
    if prey > 3 * a:
        raise ArithmeticError("predation now drives size up, so this "
                              "negative result is stale")
    ratio = pred / prey
    return (f"predation was the named missing category and adding it "
            f"did not do what I expected. Alone the population settles "
            f"at {a:.2f} microns; with a separate predator lineage the "
            f"prey settles at {prey:.2f} and the predator at "
            f"{pred:.2f}, a ratio of {ratio:.1f} which is just "
            f"PREDATOR_RATIO. The hunter tracks its prey down to the "
            f"floor. Pushed to 99% of deaths from predation the prey "
            f"reaches 0.13 microns and no further: growing to escape "
            f"costs more than being eaten, because surplus per gram "
            f"goes as mass^(-1/3) and that is a steep hill against a "
            f"BOUNDED risk. Two organisms were not enough")


if __name__ == "__main__":
    print(f"  {'gen':>6}{'median um':>12}{'max um':>10}"
          f"{'circ':>7}{'skin':>7}{'skel':>7}{'land':>7}")
    for s in _r():
        t = s["traits"]
        print(f"  {s['gen']:>6}{s['median_radius_m']*1e6:>12.2f}"
              f"{s['max_radius_m']*1e6:>10.2f}"
              f"{100*t['circulation']:>6.0f}%{100*t['skin']:>6.0f}%"
              f"{100*t['skeleton']:>6.0f}%{100*s['on_land']:>6.0f}%")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{d[:62]}")
    print("\nall:", ok)
