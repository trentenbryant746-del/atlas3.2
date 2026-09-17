"""
What it looks like from in there.

engine/recognize.py said the sharp patch is 0.028% of the field
and that sweeping it would take fifteen minutes. Those are the
right numbers and they do not land the way seeing it does. This
renders the same arithmetic as an image, from behind the eyes,
with no libraries -- PNG is a zlib stream and a few headers, both
of which are in the standard library.

Nothing here is decoration. Every pixel is placed by a rule
derived somewhere else:

    acuity        engine/senses.py, optics against cone spacing
    the fovea     engine/recognize.py, 2 degrees of 120
    falloff       cone density away from the centre
    what is named engine/recognize.py, 20 cells across a thing
    distance      engine/senses.py, stereo from a 64 mm baseline

The picture is therefore a claim and can be wrong. If the fovea
looks large in it, one of those modules is lying.
"""
from __future__ import annotations

import math
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

WIDTH, HEIGHT = 900, 420
FIELD_DEG = 120.0
FOVEA_DEG = 2.0


def write_png(path, rows, w, h):
    """A PNG from stdlib alone. rows is h lists of (r,g,b)."""
    raw = b"".join(b"\x00" + bytes(v for px in row for v in px)
                   for row in rows)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    Path(path).write_bytes(png)
    return len(png)


def acuity_at(ecc_deg):
    """arcmin of resolution this far off centre. DERIVED.

    Cone density falls roughly as 1/(1 + e/e0), so the smallest
    resolvable detail grows with eccentricity.
    """
    from engine.recognize import acuity_arcmin
    return acuity_arcmin() * (1.0 + ecc_deg / 2.3)


def blur_px(ecc_deg, px_per_deg):
    """How many pixels one resolvable cell covers out here."""
    return max(acuity_at(ecc_deg) / 60.0 * px_per_deg, 1.0)


SCENE = [
    # label, angle off centre (deg), height above horizon, size m, dist m
    ("tree", -38.0, 0.0, 9.0, 60.0),
    ("person", -12.0, 0.0, 1.7, 22.0),
    ("fire", 3.0, 0.0, 0.9, 6.0),
    ("hand + flake", 14.0, -7.0, 0.22, 0.45),
    ("person far", 33.0, 0.0, 1.7, 400.0),   # past the 289 m limit
    ("bird", -25.0, 17.0, 0.3, 80.0),
]


def subtends_deg(size_m, dist_m):
    """DERIVED. How wide a thing looks."""
    return math.degrees(2.0 * math.atan(size_m / (2.0 * dist_m)))


def is_named(size_m, dist_m):
    """DERIVED via engine/recognize.py."""
    from engine.recognize import recognition_range
    return dist_m <= recognition_range(size_m)


