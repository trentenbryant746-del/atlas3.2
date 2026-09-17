"""
Every domain has its own energy scale, and therefore its own bar.

engine/nucleo.py measures three error bars because a mass, an alpha
step and a beta step are different questions about one formula.
That was the first half of the idea. The second half is bigger: a
protein is not a nucleus, and a bar expressed in MeV means nothing
about a fold.

    nuclear binding        ~8 MeV per nucleon
    chemical bond          ~4 eV
    hydrogen bond          ~0.2 eV
    thermal noise at 310 K ~0.027 eV

That is seven orders of magnitude. A 1.2 MeV bar is forty-five
million times a hydrogen bond, so applying it to folding would
refuse every fold ever; and a folding bar applied to nuclei would
accept every decay including the ones that do not happen. Neither
error is subtle and both come from treating "the error bar" as one
thing.

SO A BAR IS A PROPERTY OF A DOMAIN, NOT OF THE REPO. This registry
holds one per domain, with how it was obtained, and refuses for a
domain that has not established one -- which is the honest state of
protein folding here.

WHAT SETS THE SCALE IN EACH CASE IS DIFFERENT, AND THAT IS THE
POINT. A nuclear bar is the formula's residual against measurement.
A folding bar is not: the question is not whether the model's energy
is accurate in some absolute sense but whether two folds are FARTHER
APART THAN THERMAL NOISE, because a gap under kT is not a preference,
it is a coin flip the molecule re-tosses continuously.

THERMAL NOISE IS DERIVED. kT at body temperature from Boltzmann's
constant, which is exact by definition of the kelvin, and the
electronvolt from the elementary charge, which is exact by
definition of the coulomb. Nothing here is fitted.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, ASSERTED, REFUSED = "DERIVED", "ASSERTED", "REFUSED"

# Exact by definition since the 2019 SI redefinition: the kelvin is
# defined by fixing Boltzmann's constant and the coulomb by fixing
# the elementary charge. These are not measurements with an error.
K_B = 1.380649e-23          # J/K, exact
E_CHARGE = 1.602176634e-19  # C, exact
T_BODY = 310.0              # K, a choice of where to evaluate, stated
T_ROOM = 298.0


def kT_eV(T=T_BODY):
    """Thermal energy, in eV. DERIVED from two exact constants."""
    return K_B * T / E_CHARGE


class Scale:
    """A domain, its energy scale, and its bar -- WITH ITS UNIT.

    The unit is not decoration. A nuclear bar is an energy because
    there is a measured mass to take a residual against. A folding
    bar is a RATE because there is no measured fold, so the only
    thing that can be counted is how often the answer survives a
    defensible change to the model. Recording the unit is what stops
    the two from ever being compared, which is the failure this
    whole module exists to prevent.
    """

    def __init__(self, name, typical_eV, bar, unit, kind, why):
        self.name, self.typical_eV = name, typical_eV
        self.bar, self.unit, self.kind, self.why = bar, unit, kind, why

    @property
    def bar_eV(self):
        """Only ever an energy. None when the bar is not one."""
        return self.bar if self.unit == "eV" else None

    def __str__(self):
        if self.bar is None:
            b = "refused"
        elif self.unit == "eV":
            b = f"{self.bar:.3e} eV"
        else:
            b = f"{self.bar:.3f} ({self.unit})"
        return f"{self.name:<18}{self.typical_eV:.3e} eV   bar {b}"


MEV = 1e6


def registry():
    """-> {domain: Scale}. Built fresh so measured bars stay live."""
    from engine.nucleo import error_bar
    out = {}
    for dom, kind in (("nuclear-mass", "mass"), ("nuclear-alpha", "decay"),
                      ("nuclear-beta", "beta")):
        try:
            v, why = error_bar(kind)
            out[dom] = Scale(dom, 8e6, v * MEV, "eV", DERIVED, why)
        except Exception as e:
            out[dom] = Scale(dom, 8e6, None, "eV", REFUSED, str(e))

    out["thermal"] = Scale(
        "thermal", kT_eV(), kT_eV(), "eV", DERIVED,
        f"kT at {T_BODY:g} K from Boltzmann's constant and the "
        f"elementary charge, both exact by definition -- the scale "
        f"below which any energy difference is re-tossed continuously")

    out["chemical-bond"] = Scale(
        "chemical-bond", 4.0, None, "eV", REFUSED,
        "a covalent bond is a few eV, but nothing here computes bond "
        "energies, so there is no residual to measure and no bar to "
        "state. engine/valence.py counts bonds; it does not weigh them")

    try:
        from engine.folding import model_bar
        rate, fwhy = model_bar()
        out["protein-fold"] = Scale(
            "protein-fold", 0.2, rate, "survival rate", DERIVED, fwhy)
    except Exception as e:
        out["protein-fold"] = Scale(
            "protein-fold", 0.2, None, "survival rate", REFUSED, str(e))

    try:
        from engine.terraform import error_bar as _pbar
        v, pwhy = _pbar()
        out["planetary-climate"] = Scale("planetary-climate", 0.026, v,
                                         "K", DERIVED, pwhy)
    except Exception as e:
        out["planetary-climate"] = Scale("planetary-climate", 0.026, None,
                                         "K", REFUSED, str(e))

    out["protein-fold-eV"] = Scale(
        "protein-fold-eV", 0.2, None, "eV", REFUSED,
        "engine/folding.py scores folds in dimensionless products of a "
        "carbon-to-polar ratio, which has no physical scale at all. Until "
        "a contact is worth a stated number of eV nothing here can say "
        "whether two folds differ by more than thermal noise, and any "
        "number would be invented. The domain HAS a bar -- see "
        "protein-fold -- but it is a rate, and a rate is not an energy")
    return out


def bar(domain):
    """-> (eV, why). Refuses for a domain with no established bar."""
    r = registry()
    if domain not in r:
        raise KeyError(f"no scale for {domain!r}; known: {sorted(r)}")
    s = r[domain]
    if s.bar is None:
        raise ValueError(f"{domain} has no error bar: {s.why}")
    return s.bar, s.unit, s.why


def spread():
    """How many orders of magnitude the domains cover. DERIVED."""
    import math
    v = [s.typical_eV for s in registry().values()]
    return math.log10(max(v) / min(v))


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("scales_span_orders", _span)
    t("thermal_is_derived", _kt)
    t("no_domain_borrows_another", _borrow)
    t("folding_bar_is_a_rate_not_an_energy", _fold)
    t("nuclear_bars_are_measured", _nuc)
    t("units_never_mix", _units_never_mix)
    return all(o[1] for o in out), out


def _span():
    s = spread()
    if s < 5:
        raise ArithmeticError(f"only {s:.1f} orders -- the domains are "
                              f"not as different as claimed")
    r = registry()
    lo = min(r.values(), key=lambda x: x.typical_eV)
    hi = max(r.values(), key=lambda x: x.typical_eV)
    return (f"{s:.1f} orders of magnitude from {lo.name} at "
            f"{lo.typical_eV:.2e} eV to {hi.name} at {hi.typical_eV:.2e} "
            f"-- a bar from one is meaningless in the other")


def _kt():
    a, b = kT_eV(T_ROOM), kT_eV(T_BODY)
    if not (0.02 < a < 0.03 and b > a):
        raise ArithmeticError(f"kT came out {a:.4f} / {b:.4f} eV")
    return (f"kT is {a:.4f} eV at {T_ROOM:g} K and {b:.4f} at "
            f"{T_BODY:g} K, from two constants that are exact by "
            f"definition -- no measurement, no fit")


def _borrow():
    """A domain must not be handed another domain's number."""
    r = registry()
    bars = [(n, s.bar_eV) for n, s in r.items() if s.bar_eV is not None]
    for n, v in bars:
        for m, w in bars:
            if n != m and v == w and not (n.startswith("nuclear")
                                          and m.startswith("nuclear")):
                raise ArithmeticError(f"{n} and {m} share a bar")
    nuc = [v for n, v in bars if n.startswith("nuclear")]
    th = r["thermal"].bar_eV
    ratio = min(nuc) / th
    return (f"{len(bars)} domains have a bar and none is borrowed; the "
            f"tightest nuclear one is {ratio:.2e} times thermal noise, so "
            f"using it on a fold would refuse every fold there is")


