# HW1 - Golden Test Results

Feature: Structured Conversation Drift Checker

## Golden 1 - Detect contradiction

Question: Does proposing MongoDB contradict the confirmed PostgreSQL decision?

Input:
{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}

Expected:
- Status: drift
- Conflicting field: database
- Expected: PostgreSQL
- Proposed: MongoDB

Actual:
{"status": "drift", "effective_state": {"database": "PostgreSQL"}, "conflicts": [{"field": "database", "expected": "PostgreSQL", "proposed": "MongoDB"}]}

Result: PASS

How tested:
python hw1/anaBalukha/src/drift_checker.py '{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}'

## Golden 2 - Explicit user change

Question: Is switching to MongoDB allowed when the user explicitly requests it?

Input:
{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"},"user_changes":{"database":"MongoDB"}}

Expected:
- Status: consistent
- Effective database: MongoDB
- No conflicts

Actual:
{"status": "consistent", "effective_state": {"database": "MongoDB"}, "conflicts": []}

Result: PASS

How tested:
python hw1/anaBalukha/src/drift_checker.py '{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"},"user_changes":{"database":"MongoDB"}}'

## Golden 3 - Invalid input

Question: What happens when the confirmed state is a list instead of an object?

Input:
{"state":[],"candidate":{"database":"MongoDB"}}

Expected:
- Error code: INVALID_INPUT
- Exit code: 2

Actual:
{"error": {"code": "INVALID_INPUT", "message": "state must be a JSON object"}}
Exit code: 2

Result: PASS

How tested:
python hw1/anaBalukha/src/drift_checker.py '{"state":[],"candidate":{"database":"MongoDB"}}'
echo "Exit code: $?"

## Automated tests

Command:
python -m pytest -q hw1/anaBalukha

Actual result:
4 passed in 0.05s
