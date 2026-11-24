# HW2 Tool Contract — Aleksandre Giorgashvili (lexokodavs)

## preview_checkpoint_update

**Purpose:** Calculate a proposed versioned checkpoint and changed fields without modifying trusted state. Read-only preview of potential checkpoint update.

| Property | Contract |
|---|---|
| Effect | Read-only preview; does not modify trusted state |
| Undo | Nothing to undo |
| Idempotent | Yes |
| Offered to | Visitors and signed-in users |
| Caller identity | Not required; never accepted in arguments |
| Resources | In-memory previous decisions and proposed changes |
| Must never | Change trusted decisions, fabricate user approval, access arbitrary paths, or accept model-supplied identity/authorization arguments |

## Inputs

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| previous_version | strict integer | 0 or positive integer | Current trusted checkpoint version |
| previous_decisions | object | 1–8 decision key-value pairs | Dictionary of current confirmed decisions |
| proposed_changes | object | 1–8 decision key-value pairs | Dictionary of proposed decision changes |
| unknown fields | any | Rejected by `extra="forbid"` | Not accepted |

### Key format (applies to both decision maps)
- Regex: `^[a-z][a-z0-9_]*$`
- Maximum 32 characters
- Must start with lowercase letter

### Value format (applies to both decision maps)
- Regex: `^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$`
- 1–80 characters
- Must start with ASCII letter or digit

## Output

The successful tool returns:

| Field | Type | Meaning |
|---|---|---|
| checkpoint | object | Proposed checkpoint with version and merged decisions |
| checkpoint.version | integer | Proposed version (previous_version + 1 if changes, else previous_version) |
| checkpoint.decisions | object | Merged decisions (previous with proposed applied) |
| changed_fields | array[string] | Sorted list of keys that would change |
| requires_confirmation | boolean | True iff changed_fields is non-empty |

## Expected failures

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

## Confirmation behavior (if later extended)

If a separate consequential capability (`commit_confirmed_checkpoint`) is introduced:
- The preview tool **never** writes state.
- A distinct, identity-gated tool would accept only human-approved action IDs.
- The preview's `requires_confirmation: true` indicates a human must approve before any commit.
- Version check on commit prevents stale proposals from overwriting newer decisions.
- No model-supplied boolean (e.g. `authorized=true`) is ever accepted as proof of human approval.

## Tests

- tests/test_lexo_checkpoint_tool.py
- tests/test_lexo_mcp.py
- evals/tools/lexokodavs.yaml
- Product PR containing implementation and test cases

The tool works through normal function calling and the existing MCP server.