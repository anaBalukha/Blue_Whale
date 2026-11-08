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

| Argument | Type | Constraint |
|---|---|---|
| question | string | 8–160 characters; regex `^[A-Za-z0-9][A-Za-z0-9 ,.:;?!'()\-]*$`; starts with an ASCII letter or digit; permits ASCII letters, digits, spaces, and `, . : ; ? ! ' ( ) -` afterward |
| limit | strict integer | 1–5; default 3; numeric strings and booleans are rejected |
| unknown fields | any | Rejected by extra="forbid" |

## Output

- count: number of returned sources
- sources: document ID, chunk ID, title, section, excerpt and similarity score

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

## Implementation links on main

- [Contract](https://github.com/anaBalukha/Blue_Whale/blob/main/src/contracts.py)
- [Retrieval tool](https://github.com/anaBalukha/Blue_Whale/blob/main/src/misha_retrieval_tool.py)
- [Tool registry](https://github.com/anaBalukha/Blue_Whale/blob/main/src/tools.py)
- [Execution gates](https://github.com/anaBalukha/Blue_Whale/blob/main/src/act.py)
- [MCP server](https://github.com/anaBalukha/Blue_Whale/blob/main/src/mcp_server.py)
- [Five goldens](https://github.com/anaBalukha/Blue_Whale/blob/main/evals/tools/mishakakhniashvili.yaml)
