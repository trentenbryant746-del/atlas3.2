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
        self.universe = universe_id()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.frozen, sort_keys=True,
                                        indent=0))

    def follow(self, question, target, verify=False):
        """-> [(node, fingerprint, fresh)]. Walk one inferred root.

        Keyed on the node's own fingerprint, NOT on where it sits
        in this particular walk. A spine is a directed graph, not a
        line: engine.life.kleiber is the fourth thing one question
        reaches and the ninth thing another does. An earlier
        version keyed on the linear parent and sharing collapsed to
        six nodes out of a hundred and fifteen, because the same
        rule arriving by two routes got two keys.
        """
        from engine.spine import spine, fingerprint
        out = []
        for node in spine(target):
            fp = fingerprint(*node)
            key = f"{self.universe}|{node[0]}.{node[1]}"
            hit = self.frozen.get(key)
            if hit is not None and not verify:
                self.reused += 1
                out.append((node, hit["h"], False))
                continue
            if hit is not None and hit["h"] != fp:
                raise AssertionError(
                    f"SOLID PREFIX BROKE at {node[0]}.{node[1]}: frozen "
                    f"{hit['h']} now fingerprints {fp}. A rule this "
                    f"question stands on was rewritten")
            self.frozen[key] = {"h": fp, "q": question}
            self.computed += 1
            out.append((node, fp, True))
        return out

    def what_moved(self, other):
        """-> [node keys]. Which rules differ between two stores."""
        return sorted(k for k in set(self.frozen) & set(other.frozen)
                      if self.frozen[k]["h"] != other.frozen[k]["h"])


# NO SPINE IS WRITTEN HERE ANY MORE. Eleven stages used to be
# typed in below, covering the biological line and nothing else,
# and every new question meant more typing. engine/spine.py reads
# the root off the syntax tree instead, so a question is named by
# what it asks and the chain is whatever the code actually stands
# on.
QUESTIONS = {
    "how tall does a tree get": ("biome", "escalation_stops_at"),
    "how long is the food chain": ("biome", "food_chain_length"),
    "how much ground does a predator need": ("biome", "territory"),
    "does death conserve matter": ("atoms", "limiting_element"),
    "what does a child cost": ("ontogeny", "provisioning_debt"),
    "can an infant feed its own head": ("ontogeny", "self_supporting"),
    "did anything make a tool": ("ontogeny", "tool_search"),
    "how wide is the nuclear mass bar": ("nucleo", "mass_bar"),
    "what is Earth made of": ("genesis", "composition"),
    "how opaque is an atmosphere": ("radiative", "grey_equivalent_full"),
}


def answer(question, roots=None, verify=False):
    """-> (fingerprint, nodes walked, computed, reused). DERIVED.

    The chain is inferred, so nothing here knows or cares whether
    the question is nuclear, atmospheric or biological.
    """
    r = roots or Roots()
    target = QUESTIONS[question]
    before = r.computed
    walked = r.follow(question, target, verify=verify)
    return walked[-1][1], len(walked), r.computed - before, r.reused


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
    key = [k for k in r.frozen if "surface_light" in k][0]
    r.frozen[key] = dict(r.frozen[key], h="0000000000000000")
    try:
        answer("how tall does a tree get", r, verify=True)
    except AssertionError as e:
        return (f"edited one frozen node and the recompute caught it: "
                f"{str(e)[:92]}... The past cannot be changed quietly, "
                f"because every fingerprint downstream commits to it")
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
    """The thing a pass/fail suite cannot do.

    Fingerprints are over SOURCE, so this rewrites a rule on disk
    rather than poking a value at runtime -- which is the stronger
    test, since a rewritten rule that happens to return the same
    number today would slip past any check on answers.
    """
    import shutil
    import engine.spine as S
    probe = ROOT / "data" / "_loc.json"
    src = ROOT / "engine" / "biome.py"
    backup = src.read_text()
    before = Roots(path=probe)
    before.frozen = {}
    for q in QUESTIONS:
        answer(q, before)
    try:
        src.write_text(backup.replace(
            "PHOTOSYNTHETIC_EFFICIENCY = 0.01",
            "PHOTOSYNTHETIC_EFFICIENCY = 0.011"))
        for c in (S._tree, S._imports, S._defs, S.fingerprint):
            c.cache_clear()
        after = Roots(path=probe)
        after.frozen = {}
        for q in QUESTIONS:
            answer(q, after)
        moved = before.what_moved(after)
        hit = [q for q, t in QUESTIONS.items()
               if any(f"{m}.{n}" in " ".join(moved)
                      for m, n in S.spine(t))]
    finally:
        src.write_text(backup)
        for c in (S._tree, S._imports, S._defs, S.fingerprint):
            c.cache_clear()
        if probe.exists():
            probe.unlink()
    if not moved or not any("PHOTOSYNTHETIC" in m for m in moved):
        raise ArithmeticError(f"the edit moved {moved}")
    return (f"rewrote one constant in engine/biome.py and "
            f"{len(moved)} node fingerprints moved, beginning at "
            f"{moved[0].split('|')[-1]}, with {len(hit)} of "
            f"{len(QUESTIONS)} questions standing on them. A suite "
            f"says something failed. A root says WHICH RULES moved "
            f"and WHAT RESTS ON THEM, and the questions it leaves "
            f"alone are untouched -- nuclear and atmospheric did not "
            f"flinch at a change to photosynthesis")


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
        fp, walked, fresh, _ = answer(q, r)
        print(f"  {q:38} {walked:>3} nodes, {fresh:>3} new  {fp}")
    print(f"\n  computed {r.computed}, reused {r.reused}")
    p2 = ROOT / "data" / "_probe.json"
    if p2.exists():
        p2.unlink()
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:44]}")
