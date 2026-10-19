import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone


def validate_decisions(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a JSON object")

    for key, item in value.items():
        if not isinstance(key, str) or not key:
            raise ValueError(f"{name} keys must be non-empty strings")
        if not isinstance(item, str):
            raise ValueError(f"{name} values must be strings")


def check_drift(state, candidate, user_changes=None):
    if user_changes is None:
        user_changes = {}

    validate_decisions(state, "state")
    validate_decisions(candidate, "candidate")
    validate_decisions(user_changes, "user_changes")

    effective_state = {**state, **user_changes}
    conflicts = []

    for field, proposed in candidate.items():
        if field in effective_state:
            expected = effective_state[field]

            if proposed != expected:
                conflicts.append({
                    "field": field,
                    "expected": expected,
                    "proposed": proposed
                })

    return {
        "status": "drift" if conflicts else "consistent",
        "effective_state": effective_state,
        "conflicts": conflicts
    }



def log_run(result):
    path = Path(os.getenv("BLUE_WHALE_DRIFT_LOG", "logs/drift.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": result["status"],
        "conflict_count": len(result["conflicts"]),
    }

    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry) + "\n")


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError("Expected one JSON input argument")

        data = json.loads(sys.argv[1])

        if not isinstance(data, dict):
            raise ValueError("Input must be a JSON object")

        if "state" not in data or "candidate" not in data:
            raise ValueError("Missing state or candidate")

        result = check_drift(
            data["state"],
            data["candidate"],
            data.get("user_changes")
        )

        log_run(result)
        print(json.dumps(result))
        return 0

    except (ValueError, TypeError) as error:
        print(json.dumps({
            "error": {
                "code": "INVALID_INPUT",
                "message": str(error)
            }
        }))
        return 2


if __name__ == "__main__":
    sys.exit(main())
