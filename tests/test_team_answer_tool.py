"""Offline contract and integration tests for the shared Lab 5 tool."""

import asyncio
import json
from functools import partial

import pytest
from mcp import Client

import src.answer as answer_pipeline
from src import llm
from src.act import call_tool, act
from src.mcp_server import mcp
from src.tools import TOOLS, tools_for


NAME = "answer_from_trusted_sources"

QUESTION = "Which interface is planned for Blue Whale MVP?"

VALID = {
    "question": QUESTION,
    "limit": 5,
}

REFUSAL_QUESTION = (
    "Which cloud provider will host Blue Whale in production?"
)


@pytest.fixture(autouse=True)
def offline_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("BLUE_WHALE_OFFLINE", "1")
    monkeypatch.setenv("BLUE_WHALE_MIN_SCORE", "0.30")

    monkeypatch.setenv(
        "BLUE_WHALE_TOOL_LOG",
        str(tmp_path / "tools.jsonl"),
    )

    monkeypatch.setattr(llm, "OFFLINE", True)

    monkeypatch.setattr(
        llm,
        "LOG_PATH",
        tmp_path / "usage.jsonl",
    )

    monkeypatch.setattr(
        answer_pipeline,
        "ANSWER_LOG",
        tmp_path / "answers.jsonl",
    )


def invoke(arguments):
    return call_tool(
        {
            "id": "team-tool-test",
            "name": NAME,
            "arguments": json.dumps(arguments),
        },
        tools_for(None),
        None,
    )


def audit_records(tmp_path):
    return [
        json.loads(line)
        for line in (
            tmp_path / "tools.jsonl"
        ).read_text(encoding="utf-8").splitlines()
    ]


def test_registered_read_only_tool():
    assert NAME in TOOLS

    tool = TOOLS[NAME]

    assert not tool.writes
    assert NAME in tools_for(None)
    assert NAME in tools_for("test-caller")

    schema = tool.schema()["function"]["parameters"]

    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"question", "limit"}

    limit = schema["properties"]["limit"]

    assert limit["minimum"] == 1
    assert limit["maximum"] == 5
    assert limit["default"] == 5


def test_grounded_answer(tmp_path):
    outcome = invoke(VALID)

    assert outcome["ok"], outcome["error"]

    result = outcome["result"]

    assert result["status"] == "answered"
    assert "terminal" in result["text"].lower()
    assert result["sources"]

    assert set(result) == {"status", "text", "sources"}

    records = audit_records(tmp_path)

    assert len(records) == 1
    assert records[0]["tool"] == NAME
    assert records[0]["ok"]

    assert QUESTION not in (
        tmp_path / "tools.jsonl"
    ).read_text(encoding="utf-8")


def test_default_limit():
    explicit = invoke(VALID)

    default = invoke({
        "question": QUESTION,
    })

    assert explicit["ok"]
    assert default["ok"]

    assert default["result"] == explicit["result"]


def test_insufficient_evidence_is_safe_refusal():
    outcome = invoke({
        "question": REFUSAL_QUESTION,
        "limit": 5,
    })

    assert outcome["ok"], outcome["error"]

    result = outcome["result"]

    assert result["status"] == "refused"
    assert result["text"] == answer_pipeline.REFUSAL
    assert result["sources"] == []


@pytest.mark.parametrize("arguments", [
    {"limit": 5},
    {**VALID, "question": "short"},
    {**VALID, "limit": 0},
    {**VALID, "limit": 6},
    {**VALID, "limit": "5"},
    {**VALID, "limit": True},
    {**VALID, "caller_id": "PrivateMarker"},
    {**VALID, "path": "PrivateMarker"},
    {**VALID, "check": False},
])
def test_invalid_arguments_never_execute(
    arguments, monkeypatch, tmp_path
):
    executed = []

    def forbidden(*args, **kwargs):
        executed.append(True)
        raise AssertionError("Answer pipeline must not run")

    monkeypatch.setattr(
        answer_pipeline,
        "answer",
        forbidden,
    )

    outcome = invoke(arguments)

    assert not outcome["ok"]
    assert outcome["result"] is None
    assert "invalid arguments" in outcome["error"]
    assert "PrivateMarker" not in outcome["error"]

    assert not executed

    records = audit_records(tmp_path)

    assert len(records) == 1
    assert records[0]["tool"] == NAME
    assert not records[0]["ok"]

    assert "PrivateMarker" not in (
        tmp_path / "tools.jsonl"
    ).read_text(encoding="utf-8")

    assert not (tmp_path / "answers.jsonl").exists()


def test_invalid_citations_are_refused(monkeypatch):
    original = answer_pipeline.answer

    def bad_model(*args, **kwargs):
        return {
            "answer": "Unsupported statement [99].",
            "citations": [99],
            "grounded": True,
        }

    monkeypatch.setattr(
        answer_pipeline,
        "answer",
        partial(original, llm=bad_model),
    )

    outcome = invoke(VALID)

    assert outcome["ok"], outcome["error"]

    result = outcome["result"]

    assert result["status"] == "refused"
    assert result["text"] == answer_pipeline.REFUSAL
    assert result["sources"] == []


def test_mcp_result_and_schema_parity(tmp_path):
    direct = invoke(VALID)

    assert direct["ok"], direct["error"]

    (tmp_path / "tools.jsonl").unlink()

    async def run():
        async with Client(mcp) as client:
            listed = (await client.list_tools()).tools

            advertised = next(
                tool for tool in listed
                if tool.name == NAME
            )

            response = await client.call_tool(
                NAME,
                VALID,
            )

            return advertised, response

    advertised, response = asyncio.run(run())

    assert not response.is_error
    assert response.structured_content == direct["result"]

    assert advertised.input_schema == (
        TOOLS[NAME].schema()["function"]["parameters"]
    )

    records = audit_records(tmp_path)

    assert len(records) == 1
    assert records[0]["tool"] == NAME
    assert records[0]["ok"]


def test_mcp_rejects_forged_identity(tmp_path):
    arguments = {
        **VALID,
        "caller_id": "PrivateMarker",
    }

    async def run():
        async with Client(mcp) as client:
            return await client.call_tool(
                NAME,
                arguments,
            )

    response = asyncio.run(run())

    assert response.is_error

    text = " ".join(
        getattr(item, "text", "")
        for item in response.content
    )

    assert "invalid arguments" in text
    assert "PrivateMarker" not in text

    records = audit_records(tmp_path)

    assert len(records) == 1
    assert records[0]["tool"] == NAME
    assert not records[0]["ok"]


def test_model_loop_can_use_team_tool(tmp_path):
    turns = []

    def model(messages, schemas):
        names = {
            schema["function"]["name"]
            for schema in schemas
        }

        assert NAME in names

        turns.append(messages[-1].copy())

        if len(turns) == 1:
            return {
                "content": None,
                "tool_calls": [{
                    "id": "team-call",
                    "name": NAME,
                    "arguments": json.dumps(VALID),
                }],
            }

        assert messages[-1]["role"] == "tool"

        result = json.loads(messages[-1]["content"])

        assert result["status"] == "answered"
        assert result["sources"]

        return {
            "content": result["text"],
            "tool_calls": [],
        }

    response = act(QUESTION, llm=model)

    assert response.status == "answered"
    assert len(response.calls) == 1
    assert response.calls[0]["ok"]
    assert len(turns) == 2
    assert len(audit_records(tmp_path)) == 1
