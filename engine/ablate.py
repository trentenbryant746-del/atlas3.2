"""
All rules at once. When that fails, remove one at a time and see.

A lab tests a rule in isolation, which is how you find out whether
the rule is sound. It does not tell you which rule is responsible
when everything is switched on and the answer is still wrong --
and by then the rules interact, so reading the code will not tell
you either.

THE PROCEDURE, AND IT IS A RULE RATHER THAN A HABIT:

    1  run with every rule on. If it passes, stop.
    2  if it fails, run again with each rule removed in turn.
    3  a rule whose REMOVAL changes the outcome is implicated.
    4  a rule whose removal changes nothing is not the problem,
       however plausible it looked.
    5  what is left is a specific failure with a specific owner,
       and THAT is what a new, narrower rule gets written for.

WHY STEP 4 MATTERS MOST. Three times now a fix looked obvious and
did nothing: a curvature term for the liquid drop, tightening the
mass bar to resolve more decays, splitting the climate bar by
manifestation. Each was a reasonable hypothesis and each cost real
work to reject. An ablation answers "would this even have helped?"
before the work, not after.

AND IT CATCHES ERRORS THAT CANCEL, which nothing else here does.
3.1.27 found alpha Q-values mixing a measured helium-4 binding into
an otherwise-SEMF difference, biasing every one by +5.455 MeV. It
had survived because the liquid drop is short by a similar amount
on heavy alpha steps, so the score looked fine. Two wrongs, one
visible answer. Ablation separates them by construction: remove one
error and the other appears, which is exactly the signature.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class Rule:
    """A switch, its description, and how to turn it off."""

    def __init__(self, name, why, disable, restore):
        self.name, self.why = name, why
        self.disable, self.restore = disable, restore


# ---------------------------------------------- the nuclear rules
def _no_shells():
    from engine import shells
    old = shells.SCALE
    shells.SCALE = 0.0
    return old


def _yes_shells(old):
    from engine import shells
    shells.SCALE = old


def _no_domain():
    from engine import shells
    old = shells.SEMF_MIN_A
    shells.SEMF_MIN_A = 1
    return old


def _yes_domain(old):
    from engine import shells
    shells.SEMF_MIN_A = old


def _mixed_sources():
    """Put the helium-4 inconsistency back, to measure what it did."""
    from engine import transitions
    old = transitions._b
    from engine.constants import B_ALPHA_MEV

    def mixed(z, n):
        if (z, n) == (2, 2):
            return B_ALPHA_MEV
        return old(z, n)
    transitions._b = mixed
    return old


def _consistent(old):
    from engine import transitions
    transitions._b = old


NUCLEAR_RULES = [
    Rule("shell-corrections",
         "closures derived from a modified oscillator, and the "
         "level-density correction they imply",
         _no_shells, _yes_shells),
    Rule("liquid-drop-domain",
         "refuse the formula below A=13, where it exceeds its own bar",
         _no_domain, _yes_domain),
    Rule("one-source-per-Q",
         "every term in a Q-value from the same formula",
         _mixed_sources, _consistent),
]


def decay_outcome():
    """-> (right, wrong, refused). The target being diagnosed."""
    import importlib
    from engine import transitions
    importlib.reload  # noqa: B018  (kept explicit: no reload, live patch)
    r = transitions.score()
    return r["right"], r["wrong"], r["refused"]


def diagnose(target=decay_outcome, rules=None, label="decay"):
    """-> dict. All rules on, then each one off in turn.

    The verdict on each rule is what its REMOVAL does, which is the
    only question that has an answer once rules interact.
    """
    rules = NUCLEAR_RULES if rules is None else rules
    base = target()
    rows = []
    for rule in rules:
        token = rule.disable()
        try:
            got = target()
        finally:
            rule.restore(token)
        rows.append({
            "rule": rule.name,
            "without_it": got,
            "changed": got != base,
            "d_wrong": got[1] - base[1],
            "why": rule.why,
        })
    return {"target": label, "all_rules_on": base, "ablations": rows}


def diagnose_pairs(target=decay_outcome, rules=None):
    """-> [rows]. Remove rules in PAIRS as well as singly.

    SINGLE ABLATION HAS A BLIND SPOT AND THE FIRST RUN HIT IT. With
    every rule on, removing shell corrections changed nothing and
    removing the helium-4 consistency changed nothing -- which reads
    as "neither matters" and is wrong. Both were inert only because
    a THIRD rule, the liquid-drop domain, shuts the alpha channel
    entirely, so neither had any input to act on.
    
    A rule downstream of a closed gate looks irrelevant no matter
    how important it is. Pairs find that: open the gate and ask
    again.
    """
    rules = NUCLEAR_RULES if rules is None else rules
    base = target()
    out = []
    for i, a in enumerate(rules):
        for b in rules[i + 1:]:
            ta = a.disable()
            tb = b.disable()
            try:
                got = target()
            finally:
                b.restore(tb)
                a.restore(ta)
            out.append({"rules": (a.name, b.name), "without_them": got,
                        "changed": got != base})
    return out


def attribute(d=None):
    """-> [(rule, effect)]. Plain English, implicated rules first."""
    d = diagnose() if d is None else d
    out = []
    for r in sorted(d["ablations"], key=lambda x: -abs(x["d_wrong"])):
        if not r["changed"]:
            out.append((r["rule"], "removing it changes nothing here -- "
                                   "not implicated, however plausible"))
        elif r["d_wrong"] > 0:
            out.append((r["rule"],
                        f"removing it makes {r['d_wrong']} more answers "
                        f"confidently WRONG, so it is load-bearing"))
        elif r["d_wrong"] < 0:
            out.append((r["rule"],
                        f"removing it makes {-r['d_wrong']} FEWER wrong, "
                        f"which does not make it correct -- check whether "
                        f"it is cancelling another error"))
        else:
            out.append((r["rule"], "shifts right against refused without "
                                   "changing how many are wrong"))
    return out


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("ablation_restores_every_rule", _restores)
    t("every_rule_is_attributable", _attrib)
    t("errors_that_cancel_are_visible", _cancel)
    t("a_masked_rule_is_found_by_pairs", _masked)
    return all(o[1] for o in out), out


def _restores():
    before = decay_outcome()
    diagnose()
    after = decay_outcome()
    if before != after:
        raise ArithmeticError(f"ablation left the system changed: "
                              f"{before} -> {after}")
    return (f"every switch is put back: {before} before and after a full "
            f"sweep. An ablation that leaked would poison every result "
            f"measured after it")


def _attrib():
    d = diagnose()
    rows = attribute(d)
    return (f"target {d['target']} with all rules on: {d['all_rules_on'][0]} "
            f"right, {d['all_rules_on'][1]} wrong, "
            f"{d['all_rules_on'][2]} refused. "
            + "; ".join(f"{n}: {e}" for n, e in rows))


def _cancel():
    """Two errors cancelling, found by removing rules in pairs."""
    single = diagnose()
    lone = [r for r in single["ablations"]
            if r["rule"] == "one-source-per-Q"][0]
    pairs = diagnose_pairs()
    both = [r for r in pairs
            if set(r["rules"]) == {"one-source-per-Q",
                                   "liquid-drop-domain"}][0]
    if lone["changed"]:
        raise ArithmeticError("the helium-4 rule now matters on its own, "
                              "so the masking described here is gone and "
                              "this reasoning needs redoing")
    if not both["changed"]:
        raise ArithmeticError("even with the domain lifted the helium-4 "
                              "inconsistency changes nothing, so the "
                              "3.1.27 finding is no longer reproducible")
    return (f"removing the helium-4 consistency alone changes nothing, "
            f"which reads as 'it does not matter' and is wrong. It is "
            f"inert only because the domain rule shuts the alpha channel "
            f"and leaves it no input. Lift both and the outcome moves to "
            f"{both['without_them']} from {single['all_rules_on']} -- the "
            f"+5.455 MeV bias reappears and partly cancels the liquid "
            f"drop's deficit on heavy alpha steps. A rule behind a closed "
            f"gate looks irrelevant however important it is, which is why "
            f"single ablation is not enough")


def _masked():
    single = diagnose()["ablations"]
    pairs = diagnose_pairs()
    inert = {r["rule"] for r in single if not r["changed"]}
    revived = set()
    for r in pairs:
        if r["changed"]:
            revived |= (set(r["rules"]) & inert)
    if not revived:
        raise ArithmeticError("no rule that looked inert alone matters in "
                              "a pair, so pairwise ablation is buying "
                              "nothing and should be dropped")
    return (f"{len(inert)} rules look inert on their own "
            f"({', '.join(sorted(inert))}) and {len(revived)} of them "
            f"matter once a second rule is lifted too "
            f"({', '.join(sorted(revived))}). Single ablation would have "
            f"reported them as not implicated and the diagnosis would "
            f"have been wrong")


if __name__ == "__main__":
    d = diagnose()
    print(f"  all rules on: {d['all_rules_on'][0]} right, "
          f"{d['all_rules_on'][1]} WRONG, {d['all_rules_on'][2]} refused\n")
    for r in d["ablations"]:
        g = r["without_it"]
        print(f"  without {r['rule']:20} {g[0]} right, {g[1]} WRONG, "
              f"{g[2]} refused   {'CHANGED' if r['changed'] else 'no change'}")
    print()
    for n, e in attribute(d):
        print(f"  {n:22}{e}")
    print()
    for r in diagnose_pairs():
        g = r["without_them"]
        print(f"  without {' + '.join(r['rules']):44} {g[0]}/{g[1]}/{g[2]}"
              f"   {'CHANGED' if r['changed'] else 'no change'}")
    ok, res = check()
    print()
    for n, o, dd in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:34}{dd[:66]}")
    print("\nall:", ok)
