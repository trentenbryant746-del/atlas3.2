"""A real baseline JPEG encoder, with the quantization table
derived from the eye rather than copied from the standard.

WHAT IS AND IS NOT HERE. An earlier version of this docstring
said the world has no light and no scene. That was wrong about
this repository's own contents -- engine/scene.py now derives
the solar constant, the Sun's colour, the sky's colour and a
shadow's length from the cosmology and the geometry that were
already here, and tools/render.py draws with them.

What is still not derivable is the SHAPE of an artifact. The
envelope is published; a box is the simplest solid with those
extents; anything more would be invention.

The compression is the derived part either way: the
quantization table below comes from the contrast sensitivity of
the eye, not from Annex K.

    python3 -m tools.jpeg        -> paper/ledger.jpg
    python3 -m tools.render      -> paper/scene.jpg
"""

import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "ledger.jpg"

ZIGZAG = [
    0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
    12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63,
]

# Annex K Huffman tables. These are ENTROPY coding, not
# perception: they are a code for the symbol statistics and
# carry no claim about eyes, so they are used as published.
DC_BITS = [0, 0, 1, 5, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
DC_VALS = list(range(12))
AC_BITS = [0, 0, 2, 1, 3, 3, 2, 4, 3, 5, 5, 4, 4, 0, 0, 1, 0x7d]
AC_VALS = [
    0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31,
    0x41, 0x06, 0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32,
    0x81, 0x91, 0xa1, 0x08, 0x23, 0x42, 0xb1, 0xc1, 0x15, 0x52,
    0xd1, 0xf0, 0x24, 0x33, 0x62, 0x72, 0x82, 0x09, 0x0a, 0x16,
    0x17, 0x18, 0x19, 0x1a, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2a,
    0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44, 0x45,
    0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56, 0x57,
    0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69,
    0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a, 0x83,
    0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92, 0x93, 0x94,
    0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3, 0xa4, 0xa5,
    0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6,
    0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7,
    0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8,
    0xd9, 0xda, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7, 0xe8,
    0xe9, 0xea, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
    0xf9, 0xfa,
]


def sensitivity(cycles_per_degree):
    """Contrast sensitivity of the eye. MEASURED, a standard CSF.

    Peaks near 4 cycles a degree and falls away above it. This
    is the only reason a photograph can be thrown away in
    pieces and still look like itself.
    """
    f = max(cycles_per_degree, 0.1)
    return 2.6 * (0.0192 + 0.114 * f) * math.exp(-((0.114 * f) ** 1.1))


def quant_table(quality=75, pixels_per_degree=60.0):
    """8x8 quantization table DERIVED from the eye. DERIVED.

    Coefficient (u,v) of an 8x8 DCT carries a spatial frequency
    of sqrt(u^2+v^2)/16 cycles per pixel, which at
    pixels_per_degree becomes cycles per degree. A coefficient
    the eye is insensitive to can be divided by more before
    anybody notices, so the step is the inverse of sensitivity
    normalised to the peak.
    """
    peak = max(sensitivity(f / 10.0) for f in range(1, 800))
    scale = 50.0 / quality if quality >= 50 else 5000.0 / quality / 100
    tbl = []
    for u in range(8):
        for v in range(8):
            cyc = math.sqrt(u * u + v * v) / 16.0 * pixels_per_degree
            s = sensitivity(cyc) / peak
            step = max(1, min(255, round(scale * 8.0 / max(s, 1e-3))))
            tbl.append(step)
    tbl[0] = max(1, min(255, round(scale * 8)))
    return tbl


def dct8(block):
    """Forward DCT-II on an 8x8 block. Straight from the sum."""
    out = [0.0] * 64
    for u in range(8):
        cu = (1 / math.sqrt(2)) if u == 0 else 1.0
        for v in range(8):
            cv = (1 / math.sqrt(2)) if v == 0 else 1.0
            total = 0.0
            for x in range(8):
                cx = math.cos((2 * x + 1) * u * math.pi / 16)
                for y in range(8):
                    total += (block[x * 8 + y] * cx
                              * math.cos((2 * y + 1) * v * math.pi / 16))
            out[u * 8 + v] = 0.25 * cu * cv * total
    return out


class Bits:
    def __init__(self):
        self.out = bytearray()
        self.acc = 0
        self.n = 0

    def write(self, value, length):
        for i in range(length - 1, -1, -1):
            self.acc = (self.acc << 1) | ((value >> i) & 1)
            self.n += 1
            if self.n == 8:
                self.out.append(self.acc)
                if self.acc == 0xFF:
                    self.out.append(0x00)     # byte stuffing
                self.acc, self.n = 0, 0

    def flush(self):
        while self.n:
            self.write(1, 1)


def huff_codes(bits, vals):
    codes, code, k = {}, 0, 0
    for length in range(1, 17):
        for _ in range(bits[length]):
            codes[vals[k]] = (code, length)
            k += 1
            code += 1
        code <<= 1
    return codes


def magnitude(v):
    if v == 0:
        return 0, 0
    a = abs(v)
    size = a.bit_length()
    return (v if v > 0 else v + (1 << size) - 1), size


DC_C_BITS = [0, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
DC_C_VALS = list(range(12))
AC_C_BITS = [0, 0, 2, 1, 2, 4, 4, 3, 4, 7, 5, 4, 4, 0, 1, 2, 0x77]
AC_C_VALS = [
    0x00, 0x01, 0x02, 0x03, 0x11, 0x04, 0x05, 0x21, 0x31, 0x06,
    0x12, 0x41, 0x51, 0x07, 0x61, 0x71, 0x13, 0x22, 0x32, 0x81,
    0x08, 0x14, 0x42, 0x91, 0xa1, 0xb1, 0xc1, 0x09, 0x23, 0x33,
    0x52, 0xf0, 0x15, 0x62, 0x72, 0xd1, 0x0a, 0x16, 0x24, 0x34,
    0xe1, 0x25, 0xf1, 0x17, 0x18, 0x19, 0x1a, 0x26, 0x27, 0x28,
    0x29, 0x2a, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3a, 0x43, 0x44,
    0x45, 0x46, 0x47, 0x48, 0x49, 0x4a, 0x53, 0x54, 0x55, 0x56,
    0x57, 0x58, 0x59, 0x5a, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68,
    0x69, 0x6a, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79, 0x7a,
    0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89, 0x8a, 0x92,
    0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9a, 0xa2, 0xa3,
    0xa4, 0xa5, 0xa6, 0xa7, 0xa8, 0xa9, 0xaa, 0xb2, 0xb3, 0xb4,
    0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0xc2, 0xc3, 0xc4, 0xc5,
    0xc6, 0xc7, 0xc8, 0xc9, 0xca, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6,
    0xd7, 0xd8, 0xd9, 0xda, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7,
    0xe8, 0xe9, 0xea, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7, 0xf8,
    0xf9, 0xfa,
]


def _block_of(plane, w, h, bx, by, sx=1, sy=1):
    out = []
    for y in range(8):
        for x in range(8):
            px = min((bx + x) * sx, w - 1)
            py = min((by + y) * sy, h - 1)
            out.append(plane[py * w + px] - 128)
    return out


def _emit(bs, co, q, dcT, acT, prev):
    z = [int(round(co[ZIGZAG[i]] / q[ZIGZAG[i]])) for i in range(64)]
    diff = z[0] - prev
    val, size = magnitude(diff)
    c, l = dcT[size]
    bs.write(c, l)
    if size:
        bs.write(val, size)
    run = 0
    for i in range(1, 64):
        if z[i] == 0:
            run += 1
            continue
        while run > 15:
            c, l = acT[0xF0]
            bs.write(c, l)
            run -= 16
        val, size = magnitude(z[i])
        c, l = acT[(run << 4) | size]
        bs.write(c, l)
        bs.write(val, size)
        run = 0
    if run:
        c, l = acT[0x00]
        bs.write(c, l)
    return z[0]


def encode_colour(rgb, width, height, quality=75):
    """-> bytes. Baseline colour JPEG, YCbCr 4:2:0.

    The subsampling is the DERIVED one: engine/image.py gets 2x
    from colour acuity being a third of brightness, and this is
    where that number is spent. Chroma also takes a coarser
    quantization table for the same reason.
    """
    qY = quant_table(quality)
    qC = [min(255, max(1, v * 2)) for v in qY]
    dcY, acY = huff_codes(DC_BITS, DC_VALS), huff_codes(AC_BITS, AC_VALS)
    dcC, acC = (huff_codes(DC_C_BITS, DC_C_VALS),
                huff_codes(AC_C_BITS, AC_C_VALS))
    n = width * height
    Y = [0] * n
    Cb = [0] * n
    Cr = [0] * n
    for i in range(n):
        r, g, b = rgb[3 * i], rgb[3 * i + 1], rgb[3 * i + 2]
        Y[i] = int(max(0, min(255, 0.299 * r + 0.587 * g + 0.114 * b)))
        Cb[i] = int(max(0, min(255, 128 - 0.168736 * r
                               - 0.331264 * g + 0.5 * b)))
        Cr[i] = int(max(0, min(255, 128 + 0.5 * r - 0.418688 * g
                               - 0.081312 * b)))
    cw, ch = (width + 1) // 2, (height + 1) // 2
    cbs = [0] * (cw * ch)
    crs = [0] * (cw * ch)
    for y in range(ch):
        for x in range(cw):
            tot_b = tot_r = 0
            for dy in range(2):
                for dx in range(2):
                    px = min(2 * x + dx, width - 1)
                    py = min(2 * y + dy, height - 1)
                    tot_b += Cb[py * width + px]
                    tot_r += Cr[py * width + px]
            cbs[y * cw + x] = tot_b // 4
            crs[y * cw + x] = tot_r // 4
    bs = Bits()
    pY = pB = pR = 0
    for my in range(0, height, 16):
        for mx in range(0, width, 16):
            for dy in (0, 8):
                for dx in (0, 8):
                    blk = _block_of(Y, width, height, mx + dx, my + dy)
                    pY = _emit(bs, dct8(blk), qY, dcY, acY, pY)
            bx, by = mx // 2, my // 2
            pB = _emit(bs, dct8(_block_of(cbs, cw, ch, bx, by)),
                       qC, dcC, acC, pB)
            pR = _emit(bs, dct8(_block_of(crs, cw, ch, bx, by)),
                       qC, dcC, acC, pR)
    bs.flush()

    def seg(marker, payload):
        return (struct.pack(">H", marker)
                + struct.pack(">H", len(payload) + 2) + payload)

    out = bytearray(b"\xFF\xD8")
    out += seg(0xFFE0, b"JFIF\x00" + bytes([1, 1, 0])
               + struct.pack(">HH", 1, 1) + bytes([0, 0]))
    out += seg(0xFFDB, bytes([0]) + bytes(qY[ZIGZAG[i]] for i in range(64)))
    out += seg(0xFFDB, bytes([1]) + bytes(qC[ZIGZAG[i]] for i in range(64)))
    out += seg(0xFFC0, bytes([8]) + struct.pack(">HH", height, width)
               + bytes([3, 1, 0x22, 0, 2, 0x11, 1, 3, 0x11, 1]))
    out += seg(0xFFC4, bytes([0x00]) + bytes(DC_BITS[1:]) + bytes(DC_VALS))
    out += seg(0xFFC4, bytes([0x10]) + bytes(AC_BITS[1:]) + bytes(AC_VALS))
    out += seg(0xFFC4, bytes([0x01]) + bytes(DC_C_BITS[1:]) + bytes(DC_C_VALS))
    out += seg(0xFFC4, bytes([0x11]) + bytes(AC_C_BITS[1:]) + bytes(AC_C_VALS))
    out += seg(0xFFDA, bytes([3, 1, 0x00, 2, 0x11, 3, 0x11, 0, 63, 0]))
    out += bytes(bs.out)
    out += b"\xFF\xD9"
    return bytes(out)


def encode(pixels, width, height, quality=75):
    """-> bytes. A baseline grayscale JPEG. Real, and it opens."""
    q = quant_table(quality)
    dc = huff_codes(DC_BITS, DC_VALS)
    ac = huff_codes(AC_BITS, AC_VALS)
    bs = Bits()
    prev_dc = 0
    for by in range(0, height, 8):
        for bx in range(0, width, 8):
            block = []
            for y in range(8):
                for x in range(8):
                    px = min(bx + x, width - 1)
                    py = min(by + y, height - 1)
                    block.append(pixels[py * width + px] - 128)
            co = dct8(block)
            z = [int(round(co[ZIGZAG[i]] / q[ZIGZAG[i]]))
                 for i in range(64)]
            diff = z[0] - prev_dc
            prev_dc = z[0]
            val, size = magnitude(diff)
            code, ln = dc[size]
            bs.write(code, ln)
            if size:
                bs.write(val, size)
            run = 0
            for i in range(1, 64):
                if z[i] == 0:
                    run += 1
                    continue
                while run > 15:
                    c, l = ac[0xF0]
                    bs.write(c, l)
                    run -= 16
                val, size = magnitude(z[i])
                c, l = ac[(run << 4) | size]
                bs.write(c, l)
                bs.write(val, size)
                run = 0
            if run:
                c, l = ac[0x00]
                bs.write(c, l)
    bs.flush()

    def seg(marker, payload):
        return (struct.pack(">H", marker)
                + struct.pack(">H", len(payload) + 2) + payload)

    out = bytearray(b"\xFF\xD8")
    out += seg(0xFFE0, b"JFIF\x00" + bytes([1, 1, 0]) +
               struct.pack(">HH", 1, 1) + bytes([0, 0]))
    out += seg(0xFFDB, bytes([0]) + bytes(q[ZIGZAG[i]] for i in range(64)))
    out += seg(0xFFC0, bytes([8]) + struct.pack(">HH", height, width)
               + bytes([1, 1, 0x11, 0]))
    out += seg(0xFFC4, bytes([0x00]) + bytes(DC_BITS[1:]) + bytes(DC_VALS))
    out += seg(0xFFC4, bytes([0x10]) + bytes(AC_BITS[1:]) + bytes(AC_VALS))
    out += seg(0xFFDA, bytes([1, 1, 0x00, 0, 63, 0]))
    out += bytes(bs.out)
    out += b"\xFF\xD9"
    return bytes(out)


def ledger_image(scale=6):
    """-> (pixels, w, h). Real values from the run. RECORDED.

    Rows are bands, columns are time, brightness is how many
    crafts that band held at that moment. Nothing here is drawn;
    every pixel is a count that happened.
    """
    from engine.world import run
    from engine.artifact import PRIMITIVES
    w = run(14000.0)
    steps = int(w.year / 10.0)
    held = [[0] * steps for _ in w.bands]
    counts = {b.ident: 0 for b in w.bands}
    order = sorted(w.ledger, key=lambda r: r[0])
    idx, total = 0, len(order)
    for s in range(steps):
        year = s * 10.0
        while idx < total and order[idx][0] <= year:
            _y, band, kind, _what = order[idx]
            if kind in ("craft", "learned"):
                counts[band] += 1
            idx += 1
        for b in w.bands:
            held[b.ident][s] = counts[b.ident]
    top = max(max(r) for r in held) or 1
    W, H = steps, len(w.bands) * scale
    px = [0] * (W * H)
    for bi, row in enumerate(held):
        for y in range(scale):
            for x in range(W):
                px[(bi * scale + y) * W + x] = int(
                    255 * row[x] / top)
    return px, W, H


if __name__ == "__main__":
    px, w, h = ledger_image()
    raw = len(px)
    data = encode(px, w, h)
    OUT.write_bytes(data)
    print(f"  {OUT.relative_to(ROOT)}  {w}x{h}, {len(data):,} bytes")
    print(f"  raw grayscale would be {raw:,} bytes "
          f"-- {raw/len(data):.1f}x")
    print(f"  starts {data[:2].hex()} ends {data[-2:].hex()}")
    q = quant_table()
    print(f"  derived quant table: DC step {q[0]}, "
          f"highest frequency step {q[63]}")
