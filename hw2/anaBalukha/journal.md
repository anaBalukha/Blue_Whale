# HW2 Pattern Journal — Ana Balukhashvili

These entries are retrospective reflections written on
8 November 2026. They do not claim that the implementation
work happened during the corresponding lecture weeks.

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
