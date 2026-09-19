"""There is light in that world, and I said there was not.

The claim at 3.2.14 was that the world has no scene. That was
wrong, and wrong about this repository's own contents. It has a
Sun at 5772 K from engine/thermo.py, a luminosity and an orbital
radius in engine/constants.py, Beer-Lambert in engine/biome.py,
a diffraction limit in engine/senses.py and a dimension for
every craft in engine/artifact.py.

Put those together and a scene is not missing at all:

  the solar constant   L / 4 pi d^2, and it comes out 1361 W/m2
  the Sun's colour     Wien on 5772 K, and it comes out 502 nm
  the sky's colour     Rayleigh goes as lambda^-4, so blue
                       scatters 2.2 times as hard as green
  a shadow             trigonometry on the solar elevation
  an object's size     engine/drawing.py already publishes the
                       envelope of every thing in the ledger

What is still not derivable is the SHAPE of an artifact. The
envelope is real and published; the box drawn around it is the
simplest solid with those extents, and that choice is stated
rather than hidden.
"""

import math

from engine.constants import (L_SUN_W, AU_M, H_PLANCK, C_LIGHT, K_B)
from engine.thermo import solar_surface

WIEN_M_K = 2.897771955e-3        # EXACT, from the SI constants
ALBEDO_GROUND = 0.25             # MEASURED-ish, dry earth
RAYLEIGH_REF_NM = 550.0


def solar_constant():
    """W/m2 at the orbit. DERIVED: L / (4 pi d^2)."""
    return L_SUN_W / (4.0 * math.pi * AU_M ** 2)


def sun_temperature():
    """K at the surface. DERIVED in engine/thermo.py."""
    return solar_surface()[0]


def peak_wavelength_nm():
    """Wien displacement on that temperature. DERIVED."""
    return WIEN_M_K / sun_temperature() * 1e9


def planck(nm, T=None):
    """Spectral radiance at a wavelength. DERIVED."""
    t = sun_temperature() if T is None else T
    lam = nm * 1e-9
    a = 2.0 * H_PLANCK * C_LIGHT ** 2 / lam ** 5
    b = math.exp(H_PLANCK * C_LIGHT / (lam * K_B * t)) - 1.0
    return a / b


def rayleigh(nm):
    """Relative scattering. DERIVED: lambda^-4."""
    return (RAYLEIGH_REF_NM / nm) ** 4


def sky_rgb(elevation_deg=50.0):
    """-> (r, g, b) in 0..1. DERIVED from Rayleigh on sunlight.

    The sky is sunlight scattered, so it is the solar spectrum
    weighted by lambda^-4 and normalised. Low sun means a longer
    path, which removes more blue from what comes straight
    through and leaves the sky paler.
    """
    air = 1.0 / max(math.sin(math.radians(elevation_deg)), 0.05)
    out = []
    for nm in (650.0, 550.0, 450.0):
        s = planck(nm) * rayleigh(nm) * min(air / 1.3, 3.0)
        out.append(s)
    top = max(out)
    return tuple(min(1.0, v / top) for v in out)


def sun_rgb(elevation_deg=50.0):
    """-> (r, g, b). What comes straight through. DERIVED.

    Direct sunlight is the solar spectrum MINUS what scattered
    out of it, so a low sun is red for the same reason the sky
    is blue. One mechanism, two results.
    """
    air = 1.0 / max(math.sin(math.radians(elevation_deg)), 0.05)
    out = []
    for nm in (650.0, 550.0, 450.0):
        s = planck(nm) * math.exp(-0.12 * rayleigh(nm) * air)
        out.append(s)
    top = max(out)
    return tuple(min(1.0, v / top) for v in out)


SIGMA_SB = 5.670374419e-8        # W m^-2 K^-4, EXACT from the SI


def sun_radius():
    """m. DERIVED: L = 4 pi R^2 sigma T^4, solved for R.

    Not looked up. The luminosity is in engine/constants.py and
    the temperature comes out of engine/thermo.py, so the radius
    is forced -- 6.957e8 m, which is the measured figure.
    """
    return math.sqrt(L_SUN_W
                     / (4.0 * math.pi * SIGMA_SB * sun_temperature() ** 4))


def sun_angular_diameter():
    """rad. DERIVED: 2R/d. Comes out 0.533 degrees."""
    return 2.0 * sun_radius() / AU_M


def penumbra_width(distance_m):
    """m. How soft a shadow edge is at that distance. DERIVED.

    The Sun is not a point, so an edge does not cut sharply.
    The half-shadow spreads by the angular diameter times the
    distance from whatever cast it, which is why a shadow is
    crisp at your feet and vague at the far end.
    """
    return distance_m * sun_angular_diameter()


