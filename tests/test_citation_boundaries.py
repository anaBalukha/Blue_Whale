import json
from types import SimpleNamespace

import pytest

from src.answer import answer


@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "[1].",
            "refused",
        ),
        (
            "AWS is our provider!The MVP uses a terminal [1].",
            "refused",
        ),
        (
            "AWS is our provider.The MVP uses a terminal [1].",
            "refused",
        ),
        (
            "AWS is our provider.the MVP uses a terminal [1].",
            "refused",
        ),
        (
            "The MVP uses a terminal [1].A web interface is deferred [1].",
            "answered",
        ),
        (
            "The MVP uses a terminal. [1] The hosting provider is AWS.",
            "refused",
        ),
        (
            "The MVP uses a terminal [1]. the hosting provider is AWS.",
            "refused",
        ),
        (
            "The MVP uses a terminal [1]. the hosting provider is AWS",
            "refused",
        ),
        (
            "The MVP uses a terminal [1]\nThe hosting provider is AWS",
            "refused",
        ),
        (
            "The MVP [1] uses a terminal. The hosting provider is AWS.",
            "refused",
        ),
        (
            "The MVP uses a terminal [1].",
            "answered",
        ),
        (
            "The MVP uses a terminal. [1]",
            "answered",
        ),
        (
            "The MVP uses a terminal [1]. A web interface is deferred [1].",
            "answered",
        ),
        (
            "The MVP uses a terminal. [1] a web interface is deferred. [1]",
            "answered",
        ),
        (
            "The MVP uses a terminal [1].\nA web interface is deferred [1].",
            "answered",
        ),
    ],
)
def test_citation_boundary(
    text, expected, monkeypatch, tmp_path
):
    log = tmp_path / "answers.jsonl"

    monkeypatch.setattr(
        "src.answer.ANSWER_LOG",
        log,
    )

    monkeypatch.setenv(
        "BLUE_WHALE_MIN_SCORE",
        "0.30",
    )

    hit = SimpleNamespace(
        score=0.9,
        chunk=SimpleNamespace(
            id="test-doc#1",
            doc_id="test-doc",
            title="Trusted decision",
            section="Interface",
            text=(
                "The MVP uses a terminal. "
                "A web interface is deferred."
            ),
        ),
    )

    result = answer(
        None,
        "Which interface is planned?",
        retrieve=lambda *args, **kwargs: [hit],
        llm=lambda *args, **kwargs: {
            "answer": text,
            "citations": [1],
            "grounded": True,
        },
    )

    assert result.status == expected

    if expected == "refused":
        assert "uncited" in result.reason
        assert "AWS" not in result.text
        assert not result.sources
    else:
        assert result.sources[0]["doc_id"] == "test-doc"

    records = [
        json.loads(line)
        for line in log.read_text().splitlines()
    ]

    assert len(records) == 1
    assert records[0]["status"] == expected
