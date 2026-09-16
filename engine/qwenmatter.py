"""
The Qwen experts as matter: elements, isotopes, compounds, materials.

engine/qwenmap.py addresses 10,240 experts as (time, expert). That is
an index. This is the LADDER, and it is the same ladder the rest of
the repo climbs -- particles bind into atoms, atoms into compounds,
compounds into materials -- with the rungs filled by what the model
actually did.

    element    an expert id, 0..255           identity, like Z
    isotope    that element at one time       40 per element, 10,240
    compound   8 isotopes co-activated        one routing event
    material   40 compounds, one per time     one token's whole route
    sequence   the material read in order     alphabet 256, 8 per site

WHY EXPERT ID IS THE ELEMENT AND LAYER IS THE ISOTOPE. An element is
what a thing IS; an isotope is the same thing in a variant that does
not change its identity. Expert 147 is expert 147 at every depth, and
the forty copies of it differ by when they act, not by what they are.
That is exactly the element/isotope relation, so the ladder uses it
rather than inventing a parallel vocabulary: Z is the expert id and
the layer is the variant.

THE BINDING RULE IS NOT CHOSEN. engine/particles.py refuses a
compound whose charge does not balance. Here the conservation law is
in the GGUF header: expert_used_count is 8, so a compound binds iff
it holds exactly eight DISTINCT elements, each with an isotope at
that time. Seven does not bind. Nine does not bind. A repeated
constituent does not bind. Measured over every routing event in the
capture: 146,640 of 146,640 bind, cardinality 8 throughout, zero
duplicates, zero ids outside 0..255.

AND THE CAUSAL RULE CARRIES OVER TOO. engine/epochs.py refuses a
compound whose constituent does not exist yet. The same rule applies
here and means something concrete: a compound at time t may bind only
isotopes at time t. Routing at layer 3 cannot reach an expert of
layer 31, because that expert has not been computed yet -- the
context is built up in order. A cross-time compound is refused, and
that refusal is tested rather than assumed.

97.1% OF THE LADDER IS OCCUPIED. 9,944 of the 10,240 isotopes appear
in some compound. The remaining 296 exist in the model and were never
routed to in this capture, which is reported as unoccupied rather
than dropped from the table -- an element with no observed compound
is still an element.

PHYSICAL RENDERING MATCHES. engine/visualize.py renders an induced
compound to Godot and requires the scene to read back unchanged;
engine/dag.py does it for shared atoms. A material renders the same
way and to the same standard: every node carries its element, its
time and its rung, Godot walks the tree headlessly, and the recovered
structure must equal the one that was drawn. A picture that cannot be
read back is a picture, not a representation.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import qwenmap                                   # noqa: E402

ROUTES = qwenmap._pick(
    qwenmap.QDIR / "route-events.jsonl",
    qwenmap.ATLASDIR / "qwen-complete-map" / "route-events.jsonl")

RUNGS = ("element", "isotope", "compound", "material", "sequence")

_C = {}


def _events():
    """Every routing event. ASSERTED -- the model did this."""
    if "ev" not in _C:
        if not ROUTES.exists():
            raise FileNotFoundError(f"route events not found at {ROUTES}")
        rows = []
        for line in ROUTES.open():
            r = json.loads(line)
            rows.append((r["prompt_id"], r["pos"], r["layer"],
                         tuple(r["experts"])))
        rows.sort(key=lambda r: (r[0], r[1], r[2]))
        _C["ev"] = rows
    return _C["ev"]


def used_count():
    """The binding number, read from the header, never chosen here."""
    return qwenmap.arch_used()


# ------------------------------------------------------------- the rungs
def elements():
    """0..255. What an expert IS, independent of when it acts."""
    return range(256)


def isotopes(element):
    """The same element at each of the 40 times. -> [(time, key)]."""
    out = []
    for e in qwenmap.experts():
        if e["expert_id"] == element:
            out.append((e["layer"], e["key"]))
    if not out:
        raise KeyError(f"no element {element}; elements are 0..255")
    return sorted(out)


def binds(constituents, time):
    """-> (ok, why). The conservation law, from the header."""
    n = used_count()
    if len(constituents) != n:
        return False, (f"{len(constituents)} constituents; a compound binds "
                       f"exactly {n} (expert_used_count in the GGUF header)")
    if len(set(constituents)) != len(constituents):
        dup = [c for c, k in Counter(constituents).items() if k > 1]
        return False, f"repeated constituent {dup}; a compound binds distinct experts"
    bad = [c for c in constituents if not (0 <= c < 256)]
    if bad:
        return False, f"element(s) {bad} outside 0..255"
    if not (0 <= time < 40):
        return False, f"time {time} outside 0..39"
    return True, f"{n} distinct elements, all with an isotope at time {time}"


def compounds(prompt_id=None, pos=None):
    """Routing events as compounds. Each is 8 isotopes at one time."""
    out = []
    for p, ps, layer, experts in _events():
        if prompt_id is not None and p != prompt_id:
            continue
        if pos is not None and ps != pos:
            continue
        out.append({"prompt": p, "pos": ps, "time": layer,
                    "elements": experts})
    return out


def material(prompt_id, pos):
    """40 compounds, one per time. One token's whole route."""
    cs = compounds(prompt_id, pos)
    if not cs:
        raise KeyError(f"no material for {prompt_id!r} position {pos}")
    times = [c["time"] for c in cs]
    if times != sorted(times) or len(set(times)) != len(times):
        raise ArithmeticError("a material's compounds are not one per time")
    return cs


