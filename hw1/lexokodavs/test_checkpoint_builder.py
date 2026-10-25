import subprocess
import json
import sys

def run_builder(arg_str):
    cmd = [sys.executable, "hw1/lexokodavs/src/checkpoint_builder.py", arg_str]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip()

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
