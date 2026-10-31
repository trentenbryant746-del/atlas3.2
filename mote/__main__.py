"""Command line for mote. Everything here is a thin wrapper."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _run(a):
    from mote.deeptime import run
    out = run(gens=a.gens, pop=a.pop, worlds=a.worlds, seed=a.seed,
              years_per_gen=a.years_per_gen, out=a.out, ratchet=not a.no_ratchet,
              extinct_every=a.extinct_every, d0=a.d0,
              progress_every=a.progress_every)
    if not a.no_report:
        _report(argparse.Namespace(dir=str(out), html=None, watch=True))


def _report(a):
    from mote import report
    an = report.analyse(a.dir)
    print(report.text_summary(an))
    path = a.html or str(Path(a.dir) / "report.html")
    report.html(an, path)
    print(f"\n  charts -> {path}")
    if getattr(a, "watch", False):
        _watch(argparse.Namespace(dir=a.dir, level=0.4, world=0, plain=False))
    return path


def _watch(a):
    import numpy as np
    from mote import bench, replay
    from mote.deeptime import load_fossils
    from mote.world import Episode
    gens, foss = load_fossils(a.dir)
    scores = bench.frozen(foss)["overall"]
    best = int(np.argmax(scores))
    ep = Episode(seed=bench.BENCH_SEEDS[0], n_worlds=4, d=a.level)
    print(f"\n  the same world, {a.level:.2f} difficulty: generation 0 "
          f"against generation {gens[best]:,}\n")
    replay.compare(foss.take([0]), foss.take([best]), ep, world=a.world,
                   labels=(f"gen 0", f"gen {gens[best]:,}"),
                   colour=not a.plain)


def _demo(a):
    from mote.deeptime import run
    print("  a short run, so the whole shape of it is visible in a minute\n")
    out = run(gens=a.gens, pop=96, worlds=3, seed=1, years_per_gen=1.0,
              out=a.out, progress_every=max(1, a.gens // 5))
    _report(argparse.Namespace(dir=str(out), html=None, watch=True))


def _selftest(a):
    from mote.tests import test_mote
    return test_mote.main()


def main(argv=None):
    p = argparse.ArgumentParser(prog="mote", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="evolve a lineage and leave a fossil record")
    r.add_argument("--gens", type=int, default=100_000)
    r.add_argument("--pop", type=int, default=128)
    r.add_argument("--worlds", type=int, default=3)
    r.add_argument("--seed", type=int, default=1)
    r.add_argument("--years-per-gen", type=float, default=1.0,
                   help="years one generation stands for (default 1)")
    r.add_argument("--out", default="runs/deep")
    r.add_argument("--d0", type=float, default=0.0)
    r.add_argument("--no-ratchet", action="store_true",
                   help="hold difficulty fixed at --d0")
    r.add_argument("--extinct-every", type=int, default=0,
                   help="bottleneck the population every N generations")
    r.add_argument("--progress-every", type=int, default=20_000)
    r.add_argument("--no-report", action="store_true")
    r.set_defaults(fn=_run)

    d = sub.add_parser("demo", help="a short end-to-end run")
    d.add_argument("--gens", type=int, default=20_000)
    d.add_argument("--out", default="runs/demo")
    d.set_defaults(fn=_demo)

    g = sub.add_parser("report", help="score the fossils and write the charts")
    g.add_argument("dir")
    g.add_argument("--html", default=None)
    g.add_argument("--watch", action="store_true")
    g.set_defaults(fn=_report)

    w = sub.add_parser("watch", help="ancestor and descendant, same world")
    w.add_argument("dir")
    w.add_argument("--level", type=float, default=0.4)
    w.add_argument("--world", type=int, default=0)
    w.add_argument("--plain", action="store_true", help="no colour")
    w.set_defaults(fn=_watch)

    s = sub.add_parser("selftest", help="run the checks")
    s.set_defaults(fn=_selftest)

    a = p.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    raise SystemExit(main())
