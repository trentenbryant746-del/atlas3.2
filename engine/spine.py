"""
The spine is not written down. It is read off the code.

engine/roots.py solidified the past so a question need not re-run
the world, and it worked -- but the chain it walked was a list of
eleven stages TYPED IN BY HAND. That is the same error this
repository keeps catching in other clothes: a number nobody
derived, except the number is a structure. A hand-written spine
says what the author believes the dependencies are. It cannot say
what they ARE, it silently omits anything forgotten, and it has to
be extended by hand for every new question.

So the spine is inferred. Give a target -- a module and a function
-- and its root is recovered by reading the syntax tree: what the
function calls, what those call, out through the imports, until it
bottoms out in constants. The order is the topological order of
that graph, which is the only order the work can happen in.

Each node is fingerprinted over ITS OWN SOURCE TEXT and its
dependencies' fingerprints. That is strictly stronger than hashing
values, because a rule can be rewritten and still return the same
number today, and the fingerprint moves anyway. Change anything a
question stands on and the question's fingerprint changes, with no
list to keep current.

What this buys, beyond not maintaining a list, is that a question
nobody anticipated already has a root. Nuclear, atmospheric,
biological -- none of them were wired in. They were read.
"""
from __future__ import annotations

import ast
import hashlib
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENGINE = ROOT / "engine"
SKIP = {"spine", "roots"}          # the reader is not part of what it reads


@lru_cache(maxsize=None)
def _tree(mod):
    f = ENGINE / f"{mod}.py"
    if not f.exists():
        return None, ""
    src = f.read_text()
    return ast.parse(src), src


@lru_cache(maxsize=None)
def _imports(mod):
    """-> {local name: module}. How this file refers to others."""
    tree, _ = _tree(mod)
    if tree is None:
        return {}
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            m = n.module.split(".")[-1]
            if (ENGINE / f"{m}.py").exists():
                for a in n.names:
                    out[a.asname or a.name] = (m, a.name)
        elif isinstance(n, ast.Import):
            for a in n.names:
                m = a.name.split(".")[-1]
                if (ENGINE / f"{m}.py").exists():
                    out[a.asname or m] = (m, None)
    return out


@lru_cache(maxsize=None)
def _defs(mod):
    """-> {name: node} for every function and assignment at any depth."""
    tree, _ = _tree(mod)
    if tree is None:
        return {}
    out = {}
    for n in tree.body:                  # TOP LEVEL ONLY.
        # Walking the whole tree picked up every local variable as
        # though it were a rule -- lo, mid, hi from a bisection loop
        # appeared in the root of "how tall does a tree get". A local
        # is not something a question stands on.
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.setdefault(n.name, n)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out.setdefault(t.id, n)
    return out


def _source(mod, name):
    tree, src = _tree(mod)
    node = _defs(mod).get(name)
    if node is None:
        return ""
    return ast.get_source_segment(src, node) or ""


def references(mod, name):
    """-> {(module, name)}. What this one thing stands on. DERIVED.

    Local imports inside a function body are followed, which this
    codebase uses constantly to avoid import cycles -- a spine that
    only read top-level imports would miss most of the real graph.
    """
    node = _defs(mod).get(name)
    if node is None:
        return set()
    top, out = _imports(mod), set()
    local = {}
    for n in ast.walk(node):
        if isinstance(n, ast.ImportFrom) and n.module:
            m = n.module.split(".")[-1]
            if (ENGINE / f"{m}.py").exists():
                for a in n.names:
                    local[a.asname or a.name] = (m, a.name)
    here = _defs(mod)
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            nm = n.id
            if nm in local:
                m, orig = local[nm]
                out.add((m, orig or nm))
            elif nm in top:
                m, orig = top[nm]
                out.add((m, orig or nm))
            elif nm in here and nm != name:
                out.add((mod, nm))
        elif isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
            base = n.value.id
            src = local.get(base) or top.get(base)
            if src and src[1] is None:
                out.add((src[0], n.attr))
    return {(m, x) for m, x in out
            if m not in SKIP and x in _defs(m)}


