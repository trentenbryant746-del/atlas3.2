"""What can be carried how far, and what that does to production.

A porter eats the cargo. Walking costs food, food IS the cargo
when the cargo is grain, and so there is a distance at which a
load arrives as nothing. That distance is computable and it sorts
everything anyone might carry into two classes.

  HEAVY AND CHEAP   grain, timber, ore. Range-limited, hard.
  LIGHT OR WEIGHTLESS   salt, obsidian, and TECHNIQUE.

Knowledge is the only cargo with no range limit, because it does
not weigh anything and the carrier still has it after handing it
over. That is not a metaphor here, it is the reason a network of
villages can specialize like one large town without anyone having
to build one.

And once the market is the network rather than the village, output
per worker moves -- not by anyone trying, but because unit cost
falls with cumulative volume, and volume is market size.
"""

import math

from engine.tradition import BAND, spread_years
from engine.craft import LEG, walk_speed

PORTER_KG = 30.0            # CHOSEN, a load carried all day
WALK_HOURS = 6.0
FOOD_MJ_KG = 15.0           # grain
PORTER_MJ_DAY = 14.0        # 10 at rest, loaded and walking
LEARNING_RATE = 0.85        # MEASURED, unit cost per doubling
FARM_EDIBLE = 1e-2          # DERIVED-ish: cultivation over foraging
from engine.power import NPP_W_M2  # one home
from engine.power import NEED_W  # one home
# One home. Was the literal 912, a ROUNDING of 912.5, in two
# modules at once -- found by eval/agreement.py as a frozen
# copy already adrift from the rule it was copied from.
from engine.disease import critical_community as _ccs
VILLAGE = _ccs()


def porter_km_day():
    """A lone adult, not a band. DERIVED from engine/craft."""
    return walk_speed(LEG["adult"]) * 3.6 * WALK_HOURS


def eaten_per_km():
    """kg of the load spent per km of round trip. DERIVED."""
    return (2.0 / porter_km_day()) * (PORTER_MJ_DAY / FOOD_MJ_KG)


def delivered(distance_km, load=PORTER_KG):
    """What arrives. DERIVED."""
    return max(0.0, load - eaten_per_km() * distance_km)


def dead_range_km(load=PORTER_KG):
    """Where the load arrives as nothing. DERIVED."""
    return load / eaten_per_km()


def price_doubles_km(load=PORTER_KG):
    """Where half the load has been eaten. DERIVED."""
    return dead_range_km(load) / 2.0


def carriable(value_per_kg, distance_km):
    """Does it still pay at that distance? DERIVED.

    The cost of carrying is the food eaten; a cargo pays if its
    value exceeds what it cost to move. Weightless cargo has no
    range at all.
    """
    if value_per_kg == math.inf:
        return True
    frac = delivered(distance_km) / PORTER_KG
    return frac > 0.0 and value_per_kg * frac > FOOD_MJ_KG


# --- the network ----------------------------------------------------

def farm_area_m2(n):
    """Ground a settlement cultivates. DERIVED."""
    return n * NEED_W / (NPP_W_M2 * FARM_EDIBLE)


def spacing_km(n=VILLAGE):
    """How far apart settlements sit. DERIVED from their fields."""
    return 2.0 * math.sqrt(farm_area_m2(n) / math.pi) / 1000.0


def network_radius_km(villages, n=VILLAGE):
    """Half-width of a region of `villages`. DERIVED."""
    return math.sqrt(villages * farm_area_m2(n) / math.pi) / 1000.0


def meetings_per_year(villages, n=VILLAGE):
    """How often neighbours actually meet. DERIVED.

    Settled neighbours are one field apart, not one migration.
    """
    round_trip_days = 2.0 * spacing_km(n) / porter_km_day()
    return min(52.0, 1.0 / max(round_trip_days / 7.0, 1.0 / 52.0))


def knowledge_spread_years(villages, n=VILLAGE):
    """Coupon collector at settled meeting rates. DERIVED."""
    return spread_years(villages, meetings_per_year(villages, n))


# --- scale ----------------------------------------------------------

def unit_cost(market, base=VILLAGE):
    """Wright's law. Cost per unit at `market` served. DERIVED."""
    if market <= base:
        return 1.0
    return LEARNING_RATE ** math.log2(market / base)


