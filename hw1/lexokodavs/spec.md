# Versioned Checkpoint Builder — Specification

## 1. Goal and Objectives
<<<<<<< HEAD
The Versioned Checkpoint Builder is a deterministic Python CLI tool designed for developers and AI assistants managing confirmed project decisions.
=======
The Versioned Checkpoint Builder is a deterministic Python CLI tool designed for developers and AI assistants managing confirmed project decisions. It takes a previous conversation checkpoint and a set of explicit user-authorized changes, merges them securely, increments the version number only when effective changes occur, and outputs a structured JSON checkpoint.

## 2. Users and Context
- **Primary Users:** Students and software developers managing conversational state transitions in structured assistants.
- **Context:** Operates offline without network dependencies or LLM calls, ensuring predictable state progression based solely on verified user input.

## 3. Input / Output Contracts
- **Input:** A single JSON-encoded string argument containing:
  - `previous`: Object with integer `version` ($\ge 0$) and `decisions` dictionary (string keys and values).
  - `user_changes`: Object with `decisions` updates.
- **Output (Success - Exit Code 0):** JSON object containing:
  - `checkpoint`: Updated version number and merged decisions dictionary.
  - `changed_fields`: Sorted list of keys whose values actually changed.
- **Output (Error - Exit Code 2):** JSON object: `{"error": {"code": "INVALID_INPUT", "message": "..."}}`.

## 4. Testable Acceptance Criteria
1. New or modified keys are merged into a copy of previous decisions while preserving unchanged keys.
2. Only effective changes appear in sorted `changed_fields`; repeating an existing value is ignored.
3. Version increments by exactly 1 if and only if at least one effective change occurs.
4. Malformed JSON, missing fields, invalid version types, or non-string values return `INVALID_INPUT` and exit code 2.

## 5. Setup, Run, and Test Commands
- **Run:** `python hw1/lexokodavs/src/checkpoint_builder.py '<JSON_PAYLOAD>'`
- **Test:** `python -m pytest hw1/lexokodavs -v`
>>>>>>> origin/main
