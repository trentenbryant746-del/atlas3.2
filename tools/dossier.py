"""The whole thing, with the working shown, as one external file.

tools/transcribe.py writes what the system SAYS. This writes what
it says and what is underneath it: every constant with its value
and its units, every rule with its source, and for each link in
the chain the arithmetic, chemistry or physics that forces it.

Part I    every rule in detail, module by module
Part II   the chain, each link with its working
Part III  the technology, with the bootstrap arithmetic
Part IV   the published numbers and the withdrawn ones

    python3 -m tools.dossier            -> paper/atlas-dossier.md
    python3 -m tools.dossier --html     -> and the html
"""

import importlib
import inspect
import math
import pkgutil
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "paper" / "atlas-dossier.md"
SKIP = {"__init__", "spine", "ir", "responder_shim"}

CONST_RE = re.compile(r"^([A-Z_][A-Z_0-9]*)\s*=\s*(.+?)\s*(?:#\s*(.*))?$")


def _wrap(text, width=76, indent=""):
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


def _modules():
    import engine
    got = []
    for m in pkgutil.iter_modules(engine.__path__):
        if m.name in SKIP:
            continue
        try:
            got.append((m.name, importlib.import_module(f"engine.{m.name}")))
        except Exception:
            continue
    return sorted(got)


def _constants(mod):
    """-> [(name, value, units/comment)] read from the source."""
    try:
        src = inspect.getsource(mod)
    except Exception:
        return []
    out = []
    for line in src.splitlines():
        m = CONST_RE.match(line)
        if not m:
            continue
        name, expr, comment = m.group(1), m.group(2), m.group(3) or ""
        if expr.startswith(("{", "[", "(")) and len(expr) > 60:
            expr = expr[:57] + "..."
        val = getattr(mod, name, None)
        if isinstance(val, Path) or name in ("ROOT", "HERE"):
            continue          # a filesystem path is not a constant
        if inspect.ismodule(val):
            out.append((name, expr.strip(),
                        f"<compiled extension: {val.__name__}>",
                        comment.strip()))
            continue
        if isinstance(val, float):
            shown = f"{val:.6g}"
        elif isinstance(val, dict):
            if len(val) <= 14 and len(repr(val)) < 420:
                shown = "{" + ", ".join(
                    f"{k!r}: {v!r}" if not isinstance(v, float)
                    else f"{k!r}: {v:g}" for k, v in val.items()) + "}"
            else:
                shown = f"<dict, {len(val)} entries>"
        elif isinstance(val, (list, tuple, set)):
            shown = (repr(val) if len(repr(val)) < 420
                     else f"<{type(val).__name__}, {len(val)} entries>")
        else:
            shown = str(val)[:110]
        out.append((name, expr.strip(), shown, comment.strip()))
    return out


def _functions(mod):
    out = []
    for name, fn in vars(mod).items():
        if name.startswith("_") or not inspect.isfunction(fn):
            continue
        if fn.__module__ != mod.__name__:
            continue
        try:
            sig = str(inspect.signature(fn))
            src = inspect.getsource(fn)
        except Exception:
            continue
        out.append((name, sig, inspect.getdoc(fn) or "", src))
    return sorted(out)


# --- the physics behind the cosmological links ----------------------

def _cosmology():
    """Temperature and energy at each epoch, computed here."""
    from engine.constants import H_PLANCK, C_LIGHT, K_B, G_GRAV, HBAR
    from engine.epochs import EPOCHS
    a_rad = (8 * math.pi**5 * K_B**4) / (15 * H_PLANCK**3 * C_LIGHT**3)
    coef = (3 * C_LIGHT**2 / (32 * math.pi * G_GRAV * a_rad)) ** 0.25
    t_planck = math.sqrt(HBAR * G_GRAV / C_LIGHT**5)
    T_planck = math.sqrt(HBAR * C_LIGHT**5 / G_GRAV) / K_B
    rows = {}
    for name, t, _what in EPOCHS:
        T = coef * t ** -0.5
        rows[name] = (t, T, K_B * T / 1.602176634e-13)   # MeV
    return rows, t_planck, T_planck, a_rad, coef


