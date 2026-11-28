# Citation Validation Correction

Date: 2026-11-28

Owner: Mikheili Kakhniashvili, Eval Keeper.

Issue: #46

## Original defect

The sentence splitter recognized only boundaries followed
by whitespace and an uppercase letter.

This allowed uncited sentences to appear in answers when
citations followed punctuation, sentences began with lowercase
letters, or claims were separated by newlines.

## Verification before correction

The first ten regression cases produced:

- 4 failed
- 6 passed

The failures reproduced the citation boundary defects
identified during the independent repository audit.

## Correction

- Introduced a shared conservative sentence parser.
- Required citations at the end of each sentence unit.
- Preserved citation-list consistency and source-range checks.
- Updated the offline extractive generator to cite each unit.

## Additional hardening

Five additional regression cases covered citation-only answers
and sentences without separating whitespace.

Before hardening:

- 4 failed
- 11 passed

The parser was corrected to reject citation-only answers
and recognize additional sentence boundaries.

## Final verification

- Citation regression tests: 15/15 passed.
- Full project suite: 139/139 passed.
- Misha HW1: 7/7 passed.
- Offline index: 23 chunks.
- Offline RAG goldens: 5/5 passed.
- Python compilation: passed.
- Git whitespace validation: passed.

Configuration:

- BLUE_WHALE_OFFLINE=1
- BLUE_WHALE_MIN_SCORE=0.30
- Retrieval k=5

Evidence:

evals/results/2026-11-28-0401-offline-k5.json

## Limitations

Citation validation checks citation placement and retrieved
source references. It does not establish semantic entailment.

The conservative parser may reject ambiguous formatting,
abbreviations or domain names.

No live model requests were made.
