# Lab 5 Shared Team Tool — Verification Evidence

Date: November 28, 2026

Issue: #57

Implementation driver: Ana Balukhashvili (@anaBalukha).

## Purpose

The shared answer_from_trusted_sources tool is separate
from the three individual HW2 tools.

It wraps the existing Lab 4 retrieval and grounded answer
pipeline rather than introducing another grounding system.

## Contract-first development

The tool contract was committed before implementation:

- Contract commit: 101bd29.
- Contract: docs/tool-contracts.md.
- Strict bounded arguments.
- Read-only access.
- No caller identity or authorization arguments.
- Citation validation cannot be disabled by the caller.

## Test-first evidence

Before implementing the tool:

- 17 tests failed in 1.06 seconds.
- Pytest exit code: 1.
- No test collection errors.
- The expected failure was that the tool was not registered.

After implementing the tool:

- The same 17 tests passed in 1.03 seconds.
- Shared regression suite: 173/173 passed.
- No existing tests were weakened.

An unnecessary trailing blank line in src/contracts.py
was caught by git diff --check and removed.

## Golden cases

| Case | Expected | Actual |
|---|---|---|
| team-g1 | Grounded MVP interface answer | PASS |
| team-g2 | Grounded drift accuracy answer | PASS |
| team-g3 | Safe insufficient-evidence refusal | PASS |
| team-g4 | Reject excessive retrieval limit | PASS |
| team-g5 | Reject forged caller identity | PASS |

Team golden cases: 5/5 passed.

All tool golden cases: 20/20 passed.

Golden coverage validation: passed.

## Full regression

- Shared product suite: 178/178 passed in 1.65 seconds.
- Offline index: 23 chunks.
- Offline RAG goldens: 5/5 passed.
- RAG configuration: k=5, minimum score 0.30.
- Git whitespace validation: passed.

All three individual HW2 tools remain operational.

## Reproduction

Use Python 3.11 or newer with requirements.txt installed.

    BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m pytest -q tests/test_team_answer_tool.py

    BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m pytest -v tests/test_tool_golden.py

    BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m pytest -q tests

## Limitations

All results above were measured offline.

The MCP integration tests use the actual SDK client with
an in-process server.

External MCP host verification of this fourth tool and
live model-driven execution have not yet been performed.

Offline results do not establish real-model answer quality.

Citation validation checks citation structure and source
references rather than semantic entailment.

Live execution can incur embedding and additional
generation costs. The nested model usage is logged by
the existing model gateway, but is not necessarily
included in the outer streaming response's cost summary.

The existing answer diagnostics can record question text.
Only synthetic, non-sensitive inputs should be used
in demonstration evidence.

No persistent conversation state is modified.
