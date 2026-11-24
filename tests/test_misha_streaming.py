import json
from types import SimpleNamespace as NS

import pytest

from src import llm
from src import chat
from src.act import MAX_ROUNDS


def delta(text=None, calls=None, reasoning=None):
    return NS(
        content=text,
        tool_calls=calls or [],
        model_extra={
            "reasoning_details": reasoning
        } if reasoning else {},
    )


def chunk(d=None, finish=None, usage=None):
    return NS(
        model="test/provider-model",
        choices=[
            NS(delta=d, finish_reason=finish)
        ] if d is not None or finish else [],
        usage=usage,
    )


def request(name, arguments, identifier="call-1"):
    return NS(
        index=0,
        id=identifier,
        function=NS(
            name=name,
            arguments=arguments,
        ),
    )


def usage():
    return NS(
        prompt_tokens=100,
        completion_tokens=25,
        model_extra={"cost": 0.001},
    )


class ProviderStream:
    def __init__(self, chunks):
        self.chunks = chunks
        self.closed = False

    def __iter__(self):
        for item in self.chunks:
            if isinstance(item, Exception):
                raise item
            yield item

    def close(self):
        self.closed = True


@pytest.fixture
def provider(monkeypatch, tmp_path):
    responses = []
    requests = []

    def create(**kwargs):
        requests.append(kwargs)
        return responses.pop(0)

    monkeypatch.setattr(llm, "OFFLINE", False)
    monkeypatch.setattr(
        llm, "LOG_PATH", tmp_path / "usage.jsonl"
    )

    monkeypatch.setattr(
        llm,
        "client",
        NS(chat=NS(completions=NS(create=create))),
    )

    monkeypatch.setenv(
        "BLUE_WHALE_TOOL_LOG",
        str(tmp_path / "tools.jsonl"),
    )

    return responses, requests


def read_logs(path):
    return [
        json.loads(line)
        for line in path.read_text().splitlines()
    ]


def test_incremental_delivery_and_final_usage(provider):
    responses, requests = provider

    wire = ProviderStream([
        chunk(delta("First ")),
        chunk(delta("second")),
        chunk(delta(), finish="stop"),
        chunk(usage=usage()),
    ])

    responses.append(wire)

    response = llm.stream([
        {"role": "user", "content": "Test streaming"}
    ])

    iterator = iter(response)

    assert next(iterator) == "First "
    assert not llm.LOG_PATH.exists()
    assert not wire.closed

    assert list(iterator) == ["second"]
    assert response.text == "First second"

    assert wire.closed
    assert requests[0]["stream"] is True
    assert requests[0]["stream_options"]["include_usage"]

    records = read_logs(llm.LOG_PATH)

    assert len(records) == 1
    assert records[0]["tokens_in"] == 100
    assert records[0]["tokens_out"] == 25
    assert records[0]["cost_usd"] == 0.001
    assert records[0]["cost_source"] == "provider"
    assert records[0]["ttft_ms"] >= 0
    assert records[0]["completed"]


def test_interrupted_stream_logs_failure(provider):
    responses, _ = provider

    wire = ProviderStream([
        chunk(delta("Partial answer")),
        RuntimeError("private-provider-error"),
    ])

    responses.append(wire)

    events = list(chat.chat_turn("Test interruption"))

    assert events[0] == (
        "token", {"text": "Partial answer"}
    )

    assert events[-1][0] == "done"
    assert events[-1][1]["status"] == "failed"
    assert "private-provider-error" not in str(events)

    records = read_logs(llm.LOG_PATH)

    assert len(records) == 1
    assert not records[0]["completed"]
    assert records[0]["tokens_in"] is None
    assert records[0]["cost_usd"] is None
    assert wire.closed


def test_incomplete_tool_stream_never_executes(
    provider, tmp_path
):
    responses, _ = provider

    responses.append(ProviderStream([
        chunk(delta(calls=[
            request(
                "check_decision_drift",
                '{"state":',
            )
        ])),
    ]))

    events = list(chat.chat_turn("Compare decisions"))

    assert events[-1][1]["status"] == "failed"
    assert not any(k == "tool" for k, _ in events)
    assert not (tmp_path / "tools.jsonl").exists()

    records = read_logs(llm.LOG_PATH)

    assert len(records) == 1
    assert not records[0]["completed"]


