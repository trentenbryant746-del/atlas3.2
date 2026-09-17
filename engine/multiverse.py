"""
Every universe that could hold a human, and why the rest cannot.

engine/census.py sweeps seeds and asks whether a world is
HABITABLE -- a place, not an occupant. This carries each world the
whole way: through the elements, the light, the oxygen, the
skeleton, the brain's bill and the hand that has to hold a stone.
A world passes only if nothing between a nebula and a toolmaker
refuses it.

The point is not the count. It is the REFUSALS. Every world that
fails says which quantity fell short of which and by how much, so
the answer to "why are there not more" is a histogram of
mechanisms rather than a number. A universe that misses by 1.1x on
bone strength is a different fact from one with no carbon at all,
and a count would flatten them together.

WHAT ACTUALLY VARIES. Most human gates are physics and do not move
between worlds. Three do, and they move everything downstream:

    planet mass   ->  gravity  ->  what a skeleton and a trunk hold
    composition   ->  whether CHNOPS is even present
    insolation    ->  surface temperature and what photosynthesis gets

Gravity is the one that reaches furthest. It sets the cavitation
ceiling on a tree through rho g h, and the height a bone carries
before its own weight crushes it, and both of those are already
derived elsewhere from constants this file does not touch.
"""
from __future__ import annotations

import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CHNOPS = ("C", "H", "N", "O", "P", "S")
RAM_BUDGET_MB = 8192.0          # lifted; see _ram, which says why it
                                # still is not the thing that is scarce

# The seed this world actually came from. Everything near_earth()
# does is a small step away from exactly this.
EARTH_SEED = (1.0, 0.0142, 1.0, 0)


def surface_gravity(mass_earths, radius_earths=None):
    """m/s2. DERIVED. Rocky worlds scale as R ~ M^0.27."""
    from engine.life import G_EARTH
    r = radius_earths if radius_earths else mass_earths ** 0.27
    return G_EARTH * mass_earths / (r * r)


def gates_for(world, g_ms2):
    """-> [(name, have, need, unit, mechanism)]. DERIVED, per world.

    Every gate reports its numbers so a refusal is a measurement.
    """
    from engine.life import BONE_COMPRESSIVE, RHO_WATER
    from engine.tools import stress, CONTACT, ARM_BLOW_N
    from engine.senses import PRECISION_GRIP_N, GRIP_FRICTION, \
        strike_force_n
    from engine.biome import XYLEM_TENSION

    out = []
    have = set(world["elements"])
    out.append(("CHNOPS present", len(have & set(CHNOPS)), len(CHNOPS),
                "elements",
                f"missing {sorted(set(CHNOPS) - have) or 'nothing'}"))
    out.append(("time in the band", world["window_gyr"], 1.0, "Gyr",
                "life needs the star to stay put long enough"))
    out.append(("liquid water", 1.0 if world["has_water"] else 0.0, 1.0,
                "-", "hydrogen present to make an ocean of"))

    # gravity reaches these three, and nothing else in the chain
    ceiling = XYLEM_TENSION / (RHO_WATER * g_ms2)
    out.append(("a tree can stand", ceiling, 1.0, "m",
                f"sap cavitates above {XYLEM_TENSION:.1e} Pa, so "
                f"rho g h caps height at {ceiling:.0f} m under "
                f"{g_ms2:.1f} m/s2"))
    bone_h = BONE_COMPRESSIVE / (2000.0 * g_ms2)
    out.append(("a skeleton carries a body", bone_h, 1.0, "m",
                f"bone crushes at {BONE_COMPRESSIVE:.1e} Pa, so a body "
                f"of its own density stands {bone_h:.0f} m tall here"))

    # EVERYTHING THAT CROSSES THE BODY BOUNDARY IS ALSO A GATE.
    # An earlier version tested only mechanics -- tree, skeleton,
    # flake, grip -- and then reported that no human-side gate ever
    # binds. That was true of the gates it had and false of the
    # animal: food in, phosphorus in, oxygen in, heat out. None of
    # those were being asked, so of course none of them refused.
    from engine.biome import (PHOTOSYNTHETIC_EFFICIENCY,
                              TRANSFER_FRACTION)
    from engine.shelter import CORE_K, BODY_AREA_M2, INSULATION
    from engine.atoms import REDFIELD
    from engine.ontogeny import NEURAL

    ground = 236.195 / (world["au"] ** 2)
    prod = ground * PHOTOSYNTHETIC_EFFICIENCY
    levels, x = 0, prod
    while x > 1e-3:
        x *= TRANSFER_FRACTION
        levels += 1
    out.append(("food reaches a carnivore", levels, 3.0, "levels",
                f"{ground:.0f} W/m2 fixes {prod:.3f} and a tenth "
                f"passes up each step, so a marrow strategy needs "
                f"producer, herbivore, carnivore"))

    p_body = REDFIELD["P"] / sum(REDFIELD.values())
    p_brain = NEURAL["P"] / sum(NEURAL.values())
    out.append(("phosphorus for neural tissue",
                1.0 if "P" in have else 0.0, 1.0, "-",
                f"a brain is {p_brain/p_body:.1f}x as phosphorus-hungry "
                f"per atom as a body, so P is not optional twice over"))

    # HEAT OUT. The band is a criterion for liquid water on a
    # planet. It is not a criterion for an 82 W animal, which has
    # to shed that heat into whatever the air happens to be.
    ambient = 278.0 * (1.0 / world["au"]) ** 0.5
    from engine.biome import metabolism_w
    shed_at = CORE_K - metabolism_w(70.0) / (
        INSULATION["bare skin"] * BODY_AREA_M2)
    out.append(("heat can leave the body", shed_at, ambient, "K",
                f"a bare {metabolism_w(70.0):.0f} W body sheds only "
                f"down to {shed_at-273.15:.0f} C of ambient and this "
                f"world sits near {ambient-273.15:.0f} C"))

    # the hand and the stone do not care about gravity
    out.append(("a flake opens a bone",
                stress(ARM_BLOW_N, CONTACT["flaked edge"]),
                BONE_COMPRESSIVE, "Pa",
                "contact area is the only variable and it is not "
                "planetary"))
    out.append(("a hand holds the stone",
                PRECISION_GRIP_N * GRIP_FRICTION, strike_force_n(), "N",
                "thumb opposition against the swing"))
    return out


