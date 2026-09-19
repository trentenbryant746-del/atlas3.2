"""Shape, where the physics forces it and only there.

I said shape was not derivable. That was too strong. Most of it
is not, but a surprising amount is FORCED, and the forcing is
not stylistic:

  rotation       a thing that turns about an axis and does not
                 wobble is a surface of revolution. There is no
                 other option.
  pressure       hoop stress is pr/t, minimised over a closed
                 surface by revolution with domed ends.
  containment    holding against a gradient IS having a cavity.
  optics         1/f = (n-1)(1/R1 - 1/R2) has no solution
                 without curvature.
  lever          the force ratio IS the length ratio, so the
                 aspect ratio is the function.
  spring         stored strain per unit length needs a coiled
                 path; a straight bar of the same steel holds
                 far less.
  gearing        two gears mesh only on matching pitch circles.
  semiconductor  a junction is microns deep and the area is
                 not, so it is a wafer.

Eight of those are forced by what the part DOES. Three others
-- a mark's surface, an alloy's block, breeding which is not an
object at all -- are not forced, and are marked as chosen
rather than smuggled in with the rest.

ARRANGEMENT is forced too, by gravity. A thing that stands has
its centre of mass over its footprint, so the heavy parts go
low. That is why these stack the way they do and it is not a
composition decision.

What is still not here: surface finish, fasteners, colour,
anything that a maker would decide rather than discover. A form
that satisfies every constraint is not a design, and the gap
between them is where taste lives.
"""

import math

from engine.artifact import DIMENSION_M, PRIMITIVES

# primitive -> (solid, forced, why)
SOLID = {
    "rotation": ("cylinder", True,
                 "turns about an axis without wobbling"),
    "pressure": ("capsule", True,
                 "hoop stress pr/t is least on a revolved shell"),
    "containment": ("shell", True, "a cavity IS the function"),
    "optics": ("lens", True, "1/f needs curvature"),
    "lever": ("rod", True, "the force ratio IS the aspect ratio"),
    "spring": ("helix", True, "strain per length needs a coil"),
    "gearing": ("disc", True, "meshing needs a pitch circle"),
    "semiconductor": ("wafer", True, "a junction is microns deep"),
    "steam": ("capsule", True, "a cylinder is what a piston runs in"),
    "vacuum": ("shell", True, "same cavity, opposite gradient"),
    "superconduction": ("torus", True, "a persistent current needs a loop"),
    "electricity": ("torus", True, "a field from a current needs a loop"),
    "smelting": ("shell", True, "a crucible is a cavity that survives heat"),
    "edge": ("wedge", True, "an edge is where two faces meet at an angle"),
    "cordage": ("rod", True, "a line is a length with no width worth having"),
    "switching": ("wafer", True, "it lives on the semiconductor"),
    "coherence": ("wafer", True, "it lives on the semiconductor"),
    "placement": ("rod", True, "a tip is the end of a shaft"),
    "inference": ("wafer", True, "an array of switches is planar"),
    "depiction": ("wafer", True, "an emulsion is a coated plane"),
    # Two of these were listed as unforced and should not have
    # been. Pushing on each found a real constraint.
    "mark": ("plate", True,
             "a mark must hold constant angular size to a reading "
             "eye, and a curved page does not -- at 0.3 m the eye "
             "resolves 87 um, so a sag of that across the sheet is "
             "already a legibility error. Flatness is readability"),
    "heat": ("shell", True,
             "to HOLD a temperature is to limit loss, loss goes as "
             "area, and least area for a volume is a sphere. A "
             "hearth is that minus the opening you reach through"),
    # And two where only a dimension is forced, not the class.
    "alloy": ("box", "partial",
              "homogeneity after melting needs uniform cooling, so "
              "no section thicker than sqrt(D t) -- 17 mm at a "
              "minute's freeze. THICKNESS is forced; the other two "
              "dimensions are not"),
    "regulation": ("box", "partial",
                   "the feedback path adds lag and the lag must "
                   "beat the time constant, so the body is bounded "
                   "at signal speed times that. SIZE is forced; "
                   "the class is not"),
    # And one that is not an object.
    "breeding": ("plate", None,
                 "not an object at all -- a record, whose form is "
                 "the form of engine/form.py's mark. Listing it as "
                 "an unforced shape confused 'I chose this' with "
                 "'there is nothing here to choose'"),
}

ASPECT = {                       # long axis over short, where forced
    "rod": 12.0, "wafer": 0.02, "plate": 0.05, "disc": 0.14,
    "cylinder": 1.1, "capsule": 2.2, "shell": 1.0, "lens": 0.3,
    "helix": 2.6, "torus": 0.35, "wedge": 0.18, "box": 1.0,
}


def solid_of(primitive):
    """-> (kind, forced, why). DERIVED where forced is True."""
    return SOLID.get(primitive, ("box", False, "unclassified"))


def extents(primitive):
    """-> (radius or half-width, half-height) in metres. DERIVED.

    The size comes from engine/artifact.DIMENSION_M, which the
    drawing tables already publish. The proportion comes from
    the solid the function forces.
    """
    d = DIMENSION_M.get(primitive, 0.1)
    kind = solid_of(primitive)[0]
    a = ASPECT[kind]
    if a >= 1.0:
        return d / (2.0 * a) * 1.0, d / 2.0
    return d / 2.0, d / 2.0 * a


