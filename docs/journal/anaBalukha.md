# Pattern Journal - Ana Balukhashvili
Retrospective entries written 2026-10-17.

## W1 - Context as Budget
For the drift checker, I limited the required context to confirmed decisions, proposed decisions, and explicit user changes. AI helped define these fields. Next time, I would document ambiguous decisions more carefully.

## W2 - Spec Before Code
I prepared testable acceptance criteria before implementing the Python feature. AI suggested pytest tests, and I verified the implementation by running them. Next time, I would also automate testing of the CLI exit codes.

## W3 - Uncertainty-Aware UX
The application returns a structured error when the input is invalid instead of silently accepting it. I verified this using an invalid JSON structure and exit code 2. Next time, I would provide more helpful error messages.

## W4 - Grounded Generation
I recorded actual application outputs for three golden questions rather than assuming they passed. I compared each result against the expected behavior. This feature does not yet implement document retrieval or source citations; I would add those checks if extending it to grounded AI answers.
