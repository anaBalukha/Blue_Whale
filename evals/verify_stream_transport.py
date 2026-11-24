import json
import socket
import tempfile
import threading
import time

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import httpx
import uvicorn

from src import llm
from src.app import app


def verify():
    release = threading.Event()

    original_chunks = llm.Stream._chunks
    original_log = llm.LOG_PATH
    original_offline = llm.OFFLINE

    def chunks(self):
        yield SimpleNamespace(
            content="First token",
            tool_calls=[],
        ), None, {}

        if not release.wait(timeout=15):
            raise RuntimeError("First token was not delivered")

        yield SimpleNamespace(
            content=" Second token",
            tool_calls=[],
        ), None, {}

        self.finish_reason = "stop"

    llm.Stream._chunks = chunks
    llm.OFFLINE = True

    try:
        with tempfile.TemporaryDirectory() as directory:
            llm.LOG_PATH = Path(directory) / "usage.jsonl"

            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                sock.listen(128)

                port = sock.getsockname()[1]

                config = uvicorn.Config(
                    app,
                    log_level="error",
                    lifespan="off",
                )

                server = uvicorn.Server(config)

                thread = threading.Thread(
                    target=server.run,
                    kwargs={"sockets": [sock]},
                    daemon=True,
                )

                thread.start()

                events = []
                first_before_completion = False

                try:
                    deadline = time.monotonic() + 10

                    while not server.started:
                        if time.monotonic() > deadline:
                            raise RuntimeError("Server startup timeout")
                        time.sleep(0.05)

                    with httpx.stream(
                        "POST",
                        f"http://127.0.0.1:{port}/chat",
                        json={"question": "Verify streaming"},
                        timeout=20,
                        trust_env=False,
                    ) as response:
                        assert response.status_code == 200

                        assert response.headers[
                            "content-type"
                        ].startswith("text/event-stream")

                        kind = None

                        for line in response.iter_lines():
                            if line.startswith("event: "):
                                kind = line[7:]

                            elif line.startswith("data: "):
                                payload = json.loads(line[6:])
                                events.append((kind, payload))

                                if kind == "token" and len(events) == 1:
                                    assert payload["text"] == "First token"
                                    assert not release.is_set()
                                    assert not llm.LOG_PATH.exists()

                                    first_before_completion = True

                                    print("PASS: First token received before completion")

                                    release.set()

                    assert first_before_completion

                    assert [k for k, _ in events] == [
                        "token", "token", "done"
                    ]

                    assert events[-1][1]["status"] == "answered"

                    records = [
                        json.loads(line)
                        for line in llm.LOG_PATH.read_text().splitlines()
                    ]

                    assert len(records) == 1
                    assert records[0]["completed"]
                    assert records[0]["ttft_ms"] >= 0
                    assert records[0]["mode"] == "offline"

                    result = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "mode": "offline_provider_simulation",
                        "transport": "real_loopback_http",
                        "passed": True,
                        "first_token_before_completion": True,
                        "event_order": [k for k, _ in events],
                        "combined_text": "".join(
                            p["text"] for k, p in events
                            if k == "token"
                        ),
                        "usage_log_entries": len(records),
                        "usage": records[0],
                        "summary": events[-1][1],
                    }

                finally:
                    release.set()
                    server.should_exit = True
                    thread.join(timeout=15)

                assert not thread.is_alive()

        output = Path(
            "evals/results/stream-transport-offline.json"
        )

        output.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )

        print("PASS: SSE event order")
        print("PASS: Exactly one usage log")
        print("PASS: Local server shutdown")
        print("Result saved:", output)

    finally:
        llm.Stream._chunks = original_chunks
        llm.LOG_PATH = original_log
        llm.OFFLINE = original_offline


if __name__ == "__main__":
    verify()
