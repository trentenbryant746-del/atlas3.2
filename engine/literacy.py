"""Writing is a skill, and at first almost nobody has it.

engine/craft.py ended by saying the cheap lever on specialization
depth is a better channel, and named writing. That was a promise,
not a derivation. Here is what writing actually changes, and it is
not "people can write things down".

THE EXEMPLAR IS A CHECK. A speaker has nothing to compare their
telling against -- the source is gone the moment it is spoken, so
the only correction available is other people, and you need a lot
of them. A copyist has the original sitting there. They can read
back and compare, glyph by glyph, as many times as they like.

Writing is the first channel on this chain where a claim carries
the thing that would catch it being wrong. That is the whole
advantage, and it is why ONE literate person can beat thirteen
speakers.

But it bootstraps orally. You cannot learn to read from a book you
cannot read yet, so literacy itself is transmitted through the
lossy channel, held by however few people hold it -- which means
it can be LOST, and the threshold for losing it is computable.
"""

import math

from engine.tradition import BAND, TELEPHONE, garbles, oral_capacity

COPY_SLIP = TELEPHONE       # a scribe slips as often as a speaker
PROOF_CATCH = 0.90          # CHOSEN, one read-back catches nine in ten
GENERATION_YEARS = 25.0     # CHOSEN
TAUGHT_PER_LIFE = 4.0       # CHOSEN, pupils one literate can carry


def copy_error(passes=1):
    """Residual error after proofreading against the exemplar."""
    return COPY_SLIP * (1.0 - PROOF_CATCH) ** max(int(passes), 0)


def equivalent_voices(passes=1, band=BAND):
    """How many speakers one checked copy is worth. DERIVED."""
    want = copy_error(passes)
    for k in range(1, band * 8):
        if garbles(k) <= want:
            return k
    return None


def written_depth(passes=2, band=BAND):
    """-> (k, s). Specialties a band can hold once it writes."""
    from engine.craft import best_depth
    return best_depth(band, copy_error(passes))[:2]


# --- who can read ---------------------------------------------------
#
# Literacy is one specialty among the others, so it lives or dies
# by the same consensus arithmetic as any other -- except that it
# cannot be written down for its own transmission.


def literacy_halflife(holders):
    """Generations until a script is half lost. DERIVED."""
    g = garbles(holders)
    return math.inf if g <= 0 else math.log(2) / -math.log(1.0 - g)


def literacy_survives(holders, generations=40):
    """Is the script still here? DERIVED."""
    return (1.0 - garbles(holders)) ** generations >= 0.5


def least_scribes(generations=40, band=BAND):
    """Fewest holders that keep a script. DERIVED."""
    for k in range(1, band * 8):
        if literacy_survives(k, generations):
            return k
    return None


def _phase(f):
    """The conserved quantity of df/dt = r f^2 (1-f). Monotone."""
    return math.log(f / (1.0 - f)) - 1.0 / f


def spread(f0, years):
    """Literate fraction after `years`. DERIVED.

    NOT plain logistic. Nobody learns to read because reading
    exists -- they learn because there is something written and
    someone to read it to, and that is the f**2 in usefulness().
    So the growth rate is proportional to the VALUE, not to the
    number of teachers:

        df/dt = r * f**2 * (1 - f)

    which has the conserved quantity ln(f/(1-f)) - 1/f. Inverting
    a monotone closed form is not a search.
    """
    r = math.log(TAUGHT_PER_LIFE) / GENERATION_YEARS
    want = _phase(f0) + r * years
    lo, hi = 1e-12, 1.0 - 1e-12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _phase(mid) < want:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def usefulness(f):
    """Value of the written channel at literate fraction f.

    A written item needs a writer AND a reader, so the pairs that
    the channel can serve go as f**2. It is not linear, which is
    why writing looks useless for a long time and then does not.
    """
    return f * f


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_exemplar_is_the_check_and_that_is_the_advantage", _check)
    t("writing_buys_the_specialties_the_band_could_not_hold", _depth)
    t("a_script_with_too_few_scribes_is_lost", _lost)
    t("writing_is_worth_the_square_of_who_can_read", _square)
    return all(x for _, x, _ in res), res


def _check():
    one, two, three = (equivalent_voices(1), equivalent_voices(2),
                       equivalent_voices(3))
    if not (one and two and three) or three <= one:
        raise ArithmeticError(f"{one} {two} {three}")
    return (f"a speaker cannot compare their telling to anything -- "
            f"the source is gone as it is spoken, so the only "
            f"correction is other people. A copyist has the original "
            f"in front of them. One read-back at {PROOF_CATCH} catch "
            f"takes a {COPY_SLIP} slip to {copy_error(1):.3f}, worth "
            f"{one} speakers; two passes {copy_error(2):.4f}, worth "
            f"{two}; three, worth {three} -- the whole "
            f"specialization depth of a band, from one person. "
            f"Writing is the first channel here where a claim "
            f"carries the thing that would catch it being wrong")


def _depth():
    from engine.craft import best_depth
    ok, os_ = best_depth()[:2]
    wk, ws = written_depth(2)
    if ws <= os_:
        raise ArithmeticError(f"{ws} <= {os_}")
    return (f"engine/craft.py bottomed out at {os_} specialties {ok} "
            f"deep, because every specialty steals voices from the "
            f"consensus that was correcting the telephone. A checked "
            f"copy does not need voices. At {copy_error(2):.4f} the "
            f"same {BAND} people hold {ws} specialties {wk} deep -- "
            f"{ws/os_:.1f}x the skills, with nobody added. This is "
            f"the lever craft.py named and did not price")


def _lost():
    need = least_scribes()
    h1, h3, hn = (literacy_halflife(1), literacy_halflife(3),
                  literacy_halflife(need))
    if need is None or need <= 1:
        raise ArithmeticError(f"{need}")
    return (f"you cannot learn to read from a book you cannot read, "
            f"so literacy bootstraps through the LOSSY channel and "
            f"is subject to the same consensus arithmetic as any "
            f"other skill. One scribe: half-life {h1:.1f} "
            f"generations. Three: {h3:.0f}. It takes {need} holders "
            f"to keep a script {40} generations ({hn:.0f} half-life), "
            f"and a band of {BAND} that spares {need} for writing has "
            f"spent a fifth of itself on a skill that feeds nobody. "
            f"A script is not lost to catastrophe. It is lost to "
            f"being held by too few people")


def _square():
    f0 = 1.0 / BAND
    pts = [(y, spread(f0, y)) for y in (0, 500, 2000, 5000)]
    early = usefulness(pts[1][1]) / usefulness(pts[0][1])
    late = usefulness(pts[3][1]) / usefulness(pts[2][1])
    if late >= early:
        raise ArithmeticError("no acceleration to explain")
    rows = "; ".join(f"{y}y {100*f:.0f}% -> {usefulness(f):.3f}"
                     for y, f in pts)
    return (f"a written item needs a writer AND a reader, so the "
            f"channel serves f**2 of the possible pairs, not f. "
            f"Starting from one literate in {BAND}: {rows}. Value "
            f"multiplies {early:.0f}x over the first {pts[1][0]} "
            f"years and only {late:.1f}x over the last "
            f"{pts[3][0]-pts[2][0]}. Growth is proportional to the "
            f"VALUE, not to the number of teachers -- nobody learns "
            f"to read because reading exists -- so df/dt = r f^2 "
            f"(1-f) and the thing crawls for millennia. Which is why "
            f"writing "
            f"looks like an expensive hobby for so long and then "
            f"stops looking like one. Nothing about the technology "
            f"changed -- the exponent did the work")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
