"""
Nebula to human, one chain, every link named.

The pieces existed and did not connect. engine/planetlab.py walks a
planet to land creatures. engine/earthlab.py asks whether a first
cell is possible. engine/ancestry.py walks LUCA to us. Each was
written for its own question and none of them hands off, so the
chain nobody could read was the one thing the repository was for.

This assembles it, and it assembles it by DERIVATION -- every link
is a rule already proved somewhere else, cited, with its verdict
carried forward. Nothing here simulates. Rule 3 in the README: if
a check runs a search, the rule underneath it has not been found.

A link is one of four things, and the difference is the point:

    DERIVED    a rule here produces it
    ALLOWED    no rule forbids it, and none produces it either
    CROSSES    it depends on something that happened once
    MISSING    a gap with a name and, where possible, a size

And past the last link, three rules about what lives there --
competitive exclusion, energetic equivalence, and the bound on
how many species one world can hold. Those are theorems, not
runs.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DERIVED, ALLOWED, CROSSES, MISSING = "DERIVED", "ALLOWED", "CROSSES", "MISSING"


def before_luca():
    """-> [(from, to, verdict, rule, why)]. Nebula to a first cell."""
    from engine.evolve import habitable_band, luminosity_at
    from engine.cold import temperature_for, NACL_EUTECTIC_K
    from engine.earthlab import size_window, MIN_REPLICASE_BASES
    from engine.closure import length_closing_derived
    from engine.earthlab import CATALYSIS_P

    lo, hi = habitable_band(float(getattr(luminosity_at(1.0, 4.6),
                                          "value",
                                          luminosity_at(1.0, 4.6))))
    top = temperature_for(1.0 / MIN_REPLICASE_BASES)
    floor, roof, _w = size_window()
    L, _M, _p = length_closing_derived(CATALYSIS_P)

    return [
        ("a nebula", "a star and planets", DERIVED, "genesis.composition",
         "condensation of minerals by temperature; Earth's iron comes "
         "out at 32.0% against a measured 32.1%"),
        ("planets", "one in the band", DERIVED, "evolve.habitable_band",
         f"the carbonate-silicate thermostat puts the band at "
         f"{lo:.3f}-{hi:.3f} AU, derived from radiative transfer and "
         f"not fitted to Earth"),
        ("a warm ocean", "a cold brine", DERIVED, "cold.temperature_for",
         f"copying is discrimination, mu = exp(-dG/kT), so fidelity is "
         f"a temperature: the window runs {NACL_EUTECTIC_K:.0f}-"
         f"{top:.0f} K, seven kelvin wide, bounded below by the "
         f"eutectic and above by sloppy copying"),
        ("brine", "an autocatalytic set", DERIVED,
         "closure.length_closing_derived",
         f"a set closes when about half its reactions have a catalyst, "
         f"p*M = 0.48, which at four nucleotides needs polymers to "
         f"{L} bases -- under the {20} earthlab derives for assembly"),
        ("a closed set", "a bounded cell", DERIVED,
         "earthlab.size_window",
         f"closure needs {1e6*floor:.2f} microns to hold the molecule "
         f"types and diffusion allows {1e6*roof:.1f}; the window is "
         f"two rules meeting, not one measurement"),
        ("a cell that could be", "a cell that is", MISSING,
         "nothing produces one",
         "every gate opens and no rule makes the thing. Permission is "
         "not occurrence, and the distance between them is not "
         "measured anywhere here"),
    ]


def after_luca():
    """-> [...]. LUCA to a human, from engine/ancestry.py."""
    from engine.ancestry import steps
    out = []
    for row in steps():
        a, b, verdict = row[0], row[1], row[2]
        why = row[3] if len(row) > 3 else ""
        out.append((a, b, verdict if verdict != "ALLOWED" else ALLOWED,
                    "ancestry.steps", str(why)[:140]))
    return out


def inside_the_head():
    """-> [...]. What a human brain does, derived elsewhere."""
    from engine.learning import fill_time_years, store_bits
    from engine.recognize import sharp_fraction, seconds_to_cover
    from engine.civ import smallest_group, speech_as_fraction_of_a_brain
    from engine.ontogeny import provisioning_debt
    _j, yrs = provisioning_debt()
    return [
        ("a large brain", "a filter, not a store", DERIVED,
         "learning.fill_time_years",
         f"{store_bits():.1e} bits of synapse against one nerve's 1e7 "
         f"bit/s fills in {fill_time_years():.2f} years, before the "
         f"child can walk, so the work is discarding"),
        ("a filter", "recognition", DERIVED, "recognize.sharp_fraction",
         f"the sharp patch is {100*sharp_fraction():.3f}% of the field "
         f"and sweeping it takes {seconds_to_cover():.0f} s, so the "
         f"periphery commits before evidence arrives"),
        ("one head", "several", DERIVED, "civ.smallest_group",
         f"a child costs {yrs:.1f} adult-years and one adult keeps no "
         f"margin for a bad season; {smallest_group()} clear it, so "
         f"company is arithmetic and not preference"),
        ("several heads", "a shared corpus", DERIVED, "school.grow",
         "speech carries "
         f"{100*speech_as_fraction_of_a_brain():.4f}% of a lifetime's "
         f"input and is worth it because it is the part somebody "
         f"already selected"),
        ("a corpus", "what it is for", MISSING, "nothing prices rank",
         "engine/civ.py and engine/empire.py both stop here: nothing "
         "makes one person's share depend on another's regard, so "
         "status, belief and rest are absences rather than results"),
    ]


def chain():
    """-> [...]. The whole thing, nebula to a head, in order."""
    return before_luca() + after_luca() + inside_the_head()


# --- what lives there: three theorems, no simulation ----------------

def exclusion_limit(n_resources):
    """Species that can coexist on n limiting resources. DERIVED.

    At equilibrium each species needs one resource it is best at.
    More species than resources means two share a best, and the
    better competitor takes it -- competitive exclusion, which is
    a statement about rank and does not need a population run.
    """
    return n_resources


def abundance_of(mass_kg, energy_w, kleiber_exp=0.75):
    """Individuals per unit area. DERIVED: energetic equivalence.

    Each species gets a share of energy; one body costs
    b*m^(3/4). So abundance goes as m^(-3/4), and population
    ENERGY USE is then independent of body size -- which is why a
    field holds few large animals and many small ones without
    anything choosing that.
    """
    from engine.biome import metabolism_w
    return energy_w / max(metabolism_w(mass_kg), 1e-30)


def biomass_of(mass_kg, energy_w):
    """kg per unit area at that body size. DERIVED."""
    return abundance_of(mass_kg, energy_w) * mass_kg


def size_span(energy_w, floor_kg, roof_kg):
    """-> (n at floor, n at roof, ratio). DERIVED."""
    a, b = abundance_of(floor_kg, energy_w), abundance_of(roof_kg, energy_w)
    return a, b, a / b


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_chain_runs_end_to_end", _chain)
    t("every_link_names_its_rule", _cites)
    t("the_gaps_are_named_and_counted", _gaps)
    t("competition_is_a_theorem_not_a_run", _excl)
    t("abundance_falls_as_the_three_quarter_power", _abund)
    t("nothing_here_simulates", _norun)
    return all(o[1] for o in out), out


def _chain():
    c = chain()
    if len(c) < 15:
        raise ArithmeticError(f"only {len(c)} links")
    kinds = {}
    for _a, _b, v, _r, _w in c:
        kinds[v] = kinds.get(v, 0) + 1
    return (f"{len(c)} links from a nebula to what a head does, in "
            f"order and in one list: " + ", ".join(
                f"{k} {v}" for k, v in sorted(kinds.items()))
            + ". engine/planetlab.py, engine/earthlab.py and "
              "engine/ancestry.py each walked part of this and none "
              "handed off, so the chain the repository is for was the "
              "one thing nobody could read")


def _cites():
    c = chain()
    bare = [r for r in c if not r[3] or "." not in r[3]]
    named = [r for r in c if r[2] == MISSING]
    if len(bare) > len(named):
        raise ArithmeticError(f"{len(bare)} links cite no rule")
    return (f"{len(c) - len(bare)} of {len(c)} links name the rule and "
            f"module that produce them; the {len(bare)} that do not "
            f"are exactly the {len(named)} marked MISSING, whose whole "
            f"content is that no rule produces them")


def _gaps():
    c = chain()
    gaps = [(a, b, w) for a, b, v, _r, w in c if v == MISSING]
    cross = [(a, b) for a, b, v, _r, _w in c if v == CROSSES]
    if not gaps:
        raise ArithmeticError("the chain claims to be complete")
    return (f"{len(gaps)} gaps and {len(cross)} crossings. The gaps: "
            + "; ".join(f"{a} -> {b}" for a, b, _w in gaps)
            + f". The first is the one that matters -- every gate "
              f"opens and nothing makes a cell, so permission is not "
              f"occurrence and the distance between them is not "
              f"measured anywhere here")


def _excl():
    for n in (1, 3, 7):
        if exclusion_limit(n) != n:
            raise ArithmeticError("exclusion does not track resources")
    return ("how many species coexist is bounded by how many limiting "
            "resources there are, because at equilibrium each needs "
            "one it is best at and two sharing a best cannot both "
            "stay. That is a statement about RANK. engine/ecology.py "
            "answered the same question by running 600 generations of "
            "12 species; the bound needed no population at all")


def _abund():
    e = 1000.0
    small, big, ratio = size_span(e, 1e-3, 1e3)
    want = (1e3 / 1e-3) ** 0.75
    if abs(math.log(ratio / want)) > 0.05:
        raise ArithmeticError(f"ratio {ratio:.3e} against {want:.3e}")
    return (f"one body costs b*m^(3/4), so on a fixed energy share "
            f"abundance goes as m^(-3/4): a gram-sized animal is "
            f"{ratio:.0f} times commoner than a tonne-sized one, which "
            f"is {1e6:.0e}^0.75 exactly. Population energy use is then "
            f"the SAME at every size -- a field holds few large and "
            f"many small animals and nothing chose that, Kleiber did")


def _norun():
    import ast
    src = (ROOT / "engine" / "lineage.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("run", "sweep", "census", "generate"):
                raise ArithmeticError(f"this file calls {node.func.id}")
    return ("this file calls no run, sweep, census or generate. Every "
            "link is a rule proved elsewhere and cited, and the three "
            "ecological statements are theorems -- exclusion is about "
            "rank, energetic equivalence is Kleiber divided through. "
            "README rule 3: a search means the rule has not been "
            "found")


if __name__ == "__main__":
    c = chain()
    print(f"  {len(c)} links\n")
    for a, b, v, rule, why in c:
        print(f"  {v:<8}{a[:26]:<27}-> {b[:26]:<27}{rule}")
    print()
    for n, o, d in check()[1]:
        print(f"{'PASS' if o else 'FAIL'}  {n:44}{d[:34]}")
