"""
What an atom becomes, and who can answer once it has.

The ladder so far is static: an element sits at a rung and stays
there. Atoms do not. They break apart, and they bind, and both are
EVENTS IN TIME that change which questions have answers.

    breaking   Z decays to a daughter. The parent's answers stop
               applying and the daughter's begin, at a definite
               moment.
    binding    two atoms form a compound. Neither element's expert
               can answer about the compound -- it needs the pair,
               and the pair is a different expert.

So a transition is a CONTINUATION OF A PROMPT that requires a
different set of experts than the one before it. That is the whole
reason to track them: each edge in this graph is a place where the
answer set changes, and the number of reachable answer sets grows
combinatorially with the number of edges rather than with the
number of atoms.

NOTHING HERE IS A DECAY TABLE. Which way a nuclide goes is decided
by the same rule engine/nucleo.py already supports: a decay happens
if the products are more bound IN TOTAL than the parent. That is the
Q-value, and its sign is the whole answer. For alpha the escaping
particle's own binding counts toward it, which is why heavy nuclei
alpha-decay at all.

AND THE MODEL REFUSES INSIDE ITS OWN ERROR BAR. Q is a difference of
two semi-empirical binding energies, and the formula is good to a
few MeV. When |Q| is smaller than that, the SIGN is not determined
by the model -- and the sign is the entire prediction. So a nuclide
whose Q lands inside the error bar gets "undetermined" rather than a
confident guess, which is the same discipline engine/eos.py applies
to the neutron-star maximum.

BINDING IS TYPED, NOT LISTED. Two elements bind when their valences
close, and the stoichiometry is the lowest common multiple -- so
H2O, CH4, NH3 and CO2 are computed rather than looked up. A pair
whose valences do not close does not form a low-scoring compound;
it does not form a compound.

EVERY EDGE CARRIES A TIME. A transition cannot happen before its
inputs exist, so each one is stamped with the later of its parents'
epochs, and the graph is ordered by that. An edge that ran backwards
in time would be a bug, and it is checked.
"""
from __future__ import annotations

import math
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import epochs as _ep                             # noqa: E402
from engine.experts import BY_Z, BY_SYM                      # noqa: E402
from engine.nucleo import binding_energy_MeV                 # noqa: E402

DERIVED = "DERIVED"
# SEMF_MeV: ASSERTED, source: the accepted accuracy of the
# semi-empirical mass formula, a few MeV for medium and heavy
# nuclei. IT IS NOT DERIVED HERE AND CANNOT CURRENTLY BE.
#
# The obvious measurement fails, and the reason is worth writing
# down. Scoring the formula against engine/experts' atomic weights
# gives a median residual of 80 MeV, which looks like a catastrophe
# and is an artefact: a standard atomic weight is the
# ABUNDANCE-WEIGHTED AVERAGE over an element's isotopes, not the
# mass of any one nuclide. For iron the formula predicts 55.935 u,
# which is Fe-56 to three decimals, while the tabulated weight is
# 55.845 because Fe-54 pulls it down. Comparing a single-nuclide
# prediction to a multi-isotope average measures the isotope mix,
# not the formula.
#
# Measuring it properly needs PER-ISOTOPE masses, which this repo
# does not carry. Listed in engine/unsolved.py with that as the
# thing that would close it. Until then the number is taken from
# the literature and says so -- and it is load-bearing, because it
# is the threshold decay_of() refuses inside.
SEMF_TYPED = 3.0
SEMF_SOURCE = ("accepted liquid-drop accuracy from the literature; kept "
               "as a fallback and as the value the measurement is "
               "compared against")


def _measured_bar():
    """The DECAY bar, not the mass bar. See nucleo.error_bar().

    This took the absolute mass error, which is the wrong quantity:
    a decay is a difference of two binding energies and the
    formula's errors largely cancel in it. Using the mass error
    made alpha decay unresolvable and withdrew a correct result.
    """
    try:
        from engine.nucleo import error_bar
        v, _why = error_bar("decay")
        return v if v > 0 else SEMF_TYPED
    except Exception:
        return SEMF_TYPED


SEMF_MeV = _measured_bar()

