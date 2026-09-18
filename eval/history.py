"""How close is any of this to what actually happened.

Every row is a number this system DERIVED against a number
somebody RECORDED. The recorded column is not from the system and
cannot be adjusted by it.

Three rules for reading it.

  A match is only evidence if the derivation could have come out
  otherwise. Band size near 28 is worth something because the
  arithmetic could have said 3 or 300. Copper before iron is worth
  nothing: a prerequisite loop was built that puts copper first,
  and it would be strange if it did not. Those rows are marked and
  not counted.

  A row is only scored if the RECORDED column is a real figure.
  Where the baseline is something I chose, the row is shown and
  not scored, because otherwise the score measures my choice of
  baseline rather than the model. Three such rows would have
  scored as matches, which is exactly why they do not count.

  A miss is worth more than a match, because it says which rule is
  wrong. The misses here are the most useful lines in the file.
"""

import math

# (label, derived, recorded, units, note, could-have-differed, basis)
ROWS = []


def _r(label, derived, recorded, units, note, free=True, basis="measured"):
    """basis: how good the RECORDED column is.

      measured   somebody measured it and the note names the source
      estimated  a real figure carrying wide error bars
      none       I chose the baseline; shown, never scored
    """
    ROWS.append((label, float(derived), float(recorded), units, note,
                 free, basis))


