# Cold email — draft

Subject lines, pick one:

- `25 labelled faults from a scientific codebase, incl. 7 in the test apparatus`
- `Does anyone have data on what actually catches errors in scientific code?`
- `A fault corpus with catching-mechanism annotations — is this useful to anyone?`

---

Dear Professor ——,

I'm an independent developer, not affiliated with a university, and I
have data I can't evaluate on my own.

Over eight months I built a 33,600-line scientific codebase under a
rule that every result carries a check that would catch it being
wrong. In the process I recorded **25 faults, each annotated in-source
with its cause and with the mechanism that caught it.** The
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
