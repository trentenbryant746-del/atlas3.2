"""Markdown -> print-ready HTML. Stdlib only, like everything else here.

Handles what the paper actually uses: headings, tables, fenced and
indented code, bold, inline code, lists, blockquotes, rules. Open the
output in a browser and print to PDF.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

CSS = """
@page { size: A4; margin: 19mm 17mm; }
* { box-sizing: border-box; }
body { font: 10.5pt/1.5 "Charter","Georgia","Times New Roman",serif;
       color:#111; max-width: 46em; margin: 0 auto; padding: 2em 1.2em; }
h1 { font-size: 19pt; line-height:1.25; margin:0 0 .15em; letter-spacing:-.01em; }
h1 + p strong { font-weight:600; }
h2 { font-size: 13pt; margin: 1.9em 0 .5em; padding-top:.5em;
     border-top: 1px solid #ddd; }
h3 { font-size: 11pt; margin: 1.4em 0 .35em; }
p, li { margin: .5em 0; }
code { font: 9.5pt ui-monospace,"SF Mono",Menlo,Consolas,monospace;
       background:#f4f4f3; padding:.1em .3em; border-radius:3px; }
pre { font: 9pt/1.45 ui-monospace,"SF Mono",Menlo,Consolas,monospace;
      background:#f7f7f6; border-left:2.5px solid #bbb; padding:.7em .9em;
      overflow-x:auto; white-space:pre; border-radius:0 3px 3px 0; }
pre code { background:none; padding:0; font-size:inherit; }
table { border-collapse: collapse; margin: .9em 0; font-size: 9.5pt;
        width:100%; }
th,td { border-bottom:1px solid #ddd; padding:.32em .7em .32em 0;
        text-align:left; vertical-align:top; }
th { border-bottom:1.5px solid #888; font-weight:600; }
td:nth-child(n+2), th:nth-child(n+2) { text-align:right; }
table.wide td:nth-child(n+2), table.wide th:nth-child(n+2){text-align:left;}
blockquote { margin:1em 0; padding:.4em 0 .4em 1em; border-left:3px solid #888;
             color:#333; font-style:normal; }
hr { border:0; border-top:1px solid #ddd; margin:2em 0; }
strong { font-weight:600; }
h2, h3 { page-break-after: avoid; }
pre, table, blockquote { page-break-inside: avoid; }
a { color:#0b5; text-decoration:none; }
"""


def inline(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def convert(md):
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
        elif ln.startswith("    ") and ln.strip():
            buf = []
            while i < len(lines) and (lines[i].startswith("    ")
                                      or not lines[i].strip()):
                buf.append(html.escape(lines[i][4:]))
                i += 1
            while buf and not buf[-1].strip():
                buf.pop()
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            continue
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")]
                     for r in rows if not set(r) <= set("|-: ")]
            wide = "wide" if max(len(c) for c in cells) >= 2 and any(
                len(x) > 18 for r in cells for x in r[1:]) else ""
            t = [f'<table class="{wide}">', "<tr>"]
            t += [f"<th>{inline(c)}</th>" for c in cells[0]]
            t.append("</tr>")
            for r in cells[1:]:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>"
                                          for c in r) + "</tr>")
            t.append("</table>")
            out.append("".join(t))
            continue
        elif ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(inline(lines[i][2:]))
                i += 1
            out.append("<blockquote>" + " ".join(buf) + "</blockquote>")
            continue
        elif re.match(r"^\s*[-*] ", ln):
            buf = []
            while i < len(lines) and (re.match(r"^\s*[-*] ", lines[i])
                                      or lines[i].startswith("  ")):
                if re.match(r"^\s*[-*] ", lines[i]):
                    buf.append("<li>" + inline(
                        re.sub(r"^\s*[-*] ", "", lines[i])))
                elif buf:
                    buf[-1] += " " + inline(lines[i].strip())
                i += 1
            out.append("<ul>" + "".join(b + "</li>" for b in buf) + "</ul>")
            continue
        elif re.match(r"^\d+\. ", ln):
            buf = []
            while i < len(lines) and (re.match(r"^\d+\. ", lines[i])
                                      or lines[i].startswith("   ")):
                if re.match(r"^\d+\. ", lines[i]):
                    buf.append("<li>" + inline(
                        re.sub(r"^\d+\. ", "", lines[i])))
                elif buf:
                    buf[-1] += " " + inline(lines[i].strip())
                i += 1
            out.append("<ol>" + "".join(b + "</li>" for b in buf) + "</ol>")
            continue
        elif ln.startswith("#"):
            n = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{n}>{inline(ln[n:].strip())}</h{n}>")
        elif ln.strip() in ("---", "***"):
            out.append("<hr>")
        elif ln.strip():
            buf = [ln]
            i += 1
            while (i < len(lines) and lines[i].strip()
                   and not re.match(r"^(#|\||>|```|\s*[-*] |\d+\. |    )",
                                    lines[i])
                   and lines[i].strip() not in ("---", "***")):
                buf.append(lines[i])
                i += 1
            out.append("<p>" + inline(" ".join(buf)) + "</p>")
            continue
        i += 1
    return "\n".join(out)


def render(src, dst, title):
    md = Path(src).read_text()
    Path(dst).write_text(
        f"<!doctype html><html><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><style>{CSS}</style>"
        f"</head><body>{convert(md)}</body></html>")
    return dst


if __name__ == "__main__":
    for src, dst, title in (
            ("paper/atlas-claim-ledger.md", "SEND/paper.html",
             "What actually catches errors in scientific code?"),
            ("LOG.md", "SEND/fault-corpus.html",
             "Fault corpus - regressions and progressions")):
        Path(dst).parent.mkdir(exist_ok=True)
        print("  wrote", render(src, dst, title))
