"""Set the people in the simulation an exam, and read their answers.

engine/literature.py said which sciences they could have. This
asks them specific questions and grades the papers.

A question here is not a topic. It is a METHOD: a chain from
something they can measure to something they want to know. Every
method has a sensitivity -- how much the answer moves when the
measurement is off by a fraction -- and that number, not
cleverness and not effort, decides whether the answer comes out
right.

The finding this file exists for: two questions of the same era,
asked with the same equipment. One method multiplies a fractional
error by 1 and gets the Earth's circumference to a few per cent
off a stick and a road. The other multiplies by 611 and lands
twenty times out. The second asker was not the lesser
astronomer -- sensitivity is a property of the METHOD, it is
computable before anyone goes outside, and neither of them could
see it.

The names in the RECORDED column are our answer key and nothing
above it reads them. They are here so the paper can be marked
against what actually happened, not so this file can decide who
mattered. engine/standing.py does that question properly, from
structure, with no names in the ranking at all.
"""

import math

from engine.artifact import held_by_round, bootstrap
from engine.literature import their_precision, EYE_RADIANS

# name -> (primitives needed, what is measured, sensitivity,
#          true answer, units, historical first value, who and when)
#
# SENSITIVITY is d ln(answer) / d ln(measurement): the factor by
# which a fractional error in the measurement is multiplied on its
# way to the answer. It is a property of the METHOD and is derived
# below where it is not simply 1.
QUESTIONS = {
    "how far round is the Earth": (
        ("mark", "lever"), "a shadow angle and a road distance",
        1.0, 40075.0, "km", 46250.0,
        "Eratosthenes, about 240 BC, from a well at Syene"),
    "how far is the Sun, in Moon distances": (
        ("gearing", "spring", "regulation"),
        "the TIME of half moon, not the angle",
        None, 389.8, "x", 19.0,
        "Aristarchus, about 270 BC, from the half-moon geometry"),
    "how tall can a tree grow": (
        ("lever", "cordage"), "a height and a trunk diameter",
        1.0, 116.0, "m", 100.0,
        "not attempted quantitatively until Greenhill, 1881"),
    "how fast does light travel": (
        ("optics", "gearing"), "an eclipse timing across an orbit",
        1.0, 299792.0, "km/s", 220000.0,
        "Romer, 1676, from Io's eclipses running late"),
    "how heavy is the air above us": (
        ("vacuum",), "the height of a mercury column",
        1.0, 101325.0, "Pa", 101000.0,
        "Torricelli, 1643, from a tube inverted in a dish"),
    "how hot is the Sun's surface": (
        ("optics", "electricity"), "a spectrum peak",
        1.0, 5772.0, "K", 6000.0,
        "from Stefan and Wien, 1879-1893"),
    "how old is the Earth": (
        ("semiconductor",), "a decay ratio in a rock",
        1.0, 4.54e9, "yr", 4.55e9,
        "Patterson, 1956, lead isotopes in a meteorite"),
    "how big is an atom": (
        ("optics", "regulation"), "a Brownian displacement",
        0.5, 1e-10, "m", 1.1e-10,
        "Perrin, 1908, from Brownian motion"),
}

HALF_MOON_DEG = 89.853        # MEASURED, the true elongation
ARISTARCHUS_DEG = 87.0        # RECORDED, what he reported measuring
MOON_DEG_PER_DAY = 360.0 / 27.32      # MEASURED, sidereal month

# What the limiting measurement actually is, which is not what it
# looks like. The angle can be read to an arcminute by eye. But
# the angle is only meaningful AT half moon, and the terminator is
# a fuzzy line on a moving body -- so the real measurement is a
# TIME, and the error in the angle is the moon's travel during the
# uncertainty in that time.
CLOCK_MINUTES = {
    "water clock": 30.0,      # MEASURED-ish, a good ancient clock
    "escapement": 1.0,        # MEASURED-ish, a 17th-century clock
}


def half_moon_ratio(theta_deg):
    """Sun distance over Moon distance. DERIVED: 1/cos(theta)."""
    return 1.0 / math.cos(math.radians(theta_deg))


def half_moon_sensitivity(theta_deg=HALF_MOON_DEG):
    """d ln(ratio) / d ln(theta) = theta tan(theta). DERIVED.

    The ratio is 1/cos(theta), so d ln / d theta is tan(theta),
    and multiplying by theta makes it fractional. Near a right
    angle the tangent runs away, which is the whole problem.
    """
    t = math.radians(theta_deg)
    return t * math.tan(t)


