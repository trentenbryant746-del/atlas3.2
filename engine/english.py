"""
English the whole way through: question in, answer out, explanation in English.

Two halves already existed and were not joined. grammar3 turned a question
into a typed call and nothing routed it. explain.py narrated a derivation
and only knew arithmetic. This closes the loop, so a single English
sentence produces:

    the CALL it was understood as        (compositional, no template)
    the ANSWER                            (from the expert that owns it)
    the CHECK that was applied            (which kind, and whether it held)
    the PROVENANCE                        (derivation steps, or a citation)
    all of it rendered back into English

The explanation is not decoration. It states which of the two ways an
answer can be right: derived and checked, or quoted from a source. A
reader can tell them apart without reading any code.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.grammar3 import parse                                # noqa: E402

DIMNAME = {(1, 0, 0): "a length", (0, 1, 0): "a mass", (0, 0, 1): "a time",
           (1, 0, -1): "a speed", (1, 0, -2): "an acceleration",
           (-3, 1, 0): "a density", (0, 0, 0): "a pure number"}


def understand(question):
    """-> (Query sem, English gloss of how it was read) or (None, reason)"""
    roots, unknown = parse(question)
    if unknown:
        return None, (f"I do not know the word"
                      f"{'s' if len(unknown) > 1 else ''} "
                      f"{', '.join(repr(u) for u in unknown)}.")
    if not roots:
        return None, "I could not read that as a question about a quantity."
    sems = {repr(r.sem): r.sem for r in roots}
    if len(sems) > 1:
        return None, (f"That reads {len(sems)} different ways: "
                      f"{', '.join(sems)}.")
    sem = next(iter(sems.values()))
    if sem.kind != "query":
        return None, "That is a phrase, not a question."
    ent = sem.args[0].name if sem.args else "?"
    return sem, (f"I read that as: find the {sem.name} of {ent}, "
                 f"which should be {DIMNAME.get(sem.dim, 'a quantity')}.")


WHY = {
    "helium": "primordial_helium", "big bang": "primordial_helium",
    "quarter of the universe": "primordial_helium",
    "fusion": "fusion_energy", "26.7": "fusion_energy",
    "iron": "iron_peak", "stop at iron": "iron_peak",
    # The Qwen accounts. Cues are deliberately long and specific: the
    # table resolves by LONGEST CUE and abstains on a tie, so a short
    # cue like "expert" would have started stealing questions from the
    # accounts that were already here.
    "does one token touch": "touched_per_token",
    "much of the model": "touched_per_token",
    "sparsity": "touched_per_token",
    "fit the file": "experts_against_the_file",
    "share of the file": "experts_against_the_file",
    "experts weigh": "subject_cost",
    "subject cost": "subject_cost",
}


def why_account(question):
    """questions that ask WHY get the whole derivation, in English"""
    q = question.lower()
    if not q.strip().startswith(("why", "how does", "how come", "explain")):
        return None
    from engine import accounts
    # Accounts now live in two modules: the physics ones that were
    # always here, and the Qwen ones. Resolution tries both so the
    # cue table does not have to know which module owns a name.
    try:
        from engine import qwenaccounts as _qa
    except Exception:
        _qa = None
    # LONGEST CUE WINS, and a genuine tie abstains. "why does fusion stop at
    # iron" contains both "fusion" and "iron"; iterating the table in order
    # answered it with the fusion-energy derivation. Specific beats generic,
    # and two equally specific cues pointing at different accounts is an
    # ambiguous question, not a coin flip.
    hits = sorted(((len(cue), cue, fn) for cue, fn in WHY.items() if cue in q),
                  reverse=True)
    if not hits:
        return None
    top = hits[0][0]
    tied = {fn for ln, _c, fn in hits if ln == top}
    if len(tied) > 1:
        return {"ok": False, "kind": "AMBIGUOUS", "call": None,
                "check": "-", "answer": None,
                "english": (f"That could be asking about {len(tied)} "
                            f"different derivations ({', '.join(sorted(tied))}). "
                            f"Ask about one of them.")}
    for _ln, cue, fn in hits[:1]:
            owner = accounts if hasattr(accounts, fn) else _qa
            if owner is None or not hasattr(owner, fn):
                return None
            d = getattr(owner, fn)()
            ok, _ = d.verify()
            return {"ok": True, "kind": "DERIVATION", "call": fn,
                    "check": "STEP RE-EXECUTION",
                    "answer": d.result, "english": d.narrate(),
                    "faithful": ok}
    return None


def derived_answer(question):
    """questions whose answer is COMPUTED -- narrate the derivation itself"""
    from engine.units import convert
    from engine.dates import solve
    from engine.parse import recognise

    v, why = convert(question)
    if v is not None:
        return {"ok": True, "call": "convert(...)", "answer": str(v),
                "kind": "DERIVED", "check": "INVERSE + REDUNDANT",
                "english": (
                    f"I read that as a unit conversion.\n"
                    f"  The answer is {v}.\n"
                    f"  This is DERIVED, not quoted: it is computed from the "
                    f"scale factors, and the dimensions had to match before "
                    f"any arithmetic ran ({why}).\n"
                    f"  Two checks were applied. Converting the result back "
                    f"returns the input exactly, and routing through SI base "
                    f"units by a separate path gives the same number. If "
                    f"either disagreed you would get nothing instead of this.")}

    v, why = solve(question)
    if v is not None:
        return {"ok": True, "call": "date(...)", "answer": str(v),
                "kind": "DERIVED", "check": "INVERSE + REDUNDANT",
                "english": (
                    f"I read that as a question about dates.\n"
                    f"  The answer is {v}.\n"
                    f"  This is DERIVED: {why}.\n"
                    f"  Adding the result back to the start date returns the "
                    f"end date, and where a weekday is involved two unrelated "
                    f"algorithms had to agree.")}

    v, span = recognise(question)
    if v is not None:
        return {"ok": True, "call": "arith(...)", "answer": str(v),
                "kind": "DERIVED", "check": "REDUNDANT",
                "english": (
                    f"I read that as the arithmetic expression {span!r}.\n"
                    f"  The answer is {v}.\n"
                    f"  This is DERIVED: it is computed, not looked up.\n"
                    f"  Two independent parsers and two independent "
                    f"evaluators produced the same value. Nothing is "
                    f"returned unless they agree.")}
    return None


def answer(question):
    """-> dict with the call, the answer, the check and an English account"""
    w = why_account(question)
    if w:
        return w
    d = derived_answer(question)
    if d:
        return d
    sem, gloss = understand(question)
    if sem is None:
        return {"ok": False, "english": gloss, "call": None}

    ent = sem.args[0].name if sem.args else None
    attr = sem.name
    out = {"call": f"{attr}({ent})", "read_as": gloss, "dim": sem.dim}

    # route the call: a sourced fact, grounded and cited
    import responder_shim as _rs
    rows = _rs.facts()
    key = f"{ent}.{attr}"
    hit = next((r for r in rows if r[0] == key), None)
    if hit is None:
        alt = [r for r in rows if r[0].startswith(ent + ".")]
        out.update(ok=False, english=(
            f"{gloss} I have no record of the {attr} of {ent}."
            + (f" I do have: {', '.join(sorted(k.split('.',1)[1] for k,_,_ in alt)[:6])}."
               if alt else "")))
        return out

    k, terse, eng = hit
    out.update(ok=True, answer=terse, source=eng,
               check="SPAN-IN-SOURCE", kind="ASSERTED")
    out["english"] = (
        f"{gloss}\n"
        f"  The answer is {terse}.\n"
        f"  This is an ASSERTED fact, not a derived one: nothing computes "
        f"the {attr} of {ent}, so it is quoted from a source.\n"
        f"  The source says: \"{eng.strip()}\"\n"
        f"  The check that applies is SPAN-IN-SOURCE -- the answer appears "
        f"verbatim in the source, which verifies faithfulness, not truth.")
    return out
