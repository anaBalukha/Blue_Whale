# HW1 - AI Delegation Log

## Tool and task
Tool: ChatGPT (GPT-6)

AI was used to help prepare the specification, four pytest tests,
and the Python implementation of the Structured Conversation Drift Checker.

The requested feature compares confirmed decisions with proposed AI
decisions, accepts explicit user changes, and reports invalid input.

## Autonomy and human verification
Autonomy Ladder: Rung 3 - AI generated the code, with human review required before merging.

The AI suggested code and commands, but they were executed locally.
The implementation was verified using four automated tests and three
golden examples with actual terminal outputs.

The source files and expected results should be reviewed before
submission. The feature does not use a live language model.

## What went wrong
The initial testing instructions assumed pytest was available in
the active Python environment. Running the tests produced:
"No module named pytest".

The problem was identified through the terminal error.
A virtual environment was created, activated, and dependencies installed.

There was also a suspicious pasted terminal line while creating
golden.md. The file was inspected using sed, confirming its contents
were correct.

## Final verification
- Automated tests: 4 passed in 0.05s.
- Golden examples: 3 passed.
- Invalid input returned INVALID_INPUT with exit code 2.
- No API credentials were needed.

## Reflection
AI accelerated implementation, but its instructions still required
environment checks and verification against actual outputs.
