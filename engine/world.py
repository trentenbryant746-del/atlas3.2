"""A world that actually runs, and a record of what gets made in it.

Everything before this module computed a constraint ENVELOPE:
what a human-like organism could not do. That is a real kind of
statement and it is not the same as saying what they did. Nothing
had state, nothing took a step, nobody tried anything.

This does. Bands hold crafts and artifacts. Each step they try
combinations of what they already have. A trial succeeds only if
the physical gates permit -- the temperature their fires reach
and the tolerance their tools hold -- and the bands do not know
those gates. They find out by failing.

WHAT IS RECORDED. Every artifact made, when, and by which band.
Most of them have no name in engine/artifact.py, because that
file names 21 things and the reachable space is 2^21. Those
unnamed ones are not errors and they are not noise. They are
combinations that are physically permitted in this world and
were never built in ours, and they are written down with
everything else.

WHAT THIS IS NOT. It is not a claim that any particular artifact
would have been built. It is a claim about which ones COULD be,
in what order the gates allow, and how long the search takes
when nobody can see the gates.
"""

import random

from engine.artifact import (PRIMITIVES, KNOWN_AS, TOL_NEEDED, GAINS,
                             TOL_GAINS, BASE_K, BASE_TOL)
from engine.tradition import BAND, garbles

TRIALS_PER_BAND_YEAR = 0.28     # novelty.TRIALS_PER_HEAD_YEAR x BAND

# THE GATES ARE NECESSARY AND NOT SUFFICIENT, and the first
# version of this file had them sufficient. A band picked a craft
# and got it the moment the physics allowed, so the whole tree
# fell in 300 years of a 12,000-year run and the inverted check
# below caught it.
#
# What was missing is that permission is not occurrence -- the
# same distinction the chain has carried since 3.1.95. Knowing
# that iron CAN be smelted at 1750 K does not hand you a
# bloomery. engine/innovation.py already measures the gap:
# useful_fraction, the share of attempts that turn out to be
# worth keeping, and it is 1.09e-4.
#
# And engine/innovation.useful_fraction turned out to be the
# wrong number to borrow. It is measured over CELL DIVISIONS --
# omissions and duplications in a genome -- and using a cell's
# success rate for a human craft attempt is a category error I
# made rather than an approximation I chose. At 1.09e-4 the run
# reaches 9 crafts of 21 in fourteen thousand years.
#
# So this is FITTED, and it is the only fitted number in the
# repository.
#
# CRAFT_SUCCESS is set so the tree completes in about the
# Holocene: the last craft arrives at year 11,380 of a run that
# starts at the end of the last glaciation. That is tuning a
# parameter to reproduce an answer, which is the thing this
# repository otherwise refuses to do, and it is marked FITTED
# rather than CHOSEN so that it cannot be mistaken for a
# judgement call. Nothing derived from this run may be quoted as
# a prediction of the TIMESCALE, because the timescale is what
# was fitted. The ORDER is not fitted and is the result.

FITTED = "FITTED"               # a fifth kind, and there is one
CRAFT_SUCCESS = 2.0e-3          # FITTED, the Holocene span
YEARS_PER_STEP = 10.0
MEETINGS_PER_STEP = 0.2         # CHOSEN, bands that meet per step


class Band:
    """A group that holds crafts and the things it has built."""

    __slots__ = ("ident", "prims", "made")

    def __init__(self, ident, seed_prims):
        self.ident = ident
        self.prims = set(seed_prims)
        self.made = set()

    def temperature(self):
        t = BASE_K
        for _label, (needs, gain) in GAINS.items():
            if set(needs) <= self.prims:
                t += gain
        return t

    def tolerance(self):
        tol = BASE_TOL
        for _label, (needs, got) in TOL_GAINS.items():
            if set(needs) <= self.prims:
                tol = min(tol, got)
        return tol

    def can_make(self, primitive):
        """The gates decide. The band cannot see them. DERIVED."""
        needs, kelvin, _rule, _words = PRIMITIVES[primitive]
        return (set(needs) <= self.prims
                and kelvin <= self.temperature()
                and TOL_NEEDED.get(primitive, BASE_TOL) >= self.tolerance())


