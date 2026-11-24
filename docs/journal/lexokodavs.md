# Pattern Journal · Aleksandre Giorgashvili (lexokodavs)

*Ongoing journal. One entry per teaching week: the pattern, one place I saw or used it, one thing I would do differently.*
*Weeks 1–4 are copied into `hw1/lexokodavs/journal.md` and Weeks 5–7 into `hw2/lexokodavs/journal.md`.*
*All entries were written or rewritten on 2026-11-24. The earlier version of this file (Weeks 1–4) was a generic retrospective; it was replaced by entries tied to real files and tests. Each entry is dated with when it was actually written.*

## Week 1 · Context as Budget (written 2026-11-24)

**Where I used it:** in PR #12 (merged 2026-10-20) I added the project rules to `AGENTS.md`. The goal was for an agent to start from a short, fixed set of rules ("Read docs/spec.md before implementing", "Preserve the latest explicit user instruction") instead of a long chat history. My HW1 builder follows the same idea at small scale: its whole context is one JSON argument, and `spec.md` §2 lists that as the only thing it reads. **Do differently:** add a context list to the spec on day one. My October spec had none, and I only added it during this correction.

## Week 2 · Spec Before Code (written 2026-11-24)

**Where I used it:** I wrote `spec.md` with four acceptance criteria before the builder was drafted (`ff23cdf`, 2026-10-20). **What went wrong:** the spec and code still drifted apart. The spec said `user_changes` held "`decisions` updates", but the code takes a flat map, and nobody noticed until I ran the nested payload on 2026-11-24 and it was refused. **Do differently:** put one concrete example payload in the spec and run that exact payload in a test, so the example cannot fall out of date.

## Week 3 · Uncertainty-Aware UX (written 2026-11-24)

**Where I used it:** in PR #13 (Lab 3) I wrote `docs/confidence-policy.md`. Its routes are `rejected`, `review`, `confirm` and `accepted`, and anything below 0.6 confidence goes to `confirm`, which "requires user confirmation before committing state". The builder applies the same rule to bad input: it does not guess at an invalid payload. It refuses with `INVALID_INPUT` and exit code 2 and prints no checkpoint. **Do differently:** refuse unknown fields from the start. Until 2026-11-24 the builder silently ignored `"authorized": true`, which is the opposite of an uncertainty-aware answer.

## Week 4 · Grounded Generation (written 2026-11-24)

**Where I saw it:** on 2026-11-24 I ran the team's offline RAG golden set (`python -m evals.run_golden --k 5`). The result was 5/5, including `g5 refusal`: "Which cloud provider will host Blue Whale in production?" is refused because no trusted document says so, rather than answered with a guess. My builder applies the same idea to state: a checkpoint value may only come from `previous` or `user_changes`, never from something the code infers. **Do differently:** write the "no evidence → refuse" case as the first golden question, as the team set does, instead of adding it last.

## Week 5 · Tool Contract (written 2026-11-24)

**Where I used it:** I wrapped my HW1 checkpoint merge as `preview_checkpoint_update`, with the contract `PreviewCheckpointUpdateArgs` (`extra="forbid"`, shared `DecisionMap` patterns). I delegated the hardening pass to an AI coding agent (Claude Code). **What came back wrong / what I noticed:** my first version had no upper bound on `previous_version` (`10**30` was accepted). The MCP function also declared `previous_version: int`, so the MCP door advertised no bounds even after I added them to the contract. Neither showed up while the tests only checked parameter *names*. The agent's first version of the constraint test also read the wrong schema key (`additionalProperties` instead of `patternProperties`) and failed. I printed both schemas to see the real shape before fixing it. **Do differently:** write the "both doors advertise the same constraints" test before the tool, comparing bounds and patterns, not names.

## Week 6 · Session State (written 2026-11-24)

**Where I used it:** I checked where Blue Whale's state lives today. `act()` rebuilds `messages` on every call, and there is no checkpoint store yet. The trusted checkpoint therefore has to come from the application, never from the model's memory of the conversation. My test `test_preview_is_idempotent_and_persists_nothing` calls the tool twice with the same arguments. Both previews are version 5, and the only file created is the audit log, so the tool holds no hidden state. **The state row I would propose to the team:** `checkpoint` (version + decisions), scope: one conversation, written only by a user-confirmed commit, never by a tool result or an AI summary. This is a proposal, not yet an agreed team contract. **Do differently:** agree the state contract row with the team before Lab 6 code, so my preview's input shape and the store's shape are the same type.

## Week 7 · Supervised Autonomy Loop (written 2026-11-24)

**Where I used it:** I marked my tool as read in `contract.md`. Because it writes nothing, a loop may call it repeatedly. **The one action that must wait for a yes:** committing a previewed checkpoint into trusted state. The real test is `test_forged_identity_or_approval_never_runs`, which sends `authorized: true`, `user_approved: true`, `caller_id` and `commit: true` through `call_tool()`. All four are refused, and a spy proves the tool body never ran. Golden a1 runs the same `authorized: true` case in CI. **What I corrected:** my first draft of this entry said the preview "must never execute inside the autonomous loop". That was wrong: the read-only preview is safe in the loop, and only the commit has to be parked for confirmation. **Do differently:** when the commit capability is built, add stale-version protection (commit only if the stored version still equals `previous_version`).
