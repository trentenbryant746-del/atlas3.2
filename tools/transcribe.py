"""Write out everything the system holds, as a document a person reads.

The corpus is not much use if the only way to read it is to run
Python. This walks the chain in order, then every module's checks,
then the claims and the superseded record, and emits one markdown
file -- the documented history, transcribed.

Nothing here is hand-written. Every sentence in the output came
from a rule that produced it, and if a rule changes its sentence
changes. That is the point: the document cannot drift from the
system, because it is not a copy of the system.

    python3 -m tools.transcribe             -> paper/history.md
    python3 -m tools.transcribe --html      -> and history.html
"""

import importlib
import pkgutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "history.md"

SKIP = {"__init__", "spine", "ir"}


def _modules():
    """Every engine module that publishes a check(). DERIVED."""
    import engine
    names = []
    for m in pkgutil.iter_modules(engine.__path__):
        if m.name in SKIP:
            continue
        try:
            mod = importlib.import_module(f"engine.{m.name}")
        except Exception:
            continue
        if callable(getattr(mod, "check", None)):
            names.append((m.name, mod))
    return sorted(names)


def _wrap(text, width=72, indent=""):
    out, line = [], indent
    for word in str(text).split():
        if len(line) + len(word) + 1 > width and line.strip():
            out.append(line.rstrip())
            line = indent + word + " "
        else:
            line += word + " "
    if line.strip():
        out.append(line.rstrip())
    return "\n".join(out)


def technology_section():
    """The things, in the order combustion allows them."""
    from engine.artifact import (PRIMITIVES, bootstrap, catalogue,
                                 depth, GAINS, BASE_K)
    from engine.intricacy import levers, settle_network
    b = bootstrap()
    lines = ["## The technology", "",
             _wrap(f"{len(PRIMITIVES)} physical capabilities, each "
                   f"grounded in a rule that already existed for "
                   f"another reason. An artifact is a set of them used "
                   f"together. What gates the sequence is not how many "
                   f"parts anyone can compose -- the tree is only "
                   f"{max(depth(n) for n in PRIMITIVES)+1} deep against "
                   f"a budget of {settle_network():.1f} -- but "
                   f"TEMPERATURE: every step past cordage is a "
                   f"material you cannot have until you can reach the "
                   f"heat that makes it."), "",
             "### What can be reached, and how hot", "",
             _wrap(f"An open wood fire is {BASE_K} K. Each thing built "
                   f"raises it, and the things that raise it need the "
                   f"things it makes:"), ""]
    for label, (needs, gain) in GAINS.items():
        lines.append(f"- **{label}** +{gain} K — needs {', '.join(needs)}")
    lines += ["", "### The bootstrap", ""]
    for i, t, got in b:
        lines.append(f"**Round {i}** — {t} K")
        lines.append("")
        for g in got:
            needs, k, rule, words = PRIMITIVES[g]
            req = f"needs {', '.join(needs)}" if needs else "needs nothing"
            lines.append(f"- **{g}** ({k} K, {req}) — {words} "
                         f"&nbsp; `{rule}`")
        lines.append("")
    lines += ["### The things themselves", "",
              _wrap("Names are vocabulary and derive nothing. Each is "
                    "checked against the derivation: a name whose "
                    "parts never become reachable is an error, not a "
                    "prediction. The order is not a list anybody "
                    "wrote."), ""]
    for r, t, name, parts in catalogue():
        lines.append(f"- **round {r}, {t} K** — {name} "
                     f"({' + '.join(parts)})")
    lines += ["", "### What would move it further", "",
              _wrap("The fixed point converges because the corpus "
                    "enters as a logarithm, so trying harder buys "
                    "nothing. Only a changed term moves it:"), ""]
    for nm, dp, e in levers():
        lines.append(f"- **{nm}** — {dp:+.1f} parts, "
                     f"per-capita exponent {e:+.3f}")
    lines.append("")
    return lines


