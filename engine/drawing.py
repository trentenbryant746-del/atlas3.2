"""Why a drawing is needed, and why it is not needed for the
reason everyone assumes.

Mass production means many makers producing parts that must fit
each other, and they cannot all stand around the original. So
something has to carry the part to them. The obvious thought is
that a drawing exists because a shape is a lot of information.

It is not. Pinning one dimension to a tolerance t costs log2(1/t)
bits, so a three-dimensional part held to a billionth is 90 bits,
and engine/tradition.py says a single telling carries 11,700. A
hundred and thirty such parts fit in one story. You could read a
nanometre-tolerance specification aloud.

The constraint is somewhere else, and there are two of them.

  A SAMPLE STOPS BEING ENOUGH. Copying an object by eye gets you
  to about a tenth, which is engine/artifact.BASE_TOL. Below
  that, handing someone the original does not let them make
  another one, and a NUMBER has to travel instead of a thing.

  A DRAWING IS A SECOND LITERACY. You can speak a number but you
  cannot speak a shape. A projection is a convention, and a
  convention is worth nothing unless the person at the other end
  holds it too -- which is the same f-squared that
  engine/literacy.py found for writing, with the same slow start
  for the same reason.
"""

import math

from engine.artifact import (PRIMITIVES, TOL_NEEDED, BASE_TOL,
                             bootstrap, held_by_round, tolerance,
                             DIMENSION_M, gauged_precision,
                             demanded_precision, self_figuring,
                             needs_gauging)
from engine.tradition import TELL_SECONDS
from engine.civ import SPEECH_BITS_S

DIMENSIONS = 3                # a part is a solid


def bits_per_dimension(tol):
    """How many bits pin one length to a tolerance. DERIVED."""
    return math.log2(1.0 / tol)


def bits_per_part(tol, dims=DIMENSIONS):
    """A whole part, all dimensions. DERIVED."""
    return dims * bits_per_dimension(tol)


def telling_bits():
    """What one spoken story carries. DERIVED."""
    return TELL_SECONDS * SPEECH_BITS_S


def parts_per_telling(tol):
    """How many specifications fit in one story. DERIVED."""
    return telling_bits() / bits_per_part(tol)


def drawing_of(primitive):
    """A dimensioned specification. DERIVED.

    This is what a drawing actually carries: a size, how true it
    must be held, and whether anybody has to measure that or the
    process delivers it. Their geometry is ours -- a length is a
    length and a circle is a circle -- so a drawing they make is
    a drawing we can read, and none of that required telling
    them a rule.
    """
    size = DIMENSION_M.get(primitive, 0.1)
    return {
        "size m": size,
        "held to": TOL_NEEDED.get(primitive, BASE_TOL),
        "that is m": gauged_precision(primitive),
        "physics wants m": demanded_precision(primitive),
        "self figuring": self_figuring(primitive),
        "needs a drawing": needs_gauging(primitive),
        "bits": bits_per_part(TOL_NEEDED.get(primitive, BASE_TOL)),
    }


def gauged_before_measurable(primitive):
    """Does it arrive before anything could check it? DERIVED."""
    want = demanded_precision(primitive)
    if want is None:
        return None
    size = DIMENSION_M.get(primitive, 0.1)
    for i, _t, got in bootstrap():
        if primitive in got:
            have = tolerance(held_by_round(i)) * size
            return have > want
    return None


def sample_suffices(tol):
    """Can a maker copy the original by eye? DERIVED.

    Eye-and-hand copying reaches BASE_TOL. Tighter than that and
    the object stops being its own specification.
    """
    return tol >= BASE_TOL


def needs_a_drawing(primitive):
    """Does this craft need a numbered spec to travel? DERIVED.

    Two conditions, and the second was missing before. A sample
    must stop being enough, AND the accuracy must be one
    somebody has to measure -- a lapped lens is true to a
    quarter wave and nobody ever gauged it, because the process
    makes the surface conform.
    """
    if self_figuring(primitive):
        return False
    return not sample_suffices(TOL_NEEDED.get(primitive, BASE_TOL))


def first_round_needing_one():
    """When a sample stops being enough for anything. DERIVED."""
    for i, _t, got in bootstrap():
        if any(needs_a_drawing(g) for g in got):
            return i
    return None


def convention_value(fraction):
    """Worth of a shared projection at that literacy. DERIVED.

    A drawing needs a drawer AND a reader, so it serves f**2 of
    the possible pairs -- the same shape engine/literacy.py found
    for writing, and slow for the same reason.
    """
    return fraction * fraction


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("REFUTED_a_drawing_exists_because_a_shape_is_large", _bits)
    t("a_drawing_is_needed_when_a_sample_stops_being_enough", _sample)
    t("a_projection_is_a_second_literacy_and_starts_as_slowly", _conv)
    t("a_lapped_surface_beats_the_instrument_that_could_check_it", _lap)
    t("one_craft_arrives_undergauged_and_nothing_saves_it", _boiler)
    return all(x for _, x, _ in res), res


