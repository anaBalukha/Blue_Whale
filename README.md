# Blue Whale

Blue Whale helps students and developers detect when AI
suggestions contradict previously confirmed decisions.

## Implemented

- Structured drift detection with explicit user overrides.
- Offline document indexing and hybrid BM25/vector retrieval.
- Grounded answers, citation checks and refusals.
- Five offline RAG golden cases: 5/5 passed at k=5.
- Ten real OpenRouter chat calls recorded separately.

- Lab 3 multimodal extraction and confidence routing.
- HW2 trusted-source retrieval and decision comparison with MCP and tool validation.

## Not yet complete

- Automatic trusted-state recovery.
- Live end-to-end RAG golden evaluation.


## Requirements

Python 3.11+ and dependencies from requirements.txt.

## Setup and commands

Install: `python -m pip install -r requirements.txt`

Test: `python -m pytest -q tests`

Drift CLI: `python -m src.drift_core '{"state":{"database":"PostgreSQL"},"candidate":{"database":"MongoDB"}}'`

Build offline index: `BLUE_WHALE_OFFLINE=1 python -m src.index`

Run offline goldens: `BLUE_WHALE_OFFLINE=1 BLUE_WHALE_MIN_SCORE=0.30 python -m evals.run_golden --k 5`

The original offline run passed 4/5 cases. After the multi-document grounding improvement in PR #24, all five cases passed at k=5 with BLUE_WHALE_MIN_SCORE=0.30. The real-model RAG evaluation remains pending.
Offline testing needs no API key. Live model calls require
an OpenRouter API key supplied via an environment variable.

## Evaluation

### Offline RAG

- Current result: 5/5 golden cases passed.
- Configuration: k=5, BLUE_WHALE_MIN_SCORE=0.30.
- [Passing result](evals/results/2026-11-08-0522-offline-k5.json)
- [Earlier failing comparison](evals/results/2026-11-08-0521-offline-k3.json)
- [Retrieval tuning decision](docs/decisions/003-offline-multidoc-g3.md)

Live end-to-end RAG evaluation remains pending.

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
- Design Review: docs/DESIGN-REVIEW.md
- Team contract: TEAM-CONTRACT.md
- Golden cases: evals/golden.yaml

Never commit private conversations, credentials or API keys.