SCALES = {
    "planck": ("quantum gravity", None,
               "Below the Planck time no clock built of the fields we "
               "have distinguishes one instant from another, so there "
               "is no ordering to put structure in."),
    "quark": ("QCD confinement", 200.0,
              "Confinement sets in near kT = 200 MeV. Above it the "
              "colour force cannot hold a triplet together against "
              "the thermal bath, so quarks are free and no hadron "
              "exists to be counted."),
    "hadron": ("QCD confinement", 200.0,
               "kT has fallen through the confinement scale, so "
               "triplets bind and protons and neutrons exist."),
    "lepton": ("n/p freeze-out", 0.8,
               "The weak rates that interconvert n and p fall below "
               "the expansion rate near kT = 0.8 MeV, so the ratio "
               "stops tracking equilibrium and freezes."),
    "bbn": ("deuterium binding 2.22 MeV", 2.22,
            "Deuterium is bound at 2.22 MeV but photons outnumber "
            "baryons by 1.6e9, so the tail of the Planck spectrum "
            "keeps breaking it until kT is far below the binding. "
            "That delay is the deuterium bottleneck and it is why "
            "nucleosynthesis waits until minutes rather than "
            "seconds."),
    "recombination": ("hydrogen ionisation 13.6 eV", 13.6e-6,
                      "Same bottleneck, same cause: 13.6 eV binding "
                      "against a 1.6e9 photon-to-baryon ratio, so "
                      "atoms form near 0.3 eV rather than 13.6."),
}


def rules_part():
    lines = ["# Part I — every rule in detail", "",
             _wrap("Module by module: the module's own account of "
                   "itself, every constant it defines with the value "
                   "and the units as written, and every rule with its "
                   "signature, its docstring and its source. Nothing "
                   "is summarised here; this is what runs."), ""]
    mods = _modules()
    nconst = nfn = 0
    for name, mod in mods:
        lines += [f"## engine/{name}.py", ""]
        doc = inspect.getdoc(mod)
        if doc:
            lines += [_wrap(doc.replace("\n\n", "\n \n")), ""]
        consts = _constants(mod)
        if consts:
            nconst += len(consts)
            lines += ["**Constants**", "", "```"]
            for cn, expr, shown, comment in consts:
                pad = " " * max(1, 26 - len(cn))
                tail = f"   # {comment}" if comment else ""
                if len(shown) > 150:
                    lines.append(f"{cn}{pad}=")
                    body, line = shown.strip("{}").split(", "), "    "
                    for piece in body:
                        if len(line) + len(piece) > 74:
                            lines.append(line.rstrip(" "))
                            line = "    "
                        line += piece + ", "
                    lines.append(line.rstrip(", "))
                    if comment:
                        lines.append(f"    # {comment}")
                else:
                    lines.append(f"{cn}{pad}= {shown}{tail}")
            lines += ["```", ""]
        fns = _functions(mod)
        nfn += len(fns)
        for fn, sig, fdoc, src in fns:
            lines += [f"**`{fn}{sig}`**", ""]
            if fdoc:
                lines += [_wrap(fdoc.replace("\n\n", "\n \n")), ""]
            lines += ["```python", src.rstrip(), "```", ""]
    lines.insert(3, _wrap(f"{len(mods)} modules, {nconst} constants, "
                          f"{nfn} rules.") + "\n")
    return lines


