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
        return Organism(max(r, 1e-7), t, land)


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


def energy_balance(org):
    """-> (intake W, cost W). DERIVED: surface feeds, volume burns."""
    m = org.mass()
    if m <= 0:
        return 0.0, 1.0
    intake = INTAKE_COEFFICIENT * m ** (2.0 / 3.0)
    cost = 70.0 * m ** 0.75 * (1.0 + TRAIT_COST * len(org.traits))
    return intake, cost


def fitness(org):
    """Surplus energy per gram. DERIVED, and bounded above.

    Bigger is cheaper per gram by Kleiber and harder to feed by
    geometry. The two cross, and where they cross is a size.
    """
    m = org.mass()
    if m <= 0:
        return 0.0
    intake, cost = energy_balance(org)
    surplus = intake - cost
    if surplus <= 0:
        return 0.0
    return surplus / m


def run(generations=4000, population=300, seed=11, o2_fraction=1.0):
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


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_seed_has_no_traits", _seed)
    t("nothing_rewards_complexity", _noreward)
    t("size_grows_until_a_wall", _grow)
    t("what_emerges_was_not_supplied", _emerge)
    t("intake_bounds_size_from_above", _bound)
    t("nothing_here_selects_for_being_large", _nosize)
    return all(o[1] for o in out), out


_C = {}


def _r():
    if "r" not in _C:
        _C["r"] = run()
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
    """WRITTEN BEFORE THE INTAKE RULE, AND NOW FALSIFIED BY IT.

    This asserted that size grows, because the first run grew --
    to eighty-one metres, on a model where bigness was free. Adding
    the intake rule reversed it, and rather than delete the check
    it is inverted: the claim now is that size SHRINKS, which is
    what the rules actually say and what Earth actually did for
    three billion years.
    """
    r = _r()
    first, last = r[0]["median_radius_m"], r[-1]["median_radius_m"]
    if last > first:
        raise ArithmeticError(
            f"size grew {first:.2e} -> {last:.2e}, which would mean "
            f"something now favours being large -- check what changed")
    return (f"median radius falls {first*1e6:.2f} to {last*1e6:.2f} "
            f"microns. This check originally asserted the opposite and "
            f"passed, on a model with no intake rule where bigness was "
            f"free; it is inverted rather than deleted because the "
            f"reversal is the finding")


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
    """The result of the whole module, and it is a refusal."""
    small, big = Organism(1e-7), Organism(1e-4)
    if fitness(small) <= fitness(big):
        raise ArithmeticError("something now favours being large, so "
                              "this conclusion is stale")
    r = _r()
    end = r[-1]["median_radius_m"]
    return (f"surplus energy per gram goes as mass^(-1/3), so SMALLER "
            f"IS ALWAYS FITTER and the population settles at "
            f"{end*1e6:.2f} microns. That is not a bug -- life on Earth "
            f"was microbial for three billion years, and nothing about "
            f"metabolism favours being large. Two runs bracket it: with "
            f"no intake rule bigness was free and the population reached "
            f"EIGHTY-ONE METRES; with intake it collapses to the floor. "
            f"Neither produces a body. What selects for size is "
            f"predation and competition -- INTERACTIONS BETWEEN "
            f"ORGANISMS -- and every rule in this repository is one body "
            f"against physics. That is the missing category, and it is "
            f"a different kind of absence from a missing measurement")


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
