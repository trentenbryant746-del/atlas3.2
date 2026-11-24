"""
English numerals, both directions, so that one can check the other.

Atlas refused "spell the number 1247 in words" and it should not have. The
answer is not a fact to be looked up, it is a COMPOSITION, and composition
is the one thing this repository is built to do: a numeral is groups of
three digits, each group named the same way, each group carrying a scale
word. Nothing about 1247 has to be stored.

WHAT IS CONVENTIONAL, STATED PLAINLY. You cannot derive that 7 is called
"seven". Thirty-five morphemes below are NAMING, in the sense
rules/kinds.py means by ASSERTED -- the same status as engine/naming.py's
KNOWN_AS table, and for the same reason. Everything else here is derived
from them: the twenties through nineties compose from the ones, the
hundreds from "hundred", and the scale words repeat every three digits.
Thirty-five conventions buy every integer up to 10^18.

AND THE CHECK IS A ROUND TRIP, which is why both directions are here. The
honest way to know that say(1247) is right is to READ IT BACK and get 1247,
which needs a parser, which is a second piece of language and not a
restatement of the first. say() walks digits outward into words; read()
accumulates words inward into a number. They fail differently, so their
agreement means something -- this is IDENTITY in rules/kinds.py's sense.

That is also why read() is worth having on its own. It is the first thing
in Atlas that can take English as INPUT rather than only emit it.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# --- the conventional part: 28 names, and nothing else is stored --------
ONES = ("zero one two three four five six seven eight nine ten eleven "
        "twelve thirteen fourteen fifteen sixteen seventeen eighteen "
        "nineteen").split()
TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty",
        70: "seventy", 80: "eighty", 90: "ninety"}
SCALES = ["", "thousand", "million", "billion", "trillion", "quadrillion",
          "quintillion"]
NEGATIVE = "negative"

MAX = 1000 ** len(SCALES) - 1


def _say_group(n: int) -> str:
    """0 < n < 1000 -> words. The whole grammar of a numeral is here."""
    if n < 20:
        return ONES[n]
    if n < 100:
        ten, one = divmod(n, 10)
        return TENS[ten * 10] + (f"-{ONES[one]}" if one else "")
    hund, rest = divmod(n, 100)
    out = f"{ONES[hund]} hundred"
    return out + (f" {_say_group(rest)}" if rest else "")


def say(n: int) -> str:
    """An integer -> its English numeral."""
    n = int(n)
    if abs(n) > MAX:
        raise ValueError(f"beyond {SCALES[-1]}: {n}")
    if n == 0:
        return ONES[0]
    sign = f"{NEGATIVE} " if n < 0 else ""
    n = abs(n)

    groups = []
    while n:
        n, g = divmod(n, 1000)
        groups.append(g)
    parts = []
    for i in range(len(groups) - 1, -1, -1):
        if groups[i] == 0:
            continue                       # "one million five", not "... zero"
        scale = SCALES[i]
        parts.append(_say_group(groups[i]) + (f" {scale}" if scale else ""))
    return sign + " ".join(parts)


# --- reading, which is a different algorithm and so can check the first -
_WORD = {w: i for i, w in enumerate(ONES)}
_WORD.update({w: v for v, w in TENS.items()})
_SCALE = {w: 1000 ** i for i, w in enumerate(SCALES) if w}


def read(s: str) -> int:
    """An English numeral -> the integer. Raises on anything else.

    Accumulates rather than composes: `total` holds groups already closed
    by a scale word and `group` the one being built, so "one million two
    hundred thousand five" needs no lookahead.
    """
    text = s.strip().lower().replace("-", " ").replace(",", " ")
    toks = [t for t in text.split() if t and t != "and"]
    if not toks:
        raise ValueError("no numeral in input")

    neg = toks[0] in (NEGATIVE, "minus")
    if neg:
        toks = toks[1:]
    if not toks:
        raise ValueError("a sign is not a number")

    total = group = 0
    seen = False
    for t in toks:
        if t in _WORD:
            group += _WORD[t]
        elif t == "hundred":
            if group == 0:
                raise ValueError("'hundred' with nothing in front of it")
            group *= 100
        elif t in _SCALE:
            if group == 0:
                raise ValueError(f"'{t}' with nothing in front of it")
            total += group * _SCALE[t]
            group = 0
        else:
            raise ValueError(f"not a numeral word: {t!r}")
        seen = True
    if not seen:
        raise ValueError("no numeral in input")
    total += group
    return -total if neg else total


def roundtrip(n: int) -> bool:
    """The claim say() makes about itself."""
    try:
        return read(say(n)) == int(n)
    except Exception:
        return False


# ------------------------------------------------------------------ check
def check():
    out = []

    def t(name, fn):
        try:
            out.append((name, True, str(fn())))
        except Exception as e:
            out.append((name, False, f"{type(e).__name__}: {e}"))
    t("every_numeral_reads_back_as_itself", _rt)
    t("the_stored_part_is_thirty_five_names", _stored)
    t("structure_is_composed_not_tabulated", _compose)
    t("a_non_numeral_is_refused_not_guessed", _refuse)
    t("scale_words_repeat_every_three_digits", _scale)
    t("the_router_answers_these_and_refuses_the_rest", _routed)
    return all(o[1] for o in out), out


def _rt():
    import random
    rng = random.Random(7)
    span = list(range(0, 1101)) + [-1, -17, -1247]
    span += [rng.randrange(0, 10 ** 15) for _ in range(4000)]
    span += [10 ** k for k in range(0, 19)]
    span += [10 ** k - 1 for k in range(1, 19)]
    bad = [n for n in span if not roundtrip(n)]
    if bad:
        raise ArithmeticError(f"{len(bad)} failed, e.g. {bad[:3]}")
    return (f"{len(span)} integers, 0 to 10^18 and negatives, each spelled "
            f"and read back to itself. say() composes outward and read() "
            f"accumulates inward, so agreement is two algorithms agreeing "
            f"and not one restated")


def _stored():
    n = len(ONES) + len(TENS) + len([s for s in SCALES if s]) + 1
    if n != 35:
        raise AssertionError(f"{n} stored names, expected 35")
    return (f"{n} conventional morphemes -- {len(ONES)} ones, {len(TENS)} "
            f"tens, {len([s for s in SCALES if s])} scales, one sign word "
            f"-- and they cover every integer to 10^18. You "
            f"cannot derive that 7 is 'seven'; everything above that is "
            f"derived from these and nothing else is stored")


def _compose():
    if "forty-seven" in TENS.values() or "forty-seven" in ONES:
        raise AssertionError("a composed form was stored")
    if say(47) != "forty-seven" or say(1247) != (
            "one thousand two hundred forty-seven"):
        raise AssertionError(f"composition wrong: {say(1247)!r}")
    return ("forty-seven and 'one thousand two hundred forty-seven' are "
            "composed at call time from 'forty', 'seven', 'hundred' and "
            "'thousand'; neither string is in the table")


def _refuse():
    for bad in ("hundred", "seven potato", "", "thousand million",
                "negative", "eleventy"):
        try:
            read(bad)
        except ValueError:
            continue
        raise AssertionError(f"read({bad!r}) returned instead of refusing")
    return ("six malformed numerals refused with a reason rather than "
            "coerced to a number -- 'hundred' alone, a word that is not a "
            "numeral, a bare sign, and a scale word with nothing in front")


def _scale():
    if read(say(10 ** 6)) != 10 ** 6 or say(10 ** 6) != "one million":
        raise AssertionError("scale words broken")
    got = say(1_000_200_005)
    if got != "one billion two hundred thousand five":
        raise AssertionError(f"empty groups mishandled: {got!r}")
    return (f"10^9 + 200,000 + 5 spells '{got}' -- the empty middle group "
            f"is skipped rather than named, which is the one place a "
            f"digit-by-digit speller gets it wrong")


def _routed():
    """The capability as the cascade sees it, not as this module sees it.

    Imported inside the function on purpose: rules/language.py imports this
    module, so a top-level import of the router would close a cycle.
    """
    from engine.route import route, ANSWERED, UNCOVERED

    want = "one thousand two hundred forty-seven"
    a = route("spell the number 1247 in words")
    if a.verdict != ANSWERED or a.answer != want:
        raise AssertionError(f"spell: {a.verdict} {a.answer!r}")
    b = route("what number is one thousand two hundred forty-seven")
    if b.verdict != ANSWERED or b.answer != "1247":
        raise AssertionError(f"read: {b.verdict} {b.answer!r}")

    # the one that mattered: a malformed numeral must ABSTAIN. The first
    # version let it reach read(), which raised ValueError straight out of
    # route() and took the cascade down with it -- a crash where the whole
    # repository's answer is a refusal.
    for bad in ("what number is eleventy seven",
                "what number is the capital of France"):
        c = route(bad)
        if c.verdict != UNCOVERED:
            raise AssertionError(f"{bad!r} gave {c.verdict}, not UNCOVERED")
    return ("both directions route and agree with their own round trip, and "
            "a numeral that does not parse is UNCOVERED rather than an "
            "exception out of route() -- binding is part of recognition, so "
            "a group that will not read means the rule does not own the "
            "question")


if __name__ == "__main__":
    for n in (0, 7, 13, 47, 100, 101, 1247, -1247, 1_000_200_005):
        print(f"  {n:>14,}  {say(n)}")
    ok, res = check()
    print()
    for n, o, d in res:
        print(f"{'PASS' if o else 'FAIL'}  {n:40}{d[:58]}")
    print("\nall:", ok)
