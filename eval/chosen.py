"""Every number somebody picked, and whether it had to be picked.

A CHOSEN constant is an admission: the rule above it is only as
good as a judgement call underneath it. This file counts them,
says which are load-bearing, and -- the part that turned out to
matter -- checks whether any two of them imply rates that
disagree.

Two constants in different modules can each look reasonable and
together be impossible. Nothing in this repository was comparing
them, because the fingerprint gate recomputes CLAIMS and a
consistency relation between two free parameters is not a claim
anybody had written down.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHOSEN_RE = re.compile(r"^([A-Z_][A-Z_0-9]*)\s*=\s*([^#]+?)\s*#\s*CHOSEN(.*)$")

# Constants whose value sets a PUBLISHED number. Named here so the
# list cannot quietly go stale: each entry says what moves.
LOAD_BEARING = {
    "YIELD_PER_SKILL": "the intricacy fixed point and half the "
                       "per-capita exponent",
    "TELEPHONE": "specialization depth and the whole oral stock",
    "PRECISION_EXPONENT": "the inference kit price and its "
                          "indivisibility",
    "DAYS_PER_PART": "the 24% of specialists priced out by tools",
    "EDIBLE_FRACTION": "forager range and the 909x defensibility",
    "TRIALS_PER_HEAD_YEAR": "the novel fraction, and see below",
    "PROOF_CATCH": "how many speakers a checked copy is worth",
    "SURPLUS_RATIO": "the literacy ceiling",
    "COPIES_PER_YEAR": "the corpus, and the press lever",
}

# Constants that USED to be chosen and are now derived. Kept so the
# progress is visible and so a regression is obvious.
NOW_DERIVED = {
    "FIRE_EFFICIENCY": ("disease.fire_efficiency",
                        "r^2/(4h^2): a pot subtends that much of a "
                        "point source radiating into 4 pi. 0.09, "
                        "against 0.10 picked"),
    "WALL_ADVANTAGE": ("power.wall_advantage",
                       "attackers enter a breach w wide at frontage "
                       "d, so w/d engage; defenders hold three sides "
                       "of the same opening, so 3w/d do. The width "
                       "cancels and the answer is 3 whatever the "
                       "breach"),
}


def scan():
    """-> {module: [(name, value, comment)]}. Read from source."""
    out = {}
    for path in sorted((ROOT / "engine").glob("*.py")):
        rows = []
        for line in path.read_text().splitlines():
            m = CHOSEN_RE.match(line.strip())
            if m:
                rows.append((m.group(1), m.group(2).strip(),
                             m.group(3).strip(" ,")))
        if rows:
            out[path.stem] = rows
    return out


def count():
    """-> (constants, modules). DERIVED."""
    got = scan()
    return sum(len(v) for v in got.values()), len(got)


def load_bearing_present():
    """Which load-bearing names are still chosen. DERIVED."""
    names = {n for rows in scan().values() for n, _v, _c in rows}
    return sorted(names & set(LOAD_BEARING))


def novelty_rate_per_band():
    """New designs a band produces in a year, from novelty.py."""
    from engine.novelty import novel_total
    from engine.tradition import BAND
    return novel_total(float(BAND))


def diffusion_rate_per_band():
    """The accident rate tradition.py's diffusion result uses.

    It used to be the literal 1/500 written inside two checks.
    That was the other half of the 8.5x disagreement this file
    found, and engine/tradition.accident_rate now DERIVES it from
    engine/novelty.py instead. There is one number where there
    were two.
    """
    from engine.tradition import accident_rate
    return accident_rate()


def rate_disagreement():
    """How far apart the two independent guesses are. DERIVED."""
    a, b = novelty_rate_per_band(), diffusion_rate_per_band()
    return a / b


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("every_chosen_number_is_counted_and_located", _count)
    t("two_of_them_stopped_being_chosen", _derived)
    t("INVERTED_two_free_numbers_imply_rates_that_disagree", _rates)
    t("INVERTED_the_load_bearing_ones_are_still_chosen", _load)
    return all(x for _, x, _ in res), res


def _count():
    n, mods = count()
    if n < 10:
        raise ArithmeticError(f"only {n} found; the scan is broken")
    biggest = sorted(scan().items(), key=lambda kv: -len(kv[1]))[:3]
    return (f"{n} constants across {mods} modules carry a CHOSEN "
            f"tag, which is an admission that the rule above each "
            f"is only as good as a judgement underneath it. The "
            f"densest are "
            + ", ".join(f"{m} ({len(r)})" for m, r in biggest)
            + f". They are counted by scanning source for the tag "
              f"rather than from a list, so a constant cannot be "
              f"chosen without appearing here")


def _derived():
    from engine.disease import fire_efficiency
    from engine.power import wall_advantage
    f, w = fire_efficiency(), wall_advantage()
    if not (0.05 < f < 0.15) or w != 3.0:
        raise ArithmeticError(f"{f} {w}")
    return (f"two constants stopped being chosen and both went to "
            f"GEOMETRY rather than to measurement. A fire is near "
            f"a point source radiating into 4 pi and a pot of "
            f"radius r at height h intercepts r^2/(4h^2) of it: "
            f"{f:.3f}, against the 0.10 that had been picked -- so "
            f"what an open fire wastes is solid angle, not "
            f"incomplete combustion. And a wall forces attackers "
            f"through a breach where only w/d engage while "
            f"defenders hold three sides of it, so the ratio is "
            f"{w:.0f} and the breach width CANCELS, which is why it "
            f"was right to be a ratio. Neither needed a judgement "
            f"call and both had one")


def _rates():
    """The disagreement this file was built to find, now closed.

    It stays as a check rather than being deleted, because the
    thing worth verifying is that there is ONE SOURCE -- not that
    two numbers happen to match.
    """
    a, b, r = (novelty_rate_per_band(), diffusion_rate_per_band(),
               rate_disagreement())
    if abs(r - 1.0) > 1e-9:
        raise ArithmeticError(
            f"{a:.3e} against {b:.3e}, {r:.2f}x apart -- two "
            f"numbers for one quantity again")
    return (f"this file was built to find a disagreement and it "
            f"found one: engine/novelty.py had a band of 28 making "
            f"{a:.2e} new designs a year, built from trials times "
            f"a novel fraction over a team size, while "
            f"engine/tradition.py assumed {1/500:.4f} per "
            f"band-year as a round number inside two checks. The "
            f"SAME QUANTITY from two directions, 8.5x apart, with "
            f"nothing comparing them because the fingerprint gate "
            f"recomputes claims and a consistency relation between "
            f"two free parameters is not a claim anybody wrote. It "
            f"is closed by DERIVATION and not by tuning: "
            f"tradition.accident_rate now calls novelty, so there "
            f"is one source where there were two. The check "
            f"remains and now fails if a second source ever "
            f"reappears -- and deriving it flipped a result, "
            f"because at the true rate a 40-band network settles a "
            f"discovery SLOWER than one band alone")


def _load():
    """INVERTED. Fails when nothing load-bearing is still chosen."""
    still = load_bearing_present()
    if not still:
        raise ArithmeticError(
            "no load-bearing constant is chosen any more, which "
            "would be excellent and should be verified rather than "
            "believed")
    return (f"{len(still)} of the {len(LOAD_BEARING)} constants "
            f"known to set a published number are still picked: "
            + "; ".join(f"{n} -> {LOAD_BEARING[n]}" for n in still[:4])
            + f" and {max(0, len(still)-4)} more. Every one of them "
              f"is a number a reader should be able to disagree "
              f"with, and the published figures move when they do. "
              f"The list is checked against the source scan, so a "
              f"constant cannot be quietly promoted")


if __name__ == "__main__":
    got = scan()
    for mod, rows in got.items():
        for name, val, comment in rows:
            flag = "  <- load-bearing" if name in LOAD_BEARING else ""
            print(f"  {mod+'.'+name:<38}{val:<12}{comment}{flag}")
    n, mods = count()
    print(f"\n  {n} chosen across {mods} modules; "
          f"{len(NOW_DERIVED)} since derived\n")
    ok, res = check()
    for n_, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n_}\n        {m}")
    print("  all hold" if ok else "  broken")
