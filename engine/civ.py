"""
Play god once, then look at the bill.

Everything else here was derived or refused. This does the
opposite deliberately: it HANDS the animals language and a rule
for living together, takes no credit for either, and then asks
what the arithmetic says about the gift. Give the answer, see
what it needed, work backwards. The tool took that route in
reverse and it worked.

So two things are GIVEN, marked GIVEN everywhere they appear, and
excluded from anything this file claims to derive:

    a channel between brains at 39 bit/s
    a rule that adults pool what they bring in

And then the numbers, which were not given.

LANGUAGE IS ALMOST NOTHING AS A PIPE. Vision delivers 1e7 bit/s
and speech 39 -- a quarter of a million times narrower.
Everything anyone says to you across seventy years comes to 5.7e10
bits, which is 0.0122% of what a brain holds. If language carried
civilisation by volume it would be the worst tool ever adopted.

WHAT IT CARRIES IS THE FILTER OUTPUT. engine/learning.py found
that a brain saturates at 1.49 years and spends the rest
discarding, so the expensive thing a brain owns is not its
contents but its SELECTION. Speech is the only channel that moves
a selection from one head to another without the second head
paying to derive it. 0.0122% is enough because it is the 0.0122%
somebody already chose.

AND CONNECTION DID NOT HAVE TO BE GIVEN. It was already implied
and nobody had looked. engine/ontogeny.py priced a child at 16.4 W
continuous for eighteen years, and the child's own body at 34 more.
That is 51 W of a forager's 97 -- 52% of one adult, leaving 46 W
and no margin at all for a bad season. Two adults leave 143. The
pull toward company is not a preference added on top of the
physics. It is the physics, and it was sitting in a module written
four versions ago.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from engine.constants import YEAR_S          # one home for a year

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# GIVEN. Not derived, not measured into existence by these rules --
# handed over, and every result that leans on them says so.
GIVEN = {
    "a channel between brains": "speech, at a measured 39 bit/s",
    "adults pool what they bring in": "a rule of living together",
}

SPEECH_BITS_S = 39.0        # MEASURED across 17 languages
WAKING_HOURS = 16.0
FORAGER_W = 97.0
LIFETIME_YR = 70.0


def channel_ratio():
    """How much narrower speech is than sight. DERIVED."""
    from engine.learning import intake_bits_s
    return intake_bits_s() / SPEECH_BITS_S


def lifetime_speech_bits(years=LIFETIME_YR):
    """Every word anyone ever says to you. DERIVED."""
    return SPEECH_BITS_S * WAKING_HOURS * 3600.0 * 365.25 * years


def speech_as_fraction_of_a_brain(years=LIFETIME_YR):
    """DERIVED. The number that says volume is not the point."""
    from engine.learning import store_bits
    return lifetime_speech_bits(years) / store_bits()


def child_load_w():
    """-> (extra W, own W, total W). DERIVED via engine/ontogeny.py."""
    from engine.ontogeny import provisioning_debt, ONTOGENY
    from engine.biome import metabolism_w
    j, _ = provisioning_debt()
    extra = j / (18.0 * YEAR_S)
    own = sum(metabolism_w(m) for _a, m, _b in ONTOGENY) / len(ONTOGENY)
    return extra, own, extra + own


def spare_w(adults, children=1):
    """W left over after the children are paid for. DERIVED."""
    return adults * FORAGER_W - children * child_load_w()[2]


def alone_is_viable(children=1, margin=0.5):
    """-> (bool, why). Can one adult absorb a bad season? DERIVED."""
    s = spare_w(1, children)
    need = FORAGER_W * margin
    return s > need, (
        f"one adult keeps {s:.0f} W spare against {need:.0f} W of "
        f"slack needed to survive a bad season")


def smallest_group(children=1, margin=0.5):
    """How many adults it takes. DERIVED, not a chosen band size."""
    n = 1
    while spare_w(n, children) <= FORAGER_W * margin and n < 50:
        n += 1
    return n


def teaching_payback(hours_taught, hours_to_rederive):
    """-> (bool, ratio). Is it cheaper to be told? DERIVED."""
    if hours_taught <= 0:
        return True, math.inf
    return hours_to_rederive > hours_taught, hours_to_rederive / hours_taught


def wants():
    """-> [(want, kind, why)]. Which appetites are derivable.

    The question was whether wants can be ADDED once language is
    given. Some can be derived instead, and saying which is which
    is the whole value of asking.
    """
    from engine.earthlab import error_threshold, ERROR_RATES
    out = []

    ok, why = alone_is_viable()
    out.append(("connection", "DERIVED" if not ok else "NOT DERIVED",
                f"{why}, so a lone adult cannot carry one child "
                f"through a bad year and {smallest_group()} adults can"))

    mu = min(ERROR_RATES.values())
    keep = error_threshold(mu)
    kv = float(getattr(keep, "value", keep))
    out.append(("sex", "PARTLY DERIVED",
                f"an error rate of {mu:.1e} caps a maintainable genome "
                f"at {kv:,.0f} bases, and a human genome is 3e9 -- six "
                f"orders past it. Something repairs, and recombination "
                f"is a candidate this file cannot single out. The NEED "
                f"is derived; the mechanism is not"))

    out.append(("food", "DERIVED",
                "a body that stops eating stops making 82 W, which "
                "engine/ontogeny.py already required continuously"))
    out.append(("shelter", "DERIVED",
                "engine/shelter.py: below 19 C worn insulation runs "
                "out and the deficit is not optional"))
    out.append(("status", "GIVEN OR ABSENT",
                "nothing here prices rank. No rule makes one adult's "
                "share depend on another's regard, so if status is "
                "real it is missing, not derived"))
    return out


def check():
    out = []

    def t(nm, fn):
        try:
            out.append((nm, True, str(fn())))
        except Exception as e:
            out.append((nm, False, f"{type(e).__name__}: {e}"))

    t("language_is_almost_nothing_as_a_pipe", _pipe)
    t("what_it_carries_is_the_selection", _select)
    t("connection_did_not_have_to_be_given", _conn)
    t("the_group_size_is_derived_not_chosen", _group)
    t("what_was_given_is_marked_as_given", _given)
    t("some_wants_derive_and_some_do_not", _wants)
    return all(o[1] for o in out), out


def _pipe():
    r, f = channel_ratio(), speech_as_fraction_of_a_brain()
    if r < 1e4:
        raise ArithmeticError(f"speech is only {r:.0f}x narrower")
    return (f"vision delivers 1e7 bit/s and speech {SPEECH_BITS_S:.0f} "
            f"-- {r:,.0f} times narrower. Everything anyone says to "
            f"you in seventy years is {lifetime_speech_bits():.2e} "
            f"bits, {100*f:.4f}% of what a brain holds. If language "
            f"carried civilisation by VOLUME it would be the worst "
            f"tool ever adopted")


def _select():
    f = speech_as_fraction_of_a_brain()
    from engine.learning import fill_time_years
    return (f"a brain saturates at {fill_time_years():.2f} years and "
            f"spends the rest discarding, so what it owns that is "
            f"expensive is its SELECTION, not its contents. Speech is "
            f"the only channel that moves a selection between heads "
            f"without the second head paying to derive it. "
            f"{100*f:.4f}% is enough because it is the {100*f:.4f}% "
            f"somebody already chose")


def _conn():
    extra, own, tot = child_load_w()
    ok, why = alone_is_viable()
    if ok:
        raise ArithmeticError("a lone adult has margin after all")
    return (f"a child costs {extra:.1f} W of provisioning plus "
            f"{own:.0f} W of its own body, {tot:.0f} W of a forager's "
            f"{FORAGER_W:.0f}. {why}. CONNECTION DID NOT HAVE TO BE "
            f"GIVEN -- it was already implied by a module written four "
            f"versions ago and nobody had looked. It is not a "
            f"preference on top of the physics, it is the physics")


def _group():
    n = smallest_group()
    if not 2 <= n <= 6:
        raise ArithmeticError(f"the group came out at {n} adults")
    return (f"{n} adults is the smallest that carries one child with "
            f"slack for a bad season: {spare_w(1):.0f} W spare alone "
            f"against {spare_w(n):.0f} W at {n}. Nobody picked a band "
            f"size -- it is where the surplus crosses the margin")


def _given():
    if len(GIVEN) != 2:
        raise ArithmeticError(f"{len(GIVEN)} things are marked given")
    w = wants()
    if any(k == "connection" and v == "GIVEN" for k, v, _ in w):
        raise ArithmeticError("connection was counted as given")
    return (f"two things were handed over and both are named: "
            + "; ".join(GIVEN) + f". Everything else in this file is "
            f"derived or refused, and the point of playing god once "
            f"is that the bill afterwards is legible -- connection "
            f"came back DERIVED, which means the gift was not needed "
            f"for it")


def _wants():
    w = wants()
    der = [x for x in w if x[1] == "DERIVED"]
    not_der = [x for x in w if "GIVEN OR ABSENT" in x[1]]
    if not der or not not_der:
        raise ArithmeticError(f"{len(der)} derived, {len(not_der)} not")
    return (f"of {len(w)} appetites, {len(der)} derive from rules "
            f"already here -- {', '.join(x[0] for x in der)} -- one is "
            f"partly derived, and {len(not_der)} does not: "
            f"{not_der[0][0]}, because nothing prices rank. No rule "
            f"makes one adult's share depend on another's regard, so "
            f"if status is real it is MISSING and not derived, and "
            f"that is a different sentence from 'people want status'")


if __name__ == "__main__":
    print(f"  GIVEN:")
    for k, v in GIVEN.items():
        print(f"    {k} -- {v}")
    print(f"\n  vision 1e7 bit/s vs speech {SPEECH_BITS_S:.0f} = "
          f"{channel_ratio():,.0f}x narrower")
    print(f"  a lifetime of speech is "
          f"{100*speech_as_fraction_of_a_brain():.4f}% of a brain\n")
    extra, own, tot = child_load_w()
    print(f"  one child: {extra:.1f} W provisioning + {own:.0f} W body "
          f"= {tot:.0f} W")
    for n in (1, 2, 3, 4):
        print(f"    {n} adult{'s' if n > 1 else ' '}: "
              f"{spare_w(n):>6.0f} W spare")
    print(f"  smallest viable group: {smallest_group()} adults\n")
    for k, kind, why in wants():
        print(f"  {k:<12}{kind:<18}{why[:60]}")
    print()
    ok, res = check()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:42}{d[:38]}")
