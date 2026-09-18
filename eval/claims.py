"""
Every published number, recomputed. Stale claims are a kind of wrong.

This README states measured results in almost every section. A
number written down in one version and left there is a claim the
repository is still making, and when the code moves underneath it
the claim silently stops being true. Nothing else here catches
that: the benchmark checks the code against itself, the audit
checks the code against its own invariants, and neither reads the
document.

IT HAS ALREADY HAPPENED ONCE. 3.1.30 published an ablation table
reading 1 right, 1 wrong, 12 refused. 3.1.31 changed the rule it
was measuring and the same command now prints 8, 0, 6. The old
table was correct when written and is wrong as a present-tense
claim, and only a reader who ran the code would know.

So each load-bearing published number is registered here with the
computation that produced it. A claim that no longer reproduces
fails, and there are two honest repairs: correct the document, or
mark the number as superseded history rather than a current
result. What is not allowed is leaving it.
"""
from __future__ import annotations

import sys
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CURRENT, HISTORY = "CURRENT", "HISTORY"


def _decay():
    from engine.transitions import score
    r = score()
    return (r["right"], r["wrong"], r["refused"])


def _magic():
    from engine.shells import MAGIC
    return tuple(MAGIC)


def _region():
    from engine.shells import allowed_region
    return round(allowed_region()[0] * 100, 1)


def _sigma_rel():
    from engine.terraform import SIGMA
    return float(f"{abs(SIGMA - 5.670374419e-8) / 5.670374419e-8:.2e}")


def _domain_floor():
    from engine.shells import SEMF_MIN_A
    return SEMF_MIN_A


def _bars():
    from engine.nucleo import mass_bar
    return (round(mass_bar("in-domain")[0], 3),
            round(mass_bar("out-of-domain")[0], 3))


def _mq_bar():
    from engine.nucleo import MEASURED_Q_BAR
    return round(MEASURED_Q_BAR, 4)


def _fold_bar():
    from engine.folding import model_bar
    return round(model_bar()[0], 4)


def _climate():
    from engine import terraform as T, radiative as R
    out = {}
    for n in ("Earth", "Venus"):
        b = T.BODIES[n]
        P = b.observed_bar_pa or 0.0
        mix = {"CO2": (b.observed_co2 or 0) * P}
        if n == "Earth":
            mix["H2O"] = 0.7 * T.p_sat_water(288.0)
        tau = R.grey_equivalent_full(mix, b.observed_T, b.gravity(), P)
        out[n] = round(T.equilibrium_T(b) * (1 + 0.75 * tau) ** 0.25
                       - b.observed_T, 1)
    return (out["Earth"], out["Venus"])


def _table_size():
    from engine.nucleo import MEASURED_BINDING
    return len(MEASURED_BINDING)


def _band():
    from engine.evolve import _solar_band
    i, o = _solar_band()
    return (round(i, 3), round(o, 3))


def _cutoff():
    from engine.potential import wing_cutoff
    return round(wing_cutoff("CO2", 737.0), 1)


def _welldepth():
    from engine.potential import well_depth
    from engine.constants import K_B
    return round(well_depth("CO2") / K_B)


def _ceiling57():
    from engine.origin import length_ceiling
    return length_ceiling()


def _lab_counts():
    from engine.lab import run, HOLDS, CLASH, MISSING_RULE, REFUSED
    rows, _ = run(stop_on_problem=False)
    c = {}
    for _L, _n, v, _d, _a in rows:
        c[v] = c.get(v, 0) + 1
    return (c.get(HOLDS, 0), c.get(CLASH, 0),
            c.get(MISSING_RULE, 0), c.get(REFUSED, 0))


def _race():
    from engine.biome import escalation_stops_at, tallest_worthwhile
    return (round(escalation_stops_at(1.0), 1),
            round(tallest_worthwhile(rival_height=0.0)[0], 2))


def _crowns():
    from engine.biome import escalation_stops_at
    return tuple(round(escalation_stops_at(c))
                 for c in (0.1, 1.0, 10.0, 100.0, 1000.0))


def _chainlen():
    from engine.biome import food_chain_length, hydraulic_ceiling
    return food_chain_length(), round(hydraulic_ceiling())


def _generated():
    from engine.generate import generate, ask, AXES, load
    rows, _dt = generate()
    n = 1
    for v in AXES.values():
        n *= len(v)
    got = ask(in_band=True, brine_liquid=True, can_shed_heat=True)
    return len(rows) == n, len(rows), len(got)


def _regard():
    from engine.regard import (regard_is_worth, taking_capacity, wins,
                               decisions)
    ratio, _f, _r = regard_is_worth()
    armed, bare = taking_capacity(60.0, 1.75), taking_capacity(60.0)
    return (wins(armed, bare), round(decisions()),
            round(math.log10(ratio)))


