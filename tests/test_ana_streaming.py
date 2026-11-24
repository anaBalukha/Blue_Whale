import json
from types import SimpleNamespace as NS

from fastapi.testclient import TestClient

from src import llm
from src.app import app
from src.chat import chat_turn


def test_offline_stream_yields_pieces_and_logs_once(
    monkeypatch, tmp_path
):
    log = tmp_path / "usage.jsonl"

    monkeypatch.setattr(llm, "OFFLINE", True)
    monkeypatch.setattr(llm, "LOG_PATH", log)

    response = llm.stream([
        {"role": "user", "content": "Hello"}
    ])

    pieces = list(response)

    assert len(pieces) > 1
    assert "".join(pieces) == response.text
    assert "Offline simulation" in response.text

    lines = log.read_text().splitlines()

    assert len(lines) == 1

    entry = json.loads(lines[0])

    assert entry["kind"] == "stream"
    assert entry["ttft_ms"] >= 0
    assert entry["completed"]
    assert entry["mode"] == "offline"
    assert not entry["usage_available"]


def test_fragmented_tool_requests_are_reassembled(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        llm, "LOG_PATH", tmp_path / "usage.jsonl"
    )

    def chunks(self):
        for index, identifier, name, arguments in [
            (1, "call-b", "second", '{"limit":'),
            (0, "call-a", "first", '{"question":'),
            (1, None, None, '3}'),
            (0, None, None, '"Hello"}'),
        ]:
            yield NS(
                content=None,
                tool_calls=[
                    NS(
                        index=index,
                        id=identifier,
                        function=NS(
                            name=name,
                            arguments=arguments,
                        ),
                    )
                ],
            ), None, {}

        self.finish_reason = "tool_calls"

        yield None, NS(
            prompt_tokens=20,
            completion_tokens=5,
        ), {}

    monkeypatch.setattr(llm.Stream, "_chunks", chunks)

    response = llm.stream([])
    assert list(response) == []

    assert response.tool_calls == [
        {
            "id": "call-a",
            "name": "first",
            "arguments": '{"question":"Hello"}',
        },
        {
            "id": "call-b",
            "name": "second",
            "arguments": '{"limit":3}',
        },
    ]

    assert response.metrics["tokens_in"] == 20
    assert response.metrics["tokens_out"] == 5
    assert response.metrics["ttft_ms"] is None

    lines = (
        tmp_path / "usage.jsonl"
    ).read_text().splitlines()

    assert len(lines) == 1


def test_streamed_tool_uses_existing_gate(
    monkeypatch, tmp_path
):
    log = tmp_path / "tools.jsonl"

    monkeypatch.setenv(
        "BLUE_WHALE_TOOL_LOG", str(log)
    )

    seen = []

    class FakeStream:
        def __init__(self, calls, text):
            self.tool_calls = calls
            self.text = text
            self.reasoning_details = []
            self.metrics = {
                "usage_available": True,
                "tokens_in": 10,
                "tokens_out": 5,
                "cost_usd": 0,
                "cost_source": "offline",
            }

        def __iter__(self):
            if self.text:
                yield self.text

    def model(messages, schemas):
        seen.append(messages[-1].copy())

        if len(seen) == 1:
            return FakeStream([
                {
                    "id": "invalid-call",
                    "name": "search_trusted_sources",
                    "arguments": json.dumps({
                        "question": "Find trusted evidence",
                        "limit": 100,
                    }),
                }
            ], "")

        assert messages[-1]["role"] == "tool"
        assert "invalid arguments" in messages[-1]["content"]

        return FakeStream([], "Invalid request handled.")

    events = list(chat_turn(
        "Find project evidence",
        llm=model,
    ))

    tool_event = next(
        value for kind, value in events
        if kind == "tool"
    )

    assert not tool_event["ok"]

    assert events[-1][0] == "done"
    assert events[-1][1]["status"] == "answered"

    entries = log.read_text().splitlines()

    assert len(entries) == 1
    assert not json.loads(entries[0])["ok"]


def test_http_stream_returns_sse(monkeypatch, tmp_path):
    monkeypatch.setattr(llm, "OFFLINE", True)

    monkeypatch.setattr(
        llm, "LOG_PATH", tmp_path / "usage.jsonl"
    )

    client = TestClient(app)

    response = client.post(
        "/chat",
        json={"question": "Hello Blue Whale"},
    )

    assert response.status_code == 200

    assert response.headers[
        "content-type"
    ].startswith("text/event-stream")

    assert "event: token" in response.text
    assert "event: done" in response.text
    assert "Offline simulation" in response.text


def test_http_request_rejects_injected_identity():
    client = TestClient(app)

    response = client.post(
        "/chat",
        json={
            "question": "Hello Blue Whale",
            "caller_id": "forged-identity",
        },
    )

    assert response.status_code == 422
    assert "forged-identity" not in response.text


def test_act_endpoint_uses_request_caller(monkeypatch):
    import src.app as application

    received = {}

    def fake_act(question, caller=None):
        received["question"] = question
        received["caller"] = caller

        return NS(to_dict=lambda: {
            "status": "answered",
            "text": "Test answer",
            "calls": [],
        })

    monkeypatch.setattr(application, "act", fake_act)

    client = TestClient(app)

    response = client.post(
        "/act",
        json={"question": "Find evidence"},
        headers={"X-Caller-Id": "test-caller"},
    )

    assert response.status_code == 200
    assert received["caller"] == "test-caller"
    assert received["question"] == "Find evidence"
