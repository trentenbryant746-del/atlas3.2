"""Their words, and why we can read them.

The encyclopedia written at 3.2.9 was in English, and the English
was mine: every phrase in it came from a description I typed into
engine/artifact.py. That is us writing their record for them.

So they get a language. Not ours -- there is no way to hand them
English that is not the same mistake in a larger form. A band
coins a token when it first makes something, out of a phoneme
inventory and nothing else. Different bands coin different words
for the same thing, because there is nothing to make them agree,
and that is what actually happens to languages left alone.

WHY WE CAN TRANSLATE ANYWAY, and this is the whole point: we
watched them name it. A word is a sound attached to an act of
making, and the ledger recorded the act. So the dictionary is
not a gift we gave them, it is an observation we made -- the
same position a field linguist is in, pointing at a thing and
writing down the noise.

What we cannot do is tell them what to call anything, and what
we must not do is read meaning into a word beyond the referent
we saw attached to it.
"""

import random

CONSONANTS = "ptkmnslwj"        # CHOSEN, a small ordinary inventory
VOWELS = "aiu"                  # CHOSEN, a three-vowel system


def coin(rng, syllables=None):
    """A new token. Sound only -- it means nothing yet. DERIVED."""
    n = syllables or rng.choice((2, 2, 3))
    return "".join(rng.choice(CONSONANTS) + rng.choice(VOWELS)
                   for _ in range(n))


class Lexicon:
    """One band's words, and what each was attached to."""

    __slots__ = ("band", "word", "means", "borrowed")

    def __init__(self, band):
        self.band = band
        self.word = {}        # referent -> token
        self.means = {}       # token -> referent
        self.borrowed = set()

    def name(self, referent, rng):
        """Coin a word for something just made. DERIVED."""
        if referent in self.word:
            return self.word[referent]
        for _ in range(40):
            tok = coin(rng)
            if tok not in self.means:
                break
        self.word[referent] = tok
        self.means[tok] = referent
        return tok

    def take(self, referent, token):
        """Borrow a neighbour's word rather than coin one."""
        if referent in self.word:
            return False
        self.word[referent] = token
        self.means[token] = referent
        self.borrowed.add(token)
        return True

    def compound(self, parts):
        """Their phrase for a thing made of several crafts.

        A compound is the part-words in the order the band
        happens to hold them. Nothing here imposes a grammar --
        this is concatenation, which is what a language does
        before it has one.
        """
        got = [self.word[p] for p in parts if p in self.word]
        return "-".join(got) if got else None


def translate(token, lexicon):
    """-> the referent we watched the word attached to.

    This is not a dictionary anybody was given. It is what we
    saw: the band made a thing, and made a noise, and the ledger
    has both. Nothing may be read into the word past that.
    """
    return lexicon.means.get(token)


def gloss(token, lexicon):
    """-> our words for their word, via the referent. DERIVED."""
    from engine.artifact import PRIMITIVES
    ref = translate(token, lexicon)
    if ref is None:
        return None
    if isinstance(ref, str):
        return PRIMITIVES[ref][3] if ref in PRIMITIVES else ref
    return "; ".join(PRIMITIVES[p][3] for p in sorted(ref)
                     if p in PRIMITIVES)


def agreement(lexicons, referent):
    """-> (distinct words, bands holding one). DERIVED.

    How many different words a region has for the same thing,
    which is a measure of how little the bands meet.
    """
    got = [lx.word[referent] for lx in lexicons if referent in lx.word]
    return len(set(got)), len(got)


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("a_word_is_a_sound_attached_to_an_act_of_making", _coin)
    t("bands_left_alone_do_not_agree_on_words", _diverge)
    t("we_can_translate_because_we_watched_them_name_it", _trans)
    return all(x for _, x, _ in res), res


def _coin():
    rng = random.Random(1)
    toks = {coin(rng) for _ in range(200)}
    if len(toks) < 150:
        raise ArithmeticError(f"only {len(toks)} distinct in 200")
    lx = Lexicon(0)
    w = lx.name("smelting", random.Random(2))
    return (f"a token is {len(CONSONANTS)} consonants and "
            f"{len(VOWELS)} vowels in open syllables, two or three "
            f"of them: {len(CONSONANTS)*len(VOWELS)} syllables and "
            f"{(len(CONSONANTS)*len(VOWELS))**2 + (len(CONSONANTS)*len(VOWELS))**3:,} "
            f"possible words, of which 200 draws gave "
            f"{len(toks)} distinct. The word for smelting in this "
            f"band is {w!r} and it means nothing -- it is a noise "
            f"that got attached to an act of making. No English "
            f"was handed to anybody, because handing them English "
            f"is the same mistake as writing their encyclopedia "
            f"for them, only larger")


def _diverge():
    rng = random.Random(3)
    lexes = [Lexicon(i) for i in range(8)]
    for lx in lexes:
        lx.name("smelting", rng)
    distinct, holders = agreement(lexes, "smelting")
    if distinct < holders:
        raise ArithmeticError(f"{distinct} words for {holders} bands")
    return (f"{holders} bands each coin a word for the same craft "
            f"and get {distinct} different words, because nothing "
            f"makes them agree. That is not a flaw in the model, "
            f"it is what happens to languages left alone -- "
            f"agreement is a CONSEQUENCE of contact and has to be "
            f"paid for in meetings. A region with one word for "
            f"smelting is a region that trades")


def _trans():
    from engine.artifact import PRIMITIVES
    rng = random.Random(4)
    lx = Lexicon(0)
    for p in ("smelting", "gearing", "optics"):
        lx.name(p, rng)
    tok = lx.word["gearing"]
    got = gloss(tok, lx)
    phrase = lx.compound(["smelting", "gearing"])
    if got != PRIMITIVES["gearing"][3]:
        raise ArithmeticError(f"{tok} -> {got}")
    return (f"we can read {tok!r} as {got!r} for one reason: we "
            f"watched them attach it. The band made the thing and "
            f"made the noise, and the ledger has both, so the "
            f"dictionary is an OBSERVATION and not a gift. That "
            f"is the position a field linguist is in -- point at "
            f"a thing, write down the sound -- and it is the only "
            f"honest way to have both a language that is theirs "
            f"and a record we can read. Their phrase for a thing "
            f"of two crafts is {phrase!r}, which is concatenation "
            f"and not grammar, because nothing here has given "
            f"them one")


if __name__ == "__main__":
    rng = random.Random(7)
    lexes = [Lexicon(i) for i in range(5)]
    for lx in lexes:
        for p in ("heat", "smelting", "gearing"):
            lx.name(p, rng)
    print(f"  {'band':<6}{'heat':<10}{'smelting':<10}{'gearing':<10}")
    for lx in lexes:
        print(f"  {lx.band:<6}{lx.word['heat']:<10}"
              f"{lx.word['smelting']:<10}{lx.word['gearing']:<10}")
    print()
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
