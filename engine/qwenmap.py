"""
All 10,240 Qwen experts mapped into Atlas, with the layer as time.

This maps; it does not run. The 21 GB GGUF is on disk and llama-cli is
built beside it, and nothing here invokes either. What is mapped is a
completed capture: every expert of every layer, its identity, its
weights' location, and -- for one layer -- which subjects route to it.

    256 experts x 40 layers = 10,240, each with a distinct sha256

THE LAYER IS THE TIME COORDINATE. A token's context is built up layer
by layer, so layer index is not a filing category, it is WHEN. Expert
147 at layer 3 and expert 147 at layer 31 are not the same expert seen
twice; they are different experts, and the thing that separates them
is time. That is the same move engine/epochs.py already makes for
matter -- the address is (what, when) and neither half is optional.

    address    (time, expert)  ->  a 256-bit key
    time       0..39           the layer, i.e. depth into the context
    expert     0..255          which of the layer's experts

WHAT IS ASSERTED AND WHAT IS DERIVED. Everything that came out of the
model is ASSERTED and nothing here can check it: the expert ids, the
sha256 keys, the tensor offsets, the gate probabilities, the subject
enrichments. What is DERIVED is computed on top, and each derivation
carries a check that would catch the map being wrong:

    10,240 slots            = 256 x 40                     INVERSE
    10,240 distinct keys    no two experts share an id      IDENTITY
    30,720 slice sizes      = shape x bits(quantization)    REDUNDANT
    120 packed tensors      256 slices tile with no gap     CONSERVATION

THE SLICE CHECK IS THE ONE THAT EARNS ITS KEEP. A Q4_K superblock is
144 bytes per 256 weights, Q5_K is 176 and Q6_K is 210, so the byte
length of one expert's slice follows from its shape and quantization
alone. All 30,720 recorded lengths reproduce, and within each of the
120 packed tensors the 256 slices abut exactly -- no gap, no overlap,
across 30,600 boundaries. A map with a wrong offset anywhere would
fail that, and it is checked without reading a single weight.

WHAT THE SUBJECT LABELS ARE NOT. The enrichments attach at time 20,
because that is the layer whose per-expert numbers were exported --
not because layer 20 is special. Router-input classification is 100%
at ALL forty layers, so the subject signal is distributed and calling
layer 20 the subject layer would be naming the layer that was looked
at. And the labels are routing associations, not causal semantic
functions: the subject phrase was identical across the ten wordings,
so what was shown is subject-associated routing, not abstract
semantic specialization. That sentence travels with every answer.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ANSWERED, REFUSED, PASS = "ANSWERED", "REFUSED", "PASS"

CODEX = Path("/Users/trentenbryant/Documents/Codex/2026-09-14/"
             "files-mentioned-by-the-user-atlas")
ATLASDIR = CODEX / "outputs/qwen-local/atlas"
TENSOR_MAP = ATLASDIR / "expert-tensor-map.json"
RESULTS = (ATLASDIR / "benchmark-runs/"
                      "qwen-topical-specialization-20x10.json")
MODEL = CODEX / "outputs/models/Qwen3.6-35B-A3B-UD-Q4_K_M.gguf"

# bytes per 256-weight superblock. These define the formats; they are
# not measurements of this model.
SUPERBLOCK = {"Q4_K": 144, "Q5_K": 176, "Q6_K": 210}

LIMITS = ("routing associations, not causal semantic functions; the "
          "subject phrase was identical across all ten wordings, so this "
          "is subject-associated routing, not abstract semantic "
          "specialization")

_C = {}


def _load(p, what):
    if p not in _C:
        if not p.exists():
            raise FileNotFoundError(f"{what} not found at {p}")
        _C[p] = json.loads(p.read_text())
    return _C[p]


GGUF_META = ATLASDIR / "qwen-complete-map" / "gguf-metadata.json"


def arch_used():
    """expert_used_count, straight from the GGUF header. ASSERTED.

    The binding number for engine/qwenmatter.py is read here rather
    than written there, so a compound's cardinality comes from the
    model's own header and not from a constant someone chose.
    """
    d = _load(GGUF_META, "the GGUF metadata")
    return d["qwen35moe.expert_used_count"]["value"]


def experts():
    """-> [{key, layer, expert_id, tensor_refs}] for all 10,240. ASSERTED."""
    return _load(TENSOR_MAP, "the expert tensor map")["experts"]


def model_sha():
    return _load(TENSOR_MAP, "the expert tensor map")["model_sha256"]


def at(time, expert_id):
    """The expert at (time, expert). The address is the whole query."""
    for e in experts():
        if e["layer"] == time and e["expert_id"] == expert_id:
            return e
    raise KeyError(f"no expert at time {time} expert {expert_id}; "
                   f"times are 0..39 and experts 0..255")


def by_time():
    """-> {time: [expert_id]}. The map, arranged as a timeline."""
    out = defaultdict(list)
    for e in experts():
        out[e["layer"]].append(e["expert_id"])
    return {k: sorted(v) for k, v in sorted(out.items())}


# ------------------------------------------- what was measured per time
def accuracy_at(time):
    """Subject classification at this time point. ASSERTED, measured."""
    al = _load(RESULTS, "the experiment")["all_layers"]
    k = str(time)
    if k not in al:
        raise KeyError(f"no measurement at time {time}")
    return al[k]


def subject_experts():
    """{subject: [(expert, mean_prob, enrichment)]} at time 20. ASSERTED."""
    t = _load(RESULTS, "the experiment")["layer_20"][
        "top_enriched_experts_by_subject"]
    return {s: [(r["expert"], r["mean_probability"],
                 r["enrichment_over_global"]) for r in rows]
            for s, rows in t.items()}


def subjects_for(expert_id, time=20):
    if time != 20:
        raise ValueError(
            f"per-expert enrichments were exported only at time 20; "
            f"time {time} has classification accuracy but no per-expert "
            f"breakdown, and this will not interpolate one")
    out = [(s, p, n) for s, rows in subject_experts().items()
           for e, p, n in rows if e == expert_id]
    return sorted(out, key=lambda r: -r[2])


# --------------------------------------------------- derived, and checked
def slot_count():
    E = experts()
    times = {e["layer"] for e in E}
    ids = {e["expert_id"] for e in E}
    n = len(times) * len(ids)
    if n != len(E):
        raise ArithmeticError(f"{len(times)} x {len(ids)} = {n} but the map "
                              f"holds {len(E)}")
    return n, (f"{len(ids)} experts x {len(times)} time points = {n:,}; "
               f"the map holds exactly that many")


def slice_arithmetic():
    """Every slice length re-derived from shape and quantization."""
    ok = bad = 0
    for e in experts():
        for t in e["tensor_refs"]:
            h, f, _n = t["packed_shape"]
            q = t["quantization"]
            if q not in SUPERBLOCK:
                raise KeyError(f"unknown quantization {q}")
            d = h * f * SUPERBLOCK[q] // 256
            if d == t["expert_slice_bytes"]:
                ok += 1
            else:
                bad += 1
    if bad:
        raise ArithmeticError(f"{bad} slice lengths do not follow from "
                              f"shape x quantization")
    return ok, (f"{ok:,} slice lengths re-derived from shape and "
                f"quantization alone, {bad} differ")


def tiling():
    """The 256 slices of each packed tensor must abut exactly."""
    by = defaultdict(list)
    for e in experts():
        for t in e["tensor_refs"]:
            by[(e["layer"], t["role"])].append(
                (t["expert_slice_offset"], t["expert_slice_bytes"]))
    gaps = boundaries = 0
    for v in by.values():
        v.sort()
        for i in range(len(v) - 1):
            boundaries += 1
            if v[i][0] + v[i][1] != v[i + 1][0]:
                gaps += 1
    if gaps:
        raise ArithmeticError(f"{gaps} gaps or overlaps")
    return boundaries, (f"{len(by)} packed tensors, {boundaries:,} internal "
                        f"boundaries, {gaps} gaps or overlaps")


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("slot_count", lambda: slot_count()[1])
    t("keys_distinct", _keys)
    t("slice_arithmetic", lambda: slice_arithmetic()[1])
    t("tiling", lambda: tiling()[1])
    t("every_time_full", _full)
    t("no_interpolation", _nointerp)
    return all(o[1] for o in out), out


def _keys():
    E = experts()
    keys = {e["key"] for e in E}
    if len(keys) != len(E):
        raise ArithmeticError(f"{len(E) - len(keys)} experts share a key")
    return f"{len(keys):,} distinct 256-bit keys for {len(E):,} experts"


def _full():
    bt = by_time()
    sizes = {len(v) for v in bt.values()}
    if sizes != {256}:
        raise ArithmeticError(f"time points hold {sizes} experts, not 256")
    acc = [accuracy_at(t)["representation_accuracy"] for t in bt]
    return (f"all {len(bt)} time points hold 256 experts; subject "
            f"classification {min(acc):.0%}-{max(acc):.0%} across them, "
            f"so the signal is not localised to one time")


def _nointerp():
    try:
        subjects_for(42, time=7)
    except ValueError:
        return ("asked for per-expert subjects at a time where none were "
                "exported, it refuses rather than interpolating")
    raise ArithmeticError("interpolated a breakdown that was never measured")


# --------------------------------------------------- the Atlas interface
R_AT = re.compile(r'\bexpert\s+(\d+)\b.{0,20}\b(?:layer|time)\s+(\d+)\b', re.I)
R_TIME = re.compile(r'\b(?:layer|time)\s+(\d+)\b', re.I)
R_SUBJ = re.compile(r'\bexperts?\b.{0,24}\b(?:for|route[sd]?|handle[sd]?)\b'
                    r'\s+([a-z_]+)', re.I)
R_EID = re.compile(r'\bwhat subject\b.{0,20}\bexpert\s+(\d+)', re.I)
R_COUNT = re.compile(r'\bhow many\b.{0,30}\bexperts?\b', re.I)


def route_expert(q):
    """-> (status, answer, expert, check, provenance). Atlas's shape."""
    if not re.search(r'\bqwen\b|\bexperts?\b', q, re.I):
        return PASS, None, "qwen_expert_map", None, "not a Qwen question"
    try:
        m = R_AT.search(q)
        if m:
            eid, tm = int(m.group(1)), int(m.group(2))
            e = at(tm, eid)
            roles = ", ".join(f"{t['role']} {t['quantization']}"
                              for t in e["tensor_refs"])
            return (ANSWERED, e["key"], "qwen_expert_map", "IDENTITY",
                    f"ASSERTED: expert {eid} at time {tm} (layer {tm}); "
                    f"{roles}; model sha {model_sha()[:12]}")
        m = R_EID.search(q)
        if m:
            subs = subjects_for(int(m.group(1)))
            if not subs:
                return (REFUSED, None, "qwen_expert_map", None,
                        f"expert {m.group(1)} is in no subject's top-5; "
                        f"5 per subject were exported, not all 256")
            return (ANSWERED, ", ".join(f"{s} (x{n:.1f})" for s, _p, n in subs),
                    "qwen_expert_map", "NONE",
                    f"ASSERTED at time 20. {LIMITS}")
        m = R_SUBJ.search(q)
        if m:
            subj = m.group(1).lower()
            se = subject_experts()
            if subj not in se:
                return (REFUSED, None, "qwen_expert_map", None,
                        f"{subj!r} is not one of the {len(se)} subjects "
                        f"tested: {sorted(se)}")
            return (ANSWERED,
                    ", ".join(f"{e} (x{n:.1f})" for e, _p, n in se[subj]),
                    "qwen_expert_map", "NONE",
                    f"ASSERTED at time 20. {LIMITS}")
        # A named time beats the global count. "how many experts at
        # layer 3" matched the count pattern first and answered
        # 10,240 -- the whole model, for a question about one time
        # point. The more specific reading wins, which is the same
        # ordering rule atlas.py's cascade is built on.
        m = R_TIME.search(q)
        if m:
            tm = int(m.group(1))
            a_ = accuracy_at(tm)
            per = len(by_time()[tm])
            if R_COUNT.search(q):
                return (ANSWERED, per, "qwen_expert_map", "ENUMERATE",
                        f"DERIVED: {per} experts counted at time {tm}, of "
                        f"{slot_count()[0]:,} across all 40")
            return (ANSWERED, f"{per} experts at time {tm}",
                    "qwen_expert_map", "NONE",
                    f"ASSERTED: subject classification "
                    f"{a_['representation_accuracy']:.0%} from the router "
                    f"input here")
        if R_COUNT.search(q):
            n, why = slot_count()
            return ANSWERED, n, "qwen_expert_map", "INVERSE", f"DERIVED: {why}"
    except (FileNotFoundError, KeyError, ValueError) as e:
        return REFUSED, None, "qwen_expert_map", None, str(e)
    return PASS, None, "qwen_expert_map", None, "no Qwen pattern matched"


if __name__ == "__main__":
    n, why = slot_count()
    print(f"THE MAP   {why}")
    print(f"          model {MODEL.name}")
    print(f"          sha   {model_sha()}")
    print(f"          {'present' if MODEL.exists() else 'ABSENT'}, "
          f"and not run by anything here")

    print("\nDERIVED, each with its check")
    for fn in (slice_arithmetic, tiling):
        print("  " + fn()[1])

    print("\nTHE TIMELINE -- 40 time points, 256 experts each")
    bt = by_time()
    for tm in list(bt)[:3] + ["..."] + list(bt)[19:21] + ["..."] + list(bt)[-2:]:
        if tm == "...":
            print("   ...")
            continue
        a = accuracy_at(tm)
        e0 = at(tm, 0)
        extra = ""
        if tm == 20:
            extra = f"   <- {len(subject_experts())} subjects mapped here"
        print(f"   t={tm:<3} 256 experts  class {a['representation_accuracy']:.0%}"
              f"  expert0 {e0['key'][:16]}{extra}")

    ok, res = check()
    print()
    for name, good, detail in res:
        print(f"{'PASS' if good else 'FAIL'}  {name:<18}{detail}")
    print("\nall:", ok)
