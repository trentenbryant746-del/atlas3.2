"""
A universe in chunks, so it can hold as much matter as it needs to.

engine/cosmos.py runs four generations of three stars: twelve stars,
251 solar masses, and about 1e56 hydrogen atoms. That is a model of
a mechanism, not a universe, and it cannot be made denser by adding
stars to a list -- the list is what it costs.

So a universe is PARTITIONED, the same way engine/chunks.py
partitions a corpus it cannot prefill. Each chunk is an independent
region with its own derived seed, and the universe is the ordered
set of them. Ten chunks or ten million: the rules are identical in
each, and what changes is how much matter the whole contains.

DENSITY COMES FROM COUNTING, NOT FROM STORING. A chunk does not
hold atoms. It holds a mass and a composition, and the atom count
follows:

    N(element) = M_chunk * f(element) / (A * u)

so a chunk of 251 solar masses contains 2.2e56 hydrogen atoms
whether or not anyone writes them down. That is the same rule the
1e9-token corpus runs on -- derive, do not materialise -- applied
to matter instead of text. A universe can be reported as holding
1e62 atoms at no cost in memory, because the number is computed
from three quantities rather than stored in 1e62 records.

CONSISTENT ACROSS UNIVERSES, AND MEASURABLY SO. A chunking is only
useful if chunk k of one universe means the same thing as chunk k
of another. So the partition rule is fixed and derived, never
sampled: chunk k's seed is hmac(universe key, k), which makes it
reproducible from the key alone, independent of its neighbours, and
different in every universe. consistency() then checks across
universes that every chunk obeys the same laws, that the count is
the same, and that the heads differ -- same structure, different
history, which is the pair of properties that makes two universes
comparable at all.

EVERY CHUNK IS KEYED AND THE KEYS CHAIN. A chunk key is
hmac(universe key, index), and the chunk digests link into one
256-bit head for the whole universe -- engine/chain.py's discipline
applied to space as well as time. Hand back a chunk key and that
chunk alone can be regenerated and matched against the head, with
nothing else rebuilt.
"""
from __future__ import annotations

import hashlib
import hmac
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine import chain, cosmos                             # noqa: E402
from engine.experts import BY_SYM                            # noqa: E402

DERIVED = "DERIVED"
U_KG = 1.66053906660e-27        # atomic mass unit
M_SUN_KG = 1.98847e30

# The partition rule. Fixed so chunk k means the same everywhere.
GENERATIONS = 4
STARS_PER_CHUNK = 3
DILUTION = 9.0


def chunk_key(universe_key, index):
    """hmac(universe key, index). Reproducible from the key alone."""
    if not universe_key:
        raise ValueError("a universe needs a key")
    return hmac.new(str(universe_key).encode(), str(index).encode(),
                    hashlib.sha256).hexdigest()


def chunk(universe_key, index):
    """One region. Seeded from its key, so neighbours do not matter."""
    k = chunk_key(universe_key, index)
    stars, gas, ledger = cosmos.run(generations=GENERATIONS, seed=k,
                                    stars_per_gen=STARS_PER_CHUNK,
                                    dilution=DILUTION)
    mass = sum(s.mass for s in stars)
    return {"index": index, "key": k, "mass_msun": mass,
            "composition": gas, "stars": len(stars),
            "conserved": all(r["conserved"] for r in ledger)}


def atoms_in(chunk_rec):
    """-> {element: count}. Derived, never stored."""
    out = {}
    kg = chunk_rec["mass_msun"] * M_SUN_KG
    for sym, frac in chunk_rec["composition"].items():
        base = sym.rstrip("0123456789")
        if base not in BY_SYM or frac <= 0:
            continue
        a = BY_SYM[base][1][2]
        out[base] = out.get(base, 0.0) + kg * frac / (a * U_KG)
    return out


def universe(universe_key, n_chunks=100):
    """-> dict. The chunks, their head, and what the whole contains."""
    chunks = [chunk(universe_key, i) for i in range(n_chunks)]
    states = [(c["key"], {"mass": round(c["mass_msun"], 9),
                          "stars": c["stars"],
                          "composition": {k: round(v, 12)
                                          for k, v in
                                          sorted(c["composition"].items())}})
              for c in chunks]
    ch = chain.build(str(universe_key), states)
    total = {}
    for c in chunks:
        for e, n in atoms_in(c).items():
            total[e] = total.get(e, 0.0) + n
    return {"key": str(universe_key), "chunks": chunks, "head": ch["head"],
            "chain": ch, "n": n_chunks,
            "mass_msun": sum(c["mass_msun"] for c in chunks),
            "atoms": total, "atom_total": sum(total.values())}


def projected(universe_key, n_chunks):
    """What N chunks would hold, WITHOUT running them.

    One chunk is enough to know the rest, because the partition rule
    is the same in each and the seed only moves which star masses
    come up. So the density of a universe is a multiplication, not a
    simulation -- which is what lets it be reported at 1e6 chunks.
    """
    c = chunk(universe_key, 0)
    per = sum(atoms_in(c).values())
    return {"chunks": n_chunks, "atoms_per_chunk": per,
            "atoms": per * n_chunks,
            "mass_msun": c["mass_msun"] * n_chunks}