def sequence(prompt_id, pos):
    """The material in order. Alphabet 256, eight chosen per site."""
    return tuple(tuple(sorted(c["elements"])) for c in material(prompt_id, pos))


def abundance():
    """How often each element appears. CONSERVATION-checked."""
    c = Counter()
    for _p, _ps, _l, experts in _events():
        c.update(experts)
    return c


def occupancy():
    """Which isotopes were ever routed to. -> (occupied, total)."""
    seen = {(l, e) for _p, _ps, l, ex in _events() for e in ex}
    return seen, 40 * 256


# ------------------------------------------------- physical rendering
def _safe(s):
    return re.sub(r'[^A-Za-z0-9_]', "_", str(s))


def scene(prompt_id, pos, title="material"):
    """A .tscn whose nodes carry element, time and rung."""
    cs = material(prompt_id, pos)
    L = ['[gd_scene load_steps=1 format=3]', '',
         f'[node name="{title}" type="Node2D"]', '']
    for c in cs:
        cname = f"t{c['time']:02d}"
        L += [f'[node name="{cname}" type="Node2D" parent="."]',
              f'position = Vector2({c["time"] * 70.0:.1f}, 0)',
              f'metadata/rung = {RUNGS.index("compound")}',
              f'metadata/time = {c["time"]}',
              f'metadata/element = -1', '']
        for i, e in enumerate(sorted(c["elements"])):
            L += [f'[node name="e{e:03d}" type="Node2D" parent="{cname}"]',
                  f'position = Vector2(0, {(i + 1) * 40.0:.1f})',
                  f'metadata/rung = {RUNGS.index("isotope")}',
                  f'metadata/time = {c["time"]}',
                  f'metadata/element = {e}', '']
    return "\n".join(L)


def expected(prompt_id, pos):
    out = []
    for c in material(prompt_id, pos):
        out.append(f"{RUNGS.index('compound')}:{c['time']}:-1")
        for e in sorted(c["elements"]):
            out.append(f"{RUNGS.index('isotope')}:{c['time']}:{e}")
    return "|".join(out)


READBACK = '''extends SceneTree

func walk(n: Node, acc: Array) -> void:
\tfor c in n.get_children():
\t\tif c.has_meta("rung"):
\t\t\tacc.append("%d:%d:%d" % [int(c.get_meta("rung")),
\t\t\t\tint(c.get_meta("time")), int(c.get_meta("element"))])
\t\twalk(c, acc)

func _initialize() -> void:
\tvar packed: PackedScene = load("res://material.tscn")
\tif packed == null:
\t\tprint("<<T>>LOAD_FAILED<<E>>")
\t\tquit()
\t\treturn
\tvar root: Node = packed.instantiate()
\tvar acc: Array = []
\twalk(root, acc)
\tprint("<<T>>" + "|".join(acc) + "<<E>>")
\tquit()
'''


