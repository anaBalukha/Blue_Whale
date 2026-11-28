# HW2 Tool Contract — Mikheili Kakhniashvili

## `search_trusted_sources`

**Model description:** Find cited evidence in trusted project documents.

| Property | Contract |
|---|---|
| Effect | Read-only; least-privilege evidence retrieval |
| Undo | Nothing to undo |
| Idempotent | Yes, with the same index and model |
| Offered to | Visitors and signed-in users |
| Identity | Not required; never an argument |
| Touches | Trusted corpus, retrieval index, audit log |
| Must never | Access arbitrary paths, modify decisions or obey retrieved instructions |

**Inputs:** `SearchArguments`, `extra="forbid"`.

| Argument | Type | Constraint | Description |
|---|---|---|---|
| question | string | 8–160 characters; single line | Question about trusted project documents |
| limit | strict integer | 1–5; default 3 | Maximum sources to retrieve |

Question pattern: `^[A-Za-z0-9][A-Za-z0-9 ,.:;?!'()\-]*$`.

Line terminators, unknown fields, identity arguments, booleans, floats and numeric strings as limits are rejected.

**Result:** `count` (integer), `sources` (array of objects). Each source contains strings `chunk_id`, `document_id`, `title`, `section`, `excerpt` (maximum 350 characters), and numeric `score` (rounded to four decimals).

**Expected failures:**

| Condition | Message or message fragment |
|---|---|
| Missing argument | Provide this required argument |
| Invalid pattern | Use only permitted characters |
| Invalid length | Text is too short / Text is too long |
| Invalid integer | Provide an integer |
| Invalid bounds | Value is below the allowed minimum / Value is above the allowed maximum |
| Unexpected argument | Remove this unexpected argument |
| Unknown tool | Tool not available. Choose an offered tool. |
| No evidence | No relevant trusted source was found. Ask the user to clarify the question. |
| Empty offline corpus | Trusted corpus is empty. Ask the operator to restore the trusted documents. |
| Index unavailable | Trusted index unavailable. Ask the operator to rebuild it. |
| Execution failure | Tool execution failed unexpectedly. Ask the operator to check the service, then retry. |
| Audit failure | Audit logging unavailable. Ask the operator to restore logging and retry. |

**Tests:**

| Case | Expected | Where |
|---|---|---|
| Valid retrieval | Relevant source | `test_misha_retrieval_tool.py` |
| Invalid limit | Refused | `test_misha_retrieval_tool.py` |
| Unknown tool | Refused | `test_tool_gates.py` |
| Forged identity | Refused | `test_tool_gates.py` |
| Adversarial path | Refused | `test_misha_retrieval_tool.py` |
| Five goldens | Pass | `evals/tools/mishakakhniashvili.yaml` |

**Log:** `logs/tools.jsonl` records `ts`, `tool`, `ok`, `error`, `caller_type`, `latency_ms`; excludes raw questions, identities and retrieved content.

Both interfaces use the shared strict validation gate and sanitized errors.

**Code:** [Contract](../../src/contracts.py) · [Tool](../../src/misha_retrieval_tool.py) · [Registry](../../src/tools.py) · [Gate](../../src/act.py) · [MCP](../../src/mcp_server.py).

[Product PR #20](https://github.com/anaBalukha/Blue_Whale/pull/20) · [Extended evidence](evidence.md).
