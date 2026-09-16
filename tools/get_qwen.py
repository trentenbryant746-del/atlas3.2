#!/usr/bin/env python3
"""
Assemble and VERIFY the Qwen artifacts. Same discipline as
tools/get_godot.py: pin the hash, check the bytes, refuse on
mismatch.

WHY ANY OF THIS. Two artifacts do not fit in a git repository the
ordinary way, for two different reasons, and they are handled
differently because the reasons differ.

    route-events.jsonl   106.1 MiB, and GitHub refuses ANY file over
                         100 MB outright -- not a warning, a refused
                         push. It is SPLIT into two parts of 45.7 and
                         60.4 MiB, both committed, and reassembled
                         here. The repo therefore contains the data.

    the 21 GB GGUF       far past anything git should hold, and
                         NOTHING IN THIS REPO OPENS IT. The expert
                         map is byte offsets, not weights. So it is
                         PINNED by SHA-256 and not fetched at all
                         unless you want the one check that needs
                         it -- comparing the map's claimed bytes
                         against the real file's size.

WHAT "PINNED" MEANS, EXACTLY. data/qwen/MANIFEST.json records the
SHA-256 and byte length of every artifact, including the reassembled
whole and the model this repo does not carry. Verification recomputes
the hash and compares. A mismatch is not a warning and not a retry:
the assembled file is DELETED and the tool exits non-zero, because a
file that is nearly right is worse than one that is missing -- it
would produce numbers that look like these and are not.

That is the same rule as everywhere else here. engine/locator.py
refuses a mistyped key rather than resolving it to a neighbour;
engine/genindex.py refuses a corpus whose fingerprint has drifted.
An artifact is a key to a set of numbers, and the check symbol is
its hash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QDIR = ROOT / "data" / "qwen"
MANIFEST = QDIR / "MANIFEST.json"


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def manifest():
    if not MANIFEST.exists():
        raise SystemExit(f"no manifest at {MANIFEST}")
    return json.loads(MANIFEST.read_text())


def verify_committed(m):
    """Every committed part, against its pin."""
    bad = []
    for name, spec in m["committed"].items():
        p = QDIR / name
        if not p.exists():
            bad.append((name, "missing"))
            continue
        if p.stat().st_size != spec["bytes"]:
            bad.append((name, f"{p.stat().st_size} bytes, pinned "
                              f"{spec['bytes']}"))
            continue
        got = sha256(p)
        if got != spec["sha256"]:
            bad.append((name, f"sha {got[:16]} against pinned "
                              f"{spec['sha256'][:16]}"))
    return bad


def assemble(force=False):
    """Join the parts and verify the WHOLE, not just the pieces."""
    m = manifest()
    name, spec = next(iter(m["assembled"].items()))
    out = QDIR / name
    if out.exists() and not force:
        got = sha256(out)
        if got == spec["sha256"]:
            return out, "already assembled and verified"
        out.unlink()
    parts = [QDIR / p for p in spec["from"]]
    missing = [p.name for p in parts if not p.exists()]
    if missing:
        raise SystemExit(f"cannot assemble: missing {missing}")
    with open(out, "wb") as w:
        for p in parts:
            w.write(p.read_bytes())
    got = sha256(out)
    if got != spec["sha256"]:
        out.unlink()
        raise SystemExit(
            f"REFUSED: assembled {name} hashes {got[:16]}..., pinned "
            f"{spec['sha256'][:16]}.... Deleted. A file that is nearly "
            f"right produces numbers that look like these and are not.")
    if out.stat().st_size != spec["bytes"]:
        out.unlink()
        raise SystemExit("REFUSED: assembled length does not match the pin")
    return out, f"assembled from {len(parts)} parts and verified"


def report():
    m = manifest()
    print("committed parts, against their pins")
    bad = verify_committed(m)
    for name, spec in m["committed"].items():
        why = dict(bad).get(name)
        print(f"  {'FAIL' if why else 'ok  '}  {name:<42}"
              f"{spec['bytes']/2**20:8.1f} MiB" + (f"  {why}" if why else ""))
    name, spec = next(iter(m["assembled"].items()))
    out = QDIR / name
    state = ("not assembled" if not out.exists()
             else "verified" if sha256(out) == spec["sha256"]
             else "PRESENT BUT WRONG")
    print(f"\nassembled\n  {name:<44}{spec['bytes']/2**20:8.1f} MiB  {state}")
    print(f"  why split: {spec['why_split']}")
    mn, ms = next(iter(m["not_committed"].items()))
    print(f"\npinned but not carried\n  {mn}")
    print(f"  sha256 {ms['sha256']}")
    print(f"  {ms['why']}")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="report what is present and whether it verifies")
    ap.add_argument("--force", action="store_true",
                    help="reassemble even if a verified copy exists")
    a = ap.parse_args(argv)
    if a.check:
        return report()
    m = manifest()
    bad = verify_committed(m)
    if bad:
        for n, w in bad:
            print(f"FAIL  {n}: {w}")
        return 1
    out, why = assemble(force=a.force)
    print(f"ok  {out.relative_to(ROOT)}  {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