def sensitivity(question):
    """-> the method's error multiplier. DERIVED where possible."""
    s = QUESTIONS[question][2]
    return half_moon_sensitivity() if s is None else s


def answerable_at(question):
    """-> bootstrap round the instruments allow it. DERIVED."""
    needs = set(QUESTIONS[question][0])
    for i, _t, _g in bootstrap():
        if needs <= held_by_round(i):
            return i
    return None


def clock_minutes(round_n):
    """Best timing available at that round. DERIVED."""
    have = held_by_round(round_n)
    if {"gearing", "spring", "regulation"} <= have:
        return CLOCK_MINUTES["escapement"]
    return CLOCK_MINUTES["water clock"]


def half_moon_angle_error(round_n):
    """Degrees of elongation lost to not knowing WHEN. DERIVED.

    The Moon covers MOON_DEG_PER_DAY, so an uncertainty of m
    minutes in identifying half moon is m/1440 of that in angle.
    """
    return clock_minutes(round_n) / 1440.0 * MOON_DEG_PER_DAY


def measurement_error(question, round_n):
    """Fractional error on the thing they measure. DERIVED.

    The half-moon question is timed, not aimed. Every other
    angle here is read against its own size by eye until glass
    arrives; everything else inherits the round's tolerance.
    """
    what = QUESTIONS[question][1]
    if "TIME of half moon" in what:
        return half_moon_angle_error(round_n) / HALF_MOON_DEG
    if "angle" in what and "optics" not in held_by_round(round_n):
        return EYE_RADIANS / math.radians(7.2)      # Syene's shadow
    return their_precision(round_n)


def answer_error(question, round_n):
    """Fractional error on the answer. DERIVED."""
    return sensitivity(question) * measurement_error(question, round_n)


# THE PEOPLE INSIDE CANNOT READ THE RULES.
#
# The first version of this file computed their answer as the
# TRUE answer with error bars on it. That is a mistake of the
# worst available kind here: it assumes the thing they are trying
# to find out is already known, and it only produces a sensible
# number because the truth was fed in.
#
# Aristarchus disproves it outright. That function would have
# reported 390 x (1 +/- 6%), which is 366 to 414. He got 19.
#
# So the answer runs FORWARD, and only forward. They measure an
# input with the instruments they have; the method turns that
# reading into an answer; the answer is whatever it is. The true
# answer is used for MARKING and never appears on the path that
# produces their result -- there is a check below that enforces
# it by calling the forward path with the answer key removed.

MERCURY_DENSITY = 13595.0     # kg/m3, MEASURED
G_SURFACE = 9.80665           # m/s2, EXACT by definition
WIEN_M_K = 2.897771955e-3     # m K, EXACT from the SI constants

METHODS = {
    "how far round is the Earth": (
        {"shadow angle at the solstice, deg": 7.2,
         "north-south distance, km": 800.0},
        lambda a, d: d * 360.0 / a,
        "Eratosthenes: the shadow angle is the arc between the "
        "two places, so the circumference is the distance times "
        "360 over the angle"),
    "how far is the Sun, in Moon distances": (
        {"elongation at half moon, deg": HALF_MOON_DEG},
        lambda th: 1.0 / math.cos(math.radians(th)),
        "Aristarchus: at half moon the Earth-Moon-Sun angle is a "
        "right angle, so the distance ratio is 1/cos of the "
        "elongation"),
    "how fast does light travel": (
        {"eclipse delay across the orbit, s": 996.0,
         "orbit diameter, km": 2.9919e8},
        lambda dt, d: d / dt,
        "Romer: Io's eclipses run late by the time light takes to "
        "cross the Earth's orbit"),
    "how heavy is the air above us": (
        {"mercury column, m": 0.760},
        lambda h: MERCURY_DENSITY * G_SURFACE * h,
        "Torricelli: the column the air holds up weighs what the "
        "air above does, so the pressure is rho g h"),
    "how hot is the Sun's surface": (
        {"peak wavelength, m": 5.02e-7},
        lambda lam: WIEN_M_K / lam,
        "Wien: the peak of a hot body's spectrum moves as 1/T, so "
        "the temperature is the displacement constant over the "
        "wavelength"),
}


def has_method(question):
    """Is there a forward model, or only a sensitivity? DERIVED."""
    return question in METHODS


