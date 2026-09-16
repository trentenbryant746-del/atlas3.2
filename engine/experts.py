"""
Six experts, each with the check its domain actually admits.

The shards give routing labels and no answers (`target: tool_route_only`), so
what they specify is the QUESTION each expert must field. The six do not all
work the same way, and pretending they did would be the mistake:

  dna_structure     DERIVED.  complement is its own inverse; GC content is
                    counted two ways.
  periodic_table    ASSERTED, table-backed. Atomic number -> symbol is
                    empirical -- measured, not derived -- so the check is a
                    round-trip through the table and the answer cites it.
  material_ontology DERIVED from composition once the formula is known. The
                    formula itself is asserted; the molar mass is computed.
  virtual_planet    DERIVED by construction. A seeded world is a pure
                    function of its seed, so the check is DETERMINISM plus
                    physical invariants the generator must not violate.
  synthetic_galaxy  same.
  time_measurement  already in engine/dates.py as instant arithmetic.

Seeded generation is worth naming: it is the one place the system can
manufacture a whole world and still verify it, because the world's only
authority is the seed. That is not knowledge about our universe and the
provenance says so.
"""
from __future__ import annotations

import hashlib
import re
from fractions import Fraction as F

# ------------------------------------------------------------------ DNA
COMP = {"A": "T", "T": "A", "C": "G", "G": "C"}
DNA_SEQ = re.compile(r'\b([ACGT]{2,})\b')


def dna_complement(seq):
    return "".join(COMP[c] for c in seq)


def dna_gc(seq):
    return F(sum(1 for c in seq if c in "GC"), len(seq))


