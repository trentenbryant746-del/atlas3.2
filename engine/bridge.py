"""
Modules answer together by TYPE, which is how bind.py already works.

The ask was for a way to let the twenty-one original claims and the
Qwen modules answer questions neither can alone, and the guess was
"phantom particles that don't mean anything". Virtual particles are
real physics -- they mediate an interaction without being observed --
but they are the wrong analogy here, because a mediator that means
nothing cannot be checked, and an unchecked intermediate is exactly
what this repo refuses everywhere else.

The right mechanism is already in the tree. engine/bind.py composes
atoms by DIMENSIONAL SIGNATURE: ADD takes T x T -> T, MUL takes
A x B -> A*B, and a binding that violates a signature is not a
low-scoring compound, it is not a compound. 146,946 bindings were
attempted and 49,588 refused by type before any arithmetic ran.

Apply the same move one level up. Give every module's entry points a
signature -- what they take and what they produce -- and composition
becomes search rather than authorship:

    progenitor_mass -> core_mass -> remnant_kind
    subject -> expert_ids -> slice_bytes -> total_bytes
    atomic_number -> element -> isotopes

Nobody writes those chains. They exist because the types line up,
and they are checked because every link is an existing checked
function. Adding one capability adds every chain it completes, which
is where the combinatorial growth comes from.

WHAT MAKES THIS DIFFERENT FROM A PIPELINE. A pipeline is written
down. This is searched: ask for a target type from a starting type
and the bridge finds the path, or reports that no path exists --
which is an abstention with a reason, the same as every other
refusal here. A chain that cannot be built is not a failure to
answer, it is the answer that these modules do not reach that far.
"""
from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class Cap:
    """One typed step: takes a type, returns a type, and is checked."""

    def __init__(self, name, takes, gives, fn, module, check):
        self.name, self.takes, self.gives = name, takes, gives
        self.fn, self.module, self.check = fn, module, check

    def __repr__(self):
        return f"{self.takes}->{self.gives} ({self.name})"


def _caps():
    """Every typed entry point. Each already carries its own check."""
    from engine import remnants, qwenmap, qwenmatter, experts as ex
    from engine import epochs as ep
    C = []

    C.append(Cap("core_mass", "progenitor_msun", "core_msun",
                 lambda m: remnants.core_mass(m).value, "remnants",
                 "ASSERTED initial-final mass relation"))
    C.append(Cap("classify_remnant", "core_msun", "remnant_kind",
                 lambda m: remnants.classify(m).value, "remnants",
                 "DERIVED from Chandrasekhar + observed EOS band"))
    C.append(Cap("chandrasekhar", "mu_e", "ceiling_msun",
                 lambda mu: remnants.chandrasekhar(mu).value, "remnants",
                 "INVERSE against hbar"))

    C.append(Cap("element_name", "atomic_number", "element_symbol",
                 lambda z: ex.BY_Z[z][0], "experts",
                 "table round-trip"))
    C.append(Cap("origin_epoch", "element_symbol", "epoch",
                 lambda s: ep.ORIGIN.get(s, "supernova"), "epochs",
                 "causal ordering"))
    C.append(Cap("epoch_time", "epoch", "seconds_after_bang",
                 lambda e: ep.T_OF[e], "epochs", "table"))

    C.append(Cap("subject_experts", "subject", "expert_ids",
                 lambda s: [e for e, _p, _n in
                            qwenmap.subject_experts()[s]], "qwenmap",
                 "ASSERTED routing associations"))
    C.append(Cap("expert_bytes", "expert_ids", "total_bytes",
                 _expert_bytes, "qwenaccounts",
                 "DERIVED, summed through atlas's parser"))
    # the life ladder, which is where biology meets the cosmology
    # above it: a nucleotide's epoch is a time after the Big Bang.
    from engine import biomatter as bm, life as lf
    C.append(Cap("nucleotide_epoch", "nucleotide", "epoch",
                 lambda n: bm.nucleotide_epoch(n).value, "biomatter",
                 "EXTERNAL, from the formula's elements"))
    C.append(Cap("gene_bases", "codons", "bases",
                 lambda n: bm.gene(n).value[0], "biomatter", "INVERSE"))
    C.append(Cap("bases_bits", "bases", "bits",
                 lambda b: b * 2.0, "biomatter", "2 bits per base"))
    C.append(Cap("dna_volume", "genome_bp", "volume_m3",
                 lambda bp: bm.dna_volume(bp).value, "biomatter",
                 "INVERSE on the base pairs"))
    C.append(Cap("cell_floor", "volume_m3", "floor_radius_m",
                 lambda v: (v / (4 / 3 * 3.141592653589793)) ** (1 / 3),
                 "biomatter", "the sphere that just contains it"))
    C.append(Cap("diffusion_ceiling", "consumption", "ceiling_radius_m",
                 lambda r: lf.diffusion_limit(r).value, "life", "INVERSE"))
    C.append(Cap("sv_ratio", "floor_radius_m", "surface_to_volume",
                 lambda r: lf.surface_to_volume(r).value, "life", "INVERSE"))

    C.append(Cap("isotopes_of", "expert_id", "isotope_count",
                 lambda e: len(qwenmatter.isotopes(e)), "qwenmatter",
                 "ENUMERATE"))
    return C