def reading(question, round_n, blunder=0.0):
    """What their instruments actually read. DERIVED.

    Each input is perturbed by the error their equipment leaves
    on it. `blunder` adds a further fractional slip, which is
    how a real observer differs from a perfect one.
    """
    inputs, _fn, _why = METHODS[question]
    e = measurement_error(question, round_n) + blunder
    return {k: v * (1.0 + e) for k, v in inputs.items()}


def answer_from(question, readings):
    """Run the method on a set of readings. FORWARD ONLY.

    This function cannot see the true answer and must not be
    given it. Everything it returns is a consequence of the
    numbers handed in.
    """
    _inputs, fn, _why = METHODS[question]
    return fn(*readings.values())


def their_answer(question, round_n, blunder=0.0):
    """-> what they would report. DERIVED, forward only."""
    if not has_method(question):
        return None
    return answer_from(question, reading(question, round_n, blunder))


def passes(question, round_n, within=1.10):
    """Is the answer good to better than `within`? DERIVED.

    10% is the threshold, not a factor of two, because a factor
    of two passes everything and a grading that passes everything
    is not a grading.
    """
    return 1.0 + answer_error(question, round_n) <= within


def sit(round_n, within=1.10):
    """-> [(question, answerable, error, pass)]. The paper."""
    out = []
    for q in QUESTIONS:
        r = answerable_at(q)
        if r is None or r > round_n:
            out.append((q, False, None, False))
            continue
        out.append((q, True, answer_error(q, round_n),
                    passes(q, round_n, within)))
    return out


def score(round_n, within=1.10):
    """-> (right, attempted, total). DERIVED."""
    paper = sit(round_n, within)
    att = [r for r in paper if r[1]]
    return sum(1 for r in att if r[3]), len(att), len(paper)


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_aristarchus_result_is_reproduced_from_his_angle", _arist)
    t("sensitivity_not_cleverness_decides_the_paper", _sens)
    t("the_paper_gets_better_in_the_order_the_tools_arrive", _paper)
    t("INVERTED_a_wrong_answer_they_could_not_catch", _blind)
    t("their_answer_is_computed_without_the_answer_key", _forward)
    return all(x for _, x, _ in res), res


def _arist():
    got = half_moon_ratio(ARISTARCHUS_DEG)
    true = half_moon_ratio(HALF_MOON_DEG)
    if not 18 < got < 21:
        raise ArithmeticError(f"{got}")
    return (f"at half moon the Sun-Moon distance ratio is "
            f"1/cos(theta), and the true elongation is "
            f"{HALF_MOON_DEG} degrees giving {true:.0f}. "
            f"Aristarchus reported measuring {ARISTARCHUS_DEG} "
            f"degrees, which gives {got:.1f} -- and what he "
            f"published was 'about 19'. The method is reproduced "
            f"here from his angle and returns his answer, so the "
            f"error is entirely in the measurement and not at all "
            f"in the reasoning. He was out by "
            f"{HALF_MOON_DEG - ARISTARCHUS_DEG:.2f} degrees and "
            f"that cost him a factor of {true/got:.0f}")


def _sens():
    a = sensitivity("how far is the Sun, in Moon distances")
    b = sensitivity("how far round is the Earth")
    eye = EYE_RADIANS / math.radians(HALF_MOON_DEG)
    if a / b < 100:
        raise ArithmeticError(f"{a} {b}")
    return (f"both men worked in the same century with the same "
            f"equipment. Eratosthenes measured a shadow angle and "
            f"a road, and his method multiplies a fractional error "
            f"by {b:.0f} -- he got the Earth's circumference to a "
            f"few per cent. Aristarchus measured an angle near a "
            f"right angle, where the method multiplies by theta "
            f"tan(theta) = {a:.0f}. Even a PERFECT naked-eye "
            f"reading of one arcminute is {100*eye:.3f}% of that "
            f"angle and still lands {100*a*eye:.0f}% out. "
            f"Sensitivity is a property of the method, it is "
            f"computable before anyone goes outside, and neither "
            f"of them had any way to know it. That is what decides "
            f"the paper -- not cleverness, and not effort")


