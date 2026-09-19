"""A bilingual dictionary, theirs to ours and back.

Not a word list we invented. Every headword below was coined by
a band in engine/world.py at the moment it first made the thing,
and every gloss is the referent we WATCHED it get attached to.
That is the whole warrant for the dictionary: a field linguist
points at an object, writes down the noise, and the pointing is
what makes it a translation rather than a guess.

Two directions, as a bilingual dictionary has:

  THEIRS TO OURS   every attested word, alphabetical, with what
                   it names, who says it, and when it first
                   appears in the ledger
  OURS TO THEIRS   every concept, with all attested forms and
                   how many speakers each has

And because nothing made the bands agree, it has dialects. The
same craft carries up to forty forms, and which ones are
widespread is not random: a craft every band found separately
keeps a word per band, while a craft that spread by teaching
carried one word along with it.

    python3 -m tools.dictionary            -> paper/lexicon.md
    python3 -m tools.dictionary --html     -> and the html
"""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "lexicon.md"
YEARS = 14000.0


def collect():
    """-> (theirs, ours). Read off the ledger, not composed."""
    from engine.world import run
    from engine.artifact import PRIMITIVES
    w = run(YEARS)
    first = {}
    for year, band, kind, what in w.ledger:
        if kind in ("craft", "learned") and isinstance(what, str):
            first.setdefault((band, what), year)
    theirs, ours = {}, {}
    for b in w.bands:
        for ref, tok in b.lex.word.items():
            e = theirs.setdefault(tok, {
                "means": ref, "bands": [], "borrowed": 0,
                "first": None})
            e["bands"].append(b.ident)
            if tok in b.lex.borrowed:
                e["borrowed"] += 1
            y = first.get((b.ident, ref))
            if y is not None and (e["first"] is None or y < e["first"]):
                e["first"] = y
            ours.setdefault(ref, {})[tok] = ours.setdefault(
                ref, {}).get(tok, 0) + 1
    return w, theirs, ours, PRIMITIVES


def syllables(word):
    """Their phonology is open CV, so split on that."""
    return "-".join(word[i:i + 2] for i in range(0, len(word), 2))


def build():
    from engine.language import CONSONANTS, VOWELS
    from engine.world import words_for
    w, theirs, ours, PRIM = collect()

    sole = sum(1 for e in theirs.values() if len(e["bands"]) == 1)
    wide = sum(1 for e in theirs.values() if len(e["bands"]) >= 6)
    borrowed = sum(len(b.lex.borrowed) for b in w.bands)

    L = ["# A lexicon of the world in engine/world.py", "",
         f"Compiled {time.strftime('%Y-%m-%d')} from a run of "
         f"{len(w.bands)} bands over {w.year:.0f} years. "
         f"{len(theirs)} headwords for {len(ours)} concepts.", "",
         "Every word here was coined by a band at the moment it "
         "first made the thing. Nothing was given to them and "
         "nothing was invented for this file. We can translate "
         "because we watched each word get attached to an act of "
         "making, which is the position a field linguist is in -- "
         "point at the object, write down the noise. Beyond that "
         "referent, nothing may be read into a word.", "",
         "## Phonology", "", "```",
         f"consonants   {' '.join(CONSONANTS)}",
         f"vowels       {' '.join(VOWELS)}",
         f"syllable     CV, open, no codas",
         f"inventory    {len(CONSONANTS)}x{len(VOWELS)} = "
         f"{len(CONSONANTS)*len(VOWELS)} syllables",
         f"word shape   two or three syllables",
         f"possible     {(len(CONSONANTS)*len(VOWELS))**2 + (len(CONSONANTS)*len(VOWELS))**3:,} words",
         f"attested     {len(theirs)}",
         "```", "",
         "## Dialect", "",
         f"{sole} of {len(theirs)} words are spoken by a single "
         f"band and {wide} by six or more. {borrowed} borrowings "
         f"are recorded -- a band that is taught a craft learns "
         f"the word with it, so teaching spreads vocabulary and "
         f"independent invention does not.", "", "```",
         f"{'concept':<16}{'forms':>7}{'bands':>7}   most widespread"]
    for p in sorted(PRIM, key=lambda x: w.first_seen().get(x, 0)):
        d, h = words_for(p, w)
        if not h:
            continue
        forms = ours.get(p, {})
        top = max(forms, key=lambda t: len(theirs[t]["bands"]))
        L.append(f"{p:<16}{d:>7}{h:>7}   {top} "
                 f"({len(theirs[top]['bands'])} bands)")
    L += ["```", "",
          "The oldest concepts carry the most forms. That is not "
          "noise: a craft every band found separately keeps a word "
          "per band, and a craft that spread by teaching carried "
          "one word with it. Basic vocabulary diverges and "
          "technical vocabulary travels, which is what happens to "
          "real languages.", "",
          "## Theirs to ours", "",
          "Headword, syllabified, then what it names, who says it "
          "and when it is first attested.", ""]
    for tok in sorted(theirs):
        e = theirs[tok]
        bands = e["bands"]
        who = (f"{len(bands)} bands" if len(bands) > 3
               else "band " + ", ".join(str(b) for b in bands))
        yr = ("year %.0f" % e["first"]) if e["first"] is not None else "-"
        borrow = f", borrowed by {e['borrowed']}" if e["borrowed"] else ""
        gloss = PRIM[e["means"]][3] if e["means"] in PRIM else e["means"]
        L.append(f"**{tok}** *{syllables(tok)}* — {gloss}. "
                 f"({e['means']}; {who}{borrow}; first {yr})")
        L.append("")
    L += ["## Ours to theirs", "",
          "Concept, our gloss, then every attested form with the "
          "number of bands that use it.", ""]
    for ref in sorted(ours):
        gloss = PRIM[ref][3] if ref in PRIM else ref
        forms = sorted(ours[ref],
                       key=lambda t: -len(theirs[t]["bands"]))
        L.append(f"### {ref} — {gloss}")
        L.append("")
        L.append(", ".join(f"**{t}** ({len(theirs[t]['bands'])})"
                           for t in forms))
        L.append("")
    L += ["## Compounds", "",
          "A thing of several crafts is named by running the "
          "part-words together. That is concatenation and not "
          "grammar: nothing in this world has given anybody a "
          "grammar, and a compound carries no order, no case and "
          "no agreement.", "", "```"]
    from engine.world import their_entry, spec
    arts = sorted(w.artifacts(), key=lambda c: (len(c), sorted(c)))
    for c in arts[:12] + arts[len(arts) // 2:len(arts) // 2 + 6]:
        who = (spec(c, w)["first built"] or (0, 0))[1]
        t = their_entry(c, who, w)
        if t:
            L.append(f"{t:<44}{' + '.join(sorted(c))}")
    L += ["```", ""]
    return "\n".join(L).rstrip() + "\n"


if __name__ == "__main__":
    text = build()
    OUT.write_text(text)
    print(f"  {OUT.relative_to(ROOT)}  {len(text):,} chars, "
          f"{len(text.splitlines()):,} lines")
    if "--html" in sys.argv:
        from paper.render import render
        html = OUT.with_suffix(".html")
        render(OUT, html, "A lexicon of the world in engine/world.py")
        print(f"  {html.relative_to(ROOT)}  "
              f"{html.stat().st_size:,} bytes")
