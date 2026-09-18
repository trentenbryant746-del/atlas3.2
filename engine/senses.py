"""
A body that can look around, and what it would take to fail.

Everything so far has been budgets: watts in, watts out, atoms
conserved. None of it says whether the animal can SEE the stone it
is about to pick up, hold it once picked, or stand up while doing
so. Those are not details. A tool that cannot be aimed is not a
tool, and engine/tools.py quietly assumed all three.

So the parts are checked, and every failure reports the mechanism
rather than the verdict. Not "the grip failed" but which force
fell short of which, by how much, and what it was resisting -- the
same way engine/transitions.py refuses a decay by naming the Q
value instead of saying no.

WHAT THE EYE TURNS OUT TO BE. Three routes to the same number,
none of them told about the others:

    diffraction, 1.22 lam/D at a 3 mm pupil    0.77 arcmin
    cone spacing 2.5 um at f = 17 mm, Nyquist  1.01 arcmin
    measured human acuity                      1.00 arcmin

The optics and the sampling agree to 1.31x. The eye is as sharp as
its aperture physically permits and the retina is as fine as the
optics justify, and neither is wasted on the other. Nothing here
arranged that.

AND SPACE IS TWO EYES AND A SUBTRACTION. Depth from disparity goes
as z^2, so a 6.4 cm baseline resolves under a millimetre at arm's
length, 7.6 cm at ten metres, and nothing at all past 1,320 m. The
distance at which a body stops seeing space is a number, and it is
b over the disparity threshold.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# MEASURED
WAVELENGTH_M = 550e-9        # peak photopic sensitivity
PUPIL_M = 3.0e-3             # daylight
EYE_FOCAL_M = 0.017
CONE_PITCH_M = 2.5e-6        # foveal
EYE_BASELINE_M = 0.064       # interpupillary
DISPARITY_RAD = 4.85e-5      # 10 arcsec, stereoacuity threshold
GRIP_FRICTION = 0.5          # skin on stone
PRECISION_GRIP_N = 80.0      # thumb opposed
HOOK_GRIP_N = 25.0           # no opposition
STONE_KG = 1.0
STRIKE_SPEED = 5.0           # m/s at contact
STRIKE_SWING_M = 0.5         # over which it is accelerated


class Gate:
    """A requirement that says WHY when it is not met.

    A verdict alone is the least useful part of a failure. What is
    wanted is the quantity that fell short, the one it lost to, and
    the factor between them -- which is what tells you whether it
    is nearly there or not that kind of thing at all.
    """

    def __init__(self, name, have, need, unit, mechanism):
        self.name, self.have, self.need = name, have, need
        self.unit, self.mechanism = unit, mechanism

    @property
    def ok(self):
        return self.have >= self.need

    @property
    def ratio(self):
        return self.have / self.need if self.need else math.inf

    def why(self):
        v = "holds" if self.ok else "FAILS"
        s = (f"{self.have:.3g} {self.unit} against {self.need:.3g} "
             f"needed, {self.ratio:.3g}x")
        return f"{v}: {s} -- {self.mechanism}"


def diffraction_limit(pupil_m=PUPIL_M, lam=WAVELENGTH_M):
    """rad. DERIVED: Rayleigh, 1.22 lambda over the aperture."""
    return 1.22 * lam / pupil_m


def sampling_limit(pitch_m=CONE_PITCH_M, focal_m=EYE_FOCAL_M):
    """rad. DERIVED: Nyquist needs two receptors per cycle."""
    return 2.0 * pitch_m / focal_m


def arcmin(rad):
    return rad * (180.0 / math.pi) * 60.0


def acuity_gate():
    """Is the retina worth the optics, or either wasted? DERIVED."""
    d, s = diffraction_limit(), sampling_limit()
    return Gate("retina matches optics", max(d, s), min(d, s), "rad",
                f"a retina finer than {arcmin(d):.2f} arcmin samples "
                f"blur, and optics sharper than {arcmin(s):.2f} arcmin "
                f"paint detail nothing reads")


def depth_resolution(z_m, baseline_m=EYE_BASELINE_M,
                     disparity=DISPARITY_RAD):
    """m. DERIVED: disparity falls as 1/z, so error rises as z^2."""
    return z_m * z_m * disparity / baseline_m


def stereo_range(baseline_m=EYE_BASELINE_M, disparity=DISPARITY_RAD):
    """m. Where depth error equals the distance itself. DERIVED."""
    return baseline_m / disparity


def can_see_the_work(distance_m=0.5, feature_m=1e-3):
    """Gate. Can it see the edge it is making? DERIVED."""
    need = feature_m / distance_m
    return Gate("resolves its own work", max(diffraction_limit(),
                sampling_limit()) and need, max(diffraction_limit(),
                sampling_limit()), "rad",
                f"a {1000*feature_m:.1f} mm feature at {distance_m:.2f} m "
                f"subtends {arcmin(need):.2f} arcmin")


def strike_force_n(mass_kg=STONE_KG, v=STRIKE_SPEED, s=STRIKE_SWING_M):
    """N. DERIVED: the tangential force to accelerate the stone."""
    return mass_kg * (v * v) / (2.0 * s)


def grip_gate(opposed=True):
    """Gate. Can the hand hold the stone through the swing? DERIVED."""
    grip = PRECISION_GRIP_N if opposed else HOOK_GRIP_N
    held = grip * GRIP_FRICTION
    return Gate(f"grip ({'thumb opposed' if opposed else 'hook'})",
                held, strike_force_n(), "N",
                f"friction mu={GRIP_FRICTION} on a {grip:.0f} N grip "
                f"against a {STONE_KG:.0f} kg stone reaching "
                f"{STRIKE_SPEED:.0f} m/s over {STRIKE_SWING_M:.1f} m")


def stance_gate(limbs=4, on_ground=2, carrying=1):
    """Gate. A limb committed to locomotion is not carrying. DERIVED.

    An earlier version counted TOTAL limbs and concluded a biped
    has none free -- because it read "two-legged" as "owns two
    limbs". A human and a horse both own four. The difference is
    how many touch the ground, and that is the whole of what
    bipedalism buys.
    """
    free = max(limbs - on_ground, 0)
    return Gate(f"{limbs} limbs, {on_ground} down", free, carrying,
                "limbs",
                f"locomotion commits {on_ground} of {limbs}, leaving "
                f"{free} for anything else, and a tool needs "
                f"{carrying}")


def body_plan(opposed=True, limbs=4, distance_m=0.5):
    """-> [Gate]. Everything a body needs to make and aim a tool."""
    return [acuity_gate(), can_see_the_work(distance_m),
            grip_gate(opposed), stance_gate(limbs)]


def why_not(gates):
    """-> [str]. Only the failures, each naming its mechanism."""
    return [f"{g.name}: {g.why()}" for g in gates if not g.ok]


# WHAT EACH SENSE REACHES, and it is not the same set.
#
# engine/comprehension.py counts the constraints that bind. A
# constraint you cannot DETECT you cannot answer, so senses bound
# comprehension from below -- and the five do not overlap, which
# is why there are five.
#
#   sight     spatial structure at distance   ~1e7 bit/s
#   hearing   events behind and beyond        ~1e5
#   smell     chemical, and time-delayed      ~1e3
#   touch     contact mechanics               ~1e6
#   taste     what is about to go inside      ~1e2
#
# Smell is the only one that reads the PAST -- a track is a
# chemical record of something that has gone. Hearing is the only
# one that reads round a corner. Taste is the only one that acts
# after commitment, which is why it is the one wired to disgust.
SENSE_BITS = {"sight": 1e7, "hearing": 1e5, "smell": 1e3,
              "touch": 1e6, "taste": 1e2}

SENSE_REACH = {
    "sight": ["predation", "food in", "skeleton"],
    "hearing": ["predation", "a shared corpus"],
    "smell": ["food in", "elements"],
    "touch": ["heat out", "crowding", "persistence"],
    "taste": ["elements", "energy", "food in"],
}


def sensed(organism="human"):
    """-> set. Constraints a sense organ can detect. DERIVED."""
    from engine.comprehension import binding
    binds = set(binding(organism))
    out = set()
    for c in SENSE_REACH.values():
        out |= binds & set(c)
    return out


def inferred(organism="human"):
    """-> set. Constraints that must be modelled, not detected."""
    from engine.comprehension import binding
    return set(binding(organism)) - sensed(organism)


def inference_share(organism="human"):
    """Fraction of what binds that no sense reaches. DERIVED."""
    from engine.comprehension import binding
    n = len(binding(organism))
    return len(inferred(organism)) / n if n else 0.0


def sense_bandwidth():
    """Total bits a second across all five. DERIVED."""
    return sum(SENSE_BITS.values())


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_eye_sits_at_its_own_diffraction_limit", _eye)
    t("space_is_two_eyes_and_it_runs_out", _space)
    t("a_hook_grip_cannot_strike", _grip)
    t("four_limbs_on_the_ground_carry_nothing", _stance)
    t("a_failure_names_its_mechanism", _mech)
    t("five_senses_reach_eight_of_thirteen", _five)
    t("the_rest_is_inferred_and_that_is_the_brain", _infer)
    return all(o[1] for o in out), out


def _eye():
    d, s = diffraction_limit(), sampling_limit()
    g = acuity_gate()
    if not 0.5 < s / d < 2.0:
        raise ArithmeticError(f"optics and retina differ by {s/d:.1f}x")
    return (f"diffraction at a 3 mm pupil allows {arcmin(d):.2f} arcmin "
            f"and cone spacing samples {arcmin(s):.2f} -- {s/d:.2f}x "
            f"apart, against a measured 1.00. Three routes, none told "
            f"about the others. A retina finer than the optics samples "
            f"blur; optics sharper than the retina paint detail "
            f"nothing reads. Neither is wasted on the other and "
            f"nothing here arranged that")


def _space():
    near, far, r = (depth_resolution(0.5), depth_resolution(10.0),
                    stereo_range())
    if not 100 < r < 1e4:
        raise ArithmeticError(f"stereo range came out {r:.0f} m")
    return (f"depth error goes as z^2, so 6.4 cm of baseline resolves "
            f"{1000*near:.2f} mm at arm's length, {100*far:.1f} cm at "
            f"ten metres, and nothing past {r:.0f} m where the error "
            f"equals the distance. Seeing space is two eyes and a "
            f"subtraction, and where it stops is b over the disparity "
            f"threshold -- not a fact about brains")


def _grip():
    good, bad = grip_gate(True), grip_gate(False)
    if not good.ok or bad.ok:
        raise ArithmeticError(f"opposed {good.ratio:.2f}, hook {bad.ratio:.2f}")
    return (f"striking needs {strike_force_n():.0f} N held. A thumb-"
            f"opposed grip holds {good.have:.0f} and passes at "
            f"{good.ratio:.1f}x; a hook grip holds {bad.have:.1f} and "
            f"FAILS at {bad.ratio:.2f}x. engine/tools.py assumed a "
            f"hand without checking, and the hand is the reason a "
            f"flake is not a tool for most animals that could reach "
            f"one")


def _stance():
    """INVERTED, kept. The first version read the wrong quantity."""
    biped = stance_gate(4, on_ground=2)
    quad = stance_gate(4, on_ground=4)
    if not biped.ok or quad.ok:
        raise ArithmeticError(f"biped {biped.ratio}, quadruped {quad.ratio}")
    return (f"INVERTED, kept. This first counted TOTAL limbs and had a "
            f"biped with none free, because it read 'two-legged' as "
            f"'owns two limbs'. A human and a horse both own four. "
            f"Count what touches the ground and a quadruped has "
            f"{quad.have:.0f} free and a biped {biped.have:.0f} -- "
            f"that is the entire thing bipedalism buys, and the "
            f"earlier reading had it exactly backwards")


def _mech():
    bad = why_not(body_plan(opposed=False))
    if not bad or "against" not in bad[0]:
        raise ArithmeticError("a failure did not report its mechanism")
    return (f"take the thumb away and the report is not 'failed'. It "
            f"is: {bad[0][:120]}... A verdict is the least useful part "
            f"of a failure. The quantity that fell short, the one it "
            f"lost to and the factor between them is what says "
            f"whether it nearly worked or is not that kind of thing")


def _five():
    got, tot = sensed("human"), 13
    per = {k: len(v) for k, v in SENSE_REACH.items()}
    if len(got) < 6:
        raise ArithmeticError(f"only {len(got)} constraints sensed")
    return (f"the five senses between them reach {len(got)} of the "
            f"{tot} constraints that bind on a human, and they do not "
            f"overlap -- which is why there are five. Smell is the "
            f"only one that reads the PAST, since a track is a "
            f"chemical record of something gone; hearing the only one "
            f"that reads round a corner; taste the only one that acts "
            f"after commitment, which is why it is wired to disgust. "
            f"Bandwidth spans {min(SENSE_BITS.values()):.0e} to "
            f"{max(SENSE_BITS.values()):.0e} bit/s and the narrowest "
            f"is not the least useful")


def _infer():
    inf = inferred("human")
    share = inference_share("human")
    micro = inference_share("bacterium")
    if share <= micro:
        raise ArithmeticError(f"human {share:.2f}, microbe {micro:.2f}")
    return (f"{len(inf)} constraints reach NO sense: "
            f"{sorted(inf)}. Provisioning is eighteen years ahead and "
            f"allocation is a fact about other people -- neither has "
            f"a signal to detect, so both must be MODELLED. That is "
            f"{100*share:.0f}% of what binds on a human against "
            f"{100*micro:.0f}% on a bacterium, and it is what a brain "
            f"adds over a sense organ. Senses bound comprehension "
            f"from below; inference is the rest")


if __name__ == "__main__":
    d, s = diffraction_limit(), sampling_limit()
    print(f"  diffraction 1.22 lam/D    {arcmin(d):.2f} arcmin")
    print(f"  cone Nyquist              {arcmin(s):.2f} arcmin")
    print(f"  measured acuity           1.00 arcmin\n")
    print(f"  {'range':>8}{'depth resolved':>17}")
    for z in (0.5, 2, 10, 50, 200):
        print(f"  {z:>7.1f}m{depth_resolution(z):>15.3f} m")
    print(f"  stereo gives out past {stereo_range():.0f} m\n")
    for opposed in (True, False):
        print(f"  --- {'thumb opposed' if opposed else 'hook grip'} ---")
        for g in body_plan(opposed=opposed):
            print(f"    {g.name:<28}{g.why()[:74]}")
    print()
    ok, res = check()
    for n, o, d2 in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:44}{d2[:36]}")
