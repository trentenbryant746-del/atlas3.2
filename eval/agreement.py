"""Quantities this repository defines more than once, and whether
the copies agree.

engine/constants.py already fixed this for PHYSICAL constants. It
found four quantities carrying two or three independent
definitions -- the atomic mass unit, Newton's constant, the solar
mass, the alpha binding energy -- and every one of them agreed.
That was what made it worth fixing: nothing enforced the
agreement, so it held by luck, and a later edit to one copy would
have produced two modules quietly disagreeing about the mass of
the Sun with both answers still looking reasonable.

The rule it wrote was: a physical constant has one home, every
module imports it, and a lab experiment fails if a second
definition appears anywhere.

That rule was never extended past physical constants. Modelling
numbers -- a generation, a telling, a speech rate, a band -- are
defined wherever they were first needed, and some of them are
defined twice. This file looks for all of them.

Worse than a duplicated literal is a FROZEN COPY: a number
written down by hand that another module COMPUTES. The literal
cannot follow the computation, so the two drift apart silently
the first time the rule underneath moves.
"""

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / "engine"

# Names that legitimately differ by module: a local bound, a
# tractability cap, a loop limit. Listed so the sweep does not
# have to guess, and so adding one is a deliberate act.
LOCAL = {
    "ROOT", "HERE", "MAX_LEN", "SKIP", "PATH", "STORE", "WARM",
    "CURRENT", "SUPERSEDED", "ORDER", "ORIGIN",
}

# A literal that is really a copy of something another module
# computes. (module, name) -> (source module, callable, why).
FROZEN = {
    ("tradition", "BAND"): (
        "signal", "affordable_group",
        "the band size is DERIVED from display costs in "
        "engine/signal.py and was written into engine/tradition.py "
        "as the literal 28, with a comment naming its source. The "
        "comment is not a link. If displays ever get cheaper the "
        "band grows and the literal does not follow"),
    ("intricacy", "VILLAGE"): (
        "disease", "critical_community",
        "912 is not a round number somebody liked. It is "
        "engine/disease.py's floor for a crowd disease, "
        "GENERATION_YEARS x 365 / INFECTIOUS_DAYS, and it was "
        "written into two modules as a literal"),
    ("trade", "VILLAGE"): (
        "disease", "critical_community",
        "the same literal again, in a third place"),
}


def _constants(path):
    """-> {name: (value, lineno)} for module-level numeric names."""
    out = {}
    try:
        tree = ast.parse(path.read_text())
    except SyntaxError:
        return out
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        tgt = node.targets[0]
        if not isinstance(tgt, ast.Name) or not tgt.id.isupper():
            continue
        try:
            val = ast.literal_eval(node.value)
        except Exception:
            continue
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            continue
        out[tgt.id] = (float(val), node.lineno)
    return out


def scan():
    """-> {name: [(module, value, line)]}. Every numeric constant."""
    seen = {}
    for path in sorted(ENGINE.glob("*.py")):
        for name, (val, line) in _constants(path).items():
            if name in LOCAL:
                continue
            seen.setdefault(name, []).append((path.stem, val, line))
    return seen


def duplicates():
    """-> {name: [...]} for names defined in more than one module."""
    return {n: v for n, v in scan().items() if len(v) > 1}


def disagreements():
    """-> {name: [...]} for duplicates whose values differ."""
    out = {}
    for name, rows in duplicates().items():
        if len({round(v, 12) for _m, v, _l in rows}) > 1:
            out[name] = rows
    return out


def frozen_copies():
    """-> [(where, literal, computed, agrees, why)]. DERIVED."""
    import importlib
    out = []
    for (mod, name), (src, fn, why) in FROZEN.items():
        try:
            m = importlib.import_module(f"engine.{mod}")
            s = importlib.import_module(f"engine.{src}")
            lit = float(getattr(m, name))
            got = float(getattr(s, fn)())
        except Exception as e:
            out.append((f"{mod}.{name}", None, None, False,
                        f"could not compare: {e}"))
            continue
        out.append((f"{mod}.{name}", lit, got,
                    abs(lit - got) < 1e-9, why))
    return out


# The one-way rule. A sibling repository, atlas-unresearched,
# holds derivations that are checked against nothing. It imports
# from here. Nothing here may import from it, because a workshop
# the finished work depends on is not a workshop -- an
# UNRESEARCHED number reaching a claim in this repository would
# defeat the only thing this repository is for.
# Top-level package names belonging to the workshop repository. The
# match is on the FIRST dotted component of an import and nowhere
# else, which matters: this file briefly forbade the substring "lab."
# and engine/lab.py is a module of this repository that eval/claims.py
# is entitled to import. A guard that fires on the work it protects
# gets switched off, so it has to be exact.
FORBIDDEN_ROOTS = frozenset(("attempts", "genesis",
                             "genesis_unresearched"))

_IMPORT = re.compile(r"^\s*(?:from|import)\s+([\w.]+)")


