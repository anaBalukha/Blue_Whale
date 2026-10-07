# Spec v0 · Blue Whale

## Problem

AI assistants can lose track of long conversations: they may forget explicit requirements, contradict earlier decisions, or start solving a different problem. This makes AI unreliable for multi-step work such as software development, studying, debugging, and project planning, where previous decisions must remain consistent.

Blue Whale detects when an AI response drifts away from the user's established task and helps recover the latest valid conversation state.

## Users

Primary users are university students and software developers who use AI assistants for long, multi-step conversations containing explicit requirements, decisions, technologies, completed tasks, and next steps.

Secondary users may later include researchers and project teams working through complex AI-assisted workflows.

## Success criteria

1. **Drift detection accuracy:** correctly classify at least 85% of cases in a labeled benchmark of at least 50 conversation examples containing both drift and non-drift cases.
2. **Recovery success:** in at least 80% of confirmed drift cases, the corrected response follows the latest valid user requirements and expected conversation state.
3. **Post-recovery consistency:** in at least 90% of successful recovery cases, the next generated response does not repeat the detected contradiction or violate the recovered decision.

## Core feature (Weeks 2 to 4 scope)

Blue Whale maintains a compact structured representation of the current conversation state. After an AI response is produced, the system compares it with that state to identify contradictions or task drift.

If drift is detected, the system retrieves the latest trusted state, injects the relevant requirements back into the model context, and produces a corrected response.

Example:

- User establishes: "We are using PostgreSQL."
- Later AI response: "Let's configure MongoDB."
- No user instruction changed the database.
- Blue Whale detects the contradiction, recovers the PostgreSQL decision, and regenerates a response consistent with it.

An explicit user change is never considered drift. If the user later says "Switch to MongoDB," the stored state must be updated.

## Context list

The system keeps a structured state containing:

- **Main task:** the user's overall objective.
- **Current goal:** the part of the task currently being worked on.
- **Requirements:** explicit must / must-not constraints.
- **Technologies and tools:** selected languages, frameworks, databases, libraries, or tools.
- **Decisions:** choices already made during the conversation.
- **Completed work:** tasks already finished.
- **Next step:** the expected continuation of the work.
- **Recent conversation:** recent turns needed for immediate context.
- **Latest user request:** the request that must currently be answered.
- **Trusted checkpoint:** the latest structured state that can be used for recovery.

For the MVP, structured state is maintained for the current session rather than storing the entire conversation permanently.

Context authority, from highest to lowest:

1. Latest explicit user instruction.
2. User-confirmed checkpoint or decision.
3. Earlier explicit user instructions that have not been superseded.
4. AI-generated summaries or assumptions.

AI-generated assumptions must never override an explicit user instruction.

## Acceptance criteria

1. **State tracking:** after a user message, the system produces or updates a structured state containing the main task, current goal, requirements, technology choices, decisions, completed work, and next step. An explicit user change replaces the conflicting older value.

2. **Drift detection:** given a conversation where PostgreSQL is an established decision and the user has not changed it, a candidate AI response proposing MongoDB must be marked as drift and the conflicting decision must be identified.

3. **Recovery:** when drift is detected, the latest relevant trusted state must be supplied to the recovery step and the resulting response must respect the established decision. If the user explicitly changes the decision to MongoDB, the same response must not be classified as drift.

## Napkin math

MVP assumption:

- approximately 300 AI requests per day
- approximately 2,000 input tokens per request
- approximately 500 output tokens per request
- model: `google/gemini-3.8-flash`
- current reference price: $0.75 / 1M input tokens and $3.75 / 1M output tokens

Baseline:

300 × ((2,000 / 1,000,000 × $0.75) + (500 / 1,000,000 × $3.75)) × 30
≈ **$30.38/month**

Additional drift-analysis or recovery calls may increase this cost, so the MVP target is to remain below approximately **$50/month** during small-scale testing.

Pricing is a planning estimate and should be updated before the Design Review if model pricing changes.

## Risks and safety

- **Incorrect or stale state:** the system may extract a requirement incorrectly or recover an older decision instead of the latest valid one. Mitigation: explicit user instructions always override stored state and checkpoints must be versioned in order.
- **False drift detection:** the system may interpret an intentional requirement change as an AI mistake. Mitigation: detect explicit user changes before applying recovery.
- **Misuse / state poisoning:** a user may deliberately provide conflicting or manipulative instructions to corrupt the stored state. Mitigation: retain the source and ordering of important state changes rather than treating generated summaries as authoritative.

Conversation data may contain private or confidential information, so the MVP should store only the minimum structured state necessary for recovery and must not commit conversation data or API keys to the repository.

## Out of scope (for now)

- Training a new language model from scratch.
- Replacing ChatGPT or other general-purpose AI assistants.
- Perfect or permanent long-term memory.
- Cross-session memory.
- Voice interaction.
- Image or video understanding.
- Multi-agent systems.
- RAG or a vector database unless later requirements make it necessary.
- A complex analytics dashboard.
- Production-scale deployment or thousands of concurrent users.
