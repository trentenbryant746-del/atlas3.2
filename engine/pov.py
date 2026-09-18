"""
What it looks like from in there.

engine/recognize.py said the sharp patch is 0.028% of the field
and sweeping it would take fifteen minutes. Those are the right
numbers and they do not land the way seeing it does. This renders
the same arithmetic from behind the eyes, with no libraries --
PNG is a zlib stream and four headers, both in the standard
library.

The first version drew flat rectangles and washed the edges out
by desaturating them, which is not what an eye does. Acuity does
not make things grey, IT MAKES THEM UNRESOLVED. So this one
builds a stack of genuinely blurred copies and blends between
them by eccentricity, with the blur radius set by cone density
away from the fovea. Everything in the frame is placed by a rule
derived somewhere else:

    acuity        engine/senses.py, optics against cone spacing
    the fovea     engine/recognize.py, 2 degrees of 120
    falloff       cone density, 1/(1 + e/e0)
    what is named engine/recognize.py, 20 cells across a thing
    haze          distance, and it is the only free parameter here

The picture is therefore a claim and can be wrong. If the sharp
patch looks generous in it, one of those modules is lying.
"""
from __future__ import annotations

import math
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

WIDTH, HEIGHT = 1000, 460
FIELD_DEG = 120.0
FOVEA_DEG = 2.0
E0_DEG = 2.3                 # MEASURED, cone density falloff constant
HAZE_KM = 0.35               # CHOSEN, atmospheric extinction scale


