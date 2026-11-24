# Blue Whale - Streaming Interface

## Scope

This slice introduces local HTTP transport and streamed model
responses. Blue Whale remains terminal-first.

Persistent conversation state is not implemented by this slice.
Its design and implementation depend on the separate state contract.

## Endpoints

- POST /act: existing bounded, validated tool conversation.
- POST /chat: streamed tool conversation using SSE.

Both accept a JSON object containing a question of 3-500 characters.
Unexpected request fields are rejected.

An optional X-Caller-Id header represents application-side caller
context for local development. It is not real authentication.
Caller identity is never a tool argument.

## Streaming

- Use the existing OpenRouter client.
- Emit text as it arrives.
- Collect tool-call fragments by their index.
- Run tools only through call_tool().
- Offer only read-only tools in the streaming conversation.
- Preserve the existing three-round budget.
- Keep provider reasoning metadata inside the model conversation.
- Write one usage entry per model stream.
- Measure milliseconds to the first textual token.
- Read usage from the provider's streaming response.
- Do not report missing usage or unknown cost as measured zero.

## SSE events

- token: text fragment.
- tool: sanitized execution outcome.
- done: completion status, token totals, latency and cost information.

Failures return a safe status rather than exposing exception details.

## Safety

The development server binds to localhost only.
No conversation is persisted by this slice.
There is no consequential action or confirmation endpoint yet.

Offline output is explicitly a simulation, not a real model answer.

## Dependencies

FastAPI provides the HTTP interface.
Uvicorn serves the local application.
HTTPX supports offline endpoint tests.

The state contract, memory controls, authentication and confirmation
workflow remain separate integration tasks.