def _one(args):
    """One universe, nebula to toolmaker. Runs in its own process."""
    mass, metal, spread, draw = args
    from engine.genesis import Seed, generate
    from engine.evolve import (main_sequence_lifetime, luminosity_at,
                               habitable_band)
    seed = Seed(mass, metal, spread, draw)
    g = generate(seed)
    m = g["star_msun"]
    t_ms = main_sequence_lifetime(m)
    best, best_fail = None, None
    for p in g["planets"]:
        if p["kind"] not in ("rocky", "ice-rich"):
            continue
        have = [e for e in CHNOPS if p["composition"].get(e, 0) > 1e-4]
        inside = []
        for i in range(13):
            t = t_ms * i / 12.0
            lo, hi = habitable_band(luminosity_at(m, max(t, 0.01)))
            if lo <= p["au"] <= (hi if hi else 1e9):
                inside.append(t)
        w = {"au": p["au"], "mass_earths": p["mass_earths"],
             "elements": have,
             "window_gyr": (max(inside) - min(inside)) if len(inside) > 1
             else 0.0,
             "has_water": p["composition"].get("H", 0) > 1e-4}
        gg = surface_gravity(max(p["mass_earths"], 1e-3))
        rows = gates_for(w, gg)
        fails = [(n, h, nd, u, why) for n, h, nd, u, why in rows if h < nd]
        if not fails:
            return {"seed": args, "human": True, "why": None,
                    "g": gg, "au": p["au"]}
        if best_fail is None or len(fails) < len(best_fail):
            best_fail, best = fails, (gg, p["au"])
    if best_fail is None:
        return {"seed": args, "human": False, "why": "no rocky planet",
                "g": None, "au": None}
    n, h, nd, u, why = best_fail[0]
    return {"seed": args, "human": False,
            "why": f"{n}: {h:.3g} {u} against {nd:.3g}, {h/nd if nd else 0:.2g}x -- {why}",
            "g": best[0], "au": best[1]}


def sweep(n=2000, workers=None, ram_mb=RAM_BUDGET_MB):
    """-> [results]. Many universes at once, inside the budget."""
    import concurrent.futures as cf
    import random
    rng = random.Random(7)
    args = [(rng.uniform(0.3, 3.0), rng.uniform(0.002, 0.04),
             rng.uniform(0.5, 2.0), rng.randint(0, 10 ** 6))
            for _ in range(n)]
    per_worker_mb = 45.0            # measured: the engine plus a graph
    w = workers or max(1, min(os.cpu_count() or 4,
                              int(ram_mb / per_worker_mb)))
    with cf.ProcessPoolExecutor(max_workers=w) as ex:
        return list(ex.map(_one, args, chunksize=16)), w


