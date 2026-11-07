"""Blue Whale MCP server using the same tool contract and gates."""
import json

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from .act import call_tool
from .contracts import Question, Limit
from .tools import SearchResult, tools_for


mcp = MCPServer(
    "blue-whale",
    instructions="Read trusted evidence without modifying decisions.",
)

READ_ONLY = ToolAnnotations(
    read_only_hint=True,
    open_world_hint=False,
)


@mcp.tool(
    annotations=READ_ONLY,
    description="Search trusted Blue Whale project documents.",
)
def search_trusted_sources(
    question: Question,
    ctx: Context,
    limit: Limit = 3,
) -> SearchResult:
    # SDK 2.x may ignore unknown parameters when binding a function.
    # Read the original request to enforce our strict Pydantic contract.
    params = ctx.request_context.params or {}
    raw = params.get("arguments")

    if not isinstance(raw, dict):
        raw = {"question": question, "limit": limit}

    outcome = call_tool(
        {
            "id": str(ctx.request_id),
            "name": "search_trusted_sources",
            "arguments": json.dumps(raw),
        },
        tools_for(None),
        None,
    )

    if not outcome["ok"]:
        raise ToolError(outcome["error"])

    return SearchResult.model_validate(outcome["result"])


if __name__ == "__main__":
    mcp.run()
