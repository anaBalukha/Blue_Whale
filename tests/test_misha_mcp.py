import asyncio

from mcp import Client

from src.mcp_server import mcp
from src.tools import TOOLS


async def inspect_server():
    async with Client(mcp) as client:
        listed = (await client.list_tools()).tools
        return listed


def test_mcp_exposes_registered_tool():
    listed = asyncio.run(inspect_server())
    names = {item.name for item in listed}
    assert "search_trusted_sources" in names
    assert names == set(TOOLS)


def test_mcp_contract_rejects_unknown_fields():
    async def run():
        async with Client(mcp) as client:
            return await client.call_tool(
                "search_trusted_sources",
                {
                    "question": "Which interface does Blue Whale use?",
                    "caller_id": "somebody-else",
                },
            )

    result = asyncio.run(run())
    assert result.is_error


def test_mcp_retrieves_real_trusted_document():
    async def run():
        async with Client(mcp) as client:
            return await client.call_tool(
                "search_trusted_sources",
                {
                    "question": "Which interface is planned for Blue Whale MVP?",
                    "limit": 3,
                },
            )

    result = asyncio.run(run())

    assert not result.is_error, result.content

    data = result.structured_content
    assert data is not None
    assert data["count"] >= 1

    returned_docs = {
        source["document_id"]
        for source in data["sources"]
    }

    assert "project/terminal-first" in returned_docs


def test_mcp_and_function_calling_expose_same_arguments():
    listed = asyncio.run(inspect_server())
    mcp_tool = next(
        tool for tool in listed
        if tool.name == "search_trusted_sources"
    )

    mcp_schema = mcp_tool.input_schema
    function_schema = TOOLS[
        "search_trusted_sources"
    ].schema()["function"]["parameters"]

    assert set(mcp_schema["properties"]) == set(
        function_schema["properties"]
    )

    assert set(mcp_schema["required"]) == set(
        function_schema["required"]
    )


def test_mcp_and_function_calling_match_constraints():
    """Verify matching advertised field validation constraints."""
    listed = asyncio.run(inspect_server())

    mcp_tool = next(
        tool for tool in listed
        if tool.name == "search_trusted_sources"
    )

    mcp_schema = mcp_tool.input_schema
    function_schema = TOOLS[
        "search_trusted_sources"
    ].schema()["function"]["parameters"]

    assert set(mcp_schema["properties"]) == set(
        function_schema["properties"]
    )

    assert set(mcp_schema["required"]) == set(
        function_schema["required"]
    )

    keys = (
        "type",
        "pattern",
        "minLength",
        "maxLength",
        "minimum",
        "maximum",
        "default",
    )

    for field in ("question", "limit"):
        mcp_field = mcp_schema["properties"][field]
        function_field = function_schema["properties"][field]

        for key in keys:
            assert mcp_field.get(key) == function_field.get(key), (
                f"Schema mismatch: {field}.{key}"
            )

    assert function_schema["additionalProperties"] is False


def test_mcp_rejects_out_of_range_limit():
    """Verify that the MCP runtime enforces numeric bounds."""
    async def run():
        async with Client(mcp) as client:
            return await client.call_tool(
                "search_trusted_sources",
                {
                    "question": (
                        "Which interface is planned for Blue Whale MVP?"
                    ),
                    "limit": 100,
                },
            )

    result = asyncio.run(run())
    assert result.is_error
