"""
One IR, several backends, and the backends check each other.

Generating GDScript directly -- as belt-atlas did -- ties the output to one
engine and leaves the check at whatever that engine's parser will say. An
intermediate representation fixes both:

    picks -> IR -> {python, ruby, gdscript, ...}

and it buys a check nothing single-target can have. Two backends are two
INDEPENDENT IMPLEMENTATIONS of the same specification. Compile the IR to
both, run both, and require byte-identical traces. A codegen bug that
survives one backend's syntax has to survive the other's semantics too, and
they were written separately.

    python  executes here  -> trace A
    ruby    executes here  -> trace B        A == B or the IR is rejected
    gdscript emitted       -> parse-shaped only; Godot is not installed, so
                              it is NOT verified by execution and is labelled
                              as such rather than counted as passing.

PROVENANCE TOKENS. Every IR node carries an id, and every emitted line
carries it in a comment. So any line of generated code in any language maps
back to the IR node, the pick, and the English phrase that caused it. That
is the index: token -> rule -> intent, readable in both directions.
"""
from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field


@dataclass
class Node:
    op: str
    args: tuple
    nid: str = ""
    origin: str = ""          # the English phrase or pick that caused it

    def __post_init__(self):
        if not self.nid:
            seed = f"{self.op}|{self.args}|{self.origin}"
            self.nid = "a" + hashlib.sha256(seed.encode()).hexdigest()[:8]


def N(op, *args, origin=""):
    return Node(op, args, origin=origin)


# ---------------------------------------------------------------- backends
class Backend:
    name = "?"
    comment = "#"

    def line(self, txt, node, depth=0):
        pad = self.indent * depth
        return f"{pad}{txt}  {self.comment} atlas:{node.nid}"

    def emit(self, prog):
        out = list(self.prelude())
        for n in prog:
            out += self.node(n, 0)
        out += self.postlude()
        return "\n".join(out) + "\n"


class Python(Backend):
    name, comment, indent = "python", "#", "    "

    def prelude(self):
        return ["TRACE = []"]

    def postlude(self):
        return ["print('<<T>>' + '|'.join(str(t) for t in TRACE) + '<<E>>')"]

    def node(self, n, d):
        a = n.args
        if n.op == "let":
            return [self.line(f"{a[0]} = {a[1]}", n, d)]
        if n.op == "loop":
            body = []
            for k in a[1]:
                body += self.node(k, d + 1)
            return [self.line(f"for _i in range({a[0]}):", n, d)] + body
        if n.op == "add":
            return [self.line(f"{a[0]} = ({a[0]} + {a[1]}) % {a[2]}", n, d)]
        if n.op == "when":
            body = []
            for k in a[2]:
                body += self.node(k, d + 1)
            return [self.line(f"if {a[0]} {a[1]}:", n, d)] + body
        if n.op == "emit":
            return [self.line(f"TRACE.append({a[0]})", n, d)]
        raise ValueError(n.op)


class Ruby(Backend):
    name, comment, indent = "ruby", "#", "  "

    def prelude(self):
        return ["TRACE = []"]

    def postlude(self):
        return ["puts '<<T>>' + TRACE.map(&:to_s).join('|') + '<<E>>'"]

    def node(self, n, d):
        a = n.args
        pad = self.indent * d
        if n.op == "let":
            return [self.line(f"{a[0]} = {a[1]}", n, d)]
        if n.op == "loop":
            body = []
            for k in a[1]:
                body += self.node(k, d + 1)
            return [self.line(f"{a[0]}.times do |_i|", n, d)] + body + [pad + "end"]
        if n.op == "add":
            return [self.line(f"{a[0]} = ({a[0]} + {a[1]}) % {a[2]}", n, d)]
        if n.op == "when":
            body = []
            for k in a[2]:
                body += self.node(k, d + 1)
            return [self.line(f"if {a[0]} {a[1]}", n, d)] + body + [pad + "end"]
        if n.op == "emit":
            return [self.line(f"TRACE.push({a[0]})", n, d)]
        raise ValueError(n.op)