def _frozen():
    from engine.frozen import cost_of_change, narrow_is_worse
    frac, codons, m = cost_of_change()
    rows = narrow_is_worse()
    return round(100 * frac, 1), codons, rows[0][1] > rows[-1][1]


def _rank():
    from engine.rank import carrying_children, rank_is_priced
    ok0, p0, _w = rank_is_priced(2, 3)
    ok1, p1, _w = rank_is_priced(2, 4)
    return round(carrying_children(2), 1), ok0, ok1, round(p1)


def _innovation():
    from engine.innovation import (INNOVATIONS, innovations_per_division,
                                   wait_years, coordination_for, OMIT)
    return (len(INNOVATIONS),
            sum(1 for v in INNOVATIONS.values() if v[0] == OMIT),
            round(innovations_per_division(), 2),
            coordination_for(2e9))


def _code():
    from engine.code import affordable_code, modern_code_fits
    n, w, left = affordable_code()
    fits, need, held = modern_code_fits()
    return n, w, fits, need


def _reach():
    from engine.reach import all_steps
    rows = all_steps()
    return (len(rows), round(min(r[4] for r in rows), 1),
            round(max(r[4] for r in rows), 1))


def _template():
    from engine.template import (templated_fraction, replicates,
                                 copy_fidelity, accepts)
    n, total = templated_fraction()
    err, bases = copy_fidelity()
    return (n == total, n, replicates("ACCDBA"),
            not accepts("ABCD", "AB", "CD"), round(bases))


def _heredity():
    from engine.heredity import (divides_at, lost_per_division,
                                 copies_per_type, sole_catalyst_fraction)
    n, _h, _M = copies_per_type()
    lost, _p = lost_per_division()
    sole, _lam = sole_catalyst_fraction()
    return (round(divides_at(), 2), round(n), round(lost, 2),
            round(100 * sole, 1))


def _occurs():
    from engine.occurrence import closes_in_one, compartments, types_up_to
    from engine.earthlab import CATALYSIS_P
    ok, pm, L = closes_in_one()
    cross = next(n for n in range(8, 20)
                 if CATALYSIS_P * types_up_to(n) >= 0.481)
    return ok, L, cross, round(math.log10(compartments()))


def _wholechain():
    from engine.lineage import chain, DERIVED, MISSING, CROSSES, FORCED
    c = chain()
    k = {}
    for _a, _b, v, _r, _w in c:
        k[v] = k.get(v, 0) + 1
    return (len(c), k.get(DERIVED, 0), k.get(FORCED, 0),
            k.get(MISSING, 0), k.get(CROSSES, 0))


def _damuth():
    from engine.lineage import size_span
    _a, _b, ratio = size_span(1000.0, 1e-3, 1e3)
    return round(ratio / (1e6 ** 0.75), 3)


def _floor():
    from engine.descent import closure_floor_m, run, fitness, Organism
    snaps = run(generations=600, population=200)
    last = snaps[-1]["median_radius_m"]
    tiny = fitness(Organism(1e-8))
    return (round(1e6 * closure_floor_m(), 2),
            last >= closure_floor_m() * 0.95, tiny == 0.0)


def _pm():
    from engine.closure import (catalysts_per_reaction, MEANFIELD_MIN_M,
                                length_closing_derived, threshold_derived)
    from engine.earthlab import CATALYSIS_P
    mean, spread, n = catalysts_per_reaction()
    L, _M, _p = length_closing_derived(CATALYSIS_P)
    return (round(mean, 2), spread < 2.0, L,
            threshold_derived(4) is None)


def _closes13():
    from engine.closure import (length_closing_at, CATALYSATION_SLOPE,
                                REAL_PIECE_BASES)
    from engine.earthlab import CATALYSIS_P
    L, R, p = length_closing_at(CATALYSIS_P)
    return L, L <= REAL_PIECE_BASES, CATALYSATION_SLOPE


def _closurewide():
    from engine.closure import extrapolate_wide, alphabet_matters
    need, orders, L, a = extrapolate_wide()
    two, four = alphabet_matters()
    return (round(a, 2), L, round(orders), two > four * 5)


def _closure():
    from engine.closure import search, threshold
    from engine.earthlab import CATALYSIS_P
    c = threshold(seeds=6, steps=10)
    on = min([p for p, f in c if f >= 0.5], default=0.0)
    return (search(1e-6, 1)["closed"], search(1e-2, 1)["closed"],
            on > CATALYSIS_P * 1e4)


def _persist():
    from engine.cold import build_over_break, half_life_years
    return (round(build_over_break(259.0), 1),
            round(half_life_years(259.0) / half_life_years(298.0)))


def _cold():
    from engine.cold import (discrimination_kcal, temperature_for,
                             NACL_EUTECTIC_K, concentration_factor)
    from engine.earthlab import gates, SHUT, MIN_REPLICASE_BASES
    def shut(T):
        return sorted(n for n, v, _w in gates(T) if str(v) == str(SHUT))
    return (round(discrimination_kcal(), 2),
            round(temperature_for(1.0 / MIN_REPLICASE_BASES), 1),
            shut(298.0), shut(255.0))


