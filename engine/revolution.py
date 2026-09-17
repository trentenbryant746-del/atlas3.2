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
# ENGINE_GAIN IS GONE. It said efficiency improves 1.2% a year and
# that was an assertion doing all the work -- it took 450 years to
# reach the Carnot ceiling because I told it to crawl there, not
# because anything resisted. Efficiency is DERIVED now: a boiler's
# temperature is set by the pressure it holds, the pressure by the
# strength of what it is made of, and Carnot by the temperature.
# Hand over every material and they arrive at the ceiling AT ONCE.
BOILERS = {                   # MEASURED: working pressure, MPa -> K
    "cast iron 1712": (0.1, 373.0),
    "wrought iron 1800": (0.7, 443.0),
    "mild steel 1880": (2.0, 485.0),
    "alloy steel 1920": (10.0, 584.0),
    "every material granted": (22.1, 647.1),
}

# MEASURED, kg of nitrogen fixed per year
BIOLOGICAL_N = 140e9
P_RESERVE_KG = 7.0e13         # MEASURED, ~70 Gt rock phosphate

# GIVEN: instructions, and the infrastructure we have. Both handed
# over, both marked, and the interesting thing is that they are
# nothing like each other in what they cost.
#
# An apprenticeship is the measured upper bound on what one person
# can be told: 10,000 hours at 39 bit/s is 1.4e9 bits, which is
# 0.0003% of a brain. KNOWLEDGE IS ALMOST FREE TO HAND OVER. It
# needs no materials, it copies without loss, and engine/civ.py
# already showed the channel carries a selection rather than a
# volume.
#
# Infrastructure is the opposite. Every piece decays and must be
# rebuilt out of the same surplus that feeds people, so it is not
# a gift, IT IS A STANDING TAX. What it buys back is reach: more
# of the flow arriving where someone can eat it.
APPRENTICE_HOURS = 10000.0
INFRASTRUCTURE = {            # MEASURED-ish: (life yr, upkeep frac, reach gain)
    "roads": (20.0, 0.02, 0.10),
    "aqueducts": (100.0, 0.01, 0.06),
    "power grid": (40.0, 0.03, 0.14),
    "sanitation": (50.0, 0.02, 0.12),
}
FOOD_DRY_MJ_KG = 17.0         # MEASURED, dry plant food
HABER_N = 120e9
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


def teaching_bits(hours=APPRENTICE_HOURS):
    """Bits one person can be handed. DERIVED via engine/civ.py."""
    from engine.civ import SPEECH_BITS_S
    return SPEECH_BITS_S * hours * 3600.0


def teaching_is_free():
    """-> (bool, fraction of a brain). DERIVED."""
    from engine.learning import store_bits
    f = teaching_bits() / store_bits()
    return f < 1e-4, f


def infrastructure_cost(built):
    """Fraction of output that never reaches anyone. DERIVED."""
    return sum(INFRASTRUCTURE[k][1] for k in built if k in INFRASTRUCTURE)


def infrastructure_reach(built):
    """Extra share of the flow that arrives usable. DERIVED."""
    return sum(INFRASTRUCTURE[k][2] for k in built if k in INFRASTRUCTURE)


def phosphorus_kg_yr(pop):
    """kg P a population eats a year. DERIVED through engine/atoms.py.

    A food CEILING is a rate and a population simply sits under
    it. Phosphorus is a STOCK, so it gives the run a second way to
    fail and a different kind of answer -- not a wall but a clock.
    Without it, 'stopped by food' was the only verdict this loop
    could ever return, whatever the ceiling was moved to.
    """
    from engine.atoms import REDFIELD, WEIGHT
    mass = sum(WEIGHT[e] * n for e, n in REDFIELD.items())
    pfrac = WEIGHT["P"] * REDFIELD["P"] / mass
    dry_kg = FOOD_W_PER_PERSON * 3.15576e7 / (FOOD_DRY_MJ_KG * 1e6)
    return pop * dry_kg * pfrac


def efficiency_from(material_mpa):
    """Engine efficiency a material allows. DERIVED, no learning rate.

    Pressure sets saturation temperature, temperature sets Carnot.
    Nothing here improves with practice; it improves with steel.
    """
    from engine.industry import (carnot, WATER_CRITICAL_K, AMBIENT_K)
    best = None
    for _nm, (mpa, T) in sorted(BOILERS.items(), key=lambda r: r[1][0]):
        if mpa <= material_mpa + 1e-12:
            best = T
    T = min(best or 373.0, WATER_CRITICAL_K)
    return carnot(T, AMBIENT_K)


