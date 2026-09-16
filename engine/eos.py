"""
The nuclear equation of state: not known, but bounded, and the
bounding is a derivation.

engine/remnants.py refuses in the 2.2-2.9 solar-mass band because
where a neutron star becomes a black hole depends on how matter
behaves at several times nuclear density, and that is an open
problem in physics. No one knows it. It cannot be derived here and
it cannot be derived anywhere yet -- it is measured, or it is
bracketed.

BUT REFUSING IS NOT THE END OF THE ROAD, AND THE BAND WAS TOO WIDE.
The limit is squeezed from both sides by observations, and each
squeeze is a one-line inference this repo can make and check:

    FROM BELOW, by existence. A neutron star that EXISTS with mass M
    proves every equation of state softer than M is wrong, so
    M_TOV >= M. PSR J0740+6620 is 2.08 solar masses and is a pulsar,
    therefore the maximum is at least 2.08. That is a derivation
    from an observation, and the observation is the asserted part.

    FROM ABOVE, by a merger that collapsed. GW170817's remnant did
    not survive as a neutron star, and the tidal deformability
    measured in the inspiral rules out the stiffest equations of
    state. Both point to a maximum near 2.2-2.3.

So the band this repo should refuse in is not 2.2-2.9. It is about
2.08-2.3, which is less than half as wide, and the narrowing came
from data rather than from anyone deciding to be more confident.

WHAT IS STILL REFUSED, AND WHY THAT IS CORRECT. Inside the narrowed
band the answer remains undetermined, because the bounds are
bounds: they say the answer is in there, not where. A remnant of
2.15 solar masses is genuinely unclassifiable today, and the honest
output is to say so and name what would settle it -- a heavier
confirmed pulsar raises the floor, a better tidal measurement
lowers the ceiling.

CAN IT BE PROBED HERE? Not derived, but CONSTRAINED, and that is
what probe() does: take a candidate maximum mass, and report which
observations exclude it. An equation of state that cannot hold 2.08
solar masses is refuted by a pulsar that exists. That is the same
shape as engine/isotopes.py scoring itself against KNOWN_STABLE --
the data is held as a fixture and the rule is scored against it,
never fitted to it.
"""
from __future__ import annotations

DERIVED, ASSERTED = "DERIVED", "ASSERTED"


class Fact:
    def __init__(self, value, kind, check, why):
        self.value, self.kind, self.check, self.why = value, kind, check, why

    def __str__(self):
        return f"{self.value}  [{self.kind}, {self.check}] {self.why}"


# ASSERTED, and held as a FIXTURE: measured objects the rule is
# scored against and never fitted to. Each is (name, mass, sigma,
# what it is, what it constrains, source).
OBSERVATIONS = (
    ("PSR J0740+6620", 2.08, 0.07, "pulsar", "floor",
     "NICER + Shapiro delay mass measurement"),
    ("PSR J0348+0432", 2.01, 0.04, "pulsar", "floor",
     "white-dwarf companion spectroscopy"),
    ("PSR J1614-2230", 1.91, 0.02, "pulsar", "floor",
     "Shapiro delay"),
    ("GW170817 remnant", 2.30, 0.10, "collapsed merger", "ceiling",
     "no long-lived neutron-star remnant; tidal deformability"),
)


def floor():
    """The heaviest thing observed to BE a neutron star. DERIVED."""
    cands = [o for o in OBSERVATIONS if o[4] == "floor"]
    best = max(cands, key=lambda o: o[1])
    return Fact(best[1], DERIVED, "EXTERNAL",
                f"{best[0]} is {best[1]} +/- {best[2]} solar masses and is "
                f"a {best[3]}, so any maximum below {best[1]} is refuted by "
                f"something that exists ({best[5]})")


def ceiling():
    """The lightest constraint that says it collapsed. DERIVED."""
    cands = [o for o in OBSERVATIONS if o[4] == "ceiling"]
    best = min(cands, key=lambda o: o[1])
    return Fact(best[1], DERIVED, "EXTERNAL",
                f"{best[0]} at {best[1]} +/- {best[2]}: {best[5]}")


