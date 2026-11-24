# Versioned Checkpoint Builder — Specification

## 0. Setup, run and test (from a fresh clone, repository root)

```bash
python -m pip install -r requirements.txt      # only pytest is needed for HW1
python hw1/lexokodavs/src/checkpoint_builder.py '{"previous":{"version":1,"decisions":{"database":"PostgreSQL"}},"user_changes":{"database":"MongoDB"}}'
python -m pytest hw1/lexokodavs -v
```

No network, no model call, no API key.

## 1. Goal

A deterministic Python CLI that takes the previous checkpoint of confirmed project decisions plus a set of changes, and returns the next checkpoint. The builder preserves unchanged decisions, increments the version only when a value actually changes, and reports exactly which fields changed.

**About "authorized".** The builder applies whatever `user_changes` it is given. It **cannot prove** that a person really authorized them; that is the caller's job (in the capstone: an application-owned confirmation step). For this reason it refuses any extra field, such as `"authorized": true`, instead of treating it as approval.

## 2. Users and context

- **Users:** developers, and the Blue Whale assistant code, that keep a versioned record of what the user has confirmed (e.g. "database = PostgreSQL").
- **Context list** (everything the builder reads): the single JSON argument on the command line. It reads no files, environment variables, network or model output.

## 3. Input and output

Input: one JSON object with **exactly** two fields.

```json
{
  "previous": {"version": 1, "decisions": {"database": "PostgreSQL", "framework": "FastAPI"}},
  "user_changes": {"database": "MongoDB"}
}
```

- `previous` has exactly `version` (integer ≥ 0; `true`/`"1"` refused) and `decisions` (object, non-empty string keys, string values).
- `user_changes` is a **flat** object of decision key → string value (not nested under `decisions`). It may be empty, which is a no-op.

Success (exit code 0):

```json
{"checkpoint": {"version": 2, "decisions": {"database": "MongoDB", "framework": "FastAPI"}}, "changed_fields": ["database"]}
```

Error (exit code 2): `{"error": {"code": "INVALID_INPUT", "message": "..."}}`. No checkpoint is printed.

## 4. Acceptance criteria (each checked by `test_checkpoint_builder.py`)

1. Changed and new keys are merged into a copy of `previous.decisions`; unchanged keys are kept (`test_checkpoint_builder_override`, `test_checkpoint_builder_new_field`).
2. `changed_fields` lists only keys whose value actually changes, sorted; repeating an existing value is ignored (`test_checkpoint_builder_noop`, `test_changed_fields_sorted_and_version_increments_once`).
3. The version increments by exactly 1 if and only if at least one field changes (same tests).
4. **Error case:** malformed JSON, a non-object payload, missing fields, a negative / boolean / string version, nested or non-string change values, or **any unknown field** return `INVALID_INPUT` with exit code 2 (`test_checkpoint_builder_invalid_input`, `test_malformed_payloads_are_refused`, `test_unknown_authorization_field_is_refused`, `test_unknown_field_inside_previous_is_refused`).

## 5. Out of scope

- Deciding or verifying who authorized a change (identity, sessions, confirmation UI).
- Storing checkpoints: the builder prints a result and saves nothing.
- Deleting decisions, validating decision *values* against a vocabulary, or bounding input size.
- Detecting drift: that is the team's `check_decision_drift` tool, not this feature.