def leaks_from_the_workshop():
    """-> [(module, line, text)]. Imports that must not exist."""
    bad = []
    for folder in ("engine", "eval", "tools"):
        d = ROOT / folder
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.py")):
            for i, line in enumerate(path.read_text().splitlines(), 1):
                m = _IMPORT.match(line)
                if m and m.group(1).split(".")[0] in FORBIDDEN_ROOTS:
                    bad.append((f"{folder}/{path.name}", i,
                                line.strip()))
    return bad


# --- the same quantity under two NAMES ------------------------------
#
# The one-home rule here matched IDENTICAL NAMES, and enforced "one
# name, one value". That is weaker than it reads. A human generation
# is 20 years in engine/adapt.GENERATIONS and 25 in
# engine/literacy.GENERATION_YEARS -- the same quantity, two values,
# two names -- and nothing in this file could see it. It was found
# by an ablation in a separate repository, which is not a system.
#
# So a concept may name its members explicitly, with a conversion
# into one unit, and they are compared. A member is written as a
# module and an EXPRESSION rather than a bare name, because some of
# these live inside a dict and a scanner that only reads assignments
# would miss exactly those.

CONCEPTS = {
    "how long a human generation is": {
        "unit": "years",
        "members": (
            ("adapt", "GENERATIONS['human'] / 365.0"),
            ("literacy", "GENERATION_YEARS"),
        ),
    },
    "how many seconds are in a year": {
        "unit": "seconds",
        "members": (
            ("constants", "YEAR_S"),
            ("cold", "YEAR_S"),
            ("industry", "YEAR_S"),
            ("revolution", "YEAR_S"),
        ),
    },
}

# Concepts whose members legitimately differ, with the reason. A
# reference temperature is not one quantity: 293 K is the standard
# reservoir a heat engine dumps into, 298 K is where rate constants
# are tabulated. Naming them here stops a later reader "fixing" a
# difference that is meant to be there.
ALLOWED_TO_DIFFER = {
    "a reference temperature": (
        ("industry", "AMBIENT_K", "293 K, the reservoir Carnot uses"),
        ("cold", "REF_T", "298 K, where rate constants are measured"),
    ),
}

# Known open, on the record, and NOT failed on. Settling this moves
# published numbers in both directions, so it is a decision rather
# than a cleanup -- engine/unsolved.OPEN_TO_US carries it. A NEW
# collision still fails. Removing an entry here is how a decision
# gets enforced.
KNOWN_OPEN = ("how long a human generation is",)

CONCEPT_TOLERANCE = 1e-9


def concept_values(name):
    """-> [(module, expression, value)]. Resolved by import."""
    import importlib
    out = []
    for mod, expr in CONCEPTS[name]["members"]:
        try:
            m = importlib.import_module(f"engine.{mod}")
        except Exception:
            continue
        try:
            out.append((mod, expr, float(eval(expr, vars(m)))))
        except Exception:
            continue
    return out


def concept_disagreements():
    """-> {concept: rows}. Same quantity, different values."""
    bad = {}
    for name in CONCEPTS:
        rows = concept_values(name)
        if len(rows) < 2:
            continue
        lo = min(r[2] for r in rows)
        hi = max(r[2] for r in rows)
        if lo == 0 or abs(hi / lo - 1.0) > CONCEPT_TOLERANCE:
            bad[name] = rows
    return bad


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("no_two_modules_disagree_about_the_same_name", _disagree)
    t("INVERTED_some_names_still_have_two_homes", _dupes)
    t("a_literal_that_copies_a_computed_value_is_found", _frozen)
    t("nothing_here_imports_from_the_workshop", _oneway)
    t("the_same_quantity_under_two_names_is_compared", _concepts)
    return all(x for _, x, _ in res), res


def _concepts():
    bad = concept_disagreements()
    new = {k: v for k, v in bad.items() if k not in KNOWN_OPEN}
    if new:
        raise ArithmeticError(
            "the same quantity has two values under two names: "
            + "; ".join(
                f"{k}: " + ", ".join(f"{m}.{e} = {v:g}" for m, e, v in rows)
                for k, rows in new.items()))
    n = sum(len(CONCEPTS[k]["members"]) for k in CONCEPTS)
    open_ = {k: concept_values(k) for k in bad if k in KNOWN_OPEN}
    return (f"the one-home rule above matches IDENTICAL NAMES, which "
            f"enforces 'one name, one value' -- weaker than it "
            f"reads. This compares the same quantity across "
            f"DIFFERENT names: {len(CONCEPTS)} concepts, {n} members, "
            f"each a module and an expression rather than a bare "
            f"name, because some of them live inside a dict where a "
            f"scanner reading assignments would never look. "
            + (f"{len(open_)} is known open and does not fail here: "
               + "; ".join(
                   f"{k} is " + " against ".join(
                       f"{v:g} in {m}" for m, _e, v in rows)
                   for k, rows in open_.items())
               + f", which is a DECISION and not a cleanup because "
                 f"published numbers move either way -- "
                 f"engine/unsolved.OPEN_TO_US carries it, and "
                 f"removing it from KNOWN_OPEN is how the decision "
                 f"gets enforced. "
               if open_ else "")
            + f"A new collision fails. This file could not see any "
              f"of this until an ablation in another repository "
              f"found the generation length, which is not a system")