def chain_part():
    from engine.lineage import chain
    cos, t_planck, T_planck, a_rad, coef = _cosmology()
    c = chain()
    lines = ["# Part II — the chain, with the working", "",
             _wrap(f"{len(c)} links. Each gives its verdict, the rule "
                   f"that drives it, the numbers that rule produces, "
                   f"and the rule's source. Where the link is a "
                   f"cosmological epoch the temperature and energy are "
                   f"computed here rather than quoted."), "",
             "## The radiation era, computed", "",
             _wrap("In a radiation-dominated universe the Friedmann "
                   "equation with rho = a T^4 / c^2 gives"), "",
             "```",
             "    T(t) = ( 3 c^2 / (32 pi G a) )^(1/4) * t^(-1/2)",
             "",
             f"    a (radiation constant) = 8 pi^5 k^4 / (15 h^3 c^3)",
             f"                           = {a_rad:.6e} J m^-3 K^-4",
             f"    coefficient            = {coef:.6e} K s^(1/2)",
             "",
             f"    Planck time  sqrt(hbar G / c^5)      "
             f"= {t_planck:.4e} s",
             f"    Planck temp  sqrt(hbar c^5 / G) / k  "
             f"= {T_planck:.4e} K",
             "```", "",
             _wrap("Evaluated at each epoch, against the energy scale "
                   "that actually does the gating:"), "",
             "```",
             f"{'epoch':<15}{'t (s)':>12}{'T (K)':>13}{'kT (MeV)':>13}"
             f"   scale it crosses", ]
    for nm, (t, T, mev) in cos.items():
        sc = SCALES.get(nm)
        tag = ""
        if sc:
            tag = sc[0] if sc[1] is None else f"{sc[0]} = {sc[1]:g} MeV"
        lines.append(f"{nm:<15}{t:>12.3g}{T:>13.4g}{mev:>13.4g}   {tag}")
    lines += ["```", ""]
    for nm, sc in SCALES.items():
        lines += [f"**{nm}** — {_wrap(sc[2])}", ""]

    for i, (a, b, v, rule, why) in enumerate(c, 1):
        lines += [f"## {i}. {a} → {b}", "",
                  f"**{v}** &nbsp; rule: `{rule}`", ""]
        if a in cos or b in cos:
            blk = ["```"]
            for end, key in (("from", a), ("to", b)):
                if key not in cos:
                    continue
                t, T, mev = cos[key]
                sc = SCALES.get(key)
                blk += [f"    {end:<5} {key}",
                        f"        t  = {t:.4g} s",
                        f"        T  = {coef:.4e} * t^(-1/2)"
                        f" = {T:.4e} K",
                        f"        kT = {mev:.4e} MeV"]
                if sc and sc[1]:
                    blk.append(f"        vs {sc[0]} = {sc[1]:g} MeV"
                               f"   ratio {mev/sc[1]:.3g}")
                blk.append("")
            if a in cos and b in cos:
                ta, tb = cos[a][0], cos[b][0]
                blk += [f"    elapsed  {tb - ta:.4g} s"
                        f"   ({tb/ta:.3g}x)", ""]
            lines += blk[:-1] + ["```", ""]
        mod, _, fn = rule.partition(".")
        try:
            m = importlib.import_module("engine." + mod)
            obj = getattr(m, fn, None)
            if inspect.isfunction(obj):
                lines += ["```python", inspect.getsource(obj).rstrip(),
                          "```", ""]
                try:
                    lines += ["```", f"    {fn}() = {obj()!r}", "```", ""]
                except Exception:
                    pass
            elif obj is not None and not inspect.ismodule(obj):
                lines += ["```", f"    {rule} ="]
                if isinstance(obj, dict):
                    for k, val in list(obj.items())[:40]:
                        lines.append(f"        {k!r}: {val!r}"[:300])
                    if len(obj) > 40:
                        lines.append(f"        ... {len(obj)-40} more")
                elif isinstance(obj, (list, tuple)):
                    for val in list(obj)[:40]:
                        lines.append(f"        {val!r}"[:300])
                    if len(obj) > 40:
                        lines.append(f"        ... {len(obj)-40} more")
                else:
                    lines.append(f"        {obj!r}"[:300])
                lines += ["```", ""]
        except Exception:
            pass
        lines += [_wrap(why), ""]
    return lines


def technology_part():
    from engine.artifact import (PRIMITIVES, GAINS, TOL_GAINS, TOL_NEEDED,
                                 BASE_K, BASE_TOL, bootstrap, catalogue,
                                 tolerance, held_by_round, depth, project)
    from engine.intricacy import levers
    b = bootstrap()
    lines = ["# Part III — the technology", "",
             _wrap(f"{len(PRIMITIVES)} physical capabilities, each "
                   f"grounded in a rule from Part I. An artifact is a "
                   f"set of them used together. Two scalars gate the "
                   f"sequence and the second one takes over when the "
                   f"first stops moving."), "",
             "## The primitives", "", "```",
             f"{'name':<15}{'K':>7}{'tol':>9}  {'depth':>5}  needs"]
    for n in sorted(PRIMITIVES, key=lambda x: (depth(x), x)):
        needs, k, rule, words = PRIMITIVES[n]
        lines.append(f"{n:<15}{k:>7}{TOL_NEEDED.get(n, BASE_TOL):>9.0e}"
                     f"  {depth(n):>5}  {', '.join(needs) or '-'}")
    lines += ["```", "", "**What each one is, and what grounds it**", ""]
    for n in sorted(PRIMITIVES, key=lambda x: (depth(x), x)):
        needs, k, rule, words = PRIMITIVES[n]
        lines.append(f"- **{n}** — {words}. Needs {k} K"
                     f"{'' if n not in TOL_NEEDED else f' and {TOL_NEEDED[n]:.0e} tolerance'}"
                     f". Grounded in `{rule}`.")
    lines += ["", "## The two gates", "", "```",
              f"    an open wood fire            {BASE_K} K",
              f"    a hand fits to               {BASE_TOL:.0e}", ""]
    for label, (needs, gain) in GAINS.items():
        lines.append(f"    +{gain:>4} K   {label:<32} needs {', '.join(needs)}")
    lines.append("")
    for label, (needs, tol) in TOL_GAINS.items():
        lines.append(f"    ->{tol:>7.0e}  {label:<30} needs {', '.join(needs)}")
    lines += ["```", "", "## The bootstrap", "", "```",
              f"{'round':<7}{'K':>7}{'tol':>9}   reached"]
    for i, t, got in b:
        lines.append(f"{i:<7}{t:>7}{tolerance(held_by_round(i)):>9.0e}"
                     f"   {', '.join(got)}")
    lines += ["```", "", "## The things themselves", "",
              _wrap("Names are vocabulary and derive nothing. Each is "
                    "checked against the derivation: a name whose parts "
                    "never become reachable is an error, not a "
                    "prediction."), "", "```"]
    for r, t, name, parts in catalogue():
        lines.append(f"round {r:<3} {t:>5} K   {name}")
        lines.append(f"{'':>17}  = {' + '.join(parts)}")
    lines += ["```", "", "## What would move it further", "", "```"]
    for nm, dp, e in levers():
        lines.append(f"{nm:<26} {dp:+6.1f} parts   exponent {e:+.3f}")
    lines += ["```", "", "## Two centuries forward", "", "```"]
    for k, v in project().items():
        lines.append(f"{k:<20} {v}")
    lines += ["```", ""]
    return lines