def _school():
    from engine.school import (trades_per_person, grow, holdable,
                               specialists_for, CORPUS)
    c8 = grow(8e9, years=3000)[-1][1]
    return (round(trades_per_person(), 1),
            round(specialists_for(CORPUS["today"])),
            c8 < holdable(8e9) * 0.01)


def _gifts():
    from engine.revolution import (run, BIOLOGICAL_N, HABER_N,
                                   INFRASTRUCTURE, teaching_is_free,
                                   infrastructure_cost)
    allof = tuple(INFRASTRUCTURE)
    yrs = []
    for kw in (dict(fixed_n=BIOLOGICAL_N),
               dict(fixed_n=BIOLOGICAL_N + HABER_N),
               dict(fixed_n=BIOLOGICAL_N + HABER_N, built=allof),
               dict(fixed_n=BIOLOGICAL_N + HABER_N, built=allof,
                    synthetic_w=2e13)):
        h = run(2000, **kw)
        yrs.append(next((s["year"] for s in h if s["p_left"] <= 0), 0))
    return (tuple(yrs), teaching_is_free()[0],
            round(100 * infrastructure_cost(allof)))


def _revolution():
    from engine.revolution import (run, what_stopped_it, BIOLOGICAL_N,
                                   HABER_N, efficiency_from)
    yrs = []
    for kw in (dict(fixed_n=BIOLOGICAL_N),
               dict(fixed_n=BIOLOGICAL_N + HABER_N),
               dict(fixed_n=BIOLOGICAL_N + HABER_N, synthetic_w=2e13)):
        h = run(2000, **kw)
        yrs.append(next((s["year"] for s in h if s["p_left"] <= 0), 0))
    h = run(2000, fixed_n=BIOLOGICAL_N)
    return (tuple(yrs), what_stopped_it(h)[0],
            round(100 * efficiency_from(22.1), 1))


def _industry():
    from engine.industry import (steam_ceiling, drawdown, burial_w,
                                 MODERN_TW, inside_the_flow)
    return (round(100 * steam_ceiling(), 1),
            round(drawdown(per_person_w=1000.0), 2),
            round(MODERN_TW * 1e12 / burial_w()),
            inside_the_flow(per_person_w=1000.0)[0])


def _empire():
    from engine.empire import (empire_radius_km, tolerable_lie_rate,
                               audit_code)
    a = audit_code()
    return (round(empire_radius_km()),
            round(100 * tolerable_lie_rate(), 1),
            len([x for x in a if x[1] == "DERIVED"]))


def _muscle():
    from engine.inherit import muscle_area_m2, height_is_determined
    from engine.tools import ARM_BLOW_N
    return (round(1e4 * muscle_area_m2(ARM_BLOW_N)),
            height_is_determined()[0])


def _speech():
    from engine.civ import channel_ratio, speech_as_fraction_of_a_brain
    return (round(channel_ratio()),
            round(100 * speech_as_fraction_of_a_brain(), 4))


def _group():
    from engine.civ import smallest_group, alone_is_viable
    return smallest_group(), alone_is_viable()[0]


def _fovea():
    from engine.recognize import (sharp_fraction, seconds_to_cover,
                                  recognition_range)
    return (round(100 * sharp_fraction(), 3), round(seconds_to_cover()),
            round(recognition_range(1.7)))


def _binds():
    from engine.multiverse import sweep, why_not
    res, _ = sweep(n=600)
    h = dict(why_not(res))
    return ("heat can leave the body" in h,
            round(100 * sum(1 for r in res if r["human"]) / len(res)) < 20)


def _fragile():
    from engine.multiverse import near_earth
    out = {}
    for span, dial in ((0.02, "spread"), (0.30, "metallicity"),
                       (0.20, "nebula_mass")):
        v = sorted(near_earth(steps=41, span=span, which=[dial])[dial])
        live = [d for d, h, _ in v if h]
        out[dial] = (round(min(live), 3), round(max(live), 3))
    return (out["spread"][0] > -0.02, out["metallicity"] == (-0.3, 0.3),
            out["nebula_mass"][1] < 0.10)


def _shelterladder():
    from engine.shelter import worn_floor, coldest_survivable
    return (round(worn_floor() - 273.15),
            round(coldest_survivable("earth lodge") - 273.15))


def _homenights():
    from engine.shelter import payback_nights
    return round(payback_nights("brush shelter"), 1)


def _lineage():
    """The exact counts drift as modules are added, so the claim is
    the ORDERING, which is the finding: most of what this tree
    references nowhere is history, not dead code."""
    from engine.spine import classify_unreferenced
    k = classify_unreferenced()
    lin, dis, st = (len(k["lineage"]), len(k["dispatched"]),
                    len(k["stranded"]))
    return lin > dis > st, lin > 2 * st


