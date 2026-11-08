# HW2 Tool Contract — Mikheili Kakhniashvili

## search_trusted_sources

**Purpose:** Retrieve relevant evidence from trusted Blue Whale
project documents without changing any data.

| Property | Contract |
|---|---|
| Effect | Read-only |
| Undo | Nothing to undo |
| Idempotent | Yes, with the same index and model |
| Offered to | Visitors and signed-in users |
| Caller identity | Not required; never accepted in arguments |
| Resources | Trusted corpus and its retrieval index |
| Must never | Access arbitrary paths, modify decisions, or trust retrieved text as instructions |

## Inputs

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| question | string | 8–160 characters; regex `^[A-Za-z0-9][A-Za-z0-9 ,.:;?!'()\\-]*$` | Question about trusted Blue Whale project documents. |
| limit | strict integer | 1–5; default 3; no booleans or numeric strings | Maximum number of trusted sources to retrieve (1 to 5). |
| unknown fields | any | Rejected by `extra="forbid"` | Not accepted |

## Output

The successful tool returns:

| Field | Type | Meaning |
|---|---|---|
| count | integer | Number of returned sources |
| sources | array of objects | Matching trusted-source chunks |
| sources[].chunk_id | string | Source chunk identifier |
| sources[].document_id | string | Trusted document identifier |
| sources[].title | string | Document title |
| sources[].section | string | Document section |
| sources[].excerpt | string | Source text, at most 350 characters |
| sources[].score | number | Retrieval relevance score, rounded to four decimals |

## Expected failures

- Invalid arguments: refuse before retrieval runs.
- Unsupported/unknown tool: refuse before execution.
- No relevant source: ask the user to clarify.
- Index unavailable: ask the operator to rebuild the index.
- Unexpected execution failure: return a generic operator/retry instruction and log the failed call without revealing exception details.

## Security and verification

Both interfaces share the SearchArguments contract.
Function calls pass through call_tool().
MCP requests also pass through call_tool() for strict validation.
Tool calls are logged without storing caller identity or raw questions.

Source files:
- src/contracts.py
- src/misha_retrieval_tool.py
- src/tools.py
- src/act.py
- src/mcp_server.py

Golden cases: evals/tools/mishakakhniashvili.yaml

## Audit log

Default destination: `logs/tools.jsonl`, configurable through
`BLUE_WHALE_TOOL_LOG`.

Each successful log write contains:

| Field | Type | Meaning |
|---|---|---|
| ts | string | UTC timestamp |
| tool | string | Registered tool name or `unknown_tool` |
| ok | boolean | Whether execution succeeded |
| error | string or null | Sanitized failure message |
| caller_type | string | `visitor` or `signed_in` |
| latency_ms | integer | Execution duration in milliseconds |

The audit log does not contain caller identity, raw questions,
retrieved source content, or arbitrary unknown argument names.

If the log cannot be written, `call_tool()` returns a structured
failure without exposing the configured logging path.
That failure cannot be recorded in the unavailable log.

## Verification

- Five HW2 goldens: `evals/tools/mishakakhniashvili.yaml`
- Golden runner: `tests/test_tool_golden.py`
- Gate verification: `tests/test_tool_gates.py`
- MCP validation and schema parity: `tests/test_misha_mcp.py`
- Error-handling regression tests: `tests/test_misha_tool_errors.py`
- Red CI proof: PR #21, closed without merging
- Original green product PR: #20

## Implementation links on main

- [Contract](https://github.com/anaBalukha/Blue_Whale/blob/main/src/contracts.py)
- [Retrieval tool](https://github.com/anaBalukha/Blue_Whale/blob/main/src/misha_retrieval_tool.py)
- [Tool registry](https://github.com/anaBalukha/Blue_Whale/blob/main/src/tools.py)
- [Execution gates](https://github.com/anaBalukha/Blue_Whale/blob/main/src/act.py)
- [MCP server](https://github.com/anaBalukha/Blue_Whale/blob/main/src/mcp_server.py)
- [Five goldens](https://github.com/anaBalukha/Blue_Whale/blob/main/evals/tools/mishakakhniashvili.yaml)
