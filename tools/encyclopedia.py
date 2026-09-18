"""Write out every tool the world made, with what it is made of.

engine/world.py runs and keeps a ledger. This turns the ledger
into something a person reads: one entry per distinct thing
built, in the order the gates allowed them, saying what it is
made of, what fire and cold and precision it costs, what must
already exist, and when it was first made and by whom.

It does NOT say what anything is for. Purpose was tried and
dropped: inferring it from what a band managed next is a
spurious correlation, because a band that builds anything goes
on to manage other things regardless.

    python3 -m tools.encyclopedia            -> paper/tools.md
    python3 -m tools.encyclopedia --html     -> and the html
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "tools.md"
YEARS = 14000.0


def build():
    from engine.world import run, describe, spec
    from engine.artifact import (PRIMITIVES, bootstrap, held_by_round,
                                 tolerance, coldness, bohr_radius)
    w = run(YEARS)
    arts = sorted(w.artifacts(),
                  key=lambda c: (spec(c, w)["first built"] or (0, 0),
                                 len(c), sorted(c)))
    named = w.named()

    L = ["# The tools of one world", "",
         f"Generated {time.strftime('%Y-%m-%d')} from a run of "
         f"engine/world.py: {len(w.bands)} bands over "
         f"{w.year:.0f} years, {len(w.ledger):,} ledger entries, "
         f"{len(arts):,} distinct things built.", "",
         "Nobody in this world can read the rules. Bands hold "
         "crafts, try combinations of what they already have, and "
         "find out about the gates by failing at them. Three "
         "gates decide everything: how hot a fire they can raise, "
         "how cold they can get, and how finely they can place "
         "matter. None of the three is visible to them.", "",
         f"Of the {len(arts):,} things here, {len(named)} have a "
         f"name in our world and {len(arts) - len(named):,} do "
         f"not. The unnamed ones are not errors. They are "
         f"combinations this world's physics permits that ours "
         f"never happened to build.", "",
         "No entry says what a thing is FOR. Purpose was tried "
         "and dropped: inferring it from what a band did next is "
         "a correlation, not a finding.", "",
         "## The three gates", "", "```",
         f"{'round':<7}{'fire':>7}{'cold':>7}{'precision':>12}"
         f"   reached"]
    for i, t, got in bootstrap():
        h = held_by_round(i)
        L.append(f"{i:<7}{t:>6} K{coldness(h):>6.0f} K"
                 f"{tolerance(h):>12.0e}   {', '.join(got)}")
    L += ["```", "",
          f"The precision ladder ends at {bohr_radius():.2e} m, "
          f"the Bohr radius, because matter cannot be placed more "
          f"finely than an atom is wide. That is a wall and not a "
          f"rung.", "",
          "## The crafts", "", "```"]
    for p in sorted(PRIMITIVES, key=lambda x: PRIMITIVES[x][1]):
        needs, k, rule, words = PRIMITIVES[p]
        L.append(f"{p:<16}{words}")
        L.append(f"{'':<16}needs {', '.join(needs) or 'nothing'}"
                 f"  |  {rule}")
    L += ["```", "", f"## The things, in the order they were made",
          ""]
    for c in arts:
        sheet = spec(c, w)
        title = sheet["named in our world"] or " + ".join(sorted(c))
        L.append(f"### {title}")
        L.append("")
        L.append(describe(c, w))
        L.append("")
    return "\n".join(L).rstrip() + "\n"


if __name__ == "__main__":
    text = build()
    OUT.write_text(text)
    print(f"  {OUT.relative_to(ROOT)}  {len(text):,} chars, "
          f"{len(text.splitlines()):,} lines")
    if "--html" in sys.argv:
        from paper.render import render
        html = OUT.with_suffix(".html")
        render(OUT, html, "The tools of one world")
        print(f"  {html.relative_to(ROOT)}  "
              f"{html.stat().st_size:,} bytes")
