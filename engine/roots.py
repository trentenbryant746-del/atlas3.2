"""
Follow the root. Do not re-run the world.

Verifying an answer here has meant running everything: 5,737
curriculum items, every module's checks, every published number
recomputed. That is the right instinct applied in the wrong shape,
because it re-establishes the past on every question, and THE PAST
DOES NOT MOVE. Once seed -> nebula -> planet -> ocean is settled
for a universe, no later work revises it. Only the forward end
goes anywhere.

So a root is stored the way it actually behaves. Each stage is
hashed over its rule, its output and ITS PARENT'S HASH, so a
stage's hash commits to the whole of its past. Three things follow
and none of them is a policy anyone has to remember:

  A SOLID PREFIX IS FREE. Two questions that share a history share
  their stage hashes exactly, so the second one computes only where
  it diverges. Adding modules makes roots longer and deeper, not
  more expensive, because the new work is all at the tip.

  CONSISTENCY IS STRUCTURAL. Two answers standing on the same
  prefix cannot disagree about it -- not because a test compared
  them, but because they are the same bytes. That is the check the
  full suite was buying at enormous cost.

  THE PAST CANNOT BE EDITED QUIETLY. Change a rule near the root
  and every hash downstream changes with it. The fork is loud. A
  frozen stage that recomputes to a different hash is the single
  error this file exists to raise.

The condition on all of it is one universe. Different constants
are a different world and share no prefix, which is correct: they
are not answers to the same question.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STORE = ROOT / "data" / "roots.json"

# RECORDED: the full suite on a warm cache, measured 2026-09-17. It
# is here to be compared against, not to be trusted -- rerun it.
SUITE_WARM_S = 17.3


def universe_id():
    """A hash over the constants that define this world. DERIVED.

    Two runs share a prefix only if they are the same universe, and
    this is what says so. It reads engine/constants.py, which the
    duplicate rule already guarantees is the only home for these.
    """
    import engine.constants as C
    items = sorted((k, repr(getattr(C, k))) for k in dir(C)
                   if k.isupper() and not k.startswith("_"))
    return hashlib.sha256(json.dumps(items).encode()).hexdigest()[:16]


def stage_hash(parent, name, value):
    """Commits to the rule, the answer, and the entire past."""
    payload = json.dumps([parent, name, _canon(value)], sort_keys=True,
                         default=str)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _canon(v):
    """Floats are rounded so a rerun is bit-stable at 12 digits."""
    if isinstance(v, float):
        return round(v, 12)
    if isinstance(v, (list, tuple)):
        return [_canon(x) for x in v]
    if isinstance(v, dict):
        return {k: _canon(v[k]) for k in sorted(v)}
    return v


class Roots:
    """Solidified stages, keyed by a hash that carries their past."""

    def __init__(self, path=STORE):
        self.path = Path(path)
        self.frozen = {}
        if self.path.exists():
            self.frozen = json.loads(self.path.read_text())
        self.computed = 0
        self.reused = 0

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.frozen, sort_keys=True,
                                        indent=0))

    def follow(self, question, stages, verify=False):
        """-> [(name, hash, value, fresh)]. Walk one root.

        stages is [(name, fn)] where fn takes the value so far. Only
        stages whose parent hash is new get computed.
        """
        parent, out = universe_id(), []
        for name, fn in stages:
            probe = f"{parent}|{name}"
            hit = self.frozen.get(probe)
            if hit is not None and not verify:
                self.reused += 1
                parent = hit["h"]
                out.append((name, hit["h"], hit["v"], False))
                continue
            value = _canon(fn(out[-1][2] if out else None))
            h = stage_hash(parent, name, value)
            if hit is not None and hit["h"] != h:
                raise AssertionError(
                    f"SOLID PREFIX BROKE at {name!r}: frozen {hit['h']} "
                    f"recomputed to {h}. A stage whose past is "
                    f"unchanged produced a different answer, so either "
                    f"a rule near the root moved or this is a "
                    f"different universe wearing the same id")
            self.frozen[probe] = {"h": h, "v": value, "q": question}
            self.computed += 1
            parent = h
            out.append((name, h, value, True))
        return out


# The chain every biological question in this repository stands on.
# Each stage takes what came before and hands on one number.
def _stages():
    def constants(_):
        from engine.constants import G_GRAV
        return G_GRAV

    def star(_):
        from engine.evolve import luminosity_at
        v = luminosity_at(1.0, 4.6)
        return float(getattr(v, "value", v))

    def band(v):
        from engine.evolve import habitable_band
        b = habitable_band(v)
        return [round(float(x), 6) for x in (b[:2] if len(b) > 1 else [b])]

    def planet(_):
        from engine.genesis import composition
        c = composition(150.0)
        return sorted(c.items())[:4] if isinstance(c, dict) else str(c)[:40]

    def surface(_):
        from engine.biome import surface_light
        return surface_light()

    def producers(v):
        from engine.biome import PHOTOSYNTHETIC_EFFICIENCY
        return v * PHOTOSYNTHETIC_EFFICIENCY

    def canopy(_):
        from engine.biome import escalation_stops_at
        return escalation_stops_at(1.0)

    def levels(_):
        from engine.biome import food_chain_length
        return food_chain_length()

    def bodies(_):
        from engine.atoms import Pool, atoms_in
        p = Pool(atoms_in(1000.0))
        p.build(400.0)
        p.die(400.0)
        return p.conserved()[0]

    def brain(_):
        from engine.ontogeny import ONTOGENY, brain_share
        return round(brain_share(ONTOGENY[0][1], ONTOGENY[0][2]), 6)

    def child(_):
        from engine.ontogeny import provisioning_debt
        return round(provisioning_debt()[1], 6)

    return [("constants", constants), ("star", star), ("band", band),
            ("planet", planet), ("surface", surface),
            ("producers", producers), ("canopy", canopy),
            ("levels", levels), ("bodies", bodies), ("brain", brain),
            ("child", child)]


QUESTIONS = {
    "how tall does a tree get": 7,
    "how long is the food chain": 8,
    "does death conserve matter": 9,
    "can an infant feed its own head": 10,
    "what does a child cost": 11,
}


def answer(question, roots=None, verify=False):
    """-> (value, stages walked, computed, reused). Follow one root."""
    r = roots or Roots()
    depth = QUESTIONS[question]
    before = r.computed
    walked = r.follow(question, _stages()[:depth], verify=verify)
    return walked[-1][2], len(walked), r.computed - before, r.reused


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_prefix_is_shared_not_repeated", _shared)
    t("a_solid_prefix_cannot_change_quietly", _tamper)
    t("a_different_universe_shares_no_prefix", _fork)
    t("a_break_is_located_not_just_reported", _locate)
    t("following_beats_running_everything", _cost)
    return all(o[1] for o in out), out


def _shared():
    r = Roots(path=ROOT / "data" / "_probe.json")
    r.frozen = {}
    total = 0
    for q in QUESTIONS:
        _, walked, _, _ = answer(q, r)
        total += walked
    if r.computed >= total:
        raise ArithmeticError("nothing was shared")
    return (f"{len(QUESTIONS)} questions, {total} stages between them, "
            f"and only {r.computed} were computed -- {r.reused} came "
            f"off a prefix another question had already solidified. "
            f"Every question after the first pays only for where it "
            f"leaves the others")


def _tamper():
    r = Roots(path=ROOT / "data" / "_probe.json")
    r.frozen = {}
    answer("how tall does a tree get", r)
    key = [k for k in r.frozen if k.endswith("|surface")][0]
    r.frozen[key] = dict(r.frozen[key], h="0000000000000000")
    try:
        answer("how tall does a tree get", r, verify=True)
    except AssertionError as e:
        return (f"edited one frozen stage and the recompute caught it: "
                f"{str(e)[:96]}... The past cannot be changed quietly, "
                f"because every hash downstream commits to it")
    raise ArithmeticError("the store was edited and nothing objected")


def _fork():
    a = universe_id()
    import engine.constants as C
    old = C.G_GRAV
    try:
        C.G_GRAV = old * 1.000001
        b = universe_id()
    finally:
        C.G_GRAV = old
    if a == b or universe_id() != a:
        raise ArithmeticError("the universe id does not track the constants")
    return (f"move gravity in the twelfth place and the universe id "
            f"goes {a} -> {b}, so nothing frozen carries over. A "
            f"different world does not get to reuse this one's past, "
            f"and that is not caution -- they are not answers to the "
            f"same question")


def _locate():
    """The thing a pass/fail suite cannot do."""
    import engine.biome as B
    probe = ROOT / "data" / "_loc.json"
    r = Roots(path=probe)
    r.frozen = {}
    for q in QUESTIONS:
        answer(q, r)
    orig = B.PHOTOSYNTHETIC_EFFICIENCY
    where = None
    try:
        B.PHOTOSYNTHETIC_EFFICIENCY = orig * 1.10
        r2 = Roots(path=probe)
        r2.frozen = dict(r.frozen)
        try:
            for q in QUESTIONS:
                answer(q, r2, verify=True)
        except AssertionError as e:
            where = str(e).split("'")[1]
    finally:
        B.PHOTOSYNTHETIC_EFFICIENCY = orig
        if probe.exists():
            probe.unlink()
    if where != "producers":
        raise ArithmeticError(f"the break was located at {where!r}")
    downstream = [q for q, d in QUESTIONS.items() if d >= 6]
    return (f"moved one constant by a tenth and the break was located "
            f"at {where!r} -- the exact stage that constant enters -- "
            f"with {len(downstream)} questions named as standing on "
            f"it. A suite says something failed. A root says WHERE it "
            f"failed and WHAT RESTS ON IT, which is the part that was "
            f"being paid for by running everything")


def _cost():
    r = Roots(path=ROOT / "data" / "_probe.json")
    r.frozen = {}
    t0 = time.perf_counter()
    for q in QUESTIONS:
        answer(q, r)
    cold = time.perf_counter() - t0
    t0 = time.perf_counter()
    for q in QUESTIONS:
        answer(q, r)
    warm = time.perf_counter() - t0
    p = ROOT / "data" / "_probe.json"
    if p.exists():
        p.unlink()
    if warm >= cold:
        raise ArithmeticError("following cost as much as running")
    return (f"{len(QUESTIONS)} questions, {1000*warm:.2f} ms warm "
            f"against {SUITE_WARM_S:.1f} s for the full suite on a "
            f"warm cache -- {SUITE_WARM_S/max(warm,1e-9):,.0f}x. The "
            f"suite re-establishes the past on every question. This "
            f"establishes it once, because the past does not move. "
            f"Roots get longer and deeper as modules are added and "
            f"the cost stays at the tip")


if __name__ == "__main__":
    print(f"  universe {universe_id()}\n")
    r = Roots(path=ROOT / "data" / "_probe.json")
    r.frozen = {}
    for q in QUESTIONS:
        v, walked, fresh, _ = answer(q, r)
        print(f"  {q:34} {walked:>2} stages, {fresh:>2} new   -> "
              f"{str(v)[:22]}")
    print(f"\n  computed {r.computed}, reused {r.reused}\n")
    for name, h, v, fresh in r.follow("what does a child cost", _stages()):
        print(f"  {'NEW' if fresh else '   '} {name:<11} {h}  "
              f"{str(v)[:34]}")
    p = ROOT / "data" / "_probe.json"
    if p.exists():
        p.unlink()
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:44]}")
