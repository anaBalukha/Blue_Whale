# Blue Whale — Team AI Delegation Log

## Entry 1 — Lab 4 retrieval and grounding

**Task:** Implement document indexing, hybrid retrieval, citation
validation, refusal handling, offline tests and golden evaluations.

**Delegated to:** ChatGPT (GPT-6), Autonomy Ladder rung 3.
The implementation was adapted from the professor's Lab 4
CampusPulse RAG reference to the Blue Whale project.

**Context provided:** Blue Whale's project specification,
three approved project documents, five golden questions
and the professor's RAG reference.

**Plan check:** The team selected the project corpus, offline
testing approach and golden cases. A dated record of formal
pre-code plan approval was not retained; this is a process gap.

**What came back wrong:** An attempted distinct-document retrieval
improvement introduced incorrect indentation in src/retrieve.py,
causing a Python SyntaxError. After correction, the reasoning
golden case g3 still failed to cite both required documents.

**Caught by:** Running python -m compileall, pytest and the
offline golden evaluation. The initial strict-threshold offline
baseline passed 1/5 cases. The later run with an experimental
0.30 score threshold passed 4/5. Case g3 remained a failure.

**Decision:** Fix the syntax error and retain the working
implementation with the known g3 limitation explicitly
documented. PR #9 was reviewed and merged with green CI.

**Human verification:** Mikheili ran the code and tests.
Ana reviewed and approved the team feature PR.

**AGENTS.md:** Existing grounding and no-weakening-goldens
rules were retained; no additional change is claimed here.

**Time spent:** Not measured reliably.

**Additional live-model evidence:** Ten real OpenRouter
chat calls were recorded in logs/usage.jsonl through PR #14.
Seven produced successfully parsed JSON responses; three
produced parsing errors. These were chat-only calls and
must not be represented as a complete live RAG evaluation.

## Follow-up

- Make document-diverse retrieval pass golden case g3.
- Run the complete golden set with real model calls.
- Record actual embeddings and full RAG request usage.
- Keep the failing baseline as evidence rather than removing it.


## Entry 2 — HW2 Tool Contract and MCP — 8 November 2026

**Owner:** Mikheili Kakhniashvili, Eval Keeper.

**Delegated to:** ChatGPT (GPT-6), Autonomy Ladder rung 3.

**Task:** Implement trusted-source retrieval, strict tool contracts,
MCP integration, supervised tool calling, and offline golden tests.

**What went wrong:** The original MCP implementation accepted
unexpected fields. One golden case also confused retrieval with
answer generation.

**Verification:** I ran tests, investigated both failures, and
corrected the implementation. The final version passed 40 tests.

**Red CI experiment:** I deliberately changed extra="forbid" to
extra="ignore". Four tests failed. GitHub Actions detected the
regression and branch protection blocked merging.

**Human review:** Ana approved and merged product PR #20.
Write-up PR #22 was separately reviewed and merged.
The deliberately failing PR #21 was closed without merging.

**Limitation:** No live model call was tested because an
OpenRouter API key was unavailable.

**Next time:** Test the MCP validation boundary earlier.

## Entry 3 — Ana HW2 Drift Tool — 8 November 2026

**Owner:** Ana Balukhashvili, Repo Keeper.

**Delegated to:** ChatGPT (GPT-6), Autonomy Ladder rung 3.

**Task:** Wrap the existing `src/drift_core.py` comparison
function as a read-only, validated model-callable tool.
Integrate it with the existing function-calling registry
and MCP server.

**Scope:** Ana's new tool, strict input contract, MCP
registration, five golden cases, unit tests, and
repository contract documentation.

**What went wrong:** The initial generated integration
script failed at an assertion while trying to update
the assistant's system prompt. The source and MCP
registration had already been written successfully.

**Correction:** I repaired the prompt integration without
repeating the earlier file-generation commands.

**Environment issue:** The first test attempt used system
Python without pytest. Activating the project's virtual
environment resolved this.

**Verification:** Six direct-tool tests, three MCP tests,
eleven tool-golden checks, and the full 63-test project
suite passed locally. Ana's four HW1 tests also passed.

**Security:** The tool refuses model-supplied
`user_changes`. It compares supplied prior decisions but
cannot independently authenticate their origin.
The caller must supply genuinely trusted state.

**Limitations:** No live-model tool invocation or external
MCP-host demonstration is claimed. GitHub CI and teammate
review are still required.

**Next time:** Inspect exact integration anchors before
running automated edits, and verify the active Python
environment before testing.

**Time spent:** Not measured reliably.


## Structured drift benchmark — Issue #31

**Date:** 2026-11-24

**Owner:** Mikheili Kakhniashvili, Eval Keeper.

**Delegated to:** ChatGPT, Autonomy Ladder rung 3.

**Task:** Create a reproducible structured drift benchmark,
evaluation runner, regression tests and updated evaluation
documentation.

**Context:** Blue Whale's specification, existing drift checker,
Design Review accuracy target and GitHub issue #31.

