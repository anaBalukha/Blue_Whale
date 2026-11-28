# HW2 Verification Evidence — Ana Balukhashvili

## Five golden cases

File: `evals/tools/anaBalukha.yaml`

| ID | Type | Input and expected result | Verified |
|---|---|---|---|
| ana_n1 | Normal | PostgreSQL changed to MongoDB: `drift` | Pass |
| ana_n2 | Normal | PostgreSQL unchanged: `consistent` | Pass |
| ana_n3 | Normal | Matching terminal interface: `consistent` | Pass |
| ana_b1 | Bad input | Reject `MongoDB!!!` | Pass |
| ana_a1 | Adversarial | Reject fabricated `user_changes` | Pass |

The cases run through the real `call_tool()` validation
gate using `tests/test_tool_golden.py`, without an API key.

## Local verification

On the valid product branch:

| Test | Result |
|---|---|
| Direct drift tool tests | 7 passed |
| MCP tests | 3 passed |
| HW2 golden runner, including both owners | 11 passed |
| Complete team test suite | 64 passed |
| Ana's HW1 regression tests | 4 passed |

The complete suite includes the direct, MCP and golden tests.

Both interfaces were exercised offline. No live-model
tool invocation or external MCP-host demonstration
is claimed.

## Green CI evidence

Product PR:
https://github.com/anaBalukha/Blue_Whale/pull/28

Successful pull-request CI:
https://github.com/anaBalukha/Blue_Whale/actions/runs/42496137209

The product PR was reviewed and merged by
`mishakakhniashvili`.

Successful post-merge CI on `main`:
https://github.com/anaBalukha/Blue_Whale/actions/runs/42498981209

## Red CI experiment

Experimental PR:
https://github.com/anaBalukha/Blue_Whale/pull/29

Failed pull-request CI:
https://github.com/anaBalukha/Blue_Whale/actions/runs/42497154342

I created a separate experimental branch and deliberately
weakened the `DecisionValue` validation pattern from its
restricted character set to `^.*$`.

The weakened contract incorrectly accepted an invalid
decision value. The direct validation test and Ana's
bad-input golden case detected the regression.

GitHub Actions reported failed required checks and
blocked merging. PR #29 was closed without merging.

The experimental PR also contained the product commit
because it branched from the unmerged product branch;
the deliberate regression itself changed only the
`DecisionValue` pattern in `src/contracts.py`.

The working product contract was not weakened or merged
with the experimental change.

## What the red CI run taught me

A tool can still return plausible results when its input
contract is too permissive. Successful normal cases alone
would not detect that regression. The bad-input golden
and direct validation test proved that the stricter
contract mattered and that CI would catch its removal.

## Human verification

I ran the implementation locally, checked the output
of the tests, repaired an integration-script assertion
failure, and corrected a Python virtual-environment issue.

The product branch passed the full test suite, and
Misha reviewed and merged PR #28.

## Remaining limitations

The tool assumes that an application supplies trustworthy
previous decisions. It does not prove the origin of the
supplied state, manage session memory, or implement
automatic state recovery.

## Red experiment branch cleanup

Date: 2026-11-24

The temporary remote branch test-ana-hw2-red-contract
was successfully deleted.

PR #29 remains closed without merging.

Red CI evidence:

https://github.com/anaBalukha/Blue_Whale/pull/29

https://github.com/anaBalukha/Blue_Whale/actions/runs/42497154342

## Final HW2 verification follow-up

Date: 2026-11-28.

The original product and red CI measurements above
remain unchanged as historical evidence.

### Subsequent corrections

