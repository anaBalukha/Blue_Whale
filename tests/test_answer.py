from types import SimpleNamespace

from src.answer import answer


def make_hit(score=0.9):
    return SimpleNamespace(
        score=score,
        chunk=SimpleNamespace(
            id="test-doc#1",
            doc_id="test-doc",
            title="Test document",
            section="Rules",
            text="Blue Whale uses a terminal interface."
        )
    )


def test_invented_citation_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr("src.answer.ANSWER_LOG", tmp_path / "answers.jsonl")
    monkeypatch.setenv("BLUE_WHALE_MIN_SCORE", "0.3")

    result = answer(
        None,
        "Which interface?",
        retrieve=lambda *args, **kwargs: [make_hit()],
        llm=lambda *args, **kwargs: {
            "answer": "Blue Whale uses a terminal interface [2].",
            "citations": [2],
            "grounded": True,
        },
    )

    assert result.status == "refused"
    assert "never retrieved" in result.reason


def test_low_score_refuses_without_model_call(tmp_path, monkeypatch):
    monkeypatch.setattr("src.answer.ANSWER_LOG", tmp_path / "answers.jsonl")
    monkeypatch.setenv("BLUE_WHALE_MIN_SCORE", "0.7")

    def forbidden_model(*args, **kwargs):
        raise AssertionError("Model must not be called")

    result = answer(
        None,
        "Unrelated question",
        retrieve=lambda *args, **kwargs: [make_hit(score=0.1)],
        llm=forbidden_model,
    )

    assert result.status == "refused"
    assert "below threshold" in result.reason


def test_valid_citation_maps_to_document(tmp_path, monkeypatch):
    monkeypatch.setattr("src.answer.ANSWER_LOG", tmp_path / "answers.jsonl")
    monkeypatch.setenv("BLUE_WHALE_MIN_SCORE", "0.3")

    result = answer(
        None,
        "Which interface?",
        retrieve=lambda *args, **kwargs: [make_hit()],
        llm=lambda *args, **kwargs: {
            "answer": "Blue Whale uses a terminal interface [1].",
            "citations": [1],
            "grounded": True,
        },
    )

    assert result.status == "answered"
    assert result.sources[0]["doc_id"] == "test-doc"
