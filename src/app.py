"""Local development HTTP interface for Blue Whale."""

import json

from fastapi import FastAPI, Header, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from .act import act
from .chat import chat_turn


app = FastAPI(title="Blue Whale")


class Ask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(
        min_length=3,
        max_length=500,
    )


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "INVALID_INPUT",
                "message": "Provide a valid question.",
            }
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/act")
def act_endpoint(
    body: Ask,
    x_caller_id: str | None = Header(
        default=None,
        max_length=80,
    ),
):
    try:
        return act(
            body.question,
            caller=x_caller_id,
        ).to_dict()

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Tool conversation unavailable. Check the service.",
        ) from None


def sse(events):
    for kind, payload in events:
        data = json.dumps(
            payload,
            ensure_ascii=False,
        )

        yield f"event: {kind}\ndata: {data}\n\n"


@app.post("/chat")
def chat_endpoint(
    body: Ask,
    x_caller_id: str | None = Header(
        default=None,
        max_length=80,
    ),
):
    return StreamingResponse(
        sse(chat_turn(
            body.question,
            caller=x_caller_id,
        )),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
