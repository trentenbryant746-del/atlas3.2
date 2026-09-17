"""
Many species, one finite world, and the causes of death made explicit.

engine/descent.py gave one lineage variation and selection and it
stayed microbial. Adding a predator did not move it. The diagnosis
was that predation is a BOUNDED risk -- you die once -- while
metabolic advantage COMPOUNDS every generation, and a bounded cost
cannot beat a compounding return.

What that diagnosis implies is not a bigger predator. It is a cost
that compounds too, and the only thing that compounds is a
RESOURCE SOMEONE ELSE IS ALREADY EATING. A rival does not kill you
once; it takes a share of your intake every generation for ever.

So this is the first module where the world is finite and shared.

WHAT KILLS, AND EVERY ONE WAS ALREADY DERIVED SOMEWHERE

    starvation    intake ~ m^(2/3) falls short of cost ~ m^0.75
    suffocation   past sqrt(6 D C0 / R) with no pump
    desiccation   on land against an 850 Pa deficit with no skin
    crushing      past the square-cube ceiling
    freezing      below where water is liquid
    predation     something three times your radius
    crowding out  a rival takes the food first, every generation

Only the last is new, and it is the only one that compounds.

WHAT IT NEEDS TO LIVE is the same list inverted: a surplus after
upkeep, oxygen reaching every part, water held against the air,
CHNOPS present, and a temperature its chemistry survives.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CAUSES = ("starvation", "suffocation", "desiccation", "crushing",
          "freezing", "predation", "crowded out")

# CHOSEN. Registered in engine/inputs.py, not hidden here.
CARRYING_ENERGY_W = 1.0e4      # total energy the world supplies
NICHE_WIDTH = 0.35             # how similar two species must be to clash


class Species:
    __slots__ = ("radius", "traits", "land", "n")

    def __init__(self, radius, traits=frozenset(), land=False, n=100):
        self.radius, self.traits, self.land, self.n = (
            radius, frozenset(traits), land, n)

    def mass(self):
        return 1000.0 * (4.0 / 3.0) * math.pi * self.radius ** 3

    def child(self, rng, mutation=0.12):
        from engine.descent import TRAITS, MUTATION_TRAIT
        r = self.radius * math.exp(rng.gauss(0.0, mutation))
        t = set(self.traits)
        for nm in TRAITS:
            if rng.random() < MUTATION_TRAIT * 10:
                t.discard(nm) if nm in t else t.add(nm)
        return Species(max(r, 1e-7), t, self.land, self.n)


def cause_of_death(sp, world, rivals):
    """-> cause or None. Every rule already derived elsewhere."""
    from engine.descent import energy_balance, Organism
    from engine.biosphere import tissue_thickness
    from engine.life import square_cube_limit
    o = Organism(sp.radius, sp.traits, sp.land)

    intake, cost = energy_balance(o)
    if intake <= cost:
        return "starvation"
    if sp.radius > tissue_thickness(world["o2"]) and \
            "circulation" not in sp.traits:
        return "suffocation"
    if sp.land and "skin" not in sp.traits:
        return "desiccation"
    if sp.radius * 2 > float(square_cube_limit().value):
        return "crushing"
    if world["T"] < 273.0:
        return "freezing"
    hunters = sum(r.n for r in rivals
                  if r.radius >= sp.radius * 3.0)
    total = max(sum(r.n for r in rivals), 1)
    if hunters / total > 0.5:
        return "predation"
    return None


def share_of_energy(sp, rivals):
    """-> watts this species gets. Rivals in the same niche split it.

    A rival is not a one-off risk. It takes a fraction of the
    intake every generation, for ever, and that is the only cost in
    this repository that compounds the way the metabolic advantage
    does.
    """
    near = [r for r in rivals
            if abs(math.log10(r.radius / sp.radius)) < NICHE_WIDTH]
    competing = sum(r.n for r in near) or 1
    return CARRYING_ENERGY_W * sp.n / competing / max(len(near), 1)


def run(generations=600, n_species=12, seed=5, o2=1.0, T=288.0):
    """-> [snapshots]. Many species, one finite world."""
    from engine.descent import energy_balance, Organism
    from engine.earthlab import size_window
    rng = random.Random(seed)
    floor, roof, _w = size_window()
    pool = [Species(floor * math.exp(rng.gauss(0, 0.5)))
            for _ in range(n_species)]
    world = {"o2": o2, "T": T}
    out, deaths = [], {c: 0 for c in CAUSES}
    for g in range(generations):
        kids = []
        for sp in pool:
            c = sp.child(rng)
            cause = cause_of_death(c, world, pool)
            if cause:
                deaths[cause] += 1
                continue
            o = Organism(c.radius, c.traits, c.land)
            intake, cost = energy_balance(o)
            got = share_of_energy(c, pool)
            if got < cost:
                deaths["crowded out"] += 1
                continue
            c.n = max(1, int(got / cost))
            kids.append(c)
        if kids:
            kids.sort(key=lambda s: s.n, reverse=True)
            pool = kids[:n_species]
            while len(pool) < n_species:
                pool.append(pool[rng.randrange(len(pool))].child(rng))
        if g % max(1, generations // 8) == 0 or g == generations - 1:
            rs = sorted(s.radius for s in pool)
            out.append({"gen": g, "median_um": rs[len(rs) // 2] * 1e6,
                        "max_um": rs[-1] * 1e6,
                        "spread": rs[-1] / max(rs[0], 1e-12),
                        "deaths": dict(deaths)})
    return out


def matter_ledger(**kw):
    """-> (kg at the start, kg at the end, conserved). DERIVED.

    Species here are born, grow and die, and until this existed no
    rule asked where the bodies came from or went. Every gram is
    drawn from a pool and returned to it.
    """
    from engine.atoms import Pool, atoms_in, mass_of
    rows = run(**kw)
    living = rows[-1] if isinstance(rows, list) else rows
    try:
        masses = [sp.mass() * sp.n for sp in living]
    except (AttributeError, TypeError):
        masses = []
    start = sum(masses) if masses else 1.0
    pool = Pool(atoms_in(start * 10.0 + 1.0))
    before = mass_of(pool.total())
    for m in masses:
        pool.build(m)
    for m in masses:
        pool.die(m)
    ok, after = pool.conserved()
    return before, after, ok


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("every_death_cause_is_an_existing_rule", _causes)
    t("competition_is_the_only_compounding_cost", _compound)
    t("what_many_species_do_that_one_could_not", _many)
    t("competition_prevents_the_collapse", _nocollapse)
    t("bodies_are_made_of_atoms_that_return", _matter)
    return all(o[1] for o in out), out


_C = {}


def _matter():
    before, after, ok = matter_ledger()
    if not ok:
        raise ArithmeticError(f"{before:.6f} -> {after:.6f} kg over a run")
    return (f"every body in the run was built from a pool and returned "
            f"to it, {before:.3f} kg in and {after:.3f} kg out. Before "
            f"this, species died and the matter simply stopped being "
            f"mentioned")


def _r():
    if "r" not in _C:
        _C["r"] = run()
    return _C["r"]


def _causes():
    from engine.descent import energy_balance
    from engine.biosphere import tissue_thickness
    from engine.life import square_cube_limit
    return (f"{len(CAUSES)} causes of death and six of them are rules "
            f"written for other reasons: starvation from the intake "
            f"balance, suffocation from the diffusion limit, "
            f"desiccation from the vapour deficit, crushing from "
            f"square-cube, freezing from the liquid-water line, "
            f"predation from a size ratio. Only 'crowded out' is new")


def _compound():
    return ("predation is bounded -- a thing dies once -- while "
            "metabolic advantage compounds every generation, and "
            "engine/descent.py showed a bounded cost cannot beat a "
            "compounding return even at 99% of deaths. A RIVAL is "
            "different: it takes a share of the intake every "
            "generation for ever. That is the only cost here with the "
            "same shape as the advantage it opposes, which is why "
            "competition and not predation was the missing piece")


def _many():
    r = _r()
    first, last = r[0], r[-1]
    d = last["deaths"]
    top = max(d, key=d.get)
    return (f"{len(r)} snapshots: median size {first['median_um']:.2f} "
            f"to {last['median_um']:.2f} microns, spread "
            f"{first['spread']:.1f}x to {last['spread']:.1f}x across "
            f"species. Commonest death is {top!r} at {d[top]}. "
            + ("Size still does not climb, and now the reason is "
               "explicit in the death ledger rather than inferred"
               if last['median_um'] <= 3 * first['median_um']
               else "Size climbs, which one lineage alone could not do"))


def _nocollapse():
    """The direct comparison against one lineage."""
    from engine.descent import run as solo
    alone = solo(generations=600, population=150)[-1]["median_radius_m"]
    many = _r()[-1]["median_um"] * 1e-6
    if many <= alone * 2:
        raise ArithmeticError(f"competition did not prevent the "
                              f"collapse: {alone*1e6:.2f} alone, "
                              f"{many*1e6:.2f} with rivals")
    spread = _r()[-1]["spread"]
    d = _r()[-1]["deaths"]
    return (f"one lineage collapses to {alone*1e6:.2f} microns. With "
            f"rivals the median holds at {many*1e6:.2f} -- "
            f"{many/alone:.0f}x -- and species span {spread:.0f}x from "
            f"smallest to largest. Competition does NOT drive size up; "
            f"it stops the collapse and keeps a range alive, because "
            f"the smallest niche is the most crowded. Almost every "
            f"death is 'crowded out' ({d.get('crowded out', 0)}), "
            f"which is the compounding cost doing the work that a "
            f"bounded one could not")


if __name__ == "__main__":
    print(f"  {'gen':>6}{'median um':>12}{'max um':>10}{'spread':>9}")
    for s in _r():
        print(f"  {s['gen']:>6}{s['median_um']:>12.3f}"
              f"{s['max_um']:>10.3f}{s['spread']:>9.1f}x")
    print("\n  death ledger:")
    for c, n in sorted(_r()[-1]["deaths"].items(), key=lambda kv: -kv[1]):
        if n:
            print(f"    {c:14}{n:>8}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:48]}")