def build():
    ROWS.clear()
    from engine.signal import affordable_group
    from engine.tradition import oral_capacity, best_band_count
    from engine.trade import spacing_km, price_doubles_km, porter_km_day
    from engine.disease import critical_community, cooking_pays
    from engine.intricacy import critical_land_share, settle, settle_network
    from engine.literacy import fed_without_farming, least_scribes
    from engine.novelty import multiple, team_size, VILLAGE
    from engine.accident import settling_threshold
    from engine.group import best_size
    from engine.power import defensibility, concentration
    from engine.capital import income_stats
    from engine.merit import best_of
    from engine.inference import least_population, corpus_bits
    from engine.artifact import bootstrap, PRIMITIVES, depth
    from engine.nucleo import binding_per_nucleon, iron_peak
    from engine.life import codon_length, square_cube_limit
    from engine.biome import food_chain_length, hydraulic_ceiling, metabolism_w
    from engine.earthlab import closure_floor
    from engine.ontogeny import provisioning_debt
    from engine.occurrence import longest_complete_polymer
    from engine.constants import H_PLANCK, C_LIGHT, K_B, G_GRAV, HBAR
    from engine.learning import landauer_j

    # --- cosmology and nuclear --------------------------------------
    a_rad = (8 * math.pi**5 * K_B**4) / (15 * H_PLANCK**3 * C_LIGHT**3)
    coef = (3 * C_LIGHT**2 / (32 * math.pi * G_GRAV * a_rad)) ** 0.25

    def mev(t):
        return K_B * coef * t**-0.5 / 1.602176634e-13

    _r("Planck time", math.sqrt(HBAR * G_GRAV / C_LIGHT**5), 5.391247e-44,
       "s", "CODATA, from the same three constants -- a definition "
       "being recomputed, not a prediction", free=False)
    _r("radiation constant a", a_rad, 7.5657e-16,
       "J/m3/K4", "the Stefan-Boltzmann radiation density constant, "
       "recomputed from h, k and c", free=False)
    _r("kT at confinement", mev(1e-6), 200.0,
       "MeV", "QCD confinement sets in near 150-250 MeV; this asks "
       "whether the epoch table lands in the right decade")
    _r("kT at n/p freeze-out", mev(1.0), 0.8,
       "MeV", "weak rates fall below the expansion rate near 0.7-0.8 "
       "MeV, which is what fixes the neutron fraction")
    _r("kT at nucleosynthesis", mev(180.0), 0.07,
       "MeV", "the deuterium bottleneck clears near T = 0.8e9 K, far "
       "below the 2.22 MeV binding, because photons outnumber "
       "baryons 1.6e9 to one")
    _r("Fe-56 binding per nucleon", binding_per_nucleon(26, 30), 8.7903,
       "MeV", "AME2020 mass evaluation; a liquid-drop formula should "
       "land close without being told the answer")
    _r("Ni-62 binding per nucleon", binding_per_nucleon(28, 34), 8.7945,
       "MeV", "AME2020; Ni-62 is the actual maximum of the curve, "
       "not Fe-56")
    _r("mass number at the binding peak", iron_peak()["A"], 62,
       "A", "the peak is Ni-62; the model finds A=58, so it has the "
       "neighbourhood and not the nuclide")
    _r("Landauer erasure at 300 K", landauer_j(1.0) * (300 / 310), 2.8705e-21,
       "J/bit", "kT ln2 at 300 K -- a definition recomputed",
       free=False)

    # --- the far future ----------------------------------------------
    from engine.farfuture import (hawking_temperature, evaporation_years,
                                  de_sitter_temperature,
                                  star_lifetime_years,
                                  black_holes_start_shrinking,
                                  hubble_time_yr, LIGHTEST_STAR_MSUN)
    _r("Hawking temperature, one sun", hawking_temperature(1.98847e30),
       6.17e-8,
       "K", "the standard figure for a solar-mass hole is 6.2e-8 K; "
       "this recomputes it from hbar, c, G and k")
    _r("solar-mass hole lifetime", evaporation_years(1.98847e30), 2.1e67,
       "yr", "Page's evaporation time for a solar mass is about "
       "2e67 years")
    _r("de Sitter floor temperature", de_sitter_temperature(), 2.6e-30,
       "K", "the horizon temperature of a universe expanding at the "
       "observed rate is quoted around 2.6e-30 K")
    _r("Hubble time", hubble_time_yr(), 1.45e10,
       "yr", "1/H0 at 67.4 km/s/Mpc is 14.5 Gyr -- arithmetic on a "
       "measured rate", free=False)
    _r("longest-lived star", star_lifetime_years(LIGHTEST_STAR_MSUN),
       1e13,
       "yr", "0.08 solar-mass red dwarfs are given lifetimes of "
       "order 1e12-1e13 years")
    _r("when holes start to shrink", black_holes_start_shrinking(),
       1e12,
       "yr", "the CMB falls below a stellar Hawking temperature "
       "somewhere around 1e11-1e12 years in the standard account",
       basis="estimated")

    # --- origin of life ---------------------------------------------
    _r("smallest closing compartment", 1e6 * closure_floor(), 0.3,
       "um", "the smallest free-living cells, Pelagibacter and "
       "Mycoplasma, run 0.2-0.4 um across")
    _r("polymer length that closes", longest_complete_polymer(), 50,
       "bases", "experimentally self-replicating ribozymes such as "
       "the Lincoln-Joyce cross-catalytic pair run to tens of "
       "nucleotides; 14 is short by a factor of a few")
    _r("codon length", codon_length().value, 3,
       "bases", "the genetic code is a triplet; 4^3 = 64 covers 21 "
       "meanings and 4^2 = 16 does not, so this could have failed")

    # --- bodies and ecosystems ---------------------------------------
    _r("human basal metabolism", metabolism_w(70.0), 84.0,
       "W", "adult basal rate is 1700-1900 kcal/day, about 85 W; "
       "Kleiber's coefficient is fitted, so this is near-definitional",
       free=False)
    _r("trophic levels supported", food_chain_length(), 4.5,
       "levels", "food chains run 4-5 levels in the field and rarely "
       "more; this falls out of 10% transfer against a metabolic floor")
    _r("tallest tree by hydraulics", hydraulic_ceiling(), 116.0,
       "m", "Hyperion, a coast redwood, is 115.9 m, close to the "
       "observed ceiling for the taxon")
    _r("tallest land column by stress", square_cube_limit().value, 116.0,
       "m", "the same observed ceiling reached by a different route "
       "-- buckling rather than water transport")
    _r("cost of raising a child", provisioning_debt()[1], 7.0,
       "adult-years", "Kaplan's forager energetics put a child at "
       "6-13 million kcal to independence, about 7 adult-years of "
       "intake", basis="estimated")

    # --- bands and foraging -------------------------------------------
    _r("band size", affordable_group(), 30,
       "people", "ethnographic hunter-gatherer bands run 25-50; the "
       "classic figure is around 30")
    _r("dominance group size", best_size()[0], 4,
       "people", "stable dominance orders in primates and small human "
       "groups tend to be 3-5 before fragmenting", basis="estimated")
    _r("bands in a regional network", best_band_count(1 / 500), 19,
       "bands", "ethnographic connubia and dialect tribes run roughly "
       "15-25 bands, about 500 people", basis="estimated")
    _r("camp residence before moving", settling_threshold(), 45.0,
       "days", "forager camps are typically occupied for weeks to a "
       "couple of months", basis="estimated")
    _r("forager band range border",
       2 * math.sqrt(65e6 / math.pi) / 1000, 9.0,
       "km", "a 65 km2 territory for 28 people is 2.3 km2 a head, "
       "inside the 1-10 km2 ethnographic range -- but that area came "
       "from a chosen edible fraction", free=False)

    # --- speech, tradition, literacy ------------------------------------
    _r("oral corpus", oral_capacity(), 12000,
       "items", "the Iliad is about 15,700 lines and the Rigveda "
       "about 10,600 verses; both were carried orally")
    _r("holders to keep a skill alive", least_scribes(), 5,
       "people", "craft traditions with a handful of masters are the "
       "ones that get lost, but I have no measured figure and chose "
       "this baseline", basis="none")
    _r("literacy ceiling", 100 * fed_without_farming(), 10,
       "%", "pre-industrial European literacy ran roughly 5-15% "
       "before mass schooling")

    # --- farming, settlement, disease -----------------------------------
    _r("village spacing", spacing_km(), 3.5,
       "km", "neolithic and medieval village spacing is typically "
       "2-5 km, about a field's walk")
    _r("cultivated land per head", 2.3, 0.4,
       "ha", "pre-modern subsistence farming needs 0.2-0.6 ha a head "
       "depending on crop and yield", basis="estimated")
    _r("crowd disease floor", critical_community(), 300000,
       "people", "measured critical community size for measles is "
       "250,000-500,000 in the pre-vaccine record")
    _r("return on cooking", cooking_pays()[2], 20.0,
       "x", "cooking's digestibility and pathogen gains are large but "
       "no clean ratio exists and this baseline is a guess",
       basis="none")

    # --- transport and trade ---------------------------------------------
    _r("porter distance per day", porter_km_day(), 30.0,
       "km", "loaded human porters and marching infantry both average "
       "25-35 km a day")
    _r("grain price doubles", price_doubles_km(), 400,
       "km", "Roman and medieval land-carriage estimates put the "
       "doubling of wheat around 300-500 km")

    # --- power, wealth, specialisation -----------------------------------
    _r("store over range defensibility", defensibility(), 100.0,
       "x", "perimeter ratios are geometric but I have no measured "
       "comparison and chose this", free=False, basis="none")
    _r("early agrarian inequality", concentration(wall=3.0), 4.0,
       "x top/mean", "Gini for early agrarian societies runs "
       "0.35-0.45, roughly a 3-5x top-to-mean ratio", basis="estimated")
    _r("top-to-median income", income_stats(3.0)[3], 15.0,
       "x", "pre-modern elite-to-median income ratios are commonly put "
       "at 10-20x", basis="estimated")
    _r("best of a band, in sigma", best_of(28), 2.58,
       "sigma", "expected maximum of 28 standard normal draws is "
       "sqrt(2 ln n) to leading order -- arithmetic against "
       "arithmetic", free=False)
    _r("land share at takeoff", critical_land_share(), 0.35,
       "share", "English agriculture fell through about a third of "
       "output in the eighteenth century, and sustained per-capita "
       "growth begins in the same window")

    # --- technology --------------------------------------------------------
    b = bootstrap()
    copper = next(i for i, _t, g in b if "smelting" in g)
    iron = next(i for i, _t, g in b if "spring" in g)
    _r("copper before iron", iron - copper, 2,
       "bootstrap rounds", "copper from about 5000 BC and worked iron "
       "from about 1200 BC: the ORDER is right and the tuyere loop "
       "was built in, so it is not evidence", free=False)
    _r("hottest fire without metal", b[copper - 1][1], 1400.0,
       "K", "a charcoal pit kiln reaches 1300-1500 K, but copper's "
       "melting point was PUT IN as the requirement, so this is an "
       "input coming back out", free=False, basis="none")
    _r("hottest fire with bellows", b[-1][1], 1800.0,
       "K", "a bloomery under forced draft runs 1500-1900 K",
       basis="estimated")
    _r("prerequisite tree depth",
       max(depth(n) for n in PRIMITIVES) + 1, 5,
       "levels", "no measurement exists; the row is here to be "
       "visible, not scored", free=False, basis="none")
    _r("parts in a complex artifact", settle(), 30.0,
       "parts", "a pre-industrial loom, clock or plough runs to tens "
       "of distinct worked components", basis="estimated")
    _r("parts at network scale", settle_network(), 30.0,
       "parts", "the same baseline; the model barely separates a "
       "village from a region, which is itself worth noticing",
       basis="none")

    # --- knowledge production ------------------------------------------------
    _r("invention team", team_size(VILLAGE), 5,
       "people", "authors per scientific paper average about 5 and "
       "inventors per patent about 3")
    _r("novelty per head", multiple(VILLAGE, 40 * VILLAGE)[0], 0.05,
       "ratio over 40x", "measured research productivity falls "
       "sharply: US total factor productivity growth is flat while "
       "researcher headcount rose more than twentyfold")
    _r("people to afford one inference kit", least_population(), 1e6,
       "people", "leading-edge lithography is held by a handful of "
       "firms serving billions", basis="estimated")
    _r("corpus a machine must hold", corpus_bits() / 8e9, 200.0,
       "GB", "a large deduplicated text corpus is hundreds of GB, so "
       "the scale is right by construction", free=False)

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