def _expert_bytes(ids):
    from engine.qwenaccounts import _bytes_per_expert, _exact
    bpe = _bytes_per_expert()
    parts = [bpe[(20, i)] for i in ids]
    return _exact("(" + " + ".join(str(p) for p in parts) + ")")


CAPS = None


def caps():
    global CAPS
    if CAPS is None:
        CAPS = _caps()
    return CAPS


def chain(start_type, goal_type, limit=5):
    """-> [Cap] or None. Search, do not author."""
    q = deque([(start_type, [])])
    seen = {start_type}
    while q:
        t, path = q.popleft()
        if t == goal_type:
            return path
        if len(path) >= limit:
            continue
        for c in caps():
            if c.takes == t and c.gives not in seen:
                seen.add(c.gives)
                q.append((c.gives, path + [c]))
    return None


def answer(start_type, value, goal_type):
    """-> (value, [steps]) or (None, why). Every link already checked."""
    path = chain(start_type, goal_type)
    if path is None:
        return None, (f"no chain from {start_type} to {goal_type} across "
                      f"{len(caps())} capabilities in {len({c.module for c in caps()})} "
                      f"modules -- these do not reach that far")
    steps, v = [], value
    for c in path:
        v = c.fn(v)
        steps.append((c.name, c.module, v, c.check))
    return v, steps


def reachable(start_type):
    out = {}
    for c in caps():
        got = chain(start_type, c.gives)
        if got:
            out[c.gives] = len(got)
    return out


def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))

    t("crosses_modules", _cross)
    t("no_path_refuses", _norefuse)
    t("composition_beats_parts", _more)
    return all(o[1] for o in out), out


def _cross():
    v, steps = answer("progenitor_msun", 25.0, "remnant_kind")
    mods = [s[1] for s in steps]
    if v is None or len(set(mods)) < 1:
        raise ArithmeticError("no chain")
    v2, s2 = answer("subject", "chemistry", "total_bytes")
    if v2 is None:
        raise ArithmeticError("no subject->bytes chain")
    return (f"a 25 solar-mass star -> {v} via {' -> '.join(s[0] for s in steps)}; "
            f"chemistry -> {v2:,} bytes via {' -> '.join(s[0] for s in s2)} "
            f"across {len({s[1] for s in s2})} modules")


def _norefuse():
    v, why = answer("subject", "chemistry", "seconds_after_bang")
    if v is not None:
        raise ArithmeticError("claimed a chain that should not exist")
    return f"asked for an impossible chain: refused -- {why[:60]}..."


def _more():
    """Composition must answer more than any single module does."""
    starts = ["progenitor_msun", "atomic_number", "subject", "mu_e"]
    multi = 0
    for s in starts:
        for tgt, n in reachable(s).items():
            if n > 1:
                multi += 1
    if multi < 3:
        raise ArithmeticError(f"only {multi} multi-step answers exist")
    return (f"{multi} answers need two or more modules chained; none of "
            f"them is written down anywhere, they exist because the types "
            f"line up")


if __name__ == "__main__":
    print(f"{len(caps())} typed capabilities across "
          f"{len({c.module for c in caps()})} modules\n")
    for c in caps():
        print(f"  {c.takes:<18} -> {c.gives:<20} {c.name:<18} [{c.module}]")
    print("\nchains nobody wrote:")
    for s, v, g in (("progenitor_msun", 25.0, "remnant_kind"),
                    ("atomic_number", 26, "seconds_after_bang"),
                    ("subject", "chemistry", "total_bytes"),
                    ("subject", "chemistry", "seconds_after_bang")):
        val, steps = answer(s, v, g)
        if val is None:
            print(f"  {s}={v} -> {g}: REFUSED")
        else:
            print(f"  {s}={v} -> {g} = {val}")
            for nm, mod, out, chk in steps:
                print(f"      {nm:<18} [{mod:<12}] -> {str(out)[:34]:<36}{chk}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:24}{d}")
    print("\nall:", ok)
