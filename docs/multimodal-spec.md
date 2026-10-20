# Multimodal Extraction Specification — Blue Whale

## 1. Overview & Goal
Extract structured project decisions (project name, database, framework) from sanitized screenshots or staged photographs containing fictional text to support conversational state recovery.

## 2. Input Contract & Pre-processing
- **Input:** Image file (PNG/JPG) under 2MB.
- **Pre-processing:** Downscale image so that its longest edge does not exceed 1024 pixels, preserving aspect ratio.

## 3. Output Schema (Pydantic)
- `project`: `{value: str | None, evidence: str | None, confidence: float}`
- `database`: `{value: str | None, evidence: str | None, confidence: float}`
- `framework`: `{value: str | None, evidence: str | None, confidence: float}`
- `document_type`: `str` (e.g. `"decision_sheet"`, `"unrelated"`)

## 4. Constraints & Rules
- Never guess missing values; return `null` for value and evidence if not clearly visible.
- Evidence must be exact visible text from the image, not an AI-invented summary.
- Self-rated confidence alone is insufficient for automatic acceptance.