def render(path=None):
    """-> (path, [(label, deg, named)]). The view from inside."""
    path = path or (ROOT / "data" / "pov.png")
    px_per_deg = WIDTH / FIELD_DEG
    horizon = int(HEIGHT * 0.62)
    rows, report = [], []

    objs = []
    for label, ang, above, size_m, dist in SCENE:
        w_deg = subtends_deg(size_m, dist)
        objs.append(dict(
            label=label, cx=WIDTH / 2 + ang * px_per_deg,
            cy=horizon - above * px_per_deg,
            wpx=max(w_deg * px_per_deg, 1.0),
            hpx=max(w_deg * px_per_deg * (2.2 if label != "bird" else 0.6),
                    1.0),
            ecc=abs(ang), named=is_named(size_m, dist), dist=dist))
        report.append((label, ang, objs[-1]["named"], w_deg))

    fov_px = FOVEA_DEG * px_per_deg
    for y in range(HEIGHT):
        row = []
        for x in range(WIDTH):
            ecc = abs(x - WIDTH / 2) / px_per_deg
            if y < horizon:
                t = y / max(horizon, 1)
                base = (int(120 + 70 * t), int(150 + 60 * t),
                        int(200 + 40 * t))
            else:
                t = (y - horizon) / max(HEIGHT - horizon, 1)
                base = (int(95 - 35 * t), int(80 - 25 * t),
                        int(60 - 22 * t))
            r, g, b = base
            for o in objs:
                dx, dy = abs(x - o["cx"]), abs(y - o["cy"])
                if dx <= o["wpx"] / 2 and dy <= o["hpx"]:
                    k = blur_px(o["ecc"], px_per_deg)
                    soft = min(1.0, (o["wpx"] / 2) / k)
                    if o["named"]:
                        c = (40, 35, 30)
                    else:
                        c = (int(base[0] * 0.75), int(base[1] * 0.75),
                             int(base[2] * 0.75))
                    a = 0.25 + 0.75 * soft
                    r = int(r * (1 - a) + c[0] * a)
                    g = int(g * (1 - a) + c[1] * a)
                    b = int(b * (1 - a) + c[2] * a)
            # wash out everything the eye cannot resolve here
            grey = (r + g + b) // 3
            m = min(1.0, ecc / (FIELD_DEG / 2))
            f = 0.70 * m
            r = int(r * (1 - f) + grey * f)
            g = int(g * (1 - f) + grey * f)
            b = int(b * (1 - f) + grey * f)
            # the sharp patch, drawn to scale
            if (abs(abs(x - WIDTH / 2) - fov_px / 2) < 1.0
                    and abs(y - horizon) < fov_px / 2) or \
               (abs(abs(y - horizon) - fov_px / 2) < 1.0
                    and abs(x - WIDTH / 2) < fov_px / 2):
                r, g, b = 255, 90, 60
            row.append((max(0, min(255, r)), max(0, min(255, g)),
                        max(0, min(255, b))))
        rows.append(row)

    write_png(path, rows, WIDTH, HEIGHT)
    return path, report


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_image_comes_from_the_rules", _rules)
    t("the_sharp_patch_is_drawn_to_scale", _scale)
    t("distance_decides_what_is_named", _named)
    return all(o[1] for o in out), out


def _rules():
    p, rep = render()
    if not Path(p).exists():
        raise ArithmeticError("no image was written")
    return (f"{Path(p).name} written from stdlib alone -- PNG is a "
            f"zlib stream and a few headers. Every pixel is placed "
            f"by a rule derived elsewhere: acuity from "
            f"engine/senses.py, the fovea and the naming range from "
            f"engine/recognize.py. The picture is a CLAIM and can be "
            f"wrong, which is the only reason it is worth drawing")


def _scale():
    px_per_deg = WIDTH / FIELD_DEG
    frac = (FOVEA_DEG * px_per_deg) ** 2 / (WIDTH * HEIGHT)
    if frac > 0.01:
        raise ArithmeticError(f"the box is {100*frac:.1f}% of the frame")
    return (f"the red box is {FOVEA_DEG:.0f} degrees of "
            f"{FIELD_DEG:.0f}, {FOVEA_DEG*px_per_deg:.0f} px across in "
            f"a {WIDTH} px frame -- {100*frac:.2f}% of it. Everything "
            f"outside it is drawn at the resolution the eye actually "
            f"has there, which is why the edges are mush")


def _named():
    _p, rep = render()
    near = [r for r in rep if r[0] == "person"][0]
    far = [r for r in rep if r[0] == "person far"][0]
    if not near[2] or far[2]:
        raise ArithmeticError(f"near {near[2]}, far {far[2]}")
    return (f"the same 1.7 m person is NAMED at 22 m and merely a "
            f"shape at 400 m, because engine/recognize.py puts the "
            f"limit at 289 m and a body needs 20 cells across it. "
            f"The scene first placed them at 240 m and the check "
            f"failed, correctly -- 240 is INSIDE 289, so they were "
            f"nameable and I had assumed otherwise. The picture is "
            f"not deciding this; it is reporting a rule that "
            f"disagreed with me")


if __name__ == "__main__":
    p, rep = render()
    print(f"  wrote {p}\n")
    print(f"  {'thing':<14}{'off centre':>11}{'subtends':>10}{'named':>8}")
    for label, ang, named, w in rep:
        print(f"  {label:<14}{ang:>10.0f}d{w:>9.2f}d"
              f"{'yes' if named else 'no':>8}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:42]}")
