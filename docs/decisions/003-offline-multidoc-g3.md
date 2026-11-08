# Decision 003 — Offline multi-document evaluation

Status: Accepted for the offline evaluation baseline
Date: 2026-11-08
Owner: Mikheili Kakhniashvili, Eval Keeper

## Problem

Golden case g3 asks whether an explicit user switch from
a terminal to a web interface counts as conversation drift.

A correct grounded answer must cite both:
- project/terminal-first
- project/explicit-user-changes

The original offline evaluation passed 4/5 cases.
Case g3 failed because the generated answer did not
use both required documents.

## Investigation

Both required documents were already retrieved at k=3.
Increasing k alone did not fix the original generator.

The offline answer generator was updated to support
multiple relevant documents:
- Preserve the strong relevance anchor of 0.60.
- Permit supporting evidence with overlap >= 0.45.
- Select up to three distinct document titles.
- Preserve citation validation and refusal handling.

An initial sentence-splitting regex error caused
regressions. It was detected by pytest and corrected.

## Results

With the corrected offline generator:

- k=3: 4/5 golden cases passed; g3 still failed.
- k=5: 5/5 golden cases passed; g3 passed.
- g5 continued refusing unsupported hosting questions.

## Decision

Use k=5 for the offline golden evaluation and CI.

Keep the original golden expectations unchanged.
Add a regression test requiring g3 to cite both
trusted decision documents.

Preserve previous failing evaluation results as evidence.

## Limitations

These results use deterministic offline embeddings and
an extractive stand-in for the chat model.

They do not demonstrate real-model reasoning quality.
A live end-to-end RAG evaluation is still required.

## Follow-up

Run the complete golden set with real embeddings and
chat once provider access is available.
