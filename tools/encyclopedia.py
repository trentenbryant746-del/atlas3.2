"""Their encyclopedia, translated.

The first version of this file wrote the encyclopedia in
English, and the English was mine -- every phrase came from a
description I had typed into engine/artifact.py. That is us
writing their record for them and then admiring it.

So the entries are now THEIRS. A band coins a token when it
first makes something, out of a phoneme inventory and nothing
else, and its name for a thing of several crafts is those
tokens run together. Nobody was handed English.

We can still read it, for one reason: we watched them attach
each word to an act of making, and the ledger has both. The
gloss is an OBSERVATION, in the position a field linguist is in
-- point at the thing, write down the noise. It is not a
dictionary anybody was given.

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
    from engine.world import (run, describe, spec, their_entry,
                              words_for)
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
    L += ["```", "", "## Their words for the crafts", "",
          "A band coins a token when it first makes something. A "
          "band that is TAUGHT something learns the word with it, "
          "so a craft everybody found separately has a word per "
          "band and a craft that spread by teaching has one word "
          "that travelled. The oldest words are the least agreed "
          "on.", "", "```",
          f"{'craft':<16}{'words':>7}{'bands':>7}   band 0 calls it"]
    for p in sorted(PRIMITIVES, key=lambda x: w.first_seen().get(x, 0)):
        d, h = words_for(p, w)
        if not h:
            continue
        mine = w.bands[0].lex.word.get(p, "-")
        L.append(f"{p:<16}{d:>7}{h:>7}   {mine}")
    L += ["```", "", "## The things, in the order they were made",
          "",
          "Each entry is headed by what a band that made it calls "
          "it, in its own words. The gloss under it is ours, and "
          "it is a translation rather than the original.", ""]
    for c in arts:
        sheet = spec(c, w)
        _y, who = sheet["first built"] or (0, 0)
        theirs = their_entry(c, who, w)
        named = sheet["named in our world"]
        head = theirs or " + ".join(sorted(c))
        L.append(f"### {head}")
        L.append("")
        if named:
            L.append(f"*Our world calls this {named}.*")
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
