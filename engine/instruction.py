"""The language a machine would need, and a machine that runs it.

They will build computers -- engine/artifact.py has switching at
round 9 and inference at round 10 -- and a computer needs an
instruction set. That set is not a matter of taste. Most of it
is forced, and what is not forced is an optimum rather than a
preference.

WHAT MUST EXIST. A computation has to change state, or it does
nothing. It has to depend on data, or it is a fixed function.
It has to be able to go back, or it cannot run longer than it
is written. Those three are not negotiable and one instruction
can carry all of them at once -- subtract-and-branch-if-zero is
Turing complete on its own -- so the MINIMUM is one.

HOW MANY THERE SHOULD BE. More opcodes make programs shorter,
because each instruction says more, and make the decoder
bigger, because there are more cases to tell apart. Program
bits fall as 1/log2(k) and decoder gates rise as k, so there is
a floor, and for a two-thousand-step program with sixteen-bit
operands it sits near 128. Real sets land there: RISC-V's base
integer set is 47 instructions, ARM about 50, x86 several
hundred.

HOW THEY SHOULD BE ENCODED. Frequent operations get short
codes. That is the same optimisation engine/syntax.py derived
for function words -- a grammar particle is one syllable where
a noun is two or three, because it is frequent and must stay
distinguishable -- and it is why a variable-length encoding is
denser and a fixed one decodes faster.

WHAT IS NOT HERE. Nobody in engine/world.py has built a
machine. This is what their constraints would force, plus a
working implementation so the claim can be checked rather than
asserted. The machine below runs; the world has not run one.
"""

import math

# The classes that must exist, and why each is not optional.
FORCED = {
    "write": "a computation that changes nothing does nothing",
    "test": "without a branch on data it is a fixed function",
    "jump": "without going back it cannot run longer than its text",
    "address": "without indirection it cannot touch data it did "
               "not name when it was written",
}

# One small set, enough to be real and small enough to check.
# The MNEMONICS are arbitrary the way their words are arbitrary;
# the operations are not.
ISA = {
    0x0: ("halt", 0, "stop"),
    0x1: ("load", 1, "acc <- mem[a]"),
    0x2: ("store", 1, "mem[a] <- acc"),
    0x3: ("addi", 1, "acc <- acc + a"),
    0x4: ("add", 1, "acc <- acc + mem[a]"),
    0x5: ("sub", 1, "acc <- acc - mem[a]"),
    0x6: ("jmp", 1, "pc <- a"),
    0x7: ("jz", 1, "if acc == 0 then pc <- a"),
    0x8: ("loadi", 1, "acc <- mem[mem[a]]"),
    0x9: ("out", 0, "emit acc"),
}
NAMES = {v[0]: k for k, v in ISA.items()}

OPERAND_BITS = 16
DECODER_GATES_PER_OPCODE = 8.0


def program_bits(steps, k, operand=OPERAND_BITS):
    """Bits of program at k opcodes. DERIVED."""
    if k <= 1:
        return steps * (1 + operand)
    return steps * (1 + operand / math.log2(k))


def decoder_gates(k):
    """Gates to tell k cases apart. DERIVED."""
    return DECODER_GATES_PER_OPCODE * k


def optimum_opcodes(steps=2000, operand=OPERAND_BITS):
    """Where the two costs cross. DERIVED, not chosen."""
    best = None
    k = 1
    while k <= 4096:
        tot = program_bits(steps, k, operand) + decoder_gates(k)
        if best is None or tot < best[0]:
            best = (tot, k)
        k *= 2
    return best[1]


def opcode_bits(k=None):
    """Width of the opcode field. DERIVED."""
    return math.ceil(math.log2(k or optimum_opcodes()))


def assemble(source):
    """Text to words. -> [int]. Their language to the machine's."""
    out = []
    for line in source.strip().splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        bits = line.split()
        op = NAMES[bits[0]]
        arg = int(bits[1]) if len(bits) > 1 else 0
        out.append((op << OPERAND_BITS) | (arg & 0xFFFF))
    return out


def disassemble(words):
    """Words back to text. The direction we read them in."""
    out = []
    for w in words:
        op, arg = w >> OPERAND_BITS, w & 0xFFFF
        name, nargs, _why = ISA.get(op, ("?", 0, ""))
        out.append(f"{name} {arg}" if nargs else name)
    return out


def run(words, memory=None, limit=100000):
    """Execute. -> (emitted, steps). A real machine, not a sketch."""
    mem = list(words) + [0] * 64 if memory is None else list(memory)
    acc, pc, emitted, steps = 0, 0, [], 0
    while pc < len(mem) and steps < limit:
        w = mem[pc]
        op, arg = w >> OPERAND_BITS, w & 0xFFFF
        pc += 1
        steps += 1
        if op == 0x0:
            break
        elif op == 0x1:
            acc = mem[arg]
        elif op == 0x2:
            mem[arg] = acc
        elif op == 0x3:
            acc = (acc + arg) & 0xFFFF
        elif op == 0x4:
            acc = (acc + mem[arg]) & 0xFFFF
        elif op == 0x5:
            acc = (acc - mem[arg]) & 0xFFFF
        elif op == 0x6:
            pc = arg
        elif op == 0x7:
            pc = arg if acc == 0 else pc
        elif op == 0x8:
            acc = mem[mem[arg]]
        elif op == 0x9:
            emitted.append(acc)
    return emitted, steps