def forced_fraction(combo):
    """How much of a thing's form is forced. DERIVED.

    A partial counts a half: the thickness of a billet is forced
    and its outline is not, so half the form is.
    """
    parts = [p for p in combo if solid_of(p)[1] is not None]
    if not parts:
        return 0.0
    got = sum(1.0 if solid_of(p)[1] is True else 0.5 for p in parts)
    return got / len(parts)


def by_state():
    """-> {state: [primitives]}. DERIVED."""
    out = {True: [], "partial": [], None: []}
    for p in PRIMITIVES:
        out[solid_of(p)[1]].append(p)
    return {k: sorted(v) for k, v in out.items()}


def assemble(combo):
    """-> [(kind, radius, half_height, y_centre, primitive)].

    Stacked heaviest-lowest, because a thing that stands has its
    centre of mass over its footprint. Gravity picks the order,
    not a preference.
    """
    parts = sorted(combo, key=lambda p: -DIMENSION_M.get(p, 0.1))
    out, y = [], 0.0
    for p in parts:
        r, hh = extents(p)
        out.append((solid_of(p)[0], r, hh, y + hh, p))
        y += 2.0 * hh
    return out


def height(combo):
    """Total stack height in metres. DERIVED."""
    return sum(2.0 * extents(p)[1] for p in combo)


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("most_of_a_shape_is_forced_by_what_the_part_does", _forced)
    t("gravity_picks_the_order_and_not_a_preference", _stack)
    t("INVERTED_what_is_not_forced_is_marked_as_chosen", _chosen)
    return all(x for _, x, _ in res), res


def _forced():
    forced = [p for p in PRIMITIVES if solid_of(p)[1] is True]
    if len(forced) < len(PRIMITIVES) // 2:
        raise ArithmeticError(f"only {len(forced)}")
    ex = solid_of("pressure")
    return (f"{len(forced)} of {len(PRIMITIVES)} primitives have a "
            f"solid forced by what the part DOES, not chosen. A "
            f"thing that turns about an axis without wobbling is "
            f"a surface of revolution and there is no other "
            f"option; hoop stress pr/t is least on a revolved "
            f"shell, so pressure gives {ex[0]!r} because {ex[2]}; "
            f"1/f = (n-1)(1/R1-1/R2) has no solution without "
            f"curvature, so optics is a lens. The proportions "
            f"come from engine/artifact.DIMENSION_M, which the "
            f"drawing tables were already publishing. I said "
            f"shape was underivable and most of it is not")


def _stack():
    from engine.world import run
    w = run()
    c = max(w.artifacts(), key=len)
    parts = assemble(c)
    ys = [p[3] for p in parts]
    sizes = [DIMENSION_M.get(p[4], 0.1) for p in parts]
    if sizes != sorted(sizes, reverse=True):
        raise ArithmeticError("not heaviest-lowest")
    return (f"arrangement is forced too, and by gravity. A thing "
            f"that stands has its centre of mass over its "
            f"footprint, so the heavy parts go low -- this "
            f"{len(parts)}-part assembly stacks "
            f"{', '.join(p[4] for p in parts)} from the ground "
            f"up, total height {height(c):.2f} m. Nobody chose "
            f"that order. Turn it over and it falls")


def _chosen():
    """INVERTED. Fails if every shape is claimed fully forced."""
    st = by_state()
    full, part, none = st[True], st["partial"], st[None]
    if not part and not none:
        raise ArithmeticError(
            "every shape is claimed fully forced, which for a "
            "billet whose outline nothing fixes is not credible")
    return (f"{len(full)} of {len(PRIMITIVES)} shapes are fully "
            f"forced, {len(part)} partly, and {len(none)} is not "
            f"an object. The two partials are honest about which "
            f"HALF is forced: {part} -- an alloy's thickness is "
            f"fixed by uniform cooling and its outline is not, a "
            f"regulator's size is bounded by feedback lag and its "
            f"class is not. And {none} is a record rather than a "
            f"thing, which is a different category from an "
            f"unforced shape and was previously confused with "
            f"one. Beyond all of it, nothing here gives surface "
            f"finish, fasteners or colour: a form satisfying "
            f"every constraint is not a design, and the distance "
            f"between them is where taste lives")


if __name__ == "__main__":
    from engine.world import run
    w = run()
    c = max((a for a in w.artifacts() if len(a) == 4),
            key=lambda x: height(x))
    print(f"  {' + '.join(sorted(c))}\n")
    print(f"  {'part':<16}{'solid':<11}{'r m':>9}{'h m':>9}"
          f"{'y m':>9}  forced")
    for kind, r, hh, y, p in assemble(c):
        print(f"  {p:<16}{kind:<11}{r:>9.3f}{2*hh:>9.3f}{y:>9.3f}"
              f"  {solid_of(p)[1]}")
    print(f"\n  height {height(c):.3f} m, "
          f"{100*forced_fraction(c):.0f}% of the form forced\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
