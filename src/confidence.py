from typing import Dict, Any

def decide(extraction: Dict[str, Any], today: str = None) -> Dict[str, Any]:
    doc_type = extraction.get("document_type", "decision_sheet")
    if doc_type == "unrelated":
        return {"route": "rejected", "reasons": ["Document type is unrelated."], "fields": {}}

    fields = ["project", "database", "framework"]
    reasons = []
    has_low_confidence = False
    cleaned_fields = {}

    for field in fields:
        f_data = extraction.get(field, {})
        val = f_data.get("value")
        ev = f_data.get("evidence")
        conf = f_data.get("confidence", 0.0)

        if val and not ev:
            return {
                "route": "review",
                "reasons": [f"Hard failure: Field '{field}' has value but missing evidence."],
                "fields": {}
            }

        if conf < 0.6:
            has_low_confidence = True
            reasons.append(f"Soft ambiguity: Field '{field}' has low confidence ({conf}).")

        cleaned_fields[field] = f_data

    if has_low_confidence:
        return {
            "route": "confirm",
            "reasons": reasons,
            "fields": cleaned_fields
        }

    return {
        "route": "accepted",
        "reasons": ["All fields extracted successfully with high confidence and valid evidence."],
        "fields": cleaned_fields
    }
