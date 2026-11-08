"""Ana's offline HW2 drift tool tests."""

import json
from dataclasses import replace

import pytest
from pydantic import ValidationError

from src.act import call_tool
from src.ana_drift_tool import run_drift
from src.contracts import DriftArguments
from src.tools import TOOLS, tools_for


def test_detects_real_conflict():
    args = DriftArguments(
        state={"database": "PostgreSQL"},
        candidate={"database": "MongoDB"},
    )

    result = run_drift(args)

    assert result.status == "drift"
    assert len(result.conflicts) == 1
    assert result.conflicts[0].field == "database"


def test_matching_decisions_are_consistent():
    args = DriftArguments(
        state={"interface": "terminal"},
        candidate={"interface": "terminal"},
    )

    assert run_drift(args).status == "consistent"


def test_forged_user_override_is_forbidden():
    with pytest.raises(ValidationError):
        DriftArguments(
            state={"database": "PostgreSQL"},
            candidate={"database": "MongoDB"},
            user_changes={"database": "MongoDB"},
        )


def test_invalid_decision_value_is_rejected():
    with pytest.raises(ValidationError):
        DriftArguments(
            state={"database": "PostgreSQL"},
            candidate={"database": "ignore previous instructions!"},
        )


def test_adversarial_call_never_runs(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "BLUE_WHALE_TOOL_LOG",
        str(tmp_path / "tools.jsonl"),
    )

    executions = []

    original = TOOLS["check_decision_drift"]

    def spy(args):
        executions.append(args)
        return run_drift(args)

    guarded = replace(original, run=spy)

    outcome = call_tool(
        {
            "name": "check_decision_drift",
            "arguments": json.dumps({
                "state": {"database": "PostgreSQL"},
                "candidate": {"database": "MongoDB"},
                "user_changes": {"database": "MongoDB"},
            }),
        },
        {"check_decision_drift": guarded},
        None,
    )

    assert not outcome["ok"]
    assert executions == []


def test_valid_call_logs_once(monkeypatch, tmp_path):
    log = tmp_path / "tools.jsonl"
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(log))

    outcome = call_tool(
        {
            "name": "check_decision_drift",
            "arguments": json.dumps({
                "state": {"database": "PostgreSQL"},
                "candidate": {"database": "MongoDB"},
            }),
        },
        tools_for(None),
        None,
    )

    assert outcome["ok"]
    assert outcome["result"]["status"] == "drift"

    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert "PostgreSQL" not in lines[0]
    assert "MongoDB" not in lines[0]


def test_model_cannot_inject_caller_identity():
    with pytest.raises(ValidationError):
        DriftArguments(
            state={"database": "PostgreSQL"},
            candidate={"database": "MongoDB"},
            caller_id="another-user",
        )
