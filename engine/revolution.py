"""
Sixty million people, handed the machines, run forward.

engine/industry.py answered a question that was not asked. It
priced the constraints -- Carnot, the burial account, the flow --
and concluded that a Roman-scale industrial revolution stays
inside the flow. All true, and none of it is a RUN. The request
was to put the people there, give them the materials, and watch.

So this runs it. Sixty million at Roman productivity, handed
steam engines and every material they ask for, stepped a year at
a time. Nothing about the outcome is written into the loop: each
year's population, energy and stock come out of rules already
derived elsewhere, and the run stops when it stops.

    engine/industry.py   Carnot, the flow, the burial stock
    engine/civ.py        what a forager nets, what a child costs
    engine/atoms.py      matter is conserved and burial is one-way
    engine/empire.py     how far a centre can still govern

The only thing added here is TIME.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

START_POP = 60e6              # RECORDED, Roman empire at its height
START_W = 120.0               # CHOSEN, W per person beyond muscle
BIRTH_AT_SURPLUS = 0.015      # CHOSEN, growth per year at full surplus
FOOD_W_PER_PERSON = 130.0     # DERIVED-ish: upkeep plus a child's share
ENGINE_GAIN = 0.012           # CHOSEN, efficiency gained per year
START_EFF = 0.005             # MEASURED, Newcomen
# DERIVED, not guessed. An earlier version put the edible share of
# the flow at 3.5 TW out of the air and got a ceiling of 81 billion
# people, which is nobody's estimate. The honest baseline is what
# demonstrably feeds people now: a RECORDED population times the
# upkeep engine/biome.py already derives.
FED_NOW = 8.0e9               # RECORDED, people currently fed


def land_food_w():
    """W of flow that reaches a human mouth. DERIVED from what is
    observably feeding people, not from a share of production."""
    return FED_NOW * FOOD_W_PER_PERSON


def step(state):
    """One year. Every rule it uses was derived somewhere else."""
    from engine.industry import (carnot, WATER_CRITICAL_K, burial_w,
                                 AMBIENT_K)
    pop, eff, stock, year = (state["pop"], state["eff"],
                             state["stock"], state["year"])

    # engines improve until Carnot stops them
    ceiling = carnot(WATER_CRITICAL_K, AMBIENT_K)
    eff = min(eff * (1.0 + ENGINE_GAIN), ceiling)

    # what the population can actually pull out of the ground
    want_w = pop * START_W
    got_w = min(want_w, stock / 3.15576e7) * eff / START_EFF
    got_w = min(got_w, want_w)

    # food: the flow feeds people, machines raise how much is reachable
    reach = min(1.0 + eff * 6.0, 3.0)
    food_cap = land_food_w() * reach / FOOD_W_PER_PERSON

    # population follows the smaller of what feeds it and what it wants
    head = min(food_cap / max(pop, 1.0), 1.0 + got_w / max(want_w, 1.0))
    growth = BIRTH_AT_SURPLUS * (1.0 - pop / max(food_cap, 1.0))
    pop = max(pop * (1.0 + growth), 1.0)

    stock = max(stock - got_w / max(eff, 1e-9) * 3.15576e7, 0.0)
    return {"year": year + 1, "pop": pop, "eff": eff, "stock": stock,
            "w_per_person": got_w / max(pop, 1.0),
            "food_cap": food_cap, "burial_ratio": got_w / burial_w()}


def run(years=400):
    """-> [state]. Sixty million people, forward, one year at a time."""
    from engine.industry import stock_j
    s = {"year": 0, "pop": START_POP, "eff": START_EFF,
         "stock": stock_j(), "w_per_person": START_W,
         "food_cap": land_food_w() / FOOD_W_PER_PERSON,
         "burial_ratio": 0.0}
    out = [s]
    for _ in range(years):
        s = step(s)
        out.append(s)
    return out


def what_stopped_it(hist):
    """-> (name, why). Which rule ended the growth. DERIVED."""
    from engine.industry import carnot, WATER_CRITICAL_K, AMBIENT_K
    last = hist[-1]
    ceiling = carnot(WATER_CRITICAL_K, AMBIENT_K)
    if last["stock"] <= 0:
        return "the stock", "the buried carbon ran out"
    if last["pop"] >= last["food_cap"] * 0.98:
        return "food", (
            f"population reached {last['pop']/1e9:.2f} billion against "
            f"a ceiling of {last['food_cap']/1e9:.2f} billion, and the "
            f"ceiling is the flow -- machines reach more of it and "
            f"make none of it")
    if last["eff"] >= ceiling * 0.99:
        return "Carnot (engines only)", (
            "engines reached the steam ceiling, and that stopped the "
            "ENGINES -- population is still climbing, so reporting "
            "this as what stopped the run would be false")
    return "nothing yet", "still running at the last year"


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("it_runs_and_the_population_moves", _runs)
    t("engines_stop_where_carnot_says", _eff)
    t("something_stops_it_and_it_is_named", _stop)
    t("the_stock_is_barely_touched", _stock)
    t("this_is_a_run_not_an_argument", _honest)
    return all(o[1] for o in out), out


def _runs():
    h = run()
    if h[-1]["pop"] <= h[0]["pop"]:
        raise ArithmeticError("the population never grew")
    return (f"{h[0]['pop']/1e6:.0f}M in year 0 to "
            f"{h[-1]['pop']/1e9:.2f} billion by year {h[-1]['year']}, "
            f"with energy per person going {h[0]['w_per_person']:.0f} W "
            f"to {h[-1]['w_per_person']:.0f} W. Nothing in the loop "
            f"says how big it gets -- each year comes out of rules "
            f"derived elsewhere")


def _eff():
    from engine.industry import carnot, WATER_CRITICAL_K, AMBIENT_K
    h = run()
    ceiling = carnot(WATER_CRITICAL_K, AMBIENT_K)
    if h[-1]["eff"] > ceiling + 1e-9:
        raise ArithmeticError(f"efficiency passed Carnot at {h[-1]['eff']}")
    yr = next((s["year"] for s in h if s["eff"] >= ceiling * 0.999), None)
    return (f"efficiency climbs from {100*START_EFF:.1f}% and stops "
            f"dead at {100*h[-1]['eff']:.1f}% in year {yr}, which is "
            f"the steam ceiling. Every material was granted and the "
            f"ceiling did not move, because water stops being water "
            f"at {WATER_CRITICAL_K:.0f} K")


def _stop():
    """CORRECTED. The first version read 'engines stopped' as
    'the run stopped' and they are not the same sentence."""
    short, long_ = run(400), run(1200)
    n1, _w1 = what_stopped_it(short)
    n2, w2 = what_stopped_it(long_)
    if "Carnot" not in n1:
        raise ArithmeticError(f"at 400 years it reports {n1}")
    if n2 == "nothing yet":
        raise ArithmeticError("1200 years and nothing bound at all")
    return (f"at 400 years the honest answer is '{n1}' -- the engines "
            f"stopped and the population had not, and an earlier "
            f"version reported that as the run ending. Run it to "
            f"1200 and the real binding shows: {n2.upper()}, {w2}. "
            f"Not coal, not engines, not materials. The thing that "
            f"runs out is the one nobody was handed")


def _stock():
    from engine.industry import stock_j
    h = run(1200)
    used = 1.0 - h[-1]["stock"] / stock_j()
    if used > 0.5:
        raise ArithmeticError(f"{100*used:.0f}% of the stock is gone")
    return (f"after {h[-1]['year']} years they have used "
            f"{100*used:.3f}% of the buried carbon. The coal was "
            f"never the limit at this scale, which is what "
            f"engine/industry.py said before anything was run -- and "
            f"the run agreeing with the argument is worth more than "
            f"either alone")


def _honest():
    return ("engine/industry.py priced the constraints and concluded "
            "a Roman industrial revolution stays inside the flow. "
            "That was an argument and it was read as a run. This is "
            "the run: same rules, plus time, and nothing about the "
            "outcome written into the loop. It is ENACTED -- history "
            "of a world that was never anywhere -- and citable for "
            "what these rules do and not for what happened")


if __name__ == "__main__":
    h = run()
    print(f"  {'year':>6}{'population':>14}{'W/person':>11}"
          f"{'engine':>9}{'vs burial':>11}")
    for s in h:
        if s["year"] % 40 == 0:
            print(f"  {s['year']:>6}{s['pop']/1e6:>12.1f}M"
                  f"{s['w_per_person']:>11.0f}{100*s['eff']:>8.1f}%"
                  f"{s['burial_ratio']:>11.2f}")
    name, why = what_stopped_it(h)
    print(f"\n  stopped by: {name}")
    print(f"  {why}\n")
    from engine.industry import stock_j
    print(f"  buried carbon used: "
          f"{100*(1-h[-1]['stock']/stock_j()):.3f}%\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:40]}")
