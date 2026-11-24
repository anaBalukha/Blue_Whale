# HW2 · Evidence · `preview_checkpoint_update` · lexokodavs

## The five golden cases

`evals/tools/lexokodavs.yaml`, run by `tests/test_tool_golden.py` through `call_tool()` (no model, no key) in the CI job `test`.
Actual outputs below were recorded on 2026-11-24 from commit `6fc047e` of the product PR, which was merged unchanged as `28b107a`.

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

On 2026-11-24, branch `hw2-lexokodavs-red` (from `main` at `28b107a`) changed one line: `extra="forbid"` → `extra="ignore"` on `PreviewCheckpointUpdateArgs` in `src/lexo_checkpoint_tool.py` (commit `ed6c8e4`).

- Red PR: [#37 · TEST ONLY: Leqso HW2 contract regression — DO NOT MERGE](https://github.com/anaBalukha/Blue_Whale/pull/37), closed without merging (`mergedAt: null`).
- Red run (pull_request): https://github.com/anaBalukha/Blue_Whale/actions/runs/45453240515. The `test` job failed with `7 failed, 103 passed`:
  - `test_tool_golden.py::test_tool_golden_case[lexokodavs-case9]` (a1): `lexokodavs: unexpected success`
  - `test_lexo_checkpoint_tool.py::test_forged_identity_or_approval_never_runs[forged0-3]`
  - `test_lexo_mcp.py::test_mcp_rejects_forged_identity_or_approval[forged0-1]`
- Merge blocked: `main` branch protection requires the `test` check (`enforcement_level: everyone`). On #37 the failing `test` check was reported `isRequired: true` and the PR's merge state was `BLOCKED`.
- Branch deleted: `git push origin --delete hw2-lexokodavs-red`; `git ls-remote --heads origin hw2-lexokodavs-red` returns nothing.
- Afterwards `main` still has `extra="forbid"`, and the full suite on `main` is 110 passed.

**What it taught me.** With `extra="ignore"`, `authorized: true` was not refused. It was silently dropped, and the tool returned a normal, successful preview. Nothing visibly went wrong, and that is the danger: the model would believe its approval flag had been accepted, and the result gave no sign that anything had been discarded. The golden case caught it only because a1 expects a refusal, not just any successful-looking output. The same red run also showed why the spy in `test_forged_identity_or_approval_never_runs` matters: it proves the tool body ran with the forged argument present, which a result-only check could not show.

## The green run

Product PR [#35](https://github.com/anaBalukha/Blue_Whale/pull/35), approved by @mishakakhniashvili and merged 2026-11-24 as `28b107a`.

- Green run on the PR's final commit `6fc047e`: https://github.com/anaBalukha/Blue_Whale/actions/runs/45448045112
- Green run on `main` after the merge: https://github.com/anaBalukha/Blue_Whale/actions/runs/45453006374

## Things I fixed after review of my own first version

- `previous_version` had no upper bound: `10**30` was accepted and returned `10**30 + 1`. It is now `0..1000000`.
- 8 existing + 8 new decisions produced a 16-decision checkpoint that the tool itself would refuse as input. That merge is now refused with a message that tells the model what to do next.
- The MCP door declared `previous_version: int`, so MCP clients were told there were no bounds even though the gate enforced them. The new constraint-comparison test caught this, and the MCP signature now reuses the same `CheckpointVersion` type.

## Limitations

- All evidence is offline and deterministic. No live-model call was made for this tool.
- The tool previews only. Blue Whale has no trusted checkpoint store yet, so nothing commits a confirmed preview.
- The product targets in `docs/spec.md` (85% drift detection, 80% recovery) are not measured by this homework.
