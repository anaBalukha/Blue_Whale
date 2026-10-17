# HW1 - Structured Conversation Drift Checker

## Goal and users
Help students and developers catch contradictions in AI-assisted projects.
The feature checks proposed decisions against confirmed conversation state.

## Run and verify
Run: python hw1/anaBalukha/src/drift_checker.py '{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}'
Test: python -m pytest -q hw1/anaBalukha

## Context and inputs
Input is a JSON object containing:
- state: confirmed decisions as string key-value pairs.
- candidate: decisions proposed by the AI.
- user_changes: optional explicit changes from the user.

Explicit user changes override older confirmed decisions.

## Acceptance criteria
1. A conflicting candidate without user permission returns status "drift" and identifies the conflicting field, expected value, and proposed value.
2. An explicit user change updates the effective state and is not classified as drift.
3. Matching decisions return status "consistent" with no conflicts.
4. Invalid input returns a structured INVALID_INPUT error and a nonzero CLI exit code.

## Success criteria
- All acceptance criteria have automated tests.
- At least three golden examples are executed and documented.
- No real model calls or API credentials are needed for tests.

## Cost and latency
This feature uses deterministic Python comparisons without an LLM.
Direct model-token cost is $0 per check. Runtime will be measured during testing.

## Risks
- Incorrect structured input may produce misleading results.
- Unstructured conversation text is not interpreted automatically.
- Invalid input must fail visibly rather than silently succeeding.

## Out of scope
Natural-language extraction, automatic recovery, web UI,
persistent storage, and live OpenRouter calls.
