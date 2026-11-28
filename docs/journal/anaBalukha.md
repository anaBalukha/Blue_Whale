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

## Week 5 — Tool Contract

**Retrospective reflection — 8 November 2026**

I applied the Tool Contract pattern to my Blue Whale drift
checker. Instead of letting the model call the comparison
function with arbitrary dictionaries, I added a Pydantic
contract with bounded decision keys and values and
`extra="forbid"`.

The tool is read-only and refuses model-provided
`user_changes`, because the model must not invent an
explicit user decision. I verified this with unit tests,
five golden cases, and the MCP interface.

Next time I would check the contract constraints and MCP
schema before writing the integration code, so unsafe
arguments are rejected from the beginning.

## Week 6 — Session State

**Retrospective reflection — 8 November 2026**

The Session State pattern is important for Blue Whale
because the system must distinguish a confirmed earlier
decision from a newer explicit user change.

My HW2 tool compares the `state` and `candidate` arguments
for one call, but does not persist conversation state
between calls. This is a real limitation: the tool
cannot establish whether the supplied earlier state
is authentic or up to date.

I did not implement session storage, retention limits,
or a deletion endpoint as part of this homework.

Next time I would define where trusted checkpoints come
from, how long they are retained, when they are updated,
and how a user deletes them before adding persistent state.

### Week 6 follow-up — Session State experiment

**Experiment performed: 2026-11-28.**

I executed four independent offline calls through the
shared call_tool validation gate.

- PostgreSQL compared with PostgreSQL returned consistent.
- Omitting previous state produced a validation error.
- Supplying only a terminal-interface decision and proposing
  MongoDB returned consistent, with no retained database decision.
- Supplying PostgreSQL again and proposing MongoDB returned
  drift, with the expected and proposed values in the conflict.

The experiment demonstrates that my tool depends on
explicitly supplied state and does not retain earlier
decisions between calls.

A consistent result does not establish that the supplied
state is complete or authentic.

Next time, I would define session scope, retention,
write conditions and deletion before implementing trusted
state storage, and test isolation between sessions.

The experiment does not implement persistent memory.

## Week 7 — Supervised Autonomy Loop

**Work and reflection — 8 November 2026**

I integrated my drift-checking tool with the existing
supervised tool loop. The model can request the tool,
but `call_tool()` validates arguments before executing
the comparison. The same gate is used by the MCP server.

I used ChatGPT to draft implementation steps and then
ran pytest after each integration stage. The first
generated integration script stopped on an assertion,
which I repaired. A later test attempt failed because
Git Bash was using system Python; activating `.venv`
resolved that environment issue.

The valid product branch passed 64 tests. I then weakened
the decision-value pattern on an experimental branch.
The direct and golden tests caught invalid input that
the weakened contract accepted. GitHub Actions failed,
and I closed the experimental PR without merging.

One thing I would do differently is run the adversarial
goldens immediately after changing the contract, and
always verify the Python environment before testing.

A live model-driven tool invocation was not verified.

## Follow-up - Streaming and MCP

Date: 2026-11-24

I implemented the streaming gateway and local HTTP interface.
The offline test produced multiple text fragments and exactly
one usage entry with time to first token.

I observed VS Code discover and execute both MCP tools.

The initial integration failed because stream() was missing.
After correcting the implementation, all 74 tests passed.

Next time I would verify module imports and workspace
configuration before running integration tests.

Persistent memory and consequential-action confirmation
are not implemented by this slice.

### Week 7 follow-up — November 28, 2026

The consequential action I propose for Blue Whale is
committing a new checkpoint into trusted conversation state.

My drift-checking tool can identify contradictions between
previous and proposed decisions, but detecting a conflict
does not authorize a change to the trusted state.

For example, if the model proposes replacing PostgreSQL
with MongoDB, the application must present the proposed
change and wait for explicit human confirmation before
committing the new decision.

My streaming interface can deliver model responses and
tool outcomes to the user, but receiving a streamed tool
result must not be interpreted as human approval.

The confirmation endpoint must execute only previously
proposed actions identified by their action IDs after
receiving explicit human confirmation.

Repeated confirmation must not apply the same change twice.

This checkpoint confirmation workflow is proposed and
still requires team agreement and implementation.

Since my original journal entry, I have implemented
the streaming gateway and local HTTP interface in PR #41.

I also reviewed the shared MCP protocol correction in
PR #49, which verified argument validation, sanitized
errors, audit logging, and matching published schemas.

Next time, I would specify the approval boundary before
integrating the model loop with consequential actions,
and test that no trusted state changes before confirmation.