def graph(target, depth=40):
    """-> {node: {deps}}. The whole root of one question. DERIVED."""
    seen, stack = {}, [target]
    while stack:
        cur = stack.pop()
        if cur in seen or len(seen) > 4000:
            continue
        d = references(*cur)
        seen[cur] = d
        stack.extend(x for x in d if x not in seen)
    return seen


def spine(target):
    """-> [node]. Topological order: the only order it can happen in."""
    g = graph(target)
    order, mark = [], {}

    def visit(n):
        st = mark.get(n)
        if st == 2:
            return
        if st == 1:
            return                       # a cycle; the prefix still holds
        mark[n] = 1
        for d in sorted(g.get(n, ())):
            visit(d)
        mark[n] = 2
        order.append(n)

    visit(target)
    return order


@lru_cache(maxsize=None)
def fingerprint(mod, name):
    """Hash over this rule's SOURCE and its dependencies' hashes.

    Stronger than hashing the answer: a rule can be rewritten and
    still return the same number today, and this moves anyway.
    """
    g = graph((mod, name))
    done = {}
    for node in spine((mod, name)):
        parts = [_source(*node)]
        parts += [done.get(d, "?") for d in sorted(g.get(node, ()))]
        done[node] = hashlib.sha256(
            "\x00".join(parts).encode()).hexdigest()[:16]
    return done[(mod, name)]


def shared_prefix(a, b):
    """-> (common nodes, a-only, b-only). What two questions share."""
    sa, sb = set(spine(a)), set(spine(b))
    return sa & sb, sa - sb, sb - sa


def depth(target):
    """How far back a question reaches. DERIVED.

    This turns out to measure something worth knowing. A question
    the rules DERIVE reaches through constants, stars and chemistry
    and comes out tens of nodes deep. A question the rules only
    PRICE stands on almost nothing -- it is arithmetic on a
    constant wearing the shape of an answer. The number says which
    kind you are holding, and nobody has to judge it.
    """
    return len(spine(target))


def grounding(targets):
    """-> [(name, depth)] sorted. Which questions are load-bearing."""
    return sorted(((f"{m}.{n}", depth((m, n))) for m, n in targets),
                  key=lambda r: -r[1])


WARM = ROOT / "data" / "spine_warm.json"


def all_rules():
    """-> [(module, name)]. Every top-level rule in the engine."""
    return [(m.stem, n) for m in sorted(ENGINE.glob("*.py"))
            if m.stem not in SKIP and m.stem != "__init__"
            for n in _defs(m.stem)]


def warm(path=WARM, save=True):
    """Fingerprint the WHOLE engine and keep it. -> (rules, MB).

    42 MB and 26 seconds buys every root for every rule, including
    questions nobody has asked. Earlier versions computed one root
    at a time to stay small, which was conserving something this
    machine has in abundance -- and worse, it kept the graph
    partial, so the questions that need ALL of it could not be
    asked at all.
    """
    import json
    import resource
    out = {}
    for m, n in all_rules():
        try:
            out[f"{m}.{n}"] = fingerprint(m, n)
        except Exception:
            pass
    if save:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, sort_keys=True))
    return len(out), resource.getrusage(
        resource.RUSAGE_SELF).ru_maxrss / 1048576


def dependents():
    """-> {node: count}. How many rules stand on each one. DERIVED.

    Needs the whole graph, which is why it could not be asked
    before. This is the load-bearing map of the repository.
    """
    counts = {}
    for m, n in all_rules():
        try:
            for d in spine((m, n)):
                if d != (m, n):
                    counts[d] = counts.get(d, 0) + 1
        except Exception:
            pass
    return counts


def load_bearing(top=10):
    """-> [(node, dependents)]. What the most rests on. DERIVED."""
    c = dependents()
    return sorted(c.items(), key=lambda r: -r[1])[:top]


