"""Run each HW2 golden through the real tool gates."""
import json
from pathlib import Path

import pytest
import yaml

from src.act import call_tool
from src.tools import tools_for

ROOT = Path(__file__).resolve().parents[1]
FILES = sorted((ROOT / "evals/tools").glob("*.yaml"))
CASES = [
    (f.stem, case)
    for f in FILES
    for case in yaml.safe_load(f.read_text())["cases"]
]


def subset(expected, actual):
    return isinstance(actual, dict) and all(
        actual.get(k) == v for k, v in expected.items()
    )


@pytest.mark.parametrize("owner,case", CASES)
def test_tool_golden_case(owner, case):
    call = {
        "id": case["id"],
        "name": case["tool"],
        "arguments": json.dumps(case["arguments"]),
    }
    out = call_tool(call, tools_for(case.get("caller")), case.get("caller"))
    if case["expect"] == "ok":
        assert out["ok"], f"{owner}: {out['error']}"
        assert subset(case.get("result_has", {}), out["result"])
        expected_doc = case.get("must_include_document")
        if expected_doc:
            returned = {
                source["document_id"]
                for source in out["result"]["sources"]
            }
            assert expected_doc in returned, (
                f"{owner}: missing required source {expected_doc}"
            )
    else:
        assert not out["ok"], f"{owner}: unexpected success"
        for phrase in case.get("error_has", []):
            assert phrase.lower() in out["error"].lower()


def test_golden_coverage():
    assert FILES, "No HW2 golden sets found"
    for file in FILES:
        cases = yaml.safe_load(file.read_text())["cases"]
        types = [case["type"] for case in cases]
        assert len(cases) >= 5
        assert types.count("normal") >= 3
        assert "bad-input" in types
        assert "adversarial" in types
