"""How close is any of this to what actually happened.

Every row is a number this system DERIVED against a number
somebody RECORDED. The recorded column is not from the system and
cannot be adjusted by it.

Two rules for reading it:

  A match is only evidence if the derivation could have come out
  otherwise. Band size near 28 is worth something because the
  arithmetic could have said 3 or 300. Copper before iron is worth
  less: a prerequisite loop was built that puts copper first, and
  it would be strange if it did not.

  A miss is worth MORE than a match, because it says which rule is
  wrong. Three of these are badly wrong and they are the useful
  part of the file.
"""

import math

# (what, derived, recorded, units, source in words, could-have-differed)
ROWS = []


def _r(label, derived, recorded, units, note, free=True):
    ROWS.append((label, float(derived), float(recorded), units, note, free))


def build():
    ROWS.clear()
    from engine.signal import affordable_group
    from engine.tradition import oral_capacity, best_band_count
    from engine.trade import spacing_km, price_doubles_km
    from engine.disease import critical_community
    from engine.intricacy import critical_land_share, spare_fraction, settle
    from engine.literacy import fed_without_farming
    from engine.novelty import multiple, team_size, VILLAGE
    from engine.artifact import PRIMITIVES, bootstrap

    _r("band size", affordable_group(), 30,
       "people", "ethnographic hunter-gatherer bands run about "
       "25-50; the classic figure is around 30")

    _r("village spacing", spacing_km(), 3.5,
       "km", "neolithic and medieval village spacing is typically "
       "2-5 km, roughly a field's walk")

    _r("oral corpus", oral_capacity(), 12000,
       "items", "the Iliad is about 15,700 lines and the Rigveda "
       "about 10,600 verses; both were carried orally")

    _r("grain price doubles", price_doubles_km(), 400,
       "km", "estimates from Roman and medieval land carriage put "
       "the doubling of wheat somewhere around 300-500 km")

    _r("literacy ceiling", 100 * fed_without_farming(), 10,
       "%", "pre-industrial literacy in Europe ran roughly 5-15% "
       "before mass schooling")

    _r("land share at takeoff", critical_land_share(), 0.35,
       "share", "English agriculture fell through about a third of "
       "output in the eighteenth century, and sustained per-capita "
       "growth begins in the same window")

    _r("copper before iron", 5 - 3, 2,
       "bootstrap rounds", "copper from about 5000 BC and worked "
       "iron from about 1200 BC: the ORDER is right but this was "
       "built in by the tuyere loop, so it is not evidence",
       free=False)

    _r("crowd disease floor", critical_community(), 300000,
       "people", "measured critical community size for measles is "
       "250,000-500,000 in the pre-vaccine record")

    _r("invention team", team_size(VILLAGE), 5,
       "people", "authors per scientific paper average about 5, "
       "and inventors per patent about 3")

    _r("novelty per head", multiple(VILLAGE, 40 * VILLAGE)[0], 0.05,
       "ratio over 40x", "measured research productivity falls "
       "sharply: US total factor productivity growth is flat while "
       "researchers rose more than twentyfold")

    return ROWS


def verdict(derived, recorded):
    """-> (ratio, word). Within 3x is a match at this resolution."""
    if recorded == 0:
        return math.inf, "NO BASELINE"
    r = derived / recorded
    off = max(r, 1.0 / r)
    if off <= 3.0:
        return r, "MATCH"
    if off <= 10.0:
        return r, "LOOSE"
    return r, "MISS"


def score():
    """-> (matches, loose, misses, free_matches). DERIVED."""
    rows = build()
    m = l = x = fm = 0
    for _lab, d, rec, _u, _n, free in rows:
        _ratio, v = verdict(d, rec)
        if v == "MATCH":
            m += 1
            fm += 1 if free else 0
        elif v == "LOOSE":
            l += 1
        else:
            x += 1
    return m, l, x, fm


