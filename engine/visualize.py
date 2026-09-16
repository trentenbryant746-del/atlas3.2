"""
Render an induced program as a Godot scene -- and read it back.

Atlas's own vocabulary maps onto the IR directly:

    particles / leaves   operands and constants
    atoms                ADD, MUL, NEG, INV
    compounds            expression trees built from atoms
    routes               the ordered edges of a compound

So a compound IS a graph, and a graph is the one thing a game engine is
unambiguously good at drawing. Every visual node is named with its
provenance token, so a shape on screen, a line of Python, a line of Ruby and
a line of GDScript all carry the same id.

THE VISUAL IS CHECKED LIKE EVERY OTHER REPRESENTATION. A picture that cannot
be read back is a picture, not a representation. Godot loads the generated
scene headlessly, walks the node tree, prints what it finds, and the
recovered structure must equal the expression that produced it. If it does
not round-trip, the scene is rejected -- the same rule belt-atlas's
compress.py applied to code.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ATOM_COLOUR = {"add": "0.28,0.62,0.95,1", "mul": "0.95,0.62,0.22,1",
               "neg": "0.85,0.32,0.42,1", "inv": "0.55,0.42,0.86,1",
               "leaf": "0.45,0.78,0.52,1"}


def layout(e, depth=0, x=0.0, out=None, parent=None, seq=None):
    """assign each atom a position and a stable id; returns flat node list"""
    if out is None:
        out, seq = [], [0]
    nid = f"n{seq[0]}"
    seq[0] += 1
    kids = [k for k in (e.kids if e.op != "leaf" else ()) if hasattr(k, "op")]
    me = {"id": nid, "op": e.op, "label": _label(e), "depth": depth,
          "parent": parent, "token": e.nid if hasattr(e, "nid") else nid}
    out.append(me)
    span = max(1, len(kids))
    for i, k in enumerate(kids):
        layout(k, depth + 1, x + (i - (span - 1) / 2) * (260 / (depth + 1)),
               out, nid, seq)
    me["x"] = x
    return out


def _label(e):
    if e.op == "leaf":
        i, c = e.kids
        return f"x{i}" if c is None else str(c)
    return {"add": "+", "mul": "x", "neg": "-", "inv": "1/"}[e.op]


def scene(nodes, title="compound"):
    """a .tscn whose node NAMES are the provenance tokens"""
    L = [f'[gd_scene load_steps=1 format=3]', '',
         f'[node name="{title}" type="Node2D"]', '']
    for n in nodes:
        parent = "." if n["parent"] is None else _path(nodes, n["parent"])
        L.append(f'[node name="{n["id"]}_{n["op"]}" type="Node2D" parent="{parent}"]')
        L.append(f'position = Vector2({n["x"]:.1f}, {n["depth"] * 120})')
        L.append(f'metadata/token = "{n["token"]}"')
        L.append(f'metadata/label = "{n["label"]}"')
        L.append('')
    return "\n".join(L)


def _path(nodes, pid):
    chain = []
    cur = pid
    by = {n["id"]: n for n in nodes}
    while cur is not None:
        n = by[cur]
        chain.append(f'{n["id"]}_{n["op"]}')
        cur = n["parent"]
    return "/".join(reversed(chain))


READBACK = '''extends SceneTree

func walk(n: Node, depth: int, acc: Array) -> void:
\tfor c in n.get_children():
\t\tvar tok := ""
\t\tvar lab := ""
\t\tif c.has_meta("token"):
\t\t\ttok = str(c.get_meta("token"))
\t\tif c.has_meta("label"):
\t\t\tlab = str(c.get_meta("label"))
\t\tacc.append("%d:%s:%s" % [depth, lab, tok])
\t\twalk(c, depth + 1, acc)

func _initialize() -> void:
\t# load() returns Variant, so := cannot infer it. Godot's parser
\t# rejects the inferred form outright -- it caught this, not me.
\tvar packed: PackedScene = load("res://compound.tscn")
\tif packed == null:
\t\tprint("<<T>>LOAD_FAILED<<E>>")
\t\tquit()
\t\treturn
\tvar root: Node = packed.instantiate()
\tvar acc: Array = []
\twalk(root, 0, acc)
\tprint("<<T>>" + "|".join(acc) + "<<E>>")
\tquit()
'''


def expected(nodes):
    return "|".join(f'{n["depth"]}:{n["label"]}:{n["token"]}' for n in nodes)


def render_and_verify(expr, godot=None):
    """-> (ok, detail, tscn). Godot must read the scene back unchanged."""
    from engine.ir import _GODOT
    godot = godot or _GODOT
    nodes = layout(expr)
    tscn = scene(nodes)
    if not godot:
        return None, "Godot not present; scene emitted but NOT read back", tscn

    with tempfile.TemporaryDirectory() as d:
        Path(d, "project.godot").write_text(
            'config_version=5\n\n[application]\nconfig/name="atlasviz"\n')
        Path(d, "compound.tscn").write_text(tscn)
        Path(d, "readback.gd").write_text(READBACK)
        p = subprocess.run([godot, "--headless", "--path", d,
                            "--script", "readback.gd"],
                           capture_output=True, text=True, timeout=90)
        m = re.search(r'<<T>>(.*?)<<E>>', p.stdout, re.S)
        if not m:
            err = (p.stderr or p.stdout or "").strip().splitlines()[-1:]
            return False, f"no readback: {err}", tscn
        got = m.group(1).strip()
        want = expected(nodes)
        if got != want:
            return False, f"round-trip differs\n  want {want[:70]}\n  got  {got[:70]}", tscn
        return True, f"{len(nodes)} atoms round-tripped through Godot", tscn