**Plan:** Use 50 synthetic cases across five categories.
Specify expected labels separately from the function under test.
Measure classification accuracy and exact conflict fields.

**What went wrong:** The initial execution used system Python
instead of the project's virtual environment. The benchmark
ran successfully, but pytest and Pydantic were unavailable.
The documentation corrections therefore did not execute.

**Correction:** Activate the existing virtual environment and
repeat verification and documentation updates.

**Measured result:**

- Cases: 50.
- Correct classifications: 50.
- Accuracy: 100.0%.
- Exact case pass rate: 100.0%.
- Accuracy target: 85.0%.
- False positives: 0.
- False negatives: 0.

**Evidence:** evals/results/drift-structured-baseline.json

**Limitations:** The cases are synthetic, with expected labels
specified separately from the checker. They are not an
independent sample of real conversations. The benchmark
does not establish natural-language extraction accuracy,
authorization correctness, recovery success or consistency.

**Human review:** Teammate review and merge are pending.

**Next time:** Verify the Python environment before starting
a multi-stage implementation.

## Streaming and application interface - Issue #33

Date: 2026-11-24

Owner: Ana Balukhashvili, Repo Keeper.

Delegated to: ChatGPT, Autonomy Ladder rung 3.

Task: Implement the streaming gateway, bounded streamed
conversation, HTTP endpoints and offline tests.

Context: Lab 5 and Lab 6 requirements and the existing
Blue Whale tool executor and model gateway.

What went wrong: The initial implementation omitted
the streaming gateway. Test collection failed because
stream() could not be imported. The MCP server was
initially sought in the wrong VS Code workspace.

Correction: Install the missing gateway and open
the Blue Whale workspace explicitly.

Verification: Six new tests passed. All 74 project
tests passed. Both external MCP demonstrations succeeded.
The offline stream produced multiple fragments and
one usage entry containing TTFT.

Evidence: docs/streaming-evidence.md.

Limitations: Live model execution, persistent memory
and consequential-action confirmation remain pending.

Next time: Verify module imports and workspace configuration
before running integration tests.

Teammate review: pending.
## Entry 4 — Leqso HW2 `preview_checkpoint_update` — 24 November 2026

**Owner:** Aleksandre Giorgashvili (@lexokodavs), Spec Keeper.

**Delegated to:** Autonomy Ladder rung 3. Which assistant, if any, drafted the first version of PR #35 (commit `84a434e`, whose message records "5 failures -> 85 passed" while fixing tests) was not recorded. The hardening pass (commit `6fc047e`) was done with Claude Code (Claude Opus 5.5).

**Task:** Wrap the HW1 checkpoint merge as a read-only tool that previews the next versioned checkpoint, registered for function calling and MCP, with five golden cases.

**Plan check:** The hardening plan was written up and approved by me before any implementation file was edited.

**What went wrong:**
- `previous_version` had no upper bound: `10**30` was accepted.
- 8 + 8 decisions produced a 16-decision checkpoint that the tool itself refuses as input.
- The MCP function declared `previous_version: int`, so the MCP door advertised no bounds.
- The first test that compared the two doors compared a schema with itself.
- The adversarial golden used a meaningless `invalid_extra_field`.

**Caught by:** Calling `call_tool()` with out-of-range inputs by hand. A new test comparing the bounds and patterns the two doors actually advertise failed on the MCP schema.

**Correction:** Version bounded to 0..1000000; oversized merges and version overflow refused with model-actionable messages; MCP signature reuses the `CheckpointVersion` type; golden a1 injects `authorized: true`.

**Evidence Rule:**
- **Test:** `tests/test_lexo_checkpoint_tool.py::test_forged_identity_or_approval_never_runs` and golden `lexokodavs` a1 fail if `extra="forbid"` is removed.
- **Log entry:** every call writes one line to `logs/tools.jsonl` (`tool`, `ok`, `error`, `caller_type`, `latency_ms`; no decision values).

**Red CI experiment:** `extra="forbid"` → `extra="ignore"` on a throwaway branch, PR #37. Seven tests failed in run 45453240515. The required `test` check blocked the merge. PR closed unmerged and branch deleted.

**Human review:** Product PR #35 approved by @mishakakhniashvili and merged. Write-up PR #36 merged.

**Verification:** 110 tests passed locally and in CI on `main`.

**Limitations:** Offline only; no live-model tool call. The tool previews; nothing commits a confirmed checkpoint yet.

**Time spent:** Not measured reliably.

## Entry 5 — Leqso HW1 post-grading corrections — 24 November 2026

**Owner:** Aleksandre Giorgashvili (@lexokodavs).

**Delegated to:** Claude Code (Claude Opus 5.5), Autonomy Ladder rung 3, after I approved the plan. The original October build agent is unknown and is recorded as such in `hw1/lexokodavs/delegation.md`.

**What went wrong:**
- Merge-conflict markers had been left in `hw1/lexokodavs/spec.md` by merge `f6f4cdf`.
- The spec described a nested `user_changes` shape that the code refuses.
- The builder silently ignored unknown fields such as `"authorized": true`.
- The tests only passed from the repository root.

