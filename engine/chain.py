"""
A universe history as a 256-bit hash chain.

Each expansion step is digested to 256 bits and linked to the one before:

    link[0] = H( seed )
    link[n] = H( link[n-1] || canonical(state[n]) )

The HEAD is a single 256 bits that identifies the entire history. You do not
need 1056 bits, or any multiple of 256 -- the chain is why. Concatenating a
digest per epoch grows with the number of epochs; chaining them does not,
and it buys the property concatenation does not have: TAMPER EVIDENCE.
Alter any epoch and every link after it changes, so the head detects an
edit anywhere in cosmic history.

Three things this gives that a plain seed does not:

    IDENTITY     one 256-bit head names a whole Big-Bang-to-now history
    INTEGRITY    any alteration anywhere changes the head
    MEMBERSHIP   an epoch's state can be proved to belong to a head by
                 replaying the chain from it, without re-running the physics

This is engine/../seal.py's discipline -- belt-atlas hashed source files in
sorted order and chained them -- applied to time instead of to a directory.
"""
from __future__ import annotations

import hashlib
import json


def canon(state) -> str:
    """a canonical encoding, so the digest depends on VALUES not formatting"""
    return json.dumps(state, sort_keys=True, separators=(",", ":"),
                      default=lambda o: round(o, 12) if isinstance(o, float) else str(o))


def link(prev_hex: str, state) -> str:
    return hashlib.sha256((prev_hex + "|" + canon(state)).encode()).hexdigest()


def build(seed: str, states) -> dict:
    """states: [(epoch_name, state_dict), ...] in time order"""
    cur = hashlib.sha256(seed.encode()).hexdigest()
    links = [{"epoch": "seed", "link": cur}]
    for name, st in states:
        cur = link(cur, {"epoch": name, "state": st})
        links.append({"epoch": name, "link": cur})
    return {"seed": seed, "head": cur, "links": links,
            "bits": 256, "epochs": len(states)}


def verify(chain, states) -> tuple[bool, str]:
    rebuilt = build(chain["seed"], states)
    if rebuilt["head"] != chain["head"]:
        for a, b in zip(chain["links"], rebuilt["links"]):
            if a["link"] != b["link"]:
                return False, f"first divergence at epoch {a['epoch']!r}"
        return False, "length differs"
    return True, f"head {chain['head'][:16]}... over {chain['epochs']} epochs"


def membership(chain, index, states) -> tuple[bool, str]:
    """prove epoch `index` belongs to this head by replaying from its link"""
    cur = chain["links"][index]["link"]
    for name, st in states[index:]:
        cur = link(cur, {"epoch": name, "state": st})
    ok = cur == chain["head"]
    return ok, (f"replaying from {chain['links'][index]['epoch']!r} reaches "
                f"{'the head' if ok else 'a different head'}")
