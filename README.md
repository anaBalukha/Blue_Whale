# Blue Whale

Blue Whale helps students and developers detect when AI
suggestions contradict previously confirmed decisions.

## Implemented

- Structured drift detection with explicit user overrides.
- Hybrid BM25/vector retrieval from trusted project documents.
- Grounded answers, citation validation and safe refusals.
- Lab 3 multimodal extraction and confidence routing.
- Strict tool contracts and shared execution gates.
- Bounded tool-calling loop with a maximum of three model rounds.
- Four read-only tools exposed through MCP and function calling.
- Local HTTP interface and SSE streaming.
- Usage, latency, cost and tool audit logging.

## Architecture

Blue Whale remains terminal-first.

- `src/drift_core.py`: structured decision comparison.
- `src/index.py` and `src/retrieve.py`: trusted-source retrieval.
- `src/answer.py`: grounded answers and citation validation.
- `src/tools.py` and `src/contracts.py`: tool registry and contracts.
- `src/act.py`: bounded tool loop and shared execution gate.
- `src/mcp_server.py`: MCP interface.
- `src/llm.py` and `src/chat.py`: model access and streaming.
- `src/app.py`: local HTTP development interface.

## Read-only tools

| Tool | Purpose |
|---|---|
| search_trusted_sources | Retrieve evidence from trusted documents |
| check_decision_drift | Compare previous and proposed decisions |
| preview_checkpoint_update | Preview a versioned checkpoint change |
| answer_from_trusted_sources | Generate a grounded answer with citations or refuse |

All four tools use the shared validation and audit gate.
A tool result is evidence or a proposal, not authorization
to modify trusted conversation state.

See [tool contracts](docs/tool-contracts.md) and
[MCP correction evidence](docs/mcp-boundary-evidence.md).

## Not yet complete

- Persistent conversation memory, retention and deletion.
- Automatic trusted-state recovery.
- Consequential checkpoint commits and human confirmation.
- The complete supervised agent workflow.
- Live end-to-end RAG golden evaluation.
- Live model-driven tool and streaming verification.
- Natural-language drift, recovery and consistency evaluation.
- Production authentication and deployment.

The current structured comparison benchmark does not establish
end-to-end natural-language drift detection or recovery accuracy.

## Requirements

Python 3.11+ and dependencies from requirements.txt.

CI uses Python 3.11.

## Setup and offline verification

From the repository root, create a virtual environment:

~~~bash
python -m venv .venv
~~~

Activate it using Git Bash on Windows:

~~~bash
source .venv/Scripts/activate
~~~

On Linux or macOS:

~~~bash
source .venv/bin/activate
~~~

Install the dependencies:

~~~bash
python -m pip install -r requirements.txt
~~~

Run the shared product tests:

~~~bash
BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m pytest -q tests
~~~

Build the offline index before running the RAG evaluation:

~~~bash
BLUE_WHALE_OFFLINE=1 python -m src.index
BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m evals.run_golden --k 5
~~~

These are the same offline settings used by CI.

Offline testing requires no API key. Offline embeddings and
answers are simulated, not real-model quality measurements.

Live model calls require OPENROUTER_API_KEY in the shell
environment and may incur provider charges.

Evaluation runs create result files in evals/results/.
Commit only intentionally selected evidence.

## Local development interfaces

### Structured drift CLI

~~~bash
python -m src.drift_core '{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}'
~~~

### MCP server (stdio)

~~~bash
BLUE_WHALE_OFFLINE=1 python -m src.mcp_server
~~~

An MCP-compatible host can discover the four registered
read-only tools.

### Local HTTP and SSE interface

Start the development server:

~~~bash
BLUE_WHALE_OFFLINE=1 python -m uvicorn src.app:app --host 127.0.0.1 --port 8000
~~~

| Endpoint | Purpose |
|---|---|
| GET /health | Service health |
| POST /act | Bounded tool conversation |
| POST /chat | SSE-streamed tool conversation |

POST requests accept a JSON object containing a question
of 3-500 characters. Unexpected fields are rejected.

Example streaming request from another terminal:

~~~bash
curl -N -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" -d '{"question":"Which interface is planned for Blue Whale MVP?"}'
~~~

The SSE interface emits token, tool and done events.

X-Caller-Id is optional local development context,
not production authentication.

See [streaming interface](docs/streaming-interface.md)
and [streaming evaluation](docs/streaming-eval.md).

## Evaluation

### Offline RAG

- Current result: 5/5 golden cases passed.
- Configuration: k=5, BLUE_WHALE_MIN_SCORE=0.30.
- [Latest recorded result](evals/results/2026-11-28-0419-offline-k5.json)
- [Earlier passing result](evals/results/2026-11-08-0522-offline-k5.json)
- [Earlier failing comparison](evals/results/2026-11-08-0521-offline-k3.json)
- [Retrieval tuning decision](docs/decisions/003-offline-multidoc-g3.md)

Live end-to-end RAG evaluation remains pending.

### Regression and streaming evidence

Recorded verification on November 28, 2026:

- Shared product suite: 185/185 passed.
- Shared Lab 5 tool regression tests: 17/17 passed.
- Tool golden cases: 20/20 passed, plus one coverage test.
- Citation regression tests: 15/15 passed.
- MCP protocol, schema and error-handling tests: 30/30 passed.
- [Latest HW2 regression evidence](hw2/mishakakhniashvili/evidence.md)
- Offline RAG goldens: 5/5 passed.
- Offline HTTP streaming transport verification: passed.

Evidence:

- [Citation correction](docs/citation-validation-evidence.md)
- [MCP boundary correction](docs/mcp-boundary-evidence.md)
- [Offline streaming result](evals/results/stream-transport-offline.json)

Ten earlier real OpenRouter chat-only calls were recorded.

- [Chat-only measurements](evals/results/live-free-chat-summary.json)

Those calls did not establish live end-to-end RAG,
tool-calling or streaming quality.

### Shared Lab 5 team tool

The answer_from_trusted_sources tool wraps the existing
grounded answer pipeline. It is separate from the three
individual HW2 tools.

- [Team tool contract](docs/tool-contracts.md)
- [Implementation](src/team_answer_tool.py)
- [Regression tests](tests/test_team_answer_tool.py)
- [Golden cases](evals/tools/lab5-team.yaml)
- [Verification evidence](docs/lab5-team-tool-evidence.md)

Offline verification passed. External MCP host and live
model-driven verification of this new tool remain pending.

The tool may perform an additional model generation call
in live mode. Citation checks validate citation structure
and references, not semantic entailment.

### Structured drift detection

- Labeled synthetic cases: 50.
- Correct classifications: 50.
- Accuracy: 100.0%.
- Exact case pass rate: 100.0%.
- Product accuracy target: 85.0%.
- False positives: 0.
- False negatives: 0.

Reproduce with:

`python -m evals.run_drift_benchmark`

- [Labeled dataset](evals/drift_cases.json)
- [Measured results](evals/results/drift-structured-baseline.json)

This benchmark measures deterministic comparison of structured
decisions. User changes are supplied as trusted application input.
It does not establish natural-language extraction accuracy,
authorization correctness, recovery success, or post-recovery
consistency.

## Project documents

- Specification: docs/spec.md
- Retrieval specification: docs/retrieval-spec.md
- [Design Review (historical snapshot)](docs/DESIGN-REVIEW.md)
- Team contract: TEAM-CONTRACT.md
- Golden cases: evals/golden.yaml

Never commit private conversations, credentials or API keys.
