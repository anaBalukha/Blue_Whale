"""Protocol-level validation, audit and schema regression tests."""

import asyncio
import json

import pytest
from jsonschema import Draft202012Validator
from mcp import Client

from src.act import call_tool
from src.mcp_server import mcp
from src.tools import TOOLS, tools_for


MARKER = "PrivateMarker"

SEARCH = {
    "question": "Which interface is planned for Blue Whale MVP?",
    "limit": 3,
}

DRIFT = {
    "state": {"database": "PostgreSQL"},
    "candidate": {"database": "MongoDB"},
}

PREVIEW = {
    "previous_version": 1,
    "previous_decisions": {"database": "PostgreSQL"},
    "proposed_changes": {"database": "MongoDB"},
}

CASES = [
    (
        "search_trusted_sources",
        {**SEARCH, "question": MARKER + "@bad"},
        False,
    ),
    (
        "search_trusted_sources",
        {**SEARCH, "limit": 100},
        False,
    ),
    (
        "search_trusted_sources",
        {**SEARCH, "caller_id": MARKER},
        False,
    ),
    (
        "search_trusted_sources",
        {"limit": 3},
        False,
    ),
    (
        "search_trusted_sources",
        SEARCH,
        True,
    ),
    (
        "check_decision_drift",
        {**DRIFT, "state": {"database": MARKER + "!!!"}},
        False,
    ),
    (
        "check_decision_drift",
        {**DRIFT, "state": {"DB": "PostgreSQL"}},
        False,
    ),
    (
        "check_decision_drift",
        {**DRIFT, "user_changes": {"database": MARKER}},
        False,
    ),
    (
        "check_decision_drift",
        DRIFT,
        True,
    ),
    (
        "preview_checkpoint_update",
        {**PREVIEW, "previous_version": -1},
        False,
    ),
    (
        "preview_checkpoint_update",
        {
            **PREVIEW,
            "proposed_changes": {"database": MARKER + "!!!"},
        },
        False,
    ),
    (
        "preview_checkpoint_update",
        {**PREVIEW, "authorized": True},
        False,
    ),
    (
        "preview_checkpoint_update",
        PREVIEW,
        True,
    ),
]


def records(path):
    if not path.exists():
        return []

    return [
        json.loads(line)
        for line in path.read_text(
            encoding="utf-8"
        ).splitlines()
    ]


@pytest.mark.parametrize("name,args,expected", CASES)
def test_protocol_boundary(
    name, args, expected, monkeypatch, tmp_path
):
    log = tmp_path / "tools.jsonl"

    monkeypatch.setenv(
        "BLUE_WHALE_TOOL_LOG",
        str(log),
    )

    direct = call_tool(
        {
            "id": "direct-test",
            "name": name,
            "arguments": json.dumps(args),
        },
        tools_for(None),
        None,
    )

    assert direct["ok"] == expected
    assert len(records(log)) == 1

    log.unlink()

    async def run():
        async with Client(mcp) as client:
            listed = (await client.list_tools()).tools

            schema = next(
                tool.input_schema
                for tool in listed
                if tool.name == name
            )

            result = await client.call_tool(name, args)

            return result, schema

    result, mcp_schema = asyncio.run(run())

    assert (not result.is_error) == expected

    logged = records(log)

    assert len(logged) == 1
    assert logged[0]["tool"] == name
    assert logged[0]["ok"] == expected

    text = " ".join(
        getattr(item, "text", "")
        for item in result.content
    )

    if expected:
        assert result.structured_content == direct["result"]
        assert logged[0]["error"] is None
    else:
        assert direct["error"] in text
        assert logged[0]["error"] == direct["error"]
        assert MARKER not in text
        assert MARKER not in log.read_text(
            encoding="utf-8"
        )

    function_schema = TOOLS[
        name
    ].schema()["function"]["parameters"]

    assert Draft202012Validator(
        mcp_schema
    ).is_valid(args) == expected

    assert Draft202012Validator(
        function_schema
    ).is_valid(args) == expected


@pytest.mark.parametrize("name", list(TOOLS))
def test_complete_schema_parity(name):
    async def run():
        async with Client(mcp) as client:
            return (await client.list_tools()).tools

    listed = asyncio.run(run())

    advertised = next(
        tool.input_schema
        for tool in listed
        if tool.name == name
    )

    expected = TOOLS[
        name
    ].schema()["function"]["parameters"]

    Draft202012Validator.check_schema(advertised)

    assert advertised == expected
    assert advertised["additionalProperties"] is False
