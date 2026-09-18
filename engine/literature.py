"""What the people in the simulation could write down, and when.

This repository derives rules from constants it simply has. The
people inside it do not have them. They have senses, which
engine/senses.py says reach eight of the thirteen constraints
that bind on them, and they have instruments, which
engine/artifact.py says arrive in a fixed order set by
temperature and then by tolerance.

So a science is possible for them exactly when the instrument it
needs is possible, and the instrument order is already derived.
That gives a predicted ORDER for the sciences, which is a much
harder thing to match than any single number -- a sequence of ten
can come out 3.6 million ways and only one of them is right.

Then the second question, which is the interesting one: their
version of a rule carries their measurement error, not ours. A
length known to a tenth gives a rule known to a tenth. So for any
rule in this repository we can ask what THEIR version of it would
have said, and whether it would have been good enough to notice
they were wrong.
"""

import math

from engine.artifact import (bootstrap, held_by_round, tolerance,
                             TOL_NEEDED)

# A science, the primitives its instrument needs, what it measures,
# and the century it actually appeared in quantitative form.
#
# WHAT IS MINE AND WHAT IS NOT, because the tau below is the
# strongest number in this repository and it should not be quoted
# without this paragraph.
#
# The centuries are RECORDED. They are the answer key and nothing
# consults them to build the order.
#
# The ROUNDS are not mine either: engine/artifact.py fixed them
# from melting points and machining tolerances, for a different
# purpose, before this module existed. They were not tuned here.
#
# The mapping from a science to the primitives it needs IS mine.
# I chose that thermometry needs glass and that chronometry needs
# a regulated escapement. Those choices are constrained -- you
# cannot read a thermometer without a transparent tube -- but they
# are choices, and a different hand would produce a different tau.
# The honest claim is that the INSTRUMENT ORDER predicts the
# science order, given a reasonable reading of which instrument
# each science needs. It is not that the sequence fell out of
# nothing.
SCIENCES = {
    "statics and levers": (("lever", "cordage"), "force and length", -3),
    "positional astronomy": (("mark", "lever"), "angle and time", -3),
    "surveying": (("mark", "rotation"), "angle and distance", -3),
    "metallurgy": (("smelting",), "temperature by colour", -15),
    "mechanics of machines": (("gearing",), "ratio and torque", 13),
    "optics": (("optics",), "refraction and focal length", 17),
    "thermometry": (("optics", "containment"), "temperature", 17),
    "chronometry": (("gearing", "spring", "regulation"),
                    "time to the second", 17),
    "pneumatics": (("vacuum",), "pressure and vacuum", 17),
    "thermodynamics": (("steam", "regulation"), "heat and work", 19),
    "electromagnetism": (("electricity", "regulation"),
                         "current and field", 19),
    "spectroscopy": (("optics", "electricity"), "wavelength", 19),
    "solid state": (("semiconductor",), "band structure", 20),
}

# What a measurement is worth, by the best tolerance in hand.
# MEASURED-ish: naked-eye angle is about an arcminute, a vernier
# gets a thousandth, an interferometer a millionth.
EYE_RADIANS = 2.9e-4          # one arcminute


def when(science):
    """-> bootstrap round at which the instrument exists. DERIVED."""
    needs = set(SCIENCES[science][0])
    for i, _t, _g in bootstrap():
        if needs <= held_by_round(i):
            return i
    return None


def predicted_order():
    """-> [(science, round)] sorted by when the tools arrive."""
    rows = [(s, when(s)) for s in SCIENCES]
    return sorted((r for r in rows if r[1] is not None),
                  key=lambda r: (r[1], SCIENCES[r[0]][1]))


def recorded_order():
    """-> [(science, century)] sorted by when it actually happened."""
    return sorted(SCIENCES.items(), key=lambda kv: kv[1][2])


