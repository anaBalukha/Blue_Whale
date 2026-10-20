# Confidence Routing Policy — Blue Whale

## Routing Table
1. **Rejected (`rejected`):** Document type is unrelated or unreadable (`document_type == "unrelated"`).
2. **Review (`review`):** Hard failure: missing required field evidence or invalid field schema. Fields must be blanked out.
3. **Confirm (`confirm`):** Soft ambiguity: confidence score below threshold (e.g., `< 0.6`) or ambiguous conflicting labels detected. Requires user confirmation before committing state.
4. **Accepted (`accepted`):** All supported fields extracted successfully with high confidence (`>= 0.6`) and valid text evidence matching the image.