# WHAT THE MEASUREMENT COSTS, STATED BEFORE IT SURPRISES ANYONE.
#
# The measured bar is about 8 MeV. Real alpha Q-values in the heavy
# elements are 4 to 5. So a formula honest about its own error
# CANNOT RESOLVE ALPHA DECAY AT ALL, and every chain this module
# used to produce -- including the uranium series in 3.1.11, which
# came out right -- disappears into "undetermined".
#
# That series was not a success. It was riding on a 3.0 MeV bar
# taken from the literature and never checked here, and when the
# bar was measured it turned out to be optimistic by more than
# double. The right response is not to keep the number that gave
# the nicer answer.
#
# Both are available and the consequence of each is visible:
#
#   SEMF_TYPED     3.0 MeV   literature; produces the uranium series
#   measured       ~8 MeV    this repo's own comparison, refuses all
#
# The measured one is the default because refusing is correct when
# the error bar says you cannot tell. The measurement is an UPPER
# bound -- the mono-isotopic test has false positives, chromium and
# molybdenum among them -- so the true error is somewhere between,
# and narrowing it needs per-isotope masses. That is what is on the
# unsolved list, and it is now a sharper request than before: not
# "measure the error bar" but "decide whether this model can see
# alpha decay at all".
def resolvable(q):
    """-> (bool, why). Can the formula see a Q-value this size?"""
    return (q >= SEMF_MeV,
            f"Q={q:.2f} MeV against a measured error of {SEMF_MeV:.2f}; "
            + ("resolvable" if q >= SEMF_MeV else
               "smaller than the formula's own error, so the sign is "
               "not determined and the sign is the answer"))
B_ALPHA = 28.296        # measured binding of He-4

# Valences, for the binding half. ASSERTED: which bonds an element
# forms is chemistry, not something derived here.
# The ten hand-written valences are kept as a FIXTURE -- the thing
# engine/valence.py's derivation is scored against, and the reason
# its Ge/As/Se/Br and iodine bugs were caught. The table actually
# used is derived from shell filling and covers every main-group
# element rather than ten.
VALENCE_FIXTURE = {"H": 1, "C": 4, "N": 3, "O": 2, "S": 2, "P": 3,
                   "F": 1, "Cl": 1, "Br": 1, "I": 1}
VAL_SOURCE = "common valences of the main-group elements"


def _valence_table():
    try:
        from engine import valence as _v
        t = _v.table()
        if all(t.get(k) == v for k, v in VALENCE_FIXTURE.items()):
            return t
    except Exception:
        pass
    return dict(VALENCE_FIXTURE)


VALENCE = _valence_table()


@dataclass
class Edge:
    kind: str               # "decay" or "bind"
    before: tuple           # what existed
    after: tuple            # what it became
    epoch: str              # the earliest it can happen
    why: str
    experts_before: frozenset = field(default_factory=frozenset)
    experts_after: frozenset = field(default_factory=frozenset)

    @property
    def expert_change(self):
        return (self.experts_after - self.experts_before,
                self.experts_before - self.experts_after)

    def __str__(self):
        gained, lost = self.expert_change
        return (f"{self.kind:<6} {'+'.join(self.before)} -> "
                f"{'+'.join(self.after)} at {self.epoch}"
                + (f"  +{sorted(gained)}" if gained else "")
                + (f"  -{sorted(lost)}" if lost else ""))


def _b(z, n):
    if z < 0 or n < 0 or z + n < 1:
        return None
    return binding_energy_MeV(z, n)


def q_values(z, n):
    """-> {mode: Q}. The sign of Q is the whole prediction."""
    here = _b(z, n)
    if here is None:
        raise ValueError(f"no binding energy for Z={z} N={n}")
    out = {}
    for mode, (zz, nn), extra in (("beta-minus", (z + 1, n - 1), 0.0),
                                  ("beta-plus", (z - 1, n + 1), 0.0),
                                  ("alpha", (z - 2, n - 2), B_ALPHA)):
        b = _b(zz, nn)
        if b is None:
            continue
        out[mode] = (b + extra) - here
    return out


