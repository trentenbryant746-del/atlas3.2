"""
Turn a run into something arguable: numbers, and charts drawn by hand.

Every fossil in the record is scored against the frozen worlds in bench.py
-- all of them in one batched call, because a hundred genomes cost barely
more than one. Nothing here reads the training fitness except to plot what
the world was doing; the claims come from worlds no run ever saw.

The charts are inline SVG written by this file. matplotlib is not
installed in this container and a chart is a polyline, an axis and some
text, so adding a dependency to draw three of those was not worth it.
"""
from __future__ import annotations

import html as _html
import json
from pathlib import Path

import numpy as np

from mote import bench
from mote.brain import HID0, N_MAX
from mote.deeptime import load_fossils, load_history

PAL = ("#2f6df6", "#e4572e", "#17a398", "#a259d9", "#d9a21b", "#555f6e")


# --------------------------------------------------------------- analysis
def analyse(run_dir):
    run_dir = Path(run_dir)
    cfg = json.loads((run_dir / "run.json").read_text())
    hist = load_history(run_dir)
    gens, foss = load_fossils(run_dir)
    ypg = cfg.get("years_per_gen", 1.0)

    fr = bench.frozen(foss)
    le = bench.lesions(foss)
    ce = bench.ceiling(foss)
    hid = foss.node_on[:, HID0:].sum(1)
    conns = (foss.conn_on & foss.node_on[:, :, None]
             & foss.node_on[:, None, :]).sum((1, 2))

    # The run may have been cut short -- deep runs write history and
    # fossils as they go precisely so that a killed run is still a usable
    # one. Every headline number therefore comes from the fossils that
    # exist, never from the generation count the run was ASKED for.
    done = int(gens[-1])
    cfg["gens_requested"] = cfg.get("gens")
    cfg["gens"] = done
    cfg["completed"] = done >= int(cfg.get("gens_requested") or done)
    first, last = 0, len(gens) - 1
    # "best" by the level the lineage actually lives in, not by an average
    # over levels three quarters of which it never trains near
    best_i = int(np.argmax(fr[0.0] + fr[0.33]))
    h2h = [bench.head_to_head(foss.take([first]), foss.take([best_i]), d=d)
           for d in bench.H2H_LEVELS]
    le_hard = bench.lesions(foss, d=bench.LESION_LEVEL_HARD)

    return {
        "cfg": cfg, "hist": hist, "gens": gens, "years": gens * ypg,
        "fossils": foss, "frozen": fr, "lesions": le, "ceiling": ce,
        "hidden": hid, "conns": conns, "first": first, "last": last,
        "best_i": best_i, "h2h": h2h, "lesions_hard": le_hard,
        "years_per_gen": ypg,
    }


def text_summary(a) -> str:
    cfg, fr, le = a["cfg"], a["frozen"], a["lesions"]
    g, yrs = a["gens"], a["years"]
    i0, ib = a["first"], a["best_i"]
    L = []
    w = L.append
    w("=" * 68)
    w(f"  {cfg['gens']:,} generations   =   {cfg['gens']*a['years_per_gen']:,.0f} "
      f"years at {a['years_per_gen']:g} yr/generation")
    if not cfg.get("completed", True):
        w(f"  (run was stopped early; it was asked for "
          f"{cfg['gens_requested']:,}. Everything below is the "
          f"{cfg['gens']:,} that actually ran.)")
    w(f"  population {cfg['pop']}   worlds/generation {cfg['worlds']}   "
      f"seed {cfg['seed']}   {len(g)} fossils")
    if "elapsed_s" in cfg:
        w(f"  wall clock {cfg['elapsed_s']/60:.1f} min "
          f"({cfg['gens']/max(cfg['elapsed_s'],1e-9):,.0f} generations/s)")
    w("=" * 68)
    w("")
    w("  FROZEN BENCHMARK -- fixed worlds, never used for selection")
    w(f"  {'':<22}{'ancestor':>12}{'best fossil':>14}{'change':>12}")
    rows = [(f"level d={d}", fr[d]) for d in bench.BENCH_LEVELS]
    rows.append(("all levels", fr["overall"]))
    for name, v in rows:
        d0, d1 = float(v[i0]), float(v[ib])
        w(f"  {name:<22}{d0:>+12.3f}{d1:>+14.3f}{d1-d0:>+12.3f}")
    w("")
    w(f"  difficulty ceiling     {a['ceiling'][i0]:>12.2f}"
      f"{a['ceiling'][ib]:>14.2f}"
      f"{a['ceiling'][ib]-a['ceiling'][i0]:>+12.2f}")
    w(f"  hidden neurons         {a['hidden'][i0]:>12d}{a['hidden'][ib]:>14d}"
      f"{a['hidden'][ib]-a['hidden'][i0]:>+12d}")
    w(f"  live connections       {a['conns'][i0]:>12d}{a['conns'][ib]:>14d}"
      f"{a['conns'][ib]-a['conns'][i0]:>+12d}")
    w("")
    w("  WHAT IT LEARNED -- lesions at d=%.2f" % bench.LESION_LEVEL)
    for k in ("intact", "none", "lying", "noisy"):
        w(f"  cue {k:<18}{le[k][i0]:>+12.3f}{le[k][ib]:>+14.3f}"
          f"{le[k][ib]-le[k][i0]:>+12.3f}")
    w(f"  memory index           {le['memory_index'][i0]:>12.3f}"
      f"{le['memory_index'][ib]:>14.3f}")
    w("")
    w("  HEAD TO HEAD -- ancestor vs best fossil, identical worlds")
    for x in a["h2h"]:
        w(f"  d={x['d']:<8.2f} descendant won {x['wins_b']}/{x['episodes']} "
          f"({100*x['win_rate_b']:.0f}%)   "
          f"score {x['score_a']:+.3f} -> {x['score_b']:+.3f}")
    w("")
    w(f"  best fossil is generation {g[ib]:,} "
      f"({yrs[ib]:,.0f} years), of {g[-1]:,}")
    w("=" * 68)
    return "\n".join(L)


