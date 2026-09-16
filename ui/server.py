"""
atlas2 UI: a prompt box, and the Godot generation made visible.

    python3 ui/server.py          then open http://localhost:8765

Two panes. Ask anything on the left and the answer comes back with its
KIND (derived / asserted / derivation), the CHECK that was applied, and the
full English account where there is one. On the right, an induced compound
is rendered as the atom tree Godot draws, with the scene round-trip run
live -- Godot loads the generated .tscn headlessly and the recovered
structure must match.

No dependencies. Standard library only.
"""
from __future__ import annotations

import json
import sys
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "engine"))

PAGE = (Path(__file__).parent / "index.html")


def ask_english(q):
    from engine.english import answer
    r = answer(q)
    return {"ok": bool(r.get("ok", True)),
            "kind": r.get("kind", "-"), "check": r.get("check", "-"),
            "call": r.get("call"), "answer": str(r.get("answer", "")),
            "english": r.get("english", "")}


def ask_cascade(q):
    import atlas
    a = atlas.ask(q)
    return {"verdict": a.verdict, "value": str(a.value) if a.value is not None else "",
            "mechanism": a.mechanism or "-", "check": a.check or "-",
            "provenance": a.provenance or "", "trace": a.trace}


def compound(seed_examples=None):
    """induce a compound and lay it out as the atom tree Godot renders"""
    from fractions import Fraction as F
    from engine.induce2 import synthesize_mim
    from engine.visualize import layout, scene
    ex = [([100, 27, -9, 96], F(-1239)), ([3, 4, 5, 6], F(29)),
          ([10, 2, 7, 1], F(83)), ([-5, 8, 3, 2], F(7)),
          ([1, 1, 1, 1], F(1)), ([6, 0, 2, 5], F(7))]
    d, _ = synthesize_mim(ex, max_size=9)
    nodes = layout(d)
    return {"expr": str(d), "nodes": nodes, "tscn": scene(nodes)}


def godot_roundtrip():
    from fractions import Fraction as F
    from engine.induce2 import synthesize_mim
    from engine.visualize import render_and_verify
    ex = [([100, 27, -9, 96], F(-1239)), ([3, 4, 5, 6], F(29)),
          ([10, 2, 7, 1], F(83)), ([-5, 8, 3, 2], F(7)),
          ([1, 1, 1, 1], F(1)), ([6, 0, 2, 5], F(7))]
    d, _ = synthesize_mim(ex, max_size=9)
    ok, detail, _tscn = render_and_verify(d)
    return {"ok": ok, "detail": detail}


def backends():
    from engine.ir import EXECUTABLE, _GODOT, cross_verify, N
    prog = [N("let", "x", 0), N("loop", 12, [N("add", "x", 3, 7), N("emit", "x")])]
    agree, srcs, traces, notes = cross_verify(prog)
    return {"executable": list(EXECUTABLE), "godot": _GODOT or "",
            "agree": agree, "traces": traces,
            "sources": {k: v for k, v in srcs.items()}}


ROUTES = {"/api/ask": ask_english, "/api/cascade": ask_cascade}
NOARG = {"/api/compound": compound, "/api/godot": godot_roundtrip,
         "/api/backends": backends}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        try:
            if u.path in ("/", "/index.html"):
                return self._send(200, PAGE.read_bytes(), "text/html")
            if u.path in NOARG:
                return self._send(200, json.dumps(NOARG[u.path]()))
            if u.path in ROUTES:
                q = parse_qs(u.query).get("q", [""])[0]
                if not q:
                    return self._send(400, json.dumps({"error": "no q"}))
                return self._send(200, json.dumps(ROUTES[u.path](q)))
            self._send(404, json.dumps({"error": "no route"}))
        except Exception as e:
            self._send(500, json.dumps({"error": f"{type(e).__name__}: {e}",
                                        "trace": traceback.format_exc()[-800:]}))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"atlas2 UI on http://localhost:{port}")
    HTTPServer(("127.0.0.1", port), H).serve_forever()
