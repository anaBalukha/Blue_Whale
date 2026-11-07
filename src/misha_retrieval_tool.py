"""Validated, read-only trusted-source retrieval for Blue Whale."""

from .contracts import SearchArguments
from .index import Index
from .retrieve import hybrid


class ToolFailure(Exception):
    """Expected failure with an actionable message for the model."""


def search_trusted_sources(
    index: Index,
    args: SearchArguments,
) -> dict:
    """Find relevant evidence in the trusted corpus without modifying it."""

    hits = hybrid(index, args.question, k=args.limit)

    relevant = [hit for hit in hits if hit.score >= 0.25]

    if not relevant:
        raise ToolFailure(
            "No relevant trusted source was found. "
            "Ask the user to clarify the question."
        )

    sources = []
    for hit in relevant:
        sources.append({
            "chunk_id": hit.chunk.id,
            "document_id": hit.chunk.doc_id,
            "title": hit.chunk.title,
            "section": hit.chunk.section,
            "excerpt": hit.chunk.text[:350],
            "score": round(hit.score, 4),
        })

    return {
        "count": len(sources),
        "sources": sources,
    }
