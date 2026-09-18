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
                             bootstrap, held_by_round, tolerance)
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


def sample_suffices(tol):
    """Can a maker copy the original by eye? DERIVED.

    Eye-and-hand copying reaches BASE_TOL. Tighter than that and
    the object stops being its own specification.
    """
    return tol >= BASE_TOL


def needs_a_drawing(primitive):
    """Does this craft need a numbered spec to travel? DERIVED."""
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
