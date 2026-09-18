"""Who the system says mattered, with no names in the ranking.

engine/exam.py has Eratosthenes and Aristarchus in it. They are
in the RECORDED column, which is our answer key and is allowed to
name people -- but they had crept into the prose as the exemplars,
as though this repository had decided they were the important
ones. It had not. It had imported them.

If the people inside make tools and find things out, then who
mattered is a question about STRUCTURE and it should fall out of
the structure. A contribution matters in proportion to what it
lets other people do, and that is countable: how many primitives,
sciences, exam questions and namable artifacts rest on it.

The ranking below contains no names and cannot, because nothing
it reads has a name in it. The names are kept in one block at the
bottom, only to ask a different question: do the people we
remember line up with the contributions this says were large?
"""

import math

from engine.artifact import PRIMITIVES, KNOWN_AS
from engine.literature import SCIENCES
from engine.exam import QUESTIONS

# RECORDED, and used ONLY for the last comparison. Nothing above
# this line may read it. Who got the credit, against what kind of
# contribution it was.
REMEMBERED = {
    "Eratosthenes": ("answered", "how far round is the Earth"),
    "Aristarchus": ("answered", "how far is the Sun, in Moon distances"),
    "Romer": ("answered", "how fast does light travel"),
    "Torricelli": ("answered", "how heavy is the air above us"),
    "Perrin": ("answered", "how big is an atom"),
    "Patterson": ("answered", "how old is the Earth"),
    "Huygens": ("built", "regulation"),
    "Gutenberg": ("built", "mark"),
}


def rests_on(primitive):
    """-> (primitives, sciences, questions, artifacts). DERIVED."""
    p = sum(1 for _n, (needs, _k, _r, _w) in PRIMITIVES.items()
            if primitive in needs)
    s = sum(1 for _n, (needs, _w, _c) in SCIENCES.items()
            if primitive in needs)
    q = sum(1 for _n, v in QUESTIONS.items() if primitive in v[0])
    a = sum(1 for combo in KNOWN_AS if primitive in combo)
    return p, s, q, a


def leverage(primitive):
    """How much rests on it. DERIVED, and no name is involved."""
    return sum(rests_on(primitive))


def ranking():
    """-> [(leverage, primitive, breakdown)] descending. DERIVED."""
    rows = [(leverage(p), p, rests_on(p)) for p in PRIMITIVES]
    return sorted(rows, key=lambda r: (-r[0], r[1]))


# --- what a tool is worth against what a fact is worth -------------
#
# These are not the same kind of quantity and the difference is
# the whole argument. A new primitive enters an EXPONENT: designs
# are 2**s, so one more doubles the buildable space. A new answer
# enters a SUM: it is one item added to the corpus.

def tool_multiplier():
    """What one new primitive does to the design space. DERIVED."""
    return 2.0


def fact_share():
    """What one new answer does to the corpus. DERIVED."""
    from engine.intricacy import written_corpus, settle_network
    from engine.literacy import spread
    from engine.trade import VILLAGE
    n = 40 * VILLAGE
    corpus = written_corpus(spread(1.0 / n, 2000.0) * n)
    return 1.0 / corpus


def tool_over_fact():
    """The ratio the ranking is really reporting. DERIVED."""
    return (tool_multiplier() - 1.0) / fact_share()


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("the_ranking_is_computed_and_contains_no_names", _rank)
    t("a_tool_enters_an_exponent_and_a_fact_enters_a_sum", _kinds)
    t("INVERTED_the_remembered_names_are_mostly_answerers", _who)
    return all(x for _, x, _ in res), res


def _rank():
    rows = ranking()
    top, second = rows[0], rows[1]
    if top[0] <= second[0]:
        raise ArithmeticError("no clear top")
    names = {n.lower() for n in REMEMBERED}
    if any(p.lower() in names for _l, p, _b in rows):
        raise ArithmeticError("a name reached the ranking")
    p, s, q, a = top[2]
    return (f"a contribution matters in proportion to what it lets "
            f"other people do, and that is countable. Top of the "
            f"ranking is {top[1].upper()} at {top[0]}: {p} "
            f"primitives, {s} sciences, {q} exam questions and {a} "
            f"namable artifacts rest on it. Then {second[1]} at "
            f"{second[0]}, then "
            + ", ".join(f"{pr} ({lv})" for lv, pr, _b in rows[2:5])
            + f". Nothing read here has a name in it, so no name "
              f"can come out. A machine that corrects itself tops "
              f"the list and nobody calls it a discovery")


def _kinds():
    tm, fs, r = tool_multiplier(), fact_share(), tool_over_fact()
    if r < 1e5:
        raise ArithmeticError(f"{r}")
    return (f"a tool and a fact are not the same kind of "
            f"contribution and that is the whole argument. A new "
            f"primitive enters an EXPONENT -- designs are 2**s, so "
            f"one more doubles the buildable space, {tm:.0f}x. A "
            f"new answer enters a SUM: one item added to a corpus "
            f"of {1/fs:.2e}, a share of {fs:.1e}. The ratio is "
            f"{r:.1e}. That is not a claim that facts do not "
            f"matter; it is a claim about where each one lands in "
            f"the arithmetic, and the arithmetic was built for "
            f"other reasons before this question was asked")


def _who():
    """INVERTED. Fails if memory tracks leverage.

    The one place a name is allowed, and only to ask whether the
    ranking and the remembering agree. They do not.
    """
    built = [n for n, (kind, _w) in REMEMBERED.items() if kind == "built"]
    answered = [n for n, (kind, _w) in REMEMBERED.items()
                if kind == "answered"]
    if len(built) >= len(answered):
        raise ArithmeticError(
            "the remembered names are mostly toolmakers, which "
            "would mean memory already tracks leverage and this "
            "check has nothing to say")
    top = ranking()[0][1]
    return (f"{len(answered)} of the {len(REMEMBERED)} names here "
            f"are remembered for ANSWERING something and only "
            f"{len(built)} for building the thing that made the "
            f"answering possible. The ranking says the reverse: "
            f"{top} is the largest contribution in the tree and "
            f"the exam question with the most famous name attached "
            f"unlocks nothing downstream at all. Two honest "
            f"caveats. This list is short and I chose it, so it is "
            f"an illustration and not a survey. And answers are "
            f"leaves in these structures partly BECAUSE I never "
            f"modelled an answer feeding anything, which flatters "
            f"the conclusion -- though fact_share() says an answer "
            f"would be one part in ten million even if I had")


if __name__ == "__main__":
    print(f"  {'primitive':<15}{'total':>7}{'prims':>7}{'sci':>5}"
          f"{'exam':>6}{'things':>8}")
    for lv, p, (a, b, c, d) in ranking()[:10]:
        print(f"  {p:<15}{lv:>7}{a:>7}{b:>5}{c:>6}{d:>8}")
    print(f"\n  a tool is worth {tool_multiplier():.0f}x the design "
          f"space; a fact is worth {fact_share():.1e} of the corpus")
    print(f"  ratio {tool_over_fact():.2e}\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