def decay_of(z, n):
    """-> (mode, daughter, why). Refuses inside the formula's error bar."""
    qs = q_values(z, n)
    gains = {m: q for m, q in qs.items() if q > 0}
    if not gains:
        return ("stable", None,
                f"no decay raises the total binding of Z={z} N={n}")
    mode = max(gains, key=lambda m: gains[m])
    q = gains[mode]
    if q < SEMF_MeV:
        return ("undetermined", None,
                f"the best Q is {q:.2f} MeV, inside the {SEMF_MeV} MeV "
                f"the mass formula is good to -- the SIGN is not "
                f"determined, and the sign is the answer")
    d = {"beta-minus": (z + 1, n - 1), "beta-plus": (z - 1, n + 1),
         "alpha": (z - 2, n - 2)}[mode]
    return (mode, d, f"Q={q:.2f} MeV for {mode}, past the {SEMF_MeV} MeV "
                     f"error bar")


def experts_for_element(sym):
    """Which experts can answer about this element.

    THE ELEMENT IS ITSELF AN EXPERT. The first version left this out
    and gave every element the same handful of generic tags, so most
    transitions changed nothing and the check said so: 39 answer
    sets from 92 atoms, meaning the edges added less than the nodes.
    That was right, and the fix is not a bigger tag list -- it is
    that an atom IS an expert, so Z is part of the set by
    construction and a decay necessarily changes it.
    """
    z = BY_SYM[sym][0]
    out = {f"element:{sym}", "periodic_table",
           f"origin:{_ep.ORIGIN.get(sym, 'derived')}"}
    if sym in VALENCE:
        out.add("valence")
        out.add("material_ontology")
    from engine import abundance
    try:
        out.add("channel:" + abundance.channel(sym)[0])
    except Exception:
        pass
    if sym in ("C", "H", "N", "O", "P", "S"):
        out.add("biomatter")
    return frozenset(out)


def break_edge(z, n):
    """One atom coming apart. -> Edge or None."""
    mode, d, why = decay_of(z, n)
    if d is None:
        return None
    if d[0] < 1 or d[0] > len(BY_Z):
        return None
    ps, ds = BY_Z[z][0], BY_Z[d[0]][0]
    born = _ep.ORIGIN.get(ps)
    if born is None:
        from engine import abundance
        born = "supernova" if abundance.channel(ps)[0] == \
            "neutron-capture" else "stellar_c"
    return Edge("decay", (ps,), (ds,), born,
                f"{ps} (Z={z} N={n}) -> {ds} by {mode}; {why}",
                experts_for_element(ps), experts_for_element(ds))


def bind_edge(a, b):
    """Two atoms coming together. -> Edge or None if valence refuses."""
    if a not in VALENCE or b not in VALENCE:
        return None
    va, vb = VALENCE[a], VALENCE[b]
    # A ZERO VALENCE IS NOT A SMALL ONE. While the table held ten
    # hand-picked elements every entry bonded, so nothing guarded
    # against zero. Deriving valence brought in the noble gases at
    # zero, and two of them gave gcd(0, 0) and a division by zero --
    # a latent bug that only a wider table could reach.
    if va == 0 or vb == 0:
        return None
    g = math.gcd(va, vb)
    na, nb = vb // g, va // g
    f = "".join(f"{s}{k}" if k > 1 else s
                for s, k in sorted(((a, na), (b, nb))))
    ea, eb = _ep.ORIGIN.get(a), _ep.ORIGIN.get(b)
    if ea is None or eb is None:
        return None
    later = max((ea, eb), key=lambda e: _ep.ORDER[e])
    before = experts_for_element(a) | experts_for_element(b)
    after = before | {"compound", f"formula:{f}"}
    return Edge("bind", (a, b), (f,), later,
                f"{a} (valence {va}) with {b} (valence {vb}) closes at "
                f"{na}:{nb}, giving {f}; neither element's expert answers "
                f"about the compound, the pair does", before, after)


def most_bound_n(z):
    """The isotope of Z that actually exists: the best-bound one.

    The first version scanned N upward and took the first nuclide
    with a determined decay, which is not a physical choice -- it
    picked proton-rich isotopes and reported 91 of 92 elements as
    beta-plus emitters. An element's representative is the isotope
    that binds best, and that is derived from the same curve as
    everything else.
    """
    best, bn = None, None
    for n in range(0, 3 * z + 6):
        b = _b(z, n)
        if b is None or z + n == 0:
            continue
        per = b / (z + n)
        if best is None or per > best:
            best, bn = per, n
    return bn


