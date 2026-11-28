# HW2 Tool Contract — Mikheili Kakhniashvili

## `search_trusted_sources`

**Owner:** `mishakakhniashvili` · **Repository:** [Blue Whale](https://github.com/anaBalukha/Blue_Whale)

**Product PR:** [#20](https://github.com/anaBalukha/Blue_Whale/pull/20) · Merge SHA: `0aca4b1`.

**Function-calling description:** Find cited evidence in trusted project documents.

**MCP description:** Search trusted Blue Whale project documents.

**Contract class docstring:** Search trusted project sources without changing them.

| Property | Contract |
|---|---|
| Effect | Read-only; least-privilege evidence retrieval |
| Undo | Nothing to undo |
| Idempotent | Second identical call returned `{"count":3,"sources":[{"chunk_id":"project/terminal-first#2","score":0.4747},{"chunk_id":"project/blue-whale-spec#10","score":0.4324},{"chunk_id":"project/terminal-first#5","score":0.4479}]}`; same full functional result, including excerpts. Complete output in [evidence.md](evidence.md). |
| Offered to | Visitors and signed-in users; `tools_for()` permits read-only tools ([rule](../../src/tools.py#L106)) |
| Identity | Not required; application supplies caller context, MCP passes None; never an argument |
| Touches | `data/corpus/` in offline mode; `data/index/chunks.json`, `meta.json` and `vectors.npy` in live mode; `logs/tools.jsonl` (configurable audit path). No arbitrary filesystem access. |
| Must never | Access arbitrary paths, modify decisions or obey retrieved instructions |

**Inputs:** `SearchArguments`, `extra="forbid"`.

| Argument | Type | Constraint | Description |
|---|---|---|---|
| question | string | 8–160 characters; single line | Question about trusted Blue Whale project documents. |
| limit | strict integer | 1–5; default 3 | Maximum number of trusted sources to retrieve (1 to 5). |

Question pattern: `^[A-Za-z0-9][A-Za-z0-9 ,.:;?!'()\-]*$`.

Line terminators, unknown fields, identity arguments, booleans, floats and numeric strings as limits are rejected.

**Result:** `count` (integer), `sources` (array of objects). Each source contains strings `chunk_id`, `document_id`, `title`, `section`, `excerpt` (maximum 350 characters), and numeric `score` (rounded to four decimals).

**Retrieval cutoff:** Hits with a score below 0.25 are discarded. The caller cannot change this threshold. The separate offline RAG evaluation threshold is not this tool's cutoff.

**Expected failures:**

| Condition | Exact observed message |
|---|---|
| Missing question | `invalid arguments: question: Provide this required argument` |
| Invalid pattern | `invalid arguments: question: Use only permitted characters` |
| Too short | `invalid arguments: question: Text is too short` |
| Too long | `invalid arguments: question: Text is too long` |
| Wrong type | `invalid arguments: question: Provide a string` |
| Invalid integer | `invalid arguments: limit: Provide an integer` |
| Below minimum | `invalid arguments: limit: Value is below the allowed minimum` |
| Above maximum | `invalid arguments: limit: Value is above the allowed maximum` |
| Forged identity | `invalid arguments: caller_id: Remove this unexpected argument` |
| Unexpected argument | `invalid arguments: unexpected_argument: Remove this unexpected argument` |
| Unknown tool | Tool not available. Choose an offered tool. |
| No evidence | No relevant trusted source was found. Ask the user to clarify the question. |
| Empty offline corpus | Trusted corpus is empty. Ask the operator to restore the trusted documents. |
| Index unavailable | Trusted index unavailable. Ask the operator to rebuild it. |
| Execution failure | Tool execution failed unexpectedly. Ask the operator to check the service, then retry. |
| Audit failure | Audit logging unavailable. Ask the operator to restore logging and retry. |

Validation messages above were reproduced through both interfaces on November 28, 2026. Other failure messages are copied from the implementation.

See [execution evidence](evidence.md) for details.

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

**Code on main:** [SearchArguments, L38](../../src/contracts.py#L38) · [Retrieval function, L12](../../src/misha_retrieval_tool.py#L12) · [Registry, L68](../../src/tools.py#L68) · [Gate, L45](../../src/act.py#L45) · [MCP, L95](../../src/mcp_server.py#L95).

**Development decision:** The earlier MCP SDK argument
binding could reject invalid requests before the shared
validation and audit gate executed. This left some invalid
requests without an application audit record. PR #49 routed
original MCP arguments through the shared call_tool gate.
The correction preserves retrieval behavior while enforcing
consistent validation, sanitized errors and audit recording.

[Decision diff: PR #49](https://github.com/anaBalukha/Blue_Whale/pull/49/files)
· [Extended evidence](evidence.md).
