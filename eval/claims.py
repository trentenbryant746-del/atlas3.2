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


# (section, claim, computation, expected, status)
CLAIMS = [
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


def run():
    rows = []
    for sec, claim, fn, want, status in CLAIMS:
        try:
            got = fn()
            ok = got == want
        except Exception as e:
            got, ok = f"{type(e).__name__}: {e}", False
        rows.append((sec, claim, want, got, ok, status))
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
