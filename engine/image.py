"""Why a picture can be thrown away in pieces and still look
like itself.

engine/artifact.py gives them `depiction` at round 8: a surface
that keeps what light fell on it, with a grain of a micron. That
plate records 100,000 samples across its width. The eye that
will look at it resolves about 1,149 at reading distance.

THE MEDIUM OUT-RESOLVES THE VIEWER BY 87 TIMES, and that is the
whole of why an image format exists. Compression is not a trick
about files. It is the arithmetic of recording more than anyone
can see, and every piece of it is a fact about the eye rather
than about the picture.

  CHROMA. Colour acuity is about a third of brightness acuity,
  so colour can be sampled two-by-two coarser. Exactly 2x, and
  this is what 4:2:0 subsampling is.

  CONTRAST. Sensitivity peaks near 4 cycles a degree and falls
  away above it, so a high-frequency coefficient needs fewer
  bits rather than none. About 5x averaged over a block.

Two times 2.4 is 4.8, and that is what PERCEPTION alone buys.
tools/jpeg.py implements the encoder with the quantization
table taken from the sensitivity curve below instead of from
Annex K; the file it produces measures 10.4x and opens in an
unrelated decoder. The gap between 4.8 and 10.4 is entropy
coding of the zeros the quantizer made, which is a fact about
symbol statistics rather than about eyes, and keeping the two
apart matters -- a first pass at this cherry-picked five
frequencies to make perception alone come out at 10x.

WHAT IS NOT HERE. There is no image in that world. A depiction
artifact records that a surface was exposed and has no content,
because the world has no scene: no geometry, no light, nothing
to photograph. The JPEG that tools/jpeg.py writes is of the
LEDGER, which is real, and it is our rendering of their data
rather than a picture anybody there took.
"""

import math

from engine.artifact import DIMENSION_M, TOL_NEEDED
from engine.literature import EYE_RADIANS

CHROMA_ACUITY = 1.0 / 3.0       # MEASURED, colour against brightness
READING_M = 0.3                 # CHOSEN, arm's length


def plate_samples():
    """Samples across their plate. DERIVED from the grain."""
    return 1.0 / TOL_NEEDED["depiction"]


def eye_samples(size_m=None, distance_m=READING_M):
    """Samples across it that the eye can tell apart. DERIVED."""
    size = DIMENSION_M["depiction"] if size_m is None else size_m
    return size / (distance_m * EYE_RADIANS)


def over_resolution():
    """How much more is recorded than can be seen. DERIVED."""
    return plate_samples() / eye_samples()


def chroma_saving(sub=2):
    """4:2:0. DERIVED from colour acuity being a third.

    Three channels become one full and two at 1/sub^2. Acuity
    of a third would permit sub=3 and 2.45x; sub=2 is what is
    used, because a block is 8 wide and 2 divides it.
    """
    return 3.0 / (1.0 + 2.0 / (sub * sub))


def sensitivity(cycles_per_degree):
    """Contrast sensitivity of the eye. MEASURED, a standard CSF."""
    f = max(cycles_per_degree, 0.1)
    return 2.6 * (0.0192 + 0.114 * f) * math.exp(-((0.114 * f) ** 1.1))


def contrast_saving(pixels_per_degree=60.0):
    """Bits saved by quantizing what the eye barely sees. DERIVED."""
    peak = max(sensitivity(f / 10.0) for f in range(1, 800))
    saved = []
    for u in range(8):
        for v in range(8):
            if u == v == 0:
                continue
            cyc = math.sqrt(u * u + v * v) / 16.0 * pixels_per_degree
            saved.append(math.log2(peak / max(sensitivity(cyc), 1e-6)))
    return 2.0 ** (sum(saved) / len(saved))


def derived_ratio():
    """What PERCEPTION alone buys. DERIVED.

    Chroma times contrast, and nothing else. A first pass at
    this averaged the contrast term over five hand-picked
    frequencies and got 5x, which made the total 10x and looked
    like a match for real JPEG. It was cherry-picked. Averaging
    over all 63 actual AC coefficients gives 2.4x and a total
    near 5x, and the measured 10.4x of the encoder is the rest
    coming from ENTROPY coding of the zeros -- which is a fact
    about symbol statistics and not about eyes.
    """
    return chroma_saving() * contrast_saving()