_TABLE = []


def table():
    """Built once per process.

    build() calls settle_network(), least_population() and friends,
    each iterating a fixed point over a 36,480-person market.
    table() calls build(), scored_rows() calls table(), score()
    calls scored_rows(), and every check calls two or three of
    those -- so the first version of this file rebuilt the whole
    table a dozen times per run and did not finish in ten minutes.
    The rows cannot change inside one process.
    """
    if _TABLE:
        return _TABLE
    for lab, d, rec, u, note, free, basis in build():
        ratio, v = verdict(d, rec)
        _TABLE.append((lab, d, rec, u, ratio, v, free, note, basis))
    return _TABLE


def scored_rows():
    """Rows whose recorded column is good enough to score against."""
    return [r for r in table() if r[8] != "none"]


def score():
    """-> (matches, loose, misses, free_matches). DERIVED.

    Only rows with a real baseline are scored. A row whose
    baseline I chose is shown and not counted, because otherwise
    the score measures my choice of baseline.
    """
    m = l = x = fm = 0
    for row in scored_rows():
        v, free = row[5], row[6]
        if v == "MATCH":
            m += 1
            fm += 1 if free else 0
        elif v == "LOOSE":
            l += 1
        else:
            x += 1
    return m, l, x, fm


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_matches_are_counted_and_most_could_have_differed", _match)
    t("INVERTED_the_misses_are_named_and_not_averaged_away", _miss)
    t("INVERTED_a_baseline_i_chose_is_not_evidence", _basis)
    t("the_crowd_disease_floor_is_wrong_by_three_orders", _ccs)
    t("the_novelty_decline_is_far_too_gentle", _nov)
    return all(x for _, x, _ in res), res


