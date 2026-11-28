# HW2 Pattern Journal — Ana Balukhashvili

These entries are retrospective reflections written on
8 November 2026. They do not claim that the implementation
work happened during the corresponding lecture weeks.

## Week 5 — Tool Contract

**Implementation references:** [DriftArguments](../../src/contracts.py#L92), [drift tool](../../src/ana_drift_tool.py), [direct tests](../../tests/test_ana_drift_tool.py), [product PR #28](https://github.com/anaBalukha/Blue_Whale/pull/28).

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

**Experiment references:** [shared execution gate](../../src/act.py), [drift tool](../../src/ana_drift_tool.py), [Session State experiment](evidence.md). No cross-call memory lifetime or deletion mechanism is implemented.

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

**Implementation references:** [bounded loop](../../src/act.py), [MCP tests](../../tests/test_ana_mcp.py), [red CI experiment #29](https://github.com/anaBalukha/Blue_Whale/pull/29). The checkpoint commit remains a proposed confirmation-required action.

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
