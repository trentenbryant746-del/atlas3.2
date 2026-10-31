"""
The long run, and the fossil record it leaves behind.

One generation is one lifetime. How many years that is depends on the
animal, not on this program, so it is a parameter: `years_per_gen`. The
default is 1.0, which is the honest reading for a small forager that
breeds once a season, and it means a million generations is a million
years and nothing has been quietly multiplied.

WHAT A RUN WRITES

    run.json        every parameter, so the run can be argued with
    history.csv     one row per logged generation, appended as it goes
    fossils/        champion genomes, saved on a schedule that is dense
                    early and even thereafter

THE FOSSIL SCHEDULE IS LOG-SPACED AND THEN UNIFORM, because the two
questions want different samples. "What happened at the start" needs
generations 1, 2, 4, 8, 16 -- almost all of the early change is over by
generation 1000. "Did it keep improving" needs even sampling across the
whole run. Taking both costs about a hundred small files.

Nothing here scores a fossil. Fossils are genomes; the claims about them
are made later, by bench.py, against worlds this run never saw.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from mote.evolve import Lineage

HISTORY_COLS = ("gen", "years", "d", "best", "mean", "topq", "topq_ema",
                "median", "hidden", "conns", "sigma", "alive", "bites")


def fossil_gens(total, n_log=26, n_even=80):
    """-> sorted generations at which to keep a champion."""
    if total <= 0:
        return [0]
    lg = np.log10(max(total, 10))
    log = {0, 1} | {int(round(10 ** x)) for x in np.linspace(0, lg, n_log)}
    even = {int(round(i * total / n_even)) for i in range(n_even + 1)}
    return sorted(g for g in (log | even) if 0 <= g <= total)


def run(gens=100_000, pop=128, worlds=3, seed=1, years_per_gen=1.0,
        out="runs/deep", log_every=0, ratchet=True, extinct_every=0,
        d0=0.0, progress_every=20_000, quiet=False):
    """Evolve for `gens` generations, leaving a readable trail. -> Path."""
    out = Path(out)
    (out / "fossils").mkdir(parents=True, exist_ok=True)
    log_every = log_every or max(1, gens // 2000)
    keep = set(fossil_gens(gens))

    cfg = {"gens": gens, "pop": pop, "worlds": worlds, "seed": seed,
           "years_per_gen": years_per_gen, "log_every": log_every,
           "ratchet": ratchet, "extinct_every": extinct_every, "d0": d0,
           "years_total": gens * years_per_gen, "n_fossils": len(keep),
           "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    (out / "run.json").write_text(json.dumps(cfg, indent=2))

    lin = Lineage(pop=pop, worlds=worlds, seed=seed, d0=d0, ratchet=ratchet,
                  extinct_every=extinct_every)
    hist = open(out / "history.csv", "w", buffering=1)
    hist.write(",".join(HISTORY_COLS) + "\n")

    t0 = time.time()
    for g in range(gens + 1):
        want = (g % log_every == 0) or (g in keep)
        s = lin.generation(want_sizes=want)
        if g in keep:
            lin.champion().save(out / "fossils" / f"g{g:09d}.npz")
        if want:
            s["years"] = g * years_per_gen
            hist.write(",".join(f"{s.get(c, '')}" for c in HISTORY_COLS) + "\n")
        if not quiet and progress_every and g % progress_every == 0:
            el = time.time() - t0
            rate = (g + 1) / max(el, 1e-9)
            eta = (gens - g) / max(rate, 1e-9)
            print(f"  gen {g:>9,}  {g*years_per_gen:>12,.0f} yr   "
                  f"d={s['d']:.3f}  topq={s.get('topq_ema', 0):+.3f}  "
                  f"hid={s.get('hidden', float('nan')):4.1f}  "
                  f"{rate:6.0f} gen/s  eta {eta/60:5.1f} min", flush=True)
    hist.close()

    cfg["elapsed_s"] = round(time.time() - t0, 1)
    cfg["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (out / "run.json").write_text(json.dumps(cfg, indent=2))
    if not quiet:
        print(f"  done: {gens:,} generations in {cfg['elapsed_s']/60:.1f} min "
              f"-> {out}", flush=True)
    return out


def load_history(out):
    """-> dict of column name to numpy array."""
    out = Path(out)
    rows = (out / "history.csv").read_text().strip().split("\n")
    cols = rows[0].split(",")
    data = np.array([[float(v) if v else np.nan for v in r.split(",")]
                     for r in rows[1:]])
    return {c: data[:, i] for i, c in enumerate(cols)}


def load_fossils(out):
    """-> (generations array, Brains with one genome per fossil)."""
    from mote.brain import Brains
    out = Path(out)
    paths = sorted((out / "fossils").glob("g*.npz"))
    gens = np.array([int(p.stem[1:]) for p in paths])
    return gens, Brains.concat([Brains.load(p) for p in paths])
