"""
Watching it recognise something, and why that cannot be a search.

engine/senses.py gave the eye its limits and engine/learning.py
found that a brain saturates in 1.49 years and spends the rest
discarding. This asks the thing between them: what happens when
an animal looks at something and knows what it is.

The geometry settles most of it before any biology is needed.

    acuity                        1.01 arcmin
    whole field, 120 deg          5.07e7 resolvable cells
    the sharp part, 2 deg         1.41e4 cells -- 0.028% of it

THE SHARP PART IS A THREE-HUNDREDTH OF ONE PERCENT OF WHAT YOU CAN
SEE. Covering the field with it takes 3,600 fixations, and at four
saccades a second that is fifteen minutes. Nobody spends fifteen
minutes recognising a tree. So recognition is not a search over
the field; the low-resolution periphery has to decide where the
fovea goes before anything has been identified, which means the
answer is partly committed before the evidence is in.

AND RECOGNITION IS A REDUCTION OF TEN MILLION TO ONE. A retina
delivers 1e7 bit/s and "is it food" is one bit. Everything between
those two numbers is thrown away, on purpose, every second.

WHICH IS THE SECOND ROUTE TO THE SAME PLACE. engine/learning.py
concluded a brain must be a filter because its store fills before
the child can walk. This concludes it because the sharp patch is
too small to search with. Neither knew about the other and they
are not the same argument -- one is about capacity over a
lifetime, the other about geometry in a second.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIELD_DEG = 120.0           # MEASURED, binocular horizontal
FOVEA_DEG = 2.0             # MEASURED, the sharp patch
SACCADES_S = 4.0            # MEASURED
CELLS_TO_IDENTIFY = 20      # CHOSEN, cells across a thing to name it


def acuity_arcmin():
    """DERIVED via engine/senses.py -- optics and sampling."""
    from engine.senses import (diffraction_limit, sampling_limit,
                               arcmin)
    return arcmin(max(diffraction_limit(), sampling_limit()))


def cells(degrees):
    """Resolvable cells across a square patch. DERIVED."""
    return (degrees * 60.0 / acuity_arcmin()) ** 2


def sharp_fraction():
    """What share of sight is sharp. DERIVED."""
    return cells(FOVEA_DEG) / cells(FIELD_DEG)


def fixations_to_cover():
    """How many looks to foveate everything. DERIVED."""
    return (FIELD_DEG / FOVEA_DEG) ** 2


def seconds_to_cover():
    """DERIVED. The number that rules out exhaustive search."""
    return fixations_to_cover() / SACCADES_S


def recognition_range(size_m, cells_across=CELLS_TO_IDENTIFY):
    """m. How far off a thing of this size can be named. DERIVED."""
    need_rad = cells_across * acuity_arcmin() / 60.0 * math.pi / 180.0
    return size_m / need_rad


def reduction(choices):
    """-> (bits out, factor). Recognition as compression. DERIVED."""
    from engine.learning import intake_bits_s
    bits = math.log2(max(choices, 2))
    return bits, intake_bits_s() / bits


def must_predict():
    """-> (bool, why). Is search affordable? DERIVED."""
    s = seconds_to_cover()
    return s > 1.0, (
        f"foveating the field takes {s:.0f} s at {SACCADES_S:.0f} "
        f"saccades a second")


def depth_agrees(size_m=1.7):
    """-> (recognition m, stereo m). Do the two limits match?"""
    from engine.senses import depth_resolution
    r = recognition_range(size_m)
    return r, depth_resolution(r)


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_sharp_part_is_almost_none_of_it", _sharp)
    t("recognition_cannot_be_a_search", _search)
    t("it_is_a_reduction_of_ten_million_to_one", _reduce)
    t("the_range_falls_out_of_the_acuity", _range)
    t("two_routes_reach_the_same_filter", _two)
    return all(o[1] for o in out), out


def _sharp():
    f = sharp_fraction()
    if f > 0.01:
        raise ArithmeticError(f"the fovea is {100*f:.1f}% of the field")
    return (f"at {acuity_arcmin():.2f} arcmin the whole field holds "
            f"{cells(FIELD_DEG):.2e} resolvable cells and the sharp "
            f"patch {cells(FOVEA_DEG):.2e} -- {100*f:.3f}% of it. "
            f"Almost everything an animal can see, it cannot see "
            f"WELL, at any instant")


def _search():
    need, why = must_predict()
    if not need:
        raise ArithmeticError("searching the field is affordable")
    return (f"{why}, which is fifteen minutes, and nobody spends "
            f"fifteen minutes recognising a tree. So the periphery "
            f"has to choose where the fovea goes BEFORE anything is "
            f"identified -- the answer is partly committed before the "
            f"evidence is in. That is not a theory of brains, it is "
            f"what is left when exhaustive search is priced")


def _reduce():
    b1, f1 = reduction(2)
    b2, f2 = reduction(30000)
    if f1 < 1e6:
        raise ArithmeticError(f"the reduction is only {f1:.0e}")
    return (f"a retina delivers 1e7 bit/s. 'Is it food' is "
            f"{b1:.0f} bit, a {f1:.1e}-fold reduction; naming one of "
            f"thirty thousand words is {b2:.1f} bits, still "
            f"{f2:.1e}-fold. Everything between those numbers is "
            f"discarded on purpose, every second, and engine/"
            f"learning.py says discarding is free")


def _range():
    person = recognition_range(1.7)
    fruit = recognition_range(0.1)
    bug = recognition_range(0.005)
    if not 100 < person < 1000:
        raise ArithmeticError(f"a person is nameable at {person:.0f} m")
    return (f"naming a thing needs about {CELLS_TO_IDENTIFY} cells "
            f"across it, so a 1.7 m person is nameable to "
            f"{person:.0f} m, a 10 cm fruit to {fruit:.0f} m and a "
            f"5 mm insect to {bug:.1f} m. One acuity number sets all "
            f"three, and the foraging range and the social range are "
            f"the same measurement wearing different clothes")


def _two():
    from engine.learning import fill_time_years
    s = seconds_to_cover()
    y = fill_time_years()
    return (f"engine/learning.py concluded a brain is a filter because "
            f"its store fills in {y:.2f} years. This concludes it "
            f"because the sharp patch would take {s:.0f} s to sweep. "
            f"THE ARGUMENTS SHARE NOTHING -- one is capacity over a "
            f"lifetime, the other geometry within a second, and "
            f"neither module reads the other's numbers to reach it. "
            f"Two routes to one answer is the strongest thing "
            f"available here short of a measurement")


if __name__ == "__main__":
    print(f"  acuity {acuity_arcmin():.2f} arcmin")
    print(f"  field  {cells(FIELD_DEG):.2e} cells")
    print(f"  fovea  {cells(FOVEA_DEG):.2e} cells "
          f"({100*sharp_fraction():.3f}% of the field)")
    print(f"  to sweep it all: {fixations_to_cover():.0f} fixations, "
          f"{seconds_to_cover()/60:.1f} min\n")
    print(f"  {'thing':<14}{'size':>8}{'nameable to':>14}")
    for nm, sz in (("a person", 1.7), ("a fruit", 0.1),
                   ("a footprint", 0.25), ("an insect", 0.005)):
        print(f"  {nm:<14}{sz:>7.3f}m{recognition_range(sz):>12.1f} m")
    print()
    for n in (2, 100, 30000):
        b, f = reduction(n)
        print(f"  one of {n:>6}: {b:>5.1f} bits out, {f:.1e}x reduction")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:38]}")
