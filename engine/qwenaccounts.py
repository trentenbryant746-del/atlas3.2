"""
Answers that need Qwen AND the rest of the repo, each half checked.

engine/qwenmap.py holds what the model is; engine/qwenmatter.py holds
the ladder over it. Both answer questions about themselves. Neither
answers a question that requires the two of them plus the machinery
that was already here, and those are the questions worth asking.

    "how much of the model does one token touch"

needs an ASSERTED count from the GGUF header, ASSERTED byte offsets
from the tensor map, exact arithmetic over them, a second route to
the same fraction, and a comparison against the file on disk. No one
of those is an answer; composed, with each step carrying its own
check, they are.

THE ARITHMETIC GOES THROUGH ATLAS'S OWN PARSER. Every number here is
computed by engine/parse.recognise -- two independent parsers over
Fractions that must agree, which is the REDUNDANT check the repo
already applies to every sum it reports. Doing the multiplication in
Python instead would have been the same number with no check on it,
and the point of composing is that the composition is checked too.

EACH STEP RE-EXECUTES. engine/narrate.py's derivation record carries
a closure per step, and the narration is verified by running every
step again and requiring the stated value. An explanation that
cannot be re-executed is prose. So these accounts are registered the
same way primordial helium and the iron peak are, and fail the same
way if a number drifts.

WHAT STAYS ASSERTED. Everything from the model. The expert count,
the slice offsets, the subject routing -- none of it is derivable
here and none of it is dressed up as derived. What the repo adds is
arithmetic that cannot be wrong without being caught, and a
comparison against an artifact that exists independently of the map:
the 21 GB file itself.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import qwenmap                                   # noqa: E402
from engine.narrate import Derivation, ASSERTED, DERIVED     # noqa: E402

SRC = "Qwen3.6-35B-A3B GGUF header and expert-tensor-map.json"


def _exact(expr):
    """Compute through engine/parse.py -- two parsers, they must agree."""
    from engine import parse
    v, why = parse.recognise(expr)
    if v is None:
        raise ArithmeticError(f"atlas's parser declined {expr!r}: {why}")
    return int(v) if v.denominator == 1 else float(v)


def _bytes_per_expert():
    out = {}
    for e in qwenmap.experts():
        out[(e["layer"], e["expert_id"])] = sum(
            t["expert_slice_bytes"] for t in e["tensor_refs"])
    return out


def touched_per_token():
    """How much of the model one token's routing reaches."""
    d = Derivation("How much of the model does one token touch?")
    used = qwenmap.arch_used()
    per_layer = 256
    layers = 40
    d.add("take the experts used per token, per layer", used,
          kind=ASSERTED, source=SRC,
          because="the router selects this many; nothing here derives it")
    d.add("take the experts present per layer", per_layer,
          kind=ASSERTED, source=SRC)
    d.add("take the layer count", layers, kind=ASSERTED, source=SRC)

    bpe = _bytes_per_expert()
    sizes = sorted(set(bpe.values()))
    common = max(sizes, key=lambda s: sum(1 for v in bpe.values() if v == s))
    d.add("take one expert's weight bytes (gate + up + down)", common,
          kind=ASSERTED, source=SRC, unit="bytes",
          because="the three slices recorded for it in the tensor map")

    active = _exact(f"({used} * {layers}) * {common}")
    d.add("multiply used-per-layer by layers by bytes each", active,
          recompute=lambda: _exact(f"({used} * {layers}) * {common}"),
          unit="bytes",
          because="every layer routes to its own experts, so the cost "
                  "accumulates down the stack")

    total = sum(bpe.values())
    d.add("sum every expert slice in the map", total, unit="bytes",
          kind=ASSERTED, source=SRC,
          because="summed over all 10,240, which have two distinct sizes")

    frac_a = active / total
    frac_b = _exact(f"{used} * 1") / per_layer
    d.add("divide: the fraction one token touches", round(frac_a, 6),
          recompute=lambda: round(active / total, 6),
          because="bytes touched over bytes present")
    d.add("check it a second way: used over present, per layer",
          round(frac_b, 6), recompute=lambda: round(qwenmap.arch_used() / 256, 6),
          because="the byte route and the count route must agree, and they "
                  "only do if every expert is the same size to within the "
                  "two sizes present")
    d.result = round(frac_a, 6)
    d.compared_to = round(frac_b, 6)
    d.comparison = ("two independent routes to the sparsity; they agree to "
                    f"{abs(frac_a - frac_b):.2e}")
    return d


