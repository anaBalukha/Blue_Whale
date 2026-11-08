"""Verify Ana's tool through the MCP interface."""

import asyncio

from mcp import Client

from src.mcp_server import mcp
from src.tools import TOOLS


async def call_mcp(arguments):
    async with Client(mcp) as client:
        return await client.call_tool(
            "check_decision_drift",
            arguments,
        )


def test_mcp_detects_conflict():
    result = asyncio.run(call_mcp({
        "state": {"database": "PostgreSQL"},
        "candidate": {"database": "MongoDB"},
    }))

    assert not result.is_error, result.content
    assert result.structured_content["status"] == "drift"


def test_mcp_refuses_forged_override():
    result = asyncio.run(call_mcp({
        "state": {"database": "PostgreSQL"},
        "candidate": {"database": "MongoDB"},
        "user_changes": {"database": "MongoDB"},
    }))

    assert result.is_error


def test_mcp_and_function_calling_match_fields():
    async def inspect():
        async with Client(mcp) as client:
            return (await client.list_tools()).tools

    listed = asyncio.run(inspect())

    mcp_tool = next(
        item for item in listed
        if item.name == "check_decision_drift"
    )

    function_schema = TOOLS[
        "check_decision_drift"
    ].schema()["function"]["parameters"]

    assert set(mcp_tool.input_schema["properties"]) == {
        "state",
        "candidate",
    }

    assert set(mcp_tool.input_schema["properties"]) == set(
        function_schema["properties"]
    )