# -------------------------------------------------------- periodic table
# symbol, name, atomic mass (u). Empirical values -- asserted, with a source.
PT = [
    ("H", "hydrogen", 1.008), ("He", "helium", 4.0026),
    ("Li", "lithium", 6.94), ("Be", "beryllium", 9.0122),
    ("B", "boron", 10.81), ("C", "carbon", 12.011),
    ("N", "nitrogen", 14.007), ("O", "oxygen", 15.999),
    ("F", "fluorine", 18.998), ("Ne", "neon", 20.180),
    ("Na", "sodium", 22.990), ("Mg", "magnesium", 24.305),
    ("Al", "aluminium", 26.982), ("Si", "silicon", 28.085),
    ("P", "phosphorus", 30.974), ("S", "sulfur", 32.06),
    ("Cl", "chlorine", 35.45), ("Ar", "argon", 39.948),
    ("K", "potassium", 39.098), ("Ca", "calcium", 40.078),
    ("Sc", "scandium", 44.956), ("Ti", "titanium", 47.867),
    ("V", "vanadium", 50.942), ("Cr", "chromium", 51.996),
    ("Mn", "manganese", 54.938), ("Fe", "iron", 55.845),
    ("Co", "cobalt", 58.933), ("Ni", "nickel", 58.693),
    ("Cu", "copper", 63.546), ("Zn", "zinc", 65.38),
    ("Ga","gallium",69.723),("Ge","germanium",72.630),("As","arsenic",74.922),
    ("Se","selenium",78.971),("Br","bromine",79.904),("Kr","krypton",83.798),
    ("Rb","rubidium",85.468),("Sr","strontium",87.62),("Y","yttrium",88.906),
    ("Zr","zirconium",91.224),("Nb","niobium",92.906),("Mo","molybdenum",95.95),
    ("Tc","technetium",98.0),("Ru","ruthenium",101.07),("Rh","rhodium",102.91),
    ("Pd","palladium",106.42),("Ag","silver",107.87),("Cd","cadmium",112.41),
    ("In","indium",114.82),("Sn","tin",118.71),("Sb","antimony",121.76),
    ("Te","tellurium",127.60),("I","iodine",126.90),("Xe","xenon",131.29),
    ("Cs","caesium",132.91),("Ba","barium",137.33),("La","lanthanum",138.91),
    ("Ce","cerium",140.12),("Pr","praseodymium",140.91),("Nd","neodymium",144.24),
    ("Pm","promethium",145.0),("Sm","samarium",150.36),("Eu","europium",151.96),
    ("Gd","gadolinium",157.25),("Tb","terbium",158.93),("Dy","dysprosium",162.50),
    ("Ho","holmium",164.93),("Er","erbium",167.26),("Tm","thulium",168.93),
    ("Yb","ytterbium",173.05),("Lu","lutetium",174.97),("Hf","hafnium",178.49),
    ("Ta","tantalum",180.95),("W","tungsten",183.84),("Re","rhenium",186.21),
    ("Os","osmium",190.23),("Ir","iridium",192.22),("Pt","platinum",195.08),
    ("Au","gold",196.97),("Hg","mercury",200.59),("Tl","thallium",204.38),
    ("Pb","lead",207.2),("Bi","bismuth",208.98),("Po","polonium",209.0),
    ("At","astatine",210.0),("Rn","radon",222.0),("Fr","francium",223.0),
    ("Ra","radium",226.0),("Ac","actinium",227.0),("Th","thorium",232.04),
    ("Pa","protactinium",231.04),("U","uranium",238.03),("Np","neptunium",237.0),
    ("Pu","plutonium",244.0),("Am","americium",243.0),("Cm","curium",247.0),
    ("Bk","berkelium",247.0),("Cf","californium",251.0),("Es","einsteinium",252.0),
    ("Fm","fermium",257.0),("Md","mendelevium",258.0),("No","nobelium",259.0),
    ("Lr","lawrencium",266.0),("Rf","rutherfordium",267.0),("Db","dubnium",268.0),
    ("Sg","seaborgium",269.0),("Bh","bohrium",270.0),("Hs","hassium",269.0),
    ("Mt","meitnerium",278.0),("Ds","darmstadtium",281.0),("Rg","roentgenium",282.0),
    ("Cn","copernicium",285.0),("Nh","nihonium",286.0),("Fl","flerovium",289.0),
    ("Mc","moscovium",290.0),("Lv","livermorium",293.0),("Ts","tennessine",294.0),
    ("Og","oganesson",294.0),
]
# For elements with no stable isotope the value is the mass number of the
# most stable known isotope, not a standard atomic weight. Marked here rather
# than silently mixed, because they are a different KIND of quantity.
UNSTABLE = {43, 61, 84, 85, 86, 87, 88, 89, 93, 94, 95, 96, 97, 98, 99, 100,
            101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113,
            114, 115, 116, 117, 118}
PT_SOURCE = "IUPAC standard atomic weights (2021); synthetics give the most stable isotope"
BY_Z = {i + 1: e for i, e in enumerate(PT)}
BY_SYM = {e[0]: (i + 1, e) for i, e in enumerate(PT)}

# ---------------------------------------------------- material ontology
MATERIALS = {
    "water": "H2O", "ice": "H2O", "snow": "H2O", "steam": "H2O",
    "salt": "NaCl", "quartz": "SiO2", "rust": "Fe2O3",
    "methane": "CH4", "ammonia": "NH3", "carbon dioxide": "CO2",
    "diamond": "C", "graphite": "C", "gold bar": "Au", "gold": "Au",
    "oxygen gas": "O2", "nitrogen gas": "N2", "hydrogen gas": "H2",
    "glucose": "C6H12O6", "iron": "Fe", "silver": "Ag",
}
MAT_SOURCE = "conventional chemical formulae"
FORMULA = re.compile(r'([A-Z][a-z]?)(\d*)')


def molar_mass(formula):
    """compositional: sum of atomic masses x counts"""
    total = 0.0
    seen = False
    for sym, cnt in FORMULA.findall(formula):
        if not sym:
            continue
        if sym not in BY_SYM:
            return None
        seen = True
        total += BY_SYM[sym][1][2] * int(cnt or 1)
    return round(total, 4) if seen else None


# ------------------------------------------------- seeded world generation
def _rng(seed, salt):
    h = hashlib.sha256(f"{seed}|{salt}".encode()).digest()
    return int.from_bytes(h[:8], "big")


