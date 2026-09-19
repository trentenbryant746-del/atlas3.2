"""What turns a shaft, and why one class of thing beats another.

Most of what this world builds uses steam, and that is worth
questioning, because steam is not merely a poor engine -- it is
in a CLASS of engine with a ceiling nothing can lift.

A heat engine takes heat from hot and dumps it to cold, and no
arrangement of metal gets past 1 - Tc/Th. That is not an
engineering limit to be worked at, it is the second law:

    a wood-fired boiler     450 K      33.3%
    superheated steam       800 K      62.5%
    a gas flame            2000 K      85.0%
    inside a cylinder      2500 K      88.0%

An electric motor is not a heat engine. There is no hot side
and no cold side, so there is no Tc/Th to subtract. Its losses
are resistance and hysteresis, which are numbers about copper
and iron rather than a law about temperature, and they fall as
the copper improves. Real motors run 90-96%.

So the difference between steam and a motor is not that one is
better made. They are in different classes, one bounded by a
law and one bounded by materials, and the bounded one loses as
soon as the other exists.

WHY THIS WORLD STILL USES STEAM. Because nothing in
engine/world.py prefers anything. A band combines what it
holds; no rule says a better engine displaces a worse one. That
is a real gap and it is named at the bottom of this file rather
than papered over -- selection needs a surplus to select on,
and the bands have not got one.
"""

import math

AMBIENT_K = 300.0                # MEASURED-ish, a working day

SOURCES = {
    "a wood fire under a boiler": (450.0, "heat"),
    "superheated steam": (800.0, "heat"),
    "a gas flame": (2000.0, "heat"),
    "inside a cylinder": (2500.0, "heat"),
    "an electric motor": (None, "not heat"),
    "a fuel cell": (None, "not heat"),
}

# MEASURED. What a real device of each class reaches, against
# its ceiling. A heat engine gives up most of its Carnot margin
# to friction, incomplete combustion and dumping hot exhaust.
REALISED = {"heat": 0.40, "not heat": 0.93}


def carnot(hot_k, cold_k=AMBIENT_K):
    """1 - Tc/Th. DERIVED, and it is a law rather than a target."""
    return max(0.0, 1.0 - cold_k / hot_k)


def ceiling(source):
    """-> (fraction or None, kind). DERIVED."""
    hot, kind = SOURCES[source]
    return (carnot(hot) if hot else None), kind


def realised(source):
    """What such a thing actually delivers. MEASURED-ish."""
    top, kind = ceiling(source)
    if top is None:
        return REALISED["not heat"]
    return top * REALISED["heat"] / 0.40 * 0.40


def bounded_by_law(source):
    """Is a ceiling here physics or metallurgy? DERIVED."""
    return SOURCES[source][0] is not None


def best_available(held):
    """Best motive source the crafts in hand allow. DERIVED."""
    if {"electricity", "rotation"} <= set(held):
        return "an electric motor"
    if {"steam", "pressure"} <= set(held):
        return "superheated steam"
    if "heat" in held:
        return "a wood fire under a boiler"
    return None


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_heat_engine_has_a_ceiling_and_it_is_a_law", _law)
    t("a_motor_is_not_a_heat_engine_so_carnot_does_not_apply", _motor)
    t("INVERTED_this_world_keeps_steam_because_nothing_chooses", _nochoice)
    return all(x for _, x, _ in res), res


def _law():
    rows = [(s, ceiling(s)[0]) for s in SOURCES if bounded_by_law(s)]
    lo, hi = min(r[1] for r in rows), max(r[1] for r in rows)
    if hi >= 1.0:
        raise ArithmeticError(f"{hi}")
    return (f"a heat engine takes heat from hot and dumps it to "
            f"cold, and no arrangement of metal gets past "
            f"1 - Tc/Th at an ambient {AMBIENT_K:.0f} K: "
            + "; ".join(f"{s} {100*c:.1f}%" for s, c in rows)
            + f". That is not an engineering limit to be worked "
              f"at, it is the second law, and the only way up is "
              f"a hotter fire. Which is why an engine's history "
              f"is a history of MATERIALS -- the ceiling moves "
              f"only when the cylinder survives more heat")


def _motor():
    e = realised("an electric motor")
    steam = ceiling("superheated steam")[0]
    if e <= steam:
        raise ArithmeticError(f"{e} {steam}")
    return (f"an electric motor is NOT a heat engine. There is "
            f"no hot side and no cold side, so there is no Tc/Th "
            f"to subtract and Carnot simply does not apply. Its "
            f"losses are resistance and hysteresis -- numbers "
            f"about copper and iron, not a law about temperature "
            f"-- so it runs {100*e:.0f}% against superheated "
            f"steam's {100*steam:.0f}% CEILING, which steam "
            f"never reaches. The difference is not that one is "
            f"better made. They are in different classes, one "
            f"bounded by a law and one by materials, and the "
            f"bounded one loses the moment the other exists")


def _nochoice():
    """INVERTED. Fails if the world ever prefers the better thing."""
    from engine.world import run
    from engine.artifact import PRIMITIVES
    w = run()
    with_steam = sum(1 for a in w.artifacts() if "steam" in a)
    with_motor = sum(1 for a in w.artifacts()
                     if {"electricity", "rotation"} <= a)
    tot = len(w.artifacts())
    if with_motor > with_steam:
        raise ArithmeticError(
            "the world now favours motors over steam, which means "
            "something in it started choosing and this check has "
            "become a claim rather than a gap")
    return (f"this world keeps building with steam -- "
            f"{with_steam:,} of {tot:,} things contain it against "
            f"{with_motor:,} that could be a motor -- and the "
            f"reason is not that steam is good. It is that "
            f"NOTHING IN engine/world.py PREFERS ANYTHING. A band "
            f"combines what it holds and no rule says a better "
            f"engine displaces a worse one. Selection needs "
            f"something to select on: a band using a 93% motor "
            f"would keep more of its fuel, and more surplus means "
            f"more teaching and more bands, which is exactly the "
            f"machinery engine/intricacy.py already has and "
            f"engine/world.py is not wired to. That is a real gap "
            f"and this check fails the day it closes")


if __name__ == "__main__":
    print(f"  ambient {AMBIENT_K:.0f} K\n")
    print(f"  {'source':<28}{'Th':>7}{'ceiling':>10}{'real':>8}"
          f"   bounded by")
    for s in SOURCES:
        top, kind = ceiling(s)
        hot = SOURCES[s][0]
        print(f"  {s:<28}{(f'{hot:.0f}' if hot else '-'):>7}"
              f"{(f'{100*top:.1f}%' if top else '-'):>10}"
              f"{100*realised(s):>7.0f}%"
              f"   {'the second law' if top else 'copper and iron'}")
    print()
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