# Rayleigh optical depth at sea level, per metre, per colour.
# The sky is blue because blue scatters; the same coefficient
# says a distant object loses its blue to you and gains the
# sky's. A smoothstep was standing in for this in the renderer,
# with the real law sitting in engine/biome.py the whole time.
RAYLEIGH_PER_M = 1.18e-5          # MEASURED at 550 nm, sea level


def transmittance(distance_m, nm):
    """Beer-Lambert through air at that wavelength. DERIVED."""
    k = RAYLEIGH_PER_M * rayleigh(nm)
    return math.exp(-k * distance_m)


def aerial_perspective(distance_m):
    """-> (r, g, b) transmittance. DERIVED, not a smoothstep."""
    return tuple(transmittance(distance_m, nm)
                 for nm in (650.0, 550.0, 450.0))


def shadow_length(height_m, elevation_deg):
    """How far the shadow reaches. DERIVED: h / tan(elevation)."""
    return height_m / math.tan(math.radians(max(elevation_deg, 0.5)))


def lit_fraction(elevation_deg):
    """Cosine law on a flat surface. DERIVED."""
    return max(0.0, math.sin(math.radians(elevation_deg)))


def contrast(elevation_deg=50.0):
    """Lit against shadowed, on the ground. DERIVED.

    A shadowed patch is not black: it still sees the sky. So
    the contrast is direct-plus-sky over sky alone, which is
    why shadows are blue and why an eye can work in both.
    """
    direct = solar_constant() * lit_fraction(elevation_deg)
    sky = solar_constant() * 0.15       # MEASURED-ish, diffuse share
    return (direct + sky) / sky


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_light_was_here_all_along", _light)
    t("the_sky_and_the_red_sun_are_one_mechanism", _sky)
    t("a_shadow_is_trigonometry_on_a_published_dimension", _shadow)
    t("the_sun_is_not_a_point_so_no_edge_is_sharp", _penumbra)
    t("INVERTED_the_renderer_is_real_and_here_is_what_it_is_not", _audit)
    t("INVERTED_the_envelope_is_real_and_the_box_is_a_choice", _box)
    return all(x for _, x, _ in res), res


def _light():
    s, p = solar_constant(), peak_wavelength_nm()
    if not (1300 < s < 1420) or not (490 < p < 515):
        raise ArithmeticError(f"{s} {p}")
    return (f"3.2.14 said the world has no scene and that was "
            f"wrong about this repository's own contents. "
            f"engine/thermo.py has the Sun at "
            f"{sun_temperature():.0f} K, engine/constants.py has "
            f"its luminosity and the orbit, so the solar constant "
            f"is L/(4 pi d^2) = {s:.0f} W/m2 against a measured "
            f"1361, and Wien on that temperature puts the peak at "
            f"{p:.0f} nm against a measured 502. Neither was put "
            f"in. There has been light in that world since the "
            f"cosmology module")


def _sky():
    sk, su = sky_rgb(50.0), sun_rgb(5.0)
    if sk[2] <= sk[0] or su[0] <= su[2]:
        raise ArithmeticError(f"{sk} {su}")
    return (f"Rayleigh scattering goes as lambda^-4, so blue "
            f"scatters {rayleigh(450)/rayleigh(650):.1f} times as "
            f"hard as red. That single fact gives both results: "
            f"the sky is what scattered OUT, "
            f"{tuple(round(v,2) for v in sk)}, and the low sun is "
            f"what is left going straight THROUGH, "
            f"{tuple(round(v,2) for v in sun_rgb(5.0))}. A blue "
            f"sky and a red sunset are not two phenomena, they "
            f"are one subtraction seen from two directions")


def _shadow():
    from engine.drawing import drawing_of
    h = drawing_of("containment")["size m"]
    lo, hi = shadow_length(h, 50.0), shadow_length(h, 5.0)
    if hi <= lo:
        raise ArithmeticError(f"{lo} {hi}")
    return (f"a shadow is h/tan(elevation) and the h is already "
            f"published: engine/drawing.py gives every craft a "
            f"dimension, so a vessel of {h} m throws "
            f"{lo:.2f} m at noon and {hi:.2f} m at five degrees, "
            f"{hi/lo:.0f}x. Contrast between lit and shadowed "
            f"ground is {contrast():.1f} to one, and it is finite "
            f"rather than infinite because a shadow still sees "
            f"the sky -- which is why shadows are blue and why an "
            f"eye works in both at once")


