import pytest
from hw1.anaBalukha.src.drift_checker import check_drift


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
