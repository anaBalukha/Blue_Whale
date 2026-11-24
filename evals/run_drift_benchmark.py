"""Evaluate structured drift detection against independently labeled cases."""

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.drift_core import check_drift

DATASET = Path("evals/drift_cases.json")


def run(dataset_path=DATASET):
    dataset = json.loads(
        Path(dataset_path).read_text(encoding="utf-8")
    )

    items = dataset["items"]

    if len(items) < 50:
        raise ValueError("Benchmark requires at least 50 cases.")

    if len({item["id"] for item in items}) != len(items):
        raise ValueError("Duplicate benchmark case IDs.")

    rows = []
    categories = defaultdict(lambda: {
        "passed": 0,
        "total": 0,
    })

    confusion = Counter({
        "true_positive": 0,
        "true_negative": 0,
        "false_positive": 0,
        "false_negative": 0,
    })

    for item in items:
        expected = item["expected_status"]

        if expected not in {"drift", "consistent"}:
            raise ValueError("Invalid expected status.")

        result = check_drift(
            item["state"],
            item["candidate"],
            item["user_changes"],
        )

        actual = result["status"]

        expected_fields = sorted(
            item["expected_conflict_fields"]
        )

        actual_fields = sorted(
            conflict["field"]
            for conflict in result["conflicts"]
        )

        correct = actual == expected
        exact_conflicts = actual_fields == expected_fields
        passed = correct and exact_conflicts

        category = categories[item["category"]]
        category["total"] += 1
        category["passed"] += int(passed)

        if expected == "drift":
            key = (
                "true_positive" if actual == "drift"
                else "false_negative"
            )
        else:
            key = (
                "true_negative" if actual == "consistent"
                else "false_positive"
            )

        confusion[key] += 1

        rows.append({
            "id": item["id"],
            "category": item["category"],
            "expected": expected,
            "actual": actual,
            "expected_conflict_fields": expected_fields,
            "actual_conflict_fields": actual_fields,
            "classification_correct": correct,
            "exact_conflicts": exact_conflicts,
            "pass": passed,
        })

    total = len(rows)
    correct_count = sum(
        row["classification_correct"] for row in rows
    )
    passed = sum(row["pass"] for row in rows)
    accuracy = correct_count / total

    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": dataset["name"],
        "scope": dataset["scope"],
        "threshold": dataset["threshold"],
        "total": total,
        "correct_classifications": correct_count,
        "accuracy": accuracy,
        "passed": passed,
        "exact_case_pass_rate": passed / total,
        "meets_accuracy_target": (
            accuracy >= dataset["threshold"]
        ),
        "confusion_matrix": dict(confusion),
        "categories": dict(categories),
        "items": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "evals/results/drift-structured-baseline.json"
        ),
    )
    args = parser.parse_args()

    report = run()

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    args.output.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("STRUCTURED DRIFT BENCHMARK")
    print("Total:", report["total"])
    print("Correct:", report["correct_classifications"])
    print("Accuracy:", f"{report['accuracy']:.1%}")
    print(
        "Exact case pass rate:",
        f"{report['exact_case_pass_rate']:.1%}",
    )
    print("Target:", f"{report['threshold']:.1%}")
    print("Confusion matrix:", report["confusion_matrix"])

    for name, category in report["categories"].items():
        print(
            f"{name}: "
            f"{category['passed']}/{category['total']}"
        )

    for item in report["items"]:
        if not item["pass"]:
            print("FAIL:", item["id"], item)

    print("Result saved:", args.output)

    return 0 if report["meets_accuracy_target"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