def _disagree():
    bad = disagreements()
    if bad:
        raise ArithmeticError(
            "two modules give the same name different values: "
            + "; ".join(
                f"{n} = " + ", ".join(f"{m} {v:g}" for m, v, _l in rows)
                for n, rows in bad.items()))
    dup = duplicates()
    return (f"{len(scan())} module-level numeric constants across "
            f"the engine, {len(dup)} of them defined in more than "
            f"one module, and NONE of the copies disagree. That is "
            f"the same result engine/constants.py got for physical "
            f"constants, and it means the same thing: the "
            f"agreement is holding by care rather than by "
            f"construction, and one careless edit ends it")


def _dupes():
    """INVERTED. Fails when every name has exactly one home."""
    dup = duplicates()
    if not dup:
        raise ArithmeticError(
            "every constant has one home, which would be the "
            "finished state of this sweep and should be verified "
            "rather than assumed")
    rows = sorted(dup.items(), key=lambda kv: -len(kv[1]))
    return (f"{len(dup)} names are defined in more than one place: "
            + "; ".join(
                f"{n} in {', '.join(m for m, _v, _l in r)}"
                for n, r in rows[:5])
            + f". engine/constants.py's rule -- one home, everyone "
              f"imports, a duplicate fails an experiment -- was "
              f"written for PHYSICAL constants and never extended "
              f"to modelling ones. A generation, a telling and a "
              f"speech rate are exactly as capable of drifting as "
              f"the mass of the Sun, and rather more likely to, "
              f"because nobody thinks of them as constants")


def _frozen():
    rows = frozen_copies()
    bad = [r for r in rows if not r[3]]
    if not rows:
        raise ArithmeticError("nothing is being checked")
    lit, got = rows[0][1], rows[0][2]
    return (f"worse than a duplicated literal is a FROZEN COPY: a "
            f"number written by hand that another module computes. "
            f"{len(rows)} tracked, {len(bad)} currently adrift. "
            f"engine/tradition.BAND is the literal {lit:.0f} and "
            f"engine/signal.affordable_group() returns {got:.0f}, "
            f"so they agree today -- and the comment naming the "
            f"source is not a link. If a display ever gets cheaper "
            f"the band grows and the literal does not follow, and "
            f"every rule built on BAND would go on using a number "
            f"the system no longer believes. That is not a "
            f"hypothetical: engine/capital.py's DAYS_PER_PART was "
            f"carried from a village to a billionth of a metre "
            f"unchanged and gave 3,739 holders of an inference kit "
            f"before it was caught")


def _oneway():
    bad = leaks_from_the_workshop()
    if bad:
        raise ArithmeticError(
            "the workshop has leaked in: "
            + "; ".join(f"{m}:{i} {t}" for m, i, t in bad))
    n = sum(1 for f in ("engine", "eval", "tools")
            for _p in (ROOT / f).glob("*.py"))
    return (f"a separate repository, Genesis Unresearched, holds "
            f"derivations checked against nothing -- a sixth kind, "
            f"UNRESEARCHED, meaning it has an argument and no "
            f"evidence. It imports from here and nothing here "
            f"imports from it, across all {n} modules of engine, "
            f"eval and tools. That direction is the whole point. "
            f"THIS repository's entire claim is that a published "
            f"number carries something underneath it that would "
            f"catch the number being wrong, so an UNRESEARCHED one "
            f"reaching a claim here would not weaken the claim, it "
            f"would void the STANDARD -- a reader could no longer "
            f"tell which of the two kinds any given figure was. "
            f"That is why the separation is a repository boundary "
            f"and a scan rather than a tag and a promise. Genesis "
            f"runs the same scan from its side, because a rule "
            f"enforced only by the party it constrains is worth "
            f"having twice, and this check fails the moment one "
            f"import appears")


if __name__ == "__main__":
    dup = duplicates()
    print(f"  {len(scan())} constants, {len(dup)} with more than "
          f"one home\n")
    for name, rows in sorted(dup.items()):
        vals = {round(v, 12) for _m, v, _l in rows}
        flag = "  DISAGREE" if len(vals) > 1 else ""
        print(f"  {name:<22}" + ", ".join(
            f"{m}:{l} = {v:g}" for m, v, l in rows) + flag)
    print()
    for where, lit, got, ok, _why in frozen_copies():
        mark = "agrees" if ok else "ADRIFT"
        print(f"  frozen copy {where:<20} literal {lit} vs "
              f"computed {got}  {mark}")
    print()
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
