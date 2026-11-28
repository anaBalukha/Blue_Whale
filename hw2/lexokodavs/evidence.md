# HW2 · Evidence · `preview_checkpoint_update` · lexokodavs

## The five golden cases

`evals/tools/lexokodavs.yaml`, run by `tests/test_tool_golden.py` through `call_tool()` (no model, no key) in the CI job `test`.
Actual outputs below were verified on 2026-11-28 against commit `b413f87` (`origin/main`) in `/tmp/bw-hw2-evidence` using `Blue_Whale/.venv` (Python 3.14.10, `mcp` 2.3.0), building on initial captures from PR #35 (`6fc047e` on 2026-11-24).

| # | Type | Call | Expected | Actual | Pass? |
|---|---|---|---|---|---|
| n1 | normal | v4, `{database: PostgreSQL, framework: FastAPI}` + `{database: MongoDB}` | v5, `changed_fields [database]`, confirmation required | `{"checkpoint": {"version": 5, "decisions": {"database": "MongoDB", "framework": "FastAPI"}}, "changed_fields": ["database"], "requires_confirmation": true}` | pass |
| n2 | normal | v2, same decisions + `{language: Python}` | v3, existing decisions kept, `[language]` | `{"checkpoint": {"version": 3, "decisions": {"database": "PostgreSQL", "framework": "FastAPI", "language": "Python"}}, "changed_fields": ["language"], "requires_confirmation": true}` | pass |
| n3 | normal | v3, `{database: PostgreSQL}` proposed again | version stays 3, no changes | `{"checkpoint": {"version": 3, "decisions": {"database": "PostgreSQL", "framework": "FastAPI"}}, "changed_fields": [], "requires_confirmation": false}` | pass |
| b1 | bad-input | `previous_version: -1` | refused before the tool runs, error names `previous_version` | `invalid arguments: previous_version: Value is below the allowed minimum` | pass |
| a1 | adversarial | valid call plus `authorized: true` | refused; the model cannot approve its own proposal | `invalid arguments: unexpected_argument: Remove this unexpected argument` | pass |

Repeated `n1` calls via `call_tool()` returned the identical `result` payload (`checkpoint` v5, `changed_fields: ["database"]`, `requires_confirmation: true`) with distinct timestamps (`ts`) and separate audit-log entries.

Sample audit line written for `a1` (without decision values or arguments):
`{"ts": "2026-11-28T15:33:36.908332+00:00", "tool": "preview_checkpoint_update", "ok": false, "error": "invalid arguments: unexpected_argument: Remove this unexpected argument", "caller_type": "visitor", "latency_ms": 0}`

**Reproduce:**

```bash
export BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30
python -m pytest -q tests/test_tool_golden.py -k lexokodavs
python -m pytest -q tests/test_lexo_checkpoint_tool.py tests/test_lexo_mcp.py
```

Both doors: `tests/test_lexo_mcp.py` drives `mcp.Client(mcp)` (`mcp` 2.3.0). Direct `Client(mcp).call_tool("preview_checkpoint_update", a1_args)` on `b413f87` returned `["invalid arguments: unexpected_argument: Remove this unexpected argument"]`, and `tests/test_lexo_mcp.py` verifies identical refusal behavior and constraint parity across the function-calling and MCP doors.

## The red run: proof the gate blocks

Changing `extra="forbid"` to `extra="ignore"` on `PreviewCheckpointUpdateArgs` allows forged/extra fields (such as `authorized: true`) to pass Pydantic input validation instead of being rejected by the shared gate.

- Red PR / branch evidence: PR #37 ("Red run" setting `extra="ignore"` on `PreviewCheckpointUpdateArgs`) confirmed that `extra="ignore"` silently bypasses schema rejection of unexpected arguments, causing golden `a1` and forged-approval tests to fail when `extra="forbid"` is removed.
- Current branch (`b413f87`): `extra="forbid"` is restored and active, blocking `a1` and extra fields prior to tool execution.

**What it taught me.** Relying on schema defaults or permissive extra-field handling (`extra="ignore"`) lets unvalidated arguments such as `authorized=true` slip past input parsing; enforcing `extra="forbid"` at the contract boundary ensures forged approval or identity fields are rejected deterministically before the tool handler runs.

## The green run

- Product PR [#35](https://github.com/anaBalukha/Blue_Whale/pull/35) (`6fc047e`) and `origin/main` (`b413f87`): `test` CI checks and `tests/test_lexo_checkpoint_tool.py` + `tests/test_lexo_mcp.py` + `tests/test_tool_golden.py` pass under `BLUE_WHALE_OFFLINE=1`.

## Things I fixed after review of my own first version

- `previous_version` had no upper bound: `10**30` was accepted and returned `10**30 + 1`. It is now `0..1000000`.
- 8 existing + 8 new decisions produced a 16-decision checkpoint that the tool itself would refuse as input. That merge is now refused with a message that tells the model what to do next.
- The MCP door declared `previous_version: int`, so MCP clients were told there were no bounds even though the gate enforced them. The new constraint-comparison test caught this, and the MCP signature now reuses the same `CheckpointVersion` type.

## Limitations

- All evidence is offline and deterministic (`BLUE_WHALE_OFFLINE=1`). No live-model call was made for this tool.
- The tool previews only. Blue Whale has no trusted checkpoint store yet, so nothing commits a confirmed preview.
- The product targets in `docs/spec.md` (85% drift detection, 80% recovery) are not measured by this homework.
