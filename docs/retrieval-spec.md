# Retrieval Spec - Blue Whale

## 1. What the documents are

| Folder in data/corpus/ | Contents | Owner | Updates |
|---|---|---|---|
| project/ | Approved project specifications and decisions | Spec keeper | When decisions change |
| checkpoints/ | Sanitized conversation-state checkpoints | Eval keeper | When a checkpoint is confirmed |

Initial sources will include docs/spec.md and the two
approved decision records. Additional non-sensitive
checkpoint examples will be prepared for testing.

Do not index private conversations, API keys, or
unverified AI assumptions.

Refuse questions whose answers are not supported
by trusted documents.

## 2. Chunking

- Split on Markdown headings or checkpoint boundaries.
- Include document title, source path, and version.
- Maximum chunk size: 800 characters.
- Overlap: one paragraph when splitting long sections.
- Preserve document IDs for citation validation.

## 3. Retrieval

- Embedding model: openai/text-embedding-3-small
- Reference price: $0.02 per million tokens (2026-10-19).
- Provider: OpenRouter.
- Retriever: vector similarity, k = 3.
- Starting cosine similarity threshold: 0.70.
- Threshold must be tested and tuned using real results.
- Record the embedding model used to build each index.

## 4. Answering

- Model: BLUE_WHALE_MODEL from the environment.
- Planned default: google/gemini-3.8-flash.
- Verify model availability before live execution.
- Reply shape: {answer, citations, grounded}.
- Validate the reply schema in code.
- Every factual answer sentence must cite retrieved evidence.
- Unknown, missing, or invalid citations cause refusal.
- Refuse before an answer-model call when retrieval
  finds no relevant document above the threshold.
- Latest explicit user instructions supersede older decisions.

## 5. What the user sees

Example: "The MVP uses a terminal interface [1]."
Source [1]: project/terminal-first

Refusal: "I cannot verify that from the saved context."
Next action: Ask the user to clarify or confirm the decision.

## 6. Acceptance criteria

- AC1: A question about the MVP interface returns
  a cited answer from the terminal-first decision.
- AC2: A question about an undocumented hosting
  provider is refused without an answer-model call.
- AC3: A citation to a document not retrieved is refused.
- AC4: Each answer or refusal produces one log entry
  with its reason and model usage where applicable.
- AC5: The five-case live golden evaluation reaches
  a pass rate of at least 0.70.

Status: Specification only. Implementation and live
evaluation have not yet been completed.