class World:
    """Bands, a clock, and a ledger of everything made."""

    def __init__(self, bands=40, seed=20260918):
        self._useful = CRAFT_SUCCESS
        self.rng = random.Random(seed)
        self.year = 0.0
        seed_prims = [p for p, v in PRIMITIVES.items() if not v[0]]
        self.bands = [Band(i, seed_prims) for i in range(bands)]
        self.ledger = []          # (year, band, kind, what)
        for b in self.bands:
            for p in seed_prims:
                self.ledger.append((0.0, b.ident, "craft", p))

    # --- one step ---------------------------------------------------

    def _try_craft(self, band):
        """Attempt a craft not yet held. Fails silently if gated.

        A band attempts what it can CONCEIVE of attempting, which
        is anything whose parts it already has. It cannot try to
        make a gear with no metal -- that is not a refused
        attempt, it is not an available action. What it cannot
        see is the temperature and the tolerance, so it tries
        things that are possible-in-parts and fails on physics it
        has no way to know about.

        The first version picked uniformly over ALL missing
        crafts, so most trials were spent on things the band
        could not even begin, and the run stalled at 5 of 21
        after forty thousand years.
        """
        missing = [p for p in PRIMITIVES
                   if p not in band.prims
                   and set(PRIMITIVES[p][0]) <= band.prims]
        if not missing:
            return
        pick = self.rng.choice(missing)
        if not band.can_make(pick):
            return                      # the physics refuses
        if self.rng.random() > self._useful:
            return                      # the physics allows, and it
            # still has to be stumbled on: permission is not occurrence
        band.prims.add(pick)
        self.ledger.append((self.year, band.ident, "craft", pick))

    def _try_combination(self, band):
        """Put two things together and see. Anything held composes."""
        if len(band.prims) < 2:
            return
        k = self.rng.randint(2, min(4, len(band.prims)))
        combo = frozenset(self.rng.sample(sorted(band.prims), k))
        if combo in band.made:
            return
        band.made.add(combo)
        self.ledger.append((self.year, band.ident, "artifact", combo))

    def _meet(self):
        """Two bands meet and one shows the other something."""
        if len(self.bands) < 2:
            return
        a, b = self.rng.sample(self.bands, 2)
        share = a.prims - b.prims
        if not share:
            return
        what = self.rng.choice(sorted(share))
        if self.rng.random() < 1.0 - garbles(len(b.prims) + 1):
            b.prims.add(what)
            self.ledger.append((self.year, b.ident, "learned", what))

    def step(self):
        trials = TRIALS_PER_BAND_YEAR * YEARS_PER_STEP
        for band in self.bands:
            n = int(trials) + (1 if self.rng.random() < trials % 1 else 0)
            for _ in range(n):
                if self.rng.random() < 0.5:
                    self._try_craft(band)
                else:
                    self._try_combination(band)
        if self.rng.random() < MEETINGS_PER_STEP * len(self.bands):
            self._meet()
        self.year += YEARS_PER_STEP

    def run(self, years=12000.0):
        while self.year < years:
            self.step()
        return self

    # --- what came out ----------------------------------------------

    def crafts_held(self):
        out = set()
        for b in self.bands:
            out |= b.prims
        return out

    def first_seen(self):
        """-> {craft: year}. When anybody first made it. RECORDED."""
        out = {}
        for year, _b, kind, what in self.ledger:
            if kind == "craft" and what not in out:
                out[what] = year
        return out

    def artifacts(self):
        """-> set of distinct things built anywhere. RECORDED."""
        return {w for _y, _b, k, w in self.ledger if k == "artifact"}

    def named(self):
        return {a for a in self.artifacts() if a in KNOWN_AS}

    def unnamed(self):
        """Built here, no name in our world. The interesting ones."""
        return {a for a in self.artifacts() if a not in KNOWN_AS}


def spec(combo, world=None):
    """-> a spec sheet for one thing in the ledger. DERIVED.

    What it is MADE OF, what FIRE and what TOLERANCE it needs,
    and what must already exist before anyone can attempt it.

    What this does NOT say is what the thing does. A set of
    capabilities is a requirement list, not a design, and naming
    it would be inventing. The sheet is real and the name would
    not be.
    """
    from engine.artifact import TOL_NEEDED
    from engine.inference import closure
    w = world or run()
    parts = sorted(combo)
    rests = set()
    for part in parts:
        rests |= closure(part)
    rests -= set(parts)
    first = None
    for year, band, kind, what in w.ledger:
        if kind == "artifact" and what == frozenset(combo):
            first = (year, band)
            break
    return {
        "made of": [(p, PRIMITIVES[p][3]) for p in parts],
        "fire": max(PRIMITIVES[p][1] for p in parts),
        "tolerance": min(TOL_NEEDED.get(p, BASE_TOL) for p in parts),
        "rests on": sorted(rests),
        "first built": first,
        "named in our world": KNOWN_AS.get(frozenset(combo)),
    }


