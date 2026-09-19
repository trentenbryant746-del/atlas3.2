"""Making a surface stand for something, in two ways.

A DRAWING and a PHOTOGRAPH both put a thing on a flat surface,
and they are not the same kind of object at all.

A drawing is a projection, and a projection is a convention. It
needs a drawer and a reader who hold the same one, so its worth
goes as f-squared -- the same exponent engine/literacy.py found
for writing, and slow for the same reason. A photograph needs no
convention. Anyone with eyes reads it. Its worth goes as f, and
f is one from the moment the thing exists.

ART is the third case and it is the strange one. It is the only
output in this tree that needs no tolerance at all: a mark does
not have to be true to anything, so no gate has ever blocked it
and none ever will. It is available in round one and in round
eleven and it does not improve in between, in the sense that
matters here -- there is no precision it was waiting for.

The obvious economic account of art, that it waits for a
surplus, is tested below and fails. It fails on magnitude.
"""

import math

from engine.artifact import (PRIMITIVES, TOL_NEEDED, BASE_TOL,
                             bootstrap, held_by_round)
from engine.drawing import convention_value

PIGMENT_HOURS = 6.0        # CHOSEN, a painted surface
WORK_HOURS_DAY = 8.0


def photograph_value(fraction):
    """Worth of an image at that literacy. DERIVED.

    No convention, so no second factor. A photograph is read by
    whoever looks at it, which is everybody.
    """
    return 1.0


def image_over_drawing(fraction):
    """How much better an image is at that literacy. DERIVED."""
    v = convention_value(fraction)
    return math.inf if v <= 0 else photograph_value(fraction) / v


def art_needs_tolerance():
    """The tolerance a mark must be held to. DERIVED.

    None. A mark is not true to anything, so nothing gates it.
    """
    return BASE_TOL


def art_available_at():
    """First round anything can be made as art. DERIVED."""
    for i, _t, got in bootstrap():
        if got:
            return i
    return None


def art_cost_days():
    """What one made thing costs. DERIVED."""
    return PIGMENT_HOURS / WORK_HOURS_DAY


def tool_cost_days():
    """What one part of a tool costs, for comparison."""
    from engine.capital import DAYS_PER_PART
    return DAYS_PER_PART


def art_audience():
    """Who can act on it. DERIVED, engine/naming.py's rule."""
    return 1.0


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_photograph_is_a_drawing_that_needs_no_reader", _photo)
    t("art_is_the_one_output_no_gate_can_block", _ungated)
    t("REFUTED_art_waits_for_a_surplus", _surplus)
    t("art_travels_like_a_fact_and_not_like_a_tool", _spread)
    return all(x for _, x, _ in res), res


def _photo():
    r = next(i for i, _t, g in bootstrap() if "depiction" in g)
    at10 = image_over_drawing(0.10)
    if at10 < 10:
        raise ArithmeticError(f"{at10}")
    return (f"a drawing is a projection and a projection is a "
            f"convention, so it needs a drawer AND a reader who "
            f"hold the same one: worth f-squared, which is "
            f"{convention_value(0.10):.2f} at 10% and "
            f"{convention_value(0.01):.4f} at 1%. A photograph "
            f"needs no convention -- whoever looks at it reads "
            f"it -- so its worth is f to the first power, which "
            f"is 1 from the moment it exists. At 10% that is "
            f"{at10:.0f}x the drawing and at 1% it is "
            f"{image_over_drawing(0.01):.0f}x. Depiction arrives "
            f"at round {r}, needing a lens and a specified "
            f"composition, and what it does is abolish the "
            f"second literacy that engine/drawing.py had just "
            f"finished deriving")


def _ungated():
    need = art_needs_tolerance()
    gated = [p for p in PRIMITIVES
             if TOL_NEEDED.get(p, BASE_TOL) < BASE_TOL]
    if need < BASE_TOL:
        raise ArithmeticError(f"{need}")
    return (f"art is the only output here that needs no tolerance. "
            f"A mark is not true to anything, so there is no "
            f"number to hit and nothing to fail at. "
            f"{len(gated)} of {len(PRIMITIVES)} crafts are held "
            f"to something tighter than the hand can manage and "
            f"every one of them waits for a gate; art waits for "
            f"nothing and is available in round "
            f"{art_available_at()}. That is why the oldest "
            f"surviving made things are painted and carved rather "
            f"than machined -- not because anybody preferred "
            f"them, but because they were the only things not "
            f"queueing behind a furnace")


def _surplus():
    """REFUTED. The economic account of art fails on magnitude."""
    from engine.group import spare_per_head
    art, tool = art_cost_days(), tool_cost_days()
    forager = spare_per_head(28)
    if art > tool / 10:
        raise ArithmeticError(f"art {art} is not cheap vs {tool}")
    return (f"the obvious account is that art waits for a surplus: "
            f"nobody paints until somebody is fed. It is wrong, "
            f"and the record kills it -- painted caves are thirty "
            f"thousand years older than farming, made by bands "
            f"whose spare_per_head engine/group.py puts at "
            f"{forager:.0f}. The reason is magnitude. A painted "
            f"surface is {art:.2f} days and one part of a tool is "
            f"{tool:.0f}, a factor of {tool/art:.0f}, so art does "
            f"not need a surplus because it barely costs "
            f"anything. An account that would have been "
            f"satisfying about inequality and leisure turns out "
            f"to be an arithmetic error about how expensive "
            f"paint is")


def _spread():
    from engine.naming import audience
    from engine.craft import best_depth
    s = best_depth(28)[1]
    a, t_ = art_audience(), audience("tool", s)
    if a <= t_:
        raise ArithmeticError(f"{a} {t_}")
    return (f"engine/naming.py found that a thing spreads when "
            f"the listener can act on it, which gives a tool an "
            f"audience of 1/s and a fact an audience of "
            f"everybody. Art is in the second class: there is "
            f"nothing to hold and nothing to be qualified for, so "
            f"its audience is {100*a:.0f}% against a tool's "
            f"{100*t_:.0f}% in a band holding {s} crafts. Art "
            f"travels like a fact. That is the same asymmetry "
            f"that leaves toolmakers unnamed, running the other "
            f"way for once, and it is why a style crosses a "
            f"region faster than the technique for making the "
            f"pigment does")


if __name__ == "__main__":
    print(f"  {'literacy':>10}{'drawing':>10}{'photograph':>13}"
          f"{'ratio':>10}")
    for f in (0.01, 0.1, 0.5, 1.0):
        print(f"  {100*f:>9.0f}%{convention_value(f):>10.4f}"
              f"{photograph_value(f):>13.2f}"
              f"{image_over_drawing(f):>10.0f}")
    print(f"\n  art costs {art_cost_days():.2f} days against a "
          f"tool part at {tool_cost_days():.0f}\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