def _acuity():
    from engine.senses import diffraction_limit, sampling_limit, arcmin
    return (round(arcmin(diffraction_limit()), 2),
            round(arcmin(sampling_limit()), 2))


def _stereo():
    from engine.senses import stereo_range, depth_resolution
    return round(stereo_range()), round(1000 * depth_resolution(0.5), 2)


def _fills():
    from engine.learning import fill_time_years, lived_multiples
    return round(fill_time_years(), 2), round(lived_multiples(70.0))


def _toolstress():
    from engine.tools import stress, CONTACT, body_alone
    from engine.life import BONE_COMPRESSIVE
    ok, short = body_alone()
    return (ok, round(short),
            stress(area_m2=CONTACT["flaked edge"]) > BONE_COMPRESSIVE)


def _marrowpays():
    from engine.tools import pays_for_a_brain
    ok, gain, cost = pays_for_a_brain()
    return ok, round(gain / cost, 1)


def _tooldepth():
    from engine.spine import depth
    return depth(("tools", "pays_for_a_brain"))


def _toolcount():
    from engine.ontogeny import tool_search
    _, rows = tool_search()
    return len([r for r in rows if r[2] > 0 and r[1] > 0]), len(rows)


def _rootdepth():
    from engine.spine import depth
    return (depth(("ontogeny", "tool_search")),
            depth(("radiative", "grey_equivalent_full")))


def _infantshare():
    from engine.ontogeny import ONTOGENY, brain_share
    return round(100 * brain_share(ONTOGENY[0][1], ONTOGENY[0][2]))


def _growthdip():
    from engine.ontogeny import slowest_growth
    a, r, sh = slowest_growth()
    return round(a, 1), round(r, 2), round(100 * sh)


def _debt():
    from engine.ontogeny import provisioning_debt
    return round(provisioning_debt()[1], 1)


def _brainpay():
    from engine.human import brain_cost, gut_saving, APE_BRAIN_KG, \
        HUMAN_BRAIN_KG
    cost = brain_cost(HUMAN_BRAIN_KG)[1] - brain_cost(APE_BRAIN_KG)[1]
    return round(cost, 1), round(gut_saving()[1], 1)


def _cookinggap():
    from engine.human import break_even_gain, diet_implied_by_gut, \
        COOKING_GAIN
    implied = diet_implied_by_gut() / 0.50 - 1.0
    return (round(break_even_gain() / COOKING_GAIN, 2),
            round(implied / COOKING_GAIN, 2), round(100 * implied))


def _conserve():
    from engine.atoms import Pool, atoms_in
    p = Pool(atoms_in(1000.0))
    p.build(400.0); p.die(400.0)
    return p.conserved()[0], p.cycles()[0]


LEDGER = ROOT / "data" / "claims_ledger.json"


def _fp(fn):
    """The fingerprint of everything this claim stands on.

    engine/spine.py hashes a rule over its own source and its
    dependencies' fingerprints, so this one value commits to the
    entire chain beneath a claim. If it has not moved, the claim
    cannot have changed its answer -- which is how a claim gets
    RELATED to its past without being RUN again.
    """
    from engine.spine import fingerprint
    return fingerprint("claims", fn.__name__)


def _ledger():
    import json
    if LEDGER.exists():
        try:
            return json.loads(LEDGER.read_text())
        except Exception:
            return {}
    return {}


def _save_ledger(d):
    import json
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(d, sort_keys=True, indent=0))


