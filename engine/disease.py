"""Why anyone would bother to cook, wash, or build a wall.

Nothing on this chain so far gives a reason to heat food. Cooking
costs fuel and gains nothing a stomach could not eventually manage.
Hygiene costs time. A house costs weeks of work. All three are
answers, and until there is a pathogen there is no question.

So the pathogen is not assumed here, it is DERIVED FROM SETTLING.
A crowd disease needs a supply of new susceptibles or it burns
through its hosts and goes extinct; a band of 28 cannot feed one.
What makes a large permanent aggregation possible is a store that
lasts a year, which engine/accident.py already found is the only
thing that stops a band moving. The same 365-day grain harvest
that makes you stationary is what makes you sick.

Then cooking, washing and walls all price out against the same
illness bill, and each of them is a SKILL -- which lands back on
engine/craft.py, where the number of skills a band can hold is
already at its ceiling.
"""

import math

from engine.tradition import BAND

# --- the pathogen has to be able to persist -------------------------
INFECTIOUS_DAYS = 10.0      # MEASURED-ish, acute crowd infection
GENERATION_YEARS = 25.0

# --- what a bout costs ----------------------------------------------
BMR_MJ_DAY = 7.0            # engine/ontogeny scale, adult at rest
FEVER_UPLIFT = 0.26         # 13% per degree, two degrees
INTAKE_MJ_DAY = 10.0        # forgone, you are not foraging
BOUT_DAYS = 7.0

# --- cooking ---------------------------------------------------------
SPECIFIC_HEAT = 3500.0      # J/kg/K, wet tissue
COOK_RISE_K = 65.0          # 10 C to 75 C
FIRE_EFFICIENCY = 0.10      # CHOSEN, open fire onto a carcass
LOG_KILL = 7.0              # 70 C held two minutes, vegetative cells
RAW_LOAD = 1e6              # organisms per gram, spoiling meat
PORTION_G = 200.0
ID50 = 1e4                  # organisms for even odds

# --- the house --------------------------------------------------------
CONDUCTANCE_W_K = 5.0       # clothed adult
SHELTER_GAIN_K = 10.0       # CHOSEN, inside against outside at night
NIGHT_S = 8.0 * 3600.0

# --- the ground -------------------------------------------------------
PERSISTENCE_DAYS = 365.0    # helminth eggs, MEASURED-ish


def critical_community():
    """Smallest population a crowd disease can live in. DERIVED.

    The pathogen must find one fresh susceptible per infectious
    period or its chain breaks. Births arrive at N/GENERATION a
    year, so N/GENERATION >= 365/INFECTIOUS.
    """
    return GENERATION_YEARS * 365.0 / INFECTIOUS_DAYS


def bands_needed():
    """How many bands must aggregate to hold one. DERIVED."""
    return critical_community() / BAND


def contacts(n):
    """Pairs that can pass it. The n(n-1)/2 again. DERIVED."""
    return n * (n - 1) / 2.0


def bout_cost_mj():
    """What one illness costs. DERIVED."""
    return BOUT_DAYS * (BMR_MJ_DAY * (1 + FEVER_UPLIFT) + INTAKE_MJ_DAY)


def infection_chance(log_kill=0.0):
    """Dose-response after `log_kill` decades of killing. DERIVED."""
    dose = RAW_LOAD * PORTION_G / (10.0 ** log_kill)
    return 1.0 - math.exp(-dose / ID50)


def cook_cost_mj(kg=1.0):
    """Wood energy to bring a portion to temperature. DERIVED."""
    return kg * SPECIFIC_HEAT * COOK_RISE_K / FIRE_EFFICIENCY / 1e6


def cooking_pays():
    """-> (saving MJ, cost MJ, ratio). DERIVED."""
    avoided = (infection_chance(0.0) - infection_chance(LOG_KILL))
    saving = avoided * bout_cost_mj()
    return saving, cook_cost_mj(), saving / cook_cost_mj()


def house_pays_mj_year():
    """What a wall saves in thermoregulation alone. DERIVED."""
    return CONDUCTANCE_W_K * SHELTER_GAIN_K * NIGHT_S * 365.0 / 1e6


def ground_load(n, residence_days):
    """Contamination underfoot. DERIVED.

    Shedding accumulates while you stay and decays over
    PERSISTENCE_DAYS, so a band that leaves never reaches the
    steady state a settlement sits in.
    """
    return n * PERSISTENCE_DAYS * (
        1.0 - math.exp(-residence_days / PERSISTENCE_DAYS))


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_band_is_too_small_to_hold_a_crowd_disease", _small)
    t("settling_is_what_invents_the_disease", _settle)
    t("cooking_pays_for_itself_fifty_times_over", _cook)
    t("a_wall_pays_before_anyone_mentions_disease", _house)
    t("every_answer_to_it_is_a_skill_and_the_band_is_full", _full)
    return all(x for _, x, _ in res), res


