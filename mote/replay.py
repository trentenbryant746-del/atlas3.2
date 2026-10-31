"""
Watch one mote live, in a terminal.

The numbers in a report say a lineage improved. They do not show you what
changed, and what changed is legible: an early mote wanders in a near
straight line and eats whatever it crosses, and a late one sweeps a patch,
turns back on itself when the food runs out, and leaves the poison alone.

The main view is a TRAIL -- one picture of a whole lifetime rather than a
hundred frames. The food layout is drawn underneath, the path over it, and
every mouthful is marked with what it turned out to be.

    o +     an untouched patch of flavour A, of flavour B
    *       a cell the mote ate and it was food
    X       a cell the mote ate and it was poison
    .       walked over, nothing there
    S  @    where it started, where it ended (or died)
"""
from __future__ import annotations

import numpy as np

from mote.brain import Brains
from mote.world import GRID, Episode

G, R, Y, B, DIM, BOLD, OFF = ("\033[32m", "\033[31m", "\033[33m",
                              "\033[36m", "\033[2m", "\033[1m", "\033[0m")
ARROWS = "→↘↓↙←↖↑↗"


def _ramp(v):
    return " .:-=+*#%@"[min(9, int(v * 9.999))]


def trail(brain: Brains, ep: Episode, world=0, colour=True):
    """-> (list of text rows, summary dict) for one lifetime."""
    sc, ex = ep.run(brain.take([0]), trace=(0, world))
    fr = ex["frames"]
    c = (lambda s, k: k + s + OFF) if colour else (lambda s, k: s)

    pol0 = fr[0]["pol"]
    a_is_food = pol0 > 0
    cell = {}
    for f in fr:
        cx, cy = int(np.floor(f["x"])) % GRID, int(np.floor(f["y"])) % GRID
        key = (cy, cx)
        if f["ate"]:
            was_good = f["good"] >= f["bad"]
            cell[key] = "ate_good" if was_good else "ate_bad"
        elif key not in cell:
            cell[key] = "walked"

    A0, B0 = ep.A0[world], ep.B0[world]
    marks = {}
    for f, ch in ((fr[0], "S"), (fr[-1], "@")):
        xx, yy = int(np.floor(f["x"])) % GRID, int(np.floor(f["y"])) % GRID
        marks[(yy, xx)] = c(ch, BOLD + (Y if ch == "S" else B))

    rows = []
    for yy in range(GRID):
        line = []
        for xx in range(GRID):
            k = cell.get((yy, xx))
            if (yy, xx) in marks:
                line.append(marks[(yy, xx)])
            elif k == "ate_good":
                line.append(c("*", BOLD + G))
            elif k == "ate_bad":
                line.append(c("X", BOLD + R))
            elif A0[yy, xx] > 0.08:
                line.append(c("o", G if a_is_food else R))
            elif B0[yy, xx] > 0.08:
                line.append(c("+", R if a_is_food else G))
            elif k == "walked":
                line.append(c(".", DIM))
            else:
                line.append(" ")
        rows.append("".join(line))

    good_bites = sum(1 for f in fr if f["ate"] and f["good"] >= f["bad"])
    bad_bites = sum(1 for f in fr if f["ate"] and f["good"] < f["bad"])
    died = next((f["t"] for f in fr if not f["alive"]), None)
    summary = {
        "score": float(sc[0, world]),
        "good_bites": good_bites, "bad_bites": bad_bites,
        "cells_visited": len(cell),
        "died_at": died, "flavour_A_is_food": bool(a_is_food),
        "flips": len(ep.flip_at),
    }
    return rows, summary


def show(brain: Brains, ep: Episode, world=0, title="", colour=True):
    rows, s = trail(brain, ep, world, colour)
    head = f"{title}  d={ep.dial['d']:.2f}"
    print(f"{BOLD}{head}{OFF}" if colour else head)
    for r in rows:
        print("  " + r)
    died = "survived" if s["died_at"] is None else f"died at tick {s['died_at']}"
    print(f"  score {s['score']:+.3f}   ate {s['good_bites']} food, "
          f"{s['bad_bites']} poison   visited {s['cells_visited']} cells   "
          f"{died}")
    return s


def compare(a: Brains, b: Brains, ep: Episode, world=0,
            labels=("ancestor", "descendant"), colour=True):
    """Two motes, the same world, side by side."""
    ra, sa = trail(a, ep, world, colour)
    rb, sb = trail(b, ep, world, colour)
    pad = " " * 4
    w = GRID
    print(f"{BOLD}{labels[0]:<{w}}{OFF}{pad}{BOLD}{labels[1]}{OFF}"
          if colour else f"{labels[0]:<{w}}{pad}{labels[1]}")
    for x, y in zip(ra, rb):
        print(f"  {x}{pad}{y}")
    for lab, s in zip(labels, (sa, sb)):
        died = "survived" if s["died_at"] is None else f"died t={s['died_at']}"
        print(f"  {lab:<12} score {s['score']:+.3f}  food {s['good_bites']:>3}  "
              f"poison {s['bad_bites']:>3}  cells {s['cells_visited']:>3}  {died}")
    return sa, sb