**Caught by:** Reading the file on `main`; running the nested and `authorized` payloads; running pytest from another folder (4 failed).

**Correction and verification:** PR #38. The builder now refuses unknown fields. Against the old code the two new tests fail; with the fix all 14 HW1 tests pass, from any folder.

**Limitation:** HW1 tests are not part of CI (`pytest -q tests`); they are run explicitly.

## Independent streaming evaluation - Issue #42

Date: 2026-11-24

Owner: Mikheili Kakhniashvili, Eval Keeper.

Delegated to: ChatGPT, Autonomy Ladder rung 3.

Task: Write independent streaming regression tests and
verify incremental HTTP delivery through a local server.

Context: Lab 6, PR #41, the existing tool safety gates
and the streaming interface contract.

Verification: Eight independent tests passed.
The full suite passed 124 tests.
Real local HTTP delivery was verified using a controlled
offline model stream. The first token reached the client
before the simulated model was allowed to finish.

Evidence: docs/streaming-eval.md and
evals/results/stream-transport-offline.json.

Limitations: No live provider requests were made.

Next time: Verify streaming over an actual HTTP connection
in addition to using an in-process HTTP test client.

Human review: pending.

## Citation validation correction - Issue #46

Date: 2026-11-28

Owner: Mikheili Kakhniashvili, Eval Keeper.

Delegated to: ChatGPT, Autonomy Ladder rung 3.

Task: Reproduce and repair citation validation defects
identified during the independent repository audit.

Context: Lab 4 grounding requirements and the existing
retrieval pipeline, citation checker and offline generator.

What went wrong: Uncited sentences could pass validation
because the original sentence splitter was too restrictive.
The first correction also accepted citation-only answers
and missed some unspaced sentence boundaries.

Correction: Introduce conservative sentence parsing,
require citations at sentence ends and reject citation-only
answers. Update the offline generator accordingly.

Verification: Two rounds of regression testing reproduced
four failures each. After correction, all 15 citation
tests and all 139 project tests passed.

All seven Misha HW1 tests and all five offline RAG golden
cases also passed.

Evidence: docs/citation-validation-evidence.md and
evals/results/2026-11-28-0401-offline-k5.json.

Limitations: Citation placement is verified, not semantic
support. No live model requests were made.

Next time: Test citation association using lowercase
sentences, newline boundaries and malformed formatting
before accepting the implementation.

Human review: pending.

## MCP protocol boundary correction - Issue #48

Date: 2026-11-28

Contributor: Mikheili Kakhniashvili

Delegated to: ChatGPT, Autonomy Ladder rung 3.

Task: Correct MCP validation bypass, unsafe validation
errors, missing audit records and shared schema mismatch.

Context: Lab 5 tool contracts, HW2 and the independent
repository audit.

What went wrong: SDK argument validation could reject
requests before the shared application gate executed.
Published schemas did not fully describe runtime rules.

Correction: Route MCP execution through the shared strict
gate and publish the same input schema through both
interfaces. Add the missing decision-key schema restriction.

Verification: The initial diagnostic checked 13 requests
and reproduced defects in ten cases.

The regression suite initially produced 13 failures
and three passes.

After correction, all 16 new protocol tests, all 16
existing MCP tests and all 155 project tests passed.

All five offline RAG golden cases also passed.

Evidence: docs/mcp-boundary-evidence.md,
tests/test_mcp_protocol_boundary.py and
evals/results/2026-11-28-0419-offline-k5.json.

Limitations: In-memory MCP transport verification.
No live model requests were made.

Next time: Verify the actual protocol boundary,
sanitized errors, audit count and complete published
schemas instead of checking rejection alone.

Human review: pending.

## README reproducibility correction - Issue #54

Date: 2026-11-28

Owner: Ana Balukhashvili, Repo Keeper.

Delegated to: ChatGPT, Autonomy Ladder rung 3.

Task: Correct outdated setup instructions, implementation
status and evaluation references in the README.

Context: Existing application, CI configuration, shared
tool contracts and recorded regression evidence.

Correction: Document reproducible offline commands,
all three read-only tools, HTTP and SSE interfaces,
and unfinished product requirements.

The original Design Review was preserved and labeled
as a historical snapshot.

What went wrong: The initial clean-tree verification
produced 17 test collection errors because the local
virtual environment lacked required dependencies.

Resolution: Explicitly select the repository's Python
executable and install dependencies from requirements.txt.

All dependency imports passed and pip check reported
no broken requirements.

Final verification in a clean copy of the tracked tree:

- Shared product tests: 155/155 passed.
- Offline index: 23 chunks.
- Offline RAG goldens: 5/5 passed.
- Git whitespace validation: passed.

Limitations: The verification reused an existing virtual
environment after installing its missing dependencies.
It was not a completely new virtual environment.

No product code, dependency requirements or CI
configuration changed.

No live model requests were made.

Next time: Verify the Python executable and dependency
imports before starting clean-tree regression tests.

Human review: pending.