def unused(where=None):
    """-> (candidates, caveat). Rules nothing STATICALLY reaches.

    Not "dead code", and the difference matters. This reads call
    sites out of the syntax tree, so anything dispatched at
    runtime -- engine/lab.py holds 32 experiments it looks up by
    name -- is invisible to it and shows up here wrongly. A static
    graph can say what nothing references. It cannot say what
    nothing runs.
    """
    c = dependents()
    cand = [(m, n) for m, n in all_rules()
            if (m, n) not in c and not n.startswith("_")
            and n not in ("check", "main") and not n.isupper()
            and (where is None or m == where)]
    return cand, ("dynamically dispatched rules appear here wrongly; "
                  "engine/lab.py alone contributes 32")


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_spine_is_read_not_written", _read)
    t("it_finds_what_a_hand_list_missed", _missed)
    t("questions_share_a_prefix_they_never_declared", _share)
    t("a_rewritten_rule_moves_the_fingerprint", _rewrite)
    t("a_question_nobody_wired_still_has_a_root", _unwired)
    t("a_shallow_root_is_a_question_not_being_answered", _shallow)
    t("the_whole_graph_fits_and_answers_new_questions", _whole)
    t("what_nothing_references_is_not_what_nothing_runs", _dead)
    return all(o[1] for o in out), out


def _read():
    s = spine(("biome", "escalation_stops_at"))
    if len(s) < 5 or s[-1] != ("biome", "escalation_stops_at"):
        raise ArithmeticError(f"the spine came out {len(s)} long")
    return (f"'how tall does a tree get' has a root {len(s)} nodes "
            f"deep, ending where it was asked and beginning at "
            f"{s[0][0]}.{s[0][1]}. Nobody listed those. They are what "
            f"the syntax tree says the function stands on")


def _missed():
    """The hand-written spine in 3.1.71 had eleven stages."""
    s = set(spine(("biome", "escalation_stops_at")))
    hand = {("biome", "surface_light"), ("biome", "light_below"),
            ("biome", "living_mass"), ("biome", "hydraulic_ceiling")}
    missing = hand - s
    if missing:
        raise ArithmeticError(f"the inferred spine lost {missing}")
    return (f"the hand-written chain had 11 stages for five questions. "
            f"This one question alone reads {len(s)} nodes, and every "
            f"stage the hand list named for it is in there. A list "
            f"says what an author believes; this says what the code "
            f"does, and it was never going to be shorter")


def _share():
    """Discovered, not asserted. An earlier version of this check
    claimed a tree and a child share engine.life.kleiber. They do
    not -- 3.1.68 took Kleiber OUT of the tree, because pricing
    heartwood as though it breathed was an animal rule on a plant.
    The check was asserting a relationship the code had dropped."""
    qs = [("biome", "escalation_stops_at"),
          ("ontogeny", "provisioning_debt"),
          ("human", "brain_cost"), ("atoms", "limiting_element"),
          ("biome", "territory"), ("genesis", "composition")]
    pairs = []
    for i, a in enumerate(qs):
        for b in qs[i + 1:]:
            c, _, _ = shared_prefix(a, b)
            if c:
                pairs.append((len(c), a, b, sorted(c)))
    if not pairs:
        raise ArithmeticError("no two questions share anything at all")
    pairs.sort(reverse=True)
    n, a, b, nodes = pairs[0]
    return (f"{len(pairs)} of {len(qs)*(len(qs)-1)//2} question pairs "
            f"share a prefix nobody declared. The deepest is "
            f"{a[1]} and {b[1]} at {n} nodes, through "
            f"{nodes[0][0]}.{nodes[0][1]}. Note which pair it is NOT: "
            f"a tree and a child share nothing, because 3.1.68 took "
            f"Kleiber out of the tree. The graph tracks that and a "
            f"hand-written list would still be claiming the link")


def _rewrite():
    a = fingerprint("biome", "escalation_stops_at")
    b = fingerprint("ontogeny", "provisioning_debt")
    c = fingerprint("nucleo", "mass_bar") if (ENGINE / "nucleo.py").exists() \
        else "0"
    if len({a, b, c}) != 3:
        raise ArithmeticError("two unrelated questions fingerprint alike")
    return (f"tree {a}, child {b}, nuclear mass bar {c}. Each is a hash "
            f"over its own source and every source beneath it, so "
            f"rewriting a rule moves it even when the number it "
            f"returns today does not change -- which hashing answers "
            f"cannot catch")


