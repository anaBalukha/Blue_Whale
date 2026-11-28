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
