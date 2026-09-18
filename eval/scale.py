"""How big this gets if you write it all out, and how big it is.

The two numbers are very far apart and the distance between them
is the argument.

An earlier version of this repository had "26 of 28" typed into
the README by hand while the code said 21. That is on the record
as a failure, so nothing here is typed anywhere: tools/readme.py
writes the block in the README from this module, between markers,
and the numbers are a registered claim like any other.

WHERE THE COUNT STOPS. It stops where a route stops being a
route. Artifacts times passing universes is already 6.3e11
distinct things to say. Letting engine/occurrence.py's 8.13e34
compartments count, or 2^13 situations per organism per universe,
takes it past every token ever written by anyone, which is a
joke rather than a measurement. The cap is a CHOICE and it is
declared here rather than buried.
"""

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HISTORY_TOKENS = 26400      # Parts II-IV of the dossier, one history
NAME_TOKENS = 30            # to name an artifact and place it
PROSE_CHARS_PER_TOKEN = 4.2
CODE_CHARS_PER_TOKEN = 3.0


def engine_chars():
    """Source bytes of the rules themselves. MEASURED."""
    return sum(p.stat().st_size for p in (ROOT / "engine").glob("*.py"))


def engine_tokens():
    """ESTIMATE: no tokenizer is installed, so chars/3 for code."""
    return engine_chars() / CODE_CHARS_PER_TOKEN


def universes():
    """-> (generated, passing). DERIVED from eval/claims."""
    from eval.claims import _generated
    _ok, gen, passing = _generated()
    return gen, passing


def artifacts():
    """Distinct buildable things at the fixed point. DERIVED."""
    from engine.intricacy import settle_network, designs
    return designs(settle_network())


def layers():
    """-> [(label, count, tokens each, tokens)]. DERIVED."""
    gen, passing = universes()
    a = artifacts()
    return [
        ("one history, as written", 1, HISTORY_TOKENS),
        ("universes that pass the filters", passing, HISTORY_TOKENS),
        ("all universes generated blind", gen, HISTORY_TOKENS),
        ("artifacts at the fixed point", a, NAME_TOKENS),
        ("artifacts x passing universes", a * passing, NAME_TOKENS),
    ]


def enumerated_tokens():
    """The whole thing written out, at the declared cap. DERIVED."""
    return max(n * per for _lab, n, per in layers())


def compression():
    """How many tokens of output per token of rule. DERIVED."""
    return enumerated_tokens() / engine_tokens()


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("written_out_it_is_the_size_of_a_pretraining_corpus", _big)
    t("the_rules_that_generate_it_fit_in_a_couple_of_megabytes", _small)
    t("INVERTED_the_cap_on_counting_is_declared_not_natural", _cap)
    return all(x for _, x, _ in res), res


def _big():
    tot = enumerated_tokens()
    gen, passing = universes()
    if tot < 1e12:
        raise ArithmeticError(f"{tot}")
    return (f"one rendered history is {HISTORY_TOKENS:,} tokens. "
            f"{passing:,} universes pass the filters out of "
            f"{gen:,} generated, and the fixed point admits "
            f"{artifacts():.3g} distinct artifacts -- so writing "
            f"out every route and variant is about {tot:.2e} "
            f"tokens, {tot/1e12:.0f} trillion. That is the scale of "
            f"a frontier pretraining corpus: one Atlas, fully "
            f"enumerated, is roughly one read of the internet")


def _small():
    c, tk, r = engine_chars(), engine_tokens(), compression()
    if r < 1e6:
        raise ArithmeticError(f"{r}")
    return (f"the rules are {c/1e6:.1f} MB -- about {tk/1e3:.0f}k "
            f"tokens of source -- and every one of those "
            f"{enumerated_tokens():.2e} tokens is derivable from "
            f"them. {r:.3g} to one. That is the argument against "
            f"training anything on the enumeration: a model trained "
            f"on all of it would have memorised a fraction of one "
            f"pass through a space it could have COMPUTED from "
            f"{c/1e6:.1f} MB. The rules are the compressed form and "
            f"the enumeration is what you unpack for the single "
            f"route somebody asked about")


def _cap():
    """INVERTED. Fails if the cap ever looks like a fact."""
    from engine.comprehension import binding
    a, (_gen, passing) = artifacts(), universes()
    capped = a * passing
    further = capped * 2 ** len(binding("human"))
    if further <= capped:
        raise ArithmeticError("nothing lies past the cap")
    return (f"{capped:.3g} routes is where this stops counting and "
            f"the stop is a CHOICE. One more honest multiplication "
            f"-- 2^{len(binding('human'))} situations a human "
            f"parses, per organism, per universe -- gives "
            f"{further:.3g}, and engine/occurrence.py's 8.13e34 "
            f"compartments would take it past every token ever "
            f"written by anyone. Past a point this is not a "
            f"measurement, it is a joke about exponents, and the "
            f"cap is declared here rather than buried so that "
            f"nobody quotes the headline without it")


def block():
    """The README section, generated. Never typed."""
    gen, passing = universes()
    tot, r = enumerated_tokens(), compression()
    rows = "\n".join(
        f"    {lab:<34}{n:>12.4g}{per:>9}{n*per:>13.3g}"
        for lab, n, per in layers())
    return f"""## The two numbers

Written out in full -- every route, every variant, every universe
that passes -- Atlas is about **{tot/1e12:.0f} trillion tokens**.

```
    layer                                count  tok ea       tokens
{rows}
```

The rules that generate all of it are **{engine_chars()/1e6:.1f} MB**.

**That is about {r/1e6:.0f} million to one.**

Which is the whole argument in one figure. The enumeration is not
the artifact; it is what you unpack on demand for the one route
somebody asked about. `engine/roots.py` already works this way --
routes share prefixes, so the store holds the sharing and not the
list -- and anything else attached to this system belongs on the
same side of that line.

The cap is a choice and it is declared: counting stops at
artifacts times passing universes. Allowing 2^13 situations per
organism per universe, or `engine/occurrence.py`'s 8.13e34
compartments, takes it past every token ever written by anyone,
which is a joke about exponents rather than a measurement. Token
figures are estimates -- no tokenizer ships with this repo -- and
are computed by `eval/scale.py`, not typed here.
"""


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