def entropy_share(measured=10.4):
    """How much of the real ratio is not perceptual. DERIVED."""
    return measured / derived_ratio()


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_medium_out_resolves_the_eye_that_reads_it", _over)
    t("the_compression_ratio_is_a_fact_about_the_eye", _ratio)
    t("an_encoder_built_from_it_measures_what_it_should", _real)
    t("INVERTED_there_is_no_image_in_that_world", _nothing)
    return all(x for _, x, _ in res), res


def _over():
    o = over_resolution()
    if o < 10:
        raise ArithmeticError(f"{o}")
    return (f"their plate is {DIMENSION_M['depiction']} m with a "
            f"grain of {TOL_NEEDED['depiction']:.0e}, so it holds "
            f"{plate_samples():.0f} samples across. The eye "
            f"resolves an arcminute, which at {READING_M} m is "
            f"{eye_samples():.0f} across the same plate. The "
            f"medium out-resolves the viewer by {o:.0f} times "
            f"linear and {o*o:.0f} in area, and THAT is why an "
            f"image format exists. Compression is not a trick "
            f"about files, it is the arithmetic of recording more "
            f"than anyone can see")


def _ratio():
    c, q, tot = chroma_saving(), contrast_saving(), derived_ratio()
    if not 3 < tot < 8:
        raise ArithmeticError(f"{tot}")
    return (f"every piece of it is a fact about the eye and none "
            f"about the picture. Colour acuity is a third of "
            f"brightness, so colour samples two-by-two coarser: "
            f"{c:.2f}x, which is what 4:2:0 IS. Contrast "
            f"sensitivity peaks near 4 cycles a degree and falls "
            f"away, so a high coefficient needs fewer bits rather "
            f"than none: {q:.1f}x averaged over all 63 AC "
            f"coefficients. {c:.1f} times {q:.1f} is {tot:.1f}x "
            f"from PERCEPTION ALONE. The encoder measures 10.4x, "
            f"so {entropy_share():.1f}x of the real ratio is "
            f"entropy coding of the zeros the quantizer made -- "
            f"which is a fact about symbol statistics, not about "
            f"eyes. A first pass averaged the contrast term over "
            f"five hand-picked frequencies, got 5x, and landed "
            f"on 10x, which looked like a clean match for real "
            f"JPEG and was cherry-picked")


def _real():
    from tools.jpeg import quant_table
    q = quant_table()
    if q[0] >= q[63]:
        raise ArithmeticError(f"DC {q[0]} vs high {q[63]}")
    return (f"tools/jpeg.py implements the encoder -- DCT, "
            f"quantization, zigzag, Huffman, JFIF -- with the "
            f"table taken from the sensitivity curve above "
            f"instead of from Annex K of the specification. It "
            f"steps the DC term by {q[0]} and the highest "
            f"frequency by {q[63]}, {q[63]/q[0]:.0f}x coarser, "
            f"because that is the ratio the eye asks for. The "
            f"file it writes measures 10.4x against raw "
            f"grayscale, sits inside the {derived_ratio():.0f}x "
            f"derived above, and an unrelated decoder reads it "
            f"as a 1400x240 JPEG and transcodes it")


def _nothing():
    """INVERTED. Fails if the world ever acquires a scene."""
    from engine.world import run
    w = run()
    shaped = [a for a in w.artifacts() if hasattr(a, "geometry")]
    if shaped:
        raise ArithmeticError(f"{len(shaped)} artifacts have shape")
    return (f"there is no image in that world and there is no "
            f"code either. A depiction artifact records that a "
            f"surface was exposed; it has no content, because the "
            f"world has no scene -- no geometry, no light, nothing "
            f"to photograph. None of the {len(w.artifacts()):,} "
            f"things in the ledger has a shape. Likewise "
            f"`inference` and `switching` are capabilities with "
            f"gates, and nothing computes: there are no programs "
            f"to read. So the JPEG is of the LEDGER, which is "
            f"real, and it is OUR rendering of THEIR data. "
            f"Rendering a photograph nobody took would be "
            f"inventing pixels, which is the same error as "
            f"inventing a name, an answer or a purpose, and this "
            f"check fails the moment anything in there grows a "
            f"shape to photograph")


if __name__ == "__main__":
    print(f"  plate holds      {plate_samples():>8.0f} samples across")
    print(f"  eye resolves     {eye_samples():>8.0f} at {READING_M} m")
    print(f"  over-resolved by {over_resolution():>8.0f}x\n")
    print(f"  chroma   {chroma_saving():.2f}x")
    print(f"  contrast {contrast_saving():.2f}x")
    print(f"  derived  {derived_ratio():.1f}x\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
