import json

import numpy as np

from src import tools
from src.act import call_tool
from src.chunk import Chunk
from src.index import Index
from src.retrieve import Hit


def request(**arguments):
    return {
        "id": "test-call",
        "name": "search_trusted_sources",
        "arguments": json.dumps(arguments),
    }


def test_unknown_tool_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(tmp_path / "log"))
    out = call_tool(
        {"name": "delete_all", "arguments": "{}"},
        tools.tools_for(None),
        None,
    )
    assert not out["ok"]


def test_identity_spoofing_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(tmp_path / "log"))
    out = call_tool(
        request(
            question="Which interface does Blue Whale use?",
            caller_id="someone-else",
        ),
        tools.tools_for(None),
        None,
    )
    assert not out["ok"]
    assert "caller_id" in out["error"]


def test_valid_call_through_gate(tmp_path, monkeypatch):
    monkeypatch.setenv("BLUE_WHALE_TOOL_LOG", str(tmp_path / "log"))
    chunk = Chunk(
        id="project/test#1",
        doc_id="project/test",
        title="Test",
        section="MVP",
        text="The MVP uses a terminal.",
    )
    index = Index(
        chunks=[chunk],
        vectors=np.array([[1.0]], dtype=np.float32),
        model="test",
    )
    monkeypatch.setattr(tools, "load", lambda: index)
    monkeypatch.setattr(
        "src.misha_retrieval_tool.hybrid",
        lambda *args, **kwargs: [Hit(chunk, 0.92)],
    )

    out = call_tool(
        request(question="Which interface does Blue Whale use?"),
        tools.tools_for(None),
        None,
    )
    assert out["ok"]
    assert out["result"]["count"] == 1
    assert len((tmp_path / "log").read_text().splitlines()) == 1
