# HW2 Tool Contract — Ana Balukhashvili

## check_decision_drift

**Purpose:** Compare existing project decisions with proposed
decisions and report contradictions without changing state.

**Owner:** Ana Balukhashvili (`anaBalukha`).

| Property | Contract |
|---|---|
| Effect | Read-only comparison |
| Undo | Nothing to undo |
| Idempotent | Yes, for identical inputs |
| Offered to | Visitors and signed-in users |
| Caller identity | Not needed and not accepted as an argument |
| Resources | Existing `src/drift_core.py` function, in memory |
| Must never | Change decisions, invent user approval, accept model-supplied overrides, or access arbitrary files |

## Inputs

The Pydantic `DriftArguments` model has `extra="forbid"`.

| Argument | Type | Constraints |
|---|---|---|
| `state` | Dictionary of strings | 1–8 confirmed previous decisions |
| `candidate` | Dictionary of strings | 1–8 proposed decisions |

Dictionary keys:
- 1–32 characters.
- Lowercase ASCII letters, digits and underscores.
- Must begin with a lowercase ASCII letter.
- Pattern: `^[a-z][a-z0-9_]*$`.

Dictionary values:
- 1–80 characters.
- Must begin with an ASCII letter or digit.
- Remaining characters limited by the `DecisionValue` pattern in `src/contracts.py`.

No user, student, account, `caller_id`, or `user_changes`
argument is permitted. There are no numeric input arguments.

## Output

The Pydantic `DriftResult` contains:

| Field | Type | Meaning |
|---|---|---|
| `status` | `drift` or `consistent` | Whether a contradiction exists |
| `effective_state` | Dictionary | Prior decisions used for comparison |
| `conflicts` | List | Each conflict has `field`, `expected`, and `proposed` |

## Expected failures

| Condition | Behavior |
|---|---|
| Missing required argument | Refuse and request the missing argument |
| Invalid value or key | Refuse with a safe validation error |
| Unexpected identity or override | Refuse before running the function |
| Tool not offered | Refuse before execution |
| Unexpected execution failure | Return a generic safe error |
| Audit log unavailable | Return a safe failure instead of an unlogged success |

## Security and limitations

Both function calling and MCP use the same Pydantic
contract and `call_tool()` execution gate.

The tool invokes the existing `check_drift()` function
without a model-provided `user_changes` override.

The model can provide `state` and `candidate`. This tool
does not independently authenticate the state source.
A production integration must obtain confirmed state
from trusted application storage.

The tool does not store, update, or delete decisions.
It also does not perform recovery by itself.

## Audit logging

The shared gate writes one line per call to
`logs/tools.jsonl` by default, recording the timestamp,
tool name, success or failure, sanitized error, caller
type and latency.

Raw decision values and caller identity are not logged.

## Verification and source links

- [Input contract](https://github.com/anaBalukha/Blue_Whale/blob/main/src/contracts.py)
- [Drift tool](https://github.com/anaBalukha/Blue_Whale/blob/main/src/ana_drift_tool.py)
- [Original comparison function](https://github.com/anaBalukha/Blue_Whale/blob/main/src/drift_core.py)
- [Tool registry](https://github.com/anaBalukha/Blue_Whale/blob/main/src/tools.py)
- [Execution gate](https://github.com/anaBalukha/Blue_Whale/blob/main/src/act.py)
- [MCP server](https://github.com/anaBalukha/Blue_Whale/blob/main/src/mcp_server.py)
- [Five golden cases](https://github.com/anaBalukha/Blue_Whale/blob/main/evals/tools/anaBalukha.yaml)
- [Direct tests](https://github.com/anaBalukha/Blue_Whale/blob/main/tests/test_ana_drift_tool.py)
- [MCP tests](https://github.com/anaBalukha/Blue_Whale/blob/main/tests/test_ana_mcp.py)

Product PR: https://github.com/anaBalukha/Blue_Whale/pull/28