def _bits():
    """REFUTED. The obvious reason is the wrong one."""
    fine = parts_per_telling(1e-9)
    if fine < 10:
        raise ArithmeticError(f"{fine}")
    return (f"the obvious account is that a drawing exists because "
            f"a shape is a lot of information, and it is wrong by "
            f"a wide margin. Pinning one dimension to a tolerance "
            f"costs log2(1/t) bits: {bits_per_dimension(1e-3):.0f} "
            f"at a thousandth, {bits_per_dimension(1e-9):.0f} at a "
            f"billionth. A three-dimensional part at a billionth "
            f"is {bits_per_part(1e-9):.0f} bits against the "
            f"{telling_bits():.0f} a single telling carries, so "
            f"{fine:.0f} such specifications fit in one story. You "
            f"could read a nanometre tolerance aloud. Information "
            f"is not the constraint and was never going to be")


def _sample():
    r = first_round_needing_one()
    need = sorted(p for p in PRIMITIVES if needs_a_drawing(p))
    if r is None or not need:
        raise ArithmeticError("nothing needs one")
    return (f"what actually forces a drawing is that the object "
            f"stops being its own specification. Copying by eye "
            f"and hand reaches {BASE_TOL:.0e}, so above that you "
            f"hand someone the original and they make another. "
            f"Below it you cannot, and a NUMBER has to travel "
            f"instead of a thing. {len(need)} of "
            f"{len(PRIMITIVES)} crafts are tighter than a maker "
            f"can match from a sample, and the first arrives at "
            f"round {r}: {', '.join(need[:5])}... Before that "
            f"round nobody needs a drawing for anything, and no "
            f"amount of wanting to mass-produce changes it")


def _conv():
    early, late = convention_value(0.01), convention_value(0.5)
    if late / early < 100:
        raise ArithmeticError(f"{early} {late}")
    return (f"you can speak a number and you cannot speak a shape, "
            f"so a drawing needs a projection, and a projection is "
            f"a convention worth nothing unless the other end "
            f"holds it. A drawing needs a drawer AND a reader, so "
            f"it serves f**2 of the pairs: {early:.4f} at 1% "
            f"holding the convention against {late:.2f} at 50%, "
            f"{late/early:.0f}x. That is the same exponent "
            f"engine/literacy.py found for writing and it has the "
            f"same consequence -- a long useless stretch followed "
            f"by a fast one, with nothing about the technique "
            f"changing in between. A drawing is a second literacy "
            f"and it starts as slowly as the first")


def _lap():
    early = [p for p in PRIMITIVES if gauged_before_measurable(p)]
    d = drawing_of("optics")
    if "optics" not in early:
        raise ArithmeticError(f"{early}")
    return (f"a lens must be true to {d['physics wants m']:.1e} m, "
            f"a quarter of a wavelength, and the best gauging "
            f"available when it arrives is "
            f"{d['that is m']:.1e} m -- three and a half orders "
            f"short. Nobody ever machined a lens to a quarter "
            f"wave. You grind two surfaces against each other "
            f"and they conform, because a sphere is the only "
            f"shape that slides on itself in every orientation, "
            f"and the accuracy comes out of the METHOD with "
            f"nobody measuring anything. Three flats lapped in "
            f"rotation give a plane the same way and a hobbed "
            f"gear generates its own involute. "
            f"{len(early)} crafts here arrive before any "
            f"instrument could check them: {sorted(early)}. That "
            f"is why lenses precede micrometers rather than "
            f"waiting for them, and it is why these need no "
            f"drawing -- a drawing carries a number somebody has "
            f"to hit, and there is no number here")


def _boiler():
    early = [p for p in PRIMITIVES if gauged_before_measurable(p)]
    stuck = [p for p in early if not self_figuring(p)]
    if not stuck:
        raise ArithmeticError("every early craft is self-figuring")
    p0 = stuck[0]
    d = drawing_of(p0)
    short = d["that is m"] / d["physics wants m"]
    return (f"two crafts arrive before anything can check them "
            f"and only one of them is rescued by its process. "
            f"{sorted(early)} arrive early; {sorted(stuck)} is "
            f"not self-figuring, so nothing makes up the "
            f"difference. A vessel at {d['size m']:.1f} m gauged "
            f"to {d['that is m']:.0e} m against a wall thickness "
            f"the hoop stress wants held to "
            f"{d['physics wants m']:.0e} -- {short:.0f}x too "
            f"coarse, with no lapping trick available because a "
            f"wall does not grind itself against anything. A "
            f"craft in that position is not merely imprecise, it "
            f"is DANGEROUS, and the model says so before anybody "
            f"mentions that early boilers exploded. It is the "
            f"one place in the tree where a thing can be built "
            f"and cannot be verified")


if __name__ == "__main__":
    print(f"  a telling carries {telling_bits():.0f} bits\n")
    print(f"  {'tolerance':>10}{'bits/part':>11}{'per telling':>13}"
          f"{'sample enough?':>16}")
    for tol in (1e-1, 1e-2, 1e-3, 1e-6, 1e-9, 1e-10):
        print(f"  {tol:>10.0e}{bits_per_part(tol):>11.0f}"
              f"{parts_per_telling(tol):>13.0f}"
              f"{str(sample_suffices(tol)):>16}")
    print(f"\n  first round needing a drawing: "
          f"{first_round_needing_one()}\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
