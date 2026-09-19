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
                              words_for, drawing_table, render_spec)
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
          "Each entry is headed by what a band that made it "
          "calls it, in its own words. The gloss under it is "
          "ours, a translation rather than the original. Under "
          "that is the drawing: not a picture but a parts "
          "table, which is what an engineering drawing's title "
          "block and schedule actually carry. Their geometry is "
          "ours, so the numbers read straight across.", "",
          "A part marked *process* reaches its accuracy by the "
          "method rather than by measurement -- a lapped lens is "
          "true to a quarter wavelength and nobody ever gauged "
          "one. A part marked *gauge* has a number somebody must "
          "hit, and those are the parts that need a drawing at "
          "all.", "",
          "Below each drawing is the RENDER block: the exact "
          "specification that produced the picture of that "
          "thing. Solids, radii, heights, stacking order, "
          "camera, sun angle and colour, sky, ground albedo, "
          "shadow length and penumbra. Nothing in it is a "
          "preference -- the solids are forced by what each part "
          "does, the order is forced by gravity, and the light "
          "is derived from a 5772 K Sun at one astronomical "
          "unit. Hand the block to any renderer and it makes the "
          "same object under the same sun.", ""]
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
        d = drawing_table(c)
        L.append("```")
        L.append(f"{'part':<16}{'size m':>10}{'held to':>10}"
                 f"{'metres':>11}   how")
        for part, size, tol, absol, how in d["parts"]:
            L.append(f"{part:<16}{size:>10.0e}{tol:>10.0e}"
                     f"{absol:>11.1e}   {how}")
        lo, hi = d["envelope m"]
        L.append(f"{'':16}")
        L.append(f"governing tolerance {d['governing tolerance']:.0e}"
                 f"   finest work {d['finest work m']:.1e} m")
        L.append(f"envelope between {lo:.0e} and {hi:.0e} m"
                 f"   |   {d['gauged parts']} part(s) need gauging")
        L.append("```")
        L.append("")
        r = render_spec(c)
        L.append("```")
        L.append(f"RENDER  {r['image'][0]}x{r['image'][1]} "
                 f"{r['image'][2]}, metres, gamma {r['gamma']}")
        for sol in r["solids"]:
            L.append(f"  {sol['part']:<15}{sol['solid']:<10}"
                     f"r={sol['radius']:<8.4f}"
                     f"h={2*sol['half_height']:<8.4f}"
                     f"y={sol['centre_y']:.4f}")
        cam, sun, sky = r["camera"], r["sun"], r["sky"]
        L.append(f"  height {r['total_height']:.4f} m   "
                 f"widest r {r['widest_radius']:.4f} m   "
                 f"form forced {100*r['form_forced']:.0f}%")
        L.append(f"  camera eye {cam['eye']} look {cam['look_at']} "
                 f"fov {cam['fov_deg']} deg")
        L.append(f"  sun  el {sun['elevation_deg']} az "
                 f"{sun['azimuth_deg']} disc "
                 f"{sun['angular_diameter_deg']} deg  rgb "
                 f"{sun['rgb']}  {sun['irradiance_w_m2']} W/m2")
        L.append(f"  sky  rgb {sky['rgb']} ambient "
                 f"{sky['ambient_fraction']}   ground albedo "
                 f"{r['ground']['albedo']}, plane {r['ground']['plane']}")
        L.append(f"  shadow {r['shadow']['length_m']:.4f} m, "
                 f"penumbra {1000*r['shadow']['penumbra_per_m']:.1f} "
                 f"mm per metre")
        L.append("```")
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