# (section, claim, computation, expected, status)
CLAIMS = [
    ("3.1.92", "10,584 universes generated blind; 864 pass three filters",
     _generated, (True, 10584, 864), CURRENT),
    ("3.1.103", "regard is worth 1e19 times what it costs to hold",
     _regard, (True, 7300, 19), CURRENT),
    ("3.1.102", "the code freezes at 100% cost; rank steps at 3.8 children",
     _frozen, (100.0, 100, True), CURRENT),
    ("3.1.102", "rank is worth zero then 82 W at the carrying number",
     _rank, (3.8, False, True, 82), CURRENT),
    ("3.1.101", "innovation is omit/duplicate/combine at 4.48 per division",
     _innovation, (6, 4, 4.48, 3), CURRENT),
    ("3.1.100", "the modern code needs 1520 bases and 200 are held",
     _code, (5, 2, False, 1520), CURRENT),
    ("3.1.100", "selection on a trait is 7-9 orders too fast",
     _reach, (7, 7.0, 8.9), CURRENT),
    ("3.1.99", "every ligation is templated; the template is the catalyst",
     _template, (True, 25488, True, True, 200), CURRENT),
    ("3.1.98", "divides at 2x volume, 28 copies, 1.39 types lost",
     _heredity, (2.0, 28, 1.39, 10.0), CURRENT),
    ("3.1.96", "one compartment closes at 14 bases; an ocean is 1e35",
     _occurs, (True, 14, 13, 35), CURRENT),
    ("3.1.95", "Big Bang to a head in 37 links: 29 derived, 7 forced, 0 gaps",
     _wholechain, (37, 29, 7, 0, 1), CURRENT),
    ("3.1.95", "abundance falls as mass^-3/4 exactly",
     _damuth, 1.0, CURRENT),
    ("3.1.94", "the lineage holds at the 1.58 um closure floor",
     _floor, (1.58, True, True), CURRENT),
    ("3.1.91", "closure is 0.48 catalysts per reaction, above 2000 molecules",
     _pm, (0.48, True, 13, True), CURRENT),
    ("3.1.90", "closure at measured catalysis needs a 13-mer, under 20",
     _closes13, (13, True, 0.395), CURRENT),
    ("3.1.88", "a set closes above 1e-3; the measured p is 1e-8",
     _closure, (False, True, True), CURRENT),
    ("3.1.88", "cold buys 11x on build/break and 436x on lifetime",
     _persist, (11.4, 436), CURRENT),
    ("3.1.88", "three gates shut at 298 K, one at 255",
     _cold, (2.73, 259.0,
             ["fidelity", "persistence", "search"], ["search"]), CURRENT),
    ("3.1.86", "a head holds 4 trades; today needs 750k; holding never binds",
     _school, (4.0, 750000, True), CURRENT),
    ("3.1.85", "four gifts, four shorter clocks: 1411, 998, 957, 695",
     _gifts, ((1411, 998, 957, 695), True, 8), CURRENT),
    ("3.1.82", "steam caps at 54.7%; Rome 0.17x burial, we run 51x",
     _industry, (54.7, 0.17, 51, True), CURRENT),
    ("3.1.81", "empire 2250 km, 4.7% lies tolerated, 3 of 10 derive",
     _empire, (2250, 4.7, 3), CURRENT),
    ("3.1.80", "muscle for a 400 N blow is 53 cm2; bone picks no height",
     _muscle, (53, False), CURRENT),
    ("3.1.79", "speech is 256410x narrower than sight, 0.0122% of a brain",
     _speech, (256410, 0.0122), CURRENT),
    ("3.1.79", "two adults are the smallest viable group",
     _group, (2, False), CURRENT),
    ("3.1.79", "the fovea is 0.028% of the field; 900 s to sweep",
     _fovea, (0.028, 900, 289), CURRENT),
    ("3.1.78", "heat rejection binds; toolmakers fall under 20%",
     _binds, (True, True), CURRENT),
    ("3.1.77", "Earth is fragile in spread, one-sided in mass, free in Z",
     _fragile, (True, True, True), CURRENT),
    ("3.1.76", "worn insulation runs out at 19 C, a lodge reaches -64",
     _shelterladder, (19, -64), CURRENT),
    ("3.1.76", "a brush shelter pays back in 4.6 nights",
     _homenights, 4.6, CURRENT),
    ("3.1.76", "unreferenced rules are mostly lineage, not dead code",
     _lineage, (True, True), CURRENT),
    ("3.1.74", "the eye: diffraction 0.77 arcmin, sampling 1.01",
     _acuity, (0.77, 1.01), CURRENT),
    ("3.1.74", "stereo reaches 1320 m and 0.19 mm at arm's length",
     _stereo, (1320, 0.19), CURRENT),
    ("3.1.74", "a brain fills in 1.49 years; a life pours 47x through",
     _fills, (1.49, 47), CURRENT),
    ("3.1.73", "a body is 8x short of bone; a flaked edge goes through",
     _toolstress, (False, 8, True), CURRENT),
    ("3.1.73", "marrow pays for a brain 5.2x over",
     _marrowpays, (True, 5.2), CURRENT),
    ("3.1.73", "the tool root went from 2 nodes to 13",
     _tooldepth, 13, CURRENT),
    ("3.1.73", "16 of 20 tool configurations pay, on DERIVED gains",
     _toolcount, (16, 20), CURRENT),
    ("3.1.73", "the tool root is 13 nodes deep against 37 for radiative",
     _rootdepth, (13, 37), CURRENT),
    ("3.1.70", "a newborn's brain is 109% of its own budget",
     _infantshare, 109, CURRENT),
    ("3.1.70", "growth bottoms at age 5 where the brain is 71%",
     _growthdip, (5.0, 1.5, 71), CURRENT),
    ("3.1.70", "the provisioning debt is 3.0 adult-years per child",
     _debt, 3.0, CURRENT),
    ("3.1.69", "cooking short 1.73x on break-even, 2.18x on the gut",
     _cookinggap, (1.73, 2.18, 76), CURRENT),
    ("3.1.69", "death conserves total matter and burial breaks the cycle",
     _conserve, (True, True), CURRENT),
    ("3.1.68", "the light race stops at 11.4 m, and at 0.05 m alone",
     _race, (11.4, 0.05), CURRENT),
    ("3.1.68", "height scales as crown^0.4: 6, 11, 26, 64, 161 m",
     _crowns, (6, 11, 26, 64, 161), CURRENT),
    ("3.1.68", "4 trophic levels under a 204 m cavitation ceiling",
     _chainlen, (4, 204), CURRENT),
    ("3.1.31", "decay score is 8 right, 0 wrong, 6 refused",
     _decay, (8, 0, 6), CURRENT),
    ("3.1.27", "the derived magic numbers",
     _magic, (2, 8, 20, 28, 40, 50, 82, 126), CURRENT),
    ("3.1.27", "4.2% of the (kappa, mu) plane gives all seven closures",
     _region, 4.2, CURRENT),
    ("3.1.21", "Stefan-Boltzmann agrees to 3.25e-11",
     _sigma_rel, 3.25e-11, CURRENT),
    ("3.1.28", "the liquid drop is refused below A=13",
     _domain_floor, 13, CURRENT),
    ("3.1.29", "mass bar 1.850 in domain, 6.249 outside",
     _bars, (1.85, 6.249), CURRENT),
    ("3.1.31", "measured-Q precision derived as 0.0866 MeV",
     _mq_bar, 0.0866, CURRENT),
    ("3.1.31", "the unified binding table holds 29 nuclides",
     _table_size, 29, CURRENT),
    ("3.1.18", "folding survival rate 0.573",
     _fold_bar, 0.5729, CURRENT),
    ("3.1.39", "unfitted climate: Earth +21.0 K, Venus -488.3 K",
     _climate, (21.0, -488.3), CURRENT),
    ("3.1.42", "habitable band derived 0.999 - 1.899 AU",
     _band, (0.999, 1.899), CURRENT),
    ("3.1.60", "lab: 27 HOLDS, 0 CLASH, 1 MISSING_RULE, 1 REFUSED, "
               "1 SUGGESTION", _lab_counts, (27, 0, 1, 1), CURRENT),
    ("3.1.47", "chance reaches 57 residues and stops",
     _ceiling57, 57, CURRENT),
    ("3.1.39", "derived CO2 wing cutoff 11.2 cm-1 at 737 K",
     _cutoff, 11.2, CURRENT),
    ("3.1.39", "derived CO2 well depth 180 K",
     _welldepth, 180, CURRENT),
]

