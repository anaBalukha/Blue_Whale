import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent / "src" / "evaluate.py"


def run(data):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), json.dumps(data)],
        capture_output=True, text=True
    )
    return result.returncode, json.loads(result.stdout)


def test_pass_and_failure():
    code, out = run({"cases": [
        {"id": "g1", "expected": "answered", "actual": "answered"},
        {"id": "g2", "expected": "refused", "actual": "answered"}
    ]})
    assert code == 0
    assert out["passed"] == 1
    assert out["pass_rate"] == 0.5
    assert out["failed_ids"] == ["g2"]
    assert out["meets_threshold"] is False


def test_threshold_met():
    code, out = run({"cases": [
        {"id": "g1", "expected": "answered", "actual": "answered"}
    ]})
    assert code == 0
    assert out["pass_rate"] == 1.0
    assert out["meets_threshold"] is True


@pytest.mark.parametrize("data", [
    {"cases": []},
    {"cases": [
        {"id": "g1", "expected": "answered", "actual": "answered"},
        {"id": "g1", "expected": "refused", "actual": "refused"}
    ]},
    {"cases": [
        {"id": "g1", "expected": "invalid", "actual": "answered"}
    ]},
    {"cases": [
        {"id": "g1", "expected": "answered", "actual": "answered"}
    ], "threshold": 2}
])
def test_invalid_input(data):
    code, out = run(data)
    assert code == 2
    assert out["error"]["code"] == "INVALID_INPUT"


def test_rounded_pass_rate_meets_threshold():
    code, out = run({
        "threshold": 0.67,
        "cases": [
            {"id": "g1", "expected": "answered", "actual": "answered"},
            {"id": "g2", "expected": "refused", "actual": "refused"},
            {"id": "g3", "expected": "answered", "actual": "refused"},
        ],
    })

    assert code == 0
    assert out["pass_rate"] == 0.67
    assert out["meets_threshold"] is True
    assert out["failed_ids"] == ["g3"]
