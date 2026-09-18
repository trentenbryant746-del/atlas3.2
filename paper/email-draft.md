# Cold email — draft

Subject lines, pick one:

- `25 labelled faults from a scientific codebase, incl. 7 in the test apparatus`
- `Does anyone have data on what actually catches errors in scientific code?`
- `A fault corpus with catching-mechanism annotations — is this useful to anyone?`

---

Dear Professor ——,

I'm an independent developer, not affiliated with a university, and I
have data I can't evaluate on my own.

I built a scientific codebase under one rule: every result carries a
check that would catch it being wrong. Working that way produced
something I did not set out to make — **25 faults, each annotated
in-source with its cause and with the mechanism that caught it.** The
distribution is not what I expected:

    deriving something previously asserted        7
    faults in the verification machinery itself   7
    an automated check fired                      6
    comparison against an external known value    4
    cross-referencing an earlier release          1

Two things surprised me. **Tests caught only 6 of 25.** The largest
category required re-deriving a quantity that had been typed in — work
no test suite performs, because the code was self-consistent and
everything passed. And **the checking apparatus failed at roughly the
same rate as the code it checks**, 7 against 18, which I have not seen
quantified anywhere.

The reason I have this data at all is a convention rather than a tool:
when a check's premise turns out false, the check is **flipped and
kept** with its history rather than deleted. Nine checks currently
record what they used to assert and why that was wrong. Deleting them
is the normal thing to do, and it would have erased nine data points.

My question is whether a fault corpus annotated by *catching
mechanism* is useful to anyone. Defects4J and BugSwarm are mined from
version control after the fact, which gives the fix but rarely the
cause and almost never what surfaced it. If this already exists I'd be
glad to be pointed at it.

Six pages attached. The corpus itself is a separate file and is the
part worth reading; §3.2, the faults in my own verification, is the
section I'd want a reviewer on.

No reply needed if it's not interesting.

Thank you,
Trenten Bryant
`github.com/trentenbryant746-del/atlas3.1`

---

## Notes on sending

**Who.** Empirical software engineering, research software engineering,
software testing, mining software repositories. People who build fault
corpora or study scientific-software quality. Secondarily, provenance
and reproducibility researchers.

**Not** domain scientists — not yet. The physics is the substrate, not
the claim; 47 of 135 inputs are values I picked, and a domain expert
would rightly review the science instead of the method.

**Lead with the corpus and the distribution.** That is the part nobody
else has. The verification infrastructure is a means of production for
it, and leading with the speed number invites "you reimplemented
Bazel," which is fair and which the paper concedes.

**Do not** lead with 33,600 lines, 5,737 curriculum items, or the
physics. Size is not a virtue, the curriculum is self-generated so its
0-wrong rate is consistency rather than accuracy, and the physics is
unreviewed.

**Attach `LOG.md`, not only the paper.** The corpus is the artifact.
The paper is an argument about the corpus.

**Expect three responses.** (i) "This exists, see X" — the best
outcome, take it. (ii) "n=1, from your own codebase" — correct, and
§8.1 concedes it; the reply is that n=1 with mechanism annotations may
still be worth more than n=400 without. (iii) Silence, which is the
base rate for cold email and means nothing.

---

## On eventually emailing physicists

The instinct that a CS reader might forward it is right, and a warm
internal referral is worth far more than a second cold email. But it
only happens if the CS email lands on its own terms. **The CS email
cannot be a Trojan horse for the physics** — if it reads as one, it
fails twice.

**What a physicist could be shown, and when.** Of 48 graded claims,
**28 rest on no `CHOSEN` input** — they are derived from measured or
exact quantities only. That subset is what could survive a domain
reviewer:

    the habitable band 0.999-1.899 AU
    Earth composition Fe 32.0%
    the 57-residue search ceiling
    the eye sits at its own diffraction limit
    steam caps at 54.7% whatever it is made of
    muscle for a 400 N blow is 53 cm2

The other 20 rest on values I picked. Showing those to a physicist
invites a review of the inputs rather than the method, and they would
be right to give it.

**The physics angle that might actually interest a physicist is not a
result — it is the grading.** A system that refuses to cite a
`CHOSEN`-backed number as derived, applied to planetary science, is a
methods proposition. The interesting sentence is not "the habitable
band is 0.999–1.899 AU," which they can compute; it is "this number is
machine-certified to rest on nothing anybody guessed, and here are the
20 sibling results that are not."

**Sequence.** Send CS first and wait. If a CS reader engages, ask
*them* whether the grading idea is worth putting to a domain person —
they will know who, and the introduction will carry weight the cold
version cannot. If CS goes silent, that is information about the
framing, and the physics email should not be sent on the same framing
until it is fixed.