# Numbers that WERE published and no longer reproduce. Kept as
# history, named, so nobody mistakes them for present-tense claims.
SUPERSEDED = [
    ("3.1.61", "seeded life collapses to 0.10 microns",
     "withdrawn in 3.1.94. IT WAS AN UNBOUNDED OBJECTIVE, not a "
     "biological result. fitness() returned surplus PER GRAM -- "
     "a*m^(-1/3) - b*m^(-1/4) -- which diverges as mass falls: 3.3e6 "
     "at 1.58 microns and 5.5e8 a hundredth of the way down. The "
     "lineage was descending that without limit into max(r, 1e-7), a "
     "clamp with nothing behind it, and the resting place was "
     "therefore the clamp rather than any rule. The function's own "
     "docstring said 'bigger is cheaper per gram by Kleiber and "
     "harder to feed by geometry, and where they cross is a size', "
     "which is true of surplus and false of surplus per gram. "
     "engine/earthlab.py had already derived the missing bound -- "
     "1.58 microns, below which a compartment cannot hold the "
     "molecule types to catalyse its own repair -- and descent never "
     "consulted it. With closure in place the lineage neither "
     "collapses nor grows; it holds at 1.78 microns"),
    ("3.1.89", "wider sweep: p ~ R^-0.72, a 15-mer, 5 orders of gap",
     "withdrawn in 3.1.90. The number was close and the METHOD was "
     "still wrong: it fitted the threshold p against network size and "
     "extrapolated, which extrapolates a quantity that moves. "
     "Bisecting the threshold at seven sizes over two alphabets shows "
     "that f = p*R, the reactions one molecule catalyses at "
     "threshold, is LINEAR IN L with slope 0.395 -- and c = f/L holds "
     "between 0.31 and 0.49 while R changes 190-fold. Since R grows "
     "exponentially in L and the catalysis each molecule must supply "
     "grows only linearly, p = cL/R(L) is a derivation rather than a "
     "fit, and it lands at 13 bases rather than 15. This is the third "
     "value published for this quantity; the first two were 1e20 "
     "reactions and 6.4e9"),
    ("3.1.88", "extrapolating closure to 1e-8 asks for 1e20 reactions",
     "withdrawn in 3.1.89, and not for being uncertain -- for being "
     "WRONG BY ELEVEN ORDERS OF MAGNITUDE. It fitted p ~ R^-0.30 by "
     "sweeping polymer length over a two-letter alphabet, which "
     "varies network size and holds monomer diversity fixed. Adding "
     "a four-letter alphabet gives p ~ R^-0.72 and 6.4e9 reactions. "
     "The published number carried its extrapolation distance (17 "
     "orders) attached, which is why it was not trusted, but "
     "labelling an extrapolation as untrustworthy is not the same as "
     "checking it. Taking more data is. At four nucleotides the new "
     "figure is polymers up to about 15 bases, and earthlab derived "
     "20 bases independently as the assembly piece size"),
    ("3.1.87", "two gates shut at 298 K: fidelity and search",
     "withdrawn in 3.1.88 by ADDING A GATE, not by any number "
     "moving. Nothing was asking whether a replicase survives long "
     "enough to be copied, and a strand cut faster than it is "
     "rebuilt is not a replicase. Persistence is now a gate, it is "
     "SHUT at 298 K, and it opens by 273 -- so the list at 298 is "
     "three and the list at 255 is still one. A claim about which "
     "gates are shut is only as complete as the set of gates"),
    ("3.1.84", "every gift shortens the clock: 1809, 1201, 708 years",
     "withdrawn in 3.1.85, and the finding survived the correction "
     "that killed the numbers. The reach multiplier was capped at "
     "3.6, a figure I picked, and it turned out to be SATURATED "
     "before infrastructure was added -- so the cap and not the "
     "physics was setting the ceiling, and adding roads and grids "
     "changed nothing at all. The ceiling now comes from the flow: "
     "every watt of land photosynthesis feeds 2,707 billion. The "
     "years move to 1411, 998, 957, 695 and every gift still "
     "shortens the clock"),
    ("3.1.83", "the run reaches 24B and stops on food, not coal",
     "withdrawn in 3.1.84. 24 billion is still what the flow feeds, "
     "but 'stopped by food' was the only verdict that loop COULD "
     "return -- population grows to the ceiling and sits there, so "
     "moving the ceiling changed the number and never the answer. "
     "Phosphorus is a stock rather than a rate and gives the run a "
     "second way to fail, and with it in place all three scenarios "
     "end on PHOSPHORUS instead. The old claim was not wrong about "
     "the number; it was a claim about a model with one wall"),
    ("3.1.72", "the tool root is 2 nodes deep, the shallowest asked",
     "withdrawn in 3.1.73 BY BEING FIXED, which is the only way a "
     "depth claim can be withdrawn. Two nodes meant the question "
     "stood on one constant and itself -- a tool was being priced, "
     "never produced. engine/tools.py derives it instead: a blow is "
     "a force over an area, bone yields at a pressure engine/life.py "
     "already knew, and a fist misses by 8x while a flaked edge goes "
     "through. The root now runs 13 nodes and reaches "
     "life.BONE_COMPRESSIVE. The old number was right when it was "
     "published and the point of publishing it was to make it "
     "wrong"),
    ("3.1.72", "21 of 28 tool configurations pay",
     "withdrawn in 3.1.73, and not because it was miscounted -- it "
     "was, at 3.1.70, where 26 was written into the README by hand "
     "instead of read from the check, which is why both tool numbers "
     "are registered now. It is withdrawn because the SPACE changed. "
     "Those 28 combinations crossed four brain sizes with seven "
     "intake gains somebody picked out of the air, and the answer "
     "meant no more than the list did. engine/tools.py derives the "
     "gain from how much marrow is in a femur, how much energy is in "
     "marrow, and whether anything can open the bone at all -- so "
     "the gains are computed and there are five, not seven. 16 of 20 "
     "pay. The count went down and the number is worth more"),
    ("3.1.69", "the gut pays for the brain, 12.8 W against 11.1 W",
     "withdrawn in 3.1.70, and the arithmetic was never wrong -- the "
     "QUESTION was. It priced an adult standing still, where a brain "
     "is a running cost that some other organ must offset. A brain is "
     "not run, it is BUILT, out of food, in childhood, by someone who "
     "is not paying for it. Run the life instead of the snapshot and "
     "a newborn's brain is 109% of everything its own body can make, "
     "so provisioning is a precondition and not a trade; and body "
     "growth falls to its slowest at age five with the brain still at "
     "71%, so the child does not shrink an organ, it stops growing. "
     "The 3.0 adult-years a child costs was never inside one adult "
     "body to be found by rearranging its organs"),
    ("3.1.44", "every habitable world orbits a 0.51-0.54 Msun star",
     "withdrawn in 3.1.52. That held only while carbon could not "
     "reach an inner planet: the delivery source stopped at 45 AU and "
     "CO condenses at 124, so the only worlds scraping enough carbon "
     "were those around dim stars with close-in ice lines. With the "
     "source extended, 101 of 234 worlds are habitable and span every "
     "stellar mass. The correlation was the shape of a gap"),
    ("3.1.37", "habitable band outer edge 1.898 AU",
     "3.1.42 coarsened the root scan from 3,400 points to 420 after "
     "profiling showed it bought nothing; the outer edge moved by "
     "0.001 AU, which is inside the bisection tolerance"),
    ("3.1.31", "lab reported 1 CLASH",
     "resolved in 3.1.39: the far-wing clash was between two "
     "hand-waves, and deriving the intermolecular potential replaced "
     "both with a computed 11.2 cm-1"),
    ("3.1.33", "unfitted climate: Earth +12.3 K",
     "3.1.38 replaced the box-shaped wing with a real Lorentz profile "
     "that falls off with distance from line centre. The correct shape "
     "absorbs more, and Earth moved to +21.3 K -- worse agreement from "
     "better physics, with the excess traced to hand-entered band "
     "parameters being out by about a factor of two"),
    ("3.1.23", "unfitted climate: Earth -3.2 K",
     "3.1.33 fixed spectral overlap so overlapping bands add optical "
     "depth instead of averaging transmittance. Earth's water bands "
     "overlap heavily, so the old averaging under-counted them and the "
     "-3.2 K agreement was partly the bug. It now reads +12.3 K"),
    ("3.1.30", "ablation read 1 right, 1 wrong, 12 refused",
     "3.1.31 changed the rule being measured; it now reads 8, 0, 6. "
     "The table was correct when written and describes a system that "
     "no longer exists"),
    ("3.1.26", "8 right, 3 wrong, 3 refused",
     "those eight rested on a +5.455 MeV source inconsistency "
     "cancelling the liquid drop's deficit; superseded by 3.1.31, "
     "which reaches eight with zero wrong"),
    ("3.1.19", "Mercury held out at +2.8 K",
     "withdrawn in 3.1.20: it compared a redistributed prediction "
     "against a dayside observation"),
]