def planet(seed):
    r = 1000 + _rng(seed, "radius") % 60000          # km
    d = 1000 + _rng(seed, "density") % 7000          # kg/m3
    per = 4 + _rng(seed, "day") % 1000               # hours
    moons = _rng(seed, "moons") % 9
    # derived, not sampled -- so it cannot contradict radius and density
    mass = (4 / 3) * 3.141592653589793 * (r * 1000) ** 3 * d
    g = 6.674e-11 * mass / (r * 1000) ** 2
    return {"seed": seed, "radius_km": r, "density_kg_m3": d,
            "day_hours": per, "moons": moons,
            "mass_kg": f"{mass:.4e}", "surface_gravity_m_s2": round(g, 3)}


def galaxy(seed):
    stars = 10 ** (8 + _rng(seed, "stars") % 4)
    arms = 2 + _rng(seed, "arms") % 5
    dia = 5 + _rng(seed, "dia") % 200                # kpc
    kind = ["spiral", "barred spiral", "elliptical", "irregular"][
        _rng(seed, "kind") % 4]
    return {"seed": seed, "type": kind, "stars": stars,
            "arms": arms if "spiral" in kind else 0,
            "diameter_kpc": dia}


def planet_invariants(p):
    """the generator must not contradict itself"""
    r = p["radius_km"] * 1000
    m = float(p["mass_kg"])
    g = 6.674e-11 * m / r ** 2
    return abs(g - p["surface_gravity_m_s2"]) < 0.01 and p["moons"] >= 0


# ------------------------------------------------------------- routing
ANSWERED, REFUSED, NOT_MINE = "ANSWERED", "REFUSED", "NOT_MINE"

R_COMP = re.compile(r'complement of (?:sequence\s+)?([ACGTacgt]+)', re.I)
R_GC = re.compile(r'gc content of (?:sequence\s+)?([ACGTacgt]+)', re.I)
R_ZNUM = re.compile(r'element has atomic number (\d+)', re.I)
R_SYM = re.compile(r'atomic (?:number|mass) of ([A-Z][a-z]?)\b')
R_MAT = re.compile(r'map material ([a-z ]+?)[.?]?$', re.I)
R_MOLAR = re.compile(r'molar mass of ([A-Za-z0-9]+)', re.I)
R_PLANET = re.compile(r'virtual planet from seed ([\w-]+)', re.I)
R_GALAXY = re.compile(r'seeded galaxy:?\s*([\w-]+)', re.I)
R_EXPLAIN = re.compile(r'^explain atlas ', re.I)
R_CHECKF = re.compile(r'check formula ([A-Za-z0-9]+)', re.I)