def _match():
    m, l, x, fm = score()
    rows, scored = table(), scored_rows()
    good = [r[0] for r in scored if r[5] == "MATCH" and r[6]]
    if m + l + x != len(scored):
        raise ArithmeticError("rows unaccounted")
    return (f"{len(rows)} derived numbers against recorded ones, "
            f"{len(scored)} scored. {m} match within 3x, {l} are "
            f"loose within 10x, {x} miss. {fm} of the {m} matches "
            f"COULD HAVE COME OUT OTHERWISE -- the rest either "
            f"recompute something definitional (the Planck time from "
            f"hbar, G and c) or hand back an input (copper's melting "
            f"point was put in as the smelting requirement). The free "
            f"matches span the whole chain, from {good[0]!r} to "
            f"{good[-1]!r}")


def _miss():
    """INVERTED. Fails if the misses ever stop being reported."""
    rows = scored_rows()
    bad = [(r[0], r[4]) for r in rows if r[5] in ("MISS", "LOOSE")]
    if not bad:
        raise ArithmeticError(
            "nothing misses, which would mean either the model is "
            "exactly right about forty independent things or the "
            "baselines have been picked to agree with it")
    worst = sorted(bad, key=lambda t: -max(t[1], 1.0 / t[1]))[:4]
    return (f"{len(bad)} of {len(rows)} scored rows do not match and "
            f"they are the useful part. Worst first: "
            + "; ".join(f"{lab} off {max(r, 1/r):.0f}x"
                        for lab, r in worst)
            + ". A model of this span agreeing with everything would "
              "mean the baselines had been chosen to agree")


