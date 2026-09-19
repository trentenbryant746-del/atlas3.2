"""Render a thing from the ledger, under the light of that world.

Everything in the frame is a number from somewhere else:

  the sky        engine/scene.sky_rgb, Rayleigh on a 5772 K Sun
  the sunlight   engine/scene.sun_rgb, what did NOT scatter out
  the brightness engine/scene.solar_constant, L / 4 pi d^2
  the shadow     h / tan(elevation)
  the object     engine/drawing.py's published envelope

The one thing chosen is that the envelope is drawn as a BOX.
The extents are real and already in the encyclopedia; a box is
the simplest solid with those extents, and engine/scene.py has
an inverted check that fails if anything claims more shape than
that.

    python3 -m tools.render        -> paper/scene.jpg
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "scene.jpg"

W, H = 640, 400
VIEW_M = 5.0                 # metres across the frame
HORIZON = 0.58               # fraction of height


def render(elevation_deg=22.0, quality=80):
    from engine.scene import (sky_rgb, sun_rgb, lit_fraction,
                              shadow_length, solar_constant)
    from engine.world import run, drawing_table, their_entry, spec
    from engine.artifact import KNOWN_AS

    w = run(14000.0)
    pick = max((a for a in w.artifacts() if len(a) == 4),
               key=lambda c: drawing_table(c)["envelope m"][0])
    d = drawing_table(pick)
    lo, hi = d["envelope m"]
    side = lo                       # the largest single part
    height = lo

    sky = sky_rgb(elevation_deg)
    sun = sun_rgb(elevation_deg)
    cosl = lit_fraction(elevation_deg)
    shadow = shadow_length(height, elevation_deg)
    ambient = 0.15

    ppm = W / VIEW_M
    ground_y = int(H * HORIZON)
    bx0 = int(W * 0.34)
    bw = max(4, int(side * ppm))
    bh = max(4, int(height * ppm))
    bx1 = bx0 + bw
    by0 = ground_y - bh

    px = [0] * (W * H * 3)

    def put(x, y, rgb):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            for k in range(3):
                px[i + k] = max(0, min(255, int(rgb[k] * 255)))

    for y in range(H):
        for x in range(W):
            if y < ground_y:
                t = y / max(ground_y, 1)
                put(x, y, tuple(c * (0.55 + 0.45 * t) for c in sky))
            else:
                lit = tuple(sun[k] * cosl * 0.25 + sky[k] * ambient
                            for k in range(3))
                put(x, y, lit)

    sh_px = int(shadow * ppm)
    for x in range(bx0, min(W, bx1 + sh_px)):
        depth = (x - bx1) / max(sh_px, 1)
        if x < bx1 or depth <= 1.0:
            for y in range(ground_y, min(H, ground_y + max(2, bh // 6))):
                put(x, y, tuple(sky[k] * ambient for k in range(3)))

    for y in range(by0, ground_y):
        for x in range(bx0, bx1):
            face = sun if x < bx0 + bw * 0.62 else None
            if face:
                put(x, y, tuple(sun[k] * cosl * 0.85 + sky[k] * ambient
                                for k in range(3)))
            else:
                put(x, y, tuple(sky[k] * ambient * 1.4 for k in range(3)))
    for x in range(bx0, bx1):
        put(x, by0, tuple(min(1.0, sun[k] * 0.95) for k in range(3)))

    from tools.jpeg import encode_colour
    data = encode_colour(px, W, H, quality)
    name = KNOWN_AS.get(pick) or their_entry(
        pick, (spec(pick, w)["first built"] or (0, 0))[1], w)
    return data, {
        "thing": name,
        "parts": sorted(pick),
        "envelope m": (lo, hi),
        "elevation deg": elevation_deg,
        "shadow m": shadow,
        "sky rgb": tuple(round(v, 2) for v in sky),
        "sun rgb": tuple(round(v, 2) for v in sun),
        "W per m2": solar_constant() * cosl,
    }


if __name__ == "__main__":
    data, info = render()
    OUT.write_bytes(data)
    for k, v in info.items():
        print(f"  {k:<16}{v}")
    print(f"\n  {OUT.relative_to(ROOT)}  {W}x{H}, {len(data):,} bytes"
          f"  ({W*H*3/len(data):.1f}x)")
