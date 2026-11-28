"""Shared Lab 5 read-only grounded answer tool."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from . import answer as answer_pipeline
from . import llm
from . import index as trusted_index
from .chunk import load_corpus
from .contracts import GroundedAnswerArguments
from .misha_retrieval_tool import ToolFailure


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    n: int
    chunk_id: str
    doc_id: str
    title: str
    section: str


class GroundedAnswerResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["answered", "refused"]
    text: str
    sources: list[SourceReference]


def run_grounded_answer(
    args: GroundedAnswerArguments,
) -> GroundedAnswerResult:
    """Reuse the existing grounded pipeline with citation checks."""

    try:
        if llm.OFFLINE:
            chunks = load_corpus(trusted_index.CORPUS)

            if not chunks:
                raise ToolFailure(
                    "Trusted corpus is empty. "
                    "Ask the operator to restore it."
                )

            index = trusted_index.build(chunks)
        else:
            index = trusted_index.load()

        if not index.chunks:
            raise ToolFailure(
                "Trusted index is empty. "
                "Ask the operator to rebuild it."
            )

    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        trusted_index.IndexMismatch,
    ) as exc:
        raise ToolFailure(
            "Trusted index unavailable. "
            "Ask the operator to rebuild it."
        ) from exc

    result = answer_pipeline.answer(
        index,
        args.question,
        k=args.limit,
        check=True,
    )

    return GroundedAnswerResult(
        status=result.status,
        text=result.text,
        sources=result.sources,
    )
