# Blue Whale

Blue Whale helps students and developers detect when AI
suggestions contradict previously confirmed decisions.

## Implemented

- Structured drift detection with explicit user overrides.
- Offline document indexing and hybrid BM25/vector retrieval.
- Grounded answers, citation checks and refusals.
- Five offline golden cases: 4/5 passed.
- Ten real OpenRouter chat calls recorded separately.

## Not yet complete

- Automatic trusted-state recovery.
- Live end-to-end RAG golden evaluation.
- Lab 3 multimodal feature (PR #13).

## Requirements

Python 3.11+ and dependencies from requirements.txt.

## Setup and commands

Install: `python -m pip install -r requirements.txt`

Test: `python -m pytest -q tests`

Drift CLI: `python -m src.drift_core '{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}'`

Build offline index: `BLUE_WHALE_OFFLINE=1 python -m src.index`

Run offline goldens: `BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m evals.run_golden --k 3`

The offline golden run previously passed 4/5 cases;
the two-document reasoning case g3 remains unsuccessful.
Offline testing needs no API key. Live model calls require
an OpenRouter API key supplied via an environment variable.

## Project documents

- Specification: docs/spec.md
- Retrieval specification: docs/retrieval-spec.md
- Design Review: docs/DESIGN-REVIEW.md
- Team contract: TEAM-CONTRACT.md
- Golden cases: evals/golden.yaml

Never commit private conversations, credentials or API keys.
