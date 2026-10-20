#!/usr/bin/env python3
import sys
import json
import copy

def error_response(message):
    return {"error": {"code": "INVALID_INPUT", "message": message}}

def main():
    if len(sys.argv) != 2:
        print(json.dumps(error_response("Exactly one JSON argument required.")))
        sys.exit(2)

    try:
        payload = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps(error_response(f"Invalid JSON: {e}")))
        sys.exit(2)

    if not isinstance(payload, dict):
        print(json.dumps(error_response("Payload must be a JSON object.")))
        sys.exit(2)

    previous = payload.get("previous")
    user_changes = payload.get("user_changes")

    if not isinstance(previous, dict) or not isinstance(user_changes, dict):
        print(json.dumps(error_response("Both 'previous' and 'user_changes' must be objects.")))
        sys.exit(2)

    # Validate previous structure
    prev_version = previous.get("version")
    prev_decisions = previous.get("decisions")

    if not isinstance(prev_version, int) or isinstance(prev_version, bool) or prev_version < 0:
        print(json.dumps(error_response("Version must be a non-negative integer.")))
        sys.exit(2)

    if not isinstance(prev_decisions, dict):
        print(json.dumps(error_response("Previous decisions must be a dictionary.")))
        sys.exit(2)

    for k, v in prev_decisions.items():
        if not isinstance(k, str) or not k or not isinstance(v, str):
            print(json.dumps(error_response("Decision keys must be non-empty strings and values must be strings.")))
            sys.exit(2)

    # Validate user_changes structure
    for k, v in user_changes.items():
        if not isinstance(k, str) or not k or not isinstance(v, str):
            print(json.dumps(error_response("Change keys must be non-empty strings and values must be strings.")))
            sys.exit(2)

    # Compute changes and new checkpoint
    new_decisions = copy.deepcopy(prev_decisions)
    changed_fields = []

    for k, v in user_changes.items():
        if k not in new_decisions or new_decisions[k] != v:
            new_decisions[k] = v
            changed_fields.append(k)

    changed_fields = sorted(list(set(changed_fields)))
    
    if len(changed_fields) > 0:
        new_version = prev_version + 1
    else:
        new_version = prev_version

    output = {
        "checkpoint": {
            "version": new_version,
            "decisions": new_decisions
        },
        "changed_fields": changed_fields
    }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