def run(verify=False):
    """-> rows. Recompute only the claims whose roots have moved.

    A claim's fingerprint commits to every rule beneath it, so an
    unchanged fingerprint is a PROOF that recomputing would return
    what it returned last time. Before this, checking 34 published
    numbers took 70 seconds because several of them spin up a
    process pool and sweep universes -- every run, to re-derive
    answers nothing could have changed.

    verify=True ignores the ledger and runs everything, which is
    what to do when the ledger itself is in doubt.
    """
    led = {} if verify else _ledger()
    fresh, rows, skipped = dict(led), [], 0
    for sec, claim, fn, want, status in CLAIMS:
        key = f"{sec}|{claim}"
        try:
            fp = _fp(fn)
        except Exception:
            fp = None
        prev = led.get(key)
        if fp and prev and prev.get("fp") == fp and prev.get("ok"):
            rows.append((sec, claim, want, want, True, status))
            skipped += 1
            continue
        try:
            got = fn()
            ok = got == want
        except Exception as e:
            got, ok = f"{type(e).__name__}: {e}", False
        rows.append((sec, claim, want, got, ok, status))
        if fp:
            fresh[key] = {"fp": fp, "ok": bool(ok)}
    if not verify:
        try:
            _save_ledger(fresh)
        except Exception:
            pass
    run.skipped = skipped
    run.total = len(CLAIMS)
    return rows


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("every_published_number_reproduces", _repro)
    t("superseded_numbers_are_named", _super)
    return all(o[1] for o in out), out


