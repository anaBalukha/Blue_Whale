import json
import math
import sys


VALID_STATUSES = {"answered", "refused"}


def evaluate(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("cases must be a non-empty list")

    threshold = data.get("threshold", 0.70)
    if (
        isinstance(threshold, bool)
        or not isinstance(threshold, (int, float))
        or not math.isfinite(threshold)
        or not 0 <= threshold <= 1
    ):
        raise ValueError("threshold must be between 0 and 1")

    seen_ids = set()
    failed_ids = []

    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each case must be an object")

        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("Each case needs a non-empty id")

        if case_id in seen_ids:
            raise ValueError("Duplicate case id")
        seen_ids.add(case_id)

        expected = case.get("expected")
        actual = case.get("actual")

        if expected not in VALID_STATUSES or actual not in VALID_STATUSES:
            raise ValueError("Invalid test status")

        if expected != actual:
            failed_ids.append(case_id)

    total = len(cases)
    passed = total - len(failed_ids)
    pass_rate = round(passed / total, 2)

    return {
        "total": total,
        "passed": passed,
        "pass_rate": pass_rate,
        "meets_threshold": pass_rate >= threshold,
        "failed_ids": failed_ids,
    }


def main():
    try:
        if len(sys.argv) != 2:
            raise ValueError("Expected one JSON input argument")

        data = json.loads(sys.argv[1])
        print(json.dumps(evaluate(data)))
        return 0

    except (ValueError, TypeError) as error:
        print(json.dumps({
            "error": {
                "code": "INVALID_INPUT",
                "message": str(error),
            }
        }))
        return 2


if __name__ == "__main__":
    sys.exit(main())