class GDScript(Backend):
    name, comment, indent = "gdscript", "#", "\t"

    # extends SceneTree, not Node: Godot runs a SceneTree script directly
    # with `--headless --script f.gd`, so no project scaffold is needed and
    # the backend becomes EXECUTABLE rather than merely emitted.
    def prelude(self):
        return ["extends SceneTree", "", "var TRACE := []", "",
                "func _initialize() -> void:"]

    def postlude(self):
        return ["\tprint(\"<<T>>\" + \"|\".join(TRACE) + \"<<E>>\")", "\tquit()"]

    def node(self, n, d):
        a = n.args
        d += 1                       # everything sits inside _ready()
        if n.op == "let":
            return [self.line(f"var {a[0]} := {a[1]}", n, d)]
        if n.op == "loop":
            body = []
            for k in a[1]:
                body += self.node(k, d)
            return [self.line(f"for _i in range({a[0]}):", n, d)] + body
        if n.op == "add":
            return [self.line(f"{a[0]} = ({a[0]} + {a[1]}) % {a[2]}", n, d)]
        if n.op == "when":
            body = []
            for k in a[2]:
                body += self.node(k, d)
            return [self.line(f"if {a[0]} {a[1]}:", n, d)] + body
        if n.op == "emit":
            return [self.line(f"TRACE.append(str({a[0]}))", n, d)]
        raise ValueError(n.op)


BACKENDS = {b.name: b() for b in (Python, Ruby, GDScript)}
import shutil as _shutil

_GODOT = None
_CANDIDATES = [
    os.environ.get("ATLAS_GODOT", ""),
    _shutil.which("godot") or "",
    "/Applications/Godot.app/Contents/MacOS/Godot",
    os.path.expanduser("~/Downloads/godot-4.7.2/Godot.app/Contents/MacOS/Godot"),
]
for _c in _CANDIDATES:
    if _c and os.path.exists(_c):
        _GODOT = _c
        break

# gdscript joins the executable set only when Godot is actually present.
# Claiming a backend is verified when its runtime is absent is the kind of
# thing this whole repo exists to not do.
EXECUTABLE = ("python", "ruby") + (("gdscript",) if _GODOT else ())


def index(prog):
    """token -> (op, args, the English that caused it). Both directions."""
    out = {}

    def walk(ns):
        for n in ns:
            out[n.nid] = {"op": n.op, "args": n.args, "origin": n.origin}
            for a in n.args:
                if isinstance(a, (list, tuple)) and a and isinstance(a[0], Node):
                    walk(a)
    walk(prog)
    return out


# ------------------------------------------------- cross-backend checking
import subprocess
import tempfile
import os

EXT = {"python": ".py", "ruby": ".rb", "gdscript": ".gd"}
RUN = {"python": ["python3"], "ruby": ["ruby"]}
if _GODOT:
    RUN["gdscript"] = [_GODOT, "--headless", "--script"]


def run_backend(name, src, timeout=20):
    if name not in RUN:
        return None, f"{name} has no runtime on this machine"
    
    with tempfile.NamedTemporaryFile("w", suffix=EXT[name], delete=False) as f:
        f.write(src)
        path = f.name
    try:
        p = subprocess.run(RUN[name] + [path], capture_output=True,
                           text=True, timeout=timeout)
        if p.returncode != 0:
            return None, (p.stderr or "").strip().splitlines()[-1:][0] if p.stderr else "nonzero exit"
        # A runtime prints what it likes -- Godot emits its version banner
        # before anything the program says. Delimiting the trace means the
        # comparison cannot be fooled by a runtime's own chatter.
        m = re.search(r'<<T>>(.*?)<<E>>', p.stdout, re.S)
        if not m:
            return None, "no delimited trace in output"
        return m.group(1).strip(), ""
    except subprocess.TimeoutExpired:
        return None, "timed out"
    finally:
        os.unlink(path)


def cross_verify(prog):
    """Compile to every backend; the EXECUTABLE ones must agree exactly.

    This is the check a single-target generator cannot have. python and ruby
    were written separately, so a codegen bug has to survive one backend's
    syntax AND the other's semantics to go unnoticed.
    """
    srcs = {n: b.emit(prog) for n, b in BACKENDS.items()}
    traces, notes = {}, []
    for n in EXECUTABLE:
        out, err = run_backend(n, srcs[n])
        if out is None:
            notes.append((n, False, f"did not run: {err}"))
        else:
            traces[n] = out
            notes.append((n, True, f"trace {out[:34]}{'...' if len(out)>34 else ''}"))
    agree = len(set(traces.values())) == 1 and len(traces) == len(EXECUTABLE)
    notes.append(("backends agree", agree,
                  "" if agree else f"{ {k: v[:24] for k, v in traces.items()} }"))
    for n in BACKENDS:
        if n not in EXECUTABLE:
            notes.append((n, None, "emitted but NOT executed -- no runtime here"))
    return agree, srcs, traces, notes