def describe(thing, world=None):
    """An encyclopedia entry, composed and not written. DERIVED.

    The words come from engine/artifact.PRIMITIVES, which already
    says what each capability is. The gates come from the same
    file. The date and the maker come from the ledger. Nothing in
    the sentence was typed for this object.

    It says what the thing is MADE OF and what it COSTS. It does
    not say what it is FOR. An earlier version inferred a purpose
    from what the band managed next, and that was a spurious
    correlation dressed as a finding -- a band that builds
    anything goes on to manage other things regardless. An
    encyclopedia of materials and costs is real; a catalogue of
    guessed purposes is not.
    """
    from engine.artifact import TOL_NEEDED, COLD_NEEDED, BASE_COLD
    sheet = spec(thing, world)
    parts = [w for _p, w in sheet["made of"]]
    body = "; ".join(parts)
    cold = min((COLD_NEEDED.get(p, BASE_COLD)
                for p, _w in sheet["made of"]), default=BASE_COLD)
    gates = f"a fire of {sheet['fire']} K"
    if sheet["tolerance"] < 1e-1:
        gates += f", work true to {sheet['tolerance']:.0e}"
    if cold < BASE_COLD:
        gates += f", and cold down to {cold:.0f} K"
    when, who = sheet["first built"] or (None, None)
    tail = (f"First made in year {when:.0f} by band {who}."
            if when is not None else "Never made in this run.")
    named = sheet["named in our world"]
    ours = (f"Our world calls this {named}."
            if named else "Our world has no word for it.")
    return (f"A thing of {body}. Making one takes {gates}, and "
            f"{len(sheet['rests on'])} crafts must already exist. "
            f"{tail} {ours}")


_RUN = {}


def run(years=12000.0):
    """One world, held, because stepping it twice is waste."""
    key = float(years)
    if key not in _RUN:
        _RUN[key] = World().run(years)
    return _RUN[key]


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("something_actually_runs_and_keeps_a_ledger", _runs)
    t("the_gates_order_it_without_anyone_seeing_them", _order)
    t("most_of_what_is_built_has_no_name_in_our_world", _novel)
    t("INVERTED_it_is_a_search_and_it_can_stall", _stall)
    t("INVERTED_exactly_one_number_here_is_fitted", _fitted)
    t("anything_in_the_ledger_has_a_spec_and_not_a_name", _spec)
    return all(x for _, x, _ in res), res


def _runs():
    w = run()
    crafts = w.crafts_held()
    if not w.ledger or len(crafts) < 4:
        raise ArithmeticError(f"{len(crafts)} crafts, {len(w.ledger)}")
    return (f"{len(w.bands)} bands over {w.year:.0f} years, "
            f"{len(w.ledger):,} entries in the ledger. They hold "
            f"{len(crafts)} of {len(PRIMITIVES)} crafts and have "
            f"built {len(w.artifacts()):,} distinct things. Nothing "
            f"here consults the bootstrap: a band tries a craft, "
            f"the gates permit it or they do not, and the band "
            f"finds out by failing. It has state, it takes steps, "
            f"and it keeps a record -- which is the difference "
            f"between this and every module before it")


def _order():
    from engine.artifact import bootstrap, held_by_round
    w = run()
    seen = w.first_seen()
    rounds = {}
    for i, _t, got in bootstrap():
        for g in got:
            rounds[g] = i
    pairs = [(seen[c], rounds[c]) for c in seen if c in rounds]
    con = dis = 0
    for i, (ya, ra) in enumerate(pairs):
        for yb, rb in pairs[i + 1:]:
            if ya == yb or ra == rb:
                continue
            if (ya > yb) == (ra > rb):
                con += 1
            else:
                dis += 1
    tau = (con - dis) / (con + dis) if con + dis else 0.0
    if tau < 0.5:
        raise ArithmeticError(f"tau {tau:.2f}")
    return (f"the bands cannot see the gates and nothing in the "
            f"step function reads engine/artifact.bootstrap. They "
            f"pick a craft at random and try it. Yet the ORDER "
            f"they arrive in matches the derived bootstrap order "
            f"at Kendall tau {tau:.2f} over {con + dis} comparable "
            f"pairs -- {con} concordant, {dis} discordant. That is "
            f"the point of running it: an ordering that was a "
            f"theorem about melting points comes back out of a "
            f"stochastic search by people who do not know any "
            f"melting points")


def _novel():
    w = run()
    named, unnamed = w.named(), w.unnamed()
    tot = len(w.artifacts())
    if not unnamed or len(unnamed) < len(named):
        raise ArithmeticError(f"{len(named)} named, {len(unnamed)} not")
    sample = sorted(sorted(c) for c in list(unnamed)[:3])
    return (f"{tot:,} distinct things built. {len(named)} of them "
            f"have a name in engine/artifact.py and "
            f"{len(unnamed):,} do not, which is "
            f"{100*len(unnamed)/tot:.1f}%. That is not a failure "
            f"of the run and not noise: engine/artifact.py names "
            f"21 things and the reachable space is 2^21, so "
            f"almost everything physically permitted here was "
            f"never built in our world and has no word for it. "
            f"Three of them: {sample}. They are recorded with "
            f"everything else, because a combination that the "
            f"gates allow is a fact about this world whether or "
            f"not it is a fact about ours")