def test_tool_only_stream_and_reasoning_metadata(provider):
    responses, requests = provider

    details = [
        {
            "type": "reasoning.encrypted",
            "data": "synthetic-metadata",
        }
    ]

    arguments = json.dumps({
        "state": {"database": "PostgreSQL"},
        "candidate": {"database": "MongoDB"},
    })

    responses.extend([
        ProviderStream([
            chunk(delta(
                calls=[
                    request(
                        "check_decision_drift",
                        arguments,
                    )
                ],
                reasoning=details,
            ), finish="tool_calls"),
            chunk(usage=usage()),
        ]),
        ProviderStream([
            chunk(delta("Drift detected.")),
            chunk(delta(), finish="stop"),
            chunk(usage=usage()),
        ]),
    ])

    events = list(chat.chat_turn("Compare decisions"))

    assert events[0][0] == "tool"
    assert events[0][1]["ok"]

    assert events[-1][1]["status"] == "answered"
    assert events[-1][1]["calls"] == 1
    assert events[-1][1]["rounds"] == 2
    assert events[-1][1]["tokens_in"] == 200
    assert events[-1][1]["tokens_out"] == 50

    messages = requests[1]["messages"]

    assistant = next(
        m for m in messages
        if m["role"] == "assistant"
    )

    assert assistant["reasoning_details"] == details

    observation = next(
        m for m in messages
        if m["role"] == "tool"
    )

    assert json.loads(observation["content"])[
        "status"
    ] == "drift"

    assert "synthetic-metadata" not in str(events)

    records = read_logs(llm.LOG_PATH)

    assert len(records) == 2
    assert records[0]["ttft_ms"] is None
    assert records[1]["ttft_ms"] >= 0


def test_unknown_cost_is_not_reported_as_zero(provider):
    responses, _ = provider

    responses.append(ProviderStream([
        chunk(delta("Answer")),
        chunk(delta(), finish="stop"),
        chunk(usage=NS(
            prompt_tokens=30,
            completion_tokens=10,
        )),
    ]))

    response = llm.stream([])
    list(response)

    assert response.metrics["usage_available"]
    assert response.metrics["cost_usd"] is None
    assert response.metrics["cost_source"] == "unavailable"


def test_write_tool_is_never_offered_or_executed(
    provider, monkeypatch
):
    responses, requests = provider

    executed = []

    write_tool = NS(
        writes=True,
        run=lambda args: executed.append(args),
    )

    monkeypatch.setattr(
        chat,
        "tools_for",
        lambda caller: {"write_checkpoint": write_tool},
    )

    responses.extend([
        ProviderStream([
            chunk(delta(calls=[
                request("write_checkpoint", "{}")
            ]), finish="tool_calls"),
            chunk(usage=usage()),
        ]),
        ProviderStream([
            chunk(delta("Action refused.")),
            chunk(delta(), finish="stop"),
            chunk(usage=usage()),
        ]),
    ])

    events = list(chat.chat_turn(
        "Attempt write",
        caller="test-caller",
    ))

    assert not executed
    assert not requests[0].get("tools")

    tool = next(
        value for kind, value in events
        if kind == "tool"
    )

    assert not tool["ok"]
    assert tool["tool"] == "unknown_tool"


def test_model_cannot_exceed_round_budget(provider):
    responses, requests = provider

    for i in range(MAX_ROUNDS):
        responses.append(ProviderStream([
            chunk(delta(calls=[
                request(
                    "unregistered_tool",
                    "{}",
                    identifier=f"call-{i}",
                )
            ]), finish="tool_calls"),
            chunk(usage=usage()),
        ]))

    events = list(chat.chat_turn("Keep requesting tools"))

    assert len(requests) == MAX_ROUNDS
    assert events[-1][1]["status"] == "stopped"

    assert events[-1][1]["rounds"] == MAX_ROUNDS
    assert events[-1][1]["calls"] == MAX_ROUNDS - 1

    assert len(read_logs(llm.LOG_PATH)) == MAX_ROUNDS


def test_cancelled_stream_closes_provider_and_logs_once(
    provider
):
    responses, _ = provider

    wire = ProviderStream([
        chunk(delta("First token")),
        chunk(delta("Second token")),
        chunk(delta(), finish="stop"),
        chunk(usage=usage()),
    ])

    responses.append(wire)

    response = llm.stream([])
    iterator = iter(response)

    assert next(iterator) == "First token"

    iterator.close()

    assert wire.closed

    records = read_logs(llm.LOG_PATH)

    assert len(records) == 1
    assert not records[0]["completed"]
