# Versioned Checkpoint Builder — Golden Cases

All three were run on 2026-11-24 from the repository root, on branch `fix/lexokodavs-hw1-evidence`.
The original HW1 submission (2026-10-20) recorded only Case 1, without the expected result or the command. These cases were re-run as a post-grading correction.

## Case 1 · Override an existing decision

- **Input:** `{"previous":{"version":1,"decisions":{"database":"PostgreSQL","framework":"FastAPI"}},"user_changes":{"database":"MongoDB"}}`
- **Expected:** version 2, `database` becomes `MongoDB`, `framework` kept, `changed_fields: ["database"]`, exit 0.
- **Actual:** `{"checkpoint": {"version": 2, "decisions": {"database": "MongoDB", "framework": "FastAPI"}}, "changed_fields": ["database"]}`, exit 0.
- **Result:** pass
- **Command:** `python hw1/lexokodavs/src/checkpoint_builder.py '{"previous":{"version":1,"decisions":{"database":"PostgreSQL","framework":"FastAPI"}},"user_changes":{"database":"MongoDB"}}'`

## Case 2 · Repeat an existing value (no-op keeps the version)

- **Input:** `{"previous":{"version":2,"decisions":{"database":"MongoDB","framework":"FastAPI"}},"user_changes":{"database":"MongoDB"}}`
- **Expected:** version stays 2, decisions unchanged, `changed_fields: []`, exit 0.
- **Actual:** `{"checkpoint": {"version": 2, "decisions": {"database": "MongoDB", "framework": "FastAPI"}}, "changed_fields": []}`, exit 0.
- **Result:** pass
- **Command:** `python hw1/lexokodavs/src/checkpoint_builder.py '{"previous":{"version":2,"decisions":{"database":"MongoDB","framework":"FastAPI"}},"user_changes":{"database":"MongoDB"}}'`

## Case 3 · Invalid input: a smuggled approval flag

- **Input:** `{"previous":{"version":1,"decisions":{"database":"PostgreSQL"}},"user_changes":{"database":"MongoDB"},"authorized":true}`
- **Expected:** refused with `INVALID_INPUT`, exit 2, no checkpoint printed.
- **Actual:** `{"error": {"code": "INVALID_INPUT", "message": "Payload must contain exactly 'previous' and 'user_changes'."}}`, exit 2.
- **Result:** pass. **Note:** before the 2026-11-24 fix the same input printed a version 2 checkpoint with exit 0, because the builder ignored unknown fields. See `delegation.md`.
- **Command:** `python hw1/lexokodavs/src/checkpoint_builder.py '{"previous":{"version":1,"decisions":{"database":"PostgreSQL"}},"user_changes":{"database":"MongoDB"},"authorized":true}'`

## Automated

`python -m pytest hw1/lexokodavs -v` → 14 passed (2026-11-24). The suite passes from the repository root and from any other folder.
