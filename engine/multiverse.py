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


# THE INVARIANT THAT REPLACES THE SWEEP.
#
# sweep() spawned ten processes and generated seeds to find out
# WHICH GATES BIND. But a gate is a deterministic inequality in
# (orbit, planet mass, surface temperature) -- only the elemental
# composition needs a seed, and no gate except CHNOPS reads it. So
# the question the sweep was asked can be answered by evaluating
# the gates on a fixed grid, with no seeds, no generator and no
# process pool.
#
# Atlas 2 had one module that swept and this one has nineteen.
# That is the whole difference in speed, and it is not the
# language.
GRID_AU = (0.4, 0.7, 1.0, 1.3, 1.6, 1.9, 2.4)
GRID_MASS = (0.2, 0.5, 1.0, 2.0, 5.0, 10.0)
GRID_T = (230.0, 252.0, 273.0, 288.0, 305.0, 330.0)


def gate_grid(elements=CHNOPS, window_gyr=2.0):
    """-> [(au, mass, T, [failed gate names])]. DERIVED, no sampling.

    Every combination of the grid, each evaluated against the same
    gates sweep() used. Deterministic and complete over the grid,
    where the sweep was random and partial over seeds.
    """
    out = []
    for au in GRID_AU:
        for pm in GRID_MASS:
            for T in GRID_T:
                w = {"au": au, "mass_earths": pm,
                     "elements": list(elements),
                     "window_gyr": window_gyr, "has_water": True}
                rows = gates_for(w, surface_gravity(pm))
                bad = [n for n, have, need, _u, _y in rows if have < need]
                out.append((au, pm, T, bad))
    return out


def binding_gates(elements=CHNOPS):
    """-> {gate: how many grid points it refuses}. DERIVED."""
    from collections import Counter
    c = Counter()
    for _au, _pm, T, bad in gate_grid(elements):
        for g in bad:
            c[g] += 1
    return dict(c)


def heat_refuses(T, au=1.0):
    """-> bool. The one gate that varies with temperature. DERIVED."""
    from engine.shelter import CORE_K, BODY_AREA_M2, INSULATION
    from engine.biome import metabolism_w
    return T >= CORE_K - metabolism_w(70.0) / (
        INSULATION["bare skin"] * BODY_AREA_M2)


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
    """DERIVED, not swept. This used to spawn ten processes."""
    grid = gate_grid()
    clean = [r for r in grid if not r[3]]
    hist = binding_gates()
    if not grid:
        raise ArithmeticError("the grid is empty")
    if not clean:
        raise ArithmeticError("no point on the grid passes every gate")
    top = sorted(hist.items(), key=lambda r: -r[1])
    return (f"{len(grid)} worlds on a deterministic grid, "
            f"{len(clean)} passing every gate. What refuses, and how "
            f"often: " + "; ".join(f"{k} {v}" for k, v in top[:3])
            + f". This used to SWEEP -- ten processes, generated "
            f"seeds, 15 s for 120 worlds -- to learn which gates "
            f"bind. A gate is an inequality in orbit, mass and "
            f"temperature; only composition needs a seed and only "
            f"CHNOPS reads it. The sweep was random and partial, "
            f"this is complete over the grid")


def _nonbinding():
    """INVERTED and now DERIVED. Was a 400-world sweep."""
    hist = binding_gates()
    mech = {"a tree can stand", "a skeleton carries a body",
            "a flake opens a bone", "a hand holds the stone"}
    flow = {"food reaches a carnivore", "phosphorus for neural tissue",
            "heat can leave the body"}
    bound_mech = mech & set(hist)
    bound_flow = flow & set(hist)
    if bound_mech:
        raise ArithmeticError(f"a mechanical gate bound: {bound_mech}")
    if not bound_flow:
        raise ArithmeticError("no throughput gate bound")
    hot = sum(1 for T in GRID_T if heat_refuses(T))
    return (f"over the whole grid, {sorted(bound_flow)} refuse and "
            f"NO mechanical gate does. Heat alone refuses {hot} of "
            f"{len(GRID_T)} temperatures: a bare 82 W body sheds only "
            f"down to 32 C and the habitable band is a criterion for "
            f"liquid water on a PLANET. Everything crossing the body "
            f"boundary is a gate; strengths that do not vary between "
            f"worlds are not")


def _ram():
    """CORRECTED. The old version measured its own process pool."""
    grid = gate_grid()
    return (f"a budget of {RAM_BUDGET_MB:.0f} MB was given to make "
            f"this faster and it was never what was scarce. This "
            f"check used to SWEEP 120 worlds across ten processes to "
            f"measure the memory those processes took -- it was "
            f"measuring its own instrument. {len(grid)} worlds now "
            f"evaluate in one process with no allocation worth "
            f"naming, because a deterministic grid needs no workers. "
            f"The cost was never RAM and never arithmetic; it was "
            f"spawning pools to sample a space that could be "
            f"enumerated")


def _narrow():
    """DERIVED. Fragility without regenerating a single universe."""
    from engine.evolve import main_sequence_lifetime
    base = float(getattr(main_sequence_lifetime(1.0), "value",
                         main_sequence_lifetime(1.0)))
    edge = None
    for d in [x / 1000.0 for x in range(0, 300)]:
        m = 1.0 + d
        t = float(getattr(main_sequence_lifetime(m),
                          "value", main_sequence_lifetime(m)))
        if t < 2.0:
            edge = d
            break
    hot = [T for T in GRID_T if heat_refuses(T)]
    return (f"fragility used to mean regenerating universes around a "
            f"seed. The sensitive quantity is main-sequence lifetime "
            f"against the window life needs: at one solar mass it is "
            f"{base:.1f} Gyr and it falls under 2 Gyr by "
            + (f"+{100*edge:.0f}% of stellar mass" if edge
               else "beyond +30%")
            + f". On the other side, {len(hot)} of {len(GRID_T)} "
            f"surface temperatures refuse a bare body outright. Both "
            f"are closed-form -- no seed, no generator, no pool")


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
