"""What a machine that answers by searching would cost, and what
its existence would say about this repository.

engine/artifact.py has `inference` as a primitive: statistics run
at a scale no head holds. It is a name with prerequisites and a
tolerance, and nothing runs there. This prices it against rules
that already exist, and the prices are not where anyone expects.

The thermodynamic floor is nowhere near binding -- ten orders
below the thing that actually costs. The interesting cost is the
KIT, because at a billionth of a metre the toolkit is the whole
prior tree, and engine/capital.py already showed what happens to
a specialty whose kit is dear: very few hold it, and
engine/merit.py prices scarcity at 1/k.

And then the part that is about this repo rather than about a
machine. README rule 3 says: if a check runs a search, the rule
underneath it has not been found yet. A machine that answers by
searching a corpus is that rule, industrialised. Its usefulness
is not a measure of how good it is. It is a measure of how much
has not been derived.
"""

import math

from engine.learning import landauer_j, store_bits, BODY_TEMP_K
from engine.intricacy import written_corpus, settle_network, VILLAGE
from engine.literacy import spread
from engine.trade import unit_cost
from engine.capital import DAYS_PER_PART, EAT_DAYS_YEAR
from engine.merit import pivotal
from engine.novelty import team_size, multiple, SPECIALTIES_PER_HEAD
from engine.artifact import PRIMITIVES, TOL_NEEDED

from engine.civ import SPEECH_BITS_S  # one home, MEASURED
from engine.tradition import TELL_SECONDS  # one home
SWITCH_J = 1e-15            # MEASURED-ish, a modern gate operation
PASSES = 1e6                # CHOSEN, touches per stored bit

# engine/capital.py prices a kit at DAYS_PER_PART a part and that
# constant was set for a village, where everything is made to
# about a tenth. It cannot be carried to a billionth unchanged --
# holding a tolerance costs more than meeting it once, and the
# cost rises faster than the tolerance falls. On the first pass
# this module reported 3,739 holders of an inference kit, which
# is plainly wrong, and the reason was exactly this: a part is
# not a part.
PRECISION_EXPONENT = 0.5    # CHOSEN, cost as (base/tol)**this


def closure(name):
    """Every primitive `name` transitively rests on. DERIVED."""
    out, stack = set(), [name]
    while stack:
        cur = stack.pop()
        for n in PRIMITIVES[cur][0]:
            if n not in out:
                out.add(n)
                stack.append(n)
    return out


def bits_per_item():
    """What one telling is worth in bits. DERIVED."""
    return SPEECH_BITS_S * TELL_SECONDS


def corpus_bits(n=None):
    """Everything the corpus holds, in bits. DERIVED."""
    n = 40 * VILLAGE if n is None else n
    f = spread(1.0 / n, 2000.0)
    return written_corpus(f * n) * bits_per_item()


def floor_j(n=None):
    """Landauer: the least it could possibly cost. DERIVED."""
    return landauer_j(corpus_bits(n))


def actual_j(n=None, passes=PASSES):
    """What a real gate would spend touching it. DERIVED."""
    return corpus_bits(n) * SWITCH_J * passes


def headroom(n=None):
    """How far the real cost sits above the floor. DERIVED."""
    return actual_j(n) / floor_j(n)


def kit_parts():
    """Primitives that must exist before one can be built."""
    return len(closure("inference")) + 1


def precision_multiplier(tol):
    """What holding a tolerance costs over meeting a tenth."""
    from engine.artifact import BASE_TOL
    return (BASE_TOL / tol) ** PRECISION_EXPONENT


def kit_days(market, tol=None):
    """Labour-days in the toolkit. DERIVED, engine/capital prices."""
    t = TOL_NEEDED["inference"] if tol is None else tol
    return (kit_parts() * DAYS_PER_PART * precision_multiplier(t)
            * unit_cost(market))


def least_population(market=None):
    """Smallest population whose surplus affords one kit. DERIVED."""
    from engine.intricacy import spare_fraction, settle_network as sn
    share = spare_fraction(sn())
    m = 40 * VILLAGE if market is None else market
    return kit_days(m) / (EAT_DAYS_YEAR * share)


def holders(n, market=None):
    """How many can command such a kit. DERIVED.

    engine/capital: one kit per holder, paid from surplus. At a
    billionth of a metre the kit does not get cheaper with the
    market fast enough to outrun its own part count.
    """
    m = n if market is None else market
    from engine.intricacy import spare_fraction, settle_network as sn
    surplus = n * EAT_DAYS_YEAR * spare_fraction(sn())
    return surplus / kit_days(m)


def team_with_system(parts):
    """Team needed when one head plus a corpus covers many crafts."""
    return max(1.0, parts / max(parts, SPECIALTIES_PER_HEAD))


def novelty_gain():
    """What removing the team term would do. DERIVED."""
    n = 40 * VILLAGE
    return team_size(n) / team_with_system(team_size(n))


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_thermodynamic_floor_is_not_the_constraint", _floor)
    t("the_kit_is_the_cost_and_scarcity_is_the_consequence", _kit)
    t("it_attacks_the_one_term_the_record_says_is_wrong", _team)
    t("INVERTED_its_usefulness_measures_what_is_underived", _rule3)
    return all(x for _, x, _ in res), res