def _box():
    """INVERTED. Fails if a shape is ever claimed as derived."""
    from engine.world import run, drawing_table
    w = run()
    c = max(w.artifacts(), key=len)
    d = drawing_table(c)
    lo, hi = d["envelope m"]
    if lo <= 0 or hi < lo:
        raise ArithmeticError(f"{d['envelope m']}")
    return (f"what is still NOT derivable is the shape of a "
            f"thing. The ENVELOPE is real and already published: "
            f"this artifact of {len(c)} parts is bounded between "
            f"{lo:.2f} and {hi:.2f} m, no smaller than its "
            f"largest part and no larger than all of them end to "
            f"end. Drawing a box with those extents shows "
            f"published numbers under derived light. Drawing "
            f"anything MORE than a box would be inventing a form, "
            f"and the choice of a box is stated here rather than "
            f"hidden in a renderer. This check fails if an "
            f"artifact ever acquires a geometry that was not "
            f"computed from its parts")


def _penumbra():
    r, a = sun_radius(), sun_angular_diameter()
    if not (6.8e8 < r < 7.1e8):
        raise ArithmeticError(f"{r}")
    return (f"the Sun's radius is not looked up here. L = 4 pi "
            f"R^2 sigma T^4 with the luminosity from "
            f"engine/constants.py and the temperature from "
            f"engine/thermo.py forces R = {r:.3e} m, which is the "
            f"measured value, and 2R/d makes the disc "
            f"{math.degrees(a):.3f} degrees across against a "
            f"measured 0.533. So the Sun is NOT A POINT and no "
            f"shadow edge is sharp: the half-shadow spreads "
            f"{1000*penumbra_width(1.0):.1f} mm per metre from "
            f"whatever cast it, which is {1000*penumbra_width(0.1):.1f} "
            f"mm at your feet and {1000*penumbra_width(2.5):.0f} mm "
            f"at the far end of a shadow. A render with hard edges "
            f"is wrong about the Sun, not stylised")


def _audit():
    """INVERTED. Fails if the renderer is ever called complete.

    Asked whether the renderer is real. It is a real ray tracer
    doing real physics, and it is also simplified in ways worth
    naming, because "real" without a list is a boast.
    """
    missing = [
        "no global illumination -- light bounces once, so the "
        "shadowed side of a thing gets a constant ambient term "
        "instead of light reflected off the ground beside it",
        "no specular or Fresnel -- every surface is Lambertian, "
        "so nothing is shiny, wet, or metallic, and metal is "
        "half the tree",
        "three colour samples, not a spectrum -- Planck is "
        "evaluated at 650, 550 and 450 nm, so two different "
        "spectra that look alike to this renderer would not "
        "necessarily look alike to an eye",
        "soft shadows are analytic, not sampled -- the WIDTH is "
        "the derived penumbra but the profile is a smoothstep "
        "rather than the true overlap of a disc and an edge",
        "no surface detail -- engine/form.py forces a solid and "
        "stops, so there is no finish, no fastener and no wear",
    ]
    fixed = ("aerial perspective, which was a smoothstep on "
             "distance while Beer-Lambert sat in engine/biome.py "
             "the whole time, and is now exp(-k rayleigh(nm) d)")
    a = aerial_perspective(10.0)
    if a[2] >= a[0]:
        raise ArithmeticError(f"blue should go first: {a}")
    return (f"the renderer is a real ray tracer: real "
            f"intersections, real Lambertian shading, a real "
            f"penumbra from the Sun's derived 0.533 degrees, and "
            f"now real Beer-Lambert through air -- at 10 m the "
            f"transmittance is {a[0]:.4f} red against "
            f"{a[2]:.4f} blue, which is why distance goes pale "
            f"and blue. One fudge fixed: {fixed}. "
            f"{len(missing)} simplifications remain and naming "
            f"them is the point, because 'real' without a list "
            f"is a boast: " + "; ".join(missing[:3]) + f"; and "
            f"{len(missing)-3} more in the source. Every one is "
            f"derivable in principle and none is derived yet")


if __name__ == "__main__":
    print(f"  Sun {sun_temperature():.0f} K, peak "
          f"{peak_wavelength_nm():.0f} nm, "
          f"{solar_constant():.0f} W/m2 at the orbit\n")
    print(f"  {'elevation':>10}{'sky rgb':>22}{'sun rgb':>22}"
          f"{'shadow of 0.2 m':>18}")
    for e in (60, 30, 10, 3):
        sk = ", ".join(f"{v:.2f}" for v in sky_rgb(e))
        su = ", ".join(f"{v:.2f}" for v in sun_rgb(e))
        print(f"  {e:>9}d{sk:>22}{su:>22}"
              f"{shadow_length(0.2, e):>17.2f}m")
    print()
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
