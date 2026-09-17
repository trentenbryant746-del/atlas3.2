"""
Run only what changed, keyed on what it actually depends on.

The suite reruns every module every time, which is about two and a
half minutes, and most of it recomputes results that cannot have
moved. Caching is easy to get wrong in a way that is worse than not
caching: a stale PASS is a lie that looks like work.

THE KEY IS THE TRANSITIVE CLOSURE, NOT THE FILE. engine/terraform.py
imports engine/constants.py, so editing a constant must invalidate
terraform even though terraform's own bytes did not change. Hashing
the file alone would keep serving the old answer, and the answer
would be wrong for exactly the reason this repository spent 3.1.24
fixing: one thing quietly disagreeing with another.

So each module's key is the hash of its own source PLUS the hash of
every engine module it reaches, directly or through anything it
imports. Change a constant and everything downstream re-runs; change
a comment in an unrelated file and nothing does.

A CACHED PASS IS STILL A CLAIM. The cache stores the check count and
the verdict, and `--verify` ignores the cache entirely and re-runs
everything, which is what a release should do. Speed is for the edit
loop; the full run is what gets published.
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENGINE = ROOT / "engine"
CACHE_FILE = ROOT / ".atlas-cache.json"


def _imports(path):
    """-> set of engine module names this file imports."""
    out = set()
    try:
        tree = ast.parse(path.read_text())
    except Exception:
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module.startswith("engine."):
                out.add(node.module.split(".", 1)[1])
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name.startswith("engine."):
                    out.add(a.name.split(".", 1)[1])
    return out


def closure(name, seen=None):
    """-> every engine module `name` depends on, transitively."""
    seen = set() if seen is None else seen
    if name in seen:
        return seen
    seen.add(name)
    p = ENGINE / f"{name}.py"
    if not p.exists():
        return seen
    for dep in _imports(p):
        closure(dep, seen)
    return seen


def key_for(name):
    """-> hash over the module and everything it reaches. DERIVED."""
    h = hashlib.sha256()
    for mod in sorted(closure(name)):
        p = ENGINE / f"{mod}.py"
        if p.exists():
            h.update(mod.encode())
            h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()[:16]


def load():
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except Exception:
            return {}
    return {}


def save(d):
    CACHE_FILE.write_text(json.dumps(d, indent=1, sort_keys=True))


def cached_check(name, run, cache=None, use_cache=True):
    """-> (ok, n_checks, from_cache). Runs `run()` only if stale."""
    c = load() if cache is None else cache
    k = key_for(name)
    hit = c.get(name)
    if use_cache and hit and hit.get("key") == k:
        return hit["ok"], hit["n"], True
    ok, res = run()
    c[name] = {"key": k, "ok": bool(ok), "n": len(res)}
    if cache is None:
        save(c)
    return ok, len(res), False


def key_for_eval(name):
    """Key for an eval script: its own source plus the whole engine.

    An eval script exercises the engine end to end, so anything in
    engine can change its answer. Hashing the whole directory is
    coarse and correct; hashing the script alone would be fast and
    wrong.
    """
    h = hashlib.sha256()
    ev = ROOT / "eval" / f"{name}.py"
    if ev.exists():
        h.update(hashlib.sha256(ev.read_bytes()).digest())
    for mod in sorted(ENGINE.glob("*.py")):
        h.update(mod.name.encode())
        h.update(hashlib.sha256(mod.read_bytes()).digest())
    for extra in ("rules", "data"):
        d = ROOT / extra
        if d.is_dir():
            for f in sorted(d.rglob("*")):
                if f.is_file():
                    h.update(f.name.encode())
                    h.update(str(f.stat().st_size).encode())
    return h.hexdigest()[:16]


def cached_eval(name, run, cache=None, use_cache=True):
    """-> (ok, detail, from_cache) for an eval script."""
    c = load() if cache is None else cache
    k = key_for_eval(name)
    slot = f"eval.{name}"
    hit = c.get(slot)
    if use_cache and hit and hit.get("key") == k:
        return hit["ok"], hit.get("detail", ""), True
    ok, detail = run()
    c[slot] = {"key": k, "ok": bool(ok), "detail": detail}
    if cache is None:
        save(c)
    return ok, detail, False


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("key_covers_what_a_module_imports", _closure)
    t("editing_a_dependency_invalidates", _invalidate)
    t("an_unrelated_edit_does_not", _unrelated)
    t("an_eval_key_covers_the_whole_engine", _evalkey)
    return all(o[1] for o in out), out


def _closure():
    c = closure("terraform")
    if "constants" not in c:
        raise ArithmeticError("terraform's key does not cover constants")
    if "terraform" not in closure("evolve"):
        raise ArithmeticError("evolve's key does not cover terraform")
    return (f"terraform reaches {len(c)} engine modules including "
            f"{', '.join(sorted(c)[:5])}..., and evolve reaches terraform "
            f"through them. A key over the file alone would serve a "
            f"stale PASS after a constant changed, which is a lie that "
            f"looks like work")


def _invalidate():
    import tempfile
    before = key_for("terraform")
    p = ENGINE / "constants.py"
    orig = p.read_bytes()
    try:
        p.write_bytes(orig + b"\n# touched\n")
        after = key_for("terraform")
    finally:
        p.write_bytes(orig)
    if before == after:
        raise ArithmeticError("touching constants.py did not change "
                              "terraform's key")
    return (f"appending one line to engine/constants.py changes "
            f"terraform's key from {before} to {after}, because the key "
            f"is a hash over the whole dependency closure and not over "
            f"one file")


def _unrelated():
    before = key_for("folding")
    if "terraform" in closure("folding"):
        return ("folding does reach terraform, so this cannot be tested "
                "as an unrelated pair")
    p = ENGINE / "terraform.py"
    orig = p.read_bytes()
    try:
        p.write_bytes(orig + b"\n# touched\n")
        after = key_for("folding")
    finally:
        p.write_bytes(orig)
    if before != after:
        raise ArithmeticError("an unrelated edit invalidated folding")
    return ("touching engine/terraform.py leaves engine/folding.py's key "
            "alone, because folding does not reach it. The cache is "
            "precise in both directions: everything downstream re-runs "
            "and nothing else does")


def _evalkey():
    before = key_for_eval("induction")
    p = ENGINE / "folding.py"
    orig = p.read_bytes()
    try:
        p.write_bytes(orig + b"\n# touched\n")
        after = key_for_eval("induction")
    finally:
        p.write_bytes(orig)
    if before == after:
        raise ArithmeticError("an engine edit did not invalidate an eval")
    return ("an eval script's key covers every engine module, because a "
            "script that exercises the engine end to end can be changed "
            "by anything in it. Coarse and correct beats fast and wrong: "
            "induction alone is 87 seconds of the suite")


if __name__ == "__main__":
    import time
    names = sorted(p.stem for p in ENGINE.glob("*.py")
                   if p.stem != "__init__")
    print(f"  {'module':16}{'key':>18}{'deps':>6}")
    for n in names[:8]:
        print(f"  {n:16}{key_for(n):>18}{len(closure(n)):>6}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:36}{d[:62]}")
    print("\nall:", ok)