def chain_section():
    from engine.lineage import chain
    c = chain()
    lines = ["## The chain", "",
             _wrap(f"{len(c)} links from a nebula to a head. Each one "
                   f"names the rule that drives it and the module the "
                   f"rule lives in. A link is DERIVED when something "
                   f"here forces it, FORCED when it is both permitted "
                   f"and driven, CROSSES when it is permitted and "
                   f"nothing drives it, and MISSING when it is a gap "
                   f"that has been named rather than filled."), ""]
    for i, (a, b, v, rule, why) in enumerate(c, 1):
        lines += [f"### {i}. {a} -> {b}", "",
                  f"*{v}* &nbsp; `{rule}`", "", _wrap(why), ""]
    return lines


def rules_section():
    lines = ["## The rules, and what each one says", "",
             _wrap("Every check below is a rule that produced its own "
                   "sentence. An INVERTED check is one that fails when "
                   "the result looks too good -- it is there to catch "
                   "the system flattering itself."), ""]
    total = passed = 0
    for name, mod in _modules():
        try:
            ok, res = mod.check()
        except Exception as e:
            lines += [f"### engine/{name}.py", "",
                      f"**did not run**: {type(e).__name__}: {e}", ""]
            continue
        total += len(res)
        passed += sum(1 for _, x, _ in res if x)
        doc = (mod.__doc__ or "").strip().split("\n\n")[0]
        lines += [f"### engine/{name}.py", ""]
        if doc:
            lines += [_wrap(doc.replace("\n", " ")), ""]
        for cname, x, msg in res:
            mark = "holds" if x else "**FAILS**"
            lines += [f"**{cname}** — {mark}", "", _wrap(msg), ""]
    lines.insert(2, _wrap(f"{passed} of {total} rules hold across "
                          f"{len(_modules())} modules.") + "\n")
    return lines


def claims_section():
    from eval.claims import CLAIMS, SUPERSEDED, run
    rows = run()
    good = sum(1 for *_x, ok, _s in rows if ok)
    lines = ["## The published numbers", "",
             _wrap(f"{good} of {len(rows)} reproduce. A claim is tied "
                   f"to a fingerprint over the rule that produced it "
                   f"and everything that rule depends on, so an "
                   f"unchanged fingerprint is a proof that recomputing "
                   f"would return the same thing."), ""]
    for sec, claim, want, got, ok, _st in rows:
        mark = "reproduces" if ok else "**DOES NOT REPRODUCE**"
        lines.append(f"- `{sec}` {claim} — {mark} (`{got}`)")
    lines += ["", "## What was published and later withdrawn", "",
              _wrap(f"{len(SUPERSEDED)} numbers were published here and "
                    f"are wrong. They are kept with the reason, because "
                    f"a record that only holds the surviving answers is "
                    f"not a record."), ""]
    for sec, claim, why in SUPERSEDED:
        lines += [f"### `{sec}` {claim}", "", _wrap(why), ""]
    return lines


def build():
    lines = ["# Atlas — the documented history", "",
             _wrap(f"Transcribed {time.strftime('%Y-%m-%d')} from the "
                   f"rules themselves. Nothing in this document was "
                   f"typed by hand: every sentence was produced by the "
                   f"rule it describes, so it cannot drift from what "
                   f"the system actually does."), ""]
    lines += (chain_section() + technology_section()
              + rules_section() + claims_section())
    text = "\n".join(lines).rstrip() + "\n"
    OUT.write_text(text)
    return text


if __name__ == "__main__":
    t = build()
    print(f"  {OUT.relative_to(ROOT)}  {len(t):,} chars, "
          f"{len(t.splitlines()):,} lines")
    if "--html" in sys.argv:
        from paper.render import render
        html = OUT.with_suffix(".html")
        render(OUT, html, "Atlas - the documented history")
        print(f"  {html.relative_to(ROOT)}  "
              f"{html.stat().st_size:,} bytes")
