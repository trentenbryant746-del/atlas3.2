"""
English -> a playable game, verified by running it.

belt-atlas established the shape: picks in, code out, and a round-trip back
to picks proving the compression was real rather than asserted. Its check was
Godot's parser. Godot is not on this machine and a parser is a weak check
anyway -- it proves the text is syntactically legal, not that the game works.

So the check here EXECUTES. A generated game must:

    parse              ast.parse accepts it
    round-trip         re-reading the emitted source recovers the same picks
    run headless       N deterministic ticks without raising
    stay consistent    its own invariants hold at every tick
    be reproducible    same seed, same trace, byte for byte

Five checks, and the last three are things a parser cannot see.

WHAT THIS CANNOT DO, and it is the part worth saying out loud: it generates a
game that WORKS. Whether the game is one anybody WANTS is not derivable from
anything here. Fun is empirical -- established by putting it in front of
people -- in exactly the way a dose is empirical and a statute is stipulated.
The system can produce and verify the possibility space; which point in it is
worth shipping is measured, never computed.
"""
from __future__ import annotations

import ast
import hashlib
import io
import re
import contextlib

# ---- the pick language ------------------------------------------------
PICKS = {
    "grid":    ("w", "h"),
    "player":  ("speed",),
    "goal":    ("count",),
    "hazard":  ("count", "damage"),
    "enemy":   ("count", "speed"),
    "health":  ("hp",),
    "timer":   ("ticks",),
}

CUES = [
    (re.compile(r'\b(\d+)\s*x\s*(\d+)\b'),            lambda m: ("grid", [int(m.group(1)), int(m.group(2))])),
    (re.compile(r'\b(\d+)\s+coins?|\bcollect (\d+)'), lambda m: ("goal", [int(m.group(1) or m.group(2))])),
    (re.compile(r'\b(\d+)\s+enem(?:y|ies)'),          lambda m: ("enemy", [int(m.group(1)), 1])),
    (re.compile(r'\b(\d+)\s+(?:spikes?|traps?|hazards?)'), lambda m: ("hazard", [int(m.group(1)), 1])),
    (re.compile(r'\b(\d+)\s+(?:hp|health|lives)'),    lambda m: ("health", [int(m.group(1))])),
    (re.compile(r'\b(\d+)\s+ticks?|\bwithin (\d+)'),  lambda m: ("timer", [int(m.group(1) or m.group(2))])),
]

DEFAULTS = {"grid": [12, 8], "player": [1], "goal": [3], "health": [3],
            "timer": [200]}


def parse_english(text):
    """-> (picks dict, notes). Explicit numbers win; the rest default."""
    picks, notes = dict(DEFAULTS), []
    for pat, fn in CUES:
        m = pat.search(text)
        if m:
            k, v = fn(m)
            picks[k] = v
            notes.append(f"{k} from {m.group(0)!r}")
    for word, key, val in (("enemy", "enemy", [2, 1]), ("enemies", "enemy", [2, 1]),
                           ("spike", "hazard", [3, 1]), ("hazard", "hazard", [3, 1])):
        if word in text.lower() and key not in picks:
            picks[key] = val
            notes.append(f"{key} implied by the word {word!r}")
    return picks, notes


def render(picks, seed=7):
    """picks -> a deterministic, headless, runnable game"""
    g = picks["grid"]
    lines = [
        "import hashlib",
        "",
        f"SEED = {seed}",
        f"W, H = {g[0]}, {g[1]}",
        f"SPEED = {picks['player'][0]}",
        f"GOALS = {picks['goal'][0]}",
        f"HP = {picks['health'][0]}",
        f"TICKS = {picks['timer'][0]}",
        f"ENEMIES = {picks.get('enemy', [0, 1])[0]}",
        f"HAZARDS = {picks.get('hazard', [0, 1])[0]}",
        "",
        "def _r(n, salt):",
        "    h = hashlib.sha256(f'{SEED}|{salt}|{n}'.encode()).digest()",
        "    return int.from_bytes(h[:4], 'big')",
        "",
        "def new_state():",
        "    return {'x': 0, 'y': 0, 'hp': HP, 'score': 0, 'tick': 0,",
        "            'goals': [( _r(i,'gx') % W, _r(i,'gy') % H) for i in range(GOALS)],",
        "            'haz':   [( _r(i,'hx') % W, _r(i,'hy') % H) for i in range(HAZARDS)],",
        "            'foes':  [( _r(i,'ex') % W, _r(i,'ey') % H) for i in range(ENEMIES)]}",
        "",
        "def step(s):",
        "    s['tick'] += 1",
        "    d = _r(s['tick'], 'move') % 4",
        "    dx, dy = [(1,0),(-1,0),(0,1),(0,-1)][d]",
        "    s['x'] = max(0, min(W-1, s['x'] + dx*SPEED))",
        "    s['y'] = max(0, min(H-1, s['y'] + dy*SPEED))",
        "    here = (s['x'], s['y'])",
        "    if here in s['goals']:",
        "        s['goals'].remove(here); s['score'] += 1",
        "    if here in s['haz']:",
        "        s['hp'] -= 1",
        "    return s",
        "",
        "def invariants(s):",
        "    return (0 <= s['x'] < W and 0 <= s['y'] < H",
        "            and s['hp'] <= HP and s['score'] <= GOALS",
        "            and s['tick'] <= TICKS)",
        "",
        "def play(ticks=TICKS):",
        "    s = new_state()",
        "    trace = []",
        "    for _ in range(ticks):",
        "        if s['hp'] <= 0 or not s['goals']:",
        "            break",
        "        step(s)",
        "        if not invariants(s):",
        "            raise AssertionError(f'invariant broken at tick {s[\"tick\"]}')",
        "        trace.append((s['x'], s['y'], s['hp'], s['score']))",
        "    return s, trace",
    ]
    return "\n".join(lines) + "\n"


