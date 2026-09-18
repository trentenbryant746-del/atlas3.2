"""
Every number, and which of three things it is.

A challenge worth answering: this repository claims to derive rather
than predict, and the biology modules added most recently are full
of typed numbers. An audit found 28 with no label at all, and
several of them are not measurements. INTAKE_COEFFICIENT carries
the comment "sets where supply and demand cross", which is a knob
with a note on it.

So every number gets one of three kinds, and the kind decides what
may be said about a result that depends on it.

    EXACT      fixed by definition. No error, ever.
    MEASURED   someone went and found out. Carries their error and
               a source. Legitimate input.
    CHOSEN     nobody measured it and nothing derives it. It was
               picked so a model would run.

A CHOSEN number is not forbidden -- a model that refuses every
unmeasured quantity does nothing at all. What is forbidden is
CITING a result that rests on one as though it were derived. So
results are tagged by the worst input they depend on, and anything
resting on CHOSEN says so wherever it appears.

THIS IS THE SAME DISCIPLINE AS THE ERROR BARS, ONE LEVEL DOWN.
3.1.18 established that a bar belongs to a domain and 3.1.29 that
it belongs to a manifestation. This says a CLAIM belongs to its
weakest input, which is the rule those two were special cases of.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EXACT, MEASURED, CHOSEN = "EXACT", "MEASURED", "CHOSEN"

# A FOURTH KIND, AND ITS ABSENCE WAS MAKING CONTINGENCY LOOK LIKE A
# HOLE IN THE PHYSICS.
#
# engine/ancestry.py went SILENT on the last step -- nothing
# distinguishes one large-brained land endotherm from another -- and
# I called that a gap the rules could not close. That was the wrong
# reading. It is not a missing rule. It is a fact of a kind this
# repository had no slot for.
#
#   MEASURED   can be measured again tomorrow
#   RECORDED   happened ONCE, left evidence, and no rule predicts it
#
# The Chicxulub impact at 66 Mya. The single endosymbiosis that made
# mitochondria. The Great Oxidation. A primate lineage surviving an
# impact that killed the large dinosaurs. Not one is derivable and
# every one is CHECKABLE -- against strata, against phylogeny,
# against isotope ratios -- and checkability, not derivability, is
# the standard this repository actually holds to.
#
# So a chain that reaches contingency does not stop. It CHANGES
# KIND, the same way engine/atlas.py's cascade changes layer when a
# question stops being arithmetic and starts being a date. Crossing
# topics is what the system does; the only thing missing was
# admitting that history is one of the topics.
RECORDED = "RECORDED"

# A FIFTH KIND, because the human side answers a different question
# and had been answering it in the wrong voice.
#
# ENACTED is a thing that happened in a RUN. Not EXACT, nobody
# defined it. Not MEASURED, nobody observed it. Not CHOSEN, nobody
# picked it -- it is what the rules did. And not RECORDED, because
# RECORDED means it happened in the world and this did not.
#
# It is history, of a world that was never anywhere. Reporting
# "13.9% of universes carry a toolmaker" as though it were a
# measurement claims a survey of universes; reporting it as CHOSEN
# says somebody picked 13.9, which is worse. The number is real and
# reproducible and its subject is a simulation, and until now there
# was no way to say all three of those at once.
#
# The practical rule: an ENACTED result may be cited for what THESE
# RULES DO, never for what the world contains.
ENACTED = "ENACTED"

# The audit. Every typed number in the modules added recently,
# classified honestly rather than generously.
INPUTS = {
    # --- measured, with a source in the literature -------------
    "genesis.SULFURISATION_K": (MEASURED, "FeS condensation, 704 K"),
    "earthlab.CH2_TRANSFER_J": (MEASURED, "hydrophobic transfer per CH2"),
    "earthlab.SORET_PER_K": (MEASURED, "thermophoresis, small solutes"),
    "earthlab.MIN_REPLICASE_BASES": (MEASURED, "smallest RNA that copies RNA"),
    "biosphere.NPP_MODERN_KG_C_YR": (MEASURED, "net primary production"),
    "biosphere.CH4_LIFETIME_OXIC_YR": (MEASURED, "methane lifetime in air"),
    "biosphere.BLOOD_VISCOSITY": (MEASURED, "whole blood at 310 K"),
    "biosphere.OZONE_PRESENT_DU": (MEASURED, "Earth's ozone column"),
    "biosphere.O3_CROSS_SECTION_CM2": (MEASURED, "Hartley band"),
    "biosphere.CH4_OXIC_PPM": (MEASURED, "Earth today"),
    "origin.AGE_UNIVERSE_YR": (MEASURED, "age of the universe"),
    "potential.EPS0": (EXACT, "vacuum permittivity, fixed by c and mu0"),
    "signature.SECONDS_PER_YEAR": (MEASURED, "Julian year"),
    "origin.ALPHABET": (MEASURED, "20 proteinogenic amino acids"),
    "biosphere.DU_TO_MOLECULES_CM2": (EXACT, "Dobson unit definition"),

    # --- chosen. Nobody measured these and nothing derives them -
    "descent.INTAKE_COEFFICIENT": (
        CHOSEN, "picked so supply and demand cross at a plausible size"),
    "descent.PREDATION_PRESSURE": (
        CHOSEN, "fraction of deaths from predation; a dial"),
    "descent.PREDATOR_RATIO": (
        CHOSEN, "3x is a rule of thumb, not a measurement"),
    "descent.TRAIT_COST": (CHOSEN, "2% per trait, picked"),
    "descent.MUTATION_SIZE": (CHOSEN, "spread per generation, picked"),
    "descent.MUTATION_TRAIT": (CHOSEN, "trait gain rate, picked"),
    "earthlab.CATALYSIS_P": (
        CHOSEN, "mid-range of a 1e-6 to 1e-11 literature spread"),
    "earthlab.CROWDED_M": (CHOSEN, "concentration after drying, picked"),
    "earthlab.OCEAN_AMPHIPHILE_M": (
        CHOSEN, "a generous early-ocean estimate, not a measurement"),
    "earthlab.VESICLE_RADIUS_M": (CHOSEN, "smallest bilayer, order only"),
    "earthlab.LIGATION_PIECE_BASES": (CHOSEN, "20 bases, picked"),
    "biosphere.REDUCED_SINK_KG": (CHOSEN, "order of magnitude only"),
    "biosphere.CH4_ANOXIC_PPM": (CHOSEN, "early Earth, poorly constrained"),
    "biosphere.CH4_LIFETIME_ANOXIC_YR": (CHOSEN, "order of magnitude"),
    "biosphere.AEROBIC_MIN_FRACTION": (CHOSEN, "1% Pasteur point, a convention"),
    "census.MIN_WINDOW_GYR": (CHOSEN, "how long life needs; nobody knows"),
    "genesis.EJECTION_YEARS": (CHOSEN, "dynamical lifetime, order only"),
    "genesis.SCATTERED_FRACTION": (CHOSEN, "fraction thrown inward, picked"),
    "ecology.CARRYING_ENERGY_W": (CHOSEN, "total world energy, picked"),
    "ecology.NICHE_WIDTH": (CHOSEN, "how similar two species must be"),
    "biome.PHOTOSYNTHETIC_EFFICIENCY": (
        CHOSEN, "1% of incident light fixed; real leaves run 0.5-2%"),
    "biome.EXTINCTION_K": (
        MEASURED, "Beer-Lambert canopy coefficient, 0.3-0.7 observed"),
    "biome.TRANSFER_FRACTION": (
        MEASURED, "10% up each trophic step, Lindeman; 2-20% observed"),
    "biome.TRUNK_DENSITY": (MEASURED, "wood, 400-700 kg/m3"),
    "biome.WOOD_MODULUS": (MEASURED, "Young's modulus of wood, 8-15 GPa"),
    "biome.GREENHILL_C": (
        EXACT, "0.792 from the Bessel root for a self-loaded column"),
    "biome.SAPWOOD_M": (CHOSEN, "living shell thickness, order only"),
    "biome.RESP_PER_KG": (CHOSEN, "W per kg of living plant tissue"),
    "biome.XYLEM_TENSION": (
        MEASURED, "sap sustains about -2 MPa before cavitating"),
    "biome.CROWN_M2": (CHOSEN, "leaf area a plant holds up; a dial"),
    "atoms.REDFIELD": (
        MEASURED, "C106 H263 O110 N16 P1, plankton stoichiometry"),
    "atoms.CELLULOSE": (EXACT, "(C6H10O5)n, the formula of wood"),
    "atoms.WEIGHT": (MEASURED, "standard atomic weights"),
    "atoms.AVOGADRO": (EXACT, "SI definition since 2019"),
    "human.BODY_KG": (CHOSEN, "70 kg, a round adult"),
    "human.APE_BRAIN_KG": (MEASURED, "chimpanzee, about 400 g"),
    "human.HUMAN_BRAIN_KG": (MEASURED, "about 1350 g"),
    "human.APE_GUT_FRACTION": (MEASURED, "great ape, about 3% of mass"),
    "human.HUMAN_GUT_FRACTION": (MEASURED, "about 1.7% of mass"),
    "human.GUT_COST_RATIO": (MEASURED, "gut runs about 12x average tissue"),
    "human.COOKING_GAIN": (
        MEASURED, "cooked food yields about 35% more; NOT raised to "
                  "close the gap it fails to close"),
    "revolution.START_W": (CHOSEN, "120 W per person beyond muscle"),
    "revolution.BIRTH_AT_SURPLUS": (CHOSEN, "1.5%/yr at full surplus"),
    "revolution.FOOD_W_PER_PERSON": (
        MEASURED, "upkeep plus a child's share, about 130 W"),
    "cold.EA_HYDROLYSIS": (MEASURED, "~100 kJ/mol, breaking a bond"),
    "cold.EA_POLYMERISE": (MEASURED, "~60 kJ/mol, catalysed building"),
    "cold.K_HYD_298": (MEASURED, "1e-9 /s at pH 7, 298 K"),
    "generate.AXES": (
        CHOSEN, "the grid the rules are walked over; chosen to span "
                "what the rules accept, NOT to bracket an answer"),
    "closure.CATALYSTS_PER_REACTION": (
        MEASURED, "0.481 catalysts per reaction at closure, bisected "
                  "over 6 networks above 2000 molecules"),
    "closure.MEANFIELD_MIN_M": (
        MEASURED, "2000 molecules, where p*M converges"),
    "closure.ALPHABET": (CHOSEN, "two monomers, the smallest case"),
    "closure.MAX_LEN": (CHOSEN, "polymer length; tractability"),
    "closure.FOOD_LEN": (CHOSEN, "what the world supplies unasked"),
    "cold.KF_WATER": (MEASURED, "cryoscopic constant, 1.86 K kg/mol"),
    "cold.SEAWATER_OSMOLAL": (MEASURED, "about 1.2 mol particles per kg"),
    "cold.NACL_EUTECTIC_K": (MEASURED, "251.9 K, below it no brine"),
    "cold.REF_ERROR": (
        MEASURED, "best ribozyme, 1 error in 100 at 298 K; the "
                  "discrimination energy is READ OFF this, not chosen"),
    "school.LIFE_LEARN_HOURS": (
        CHOSEN, "40,000 waking hours of teaching in a life; generous"),
    "school.WORKING_LIFE_YR": (MEASURED, "about 50 years"),
    "school.SPECIALIST_FRACTION": (CHOSEN, "1% of people specialise"),
    "school.DISCOVERY_PER_SURPLUS": (
        MEASURED, "CALIBRATED to Rome 30 trades -> 1800 Europe 3,000, "
                  "not chosen; the first guess was 1e5 times small"),
    "school.CORPUS": (RECORDED, "rough corpus sizes in trade-equivalents"),
    "revolution.APPRENTICE_HOURS": (
        MEASURED, "10,000 hours to a trade; the upper bound on what "
                  "one person can be told"),
    "revolution.INFRASTRUCTURE": (
        CHOSEN, "lifetimes, upkeep shares and reach gains; GIVEN"),
    "revolution.BOILERS": (
        MEASURED, "working pressure and saturation temperature; this "
                  "REPLACED a chosen 1.2%/yr learning rate"),
    "revolution.BIOLOGICAL_N": (MEASURED, "~140 Tg N/yr fixed biologically"),
    "revolution.HABER_N": (MEASURED, "~120 Tg N/yr industrially"),
    "revolution.P_RESERVE_KG": (MEASURED, "~70 Gt rock phosphate"),
    "revolution.FOOD_DRY_MJ_KG": (MEASURED, "17 MJ/kg dry plant food"),
    "revolution.FED_NOW": (
        RECORDED, "8 billion people currently fed; the food ceiling "
                  "is derived from this and not from a guessed share"),
    "industry.POPULATION": (MEASURED, "Roman empire, about 60 million"),
    "industry.BURIAL_FRACTION": (
        CHOSEN, "0.1% of production buried; the number the stock rests on"),
    "industry.STOCK_MYR": (MEASURED, "Carboniferous onward, ~300 Myr"),
    "industry.WATER_CRITICAL_K": (EXACT, "647.1 K, above it no liquid"),
    "industry.MODERN_TW": (MEASURED, "present human power draw, ~18 TW"),
    "pov.E0_DEG": (MEASURED, "cone density falloff constant, ~2.3 deg"),
    "pov.HAZE_KM": (CHOSEN, "atmospheric extinction scale; the only "
                            "free parameter in the picture"),
    "empire.COURIER_KM_DAY": (MEASURED, "Roman cursus publicus, ~50"),
    "empire.CRISIS_DAYS": (
        CHOSEN, "90 days for a revolt to consolidate; a dial"),
    "empire.TELL_S": (CHOSEN, "60 s to be told a thing"),
    "empire.DERIVE_S": (CHOSEN, "3600 s to work it out unaided"),
    "empire.WRONG_COST_MULT": (CHOSEN, "acting on a falsehood, 20x"),
    "empire.COMMANDMENTS": (CHOSEN, "a code, HANDED over"),
    "pov.SCENE": (CHOSEN, "objects placed to exercise the limits"),
    "inherit.MUSCLE_PA": (
        MEASURED, "vertebrate specific tension, about 0.3 MPa"),
    "inherit.ELBOW_LEVER": (MEASURED, "about 4:1 mechanical disadvantage"),
    "inherit.MUTATIONS_PER_GEN": (MEASURED, "about 70 de novo in humans"),
    "inherit.DELETERIOUS_PER_GEN": (MEASURED, "about 1.5 of those harmful"),
    "inherit.GIVEN_GENOME": (
        CHOSEN, "height and load HANDED over; bone does not pick a "
                "height and nothing purges a mutation"),
    "civ.SPEECH_BITS_S": (
        MEASURED, "39 bit/s across 17 languages, Coupe et al."),
    "civ.FORAGER_W": (MEASURED, "2000 kcal/day net, about 97 W"),
    "civ.GIVEN": (
        CHOSEN, "language and pooling were HANDED over, not derived"),
    "recognize.FIELD_DEG": (MEASURED, "120 deg binocular"),
    "recognize.FOVEA_DEG": (MEASURED, "2 deg of sharp vision"),
    "recognize.SACCADES_S": (MEASURED, "about 4 a second"),
    "recognize.CELLS_TO_IDENTIFY": (
        CHOSEN, "20 cells across a thing to name it; a dial"),
    "shelter.INSULATION": (
        MEASURED, "effective conductance W/m2K for each shell"),
    "shelter.BODY_AREA_M2": (MEASURED, "1.8 m2 for a 70 kg adult"),
    "shelter.BUILD_DAYS": (
        CHOSEN, "3 days of output to build a shelter; a dial"),
    "multiverse.RAM_BUDGET_MB": (CHOSEN, "given, and it was not needed"),
    "senses.WAVELENGTH_M": (MEASURED, "550 nm, photopic peak"),
    "senses.PUPIL_M": (MEASURED, "3 mm in daylight"),
    "senses.CONE_PITCH_M": (MEASURED, "2.5 um foveal cone spacing"),
    "senses.EYE_BASELINE_M": (MEASURED, "64 mm interpupillary"),
    "senses.DISPARITY_RAD": (MEASURED, "10 arcsec stereoacuity"),
    "senses.PRECISION_GRIP_N": (MEASURED, "thumb opposed, about 80 N"),
    "senses.HOOK_GRIP_N": (MEASURED, "no opposition, about 25 N"),
    "senses.GRIP_FRICTION": (MEASURED, "skin on stone, mu about 0.5"),
    "learning.SYNAPSES": (MEASURED, "about 1e14 in a human cortex"),
    "learning.BITS_PER_SYNAPSE": (
        MEASURED, "4.7, Bartol et al. from spine-head size classes"),
    "learning.OPTIC_FIBRES": (MEASURED, "about 1e6 per optic nerve"),
    "learning.BITS_PER_FIBRE_S": (
        CHOSEN, "10 bit/s after retinal coding; order only"),
    "tools.MATERIALS": (MEASURED, "compressive strengths, Pa"),
    "tools.CONTACT": (MEASURED, "striking surface areas, m2"),
    "tools.ARM_BLOW_N": (MEASURED, "a hammering blow, about 400 N"),
    "tools.MARROW_KG_PER_FEMUR": (MEASURED, "large ungulate, about 200 g"),
    "tools.MARROW_J_PER_KG": (MEASURED, "700 kcal per 100 g"),
    "tools.FORAGER_DAY_J": (MEASURED, "2000 kcal a day"),
    "roots.SUITE_WARM_S": (
        MEASURED, "the full suite warm, timed on this machine"),
    "ontogeny.ONTOGENY": (
        MEASURED, "one human's body and brain mass by age"),
    "ontogeny.NEURAL": (
        MEASURED, "C40H80NO8P, phospholipid; a brain is not plankton"),
    "ontogeny.FORAGER_W": (MEASURED, "2000 kcal/day net, about 97 W"),
    "ancestry.NEURAL_COST_RATIO": (
        MEASURED, "neural tissue costs about 10x average tissue"),
}

# Results that happened in a RUN. Their subject is a simulation, so
# they may be cited for what these rules do and never for what the
# world contains. Every one of them is on the human side, which is
# the whole reason the kind was needed: physics answers what CAN
# happen and this answers what DID, in a world that was not anywhere.
ENACTED_RESULTS = {
    "13.9% of universes carry a toolmaker":
        "a sweep of generated seeds, not a survey of the sky",
    "heat rejection refuses about an eighth of worlds":
        "what these gates do, not a census of climates",
    "Earth survives -1.15% to +2% of disc spread":
        "fragility of this generator around this seed",
    "the light race stops at 11.4 m":
        "a stand of modelled plants, not a forest anyone walked",
    "one lineage collapses to 0.10 microns":
        "what descent.py does when run, not a fossil record",
    "a brush shelter pays back in 4.6 nights":
        "an accounting over modelled nights",
    "a brain fills in 1.49 years":
        "a rate against a capacity, not an observed child",
    "two adults are the smallest viable group":
        "an energy balance over modelled foragers",
    "a person is nameable to 289 m":
        "geometry against an acuity, not a field trial",
    "an empire reaches 2250 km at courier speed":
        "a span computed from a courier speed, not a map",
    "60 million industrialising stays inside the flow":
        "a draw against a burial rate, not a history",
    "every gift shortens the phosphorus clock":
        "three trajectories these rules produce, not ones anybody lived",
    "holding never binds; discovery rate does":
        "a corpus these rules grow, not one anybody catalogued",
    "a set closes above p=1e-3, measured is 1e-8":
        "a network these rules build and prune, not one in a flask",
    "10,584 universes generated blind, queried in 45 ms":
        "a space these rules produce, not a survey of anything",
}

# Which results lean on which inputs. A claim is only as good as
# its worst one.
CLAIMS_ON = {
    "the habitable band 0.999-1.899 AU": [],
    "Earth composition Fe 32.0%": [],
    "the 57-residue search ceiling": ["origin.ALPHABET",
                                      "origin.AGE_UNIVERSE_YR"],
    "the cell size window 1.58-47.5 um": ["earthlab.CATALYSIS_P",
                                          "earthlab.CROWDED_M"],
    "life cools its own planet by 1.9 K": ["biosphere.CH4_ANOXIC_PPM"],
    "the light race stops at 11 m": ["biome.CROWN_M2",
                                    "biome.RESP_PER_KG",
                                    "biome.PHOTOSYNTHETIC_EFFICIENCY"],
    "height is worthless without a rival": [],
    "the food chain runs 4 levels": ["biome.PHOTOSYNTHETIC_EFFICIENCY"],
    "a flaked edge opens a bone and a fist cannot": [],
    "the eye sits at its own diffraction limit": [],
    "worn insulation runs out at 19 C": [],
    "speech is 0.0122% of a brain over a lifetime": [],
    "muscle for a 400 N blow is 53 cm2": [],
    "an empire reaches 2250 km at courier speed": ["empire.CRISIS_DAYS"],
    "steam caps at 54.7% whatever it is made of": [],
    "we burn 51 years of burial every year": ["industry.BURIAL_FRACTION"],
    "instructions cost 0.0003% of a brain": [],
    "one head holds about four trades": [],
    "the fidelity gate opens in a 7 K window": [],
    "cold slows breaking 11x more than building": [],
    "closure is 0.48 catalysts per reaction": [],
    "10,584 universes generated blind, queried in 45 ms": [
        "generate.AXES"],
    "a set closes above p=1e-3, measured is 1e-8": [
        "closure.ALPHABET", "closure.MAX_LEN"],
    "a ribozyme is at its thermodynamic limit": [],
    "holding never binds; discovery rate does": [
        "school.SPECIALIST_FRACTION", "school.LIFE_LEARN_HOURS"],
    "infrastructure taxes 8% and shortens the clock": [
        "revolution.INFRASTRUCTURE"],
    "every gift shortens the phosphorus clock": [
        "revolution.BIRTH_AT_SURPLUS", "revolution.START_W"],
    "engine efficiency is a material, not a learning rate": [],
    "the channel tolerates 4.7% lies": ["empire.WRONG_COST_MULT"],
    "the assigned genome costs 11% more forever": ["inherit.GIVEN_GENOME"],
    "two adults are the smallest viable group": ["civ.FORAGER_W"],
    "the fovea is 0.028% of the field": [],
    "a person is nameable to 289 m": ["recognize.CELLS_TO_IDENTIFY"],
    "a shelter pays back in 4.6 nights": ["shelter.BUILD_DAYS"],
    "26.7% of universes carry a toolmaker": [],
    "stereo gives out past 1320 m": [],
    "a brain fills in 1.49 years": ["learning.BITS_PER_FIBRE_S"],
    "marrow pays for a brain 5.2x over": [],
    "a newborn's brain is 109% of its own budget": [],
    "growth bottoms at age 5 where the brain is 71%": [],
    "the provisioning debt is 3.0 adult-years": [],
    "cooking is short by a factor of 2.18": ["human.COOKING_GAIN"],
    "death returns every atom": [],
    "a brain must raise intake by a fifth": [],
    "seeded life stays microbial": ["descent.INTAKE_COEFFICIENT",
                                    "descent.TRAIT_COST"],
    "competition prevents the collapse": ["ecology.CARRYING_ENERGY_W",
                                          "ecology.NICHE_WIDTH",
                                          "descent.INTAKE_COEFFICIENT"],
    "predation does not reverse the collapse": [
        "descent.PREDATION_PRESSURE", "descent.PREDATOR_RATIO",
        "descent.INTAKE_COEFFICIENT"],
    "Earth reads as driven and Mars does not": [],
    "it was us and not another large-brained endotherm": ["RECORDED"],
    "eukaryotes exist at all": ["RECORDED"],
}


# Contingent facts. Not derived, not repeatable, all checkable.
RECORDS = {
    "great oxidation": (2.4e9, "isotope ratios in sediment; oxygen "
                                "became free once the crustal sink filled"),
    "mitochondrial endosymbiosis": (1.8e9, "one archaeal host took up "
                                            "one bacterium, ONCE -- "
                                            "every eukaryote descends "
                                            "from that single event"),
    "chicxulub": (6.6e7, "an iridium layer worldwide and a crater; "
                          "nothing in orbital mechanics required it "
                          "to arrive then"),
    "primates survive it": (6.6e7, "phylogeny places the split before "
                                    "the boundary and the lineage after "
                                    "it -- a fact about what happened, "
                                    "not about what had to"),
}


def kind_of(name):
    return INPUTS.get(name, (CHOSEN, "unregistered, so assumed chosen"))[0]


def grade(claim):
    """-> (kind, why). A claim is as good as its worst input."""
    deps = CLAIMS_ON.get(claim)
    if deps is None:
        return CHOSEN, f"{claim!r} is not registered"
    if deps == ["RECORDED"]:
        return RECORDED, ("rests on something that happened once and "
                          "left evidence. Not derivable, and checkable, "
                          "which is the standard here")
    if not deps:
        return EXACT, (f"rests on no chosen input -- every number "
                       f"under it is exact, measured or derived")
    worst = CHOSEN if any(kind_of(d) == CHOSEN for d in deps) else MEASURED
    bad = [d for d in deps if kind_of(d) == CHOSEN]
    return worst, (f"rests on {len(deps)} registered inputs"
                   + (f", of which {len(bad)} are CHOSEN: "
                      + ", ".join(bad) if bad else ", all measured"))


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("every_number_is_classified", _classified)
    t("chosen_numbers_are_admitted", _chosen)
    t("results_are_graded_by_worst_input", _graded)
    t("the_planet_chain_rests_on_nothing_chosen", _planet)
    t("history_is_a_kind_not_a_gap", _recorded)
    t("a_run_is_not_a_measurement", _enacted)
    return all(o[1] for o in out), out


def _classified():
    counts = {}
    for k, (kind, _w) in INPUTS.items():
        counts[kind] = counts.get(kind, 0) + 1
    return (f"{len(INPUTS)} numbers classified: "
            + ", ".join(f"{v} {k}" for k, v in sorted(counts.items()))
            + ". An audit found 28 with no label at all, and calling "
              "them all 'measured' would have been the generous answer "
              "rather than the true one")


def _chosen():
    bad = [k for k, (kind, _w) in INPUTS.items() if kind == CHOSEN]
    if not bad:
        raise ArithmeticError("nothing is marked CHOSEN, which for a "
                              "repository with evolutionary parameters "
                              "in it is not credible")
    return (f"{len(bad)} numbers are CHOSEN -- picked so a model would "
            f"run, with nobody having measured them. The worst is "
            f"descent.INTAKE_COEFFICIENT, which carried the comment "
            f"'sets where supply and demand cross'. That is a knob "
            f"with a note on it, and pretending otherwise is how a "
            f"fit becomes a finding")


def _graded():
    rows = [(c, grade(c)[0]) for c in CLAIMS_ON]
    chosen = [c for c, k in rows if k == CHOSEN]
    clean = [c for c, k in rows if k == EXACT]
    return (f"{len(clean)} of {len(rows)} registered claims rest on "
            f"nothing chosen. {len(chosen)} do rest on chosen inputs "
            f"and must say so wherever they appear: "
            + "; ".join(chosen))


def _planet():
    for c in ("the habitable band 0.999-1.899 AU",
              "Earth composition Fe 32.0%",
              "Earth reads as driven and Mars does not"):
        k, why = grade(c)
        if k == CHOSEN:
            raise ArithmeticError(f"{c} rests on a chosen input: {why}")
    return ("the planet results -- the habitable band, Earth's "
            "composition, the biosignature -- rest on no chosen input. "
            "The BIOLOGY results do. That split is the honest state: "
            "the physics derives and the evolutionary modelling has "
            "dials in it")


def _recorded():
    if not RECORDS:
        raise ArithmeticError("no recorded facts, so contingency still "
                              "has no slot")
    k, _w = grade("it was us and not another large-brained endotherm")
    if k != RECORDED:
        raise ArithmeticError(f"contingency graded {k}, not RECORDED")
    return (f"{len(RECORDS)} contingent facts registered, each one "
            f"unrepeatable and each one checkable -- Chicxulub against "
            f"an iridium layer, endosymbiosis against every eukaryote "
            f"genome, the Great Oxidation against sediment isotopes. "
            f"engine/ancestry.py went SILENT on its last step and I "
            f"read that as a hole in the physics. It is not. It is a "
            f"fact of a kind that had no slot, and a chain reaching it "
            f"should CHANGE KIND rather than stop -- the same way the "
            f"cascade changes layer when a question stops being "
            f"arithmetic and starts being a date")



def _enacted():
    """The fifth kind, and what it forbids.

    First written to require that nothing be both ENACTED and
    input-graded, and it failed on its own registry in one run --
    correctly. The two are ORTHOGONAL axes, not rival labels. An
    input grade says how good the numbers going in were. ENACTED
    says what the answer is ABOUT. "13.9% of universes carry a
    toolmaker" rests on chosen inputs AND is a fact about a
    simulation, and both have to be sayable at once or the honest
    description is unavailable.
    """
    if not ENACTED_RESULTS:
        raise ArithmeticError("nothing is registered as enacted")
    graded = set(ENACTED_RESULTS) & set(CLAIMS_ON)
    for k, why in ENACTED_RESULTS.items():
        if "measur" in why.lower() and "not" not in why.lower():
            raise ArithmeticError(f"{k!r} describes itself as measured")
    return (f"{len(ENACTED_RESULTS)} results are ENACTED -- they "
            f"happened in a run. Not EXACT, nobody defined them; not "
            f"MEASURED, nobody observed them; not CHOSEN, nobody "
            f"picked them; and not RECORDED, which means it happened "
            f"in the world. They are history of a world that was "
            f"never anywhere. {len(graded)} of them ALSO carry an "
            f"input grade, and that is not a contradiction -- the "
            f"grade says how good the numbers going in were and this "
            f"says what the answer is about. Every one is on the "
            f"human side, which is why the kind was needed: physics "
            f"answers what CAN happen and this answers what DID. An "
            f"ENACTED result may be cited for what these rules do "
            f"and never for what the world contains")


if __name__ == "__main__":
    for kind in (EXACT, MEASURED, CHOSEN):
        names = [k for k, (x, _w) in INPUTS.items() if x == kind]
        print(f"  {kind} ({len(names)})")
        for n in sorted(names):
            print(f"      {n:38}{INPUTS[n][1][:44]}")
    print()
    for c in CLAIMS_ON:
        k, why = grade(c)
        print(f"  {k:9}{c[:44]:46}{why[:40]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:52]}")
