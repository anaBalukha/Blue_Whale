"""Tests for Blue Whale's supervised function-calling loop."""
import json
from dataclasses import replace

import pytest

from src import tools
from src.act import MAX_ROUNDS, act


def request(limit=3):
    return {
        "id": "call-1",
        "name": "search_trusted_sources",
        "arguments": json.dumps({
            "question": "Which interface does Blue Whale use?",
            "limit": limit,
        }),
    }


@pytest.fixture
def fake_search(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "BLUE_WHALE_TOOL_LOG",
        str(tmp_path / "tool-calls.jsonl"),
    )

    def search(args):
        return tools.SearchResult(
            count=1,
            sources=[{
                "document_id": "project/terminal-first",
                "excerpt": "Blue Whale uses a terminal interface.",
            }],
        )

    original = tools.TOOLS["search_trusted_sources"]
    monkeypatch.setitem(
        tools.TOOLS,
        "search_trusted_sources",
        replace(original, run=search),
    )
    return tmp_path / "tool-calls.jsonl"


def test_model_calls_tool_then_answers(fake_search):
    turns = []

    def model(messages, schemas):
        turns.append(messages)
        assert schemas[0]["function"]["name"] == "search_trusted_sources"

        if len(turns) == 1:
            return {"content": None, "tool_calls": [request()]}

        assert messages[-1]["role"] == "tool"
        data = json.loads(messages[-1]["content"])
        assert data["count"] == 1

        return {
            "content": "Blue Whale uses a terminal interface [1].",
            "tool_calls": [],
        }

    result = act("Which interface does Blue Whale use?", llm=model)

    assert result.status == "answered"
    assert len(result.calls) == 1
    assert result.calls[0]["ok"]
    assert len(fake_search.read_text().splitlines()) == 1


def test_model_repairs_invalid_arguments(fake_search):
    turns = []

    def model(messages, schemas):
        turns.append(messages)

        if len(turns) == 1:
            return {"content": None, "tool_calls": [request(100)]}

        if len(turns) == 2:
            assert "invalid arguments" in messages[-1]["content"]
            return {"content": None, "tool_calls": [request(3)]}

        return {"content": "Evidence found [1].", "tool_calls": []}

    result = act("Find project evidence", llm=model)

    assert result.status == "answered"
    assert [call["ok"] for call in result.calls] == [False, True]
    assert len(fake_search.read_text().splitlines()) == 2


def test_loop_respects_round_budget(fake_search):
    def model(messages, schemas):
        return {"content": None, "tool_calls": [request(100)]}

    result = act("Find project evidence", llm=model)

    assert result.status == "stopped"
    assert len(result.calls) == MAX_ROUNDS
    assert all(not call["ok"] for call in result.calls)