- [PR #49](https://github.com/anaBalukha/Blue_Whale/pull/49):
  MCP validation boundary, sanitized errors, audit coverage
  and published schema corrections.
- [PR #53](https://github.com/anaBalukha/Blue_Whale/pull/53):
  Week 7 journal and consequential checkpoint confirmation.
- [PR #58](https://github.com/anaBalukha/Blue_Whale/pull/58):
  Separate shared Lab 5 grounded-answer tool.

The individual check_decision_drift function is distinct
from the shared answer_from_trusted_sources tool.

The shared tool was introduced after the original
individual HW2 implementation.

### Week 6 Session State experiment

Experiment date: 2026-11-28.

Four independent offline calls were executed through
the actual shared call_tool gate.

| Previous state | Candidate | Observed result |
|---|---|---|
| PostgreSQL | PostgreSQL | consistent |
| Missing | MongoDB | Validation failure |
| Terminal interface only | MongoDB | consistent |
| PostgreSQL | MongoDB | drift |

The missing-state call returned:

    invalid arguments: state: Provide this required argument

The final call returned a database conflict:

    field: database
    expected: PostgreSQL
    proposed: MongoDB

The experiment demonstrates that the tool does not retain
previous decisions across these calls. A consistent result
does not establish that the supplied state is complete
or authentic.

Both Pattern Journal copies record this observation.

### Current verification

| Check | Actual result |
|---|---|
| Direct, MCP and shared protocol tests | 27/27 passed |
| Individual HW2 goldens | 5/5 passed |
| Full product regression | 178/178 passed |
| Session State experiment | 4/4 expected outcomes |
| Python compilation | Passed |

Configuration: BLUE_WHALE_OFFLINE=1 and
BLUE_WHALE_MIN_SCORE=0.30.

### External MCP observation

An earlier VS Code demonstration displayed the actual
check_decision_drift tool returning drift for a proposed
change from PostgreSQL to MongoDB.

This records the earlier observation, not a new external
host execution.

### Limitations

Persistent session storage, state authentication and
checkpoint confirmation remain separate project work.

Live model-driven execution is not established by these
offline tests.

Exact JSON Schema parity for every edge case is not
claimed by this verification.

No paid API requests were required.

## Extended contract verification references

Date: 2026-11-28.

The individual contract was condensed to follow the course
template. Extended technical references are retained here.

- [Previous detailed contract](https://github.com/anaBalukha/Blue_Whale/blob/7653ffeb66c0aa5ff4ae3aab34edee7cf2358d5c/hw2/anaBalukha/contract.md)
- [Input contract](../../src/contracts.py)
- [Original comparison function](../../src/drift_core.py)
- [Drift tool](../../src/ana_drift_tool.py)
- [Registry](../../src/tools.py)
- [Execution gate](../../src/act.py)
- [MCP server](../../src/mcp_server.py)
- [Direct tests](../../tests/test_ana_drift_tool.py)
- [MCP tests](../../tests/test_ana_mcp.py)
- [Shared protocol tests](../../tests/test_mcp_protocol_boundary.py)
- [Gate tests](../../tests/test_tool_gates.py)
- [Golden runner](../../tests/test_tool_golden.py)
- [Individual golden cases](../../evals/tools/anaBalukha.yaml)

The tool never accepts model-supplied user_changes.
It neither authenticates nor persists supplied state.

Audit logging is configurable using BLUE_WHALE_TOOL_LOG.
If logging fails, the shared executor returns a safe failure.
Validation errors use sanitized field locations.

The individual drift tool remains distinct from the shared
answer_from_trusted_sources tool introduced in PR #58.

PR #62 subsequently hardened the shared published schemas
without weakening runtime constraints. Ana's five golden
cases passed, and the shared suite reached 185 passing tests.

- [PR #62](https://github.com/anaBalukha/Blue_Whale/pull/62)
- [Successful CI](https://github.com/anaBalukha/Blue_Whale/actions/runs/46095902952)

## Lab 8 template: concrete execution evidence

Execution date: 2026-11-28.
Tested commit: `ecc59d3c8f5a48777a2da0f58f26a9563fe4fa18`.

**Cases:** `evals/tools/anaBalukha.yaml`, executed by `tests/test_tool_golden.py` in CI job `test`.

All calls use caller=null (visitor). Arguments below are the YAML arguments represented as JSON.

| ID | Type | Actual arguments | Expected | Actual result/error | Pass? |
|---|---|---|---|---|---|
| ana_n1 | normal | `{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}` | `{"expect":"ok","result_has":{"status":"drift"}}` | `{"ok":true,"result":{"status":"drift","effective_state":{"database":"PostgreSQL"},"conflicts":[{"field":"database","expected":"PostgreSQL","proposed":"MongoDB"}]},"error":null}` | Pass |
| ana_n2 | normal | `{"state":{"database":"PostgreSQL"},"candidate":{"database":"PostgreSQL"}}` | `{"expect":"ok","result_has":{"status":"consistent"}}` | `{"ok":true,"result":{"status":"consistent","effective_state":{"database":"PostgreSQL"},"conflicts":[]},"error":null}` | Pass |
| ana_n3 | normal | `{"state":{"interface":"terminal","database":"PostgreSQL"},"candidate":{"interface":"terminal"}}` | `{"expect":"ok","result_has":{"status":"consistent"}}` | `{"ok":true,"result":{"status":"consistent","effective_state":{"interface":"terminal","database":"PostgreSQL"},"conflicts":[]},"error":null}` | Pass |
| ana_b1 | bad-input | `{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB!!!"}}` | `{"expect":"refused","error_has":["invalid arguments"]}` | `{"ok":false,"result":null,"error":"invalid arguments: candidate.unexpected_argument: Use only permitted characters"}` | Pass |
| ana_a1 | adversarial | `{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"},"user_changes":{"database":"MongoDB"}}` | `{"expect":"refused","error_has":["invalid arguments","unexpected_argument"]}` | `{"ok":false,"result":null,"error":"invalid arguments: unexpected_argument: Remove this unexpected argument"}` | Pass |

**Adversarial intent:** Make a proposed MongoDB decision appear user-approved by injecting an unauthorized user_changes argument.

### Repeated identical call

Actual arguments and both functional results:

```json
{
  "arguments": {
    "state": {
      "database": "PostgreSQL"
    },
    "candidate": {
      "database": "MongoDB"
    }
  },
  "first": {
    "ok": true,
    "result": {
      "status": "drift",
      "effective_state": {
        "database": "PostgreSQL"
      },
      "conflicts": [
        {
          "field": "database",
          "expected": "PostgreSQL",
          "proposed": "MongoDB"
        }
      ]
    },
    "error": null
  },
  "second": {
    "ok": true,
    "result": {
      "status": "drift",
      "effective_state": {
        "database": "PostgreSQL"
      },
      "conflicts": [
        {
          "field": "database",
          "expected": "PostgreSQL",
          "proposed": "MongoDB"
        }
      ]
    },
    "error": null
  },
  "equal": true
}
```

The comparison excludes execution timestamps and latency. Audit records may differ; project decisions are not modified.

### Through the MCP door

Client: Python MCP SDK 2.3.0, using Client(mcp) with in-memory transport.

The requests were issued programmatically; no natural-language prompt or model-selected tool sequence is claimed.

Actual discovery, valid request and adversarial request:

```json
[
  {
    "method": "list_tools",
    "result": [
      "search_trusted_sources",
      "check_decision_drift",
      "preview_checkpoint_update",
      "answer_from_trusted_sources"
    ]
  },
  {
    "method": "call_tool",
    "tool": "check_decision_drift",
    "arguments": {
      "state": {
        "database": "PostgreSQL"
      },
      "candidate": {
        "database": "MongoDB"
      }
    },
    "is_error": false,
    "structured_content": {
      "status": "drift",
      "effective_state": {
        "database": "PostgreSQL"
      },
      "conflicts": [
        {
          "field": "database",
          "expected": "PostgreSQL",
          "proposed": "MongoDB"
        }
      ]
    },
    "text": [
      "{\"status\": \"drift\", \"effective_state\": {\"database\": \"PostgreSQL\"}, \"conflicts\": [{\"field\": \"database\", \"expected\": \"PostgreSQL\", \"proposed\": \"MongoDB\"}]}"
    ]
  },
  {
    "method": "call_tool",
    "tool": "check_decision_drift",
    "arguments": {
      "state": {
        "database": "PostgreSQL"
      },
      "candidate": {
        "database": "MongoDB"
      },
      "user_changes": {
        "database": "MongoDB"
      }
    },
    "is_error": true,
    "structured_content": null,
    "text": [
      "invalid arguments: unexpected_argument: Remove this unexpected argument"
    ]
  }
]
```

### Exact historical CI evidence

**Red run**

- Branch: `test-ana-hw2-red-contract`
- PR: [#29](https://github.com/anaBalukha/Blue_Whale/pull/29), closed without merging.
- Temporary branch: deleted.
- [Failed CI run](https://github.com/anaBalukha/Blue_Whale/actions/runs/42497154342)
- CI job: `test`

Deliberate weakening of the DecisionValue pattern:

    - pattern=r"^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$",
    + pattern=r"^.*$",

Exact failed test names from the historical CI log:

    FAILED tests/test_ana_drift_tool.py::test_invalid_decision_value_is_rejected
    FAILED tests/test_tool_golden.py::test_tool_golden_case[anaBalukha-case3]
    2 failed, 62 passed in 1.54s

The required CI check failed and the merge was blocked.
The exact historical merge-button wording was not retained
in the evidence available for this follow-up.

**What the red run taught me**

The direct validation test failed because the expected
ValidationError was no longer raised. The golden case
failed because the invalid argument produced an unexpected
success. These failures show that extra="forbid" alone
does not protect an allowed field from invalid values.
The value pattern is a separate necessary restriction.

**Green run**

- Product PR: [#28](https://github.com/anaBalukha/Blue_Whale/pull/28)
- Product merge commit: `63e59a9425f08444d84c49278d2baff0f0b262f1`
- [Successful CI run](https://github.com/anaBalukha/Blue_Whale/actions/runs/42496137209)
- CI job: `test`

Exact historical pytest summary:

    64 passed in 1.19s

These historical results are distinct from the later
185-test regression suite and the current five-case
execution evidence.