def _fold():
    """Folding has a bar, it is not an energy, and it never poses as one."""
    v, u, _w = bar("protein-fold")
    if u == "eV":
        raise ArithmeticError("a folding energy bar was produced from "
                              "dimensionless units")
    if not 0.0 <= v <= 1.0:
        raise ArithmeticError(f"a survival rate of {v}")
    try:
        bar("protein-fold-eV")
    except ValueError:
        pass
    else:
        raise ArithmeticError("an eV bar for folding came from nothing")
    return (f"folding's bar is {v:.2f} as a {u} and refuses to be an "
            f"energy -- {100*(1-v):.0f}% of its exact minima move when a "
            f"choice the chemistry does not settle is made the other way")


def _units_never_mix():
    """The whole point: no comparing a rate to an energy."""
    r = registry()
    have = {n: s.unit for n, s in r.items() if s.bar is not None}
    units = set(have.values())
    if len(units) < 2:
        raise ArithmeticError(f"every bar is in {units} -- if the kinds of "
                              f"bar do not differ, nothing was learned")
    if len(units) < 3:
        raise ArithmeticError(f"only {len(units)} kinds of bar: {units}")
    by = {}
    for n, u in have.items():
        by.setdefault(u, []).append(n)
    return ("; ".join(f"{u}: {', '.join(sorted(v))}"
                      for u, v in sorted(by.items()))
            + " -- three kinds of claim. A residual in MeV over many "
              "nuclides, a residual in K over two bodies, and a rate "
              "against another model where nothing was ever measured. "
              "The unit is what stops them being compared")


def _nuc():
    rows = []
    for d in ("nuclear-mass", "nuclear-alpha", "nuclear-beta"):
        v, u, _w = bar(d)
        if u != "eV":
            raise ArithmeticError(f"{d} came back in {u}, not an energy")
        rows.append(f"{d.split('-')[1]} {v/MEV:.2f} MeV")
    return ("measured, not typed: " + ", ".join(rows)
            + " -- three questions about one formula, three answers")


if __name__ == "__main__":
    for s in registry().values():
        print("  " + str(s))
    print(f"\n  spread: {spread():.1f} orders of magnitude")
    print(f"  kT at {T_BODY:g} K = {kT_eV():.4f} eV")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{d[:84]}")
    print("\nall:", ok)
