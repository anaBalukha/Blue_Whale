# HW2 Pattern Journal — Mikheili Kakhniashvili

# 

# Week 5 — Tool Contract

# \*Retrospective entry, written November 8, 2026\*

# 

# I reviewed the Tool Contract pattern and applied it while developing Blue Whale's `search\_trusted\_sources` tool. I used Pydantic with `extra="forbid"` to reject unexpected arguments and restricted the search limit to 1–5. The tool is read-only and does not accept user identity from the model.

# 

# One thing I would do differently is test invalid and adversarial arguments earlier, especially through the MCP interface rather than only testing the Python function.

# 

# \## Week 6 — Session State

# \*Retrospective entry, written November 8, 2026\*

# 

# I considered how Session State applies to Blue Whale. The product needs to remember confirmed user decisions across conversation turns so that it can detect contradictions and recover the correct context. I reviewed the importance of keeping user-confirmed decisions separate from AI-generated assumptions.

# 

# We have not yet implemented persistent session memory. One thing I would do differently is define the memory scope, expiration rules, and deletion mechanism before implementing the storage layer.

# 

# Week 7 — Supervised Autonomy Loop

# Work performed November 8, 2026

# 

# I implemented a supervised tool-calling loop with a maximum of three model rounds. The model can request `search\_trusted\_sources`, but execution passes through validation gates before the tool runs.

# 

# I delegated initial implementation drafts to ChatGPT at Autonomy Ladder rung 3, reviewed the implementation, and verified it with pytest. The original MCP implementation did not reject unexpected fields correctly, so I added validation of the original request arguments.

# 

# I also deliberately changed `extra="forbid"` to `extra="ignore"` on a temporary branch. Four tests failed, including the adversarial golden case. GitHub Actions detected the regression and branch protection blocked merging. The working implementation passed all 40 tests.

# 

# One thing I would do differently is test the MCP request boundary at the beginning and verify the complete tool behavior through both interfaces before expanding the implementation.

# 

# A live model-driven tool call remains untested because I do not currently have an OpenRouter API key.