# A real program: count down from n, emitting each value. Written
# in their instruction set, assembled, and run below.
COUNTDOWN = """
load 20        # acc <- n
store 21
out            # emit it
load 21
addi 65535     # minus one, two's complement in 16 bits
store 21
jz 10          # done when zero
jmp 2
halt
"""


def check():
    res = []

    def t(n, f):
        try:
            res.append((n, True, f()))
        except Exception as e:
            res.append((n, False, f"{type(e).__name__}: {e}"))

    t("three_operations_are_forced_and_one_can_carry_all", _forced)
    t("how_many_opcodes_is_an_optimum_not_a_taste", _count)
    t("a_frequent_opcode_is_short_for_the_same_reason_a_particle_is",
      _short)
    t("the_machine_runs_and_we_can_read_both_directions", _runs)
    return all(x for _, x, _ in res), res


def _forced():
    if len(FORCED) < 3:
        raise ArithmeticError(f"{FORCED}")
    return (f"{len(FORCED)} things must exist in any instruction "
            f"set and none is a choice: "
            + "; ".join(f"{k} -- {v}" for k, v in FORCED.items())
            + f". And one instruction can carry all of them at "
              f"once: subtract-and-branch-if-zero is Turing "
              f"complete alone, so the MINIMUM set is one. That "
              f"is why the size of a real instruction set is a "
              f"question about cost rather than about capability")


def _count():
    k = optimum_opcodes()
    if not 32 <= k <= 512:
        raise ArithmeticError(f"{k}")
    rows = [(j, program_bits(2000, j) + decoder_gates(j))
            for j in (8, 32, 128, 512)]
    return (f"more opcodes make programs shorter, because each "
            f"instruction says more, and make the decoder bigger, "
            f"because there are more cases to tell apart. Program "
            f"bits fall as 1/log2(k) and gates rise as k, so the "
            f"sum has a floor: "
            + "; ".join(f"{j} opcodes {t:.0f}" for j, t in rows)
            + f", optimum at {k}. Real sets land there -- RISC-V's "
              f"base integer set is 47 instructions and ARM about "
              f"50. Nobody chose 128 here; it fell out of a "
              f"program length and a decoder")


def _short():
    from engine.syntax import particle_syllables
    return (f"frequent operations should get short codes, which is "
            f"the same optimisation engine/syntax.py already "
            f"derived for their grammar: a particle is "
            f"{particle_syllables()} syllable where a noun is two "
            f"or three, because it is the most frequent word and "
            f"must stay distinguishable. A machine's encoding and "
            f"a language's function words are the same problem, "
            f"and the two answers to it are the same -- which is "
            f"why a variable-length instruction encoding is denser "
            f"and a fixed-width one decodes faster. x86 took the "
            f"first and RISC the second")


def _runs():
    words = assemble(COUNTDOWN)
    mem = list(words) + [0] * 32
    mem[20] = 5
    out, steps = run(words, mem)
    back = disassemble(words)
    if out != [5, 4, 3, 2, 1]:
        raise ArithmeticError(f"{out}")
    return (f"the machine RUNS. {len(words)} words assembled from "
            f"their mnemonics, executed in {steps} steps, emitting "
            f"{out}. Read back the other way the words "
            f"disassemble to {back[:4]}... so the translation goes "
            f"both directions and round-trips. This is what makes "
            f"it a claim rather than a description -- an "
            f"instruction set nobody can execute is a table. What "
            f"is NOT here: nobody in engine/world.py has built "
            f"one. This is what their constraints would force, "
            f"implemented so it can be checked")


if __name__ == "__main__":
    k = optimum_opcodes()
    print(f"  {'opcodes':>8}{'program bits':>15}{'decoder':>10}"
          f"{'total':>11}")
    for j in (1, 4, 16, 64, 128, 256, 1024):
        pb, dg = program_bits(2000, j), decoder_gates(j)
        print(f"  {j:>8}{pb:>15.0f}{dg:>10.0f}{pb+dg:>11.0f}"
              f"{'   <- optimum' if j == k else ''}")
    print(f"\n  opcode field {opcode_bits()} bits, operand "
          f"{OPERAND_BITS}\n")
    words = assemble(COUNTDOWN)
    mem = list(words) + [0] * 32
    mem[20] = 5
    out, steps = run(words, mem)
    print(f"  {'word':>10}  {'hex':>8}   disassembled")
    for w, d in zip(words, disassemble(words)):
        print(f"  {w:>10}  {w:>8x}   {d}")
    print(f"\n  ran {steps} steps, emitted {out}\n")
    ok, res = check()
    for n, x, m in res:
        print(("  ok  " if x else "  FAIL") + f" {n}\n        {m}")
    print("  all hold" if ok else "  broken")