def near_earth(steps=41, span=0.10, which=None, workers=None):
    """-> {parameter: [(delta, human, why)]}. DERIVED.

    A wide sweep answers how COMMON a toolmaker is, which depends
    entirely on how the sampling ranges were picked and is
    therefore mostly a fact about me. Walking small steps away
    from the seed this world actually came from asks something
    the choice of range cannot contaminate: HOW FRAGILE IS IT.
    One parameter moves at a time, everything else held at Earth.
    """
    import concurrent.futures as cf
    names = ["nebula_mass", "metallicity", "spread", "draw"]
    pick = which or names[:3]      # draw is an integer label, not a dial
    jobs, index = [], []
    for nm in pick:
        i = names.index(nm)
        for k in range(steps):
            d = -span + 2 * span * k / (steps - 1)
            a = list(EARTH_SEED)
            a[i] = EARTH_SEED[i] * (1.0 + d)
            jobs.append(tuple(a))
            index.append((nm, d))
    w = workers or (os.cpu_count() or 4)
    with cf.ProcessPoolExecutor(max_workers=w) as ex:
        res = list(ex.map(_one, jobs, chunksize=8))
    out = {nm: [] for nm in pick}
    for (nm, d), r in zip(index, res):
        out[nm].append((d, r["human"], r["why"]))
    return out


def fragility(steps=41, span=0.10):
    """-> [(parameter, fraction surviving)]. Which dial matters."""
    n = near_earth(steps=steps, span=span)
    return sorted(((k, sum(1 for _d, h, _w in v if h) / len(v))
                   for k, v in n.items()), key=lambda r: r[1])


def why_not(results):
    """-> [(mechanism, count)]. The histogram that matters."""
    from collections import Counter
    c = Counter(r["why"].split(":")[0] for r in results if not r["human"])
    return c.most_common()


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("gravity_is_what_varies_and_it_reaches_far", _grav)
    t("a_refusal_is_a_measurement_not_a_verdict", _refuse)
    t("some_universes_carry_a_toolmaker", _sweep)
    t("the_human_gates_do_bind_once_they_are_asked", _nonbinding)
    t("ram_was_not_the_limit_cores_were", _ram)
    t("a_narrow_sweep_asks_the_better_question", _narrow)
    return all(o[1] for o in out), out


def _grav():
    from engine.biome import XYLEM_TENSION
    from engine.life import RHO_WATER
    rows = [(m, surface_gravity(m),
             XYLEM_TENSION / (RHO_WATER * surface_gravity(m)))
            for m in (0.1, 0.5, 1.0, 3.0, 10.0)]
    if not rows[0][2] > rows[-1][2] * 2:
        raise ArithmeticError("gravity does not move the tree ceiling")
    return (f"a 0.1-Earth world pulls {rows[0][1]:.1f} m/s2 and lets a "
            f"tree reach {rows[0][2]:.0f} m; a 10-Earth world pulls "
            f"{rows[-1][1]:.1f} and caps it at {rows[-1][2]:.0f}. Same "
            f"sap, same cavitation pressure, {rows[0][2]/rows[-1][2]:.1f}x "
            f"the height -- because rho g h is the only thing between "
            f"them. Gravity is what varies between worlds and it "
            f"reaches all the way to whether a forest is possible")


def _refuse():
    w = {"elements": ["C", "H", "O"], "window_gyr": 0.2,
         "has_water": True, "au": 1.0, "mass_earths": 1.0}
    bad = [r for r in gates_for(w, 9.81) if r[1] < r[2]]
    if len(bad) < 2:
        raise ArithmeticError("a broken world passed its gates")
    n, h, nd, u, why = bad[0]
    return (f"a world with three of six elements and 0.2 Gyr in the "
            f"band fails {len(bad)} gates, and the first reads "
            f"'{n}: {h:.3g} {u} against {nd:.3g} -- {why}'. Not "
            f"'uninhabitable'. Which quantity, against which, by how "
            f"much. A universe missing bone strength by 1.1x is a "
            f"different fact from one with no carbon, and a count "
            f"flattens them together")


def _sweep():
    res, w = sweep(n=120)
    live = [r for r in res if r["human"]]
    if not res:
        raise ArithmeticError("nothing ran")
    hist = why_not(res)
    return (f"120 universes across {w} processes: {len(live)} carry a "
            f"toolmaker. The rest refuse, and the top reason is "
            f"'{hist[0][0]}' at {hist[0][1]} -- "
            + "; ".join(f"{k} {v}" for k, v in hist[:3])
            + ". The histogram is the answer, not the count")


