"""Who holds what, and why nobody could hold anything before.

engine/group.py already answered the flat case and the answer was
flat: strength_share(n) = 1/n, and spare_per_head() = 0 at every
band size. There was nothing over. A forager cannot be rich
because there is no surplus and, more to the point, nowhere to
put one -- a carcass is worthless in a week.

So power is not assumed here either. Three things have to be true
before anyone can hold more than a share, and each one arrives
somewhere else on this chain:

  A SURPLUS      farming. engine/accident.py's grain harvest
  SOMETHING TO PUT IT IN  the same harvest: 365 days, not 14
  A WAY TO KEEP OTHERS OFF  and this is the one that does the work

The third is geometry. A granary is a POINT and a foraging range
is an AREA, and you defend a point with a perimeter of metres and
an area with a perimeter of kilometres. That ratio is the whole
of it.
"""

import math

from engine.tradition import BAND

# what a forager needs underfoot
NPP_W_M2 = 0.5              # MEASURED, temperate net primary production
EDIBLE_FRACTION = 1e-4      # CHOSEN, of NPP a human can actually eat
NEED_W = 116.0              # 10 MJ/day
GRANARY_RADIUS_M = 5.0

WALL_ADVANTAGE = 3.0        # CHOSEN, one behind a wall matches three


def range_per_head_m2():
    """Ground one forager needs. DERIVED."""
    return NEED_W / (NPP_W_M2 * EDIBLE_FRACTION)


def range_perimeter_m(n=BAND):
    """The border of the country that feeds a band. DERIVED."""
    area = range_per_head_m2() * n
    return 2.0 * math.pi * math.sqrt(area / math.pi)


def store_perimeter_m():
    """The border of a granary. DERIVED."""
    return 2.0 * math.pi * GRANARY_RADIUS_M


def defensibility(n=BAND):
    """How much cheaper a store is to hold than a range. DERIVED."""
    return range_perimeter_m(n) / store_perimeter_m()


def insiders(n=BAND, wall=1.0):
    """How many must share the holding to keep it. DERIVED.

    Strength is headcount (engine/group.strength_share), so g
    holders backed by `wall` must match the n-1-g excluded:
    g*wall >= n-1-g.
    """
    g = math.ceil((n - 1) / (wall + 1.0))
    return int(g) + 1


def power_share(n=BAND, wall=1.0):
    """Fraction of the stock one insider commands. DERIVED."""
    return 1.0 / insiders(n, wall)


def concentration(n=BAND, wall=1.0):
    """Insider's share over an equal share. DERIVED."""
    return power_share(n, wall) * n


def reach(literate_fraction, population):
    """People a claim can bind. DERIVED.

    Spoken, a claim binds whoever heard it and dies with them.
    Written, it binds anyone who can read it, including people
    not yet born -- so the reach of a claim is the reach of the
    channel, and engine/literacy.py says that is f, growing.
    """
    return max(1.0, literate_fraction * population)


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_forager_cannot_be_rich_and_it_is_not_about_virtue", _flat)
    t("a_store_is_a_point_and_a_range_is_an_area", _geom)
    t("power_is_shared_wider_than_anyone_holding_it_wants", _share)
    t("a_wall_concentrates_power_and_was_built_for_warmth", _wall)
    t("writing_is_what_makes_a_claim_outlive_its_witnesses", _claim)
    return all(x for _, x, _ in res), res


def _flat():
    from engine.group import spare_per_head, strength_share
    sp = [spare_per_head(n) for n in (3, 10, 28)]
    # spare_per_head is a difference of terms around 1e9 J, so the
    # floor is float noise at ~1e-7 relative, not zero. Anything
    # under a joule is not a surplus anybody could eat.
    noise = max(abs(x) for x in sp)
    if noise > 1.0:
        raise ArithmeticError(f"there is a surplus after all: {sp}")
    return (f"engine/group.py already ran this and got a flat "
            f"answer: strength_share({BAND}) = "
            f"{strength_share(BAND):.4f} = 1/{BAND}, and "
            f"spare_per_head is zero to {noise:.1e} J at 3, 10 and "
            f"{BAND} -- float noise on a difference of gigajoule "
            f"terms, not a crumb. Nothing is over. A forager is not egalitarian by disposition, "
            f"they are egalitarian because a carcass is worthless in "
            f"a week and there is no second helping to withhold. "
            f"Power needs a surplus AND somewhere to keep it, and "
            f"engine/accident.py's grain harvest is the first thing "
            f"on this chain that is both")


def _geom():
    d = defensibility()
    if d < 10:
        raise ArithmeticError(f"{d}")
    return (f"a band of {BAND} eats "
            f"{range_per_head_m2()*BAND/1e6:.0f} km2 of country -- "
            f"{NEED_W:.0f} W each against {NPP_W_M2} W/m2 of "
            f"production at an edible fraction of "
            f"{EDIBLE_FRACTION:.0e} -- and its border is "
            f"{range_perimeter_m()/1000:.1f} km. A granary's border "
            f"is {store_perimeter_m():.0f} m. {d:.0f}x. You cannot "
            f"own a range and you can stand in the door of a barn. "
            f"That is why wealth appears when people stop moving, "
            f"and it is geometry, not a change of heart")


def _share():
    g, c = insiders(), concentration()
    if c <= 1 or g <= 1:
        raise ArithmeticError(f"{g} {c}")
    return (f"strength is headcount, so a holder needs enough "
            f"backing to match everyone they exclude: g >= "
            f"({BAND}-1)/2, which is {g} people in on it and "
            f"{BAND-g} out. Each insider commands "
            f"{100*power_share():.0f}% against an equal "
            f"{100/BAND:.0f}% -- {c:.1f}x, and no more. The first "
            f"concentration is not a chief with everything, it is "
            f"half the band with slightly more, because the "
            f"arithmetic will not carry a chief yet")


def _wall():
    flat, walled = concentration(), concentration(wall=WALL_ADVANTAGE)
    gf, gw = insiders(), insiders(wall=WALL_ADVANTAGE)
    if walled <= flat:
        raise ArithmeticError(f"{walled} <= {flat}")
    return (f"engine/disease.py built the wall for 526 MJ a year of "
            f"thermoregulation and the separation came free. It is "
            f"not free here. One defender behind it matches "
            f"{WALL_ADVANTAGE:.0f}, so the backing needed drops from "
            f"{gf} to {gw} and each insider's share goes "
            f"{flat:.1f}x -> {walled:.1f}x. The building that was "
            f"worth {53} days of food for being warm turns out to "
            f"decide who eats. Nobody chose that when they built it, "
            f"which is the point -- it is the same shape as cooking, "
            f"adopted for one reason and kept for another")


def _claim():
    from engine.literacy import spread
    f0 = 1.0 / BAND
    pop = 5000.0
    near, far = reach(f0, pop), reach(spread(f0, 1000), pop)
    if far <= near * 5:
        raise ArithmeticError(f"{near} {far}")
    return (f"spoken, a claim binds whoever heard it and dies with "
            f"the last witness -- so the most anyone can be owed is "
            f"a lifetime and a band. Written, it binds anyone who "
            f"can read it, including people not yet born. In a "
            f"population of {pop:.0f} the reach goes {near:.0f} -> "
            f"{far:.0f} over a thousand years of literacy spreading, "
            f"{far/near:.0f}x, and a claim that outlives its holder "
            f"is the definition of inheritance. A stock can cross a "
            f"death and a flow cannot. That is why hereditary power "
            f"waits for the granary and then for the ledger, and "
            f"why the first writing anyone does is an inventory")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
