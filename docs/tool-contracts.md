# Blue Whale — Tool Contracts

## check_decision_drift

Owner: Ana Balukhashvili (@anaBalukha)

**Model-facing description:** Compare supplied previous project
decisions with proposed decisions and report conflicts. Read-only.

| Property | Contract |
|---|---|
| Effect | Reads and compares supplied data |
| Undo | Nothing to undo |
| Idempotent | Yes |
| Offered to | Visitors and signed-in users |
| Identity | Not needed; never a tool argument |
| Touches | src/drift_core.py in memory; no database writes |
| Must never | Change confirmed decisions, fabricate user approval, access arbitrary paths, or accept model-supplied user_changes |

### Inputs

- `state`: 1–8 prior decisions, supplied as a JSON object.
- `candidate`: 1–8 proposed decisions, supplied as a JSON object.
- Keys: lowercase ASCII letters, numbers and underscores;
  start with a letter; maximum 32 characters.
- Values: 1–80 characters, starting with an ASCII letter or digit;
  remaining characters limited to letters, digits, spaces,
  underscores and selected ordinary punctuation.
- Extra arguments are forbidden.
- No identity or user_changes argument is accepted.

The model sees both input fields. The tool compares their contents;
it does not independently authenticate the supplied prior state.
A production caller must obtain trusted state from application-owned
storage rather than treating model text as authoritative.

### Result

- `status`: `drift` or `consistent`
- `effective_state`: dictionary of compared prior decisions
- `conflicts`: list of objects containing `field`, `expected`,
  and `proposed`

### Expected failures

| Failure | Model-facing behavior |
|---|---|
| Missing state or candidate | Explain that the required input is missing |
| Invalid field or value | Refuse with a validation error |
| Forged user_changes | Refuse unexpected argument |
| Unknown tool | Refuse without execution |
| Unexpected execution failure | Return a generic safe error |
| Audit logging unavailable | Return a safe failure |

The shared execution gate validates inputs before running the tool
and logs calls without raw decisions or caller identity.

### Tests

- tests/test_ana_drift_tool.py
- tests/test_ana_mcp.py
- tests/test_tool_golden.py
- evals/tools/anaBalukha.yaml

## search_trusted_sources

Owner: Mikheili Kakhniashvili (@mishakakhniashvili)

See the full contract at: `hw2/mishakakhniashvili/contract.md`

Summary:
- Read-only trusted document retrieval tool
- Validated Pydantic contract with `extra="forbid"`
- Five golden cases (normal, invalid, adversarial)
- Bounded tool loop, safe error handling, audit logging
- Function-calling and MCP registration

### Tests

- tests/test_misha_retrieval_tool.py
- tests/test_misha_mcp.py
- tests/test_misha_tool_errors.py
- evals/tools/mishakakhniashvili.yaml

## preview_checkpoint_update

Owner: Aleksandre Giorgashvili (@lexokodavs)

**Model-facing description:** Calculate a proposed versioned checkpoint and changed fields without modifying trusted state. Read-only preview of potential checkpoint update.

| Property | Contract |
|---|---|
| Effect | Read-only preview; does not modify trusted state |
| Undo | Nothing to undo |
| Idempotent | Yes |
| Offered to | Visitors and signed-in users |
| Identity | Not needed; never a tool argument |
| Touches | src/lexo_checkpoint_tool.py in memory; no database writes |
| Must never | Change trusted decisions, fabricate user approval, access arbitrary paths, or accept model-supplied identity/authorization arguments |

### Inputs

- `previous_version`: strict integer, 0 to 1000000 inclusive (booleans, strings and floats are refused); the current trusted checkpoint version.
- `previous_decisions`: 1 to 8 decision key-value pairs (shared `DecisionMap` from `src/contracts.py`).
- `proposed_changes`: 1 to 8 decision key-value pairs (shared `DecisionMap`). An empty change map is refused.
- Keys must match `^[a-z][a-z0-9_]*$` (1-32 characters); values must match `^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$` (1-80 characters).

- Keys: lowercase ASCII letters, numbers and underscores;
  - start with a letter; maximum 32 characters.
- Values: 1–80 characters, starting with an ASCII letter or digit;
  - remaining characters limited to letters, digits, spaces, underscores and selected ordinary punctuation.
- Extra arguments are forbidden.
- No identity, approval (`authorized`, `user_approved`) or `user_changes` argument is accepted.

