# AGENTS.md · Blue Whale

Blue Whale detects conversation drift and helps AI assistants recover the latest valid user context.
Product specification: docs/spec.md

## Commands
- Install: python -m pip install -r requirements.txt
- Test (CI runs this): BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m pytest -q tests
- HW1 folders are not in CI; run them explicitly: python -m pytest -q hw1/<username>
- Drift CLI: python -m src.drift_core '{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}'
- MCP server (stdio): python -m src.mcp_server
- Offline RAG goldens: BLUE_WHALE_OFFLINE=1 python -m src.index && BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m evals.run_golden --k 5
- Drift benchmark: python -m evals.run_drift_benchmark
- There is no end-user app entry point yet; the MVP interface is terminal-first (docs/decisions/001-terminal-first.md).
- Running the evals rewrites files in evals/results/; commit a result only when it is intended evidence.

## Stack and conventions
- Python 3.11+ and pytest.
- LLM provider: OpenRouter.
- Model: BLUE_WHALE_MODEL, default google/gemini-3.8-flash.
- API key: OPENROUTER_API_KEY from the environment.
- Keep model calls centralized in src/ when implemented.
- Record token usage, cost, and latency without exposing secrets.
- Preserve the latest explicit user instruction over older decisions.
- Do not treat AI-generated assumptions as confirmed user requirements.
- Explicit user changes must update state, not trigger recovery.
- Keep structured checkpoints small and traceable to user messages.
- New features require tests covering success and error cases.
- Planned API errors use {"error":{"code":"...","message":"..."}}.

## Tools (Lab 5 / HW2)
- Registry: src/tools.py (TOOLS). Contracts: src/contracts.py or the tool's own module. Shared gate: call_tool() in src/act.py. MCP: src/mcp_server.py.
- Every tool contract uses extra="forbid", a pattern or fixed set on every string, and bounds on every number.
- MCP wrappers pass the raw request arguments to call_tool(); never validate a filtered copy.
- Every tool has golden cases in evals/tools/<github-username>.yaml (>=3 normal, 1 bad-input, 1 adversarial, each with a `why`).
- Contracts and ownership are recorded in docs/tool-contracts.md; keep it in sync with the code.
- Tool results are proposals or evidence, never user approval. Never accept a model-supplied flag (authorized, user_approved, commit) or identity as proof of anything.
- A tool that changes trusted state must be writes=True and run only after a human confirmation recorded by the application. No such tool exists yet.

## Always
- Read docs/spec.md before implementing a feature.
- Propose a plan before editing implementation files.
- Run tests and report the actual results.
- Follow the specification and acceptance criteria.

## Ask first
- Adding or changing dependencies.
- Modifying the public API or response format.
- Editing GitHub Actions or CI configuration.
- Changing established project requirements.
- Adding a tool that writes trusted state, or changing who a tool is offered to.

## Never
- Never add a tool that deletes or sends without asking first.
- Never put a user, student, or account id in a tool's arguments.
- Read, print, commit, or expose API keys or .env contents.
- Delete, skip, or weaken tests to make them pass.
- Override explicit user decisions with AI-generated assumptions.

## Ownership
- docs/spec.md and AGENTS.md: Spec Keeper (lexokodavs).
- evals/, golden sets, recorded results: Eval Keeper (mishakakhniashvili).
- .github/, branch rules, tags: Repo Keeper (anaBalukha).

## Safety & Operational Rules
- **Never:** Accept low-confidence extracted values without confirmation; invent a value if evidence is missing; emit a grounded answer without valid citations; weaken goldens to make tests pass.
