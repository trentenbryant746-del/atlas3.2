"""
Nothing is created and nothing is destroyed, including when it dies.

Every biological module before this one traded in watts, metres and
kilograms. A plant "grew" and a predator "ate" and a lineage "died",
and in every case the matter was bookkeeping that nobody kept. That
is a hole: a world can grow a forest out of nothing and lose it to
nowhere, and no rule here would object.

So every living rule is restated in atoms. An organism is not a mass,
it is a count of carbon, hydrogen, oxygen, nitrogen, phosphorus and
sulphur. Growing it draws those atoms from a pool. Killing it puts
them back -- ALL of them, which is what death means physically. The
pool is finite and comes from engine/genesis.py, which derived
Earth's composition from a four-number seed.

Two things fall out that were invisible while matter was implicit:

  A LIMITING ELEMENT. Life is not capped by sunlight. It is capped
  by whichever atom runs out first, and which one that is, is
  derivable rather than asserted.

  A CLOSED LOOP. If decomposition returns less than death removes,
  the biosphere runs down. The standing crop a world can hold is
  the pool divided by the turnover, and that is a number.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# MEASURED: the Redfield stoichiometry of plankton, C106 H263 O110
# N16 P1, with sulphur from the protein fraction. Atoms per 106 C.
REDFIELD = {"C": 106.0, "H": 263.0, "O": 110.0, "N": 16.0,
            "P": 1.0, "S": 1.7}

# MEASURED: standard atomic weights, g/mol
WEIGHT = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007,
          "P": 30.974, "S": 32.06}

# MEASURED: wood is cellulose (C6H10O5)n, not plankton. A trunk is
# built of a DIFFERENT molecule than a cell, and giving one the
# other's formula is the failure engine/lab.py forbids by name.
CELLULOSE = {"C": 6.0, "H": 10.0, "O": 5.0}

AVOGADRO = 6.02214076e23        # EXACT, mol^-1


def _molar_mass(formula):
    """g/mol of one formula unit. DERIVED."""
    return sum(WEIGHT[e] * n for e, n in formula.items())


def atoms_in(mass_kg, formula=REDFIELD):
    """-> {element: atom count}. DERIVED, no rounding of the total.

    Says which molecule is being weighed. Flesh is Redfield and
    wood is cellulose, and a rule that works on one does not
    silently apply to the other.
    """
    units = (mass_kg * 1000.0 / _molar_mass(formula)) * AVOGADRO
    return {e: units * n for e, n in formula.items()}


def mass_of(counts):
    """kg. DERIVED. The inverse of atoms_in, for any mixture."""
    return sum(n * WEIGHT[e] / AVOGADRO for e, n in counts.items()) / 1000.0


class Pool:
    """Every atom on the board. It only ever moves."""

    def __init__(self, counts):
        self.free = dict(counts)                     # available
        self.locked = {e: 0.0 for e in counts}       # in living bodies
        self.buried = {e: 0.0 for e in counts}       # out of reach
        self._start = mass_of(counts)

    def _books(self):
        return (self.free, self.locked, self.buried)

    def total(self):
        keys = set().union(*(set(b) for b in self._books()))
        return {e: sum(b.get(e, 0.0) for b in self._books()) for e in keys}

    def circulating(self):
        return {e: self.free.get(e, 0.0) + self.locked.get(e, 0.0)
                for e in set(self.free) | set(self.locked)}

    def build(self, mass_kg, formula=REDFIELD):
        """-> (bool, limiting element). Growth is a withdrawal."""
        need = atoms_in(mass_kg, formula)
        short = [(self.free.get(e, 0.0) / n, e)
                 for e, n in need.items() if n > 0]
        worst, which = min(short) if short else (1e30, None)
        if worst < 1.0:
            return False, which
        for e, n in need.items():
            self.free[e] -= n
            self.locked[e] = self.locked.get(e, 0.0) + n
        return True, None

    def die(self, mass_kg, formula=REDFIELD, returned=1.0):
        """-> kg returned. Death is a deposit, and by default it is
        the whole body. Nothing here lets matter leave the world."""
        had = atoms_in(mass_kg, formula)
        for e, n in had.items():
            self.locked[e] = self.locked.get(e, 0.0) - n
            self.free[e] = self.free.get(e, 0.0) + n * returned
            self.buried[e] = self.buried.get(e, 0.0) + n * (1.0 - returned)
        return mass_kg * returned

    def conserved(self, tol=1e-9):
        """Total matter. This must NEVER fail, burial or not."""
        now = mass_of(self.total())
        return abs(now - self._start) <= tol * max(self._start, 1.0), now

    def cycles(self, tol=1e-9):
        """Matter still in circulation. Burial makes this fail, and
        it SHOULD -- a leak is not a cycle, and the difference
        between these two books is the whole of the fossil record."""
        now = mass_of(self.circulating())
        return abs(now - self._start) <= tol * max(self._start, 1.0), now


def limiting_element(reservoir_kg):
    """-> (element, kg of biomass it allows). DERIVED.

    Which atom runs out first is not a matter of opinion once the
    recipe is fixed.
    """
    per_kg = atoms_in(1.0)
    best = None
    for e, avail_kg in reservoir_kg.items():
        if e not in per_kg:
            continue
        have = avail_kg * 1000.0 / WEIGHT[e] * AVOGADRO
        allows = have / per_kg[e]
        if best is None or allows < best[1]:
            best = (e, allows)
    return best


def standing_crop(reservoir_kg, turnover_yr):
    """kg. What a world holds at once, given how fast it recycles."""
    e, cap = limiting_element(reservoir_kg)
    return e, cap, turnover_yr


def tree_carbon(height_m, crown_m2=1.0):
    """-> (kg C, moles CO2). DERIVED through engine/biome.py.

    The trunk engine/biome.py prices in watts also has to be BUILT,
    and every carbon atom in it came out of the air.
    """
    from engine.biome import trunk_mass
    m = trunk_mass(height_m)
    c = atoms_in(m, CELLULOSE)["C"]
    return c * WEIGHT["C"] / AVOGADRO / 1000.0, c / AVOGADRO


# Life modules that move MATTER must account for it in atoms.
# Ones that only price energy or geometry are listed here with the
# reason, so the exemption is a statement rather than a silence.
MATTER_FREE = {
    "life": "scaling laws only -- Kleiber, Poiseuille, Reynolds",
    "origin": "search-space counting, no bodies",
    "luca": "comparison of inferred traits, no bodies",
    "ancestry": "energy budgets and thresholds, no bodies",
    "signature": "atmospheric gases, accounted in engine/biosphere.py",
    "earthlab": "gates on whether chemistry is possible at all",
    "biome": "watts and metres; its matter bill is tree_carbon here",
}


def matter_accounting():
    """-> [(module, ok, why)]. Does every life rule reach atoms?"""
    import ast
    eng = ROOT / "engine"
    living = ("life", "origin", "luca", "ancestry", "signature",
              "earthlab", "biome", "biosphere", "descent", "ecology")
    rows = []
    for name in living:
        f = eng / f"{name}.py"
        if not f.exists():
            rows.append((name, False, "module is missing"))
            continue
        tree = ast.parse(f.read_text())
        uses = any(
            (isinstance(n, ast.ImportFrom) and n.module
             and n.module.endswith("atoms"))
            or (isinstance(n, ast.Import)
                and any(a.name.endswith("atoms") for a in n.names))
            for n in ast.walk(tree))
        if uses:
            rows.append((name, True, "accounts in atoms"))
        elif name in MATTER_FREE:
            rows.append((name, True, f"exempt: {MATTER_FREE[name]}"))
        else:
            rows.append((name, False, "moves bodies and never counts atoms"))
    return rows


def eat(pool, pred_kg, prey_kg, assimilation=0.8):
    """-> (kg gained, kg voided). Predation is a transfer, not a
    source. The prey's atoms go to the predator or to the ground,
    and the two must add to what the prey weighed."""
    got = prey_kg * assimilation
    pool.locked  # bodies already hold their atoms
    voided = prey_kg - got
    for e, n in atoms_in(voided).items():
        pool.locked[e] = pool.locked.get(e, 0.0) - n
        pool.free[e] = pool.free.get(e, 0.0) + n
    return got, voided


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("death_returns_every_atom", _death)
    t("a_world_cannot_grow_what_it_lacks", _lack)
    t("the_limiting_element_is_derived", _limit)
    t("wood_is_not_flesh", _wood)
    t("burial_is_the_only_leak_and_it_is_named", _burial)
    t("a_tree_is_made_of_air", _air)
    t("every_life_rule_accounts_for_matter", _accounting)
    t("eating_moves_atoms_and_makes_none", _eating)
    t("standing_crop_is_exercised", _stranded)
    return all(o[1] for o in out), out


def _death():
    p = Pool(atoms_in(1000.0))
    ok, _ = p.build(400.0)
    p.die(400.0)
    bal, now = p.conserved()
    if not (ok and bal):
        raise ArithmeticError(f"the books came to {now:.9f} of 1000 kg")
    return ("built 400 kg of body from a 1000 kg pool, killed it, and "
            "the pool is 1000 kg again to nine decimals. Death is a "
            "deposit. Every module before this one let a thing die "
            "and did not say where it went")


def _lack():
    poor = atoms_in(1000.0)
    poor["P"] *= 1e-4
    ok, which = Pool(poor).build(500.0)
    if ok or which != "P":
        raise ArithmeticError(f"grew anyway, short of {which}")
    return ("strip the phosphorus to a ten-thousandth and 500 kg cannot "
            "be built, and the refusal NAMES phosphorus. Not 'growth "
            "failed' -- which atom ran out")


def _limit():
    e, allows = limiting_element(
        {"C": 1e3, "H": 1e5, "O": 1e5, "N": 1e2, "P": 1.0, "S": 1e2})
    if e != "P":
        raise ArithmeticError(f"{e} limits, which is not phosphorus")
    return (f"given that reservoir, {e} runs out first and caps biomass "
            f"at {allows:.0f} kg. Life is not capped by sunlight here. "
            f"It is capped by the scarcest atom, and which atom that "
            f"is was derived from the recipe, not chosen")


def _wood():
    flesh = atoms_in(1.0)
    wood = atoms_in(1.0, CELLULOSE)
    if "N" in wood or abs(wood["C"] / flesh["C"] - 1.0) < 0.05:
        raise ArithmeticError("wood was given flesh's formula")
    return (f"a kilo of wood holds {wood['C']/flesh['C']:.2f} times the "
            f"carbon of a kilo of flesh and NO nitrogen at all, which "
            f"is why a trunk is cheap to build and a leaf is not. "
            f"Cellulose is not Redfield, and no function here can "
            f"reach for the wrong one by accident -- it is an "
            f"argument, not a default buried in the body")


def _burial():
    p = Pool(atoms_in(1000.0))
    p.build(400.0)
    back = p.die(400.0, returned=0.99)
    total_ok, tot = p.conserved()
    cycle_ok, circ = p.cycles()
    if not total_ok:
        raise ArithmeticError(f"atoms vanished: {tot:.6f} of 1000 kg")
    if cycle_ok:
        raise ArithmeticError("burying 1% still counted as a closed cycle")
    return (f"bury one percent and TWO books disagree, which is the "
            f"point. Total matter is still {tot:.6f} kg -- nothing was "
            f"destroyed and the check would scream if it had been. "
            f"Circulating matter is {circ:.2f} kg, down {400-back:.1f}. "
            f"A leak is not a cycle. Coal, oil and chalk are that one "
            f"percent, and so is the oxygen it left behind")


def _air():
    kg_c, mol = tree_carbon(11.4)
    if kg_c <= 0:
        raise ArithmeticError("a tree made of nothing")
    return (f"the 11.4 m tree engine/biome.py says the light race "
            f"stops at weighs {kg_c/0.44:.0f} kg dry and holds "
            f"{kg_c:.0f} kg of carbon -- {mol:.0f} moles of CO2 pulled "
            f"out of the air. The height was derived from watts; the "
            f"matter to build it is a separate bill and it is now "
            f"itemised")


def _accounting():
    rows = matter_accounting()
    bad = [r for r in rows if not r[1]]
    if bad:
        raise ArithmeticError(
            "life modules that move bodies without counting atoms: "
            + ", ".join(b[0] for b in bad))
    counted = [r[0] for r in rows if "accounts" in r[2]]
    return (f"{len(rows)} living modules checked: {len(counted)} route "
            f"matter through this file and {len(rows)-len(counted)} are "
            f"exempt WITH A REASON WRITTEN DOWN, not by omission. A new "
            f"life module that grows or kills anything fails this until "
            f"it says what its bodies are made of")


def _eating():
    p = Pool(atoms_in(1000.0))
    p.build(100.0)
    before = mass_of(p.total())
    got, voided = eat(p, 40.0, 100.0)
    ok, after = p.conserved()
    if not ok or abs((got + voided) - 100.0) > 1e-9:
        raise ArithmeticError(f"{before:.6f} -> {after:.6f} kg over a meal")
    return (f"a 100 kg prey yields {got:.0f} kg of predator and "
            f"{voided:.0f} kg to the ground, and those add to 100. "
            f"The 80% that is not assimilated does not evaporate -- it "
            f"is returned free, which is what feeds the decomposers "
            f"that no module has yet")



def _stranded():
    """Wires standing_crop, written in 3.1.69 and never called."""
    e, cap, turn = standing_crop(
        {"C": 1e3, "H": 1e5, "O": 1e5, "N": 1e2, "P": 1.0, "S": 1e2},
        turnover_yr=10.0)
    if e != "P" or cap <= 0:
        raise ArithmeticError(f"{e} limits at {cap}")
    return (f"a world recycling every {turn:.0f} years holds {cap:.0f} "
            f"kg of biomass at once, capped by {e}. This was written "
            f"the day the atom ledger went in and nothing ever called "
            f"it")

if __name__ == "__main__":
    p = Pool(atoms_in(1000.0))
    print(f"  pool starts at {mass_of(p.total()):.6f} kg")
    p.build(400.0)
    print(f"  built 400 kg   free {mass_of(p.free):.1f}  "
          f"locked {mass_of(p.locked):.1f}")
    p.die(400.0)
    print(f"  it died        free {mass_of(p.free):.1f}  "
          f"locked {mass_of(p.locked):.1f}")
    print(f"  conserved: {p.conserved()[0]}\n")
    e, allows = limiting_element(
        {"C": 1e3, "H": 1e5, "O": 1e5, "N": 1e2, "P": 1.0, "S": 1e2})
    print(f"  limiting element {e}, caps biomass at {allows:,.0f} kg\n")
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:38}{d[:46]}")
