"""Why a band is slow, and what the slowness buys.

Two rules that look unrelated and are the same rule.

  PACE    a band moves at its slowest member, so it spends longer
          on the same ground. Hazards are charged by the DAY and
          forage is collected by the KILOMETRE, so going slowly
          does not reduce the problems -- it multiplies them per
          unit of ground. A band therefore meets more trouble
          than a lone adult covering the same country, and has
          more heads to meet it with, and a corpus to keep the
          answer in. Slowness is not the price of company. It is
          the input to the only process here that accumulates.

  SKILL   not everyone has to hold everything. Splitting the band
          into specialties multiplies what it can carry by the
          number of specialties, and divides the number of people
          holding each one -- which is exactly the number that
          was correcting the telephone. So specialization trades
          breadth against fidelity, and the trade has a bottom.
"""

import math

from engine.tradition import BAND, TELEPHONE, garbles, oral_capacity

# --- PACE -----------------------------------------------------------
#
# Walking is an inverted pendulum. The speed at a given Froude
# number goes as sqrt(g*L), so pace is set by leg length and
# nothing else -- which is why the band's pace is the child's and
# why the ratio is a square root, not a preference.
FROUDE = 0.25               # walk, before the run transition
GRAVITY = 9.81
LEG = {"adult": 0.90, "four-year-old": 0.45, "elder": 0.85}


def walk_speed(leg_m):
    """m/s at the walk. DERIVED: inverted pendulum."""
    return math.sqrt(FROUDE * GRAVITY * leg_m)


def band_pace():
    """m/s. The band moves at its slowest walker. DERIVED."""
    return min(walk_speed(L) for L in LEG.values())


def slowdown():
    """How much longer the same ground takes. DERIVED."""
    return walk_speed(LEG["adult"]) / band_pace()


def problems_per_km(pace):
    """Hazards are per-day, ground is per-km, so they divide."""
    return 1.0 / pace


def kept_innovations_ratio(heads=BAND, q=1e-3):
    """Band over lone adult, per km of ground. DERIVED.

    q is the chance one head solves one problem. It cancels to
    first order -- 1-(1-q)^m over q tends to m -- so the ratio
    does not depend on the number nobody has measured.
    """
    solved = (1.0 - (1.0 - q) ** heads) / q
    return slowdown() * solved


# --- SKILL ----------------------------------------------------------
#
# s specialties, k = BAND/s holders each. The band can carry s
# times one head's capacity, and each specialty is corrected by
# only k voices instead of all 28.
#
#   held(k) = (BAND/k) * a / (1 - untold * (1 - garbles(k)))
#
# k is a count of people, so there are 28 candidates and no more.
# Evaluating a closed form at every point of a bounded integer
# domain is arithmetic, not a search: there is nothing underneath
# this that has not been found.


def specialties(k, band=BAND):
    """How many distinct skills k-deep redundancy affords."""
    return band // max(int(k), 1)


def held_by_band(k, band=BAND, e=TELEPHONE):
    """Equilibrium items the whole band carries. DERIVED."""
    untold = 1.0 - 1.0 / oral_capacity()
    r = untold * (1.0 - garbles(k, e))
    return specialties(k, band) / (1.0 - r)


_DEPTH = {}


def best_depth(band=BAND, e=TELEPHONE):
    """-> (k, s, held). Exhaustive over 1..band. DERIVED.

    Pure in (band, e) and scanned over every integer up to band,
    so a village-scale call is 912 binomial tails and a network
    one is 36,480. engine/intricacy.settle iterates a fixed point
    that calls this forty times with the same arguments, which is
    forty identical scans. Held.
    """
    key = (int(band), float(e))
    if key in _DEPTH:
        return _DEPTH[key]
    best = max(range(1, int(band) + 1),
               key=lambda k: held_by_band(k, band, e))
    got = (best, specialties(best, band), held_by_band(best, band, e))
    _DEPTH[key] = got
    return got


def band_for_specialties(s, e=TELEPHONE, cap=4000):
    """Smallest band that beats holding everything, at s skills."""
    n = s
    while n <= cap:
        k, got, _ = best_depth(n, e)
        if got >= s:
            return n, k
        n += 1
    return None, None


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_band_walks_at_its_shortest_legs", _pace)
    t("slowness_is_what_supplies_the_problems", _slow)
    t("specialization_is_bounded_by_the_telephone", _depth)
    t("more_skills_needs_a_bigger_band_or_a_better_channel", _more)
    return all(x for _, x, _ in res), res


def _pace():
    a, b = walk_speed(LEG["adult"]), band_pace()
    if b >= a:
        raise ArithmeticError(f"{b} >= {a}")
    return (f"walking is an inverted pendulum, so speed goes as "
            f"sqrt(g*L) and pace is leg length and nothing else. "
            f"Adult {a:.2f} m/s ({3.6*a:.1f} km/h), four-year-old "
            f"{b:.2f} m/s ({3.6*b:.1f} km/h). The band moves at the "
            f"child, so the ratio is sqrt(0.45/0.90) = "
            f"{1/slowdown():.3f} -- a square root, not a preference, "
            f"and the 18-year provisioning span of "
            f"engine/comprehension is why a child is there at all")


def _slow():
    r = kept_innovations_ratio()
    if r <= slowdown():
        raise ArithmeticError(f"{r}")
    return (f"hazards are charged by the day and forage is "
            f"collected by the kilometre, so a band at "
            f"{1/slowdown():.3f} of adult pace meets "
            f"{slowdown():.2f}x the trouble per km -- slowness does "
            f"not avoid problems, it concentrates them. And it "
            f"brings {BAND} heads to them instead of one, so kept "
            f"innovations per km run {r:.0f}x a lone adult. The "
            f"per-head solve rate cancels: (1-(1-q)^m)/q -> m. "
            f"Slowness is not the price of company, it is the input "
            f"to the only thing here that accumulates")


def _depth():
    k, s, got = best_depth()
    alone, thin = held_by_band(BAND), held_by_band(1)
    if s < 2 or got <= alone or got <= thin:
        raise ArithmeticError(f"k={k} s={s} {got} vs {alone} / {thin}")
    return (f"s specialties means BAND/s holders each, and those "
            f"holders were the votes correcting the telephone. "
            f"Breadth multiplies by s, fidelity divides by it. The "
            f"trade bottoms out at {k} holders and {s} specialties, "
            f"carrying {got:.0f}a -- against {alone:.0f}a if all "
            f"{BAND} hold one corpus, and {thin:.0f}a if all {BAND} "
            f"specialize alone, where every skill dies with the one "
            f"who knows it. {got/thin:.0f}x. How specialized a band "
            f"can be is not set by how many useful skills exist")


def _more():
    k, s, _ = best_depth()
    want = s + 4
    n, kk = band_for_specialties(want)
    better = 0.01
    k2, s2, _ = best_depth(BAND, better)
    if n is None or n <= BAND or s2 <= s:
        raise ArithmeticError(f"{n} / {s2}")
    return (f"to hold {want} skills instead of {s}, either the band "
            f"grows to {n} ({kk} deep) or the channel improves: drop "
            f"the telephone from {TELEPHONE} to {better} and the "
            f"same {BAND} people carry {s2} specialties at {k2} "
            f"deep. Specialization depth is transmission fidelity "
            f"and headcount, in that order. Writing is the second "
            f"lever and it is the cheap one, which is the whole "
            f"reason it is worth inventing")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
