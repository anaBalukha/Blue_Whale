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