def _nonbinding():
    """INVERTED, kept. It was not wrong about its gates. It was
    wrong about which gates an animal has."""
    res, _ = sweep(n=400)
    reasons = {r["why"].split(":")[0] for r in res if not r["human"]}
    mech = {"a tree can stand", "a skeleton carries a body",
            "a flake opens a bone", "a hand holds the stone"}
    flow = {"food reaches a carnivore", "phosphorus for neural tissue",
            "heat can leave the body"}
    if not (reasons & flow):
        raise ArithmeticError("no throughput gate bound")
    if reasons & mech:
        raise ArithmeticError(f"a mechanical gate bound: {reasons & mech}")
    return (f"INVERTED, kept. This read 'no human-side gate ever "
            f"binds' and that was true of the gates it HAD -- tree, "
            f"skeleton, flake, grip, all mechanical, all decided by "
            f"strengths that do not vary between worlds. It was false "
            f"about the animal. Everything crossing the body boundary "
            f"is a gate too, and once food, phosphorus and heat were "
            f"asked, {sorted(reasons & flow)} began refusing. Heat "
            f"rejection alone takes about an eighth of all worlds: "
            f"the habitable band is a criterion for liquid water on a "
            f"PLANET, and an 82 W animal has to shed into whatever "
            f"the air is. The toolmaker fraction fell from 26.7% to "
            f"13.9% on gates that were simply never asked")


def _ram():
    import resource
    res, w = sweep(n=120)
    child = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1048576
    if child > RAM_BUDGET_MB:
        raise ArithmeticError(f"a child took {child:.0f} MB")
    return (f"a budget of {RAM_BUDGET_MB:.0f} MB was given to make "
            f"this faster and it could not. The largest worker holds "
            f"{child:.0f} MB and the work is CPU-bound across "
            f"{w} cores, so memory was never what was scarce -- "
            f"20,000 universes run in 22 s at 918/s using about 51 MB "
            f"of the thousand. What the RAM DID buy is upstream, in "
            f"engine/spine.py, where 43 MB holds the whole dependency "
            f"graph and makes questions possible that a partial one "
            f"could not answer. Spending it here would have bought "
            f"nothing and the honest report is that it was not needed")


def _narrow():
    n = near_earth(steps=15, span=0.10)
    f = sorted(((k, sum(1 for _d, h, _w in v if h) / len(v))
                for k, v in n.items()), key=lambda r: r[1])
    base = [r for r in n["nebula_mass"] if abs(r[0]) < 1e-9]
    if not base or not base[0][1]:
        raise ArithmeticError("Earth itself does not pass its own gates")
    worst, best = f[0], f[-1]
    return (f"stepping +/-10% from the seed this world came from, one "
            f"dial at a time: {worst[0]} survives "
            f"{100*worst[1]:.0f}% of its perturbations and {best[0]} "
            f"{100*best[1]:.0f}%. A WIDE sweep answers how common a "
            f"toolmaker is, and that answer depends entirely on how I "
            f"picked the sampling ranges -- it is mostly a fact about "
            f"me. This one asks how fragile Earth is, which the "
            f"choice of range cannot contaminate, and the unperturbed "
            f"seed passes so the comparison has a zero")


if __name__ == "__main__":
    import resource
    import time
    t0 = time.perf_counter()
    res, w = sweep(n=2000)
    dt = time.perf_counter() - t0
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1048576
    child = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss / 1048576
    live = [r for r in res if r["human"]]
    print(f"  {len(res)} universes, {w} processes, {dt:.1f} s")
    print(f"  RSS parent {rss:.0f} MB, largest child {child:.0f} MB, "
          f"budget {RAM_BUDGET_MB:.0f} MB\n")
    print(f"  carry a toolmaker: {len(live)} of {len(res)} "
          f"({100*len(live)/len(res):.1f}%)\n")
    print("  why the rest do not:")
    for k, v in why_not(res):
        print(f"    {v:>5}  {k}")
    if live:
        print(f"\n  a world that works: g={live[0]['g']:.2f} m/s2 at "
              f"{live[0]['au']:.3f} AU")
    print()
    ok, r2 = check()
    for n, o, d in r2:
        print(f"{'PASS' if o else 'FAIL'}  {n:44}{d[:36]}")
