# HW2 Tool Contract — Ana Balukhashvili

## `check_decision_drift`

**Model description:** Compare supplied prior and proposed project decisions without modifying either.

| Property | Contract |
|---|---|
| Effect | Read-only; least-privilege in-memory comparison |
| Undo | Nothing to undo |
| Idempotent | Yes, for identical inputs |
| Offered to | Visitors and signed-in users |
| Identity | Not required; never an argument |
| Touches | `src/drift_core.py`; audit log |
| Must never | Change trusted state or fabricate user approval |

**Inputs:** `DriftArguments`, `extra="forbid"`.

| Argument | Type | Constraint | Description |
|---|---|---|---|
| state | dict[str, str] | 1–8 entries | Prior decisions |
| candidate | dict[str, str] | 1–8 entries | Proposed decisions |

Keys: 1–32 characters, `^[a-z][a-z0-9_]*$`.

Values: 1–80 characters, `^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$`.

Line terminators are forbidden. No numeric, identity or override arguments.

**Result:** `status` (`consistent` or `drift`), `effective_state` (dict[str, str]), `conflicts` (list of objects with string fields `field`, `expected`, `proposed`).

**Expected failures:**

| Condition | Message or message fragment |
|---|---|
| Missing argument | Provide this required argument |
| Invalid pattern | Use only permitted characters |
| Invalid length | Text is too short / Text is too long |
| Invalid map | Use a value that satisfies the tool contract |
| Unexpected argument | Remove this unexpected argument |
| Tool not offered | Tool not available. Choose an offered tool. |
| Execution failure | Tool execution failed unexpectedly. Ask the operator to check the service, then retry. |
| Audit failure | Audit logging unavailable. Ask the operator to restore logging and retry. |

**Tests:**

| Case | Expected | Where |
|---|---|---|
| Valid comparison | Correct status | `test_ana_drift_tool.py` |
| Invalid input | Refused | `test_ana_drift_tool.py` |
| Tool not offered | Refused | `test_tool_gates.py` |
| Forged identity | Refused | `test_ana_drift_tool.py` |
| Fabricated override | Refused | `test_ana_mcp.py` |
| Five goldens | Pass | `evals/tools/anaBalukha.yaml` |

**Log:** `logs/tools.jsonl` records `ts`, `tool`, `ok`, `error`, `caller_type`, `latency_ms`; excludes raw decisions and identities.

**Limits:** No persistent memory or state authentication. Both interfaces use the shared validation gate.

**Code:** [Contract](../../src/contracts.py) · [Tool](../../src/ana_drift_tool.py) · [Registry](../../src/tools.py) · [Gate](../../src/act.py) · [MCP](../../src/mcp_server.py).

[Product PR #28](https://github.com/anaBalukha/Blue_Whale/pull/28) · [Extended evidence](evidence.md).