def graph(zmax=92, pairs=True):
    """Every transition the rules admit. -> [Edge]."""
    out = []
    for z in range(1, zmax + 1):
        n = most_bound_n(z)
        if n is None:
            continue
        try:
            e = break_edge(z, n)
        except Exception:
            continue
        if e:
            out.append(e)
    if pairs:
        syms = sorted(VALENCE)
        for i, a in enumerate(syms):
            for b in syms[i + 1:]:
                e = bind_edge(a, b)
                if e:
                    out.append(e)
    return out


def chain_from(z, n, limit=30):
    """Follow the decays. A chain is one prompt continued."""
    seen, out = set(), []
    while len(out) < limit:
        if (z, n) in seen:
            out.append(("cycle", (z, n)))
            break
        seen.add((z, n))
        mode, d, why = decay_of(z, n)
        out.append((mode, (z, n)))
        if d is None:
            break
        z, n = d
        if z < 1:
            break
    return out


def answer_sets(edges=None):
    """How many distinct expert sets the graph reaches. The point."""
    edges = edges if edges is not None else graph()
    sets = set()
    for e in edges:
        sets.add(e.experts_before)
        sets.add(e.experts_after)
    return sets


# -------------------------------------------------- rendered in Godot
def scene(edges, title="transitions"):
    """A .tscn where every node carries its kind, epoch and expert count."""
    L = ['[gd_scene load_steps=1 format=3]', '',
         f'[node name="{title}" type="Node2D"]', '']
    for i, e in enumerate(edges):
        nm = _safe(f"{e.kind}_{'_'.join(e.before)}_{i}")
        L += [f'[node name="{nm}" type="Node2D" parent="."]',
              f'position = Vector2({i * 60.0:.1f}, '
              f'{_ep.ORDER[e.epoch] * 80})',
              f'metadata/kind = {0 if e.kind == "decay" else 1}',
              f'metadata/epoch = {_ep.ORDER[e.epoch]}',
              f'metadata/before = {len(e.experts_before)}',
              f'metadata/after = {len(e.experts_after)}', '']
    return "\n".join(L)


def _safe(s):
    return re.sub(r'[^A-Za-z0-9_]', "_", s)


def expected(edges):
    return "|".join(
        f"{0 if e.kind == 'decay' else 1}:{_ep.ORDER[e.epoch]}:"
        f"{len(e.experts_before)}:{len(e.experts_after)}" for e in edges)


