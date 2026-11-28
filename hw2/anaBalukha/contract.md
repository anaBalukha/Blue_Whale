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

**Model-facing description:** Compare supplied prior and proposed project decisions without modifying either.

The tool is least-privilege because it only compares supplied decisions in memory. It cannot modify trusted state. Audit logging is its only execution-side write.

## Inputs

The Pydantic `DriftArguments` model has `extra="forbid"`.

| Argument | Type | Constraints | Description |
|---|---|---|---|
| `state` | dict[str, str] | 1–8 decisions | Prior project decisions supplied for comparison |
| `candidate` | dict[str, str] | 1–8 decisions | Proposed project decisions |

Dictionary keys:
- 1–32 characters.
- Lowercase ASCII letters, digits and underscores.
- Must begin with a lowercase ASCII letter.
- Pattern: `^[a-z][a-z0-9_]*$`.

Dictionary values:
- 1–80 characters.
- Must begin with an ASCII letter or digit.
- Pattern: `^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$`.

No user, student, account, `caller_id`, or `user_changes`
argument is permitted. There are no numeric input arguments.

## Output

The Pydantic `DriftResult` contains:

| Field | Type | Meaning |
|---|---|---|
| `status` | `drift` or `consistent` | Whether a contradiction exists |
| `effective_state` | dict[str, str] | Prior decisions used for comparison |
| `conflicts` | list[Conflict] | Detected conflicts |
| `conflicts[].field` | string | Decision key |
| `conflicts[].expected` | string | Prior value |
| `conflicts[].proposed` | string | Proposed value |

## Expected failures

| Condition | Actual message or message fragment |
|---|---|
| Missing argument | Provide this required argument |
| Invalid pattern | Use only permitted characters |
| Invalid string length | Text is too short / Text is too long |
| Invalid decision map | Use a value that satisfies the tool contract |
| Unexpected argument | Remove this unexpected argument |
| Tool not offered | Tool not available. Choose an offered tool. |
| Execution failure | Tool execution failed unexpectedly. Ask the operator to check the service, then retry. |
| Audit failure | Audit logging unavailable. Ask the operator to restore logging and retry. |

Validation errors include sanitized field locations,
not raw argument values.

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

The log fields are `ts`, `tool`, `ok`, `error`, `caller_type` and `latency_ms`.

The destination is configurable through `BLUE_WHALE_TOOL_LOG`.

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


Golden runner: `tests/test_tool_golden.py`.

Shared protocol regression tests:
`tests/test_mcp_protocol_boundary.py`.

## Distinction from the shared Lab 5 tool

My individual tool is `check_decision_drift`.

The shared Lab 5 tool is `answer_from_trusted_sources`,
implemented separately in PR #58 after the original HW2
implementation.

- [Shared tool implementation](../../src/team_answer_tool.py)
- [Shared tool contract](../../docs/tool-contracts.md)
- [PR #58](https://github.com/anaBalukha/Blue_Whale/pull/58)
