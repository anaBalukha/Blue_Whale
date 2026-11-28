# MCP Protocol Boundary Correction

Date: 2026-11-28

Contributor: Mikheili Kakhniashvili

Issue: #48

## Original defects

An independent diagnostic audit checked 13 requests
through the actual MCP client.

Ten cases exhibited defects:

- Seven requests produced no shared audit record.
- Three error responses reflected raw input.
- Four invalid requests were accepted by the MCP schema.
- One invalid decision key was accepted by the function schema.
- Seven requests returned inconsistent validation errors.

All ten invalid requests were rejected at runtime.
All three valid requests succeeded.

These defect categories overlap.

## Root cause

The MCP SDK's typed argument binder could reject
malformed input before the application's shared
validation and audit gate executed.

The generated MCP schemas also differed from the
function-calling schemas.

## Correction

- Route MCP tool execution through the shared call_tool gate.
- Preserve strict runtime argument validation.
- Return sanitized errors from the shared gate.
- Publish the shared input contract through both interfaces.
- Include the decision-key regex in propertyNames.
- Preserve valid structured responses and read-only behavior.

The existing business logic of all three tools is unchanged.

## Regression evidence

MCP SDK version: 2.3.0.

Before correction:

- 13 failed, 3 passed.

After correction:

- New MCP protocol tests: 16/16 passed.
- Existing MCP tests: 16/16 passed.
- Full project suite: 155/155 passed.
- Offline index: 23 chunks.
- Offline RAG goldens: 5/5 passed.
- Python compilation: passed.
- Git whitespace validation: passed.

Configuration:

- BLUE_WHALE_OFFLINE=1
- BLUE_WHALE_MIN_SCORE=0.30
- Retrieval k=5

Evidence:

- tests/test_mcp_protocol_boundary.py
- evals/results/2026-11-28-0419-offline-k5.json

## Limitations

The protocol tests use the actual MCP client with
an in-memory server transport.

The tests establish validation and audit behavior
for the covered requests, not every possible malformed
protocol message.

The implementation depends on MCP SDK 2.x behavior.
Compatibility must be verified when upgrading the SDK.

No live model requests were made.
