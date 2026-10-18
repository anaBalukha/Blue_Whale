# Decision 001 - Terminal-first MVP

Status: Accepted

## Context
Blue Whale needs a simple interface to test conversation drift detection and recovery.

## Decision
Build a terminal application before introducing a web interface.

## Reason
A terminal application is simpler to implement, debug, and test.

## Consequences
The MVP will use command-line interaction. A web interface is deferred.

## Evidence
See docs/spec.md and hw1/anaBalukha/src/drift_checker.py.
