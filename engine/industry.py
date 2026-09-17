"""
Sixty million people, every material they ask for, and the answer.

The request was to spawn a Roman-empire population, hand them the
industrial revolution and every material it needs, and see what
happens. Giving away the materials is the interesting part,
because it removes the answer everyone expects and leaves whatever
was actually in the way.

WHAT AN INDUSTRIAL REVOLUTION IS, IN THIS REPOSITORY'S OWN TERMS.
engine/atoms.py already keeps two books: matter in CIRCULATION and
matter BURIED. Burial was introduced as the leak that stops a
cycle being a cycle -- the one percent that does not come back,
which the module named as coal and oil before anything here
intended to burn any. An industrial revolution is not a new kind
of energy. IT IS THE BURIAL ACCOUNT, RUN BACKWARDS.

    land photosynthesis, the FLOW      352 TW
    buried each year at 0.1%           352 GW
    accumulated over 300 Myr, the STOCK  3.3e27 J

AND FREE MATERIALS DO NOT LIFT THE CEILING. Carnot does not care
what the boiler is made of, only how hot it runs, and a steam
engine cannot run hotter than water stays water. Past 647 K there
is no liquid to boil, so the working fluid caps the whole thing at
about 55% no matter what is spawned. Newcomen got 0.5% against a
21% ceiling -- the gap was never a shortage of iron.

SIXTY MILLION IS NOT ENOUGH TO MATTER. At a kilowatt each they
draw 60 GW against a 352 GW burial rate: a sixth of what the
planet buries while they burn it. A Roman industrial revolution
would have been INSIDE THE FLOW, and would not have been the thing
that word now means.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

POPULATION = 60e6            # RECORDED, Roman empire at its height
LAND_M2 = 1.49e14            # MEASURED
BURIAL_FRACTION = 1e-3       # CHOSEN, share of production buried
STOCK_MYR = 300.0            # MEASURED, Carboniferous onward
WATER_CRITICAL_K = 647.1     # MEASURED, above this no liquid
AMBIENT_K = 293.0            # MEASURED
MUSCLE_W = 97.0              # MEASURED, a working human
MODERN_TW = 18.0             # RECORDED, present human power draw

ENGINES = {                  # MEASURED boiler temperatures
    "Newcomen 1712": 373.0, "Watt 1776": 400.0,
    "high pressure 1850": 450.0, "triple expansion 1890": 480.0,
}


def flow_w():
    """W. Everything photosynthesis makes on land. DERIVED."""
    from engine.biome import surface_light, PHOTOSYNTHETIC_EFFICIENCY
    return surface_light() * PHOTOSYNTHETIC_EFFICIENCY * LAND_M2


def burial_w():
    """W-equivalent buried each year. DERIVED."""
    return flow_w() * BURIAL_FRACTION


def stock_j(myr=STOCK_MYR):
    """J sitting underground. DERIVED from the burial rate and time."""
    return burial_w() * myr * 1e6 * 3.15576e7


def carnot(hot_k, cold_k=AMBIENT_K):
    """Ceiling on any heat engine. DERIVED, and it ignores materials."""
    return 1.0 - cold_k / hot_k


def steam_ceiling():
    """The best a steam engine can ever do. DERIVED.

    Materials do not enter. Water stops being water at 647 K.
    """
    return carnot(WATER_CRITICAL_K)


def muscle_w(pop=POPULATION):
    """W of human output. DERIVED."""
    return pop * MUSCLE_W


def draw_w(pop=POPULATION, per_person_w=1000.0):
    """W an industrialised population pulls. DERIVED."""
    return pop * per_person_w


def drawdown(pop=POPULATION, per_person_w=1000.0):
    """-> ratio. Years of burial burned per year. DERIVED."""
    return draw_w(pop, per_person_w) / burial_w()


def inside_the_flow(pop=POPULATION, per_person_w=1000.0):
    """-> (bool, why). Is this a revolution or just machinery?"""
    d = drawdown(pop, per_person_w)
    return d < 1.0, (
        f"{pop/1e6:.0f} million at {per_person_w:.0f} W each draw "
        f"{draw_w(pop, per_person_w)/1e9:.0f} GW against "
        f"{burial_w()/1e9:.0f} GW buried a year, a ratio of {d:.2f}")


def what_materials_buy(hot_k):
    """-> (achievable, ceiling, why). DERIVED."""
    c = carnot(min(hot_k, WATER_CRITICAL_K))
    return c, steam_ceiling(), (
        f"a boiler at {hot_k:.0f} K allows {100*c:.1f}% and no "
        f"material raises it past {100*steam_ceiling():.1f}%, because "
        f"water is not liquid above {WATER_CRITICAL_K:.0f} K")


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("an_industrial_revolution_is_burial_run_backwards", _books)
    t("free_materials_do_not_lift_the_ceiling", _carnot)
    t("sixty_million_is_not_enough_to_matter", _scale)
    t("what_we_actually_do_is_the_striking_number", _modern)
    t("the_stock_is_finite_and_that_is_arithmetic", _finite)
    return all(o[1] for o in out), out


def _books():
    from engine.atoms import Pool, atoms_in
    p = Pool(atoms_in(1000.0))
    p.build(400.0)
    p.die(400.0, returned=0.999)
    buried = sum(p.buried.values())
    if buried <= 0:
        raise ArithmeticError("nothing was buried")
    return (f"engine/atoms.py already kept two books and called the "
            f"gap between them coal and oil, before anything here "
            f"intended to burn any. Land photosynthesis runs "
            f"{flow_w()/1e12:.0f} TW and buries "
            f"{burial_w()/1e9:.0f} GW-equivalent a year, which over "
            f"{STOCK_MYR:.0f} Myr is {stock_j():.2e} J. An industrial "
            f"revolution is not a new kind of energy -- IT IS THE "
            f"BURIAL ACCOUNT RUN BACKWARDS")


def _carnot():
    best = max(ENGINES.values())
    got, ceil, why = what_materials_buy(best)
    if ceil > 0.7 or got > ceil:
        raise ArithmeticError(f"{100*got:.0f}% against {100*ceil:.0f}%")
    return (f"{why}. Newcomen managed about 0.5% against a "
            f"{100*carnot(ENGINES['Newcomen 1712']):.0f}% ceiling, so "
            f"the gap was never a shortage of iron. Spawning every "
            f"material asked for moves NOTHING here: Carnot does not "
            f"read the parts list, only the temperature")


def _scale():
    ok, why = inside_the_flow()
    if not ok:
        raise ArithmeticError("60 million already overruns the flow")
    return (f"{why}. A Roman industrial revolution would have been "
            f"INSIDE THE FLOW -- machinery, not a revolution, and "
            f"not the thing that word now means. Their whole muscle "
            f"output is {muscle_w()/1e9:.1f} GW, so a thousand watts "
            f"each is already a tenfold change in their lives and "
            f"still invisible to the planet")


def _modern():
    d = MODERN_TW * 1e12 / burial_w()
    if d < 10:
        raise ArithmeticError(f"the modern ratio is only {d:.1f}")
    return (f"we draw {MODERN_TW:.0f} TW against {burial_w()/1e9:.0f} "
            f"GW of burial, so EVERY YEAR WE BURN ABOUT {d:.0f} YEARS "
            f"OF ACCUMULATION. That number, and not any invention, is "
            f"what separates an industrial revolution from a lot of "
            f"machinery -- and it came out of a burial rate this "
            f"repository wrote down to explain why a leak is not a "
            f"cycle")


def _finite():
    years = stock_j() / (MODERN_TW * 1e12) / 3.15576e7
    if years <= 0:
        raise ArithmeticError("the stock is empty")
    return (f"{stock_j():.2e} J at {MODERN_TW:.0f} TW lasts "
            f"{years:,.0f} years. That is arithmetic and not a "
            f"warning -- a stock divided by a rate. Whether the "
            f"estimate of what is recoverable matches what was "
            f"buried is a question this file cannot answer, and the "
            f"burial fraction it rests on is CHOSEN")


if __name__ == "__main__":
    print(f"  flow    {flow_w()/1e12:>8.1f} TW   all land photosynthesis")
    print(f"  burial  {burial_w()/1e9:>8.1f} GW   at "
          f"{100*BURIAL_FRACTION:.1f}% of production")
    print(f"  stock   {stock_j():>8.2e} J    over {STOCK_MYR:.0f} Myr\n")
    print(f"  {'engine':<24}{'boiler':>8}{'Carnot':>9}")
    for nm, k in ENGINES.items():
        print(f"  {nm:<24}{k:>7.0f}K{100*carnot(k):>8.1f}%")
    print(f"  {'any steam engine ever':<24}{WATER_CRITICAL_K:>7.0f}K"
          f"{100*steam_ceiling():>8.1f}%\n")
    print(f"  {POPULATION/1e6:.0f}M people:")
    for w in (100, 1000, 5000):
        ok, why = inside_the_flow(per_person_w=w)
        print(f"    {w:>5} W each -> {drawdown(per_person_w=w):>6.2f}x "
              f"the burial rate  {'inside the flow' if ok else 'DRAWING DOWN'}")
    print(f"    modern world    -> "
          f"{MODERN_TW*1e12/burial_w():>6.0f}x\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:48}{d[:32]}")
