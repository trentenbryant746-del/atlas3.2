"""
What a star leaves behind, and what it throws off, both recorded.

engine/cosmos.py conserved mass across every stellar event and then
recorded the remnant as a NUMBER -- `"remnant": rm` -- so the ledger
knew how many solar masses stayed put and nothing about what they
became. A black hole and a white dwarf of the same mass were the
same entry. That is a real loss: the remnant is a thing with a
meaning and a future, not a mass balance.

The ejecta had the same problem from the other side. evolve()
computes a full composition, run() mixes it into the next
generation's gas, and the per-event breakdown is gone. But the
elements a star throws off ARE the answer to a long prompt -- what
is in this rock, why is there iodine in a thyroid -- and that answer
is a chain of events, each of which has to still be on the record
for the chain to be walkable.

So both halves are recorded: the remnant with its kind, the ejecta
with their elements.

THE THRESHOLD IS DERIVED, NOT LOOKED UP. The Chandrasekhar mass is
the largest a body can be and still be held up by electron
degeneracy pressure, and it follows from fundamental constants:

    M_Ch = C * (hbar c / G)^(3/2) / (mu_e m_H)^2

Computed from hbar, c, G and the hydrogen mass already available,
it comes out at 1.44 solar masses against an accepted 1.4 -- the
same kind of result as engine/nucleo.py deriving the iron peak
rather than storing it. The one piece not derived here is C, the
Lane-Emden n=3 polytrope constant, which is the numerical solution
of a differential equation this module does not solve. It is
ASSERTED and says so.

AND THE UPPER THRESHOLD IS NOT DERIVED, SO THE RULE REFUSES. Where
a neutron star becomes a black hole depends on the equation of
state of matter at nuclear density, which is not known. The
literature bounds it somewhere around 2.2 to 2.9 solar masses. A
remnant in that band is NOT classified: the module returns
"undetermined" and says why, which is the same rule engine/
isotopes.py applies when a Q-value lands inside its own error bar.
Naming it would be inventing the equation of state.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, ASSERTED = "DERIVED", "ASSERTED"
INHERITED = "DERIVED_FROM_ASSERTED"

# measured constants
HBAR = 1.054571817e-34      # J s
C_LIGHT = 2.99792458e8      # m/s
G_NEWTON = 6.67430e-11      # m^3 / (kg s^2)
M_H = 1.67262192369e-27     # kg, hydrogen (proton) mass
M_SUN = 1.98847e30          # kg
MU_E = 2.0                  # electrons per nucleon in a C/O dwarf

# ASSERTED: the Lane-Emden n=3 polytrope constant. This is the
# numerical solution of a differential equation, not a measurement
# and not something this module derives.
LANE_EMDEN_C = 3.0984
LE_SOURCE = "Lane-Emden n=3 polytrope, (sqrt(3 pi)/2) * omega_3 with omega_3 = 2.018"

# ASSERTED and UNCERTAIN: the neutron-star maximum depends on the
# nuclear equation of state, which is unknown. Both ends are carried
# so the rule can refuse between them.
TOV_LO, TOV_HI = 2.2, 2.9
TOV_SOURCE = "observational and theoretical bounds on the TOV limit"


class Fact:
    def __init__(self, value, kind, check, why):
        self.value, self.kind, self.check, self.why = value, kind, check, why

    def __str__(self):
        return f"{self.value}  [{self.kind}, {self.check}] {self.why}"


def chandrasekhar(mu_e=MU_E):
    """The white-dwarf ceiling, from constants. INVERSE-checked."""
    base = (HBAR * C_LIGHT / G_NEWTON) ** 1.5 / (mu_e * M_H) ** 2
    kg = LANE_EMDEN_C * base
    msun = kg / M_SUN
    back = (kg / LANE_EMDEN_C * (mu_e * M_H) ** 2) ** (2 / 3) * G_NEWTON \
        / C_LIGHT
    if not math.isclose(back, HBAR, rel_tol=1e-9):
        raise ArithmeticError("Chandrasekhar mass does not invert to hbar")
    return Fact(msun, INHERITED, "INVERSE",
                f"{msun:.3f} solar masses from hbar, c, G and the hydrogen "
                f"mass at mu_e={mu_e}; the polytrope constant "
                f"{LANE_EMDEN_C} is ASSERTED ({LE_SOURCE}), so this "
                f"inherits it. Accepted value 1.4")


def classify(remnant_msun, mu_e=MU_E, universe=None):
    """-> Fact. What the remnant is, or a refusal to say.

    COMPOSITION IS NOT A CONSTANT, AND THIS USED TO PRETEND IT WAS.
    mu_e was fixed at 2 -- carbon and oxygen -- so the rule returned
    a composition-specific verdict dressed as physics. M_Ch goes as
    mu_e^-2, so a hydrogen remnant in THIS universe has a ceiling of
    5.74 solar masses and a 5-solar-mass one is a white dwarf, not
    the black hole the fixed version reported. The composition
    travels with the question now.
    """
    if remnant_msun <= 0:
        raise ValueError("a remnant has positive mass")
    ch = chandrasekhar(mu_e).value if universe is None else \
        universe.chandrasekhar(mu_e)
    if remnant_msun < ch:
        return Fact("white_dwarf", INHERITED, "EXTERNAL",
                    f"{remnant_msun:.2f} < {ch:.2f} solar masses at "
                    f"mu_e={mu_e:g}, so electron degeneracy holds it up")
    # THE UPPER THRESHOLD COMES FROM DATA, NOT FROM THIS FILE.
    # TOV_LO/TOV_HI were my asserted 2.2-2.9. engine/eos.py derives
    # the band from observed pulsars and GW170817 and gets 2.08-2.3
    # -- 69% narrower, and from measurements rather than from someone
    # deciding how confident to be. Use it when it is available and
    # fall back to the asserted band only if it is not.
    try:
        from engine import eos
        return eos.classify(remnant_msun)
    except Exception:
        pass
    if remnant_msun >= TOV_HI:
        return Fact("black_hole", INHERITED, "EXTERNAL",
                    f"{remnant_msun:.2f} >= {TOV_HI} solar masses, past any "
                    f"proposed neutron-star maximum, so nothing known holds "
                    f"it up")
    if remnant_msun < TOV_LO:
        return Fact("neutron_star", INHERITED, "EXTERNAL",
                    f"{remnant_msun:.2f} is above the Chandrasekhar mass "
                    f"{ch:.2f} at mu_e={mu_e:g} and below {TOV_LO}, so "
                    f"neutron degeneracy holds it up")
    return Fact("undetermined", ASSERTED, "NONE",
                f"{remnant_msun:.2f} solar masses falls in the {TOV_LO}-"
                f"{TOV_HI} band where the neutron-star maximum is not "
                f"known; naming it would be inventing the nuclear equation "
                f"of state ({TOV_SOURCE})")


# ASSERTED: the initial-final mass relation. How much core a star of
# a given birth mass builds is the output of stellar-evolution
# modelling, not something derivable here, so the anchors are
# asserted with their source and interpolated between. What is NOT
# asserted is the decision made on top of them -- that is the two
# degeneracy limits, and it is the same decision at every mass.
IFMR = ((1.0, 0.55), (3.0, 0.75), (8.0, 1.35), (12.0, 1.55),
        (20.0, 1.95), (25.0, 2.6), (40.0, 8.0), (100.0, 30.0))
IFMR_SOURCE = "initial-final mass relation, stellar-evolution models"


def core_mass(progenitor_msun):
    """The degenerate core a star of this birth mass leaves behind."""
    if progenitor_msun <= 0:
        raise ValueError("a star has positive mass")
    pts = IFMR
    if progenitor_msun <= pts[0][0]:
        return Fact(pts[0][1], ASSERTED, "NONE",
                    f"below {pts[0][0]} solar masses the relation is "
                    f"extrapolated, so the core mass is taken as its "
                    f"lowest anchor ({IFMR_SOURCE})")
    if progenitor_msun >= pts[-1][0]:
        return Fact(pts[-1][1], ASSERTED, "NONE",
                    f"above {pts[-1][0]} solar masses, taken as the "
                    f"highest anchor ({IFMR_SOURCE})")
    for (m0, c0), (m1, c1) in zip(pts, pts[1:]):
        if m0 <= progenitor_msun <= m1:
            f = (progenitor_msun - m0) / (m1 - m0)
            c = c0 + f * (c1 - c0)
            return Fact(c, ASSERTED, "NONE",
                        f"{c:.2f} solar masses of core, interpolated "
                        f"between the {m0}->{c0} and {m1}->{c1} anchors "
                        f"({IFMR_SOURCE})")
    raise ArithmeticError("initial-final mass relation has a gap")


def from_progenitor(progenitor_msun):
    """-> Fact. What a star of this BIRTH mass leaves, and why.

    This is the rule rather than a lookup, and it is one rule at
    every mass: a star builds a degenerate core, and what holds that
    core up decides what it becomes.

        core < Chandrasekhar      electrons hold it -> white dwarf
        core >= Chandrasekhar     electrons cannot; it collapses
          collapsed < TOV         neutrons hold it -> neutron star
          collapsed >= TOV        nothing known holds it -> black hole

    A one-solar-mass star does not leave a neutron star because its
    core never reaches the Chandrasekhar mass -- not because of
    anything about which stars happen to be in a simulation. The
    threshold is derived from hbar, c and G, so the reason is the
    same physics wherever it is asked.
    """
    c = core_mass(progenitor_msun)
    k = classify(c.value)
    return Fact(k.value, k.kind, k.check,
                f"a {progenitor_msun:g} solar-mass star leaves a "
                f"{c.value:.2f} solar-mass core; {k.why}")


# ------------------------------------------------- other universes
class Universe:
    """A universe is a set of constants. The rule is the same in all.

    Nothing about the remnant rule is special to ours: M_Ch follows
    from hbar, c, G and the composition, so scaling any of them
    scales the boundary and the whole stellar population changes with
    it. Measured exponents, by doubling each in turn:

        hbar   +1.5      M_Ch ~ (hbar c / G)^(3/2) / (mu_e m_H)^2
        c      +1.5
        G      -1.5
        mu_e   -2.0

    Those are exact, not fitted -- scaling() re-measures them and the
    check requires them to come out at the analytic values. So a
    universe with eight times our G has a Chandrasekhar mass of 0.06
    solar masses and essentially no white dwarfs; one with a quarter
    of it is full of them. Same rule, different universe, different
    complexity to generate over.
    """

    def __init__(self, hbar=1.0, c=1.0, G=1.0, name="ours"):
        self.hbar, self.c, self.G, self.name = hbar, c, G, name

    def chandrasekhar(self, mu_e=MU_E):
        return (LANE_EMDEN_C
                * ((HBAR * self.hbar) * (C_LIGHT * self.c)
                   / (G_NEWTON * self.G)) ** 1.5
                / ((mu_e * M_H) ** 2) / M_SUN)

    def __repr__(self):
        return (f"Universe({self.name}: hbar x{self.hbar:g}, c x{self.c:g}, "
                f"G x{self.G:g}, M_Ch {self.chandrasekhar():.3f})")


OURS = Universe()


def scaling(universe=OURS):
    """Re-measure the exponents rather than asserting them."""
    base = universe.chandrasekhar()
    out = {}
    for name, kw in (("hbar", {"hbar": 2}), ("c", {"c": 2}), ("G", {"G": 2})):
        u = Universe(hbar=universe.hbar, c=universe.c, G=universe.G)
        setattr(u, name, getattr(u, name) * 2)
        out[name] = math.log2(u.chandrasekhar() / base)
    out["mu_e"] = math.log2(universe.chandrasekhar(MU_E * 2) / base)
    return out


def record(star_id, progenitor_msun, remnant_msun, ejecta, ejected_msun,
           epoch):
    """The whole event: what stayed, what left, and what each is."""
    k = classify(remnant_msun)
    parts = sorted(((el, f) for el, f in ejecta.items() if f > 0),
                   key=lambda r: -r[1])
    return {
        "star": star_id,
        "epoch": epoch,
        "progenitor_msun": progenitor_msun,
        "remnant_msun": remnant_msun,
        "remnant_kind": k.value,
        "remnant_why": k.why,
        "ejected_msun": ejected_msun,
        # the elements broken off, each with the mass that left. This
        # is what a long prompt walks back along.
        "ejecta": [{"element": el, "fraction": f,
                    "msun": f * ejected_msun} for el, f in parts],
        "conserved": abs((remnant_msun + ejected_msun)
                         - progenitor_msun) < 1e-9,
    }


def ledger(seed="universe-0", generations=4, stars_per_gen=3, dilution=9.0):
    """Every stellar death in a universe, with remnant and ejecta."""
    from engine import cosmos
    stars, _gas, _old = cosmos.run(generations=generations, seed=seed,
                                   stars_per_gen=stars_per_gen,
                                   dilution=dilution)
    out = []
    for s in stars:
        ej, em, rm, ep = cosmos.evolve(s)
        out.append(record(s.sid, s.mass, rm, ej, em, ep))
    return out


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("chandrasekhar", _ch)
    t("classification", _cls)
    t("refuses_the_unknown_band", _refuse)
    t("progenitor_rule", _prog)
    t("composition_matters", _comp)
    t("scaling_exponents", _scale)
    t("other_universes", _univ)
    t("every_death_recorded", _rec)
    t("ejecta_conserved", _ej)
    return all(o[1] for o in out), out


def _ch():
    v = chandrasekhar().value
    if not (1.3 < v < 1.5):
        raise ArithmeticError(f"{v:.3f} is nowhere near the accepted 1.4")
    return (f"{v:.3f} solar masses derived from hbar, c, G, m_H; accepted "
            f"1.4, so the derivation is {abs(v-1.4)/1.4:.1%} out")


def _cls():
    want = {0.6: "white_dwarf", 1.8: "neutron_star", 5.0: "black_hole",
            30.0: "black_hole"}
    for m, k in want.items():
        got = classify(m).value
        if got != k:
            raise ArithmeticError(f"{m} solar masses -> {got}, wanted {k}")
    return f"{len(want)} remnants classified: {sorted(set(want.values()))}"


def _refuse():
    """Refuse inside the band ACTUALLY in force, not the one I asserted.

    This tested 2.3/2.5/2.8 against the asserted 2.2-2.9. Once
    engine/eos.py narrowed the band from observations to 2.08-2.3,
    2.5 became a correct black hole and the stale check called that
    a failure. A check pinned to a superseded constant reports
    progress as a regression.
    """
    from engine import eos
    lo, hi = eos.band().value
    inside = [lo + (hi - lo) * f for f in (0.1, 0.5, 0.9)]
    for m in inside:
        f = classify(m)
        if f.value != "undetermined":
            raise ArithmeticError(f"{m:.2f} was named {f.value} inside the "
                                  f"{lo}-{hi} band")
    for m in (lo - 0.05, hi + 0.05):
        if classify(m).value == "undetermined":
            raise ArithmeticError(f"{m:.2f} is outside {lo}-{hi} and was "
                                  f"still refused")
    return (f"{len(inside)} remnants inside the observational band "
            f"{lo}-{hi} refused; either side of it decided. The asserted "
            f"{TOV_LO}-{TOV_HI} is superseded and kept only as a fallback")


def _prog():
    """The rule must give all three outcomes from birth mass alone."""
    got = {}
    for m in (1, 2, 5, 8, 10, 15, 20, 25, 40, 80):
        got[m] = from_progenitor(m).value
    kinds = {v for v in got.values()}
    if not {"white_dwarf", "neutron_star", "black_hole"} <= kinds:
        raise ArithmeticError(f"the rule never produces some outcome: {got}")
    ch = chandrasekhar().value
    for m, k in got.items():
        c = core_mass(m).value
        if (c < ch) != (k == "white_dwarf"):
            raise ArithmeticError(
                f"{m} Msun: core {c:.2f} against Chandrasekhar {ch:.2f} "
                f"disagrees with the verdict {k}")
    line = ", ".join(f"{m}->{k.split('_')[0]}" for m, k in got.items())
    return (f"birth mass decides it through the core and the two "
            f"degeneracy limits: {line}")


def _comp():
    """The same remnant, two compositions, two verdicts."""
    co = classify(5.0, mu_e=2.0).value
    h = classify(5.0, mu_e=1.0).value
    if co == h:
        raise ArithmeticError("composition changed nothing, but M_Ch goes "
                              "as mu_e^-2")
    return (f"a 5.0 solar-mass remnant is a {co} at mu_e=2 and a {h} at "
            f"mu_e=1 -- M_Ch is {chandrasekhar(2.0).value:.2f} against "
            f"{chandrasekhar(1.0).value:.2f}. Same universe, and the "
            f"composition decides it")


def _scale():
    want = {"hbar": 1.5, "c": 1.5, "G": -1.5, "mu_e": -2.0}
    got = scaling()
    for k, v in want.items():
        if abs(got[k] - v) > 1e-9:
            raise ArithmeticError(f"{k} exponent {got[k]:.4f}, not {v}")
    return ("measured by doubling each constant: "
            + ", ".join(f"{k} {got[k]:+.1f}" for k in want)
            + " -- the analytic exponents, re-measured not asserted")


def _univ():
    us = [Universe(name="ours"), Universe(G=8, name="strong gravity"),
          Universe(G=0.125, name="weak gravity"),
          Universe(hbar=4, name="large hbar")]
    rows = []
    for u in us:
        m = u.chandrasekhar()
        rows.append(f"{u.name} M_Ch={m:.3f}")
    ch = [u.chandrasekhar() for u in us]
    if len(set(round(c, 6) for c in ch)) != len(ch):
        raise ArithmeticError("different constants gave the same boundary")
    v = classify(5.0, universe=us[2]).value
    if v != "white_dwarf":
        raise ArithmeticError(f"in weak gravity a 5 Msun remnant is {v}")
    return ("; ".join(rows) + "; and in weak gravity a 5 solar-mass "
            "remnant is a white dwarf, which in ours is a black hole")


def _rec():
    L = ledger()
    if not L:
        raise ArithmeticError("no deaths recorded")
    kinds = sorted({r["remnant_kind"] for r in L})
    withej = sum(1 for r in L if r["ejecta"])
    return (f"{len(L)} stellar deaths, every one carrying a remnant kind "
            f"{kinds} and {withej} carrying an ejecta breakdown")


def _ej():
    L = ledger()
    bad = [r["star"] for r in L if not r["conserved"]]
    if bad:
        raise ArithmeticError(f"mass not conserved for {bad}")
    tot = sum(sum(e["msun"] for e in r["ejecta"]) for r in L)
    want = sum(r["ejected_msun"] for r in L)
    if not math.isclose(tot, want, rel_tol=1e-9):
        raise ArithmeticError(f"ejecta masses sum to {tot}, not {want}")
    return (f"{len(L)} events: remnant + ejecta = progenitor in every one, "
            f"and the per-element masses sum to the ejected mass "
            f"({tot:.2f} solar masses total)")


if __name__ == "__main__":
    print(chandrasekhar())
    print()
    for m in (0.6, 1.2, 1.8, 2.5, 5.0, 30.0):
        print(f"  remnant {m:>5} Msun -> {classify(m)}")
    print()
    for m in (1, 8, 15, 22, 25, 40):
        print(f"  star    {m:>5} Msun -> {from_progenitor(m)}")
    print()
    L = ledger()
    print(f"{len(L)} stellar deaths recorded")
    for r in L[:3]:
        top = ", ".join(f"{e['element']} {e['msun']:.2f}"
                        for e in r["ejecta"][:4])
        print(f"  {r['star']:<7} {r['progenitor_msun']:6.2f} Msun -> "
              f"{r['remnant_kind']:<12} {r['remnant_msun']:5.2f} + "
              f"{r['ejected_msun']:5.2f} ejected  [{top}]")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:26}{d}")
    print("\nall:", ok)
