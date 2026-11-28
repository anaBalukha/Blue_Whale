# HW2 Verification Evidence — Mikheili Kakhniashvili

## Five golden cases

| ID | Type | Expected | Verified locally |
|---|---|---|---|
| n1 | Normal | Retrieve approved MVP interface source | Pass |
| n2 | Normal | Retrieve accuracy target source | Pass |
| n3 | Normal | Retrieve explicit user override source | Pass |
| b1 | Bad input | Reject limit=100 | Pass |
| a1 | Adversarial | Reject forged caller_id | Pass |

## Green run

GitHub Actions branch run:
https://github.com/anaBalukha/Blue_Whale/actions/runs/42426180338

Local full suite: 40 passed.

## Red run

Red PR: https://github.com/anaBalukha/Blue_Whale/pull/21
Red pull-request CI: https://github.com/anaBalukha/Blue_Whale/actions/runs/42428950594
GitHub showed the failing `ci / test` check as Required and displayed `Merging is blocked`. Approval was also required.
Changing `extra="forbid"` to `extra="ignore"` caused 4 tests to fail while 36 passed. The adversarial case showed that an unexpected `caller_id` could bypass the strict input contract. The test gate detected this regression before it could reach main.

## Both-door verification

Function-calling gate: tested offline.
MCP in-memory client: tested offline, including real trusted documents.
Model-generated live tool call: not performed; API key unavailable.

## Product PR

Product PR: https://github.com/anaBalukha/Blue_Whale/pull/20
Green pull-request CI: https://github.com/anaBalukha/Blue_Whale/actions/runs/42426609593

## Human verification

I checked the tool's input validation, execution gates,
MCP integration and test results. The initial implementation
did not correctly reject extra MCP arguments, so raw-request
validation was added. An incorrectly specified retrieval
golden was corrected to test source relevance rather than
answer generation.

I verified the final implementation with 40 passing local
tests, green GitHub Actions, and a deliberately failing
contract-regression PR. Four regression tests failed as
expected, and branch protection blocked the merge.

The live model-driven call was not tested because an
OpenRouter API key was unavailable.

## Final main-branch verification

Product PR #20 was approved by Ana and merged.
The post-merge CI run passed:
https://github.com/anaBalukha/Blue_Whale/actions/runs/42429188145


## Final HW2 verification follow-up

Date: 2026-11-28.

The original 40-test result and historical red and
green CI evidence remain unchanged.

### Subsequent corrections

