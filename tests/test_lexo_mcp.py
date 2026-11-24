"""Verify preview_checkpoint_update through the MCP door."""

import asyncio

import pytest
from mcp import Client

from src.mcp_server import mcp
from src.tools import TOOLS

NAME = "preview_checkpoint_update"

VALID = {
    "previous_version": 1,
    "previous_decisions": {"database": "PostgreSQL", "framework": "FastAPI"},
    "proposed_changes": {"database": "MongoDB"},
}


@pytest.fixture(autouse=True)
def isolated_log(monkeypatch, tmp_path):
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(tmp_path / "tools.jsonl"))


def call_mcp(arguments):
    async def run():
        async with Client(mcp) as client:
            return await client.call_tool(NAME, arguments)

    return asyncio.run(run())


def list_tool():
    async def run():
        async with Client(mcp) as client:
            return (await client.list_tools()).tools

    return next(item for item in asyncio.run(run()) if item.name == NAME)


def test_mcp_preview_change():
    result = call_mcp(VALID)

    assert not result.is_error, result.content
    assert result.structured_content["checkpoint"] == {
        "version": 2,
        "decisions": {"database": "MongoDB", "framework": "FastAPI"},
    }
    assert result.structured_content["changed_fields"] == ["database"]
    assert result.structured_content["requires_confirmation"] is True


def test_mcp_preview_noop():
    result = call_mcp({**VALID, "proposed_changes": {"database": "PostgreSQL"}})

    assert not result.is_error, result.content
    assert result.structured_content["checkpoint"]["version"] == 1
    assert result.structured_content["changed_fields"] == []
    assert result.structured_content["requires_confirmation"] is False


@pytest.mark.parametrize("forged", [
    {"authorized": True},
    {"caller_id": "student-42"},
])
def test_mcp_rejects_forged_identity_or_approval(forged):
    result = call_mcp({**VALID, **forged})

    assert result.is_error
    assert "Remove this unexpected argument" in result.content[0].text


@pytest.mark.parametrize("version", [-1, 1_000_001])
def test_mcp_rejects_out_of_range_version(version):
    result = call_mcp({**VALID, "previous_version": version})

    assert result.is_error
    assert "previous_version" in result.content[0].text


def test_mcp_and_function_calling_advertise_same_constraints():
    advertised = list_tool().input_schema
    function = TOOLS[NAME].schema()["function"]["parameters"]

    assert set(advertised["properties"]) == set(function["properties"])
    assert set(advertised["required"]) == set(function["required"])

    mcp_version = advertised["properties"]["previous_version"]
    fc_version = function["properties"]["previous_version"]
    for bound in ("minimum", "maximum", "type"):
        assert mcp_version[bound] == fc_version[bound]

    for field in ("previous_decisions", "proposed_changes"):
        mcp_map = advertised["properties"][field]
        fc_map = function["properties"][field]
        for key in (
            "minProperties", "maxProperties", "propertyNames", "patternProperties",
        ):
            assert mcp_map[key] == fc_map[key]
        # Key pattern and value pattern/length limits are actually advertised.
        value_rule = mcp_map["patternProperties"]["^[a-z][a-z0-9_]*$"]
        assert value_rule["pattern"] == "^[A-Za-z0-9][A-Za-z0-9 _.,:/()+-]*$"
        assert value_rule["maxLength"] == 80