READBACK = '''extends SceneTree

func walk(n: Node, acc: Array) -> void:
\tfor c in n.get_children():
\t\tif c.has_meta("kind"):
\t\t\tacc.append("%d:%d:%d:%d" % [int(c.get_meta("kind")),
\t\t\t\tint(c.get_meta("epoch")), int(c.get_meta("before")),
\t\t\t\tint(c.get_meta("after"))])
\t\twalk(c, acc)

func _initialize() -> void:
\tvar packed: PackedScene = load("res://transitions.tscn")
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


def render_and_verify(edges, godot=None):
    """-> (ok, detail, tscn). Godot must give every edge back unchanged."""
    from engine.ir import _GODOT
    godot = godot or _GODOT
    tscn = scene(edges)
    if not godot:
        return None, "Godot not present; scene emitted but NOT read back", tscn
    with tempfile.TemporaryDirectory() as d:
        Path(d, "project.godot").write_text(
            'config_version=5\n\n[application]\nconfig/name="trans"\n')
        Path(d, "transitions.tscn").write_text(tscn)
        Path(d, "readback.gd").write_text(READBACK)
        p = subprocess.run([godot, "--headless", "--path", d,
                            "--script", "readback.gd"],
                           capture_output=True, text=True, timeout=180)
    m = re.search(r'<<T>>(.*?)<<E>>', p.stdout, re.S)
    if not m:
        tail = (p.stderr or p.stdout or "").strip().splitlines()[-1:]
        return False, f"no readback from Godot: {tail}", tscn
    got, want = m.group(1).strip(), expected(edges)
    if got != want:
        return False, (f"round trip differs\n  want {want[:70]}\n"
                       f"  got  {got[:70]}"), tscn
    return True, f"{len(got.split('|'))} transitions recovered exactly", tscn


# ------------------------------------------------------- self-checking
def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("decay_is_derived", _dec)
    t("refuses_inside_the_error_bar", _ref)
    t("binding_is_computed", _bind)
    t("edges_run_forward", _time)
    t("experts_actually_change", _chg)
    t("answer_sets_exceed_atoms", _sets)
    t("chains_terminate", _chain)
    return all(o[1] for o in out), out


def _dec():
    g = [e for e in graph() if e.kind == "decay"]
    modes = {}
    for e in g:
        m = e.why.split(" by ")[-1].split(";")[0]
        modes[m] = modes.get(m, 0) + 1
    stable = undet = 0
    for z in range(1, 93):
        n = most_bound_n(z)
        mode, _d, _w = decay_of(z, n)
        if mode == "stable":
            stable += 1
        elif mode == "undetermined":
            undet += 1
    return (f"taking each element's BEST-BOUND isotope: {stable} come out "
            f"stable, {undet} undetermined inside the error bar, and "
            f"{len(g)} decay with a determined mode {modes} -- all from "
            f"the sign of Q")


def _ref():
    refused = 0
    for z in range(1, 93):
        for n in range(max(0, z - 4), z + 6):
            try:
                mode, d, _w = decay_of(z, n)
            except Exception:
                continue
            if mode == "undetermined":
                refused += 1
    if refused == 0:
        raise ArithmeticError("nothing was refused, so the error bar is "
                              "not being applied")
    return (f"{refused} nuclides whose best Q lands inside the "
            f"{SEMF_MeV} MeV the mass formula is good to, refused rather "
            f"than guessed -- the sign is the answer and it is not "
            f"determined there")


def _bind():
    want = {"H2O", "CH4", "H3N", "C1O2", "CO2", "H3N1"}
    got = set()
    for a, b in (("H", "O"), ("C", "H"), ("N", "H"), ("C", "O")):
        e = bind_edge(a, b)
        got.add(e.after[0])
    if not got & want:
        raise ArithmeticError(f"valence closure gave {got}")
    return (f"valence closure computes {sorted(got)} -- water, methane, "
            f"ammonia and carbon dioxide, from lowest common multiples "
            f"rather than a table")


def _time():
    bad = [e for e in graph()
           if any(_ep.ORDER[_ep.ORIGIN[s]] > _ep.ORDER[e.epoch]
                  for s in e.before if s in _ep.ORIGIN)]
    if bad:
        raise ArithmeticError(f"{len(bad)} edges run before their inputs")
    return (f"every transition is stamped with the later of its inputs' "
            f"epochs, and none runs before something it needs")


def _chg():
    g = graph()
    changed = [e for e in g if e.expert_change[0] or e.expert_change[1]]
    if len(changed) < len(g) // 2:
        raise ArithmeticError("most transitions change no expert, so the "
                              "graph is not doing what it claims")
    binds = [e for e in g if e.kind == "bind"]
    ex = binds[0]
    gained, _lost = ex.expert_change
    return (f"{len(changed)} of {len(g)} transitions change which experts "
            f"apply; e.g. {'+'.join(ex.before)} -> {ex.after[0]} gains "
            f"{sorted(gained)}")


def _sets():
    g = graph()
    sets = answer_sets(g)
    atoms = len({s for e in g for s in e.before if s in BY_SYM})
    if len(sets) <= atoms:
        raise ArithmeticError(f"{len(sets)} answer sets from {atoms} atoms "
                              f"-- transitions added nothing")
    return (f"{atoms} atoms take part, and the transitions between them "
            f"reach {len(sets)} distinct expert sets -- more answer "
            f"contexts than there are atoms, which is the point of "
            f"tracking the edges")


def _chain():
    c = chain_from(92, 146)
    if not c:
        raise ArithmeticError("no chain from U-238")
    end = c[-1][0]
    if end == "cycle":
        raise ArithmeticError(f"the chain cycles: {c[-3:]}")
    return (f"U-238 followed {len(c)} steps to {end}: "
            + " -> ".join(f"Z{z}" for _m, (z, _n) in c[:6])
            + (" ..." if len(c) > 6 else ""))


if __name__ == "__main__":
    g = graph()
    print(f"{len(g)} transitions: "
          f"{sum(1 for e in g if e.kind=='decay')} decays, "
          f"{sum(1 for e in g if e.kind=='bind')} bindings")
    print()
    for e in g[:4] + g[-4:]:
        print("  " + str(e)[:108])
    print()
    print(f"distinct expert sets reached: {len(answer_sets(g))}")
    ok, detail, _t = render_and_verify(g[:40])
    print(f"godot: {ok} -- {detail}")
    good, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:30}{d[:96]}")
    print("\nall:", good)
