import json
import subprocess
import sys
from pathlib import Path

import pytest

# Resolve the script relative to this file so the tests pass from any folder.
BUILDER = Path(__file__).resolve().parent / "src" / "checkpoint_builder.py"


def run_builder(arg_str):
    cmd = [sys.executable, str(BUILDER), arg_str]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip()


def assert_invalid(payload_text):
    code, out = run_builder(payload_text)
    assert code == 2
    data = json.loads(out)
    assert data["error"]["code"] == "INVALID_INPUT"
    assert "checkpoint" not in data
    return data["error"]["message"]


def test_checkpoint_builder_override():
    payload = {
        "previous": {"version": 1, "decisions": {"database": "PostgreSQL", "framework": "FastAPI"}},
        "user_changes": {"database": "MongoDB"}
    }
    code, out = run_builder(json.dumps(payload))
    assert code == 0
    data = json.loads(out)
    assert data["checkpoint"]["version"] == 2
    assert data["checkpoint"]["decisions"]["database"] == "MongoDB"
    assert data["checkpoint"]["decisions"]["framework"] == "FastAPI"
    assert data["changed_fields"] == ["database"]


def test_checkpoint_builder_noop():
    payload = {
        "previous": {"version": 2, "decisions": {"database": "MongoDB"}},
        "user_changes": {"database": "MongoDB"}
    }
    code, out = run_builder(json.dumps(payload))
    assert code == 0
    data = json.loads(out)
    assert data["checkpoint"]["version"] == 2
    assert data["changed_fields"] == []


def test_checkpoint_builder_new_field():
    payload = {
        "previous": {"version": 1, "decisions": {"database": "PostgreSQL"}},
        "user_changes": {"framework": "FastAPI"}
    }
    code, out = run_builder(json.dumps(payload))
    assert code == 0
    data = json.loads(out)
    assert data["checkpoint"]["version"] == 2
    assert data["checkpoint"]["decisions"]["framework"] == "FastAPI"
    assert data["changed_fields"] == ["framework"]


def test_checkpoint_builder_invalid_input():
    payload = {
        "previous": {"version": -1, "decisions": {}},
        "user_changes": {}
    }
    code, out = run_builder(json.dumps(payload))
    assert code == 2
    data = json.loads(out)
    assert "error" in data
    assert data["error"]["code"] == "INVALID_INPUT"


def test_changed_fields_sorted_and_version_increments_once():
    payload = {
        "previous": {"version": 0, "decisions": {"database": "PostgreSQL"}},
        "user_changes": {"ui": "Terminal", "database": "MongoDB", "cache": "Redis"},
    }
    code, out = run_builder(json.dumps(payload))
    assert code == 0
    data = json.loads(out)
    assert data["changed_fields"] == ["cache", "database", "ui"]
    assert data["checkpoint"]["version"] == 1


def test_unknown_authorization_field_is_refused():
    payload = {
        "previous": {"version": 1, "decisions": {"database": "PostgreSQL"}},
        "user_changes": {"database": "MongoDB"},
        "authorized": True,
    }
    message = assert_invalid(json.dumps(payload))
    assert "exactly 'previous' and 'user_changes'" in message


def test_unknown_field_inside_previous_is_refused():
    payload = {
        "previous": {"version": 1, "decisions": {"database": "PostgreSQL"}, "confirmed_by": "user"},
        "user_changes": {"database": "MongoDB"},
    }
    assert_invalid(json.dumps(payload))


@pytest.mark.parametrize("payload_text", [
    "not json",
    "[]",
    json.dumps({"previous": {"version": True, "decisions": {}}, "user_changes": {}}),
    json.dumps({"previous": {"version": "1", "decisions": {}}, "user_changes": {}}),
    json.dumps({"previous": {"version": 1, "decisions": {"database": "PostgreSQL"}},
                "user_changes": {"decisions": {"database": "MongoDB"}}}),
    json.dumps({"previous": {"version": 1, "decisions": {}}, "user_changes": {"database": 5}}),
    json.dumps({"previous": {"version": 1}, "user_changes": {}}),
])
def test_malformed_payloads_are_refused(payload_text):
    assert_invalid(payload_text)
