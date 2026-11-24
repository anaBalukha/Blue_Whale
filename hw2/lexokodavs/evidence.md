# HW2 · Evidence · `preview_checkpoint_update` · lexokodavs

## The five golden cases

`evals/tools/lexokodavs.yaml`, run by `tests/test_tool_golden.py` through `call_tool()` (no model, no key) in the CI job `test`.
Actual outputs below were recorded on 2026-11-24 from commit `6fc047e` of the product PR.

| # | Type | Call | Expected | Actual | Pass? |
|---|---|---|---|---|---|
| n1 | normal | v4, `{database: PostgreSQL, framework: FastAPI}` + `{database: MongoDB}` | v5, `changed_fields [database]`, confirmation required | `{"version": 5, "decisions": {"database": "MongoDB", "framework": "FastAPI"}}`, `["database"]`, `requires_confirmation: true` | pass |
| n2 | normal | v2, same decisions + `{language: Python}` | v3, existing decisions kept, `[language]` | `{"version": 3, "decisions": {"database": "PostgreSQL", "framework": "FastAPI", "language": "Python"}}`, `["language"]`, `true` | pass |
| n3 | normal | v3, `{database: PostgreSQL}` proposed again | version stays 3, no changes | `{"version": 3, ...}`, `[]`, `requires_confirmation: false` | pass |
| b1 | bad-input | `previous_version: -1` | refused before the tool runs, error names `previous_version` | `invalid arguments: previous_version: Value is below the allowed minimum` | pass |
| a1 | adversarial | valid call plus `authorized: true` | refused; the model cannot approve its own proposal | `invalid arguments: unexpected_argument: Remove this unexpected argument` | pass |

The audit line written for a1: `{"tool": "preview_checkpoint_update", "ok": false, "error": "invalid arguments: unexpected_argument: Remove this unexpected argument", "caller_type": "visitor", "latency_ms": 0}` (no decision values recorded).

**Reproduce:**

```bash
export BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30
python -m pytest -q tests/test_tool_golden.py -k lexokodavs     # 5 passed
python -m pytest -q tests/test_lexo_checkpoint_tool.py tests/test_lexo_mcp.py
python -m pytest -q tests                                       # full suite
```

Full suite locally on the product branch, 2026-11-24: **110 passed**.

Both doors: `tests/test_lexo_mcp.py` drives the real MCP server with `mcp.Client`. The MCP door refuses `authorized` and `caller_id` with the same message as the function-calling door, and the two doors advertise the same bounds and patterns.

## The red run: proof the gate blocks

**PENDING. Done after PR #35 is merged.**

Plan: on a throwaway branch, change `extra="forbid"` to `extra="ignore"` on `PreviewCheckpointUpdateArgs` and nothing else. Locally that change makes 7 tests fail, including `test_tool_golden_case[lexokodavs-case9]` (a1) and the forged-approval tests in both doors (checked 2026-11-24 and reverted).

- Red PR: _pending_
- Red run: _pending_
- Merge button state: _pending_
- Branch deleted: _pending_

**What it taught me.** _Pending the red run._

## The green run

Product PR [#35](https://github.com/anaBalukha/Blue_Whale/pull/35): green CI run _pending final link after merge_.

## Things I fixed after review of my own first version

- `previous_version` had no upper bound: `10**30` was accepted and returned `10**30 + 1`. It is now `0..1000000`.
- 8 existing + 8 new decisions produced a 16-decision checkpoint that the tool itself would refuse as input. That merge is now refused with a message that tells the model what to do next.
- The MCP door declared `previous_version: int`, so MCP clients were told there were no bounds even though the gate enforced them. The new constraint-comparison test caught this, and the MCP signature now reuses the same `CheckpointVersion` type.

## Limitations

- All evidence is offline and deterministic. No live-model call was made for this tool.
- The tool previews only. Blue Whale has no trusted checkpoint store yet, so nothing commits a confirmed preview.
- The product targets in `docs/spec.md` (85% drift detection, 80% recovery) are not measured by this homework.