# ----------------------------------------------------------------- charts
def _nice(lo, hi, n=5):
    if hi <= lo:
        hi = lo + 1.0
    raw = (hi - lo) / n
    mag = 10 ** np.floor(np.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            stepsize = m * mag
            break
    start = np.floor(lo / stepsize) * stepsize
    ticks = []
    v = start
    while v <= hi + stepsize * 0.5:
        ticks.append(round(v, 10))
        v += stepsize
    return ticks


def _fmt_years(v):
    if v >= 1e6:
        return f"{v/1e6:g}M"
    if v >= 1e3:
        return f"{v/1e3:g}k"
    return f"{v:g}"


def _chart(xs, series, title, ylabel, hline=None, W=820, H=300):
    """series: [(label, y array)]. x is log scale, clamped at 1."""
    L, Rm, T, Bm = 64, 136, 34, 40
    pw, ph = W - L - Rm, H - T - Bm
    x = np.maximum(np.asarray(xs, dtype=float), 1.0)
    lx0, lx1 = np.log10(x.min()), np.log10(max(x.max(), x.min() * 10))

    ys = np.concatenate([np.asarray(s[1], dtype=float) for s in series])
    ys = ys[np.isfinite(ys)]
    lo, hi = (float(ys.min()), float(ys.max())) if ys.size else (0.0, 1.0)
    if hline is not None:
        lo, hi = min(lo, hline), max(hi, hline)
    pad = (hi - lo) * 0.08 or 0.5
    yt = _nice(lo - pad, hi + pad)
    y0, y1 = yt[0], yt[-1]

    def px(v):
        return L + pw * (np.log10(max(v, 1.0)) - lx0) / max(lx1 - lx0, 1e-9)

    def py(v):
        return T + ph * (1 - (v - y0) / max(y1 - y0, 1e-9))

    o = [f'<svg viewBox="0 0 {W} {H}" class="ch" role="img" '
         f'aria-label="{_html.escape(title)}">',
         f'<text x="{L}" y="20" class="t">{_html.escape(title)}</text>']

    for v in yt:                                        # y grid
        o.append(f'<line x1="{L}" y1="{py(v):.1f}" x2="{L+pw}" '
                 f'y2="{py(v):.1f}" class="g"/>')
        o.append(f'<text x="{L-8}" y="{py(v)+4:.1f}" class="a" '
                 f'text-anchor="end">{v:g}</text>')
    dec = range(int(np.floor(lx0)), int(np.ceil(lx1)) + 1)
    for e in dec:                                       # x decades
        v = 10.0 ** e
        if not (x.min() * 0.999 <= v <= 10 ** lx1 * 1.001):
            continue
        o.append(f'<line x1="{px(v):.1f}" y1="{T}" x2="{px(v):.1f}" '
                 f'y2="{T+ph}" class="g"/>')
        o.append(f'<text x="{px(v):.1f}" y="{T+ph+18}" class="a" '
                 f'text-anchor="middle">{_fmt_years(v)}</text>')
    if hline is not None:
        o.append(f'<line x1="{L}" y1="{py(hline):.1f}" x2="{L+pw}" '
                 f'y2="{py(hline):.1f}" class="z"/>')

    for i, (lab, yv) in enumerate(series):
        yv = np.asarray(yv, dtype=float)
        pts = " ".join(f"{px(xx):.1f},{py(vv):.1f}"
                       for xx, vv in zip(x, yv) if np.isfinite(vv))
        c = PAL[i % len(PAL)]
        o.append(f'<polyline points="{pts}" fill="none" stroke="{c}" '
                 f'stroke-width="2" stroke-linejoin="round"/>')
        ly = T + 4 + i * 17
        o.append(f'<line x1="{L+pw+12}" y1="{ly}" x2="{L+pw+30}" y2="{ly}" '
                 f'stroke="{c}" stroke-width="2"/>')
        o.append(f'<text x="{L+pw+36}" y="{ly+4}" class="a">'
                 f'{_html.escape(lab)}</text>')

    o.append(f'<text x="{L+pw/2}" y="{H-6}" class="a" '
             f'text-anchor="middle">years (log scale)</text>')
    o.append(f'<text x="14" y="{T+ph/2}" class="a" text-anchor="middle" '
             f'transform="rotate(-90 14 {T+ph/2})">{_html.escape(ylabel)}</text>')
    o.append("</svg>")
    return "".join(o)


CSS = """
:root{--bg:#fbfbfa;--fg:#1c1b19;--mut:#6b6a66;--card:#fff;--line:#e5e3df;
--grid:#e9e7e2;--zero:#b9b5ad}
:root:not([data-theme=light]) @media (prefers-color-scheme:dark){}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--bg:#1a1a18;--fg:#eceae6;--mut:#a3a09a;--card:#232320;--line:#34332f;
--grid:#30302c;--zero:#55534e}}
:root[data-theme=dark]{--bg:#1a1a18;--fg:#eceae6;--mut:#a3a09a;--card:#232320;
--line:#34332f;--grid:#30302c;--zero:#55534e}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.6 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:40px 16px 72px}
h1{font-size:28px;letter-spacing:-.02em;margin:0 0 6px}
.sub{color:var(--mut);margin:0 0 28px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:18px;margin:0 0 18px;overflow:hidden}
h2{font-size:17px;margin:0 0 4px}
.note{color:var(--mut);font-size:13.5px;margin:0 0 14px}
.ch{width:100%;height:auto;display:block}
.ch .t{font:600 13px ui-sans-serif,sans-serif;fill:var(--fg)}
.ch .a{font:11px ui-sans-serif,sans-serif;fill:var(--mut)}
.ch .g{stroke:var(--grid);stroke-width:1}
.ch .z{stroke:var(--zero);stroke-width:1;stroke-dasharray:4 3}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
gap:12px;margin:0 0 18px}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:14px}
.kpi .v{font-size:24px;font-weight:650;letter-spacing:-.02em}
.kpi .k{color:var(--mut);font-size:12.5px;margin-top:2px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th,td{text-align:right;padding:7px 8px;border-bottom:1px solid var(--line)}
th:first-child,td:first-child{text-align:left}
th{color:var(--mut);font-weight:550}
pre{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:16px;overflow-x:auto;font:12.5px/1.5 ui-monospace,monospace}
@media (max-width:560px){.wrap{padding:24px 16px 56px}h1{font-size:23px}}
"""


def html(a, path):
    cfg, fr, le = a["cfg"], a["frozen"], a["lesions"]
    yrs, i0, ib = a["years"], a["first"], a["best_i"]
    ov0, ov1 = float(fr[0.0][i0]), float(fr[0.0][ib])
    h = a["h2h"][0]

    kpi = [
        (f"{cfg['gens']*a['years_per_gen']:,.0f}", "years simulated"),
        (f"{cfg['gens']:,}", "generations"),
        (f"{ov0:+.3f} &rarr; {ov1:+.3f}", "benchmark score, easiest level"),
        (f"{100*h['win_rate_b']:.0f}%", f"descendant wins, d={h['d']:.2f}"),
        (f"{a['ceiling'][i0]:.1f} &rarr; {a['ceiling'][ib]:.1f}",
         "hardest world survivable"),
        (f"{a['hidden'][i0]} &rarr; {a['hidden'][ib]}", "hidden neurons"),
    ]
    charts = [
        ("Competence on worlds that never change",
         "Each fossil champion scored on the frozen benchmark: fixed seeds, "
         "fixed difficulty, never visible to selection. This is the only "
         "curve entitled to the word improvement.",
         _chart(yrs, [(f"d={d}", fr[d]) for d in bench.BENCH_LEVELS]
                + [("all levels", fr["overall"])],
                "frozen benchmark score", "score", hline=0.0)),
        ("The hardest world it can still make a living in",
         "Difficulty is scanned upward and stopped at the first level where "
         "the mote can no longer end its life with more energy than it "
         "spent. Higher is a wider band of worlds it is viable in.",
         _chart(yrs, [("ceiling", a["ceiling"])], "difficulty ceiling",
                "difficulty d")),
        ("How much of the competence is memory",
         "The cue announcing which flavour is food is lesioned three ways. A "
         "mote that remembers is wrecked when the cue lies; one that "
         "taste-tests never notices. The gap is the memory index.",
         _chart(yrs, [("cue intact", le["intact"]), ("cue absent", le["none"]),
                      ("cue lying", le["lying"]),
                      ("double noise", le["noisy"])],
                "score under lesion", "score", hline=0.0)),
        ("The brain it decided to pay for",
         "Hidden neurons cost metabolism every tick, so size is an economic "
         "outcome rather than a free parameter. Connections are counted "
         f"between live nodes only; the array ceiling is {N_MAX-HID0}.",
         _chart(yrs, [("hidden neurons", a["hidden"]),
                      ("live connections", a["conns"])],
                "count", "count")),
        ("The world kept up",
         "Training difficulty is not a schedule. It rises when the top "
         "quartile eats well and falls when it starves, so this curve is a "
         "readout of the population's competence at the time.",
         _chart(np.maximum(a["hist"]["years"], 1),
                [("difficulty d", a["hist"]["d"]),
                 ("top-quartile score", a["hist"]["topq_ema"])],
                "training world", "value")),
    ]

    sel = sorted(set(np.linspace(0, len(a["gens"]) - 1, 14).astype(int)))
    rows = "".join(
        f"<tr><td>{a['gens'][i]:,}</td><td>{yrs[i]:,.0f}</td>"
        f"<td>{fr['overall'][i]:+.3f}</td><td>{fr[1.0][i]:+.3f}</td>"
        f"<td>{a['ceiling'][i]:.1f}</td><td>{a['hidden'][i]}</td>"
        f"<td>{a['conns'][i]}</td>"
        f"<td>{le['memory_index'][i]:.2f}</td></tr>" for i in sel)

    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mote Deep Time</title><style>{CSS}</style></head><body><div class="wrap">
<h1>One mote, {cfg['gens']*a['years_per_gen']:,.0f} years</h1>
<p class="sub">{'' if cfg.get('completed', True) else
 f"Stopped early at {cfg['gens']:,} of {cfg['gens_requested']:,} requested generations. "}A {cfg['pop']}-genome lineage of tiny recurrent brains, evolved
for {cfg['gens']:,} generations at {a['years_per_gen']:g} year per generation.
Every number below comes from worlds that never changed and were never
available to selection.</p>
<div class="kpis">{''.join(f'<div class="kpi"><div class="v">{v}</div><div class="k">{k}</div></div>' for v, k in kpi)}</div>
{''.join(f'<div class="card"><h2>{t}</h2><p class="note">{n}</p>{c}</div>' for t, n, c in charts)}
<div class="card"><h2>The record</h2>
<p class="note">Fossil champions sampled across the run.</p>
<table><thead><tr><th>generation</th><th>years</th><th>bench</th>
<th>d=1.0</th><th>ceiling</th><th>neurons</th><th>conns</th><th>memory</th>
</tr></thead><tbody>{rows}</tbody></table></div>
<div class="card"><h2>Head to head</h2>
<p class="note">The first fossil and the best fossil placed in the same
episodes, meeting the same patch layouts and the same sensor noise.</p>
<table><thead><tr><th>difficulty</th><th>ancestor</th><th>descendant</th>
<th>descendant wins</th></tr></thead><tbody>
{''.join(f"<tr><td>d={x['d']:.2f}</td><td>{x['score_a']:+.3f}</td><td>{x['score_b']:+.3f}</td><td>{x['wins_b']}/{x['episodes']}</td></tr>" for x in a['h2h'])}
</tbody></table></div>
<div class="card"><h2>Summary</h2><pre>{_html.escape(text_summary(a))}</pre></div>
</div></body></html>"""
    Path(path).write_text(doc)
    return path
