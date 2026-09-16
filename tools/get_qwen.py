#!/usr/bin/env python3
"""
Assemble and VERIFY the Qwen artifacts. Same discipline as
tools/get_godot.py: pin the hash, check the bytes, refuse on
mismatch.

WHY ANY OF THIS. The repository carries source, not data. The Qwen
artifacts are 117 MiB and the model they describe is 21 GB, and
neither belongs in git -- so the repo carries their HASHES and this
tool goes and gets them.

    the artifacts     expert-tensor-map.json, route-events.jsonl,
                      the GGUF header and the experiment results.
                      117 MiB. Every module here reads them, so the
                      tool must produce them or nothing runs.

    the 21 GB GGUF    NOTHING IN THIS REPO OPENS IT. The expert map
                      is byte offsets, not weights. Pinned and never
                      fetched unless you want the one check that
                      needs it -- comparing the map's claimed bytes
                      against the real file's size.

A NOTE ON THE 100 MB LIMIT, because it is easy to misremember.
GitHub refuses any single FILE over 100 MB; there is no such cap on
the repository as a whole. The largest artifact here is 106.1 MiB,
which is why it is stored split in two. That split is kept because
it makes each piece uploadable anywhere, not because the total
would have been refused.

WHERE THEY COME FROM. Three sources are tried in order, and each is
verified the same way:

    1. already in data/qwen and hashing correctly -> use it
    2. a local directory, if you have the originals (ATLAS_QWEN_DIR)
    3. a URL base (ATLAS_QWEN_URL or --url), for a GitHub Release
       asset or any other host

A Release asset takes files up to 2 GB and does not count against
the repository, which is the natural home for these. Until one is
published, the local directory path is what works.

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
import os
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


def _local_dirs():
    """Where the originals might already be, in order of preference."""
    out = []
    env = os.environ.get("ATLAS_QWEN_DIR")
    if env:
        out.append(Path(env))
    out += [Path("/Users/trentenbryant/Documents/Codex/2026-09-14/"
                 "files-mentioned-by-the-user-atlas/outputs/qwen-local/"
                 "atlas"),
            Path("/Users/trentenbryant/Documents/Codex/2026-09-14/"
                 "files-mentioned-by-the-user-atlas/outputs/qwen-local/"
                 "atlas/qwen-complete-map"),
            Path("/Users/trentenbryant/Documents/Codex/2026-09-14/"
                 "files-mentioned-by-the-user-atlas/outputs/qwen-local/"
                 "atlas/benchmark-runs")]
    return [d for d in out if d.is_dir()]


def _fetch_one(name, spec, url_base):
    """-> (path, how). Verified, or it does not return a path."""
    QDIR.mkdir(parents=True, exist_ok=True)
    dest = QDIR / name
    if dest.exists() and sha256(dest) == spec["sha256"]:
        return dest, "already present and verified"

    for d in _local_dirs():
        src = d / name
        if src.exists() and src.stat().st_size == spec["bytes"]:
            if sha256(src) == spec["sha256"]:
                dest.write_bytes(src.read_bytes())
                return dest, f"copied from {d}"

    if url_base:
        import urllib.request
        url = url_base.rstrip("/") + "/" + name
        tmp = dest.with_suffix(dest.suffix + ".part")
        try:
            urllib.request.urlretrieve(url, tmp)
        except Exception as e:
            if tmp.exists():
                tmp.unlink()
            return None, f"download failed: {e}"
        got = sha256(tmp)
        if got != spec["sha256"]:
            tmp.unlink()
            return None, (f"REFUSED: downloaded {name} hashes "
                          f"{got[:16]}..., pinned {spec['sha256'][:16]}...")
        tmp.rename(dest)
        return dest, f"downloaded from {url_base}"

    return None, ("not found locally and no URL given -- set "
                  "ATLAS_QWEN_URL or pass --url")


def fetch(url_base=None):
    """Get every pinned part, from wherever it can be had."""
    m = manifest()
    got, failed = [], []
    for name, spec in m["committed"].items():
        p, how = _fetch_one(name, spec, url_base)
        (got if p else failed).append((name, how))
    return got, failed


def assemble(force=False, url_base=None):
    """Produce the whole file, and verify the WHOLE, not just pieces.

    THE PARTS ARE A TRANSPORT FORMAT, NOT THE SOURCE. A cold start
    found this: the split halves exist only where this tool wrote
    them, while the original 106.1 MiB file sits intact in the
    directory the experiment produced. Looking only for parts meant
    a machine holding the real thing could not use it. So the whole
    file is looked for first, and the split is what gets it ONTO a
    host with a per-file limit, not what defines it.
    """
    m = manifest()
    name, spec = next(iter(m["assembled"].items()))
    out = QDIR / name
    if out.exists() and not force:
        if sha256(out) == spec["sha256"]:
            return out, "already assembled and verified"
        out.unlink()

    # 1. the whole file, sitting somewhere local
    for d in _local_dirs():
        src = d / name
        if src.exists() and src.stat().st_size == spec["bytes"]:
            if sha256(src) == spec["sha256"]:
                QDIR.mkdir(parents=True, exist_ok=True)
                out.write_bytes(src.read_bytes())
                return out, f"copied whole from {d}"

    # 2. failing that, the parts -- fetched if a URL was given
    parts = [QDIR / p for p in spec["from"]]
    if url_base and not all(p.exists() for p in parts):
        for pname in spec["from"]:
            _fetch_one(pname, m["committed"][pname], url_base)
        parts = [QDIR / p for p in spec["from"]]
    missing = [p.name for p in parts if not p.exists()]
    if missing:
        raise SystemExit(
            f"cannot assemble {name}: no whole copy in {len(_local_dirs())} "
            f"local directories and missing parts {missing}. Set "
            f"ATLAS_QWEN_DIR to a directory holding it, or ATLAS_QWEN_URL "
            f"to a host serving the parts.")
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
    ap.add_argument("--url", default=os.environ.get("ATLAS_QWEN_URL"),
                    help="base URL holding the pinned artifacts, e.g. a "
                         "GitHub Release asset directory")
    a = ap.parse_args(argv)
    if a.check:
        return report()
    m = manifest()
    split = set(next(iter(m["assembled"].values()))["from"])
    got, failed = fetch(a.url)
    for n, how in got:
        print(f"ok  {n:<42}{how}")
    # A missing PART is not a failure if the whole file can be had --
    # the parts exist to cross a per-file size limit, nothing more.
    hard = [(n, w) for n, w in failed if n not in split]
    for n, how in failed:
        print(f"{'FAIL' if n in dict(hard) else 'note'}  {n}: {how}")
    if hard:
        return 1
    out, why = assemble(force=a.force, url_base=a.url)
    print(f"ok  {out.relative_to(ROOT)}  {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
