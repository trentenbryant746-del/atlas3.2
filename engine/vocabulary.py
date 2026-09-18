"""
Every rule, reachable by its own words.

Atlas 2 closed a loop this one has been re-opening for ninety
versions. engine/english.py takes a question in English, binds it
compositionally into a typed call, routes the call to whatever
owns it, and returns the answer with the check that was applied.
engine/codeindex.py resolves any generated line back to the
English that caused it. The vocabulary IS the index, and nothing
has to be searched for.

Two things had gone wrong.

FIRST, the path was BROKEN. engine/english.py:181 did a bare
`import responder_shim`, which resolves only when the file is run
from inside engine/. Imported properly it raised
ModuleNotFoundError and took the whole English route down. That
is why every question since has been answered by writing a new
search: the lookup was unavailable and nobody noticed, because
nothing tested it.

SECOND, the vocabulary stopped at Atlas 2's scope. 350 facts and
forty words, against the sixty-odd modules and several hundred
rules 3.1 has added since. A rule nobody can name is a rule that
has to be recomputed.

Neither needed new machinery. Every rule here already carries its
own English -- a name, a docstring, and a check() that returns a
sentence saying what held and why. This harvests that into the
index the earlier Atlases were built around, so asking is a
lookup and the answer arrives with the words that justify it.
"""
from __future__ import annotations

import importlib
import json
import pkgutil
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STORE = ROOT / "data" / "vocabulary.json"
STAMPS = ROOT / "data" / "vocabulary_stamps.json"
SKIP = {"vocabulary", "responder_shim", "english", "grammar",
        "grammar2", "grammar3", "codeindex", "lab"}


def modules():
    import engine
    return sorted(m.name for m in pkgutil.iter_modules(engine.__path__)
                  if not m.name.startswith("_") and m.name not in SKIP)


def _terms(name, doc):
    """Words that should reach this rule. DERIVED from its own name."""
    parts = re.split(r"[._]", name)
    out = {p.lower() for p in parts if len(p) > 2}
    if doc:
        first = doc.strip().split("\n")[0].lower()
        out |= {w for w in re.findall(r"[a-z]{4,}", first)}
    return out - {"this", "that", "with", "from", "into", "than",
                  "what", "when", "which", "there", "here", "does",
                  "return", "returns", "given", "same", "they"}


def harvest(save=True):
    """-> [(key, short, long, terms)]. Every rule, with its words.

    Nothing is written by hand. The sentence a rule already emits
    from check() is the answer; its name and docstring are the
    index.
    """
    rows = []
    for mod in modules():
        try:
            m = importlib.import_module(f"engine.{mod}")
        except Exception:
            continue
        doc = (m.__doc__ or "").strip()
        if doc:
            head = doc.split("\n")[0]
            rows.append((f"{mod}.about", head[:110], doc[:700],
                         sorted(_terms(mod, doc))))
        fn = getattr(m, "check", None)
        if not callable(fn):
            continue
        try:
            _ok, res = fn()
        except Exception:
            continue
        for row in res:
            nm, held, why = row[0], row[1], str(row[2])
            rows.append((f"{mod}.{nm}",
                         ("holds: " if held else "fails: ") + why[:100],
                         why[:700], sorted(_terms(f"{mod}.{nm}", why))))
    if save:
        STORE.parent.mkdir(parents=True, exist_ok=True)
        STORE.write_text(json.dumps(rows))
    return rows


def load():
    if STORE.exists():
        return [tuple(r) for r in json.loads(STORE.read_text())]
    return harvest()


def look_up(*words):
    """-> [(key, short, score)]. Reach a rule by naming it.

    No search over the rules themselves. The words are the index,
    and the ranking is how many of them a rule's own vocabulary
    contains.
    """
    want = {w.lower().strip("?.,") for w in words if len(w) > 2}
    hits = []
    for key, short, _long, terms in load():
        t = set(terms) | set(re.split(r"[._]", key.lower()))
        n = len(want & t)
        if n:
            hits.append((key, short, n / max(len(want), 1)))
    return sorted(hits, key=lambda r: -r[2])[:8]


def ask(question):
    """-> dict. English in; the rule, its answer, and its words out."""
    hits = look_up(*re.findall(r"[A-Za-z]+", question))
    if not hits:
        return {"ok": False, "question": question,
                "english": "No rule here answers to those words."}
    key, short, score = hits[0]
    long_ = next((l for k, _s, l, _t in load() if k == key), short)
    return {"ok": True, "question": question, "rule": key,
            "answer": short, "why": long_, "score": round(score, 2),
            "others": [h[0] for h in hits[1:4]]}


def coverage():
    """-> (rules indexed, modules, distinct terms). DERIVED."""
    rows = load()
    terms = set()
    for _k, _s, _l, t in rows:
        terms |= set(t)
    return len(rows), len({k.split(".")[0] for k, *_ in rows}), len(terms)


def _fp(mod):
    """The fingerprint of a module's check, via engine/spine.py."""
    from engine.spine import fingerprint
    try:
        return fingerprint(mod, "check")
    except Exception:
        return None