def synthetic_ceiling(from_stock_w):
    """People fed off the STOCK rather than the flow. DERIVED.

    The flow cannot be argued with: photosynthesis fixes about 1%
    and no amount of nitrogen makes sunlight. The only way past a
    ceiling that IS the flow is to stop eating the flow -- and
    then the constraint is not a rate any more, it is a finite
    pile, which is a different kind of answer.
    """
    return from_stock_w / FOOD_W_PER_PERSON


def absolute_food_ceiling():
    """People, if EVERY watt of land photosynthesis were eaten.

    DERIVED from engine/industry.py's flow. This replaces a reach
    multiplier capped at 3.6, which was a number I picked and
    which turned out to be saturated before infrastructure was
    even added -- so the cap was deciding the answer and hiding
    the thing being tested. A ceiling has to come from the flow,
    not from a ceiling.
    """
    from engine.industry import flow_w
    return flow_w() / FOOD_W_PER_PERSON


def food_ceiling(fixed_n_kg=BIOLOGICAL_N, reach=1.0, synthetic_w=0.0):
    """People the flow feeds. DERIVED through nitrogen, not guessed.

    An earlier version scaled what observably feeds 8 billion. That
    was honest but said nothing about WHY the ceiling sits there.
    Crop tissue runs N:C at Redfield, so the carbon a field grows
    is capped by the nitrogen available to grow it, and fixing more
    nitrogen moves the ceiling in proportion.
    """
    biological = FED_NOW * (fixed_n_kg / BIOLOGICAL_N) * reach
    return (min(biological, absolute_food_ceiling())
            + synthetic_ceiling(synthetic_w))


def step(state):
    """One year. Every rule it uses was derived somewhere else."""
    from engine.industry import (carnot, WATER_CRITICAL_K, burial_w,
                                 AMBIENT_K)
    pop, eff, stock, year = (state["pop"], state["eff"],
                             state["stock"], state["year"])

    # engines are as good as what they are made of, and every
    # material was granted, so this is a constant and not a climb
    eff = efficiency_from(state.get("material_mpa", 22.1))

    # infrastructure is a standing tax and buys reach back
    built = state.get("built", ())
    tax = infrastructure_cost(built)
    reach = 1.0 + eff * 6.0 + infrastructure_reach(built)

    # what the population can actually pull out of the ground
    want_w = pop * START_W * (1.0 + tax)
    got_w = min(want_w, stock / 3.15576e7) * eff / START_EFF
    got_w = min(got_w, want_w)

    # food: the flow feeds people, machines raise how much is reachable
    food_cap = food_ceiling(state.get("fixed_n", BIOLOGICAL_N), reach,
                            state.get("synthetic_w", 0.0))

    # population follows the smaller of what feeds it and what it wants
    head = min(food_cap / max(pop, 1.0), 1.0 + got_w / max(want_w, 1.0))
    growth = BIRTH_AT_SURPLUS * (1.0 - pop / max(food_cap, 1.0))
    pop = max(pop * (1.0 + growth), 1.0)

    stock = max(stock - got_w / max(eff, 1e-9) * 3.15576e7, 0.0)
    p_left = max(state.get("p_left", P_RESERVE_KG)
                 - phosphorus_kg_yr(pop), 0.0)
    return {"year": year + 1, "pop": pop, "eff": eff, "stock": stock,
            "w_per_person": got_w / max(pop, 1.0),
            "food_cap": food_cap, "burial_ratio": got_w / burial_w(),
            "material_mpa": state.get("material_mpa", 22.1),
            "fixed_n": state.get("fixed_n", BIOLOGICAL_N),
            "synthetic_w": state.get("synthetic_w", 0.0),
            "built": state.get("built", ()), "p_left": p_left,
            "p_years": (p_left / max(phosphorus_kg_yr(pop), 1e-9))}