def _small():
    n, b = critical_community(), bands_needed()
    if n <= BAND:
        raise ArithmeticError(f"{n}")
    return (f"a crowd disease with a {INFECTIOUS_DAYS:.0f}-day "
            f"infectious period needs one fresh susceptible per "
            f"period or the chain breaks, and births arrive at "
            f"N/{GENERATION_YEARS:.0f} a year -- so it cannot live "
            f"below {n:.0f} people. A band of {BAND} burns through "
            f"every host in a month and the pathogen goes extinct "
            f"with them. It takes {b:.0f} bands in permanent contact. "
            f"Foragers do not have epidemics; they have parasites "
            f"and whatever the animals gave them")


def _settle():
    from engine.accident import STORES, settling_threshold
    grain, meat = STORES["a grain harvest"], STORES["dried meat"]
    settled = ground_load(critical_community(), grain)
    mobile = ground_load(BAND, settling_threshold())
    if settled <= mobile:
        raise ArithmeticError(f"{settled} vs {mobile}")
    return (f"engine/accident.py found that only a "
            f"{grain:.0f}-day store beats the "
            f"{settling_threshold():.0f}-day threshold for staying "
            f"put. Staying put is the whole mechanism: shedding "
            f"accumulates toward a steady state over "
            f"{PERSISTENCE_DAYS:.0f} days, and a band that leaves at "
            f"{settling_threshold():.0f} days never gets near it. "
            f"Settled ground carries {settled/mobile:.0f}x the load "
            f"of a camp, and the aggregation that a year's grain "
            f"allows finally clears the {critical_community():.0f} "
            f"floor. The pathogen is not an extra assumption. It is "
            f"the grain harvest, seen from the other side")


def _cook():
    save, cost, ratio = cooking_pays()
    if ratio < 10:
        raise ArithmeticError(f"{ratio}")
    return (f"raw: {RAW_LOAD:.0e}/g over {PORTION_G:.0f} g against an "
            f"ID50 of {ID50:.0e} is infection with p="
            f"{infection_chance(0.0):.3f}. {LOG_KILL:.0f} decades of "
            f"killing takes it to p={infection_chance(LOG_KILL):.4f}. "
            f"A bout is {BOUT_DAYS:.0f} days of fever at "
            f"+{100*FEVER_UPLIFT:.0f}% BMR plus the food you did not "
            f"go and get: {bout_cost_mj():.0f} MJ. Heating a kilo "
            f"{COOK_RISE_K:.0f} K on a {100*FIRE_EFFICIENCY:.0f}% "
            f"efficient fire costs {cost:.1f} MJ of wood. "
            f"{ratio:.0f}x. Nobody had to understand why")


def _house():
    yr = house_pays_mj_year()
    days = yr / INTAKE_MJ_DAY
    if days < 10:
        raise ArithmeticError(f"{days}")
    return (f"a wall is worth {yr:.0f} MJ a year in thermoregulation "
            f"alone -- {CONDUCTANCE_W_K:.0f} W/K across "
            f"{SHELTER_GAIN_K:.0f} K for {NIGHT_S/3600:.0f} hours, "
            f"365 nights -- which is {days:.0f} days of food. It "
            f"pays on heat before anyone mentions disease, and the "
            f"separation from your own ground comes free with it. "
            f"That is the shape of all three: the hygienic thing is "
            f"adopted for a reason that is not hygiene, and keeps "
            f"being done because the people who do it are the ones "
            f"still alive")


def _full():
    from engine.craft import best_depth
    from engine.literacy import written_depth
    spoken = best_depth()[1]
    written = written_depth(2)[1]
    answers = 3                       # fire, washing, walls
    if spoken >= answers:
        raise ArithmeticError(f"{spoken} >= {answers}")
    return (f"fire, washing and walls are {answers} skills, and each "
            f"has to be held and handed on like any other. "
            f"engine/craft.py says a band of {BAND} bottoms out at "
            f"{spoken} specialties before fidelity eats the "
            f"breadth -- it cannot hold the answers to the problem "
            f"that settling created. Written, the same {BAND} hold "
            f"{written}. So the disease does not just follow the "
            f"grain; it puts the load on the channel, and the "
            f"channel was already at its ceiling. That is a "
            f"pressure, not a gap")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