def table():
    rows = build()
    out = []
    for lab, d, rec, u, note, free in rows:
        ratio, v = verdict(d, rec)
        out.append((lab, d, rec, u, ratio, v, free, note))
    return out


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_matches_are_counted_and_most_could_have_differed", _match)
    t("INVERTED_the_misses_are_named_and_not_averaged_away", _miss)
    t("the_crowd_disease_floor_is_wrong_by_three_orders", _ccs)
    t("the_novelty_decline_is_far_too_gentle", _nov)
    return all(x for _, x, _ in res), res


def _match():
    m, l, x, fm = score()
    rows = table()
    good = [r[0] for r in rows if r[5] == "MATCH"]
    if m + l + x != len(rows):
        raise ArithmeticError("rows unaccounted")
    return (f"{len(rows)} derived numbers against recorded ones. "
            f"{m} match within 3x, {l} are loose within 10x, {x} "
            f"miss. The matches: {good}. {fm} of the {m} could have "
            f"come out otherwise -- the arithmetic for band size "
            f"could have said 3 or 300 and said 28 against a "
            f"recorded 25-50. The one that could NOT is copper "
            f"before iron, which was built in by the tuyere loop "
            f"and is therefore not evidence of anything, and it is "
            f"marked as such rather than counted")


def _miss():
    """INVERTED. Fails if the misses ever stop being reported."""
    rows = table()
    bad = [(r[0], r[4]) for r in rows if r[5] in ("MISS", "LOOSE")]
    if not bad:
        raise ArithmeticError(
            "nothing misses, which would mean either the model is "
            "exactly right about ten independent things or the "
            "baselines have been chosen to agree with it")
    return (f"{len(bad)} of {len(rows)} do not match, and they are "
            f"the useful part: "
            + "; ".join(f"{lab} off by {max(r,1/r):.0f}x"
                        for lab, r in bad)
            + f". A model of this scope agreeing with everything "
              f"would mean the baselines had been picked to agree. "
              f"These are listed with the rule each one indicts")


def _ccs():
    from engine.disease import critical_community
    d, rec = critical_community(), 300000.0
    if d > rec / 50:
        raise ArithmeticError(f"{d} is no longer far below {rec}")
    return (f"engine/disease.py derives {d:.0f} people as the floor "
            f"for a crowd disease and the measured figure for "
            f"measles is 250,000-500,000. Wrong by {rec/d:.0f}x, "
            f"and the reason is nameable: the derivation asks only "
            f"that ONE susceptible arrive per infectious period, "
            f"which is a DETERMINISTIC condition. A real chain "
            f"breaks by chance long before that -- the number of "
            f"infectives is small and integer, and a run of bad "
            f"luck ends it. The stochastic margin is the missing "
            f"rule. The conclusion drawn from it (a band of 28 "
            f"cannot hold a crowd disease, so settling is what "
            f"invents one) survives, because 28 is below both "
            f"figures by a wide margin -- but the FLOOR itself "
            f"should not be quoted")


def _nov():
    from engine.novelty import multiple, VILLAGE
    per = multiple(VILLAGE, 40 * VILLAGE)[0]
    if per < 0.3:
        raise ArithmeticError(f"{per} is no longer too gentle")
    return (f"engine/novelty.py has novelty per head falling to "
            f"{per:.2f} over a 40x population. The measured "
            f"collapse is far steeper: research productivity in "
            f"the US record falls by something like 20x over a "
            f"comparable rise in researchers. The model is gentle "
            f"because its only headwind is team size, which is a "
            f"LOGARITHM of the corpus. Something else is eating "
            f"the returns and this system does not have it -- the "
            f"candidates are that the easy region of the design "
            f"space is exhausted first rather than uniformly, and "
            f"that verification cost rises with the corpus even "
            f"when discovery does not. Neither is derived here, so "
            f"neither is claimed")


if __name__ == "__main__":
    print(f"  {'':<24}{'derived':>12}{'recorded':>12}"
          f"{'ratio':>9}  verdict")
    for lab, d, rec, u, ratio, v, free, _n in table():
        star = "" if free else "  (built in)"
        print(f"  {lab:<24}{d:>12.4g}{rec:>12.4g}{ratio:>9.2f}  "
              f"{v}{star}")
    m, l, x, fm = score()
    print(f"\n  {m} match, {l} loose, {x} miss "
          f"({fm} of the matches could have differed)")
