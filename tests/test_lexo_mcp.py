"""Verify PreviewCheckpointUpdate tool through the MCP interface."""

import asyncio
import json

from mcp import Client

from src.mcp_server import mcp


async def call_mcp(arguments):
    async with Client(mcp) as client:
        return await client.call_tool(
            "preview_checkpoint_update",
            arguments,
        )


def test_mcp_preview_conflict():
    result = asyncio.run(call_mcp({
        "previous_version": 1,
        "previous_decisions": {"database": "PostgreSQL", "framework": "FastAPI"},
        "proposed_changes": {"database": "MongoDB"}
    }))

    assert not result.is_error, result.content
    assert result.structured_content["checkpoint"]["version"] == 2
    assert result.structured_content["changed_fields"] == ["database"]
    assert result.structured_content["requires_confirmation"] is True


def test_mcp_preview_noop():
    result = asyncio.run(call_mcp({
        "previous_version": 2,
        "previous_decisions": {"database": "PostgreSQL", "framework": "FastAPI"},
        "proposed_changes": {"database": "PostgreSQL", "framework": "FastAPI"}
    }))

    assert not result.is_error, result.content
    assert result.structured_content["checkpoint"]["version"] == 2
    assert result.structured_content["changed_fields"] == []
    assert result.structured_content["requires_confirmation"] is False


def test_mcp_and_function_calling_match_fields():
    async def inspect():
        async with Client(mcp) as client:
            return (await client.list_tools()).tools

    listed = asyncio.run(inspect())

    mcp_tool = next(
        item for item in listed
        if item.name == "preview_checkpoint_update"
    )

    function_schema = mcp_tool.input_schema

    assert set(mcp_tool.input_schema["properties"]) == {
        "previous_version",
        "previous_decisions",
        "proposed_changes",
    }

    assert set(function_schema["properties"]) == {
        "previous_version",
        "previous_decisions",
        "proposed_changes",
    }