The model sees all input fields. The tool compares the proposed changes against the previous state and calculates a proposed checkpoint without modifying trusted state.

### Result

- `checkpoint`: Dictionary containing:
  - `version`: Proposed version number (previous_version + 1 if changes exist, else previous_version)
  - `decisions`: Merged decisions dictionary (previous decisions with proposed changes applied)
- `changed_fields`: Sorted list of decision keys that would change
- `requires_confirmation`: `true` exactly when `changed_fields` is non-empty. It is informational: the preview is never written to trusted state, and only a separate, human-confirmed capability could commit it.

### Expected failures

| Failure | Model-facing behavior |
|---|---|
| Missing or malformed input | Explain which required field is missing or invalid |
| Invalid version (non-integer, negative, above 1000000) | Refuse with validation error naming `previous_version` |
| Merged checkpoint would exceed 8 decisions | "Proposed checkpoint would exceed 8 decisions. Propose fewer new decision fields or change existing ones." |
| Effective change at version 1000000 | "Checkpoint version limit reached. Ask the operator to archive this checkpoint before changing it." |
| Invalid decision key (wrong pattern) | Refuse with validation error |
| Invalid decision value (wrong pattern) | Refuse with validation error |
| Extra arguments | Refuse with validation error |
| Unexpected execution failure | Return a generic safe error |
| Audit logging unavailable | Return a safe failure |

The shared execution gate validates inputs before running the tool and logs calls without raw decisions or caller identity.

### Tests

- tests/test_lexo_checkpoint_tool.py
- tests/test_lexo_mcp.py
- evals/tools/lexokodavs.yaml
- Product PR containing implementation and test cases

The tool must work through normal function calling and the existing MCP server.

## answer_from_trusted_sources

Status: Implemented and offline-tested. External host and live model verification pending.

This tool is separate from the three individual HW2 tools.

**Model-facing description:** Answer a project question
using trusted Blue Whale documents, returning validated
citations or a safe refusal.

| Property | Contract |
|---|---|
| Effect | Read-only with respect to project state |
| Undo | Nothing to undo |
| Idempotent | No state changes; generated wording may vary |
| Offered to | Visitors and signed-in users |
| Identity | Not needed; never a tool argument |
| Touches | Existing trusted index, retrieval and answer pipeline |
| Must never | Modify decisions, invent sources, access arbitrary files or accept model-supplied authorization |

### Inputs

- question: ASCII string, 8-160 characters.
- Reuse the existing Question pattern and length constraints.
- limit: strict integer between 1 and 5, default 5.
- Extra arguments are forbidden.
- No identity, path, approval or authorization argument.
- Citation validation cannot be disabled by the caller.

### Result

- status: answered or refused.
- text: Grounded answer or safe refusal.
- sources: Retrieved source references used by the answer.

An insufficient-evidence refusal is a valid result,
not an execution failure.

### Expected failures

| Failure | Model-facing behavior |
|---|---|
| Invalid question | Provide a valid question |
| Invalid limit | Use an integer between 1 and 5 |
| Unexpected argument | Remove the unexpected argument |
| Trusted index unavailable | Ask the operator to rebuild the index |
| Insufficient evidence | Return the existing safe refusal |
| Invalid citations | Return the existing safe refusal |
| Unexpected execution failure | Return a generic safe error |
| Audit logging unavailable | Return a safe failure |

### Safety and resource limits

Reuse the existing grounded answer function with citation
checking enabled.

The tool may perform retrieval and one additional answer
generation call per invocation. Live mode can incur
embedding and generation costs.

Offline tests must use simulated model responses and
must not require an API key.

The tool audit log must not contain raw questions or
caller identities. Existing answer diagnostics may record
the question, so demonstration inputs must be synthetic
and non-sensitive.

A returned answer is not authorization to update
trusted conversation state.

### Verification plan

- Valid grounded answer with citations.
- Safe refusal when evidence is insufficient.
- Refusal when the answer contains invalid citations.
- Invalid arguments never reach the answer pipeline.
- Forged identity and arbitrary path arguments rejected.
- Function-calling and MCP result parity.
- Exactly one tool audit entry per invocation.
- Existing product tests and HW2 goldens remain green.

## HW2 ownership

| Member | HW2 tool |
|---|---|
| Ana Balukhashvili | check_decision_drift |
| Mikheili Kakhniashvili | search_trusted_sources |
| Aleksandre Giorgashvili | preview_checkpoint_update |