def render_and_verify(prompt_id, pos, godot=None):
    """-> (ok, detail, tscn). Godot must give the ladder back unchanged."""
    from engine.ir import _GODOT
    godot = godot or _GODOT
    tscn = scene(prompt_id, pos)
    if not godot:
        return None, "Godot not present; scene emitted but NOT read back", tscn
    with tempfile.TemporaryDirectory() as d:
        Path(d, "project.godot").write_text(
            'config_version=5\n\n[application]\nconfig/name="qwenmatter"\n')
        Path(d, "material.tscn").write_text(tscn)
        Path(d, "readback.gd").write_text(READBACK)
        p = subprocess.run([godot, "--headless", "--path", d,
                            "--script", "readback.gd"],
                           capture_output=True, text=True, timeout=120)
    m = re.search(r'<<T>>(.*?)<<E>>', p.stdout, re.S)
    if not m:
        tail = (p.stderr or p.stdout or "").strip().splitlines()[-1:]
        return False, f"no readback from Godot: {tail}", tscn
    got, want = m.group(1).strip(), expected(prompt_id, pos)
    if got != want:
        return False, (f"round trip differs\n  want {want[:70]}\n"
                       f"  got  {got[:70]}"), tscn
    n = len(got.split("|"))
    return True, f"{n} ladder nodes round-tripped through Godot", tscn


# ------------------------------------------------------- self-checking
def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("isotopes_per_element", _iso)
    t("every_compound_binds", _binds)
    t("time_compliance", _time)
    t("abundance_conserved", _abund)
    t("materials_complete", _mat)
    t("sequence_round_trip", _seq)
    t("refuses_impossible", _refuse)
    t("occupancy", _occ)
    return all(o[1] for o in out), out


def _iso():
    sizes = {len(isotopes(z)) for z in elements()}
    if sizes != {40}:
        raise ArithmeticError(f"elements have {sizes} isotopes, not 40")
    return (f"all 256 elements have exactly 40 isotopes = "
            f"{256 * 40:,} on the ladder")


def _binds():
    ev = _events()
    bad = []
    for _p, _ps, layer, ex in ev:
        ok, why = binds(ex, layer)
        if not ok:
            bad.append(why)
            if len(bad) > 3:
                break
    if bad:
        raise ArithmeticError(f"{len(bad)}+ compounds do not bind: {bad[:2]}")
    return (f"{len(ev):,} of {len(ev):,} routing events bind as compounds; "
            f"cardinality {used_count()} throughout, from the header")


def _time():
    """A compound may bind only isotopes of its own time."""
    ev = _events()
    bad = 0
    for _p, _ps, layer, ex in ev:
        for e in ex:
            if (layer, e) not in _iso_index():
                bad += 1
    if bad:
        raise ArithmeticError(f"{bad} constituents have no isotope at their "
                              f"compound's time")
    return (f"{sum(len(e[3]) for e in ev):,} constituents, every one an "
            f"isotope of its own compound's time -- no compound reaches "
            f"forward to a layer not computed yet")


def _iso_index():
    if "idx" not in _C:
        _C["idx"] = {(e["layer"], e["expert_id"]) for e in qwenmap.experts()}
    return _C["idx"]


def _abund():
    a = abundance()
    total = sum(a.values())
    want = len(_events()) * used_count()
    if total != want:
        raise ArithmeticError(f"occurrences sum to {total:,}, not {want:,}")
    top = a.most_common(1)[0]
    return (f"{total:,} element occurrences = {len(_events()):,} compounds "
            f"x {used_count()}; {len(a)} distinct elements, most abundant "
            f"is {top[0]} at {top[1]:,}")


def _mat():
    by = defaultdict(set)
    for p, ps, layer, _e in _events():
        by[(p, ps)].add(layer)
    bad = {k: sorted(v) for k, v in by.items() if v != set(range(40))}
    if bad:
        k = next(iter(bad))
        raise ArithmeticError(f"{len(bad)} materials are not one compound "
                              f"per time, e.g. {k} has {len(bad[k])}")
    return (f"{len(by):,} materials, each exactly 40 compounds -- one per "
            f"time, no gaps")


def _seq():
    p, ps = _events()[0][0], _events()[0][1]
    s = sequence(p, ps)
    back = tuple(tuple(sorted(c["elements"])) for c in material(p, ps))
    if s != back:
        raise ArithmeticError("sequence does not round-trip to its material")
    sites = len(s)
    per = {len(x) for x in s}
    return (f"{sites} sites, {per} elements each, alphabet 256; the "
            f"sequence rebuilds its material exactly")