def recover(src):
    """source -> picks. The round-trip half; nothing else reads the code."""
    def grab(name):
        m = re.search(rf'^{name} = (.+)$', src, re.M)
        return m.group(1) if m else None
    wh = re.search(r'^W, H = (\d+), (\d+)$', src, re.M)
    if not wh:
        return None
    out = {"grid": [int(wh.group(1)), int(wh.group(2))],
           "player": [int(grab("SPEED"))],
           "goal": [int(grab("GOALS"))],
           "health": [int(grab("HP"))],
           "timer": [int(grab("TICKS"))]}
    e, h = int(grab("ENEMIES")), int(grab("HAZARDS"))
    if e:
        out["enemy"] = [e, 1]
    if h:
        out["hazard"] = [h, 1]
    return out


def verify(picks, src):
    """-> (ok, [check results]). Five checks, three of which need execution."""
    res = []

    try:
        ast.parse(src)
        res.append(("parses", True, ""))
    except SyntaxError as e:
        return False, [("parses", False, str(e))]

    back = recover(src)
    same = back == {k: v for k, v in picks.items() if k in (back or {})}
    res.append(("round-trips to the same picks", bool(same),
                "" if same else f"{back} != {picks}"))

    ns = {}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(src, "<game>", "exec"), ns)
        s, trace = ns["play"]()
        res.append(("runs headless", True, f"{len(trace)} ticks"))
    except Exception as e:
        res.append(("runs headless", False, f"{type(e).__name__}: {e}"))
        return False, res

    res.append(("invariants held every tick", ns["invariants"](s), ""))

    ns2 = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(src, "<game>", "exec"), ns2)
    _s2, trace2 = ns2["play"]()
    det = (hashlib.sha256(str(trace).encode()).hexdigest() ==
           hashlib.sha256(str(trace2).encode()).hexdigest())
    res.append(("reproducible from the seed", det, ""))

    return all(r[1] for r in res), res


# words that carry INTENT the pick language cannot express. Not a failure of
# vocabulary -- there is no number of cues that turns "relaxing" into a grid
# size, because the mapping does not exist to be learned. Fun is empirical:
# established by putting the thing in front of people.
AESTHETIC = re.compile(
    r'\b(fun|hard|easy|relaxing|tense|scary|cosy|cozy|beautiful|addictive|'
    r'boring|exciting|satisfying|charming|atmospheric|immersive|good|great|'
    r'better|best|engaging|compelling|polished)\b', re.I)
REFERENTIAL = re.compile(r'\b(like|similar to|in the style of|reminiscent of)\b', re.I)
NARRATIVE = re.compile(
    r'\b(story|character|cat|dog|hero|villain|rescue|escape|journey|home|'
    r'lost|find|save|quest|world|adventure)\b', re.I)


def understood(description, notes):
    """what fraction of the description turned into a decision"""
    words = [w for w in re.findall(r"[a-z0-9']+", description.lower())]
    unmet = []
    if AESTHETIC.search(description):
        unmet.append(("aesthetic", AESTHETIC.findall(description),
                      "not derivable: fun is empirical, measured by playtest"))
    if REFERENTIAL.search(description):
        unmet.append(("referential", REFERENTIAL.findall(description),
                      "requires knowing the referenced game; no source given"))
    if NARRATIVE.search(description):
        unmet.append(("narrative", NARRATIVE.findall(description)[:4],
                      "the pick language has no representation for theme"))
    return {"words": len(words), "picks_from_text": len(notes),
            "unmet": unmet}


def make(description, seed=7):
    picks, notes = parse_english(description)
    src = render(picks, seed)
    ok, checks = verify(picks, src)
    u = understood(description, notes)
    return {"picks": picks, "notes": notes, "source": src,
            "ok": ok, "checks": checks, "understood": u,
            # a game that runs is not a game that was ASKED FOR. When nothing
            # in the description became a decision, saying so is the answer;
            # emitting the default game silently is how you ship a generic
            # thing and call it a response.
            "matches_request": u["picks_from_text"] > 0 and not u["unmet"],
            "tokens_in": len(description.split()),
            "lines_out": src.count("\n")}