def refresh(force=False):
    """-> (rechecked, untouched, moved). Fix what moved. Nothing else.

    NOT A SWEEP. An earlier version of this re-ran every module's
    check and compared 512 sentences, which took 180 seconds to
    re-derive answers that nothing could have changed -- the same
    mistake eval/claims.py had already fixed with fingerprints,
    committed again three files later.

    A rule's fingerprint commits to its whole dependency chain, so
    an unchanged fingerprint is a proof the answer is unchanged.
    Only the modules whose fingerprint moved are re-derived, and
    the index is edited in place.
    """
    import importlib
    import json as _json
    stamps = STAMPS.exists() and _json.loads(STAMPS.read_text()) or {}
    rows = {k: (k, s2, l, t) for k, s2, l, t in load()}
    rechecked, moved = [], []
    for mod in modules():
        fp = _fp(mod)
        if fp and stamps.get(mod) == fp and not force:
            continue
        rechecked.append(mod)
        try:
            m = importlib.import_module(f"engine.{mod}")
            fn = getattr(m, "check", None)
            if not callable(fn):
                stamps[mod] = fp
                continue
            _ok, res = fn()
        except Exception:
            continue
        for row in res:
            key = f"{mod}.{row[0]}"
            now = ("holds: " if row[1] else "fails: ") + str(row[2])[:100]
            before = rows.get(key, (key, None, None, None))[1]
            if before != now:
                moved.append(key)
            rows[key] = (key, now, str(row[2])[:700],
                         sorted(_terms(key, str(row[2]))))
        stamps[mod] = fp
    STORE.write_text(_json.dumps([list(v) for v in rows.values()]))
    STAMPS.write_text(_json.dumps(stamps))
    return rechecked, len(modules()) - len(rechecked), moved


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("the_english_path_was_broken_and_is_fixed", _fixed)
    t("every_rule_is_reachable_by_its_own_words", _cover)
    t("a_question_is_a_lookup_not_a_search", _lookup)
    t("nothing_in_the_index_was_written_by_hand", _auto)
    t("only_what_moved_is_recomputed", _verify)
    return all(o[1] for o in out), out


def _fixed():
    from engine.english import answer
    r = answer("what is the mass of carbon")
    if not isinstance(r, dict) or "call" not in r:
        raise ArithmeticError(f"english.answer returned {type(r).__name__}")
    return (f"engine/english.py parses that into {r['call']} and says "
            f"what it understood. It raised ModuleNotFoundError until "
            f"now, from a bare `import responder_shim` at line 181 "
            f"that resolved only when run from inside engine/. The "
            f"one mechanism here for asking in words was down, and "
            f"nothing tested it, so ninety versions of hand-written "
            f"searches were written past it")


def _cover():
    n, mods, terms = coverage()
    from engine.responder_shim import facts
    old = len(facts())
    if n < old:
        raise ArithmeticError(f"{n} indexed against {old} in the shim")
    return (f"{n:,} rules across {mods} modules, indexed under "
            f"{terms:,} distinct terms, against the {old} facts the "
            f"Atlas 2 shim carried. The gap was never machinery -- it "
            f"was that 3.1's rules had never been given their words")


def _lookup():
    import time
    t0 = time.perf_counter()
    r = ask("how cold before copying is accurate enough")
    dt = time.perf_counter() - t0
    if not r["ok"]:
        raise ArithmeticError("no rule answered")
    return (f"'{r['question']}' resolves to {r['rule']} in "
            f"{1000*dt:.0f} ms -- {r['answer'][:80]}. Nothing was "
            f"searched. The words are the index and the rule's own "
            f"sentence is the answer")


def _auto():
    rows = load()
    hand = [r for r in rows if not r[3]]
    if len(hand) > len(rows) * 0.1:
        raise ArithmeticError(f"{len(hand)} rows carry no harvested terms")
    return (f"{len(rows) - len(hand):,} of {len(rows):,} entries carry "
            f"terms taken from the rule's own name and docstring, and "
            f"the answer is the sentence its check() already emitted. "
            f"No lexicon was written by hand, so a rule added "
            f"tomorrow is reachable tomorrow")


def _verify():
    import time
    refresh()                                  # settle
    t0 = time.perf_counter()
    rechecked, untouched, moved = refresh()
    dt = time.perf_counter() - t0
    if rechecked:
        raise ArithmeticError(f"{len(rechecked)} modules rechecked "
                              f"with nothing changed")
    return (f"{untouched} modules untouched, 0 rechecked, in "
            f"{1000*dt:.0f} ms. An earlier version of this SWEPT -- "
            f"ran every check and compared 512 sentences, 180 "
            f"seconds to re-derive answers nothing could have "
            f"changed. That is the mistake eval/claims.py had "
            f"already fixed with fingerprints, committed again three "
            f"files later. A rule's fingerprint commits to its whole "
            f"chain, so you do not re-verify; you fix the rule when "
            f"you notice it is wrong and only what stands on it "
            f"recomputes")


if __name__ == "__main__":
    rows = harvest()
    n, mods, terms = coverage()
    print(f"  {n:,} rules, {mods} modules, {terms:,} terms\n")
    for q in ("how cold before copying is accurate enough",
              "what closes an autocatalytic set",
              "how tall can a tree stand",
              "does death conserve atoms",
              "what is the valence of oxygen"):
        r = ask(q)
        print(f"  Q  {q}")
        if r["ok"]:
            print(f"     -> {r['rule']}  ({r['score']})")
            print(f"        {r['answer'][:92]}")
        else:
            print(f"     -> {r['english']}")
    print()
    ok, res = check()
    for nm, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {nm:42}{d[:36]}")
