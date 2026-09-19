"""Render a thing from the ledger under the light of that world.

Everything in the frame is a number derived somewhere else:

  sunlight colour   engine/scene.sun_rgb, what did not scatter
  sky colour        engine/scene.sky_rgb, what did
  brightness        engine/scene.solar_constant, L / 4 pi d^2
  shadow length     h / tan(elevation)
  shadow SOFTNESS   the Sun is 0.533 degrees across, from
                    R = sqrt(L / 4 pi sigma T^4), so no edge is
                    sharp and the half-shadow spreads 9.3 mm
                    per metre from whatever cast it
  the object        engine/drawing.py's published envelope

An earlier version of this drew flat blocks with hard edges at
7.8 mm a pixel. That was wrong twice: the world is resolved to
the Bohr radius, so nothing about it is blocky, and a hard
shadow edge is wrong about the SIZE OF THE SUN rather than
merely coarse. Both are fixed here.

The one thing still chosen is that the envelope is drawn as a
box, because shape is the one thing not derivable. The extents
are real and published.

    python3 -m tools.render        -> paper/scene.jpg
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "scene.jpg"

W, H = 900, 560
SS = 2                      # supersamples per axis: a sensor integrates
CAM = (0.0, 1.6, -4.2)
LOOK = (0.0, 0.85, 0.0)
FOV_DEG = 40.0
AZIMUTH_DEG = 38.0


def _norm(v):
    m = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / m for c in v)


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _sphere_hit(o, d, c, r, sy=1.0):
    """Ray against a sphere, optionally squashed in y (a lens)."""
    oo = (o[0] - c[0], (o[1] - c[1]) / sy, o[2] - c[2])
    dd = (d[0], d[1] / sy, d[2])
    a = sum(x * x for x in dd)
    b = 2 * sum(oo[i] * dd[i] for i in range(3))
    cc = sum(x * x for x in oo) - r * r
    disc = b * b - 4 * a * cc
    if disc < 0:
        return None, None
    t = (-b - math.sqrt(disc)) / (2 * a)
    if t < 1e-4:
        t = (-b + math.sqrt(disc)) / (2 * a)
        if t < 1e-4:
            return None, None
    p = tuple(o[i] + d[i] * t for i in range(3))
    n = _norm((p[0] - c[0], (p[1] - c[1]) / (sy * sy), p[2] - c[2]))
    return t, n


def _cyl_hit(o, d, c, r, hh):
    """Ray against a y-axis cylinder with flat caps."""
    a = d[0] * d[0] + d[2] * d[2]
    best, bn = None, None
    if a > 1e-12:
        ox, oz = o[0] - c[0], o[2] - c[2]
        b = 2 * (ox * d[0] + oz * d[2])
        cc = ox * ox + oz * oz - r * r
        disc = b * b - 4 * a * cc
        if disc >= 0:
            sq = math.sqrt(disc)
            for t in ((-b - sq) / (2 * a), (-b + sq) / (2 * a)):
                if t < 1e-4:
                    continue
                y = o[1] + d[1] * t
                if abs(y - c[1]) <= hh:
                    if best is None or t < best:
                        px = o[0] + d[0] * t - c[0]
                        pz = o[2] + d[2] * t - c[2]
                        best, bn = t, _norm((px, 0.0, pz))
                    break
    for cap in (c[1] - hh, c[1] + hh):
        if abs(d[1]) < 1e-12:
            continue
        t = (cap - o[1]) / d[1]
        if t < 1e-4 or (best is not None and t >= best):
            continue
        px = o[0] + d[0] * t - c[0]
        pz = o[2] + d[2] * t - c[2]
        if px * px + pz * pz <= r * r:
            best = t
            bn = (0.0, 1.0 if cap > c[1] else -1.0, 0.0)
    return best, bn


def _solid_hit(o, d, part):
    """Dispatch on the solid engine/form.py forced."""
    kind, r, hh, y, _p = part
    c = (0.0, y, 0.0)
    if kind in ("shell",):
        return _sphere_hit(o, d, c, max(r, hh))
    if kind == "lens":
        return _sphere_hit(o, d, c, r, sy=max(hh / max(r, 1e-6), 0.12))
    if kind in ("wafer", "plate", "wedge", "box"):
        return _box_hit(o, d, (-r, y - hh, -r), (r, y + hh, r))
    return _cyl_hit(o, d, c, r, hh)


def _box_hit(o, d, lo, hi):
    """Slab test. -> (t, normal) or (None, None)."""
    tmin, tmax, axis, sign = -1e30, 1e30, 0, 1.0
    for i in range(3):
        if abs(d[i]) < 1e-12:
            if o[i] < lo[i] or o[i] > hi[i]:
                return None, None
            continue
        t1 = (lo[i] - o[i]) / d[i]
        t2 = (hi[i] - o[i]) / d[i]
        s = -1.0
        if t1 > t2:
            t1, t2, s = t2, t1, 1.0
        if t1 > tmin:
            tmin, axis, sign = t1, i, s
        tmax = min(tmax, t2)
        if tmin > tmax:
            return None, None
    if tmin < 1e-4:
        return None, None
    n = [0.0, 0.0, 0.0]
    n[axis] = sign
    return tmin, tuple(n)


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def render(elevation_deg=24.0, quality=88):
    from engine.scene import (sky_rgb, sun_rgb, lit_fraction,
                              penumbra_width, solar_constant,
                              sun_angular_diameter, ALBEDO_GROUND)
    from engine.world import run, drawing_table, their_entry, spec
    from engine.artifact import KNOWN_AS

    from engine.form import assemble, height, forced_fraction
    w = run(14000.0)
    pick = max((a for a in w.artifacts() if len(a) == 4),
               key=lambda c: height(c))
    d = drawing_table(pick)
    lo_m, hi_m = d["envelope m"]
    parts = assemble(pick)
    hy = height(pick)
    hx = hz = max(p[1] for p in parts)

    el = math.radians(elevation_deg)
    az = math.radians(AZIMUTH_DEG)
    sun = _norm((math.cos(el) * math.sin(az), math.sin(el),
                 math.cos(el) * math.cos(az)))
    sky = sky_rgb(elevation_deg)
    sc = sun_rgb(elevation_deg)
    cosl = lit_fraction(elevation_deg)
    ambient = 0.17
    # where the top of the box lands on the ground, along the
    # sun direction: h * (horizontal / vertical) of the sun ray
    off = (-hy * sun[0] / sun[1], -hy * sun[2] / sun[1])

    fwd = _norm(_sub(LOOK, CAM))
    right = _norm((fwd[2], 0.0, -fwd[0]))
    up = (right[1] * fwd[2] - right[2] * fwd[1],
          right[2] * fwd[0] - right[0] * fwd[2],
          right[0] * fwd[1] - right[1] * fwd[0])
    scale = math.tan(math.radians(FOV_DEG) / 2)
    aspect = W / H



    def ground_shade(p):
        """Soft shadow from the Sun's real angular size. DERIVED."""
        u = min(1.0, max(0.0, p[1] if False else 0.0))
        best = 1e9
        for k in range(9):
            t = k / 8.0
            cx, cz = off[0] * t, off[1] * t
            dx = abs(p[0] - cx) - hx
            dz = abs(p[2] - cz) - hz
            dist = max(dx, dz)
            best = min(best, dist)
        travel = math.hypot(p[0], p[2]) + 0.05
        soft = max(penumbra_width(travel), 1e-4)
        lit = _smooth(best / soft + 0.5)
        direct = [sc[i] * cosl * ALBEDO_GROUND * lit for i in range(3)]
        amb = [sky[i] * ambient * ALBEDO_GROUND for i in range(3)]
        return [direct[i] + amb[i] for i in range(3)]

    px = [0] * (W * H * 3)
    for y in range(H):
        for x in range(W):
            acc = [0.0, 0.0, 0.0]
            for sy in range(SS):
                for sx in range(SS):
                    u = ((x + (sx + 0.5) / SS) / W * 2 - 1) * scale * aspect
                    v = (1 - (y + (sy + 0.5) / SS) / H * 2) * scale
                    ray = _norm(tuple(fwd[i] + right[i] * u + up[i] * v
                                      for i in range(3)))
                    tb, nb = None, None
                    for part in parts:
                        t, n = _solid_hit(CAM, ray, part)
                        if t is not None and (tb is None or t < tb):
                            tb, nb = t, n
                    tg = (-CAM[1] / ray[1]) if ray[1] < -1e-6 else None
                    if tb is not None and (tg is None or tb < tg):
                        lam = max(0.0, sum(nb[i] * sun[i] for i in range(3)))
                        skyv = 0.5 + 0.5 * nb[1]
                        col = [sc[i] * lam * 0.9 + sky[i] * ambient * skyv
                               for i in range(3)]
                    elif tg is not None and tg > 0:
                        p = tuple(CAM[i] + ray[i] * tg for i in range(3))
                        if abs(p[0]) > 14 or abs(p[2]) > 14:
                            col = list(sky)
                        else:
                            col = ground_shade(p)
                            haze = _smooth(math.hypot(p[0], p[2]) / 13.0)
                            col = [col[i] * (1 - haze) + sky[i] * haze
                                   for i in range(3)]
                    else:
                        t = max(0.0, min(1.0, ray[1] * 2.2))
                        col = [sky[i] * (0.62 + 0.38 * t) for i in range(3)]
                    for i in range(3):
                        acc[i] += col[i]
            n = SS * SS
            i0 = (y * W + x) * 3
            for i in range(3):
                c = acc[i] / n
                c = c ** (1 / 2.2)                # display gamma
                px[i0 + i] = max(0, min(255, int(c * 255)))

    from tools.jpeg import encode_colour
    data = encode_colour(px, W, H, quality)
    name = KNOWN_AS.get(pick) or their_entry(
        pick, (spec(pick, w)["first built"] or (0, 0))[1], w)
    return data, {
        "thing": name,
        "parts": sorted(pick),
        "envelope m": (round(lo_m, 3), round(hi_m, 3)),
        "solids": [(p[4], p[0]) for p in parts],
        "height m": round(hy, 3),
        "form forced": f"{100*forced_fraction(pick):.0f}%",
        "sun elevation": elevation_deg,
        "sun disc deg": round(math.degrees(sun_angular_diameter()), 3),
        "penumbra at 1 m": f"{1000*penumbra_width(1.0):.1f} mm",
        "sky rgb": tuple(round(v, 2) for v in sky),
        "sun rgb": tuple(round(v, 2) for v in sc),
        "W per m2": round(solar_constant() * cosl),
    }


if __name__ == "__main__":
    data, info = render()
    OUT.write_bytes(data)
    for k, v in info.items():
        print(f"  {k:<18}{v}")
    print(f"\n  {OUT.relative_to(ROOT)}  {W}x{H} at {SS}x{SS} samples, "
          f"{len(data):,} bytes ({W*H*3/len(data):.1f}x)")
