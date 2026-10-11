# AGENTS.md · Blue Whale

Blue Whale detects conversation drift and helps AI assistants recover the latest valid user context.
Product specification: docs/spec.md

## Commands
- Install: python -m pip install -r requirements.txt
- Run: Not available yet; the app entry point will be created in Lab 2.
- Test: python -m pytest -q tests

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

## Never
- Read, print, commit, or expose API keys or .env contents.
- Delete, skip, or weaken tests to make them pass.
- Override explicit user decisions with AI-generated assumptions.
