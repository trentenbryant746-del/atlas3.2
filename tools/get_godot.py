"""
Fetch and verify the exact Godot this repo was built against.

The binary is NOT committed, and that is not a compromise -- the macOS
build is 162.7 MB and GitHub rejects any file over 100 MB outright. Git LFS
would accept it and then put a 163 MB pull on every clone against a
bandwidth quota, for a platform-specific artefact that goes stale.

Pinning the version and the checksum gives the same reproducibility with
none of that: one command, and you have byte-for-byte the build that
produced every gdscript number in the README.

    python3 tools/get_godot.py              fetch, verify, unpack
    python3 tools/get_godot.py --check      only report what is present
    python3 tools/get_godot.py --where      print the binary path and exit

Godot is optional. Without it GDScript is emitted and reported as
unverified rather than counted as passing, and every other check still
runs -- see EXECUTABLE in engine/ir.py.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import platform
import sys
import urllib.request
import zipfile
from pathlib import Path

VERSION = "4.7.2-stable"
BASE = f"https://github.com/godotengine/godot/releases/download/{VERSION}"

# SHA-512, taken from the release's own SHA512-SUMS.txt and pinned here.
# A hash that has not been checked against the release is worse than
# no hash, because it looks like verification. Only macOS is pinned
# here -- it is the one that was downloaded and hashed. The others
# name their file and carry None, and the installer REFUSES rather
# than fetching something it cannot verify. ATLAS_GODOT still points
# at an existing install on any platform, which is the escape hatch.
BUILDS = {
    "macos": ("Godot_v4.7.2-stable_macos.universal.zip",
              "38aa16e5bba2083941fc5b3e54be0089bd4cc35e32415f5b9fd9a8a6a7b98182"
              "55d44532ea8ef94b5aef56c4b407c2d634fa4f657e4ebe681ebbf59b7bac69ca"),
    "linux": ("Godot_v4.7.2-stable_linux.x86_64.zip", None),
    "windows": ("Godot_v4.7.2-stable_win64.exe.zip", None),
}

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "vendor" / f"godot-{VERSION}"


def plat():
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    return s


def binary_path():
    """where engine/ir.py will look, in order"""
    cands = [
        os.environ.get("ATLAS_GODOT", ""),
        str(DEST / "Godot.app" / "Contents" / "MacOS" / "Godot"),
        "/Applications/Godot.app/Contents/MacOS/Godot",
        os.path.expanduser(
            "~/Downloads/godot-4.7.2/Godot.app/Contents/MacOS/Godot"),
    ]
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def sha512(path, chunk=1 << 20):
    h = hashlib.sha512()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def fetch(verbose=True):
    p = plat()
    if p not in BUILDS:
        print(f"no pinned build for {p!r}. Install Godot {VERSION} yourself "
              f"and set ATLAS_GODOT to the binary.")
        return None
    name, want = BUILDS[p]
    if want is None:
        print(f"{p!r} names its build ({name}) but its SHA-512 has not "
              f"been checked against the release, and downloading "
              f"something unverifiable is worse than not downloading "
              f"it. Install Godot {VERSION} yourself and set "
              f"ATLAS_GODOT, or pin the hash in BUILDS.")
        return None
    DEST.mkdir(parents=True, exist_ok=True)
    zpath = DEST / name

    if not zpath.exists():
        url = f"{BASE}/{name}"
        if verbose:
            print(f"downloading {name} ...")
        urllib.request.urlretrieve(url, zpath)

    got = sha512(zpath)
    if got != want:
        # An EXACT filename match matters: "mono_macos.universal.zip" contains
        # "macos.universal.zip" as a substring, and matching loosely against
        # the sums file once compared a good download to the mono build's
        # hash and reported MISMATCH.
        zpath.unlink()
        print(f"CHECKSUM MISMATCH -- deleted the download.\n"
              f"  expected {want[:32]}...\n  got      {got[:32]}...")
        return None
    if verbose:
        print(f"sha512 verified: {got[:32]}...")

    with zipfile.ZipFile(zpath) as z:
        z.extractall(DEST)
    b = binary_path()
    if b:
        os.chmod(b, 0o755)
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--where", action="store_true")
    a = ap.parse_args()

    have = binary_path()
    if a.where:
        print(have or "")
        return 0 if have else 1
    if a.check:
        print(f"godot {VERSION}: {have or 'not found'}")
        if have:
            os.system(f'"{have}" --headless --version')
        else:
            print("  run: python3 tools/get_godot.py")
        return 0

    if have:
        print(f"already present: {have}")
        return 0
    b = fetch()
    if not b:
        return 1
    print(f"installed: {b}")
    os.system(f'"{b}" --headless --version')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
