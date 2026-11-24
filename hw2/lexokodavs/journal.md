# HW2 Pattern Journal — Aleksandre Giorgashvili (lexokodavs)

## Week 5 — Tool Contract (2026-11-24)

**Delegated work:** Implementation of read-only checkpoint preview tool.

**Rung:** Assisted coding with strict deterministic spec constraints.

**What went wrong / what I checked:** The preview tool correctly treats `requires_confirmation: true` as informational only; it must never authorize state changes itself.

**Correction:** Validation is strict via Pydantic (`extra="forbid"`, version ≥ 0, regex-validated keys/values).

**Verification:** 86 tests passing, five golden cases green, MCP path verified through `call_tool` gates.

**One improvement:** Keep the contract doc and executable contract synchronized exactly (regex escaping).

## Week 6 — Session State (2026-11-24)

**Delegated work:** Design of the trusted checkpoint state representation.

**Observation:** Session state design requires a versioned checkpoint (previous version + decisions) to be separate from conversation history.

**Check:** The preview tool is designed to operate over this shape without mutation.

**Improvement:** Later implement state storage on top of the versioned checkpoint.

## Week 7 — Supervised Autonomy Loop (2026-11-24)

**Delegated work:** Design of the human confirmation gate.

**Decision:** The consequential action (`commit_confirmed_checkpoint`) must be parked by the loop and executed only via deterministic user confirmation.

**Check:** The preview tool must never execute inside the autonomous loop.

**Improvement:** Add stale-version protection when applying a confirmed commit.