def prove(u, key_of_chunk):
    """Regenerate ONE chunk from its key and match it to the head."""
    idx = next((c["index"] for c in u["chunks"]
                if c["key"] == key_of_chunk), None)
    if idx is None:
        raise KeyError("no such chunk key in this universe")
    c = chunk(u["key"], idx)
    want = u["chain"]["links"][idx + 1]["link"]
    prev = u["chain"]["links"][idx]["link"]
    got = chain.link(prev, {"epoch": c["key"],
                            "state": {"mass": round(c["mass_msun"], 9),
                                      "stars": c["stars"],
                                      "composition": {k: round(v, 12)
                                                      for k, v in
                                                      sorted(c["composition"].items())}}})
    return got == want, (f"chunk {idx} regenerated from its key alone and "
                         f"matches link {got[:16]}...")


def consistency(keys, n_chunks=6):
    """Across universes: same structure, different history."""
    us = [universe(k, n_chunks) for k in keys]
    rows = []
    rows.append(("same chunk count",
                 len({u["n"] for u in us}) == 1,
                 f"{[u['n'] for u in us]}"))
    rows.append(("laws hold in every chunk",
                 all(c["conserved"] for u in us for c in u["chunks"]),
                 f"{sum(len(u['chunks']) for u in us)} chunks, all mass "
                 f"conserved"))
    rows.append(("heads differ",
                 len({u["head"] for u in us}) == len(us),
                 f"{len({u['head'] for u in us})} distinct heads from "
                 f"{len(us)} keys"))
    masses = [u["mass_msun"] for u in us]
    spread = (max(masses) - min(masses)) / (sum(masses) / len(masses))
    rows.append(("comparable scale", spread < 0.5,
                 f"total mass varies {spread:.1%} across universes -- "
                 f"same rule, different draw"))
    els = [frozenset(u["atoms"]) for u in us]
    rows.append(("same elements present", len(set(els)) == 1,
                 f"{len(els[0])} elements in every universe"))
    return us, rows


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("density_is_counted", _dens)
    t("mass_conserved_across_chunks", _mass)
    t("chunk_proves_itself", _prove)
    t("consistent_across_universes", _cons)
    t("scales_without_running", _scale)
    return all(o[1] for o in out), out


def _dens():
    u = universe("universe-0", 8)
    per = u["atom_total"] / u["n"]
    return (f"{u['n']} chunks, {u['mass_msun']:,.0f} solar masses, "
            f"{u['atom_total']:.3e} atoms -- {per:.3e} per chunk, counted "
            f"from mass and composition and stored nowhere")


def _mass():
    u = universe("universe-0", 8)
    s = sum(c["mass_msun"] for c in u["chunks"])
    if abs(s - u["mass_msun"]) > 1e-9:
        raise ArithmeticError("chunk masses do not sum to the universe")
    bad = [c["index"] for c in u["chunks"] if not c["conserved"]]
    if bad:
        raise ArithmeticError(f"mass not conserved in chunks {bad}")
    return (f"{len(u['chunks'])} chunks sum to {s:,.2f} solar masses "
            f"exactly, and every one conserves mass internally")


def _prove():
    u = universe("universe-0", 6)
    ok, why = prove(u, u["chunks"][3]["key"])
    if not ok:
        raise ArithmeticError(why)
    bad = chunk_key("another universe", 3)
    try:
        prove(u, bad)
    except KeyError:
        return (f"{why}; a key from another universe is refused rather "
                f"than matched to the same index")
    raise ArithmeticError("a foreign chunk key was accepted")


def _cons():
    _us, rows = consistency(["universe-0", "universe-1", "universe-2"], 5)
    bad = [n for n, ok, _d in rows if not ok]
    if bad:
        raise ArithmeticError(f"inconsistent across universes: {bad}")
    return "; ".join(f"{n}" for n, _ok, _d in rows)


def _scale():
    p1 = projected("universe-0", 1)
    p6 = projected("universe-0", 1_000_000)
    if abs(p6["atoms"] / p1["atoms"] - 1_000_000) > 1:
        raise ArithmeticError("projection is not linear in chunks")
    return (f"one chunk holds {p1['atoms']:.3e} atoms, so a million hold "
            f"{p6['atoms']:.3e} across {p6['mass_msun']:.3e} solar "
            f"masses -- reported without running them, because the rule "
            f"is the same in each")


if __name__ == "__main__":
    u = universe("universe-0", 10)
    print(f"universe {u['key']!r}: {u['n']} chunks, "
          f"{u['mass_msun']:,.0f} solar masses")
    print(f"  head        {u['head']}")
    print(f"  atoms       {u['atom_total']:.4e}")
    for e, n in sorted(u["atoms"].items(), key=lambda kv: -kv[1])[:6]:
        print(f"    {e:<4}{n:.4e}")
    print()
    for n in (10, 1_000, 1_000_000, 1_000_000_000):
        p = projected("universe-0", n)
        print(f"  {n:>13,} chunks -> {p['atoms']:.3e} atoms, "
              f"{p['mass_msun']:.3e} Msun")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:32}{d[:92]}")
    print("\nall:", ok)