def productivity(market, base=VILLAGE):
    """Output per worker against a single village. DERIVED."""
    return 1.0 / unit_cost(market, base)


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_porter_eats_the_cargo_and_that_sets_the_range", _range)
    t("knowledge_is_the_only_cargo_with_no_range_limit", _weightless)
    t("settling_puts_neighbours_a_field_apart_not_a_migration", _near)
    t("a_network_specializes_like_a_town_nobody_built", _net)
    return all(x for _, x, _ in res), res


def _range():
    dead, half = dead_range_km(), price_doubles_km()
    if dead <= 0 or delivered(dead) > 1e-9:
        raise ArithmeticError(f"{dead}")
    return (f"a porter carries {PORTER_KG:.0f} kg and walks "
            f"{porter_km_day():.0f} km a day, burning "
            f"{PORTER_MJ_DAY:.0f} MJ against grain at "
            f"{FOOD_MJ_KG:.0f} MJ/kg -- so a round trip spends "
            f"{eaten_per_km():.3f} kg of the load per km. The load "
            f"arrives as nothing at {dead:.0f} km and has doubled in "
            f"price at {half:.0f} km. Grain is not traded far "
            f"because it cannot be: the cargo and the fuel are the "
            f"same substance, and that is a fact about food, not "
            f"about markets")


def _weightless():
    far = 2000.0
    grain, salt = carriable(FOOD_MJ_KG, far), carriable(400.0, far)
    know = carriable(math.inf, far)
    if grain or not know:
        raise ArithmeticError(f"{grain} {salt} {know}")
    return (f"at {far:.0f} km grain delivers "
            f"{delivered(far):.0f} kg and pays: {grain}. Value "
            f"density sorts everything -- salt and obsidian go where "
            f"grain cannot. But technique weighs nothing AND the "
            f"carrier still has it after handing it over, which no "
            f"other cargo does. It is the only thing on this chain "
            f"with no range limit and no loss on transfer, so a "
            f"region can share what it knows long before it can "
            f"share what it grows. Knowledge trade precedes goods "
            f"trade for a reason in physics")


def _near():
    v = 40
    sp, m = spacing_km(), meetings_per_year(v)
    settled, mobile = knowledge_spread_years(v), spread_years(v, 2.0)
    if settled >= mobile:
        raise ArithmeticError(f"{settled} {mobile}")
    return (f"a village of {VILLAGE:.0f} cultivates "
            f"{farm_area_m2(VILLAGE)/1e6:.0f} km2, so settlements sit "
            f"{sp:.1f} km apart -- against the "
            f"{2*math.sqrt(65e6/math.pi)/1000:.0f} km a forager band "
            f"needed. Neighbours are a morning away, not a "
            f"migration, so they meet {m:.0f} times a year instead "
            f"of 2, and a discovery crosses {v} villages in "
            f"{settled:.1f} years instead of {mobile:.0f}. The same "
            f"settling that made everyone sick made everyone "
            f"{mobile/settled:.0f}x quicker to hear about it")


def _net():
    from engine.craft import best_depth
    from engine.literacy import copy_error
    v = 40
    mkt = v * VILLAGE
    one = best_depth(int(VILLAGE), copy_error(2))[1]
    many = best_depth(int(mkt), copy_error(2))[1]
    p = productivity(mkt)
    if many <= one or p <= 1.0:
        raise ArithmeticError(f"{one} {many} {p}")
    return (f"{v} villages of {VILLAGE:.0f} inside a "
            f"{network_radius_km(v):.0f} km radius are "
            f"{mkt:.0f} people who can reach each other. One village "
            f"supports {one} specialties; the network supports "
            f"{many}. And unit cost falls {LEARNING_RATE} per "
            f"doubling of volume, so serving {mkt/VILLAGE:.0f}x the "
            f"market is {math.log2(mkt/VILLAGE):.1f} doublings and "
            f"{p:.1f}x the output per worker. Nobody built a town. "
            f"The specialization a city is usually credited with is "
            f"available to a region that merely keeps in touch, "
            f"because the binding quantity was never how close "
            f"people stand -- it was how many the corpus reaches")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
