"""
Plants, the things that eat them, and a test for intelligence.

Every previous run failed to produce size because nothing rewarded
it. Predation is bounded -- you die once. Competition for food is
compounding but shares: a rival takes a FRACTION of your intake.

LIGHT IS NEITHER, AND THAT IS WHY PLANTS MATTER. A rival growing
above you does not take a share of your light. It takes all of it,
and it keeps taking it every day for as long as it stands there.
Beer-Lambert through a canopy: at leaf area index 4 only 13.5% of
the light reaches below, at 8 only 1.8%. That is the first
winner-take-all pressure in this repository, and it is the only
one whose reward scales with being LARGER rather than smaller.

    cost of height    a trunk holds itself up, mass ~ h^3
    benefit           everything above the neighbours

TROPHIC LEVELS FALL OUT OF THE SAME ARITHMETIC. A plant fixes
about 1% of 236 W/m2. Each step up loses most of what it eats --
respiration is the Kleiber cost and only the surplus is available
to whatever eats you -- so the energy at level n is the production
times the transfer fraction to the n-th power. That is why food
chains are short, and the length is derivable rather than
asserted.

AND INTELLIGENCE IS TESTED THE WAY CIRCULATION WAS. Not "did a
brain appear" but "does a brain PAY". Neural tissue costs about
ten times average, so a brain at 2% of body mass takes 20% of the
budget. For that to be worth carrying it must raise intake by more
than 20%, and whether tool use does that is a question with a
number in it.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.life import G_EARTH, RHO_WATER

# CHOSEN, registered in engine/inputs.py
PHOTOSYNTHETIC_EFFICIENCY = 0.01
EXTINCTION_K = 0.5            # Beer-Lambert through a canopy
TRANSFER_FRACTION = 0.10      # energy passed to the next level
TRUNK_DENSITY = 500.0         # kg/m3, wood
WOOD_MODULUS = 1.0e10         # Pa, Young's modulus of wood
GREENHILL_C = 0.792           # self-loaded column, Greenhill
SAPWOOD_M = 0.02              # m, thickness of the living shell
RESP_PER_KG = 0.10            # W/kg of LIVING tissue
XYLEM_TENSION = 2.0e6         # Pa, before the water column cavitates
CROWN_M2 = 1.0                # m2 of leaf a plant can hold up


def surface_light():
    """W/m2 absorbed at the ground. DERIVED from engine/terraform.py."""
    from engine.terraform import BODIES
    e = BODIES["Earth"]
    return e.flux() * (1 - e.albedo) / 4.0


def light_below(lai):
    """Fraction reaching under a canopy. DERIVED: Beer-Lambert."""
    return math.exp(-EXTINCTION_K * max(lai, 0.0))


def safe_radius(height_m):
    """m. Thinner than this and the column buckles. DERIVED: Greenhill."""
    scale = GREENHILL_C * (WOOD_MODULUS / (TRUNK_DENSITY * G_EARTH)) ** (1/3)
    return (height_m / scale) ** 1.5


def trunk_mass(height_m):
    """kg, total. DERIVED from the radius that does not buckle."""
    r = safe_radius(height_m)
    return TRUNK_DENSITY * math.pi * r * r * height_m


def living_mass(height_m):
    """kg. A trunk is mostly heartwood -- dead, load-bearing, and it
    does NOT respire. Only the sapwood shell is alive. DERIVED."""
    r = safe_radius(height_m)
    total = trunk_mass(height_m)
    shell = TRUNK_DENSITY * math.pi * height_m * (r*r - max(r - SAPWOOD_M, 0.0)**2)
    return min(shell, total)


def hydraulic_ceiling():
    """m. Water is PULLED up under tension and the column breaks.
    DERIVED: the cavitation pressure divided by rho g."""
    return XYLEM_TENSION / (RHO_WATER * G_EARTH)


def plant_energy(height_m, rival_height=0.0, crown_m2=CROWN_M2,
                 rival_lai=4.0):
    """-> (W gained, W spent). DERIVED.

    Crown area is NOT tied to height. An earlier version set the
    crown to a tenth of the height, which made tallness pay for
    itself with no competitor present -- it assumed the conclusion.
    A shrub can hold a wide crown one metre off the ground. Height
    buys exactly one thing: the light a neighbour would otherwise
    take, all of it, every day.

    Kleiber is NOT used. Kleiber prices an animal, and a trunk is
    four percent alive at a hundred metres.
    """
    if height_m <= 0:
        return 0.0, 0.0
    fix = surface_light() * PHOTOSYNTHETIC_EFFICIENCY
    under = light_below(rival_lai)
    if height_m > rival_height:
        share = 1.0                      # above every leaf they have
    elif height_m < rival_height:
        share = under                    # beneath all of them
    else:
        share = 0.5 * (1.0 + under)      # level, shading each other
    return fix * share * crown_m2, living_mass(height_m) * RESP_PER_KG


def tallest_worthwhile(rival_height=0.0, crown_m2=CROWN_M2,
                       lo=0.05, hi=400.0):
    """-> (m, W). The best reply to a canopy at rival_height."""
    ceiling = hydraulic_ceiling()
    best, best_h, n = -1e30, lo, 900
    for i in range(n):
        h = lo * (hi / lo) ** (i / (n - 1))
        if h > ceiling:
            break
        g, c = plant_energy(h, rival_height, crown_m2)
        if g - c > best + 1e-12:
            best, best_h = g - c, h
    return best_h, best


def must_outgrow(rival_height, crown_m2=CROWN_M2):
    """-> (bool, why). Is staying short survivable under a canopy?"""
    g, c = plant_energy(max(rival_height * 0.5, 0.05), rival_height,
                        crown_m2)
    over_g, over_c = plant_energy(rival_height * 1.05 + 0.05,
                                  rival_height, crown_m2)
    return (over_g - over_c) > (g - c), (
        f"under a {rival_height:.1f} m canopy a short plant nets "
        f"{g-c:.3f} W; clearing it nets {over_g-over_c:.3f} W")


def escalation_stops_at(crown_m2=CROWN_M2, rival_lai=4.0):
    """m. Where the arms race ends. DERIVED, no iteration on height.

    The reply to a neighbour at H metres is H and a hair, so the
    climb is continuous and only its endpoint is physical. It is
    the height whose trunk costs as much as the light being fought
    over -- the eighty-six percent a canopy takes from you.
    """
    prize = (surface_light() * PHOTOSYNTHETIC_EFFICIENCY * crown_m2
             * (1.0 - light_below(rival_lai)))
    lo, hi = 1e-3, hydraulic_ceiling()
    if living_mass(hi) * RESP_PER_KG <= prize:
        return hi                        # the water column gives out first
    for _ in range(60):
        mid = (lo * hi) ** 0.5
        if living_mass(mid) * RESP_PER_KG > prize:
            hi = mid
        else:
            lo = mid
    return (lo * hi) ** 0.5


def ratchet(rounds=10, start=0.05, crown_m2=CROWN_M2):
    """-> [m]. Each generation answers the canopy the last one built.

    This is the test engine/descent.py kept failing. Predation put
    a ceiling on size; competition for food put a floor under it.
    Neither pushed UP. Light does, because the best reply to a
    neighbour at H metres is H and a hair, and that reply is the
    next generation's canopy.
    """
    stop, h, out = escalation_stops_at(crown_m2), start, [start]
    for _ in range(rounds):
        h = min(h * 3.0, stop)
        out.append(h)
        if h >= stop:
            break
    return out


def metabolism_w(mass_kg):
    """W. DERIVED via engine.life.kleiber, which already returns WATTS.

    Its b0_kcal_day argument names the INPUT unit, not the output,
    and the Fact it hands back says "53.9 W at 40 kg" in its own
    why string. An earlier version here converted anyway and shrank
    every animal's bill twentyfold. The Fact carried its units and
    was not read.
    """
    from engine.life import kleiber
    k = kleiber(mass_kg)
    return float(k.value if hasattr(k, "value") else k)


def energy_at_level(level):
    """W/m2 available to trophic level n. DERIVED."""
    return (surface_light() * PHOTOSYNTHETIC_EFFICIENCY
            * TRANSFER_FRACTION ** max(level, 0))


def territory(mass_kg, level):
    """m2 one animal must hunt to feed itself. DERIVED.

    A square metre does not feed a predator -- it ranges over one.
    An earlier version read the body mass straight off the power in
    a single square metre and produced a sixty-milligram top
    predator, which is a shrew pretending to be a lion.
    """
    return metabolism_w(mass_kg) / energy_at_level(level)


def food_chain_length(minimum_w=1e-3):
    """How many trophic levels the light supports. DERIVED."""
    e, n = surface_light() * PHOTOSYNTHETIC_EFFICIENCY, 0
    while e > minimum_w:
        e *= TRANSFER_FRACTION
        n += 1
    return n


def predator_prey_ratio(pred_kg, prey_kg, pred_level=2, prey_level=1):
    """-> prey individuals standing per predator. DERIVED."""
    return (territory(pred_kg, pred_level) * energy_at_level(prey_level)
            / metabolism_w(prey_kg))


def trophic_ladder(levels=5):
    """-> [(name, W/m2, km2 a 10 kg body would need)]. DERIVED."""
    names = ["producer", "herbivore", "carnivore", "top predator",
             "level 5", "level 6", "level 7"]
    return [(names[i], energy_at_level(i),
             territory(10.0, i) / 1e6) for i in range(levels)]


def brain_pays(brain_fraction, intake_gain):
    """-> (bool, why). Does thinking earn its keep? DERIVED."""
    from engine.ancestry import brain_share
    cost = brain_share(brain_fraction)
    return intake_gain > cost, (
        f"a brain at {100*brain_fraction:.1f}% of body mass costs "
        f"{100*cost:.0f}% of the energy budget, so it must raise intake "
        f"by more than that. At {100*intake_gain:.0f}% it "
        + ("pays" if intake_gain > cost else "does NOT pay"))


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("light_is_winner_take_all", _light)
    t("height_is_worthless_without_a_rival", _height)
    t("light_ratchets_size_upward", _ratchet)
    t("the_food_chain_has_a_derivable_length", _chain)
    t("each_trophic_level_is_smaller_in_total", _ladder)
    t("a_predator_needs_ground_not_a_square_metre", _range)
    t("a_brain_must_pay_for_itself", _brain)
    t("intelligence_is_not_claimed", _humble)
    return all(o[1] for o in out), out


def _light():
    a, b = light_below(4.0), light_below(8.0)
    if a > 0.2 or b > 0.05:
        raise ArithmeticError("a canopy is not shading enough to matter")
    return (f"at leaf area index 4 only {100*a:.1f}% of light reaches "
            f"below, at 8 only {100*b:.1f}%. A rival eating your food "
            f"takes a SHARE; a rival growing above you takes it ALL, "
            f"and keeps taking it every day it stands there. That is "
            f"the first winner-take-all pressure here, and the only "
            f"one whose reward grows with being larger")


def _height():
    alone, _ = tallest_worthwhile(rival_height=0.0)
    if alone > 0.1:
        raise ArithmeticError(f"a plant with no neighbour grew {alone:.1f} m")
    inverted = escalation_stops_at(1.0)
    return (f"INVERTED, kept. This rule first said height has an optimum "
            f"and it is tall, and it passed at 92 m -- because the crown "
            f"was set to a tenth of the height, so tallness paid for "
            f"itself with nobody to outgrow. It assumed the conclusion. "
            f"Cut that tie and a plant alone stays at the floor "
            f"({alone:.2f} m): sunlight does not get brighter further "
            f"up. Height is worth nothing on its own and {inverted:.0f} m "
            f"against a rival. The pressure is the neighbour, not the sun")


def _ratchet():
    r = ratchet()
    ceiling = hydraulic_ceiling()
    if r[-1] <= r[0] * 10:
        raise ArithmeticError("light did not push size up either")
    if r[-1] >= ceiling:
        raise ArithmeticError("the race hit the water column, not a cost")
    return (f"{r[0]:.2f} m -> {r[-1]:.0f} m, a {r[-1]/r[0]:.0f}-fold "
            f"climb that stops where the trunk costs as much as the "
            f"light being fought over, well under the {ceiling:.0f} m "
            f"cavitation ceiling. Every other pressure here pushed "
            f"size DOWN -- engine/descent.py collapsed a lineage to "
            f"0.1 um and predation could not stop it at 99% "
            f"mortality. Light is the first that pushes UP, because "
            f"a rival eating your food takes a share and a rival "
            f"standing over you takes all of it")


def _ladder():
    lad = trophic_ladder()
    if not all(a[1] > b[1] for a, b in zip(lad, lad[1:])):
        raise ArithmeticError("energy did not fall going up the ladder")
    return (f"producers hold {lad[0][1]:.2f} W/m2 and top predators "
            f"{lad[3][1]:.2e}, a {lad[0][1]/lad[3][1]:.0f}-fold drop "
            f"over three steps, so the same 10 kg body needs "
            f"{lad[0][2]:.3g} km2 as a grazer and {lad[3][2]:.3g} as a "
            f"hunter. Predators are rare because the arithmetic makes "
            f"them rare, not because anything said so")


def _range():
    """MISSING_RULE, named not patched."""
    wolf = territory(40.0, 2) / 1e6
    lion = territory(175.0, 3) / 1e6
    real_wolf = 100.0                      # RECORDED, km2, the low end
    if wolf > real_wolf:
        raise ArithmeticError(
            f"the derived minimum {wolf:.3g} km2 exceeds the smallest "
            f"home range anyone has measured, so the energetics is "
            f"claiming more ground than exists")
    return (f"MISSING_RULE. A 40 kg carnivore needs {wolf:.4f} km2 to "
            f"cover {metabolism_w(40.0):.0f} W, and a 175 kg one at the "
            f"top {lion:.3f} km2. Real wolf packs hold 100-1000 km2 -- "
            f"{real_wolf/wolf:.0f} times more. The derivation is a "
            f"floor and reality sits far above it, which is the right "
            f"direction but not an explanation. What is absent is that "
            f"A TROPHIC LEVEL IS A GUILD, NOT A SPECIES: the tenth "
            f"that passes upward is split across every carnivore, "
            f"most of it invertebrate, and one wolf takes a sliver. "
            f"No rule here partitions a level among its occupants, so "
            f"the number is not being fixed by hand")


def _chain():
    n = food_chain_length()
    if not 3 <= n <= 7:
        raise ArithmeticError(f"{n} trophic levels is not a food chain")
    e = surface_light() * PHOTOSYNTHETIC_EFFICIENCY
    return (f"{surface_light():.0f} W/m2 reaches the ground, plants fix "
            f"{e:.2f}, and each level passes about "
            f"{100*TRANSFER_FRACTION:.0f}% up -- so the chain runs "
            f"{n} levels before there is nothing left to be. Food "
            f"chains are short because the arithmetic is exponential, "
            f"not because anyone decided")


def _brain():
    small, _w1 = brain_pays(0.005, 0.10)
    human, _w2 = brain_pays(0.02, 0.15)
    big, w3 = brain_pays(0.02, 0.50)
    if human:
        raise ArithmeticError("a human-sized brain pays on a 15% intake "
                              "gain, which would make it cheap")
    if not big:
        raise ArithmeticError("a 50% intake gain does not cover a brain")
    return (f"a brain at 2% of mass costs 20% of the budget, so it must "
            f"raise intake by MORE than a fifth or it is dead weight. A "
            f"15% gain does not cover it; a 50% gain does. That is the "
            f"same test circulation passed at 0.01% -- and a brain is "
            f"two thousand times more expensive than a heart")


def _humble():
    return ("nothing here says a brain appeared, and nothing says tools "
            "were made. The question asked is whether thinking EARNS "
            "its keep, which has a number in it, and the answer is "
            "that it only does above a large intake gain. Whether any "
            "lineage found one is not something these rules can "
            "reach -- it needs the mechanism that generates variation, "
            "which engine/descent.py showed is absent")


if __name__ == "__main__":
    print(f"  ground light {surface_light():.0f} W/m2, plants fix "
          f"{surface_light()*PHOTOSYNTHETIC_EFFICIENCY:.2f} W/m2\n")
    print(f"  {'LAI above':>10}{'light below':>13}")
    for lai in (0, 1, 2, 4, 8):
        print(f"  {lai:>10}{100*light_below(lai):>12.1f}%")
    print(f"\n  {'crown m2':>10}{'race stops at':>16}{'trunk':>14}")
    for c in (0.1, 1.0, 10.0, 100.0, 1000.0):
        st = escalation_stops_at(c)
        print(f"  {c:>10.1f}{st:>14.1f} m{trunk_mass(st):>12,.0f} kg")
    print(f"\n  alone, the best height is "
          f"{tallest_worthwhile(rival_height=0.0)[0]:.2f} m -- "
          f"sunlight does not get brighter further up")
    print(f"  ratchet  " + " -> ".join(f"{x:.2f}" for x in ratchet()))
    print(f"  cavitation ceiling {hydraulic_ceiling():.0f} m")
    print(f"\n  {'level':>14}{'W/m2':>12}{'km2 for 10 kg':>16}")
    for n, e, a in trophic_ladder():
        print(f"  {n:>14}{e:>12.3e}{a:>15.3g}")
    print(f"\n  a 40 kg carnivore covers {metabolism_w(40.0):.0f} W off "
          f"{territory(40.0,2):,.0f} m2, standing on "
          f"{predator_prey_ratio(40.0,20.0):.0f} prey -- real packs hold "
          f"100-1000 km2, see the MISSING_RULE below\n")
    for bf, gain in ((0.005, 0.10), (0.02, 0.15), (0.02, 0.50)):
        ok, why = brain_pays(bf, gain)
        print(f"  {'pays' if ok else 'no  '}  {why[:74]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:40}{d[:48]}")