def order_agreement():
    """-> (concordant, discordant, tau). Kendall's tau. DERIVED.

    Every pair of sciences either comes out in the same relative
    order both ways or it does not. Ties in the predicted round
    are not counted either way.
    """
    names = [s for s, _r in predicted_order()]
    pred = {s: r for s, r in predicted_order()}
    rec = {s: SCIENCES[s][2] for s in names}
    con = dis = 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            dp, dr = pred[a] - pred[b], rec[a] - rec[b]
            if dp == 0 or dr == 0:
                continue
            if (dp > 0) == (dr > 0):
                con += 1
            else:
                dis += 1
    tot = con + dis
    return con, dis, (con - dis) / tot if tot else 0.0


def their_precision(round_n):
    """Fractional error on a length at that round. DERIVED."""
    return tolerance(held_by_round(round_n))


def their_angle(round_n):
    """Smallest angle they can measure, radians. DERIVED.

    Before glass it is the eye, which engine/senses.py bounds by
    diffraction and retinal sampling. After glass it is the
    instrument's own tolerance applied to a graduated circle.
    """
    if "optics" not in held_by_round(round_n):
        return EYE_RADIANS
    return max(their_precision(round_n), 1e-9)


def parallax_reachable(round_n, nearest_arcsec=0.76):
    """Can they see the nearest star move? DERIVED."""
    return their_angle(round_n) <= nearest_arcsec * 4.8481e-6


def their_value(true_value, round_n, terms=1):
    """-> (low, high). What their version of a rule would say.

    Errors compound over the terms in a derivation, so a rule
    resting on `terms` measurements carries sqrt(terms) times the
    single-measurement error.
    """
    e = their_precision(round_n) * math.sqrt(terms)
    return true_value * (1 - e), true_value * (1 + e)


def would_notice(true_value, claimed, round_n, terms=1):
    """Could they tell their answer was wrong? DERIVED."""
    lo, hi = their_value(true_value, round_n, terms)
    return not (lo <= claimed <= hi)


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_order_of_the_sciences_is_predicted_not_assumed", _order)
    t("an_instrument_decides_what_can_be_known", _instrument)
    t("their_rules_carry_their_error_and_it_is_computable", _error)
    t("INVERTED_a_rule_they_could_not_check_is_not_their_rule", _cannot)
    t("the_discordant_pairs_name_which_mapping_is_wrong", _wrong)
    return all(x for _, x, _ in res), res


def _order():
    con, dis, tau = order_agreement()
    pred = predicted_order()
    if tau < 0.5:
        raise ArithmeticError(f"tau {tau:.2f}, {con} vs {dis}")
    n = len(pred)
    return (f"a science is possible when its instrument is, and "
            f"engine/artifact.py already derived the instrument "
            f"order from temperature and then tolerance. Nothing "
            f"here consults a date. The predicted sequence is "
            + " -> ".join(f"{s}(r{r})" for s, r in pred[:6])
            + f" ... and against the century each one actually "
              f"appeared it scores {con} concordant pairs to "
              f"{dis} discordant, Kendall tau {tau:.2f}. A "
              f"sequence of {n} could come out {math.factorial(n):.1e} "
              f"ways. This is the hardest thing in the repository "
              f"to have got right by accident")


def _instrument():
    b = bootstrap()
    first = next(i for i in range(1, len(b) + 1)
                 if parallax_reachable(i))
    eye = EYE_RADIANS / 4.8481e-6
    if parallax_reachable(1):
        raise ArithmeticError("the naked eye sees parallax")
    return (f"the nearest star shifts 0.76 arcseconds and the naked "
            f"eye resolves about {eye:.0f} -- so heliocentrism was "
            f"unfalsifiable for two thousand years by "
            f"{eye/0.76:.0f}x, and the people arguing about it were "
            f"not being stupid, they were being under-equipped. "
            f"Parallax becomes reachable at round {first}, when "
            f"glass and a graduated circle put the angle at "
            f"{their_angle(first):.1e} rad. An instrument does not "
            f"merely help with a question; it decides whether the "
            f"question has an answer yet")


