"""A name is a mechanism, not an imposition from outside.

engine/standing.py ranked contributions with no names in it,
which was right as far as it went and slightly missed the point.
Naming is not something we do to the simulation from our side. It
is something the people inside do, for reasons that are derivable
from rules already here, and it belongs in the system.

Three things a name is:

  AN INDEX. engine/tradition.py holds a corpus of about 8,700
  items. Without a handle, finding one is a search. With a
  handle, it is a lookup. That is the whole of why anything gets
  named, and it is worth thousands of comparisons per retrieval.

  A CREDIT CLAIM. engine/merit.py prices a specialist at 1/k,
  where k is how many hold the skill. Attaching a name to a
  contribution is the act that sets k to one for that
  contribution. Naming is not decoration on top of the reward
  system, it IS the reward system's addressing.

  A THING THAT MUST SURVIVE TRANSMISSION. A name is an item in
  the corpus like any other, so it is subject to the same
  consensus arithmetic, and a name held by too few people is lost
  exactly as a craft is.

And one thing a name is NOT, which this module set out to show
and failed to: an artefact of what is easy to tell. That
hypothesis is recorded below with the number that killed it.
"""

import math

from engine.artifact import PRIMITIVES
from engine.inference import closure
from engine.tradition import oral_capacity, garbles, BAND
from engine.merit import pivotal
from engine.standing import leverage, REMEMBERED


def search_cost():
    """Comparisons to find an unnamed item. DERIVED."""
    return oral_capacity() / 2.0


def index_cost():
    """Comparisons to find a named one. DERIVED."""
    return 1.0


def naming_is_worth():
    """Retrievals saved by having a handle. DERIVED."""
    return search_cost() / index_cost()


def credit_of(holders):
    """What a name is worth to the one who carries it. DERIVED."""
    return pivotal(holders)


def name_survives(holders, generations=40):
    """A name is an item and decays like one. DERIVED."""
    return (1.0 - garbles(holders)) ** generations >= 0.5


def least_holders(generations=40):
    """Fewest people who must carry a name to keep it. DERIVED."""
    for k in range(1, BAND * 8):
        if name_survives(k, generations):
            return k
    return None


# --- the hypothesis that failed -------------------------------------
#
# The guess was that high-leverage contributions are harder to
# explain, so they travel badly as stories and do not collect
# names, while a fact with a person and a place fits in one
# telling. It is a tidy account of why toolmakers are less often
# remembered than answerers. It is also not true here.

def tellings_to_explain(primitive):
    """A telling carries one item, so k prerequisites is k+1."""
    return len(closure(primitive)) + 1


def leverage_vs_tellability():
    """-> (r, n). Pearson between the two. DERIVED."""
    rows = [(leverage(p), tellings_to_explain(p)) for p in PRIMITIVES]
    n = len(rows)
    xs = [a for a, _b in rows]
    ys = [b for _a, b in rows]
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return (cov / (sx * sy) if sx and sy else 0.0), n


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_name_is_an_index_and_that_is_what_it_is_for", _index)
    t("a_name_is_how_credit_is_addressed", _credit)
    t("a_name_decays_like_any_other_item", _decay)
    t("REFUTED_the_tellability_account_of_who_gets_named", _failed)
    return all(x for _, x, _ in res), res


def _index():
    w = naming_is_worth()
    if w < 100:
        raise ArithmeticError(f"{w}")
    return (f"engine/tradition.py holds about {oral_capacity():.0f} "
            f"items. Finding one without a handle is a search, "
            f"averaging {search_cost():.0f} comparisons; with a "
            f"handle it is a lookup. A name is worth {w:.0f} "
            f"retrievals, and that is the whole of why anything "
            f"gets one -- names are not honours, they are "
            f"addresses. It also explains why the earliest ones "
            f"attach to places and rivers rather than people: you "
            f"look those up more often")


def _credit():
    alone, common = credit_of(1), credit_of(BAND)
    if alone <= common:
        raise ArithmeticError(f"{alone} {common}")
    return (f"engine/merit.py prices a contribution at 1/k, where "
            f"k is how many hold it. Attaching a name is the act "
            f"that sets k to one: {100*alone:.0f}% against "
            f"{100*common:.0f}% for something everybody is held to "
            f"have done. So naming is not decoration on top of the "
            f"reward system, it is the reward system's ADDRESSING, "
            f"and a dispute over who gets named is a dispute about "
            f"1/k with the arithmetic already settled")


def _decay():
    need = least_holders()
    if need is None or need < 2:
        raise ArithmeticError(f"{need}")
    return (f"a name is an item in the corpus and decays like one. "
            f"It takes {need} holders to keep one for forty "
            f"generations, the same figure engine/literacy.py got "
            f"for keeping a script -- because it is the same "
            f"arithmetic, not a coincidence. A name held by one "
            f"person dies with them, which means the record of who "
            f"did what is subject to the same consensus correction "
            f"as everything else, and is wrong in the same way and "
            f"for the same reasons")


def _failed():
    """REFUTED. A hypothesis this module was built to show, and did not.

    Kept because a refuted guess with its number attached is
    worth more than no guess, and considerably more than the
    tidy story it would have justified.
    """
    r, n = leverage_vs_tellability()
    built = sum(1 for _x, (k, _w) in REMEMBERED.items() if k == "built")
    if abs(r) > 0.6:
        raise ArithmeticError(
            f"r = {r:+.2f}: the correlation is now strong enough "
            f"that the tellability account should be reinstated "
            f"rather than left refuted")
    top = max(PRIMITIVES, key=leverage)
    return (f"the guess was that high-leverage contributions are "
            f"harder to explain -- a telling carries one item, so "
            f"something with k prerequisites needs k+1 tellings to "
            f"travel -- and that this is why toolmakers are "
            f"remembered less than answerers. It is tidy and it is "
            f"not true here: across n={n} primitives the "
            f"correlation between leverage and tellings-to-explain "
            f"is r = {r:+.2f}, which is nothing, and the sign is "
            f"the wrong way besides. {top} tops the ranking at "
            f"{leverage(top)} and needs {tellings_to_explain(top)} "
            f"tellings, while lever sits at {leverage('lever')} on "
            f"{tellings_to_explain('lever')}. So the naming bias "
            f"in engine/standing.py -- {len(REMEMBERED)-built} "
            f"answerers to {built} builders -- is NOT explained by "
            f"anything derivable here, and the evidence for the "
            f"bias was eight names I chose. Two unsupported "
            f"things, and neither gets to prop up the other")


if __name__ == "__main__":
    print(f"  a name saves {naming_is_worth():.0f} retrievals")
    print(f"  a name needs {least_holders()} holders to last 40 "
          f"generations")
    print(f"  a name takes credit from {100*credit_of(BAND):.0f}% "
          f"to {100*credit_of(1):.0f}%\n")
    r, n = leverage_vs_tellability()
    print(f"  {'primitive':<14}{'leverage':>9}{'tellings':>10}")
    for p in sorted(PRIMITIVES, key=leverage, reverse=True)[:6]:
        print(f"  {p:<14}{leverage(p):>9}{tellings_to_explain(p):>10}")
    print(f"\n  leverage vs tellability: r = {r:+.3f} over n={n} "
          f"-- REFUTED\n")
    ok, res = check()
    for nm, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {nm}\n        {m}")
    print("  all hold" if ok else "  broken")