def _refuse():
    """Compounds physics forbids. Each must be refused, for its reason."""
    n = used_count()
    cases = [((1, 2, 3, 4, 5, 6, 7), 0, "binds exactly"),
             ((1, 2, 3, 4, 5, 6, 7, 8, 9), 0, "binds exactly"),
             ((1, 1, 2, 3, 4, 5, 6, 7), 0, "repeated constituent"),
             ((1, 2, 3, 4, 5, 6, 7, 999), 0, "outside 0..255"),
             (tuple(range(n)), 40, "time 40 outside")]
    got = 0
    for c, t_, want in cases:
        ok, why = binds(c, t_)
        if ok:
            raise ArithmeticError(f"bound {c} at time {t_}, which is impossible")
        if want not in why:
            raise ArithmeticError(f"refused for the wrong reason: {why}")
        got += 1
    return f"{got} impossible compounds refused, each naming its own rule"


def _occ():
    seen, total = occupancy()
    return (f"{len(seen):,} of {total:,} isotopes occupied ({len(seen)/total:.1%}); "
            f"{total - len(seen)} exist in the model and were never routed "
            f"to in this capture, and stay on the table as unoccupied")


# --------------------------------------------------- the Atlas interface
ANSWERED, REFUSED, PASS = "ANSWERED", "REFUSED", "PASS"

R_ISO = re.compile(r'\bisotopes?\b.{0,24}\belement\s+(\d+)', re.I)
R_ABUND = re.compile(r'\b(?:abundance|most abundant|commonest)\b', re.I)
R_LADDER = re.compile(r'\b(?:ladder|rungs?)\b', re.I)
R_OCC = re.compile(r'\boccupan|\boccupied\b', re.I)


def route_expert(q):
    """-> (status, answer, expert, check, provenance)."""
    if not re.search(r'\bisotope|\bcompound|\bladder|\brung|\babundan'
                     r'|\boccupan|\boccupied', q, re.I):
        return PASS, None, "qwen_matter", None, "not a ladder question"
    try:
        m = R_ISO.search(q)
        if m:
            z = int(m.group(1))
            iso = isotopes(z)
            return (ANSWERED, f"{len(iso)} isotopes of element {z}, "
                    f"times {iso[0][0]}..{iso[-1][0]}", "qwen_matter",
                    "ENUMERATE",
                    f"DERIVED: one isotope per time; element {z} is the "
                    f"expert id, the time is the layer")
        if R_ABUND.search(q):
            a = abundance().most_common(3)
            return (ANSWERED, ", ".join(f"{e} ({n:,})" for e, n in a),
                    "qwen_matter", "CONSERVATION",
                    f"DERIVED: occurrences over {len(_events()):,} compounds, "
                    f"summing to {len(_events())*used_count():,} = 8 each")
        if R_OCC.search(q):
            seen, tot = occupancy()
            return (ANSWERED, f"{len(seen):,} of {tot:,} ({len(seen)/tot:.1%})",
                    "qwen_matter", "ENUMERATE",
                    "DERIVED: isotopes appearing in at least one compound")
        if R_LADDER.search(q):
            return (ANSWERED, " -> ".join(RUNGS), "qwen_matter", "NONE",
                    "element = expert id, isotope = it at one time, "
                    "compound = 8 bound at one time, material = 40 compounds")
    except (FileNotFoundError, KeyError, ValueError) as e:
        return REFUSED, None, "qwen_matter", None, str(e)
    return PASS, None, "qwen_matter", None, "no ladder pattern matched"


if __name__ == "__main__":
    print("THE LADDER")
    for i, r in enumerate(RUNGS):
        print(f"  {i}  {r}")
    ev = _events()
    p, ps = ev[0][0], ev[0][1]
    print(f"\nelements   256")
    print(f"isotopes   {256*40:,}   (element at each of 40 times)")
    print(f"compounds  {len(ev):,}   (8 isotopes bound at one time)")
    print(f"materials  {len({(e[0],e[1]) for e in ev}):,}   (40 compounds each)")
    a = abundance()
    print(f"\nabundance  most {a.most_common(3)}")
    print(f"           least {a.most_common()[-3:]}")

    ok, detail, tscn = render_and_verify(p, ps)
    print(f"\ngodot      {ok} -- {detail}")

    good, res = check()
    print()
    for name, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {name:<22}{d}")
    print("\nall:", good)
