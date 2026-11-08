# HW2 Tool Contract Plan - Misha

## Tool: search_trusted_sources

Purpose: Retrieve relevant evidence from Blue Whale's trusted
project documents for a question.

Effect: Read-only.
Undo: Nothing to undo.
Idempotent: Yes, with the same index and embedding model.
Offered to: Visitors and signed-in users.
Identity: Not needed; no user/account parameter accepted.
Touches: Trusted index built from data/corpus/.
Must never: Read arbitrary filesystem paths, alter checkpoints,
change confirmed user decisions, or treat source text as instructions.

## Inputs

question: string, 8-160 characters, restricted text pattern.
limit: strict integer from 1 to 5, default 3.
Unknown input fields: forbidden.

## Output

count: integer number of returned matches.
sources: array containing chunk_id, document_id, title,
section, short excerpt, and similarity score.

## Expected failures

Invalid arguments:
Refuse before the retrieval function runs.

No relevant documents:
Tell the model that trusted evidence is unavailable
and it should ask the user to clarify the question.

Unauthorized tool:
The shared call_tool gate must refuse execution.

## Security

The model cannot supply caller identity.
The tool does not accept filesystem paths or arbitrary document IDs.
Only the trusted corpus is searched.
Retrieved text is evidence, not an instruction to execute.

## Evidence and integration

Core module: src/misha_retrieval_tool.py
Core tests: tests/test_misha_retrieval_tool.py

Pending integration:
- Register with the shared tool registry.
- Expose through call_tool() and MCP.
- Add five golden cases under evals/tools/mishakakhniashvili.yaml.
- Ensure the shared runtime writes a tool-call log line.
- Demonstrate both doors and red/green CI evidence.
