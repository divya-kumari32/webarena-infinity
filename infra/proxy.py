#!/usr/bin/env python3
"""Anthropic ↔ OpenAI translation proxy for Claude Code CLI.

Receives Anthropic Messages API requests from Claude Code CLI,
translates them to OpenAI Chat Completions format, forwards to an
OpenAI-compatible endpoint, and translates the response back.

Usage:
    python infra/proxy.py --port 4000

Environment variables:
    PROXY_TARGET_URL   — OpenAI-compatible base URL (e.g. https://litellm.example.com)
    PROXY_TARGET_KEY   — API key for the target endpoint
    PROXY_TARGET_MODEL — Model name to send (e.g. azure/gpt-oss-120b)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import uuid

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import uvicorn

logging.basicConfig(level=logging.INFO, format="%(asctime)s [proxy] %(message)s")
log = logging.getLogger("proxy")

app = FastAPI()

TARGET_URL = os.environ.get("PROXY_TARGET_URL", "https://ete-litellm.ai-models.vpc.res.ibm.com")
TARGET_KEY = os.environ.get("PROXY_TARGET_KEY", "sk-RWMz_-kGpO4Q-dbfiIE1IQ")
TARGET_MODEL = os.environ.get("PROXY_TARGET_MODEL", "azure/gpt-oss-120b")

# ---------------------------------------------------------------------------
# Request translation: Anthropic → OpenAI
# ---------------------------------------------------------------------------


def convert_tools(anthropic_tools: list[dict]) -> list[dict]:
    openai_tools = []
    for tool in anthropic_tools:
        openai_tools.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
            },
        })
    return openai_tools


def convert_tool_choice(anthropic_choice: dict | str | None) -> dict | str | None:
    if anthropic_choice is None:
        return None
    if isinstance(anthropic_choice, str):
        return anthropic_choice
    tc_type = anthropic_choice.get("type", "auto")
    if tc_type == "tool":
        return {"type": "function", "function": {"name": anthropic_choice["name"]}}
    if tc_type == "any":
        return "required"
    return tc_type  # "auto", "none"


def convert_messages(anthropic_messages: list[dict], system: str | list | None = None) -> list[dict]:
    openai_messages = []

    # System prompt
    if system:
        if isinstance(system, list):
            text_parts = [b["text"] for b in system if b.get("type") == "text"]
            system_text = "\n".join(text_parts)
        else:
            system_text = system
        if system_text:
            openai_messages.append({"role": "system", "content": system_text})

    for msg in anthropic_messages:
        role = msg.get("role", "user")
        content = msg.get("content")

        # Simple string content
        if isinstance(content, str):
            openai_messages.append({"role": role, "content": content})
            continue

        # Content is a list of blocks
        if isinstance(content, list):
            if role == "assistant":
                openai_messages.extend(_convert_assistant_blocks(content))
            elif role == "user":
                openai_messages.extend(_convert_user_blocks(content))
            else:
                # Fallback: concatenate text blocks
                text = " ".join(
                    b.get("text", "") for b in content if b.get("type") == "text"
                )
                openai_messages.append({"role": role, "content": text or ""})

    return openai_messages


def _convert_assistant_blocks(blocks: list[dict]) -> list[dict]:
    text_parts = []
    tool_calls = []

    for block in blocks:
        if block.get("type") == "text":
            text_parts.append(block.get("text", ""))
        elif block.get("type") == "tool_use":
            tool_calls.append({
                "id": block["id"],
                "type": "function",
                "function": {
                    "name": block["name"],
                    "arguments": json.dumps(block.get("input", {})),
                },
            })

    msg: dict = {"role": "assistant", "content": "\n".join(text_parts) if text_parts else None}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return [msg]


def _convert_user_blocks(blocks: list[dict]) -> list[dict]:
    messages = []
    text_parts = []

    for block in blocks:
        if block.get("type") == "tool_result":
            # Tool results become separate role:"tool" messages
            result_content = block.get("content", "")
            if isinstance(result_content, list):
                result_content = " ".join(
                    b.get("text", "") for b in result_content if b.get("type") == "text"
                )
            messages.append({
                "role": "tool",
                "tool_call_id": block["tool_use_id"],
                "content": str(result_content),
            })
        elif block.get("type") == "text":
            text_parts.append(block.get("text", ""))
        elif block.get("type") == "image":
            # Pass image blocks as text description
            text_parts.append("[image]")

    if text_parts:
        messages.insert(0, {"role": "user", "content": "\n".join(text_parts)})

    return messages


def anthropic_to_openai(request: dict) -> dict:
    openai_req: dict = {
        "model": TARGET_MODEL,
        "messages": convert_messages(
            request.get("messages", []),
            system=request.get("system"),
        ),
    }

    if "tools" in request:
        openai_req["tools"] = convert_tools(request["tools"])

    tc = convert_tool_choice(request.get("tool_choice"))
    if tc is not None:
        openai_req["tool_choice"] = tc

    if "max_tokens" in request:
        openai_req["max_tokens"] = request["max_tokens"]
    if "temperature" in request:
        openai_req["temperature"] = request["temperature"]
    if "top_p" in request:
        openai_req["top_p"] = request["top_p"]
    if "stop_sequences" in request:
        openai_req["stop"] = request["stop_sequences"]

    if request.get("stream", False):
        openai_req["stream"] = True

    return openai_req


# ---------------------------------------------------------------------------
# Response translation: OpenAI → Anthropic
# ---------------------------------------------------------------------------

STOP_REASON_MAP = {
    "stop": "end_turn",
    "tool_calls": "tool_use",
    "length": "max_tokens",
    "content_filter": "end_turn",
}


def openai_to_anthropic(response: dict, request_model: str) -> dict:
    choice = response.get("choices", [{}])[0]
    message = choice.get("message", {})
    finish_reason = choice.get("finish_reason", "stop")

    content_blocks = []

    # Text content
    text = message.get("content")
    if text:
        content_blocks.append({"type": "text", "text": text})

    # Tool calls
    for tc in message.get("tool_calls", []):
        func = tc.get("function", {})
        try:
            input_obj = json.loads(func.get("arguments", "{}"))
        except json.JSONDecodeError:
            input_obj = {}
        content_blocks.append({
            "type": "tool_use",
            "id": tc.get("id", f"toolu_{uuid.uuid4().hex[:12]}"),
            "name": func.get("name", ""),
            "input": input_obj,
        })

    if not content_blocks:
        content_blocks.append({"type": "text", "text": ""})

    usage = response.get("usage", {})

    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "content": content_blocks,
        "model": request_model,
        "stop_reason": STOP_REASON_MAP.get(finish_reason, "end_turn"),
        "stop_sequence": None,
        "usage": {
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        },
    }


# ---------------------------------------------------------------------------
# Streaming translation: OpenAI chunks → Anthropic SSE events
# ---------------------------------------------------------------------------


def _sse_event(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def stream_openai_to_anthropic(openai_response: httpx.Response, request_model: str):
    msg_id = f"msg_{uuid.uuid4().hex[:24]}"

    # message_start
    yield _sse_event("message_start", {
        "type": "message_start",
        "message": {
            "id": msg_id,
            "type": "message",
            "role": "assistant",
            "content": [],
            "model": request_model,
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        },
    })

    content_index = 0
    text_block_started = False
    tool_blocks: dict[int, dict] = {}  # index → {id, name, args_buffer}
    tool_block_indices: dict[int, int] = {}  # openai tool index → anthropic content index

    async for line in openai_response.aiter_lines():
        if not line.startswith("data: "):
            continue
        data_str = line[6:].strip()
        if data_str == "[DONE]":
            break

        try:
            chunk = json.loads(data_str)
        except json.JSONDecodeError:
            continue

        choice = (chunk.get("choices") or [{}])[0]
        delta = choice.get("delta", {})
        finish_reason = choice.get("finish_reason")

        # Text content
        text_delta = delta.get("content")
        if text_delta:
            if not text_block_started:
                yield _sse_event("content_block_start", {
                    "type": "content_block_start",
                    "index": content_index,
                    "content_block": {"type": "text", "text": ""},
                })
                text_block_started = True

            yield _sse_event("content_block_delta", {
                "type": "content_block_delta",
                "index": content_index,
                "delta": {"type": "text_delta", "text": text_delta},
            })

        # Tool calls
        for tc in delta.get("tool_calls", []):
            tc_index = tc.get("index", 0)

            if tc_index not in tool_blocks:
                # Close text block if open
                if text_block_started:
                    yield _sse_event("content_block_stop", {
                        "type": "content_block_stop",
                        "index": content_index,
                    })
                    content_index += 1
                    text_block_started = False

                tool_id = tc.get("id", f"toolu_{uuid.uuid4().hex[:12]}")
                tool_name = tc.get("function", {}).get("name", "")
                tool_blocks[tc_index] = {"id": tool_id, "name": tool_name, "args": ""}
                tool_block_indices[tc_index] = content_index

                yield _sse_event("content_block_start", {
                    "type": "content_block_start",
                    "index": content_index,
                    "content_block": {
                        "type": "tool_use",
                        "id": tool_id,
                        "name": tool_name,
                        "input": {},
                    },
                })
                content_index += 1

            # Argument chunks
            args_delta = tc.get("function", {}).get("arguments", "")
            if args_delta:
                tool_blocks[tc_index]["args"] += args_delta
                yield _sse_event("content_block_delta", {
                    "type": "content_block_delta",
                    "index": tool_block_indices[tc_index],
                    "delta": {"type": "input_json_delta", "partial_json": args_delta},
                })

        # Finish
        if finish_reason:
            # Close any open text block
            if text_block_started:
                yield _sse_event("content_block_stop", {
                    "type": "content_block_stop",
                    "index": content_index if not tool_blocks else 0,
                })

            # Close tool blocks
            for tc_idx, tb in tool_blocks.items():
                yield _sse_event("content_block_stop", {
                    "type": "content_block_stop",
                    "index": tool_block_indices[tc_idx],
                })

            stop_reason = STOP_REASON_MAP.get(finish_reason, "end_turn")

            # Get usage from chunk if available
            usage = chunk.get("usage", {})
            yield _sse_event("message_delta", {
                "type": "message_delta",
                "delta": {"stop_reason": stop_reason, "stop_sequence": None},
                "usage": {"output_tokens": usage.get("completion_tokens", 0)},
            })

            yield _sse_event("message_stop", {"type": "message_stop"})


# ---------------------------------------------------------------------------
# FastAPI endpoints
# ---------------------------------------------------------------------------


@app.head("/")
@app.get("/")
async def health():
    return Response(status_code=200)


@app.api_route("/v1/messages", methods=["POST"])
async def messages(request: Request):
    body = await request.json()
    request_model = body.get("model", TARGET_MODEL)
    is_stream = body.get("stream", False)

    openai_req = anthropic_to_openai(body)

    log.info("Forwarding to %s model=%s stream=%s tools=%d",
             TARGET_URL, TARGET_MODEL, is_stream,
             len(openai_req.get("tools", [])))

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TARGET_KEY}",
    }

    if is_stream:
        async with httpx.AsyncClient(timeout=600.0) as client:
            openai_resp = await client.send(
                client.build_request(
                    "POST",
                    f"{TARGET_URL}/v1/chat/completions",
                    json=openai_req,
                    headers=headers,
                ),
                stream=True,
            )
            if openai_resp.status_code != 200:
                error_body = await openai_resp.aread()
                log.error("Target returned %d: %s", openai_resp.status_code, error_body[:500])
                return Response(
                    content=error_body,
                    status_code=openai_resp.status_code,
                    media_type="application/json",
                )

            return StreamingResponse(
                stream_openai_to_anthropic(openai_resp, request_model),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache"},
            )
    else:
        async with httpx.AsyncClient(timeout=600.0) as client:
            openai_resp = await client.post(
                f"{TARGET_URL}/v1/chat/completions",
                json=openai_req,
                headers=headers,
            )

        if openai_resp.status_code != 200:
            log.error("Target returned %d: %s", openai_resp.status_code, openai_resp.text[:500])
            return Response(
                content=openai_resp.content,
                status_code=openai_resp.status_code,
                media_type="application/json",
            )

        anthropic_resp = openai_to_anthropic(openai_resp.json(), request_model)
        return Response(
            content=json.dumps(anthropic_resp),
            media_type="application/json",
        )


# Also handle the path with query params that Claude Code uses
@app.api_route("/v1/messages/{path:path}", methods=["POST"])
async def messages_with_path(request: Request, path: str):
    return await messages(request)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anthropic↔OpenAI translation proxy")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PROXY_PORT", "4000")))
    parser.add_argument("--host", default="0.0.0.0")
    args = parser.parse_args()

    log.info("Starting proxy on %s:%d", args.host, args.port)
    log.info("  Target: %s", TARGET_URL)
    log.info("  Model:  %s", TARGET_MODEL)

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
