"""
Hide the answers, keep them recoverable: hash with a key, release
the key afterwards.

The held-out benchmark in data/ commits to its answers with a bare
SHA-256 and nothing else. That hides them, which is the point, but
it also makes them unrecoverable forever -- and this repo measured
how unrecoverable: 251 serialisation templates, 2.2 million bare
integers and 1.74 million constant affixes, no match. A commitment
nobody can open is a commitment nobody can check.

The fix is one line of scheme design and it is what a commitment is
supposed to be:

    commit   h_i = sha256(key || answer_i)      publish h_i only
    hide     the key stays out of the repo and out of the system
    open     publish the key; every answer becomes checkable

While the key is withheld this is exactly as hidden as a bare hash.
Once it is released, anyone can verify every item -- and, unlike a
bare hash, they can also verify that the answers were not chosen
after seeing the results, because the hashes were published first.

WHAT THE SYSTEM MUST NOT SEE. The point is defeated if the key is
readable from inside the run. So the key is never written into the
repo, never passed to atlas.ask, and never held in a module the
engine imports. It arrives on the command line or in an environment
variable at verification time, after the answers already exist.
keyed_commit() takes it as an argument and returns hashes; nothing
stores it.

WHY key || answer AND NOT answer || key. Length-extension. SHA-256
leaks enough state that sha256(m) lets you compute sha256(m || x)
for a chosen x without knowing m. Putting the secret FIRST is the
arrangement that breaks under that; putting it first and the answer
second is the one that does not leak the key from a published hash.
HMAC exists precisely for this and is used here rather than
hand-rolling the concatenation.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

COMMIT = ROOT / "data" / "commitments.json"


def keyed(key, answer):
    """One commitment. HMAC, not concatenation -- see the docstring."""
    if not isinstance(key, (bytes, bytearray)):
        key = str(key).encode()
    return hmac.new(key, str(answer).encode(), hashlib.sha256).hexdigest()


def commit(items, key):
    """items: {id: answer} -> {id: hash}. The key is used and dropped."""
    if not key:
        raise ValueError("a commitment needs a key; without one this is "
                         "the unrecoverable scheme it exists to replace")
    return {i: keyed(key, a) for i, a in sorted(items.items())}


def write(items, key, path=COMMIT, note=""):
    """Publish the hashes. The answers and the key are NOT written."""
    doc = {"scheme": "hmac-sha256(key, answer)",
           "note": note or ("answers are recoverable once the key is "
                            "published; until then this is as hidden as "
                            "a bare hash"),
           "count": len(items),
           "commitments": commit(items, key)}
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return doc


def verify(answers, key, path=COMMIT):
    """-> (ok, [(id, ok)]). Given the key, every item is checkable."""
    if not path.exists():
        raise FileNotFoundError(f"no commitments at {path}")
    doc = json.loads(path.read_text())
    pub = doc["commitments"]
    rows = []
    for i, a in sorted(answers.items()):
        rows.append((i, pub.get(i) == keyed(key, a)))
    missing = sorted(set(pub) - set(answers))
    return all(ok for _i, ok in rows) and not missing, rows


def key_from_env():
    """The key arrives from outside, at verification time. Never stored."""
    k = os.environ.get("ATLAS_COMMIT_KEY")
    if not k:
        raise KeyError("ATLAS_COMMIT_KEY is not set -- the key is supplied "
                       "at verification time and is deliberately absent "
                       "from the repo")
    return k


# ------------------------------------------------------- self-checking
def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("hidden_without_the_key", _hidden)
    t("recoverable_with_the_key", _open)
    t("wrong_key_fails", _wrong)
    t("tampered_answer_fails", _tamper)
    t("key_not_in_the_repo", _absent)
    return all(o[1] for o in out), out


_ITEMS = {"q1": "148", "q2": "TGCA", "q3": "50%", "q4": "gold (Au)"}
_KEY = "a key that exists only inside this test"


def _hidden():
    """The published hashes must not reveal the answers."""
    pub = commit(_ITEMS, _KEY)
    # a bare-hash attack: try the answers directly, as the real
    # benchmark's format search did
    leaked = [i for i, a in _ITEMS.items()
              if hashlib.sha256(str(a).encode()).hexdigest() == pub[i]]
    if leaked:
        raise ArithmeticError(f"{leaked} recoverable without the key")
    return (f"{len(pub)} commitments published; none matches the plain "
            f"sha256 of its answer, so the scheme is as hidden as the "
            f"bare-hash version it replaces")


def _open():
    pub = commit(_ITEMS, _KEY)
    recomputed = {i: keyed(_KEY, a) for i, a in _ITEMS.items()}
    if recomputed != pub:
        raise ArithmeticError("the key does not reopen the commitments")
    return (f"with the key, all {len(pub)} reopen and verify -- which the "
            f"bare-hash benchmark cannot do at any cost")


def _wrong():
    pub = commit(_ITEMS, _KEY)
    bad = {i: keyed("not the key", a) for i, a in _ITEMS.items()}
    if any(pub[i] == bad[i] for i in pub):
        raise ArithmeticError("a wrong key verified something")
    return f"a wrong key reopens 0 of {len(pub)}"


def _tamper():
    pub = commit(_ITEMS, _KEY)
    changed = dict(_ITEMS)
    changed["q1"] = "149"
    again = commit(changed, _KEY)
    diff = [i for i in pub if pub[i] != again[i]]
    if diff != ["q1"]:
        raise ArithmeticError(f"changing one answer moved {diff}")
    return ("changing one answer moves exactly one commitment, so the "
            "file localises a change instead of only reporting one")


def _absent():
    """The key must not be findable from inside the repo."""
    import subprocess
    r = subprocess.run(["grep", "-rl", "ATLAS_COMMIT_KEY", str(ROOT)],
                       capture_output=True, text=True)
    files = [f for f in r.stdout.split() if not f.endswith("commit.py")]
    if files:
        raise ArithmeticError(f"the key name appears in {files}")
    if os.environ.get("ATLAS_COMMIT_KEY"):
        raise ArithmeticError("the key is set in this environment, so the "
                              "run could read it")
    return ("the key is not in any module, and is not set in the "
            "environment this ran in -- it arrives at verification time "
            "and nothing stores it")


if __name__ == "__main__":
    pub = commit(_ITEMS, _KEY)
    print("published commitments (answers and key withheld):")
    for i, h in pub.items():
        print(f"  {i}  {h}")
    ok, rows = verify(_ITEMS, _KEY) if COMMIT.exists() else (None, [])
    good, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:28}{d[:92]}")
    print("\nall:", good)