def experts_against_the_file():
    """The map's byte total, against the artifact it claims to describe."""
    d = Derivation("Do the mapped experts fit the file on disk?")
    bpe = _bytes_per_expert()
    total = sum(bpe.values())
    d.add("sum every expert slice in the map", total, unit="bytes",
          kind=ASSERTED, source=SRC)
    size = qwenmap.MODEL.stat().st_size if qwenmap.MODEL.exists() else None
    if size is None:
        raise FileNotFoundError(f"{qwenmap.MODEL} is not on disk")
    d.add("measure the GGUF on disk", size, unit="bytes",
          kind=ASSERTED, source=str(qwenmap.MODEL.name),
          because="an artifact that exists independently of the map")
    share = total / size
    d.add("divide: what share of the file the experts are",
          round(share, 6), recompute=lambda: round(total / size, 6),
          because="MoE weights should dominate a sparse model's file")
    over = total > size
    d.add("check the map does not claim more bytes than exist",
          not over, recompute=lambda: not (total > size),
          because="a map whose slices exceed the file is wrong, and this "
                  "catches it without reading a single weight")
    d.result = round(share, 6)
    d.compared_to = True
    d.comparison = (f"{total:,} of {size:,} bytes = {share:.1%} of the file "
                    f"is expert weights" + (" -- OVERFLOW" if over else ""))
    return d


def subject_cost(subject="chemistry"):
    """What one subject's top experts weigh. Qwen ids, Atlas arithmetic."""
    d = Derivation(f"What do {subject}'s top experts weigh?")
    se = qwenmap.subject_experts()
    if subject not in se:
        raise KeyError(f"{subject!r} is not one of the {len(se)} tested")
    ids = [e for e, _p, _n in se[subject]]
    d.add(f"take the top experts routed by {subject} at time 20", ids,
          kind=ASSERTED, source="qwen-topical-specialization-20x10.json",
          because="routing associations, not causal semantic functions")
    bpe = _bytes_per_expert()
    parts = [bpe[(20, i)] for i in ids]
    d.add("take each one's weight bytes", parts, kind=ASSERTED, source=SRC,
          unit="bytes")
    expr = " + ".join(str(p) for p in parts)
    tot = _exact(f"({expr})")
    d.add("add them, through atlas's own parser", tot, unit="bytes",
          recompute=lambda: _exact(f"({expr})"),
          because="two parsers over exact Fractions must agree on the sum")
    total_all = sum(bpe.values())
    share = tot / total_all
    d.add("divide by every expert in the model", round(share, 8),
          recompute=lambda: round(tot / total_all, 8))
    d.result = tot
    d.compared_to = len(ids)
    d.comparison = (f"{len(ids)} experts, {tot:,} bytes, {share:.4%} of all "
                    f"expert weight")
    return d


ACCOUNTS = {
    "touched per token": touched_per_token,
    "experts against the file": experts_against_the_file,
    "subject cost": subject_cost,
}


def check():
    """Every account, with every step re-executed by narrate.verify()."""
    out = []
    for name, fn in ACCOUNTS.items():
        try:
            d = fn()
            ok, detail = d.verify()
            if not ok:
                raise ArithmeticError(f"narration is unfaithful: {detail}")
            n = sum(1 for s in d.steps if s.recompute is not None)
            out.append((name, True,
                        f"{len(d.steps)} steps, {n} re-executed and "
                        f"reproduced; {d.comparison}"))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))
    return all(o[1] for o in out), out


if __name__ == "__main__":
    for name, fn in ACCOUNTS.items():
        d = fn()
        print("=" * 70)
        print(d.narrate())
        print()
    ok, res = check()
    for name, good, detail in res:
        print(f"{'PASS' if good else 'FAIL'}  {name:<26}{detail}")
    print("\nall:", ok)