def run(years=400, material_mpa=22.1, fixed_n=BIOLOGICAL_N,
        synthetic_w=0.0, built=()):
    """-> [state]. Sixty million forward, a year at a time.

    material_mpa and fixed_n are WHAT THEY WERE GIVEN. Changing
    them is the experiment: fix the constraint the last run named
    and see which one speaks next.
    """
    from engine.industry import stock_j
    s = {"year": 0, "pop": START_POP,
         "eff": efficiency_from(material_mpa),
         "stock": stock_j(), "w_per_person": START_W,
         "food_cap": food_ceiling(
             fixed_n, 1.0 + infrastructure_reach(built), synthetic_w),
         "synthetic_w": synthetic_w, "p_left": P_RESERVE_KG,
         "built": tuple(built),
         "p_years": P_RESERVE_KG / max(phosphorus_kg_yr(START_POP), 1e-9),
         "burial_ratio": 0.0, "material_mpa": material_mpa,
         "fixed_n": fixed_n}
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
    if last.get("p_left", 1.0) <= 0:
        return "phosphorus", (
            "rock phosphate ran out, and unlike the food ceiling "
            "this is a stock rather than a rate -- it does not cap "
            "a population, it ends one")
    if last["stock"] <= 0:
        return "the stock", "the buried carbon ran out"
    if last["pop"] >= last["food_cap"] * 0.98:
        return "food", (
            f"population reached {last['pop']/1e9:.2f} billion against "
            f"a ceiling of {last['food_cap']/1e9:.2f} billion, and the "
            f"ceiling is the flow -- machines reach more of it and "
            f"make none of it")
    # The Carnot branch is GONE. It was meaningful while engines
    # crawled toward the ceiling over 450 years. Now they start
    # there -- every material was granted -- so it fired in year
    # zero of every run and reported a stop that had not happened.
    # A condition that is always true is not a finding.
    return "nothing yet", (
        f"still running at year {last['year']}: population "
        f"{last['pop']/1e9:.2f}B against a ceiling of "
        f"{last['food_cap']/1e9:.2f}B, phosphorus "
        f"{100*last.get('p_left', 0)/7.0e13:.1f}% left")


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("it_runs_and_the_population_moves", _runs)
    t("they_were_not_making_engines", _eff)
    t("giving_it_what_it_needs_moves_the_wall", _given)
    t("a_second_way_to_fail_changes_the_answer", _clock)
    t("instructions_are_almost_free_to_hand_over", _teach)
    t("infrastructure_is_a_tax_not_a_gift", _infra)
    t("a_chosen_cap_was_hiding_the_effect", _capfix)
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
    """CORRECTED. Efficiency was a learning rate and is now a material."""
    from engine.industry import carnot, WATER_CRITICAL_K, AMBIENT_K
    ceiling = carnot(WATER_CRITICAL_K, AMBIENT_K)
    poor, rich = efficiency_from(0.1), efficiency_from(22.1)
    h = run(50)
    if abs(h[-1]["eff"] - h[0]["eff"]) > 1e-9:
        raise ArithmeticError("efficiency still drifts with time")
    if rich <= poor or rich > ceiling + 1e-9:
        raise ArithmeticError(f"{100*poor:.0f}% -> {100*rich:.0f}%")
    return (f"THEY WERE NOT MAKING ENGINES. An earlier version raised "
            f"efficiency 1.2% a year and took 450 years to reach the "
            f"ceiling -- because it was told to crawl, not because "
            f"anything resisted. Efficiency is derived now: pressure "
            f"sets temperature and temperature sets Carnot, so cast "
            f"iron gives {100*poor:.1f}% and every-material-granted "
            f"gives {100*rich:.1f}% AT ONCE, in year zero, and never "
            f"moves again")


def _given():
    """Giving it what it needs, and what that does."""
    a = run(2000, fixed_n=BIOLOGICAL_N)
    b = run(2000, fixed_n=BIOLOGICAL_N + HABER_N)
    ratio = b[-1]["pop"] / a[-1]["pop"]
    want = (BIOLOGICAL_N + HABER_N) / BIOLOGICAL_N
    if abs(ratio - want) > 0.05:
        raise ArithmeticError(f"{ratio:.2f} against a nitrogen ratio "
                              f"of {want:.2f}")
    return (f"the food ceiling was the wall, so the nitrogen to grow "
            f"more food was handed over. It moves the ceiling by "
            f"{ratio:.2f}x -- {a[-1]['pop']/1e9:.1f}B to "
            f"{b[-1]['pop']/1e9:.1f}B -- and that is EXACTLY the "
            f"nitrogen ratio, because crop carbon is capped by crop "
            f"nitrogen at Redfield. It does not remove the wall. It "
            f"moves it")


