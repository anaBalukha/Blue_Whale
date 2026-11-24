"""Regression checks for the structured drift benchmark."""

import json
from collections import Counter

from evals.run_drift_benchmark import DATASET, run


def test_benchmark_contains_required_case_categories():
    dataset = json.loads(
        DATASET.read_text(encoding="utf-8")
    )
    items = dataset["items"]

    assert len(items) >= 50
    assert len({item["id"] for item in items}) == len(items)
    assert dataset["threshold"] == 0.85

    counts = Counter(
        item["category"] for item in items
    )

    assert counts["unauthorized_drift"] >= 10
    assert counts["consistent"] >= 10
    assert counts["explicit_override"] >= 10
    assert counts["mixed_override_and_drift"] >= 10
    assert counts["partial_or_new_decision"] >= 10


def test_structured_drift_accuracy_meets_target():
    report = run()

    assert report["accuracy"] >= 0.85
    assert report["meets_accuracy_target"]


def test_benchmark_reports_exact_conflicts():
    report = run()

    failures = [
        item["id"]
        for item in report["items"]
        if not item["exact_conflicts"]
    ]

    assert not failures, failures


def test_benchmark_confusion_matrix_is_complete():
    report = run()

    assert sum(
        report["confusion_matrix"].values()
    ) == report["total"]

    assert sum(
        category["total"]
        for category in report["categories"].values()
    ) == report["total"]
