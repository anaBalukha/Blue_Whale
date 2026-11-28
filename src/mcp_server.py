"""Blue Whale MCP server using the same tool contract and gates."""
import asyncio
import json

from mcp.server import MCPServer
from mcp.server.mcpserver import Context
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import CallToolResult, TextContent, ToolAnnotations

from .act import call_tool
from .contracts import Question, Limit, DecisionMap
from .tools import SearchResult, tools_for
from .ana_drift_tool import DriftResult
from .lexo_checkpoint_tool import CheckpointVersion, PreviewResult


class BlueWhaleMCPServer(MCPServer):
    """Expose the shared strict tool gate through MCP."""

    async def call_tool(
        self, name, arguments, context=None
    ):
        # Validate the original arguments at our own boundary.
        # Do not send them through the SDK's typed binder first.
        outcome = await asyncio.to_thread(
            call_tool,
            {
                "name": name,
                "arguments": arguments,
            },
            tools_for(None),
            None,
        )

        if not outcome["ok"]:
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=outcome["error"],
                    )
                ],
                is_error=True,
            )

        result = outcome["result"]

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(
                        result,
                        ensure_ascii=False,
                    ),
                )
            ],
            structured_content=result,
            is_error=False,
        )

    async def list_tools(self):
        registered = await super().list_tools()
        allowed = tools_for(None)

        return [
            item.model_copy(
                update={
                    "input_schema": allowed[
                        item.name
                    ].schema()["function"]["parameters"]
                }
            )
            for item in registered
            if item.name in allowed
        ]


mcp = BlueWhaleMCPServer(
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


@mcp.tool(
    annotations=READ_ONLY,
    description=(
        "Compare supplied previous project decisions with proposed "
        "decisions, without changing either."
    ),
)
def check_decision_drift(
    state: DecisionMap,
    candidate: DecisionMap,
    ctx: Context,
) -> DriftResult:
    """Use the same strict gate as the function-calling interface."""

    params = ctx.request_context.params or {}
    raw = params.get("arguments")

    if not isinstance(raw, dict):
        raw = {
            "state": state,
            "candidate": candidate,
        }

    outcome = call_tool(
        {
            "id": str(ctx.request_id),
            "name": "check_decision_drift",
            "arguments": json.dumps(raw),
        },
        tools_for(None),
        None,
    )

    if not outcome["ok"]:
        raise ToolError(outcome["error"])

    return DriftResult.model_validate(outcome["result"])


@mcp.tool(
    annotations=READ_ONLY,
    description=(
        "Calculate a proposed versioned checkpoint and changed fields "
        "without modifying trusted state (read-only preview)."
    ),
)
def preview_checkpoint_update(
    previous_version: CheckpointVersion,
    previous_decisions: DecisionMap,
    proposed_changes: DecisionMap,
    ctx: Context,
) -> PreviewResult:
    """Use the same strict gate as the function-calling interface."""

    params = ctx.request_context.params or {}
    raw = params.get("arguments")

    if not isinstance(raw, dict):
        raw = {
            "previous_version": previous_version,
            "previous_decisions": previous_decisions,
            "proposed_changes": proposed_changes,
        }

    outcome = call_tool(
        {
            "id": str(ctx.request_id),
            "name": "preview_checkpoint_update",
            "arguments": json.dumps(raw),
        },
        tools_for(None),
        None,
    )

    if not outcome["ok"]:
        raise ToolError(outcome["error"])

    return PreviewResult.model_validate(outcome["result"])


if __name__ == "__main__":
    mcp.run()