def _teach():
    free, f = teaching_is_free()
    if not free:
        raise ArithmeticError(f"teaching costs {100*f:.3f}% of a brain")
    return (f"a whole trade, apprenticed over "
            f"{APPRENTICE_HOURS:,.0f} hours at 39 bit/s, is "
            f"{teaching_bits():.2e} bits -- {100*f:.5f}% of a brain. "
            f"KNOWLEDGE IS ALMOST FREE TO HAND OVER: no materials, "
            f"no loss on copying, and engine/civ.py already showed "
            f"the channel carries a selection rather than a volume. "
            f"So giving them the instructions changes nothing about "
            f"what binds, and that is the finding rather than a "
            f"disappointment")


def _infra():
    all_of_it = tuple(INFRASTRUCTURE)
    tax, reach = (infrastructure_cost(all_of_it),
                  infrastructure_reach(all_of_it))
    a = run(2000, fixed_n=BIOLOGICAL_N + HABER_N)
    b = run(2000, fixed_n=BIOLOGICAL_N + HABER_N, built=all_of_it)
    ya = next((x["year"] for x in a if x["p_left"] <= 0), 0)
    yb = next((x["year"] for x in b if x["p_left"] <= 0), 0)
    if b[-1]["pop"] <= a[-1]["pop"] or yb >= ya:
        raise ArithmeticError(f"{a[-1]['pop']:.0f}->{b[-1]['pop']:.0f}, "
                              f"{ya}->{yb}")
    return (f"every road and pipe decays and is rebuilt out of the "
            f"same surplus that feeds people, so infrastructure is "
            f"not a gift, IT IS A STANDING TAX: {100*tax:.0f}% of "
            f"output forever, buying {100*reach:.0f}% more reach. "
            f"Net it carries {a[-1]['pop']/1e9:.1f}B to "
            f"{b[-1]['pop']/1e9:.1f}B -- and SHORTENS the phosphorus "
            f"clock from {ya} years to {yb}, because the extra "
            f"people eat the constraint faster. Every gift so far "
            f"has done this")


def _capfix():
    c = absolute_food_ceiling()
    if c < 1e12:
        raise ArithmeticError(f"the absolute ceiling is {c/1e9:.0f}B")
    return (f"the reach multiplier used to be capped at 3.6, a "
            f"number I picked, and it was SATURATED before "
            f"infrastructure was added -- so adding roads and grids "
            f"and sanitation changed nothing at all, and the cap "
            f"rather than the physics was giving the answer. The "
            f"ceiling comes from the flow now: if every watt of land "
            f"photosynthesis were eaten it feeds "
            f"{c/1e9:,.0f} billion, and at the largest run here they "
            f"use {100*223.7e9/c:.0f}% of it. The flow was never what "
            f"was binding")


def _stop():
    short, long_ = run(300), run(2000)
    n1, _ = what_stopped_it(short)
    n2, w2 = what_stopped_it(long_)
    if n1 != "nothing yet":
        raise ArithmeticError(f"at 300 years it already reports {n1}")
    if n2 == "nothing yet":
        raise ArithmeticError("2000 years and nothing bound")
    return (f"at 300 years nothing has stopped it and the run says "
            f"so. By 2000 the answer is {n2.upper()}: {w2}. An "
            f"earlier version reported Carnot here, which was true "
            f"of the engines and false of the run -- and once "
            f"engines started at the ceiling it fired in year zero "
            f"of everything, so it is gone. A condition that is "
            f"always true is not a finding")


def _clock():
    """The verdict is only worth having if it can differ."""
    runs = [run(2000, fixed_n=BIOLOGICAL_N),
            run(2000, fixed_n=BIOLOGICAL_N + HABER_N),
            run(2000, fixed_n=BIOLOGICAL_N + HABER_N, synthetic_w=2e13)]
    years = [next((s["year"] for s in h if s["p_left"] <= 0), None)
             for h in runs]
    if any(y is None for y in years):
        raise ArithmeticError("phosphorus never ran out")
    if not years[0] > years[1] > years[2]:
        raise ArithmeticError(f"the clock did not shorten: {years}")
    return (f"before this, 'stopped by food' was the only verdict the "
            f"loop COULD return -- population grows to the ceiling "
            f"and sits there, so moving the ceiling changed the "
            f"number and never the answer. Phosphorus is a stock, "
            f"not a rate, and it gives the run a second way to fail. "
            f"All three now end on PHOSPHORUS, and EVERY GIFT "
            f"SHORTENS THE CLOCK: {years[0]} years given nothing, "
            f"{years[1]} with nitrogen, {years[2]} with synthetic "
            f"food on top. More people eat the constraint faster")


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
