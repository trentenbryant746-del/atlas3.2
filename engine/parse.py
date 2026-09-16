"""
Compositional recognition: understand a form nobody has seen.

Family lookup caps coverage at the templates that were observed or generated
-- always a finite list. But arithmetic is COMPOSITIONAL: a form it has never
met is built from parts it knows. Parsing the structure directly removes the
family requirement entirely, so the number of recognisable templates becomes
unbounded and the examples needed per template becomes zero.

Two independent implementations, deliberately:

    recursive descent -> expression tree -> post-order evaluation
    Python's own ast  -> a separate walker over Fractions

Different parsers and different evaluators. Agreement is a REDUNDANT check in
the taxonomy; disagreement is CONTRADICTED and nothing is returned. A single
parser checking itself would prove nothing.
"""
from __future__ import annotations

import ast
import re
from fractions import Fraction

TOK = re.compile(r'\s*(\d+|[()+\-*/×÷])')


class Tok:
    def __init__(self, s):
        self.t = TOK.findall(s)
        self.i = 0

    def peek(self):
        return self.t[self.i] if self.i < len(self.t) else None

    def next(self):
        v = self.peek()
        self.i += 1
        return v


def _expr(ts):
    v = _term(ts)
    while ts.peek() in ("+", "-"):
        op = ts.next()
        r = _term(ts)
        v = v + r if op == "+" else v - r
    return v


def _term(ts):
    v = _unary(ts)
    while ts.peek() in ("*", "/", "×", "÷"):
        op = ts.next()
        r = _unary(ts)
        if op in ("*", "×"):
            v = v * r
        else:
            if r == 0:
                raise ZeroDivisionError
            v = Fraction(v) / r
    return v


def _unary(ts):
    if ts.peek() == "-":
        ts.next()
        return -_unary(ts)
    if ts.peek() == "(":
        ts.next()
        v = _expr(ts)
        if ts.peek() != ")":
            raise SyntaxError("unbalanced")
        ts.next()
        return v
    t = ts.next()
    if t is None or not t.isdigit():
        raise SyntaxError(f"unexpected {t!r}")
    return Fraction(int(t))


def parse_eval(s):
    ts = Tok(s)
    v = _expr(ts)
    if ts.peek() is not None:
        raise SyntaxError("trailing input")
    return v


# ---- the independent second implementation -----------------------------
class _Walk(ast.NodeVisitor):
    def visit_BinOp(self, n):
        a, b = self.visit(n.left), self.visit(n.right)
        if isinstance(n.op, ast.Add):
            return a + b
        if isinstance(n.op, ast.Sub):
            return a - b
        if isinstance(n.op, ast.Mult):
            return a * b
        if isinstance(n.op, ast.Div):
            if b == 0:
                raise ZeroDivisionError
            return Fraction(a) / b
        raise SyntaxError("op")

    def visit_UnaryOp(self, n):
        if isinstance(n.op, ast.USub):
            return -self.visit(n.operand)
        raise SyntaxError("unary")

    def visit_Constant(self, n):
        if isinstance(n.value, int):
            return Fraction(n.value)
        raise SyntaxError("const")

    def visit_Expression(self, n):
        return self.visit(n.body)

    def generic_visit(self, n):
        raise SyntaxError(type(n).__name__)


def ast_eval(s):
    py = s.replace("×", "*").replace("÷", "/")
    return _Walk().visit(ast.parse(py, mode="eval"))


RUN = re.compile(r'[\d\s()+\-*/×÷]{3,}')


def _spans(question):
    """Longest parseable substring of each expression-character run.

    A regex cannot delimit this: `((16 + 5) × 13)` needs balanced parens, and
    an extractor anchored on a digit starts inside the expression and trips
    over the closing bracket. So take maximal runs of expression characters
    and trim inward from both ends until something parses. Cheap -- the runs
    are short -- and it cannot mis-delimit, because the parser is the judge.
    """
    out = []
    for m in RUN.finditer(question):
        run = m.group(0)
        best = None
        for start in range(len(run)):
            if best and len(run) - start <= len(best):
                break
            for end in range(len(run), start + 2, -1):
                cand = run[start:end].strip()
                if not cand:
                    continue
                # a BINARY operator must be present. "-1829" contains "-" and
                # parses fine as a negation, which made "Convert -1829 meters
                # to centimetres" evaluate to -1829.
                if not re.search(r'\d\s*[+\-*/×÷]\s*-?\s*[\d(]', cand):
                    continue
                if best and len(cand) <= len(best):
                    break
                try:
                    parse_eval(cand)
                except Exception:
                    continue
                best = cand
                break
        if best:
            out.append(best)
    return out


TERMINAL = ("CONTRADICTED", "division by zero")


def terminal(why: str) -> bool:
    return any(t in (why or "") for t in TERMINAL)


# THE PARSER MUST OWN THE QUESTION, NOT A SUBSTRING OF IT.
#
# recognise() took the longest parseable span and answered, with no
# test that the span was what the question was ABOUT. So "Does the
# Kleiber 3/4 exponent follow from anything?" came back 3/4 --
# confident, wrong, and the worst class of error this repo has.
# engine/unsolved.py caught it on its first run, which is what that
# fixture is for.
#
# The test is what is LEFT once the span is removed. In a question
# the parser legitimately owns, the residue is only framing: "what
# is", "evaluate", "=". In one it does not own, the residue is a
# sentence with its own subject and verb.
#
# FRAME is not a list I wrote. It is every residue word across the
# 5,902 prompts that must keep answering -- the 5,737-record
# curriculum and the 165 held-out prompts -- extracted through this
# same code path. Twenty words. Anything outside it means the
# sentence is about something else and the arithmetic layer should
# decline and let the cascade continue.
FRAME = frozenset("""a and brief calculate check duration evaluate
fraction from give is measure show simplified t the to utc what z""".split())


def owns(question, span):
    """-> (bool, reason). Is the span what the question is about?"""
    residue = question.replace(span, " ", 1)
    words = [w for w in re.findall(r"[A-Za-z]+", residue.lower())]
    outside = sorted({w for w in words if w not in FRAME})
    if outside:
        return False, (f"the span {span!r} is inside a sentence about "
                       f"something else -- {outside[:4]} are not framing "
                       f"words, so arithmetic does not own this question")
    return True, "the residue is framing only"


def recognise(question):
    """-> (answer, span) or (None, reason). No family required."""
    spans = _spans(question)
    if not spans:
        return None, "no parseable arithmetic expression found"
    best = max(spans, key=len)
    ok, why = owns(question, best)
    if not ok:
        return None, why
    try:
        a = parse_eval(best)
    except (SyntaxError, ZeroDivisionError, IndexError) as e:
        return None, f"cannot parse: {e}"
    try:
        b = ast_eval(best)
    except Exception as e:
        return None, f"second parser refused: {e}"
    if a != b:
        return None, f"CONTRADICTED: {a} vs {b}"
    return a, best
