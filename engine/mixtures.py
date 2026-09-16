"""
Mixtures, biogenic composition, and a correction.

I claimed the ladder stops at compounds -- that dirt and ore "are not
compositional objects and no set of rules will make them one". That was
wrong. A mixture is compositional under a DIFFERENT rule:

    compound   fixed integer ratio      H2O          exact, a formula
    mixture    real-valued fractions    dirt         sum(f) = 1, plus a seed

sum of fractions = 1 is a conservation law exactly like charge balance, and
it is just as checkable. What a mixture lacks is not composition, it is a
CANONICAL composition -- two handfuls of dirt differ. So the representation
carries a SEED: same seed, same mixture, reproducible and verifiable. The
seed is the watermark. That is the same device the virtual planets already
use, applied one level down.

BIOGENIC ELEMENTS. Two different questions have two different answers and
conflating them is the classic error:

    most abundant by MASS   oxygen  (~65% of a human)
    most abundant by COUNT  hydrogen (~62% of the atoms)

Both are true. Which one is wanted depends on the question, so both are
stored and the query has to say which.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

# human body, fraction by MASS -- empirical, a measurement not a derivation
BODY_BY_MASS = {"O": 0.650, "C": 0.185, "H": 0.095, "N": 0.032, "Ca": 0.015,
                "P": 0.010, "K": 0.004, "S": 0.003, "Na": 0.002, "Cl": 0.002,
                "Mg": 0.001, "Fe": 0.00006}
# same body, fraction by ATOM COUNT -- a different quantity, not a restatement
BODY_BY_COUNT = {"H": 0.620, "O": 0.240, "C": 0.120, "N": 0.011, "Ca": 0.0022,
                 "P": 0.0022, "S": 0.0004, "Na": 0.0004, "K": 0.0003,
                 "Cl": 0.0003, "Mg": 0.00007}

CHNOPS = ("C", "H", "N", "O", "P", "S")
DNA_ELEMENTS = ("C", "H", "N", "O", "P")      # phosphate backbone supplies P
SOURCE = "standard reference body composition; empirical"


def most_abundant(basis="mass"):
    d = BODY_BY_MASS if basis == "mass" else BODY_BY_COUNT
    sym = max(d, key=d.get)
    return sym, d[sym], basis


@dataclass
class Mixture:
    name: str
    seed: str
    fractions: dict            # symbol or compound -> fraction by mass
    kind: str = "mixture"
    note: str = ""

    def normalised(self, tol=1e-9):
        return abs(sum(self.fractions.values()) - 1.0) <= tol

    def watermark(self):
        """reproducible identity: same seed and same composition, same mark"""
        body = "|".join(f"{k}:{self.fractions[k]:.6f}"
                        for k in sorted(self.fractions))
        return hashlib.sha256(f"{self.seed}|{body}".encode()).hexdigest()[:16]

    def check(self):
        out = [("fractions sum to 1", self.normalised(),
                f"sum={sum(self.fractions.values()):.6f}"),
               ("no negative fraction",
                all(v >= 0 for v in self.fractions.values()), ""),
               ("watermark reproducible",
                self.watermark() == Mixture(self.name, self.seed,
                                            dict(self.fractions)).watermark(), "")]
        return all(o[1] for o in out), out


def seeded_mixture(name, seed, components, rng_span=0.4):
    """a mixture whose exact proportions come from the seed, then normalised.

    Two handfuls of dirt are not identical, so a mixture without a seed has
    no identity. With one it has exactly one, and it is reproducible.

    REPRODUCIBLE IS NOT REALISTIC. The proportions here are near-uniform
    from the hash, so `seeded_mixture("star", ...)` returns something like
    24% oxygen -- a real star is ~74% hydrogen and ~24% helium. The seed
    guarantees the same mixture every time; it guarantees nothing about
    whether that mixture occurs in nature. Realistic proportions are
    empirical and belong in `observed()` below, with a citation.
    """
    raw = {}
    for c in components:
        h = hashlib.sha256(f"{seed}|{c}".encode()).digest()
        raw[c] = 1.0 + (int.from_bytes(h[:4], "big") / 2**32) * rng_span
    tot = sum(raw.values())
    return Mixture(name, seed, {c: v / tot for c, v in raw.items()})


# Measured compositions, kept separate from generated ones. A generated
# mixture is reproducible; an observed one is sourced. Mixing the two would
# let a hash masquerade as an observation.
OBSERVED = {
    # the listed elements sum to 0.9972 -- the remainder is explicit rather
    # than rounded away. The sum-to-one check caught this; loosening the
    # tolerance would have hidden a truncated table instead of naming it.
    "sun": ({"H": 0.7346, "He": 0.2483, "O": 0.0077, "C": 0.0029,
             "Fe": 0.0016, "Ne": 0.0012, "N": 0.0009, "other": 0.0028},
            "solar photospheric abundance by mass, Asplund et al.; "
            "'other' is the unlisted remainder"),
    "earth-crust": ({"O": 0.461, "Si": 0.282, "Al": 0.082, "Fe": 0.056,
                     "Ca": 0.042, "Na": 0.024, "Mg": 0.023, "K": 0.021,
                     "Ti": 0.0057, "other": 0.0033},
                    "continental crust by mass, standard reference"),
}


def observed(name):
    """-> (Mixture, citation) or (None, reason). Never generated."""
    if name not in OBSERVED:
        return None, (f"no measured composition on record for {name!r}; "
                      f"have {sorted(OBSERVED)}")
    fr, cite = OBSERVED[name]
    return Mixture(name, seed="observed", fractions=dict(fr),
                   kind="observed", note=cite), cite
