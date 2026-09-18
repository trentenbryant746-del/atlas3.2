"""Write the generated blocks into README.md, between markers.

A published number typed by hand is on this repository's record as
a failure: "26 of 28" sat in the README while the code said 21. So
the numbers in the README are not typed. They live between markers
and this tool replaces what is between them.

    python3 -m tools.readme            check only, reports drift
    python3 -m tools.readme --write    rewrite the blocks
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

BLOCKS = {}


def _register(name, fn):
    BLOCKS[name] = fn


def _scale():
    from eval.scale import block
    return block()


_register("SCALE", _scale)


def _span(text, name):
    open_, close = f"<!-- {name} -->", f"<!-- /{name} -->"
    i, j = text.find(open_), text.find(close)
    return (i, j, open_, close) if i >= 0 and j > i else (None,) * 4


def apply(write=False):
    text = README.read_text()
    out, drifted, missing = text, [], []
    for name, fn in BLOCKS.items():
        want = fn().strip()
        i, j, open_, close = _span(out, name)
        if i is None:
            missing.append(name)
            continue
        have = out[i + len(open_):j].strip()
        if have != want:
            drifted.append(name)
        out = out[:i] + open_ + "\n\n" + want + "\n\n" + out[j:]
    if write and out != text:
        README.write_text(out)
    return drifted, missing, out != text


if __name__ == "__main__":
    w = "--write" in sys.argv
    drifted, missing, changed = apply(write=w)
    if missing:
        print(f"  markers not found: {missing}")
    if drifted:
        print(f"  {'rewrote' if w else 'DRIFTED'}: {drifted}")
    if not drifted and not missing:
        print("  README matches the rules")
    sys.exit(1 if (drifted and not w) or missing else 0)
