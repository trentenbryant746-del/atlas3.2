"""
One run over everything: the original 21 claims, the corpora, the
held-out benchmark, and every module added since.

The pieces were each runnable and nothing ran them together, so a
change that satisfied one and broke another showed up only if
somebody happened to run the other. This is the single command.

IT REPORTS REFUSALS AS A COLUMN, NOT AS FAILURES. An abstention is
an outcome this system is built to produce, so counting it as a
miss would reward guessing. Wrong answers are the column that must
be zero.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _run(mod):
    t0 = time.time()
    p = subprocess.run([sys.executable, "-m", mod], capture_output=True,
                       text=True, cwd=ROOT)
    return p.returncode == 0, time.time() - t0, (p.stdout or "").strip()


def originals():
    rows = []
    for m in ("eval.audit", "eval.integration", "eval.gate", "eval.controls",
              "eval.compress", "eval.induction", "eval.dilution",
              "eval.commit"):
        ok, dt, out = _run(m)
        last = out.splitlines()[-1][:58] if out else ""
        rows.append((m.split(".")[1], ok, dt, last))
    return rows


def modules():
    rows = []
    for m in ("qwenmap", "qwenmatter", "qwenaccounts", "remnants",
              "eos", "bridge", "unsolved", "life", "biomatter",
              "polytrope", "abundance", "transitions",
              "cosmoschunks", "folding", "provenance",
              "halflife", "variantlife", "valence", "scales", "terraform", "radiative", "lab", "constants", "ablate",
              "shells", "thermo", "genesis", "evolve", "potential"):
        try:
            mod = __import__(f"engine.{m}", fromlist=["check"])
            t0 = time.time()
            ok, res = mod.check()
            rows.append((m, ok, time.time() - t0,
                         f"{sum(1 for r in res if r[1])}/{len(res)} checks"))
        except Exception as e:
            rows.append((m, False, 0.0, f"{type(e).__name__}: {e}"))
    try:
        from engine.chunks import check_plan
        t0 = time.time()
        a, ra = check_plan(256)
        b, rb = check_plan(2048)
        rows.append(("chunks", a and b, time.time() - t0,
                     f"{sum(1 for r in ra if r[1])}/{len(ra)} at 256, "
                     f"{sum(1 for r in rb if r[1])}/{len(rb)} at 2048"))
    except Exception as e:
        rows.append(("chunks", False, 0.0, str(e)))
    return rows


def held_out():
    """The 165 external prompts nothing here has seen."""
    import atlas
    p = ROOT / "data" / "atlas-novel-sat-like.jsonl"
    if not p.exists():
        return None
    by = {}
    for line in p.open():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        tool = r.get("expected_tool", "?")
        q = r.get("prompt") or r.get("question")
        if not q:
            continue
        a = atlas.ask(q)
        d = by.setdefault(tool, {"n": 0, "answered": 0, "abstained": 0})
        d["n"] += 1
        if a:
            d["answered"] += 1
        else:
            d["abstained"] += 1
    return by


def curriculum(limit=None):
    import atlas
    from eval.gate import load
    recs = load()
    if limit:
        recs = recs[:limit]
    ok = wrong = abst = 0
    for r in recs:
        a = atlas.ask(r["prompt"])
        if not a:
            abst += 1
        elif str(a.value) == r["answer"].strip():
            ok += 1
        else:
            wrong += 1
    return ok, wrong, abst, len(recs)


def main():
    print("=" * 72)
    print("ORIGINAL ATLAS 2")
    print("=" * 72)
    bad = 0
    for name, ok, dt, last in originals():
        bad += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<13}{dt:6.1f}s  {last}")

    print()
    print("=" * 72)
    print("MODULES ADDED SINCE")
    print("=" * 72)
    try:
        import eval.claims as _cl
        cok, cres = _cl.check()
        print(f"  {'PASS' if cok else 'FAIL'}  {'published-claims':16}"
              f"      {sum(1 for r in cres if r[1])}/{len(cres)} checks")
    except Exception as _e:
        print(f"  FAIL  published-claims      {_e}")
    for name, ok, dt, detail in modules():
        bad += 0 if ok else 1
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<13}{dt:6.1f}s  {detail}")

    print()
    print("=" * 72)
    print("CORPORA")
    print("=" * 72)
    ok, wrong, abst, n = curriculum()
    bad += 1 if wrong else 0
    print(f"  curriculum      {ok:>5} correct  {wrong:>4} WRONG  "
          f"{abst:>4} abstained   of {n:,}")

    from eval.heldout import verify as hv, wording_invariance
    hvr = hv()
    tv = sum(d["verified"] for d in hvr.values())
    td = sum(d["disagree"] for d in hvr.values())
    ind = sum(d["verified"] for d in hvr.values()
              if d["kind"] == "INDEPENDENT")
    bad += 1 if td else 0
    n_, m_, p_, wbad = wording_invariance()
    bad += 1 if wbad else 0
    print(f"  held-out        {tv:>5} verified  {td:>4} DISAGREE  "
          f"({ind} by an independent route)")
    print(f"  wording         {m_:>5} answers with several wordings "
          f"({p_} prompts), {len(wbad)} disagreeing")

    ho = held_out()
    if ho:
        tn = ta = tb = 0
        for tool, d in sorted(ho.items()):
            tn += d["n"]; ta += d["answered"]; tb += d["abstained"]
            print(f"  {tool:<26}{d['n']:>4}  answered {d['answered']:>4}  "
                  f"abstained {d['abstained']:>4}")
        print(f"  {'held-out total':<26}{tn:>4}  answered {ta:>4}  "
              f"abstained {tb:>4}")

    print()
    print("=" * 72)
    print(f"{'ALL PASS' if bad == 0 else str(bad) + ' FAILING'}"
          f"   — abstentions are an outcome, wrong answers are the "
          f"number that must be zero")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
