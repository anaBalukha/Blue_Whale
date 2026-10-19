import pytest
from src.drift_core import check_drift


def test_detects_drift():
    result = check_drift(
        {"database": "PostgreSQL"},
        {"database": "MongoDB"}
    )
    assert result["status"] == "drift"
    assert result["conflicts"] == [
        {
            "field": "database",
            "expected": "PostgreSQL",
            "proposed": "MongoDB"
        }
    ]


def test_explicit_user_change():
    result = check_drift(
        {"database": "PostgreSQL"},
        {"database": "MongoDB"},
        {"database": "MongoDB"}
    )
    assert result["status"] == "consistent"
    assert result["effective_state"]["database"] == "MongoDB"


def test_matching_decisions():
    result = check_drift(
        {"database": "PostgreSQL"},
        {"database": "PostgreSQL"}
    )
    assert result["status"] == "consistent"
    assert result["conflicts"] == []


def test_invalid_input():
    with pytest.raises(ValueError):
        check_drift([], {"database": "MongoDB"})


def test_log_contains_status_without_private_decisions(tmp_path, monkeypatch):
    import json
    from src.drift_core import log_run

    path = tmp_path / "drift.jsonl"
    monkeypatch.setenv("BLUE_WHALE_DRIFT_LOG", str(path))

    log_run({
        "status": "drift",
        "conflicts": [{
            "field": "database",
            "expected": "PRIVATE_VALUE",
            "proposed": "MongoDB"
        }]
    })

    content = path.read_text(encoding="utf-8")
    entry = json.loads(content)

    assert entry["status"] == "drift"
    assert entry["conflict_count"] == 1
    assert "PRIVATE_VALUE" not in content
