# HW1 - Golden Test Evaluation Reporter

## Goal
Build a Python CLI tool that evaluates expected versus actual test
outcomes, calculates a pass rate, and identifies failed test cases.

## Users
QA engineers and developers evaluating AI-powered applications.

## Input
A JSON object containing:
- cases: a non-empty list of test cases
- threshold: optional minimum pass rate, default 0.70

Each case has a unique id, expected status, and actual status.
Supported statuses are "answered" and "refused".

## Output
JSON containing total, passed, pass_rate, meets_threshold,
and failed_ids.

## Acceptance criteria
- AC1: Matching expected and actual statuses count as passed.
- AC2: Mismatches are reported in failed_ids.
- AC3: pass_rate equals passed / total, rounded to 2 decimals.
- AC4: meets_threshold is true when pass_rate >= threshold.
- AC5: Empty cases, duplicate IDs, invalid statuses, or a
  threshold outside 0..1 return INVALID_INPUT and exit code 2.

## Context
The tool evaluates supplied test outcomes only. It does not
generate AI responses or decide whether an answer is correct.

## Out of scope
Live model calls, retrieval, citation scoring, and dashboards.

## Run
python hw1/mishakakhniashvili/src/evaluate.py '<JSON input>'

## Test
python -m pytest hw1/mishakakhniashvili
