"""
Every published number, recomputed. Stale claims are a kind of wrong.

This README states measured results in almost every section. A
number written down in one version and left there is a claim the
repository is still making, and when the code moves underneath it
the claim silently stops being true. Nothing else here catches
that: the benchmark checks the code against itself, the audit
checks the code against its own invariants, and neither reads the
document.

IT HAS ALREADY HAPPENED ONCE. 3.1.30 published an ablation table
reading 1 right, 1 wrong, 12 refused. 3.1.31 changed the rule it
was measuring and the same command now prints 8, 0, 6. The old
table was correct when written and is wrong as a present-tense
claim, and only a reader who ran the code would know.

So each load-bearing published number is registered here with the
computation that produced it. A claim that no longer reproduces
fails, and there are two honest repairs: correct the document, or
mark the number as superseded history rather than a current
result. What is not allowed is leaving it.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CURRENT, HISTORY = "CURRENT", "HISTORY"


def _decay():
    from engine.transitions import score
    r = score()
    return (r["right"], r["wrong"], r["refused"])


def _magic():
    from engine.shells import MAGIC
    return tuple(MAGIC)


def _region():
    from engine.shells import allowed_region
    return round(allowed_region()[0] * 100, 1)


def _sigma_rel():
    from engine.terraform import SIGMA
    return float(f"{abs(SIGMA - 5.670374419e-8) / 5.670374419e-8:.2e}")


def _domain_floor():
    from engine.shells import SEMF_MIN_A
    return SEMF_MIN_A


def _bars():
    from engine.nucleo import mass_bar
    return (round(mass_bar("in-domain")[0], 3),
            round(mass_bar("out-of-domain")[0], 3))


def _mq_bar():
    from engine.nucleo import MEASURED_Q_BAR
    return round(MEASURED_Q_BAR, 4)


def _fold_bar():
    from engine.folding import model_bar
    return round(model_bar()[0], 4)


def _climate():
    from engine import terraform as T, radiative as R
    out = {}
    for n in ("Earth", "Venus"):
        b = T.BODIES[n]
        P = b.observed_bar_pa or 0.0
        mix = {"CO2": (b.observed_co2 or 0) * P}
        if n == "Earth":
            mix["H2O"] = 0.7 * T.p_sat_water(288.0)
        tau = R.grey_equivalent_full(mix, b.observed_T, b.gravity(), P)
        out[n] = round(T.equilibrium_T(b) * (1 + 0.75 * tau) ** 0.25
                       - b.observed_T, 1)
    return (out["Earth"], out["Venus"])


def _table_size():
    from engine.nucleo import MEASURED_BINDING
    return len(MEASURED_BINDING)


def _band():
    from engine.evolve import _solar_band
    i, o = _solar_band()
    return (round(i, 3), round(o, 3))


def _lab_counts():
    from engine.lab import run, HOLDS, CLASH, MISSING_RULE, REFUSED
    rows, _ = run(stop_on_problem=False)
    c = {}
    for _L, _n, v, _d, _a in rows:
        c[v] = c.get(v, 0) + 1
    return (c.get(HOLDS, 0), c.get(CLASH, 0),
            c.get(MISSING_RULE, 0), c.get(REFUSED, 0))


# (section, claim, computation, expected, status)
CLAIMS = [
    ("3.1.31", "decay score is 8 right, 0 wrong, 6 refused",
     _decay, (8, 0, 6), CURRENT),
    ("3.1.27", "the derived magic numbers",
     _magic, (2, 8, 20, 28, 40, 50, 82, 126), CURRENT),
    ("3.1.27", "4.2% of the (kappa, mu) plane gives all seven closures",
     _region, 4.2, CURRENT),
    ("3.1.21", "Stefan-Boltzmann agrees to 3.25e-11",
     _sigma_rel, 3.25e-11, CURRENT),
    ("3.1.28", "the liquid drop is refused below A=13",
     _domain_floor, 13, CURRENT),
    ("3.1.29", "mass bar 1.850 in domain, 6.249 outside",
     _bars, (1.85, 6.249), CURRENT),
    ("3.1.31", "measured-Q precision derived as 0.0866 MeV",
     _mq_bar, 0.0866, CURRENT),
    ("3.1.31", "the unified binding table holds 29 nuclides",
     _table_size, 29, CURRENT),
    ("3.1.18", "folding survival rate 0.573",
     _fold_bar, 0.5729, CURRENT),
    ("3.1.33", "unfitted climate: Earth +12.3 K, Venus -495.6 K",
     _climate, (12.3, -495.6), CURRENT),
    ("3.1.37", "habitable band derived 0.999 - 1.898 AU",
     _band, (0.999, 1.898), CURRENT),
    ("3.1.31", "lab: 23 HOLDS, 1 CLASH, 1 MISSING_RULE, 1 REFUSED",
     _lab_counts, (23, 1, 1, 1), CURRENT),
]

# Numbers that WERE published and no longer reproduce. Kept as
# history, named, so nobody mistakes them for present-tense claims.
SUPERSEDED = [
    ("3.1.23", "unfitted climate: Earth -3.2 K",
     "3.1.33 fixed spectral overlap so overlapping bands add optical "
     "depth instead of averaging transmittance. Earth's water bands "
     "overlap heavily, so the old averaging under-counted them and the "
     "-3.2 K agreement was partly the bug. It now reads +12.3 K"),
    ("3.1.30", "ablation read 1 right, 1 wrong, 12 refused",
     "3.1.31 changed the rule being measured; it now reads 8, 0, 6. "
     "The table was correct when written and describes a system that "
     "no longer exists"),
    ("3.1.26", "8 right, 3 wrong, 3 refused",
     "those eight rested on a +5.455 MeV source inconsistency "
     "cancelling the liquid drop's deficit; superseded by 3.1.31, "
     "which reaches eight with zero wrong"),
    ("3.1.19", "Mercury held out at +2.8 K",
     "withdrawn in 3.1.20: it compared a redistributed prediction "
     "against a dayside observation"),
]


def run():
    rows = []
    for sec, claim, fn, want, status in CLAIMS:
        try:
            got = fn()
            ok = got == want
        except Exception as e:
            got, ok = f"{type(e).__name__}: {e}", False
        rows.append((sec, claim, want, got, ok, status))
    return rows


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("every_published_number_reproduces", _repro)
    t("superseded_numbers_are_named", _super)
    return all(o[1] for o in out), out


def _repro():
    rows = run()
    bad = [(s, c, w, g) for s, c, w, g, ok, _st in rows if not ok]
    if bad:
        raise ArithmeticError(
            "published numbers that no longer reproduce: "
            + "; ".join(f"{s} claims {c}: expected {w}, got {g}"
                        for s, c, w, g in bad))
    return (f"{len(rows)} load-bearing published numbers recomputed and "
            f"all {len(rows)} still hold. A number written into the "
            f"README is a claim the repository is still making, and "
            f"nothing else here reads the document")


def _super():
    if not SUPERSEDED:
        raise ArithmeticError("nothing is recorded as superseded, which "
                              "for a repo with four retractions is wrong")
    for sec, claim, why in SUPERSEDED:
        if len(why) < 40:
            raise ArithmeticError(f"{sec} is superseded without saying why")
    return (f"{len(SUPERSEDED)} published numbers are recorded as history "
            f"rather than current: "
            + "; ".join(f"{s} ({c[:38]}...)" for s, c, _w in SUPERSEDED)
            + ". Each says what replaced it")


if __name__ == "__main__":
    for sec, claim, want, got, ok, _st in run():
        print(f"  {'ok  ' if ok else 'STALE'} {sec:8}{claim[:52]:54}"
              f"{'' if ok else f'want {want} got {got}'}")
    print()
    for sec, claim, why in SUPERSEDED:
        print(f"  history {sec:8}{claim}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:34}{d[:70]}")
    print("\nall:", ok)