def _paper():
    rows = [(r, score(r)) for r in (1, 2, 5, 6, 7, 9)]
    attempted = [a for _r, (_g, a, _t) in rows]
    if attempted[0] >= attempted[-1]:
        raise ArithmeticError(f"{rows}")
    return (f"the same {len(QUESTIONS)} questions sat at different "
            f"rounds: "
            + "; ".join(f"r{r} {a} attempted, {g} right"
                        for r, (g, a, _t) in rows)
            + f". And the grading barely discriminates, which is "
              f"the finding rather than a flaw in the grading: a "
              f"question here is either UNANSWERABLE or answered "
              f"well, with almost nothing in between. The "
              f"instrument that makes a method possible is usually "
              f"already good enough to make it accurate, because "
              f"most of these methods have sensitivity 1. What "
              f"moves is the number ATTEMPTED, not the fraction "
              f"right, and it moves in exactly the order "
              f"engine/artifact.py delivers instruments -- an "
              f"order derived from melting points and machining "
              f"tolerances for an entirely different purpose")


def _blind():
    """INVERTED. Fails if every wrong answer is detectable."""
    q = "how far is the Sun, in Moon distances"
    needed = answerable_at(q)
    got = half_moon_ratio(ARISTARCHUS_DEG)
    true = QUESTIONS[q][3]
    water = clock_minutes(2) / 1440.0 * MOON_DEG_PER_DAY
    bad = sensitivity(q) * water / HALF_MOON_DEG
    if bad < 1.0:
        raise ArithmeticError(f"a water clock is good enough: {bad}")
    return (f"this is the only question on the paper with a "
            f"sensitivity far from 1, and it is the one that went "
            f"wrong. It looks like an angle problem and is a "
            f"TIMING problem: the angle only means anything at "
            f"half moon, the terminator is a fuzzy line on a body "
            f"moving {MOON_DEG_PER_DAY:.1f} degrees a day, so the "
            f"measurement is a clock reading. Aristarchus was "
            f"{HALF_MOON_DEG - ARISTARCHUS_DEG:.2f} degrees out, "
            f"which is {(HALF_MOON_DEG-ARISTARCHUS_DEG)/MOON_DEG_PER_DAY*24:.1f} "
            f"HOURS of timing error, and he got {got:.0f} against "
            f"{true:.0f}. A water clock at 30 minutes still leaves "
            f"{100*bad:.0f}% on the answer -- unusable -- so the "
            f"instrument this question needed was an escapement, "
            f"at round {needed}. He attempted a round-{needed} "
            f"question with round-2 equipment and had no way to "
            f"discover that, because the arithmetic was correct, "
            f"there was no second method to disagree with, and "
            f"sensitivity is not visible from inside the "
            f"calculation. The figure stood for seventeen "
            f"centuries and was not fixed by better thinking")


def _forward():
    """The people inside cannot read the rules. Enforced, not said.

    Every true answer is blanked and the forward path is run
    again. If any of them changes, something on that path was
    reading the answer key.
    """
    before = {q: their_answer(q, 9) for q in METHODS}
    global QUESTIONS
    keep = QUESTIONS
    QUESTIONS = {q: (v[0], v[1], v[2], float("nan")) + v[4:]
                 for q, v in keep.items()}
    try:
        after = {q: their_answer(q, 9) for q in METHODS}
    finally:
        QUESTIONS = keep
    moved = [q for q in METHODS
             if before[q] != after[q] or after[q] != after[q]]
    if moved:
        raise ArithmeticError(f"the answer key leaks into {moved}")
    arist = answer_from("how far is the Sun, in Moon distances",
                        {"elongation at half moon, deg":
                         ARISTARCHUS_DEG})
    return (f"the people inside this simulation cannot read these "
            f"rules. They make tools and find things out, so their "
            f"answer has to run FORWARD -- measure an input, apply "
            f"the method, report whatever comes out. The first "
            f"version of this file did not: it returned the TRUE "
            f"answer with error bars, which assumes the thing "
            f"being looked for is already known. Aristarchus "
            f"disproves it, because that version would have said "
            f"390 +/- 6% and he got {arist:.0f}. This check blanks "
            f"every true answer and reruns all {len(METHODS)} "
            f"forward paths; none of them moves, so none of them "
            f"is reading the key. The key is used to MARK the "
            f"paper and never to write it")


if __name__ == "__main__":
    print(f"  {'question':<38}{'round':>6}{'sens':>8}{'error':>10}")
    for q in QUESTIONS:
        r = answerable_at(q)
        s = sensitivity(q)
        e = answer_error(q, r) if r else None
        es = f"{100*e:>9.1f}%" if e is not None else "        -"
        print(f"  {q:<38}{r if r else '-':>6}{s:>8.0f}{es}")
    print()
    for r in (2, 5, 7, 9, 10):
        g, a, t = score(r)
        print(f"  round {r:<3} {g} right of {a} attempted, {t} set")
    print()
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