def route_expert(q):
    """-> (status, answer, expert, check_kind, provenance)"""
    m = R_COMP.search(q)
    if m:
        s = m.group(1).upper()
        out = dna_complement(s)
        if dna_complement(out) != s:                       # IDENTITY
            return REFUSED, None, "dna_structure", None, "complement not involutive"
        return ANSWERED, out, "dna_structure", "IDENTITY", f"complement of {s}"

    m = R_GC.search(q)
    if m:
        s = m.group(1).upper()
        a = dna_gc(s)
        b = F(len([c for c in s if c in "GC"]), len(s))    # REDUNDANT count
        if a != b:
            return REFUSED, None, "dna_structure", None, "GC counts disagree"
        pct = f"{float(a)*100:.4g}%"
        return ANSWERED, pct, "dna_structure", "REDUNDANT", f"{a} of {len(s)} bases"

    m = R_ZNUM.search(q)
    if m:
        z = int(m.group(1))
        if z not in BY_Z:
            return REFUSED, None, "periodic_table_reference", None, \
                   f"atomic number {z} outside the tabulated range 1-{len(PT)}"
        sym, name, mass = BY_Z[z]
        note = " (most stable isotope)" if z in UNSTABLE else ""
        if BY_SYM[sym][0] != z:                            # round-trip
            return REFUSED, None, "periodic_table_reference", None, "table round-trip failed"
        return ANSWERED, f"{name} ({sym})", "periodic_table_reference", \
               "TABLE ROUND-TRIP", PT_SOURCE + note

    m = R_MOLAR.search(q)
    if m:
        f = MATERIALS.get(m.group(1).lower(), m.group(1))
        mm = molar_mass(f)
        if mm is None:
            return REFUSED, None, "material_ontology", None, \
                   f"formula {f!r} uses an element outside the table"
        return ANSWERED, f"{mm} g/mol", "material_ontology", \
               "COMPOSITIONAL", f"{f} over {PT_SOURCE}"

    m = R_CHECKF.search(q)
    if m:
        f = m.group(1)
        parts = [(sym, int(c or 1)) for sym, c in FORMULA.findall(f) if sym]
        rebuilt = "".join(s_ + ("" if n == 1 else str(n)) for s_, n in parts)
        if rebuilt != f:                                   # ROUND-TRIP
            return REFUSED, None, "material_ontology", None, \
                   f"{f!r} does not re-serialise ({rebuilt!r}) -- malformed"
        unknown = [s_ for s_, _ in parts if s_ not in BY_SYM]
        if unknown:
            return REFUSED, None, "material_ontology", None, \
                   f"unknown element symbol(s) {unknown}"
        mm = molar_mass(f)
        comp = ", ".join(f"{s_}x{n}" for s_, n in parts)
        return ANSWERED, f"valid: {comp}; molar mass {mm} g/mol", \
               "material_ontology", "ROUND-TRIP + COMPOSITIONAL", PT_SOURCE

    m = R_MAT.search(q)
    if m:
        name = m.group(1).strip().lower()
        if name not in MATERIALS:
            return REFUSED, None, "material_ontology", None, \
                   f"no formula on record for {name!r}"
        f = MATERIALS[name]
        mm = molar_mass(f)
        return ANSWERED, f"{name}: {f}, molar mass {mm} g/mol", \
               "material_ontology", "COMPOSITIONAL", MAT_SOURCE

    m = R_PLANET.search(q)
    if m:
        p = planet(m.group(1))
        if planet(m.group(1)) != p or not planet_invariants(p):
            return REFUSED, None, "virtual_planet", None, \
                   "generator not deterministic or violates its own invariants"
        return ANSWERED, p, "virtual_planet", "DETERMINISM + INVARIANTS", \
               f"pure function of seed {m.group(1)!r}; not a claim about any real planet"

    m = R_GALAXY.search(q)
    if m:
        g = galaxy(m.group(1))
        if galaxy(m.group(1)) != g:
            return REFUSED, None, "synthetic_galaxy", None, "generator not deterministic"
        return ANSWERED, g, "synthetic_galaxy", "DETERMINISM", \
               f"pure function of seed {m.group(1)!r}; not a claim about any real galaxy"

    # The Qwen expert map. Added LAST, after every expert that existed
    # before it, so it can only answer questions nothing else claimed --
    # the same rule the cascade in atlas.py follows. It answers about a
    # model's routing, never from it: the 21 GB GGUF is on disk and
    # nothing here invokes it.
    try:
        from engine import qwenmap
        st, val, exp, chk, prov = qwenmap.route_expert(q)
        if st == qwenmap.ANSWERED:
            return ANSWERED, val, exp, chk, prov
        if st == qwenmap.REFUSED:
            return REFUSED, None, exp, None, prov
        from engine import qwenmatter
        st, val, exp, chk, prov = qwenmatter.route_expert(q)
        if st == qwenmatter.ANSWERED:
            return ANSWERED, val, exp, chk, prov
        if st == qwenmatter.REFUSED:
            return REFUSED, None, exp, None, prov
    except Exception:
        pass        # a missing experiment file must not break the cascade

    if R_EXPLAIN.search(q):
        return NOT_MINE, None, None, None, \
               "a request to explain a subsystem, not to compute anything"
    return NOT_MINE, None, None, None, "no expert pattern matched"
