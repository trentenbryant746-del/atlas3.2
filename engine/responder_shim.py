"""belt-atlas's fact table, loaded without importing its CLI."""
from pathlib import Path

import os

# bundled copy; ATLAS_NET points elsewhere if you have the original tree.
NET = Path(os.environ.get(
    "ATLAS_NET",
    str(Path(__file__).resolve().parent.parent / "data" / "external"
        / "belt-atlas-net.tsv")))


def facts():
    out = []
    if not NET.exists():
        return out
    for line in NET.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        p = line.split("\t")
        if len(p) >= 3:
            out.append((p[0].strip(), p[1].strip(), p[2].strip()))
    return out
