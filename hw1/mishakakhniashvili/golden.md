# HW1 - Golden Test Results

Feature: Golden Test Evaluation Reporter

All three cases were executed using Python CLI.
Result: 3/3 golden cases passed.

## Golden 1 - All Cases Pass

Input: Two cases with matching expected and actual statuses.

Command:

    python hw1/mishakakhniashvili/src/evaluate.py '{"cases":[{"id":"g1","expected":"answered","actual":"answered"},{"id":"g2","expected":"refused","actual":"refused"}]}'

Expected: 2 passed, pass rate 1.0, threshold met, no failures.

Actual:

    {"total": 2, "passed": 2, "pass_rate": 1.0, "meets_threshold": true, "failed_ids": []}

Result: PASS

## Golden 2 - One Case Fails

Input: Two cases, with one mismatched status.

Command:

    python hw1/mishakakhniashvili/src/evaluate.py '{"cases":[{"id":"g1","expected":"answered","actual":"answered"},{"id":"g2","expected":"refused","actual":"answered"}]}'

Expected: 1 passed, pass rate 0.5, threshold not met,
failed ID g2.

Actual:

    {"total": 2, "passed": 1, "pass_rate": 0.5, "meets_threshold": false, "failed_ids": ["g2"]}

Result: PASS

## Golden 3 - Invalid Input

Input: Empty list of cases.

Command:

    python hw1/mishakakhniashvili/src/evaluate.py '{"cases":[]}'
    echo "Exit code: $?"

Expected: INVALID_INPUT error and exit code 2.

Actual:

    {"error": {"code": "INVALID_INPUT", "message": "cases must be a non-empty list"}}
    Exit code: 2

Result: PASS

## Automated Verification

Command:

    python -m pytest hw1/mishakakhniashvili -v

Actual result: 6 passed in 0.23s.
