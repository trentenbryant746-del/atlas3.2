"""
A code of law and an empire, handed over, then audited.

The same god-move as engine/civ.py: give the animals a list of
injunctions and a state to run them, claim no credit, and then ask
the arithmetic which parts it already knew. What comes back is a
split, and the split is the result.

HOW BIG CAN AN EMPIRE BE. Not a question about ambition. A centre
that cannot answer a crisis before the crisis finishes does not
govern the place, so the radius is signal speed times half the
window a revolt takes to become irreversible.

    runner on foot          40 km/day  ->  1,800 km
    Roman cursus publicus   50         ->  2,250 km
    mounted relay          200         ->  9,000 km
    optical telegraph      800         -> the whole planet

Rome to Hadrian's Wall is about 1,900 km and Rome to the Euphrates
about 2,500. The derived 2,250 lands between them, from a courier
speed and a crisis window and nothing else.

AND ONE COMMANDMENT DERIVES FROM THE CHANNEL ITSELF. engine/civ.py
found language is worth having only because it carries a SELECTION
another brain already paid for -- 0.0122% of a lifetime's input,
but the chosen 0.0122%. That value is conditional. If the
selection cannot be trusted the receiver has to verify, verifying
costs what deriving it would have cost, and then the channel is
worse than useless: you pay the telling AND the deriving.

So there is a maximum tolerable lie rate and it falls out of the
ratio. Where acting wrongly costs twenty times the derivation, the
channel survives about 4.7% lies and collapses above it. DO NOT
BEAR FALSE WITNESS is not an ethical premise here. It is the
condition under which speech remains cheaper than thinking.

The rest mostly do not derive, and saying which is the point.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# GIVEN. A code, handed over, no credit taken.
COMMANDMENTS = (
    "no other gods", "no idols", "do not misuse the name",
    "keep the sabbath", "honour your parents", "do not kill",
    "do not commit adultery", "do not steal",
    "do not bear false witness", "do not covet",
)

# MEASURED
COURIER_KM_DAY = 50.0        # Roman cursus publicus
CRISIS_DAYS = 90.0           # a revolt consolidating
EARTH_R_KM = 6371.0
TELL_S = 60.0                # to be told a thing
DERIVE_S = 3600.0            # to work it out unaided
WRONG_COST_MULT = 20.0       # acting on a falsehood


def empire_radius_km(speed_km_day=COURIER_KM_DAY, crisis_days=CRISIS_DAYS):
    """km. DERIVED: the centre must answer inside the window."""
    return speed_km_day * crisis_days / 2.0


def reachable_km2(radius_km):
    """km2 on a sphere. DERIVED, spherical cap."""
    a = min(radius_km / EARTH_R_KM, math.pi)
    return 2.0 * math.pi * EARTH_R_KM ** 2 * (1.0 - math.cos(a))


def tolerable_lie_rate(tell_s=TELL_S, derive_s=DERIVE_S,
                       wrong_mult=WRONG_COST_MULT):
    """Fraction of messages that may be false. DERIVED.

    Accept without verifying while the expected loss is under the
    expected saving. Above it, everything must be checked, and
    checking costs what deriving would have.
    """
    save = derive_s - tell_s
    loss = derive_s * wrong_mult
    return save / (loss + save)


def channel_survives(lie_rate):
    """-> (bool, why). DERIVED."""
    p = tolerable_lie_rate()
    return lie_rate < p, (
        f"the channel tolerates {100*p:.1f}% lies and this is "
        f"{100*lie_rate:.1f}%")


def audit_code():
    """-> [(injunction, verdict, why)]. Which parts were known."""
    from engine.civ import smallest_group, alone_is_viable, FORAGER_W
    from engine.ontogeny import provisioning_debt
    out = []
    p = tolerable_lie_rate()
    _, yrs = provisioning_debt()
    n = smallest_group()

    out.append(("do not bear false witness", "DERIVED",
                f"speech is worth its cost only while it carries a "
                f"selection that need not be checked; above "
                f"{100*p:.1f}% lies the receiver must verify, and "
                f"verifying costs what deriving would have"))
    out.append(("do not kill", "DERIVED",
                f"the smallest group that carries a child is {n} "
                f"adults with {FORAGER_W:.0f} W each; removing one "
                f"does not cost one life, it costs the child too"))
    out.append(("honour your parents", "DERIVED",
                f"provisioning is a ledger and it ran {yrs:.1f} "
                f"adult-years in one direction before it could run "
                f"the other"))
    out.append(("do not steal", "PARTLY DERIVED",
                "moving calories produces none, so a group gains "
                "nothing; what is absent is any rule making the "
                "group the unit that gains"))
    out.append(("do not commit adultery", "PARTLY DERIVED",
                "the provisioning ledger has to be allocated to "
                "somebody, and nothing here says to whom"))
    out.append(("keep the sabbath", "NOT DERIVED",
                "no rule prices recovery; a body here runs at "
                "Kleiber whether or not it rested"))
    out.append(("do not covet", "NOT DERIVED",
                "engine/civ.py already found nothing prices rank, "
                "and this is the same absence again"))
    for c in ("no other gods", "no idols", "do not misuse the name"):
        out.append((c, "NOT DERIVED",
                    "nothing here prices belief, so these are "
                    "injected whole and are marked as injected"))
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("an_empire_is_bounded_by_its_signal_speed", _span)
    t("the_derived_span_lands_on_rome", _rome)
    t("honesty_is_a_condition_on_the_channel", _lie)
    t("most_of_the_code_does_not_derive", _audit)
    t("faster_signals_make_bigger_empires", _faster)
    return all(o[1] for o in out), out


def _span():
    r = empire_radius_km()
    a = reachable_km2(r)
    if not 1e3 < r < 1e4:
        raise ArithmeticError(f"the radius came out {r:.0f} km")
    return (f"a centre that cannot answer before a crisis finishes "
            f"does not govern the place, so the radius is "
            f"{COURIER_KM_DAY:.0f} km/day times half a "
            f"{CRISIS_DAYS:.0f}-day window: {r:,.0f} km, reaching "
            f"{a:,.0f} km2 or {100*a/5.1e8:.1f}% of Earth. Not a "
            f"question about ambition")


def _rome():
    r = empire_radius_km()
    wall, euphrates = 1900.0, 2500.0     # RECORDED
    if not wall < r < euphrates:
        raise ArithmeticError(f"{r:.0f} km misses the Roman span")
    return (f"Rome to Hadrian's Wall is {wall:,.0f} km and Rome to "
            f"the Euphrates {euphrates:,.0f}. The derived radius is "
            f"{r:,.0f} km and lands between them, out of a courier "
            f"speed and a crisis window and nothing else. This is "
            f"the one place in the whole human chain where a number "
            f"here meets something that actually happened")


def _lie():
    p = tolerable_lie_rate()
    ok_low, _ = channel_survives(0.01)
    ok_high, why = channel_survives(0.30)
    if not ok_low or ok_high:
        raise ArithmeticError(f"threshold {p:.3f} sorts wrong")
    return (f"speech is worth its cost only because it carries a "
            f"selection the receiver need not check. Above "
            f"{100*p:.1f}% lies, {why[:40]}... -- everything must be "
            f"verified and verifying costs what deriving would have, "
            f"so you pay the telling AND the thinking. DO NOT BEAR "
            f"FALSE WITNESS is not an ethical premise here, it is "
            f"the condition under which speech stays cheaper than "
            f"thought")


def _audit():
    a = audit_code()
    der = [x for x in a if x[1] == "DERIVED"]
    not_der = [x for x in a if x[1] == "NOT DERIVED"]
    if len(der) < 2 or len(not_der) < 4:
        raise ArithmeticError(f"{len(der)} derived, {len(not_der)} not")
    return (f"of {len(a)} injunctions, {len(der)} derive from rules "
            f"already here ({', '.join(x[0] for x in der)}), two are "
            f"partial, and {len(not_der)} do not derive at all. The "
            f"code was HANDED OVER and most of it stayed handed "
            f"over. What is worth saying is not that the rest is "
            f"wrong -- it is that nothing here prices belief, rank "
            f"or rest, so those are absences and not refutations")


def _faster():
    slow = empire_radius_km(40.0)
    fast = empire_radius_km(800.0)
    if fast <= slow:
        raise ArithmeticError("faster signals did not reach further")
    whole = reachable_km2(fast) / 5.1e8
    return (f"a runner at 40 km/day governs {slow:,.0f} km and an "
            f"optical telegraph at 800 governs {fast:,.0f}, which is "
            f"{100*min(whole,1.0):.0f}% of the planet. The size of "
            f"the largest possible empire is a fact about signalling "
            f"and moves when signalling does -- it predicts that "
            f"global empires cannot precede fast signals, and they "
            f"did not")


if __name__ == "__main__":
    print(f"  {'signal':<24}{'km/day':>8}{'radius':>12}{'% Earth':>10}")
    for nm, s in (("runner on foot", 40), ("Roman cursus publicus", 50),
                  ("mounted relay", 200), ("optical telegraph", 800)):
        r = empire_radius_km(s)
        print(f"  {nm:<24}{s:>8.0f}{r:>10,.0f}km"
              f"{100*reachable_km2(r)/5.1e8:>9.1f}%")
    print(f"\n  Rome to Hadrian's Wall ~1,900 km, to the Euphrates "
          f"~2,500\n  derived {empire_radius_km():,.0f} km\n")
    print(f"  tolerable lie rate {100*tolerable_lie_rate():.1f}%\n")
    for c, v, why in audit_code():
        print(f"  {c:<26}{v:<16}{why[:42]}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:38]}")
