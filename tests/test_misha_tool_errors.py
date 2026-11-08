"""Security regression tests for the HW2 tool execution gates."""

import json
from dataclasses import replace

from src.act import call_tool
from src.tools import TOOLS, tools_for


QUESTION = "Which interface is planned for Blue Whale MVP?"


def test_unexpected_timeout_is_safe_and_logged(
    monkeypatch, tmp_path
):
    log = tmp_path / "tools.jsonl"
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(log))

    private_path = "/private/example/secret.txt"

    def failing_retrieval(args):
        raise TimeoutError(
            f"Retrieval timed out while reading {private_path}"
        )

    original = TOOLS["search_trusted_sources"]
    failing = replace(original, run=failing_retrieval)

    result = call_tool(
        {
            "name": "search_trusted_sources",
            "arguments": json.dumps({
                "question": QUESTION,
                "limit": 3,
            }),
        },
        {"search_trusted_sources": failing},
        None,
    )

    assert result["ok"] is False
    assert result["result"] is None
    assert "check the service" in result["error"]
    assert private_path not in str(result)

    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1

    recorded = json.loads(lines[0])
    assert recorded["ok"] is False
    assert private_path not in lines[0]


def test_malicious_field_name_is_not_reflected(
    monkeypatch, tmp_path
):
    log = tmp_path / "tools.jsonl"
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(log))

    private_path = "/private/example"

    result = call_tool(
        {
            "name": "search_trusted_sources",
            "arguments": json.dumps({
                "question": QUESTION,
                private_path: "malicious value",
            }),
        },
        tools_for(None),
        None,
    )

    assert result["ok"] is False
    assert "invalid arguments" in result["error"]
    assert private_path not in str(result)

    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert private_path not in lines[0]


def test_normal_identity_spoofing_still_names_field(
    monkeypatch, tmp_path
):
    monkeypatch.setenv(
        "BLUE_WHALE_TOOL_LOG",
        str(tmp_path / "tools.jsonl"),
    )

    result = call_tool(
        {
            "name": "search_trusted_sources",
            "arguments": json.dumps({
                "question": QUESTION,
                "caller_id": "another-user",
            }),
        },
        tools_for(None),
        None,
    )

    assert result["ok"] is False
    assert "caller_id" in result["error"]


def test_private_looking_field_name_is_hidden(monkeypatch, tmp_path):
    log = tmp_path / "tools.jsonl"
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(log))

    result = call_tool(
        {
            "name": "search_trusted_sources",
            "arguments": json.dumps({
                "question": QUESTION,
                "PrivateCaseAlice123": "secret",
            }),
        },
        tools_for(None),
        None,
    )

    assert result["ok"] is False
    assert "unexpected_argument" in result["error"]
    assert "PrivateCaseAlice123" not in str(result)
    assert "PrivateCaseAlice123" not in log.read_text()


def test_unknown_tool_name_is_hidden(monkeypatch, tmp_path):
    log = tmp_path / "tools.jsonl"
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(log))

    result = call_tool(
        {
            "name": "PrivateCaseAlice123",
            "arguments": "{}",
        },
        tools_for(None),
        None,
    )

    assert result["ok"] is False
    assert result["tool"] == "unknown_tool"
    assert "PrivateCaseAlice123" not in str(result)
    assert "PrivateCaseAlice123" not in log.read_text()


def test_unavailable_audit_log_returns_safe_failure(
    monkeypatch, tmp_path
):
    from dataclasses import replace
    from src.tools import SearchResult

    # A directory cannot be opened as the JSONL log file.
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(tmp_path))

    original = TOOLS["search_trusted_sources"]
    fake = replace(
        original,
        run=lambda args: SearchResult(count=0, sources=[]),
    )

    result = call_tool(
        {
            "name": "search_trusted_sources",
            "arguments": json.dumps({"question": QUESTION}),
        },
        {"search_trusted_sources": fake},
        None,
    )

    assert result["ok"] is False
    assert result["result"] is None
    assert "Audit logging unavailable" in result["error"]
    assert str(tmp_path) not in str(result)
