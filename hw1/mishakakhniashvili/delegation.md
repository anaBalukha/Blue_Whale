# HW1 - AI Delegation Log

## Feature
Golden Test Evaluation Reporter

## AI delegation
Tool: ChatGPT
Autonomy: Rung 3 - AI drafts the implementation; the student
reviews and verifies the results before submission.

I delegated the initial Python implementation, CLI structure,
and pytest test suggestions to ChatGPT. The feature evaluates
expected and actual test statuses, calculates a pass rate,
and reports failed test IDs.

## What went wrong
The initial implementation rounded the displayed pass rate
to two decimals but compared the threshold using the
unrounded value.

With 2 of 3 cases passing and a threshold of 0.67,
the program displayed 0.67 but returned
meets_threshold=false.

## How I detected and corrected it
I executed a boundary case and compared the actual JSON
output against the written specification.

After identifying the inconsistency, I changed the
threshold comparison to use the rounded pass_rate.

I reran the previously failing case and added a regression
test named test_rounded_pass_rate_meets_threshold.

## Verification
- Three CLI golden cases executed successfully.
- Seven automated pytest tests passed.
- The boundary case now returns meets_threshold=true.
- No real model calls or API credentials are required.

The final implementation and verification evidence are
in this individual HW1 folder.