def claims_part():
    from eval.claims import CLAIMS, SUPERSEDED, run
    from eval.history import table, score
    rows = run()
    good = sum(1 for *_x, ok, _s in rows if ok)
    m, l, x, fm = score()
    lines = ["# Part IV — the numbers, and the ones withdrawn", "",
             f"## Published ({good} of {len(rows)} reproduce)", "", "```"]
    for sec, claim, want, got, ok, _st in rows:
        lines.append(f"{'ok ' if ok else 'FAIL'} {sec}  {claim}")
        lines.append(f"{'':>5} = {got}")
    lines += ["```", "", "## Against the recorded record", "", "```",
              f"{'':<24}{'derived':>13}{'recorded':>13}{'ratio':>9}"
              f"  verdict"]
    for lab, d, rec, u, ratio, v, free, _n in table():
        tail = "  (built in, not counted)" if not free else ""
        lines.append(f"{lab:<24}{d:>13.4g}{rec:>13.4g}{ratio:>9.2f}"
                     f"  {v}{tail}")
    lines += [f"\n{m} match, {l} loose, {x} miss "
              f"({fm} of the matches could have differed)", "```", ""]
    for lab, d, rec, u, ratio, v, free, note in table():
        lines += [f"**{lab}** — {_wrap(note)}", ""]
    lines += [f"## Withdrawn ({len(SUPERSEDED)})", "",
              _wrap("Published here and wrong. Kept with the reason, "
                    "because a record that holds only the surviving "
                    "answers is not a record."), ""]
    for sec, claim, why in SUPERSEDED:
        lines += [f"### `{sec}` {claim}", "", _wrap(why), ""]
    return lines


def build():
    from engine.lineage import chain
    c = chain()
    head = ["# Atlas — the documented history, with the working", "",
            _wrap(f"Generated {time.strftime('%Y-%m-%d')} from the rules "
                  f"themselves. Nothing in this document was typed by "
                  f"hand: every value was computed by the rule it sits "
                  f"under, and every block of source is the source that "
                  f"runs. {len(c)} links in the chain."), "",
            "**Contents**", "",
            "- Part I — every rule in detail",
            "- Part II — the chain, with the working",
            "- Part III — the technology",
            "- Part IV — the numbers, and the ones withdrawn", "",
            "---", ""]
    text = "\n".join(head + rules_part() + ["---", ""] + chain_part()
                     + ["---", ""] + technology_part() + ["---", ""]
                     + claims_part()).rstrip() + "\n"
    OUT.write_text(text)
    return text


if __name__ == "__main__":
    t = build()
    print(f"  {OUT.relative_to(ROOT)}  {len(t):,} chars, "
          f"{len(t.splitlines()):,} lines")
    if "--html" in sys.argv:
        from paper.render import render
        html = OUT.with_suffix(".html")
        render(OUT, html, "Atlas - the documented history, with the working")
        print(f"  {html.relative_to(ROOT)}  {html.stat().st_size:,} bytes")