def _basis():
    """INVERTED. Fails if every baseline is suddenly solid."""
    rows = table()
    weak = [r[0] for r in rows if r[8] == "none"]
    soft = [r[0] for r in rows if r[8] == "estimated"]
    would = [r[0] for r in rows if r[8] == "none" and r[5] == "MATCH"]
    if not weak:
        raise ArithmeticError(
            "every baseline is claimed to be measured, which for a "
            "table spanning nucleosynthesis to lithography is not "
            "credible")
    return (f"{len(weak)} of {len(rows)} rows have a baseline I chose "
            f"rather than found, and they are shown WITHOUT being "
            f"scored: {weak}. Another {len(soft)} carry real figures "
            f"with wide error bars and are marked. Scoring the chosen "
            f"ones would measure my baseline rather than the model, "
            f"and {len(would)} of them would have counted as matches "
            f"-- which is precisely why they do not")


def _ccs():
    from engine.disease import critical_community
    d, rec = critical_community(), 300000.0
    if d > rec / 50:
        raise ArithmeticError(f"{d} is no longer far below {rec}")
    return (f"engine/disease.py derives {d:.0f} people as the floor "
            f"for a crowd disease against a measured 250,000-500,000 "
            f"for measles. Wrong by {rec/d:.0f}x, and the reason is "
            f"nameable: the derivation asks only that ONE susceptible "
            f"arrive per infectious period, which is DETERMINISTIC. A "
            f"real chain breaks by chance long before that, because "
            f"the number of infectives is small and integer. The "
            f"stochastic margin is the missing rule. The conclusion "
            f"drawn from it survives -- 28 is far below both figures "
            f"-- but the floor itself must not be quoted")


def _nov():
    from engine.novelty import multiple, VILLAGE
    per = multiple(VILLAGE, 40 * VILLAGE)[0]
    if per < 0.3:
        raise ArithmeticError(f"{per} is no longer too gentle")
    return (f"engine/novelty.py has novelty per head falling to "
            f"{per:.2f} over a 40x population where the record says "
            f"something nearer 0.05. The model is gentle because its "
            f"only headwind is team size, which is a LOGARITHM of the "
            f"corpus. Something else is eating the returns and this "
            f"system does not have it. Two candidates -- the easy "
            f"region of the design space going first rather than "
            f"uniformly, and verification cost rising with the corpus "
            f"even when discovery does not -- are named and neither "
            f"is derived, so neither is claimed")


if __name__ == "__main__":
    print(f"  {'':<34}{'derived':>12}{'recorded':>12}{'ratio':>8}"
          f"  verdict")
    for lab, d, rec, u, ratio, v, free, _n, basis in table():
        tag = {"measured": "", "estimated": "  ~",
               "none": "  (not scored)"}[basis]
        bi = "  [built in]" if not free else ""
        print(f"  {lab[:33]:<34}{d:>12.4g}{rec:>12.4g}{ratio:>8.2f}"
              f"  {v}{tag}{bi}")
    m, l, x, fm = score()
    print(f"\n  {len(table())} rows, {len(scored_rows())} scored")
    print(f"  {m} match, {l} loose, {x} miss "
          f"({fm} of the matches could have differed)")
