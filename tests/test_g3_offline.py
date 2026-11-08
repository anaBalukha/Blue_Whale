"""Regression test for multi-document offline grounding."""

import yaml

from src.answer import answer
from src.chunk import load_corpus
from src.index import CORPUS, build
from evals.run_golden import score


def test_g3_uses_both_trusted_decisions(monkeypatch, tmp_path):
    monkeypatch.setenv("BLUE_WHALE_MIN_SCORE", "0.30")
    monkeypatch.setattr(
        "src.answer.ANSWER_LOG",
        tmp_path / "answers.jsonl",
    )

    spec = yaml.safe_load(
        open("evals/golden.yaml", encoding="utf-8")
    )
    item = next(
        item for item in spec["items"]
        if item["id"] == "g3"
    )

    index = build(load_corpus(CORPUS))
    result = answer(index, item["question"], k=5)

    passed, reasons = score(item, result)

    assert passed, reasons
    assert result.status == "answered"
    assert len({
        source["doc_id"] for source in result.sources
    }) >= 2
