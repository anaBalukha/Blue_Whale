# Independent Streaming Evaluation

Date: 2026-11-24

Owner: Mikheili Kakhniashvili, Eval Keeper.

Issue: #42

Implementation under review: PR #41.

## Automated regression tests

File: tests/test_misha_streaming.py

- Incremental delivery and final usage accounting.
- Interrupted stream failure handling.
- Incomplete tool requests never execute.
- Tool-only streams and reasoning metadata.
- Unknown cost is not reported as zero.
- Unauthorized write tools cannot execute.
- Bounded model rounds.
- Cancelled streams close the provider and log once.

Results:

- Independent streaming tests: 8/8 passed.
- Full project suite: 124/124 passed.
- Python compilation: passed.

## Real HTTP transport verification

Command: python -m evals.verify_stream_transport

Transport: local HTTP using Uvicorn and HTTPX.

The simulated model was prevented from producing its second
token until the HTTP client received the first token.

First token received before completion: yes.

Observed event order: token, token, done.

Usage log entries: 1.

Observed TTFT: 0 ms.

Evidence: evals/results/stream-transport-offline.json

## Limitations

The model provider is simulated.

No live OpenRouter streaming or real-model performance
claims are made.

Persistent memory, real client-disconnection behavior,
confirmation-gated execution and automatic recovery
require separate verification.