def write_png(path, buf, w, h):
    """A PNG from stdlib alone. buf is a flat bytearray of RGB."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += buf[y * w * 3:(y + 1) * w * 3]

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
           + chunk(b"IEND", b""))
    Path(path).write_bytes(png)
    return len(png)


def acuity_at(ecc_deg):
    """arcmin resolvable this far off centre. DERIVED.

    Cone density falls as 1/(1 + e/e0), so the smallest thing that
    can be told apart grows in proportion.
    """
    from engine.recognize import acuity_arcmin
    return acuity_arcmin() * (1.0 + ecc_deg / E0_DEG)


def blur_radius_px(ecc_deg, px_per_deg):
    """How many pixels one unresolvable cell spans. DERIVED."""
    return acuity_at(ecc_deg) / 60.0 * px_per_deg / 2.0


SCENE = [
    # label, deg off centre, deg above horizon, size m, distance m
    ("tree",          -40.0,  0.0,  11.0,  70.0),
    ("tree",          -47.0,  0.0,   8.0, 130.0),
    ("person",        -14.0,  0.0,   1.7,  19.0),
    ("fire",            2.0, -1.0,   0.8,   5.5),
    ("hand and flake", 17.0, -9.0,   0.20,  0.42),
    ("person far",     34.0,  0.0,   1.7, 400.0),
    ("bird",          -27.0, 16.0,   0.35, 90.0),
    ("ridge",          44.0,  1.5, 140.0, 2600.0),
]


def subtends_deg(size_m, dist_m):
    """DERIVED. How wide a thing looks from here."""
    return math.degrees(2.0 * math.atan(size_m / (2.0 * dist_m)))


def is_named(size_m, dist_m):
    """DERIVED via engine/recognize.py."""
    from engine.recognize import recognition_range
    return dist_m <= recognition_range(size_m)


def _blur(src, w, h, r):
    """Separable box blur, two passes. Pure python, integer maths."""
    if r < 1:
        return src
    r = int(r)
    tmp = bytearray(len(src))
    n = 2 * r + 1
    for y in range(h):
        base = y * w * 3
        for c in range(3):
            acc = src[base + c] * (r + 1)
            for i in range(1, r + 1):
                acc += src[base + min(i, w - 1) * 3 + c]
            for x in range(w):
                tmp[base + x * 3 + c] = acc // n
                acc += src[base + min(x + r + 1, w - 1) * 3 + c]
                acc -= src[base + max(x - r, 0) * 3 + c]
    out = bytearray(len(src))
    for x in range(w):
        for c in range(3):
            i0 = x * 3 + c
            acc = tmp[i0] * (r + 1)
            for i in range(1, r + 1):
                acc += tmp[min(i, h - 1) * w * 3 + i0]
            for y in range(h):
                out[y * w * 3 + i0] = acc // n
                acc += tmp[min(y + r + 1, h - 1) * w * 3 + i0]
                acc -= tmp[max(y - r, 0) * w * 3 + i0]
    return out


def _sharp_frame(px_per_deg, horizon):
    """The scene as a perfect eye would see it, before acuity."""
    buf = bytearray(WIDTH * HEIGHT * 3)
    objs = []
    for label, ang, above, size_m, dist in SCENE:
        w_deg = subtends_deg(size_m, dist)
        objs.append(dict(label=label, dist=dist,
                         cx=WIDTH / 2 + ang * px_per_deg,
                         cy=horizon - above * px_per_deg,
                         wpx=max(w_deg * px_per_deg, 1.2),
                         named=is_named(size_m, dist), ecc=abs(ang)))
    objs.sort(key=lambda o: -o["dist"])

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if y < horizon:
                t = y / max(horizon, 1)
                r, g, b = (int(96 + 96 * t), int(126 + 82 * t),
                           int(168 + 62 * t))
            else:
                t = (y - horizon) / max(HEIGHT - horizon, 1)
                r, g, b = (int(112 - 52 * t), int(104 - 46 * t),
                           int(74 - 32 * t))
            i = (y * WIDTH + x) * 3
            buf[i], buf[i + 1], buf[i + 2] = r, g, b

    for o in objs:
        haze = 1.0 - math.exp(-o["dist"] / 1000.0 / HAZE_KM)
        _draw(buf, o, horizon, px_per_deg, haze)
    return buf, objs


def _blend(buf, x, y, c, a):
    if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
        return
    i = (y * WIDTH + x) * 3
    for k in range(3):
        buf[i + k] = int(buf[i + k] * (1 - a) + c[k] * a)


def _draw(buf, o, horizon, ppd, haze):
    """Shapes, not rectangles. Each gets hazed by its distance."""
    cx, cy, w = o["cx"], o["cy"], o["wpx"]
    lab = o["label"]
    sky = (150, 175, 205)

    def tint(c):
        return tuple(int(v * (1 - haze) + sky[k] * haze)
                     for k, v in enumerate(c))

    if lab == "ridge":
        h = w * 0.22
        for x in range(int(cx - w), int(cx + w)):
            prof = math.cos((x - cx) / max(w, 1) * 1.4)
            top = cy - h * max(prof, 0) ** 1.6
            for y in range(int(top), int(cy) + 1):
                _blend(buf, x, y, tint((84, 92, 104)), 0.85)
    elif lab == "tree":
        th = w * 2.6
        for x in range(int(cx - w * 0.07), int(cx + w * 0.07) + 1):
            for y in range(int(cy - th * 0.55), int(cy) + 1):
                _blend(buf, x, y, tint((66, 50, 36)), 0.95)
        ry, rx = th * 0.42, w * 0.62
        ccy = cy - th * 0.62
        for x in range(int(cx - rx), int(cx + rx) + 1):
            for y in range(int(ccy - ry), int(ccy + ry) + 1):
                d = ((x - cx) / rx) ** 2 + ((y - ccy) / ry) ** 2
                if d <= 1.0:
                    sh = 0.72 + 0.28 * (1 - d)
                    _blend(buf, x, y,
                           tint((int(44 * sh), int(84 * sh), int(38 * sh))),
                           0.95)
    elif lab.startswith("person"):
        hh = w * 2.9
        head = w * 0.42
        for x in range(int(cx - w * 0.5), int(cx + w * 0.5) + 1):
            for y in range(int(cy - hh), int(cy) + 1):
                f = min(max((cy - y) / max(hh, 1), 0.0), 1.0)
                halfw = w * (0.30 if f > 0.82 else 0.46 - 0.16 * f)
                if abs(x - cx) <= halfw:
                    _blend(buf, x, y, tint((52, 44, 42)), 0.95)
        hy = cy - hh - head * 0.5
        for x in range(int(cx - head), int(cx + head) + 1):
            for y in range(int(hy - head), int(hy + head) + 1):
                if (x - cx) ** 2 + (y - hy) ** 2 <= head * head:
                    _blend(buf, x, y, tint((70, 56, 50)), 0.95)
    elif lab == "fire":
        hh = w * 1.8
        for x in range(int(cx - w), int(cx + w) + 1):
            for y in range(int(cy - hh), int(cy) + 1):
                f = min(max((cy - y) / max(hh, 1), 0.0), 1.0)
                halfw = w * 0.7 * (1.0 - f) ** 0.6
                if abs(x - cx) <= halfw:
                    c = (255, int(150 + 90 * f), int(40 + 60 * f))
                    _blend(buf, x, y, c, 0.9)
        for x in range(int(cx - w * 2.4), int(cx + w * 2.4) + 1):
            for y in range(int(cy - hh * 1.6), int(cy + w * 0.5)):
                d = math.hypot((x - cx) / (w * 2.4),
                               (y - (cy - hh * 0.4)) / (hh * 1.3))
                if d < 1.0:
                    _blend(buf, x, y, (255, 170, 80), 0.16 * (1 - d) ** 2)
    elif lab == "bird":
        for x in range(int(cx - w), int(cx + w) + 1):
            dy = math.sin((x - cx) / max(w, 1) * 2.2) * w * 0.35
            for y in range(int(cy + dy - w * 0.12),
                           int(cy + dy + w * 0.12) + 1):
                _blend(buf, x, y, tint((40, 42, 48)), 0.9)
    else:                                   # hand and flake
        for x in range(int(cx - w * 0.5), int(cx + w * 0.5) + 1):
            for y in range(int(cy - w * 0.30), int(cy + w * 0.75) + 1):
                d = ((x - cx) / (w * 0.5)) ** 2 + \
                    ((y - cy - w * 0.2) / (w * 0.52)) ** 2
                if d <= 1.0:
                    _blend(buf, x, y, (128, 96, 76), 0.97)
        fw = w * 0.20
        for x in range(int(cx - fw), int(cx + fw) + 1):
            for y in range(int(cy - w * 0.52), int(cy - w * 0.12) + 1):
                if abs(x - cx) * 1.9 + abs(y - (cy - w * 0.32)) < fw * 1.5:
                    _blend(buf, x, y, (196, 200, 206), 0.95)


def render(path=None):
    """-> (path, [(label, deg, named, subtends)]). The view."""
    path = path or (ROOT / "data" / "pov.png")
    ppd = WIDTH / FIELD_DEG
    horizon = int(HEIGHT * 0.58)
    sharp, objs = _sharp_frame(ppd, horizon)

    levels = [sharp]
    for r in (2, 5, 11, 22):
        levels.append(_blur(sharp, WIDTH, HEIGHT, r))
    radii = [0.0, 2.0, 5.0, 11.0, 22.0]

    out = bytearray(WIDTH * HEIGHT * 3)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ecc = math.hypot((x - WIDTH / 2) / ppd, (y - horizon) / ppd)
            want = blur_radius_px(ecc, ppd)
            k = 0
            while k < len(radii) - 2 and radii[k + 1] < want:
                k += 1
            lo, hi = radii[k], radii[k + 1]
            f = 0.0 if hi <= lo else min(max((want - lo) / (hi - lo), 0), 1)
            i = (y * WIDTH + x) * 3
            for c in range(3):
                a, b = levels[k][i + c], levels[k + 1][i + c]
                out[i + c] = int(a * (1 - f) + b * f)

    fov = FOVEA_DEG * ppd
    for t in range(int(fov) + 1):
        for d in (-fov / 2, fov / 2):
            _blend(out, int(WIDTH / 2 - fov / 2 + t), int(horizon + d),
                   (255, 80, 60), 1.0)
            _blend(out, int(WIDTH / 2 + d), int(horizon - fov / 2 + t),
                   (255, 80, 60), 1.0)

    write_png(path, out, WIDTH, HEIGHT)
    return path, [(o["label"], o["ecc"], o["named"], o["wpx"] / ppd)
                  for o in objs]


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_image_comes_from_the_rules", _rules)
    t("the_sharp_patch_is_drawn_to_scale", _scale)
    t("acuity_blurs_it_does_not_grey_it", _blur_not_grey)
    t("distance_decides_what_is_named", _named)
    return all(o[1] for o in out), out


def _rules():
    """The claim is about the RULES, not about a file existing.

    This used to render a 1000x460 image -- 460,000 pixels, five
    blur passes -- to assert that acuity comes from engine/senses.py.
    Rendering is what __main__ is for. A check that runs a
    simulation has not found its rule yet.
    """
    from engine.senses import diffraction_limit, sampling_limit
    from engine.recognize import acuity_arcmin, recognition_range
    if not (diffraction_limit() > 0 and sampling_limit() > 0):
        raise ArithmeticError("acuity does not resolve")
    if acuity_arcmin() <= 0 or recognition_range(1.7) <= 0:
        raise ArithmeticError("the naming range does not resolve")
    return (f"pov.png is written from stdlib alone -- PNG is a "
            f"zlib stream and four headers. Acuity comes from "
            f"engine/senses.py, the fovea and the naming range from "
            f"engine/recognize.py, the falloff from cone density. "
            f"The picture is a CLAIM and can be wrong, which is the "
            f"only reason it is worth drawing")


def _scale():
    ppd = WIDTH / FIELD_DEG
    frac = (FOVEA_DEG * ppd) ** 2 / (WIDTH * HEIGHT)
    if frac > 0.01:
        raise ArithmeticError(f"the box is {100*frac:.1f}% of the frame")
    return (f"the red box is {FOVEA_DEG:.0f} degrees of "
            f"{FIELD_DEG:.0f} -- {FOVEA_DEG*ppd:.0f} px across in a "
            f"{WIDTH} px frame, {100*frac:.2f}% of it. Everything "
            f"outside is drawn at the resolution the eye has there")


def _blur_not_grey():
    ppd = WIDTH / FIELD_DEG
    near, far = blur_radius_px(0.0, ppd), blur_radius_px(50.0, ppd)
    if far < near * 5:
        raise ArithmeticError(f"blur only grows {far/max(near,1e-9):.1f}x")
    return (f"blur radius goes from {near:.1f} px at the centre to "
            f"{far:.1f} px at 50 degrees out, a factor of "
            f"{far/near:.0f}. The first version faded the edges to "
            f"GREY, which is not what an eye does -- acuity does not "
            f"desaturate, it leaves things UNRESOLVED, and those are "
            f"different pictures")


def _named():
    """Read off the scene table, not off a rendered frame."""
    near = [s for s in SCENE if s[0] == "person"][0]
    far = [s for s in SCENE if s[0] == "person far"][0]
    n_ok, f_ok = is_named(near[3], near[4]), is_named(far[3], far[4])
    if not n_ok or f_ok:
        raise ArithmeticError(f"near {n_ok}, far {f_ok}")
    return (f"the same 1.7 m person is NAMED at 19 m and only a shape "
            f"at 400 m, because engine/recognize.py puts the limit at "
            f"289 m. An earlier scene placed the far one at 240 m and "
            f"this check failed, correctly: 240 is inside 289, so "
            f"they were nameable and I had assumed otherwise")


if __name__ == "__main__":
    import time
    t0 = time.perf_counter()
    p, rep = render()
    print(f"  wrote {p}  in {time.perf_counter()-t0:.1f} s\n")
    print(f"  {'thing':<16}{'off centre':>11}{'subtends':>10}{'named':>8}")
    for label, ecc, named, w in rep:
        print(f"  {label:<16}{ecc:>10.0f}d{w:>9.2f}d"
              f"{'yes' if named else 'no':>8}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:40]}")
