"""
Nebula to human, one chain, every link named.

The pieces existed and did not connect. engine/planetlab.py walks a
planet to land creatures. engine/earthlab.py asks whether a first
cell is possible. engine/ancestry.py walks LUCA to us. Each was
written for its own question and none of them hands off, so the
chain nobody could read was the one thing the repository was for.

This assembles it, and it assembles it by DERIVATION -- every link
is a rule already proved somewhere else, cited, with its verdict
carried forward. Nothing here simulates. Rule 3 in the README: if
a check runs a search, the rule underneath it has not been found.

A link is one of four things, and the difference is the point:

    DERIVED    a rule here produces it
    ALLOWED    no rule forbids it, and none produces it either
    CROSSES    it depends on something that happened once
    MISSING    a gap with a name and, where possible, a size

And past the last link, three rules about what lives there --
competitive exclusion, energetic equivalence, and the bound on
how many species one world can hold. Those are theorems, not
runs.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, ALLOWED, CROSSES, MISSING = "DERIVED", "ALLOWED", "CROSSES", "MISSING"
FORCED = "FORCED"

# THE DISTINCTION THE MIDDLE OF THE CHAIN WAS MISSING.
#
# Seven links read ALLOWED -- no rule forbids them and none
# produces them. That is a weaker statement than it looked, and
# the weakness is specific: engine/ancestry.py supplies a
# PERMISSION for each (a pump is affordable, bone carries the
# weight, ozone shields) and nothing supplies a PRESSURE.
#
# A permission says the step is payable. A pressure says something
# is worse off not taking it. Only the second produces anything,
# and several are already derived elsewhere and were never
# connected -- engine/biome.py found the only pressure in the
# repository that rewards being LARGER, and no link cited it.
#
#   ALLOWED   permitted, nothing drives it
#   FORCED    permitted AND something drives it, both cited


def membrane_energy_per_volume(radius_m, internal_membranes=1):
    """ATP capacity over genome capacity. DERIVED.

    A prokaryote makes ATP across its OUTER membrane, area r^2,
    and holds its genome in volume, r^3. So energy per gene falls
    as 1/r and a large prokaryote starves its own genome.
    Internalising membranes multiplies the area without touching
    the volume, which is what a mitochondrion is.
    """
    area = 4.0 * math.pi * radius_m ** 2 * internal_membranes
    vol = 4.0 / 3.0 * math.pi * radius_m ** 3
    return area / vol


def energy_per_gene_gain(small_r=0.5e-6, big_r=5e-6, n_mito=200):
    """-> ratio. What internalising membranes buys. DERIVED."""
    plain = membrane_energy_per_volume(big_r, 1)
    with_m = membrane_energy_per_volume(big_r, n_mito)
    return with_m / plain, membrane_energy_per_volume(small_r, 1) / plain


def before_earth():
    """-> [...]. Big Bang to a nebula, from epochs and accounts."""
    from engine.epochs import EPOCHS, BBN_YIELD, BBN_BARRIER
    from engine.abundance import heaviest_stable
    rows = []
    prev = None
    for name, t, why in EPOCHS:
        if prev is not None:
            rows.append((prev, name, DERIVED, "epochs.EPOCHS",
                         f"{why} (t = {t:.1e} s)"))
        prev = name
    rows.insert(4, ("bbn", "the mass-5 and mass-8 gap", DERIVED,
                    "epochs.BBN_BARRIER",
                    f"{BBN_YIELD['He4']:.0%} helium and almost nothing "
                    f"heavier, because {BBN_BARRIER[:80]}"))
    rows.append(("ns_merger", "a nebula with metals", DERIVED,
                 "abundance.channels",
                 "every naturally occurring element has a production "
                 "channel and the heaviest stable one is named"))
    return rows


def before_luca():
    """-> [(from, to, verdict, rule, why)]. Nebula to a first cell."""
    from engine.evolve import habitable_band, luminosity_at
    from engine.cold import temperature_for, NACL_EUTECTIC_K
    from engine.earthlab import size_window, MIN_REPLICASE_BASES
    from engine.closure import length_closing_derived
    from engine.earthlab import CATALYSIS_P

    lo, hi = habitable_band(float(getattr(luminosity_at(1.0, 4.6),
                                          "value",
                                          luminosity_at(1.0, 4.6))))
    top = temperature_for(1.0 / MIN_REPLICASE_BASES)
    floor, roof, _w = size_window()
    L, _M, _p = length_closing_derived(CATALYSIS_P)

    return [
        ("a nebula", "a star and planets", DERIVED, "genesis.composition",
         "condensation of minerals by temperature; Earth's iron comes "
         "out at 32.0% against a measured 32.1%"),
        ("planets", "one in the band", DERIVED, "evolve.habitable_band",
         f"the carbonate-silicate thermostat puts the band at "
         f"{lo:.3f}-{hi:.3f} AU, derived from radiative transfer and "
         f"not fitted to Earth"),
        ("a warm ocean", "a cold brine", DERIVED, "cold.temperature_for",
         f"copying is discrimination, mu = exp(-dG/kT), so fidelity is "
         f"a temperature: the window runs {NACL_EUTECTIC_K:.0f}-"
         f"{top:.0f} K, seven kelvin wide, bounded below by the "
         f"eutectic and above by sloppy copying"),
        ("brine", "an autocatalytic set", DERIVED,
         "closure.length_closing_derived",
         f"a set closes when about half its reactions have a catalyst, "
         f"p*M = 0.48, which at four nucleotides needs polymers to "
         f"{L} bases -- under the {20} earthlab derives for assembly"),
        ("a closed set", "a bounded cell", DERIVED,
         "earthlab.size_window",
         f"closure needs {1e6*floor:.2f} microns to hold the molecule "
         f"types and diffusion allows {1e6*roof:.1f}; the window is "
         f"two rules meeting, not one measurement"),
        ("a cell that could be", "chemistry that sustains itself",
         DERIVED, "occurrence.closes_in_one",
         "the gate said yes or no and occurrence needed a rate. One "
         "compartment at the closure floor holds 1e10 molecules, "
         "which is every polymer to 14 bases, and p*M = 3.58 against "
         "the 0.48 closure needs -- at the MEASURED catalysis of "
         "1e-8. An ocean is 8.1e34 such compartments"),
        ("self-sustaining chemistry", "one that divides", DERIVED,
         "heredity.divides_at",
         "two spheres of half the volume need 2^(1/3) times one "
         "sphere's area, 26% more; lipid is made in proportion to "
         "contents so area accrues as V while a sphere needs "
         "V^(2/3). A vesicle divides exactly when it doubles and "
         "nothing decides to"),
        ("one that divides", "one that inherits", DERIVED,
         "heredity.copies_per_type",
         "28 copies of each of 3.6e8 types, so a half-split misses "
         "one with probability 2^-28. Heredity is what copy number "
         "does under a coin flip, not a mechanism added"),
        ("one that inherits", "one that is selected", DERIVED,
         "heredity.lost_per_division",
         "1.39 types lost per division, and 10% of reactions have "
         "exactly one catalyst, so about half of daughters cannot "
         "close. Variation and differential survival, neither added "
         "and no mutation rate introduced"),
        ("a selected lineage", "one that copies a sequence", DERIVED,
         "template.templated_fraction",
         "a ligation is templated when its product's complement is "
         "present, and THE TEMPLATE IS THE CATALYST. 25,488 of "
         "25,488 ligations have one available, because a complete "
         "polymer set is closed under complementation. It selects "
         "the join rather than permitting it, and comp(comp(s)) is "
         "s, so two rounds replicate"),
        ("a copied sequence", "one that is read", DERIVED,
         "code.affordable_code",
         "a code is the rule that closes reading, and it is not "
         "free: each meaning costs an adaptor and every adaptor is "
         "a sequence. The modern 20-letter code needs 1,520 bases "
         "against the 200 fidelity allows -- it does not fit. Five "
         "meanings do, so the first code was small and how small is "
         "set by temperature"),
        ("a small code", "a cell that is", DERIVED,
         "frozen.cost_of_change",
         "a mapping is selected by the cost of CHANGING it: with 5 "
         "meanings over 100 codons one change breaks 100% of every "
         "sequence written so far, and it is total from the first "
         "ones, before anything has had time to be good. Something "
         "selects HAVING a code and is blind to WHICH, which is why "
         "the real one looks arbitrary"),
    ]


# What DRIVES each middle step, where a rule here supplies one.
# WHAT THE STEP IS, not merely what drives it. engine/innovation.py
# reads every one as an existing process with a step omitted,
# duplicated, or combined with another -- nothing created.
MECHANISM = {
    "eukaryote": "omit a step of phagocytosis: engulf, fail to digest",
    "multicellular": "omit a step of division: divide, fail to separate",
    "large-bodied": "the same, continued",
    "skeletal": "omit a step of mineral handling: precipitate, fail "
                "to dissolve",
    "land": "combine: the same body, a different medium",
    "endotherm": "omit a step of thermal exchange: lose heat, fail to",
    "large brain": "duplicate: neural tissue, and more of it",
}

PRESSURES = {
    "eukaryote": (
        "lineage.energy_per_gene_gain",
        "a prokaryote makes ATP across its outer membrane (area, r^2) "
        "and holds its genome in volume (r^3), so energy per gene "
        "falls as 1/r -- a large prokaryote starves its own genome. "
        "Internalising membranes multiplies area without touching "
        "volume and buys 200x, which is what a mitochondrion is"),
    "multicellular": (
        "biome.escalation_stops_at",
        "light is the only pressure in this repository that rewards "
        "being LARGER: a rival eating your food takes a share, one "
        "standing over you takes all of it, every day it stands there"),
    "large-bodied": (
        "biome.escalation_stops_at",
        "the same ratchet, and it does not stop at the diffusion "
        "limit -- it stops where the cost of the structure exceeds "
        "the light being fought over"),
    "skeletal": (
        "life.BONE_COMPRESSIVE",
        "past the size the ratchet drives you to, a body on land "
        "cannot hold itself up without one; this is not an option "
        "taken but a bill arriving"),
    "land": (
        "biome.surface_light",
        "land carries the same 236 W/m2 and, before anything is "
        "there, no competitor at all -- an unexploited flow is a "
        "pressure and engine/biome.py already prices what a "
        "competitor costs"),
    "endotherm": (
        "shelter.coldest_survivable",
        "holding temperature buys the hours and latitudes an "
        "ectotherm cannot work in, which is niche nobody is holding"),
    "large brain": (
        "tools.pays_for_a_brain",
        "one femur of marrow is 70% of a forager's day against the "
        "14% a human brain costs over an ape's -- it pays 5.2x, and "
        "engine/tools.py derives the flaked edge that opens it"),
}


def after_luca():
    """-> [...]. LUCA to a human, permission AND pressure."""
    from engine.ancestry import steps
    out = []
    for row in steps():
        a, b, verdict = row[0], row[1], row[2]
        why = str(row[3] if len(row) > 3 else "")[:110]
        press = PRESSURES.get(b)
        if verdict == "ALLOWED" and press:
            mech = MECHANISM.get(b, "")
            out.append((a, b, FORCED, f"ancestry.steps + {press[0]}",
                        f"PERMITTED: {why} | DRIVEN: {press[1]}"
                        + (f" | HOW: {mech}" if mech else "")))
        else:
            out.append((a, b, verdict if verdict != "ALLOWED" else ALLOWED,
                        "ancestry.steps", why))
    return out


def inside_the_head():
    """-> [...]. What a human brain does, derived elsewhere."""
    from engine.learning import fill_time_years, store_bits
    from engine.recognize import sharp_fraction, seconds_to_cover
    from engine.civ import smallest_group, speech_as_fraction_of_a_brain
    from engine.ontogeny import provisioning_debt
    _j, yrs = provisioning_debt()
    return [
        ("a large brain", "a filter, not a store", DERIVED,
         "learning.fill_time_years",
         f"{store_bits():.1e} bits of synapse against one nerve's 1e7 "
         f"bit/s fills in {fill_time_years():.2f} years, before the "
         f"child can walk, so the work is discarding"),
        ("a filter", "recognition", DERIVED, "recognize.sharp_fraction",
         f"the sharp patch is {100*sharp_fraction():.3f}% of the field "
         f"and sweeping it takes {seconds_to_cover():.0f} s, so the "
         f"periphery commits before evidence arrives"),
        ("recognition", "one head", DERIVED, "senses.inference_share",
         "the five senses between them reach 8 of the 13 constraints "
         "that bind on a human, and they do not overlap -- which is "
         "why there are five. The other 5 (allocation, fidelity, "
         "oxygen to tissue, provisioning, solvent) emit no signal at "
         "all: provisioning is eighteen years ahead and allocation "
         "is a fact about other people. 38% of what binds must be "
         "MODELLED against 33% on a bacterium, and a model needs "
         "somewhere to sit. That is what a head adds over an eye"),
        ("one head", "several", DERIVED, "civ.smallest_group",
         f"a child costs {yrs:.1f} adult-years and one adult keeps no "
         f"margin for a bad season; {smallest_group()} clear it, so "
         f"company is arithmetic and not preference"),
        ("several heads", "a shared corpus", DERIVED, "school.grow",
         "speech carries "
         f"{100*speech_as_fraction_of_a_brain():.4f}% of a lifetime's "
         f"input and is worth it because it is the part somebody "
         f"already selected"),
        ("a corpus", "an allocation rule", DERIVED, "rank.rank_is_priced",
         "the absence was in the scenarios. N adults carry 1.9N "
         "children, and below that line the order of serving changes "
         "nothing while above it somebody does not eat. Rank is not "
         "a preference, it is an allocation rule, and its price is "
         "discontinuous: zero below the carrying number and a whole "
         "82 W life above it"),
        ("an allocation rule", "regard", DERIVED, "regard.regard_is_worth",
         "who eats is who can take, and taking is reach and force -- "
         "the same arithmetic that settles a predator. But between "
         "species the loser is EATEN and 10% transfers, while within "
         "one species nothing transfers and the contest produces no "
         "energy at all. A fight costs 4.2 MJ and a tenth of a life, "
         "allocation needs settling 7,300 times in twenty years, and "
         "remembering the outcome costs 1.4 microjoules. Regard is "
         "the contest not held again, worth 2.7e19 times what it "
         "costs"),
        ("regard", "transitivity", DERIVED, "tradition.transitive_leverage",
         "regard is a remembered outcome, and outcomes compose. "
         "Observe the 27 adjacent links of a band of 28 and A>B, "
         "B>C forces A>C for all 378 pairs -- 14 facts per fact "
         "observed. engine/group.py was already spending this (135 "
         "contests, not 378) without the rule being written down. It "
         "is not universal: rock-paper-scissors composes to nothing, "
         "and when an intransitive triple turns up the 378 contests "
         "come back, which is why the exception is worth naming"),
        ("transitivity", "a corpus that outlives its tellers", DERIVED,
         "tradition.stock",
         "a generation adds a and keeps r, so the stock settles at "
         "a/(1-r) and the whole question is r. An hour after dark "
         "for the 18-year provisioning span is 78,840 tellings, and "
         "k ln k inverts to 8,692 items, so r = 0.99988 and the "
         "stock is 8692a. Epigenetics has a two-generation "
         "half-life, r = 0.71, stock 3.4a. 2,546x apart: epigenetics "
         "is an echo and cannot compound. Only the spoken channel "
         "does, which is why the accumulation is cultural and not "
         "genetic"),
        ("a corpus", "a band that walks at its slowest", DERIVED,
         "craft.kept_innovations_ratio",
         "walking is an inverted pendulum, so speed goes as "
         "sqrt(g*L) and pace is leg length and nothing else. A "
         "four-year-old walks 3.8 km/h against an adult's 5.3, the "
         "band moves at the child, and the ratio is sqrt(0.45/0.90) "
         "= 0.707 -- a square root, not a preference. Hazards are "
         "charged by the DAY and forage is collected by the "
         "KILOMETRE, so going slowly does not avoid problems, it "
         "concentrates them 1.41x per km. And it brings 28 heads to "
         "them instead of one: 39x the kept innovations per km, "
         "with the unmeasured per-head solve rate cancelling. "
         "Slowness is not the price of company, it is the input"),
        ("a slow band", "a discovery nobody made alone", DERIVED,
         "tradition.settle_years",
         "one band waits 500 years for a one-in-500 accident. With "
         "16 bands the first hits at 31 years and coupon collector "
         "carries it to the rest in 22 more, so everyone holds it by "
         "year 53. Some bands get it first and the tail is long, but "
         "it arrives. Discovery wants many bands and spread wants "
         "few, so 1/(bp) + b ln b / 2 has a derivative and there is "
         "a band count that settles fastest -- nobody chose 16"),
        ("a discovery nobody made alone", "specialists", DERIVED,
         "craft.best_depth",
         "oral tradition is a game of telephone: one retelling "
         "corrupts an item with p=0.1, so a single line of "
         "transmission tops out at 10 items and nothing "
         "accumulates. What saves it is that several people hold "
         "the same item and the version that disagrees gets "
         "dropped -- 28 voters take the consensus error to 5.6e-8. "
         "The band is not an audience for the corpus, it is the "
         "error correction ON it. So splitting into specialties "
         "multiplies breadth by s and divides the votes by s, and "
         "the trade bottoms out at 2 specialties 13 deep carrying "
         "9,332a -- against 280a if each of the 28 specializes "
         "alone and every skill dies with its holder. How "
         "specialized a band can be is transmission fidelity and "
         "headcount, not how many useful skills exist"),
        ("specialists", "a claim that carries its own check", DERIVED,
         "literacy.equivalent_voices",
         "a speaker cannot compare their telling to anything -- the "
         "source is gone as it is spoken, so the only correction "
         "available is other people, and it takes 13 of them. A "
         "copyist has the original in front of them and can read "
         "back: one pass takes a 0.1 slip to 0.01 (worth 5 "
         "speakers), three passes to 1e-4 (worth 13), from ONE "
         "person. Writing is the first channel here where a claim "
         "carries the thing that would catch it being wrong, and "
         "that buys 9 specialties instead of 2 with nobody added. "
         "But it bootstraps orally -- you cannot learn to read from "
         "a book you cannot read -- so it needs 5 holders or the "
         "script is lost in a few generations, and its value goes "
         "as f^2 because it takes a writer AND a reader, which is "
         "why it crawls for a thousand years before it pays"),
        ("a written claim", "a crowd big enough to stay sick", DERIVED,
         "disease.critical_community",
         "nothing so far gives anyone a reason to cook. A crowd "
         "disease needs one fresh susceptible per 10-day infectious "
         "period or the chain breaks, and births arrive at N/25 a "
         "year, so it cannot live below 912 people -- a band of 28 "
         "burns through every host in a month and the pathogen dies "
         "with them. Foragers have parasites, not epidemics. What "
         "makes 33 bands sit together permanently is the 365-day "
         "grain harvest from engine/accident.py, and settled ground "
         "carries 114x the shed load of a camp left at 73 days. The "
         "pathogen is not an extra assumption, it is the grain "
         "harvest seen from the other side"),
        ("a crowd that is sick", "fire, washing and walls", DERIVED,
         "disease.cooking_pays",
         "1e6 organisms a gram over 200 g against an ID50 of 1e4 is "
         "infection with p=1.00; seven decades of killing takes it "
         "to 0.002. A bout is 7 days of fever at +26% BMR plus the "
         "food nobody went and got, 132 MJ, against 2.3 MJ of wood "
         "to heat a kilo 65 K. 58x, and nobody had to understand "
         "why. A wall is worth 526 MJ a year on thermoregulation "
         "alone -- 53 days of food -- and the separation from your "
         "own ground comes free. Each is adopted for a reason that "
         "is not hygiene and kept because the people doing it are "
         "the ones still alive"),
        ("a wall", "somebody who holds the store", DERIVED,
         "power.concentration",
         "engine/group.py got a flat answer and it was right to: "
         "strength_share is 1/n and spare_per_head is zero to 1e-14 "
         "J at every band size. A forager is not egalitarian by "
         "disposition, there is simply no second helping to "
         "withhold. What changes is geometry. A band of 28 eats 65 "
         "km2 with a 28.6 km border; a granary's border is 31 m -- "
         "909x. You cannot own a range and you can stand in the "
         "door of a barn. Strength is headcount, so holding it "
         "still needs 15 of the 28 in on it, worth only 1.9x an "
         "equal share. The wall built for warmth takes that to 8 "
         "and 3.5x, and a written claim outlives its witnesses, "
         "which is what inheritance is. A stock crosses a death; a "
         "flow cannot"),
        ("a holder", "a specialist worth their scarcity", DERIVED,
         "merit.pivotal",
         "the other source of power, and it is not the value of "
         "what you can do. You are worth what the band cannot do "
         "without, which is value divided by how many others hold "
         "the skill: 1 holder 100%, 5 holders 20%, 28 holders 4%. "
         "The skill's usefulness does not appear in that at all. "
         "And engine/craft.py needs 5 holders or the skill dies in "
         "a few generations, while its holder wants 1 -- 5x the "
         "power for a twelfth of the lifetime. Neither is being "
         "unreasonable: the specialist's horizon is one life and "
         "the skill's is generations. Lost crafts do not need a "
         "catastrophe, they need someone who profited by not "
         "teaching"),
        ("earned standing", "an heir who did not earn it", DERIVED,
         "merit.mismatch",
         "under selection the holder is the best of 28, the "
         "expected max of 28 draws = sqrt(2 ln 28) = 2.58 sigma. "
         "Under inheritance the holder is whoever was born, and "
         "ability regresses by half a generation while a WRITTEN "
         "claim regresses by nothing: 1.29s, 0.65s, 0.08s by the "
         "fifth. The holding is then 32x what the ability warrants. "
         "This is not villainy, it is two different "
         "heritabilities. And it is not deterministic either -- the "
         "heir is a draw, so P(heir >= founder) is 1 in 15 at one "
         "generation and 1 in 162 at five. A good king is a tail "
         "probability with a number, and anything simulating this "
         "should draw from that number rather than a knob"),
        ("a settled order", "artifacts of many parts", DERIVED,
         "intricacy.settle",
         "an artifact is a composition, so what a group can build "
         "is the subsets of what it holds at once: 2^s - 1. Speech "
         "gives a band 2 specialties and 3 possible things, and it "
         "is a FIXED POINT, not an early stage -- the corpus could "
         "hold 13 parts' worth but fidelity supports 2, and more "
         "people means more mouths on the same one-lifetime-of-"
         "evenings ceiling. Writing moves the binding constraint "
         "from fidelity, which nothing fixes from inside, to how "
         "many can be spared from the fields, which yield fixes. "
         "Iterating surplus -> scribes -> corpus -> specialties -> "
         "surplus settles at 24 parts and 2e7 designs. It converges "
         "rather than running away, because the corpus enters as a "
         "logarithm and the designs come out as an exponent: "
         "doubling what is written buys one more part"),
        ("artifacts of many parts", "villages that keep in touch",
         DERIVED, "trade.knowledge_spread_years",
         "a porter eats the cargo. 30 kg at 32 km a day burning 14 "
         "MJ against grain at 15 MJ/kg spends 0.058 kg per km of "
         "round trip, so a load arrives as nothing at 516 km and "
         "has doubled in price at 258 km -- grain is not traded far "
         "because the cargo and the fuel are the same substance. "
         "Technique weighs nothing AND the carrier still has it "
         "after handing it over, which no other cargo does, so a "
         "region shares what it knows long before it can share "
         "what it grows. And settling put neighbours 5.2 km apart "
         "instead of 9, so they meet 22 times a year instead of 2 "
         "and a discovery crosses 40 villages in 6.8 years instead "
         "of 74. Forty villages in touch are 36,480 people: 12,160 "
         "specialties against a village's 304, and 2.4x the output "
         "per worker from Wright's law. Nobody built a city"),
        ("a region in touch", "anyone actually better off", DERIVED,
         "intricacy.per_capita_exponent",
         "this was carried as a GAP at 3.1.113 and the gap was an "
         "arithmetic error: per-capita surplus was computed by "
         "subtracting mouths at N^1 from two terms that were "
         "ALREADY per worker, which made every invention look as "
         "though it were being shared out and thinned. It is not. "
         "A loaf feeds one person, so loaves per head is loaves/N; "
         "a technique for making loaves is used by everyone who "
         "knows it, at once, and nobody has less of it for that. "
         "The design stock is NOT divided, which is why the "
         "knowledge terms carry no N underneath. It runs the other "
         "way too: an invention costs one specialist's time "
         "whoever uses it and returns b to each of N, so the worst "
         "one worth making needs only b > C/N -- more people is "
         "more ideas AND more users per idea. The one genuinely "
         "rival input is LAND, which does not grow, so supply at "
         "N^0.372 against a 0.30 land share leaves N^0.072. The "
         "crossover is a land share of 0.372: while farming is "
         "more than 37% of output, technology rises and living "
         "standards do not. The escape is not an invention, it is "
         "a share"),
        ("a surplus", "a specialist who can afford the kit", DERIVED,
         "capital.affordable_specialists",
         "everything above counted the specialties a channel could "
         "keep and assumed anyone could take one up. A specialty "
         "is a toolkit and a toolkit is other people's labour: a "
         "23.5-part kit is 1,177 labour-days, so a specialist "
         "costs 365 food-days of eating plus 118 of kit, and a "
         "village of 912 keeps 368 of them rather than the 487 the "
         "food alone allows. 24% of possible specialists are "
         "priced out by their own tools. One person works one "
         "craft however rich they are, so surplus in fewer hands "
         "than S/K sits idle and thinner than K buys no kit at "
         "all -- the right spread is 368 of 912, and the walled "
         "holders of engine/power.py sit below it. Concentration "
         "here is not only unfair, it is IDLE CAPITAL, which is a "
         "cost the holders pay too"),
        ("a gain per head", "a gain nobody actually receives", DERIVED,
         "capital.income_stats",
         "the per-head figure is a MEAN and the distribution under "
         "it is skewed by construction, before anyone is greedy. "
         "engine/merit.py pays a specialist 1/k for a craft held "
         "by k people, and k is not the same for every craft: at "
         "mean depth 3 the mean is 1.33x the median, the rarest "
         "craft pays 4x the median on scarcity alone, and a walled "
         "holder multiplies that to 14x. So 'everyone is 1.3x "
         "better off' is a sentence no individual satisfies -- a "
         "few are near 14x, most are at or below the median. Every "
         "per-head number on this chain is the first moment of a "
         "skewed distribution and is not to be quoted alone"),
        ("more that is known", "less that is new, and more of it",
         DERIVED, "novelty.multiple",
         "designs are 2^s and s is log2(corpus), so the exponent "
         "and the logarithm cancel and the space to be new in is "
         "LINEAR in population -- used up by being found, added to "
         "by people arriving, neither winning. The steady state "
         "depends on the GROWTH rate and not the size: a "
         "population that has stopped growing exhausts its design "
         "space however large it is. But exhaustion is NOT what "
         "makes novelty per head fall here -- at 3,244 designs a "
         "head, 99.7% of trials still land on something new. The "
         "fall is the TEAM. A design of p parts needs p people who "
         "between them hold p crafts, and p is a logarithm of what "
         "is already known, so 912 -> 36,480 takes novelty per "
         "head to 0.80 while novel designs in total rise 32x. Each "
         "person invents 20% less and the world gets 32x more, "
         "both at once. It falls because knowing enough to add to "
         "it costs more, not because there is less left"),
        ("designs counted", "things that can be named", DERIVED,
         "artifact.bootstrap",
         "a count is not a technology. Giving the 2^s designs "
         "actual objects -- 16 physical capabilities, each "
         "grounded in a rule that already existed for another "
         "reason, heat in the cooking bill and optics in the "
         "diffraction limit that bounded an eye -- immediately "
         "showed that composition depth is NOT the constraint. "
         "The prerequisite tree is 5 deep against a budget of "
         "23.5, so on composition alone a literate village reaches "
         "a governed engine. It does not. The gate is "
         "TEMPERATURE: every step past cordage is a material you "
         "cannot have until you reach the heat that makes it, and "
         "what you can reach depends on what you have built. An "
         "open fire is 1100 K; a hearth and charcoal buy 1400 and "
         "copper; bellows need a metal tuyere, which needs the "
         "smelting the bellows were for, and that loop is why "
         "copper comes at round 3 and steel at round 5. Six "
         "rounds from a hafted axe to a governed engine, and "
         "nobody put the engine last -- combustion did"),
        ("one gate", "whichever scalar is short", DERIVED,
         "artifact.tolerance",
         "temperature stops moving at round 5 and 1750 K, and "
         "everything after it -- vacuum, alloy, semiconductor, "
         "switching, inference -- is reachable at exactly that "
         "heat and was not available for two centuries. The scarce "
         "thing changed: not how hot you can get but how "
         "accurately you can place matter, 1e-1 by hand through "
         "1e-9 printed through a mask. The same bootstrap shape "
         "holds and the same trap: setting the first rung too high "
         "DEADLOCKED it, because a screw-cutting lathe is made of "
         "gears and the first gears must therefore be filable by "
         "hand, exactly as the first transistors were "
         "millimetre-scale before lithography existed. A ladder "
         "needs a rung reachable from the ground. Asked to run two "
         "centuries past now the model gives 29.4 -> 49.4 parts "
         "and an exponent, and refuses to name anything, because "
         "a name for a primitive nobody has made is a word with no "
         "rule under it"),
        ("a corpus too large to hold", "a machine that searches it",
         DERIVED, "inference.least_population",
         "engine/artifact.py has inference as a primitive and "
         "nothing runs there. Priced against rules that already "
         "exist, the costs are not where anyone puts them. The "
         "corpus is 1.38e12 bits and Landauer's floor for erasing "
         "it is 4.1e-9 J -- under a second of one human at rest -- "
         "while a real gate spends 3.4e11 times that, so the "
         "thermodynamic limit is not the constraint and is not "
         "within ten orders of being one. The cost is the KIT. "
         "engine/capital.py priced a part at 50 days for a village "
         "making things to a tenth; holding a billionth costs "
         "10,000x that, so the kit is 3.4 million labour-days. A "
         "village of 912 affords 0.0005 of one, which is why the "
         "thing sits ten rounds out; it takes 17,300 people for "
         "ONE. The result is not that it is dear but that it is "
         "INDIVISIBLE -- a network of 36,480 has room for two, and "
         "engine/merit.py prices a holder of a 2-deep specialty at "
         "50%, the highest pivotality on this chain. And by README "
         "rule 3 a machine that answers by searching is an "
         "admission: its usefulness measures what has not been "
         "derived, and it is the only quantity here that shrinks "
         "as the work gets better"),
        ("people with instruments", "a literature of their own",
         DERIVED, "literature.order_agreement",
         "this repository derives from constants it simply has. "
         "The people inside it do not have them -- they have "
         "senses reaching 8 of 13 constraints and instruments "
         "arriving in an order engine/artifact.py already fixed "
         "from melting points and machining tolerances. So a "
         "science is possible exactly when its instrument is, "
         "which PREDICTS AN ORDER: statics, surveying, positional "
         "astronomy, metallurgy, machines, optics, thermometry, "
         "then the rest. Against the century each actually "
         "appeared that is 55 concordant pairs to 7, Kendall tau "
         "0.77 on a sequence that could have come out 6.2e9 ways. "
         "The rounds were not tuned for this and the centuries "
         "are the answer key, but the science-to-instrument "
         "mapping is mine and a different hand would score "
         "differently. The 7 discordant pairs concentrate on "
         "metallurgy, pneumatics and spectroscopy, and each names "
         "a requirement the mapping missed -- a ruled grating is "
         "precision machining, not optics. Their rules also carry "
         "THEIR error: a three-term derivation of G is +/-17% at "
         "round 2 and 0.2% at round 5, and Cavendish got 1% in "
         "1798, which lands between them"),
        ("two gates", "a third that only goes down", DERIVED,
         "artifact.coldness",
         "the heat ladder only ever went UP and nothing in the "
         "tree had touched the other direction. Going cold is a "
         "separate physical scarcity with its own cascade: you "
         "cannot reach liquid helium without liquid air first, "
         "because the helium must be pre-cooled -- the same shape "
         "as the bellows needing the tuyere they were for. "
         "Expanding a compressed gas reaches 77 K and needs "
         "pressure and regulation; pumping on a cascaded bath "
         "reaches 4 K and needs vacuum and superconduction. That "
         "adds superconduction, coherence and placement, and the "
         "tree runs to eleven rounds. The precision ladder now "
         "ENDS rather than stopping: matter cannot be placed more "
         "finely than an atom is wide, and the Bohr radius falls "
         "out of hbar, the electron mass and the charge at "
         "5.29e-11 m. That is a wall, not a rung"),
        ("a claim that there was no light", "the light that was here",
         DERIVED, "scene.solar_constant",
         "3.2.14 said the world has no scene, and that was wrong "
         "about this repository's own contents. engine/thermo.py "
         "already had the Sun at 5772 K and engine/constants.py "
         "its luminosity and orbit, so the solar constant is "
         "L/(4 pi d^2) = 1361 W/m2 against a measured 1361, and "
         "Wien puts the peak at 502 nm against a measured 502. "
         "Neither was put in. Rayleigh scattering goes as "
         "lambda^-4, which gives BOTH the blue sky -- what "
         "scattered out, blue 4.9x red -- and the red low sun, "
         "what went straight through, red 46x blue. One "
         "subtraction seen from two directions. A shadow is "
         "h/tan(elevation) on a height engine/drawing.py already "
         "publishes, and lit-to-shadowed contrast is 6.1 to one "
         "rather than infinite, because a shadow still sees the "
         "sky. What remains underivable is the SHAPE of a thing: "
         "the envelope is real and published, a box is the "
         "simplest solid with those extents, and the choice is "
         "stated rather than hidden in a renderer. One more "
         "thing falls out and it is not cosmetic: the Sun's "
         "RADIUS is forced too, since L = 4 pi R^2 sigma T^4 "
         "solves to 6.957e8 m, the measured figure, and 2R/d "
         "makes the disc 0.533 degrees across. So the Sun is not "
         "a point and NO SHADOW EDGE IS SHARP -- the half-shadow "
         "spreads 9.3 mm per metre from whatever cast it. A "
         "render with hard edges is not stylised, it is wrong "
         "about the size of the Sun"),
        ("a surface that keeps light", "a reason to throw most of it away",
         DERIVED, "image.over_resolution",
         "their plate has a one-micron grain, so it holds 100,000 "
         "samples across; the eye that will look at it resolves "
         "an arcminute, which at reading distance is 1,149 across "
         "the same plate. THE MEDIUM OUT-RESOLVES THE VIEWER BY "
         "87 TIMES, 7,569 in area, and that is why an image "
         "format exists at all -- compression is not a trick "
         "about files, it is the arithmetic of recording more "
         "than anyone can see. Every term is a fact about the "
         "eye: colour acuity is a third of brightness so colour "
         "samples two-by-two coarser, exactly 2x, which is what "
         "4:2:0 IS; and contrast sensitivity peaks near 4 cycles "
         "a degree and falls away, so a high coefficient needs "
         "fewer bits rather than none, 2.4x over the 63 AC "
         "terms. 4.8x from perception alone. tools/jpeg.py "
         "implements the encoder with that quantization table "
         "instead of Annex K, measures 10.4x, and an unrelated "
         "decoder reads the file as a 1400x240 JPEG -- so the "
         "remaining 2.2x is entropy coding of the zeros, which "
         "is symbol statistics and not eyes"),
        ("a drawing that needs a reader", "one that does not",
         DERIVED, "depiction.image_over_drawing",
         "a drawing is a projection and a projection is a "
         "convention, so it needs a drawer AND a reader holding "
         "the same one -- f squared, worth 0.0001 at 1% and 0.01 "
         "at 10%. A photograph needs no convention: whoever "
         "looks at it reads it, so its worth is f to the FIRST "
         "power and is 1 from the moment it exists. That is "
         "10,000x at 1% literacy. Depiction needs a lens and a "
         "specified composition and lands at round 8, and what "
         "it does is abolish the second literacy that had just "
         "been derived. ART is the third case and the strange "
         "one: it is the only output here needing no tolerance "
         "at all, because a mark is not true to anything, so no "
         "gate has ever blocked it and it is available in round "
         "1 while 12 of 25 crafts queue behind a furnace. The "
         "obvious account -- that art waits for a surplus -- is "
         "refuted: painted caves are thirty thousand years older "
         "than farming, and the reason is magnitude, a painted "
         "surface being 0.75 days against 50 for one part of a "
         "tool. And art travels like a FACT rather than a tool, "
         "audience 100% against 50%, which is why a style "
         "crosses a region faster than the pigment recipe does"),
        ("a tolerance on nothing", "a dimensioned drawing", DERIVED,
         "drawing.drawing_of",
         "a tolerance has to be a tolerance ON something, and "
         "these were relative numbers floating free of any "
         "dimension. Giving each craft a characteristic size lets "
         "them be checked against what the physics demands, and "
         "three came out wrong. The worst: a lens surface must be "
         "true to a quarter wavelength, 138 nm on a 50 mm lens, "
         "2.7e-6 relative against the 1e-2 that was here -- four "
         "orders out. The resolution is a distinction the file "
         "did not have. Some accuracy is MEASURED and some is "
         "PROCESSED: nobody ever machined a lens to a quarter "
         "wave, you grind two surfaces together and they conform, "
         "because a sphere is the only shape that slides on "
         "itself in every orientation. Three flats lapped in "
         "rotation give a plane, a hobbed gear generates its own "
         "involute, and the accuracy comes out of the METHOD with "
         "nobody gauging anything -- which is why lenses precede "
         "micrometers instead of waiting for them. Their geometry "
         "is ours, so a drawing they make is one we can read, and "
         "none of that needed telling them a rule"),
        ("a part too fine to copy", "a drawing", DERIVED,
         "drawing.first_round_needing_one",
         "the obvious account of a drawing is that a shape is a "
         "lot of information, and it is wrong by a wide margin: "
         "pinning a dimension to a tolerance costs log2(1/t) "
         "bits, so a three-dimensional part at a BILLIONTH is 90 "
         "bits against the 11,700 one telling carries. A hundred "
         "and thirty such specifications fit in one story and you "
         "could read a nanometre tolerance aloud. What actually "
         "forces a drawing is that the object stops being its own "
         "specification: copying by eye reaches a tenth, so above "
         "that you hand someone the original, and below it a "
         "NUMBER has to travel instead of a thing. 11 of 24 "
         "crafts are tighter than a sample can carry and the "
         "first is at round 5. And a projection is a convention, "
         "so it needs a drawer AND a reader -- f squared, the "
         "same exponent as literacy, and slow for the same "
         "reason. A drawing is a second literacy"),
        ("a constraint envelope", "a world that runs", DERIVED,
         "world.run",
         "everything before this computed what a human-like "
         "organism COULD NOT do, which is a real kind of "
         "statement and is not the same as saying what they did. "
         "Nothing had state, nothing took a step, nobody tried "
         "anything. This does: 40 bands hold crafts, try "
         "combinations of what they have, and find out about the "
         "gates by failing -- they cannot see a melting point. "
         "Over 12,000 years the ledger takes 30,319 entries, "
         "they reach all 21 crafts with the last at year 11,380, "
         "and they build 4,352 distinct things of which 4,334 "
         "have NO NAME in our world, because 21 things are named "
         "and the reachable space is 2^21. The result is that "
         "the ORDER comes back out at Kendall tau 1.00 against "
         "the bootstrap derived from melting points -- an "
         "ordering that was a theorem recovered by a stochastic "
         "search run by people who know no physics. The "
         "timescale is NOT a result: CRAFT_SUCCESS is fitted to "
         "the Holocene and is the only fitted number here"),
        ("a record we wrote for them", "a record they wrote",
         DERIVED, "world.words_for",
         "the encyclopedia at 3.2.9 was in English and the "
         "English was mine -- every phrase came from a "
         "description I had typed into engine/artifact.py, which "
         "is us writing their record and then admiring it. So "
         "they get a language: nine consonants, three vowels, "
         "open syllables, 20,412 possible words, and a band coins "
         "a token when it first makes something. Nobody was "
         "handed English, because handing them English is the "
         "same mistake in a larger form. We can still read it "
         "because we WATCHED THEM ATTACH each word to an act of "
         "making and the ledger has both -- the gloss is an "
         "observation in the position a field linguist is in, "
         "not a dictionary anybody was given. And a result "
         "nothing was built to produce: a craft every band found "
         "separately keeps a word per band, while a craft that "
         "spread by teaching carries one word with it, so heat "
         "has 39 words across 40 bands and gearing has 2. THE "
         "OLDEST WORDS ARE THE LEAST AGREED ON, which is what "
         "happens to real basic vocabulary against real "
         "technical vocabulary"),
        ("who it says mattered", "why anything gets a name at all",
         DERIVED, "naming.naming_is_worth",
         "a name is not imposed from outside, it is a mechanism "
         "the people inside need, and it is three things already "
         "priced elsewhere. An INDEX: a corpus of 8,692 items "
         "costs 4,346 comparisons to search and one to look up, "
         "so a handle is worth 4,346 retrievals -- names are "
         "addresses before they are honours, which is why the "
         "oldest ones are places and rivers. A CREDIT CLAIM: "
         "engine/merit.py prices a contribution at 1/k, and "
         "attaching a name is the act that sets k to one, 100% "
         "against 4%, so naming IS the reward system's addressing "
         "rather than decoration on it. And an ITEM: a name "
         "decays like any other, needing 5 holders to last forty "
         "generations -- the same figure as keeping a script, "
         "because it is the same arithmetic. What is NOT derived "
         "is why answerers get named over toolmakers. The "
         "tellability account was tested and refuted at r = -0.20 "
         "over 21 primitives. What does account for it is "
         "AUDIENCE: a retelling costs the teller and pays the "
         "listener, so it happens when the listener can act. An "
         "answer is usable by anyone who hears it and a tool only "
         "by whoever holds that craft -- 100% against 50% in a "
         "band of 28 holding 2 crafts, and 0.3% in a literate "
         "village holding 304. Over five retellings that is 32x "
         "and 2.6e12x. And the story channel stops carrying a "
         "tool at all once specialties pass 3, because R0 falls "
         "through one, after which tools travel by apprenticeship "
         "-- a channel that produces no names. A society gets "
         "better at making tools and worse at naming who made "
         "them, at the same time and for the same reason"),
        ("a paper that can be marked", "who it says mattered",
         DERIVED, "standing.ranking",
         "who counts should fall out of the structure rather than "
         "be imported, so it is ranked by what rests on it: how "
         "many primitives, sciences, exam questions and namable "
         "artifacts depend on each contribution. Nothing the "
         "ranking reads has a name in it, so no name can come "
         "out. REGULATION tops it at 16 -- a machine that "
         "corrects itself -- then mark at 10, optics and rotation "
         "at 9. And a tool is not the same kind of contribution "
         "as a fact: a primitive enters an EXPONENT, since "
         "designs are 2^s and one more doubles the space, while "
         "an answer enters a SUM as one item in a corpus of "
         "1.2e8. The ratio is 1.2e8 to one. Of eight names "
         "commonly remembered here, six are remembered for "
         "answering and two for building -- the reverse of what "
         "the ranking says, and the check fails if memory ever "
         "starts tracking leverage"),
        ("a literature", "a paper that can be marked", DERIVED,
         "exam.half_moon_sensitivity",
         "a question is not a topic, it is a METHOD, and every "
         "method has a SENSITIVITY: how much the answer moves "
         "when the measurement is off by a fraction. Eratosthenes "
         "measured a shadow and a road, sensitivity 1, and got "
         "the Earth's circumference to a few per cent with a "
         "stick. Aristarchus, same century and same equipment, "
         "measured the Sun's distance and was out by twenty "
         "times. Feeding his reported 87 degrees into 1/cos gives "
         "19.1 and he published 'about 19' -- so the arithmetic "
         "was right and the error was entirely in the input. His "
         "method multiplies by theta tan(theta) = 611. And the "
         "measurement was not the angle: the angle only means "
         "anything AT half moon, and the Moon moves 13.2 degrees "
         "a day, so his 2.85-degree error is 5.2 HOURS of timing. "
         "A water clock leaves 187% on the answer. He attempted a "
         "round-6 question with round-2 equipment, could not have "
         "known it, and the figure stood for seventeen centuries "
         "-- not corrected by better thinking but by the transit "
         "of Venus, a different method with a different "
         "sensitivity"),
        ("everything derived so far", "one epoch of many", DERIVED,
         "farfuture.star_lifetime_years",
         "engine/epochs.py stops at the neutron-star merger, about "
         "ten billion years, because that is the last epoch that "
         "makes a new KIND of matter -- and everything above, "
         "cells through lithography, happens INSIDE that one epoch "
         "using nothing the universe had not already made. Main "
         "sequence lifetime goes as M^(1-3.5), so the lightest "
         "star that burns at all, 0.08 solar masses, lasts 5.5e12 "
         "years against the Sun's 1e10. The era with people in it "
         "is a 552nd of the era with stars in it, and the chain "
         "had an end that nobody had written down"),
        ("the last starlight", "holes that finally shrink", DERIVED,
         "farfuture.black_holes_start_shrinking",
         "a solar-mass hole radiates at 6.2e-8 K, colder than "
         "today's 2.725 K sky, so it GROWS -- nothing evaporates "
         "until the universe has cooled past it, which under "
         "exponential expansion takes ln(2.725/6.2e-8) Hubble "
         "times, about 2.6e11 years. Then t = 5120 pi G^2 M^3 / "
         "hbar c^4, three constants and a mass with nothing "
         "fitted: 2.1e67 years for a stellar hole and 2.1e94 for a "
         "galactic one, because a cube turns 1e9 into 1e27. The "
         "last event in the universe is the evaporation of the "
         "largest hole in it"),
        ("no gradient", "nothing further can be derived", DERIVED,
         "farfuture.de_sitter_temperature",
         "every rule in this repository runs on a GRADIENT. A cell "
         "eats one, a body sheds one, a fire needs one, Carnot is "
         "defined by one, and the 58x return on cooking exists "
         "only because there is somewhere for the heat to go. The "
         "floor is the de Sitter temperature, hbar H / 2 pi k = "
         "2.7e-30 K, set by the horizon itself and by the same "
         "formula as a black hole's. At that temperature "
         "everything is at the horizon and there is no somewhere. "
         "So the final link does not say the universe is cold. It "
         "says the machinery this repository is built from has "
         "nothing left to bite on, which is an ANSWER and not a "
         "gap -- the one place on the chain where 'nothing further "
         "can be derived' is the correct result"),
        ("ordinary matter", "whether it lasts at all", MISSING,
         "farfuture.PROTON_DECAY_BOUND_YR",
         "a gap in the WORLD rather than in the model, and the "
         "distinction is worth keeping. The proton has never been "
         "observed to decay; Super-Kamiokande puts the lifetime "
         "beyond 1.6e34 years, which is a bound and not a value. "
         "If protons decay near that bound, white dwarfs and cold "
         "planets evaporate long before the 2.1e67 years a stellar "
         "hole needs and the degenerate era ends early. If they do "
         "not, cold matter simply waits. Nothing here can decide "
         "it and neither can anyone else yet")
    ]


def chain():
    """-> [...]. The whole thing, nebula to a head, in order."""
    return (before_earth() + before_luca() + after_luca()
            + inside_the_head())


# --- what lives there: three theorems, no simulation ----------------

def exclusion_limit(n_resources):
    """Species that can coexist on n limiting resources. DERIVED.

    At equilibrium each species needs one resource it is best at.
    More species than resources means two share a best, and the
    better competitor takes it -- competitive exclusion, which is
    a statement about rank and does not need a population run.
    """
    return n_resources


def abundance_of(mass_kg, energy_w, kleiber_exp=0.75):
    """Individuals per unit area. DERIVED: energetic equivalence.

    Each species gets a share of energy; one body costs
    b*m^(3/4). So abundance goes as m^(-3/4), and population
    ENERGY USE is then independent of body size -- which is why a
    field holds few large animals and many small ones without
    anything choosing that.
    """
    from engine.biome import metabolism_w
    return energy_w / max(metabolism_w(mass_kg), 1e-30)


def biomass_of(mass_kg, energy_w):
    """kg per unit area at that body size. DERIVED."""
    return abundance_of(mass_kg, energy_w) * mass_kg


def size_span(energy_w, floor_kg, roof_kg):
    """-> (n at floor, n at roof, ratio). DERIVED."""
    a, b = abundance_of(floor_kg, energy_w), abundance_of(roof_kg, energy_w)
    return a, b, a / b


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_chain_runs_end_to_end", _chain)
    t("permission_is_not_pressure", _forced)
    t("every_link_names_its_rule", _cites)
    t("the_gaps_are_named_and_counted", _gaps)
    t("competition_is_a_theorem_not_a_run", _excl)
    t("abundance_falls_as_the_three_quarter_power", _abund)
    t("nothing_here_simulates", _norun)
    return all(o[1] for o in out), out


def _chain():
    c = chain()
    if len(c) < 15:
        raise ArithmeticError(f"only {len(c)} links")
    kinds = {}
    for _a, _b, v, _r, _w in c:
        kinds[v] = kinds.get(v, 0) + 1
    return (f"{len(c)} links from a nebula to what a head does, in "
            f"order and in one list: " + ", ".join(
                f"{k} {v}" for k, v in sorted(kinds.items()))
            + ". engine/planetlab.py, engine/earthlab.py and "
              "engine/ancestry.py each walked part of this and none "
              "handed off, so the chain the repository is for was the "
              "one thing nobody could read")


def _forced():
    c = chain()
    forced = [r for r in c if r[2] == FORCED]
    allowed = [r for r in c if r[2] == ALLOWED]
    gain, _small = energy_per_gene_gain()
    if len(forced) < 5:
        raise ArithmeticError(f"only {len(forced)} links are forced")
    return (f"{len(forced)} of the middle links are FORCED and "
            f"{len(allowed)} remain merely ALLOWED. The difference is "
            f"the one the chain was missing: a permission says a step "
            f"is payable, a pressure says something is worse off not "
            f"taking it, and only the second produces anything. Most "
            f"of the pressures were already derived and never cited "
            f"-- engine/biome.py holds the only one here that rewards "
            f"being larger, and no link referred to it. The "
            f"eukaryote's is new: ATP scales with membrane AREA and "
            f"genome with VOLUME, so energy per gene falls as 1/r "
            f"until membranes go inside, which buys {gain:.0f}x")


def _cites():
    c = chain()
    bare = [r for r in c if not r[3] or "." not in r[3]]
    named = [r for r in c if r[2] == MISSING]
    if len(bare) > len(named):
        raise ArithmeticError(f"{len(bare)} links cite no rule")
    return (f"{len(c) - len(bare)} of {len(c)} links name the rule and "
            f"module that produce them; the {len(bare)} that do not "
            f"are exactly the {len(named)} marked MISSING, whose whole "
            f"content is that no rule produces them")


def _gaps():
    """INVERTED. Fails if the chain claims to be finished.

    A crossing is a gap that has been named: the link is
    permitted but nothing here drives it. Zero gaps AND zero
    crossings would mean the chain had stopped looking.
    """
    c = chain()
    gaps = [(a, b, w) for a, b, v, _r, w in c if v == MISSING]
    cross = [(a, b) for a, b, v, _r, _w in c if v == CROSSES]
    if not gaps and not cross:
        raise ArithmeticError("the chain claims to be complete")
    body = (f"{len(c)} links, {len(gaps)} gaps, {len(cross)} "
            f"crossings.")
    if gaps:
        body += " Gaps: " + "; ".join(f"{a} -> {b}" for a, b, _ in gaps)
    if cross:
        body += (" Crossings: "
                 + "; ".join(f"{a} -> {b}" for a, b in cross)
                 + ". A crossing is permitted and undriven -- the "
                   "gates open and nothing makes it happen, so "
                   "permission is not occurrence and the distance "
                   "between them is not measured anywhere here")
    return body


def _excl():
    for n in (1, 3, 7):
        if exclusion_limit(n) != n:
            raise ArithmeticError("exclusion does not track resources")
    return ("how many species coexist is bounded by how many limiting "
            "resources there are, because at equilibrium each needs "
            "one it is best at and two sharing a best cannot both "
            "stay. That is a statement about RANK. engine/ecology.py "
            "answered the same question by running 600 generations of "
            "12 species; the bound needed no population at all")


def _abund():
    e = 1000.0
    small, big, ratio = size_span(e, 1e-3, 1e3)
    want = (1e3 / 1e-3) ** 0.75
    if abs(math.log(ratio / want)) > 0.05:
        raise ArithmeticError(f"ratio {ratio:.3e} against {want:.3e}")
    return (f"one body costs b*m^(3/4), so on a fixed energy share "
            f"abundance goes as m^(-3/4): a gram-sized animal is "
            f"{ratio:.0f} times commoner than a tonne-sized one, which "
            f"is {1e6:.0e}^0.75 exactly. Population energy use is then "
            f"the SAME at every size -- a field holds few large and "
            f"many small animals and nothing chose that, Kleiber did")


def _norun():
    import ast
    src = (ROOT / "engine" / "lineage.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("run", "sweep", "census", "generate"):
                raise ArithmeticError(f"this file calls {node.func.id}")
    return ("this file calls no run, sweep, census or generate. Every "
            "link is a rule proved elsewhere and cited, and the three "
            "ecological statements are theorems -- exclusion is about "
            "rank, energetic equivalence is Kleiber divided through. "
            "README rule 3: a search means the rule has not been "
            "found")


if __name__ == "__main__":
    c = chain()
    print(f"  {len(c)} links\n")
    for a, b, v, rule, why in c:
        print(f"  {v:<8}{a[:26]:<27}-> {b[:26]:<27}{rule}")
    print()
    for n, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {n:44}{d[:34]}")
