# HW2 Evidence — Aleksandre Giorgashvili (lexokodavs)

## Tool implementation

- Tool: `preview_checkpoint_update`
- Source: `src/lexo_checkpoint_tool.py`
- Registration: `src/tools.py` (`call_tool` path) and `src/mcp_server.py` (`@mcp.tool(READ_ONLY)` path)
- Owner: Aleksandre Giorgashvili (@lexokodavs)

## Implementation approach

- The tool is a **pure read-only preview**: it takes `previous_version` + `previous_decisions` + `proposed_changes` and computes the proposed checkpoint without touching trusted state.
- Version increments by exactly 1 iff at least one effective change occurs.
- `changed_fields` is a sorted list of keys that would change; no-op proposals leave version unchanged.
- Unknown/extra fields are rejected (`extra="forbid"`); decision keys/values validated by regex.
- No identity or approval arguments accepted. A model-supplied proposal can never be declared authorized by itself.

## Golden cases and results

Five golden cases in `evals/tools/lexokodavs.yaml`, all passing:

| Case | Type | Result |
|---|---|---|
| n1 | normal | Existing decision change → version 5, changed_fields `["database"]`, `requires_confirmation: true` ✅ |
| n2 | normal | New decision added → version 3, changed_fields `["language"]`, existing decisions preserved ✅ |
| n3 | normal | No-op proposal → version unchanged, `changed_fields: []`, `requires_confirmation: false` ✅ |
| b1 | bad-input | Negative version rejected (`invalid arguments`) ✅ |
| a1 | adversarial | Injected extra/forgery argument rejected as `unexpected_argument` ✅ |

Full suite result: **86 passed** (`pytest -q tests hw1/lexokodavs`).

## Red CI demonstration

A deliberate contract regression was prepared to prove that the adversarial contract protection blocks merging:

- Temporary change: `extra="forbid"` → `extra="ignore"` on `PreviewCheckpointUpdateArgs`.
- Expected failure: adversarial golden case fails.
- Status: Pending red-run execution. See Phase 3.

## Limitations

- Offline/in-memory golden execution; no live-model demonstration performed (not explicitly required for individual HW2).
- The 85% drift-detection and 80% recovery targets are product goals, not HW2 results.

## Evidence links

- Product PR: https://github.com/anaBalukha/Blue_Whale/pull/35
- CI run: https://github.com/anaBalukha/Blue_Whale/actions/runs/45442964561
