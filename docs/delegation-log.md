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
