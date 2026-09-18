# Cold email — draft

Subject lines, pick one:

- `Fingerprint-gated verification of published claims — is this a solved problem?`
- `Short question: claim-granularity staleness detection (6pp, with fault injection)`
- `Asking whether I've reinvented Bazel`

---

Dear Professor ——,

I'm an independent developer, not affiliated with a university. I've
built something I can't evaluate on my own and I'd value ten minutes of
your judgement — specifically on whether it is already a solved
problem.

The system is a scientific codebase (33k lines, no dependencies) that
publishes 47 numbered results. Each result's re-verification is gated
on a content-addressed fingerprint of its transitive dependencies,
recovered from the AST rather than declared. An unchanged fingerprint
is a proof the answer cannot have moved, so verification drops from
70.9 s to 0.0 s. I tested soundness by fault injection rather than
assuming it: four injected faults, all four caught, each recomputing
only its dependent subset; three irrelevant edits, zero spurious
recomputes.

The part I'm least sure about is a by-product. The depth of a claim's
dependency graph turns out to separate results the rules *derive* from
results that are arithmetic over a constant wearing the shape of a
derivation. It caught one real case in my own code. One case is an
anecdote.

**My honest question is whether the claim-granularity framing adds
anything over Nix, Bazel, DVC or Snakemake.** I haven't run that
comparison and I'd rather be told it's unnecessary than keep going.

Six pages attached, including a section listing what the system got
wrong — fourteen withdrawn results, nine checks that had to be inverted
when their premise turned out false, and a unit error that was off by a
factor of a million. That section is the one I'd read first.

No reply needed if it's not interesting.

Thank you,
Trenten Bryant
`github.com/trentenbryant746-del/atlas3.1`

---

## Notes on sending

**Who.** Software engineering / programming languages / research
software engineering. People who work on build systems, provenance,
reproducibility, or scientific-software quality. Not systems-biology or
astronomy people — the domain content is the substrate, not the claim,
and sending it to a domain expert invites them to review physics I am
not defending.

**Do not** lead with the physics, the scale of the codebase, or the
5,737-item curriculum. The first is unreviewed, the second is not a
virtue, and the third is self-generated and proves consistency rather
than accuracy.

**Do** lead with the falsifiable part: fault injection, the benchmark,
and the list of errors. A cold email that volunteers its own failures
reads differently from one that does not.

**Expect** "this is Bazel." That is a legitimate answer and §8.2 of the
paper already concedes the comparison has not been run. If two people
say it independently, run the comparison before writing to anyone else.
