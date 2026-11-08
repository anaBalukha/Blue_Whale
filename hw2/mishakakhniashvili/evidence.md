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
