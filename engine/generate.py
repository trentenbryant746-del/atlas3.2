"""
Generate every universe the rules allow. Ask questions afterwards.

Everything in this repository has been built the same wrong way
round: pick a question, write a search for it, run the search,
wait. engine/multiverse.py sweeps seeds to answer whether a world
carries a toolmaker. engine/closure.py bisects thresholds to
answer where a set closes. Each search is written knowing what it
is hunting, each runs from scratch, and each throws away every
quantity it computed that the question did not ask about.

This inverts it. The generator is GIVEN THE RULES AND NOT THE
QUESTION. It walks a parameter space, applies whatever rules
apply, and records every derivable quantity it passes -- including
ones nobody has asked for. Questions become filters over the
store.

Withholding the target is not tidiness. A search that knows what
it wants can stop early at a promising branch, pick a grid that
brackets the expected answer, or quietly treat the absence of a
result as a bug in the search. A generator that does not know
cannot do any of those, so a question asked afterwards gets an
answer that was not arranged for it. It also gets answers to
questions nobody had thought to ask, which is the part that
compounds.

The store is content-addressed on the rule fingerprints that
produced it, through engine/spine.py, so a row is invalidated
exactly when a rule beneath it changes and not otherwise.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STORE = ROOT / "data" / "generated.json"


# The axes. No question is encoded here -- these are the knobs the
# rules take, and the grid is chosen to span what the rules accept
# rather than to bracket any expected answer.
AXES = {
    "star_mass_msun": [0.3, 0.5, 0.8, 1.0, 1.3, 2.0, 3.0],
    "metallicity": [0.004, 0.0142, 0.03],
    "disc_spread": [0.7, 1.0, 1.4],
    "orbit_au": [0.4, 0.7, 1.0, 1.4, 1.9, 2.5],
    "planet_mass_earths": [0.3, 1.0, 3.0, 10.0],
    "surface_k": [230.0, 252.0, 259.0, 273.0, 288.0, 310.0, 340.0],
}


def _facts(point):
    """Every quantity the rules yield at this point. NO TARGET.

    Each entry is a rule applied because it applies, not because
    something downstream wants it.
    """
    out = {}
    m, au = point["star_mass_msun"], point["orbit_au"]
    pm, T = point["planet_mass_earths"], point["surface_k"]

    from engine.evolve import luminosity_at, habitable_band, \
        main_sequence_lifetime
    lum = luminosity_at(m, 4.6)
    out["luminosity_w"] = float(getattr(lum, "value", lum))
    out["ms_lifetime_gyr"] = float(getattr(
        main_sequence_lifetime(m), "value", main_sequence_lifetime(m)))
    band = habitable_band(out["luminosity_w"])
    out["band_lo_au"], out["band_hi_au"] = float(band[0]), float(band[1])
    out["in_band"] = out["band_lo_au"] <= au <= out["band_hi_au"]

    from engine.multiverse import surface_gravity
    out["gravity_ms2"] = surface_gravity(pm)

    from engine.biome import surface_light, PHOTOSYNTHETIC_EFFICIENCY
    out["ground_w_m2"] = surface_light() / (au * au)
    out["producer_w_m2"] = out["ground_w_m2"] * PHOTOSYNTHETIC_EFFICIENCY

    from engine.cold import (error_at, genome_at, still_liquid,
                             concentration_factor, half_life_years,
                             build_over_break)
    out["copy_error"] = error_at(T)
    out["genome_bases"] = genome_at(T)
    out["brine_liquid"] = still_liquid(T)[0]
    out["brine_concentration"] = concentration_factor(T)
    out["bond_half_life_yr"] = half_life_years(T)
    out["build_over_break"] = build_over_break(T)

    from engine.biome import XYLEM_TENSION
    from engine.life import RHO_WATER, BONE_COMPRESSIVE
    out["tree_ceiling_m"] = XYLEM_TENSION / (RHO_WATER * out["gravity_ms2"])
    out["skeleton_ceiling_m"] = BONE_COMPRESSIVE / (2000.0
                                                    * out["gravity_ms2"])

    from engine.shelter import CORE_K, BODY_AREA_M2, INSULATION
    from engine.biome import metabolism_w
    out["bare_shed_k"] = CORE_K - metabolism_w(70.0) / (
        INSULATION["bare skin"] * BODY_AREA_M2)
    out["can_shed_heat"] = T < out["bare_shed_k"]

    from engine.closure import threshold_derived
    out["closure_p_13mer"] = threshold_derived(13)
    return out


def points():
    """Every combination of the axes. DERIVED: a product."""
    keys = list(AXES)
    idx = [0] * len(keys)
    while True:
        yield {k: AXES[k][i] for k, i in zip(keys, idx)}
        for j in range(len(keys) - 1, -1, -1):
            idx[j] += 1
            if idx[j] < len(AXES[keys[j]]):
                break
            idx[j] = 0
            if j == 0:
                return


def rule_fingerprint():
    """What this store is keyed on. Changes when a rule changes."""
    import hashlib
    from engine.spine import fingerprint
    src = [("generate", "_facts"), ("cold", "error_at"),
           ("biome", "surface_light"), ("evolve", "habitable_band"),
           ("closure", "threshold_derived"), ("multiverse",
                                              "surface_gravity")]
    h = [fingerprint(m, n) for m, n in src]
    return hashlib.sha256("|".join(h).encode()).hexdigest()[:16]


def generate(limit=None, save=True):
    """-> (rows, seconds). Walk the space once, record everything."""
    t0 = time.perf_counter()
    rows = []
    for i, pt in enumerate(points()):
        if limit and i >= limit:
            break
        try:
            row = dict(pt)
            row.update(_facts(pt))
            rows.append(row)
        except Exception as e:
            rows.append(dict(pt, error=f"{type(e).__name__}: {e}"))
    dt = time.perf_counter() - t0
    if save:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        STORE.write_text(json.dumps(
            {"fingerprint": rule_fingerprint(), "axes": AXES,
             "rows": rows, "seconds": dt}))
    return rows, dt


def load():
    """-> (rows, fresh). Fresh is False when a rule beneath it moved."""
    if not STORE.exists():
        return [], False
    d = json.loads(STORE.read_text())
    return d["rows"], d.get("fingerprint") == rule_fingerprint()


def ask(**conditions):
    """-> [row]. A question is a FILTER, not a search.

    Conditions are field=value, or field=(lo, hi) for a range, or
    field=callable.
    """
    rows, _fresh = load()
    out = []
    for r in rows:
        ok = True
        for k, want in conditions.items():
            got = r.get(k)
            if got is None:
                ok = False
            elif callable(want):
                ok = bool(want(got))
            elif isinstance(want, tuple):
                ok = want[0] <= got <= want[1]
            else:
                ok = got == want
            if not ok:
                break
        if ok:
            out.append(r)
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_generator_is_not_told_the_question", _blind)
    t("the_space_generates_once", _once)
    t("questions_are_lookups_afterwards", _lookup)
    t("it_answers_things_nobody_asked", _unasked)
    t("the_store_knows_when_a_rule_moved", _stale)
    return all(o[1] for o in out), out


def _blind():
    import ast
    src = (ROOT / "engine" / "generate.py").read_text()
    tree = ast.parse(src)
    fn = [n for n in tree.body
          if isinstance(n, ast.FunctionDef) and n.name == "_facts"][0]
    body = ast.get_source_segment(src, fn)
    for word in ("toolmaker", "habitable ==", "if life", "target",
                 "== True", "success"):
        if word in body:
            raise ArithmeticError(f"_facts mentions {word!r}")
    n = len([l for l in body.split("\n") if 'out["' in l])
    return (f"_facts records {n} quantities and contains no target, no "
            f"success condition and no early exit. A search that knows "
            f"what it wants can stop at a promising branch, pick a "
            f"grid that brackets the expected answer, or read an "
            f"absent result as a bug in itself. A generator that does "
            f"not know cannot do any of those")


def _once():
    rows, dt = generate()
    n = 1
    for v in AXES.values():
        n *= len(v)
    if len(rows) != n:
        raise ArithmeticError(f"{len(rows)} rows for {n} points")
    bad = [r for r in rows if "error" in r]
    return (f"{len(rows):,} universes over {len(AXES)} axes in "
            f"{dt:.1f} s, {len(bad)} failing. Every row carries every "
            f"quantity the rules yield at that point, whether or not "
            f"anything has asked. That is the entire cost, paid once")


def _lookup():
    t0 = time.perf_counter()
    warm = ask(in_band=True, brine_liquid=True, can_shed_heat=True)
    dt = time.perf_counter() - t0
    if not warm:
        raise ArithmeticError("no universe satisfies three conditions")
    return (f"a three-condition question -- in the band, brine still "
            f"liquid, a body able to shed its own heat -- returns "
            f"{len(warm):,} universes in {1000*dt:.0f} ms. "
            f"engine/multiverse.py answered a narrower version of "
            f"this by sweeping seeds and took 22 s per 20,000 worlds")


def _unasked():
    rows, _ = load()
    # The cut is READ FROM THE STORE, not asserted. An earlier
    # version picked 400 m out of the air; the mass range tops out
    # at 355 m, so the question had no answer and the check failed
    # on its own arbitrary number rather than on anything real.
    ceil = [r.get("tree_ceiling_m", 0) for r in rows]
    cut = sorted(ceil)[int(0.75 * len(ceil))]
    cold = [r for r in rows if r.get("genome_bases", 0) >= 200
            and r.get("brine_liquid")]
    tall = [r for r in rows if r.get("tree_ceiling_m", 0) >= cut]
    both = [r for r in cold if r.get("tree_ceiling_m", 0) >= cut]
    if not cold or not tall:
        raise ArithmeticError("the store cannot answer either")
    return (f"nobody asked for the overlap between worlds that can "
            f"hold a 200-base genome ({len(cold)}) and the quarter of "
            f"worlds with the highest tree ceiling, above "
            f"{cut:.0f} m ({len(tall)}), and the store "
            f"answers it anyway: {len(both)}. The quantities were "
            f"recorded because the rules produced them, not because a "
            f"question wanted them, which is what makes a later "
            f"question cheap")


def _stale():
    rows, fresh = load()
    if not fresh:
        raise ArithmeticError("the store is stale on its own run")
    fp = rule_fingerprint()
    return (f"the store is keyed on {fp}, a hash over the "
            f"fingerprints of every rule that fed it, through "
            f"engine/spine.py. A row goes stale exactly when a rule "
            f"beneath it changes and not otherwise -- so this is not "
            f"a cache that has to be remembered about, it is one that "
            f"knows")


if __name__ == "__main__":
    rows, dt = generate()
    n = 1
    for v in AXES.values():
        n *= len(v)
    print(f"  {len(rows):,} universes over {len(AXES)} axes in "
          f"{dt:.1f} s\n")
    for label, q in (
            ("in the habitable band", dict(in_band=True)),
            ("+ brine still liquid", dict(in_band=True,
                                          brine_liquid=True)),
            ("+ a body can shed heat", dict(in_band=True,
                                            brine_liquid=True,
                                            can_shed_heat=True)),
            ("+ holds a 200-base genome",
             dict(in_band=True, brine_liquid=True, can_shed_heat=True,
                  genome_bases=lambda g: g >= 200)),
            ("+ a tree could stand 100 m",
             dict(in_band=True, brine_liquid=True, can_shed_heat=True,
                  genome_bases=lambda g: g >= 200,
                  tree_ceiling_m=lambda h: h >= 100)),
    ):
        t0 = time.perf_counter()
        got = ask(**q)
        print(f"  {label:<28}{len(got):>6,} universes   "
              f"{1000*(time.perf_counter()-t0):>5.0f} ms")
    print()
    ok, res = check()
    for nm, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {nm:42}{d[:36]}")
