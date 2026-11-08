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
