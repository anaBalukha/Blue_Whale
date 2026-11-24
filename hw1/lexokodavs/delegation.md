# AI Delegation Log — Aleksandre Giorgashvili (lexokodavs)

## 1 · Original build (2026-10-20, commits `ff23cdf`, `175c0bb`)

- **What I delegated:** drafting `src/checkpoint_builder.py` and its four pytest cases from my spec (merge previous decisions with user changes, version +1 only on an effective change, `INVALID_INPUT` with exit code 2).
- **Agent / model:** unknown. I did not record which assistant I used, and I cannot reconstruct it now.
- **Rung:** 3 (the agent drafted the code against my written spec; I reviewed and ran it).
- **What came back wrong / how I caught it:** not recorded at the time. The original log was a single line, so I cannot honestly claim a specific catch from October.

## 2 · Post-grading re-verification (2026-11-24, branch `fix/lexokodavs-hw1-evidence`)

- **What I delegated:** an audit of my HW1 folder against `Lab-3/MILESTONE-1.md`, plus the fixes, to an AI coding agent (Claude Code, Claude Opus 5.5).
- **Rung:** 3. The agent proposed a plan and I approved it before any file changed. The agent ran every check itself, and I reviewed each diff.
- **What was wrong, and how it was caught:**
  1. **Conflict markers in `spec.md`** (`<<<<<<< HEAD` … `>>>>>>> origin/main`), introduced by merge `f6f4cdf` on 2026-10-25 and merged to `main` in PR #18. Caught by reading the file on `main`, and confirmed with `git show origin/main:hw1/lexokodavs/spec.md | grep '<<<<<<<'`. Fixed by keeping the complete spec text.
  2. **Spec and code disagreed on the input shape.** The spec said `user_changes` contained "`decisions` updates", but the code expects a flat map: `{"user_changes":{"decisions":{...}}}` is refused. Caught by running that payload. The spec now documents the flat shape, and a test covers the nested one.
  3. **Unknown fields were silently accepted.** `{"...","authorized": true}` printed an updated checkpoint with exit 0. The spec claimed the changes were "user-authorized" and merged "securely", but nothing checked authorization. Caught by running that payload by hand. Fixed: the builder now refuses unknown top-level and `previous` fields. Against the old code the two new tests fail (2 failed, 12 passed), and with the fix all 14 pass.
  4. **Tests only passed from the repo root.** They called `hw1/lexokodavs/src/...` relative to the working directory, so running `pytest /full/path/hw1/lexokodavs` from another folder gave `4 failed`. Fixed by resolving the script path from `__file__`, and checked from `/tmp`: 14 passed.
- **Also caught in the agent's own work:** none of the fixes above was taken on trust. Each one was re-run, and the new tests were run against the old code to prove they can fail.

These are corrections made after HW1 was graded. They are not a new on-time submission.