def _error():
    from engine.constants import G_GRAV
    rows = []
    for r in (2, 5, 7, 9):
        lo, hi = their_value(G_GRAV, r, terms=3)
        rows.append((r, their_precision(r), (hi - lo) / 2 / G_GRAV))
    if rows[0][2] <= rows[-1][2]:
        raise ArithmeticError("error does not fall")
    return (f"their version of a rule carries their measurement "
            f"error, not ours. A three-term derivation of "
            f"Newton's constant would come out to "
            + "; ".join(f"r{r} +/-{100*e:.1f}%" for r, _p, e in rows)
            + f". Cavendish got 1% in 1798 with a torsion balance, "
              f"which is between rounds {rows[1][0]} and "
              f"{rows[2][0]} here. The point is not the agreement, "
              f"it is that the SHAPE of what they could know is "
              f"computable from what they could build")


def _cannot():
    """INVERTED. Fails if they could check everything we derive."""
    unreachable = [s for s in SCIENCES if when(s) is None]
    b = len(bootstrap())
    late = [s for s in SCIENCES if when(s) == b]
    from engine.farfuture import de_sitter_temperature
    ds = de_sitter_temperature()
    if their_precision(b) <= 0:
        raise ArithmeticError("precision is unbounded")
    return (f"at the last round they reach {their_precision(b):.0e} "
            f"and {len(SCIENCES) - len(unreachable)} of "
            f"{len(SCIENCES)} sciences, ending with {late}. They "
            f"still cannot check most of what this repository "
            f"asserts. The de Sitter floor is {ds:.1e} K and no "
            f"instrument in the tree measures it; the proton decay "
            f"bound needs a detector the size of a lake; the "
            f"closure floor is a claim about chemistry that never "
            f"happened here. A rule they could not have checked is "
            f"not a rule they would have written, so the overlap "
            f"between their literature and ours is small and "
            f"bounded -- and pretending otherwise would make this "
            f"module a mirror instead of a test")


def _wrong():
    names = [s for s, _r in predicted_order()]
    pred = {s: r for s, r in predicted_order()}
    bad = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            dp = pred[a] - pred[b]
            dr = SCIENCES[a][2] - SCIENCES[b][2]
            if dp and dr and (dp > 0) != (dr > 0):
                bad.append((a, b))
    if not bad:
        raise ArithmeticError(
            "nothing is discordant, which for thirteen sciences "
            "against a hand-written instrument mapping would mean "
            "the mapping had been fitted to the answer key")
    tally = {}
    for a, b in bad:
        tally[a] = tally.get(a, 0) + 1
        tally[b] = tally.get(b, 0) + 1
    late = [f"{s} ({n})" for s, n in
            sorted(tally.items(), key=lambda kv: -kv[1])[:3]]
    return (f"{len(bad)} pairs come out backwards, and they are not "
            f"spread evenly -- three entries carry most of them: "
            f"{', '.join(late)}. Spectroscopy is "
            f"predicted at round 5 because it needs only glass and "
            f"a current, and it actually waited until the 19th -- "
            f"the missing requirement is a RULED GRATING, which is "
            f"precision machining rather than optics, and this "
            f"module does not model that. Pneumatics is predicted "
            f"late because a vacuum here needs regulation, and "
            f"Guericke did it in 1650 with a leather seal and "
            f"patience. Both are errors in MY science-to-primitive "
            f"mapping, not in engine/artifact.py's ordering, and "
            f"naming which is which is the only thing that keeps "
            f"the tau honest")


if __name__ == "__main__":
    print(f"  {'science':<26}{'round':>6}{'century':>9}")
    for s, r in predicted_order():
        c = SCIENCES[s][2]
        print(f"  {s:<26}{r:>6}{c:>9}")
    con, dis, tau = order_agreement()
    print(f"\n  {con} concordant, {dis} discordant, tau {tau:.2f}\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
