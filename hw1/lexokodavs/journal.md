# Pattern Journal · lexokodavs · Weeks 1 to 4

*The original HW1 journal (2026-10-20) had only a one-line Week 1 entry. The entries below were written on **2026-11-24** as a retrospective correction. Each one points to a real file, PR or check rather than to memory of the lecture.*

## Week 1 · Context as Budget (written 2026-11-24)

**Where I used it:** in PR #12 (merged 2026-10-20) I added the project rules to `AGENTS.md`. The goal was for an agent to start from a short, fixed set of rules ("Read docs/spec.md before implementing", "Preserve the latest explicit user instruction") instead of a long chat history. My HW1 builder follows the same idea at small scale: its whole context is one JSON argument, and `spec.md` §2 lists that as the only thing it reads. **Do differently:** add a context list to the spec on day one. My October spec had none, and I only added it during this correction.

## Week 2 · Spec Before Code (written 2026-11-24)

**Where I used it:** I wrote `spec.md` with four acceptance criteria before the builder was drafted (`ff23cdf`, 2026-10-20). **What went wrong:** the spec and code still drifted apart. The spec said `user_changes` held "`decisions` updates", but the code takes a flat map, and nobody noticed until I ran the nested payload on 2026-11-24 and it was refused. **Do differently:** put one concrete example payload in the spec and run that exact payload in a test, so the example cannot fall out of date.

## Week 3 · Uncertainty-Aware UX (written 2026-11-24)

**Where I used it:** in PR #13 (Lab 3) I wrote `docs/confidence-policy.md`. Its routes are `rejected`, `review`, `confirm` and `accepted`, and anything below 0.6 confidence goes to `confirm`, which "requires user confirmation before committing state". The builder applies the same rule to bad input: it does not guess at an invalid payload. It refuses with `INVALID_INPUT` and exit code 2 and prints no checkpoint. **Do differently:** refuse unknown fields from the start. Until 2026-11-24 the builder silently ignored `"authorized": true`, which is the opposite of an uncertainty-aware answer.

## Week 4 · Grounded Generation (written 2026-11-24)

**Where I saw it:** on 2026-11-24 I ran the team's offline RAG golden set (`python -m evals.run_golden --k 5`). The result was 5/5, including `g5 refusal`: "Which cloud provider will host Blue Whale in production?" is refused because no trusted document says so, rather than answered with a guess. My builder applies the same idea to state: a checkpoint value may only come from `previous` or `user_changes`, never from something the code infers. **Do differently:** write the "no evidence → refuse" case as the first golden question, as the team set does, instead of adding it last.