def _floor():
    b, fl, ac, hr = corpus_bits(), floor_j(), actual_j(), headroom()
    if hr < 1e6:
        raise ArithmeticError(f"headroom only {hr:.1e}")
    return (f"the corpus is {b:.2e} bits -- {written_corpus(spread(1/(40*VILLAGE), 2000.0)*40*VILLAGE):.2e} "
            f"items at {bits_per_item():.0f} bits a telling, speech "
            f"running {SPEECH_BITS_S:.0f} bit/s across every "
            f"language anyone has measured. Landauer at "
            f"{BODY_TEMP_K:.0f} K puts the floor for erasing it "
            f"once at {fl:.2e} J: less than a second of one human "
            f"at rest. A real gate at {SWITCH_J:.0e} J touching "
            f"each bit {PASSES:.0e} times spends {ac:.2e} J, which "
            f"is {hr:.1e}x the floor. The thermodynamic limit is "
            f"not the constraint and is not within ten orders of "
            f"being one -- the same shape as temperature, which "
            f"stopped mattering at round 5 and kept being quoted")


def _kit():
    mkt = 40 * VILLAGE
    parts, days = kit_parts(), kit_days(mkt)
    k, need = holders(mkt), least_population()
    village_k = holders(VILLAGE, mkt)
    if k >= 10.0 or village_k >= 1.0:
        raise ArithmeticError(f"network {k}, village {village_k}")
    return (f"inference rests transitively on {parts-1} other "
            f"primitives, so the kit is the near-whole tree. But a "
            f"part is not a part: engine/capital.py's "
            f"{DAYS_PER_PART:.0f} days was set for a village where "
            f"everything is made to a tenth, and holding "
            f"{TOL_NEEDED['inference']:.0e} costs "
            f"{precision_multiplier(TOL_NEEDED['inference']):,.0f}x "
            f"that. The kit is {days:,.0f} labour-days. A village "
            f"of {VILLAGE:.0f} affords {village_k:.4f} of one, so "
            f"the specialty cannot exist there at all -- which is "
            f"the derived answer to why it sits ten rounds out. It "
            f"takes {need:,.0f} people before ONE kit is "
            f"affordable, a city rather than a region, and a "
            f"network of {mkt:.0f} affords {k:.1f}. That is the "
            f"result: not that it is expensive but that it is "
            f"INDIVISIBLE and there is room for about two. "
            f"engine/merit.py prices a holder at 1/k, so each is "
            f"worth {100*pivotal(round(k)):.0f}% of what the thing "
            f"is worth to everybody -- the highest pivotality of "
            f"any specialty on this chain. The cost was never the "
            f"electricity, and the consequence is not cost, it is "
            f"that two parties hold it")


def _team():
    g = novelty_gain()
    n = 40 * VILLAGE
    per_now = multiple(VILLAGE, n)[0]
    if g <= 1.0:
        raise ArithmeticError(f"{g}")
    return (f"engine/novelty.py found that novelty per head falls "
            f"because a design of p parts needs p people who "
            f"between them hold p crafts -- the team is the whole "
            f"headwind. A corpus one head can consult collapses "
            f"exactly that term: team {team_size(n):.1f} -> 1, so "
            f"the model says novelty per head rises {g:.0f}x and "
            f"the {per_now:.2f} decline reverses. Take that "
            f"lightly. eval/history.py records this same term as "
            f"the repo's second-worst miss: the model's decline is "
            f"16x GENTLER than measured, so team size is already "
            f"known not to be what is really limiting. Removing a "
            f"term that was too weak cannot buy back a gap it "
            f"never explained. The prediction is large and the "
            f"rule under it is one of the two this repo knows to "
            f"be wrong")


def _rule3():
    """INVERTED. Fails if searching ever stops meaning something."""
    from engine.lineage import chain, MISSING, CROSSES
    c = chain()
    open_ = [1 for _a, _b, v, _r, _w in c if v in (MISSING, CROSSES)]
    if not open_:
        raise ArithmeticError(
            "the chain has no open links, so a machine that "
            "answered by searching would have nothing to be "
            "useful about, and this rule would be empty")
    return (f"README rule 3: if a check runs a search, the rule "
            f"underneath it has not been found yet. A machine that "
            f"answers by searching a corpus is that sentence "
            f"industrialised -- it is very good at the thing this "
            f"repository treats as an admission. So its usefulness "
            f"here is not a measure of how good it is; it is a "
            f"measure of how much has not been derived. The chain "
            f"has {len(c)} links and {len(open_)} still open, and "
            f"every one of the 550 rules that DID get found is a "
            f"question such a machine would no longer be needed "
            f"for. That is the honest account of what building one "
            f"would be worth to this system, and it is the only "
            f"claim here that gets smaller as the work gets better")


if __name__ == "__main__":
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
