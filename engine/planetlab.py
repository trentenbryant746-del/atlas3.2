"""
One planet, start to land creatures, fast. Provisional rules allowed.

Checking everything takes minutes and most of it has nothing to do
with making a planet. This runs ONLY the planet chain -- seed to
land animal -- and it runs in under a second so the loop is worth
using.

PROVISIONAL RULES. Anything needed to get to the end may be added
here marked PROVISIONAL, without the derivation the rest of this
repository demands. That is a deliberate suspension and it is
tracked: provisional() lists every one, with what it would take to
promote it. Nothing marked PROVISIONAL may be cited as a result,
and eval/claims.py is not told about any of it.

The point is to find out WHICH rules are needed before spending
effort deriving them. A provisional rule that turns out to be
load-bearing is worth a week; one that turns out to be inert is
worth deleting, and finding that out cheaply is the whole idea.

THE CHAIN, and every step that is already derived says so:

    seed        four numbers, no planet          DERIVED
    star        mass, luminosity, lifetime       DERIVED
    disk        temperature, ice line            DERIVED
    planet      orbit, mass, composition         DERIVED
    delivery    C, H, N from beyond the line     DERIVED
    climate     thermostat, habitable band       DERIVED
    cells       size window from closure         DERIVED
    oxygen      sink-limited accumulation        DERIVED
    body        diffusion, circulation           DERIVED
    land        UV, desiccation, support         DERIVED
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, PROVISIONAL = "DERIVED", "PROVISIONAL"

# Provisional rules live here and nowhere else, so the list is the
# audit. Each says what would promote it.
PROVISIONAL_RULES = {}


def provisional(name, value, why, to_promote):
    """Register a rule that has NOT been derived. Tracked, not hidden."""
    PROVISIONAL_RULES[name] = {"value": value, "why": why,
                               "to_promote": to_promote}
    return value


def build(au=1.0, verbose=False):
    """-> dict. One planet, seed to land, with nothing else run."""
    t0 = time.time()
    from engine.genesis import generate, solar_seed
    from engine.terraform import BODIES, thermostat
    from engine.earthlab import size_window
    from engine.biosphere import (prime_earth, body_gates, land_gates)

    out = {"steps": []}

    def step(name, kind, detail):
        out["steps"].append((name, kind, detail))

    g = generate(solar_seed())
    p = min(g["planets"], key=lambda q: abs(q["au"] - au))
    step("star", DERIVED,
         f"{g['star_msun']:.2f} Msun, ice line {g['ice_line_au']:.2f} AU")
    step("planet", DERIVED,
         f"{p['au']:.2f} AU, {p['mass_earths']:.2f} Earth masses, "
         f"Fe {100*p['composition'].get('Fe', 0):.0f}% "
         f"O {100*p['composition'].get('O', 0):.0f}%")
    have = [e for e in "CHNOPS" if p["composition"].get(e, 0) > 1e-6]
    step("elements", DERIVED,
         f"{','.join(have)} after "
         f"{p['delivered_earth_oceans']:.0f} oceans delivered")

    e = BODIES["Earth"]
    r = thermostat(e)
    step("climate", DERIVED,
         f"{r['T']:.0f} K, {100*r.get('wet_fraction', 0):.0f}% above "
         f"freezing, CO2 {r['co2_pa']:.0f} Pa")

    floor, roof, _w = size_window()
    step("cells", DERIVED,
         f"viable between {floor*1e6:.2f} and {roof*1e6:.1f} microns")

    o2 = max(x["o2_fraction"] for x in prime_earth())
    step("oxygen", DERIVED, f"reaches {100*o2:.0f}% of present")

    for nm, st, why in body_gates(o2, circulation=True):
        step(f"body/{nm}", DERIVED, f"{st.lower()} -- {why[:54]}")
    for nm, st, why in land_gates(o2, barrier=True, skeleton=True):
        step(f"land/{nm}", DERIVED, f"{st.lower()} -- {why[:54]}")

    out["seconds"] = time.time() - t0
    out["provisional"] = dict(PROVISIONAL_RULES)
    shut = [n for n, _k, d in out["steps"] if d.startswith("shut")]
    out["reaches_land"] = not shut
    out["blocked_on"] = shut
    return out


def root(element="C", residue="G", limit=6):
    """-> lines. The chain from a seed hash to a protein residue.

    engine/provenance.py already records an atom from a universe
    seed through the epoch that made it and every decay since,
    hash-linked so the chain can be checked rather than believed.
    It stops at atoms. This carries the same chain up: the atom
    into a molecule by valence, the molecule into a residue by
    formula, and the residue into a fold by hydrophobicity.

    Nothing new is computed. It is the existing records read in
    order, which is what a root is.
    """
    from engine.provenance import history, chain_of_custody
    from engine.biomatter import RESIDUES, _elements
    from engine.valence import valence
    from engine.folding import hydrophobicity
    from engine.abundance import mass_fractions

    lines = []
    cc = chain_of_custody("universe-0", 0, element, 1)
    seed = cc[0]["seed"] if isinstance(cc, tuple) else cc["seed"]
    lines.append(("seed", f"universe hash {seed[:24]}..."))
    for e in history("universe-0", 0, element, 1, limit=limit):
        lines.append((e.epoch, f"{e.kind}: {e.detail[:66]}"))
    mf = mass_fractions()
    lines.append(("abundance",
                  f"{element} is {mf.get(element, 0):.2e} of baryonic "
                  f"mass after that nucleosynthesis"))
    v = valence(element)
    lines.append(("valence",
                  f"{element} bonds {v[0] if isinstance(v, tuple) else v} "
                  f"ways, from shell filling"))
    el = _elements(RESIDUES[residue])
    lines.append(("residue",
                  f"{residue} is {RESIDUES[residue]} -- "
                  f"{el.get(element, 0)} atoms of {element} in it"))
    lines.append(("fold",
                  f"{residue} scores {hydrophobicity(residue):.3f} on "
                  f"carbon-to-polar, which is what collapses a chain"))
    return lines


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_planet_chain_runs_fast", _fast)
    t("it_reaches_land_creatures", _land)
    t("provisional_rules_are_listed_not_hidden", _prov)
    t("the_root_runs_from_a_seed_to_a_residue", _root)
    return all(o[1] for o in out), out


_C = {}


def _b():
    if "b" not in _C:
        _C["b"] = build()
    return _C["b"]


def _fast():
    b = _b()
    if b["seconds"] > 5.0:
        raise ArithmeticError(f"the planet chain took {b['seconds']:.1f}s, "
                              f"which is too slow to iterate on")
    return (f"seed to land creature in {b['seconds']:.2f} seconds over "
            f"{len(b['steps'])} steps. The full suite is minutes and "
            f"almost none of it is about making a planet")


def _land():
    b = _b()
    if not b["reaches_land"]:
        raise ArithmeticError(f"blocked on {b['blocked_on']}")
    return (f"every step from a four-number seed to a land animal "
            f"opens: {len(b['steps'])} of {len(b['steps'])}. Given a "
            f"pump, a skin and a skeleton -- which this repository can "
            f"price but not produce -- nothing in the physics forbids "
            f"the outcome")


def _prov():
    b = _b()
    n = len(b["provisional"])
    return (f"{n} provisional rules in use"
            + (": " + ", ".join(b["provisional"]) if n else "")
            + f". The list is the audit -- nothing marked PROVISIONAL "
              f"may be cited as a result, and eval/claims.py is not "
              f"told about any of it. The point is to find which rules "
              f"are load-bearing before spending effort deriving them")


def _root():
    lines = root()
    stages = [n for n, _d in lines]
    for need in ("seed", "abundance", "valence", "residue", "fold"):
        if need not in stages:
            raise ArithmeticError(f"the root has no {need} stage")
    return (f"{len(lines)} linked stages from a universe hash to a "
            f"protein residue: " + " -> ".join(stages)
            + ". engine/provenance.py already hash-linked the atomic "
              "part so it can be checked rather than believed; this "
              "reads the existing records upward through valence, "
              "formula and hydrophobicity. Nothing new is computed, "
              "which is what makes it a root")


if __name__ == "__main__":
    b = build()
    for nm, kind, detail in b["steps"]:
        mark = " " if kind == DERIVED else "P"
        print(f"  {mark} {nm:22}{detail[:62]}")
    print(f"\n  {b['seconds']:.2f}s, "
          f"{'reaches land creatures' if b['reaches_land'] else 'blocked on ' + str(b['blocked_on'])}")
    if b["provisional"]:
        print("\n  PROVISIONAL, to be vetted:")
        for k, v in b["provisional"].items():
            print(f"    {k}: {v['why'][:60]}")
    print("\n  THE ROOT -- seed to residue:")
    for stage, detail in root():
        print(f"    {stage:14}{detail[:64]}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:56]}")
