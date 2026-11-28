# Tool contract · Blue Whale · `preview_checkpoint_update` · lexokodavs

*From `Lab-5/templates/tool-contract.md`. Every rule below exists in code:
[`src/lexo_checkpoint_tool.py`](https://github.com/anaBalukha/Blue_Whale/blob/main/src/lexo_checkpoint_tool.py) (`PreviewCheckpointUpdateArgs` at line 33, `run_preview_checkpoint_update` at line 58),
[`src/tools.py`](https://github.com/anaBalukha/Blue_Whale/blob/main/src/tools.py) (`preview_checkpoint_update` registration at line 83, `writes=False` at line 101, `tools_for` at line 106),
[`src/mcp_server.py`](https://github.com/anaBalukha/Blue_Whale/blob/main/src/mcp_server.py) (`call_tool` at line 21, `preview_checkpoint_update` at lines 170 and 191),
[`src/contracts.py`](https://github.com/anaBalukha/Blue_Whale/blob/main/src/contracts.py) (shared `DecisionMap`).
Product PR: [#35](https://github.com/anaBalukha/Blue_Whale/pull/35).*

## `preview_checkpoint_update`

**In one sentence, for the model:** "Calculate a proposed versioned checkpoint and changed fields without modifying trusted state (read-only preview)."

**Read or consequential?** Read. It only computes a proposal from the arguments it is given; it writes nothing except the shared audit-log line, so it is safe for a loop to call any number of times. Committing the proposal would be consequential, and that is deliberately *not* this tool.

| | |
|---|---|
| **Effect** | reads (computes a preview in memory) |
| **Undo** | nothing to undo |
| **Idempotent?** | yes: the same arguments always return the same preview, and nothing is stored, so a second call changes nothing |
| **Offered to** | visitors and signed-in users (`writes=False`, so `tools_for(None)` includes it) |
| **Identity from** | not needed. No identity argument exists; `caller_id` or any other extra field is refused |
| **Touches** | only its own arguments in memory, plus one line in `logs/tools.jsonl` written by the shared gate |
| **Must never** | turn a proposal into a confirmed user decision: it never writes trusted state and never accepts an approval flag such as `authorized=true` |

**Inputs.** Contract class `PreviewCheckpointUpdateArgs` (`src/lexo_checkpoint_tool.py`, line 33), `extra="forbid"`.

| Argument | Type | Constraint | Description the model reads |
|---|---|---|---|
| `previous_version` | strict integer | `0 <= v <= 1000000`; `true`, `"4"`, `4.0` refused | Current trusted checkpoint version (integer from 0 to 1000000). |
| `previous_decisions` | object | 1 to 8 entries; key `^[a-z][a-z0-9_]*$`, 1-32 chars; value `^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$`, 1-80 chars | One to eight project decisions. |
| `proposed_changes` | object | same as above; an empty map is refused | One to eight project decisions. |
| anything else | — | refused: "Remove this unexpected argument" | — |

No defaults: all three arguments are required.

**Result** (`PreviewResult`, `extra="forbid"`).

| Field | Type | Meaning |
|---|---|---|
| `checkpoint.version` | int | `previous_version + 1` if any field changes, otherwise unchanged |
| `checkpoint.decisions` | object (str → str) | previous decisions with the proposed changes applied |
| `changed_fields` | list[str], sorted | keys that are new or whose value differs |
| `requires_confirmation` | bool | `true` exactly when `changed_fields` is non-empty |

**Expected failures.** Validation errors come from the shared gate (`src/act.py`, `brief()`), which never echoes the input.

| When | Message the model reads |
|---|---|
| version below 0 | `invalid arguments: previous_version: Value is below the allowed minimum` |
| version above 1000000 | `invalid arguments: previous_version: Value is above the allowed maximum` |
| version not an integer | `invalid arguments: previous_version: Provide an integer` |
| bad key or value | `invalid arguments: ...: Use only permitted characters` (or too short / too long) |
| `authorized`, `caller_id` or any extra field | `invalid arguments: ...: Remove this unexpected argument` |
| merged checkpoint over 8 decisions | `Proposed checkpoint would exceed 8 decisions. Propose fewer new decision fields or change existing ones.` |
| a change at version 1000000 | `Checkpoint version limit reached. Ask the operator to archive this checkpoint before changing it.` |
| unexpected crash | `Tool execution failed unexpectedly. Ask the operator to check the service, then retry.` |
| audit log unwritable | `Audit logging unavailable. Ask the operator to restore logging and retry.` (result withheld) |

**Tests and golden cases.**

| Case | Expect | Where |
|---|---|---|
| a valid call | runs, version 5, `changed_fields: [database]` | `evals/tools/lexokodavs.yaml` n1; `test_function_calling_door_returns_structured_preview` |
| invalid arguments | refused before the tool runs | yaml b1; `test_invalid_versions_are_rejected`, `test_malformed_or_out_of_range_maps_are_rejected` |
| not offered to this caller | n/a: read-only, offered to everyone | `test_offered_to_visitors_as_read_only` |
| identity in the arguments | refused, tool body never runs | `test_forged_identity_or_approval_never_runs[caller_id]`, `test_mcp_rejects_forged_identity_or_approval` |
| adversarial: `authorized=true` approval forgery | refused | yaml a1 |
| both doors advertise the same limits | same bounds and patterns | `tests/test_lexo_mcp.py::test_mcp_and_function_calling_advertise_same_constraints` |

**Log line.** `logs/tools.jsonl` (path from `BLUE_WHALE_TOOL_LOG`), one line per call:
`ts` (ISO-8601 string), `tool` (str), `ok` (bool), `error` (str or null), `caller_type` (`"visitor"` or `"signed_in"`), `latency_ms` (int).
It deliberately leaves out the arguments, the decision values and the caller id (`test_audit_log_has_outcome_without_decisions`).

**If a commit capability is added later.** A separate tool (for example `commit_confirmed_checkpoint`) would be `writes=True`, so the shared gate already refuses it for visitors and without a separately authorized write handler. It would run only after a human confirmation the application records, never because of a model-supplied flag. It would also check that the stored version still equals `previous_version`, so a stale preview cannot overwrite newer decisions. That tool does not exist yet.