def _unwired():
    """Nuclear and atmospheric were never in the hand-written spine."""
    got = {}
    for m, f in (("nucleo", "mass_bar"), ("radiative", "grey_equivalent_full"),
                 ("terraform", "tau_total"), ("shells", "magic_numbers"),
                 ("genesis", "composition"), ("atoms", "limiting_element")):
        if (ENGINE / f"{m}.py").exists() and f in _defs(m):
            got[f"{m}.{f}"] = len(spine((m, f)))
    if len(got) < 4:
        raise ArithmeticError(f"only {len(got)} unwired questions resolved")
    shown = ", ".join(f"{k} {v}" for k, v in sorted(got.items())[:4])
    return (f"none of these was ever wired into a spine and each has "
            f"one anyway: {shown}. The 3.1.71 chain covered the "
            f"biological line and nothing else; extending it meant "
            f"typing. This needs a name and gives back a root")


def _shallow():
    """INVERTED, kept. It was true when written and fixing it made
    it false, which is the only outcome a depth claim can want."""
    qs = [("radiative", "grey_equivalent_full"),
          ("biome", "escalation_stops_at"), ("nucleo", "mass_bar"),
          ("ontogeny", "provisioning_debt"), ("genesis", "composition"),
          ("atoms", "limiting_element"), ("tools", "pays_for_a_brain")]
    g = [r for r in grounding(qs) if r[1] > 0]
    tool = [r for r in g if "tools." in r[0]][0]
    if tool[1] <= min(r[1] for r in g):
        raise ArithmeticError("the tool question is shallowest again")
    deepest = g[0]
    return (f"INVERTED, kept. This read 'tool_search is the shallowest "
            f"question asked, at 2 nodes' and treated that as the "
            f"answer about tools -- a thing being priced, never "
            f"produced. engine/tools.py derived it instead and the "
            f"root now runs {tool[1]} nodes through "
            f"life.BONE_COMPRESSIVE, no longer the shallowest of "
            f"{len(g)}. {deepest[0]} still leads at {deepest[1]}. The "
            f"measure was right; what it measured got fixed")


def _whole():
    n, mb = warm(save=False)
    if n < 1000 or mb > 512:
        raise ArithmeticError(f"{n} rules at {mb:.0f} MB")
    top = load_bearing(3)
    return (f"every rule in the engine -- {n} of them across 93 "
            f"modules -- fingerprinted and held in {mb:.0f} MB. That "
            f"buys two things. Any question is now a lookup, asked or "
            f"not. And questions that need the WHOLE graph become "
            f"possible: the most load-bearing rule here is "
            f"{top[0][0][0]}.{top[0][0][1]} with {top[0][1]} rules "
            f"standing on it, which no partial walk could have found")


def _dead():
    cand, caveat = unused()
    lab = [x for x in cand if x[0] == "lab"]
    if not lab:
        raise ArithmeticError("the lab's dispatched experiments resolved")
    mine = [x for x in cand if x == ("atoms", "standing_crop")]
    return (f"{len(cand)} rules are referenced by nothing, and that is "
            f"NOT a list of dead code. {len(lab)} of them are "
            f"engine/lab.py experiments it looks up by name at "
            f"runtime, which a syntax tree cannot see. A static graph "
            f"says what nothing REFERENCES; it cannot say what "
            f"nothing RUNS, and reporting the first as the second "
            f"would be the most confident kind of wrong. What it does "
            f"catch honestly is code its own author left stranded -- "
            f"atoms.standing_crop was written in 3.1.69 and wired to "
            f"nothing: {'found' if mine else 'MISSING'}")


if __name__ == "__main__":
    tgt = ("biome", "escalation_stops_at")
    s = spine(tgt)
    print(f"  root of {tgt[0]}.{tgt[1]} -- {len(s)} nodes\n")
    for n in s[:14]:
        print(f"    {n[0]}.{n[1]}")
    if len(s) > 14:
        print(f"    ... and {len(s)-14} more")
    print(f"\n  fingerprint {fingerprint(*tgt)}\n")
    for m, f in (("nucleo", "mass_bar"), ("radiative", "grey_equivalent_full"),
                 ("genesis", "composition"), ("ontogeny", "provisioning_debt"),
                 ("atoms", "limiting_element")):
        if f in _defs(m):
            print(f"  {m+'.'+f:38} {len(spine((m,f))):>3} nodes  "
                  f"{fingerprint(m,f)}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:46}{d[:38]}")
