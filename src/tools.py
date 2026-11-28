"""Blue Whale tool registry: one contract for both interfaces."""
from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel

from .contracts import SearchArguments
from .contracts import GroundedAnswerArguments
from .team_answer_tool import run_grounded_answer
from .contracts import DriftArguments
from .ana_drift_tool import DriftResult, run_drift
from .index import IndexMismatch, load
from .lexo_checkpoint_tool import PreviewCheckpointUpdateArgs, PreviewResult, run_preview_checkpoint_update
from .misha_retrieval_tool import ToolFailure, search_trusted_sources


class SearchResult(BaseModel):
    count: int
    sources: list[dict]


def run_search(args: SearchArguments) -> SearchResult:
    import os
    from .chunk import load_corpus
    from .index import CORPUS, build

    try:
        if os.environ.get("BLUE_WHALE_OFFLINE") == "1":
            chunks = load_corpus(CORPUS)
            if not chunks:
                raise ToolFailure(
                    "Trusted corpus is empty. "
                    "Ask the operator to restore the trusted documents."
                )
            index = build(chunks)
        else:
            index = load()
    except (OSError, IndexMismatch, ValueError) as exc:
        raise ToolFailure(
            "Trusted index unavailable. Ask the operator to rebuild it."
        ) from exc

    return SearchResult.model_validate(
        search_trusted_sources(index, args)
    )


@dataclass(frozen=True)
class Tool:
    name: str
    args: type[BaseModel]
    run: Callable
    description: str
    writes: bool = False

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args.model_json_schema(),
            },
        }


TOOLS = {
    "search_trusted_sources": Tool(
        name="search_trusted_sources",
        args=SearchArguments,
        run=run_search,
        description="Find cited evidence in trusted project documents.",
    ),
    "check_decision_drift": Tool(
        name="check_decision_drift",
        args=DriftArguments,
        run=run_drift,
        description=(
            "Compare supplied prior and proposed project decisions "
            "without modifying either."
        ),
    ),
    "preview_checkpoint_update": Tool(
        name="preview_checkpoint_update",
        args=PreviewCheckpointUpdateArgs,
        run=run_preview_checkpoint_update,
        description=(
            "Calculate a proposed versioned checkpoint and changed fields "
            "without modifying trusted state (read-only preview)."
        ),
    ),
    "answer_from_trusted_sources": Tool(
        name="answer_from_trusted_sources",
        args=GroundedAnswerArguments,
        run=run_grounded_answer,
        description=(
            "Answer a project question using trusted Blue Whale "
            "documents. Return validated citations or a safe refusal. "
            "Does not modify trusted state."
        ),
        writes=False,
    ),
}


def tools_for(caller: str | None) -> dict[str, Tool]:
    return {
        name: tool
        for name, tool in TOOLS.items()
        if caller is not None or not tool.writes
    }
