"""Bounded streaming conversation using existing tool safety gates."""

import json
import time

from .act import (
    MAX_ROUNDS,
    SYSTEM_PROMPT,
    as_assistant,
    call_tool,
)
from .llm import stream, ms_since
from .tools import tools_for


def chat_turn(question, caller=None, llm=None):
    llm = llm or stream

    allowed = {
        name: tool
        for name, tool in tools_for(caller).items()
        if not tool.writes
    }

    schemas = [
        tool.schema() for tool in allowed.values()
    ]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    started = time.perf_counter()
    first_token = None
    metrics = []
    calls = 0
    status = "stopped"
    error = None

    try:
        for round_number in range(MAX_ROUNDS):
            current = llm(messages, schemas)

            for piece in current:
                if first_token is None:
                    first_token = ms_since(started)

                yield "token", {"text": piece}

            metrics.append(current.metrics)

            if not current.tool_calls:
                if not current.text.strip():
                    raise RuntimeError("Empty model response.")

                status = "answered"
                break

            if round_number == MAX_ROUNDS - 1:
                break

            messages.append(as_assistant({
                "content": current.text or None,
                "tool_calls": current.tool_calls,
                "reasoning_details": current.reasoning_details,
            }))

            for request in current.tool_calls:
                outcome = call_tool(
                    request,
                    allowed,
                    caller,
                )

                calls += 1

                yield "tool", {
                    "tool": outcome["tool"],
                    "ok": outcome["ok"],
                    "error": outcome["error"],
                }

                observation = (
                    outcome["result"]
                    if outcome["ok"]
                    else {"error": outcome["error"]}
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": request["id"],
                    "content": json.dumps(observation),
                })

    except Exception:
        status = "failed"
        error = (
            "Streaming failed. Ask the operator "
            "to check the service and retry."
        )

    usage_complete = (
        status != "failed"
        and bool(metrics)
        and all(m["usage_available"] for m in metrics)
    )

    costs_complete = (
        status != "failed"
        and bool(metrics)
        and all(m["cost_usd"] is not None for m in metrics)
    )

    yield "done", {
        "status": status,
        "error": error,
        "ttft_ms": first_token,
        "latency_ms": ms_since(started),
        "calls": calls,
        "rounds": len(metrics),
        "usage_complete": usage_complete,
        "tokens_in": (
            sum(m["tokens_in"] for m in metrics)
            if usage_complete else None
        ),
        "tokens_out": (
            sum(m["tokens_out"] for m in metrics)
            if usage_complete else None
        ),
        "cost_usd": (
            round(sum(m["cost_usd"] for m in metrics), 6)
            if costs_complete else None
        ),
        "cost_sources": sorted({
            m["cost_source"] for m in metrics
        }),
    }
