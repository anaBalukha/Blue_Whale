"""Offline tests for Misha's retrieval-tool core."""

import numpy as np
import pytest
from pydantic import ValidationError

from src.chunk import Chunk
from src.index import Index
from src.retrieve import Hit
from src import misha_retrieval_tool as tool


@pytest.fixture
def sample_index():
    chunk = Chunk(
        id="project/terminal-first#1",
        doc_id="project/terminal-first",
        title="Terminal-first decision",
        section="MVP",
        text="Blue Whale uses a terminal interface.",
    )
    return Index(
        chunks=[chunk],
        vectors=np.array([[1.0]], dtype=np.float32),
        model="test",
    )


def test_valid_retrieval_returns_source(monkeypatch, sample_index):
    chunk = sample_index.chunks[0]
    monkeypatch.setattr(
        tool,
        "hybrid",
        lambda index, question, k: [Hit(chunk, 0.92)],
    )

    args = tool.SearchArguments(
        question="Which interface does Blue Whale use?",
        limit=3,
    )
    result = tool.search_trusted_sources(sample_index, args)

    assert result["count"] == 1
    assert result["sources"][0]["document_id"] == "project/terminal-first"
    assert result["sources"][0]["score"] == 0.92


def test_no_relevant_source_is_refused(monkeypatch, sample_index):
    monkeypatch.setattr(tool, "hybrid", lambda *a, **k: [])

    args = tool.SearchArguments(
        question="Which hosting provider is selected?",
    )

    with pytest.raises(tool.ToolFailure, match="No relevant trusted source"):
        tool.search_trusted_sources(sample_index, args)


def test_unknown_arguments_are_forbidden():
    with pytest.raises(ValidationError):
        tool.SearchArguments(
            question="Which interface does Blue Whale use?",
            caller_id="another-user",
        )


@pytest.mark.parametrize("limit", [0, 6, -1, "3"])
def test_invalid_limit_is_refused(limit):
    with pytest.raises(ValidationError):
        tool.SearchArguments(
            question="Which interface does Blue Whale use?",
            limit=limit,
        )


def test_adversarial_path_is_refused():
    with pytest.raises(ValidationError):
        tool.SearchArguments(question="../../.env")


def test_oversized_question_is_refused():
    with pytest.raises(ValidationError):
        tool.SearchArguments(question="A" * 200)