def band():
    """-> (lo, hi). Where the maximum is, and how wide that still is."""
    lo, hi = floor().value, ceiling().value
    if lo > hi:
        raise ArithmeticError(
            f"observations are inconsistent: a {lo} solar-mass neutron "
            f"star exists but the ceiling is {hi}")
    return Fact((lo, hi), DERIVED, "SPAN",
                f"the maximum is between {lo} and {hi} solar masses -- "
                f"{hi - lo:.2f} wide, against the 0.70 the module refused "
                f"in before the observations were consulted")


def probe(candidate_max):
    """Which observations refute this proposed maximum mass?"""
    out = []
    for name, m, sig, what, side, src in OBSERVATIONS:
        if side == "floor" and candidate_max < m:
            out.append((name, f"a {what} of {m} solar masses exists, and "
                              f"this maximum cannot hold it"))
        if side == "ceiling" and candidate_max > m:
            out.append((name, f"{src}, which this maximum contradicts"))
    return out


def classify(remnant_msun):
    """-> Fact. Neutron star, black hole, or still undetermined."""
    lo, hi = band().value
    if remnant_msun < lo:
        return Fact("neutron_star", DERIVED, "EXTERNAL",
                    f"{remnant_msun:.2f} is below {lo}, and a "
                    f"{lo}-solar-mass neutron star is observed, so nothing "
                    f"about the unknown equation of state is needed")
    if remnant_msun > hi:
        return Fact("black_hole", DERIVED, "EXTERNAL",
                    f"{remnant_msun:.2f} is above {hi}, past every "
                    f"equation of state the observations leave open")
    return Fact("undetermined", ASSERTED, "NONE",
                f"{remnant_msun:.2f} is inside {lo}-{hi}, where the "
                f"equation of state is not known. A confirmed pulsar "
                f"heavier than {remnant_msun:.2f} would settle it as a "
                f"neutron star; a tighter tidal measurement would settle "
                f"it the other way")


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("band_from_data", lambda: band().why)
    t("narrower_than_asserted", _narrow)
    t("probe_refutes", _probe)
    t("still_refuses_inside", _inside)
    t("observations_consistent", _consist)
    return all(o[1] for o in out), out


def _narrow():
    from engine.remnants import TOV_LO, TOV_HI
    lo, hi = band().value
    old, new = TOV_HI - TOV_LO, hi - lo
    if new >= old:
        raise ArithmeticError(f"observations did not narrow anything: "
                              f"{new:.2f} vs {old:.2f}")
    return (f"the asserted band was {TOV_LO}-{TOV_HI} ({old:.2f} wide); "
            f"observations give {lo}-{hi} ({new:.2f} wide), "
            f"{1 - new/old:.0%} narrower and from data")


def _probe():
    soft = probe(1.8)
    stiff = probe(2.6)
    if not soft:
        raise ArithmeticError("a 1.8 maximum was not refuted, but heavier "
                              "neutron stars are observed")
    if not stiff:
        raise ArithmeticError("a 2.6 maximum was not refuted")
    return (f"a proposed maximum of 1.8 is refuted by {len(soft)} observed "
            f"pulsars; one of 2.6 is refuted by {len(stiff)} merger "
            f"constraint(s). The data excludes, it does not derive")


def _inside():
    f = classify(2.15)
    if f.value != "undetermined":
        raise ArithmeticError(f"2.15 was named {f.value} inside the band")
    return ("2.15 solar masses is still undetermined, and the refusal now "
            "names what would settle it")


def _consist():
    lo, hi = floor().value, ceiling().value
    if lo > hi:
        raise ArithmeticError("floor above ceiling")
    return (f"{len(OBSERVATIONS)} observations, floor {lo} <= ceiling {hi}, "
            f"so no observed neutron star is heavier than the collapse "
            f"constraint allows")


if __name__ == "__main__":
    print(floor())
    print(ceiling())
    print(band())
    print()
    for m in (1.5, 2.0, 2.15, 2.5, 5.0):
        print(f"  {m:>5} Msun -> {classify(m)}")
    print()
    for c in (1.8, 2.1, 2.6):
        r = probe(c)
        print(f"  a maximum of {c}: "
              + (f"refuted by {', '.join(n for n, _w in r)}" if r
                 else "not refuted by anything on record"))
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:26}{d}")
    print("\nall:", ok)
