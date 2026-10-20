# Decision 002 - Explicit User Changes Take Priority

Status: Accepted

## Context
Blue Whale must detect when an AI contradicts previously established requirements.
However, users must remain free to intentionally change those requirements.

## Decision
An explicit user-approved change supersedes the corresponding earlier decision.
Changes introduced only by the AI are treated as potential conversation drift.
Ambiguous changes require user confirmation.

## Reason
This prevents Blue Whale from incorrectly rejecting legitimate changes while still detecting AI mistakes.

## Consequences
The application must distinguish explicit changes from unintended contradictions.
The original and updated decisions should remain traceable.

## Evidence
See docs/spec.md and hw1/anaBalukha/src/drift_checker.py.
The individual HW1 prototype demonstrates this rule; team-level integration remains pending.