def _stall():
    """INVERTED. Fails if the search ever finds everything easily."""
    w = run()
    held, total = len(w.crafts_held()), len(PRIMITIVES)
    seen = w.first_seen()
    last = max(seen.values()) if seen else 0.0
    if held == total and last < w.year / 2:
        raise ArithmeticError(
            "every craft arrived in the first half of the run, "
            "which means the gates are not binding and the search "
            "is not a search")
    missing = sorted(set(PRIMITIVES) - w.crafts_held())
    return (f"after {w.year:.0f} years they hold {held} of {total} "
            f"crafts and the last arrived at year {last:.0f}. "
            f"Still missing: {missing if missing else 'nothing'}. "
            f"This is a SEARCH and a search can stall: a band that "
            f"has not stumbled on the prerequisite cannot try the "
            f"thing that needs it, and no amount of effort "
            f"substitutes. The run is gate-limited rather than "
            f"effort-limited, which is what every module before "
            f"this one asserted and none of them tested")


def _fitted():
    """INVERTED. Fails if a second fitted number appears.

    One is a calibration and can be declared. Two is a model
    being shaped to its answer.
    """
    import re
    from pathlib import Path as _P
    pat = re.compile(r"^([A-Z_][A-Z_0-9]*)\s*=\s*[^#]+#\s*FITTED")
    hits = []
    for path in sorted((_P(__file__).parent).glob("*.py")):
        for line in path.read_text().splitlines():
            m = pat.match(line.strip())
            if m:
                hits.append(f"{path.stem}.{m.group(1)}")
    if len(hits) != 1:
        raise ArithmeticError(
            f"{len(hits)} fitted constants across the engine: "
            f"{hits}. One is a calibration that can be declared; "
            f"two is a model being shaped to its answer")
    w = run()
    seen = w.first_seen()
    return (f"CRAFT_SUCCESS = {CRAFT_SUCCESS:.0e} is FITTED, and "
            f"it is the only fitted number in this repository. It "
            f"was set so the tree completes in about the "
            f"Holocene -- the last craft lands at year "
            f"{max(seen.values()):.0f} -- which is tuning a "
            f"parameter to reproduce an answer. Everything else "
            f"here is EXACT, MEASURED, CHOSEN, RECORDED or "
            f"ENACTED, and the difference matters: a CHOSEN "
            f"number is a judgement somebody can disagree with, "
            f"a FITTED one has already been told the answer. So "
            f"nothing from this run may be quoted as a prediction "
            f"of the TIMESCALE, because the timescale is what was "
            f"fitted. The ORDER was not fitted and is the result. "
            f"engine/innovation.useful_fraction was tried first "
            f"and is a category error -- it measures omissions in "
            f"a genome, not human craft attempts -- and it gives "
            f"9 crafts of 21 in fourteen thousand years")


def _spec():
    w = run()
    late = max(w.unnamed(), key=lambda c: (len(c), sorted(c)))
    sheet = spec(late, w)
    if sheet["named in our world"] is not None:
        raise ArithmeticError("picked a named one")
    if not sheet["made of"] or sheet["first built"] is None:
        raise ArithmeticError(f"{sheet}")
    parts = " + ".join(p for p, _w in sheet["made of"])
    return (f"anything in the ledger can be given a sheet, and the "
            f"sheet is real where a name would not be. Take "
            f"{parts}, first built in year "
            f"{sheet['first built'][0]:.0f} by band "
            f"{sheet['first built'][1]}: it needs a fire of "
            f"{sheet['fire']} K and a tolerance of "
            f"{sheet['tolerance']:.0e}, and it rests on "
            f"{len(sheet['rests on'])} crafts that must exist "
            f"first ({', '.join(sheet['rests on'][:4])}...). That "
            f"is what it is MADE OF and what it COSTS to attempt. "
            f"What the sheet does not say is what it DOES, "
            f"because a set of capabilities is a requirement list "
            f"and not a design. Naming it would be inventing, and "
            f"the {len(w.unnamed()):,} unnamed things in this "
            f"ledger are unnamed on purpose")


if __name__ == "__main__":
    w = run()
    print(f"  {len(w.bands)} bands, {w.year:.0f} years, "
          f"{len(w.ledger):,} ledger entries\n")
    print(f"  {'craft':<15}{'first seen':>12}")
    for c, y in sorted(w.first_seen().items(), key=lambda kv: kv[1]):
        print(f"  {c:<15}{y:>12.0f}")
    print(f"\n  built {len(w.artifacts()):,} distinct things, "
          f"{len(w.named())} named, {len(w.unnamed()):,} unnamed\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
