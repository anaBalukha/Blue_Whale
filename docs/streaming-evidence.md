# Streaming and MCP Verification Evidence

Date: 2026-11-24

Owner: Ana Balukhashvili

Related issue: #33

## External MCP demonstration

Host: VS Code Agent chat.
Transport: local stdio.
Connection: running.
Discovered tools: 2.

### Trusted-source retrieval

Question: Which interface is planned for the Blue Whale MVP?

The host executed search_trusted_sources.

Answer: A terminal application; the web interface is deferred.

Sources:
- project/blue-whale-spec
- project/terminal-first

### Decision drift

The host executed check_decision_drift.

Previous database: PostgreSQL.
Proposed database: MongoDB.

Observed status: drift.
Conflict field: database.
Expected: PostgreSQL.
Proposed: MongoDB.

Both demonstrations used the offline-configured MCP server.
They prove external host integration, not live OpenRouter calls.

## Offline streaming

HTTP status: 200.
Text fragments: 2.
Combined text: Offline simulation only. No real model was called.
Status: answered.
Usage log entries: 1.
TTFT: 0 ms.
Mode: offline simulation.

The HTTP test client verifies SSE event formatting.
Real network streaming and live-model streaming remain pending.

## Verification

- Streaming tests: 6 passed.
- Full project suite: 74 passed.
- Ana HW1: 4 passed.
- Misha HW1: 7 passed.
- Structured drift benchmark: 50/50.
- Offline RAG goldens: 5/5.
- Compilation and dependency checks: passed.

## Remaining work

Live model demonstrations, persistent memory, memory controls,
scope and deletion tests, and the Lab 7 confirmation gate.
