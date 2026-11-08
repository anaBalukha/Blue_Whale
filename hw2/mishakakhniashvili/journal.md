# HW2 Pattern Journal — Mikheili Kakhniashvili

## Week 5 — Tool Contract

*Retrospective entry, written November 8, 2026.*

I reviewed the Tool Contract pattern and applied it while developing Blue Whale's `search_trusted_sources` tool. I used Pydantic with `extra="forbid"` to reject unexpected arguments and restricted the search limit to 1–5. The tool is read-only and does not accept user identity from the model.

One thing I would do differently is test invalid and adversarial arguments earlier, especially through the MCP interface rather than only testing the Python function.

## Week 6 — Session State

*Retrospective entry, written November 8, 2026.*

I examined how Session State applies to Blue Whale and ran a
two-call offline experiment using an injected test model.

The first call established PostgreSQL as a project decision.
The second call asked which database was previously selected.
Inspecting the messages passed to the test model showed that
each call started with only a system message and the current
user message. The earlier decision was not carried forward.

This demonstrated a concrete limitation in the current
`src/act.py` implementation: it does not preserve conversation
history across separate calls. Persistent session memory,
expiration, and deletion have not yet been implemented.

One thing I would do differently is define the memory scope,
retention period, explicit write conditions, and deletion
mechanism before implementing session storage.

## Week 7 — Supervised Autonomy Loop

*Work performed November 8, 2026.*

I implemented a supervised tool-calling loop with a maximum of three model rounds. The model can request `search_trusted_sources`, but execution passes through validation gates before the tool runs.

I delegated implementation drafts to ChatGPT at Autonomy Ladder rung 3 and verified the implementation with pytest. The initial MCP implementation did not reject unexpected fields correctly, so validation of the original request arguments was added.

I also deliberately changed `extra="forbid"` to `extra="ignore"` on a temporary branch. Four tests failed, including the adversarial golden case. GitHub Actions detected the regression and branch protection blocked merging. The working implementation passed all 40 tests.

One thing I would do differently is test the MCP request boundary earlier and verify behavior through both interfaces before expanding the implementation.

A live model-driven tool call remains untested because I do not currently have an OpenRouter API key.
