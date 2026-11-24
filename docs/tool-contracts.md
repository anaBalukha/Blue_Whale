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

- `previous_version`: 0 or positive integer representing the current trusted checkpoint version.
- `previous_decisions`: Dictionary of decision key-value pairs (string keys and string values).
- `proposed_changes`: Dictionary of decision key-value pairs (string keys and string values).

- Keys: lowercase ASCII letters, numbers and underscores;
  - start with a letter; maximum 32 characters.
- Values: 1–80 characters, starting with an ASCII letter or digit;
  - remaining characters limited to letters, digits, spaces, underscores and selected ordinary punctuation.
- Extra arguments are forbidden.
- No identity or user_changes argument is accepted.

The model sees all input fields. The tool compares the proposed changes against the previous state and calculates a proposed checkpoint without modifying trusted state.

### Result

- `checkpoint`: Dictionary containing:
  - `version`: Proposed version number (previous_version + 1 if changes exist, else previous_version)
  - `decisions`: Merged decisions dictionary (previous decisions with proposed changes applied)
- `changed_fields`: Sorted list of decision keys that would change
- `requires_confirmation`: Boolean indicating whether human approval is required before applying the proposed changes

### Expected failures

| Failure | Model-facing behavior |
|---|---|
| Missing or malformed input | Explain which required field is missing or invalid |
| Invalid version (non-integer, negative) | Refuse with validation error |
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

## HW2 ownership

| Member | HW2 tool |
|---|---|
| Ana Balukhashvili | check_decision_drift |
| Mikheili Kakhniashvili | search_trusted_sources |
| Aleksandre Giorgashvili | preview_checkpoint_update |