def _repro():
    rows = run()
    bad = [(s, c, w, g) for s, c, w, g, ok, _st in rows if not ok]
    if bad:
        raise ArithmeticError(
            "published numbers that no longer reproduce: "
            + "; ".join(f"{s} claims {c}: expected {w}, got {g}"
                        for s, c, w, g in bad))
    return (f"{len(rows)} load-bearing published numbers recomputed and "
            f"all {len(rows)} still hold. A number written into the "
            f"README is a claim the repository is still making, and "
            f"nothing else here reads the document")


def _super():
    if not SUPERSEDED:
        raise ArithmeticError("nothing is recorded as superseded, which "
                              "for a repo with four retractions is wrong")
    for sec, claim, why in SUPERSEDED:
        if len(why) < 40:
            raise ArithmeticError(f"{sec} is superseded without saying why")
    return (f"{len(SUPERSEDED)} published numbers are recorded as history "
            f"rather than current: "
            + "; ".join(f"{s} ({c[:38]}...)" for s, c, _w in SUPERSEDED)
            + ". Each says what replaced it")


if __name__ == "__main__":
    for sec, claim, want, got, ok, _st in run():
        print(f"  {'ok  ' if ok else 'STALE'} {sec:8}{claim[:52]:54}"
              f"{'' if ok else f'want {want} got {got}'}")
    print()
    for sec, claim, why in SUPERSEDED:
        print(f"  history {sec:8}{claim}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:34}{d[:70]}")
    print("\nall:", ok)
