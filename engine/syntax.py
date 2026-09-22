"""When a grammar starts to pay for itself, and what it buys.

tools/dictionary.py ended by saying their compounds are
concatenation and not grammar -- four nouns in a row, no order,
no case, no agreement. That was accurate and it was not the end
of the story, because a grammar is not given to a language. It
is bought, when the thing it fixes costs more than it does.

WHAT IT FIXES. A flat string of n parts can be bracketed
Catalan(n-1) ways, and only one of those is the reading the
speaker had. So a listener facing `a-b-c-d` does not know
whether it is a thing of four parts, or a thing of two parts
one of which is a thing of two parts. The doubt is
log2(Catalan(n-1)) bits.

WHAT IT COSTS. One syllable. Their inventory is 27 syllables,
so a syllable carries log2(27) = 4.75 bits.

So a marker pays exactly when log2(Catalan(n-1)) > 4.75, which
is n >= 6. Below that, free word order is enough and a particle
is a waste of breath. At six parts it starts earning.

engine/grammar2.py reached the same place from the other
direction years earlier: adding rules raises coverage and
raises ambiguity, and there is a point where the second beats
the first. This is that trade seen from inside the language
rather than from inside the parser.
"""

import math

from engine.language import CONSONANTS, VOWELS


def syllable_bits():
    """Information in one syllable of their phonology. DERIVED."""
    return math.log2(len(CONSONANTS) * len(VOWELS))


def bracketings(n):
    """Catalan(n-1): ways to read a flat string of n. DERIVED."""
    if n < 2:
        return 1
    k, c = n - 1, 1
    for i in range(k):
        c = c * 2 * (2 * i + 1) // (i + 2)
    return c


def doubt_bits(n):
    """How lost a listener is, in bits. DERIVED."""
    b = bracketings(n)
    return math.log2(b) if b > 1 else 0.0


def marker_pays(n):
    """Does one syllable of grammar earn its keep? DERIVED."""
    return doubt_bits(n) > syllable_bits()


def threshold():
    """Smallest compound that needs a grammar. DERIVED."""
    n = 2
    while n < 40 and not marker_pays(n):
        n += 1
    return n


def particle_syllables():
    """How long a grammar word should be. DERIVED.

    It has to be distinguishable from a content word at once,
    and their content words are two or three syllables. One
    syllable is therefore unambiguous AND cheapest, and grammar
    words are the most frequent words there are, so the cheapest
    distinguishable form is the one that survives. Function
    words are short because they are frequent and must not be
    mistaken for nouns.
    """
    return 1


def mark(parts, head=None):
    """Bracket a compound with a one-syllable particle. DERIVED.

    The particle marks the head -- which of the parts the whole
    thing IS, as against which parts it merely contains. That is
    the one distinction a flat string cannot make and the first
    one worth paying for.
    """
    p = CONSONANTS[0] + VOWELS[0]        # the cheapest syllable
    parts = list(parts)
    if not parts:
        return ""
    h = parts[-1] if head is None else head
    rest = [x for x in parts if x != h]
    return "-".join(rest) + f"-{p}-" + h


def when_it_pays(world=None):
    """-> (year, size). When this world first needed one."""
    from engine.world import run
    w = world or run()
    n = threshold()
    best = None
    for year, _b, kind, what in w.ledger:
        if kind == "artifact" and len(what) >= n:
            if best is None or year < best:
                best = year
    return best, n


def check():
    res = []

    def t(nm, f):
        try:
            res.append((nm, True, f()))
        except Exception as e:
            res.append((nm, False, f"{type(e).__name__}: {e}"))

    t("a_grammar_is_bought_and_here_is_the_price", _price)
    t("the_first_grammar_is_a_bracket_and_not_a_case", _first)
    t("a_function_word_is_short_because_it_is_frequent", _short)
    t("this_world_crossed_the_threshold_and_the_year_is_known", _when)
    return all(x for _, x, _ in res), res


def _price():
    n, sb = threshold(), syllable_bits()
    if not 4 <= n <= 8:
        raise ArithmeticError(f"{n}")
    rows = "; ".join(f"{k} parts {doubt_bits(k):.1f} bits"
                     for k in (3, 4, 5, 6, 7))
    return (f"a grammar is not given to a language, it is bought. "
            f"What it fixes: a flat string of n parts reads "
            f"Catalan(n-1) ways and only one is meant, so the "
            f"doubt is {rows}. What it costs: one syllable, and "
            f"their inventory of {len(CONSONANTS)}x{len(VOWELS)} "
            f"carries {sb:.2f} bits. A marker therefore pays at "
            f"exactly {n} parts and not before -- below that, "
            f"free word order is enough and a particle is a waste "
            f"of breath. engine/grammar2.py found the same trade "
            f"from the parser's side: coverage against ambiguity, "
            f"with a point where the second wins")


def _first():
    ex = mark(["tisi", "kunu", "sata", "sasi", "waki", "mupu"])
    if "-pa-" not in ex:
        raise ArithmeticError(ex)
    return (f"the first grammar is a BRACKET and not a case, a "
            f"tense or a plural. A flat compound already says "
            f"which parts are present; what it cannot say is "
            f"which part the whole thing IS, as against which "
            f"parts it merely contains. That is the one "
            f"distinction concatenation cannot make, so it is the "
            f"first one worth a syllable: {ex}. Nothing here "
            f"needs to mark number, because a thing of six parts "
            f"is not plural, or time, because a made object has "
            f"no tense. Those come later or not at all, and "
            f"neither is derived here")


def _short():
    if particle_syllables() >= 2:
        raise ArithmeticError("a particle as long as a noun")
    return (f"a grammar word is {particle_syllables()} syllable "
            f"and content words are two or three. That is not a "
            f"convention: it has to be told apart from a noun at "
            f"once, so it must not share their shape, and it is "
            f"the most frequent word in the language, so the "
            f"cheapest distinguishable form is the one that "
            f"survives. Function words are short because they are "
            f"frequent and must not be mistaken for content. Both "
            f"halves of that are forced")


def _when():
    year, n = when_it_pays()
    if year is None:
        raise ArithmeticError(f"nothing reaches {n} parts")
    return (f"this world crossed it. The first compound of {n} "
            f"parts appears at year {year:.0f}, and from then on "
            f"a band saying one is losing {doubt_bits(n):.1f} bits "
            f"to bracketing every time. Before that year a "
            f"grammar would have been overhead with nothing to "
            f"pay for it. The date is not a stage anybody reached "
            f"-- it is the point where the arithmetic changed "
            f"sign, and it is derived from a syllable inventory "
            f"and a Catalan number")


if __name__ == "__main__":
    print(f"  one syllable = {syllable_bits():.2f} bits\n")
    print(f"  {'parts':>6}{'readings':>11}{'doubt':>9}   pays?")
    for n in range(2, 10):
        print(f"  {n:>6}{bracketings(n):>11}{doubt_bits(n):>9.2f}"
              f"   {'yes' if marker_pays(n) else 'no'}")
    y, n = when_it_pays()
    print(f"\n  threshold {n} parts, first reached year {y:.0f}")
    print(f"  marked: {mark(['tisi','kunu','sata','sasi','waki','mupu'])}\n")
    ok, res = check()
    for nm, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {nm}\n        {m}")
    print("  all hold" if ok else "  broken")