- [PR #25](https://github.com/anaBalukha/Blue_Whale/pull/25):
  Tool error handling and regression verification.
- [PR #26](https://github.com/anaBalukha/Blue_Whale/pull/26):
  Sanitized errors and audit-log failure handling.
- [PR #49](https://github.com/anaBalukha/Blue_Whale/pull/49):
  Shared MCP protocol validation and schema correction.
- [PR #51](https://github.com/anaBalukha/Blue_Whale/pull/51):
  Week 7 consequential-action journal reflection.
- [PR #58](https://github.com/anaBalukha/Blue_Whale/pull/58):
  Separate shared Lab 5 grounded-answer tool.

My individual retrieval tool remains distinct from the
shared grounded-answer tool, which was introduced later.

### Issue #61: Test-first correction

Six additional protocol regression cases reproduced a
schema discrepancy involving trailing newline characters.

Runtime validation already rejected these inputs, but
the published schemas incorrectly accepted them under
the tested JSON Schema validator.

A seventh regression case reproduced a non-actionable
empty-corpus error.

Before correction:

- 7 expected failures.
- 13 passing existing cases.

After correction:

- The same selection passed all 20 tests.
- No existing tests or runtime restrictions were weakened.

The published schemas now explicitly reject line
terminators. The empty-corpus failure tells the model
to ask the operator to restore the trusted documents.

The expected failures above are local test-first evidence,
not a replacement for the historical red CI experiment.

### Measured verification

| Check | Actual result |
|---|---|
| Protocol and error-handling tests | 30/30 passed |
| Individual retrieval and gate tests | 28/28 passed |
| Misha HW2 goldens | 5/5 passed |
| Ana HW2 goldens | 5/5 passed |
| All tool goldens and coverage | 21/21 passed |
| Full product regression | 185/185 passed |
| Offline RAG goldens | 5/5 passed |
| Python compilation | Passed |
| Dependency consistency | Passed |
| Git whitespace validation | Passed |

Configuration: BLUE_WHALE_OFFLINE=1,
BLUE_WHALE_MIN_SCORE=0.30, retrieval k=5.

### Reproduction

Run from the repository root:

    BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m pytest -q tests

The new cases are in tests/test_mcp_protocol_boundary.py
and tests/test_misha_tool_errors.py.

### Limitations

The original API-key limitation describes the historical
implementation period. This verification was performed
offline and required no paid model requests.

MCP verification uses the actual SDK client with
in-memory transport. Live provider-specific schema
compatibility and live model-driven tool selection
are not established by these tests.

Strict runtime integer validation is retained even
where JSON Schema validators accept integral floats.

## Extended contract verification references

Date: 2026-11-28.

The individual contract was condensed to follow the course
template. Extended technical references are retained here.

- [Previous detailed contract](https://github.com/anaBalukha/Blue_Whale/blob/f1382833ac460448a45f497e698bd18026eab8b4/hw2/mishakakhniashvili/contract.md)
- [Input contract](../../src/contracts.py)
- [Retrieval tool](../../src/misha_retrieval_tool.py)
- [Registry](../../src/tools.py)
- [Execution gate](../../src/act.py)
- [MCP server](../../src/mcp_server.py)
- [Direct retrieval tests](../../tests/test_misha_retrieval_tool.py)
- [MCP tests](../../tests/test_misha_mcp.py)
- [Error-handling tests](../../tests/test_misha_tool_errors.py)
- [Shared protocol tests](../../tests/test_mcp_protocol_boundary.py)
- [Gate tests](../../tests/test_tool_gates.py)
- [Golden runner](../../tests/test_tool_golden.py)
- [Individual golden cases](../../evals/tools/mishakakhniashvili.yaml)

Both interfaces enforce the same SearchArguments contract.
Invalid arguments are rejected before retrieval executes.

Audit logging is configurable using BLUE_WHALE_TOOL_LOG.
The audit log excludes raw questions, retrieved content,
caller identity and arbitrary unknown argument names.

The shared executor returns a safe failure if audit logging
is unavailable, without revealing the configured path.
That failure cannot be recorded in the unavailable log.

The individual search_trusted_sources tool remains distinct
from the shared answer_from_trusted_sources tool introduced
in PR #58.

PR #62 corrected the published schema discrepancy and
introduced an actionable empty-corpus failure message.

All seven new regression cases passed. The shared product
suite reached 185 passing tests and all five individual
golden cases remained green.

- [PR #62](https://github.com/anaBalukha/Blue_Whale/pull/62)
- [Successful CI](https://github.com/anaBalukha/Blue_Whale/actions/runs/46095902952)

## Lab 8 template: concrete execution evidence

Execution date: 2026-11-28.
Tested commit: `219d9058e6f90930e0ce63314e8a8dcdb63bede0`.

**Cases:** `evals/tools/mishakakhniashvili.yaml`, executed by `tests/test_tool_golden.py` in CI job `test`.

All calls use caller=null (visitor). The YAML arguments are represented below as JSON.

| ID | Type | Actual arguments | Expected | Actual outcome | Pass? |
|---|---|---|---|---|---|
| n1 | normal | `{"question":"Which interface is planned for Blue Whale MVP?","limit":3}` | `{"expect":"ok","must_include_document":"project/terminal-first"}` | `{"ok":true,"count":3,"documents":["project/terminal-first","project/blue-whale-spec","project/terminal-first"]}` | Pass |
| n2 | normal | `{"question":"What is the target drift detection accuracy?","limit":3}` | `{"expect":"ok","must_include_document":"project/blue-whale-spec"}` | `{"ok":true,"count":3,"documents":["project/blue-whale-spec","project/terminal-first","project/blue-whale-spec"]}` | Pass |
| n3 | normal | `{"question":"Does an explicit user change count as drift?","limit":3}` | `{"expect":"ok","must_include_document":"project/explicit-user-changes"}` | `{"ok":true,"count":3,"documents":["project/explicit-user-changes","project/blue-whale-spec","project/explicit-user-changes"]}` | Pass |
| b1 | bad-input | `{"question":"Which interface is planned for Blue Whale MVP?","limit":100}` | `{"expect":"refused","error_has":["invalid arguments","limit"]}` | `{"ok":false,"result":null,"error":"invalid arguments: limit: Value is above the allowed maximum"}` | Pass |
| a1 | adversarial | `{"question":"Which interface is planned for Blue Whale MVP?","caller_id":"another-user"}` | `{"expect":"refused","error_has":["invalid arguments","caller_id"]}` | `{"ok":false,"result":null,"error":"invalid arguments: caller_id: Remove this unexpected argument"}` | Pass |

**Adversarial intent:** Inject another caller's identity through caller_id to bypass the application's trusted caller context.

### Complete actual golden results

The table above summarizes the observed results. The following is the complete captured output, including all excerpts, scores and exact refusal messages.

    [
      {
        "case": {
          "id": "n1",
          "type": "normal",
          "why": "Finds the approved MVP interface decision.",
          "tool": "search_trusted_sources",
          "caller": null,
          "arguments": {
            "question": "Which interface is planned for Blue Whale MVP?",
            "limit": 3
          },
          "expect": "ok",
          "must_include_document": "project/terminal-first"
        },
        "actual": {
          "ok": true,
          "result": {
            "count": 3,
            "sources": [
              {
                "chunk_id": "project/terminal-first#2",
                "document_id": "project/terminal-first",
                "title": "Decision 001 - Terminal-first MVP",
                "section": "Context",
                "excerpt": "Blue Whale needs a simple interface to test conversation drift detection and recovery.",
                "score": 0.4747
              },
              {
                "chunk_id": "project/blue-whale-spec#10",
                "document_id": "project/blue-whale-spec",
                "title": "Spec v0 · Blue Whale",
                "section": "Lab 1 AI critique decisions",
                "excerpt": "- Interface: A terminal application for the MVP. A web interface is deferred.\n- State: Automatically track conversation state in memory. Explicit user changes override older decisions.\n- Recovery: Regenerate once after detecting drift. If recovery fails, warn the user and request clarification.",
                "score": 0.4324
              },
              {
                "chunk_id": "project/terminal-first#5",
                "document_id": "project/terminal-first",
                "title": "Decision 001 - Terminal-first MVP",
                "section": "Consequences",
                "excerpt": "The MVP will use command-line interaction. A web interface is deferred.",
                "score": 0.4479
              }
            ]
          },
          "error": null
        },
        "passed": true
      },
      {
        "case": {
          "id": "n2",
          "type": "normal",
          "why": "Retrieves the numeric drift accuracy target.",
          "tool": "search_trusted_sources",
          "caller": null,
          "arguments": {
            "question": "What is the target drift detection accuracy?",
            "limit": 3
          },
          "expect": "ok",
          "must_include_document": "project/blue-whale-spec"
        },
        "actual": {
          "ok": true,
          "result": {
            "count": 3,
            "sources": [
              {
                "chunk_id": "project/blue-whale-spec#3",
                "document_id": "project/blue-whale-spec",
                "title": "Spec v0 · Blue Whale",
                "section": "Success criteria",
                "excerpt": "1. **Drift detection accuracy:** correctly classify at least 85% of cases in a labeled benchmark of at least 50 conversation examples containing both drift and non-drift cases.\n2. **Recovery success:** in at least 80% of confirmed drift cases, the corrected response follows the latest valid user requirements and expected conversation state.\n3. **Po",
                "score": 0.4363
              },
              {
                "chunk_id": "project/terminal-first#2",
                "document_id": "project/terminal-first",
                "title": "Decision 001 - Terminal-first MVP",
                "section": "Context",
                "excerpt": "Blue Whale needs a simple interface to test conversation drift detection and recovery.",
                "score": 0.4152
              },
              {
                "chunk_id": "project/blue-whale-spec#11",
                "document_id": "project/blue-whale-spec",
                "title": "Spec v0 · Blue Whale",
                "section": "Success criteria verification",
                "excerpt": "- Detection: At least 85% accuracy on 50 or more labeled cases, including drift, no drift, and intentional changes.\n- Recovery: At least 80% of confirmed drift cases must produce responses consistent with the latest trusted state.\n- Consistency: At least 90% of successful recoveries must remain consistent in the next response.",
                "score": 0.3882
              }
            ]
          },
          "error": null
        },
        "passed": true
      },
      {
        "case": {
          "id": "n3",
          "type": "normal",
          "why": "Retrieves the explicit-user-override decision.",
          "tool": "search_trusted_sources",
          "caller": null,
          "arguments": {
            "question": "Does an explicit user change count as drift?",
            "limit": 3
          },
          "expect": "ok",
          "must_include_document": "project/explicit-user-changes"
        },
        "actual": {
          "ok": true,
          "result": {
            "count": 3,
            "sources": [
              {
                "chunk_id": "project/explicit-user-changes#3",
                "document_id": "project/explicit-user-changes",
                "title": "Decision 002 - Explicit User Changes Take Priority",
                "section": "Decision",
                "excerpt": "An explicit user-approved change supersedes the corresponding earlier decision.\nChanges introduced only by the AI are treated as potential conversation drift.\nAmbiguous changes require user confirmation.",
                "score": 0.5438
              },
              {
                "chunk_id": "project/blue-whale-spec#6",
                "document_id": "project/blue-whale-spec",
                "title": "Spec v0 · Blue Whale",
                "section": "Acceptance criteria",
                "excerpt": "1. **State tracking:** after a user message, the system produces or updates a structured state containing the main task, current goal, requirements, technology choices, decisions, completed work, and next step. An explicit user change replaces the conflicting older value.\n\n2. **Drift detection:** given a conversation where PostgreSQL is an establis",
                "score": 0.373
              },
              {
                "chunk_id": "project/explicit-user-changes#2",
                "document_id": "project/explicit-user-changes",
                "title": "Decision 002 - Explicit User Changes Take Priority",
                "section": "Context",
                "excerpt": "Blue Whale must detect when an AI contradicts previously established requirements.\nHowever, users must remain free to intentionally change those requirements.",
                "score": 0.3759
              }
            ]
          },
          "error": null
        },
        "passed": true
      },
      {
        "case": {
          "id": "b1",
          "type": "bad-input",
          "why": "Rejects limits outside the accepted range.",
          "tool": "search_trusted_sources",
          "caller": null,
          "arguments": {
            "question": "Which interface is planned for Blue Whale MVP?",
            "limit": 100
          },
          "expect": "refused",
          "error_has": [
            "invalid arguments",
            "limit"
          ]
        },
        "actual": {
          "ok": false,
          "result": null,
          "error": "invalid arguments: limit: Value is above the allowed maximum"
        },
        "passed": true
      },
      {
        "case": {
          "id": "a1",
          "type": "adversarial",
          "why": "Prevents a model from injecting caller identity.",
          "tool": "search_trusted_sources",
          "caller": null,
          "arguments": {
            "question": "Which interface is planned for Blue Whale MVP?",
            "caller_id": "another-user"
          },
          "expect": "refused",
          "error_has": [
            "invalid arguments",
            "caller_id"
          ]
        },
        "actual": {
          "ok": false,
          "result": null,
          "error": "invalid arguments: caller_id: Remove this unexpected argument"
        },
        "passed": true
      }
    ]

### Repeated identical call

Actual arguments and both complete functional results:

    {
      "arguments": {
        "question": "Which interface is planned for Blue Whale MVP?",
        "limit": 3
      },
      "first": {
        "ok": true,
        "result": {
          "count": 3,
          "sources": [
            {
              "chunk_id": "project/terminal-first#2",
              "document_id": "project/terminal-first",
              "title": "Decision 001 - Terminal-first MVP",
              "section": "Context",
              "excerpt": "Blue Whale needs a simple interface to test conversation drift detection and recovery.",
              "score": 0.4747
            },
            {
              "chunk_id": "project/blue-whale-spec#10",
              "document_id": "project/blue-whale-spec",
              "title": "Spec v0 · Blue Whale",
              "section": "Lab 1 AI critique decisions",
              "excerpt": "- Interface: A terminal application for the MVP. A web interface is deferred.\n- State: Automatically track conversation state in memory. Explicit user changes override older decisions.\n- Recovery: Regenerate once after detecting drift. If recovery fails, warn the user and request clarification.",
              "score": 0.4324
            },
            {
              "chunk_id": "project/terminal-first#5",
              "document_id": "project/terminal-first",
              "title": "Decision 001 - Terminal-first MVP",
              "section": "Consequences",
              "excerpt": "The MVP will use command-line interaction. A web interface is deferred.",
              "score": 0.4479
            }
          ]
        },
        "error": null
      },
      "second": {
        "ok": true,
        "result": {
          "count": 3,
          "sources": [
            {
              "chunk_id": "project/terminal-first#2",
              "document_id": "project/terminal-first",
              "title": "Decision 001 - Terminal-first MVP",
              "section": "Context",
              "excerpt": "Blue Whale needs a simple interface to test conversation drift detection and recovery.",
              "score": 0.4747
            },
            {
              "chunk_id": "project/blue-whale-spec#10",
              "document_id": "project/blue-whale-spec",
              "title": "Spec v0 · Blue Whale",
              "section": "Lab 1 AI critique decisions",
              "excerpt": "- Interface: A terminal application for the MVP. A web interface is deferred.\n- State: Automatically track conversation state in memory. Explicit user changes override older decisions.\n- Recovery: Regenerate once after detecting drift. If recovery fails, warn the user and request clarification.",
              "score": 0.4324
            },
            {
              "chunk_id": "project/terminal-first#5",
              "document_id": "project/terminal-first",
              "title": "Decision 001 - Terminal-first MVP",
              "section": "Consequences",
              "excerpt": "The MVP will use command-line interaction. A web interface is deferred.",
              "score": 0.4479
            }
          ]
        },
        "error": null
      },
      "equal": true
    }

The comparison excludes timestamps and execution latency. Both calls returned identical retrieval results. Audit records may differ, but project decisions are unchanged.

### Through the MCP door

Client: Python MCP SDK 2.3.0, using Client(mcp) with in-memory transport.

Requests were issued programmatically. No natural-language model prompt or model-selected tool sequence is claimed.

Actual discovery, valid retrieval and adversarial request:

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
        "tool": "search_trusted_sources",
        "arguments": {
          "question": "Which interface is planned for Blue Whale MVP?",
          "limit": 3
        },
        "is_error": false,
        "structured_content": {
          "count": 3,
          "sources": [
            {
              "chunk_id": "project/terminal-first#2",
              "document_id": "project/terminal-first",
              "title": "Decision 001 - Terminal-first MVP",
              "section": "Context",
              "excerpt": "Blue Whale needs a simple interface to test conversation drift detection and recovery.",
              "score": 0.4747
            },
            {
              "chunk_id": "project/blue-whale-spec#10",
              "document_id": "project/blue-whale-spec",
              "title": "Spec v0 · Blue Whale",
              "section": "Lab 1 AI critique decisions",
              "excerpt": "- Interface: A terminal application for the MVP. A web interface is deferred.\n- State: Automatically track conversation state in memory. Explicit user changes override older decisions.\n- Recovery: Regenerate once after detecting drift. If recovery fails, warn the user and request clarification.",
              "score": 0.4324
            },
            {
              "chunk_id": "project/terminal-first#5",
              "document_id": "project/terminal-first",
              "title": "Decision 001 - Terminal-first MVP",
              "section": "Consequences",
              "excerpt": "The MVP will use command-line interaction. A web interface is deferred.",
              "score": 0.4479
            }
          ]
        },
        "text": [
          "{\"count\": 3, \"sources\": [{\"chunk_id\": \"project/terminal-first#2\", \"document_id\": \"project/terminal-first\", \"title\": \"Decision 001 - Terminal-first MVP\", \"section\": \"Context\", \"excerpt\": \"Blue Whale needs a simple interface to test conversation drift detection and recovery.\", \"score\": 0.4747}, {\"chunk_id\": \"project/blue-whale-spec#10\", \"document_id\": \"project/blue-whale-spec\", \"title\": \"Spec v0 · Blue Whale\", \"section\": \"Lab 1 AI critique decisions\", \"excerpt\": \"- Interface: A terminal application for the MVP. A web interface is deferred.\\n- State: Automatically track conversation state in memory. Explicit user changes override older decisions.\\n- Recovery: Regenerate once after detecting drift. If recovery fails, warn the user and request clarification.\", \"score\": 0.4324}, {\"chunk_id\": \"project/terminal-first#5\", \"document_id\": \"project/terminal-first\", \"title\": \"Decision 001 - Terminal-first MVP\", \"section\": \"Consequences\", \"excerpt\": \"The MVP will use command-line interaction. A web interface is deferred.\", \"score\": 0.4479}]}"
        ]
      },
      {
        "method": "call_tool",
        "tool": "search_trusted_sources",
        "arguments": {
          "question": "Which interface is planned for Blue Whale MVP?",
          "caller_id": "another-user"
        },
        "is_error": true,
        "structured_content": null,
        "text": [
          "invalid arguments: caller_id: Remove this unexpected argument"
        ]
      }
    ]

### Exact historical CI evidence

**Red run**

- Branch: `hw2-misha-red-proof`
- PR: [#21](https://github.com/anaBalukha/Blue_Whale/pull/21), closed without merging.
- Temporary branch: deleted.
- [Failed CI run](https://github.com/anaBalukha/Blue_Whale/actions/runs/42428950594)
- CI job: `test`

Deliberate weakening of the SearchArguments contract:

    - model_config = ConfigDict(extra="forbid")
    + model_config = ConfigDict(extra="ignore")

Exact failed test names from the historical CI log:

    FAILED tests/test_misha_mcp.py::test_mcp_contract_rejects_unknown_fields
    FAILED tests/test_misha_retrieval_tool.py::test_unknown_arguments_are_forbidden
    FAILED tests/test_tool_gates.py::test_identity_spoofing_refused
    FAILED tests/test_tool_golden.py::test_tool_golden_case[mishakakhniashvili-case4]
    4 failed, 36 passed in 1.35s

The original verification evidence records the required
ci / test check failing and GitHub displaying:

    Merging is blocked

The wording is retained from the original evidence,
rather than reconstructed from the CI log.

**What the red run taught me**

Changing extra="forbid" to extra="ignore" allowed
unexpected arguments to be silently discarded.
The direct validation, MCP, execution-gate and adversarial
golden tests all detected that change. A bounded search
limit and restricted question pattern do not prevent
identity injection if unexpected fields are accepted.
Strict rejection of additional fields is therefore
a separate necessary contract restriction.

**Green run**

- Product PR: [#20](https://github.com/anaBalukha/Blue_Whale/pull/20)
- Product merge commit: `0aca4b1ba752ad7faa9bd049133aca3e5861974d`
- [Successful CI run](https://github.com/anaBalukha/Blue_Whale/actions/runs/42426609593)
- CI job: `test`

Exact historical pytest summary:

    40 passed in 0.94s

These historical results are distinct from the subsequent
185-test regression suite and the current five-case
execution evidence.

## Final contract and external MCP verification

Date: 2026-11-28.

Tested commit: `a257bbc9aee45dc93e47c3c65c1c726ff657ba2f`.

### Exact validation messages

Ten invalid requests were exercised through call_tool() and the actual MCP SDK client. Every request was rejected, and both interfaces returned identical error messages.

| Case | Exact arguments | Actual error | Both doors |
|---|---|---|---|
| missing_question | `{}` | `invalid arguments: question: Provide this required argument` | Pass |
| invalid_pattern | `{"question":"../../.env"}` | `invalid arguments: question: Use only permitted characters` | Pass |
| too_short | `{"question":"Hi"}` | `invalid arguments: question: Text is too short` | Pass |
| too_long | `{"question":"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"}` | `invalid arguments: question: Text is too long` | Pass |
| wrong_type | `{"question":123}` | `invalid arguments: question: Provide a string` | Pass |
| invalid_integer | `{"question":"Which interface is planned for Blue Whale MVP?","limit":"3"}` | `invalid arguments: limit: Provide an integer` | Pass |
| below_minimum | `{"question":"Which interface is planned for Blue Whale MVP?","limit":0}` | `invalid arguments: limit: Value is below the allowed minimum` | Pass |
| above_maximum | `{"question":"Which interface is planned for Blue Whale MVP?","limit":100}` | `invalid arguments: limit: Value is above the allowed maximum` | Pass |
| forged_identity | `{"question":"Which interface is planned for Blue Whale MVP?","caller_id":"another-user"}` | `invalid arguments: caller_id: Remove this unexpected argument` | Pass |
| unexpected_argument | `{"question":"Which interface is planned for Blue Whale MVP?","unexpected":true}` | `invalid arguments: unexpected_argument: Remove this unexpected argument` | Pass |

All ten invalid-input cases passed.

The MCP and function-calling input schemas also matched exactly in this verification.

### External MCP host demonstration

Host: VS Code Agent Chat.

Workspace: Blue_Whale_Ana.

MCP server shown by the host: blue-whale-lab5.

The natural-language prompt was:

> Use the Blue Whale MCP tool search_trusted_sources to find which interface is planned for the Blue Whale MVP. Set limit to 3. Show the tool call and returned sources.

The host displayed an actual execution of search_trusted_sources with these arguments:

```json
{
  "question": "Which interface is planned for the Blue Whale MVP?",
  "limit": 3
}
```

### Sources displayed by the host

1. Decision 001 - Terminal-first MVP: Blue Whale needs a simple interface to test conversation drift detection and recovery.

2. Spec v0 - Blue Whale: Interface: A terminal application for the MVP. A web interface is deferred.

3. Decision 001 - Terminal-first MVP: The MVP will use command-line interaction. A web interface is deferred.

Observed answer: The planned MVP interface is terminal-first (command-line).

The displayed tool-call sequence contained one search_trusted_sources invocation.

These observations are transcribed from the external host display, not represented as raw MCP protocol output. Complete SDK responses are retained in the earlier evidence sections.

The demonstration confirms external MCP host integration. It does not establish live OpenRouter integration or live embedding quality.

Earlier external host evidence is available in [streaming-evidence.md](../../docs/streaming-evidence.md).

Original historical CI evidence is retained.
