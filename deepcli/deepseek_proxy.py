#!/usr/bin/env python3
"""
OpenAI-compatible API proxy for DeepSeek internal API.
Uses deepcli/core.py under the hood.

Start:   python deepseek_proxy.py
Test:    curl http://localhost:8800/v1/models
         curl -X POST http://localhost:8800/v1/chat/completions \
              -H 'Content-Type: application/json' \
              -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}],"stream":true}'
"""

import sys, os, json, time, uuid, base64, queue, threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Generator

# Make sure deepcli is importable (adjust path to your setup)
DEEPCLI_DIR = Path.home() / "deepcli"
sys.path.insert(0, str(DEEPCLI_DIR))
sys.path.insert(0, str(DEEPCLI_DIR / "deepcli"))  # in case core.py is inside deepcli/deepcli

from deepcli.core import (
    get_token, create_session, get_history, _cache_path,
    get_session, get_pow_challenge, solve_pow, BASE_URL, CONFIG_DIR
)

# Rich is used by core.py but we'll only use it for server logs (optional)
try:
    from rich.console import Console
    console = Console()
except ImportError:
    import logging
    console = logging.getLogger("rich")

# ────────────────────────────────
# Session store (maps external conversation_id → internal deepseek session)
# ────────────────────────────────
sessions: Dict[str, Dict[str, Any]] = {}          # conv_id → {session_id, last_user_msg_id, last_assistant_msg_id}
lock = threading.Lock()

def get_or_create_conv(conv_id: str) -> str:
    """Return the deepseek session_id for a given conversation id, creating one if needed."""
    with lock:
        if conv_id in sessions:
            return sessions[conv_id]["session_id"]
        token = get_token()
        sid = create_session(token)
        sessions[conv_id] = {
            "session_id": sid,
            "last_user_message_id": None,
            "last_assistant_message_id": None,
        }
        return sid

def update_parent_ids(conv_id: str):
    """After a response, fetch history and update the last message IDs."""
    token = get_token()
    with lock:
        if conv_id not in sessions:
            return
        sid = sessions[conv_id]["session_id"]
    try:
        msgs = get_history(token, sid, force_refresh=True)
        last_user = None
        last_assistant = None
        for m in msgs:
            role = m.get("role", "").upper()
            if role == "USER":
                last_user = m["message_id"]
            elif role == "ASSISTANT":
                last_assistant = m["message_id"]
        with lock:
            if conv_id in sessions:
                sessions[conv_id]["last_user_message_id"] = last_user
                sessions[conv_id]["last_assistant_message_id"] = last_assistant
    except Exception:
        pass

# ────────────────────────────────
# Streaming chunk generator (reuses core.py internals)
# ────────────────────────────────
def stream_chat_chunks(token: str, prompt: str, session_id: str,
                       parent_message_id: Optional[str] = None,
                       thinking: bool = False, search: bool = False,
                       file_ids: Optional[List[str]] = None,
                       auto_retry: bool = True) -> Generator[str, None, None]:
    """
    Synchronous generator that yields content chunks from the DeepSeek stream.
    Adapted from deepcli.core.stream_completion(), but yields instead of printing.
    """
    import requests as http_requests

    challenge = get_pow_challenge(token, "/api/v0/chat/completion")
    pow_header = solve_pow(challenge)

    payload = {
        "chat_session_id": session_id,
        "parent_message_id": int(parent_message_id) if parent_message_id else None,
        "prompt": prompt,
        "ref_file_ids": file_ids or [],
        "thinking_enabled": thinking,
        "search_enabled": search,
        "stream": True
    }

    base_sess = get_session(token)
    headers = base_sess.headers.copy()
    headers["X-Ds-Pow-Response"] = pow_header
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "text/event-stream"

    url = f"{BASE_URL}/api/v0/chat/completion"
    retries = 0
    max_retries = 8
    base_delay = 2
    while retries < max_retries:
        try:
            # Use plain requests for reliable streaming iter_lines
            resp = http_requests.post(url, json=payload, headers=headers, stream=True)
            if resp.status_code == 403:
                retries += 1
                delay = base_delay * (2 ** retries) + random.uniform(0, base_delay)
                time.sleep(min(delay, 30))
                continue
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data:"):
                    continue
                try:
                    data = json.loads(line[5:].strip())
                except json.JSONDecodeError:
                    continue
                chunk = data.get("v") or data.get("content")
                if chunk and isinstance(chunk, str) and chunk != "FINISHED":
                    yield chunk
            return   # success
        except Exception as e:
            retries += 1
            delay = min(10 * retries, 60)
            time.sleep(delay)
    raise RuntimeError("DeepSeek stream failed after multiple retries")

# ────────────────────────────────
# FastAPI application
# ────────────────────────────────
try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import StreamingResponse, JSONResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("Missing dependencies. Install them with:")
    print("  pip install fastapi uvicorn pydantic")
    sys.exit(1)

app = FastAPI(title="DeepSeek Local API")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "deepseek-chat"
    messages: List[Message]
    stream: bool = False
    temperature: Optional[float] = None

# ────────────────────────────────
# SSE adapter: turn sync generator into async Server-Sent Events
# ────────────────────────────────
async def sse_adapter(sync_gen, conv_id: str):
    """Wrap a synchronous chunk generator into async SSE chunks."""
    import asyncio, random
    loop = asyncio.get_running_loop()
    try:
        # Run the sync generator in a thread to avoid blocking the event loop
        def run_generator():
            return list(sync_gen)
        chunks = await loop.run_in_executor(None, run_generator)
    except Exception as e:
        yield f'data: {{"error": "{str(e)}"}}\n\n'
        yield 'data: [DONE]\n\n'
        return

    # Send each chunk as a delta, then finish
    for i, chunk in enumerate(chunks):
        data = json.dumps({
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "deepseek-chat",
            "choices": [{
                "index": 0,
                "delta": {"content": chunk} if i < len(chunks) - 1 else {},
                "finish_reason": "stop" if i == len(chunks) - 1 else None
            }]
        })
        yield f"data: {data}\n\n"
        await asyncio.sleep(0.01)  # tiny delay for visual effect

    yield "data: [DONE]\n\n"

@app.get("/v1/models")
async def list_models():
    return JSONResponse({
        "object": "list",
        "data": [
            {"id": "deepseek-chat", "object": "model", "created": 1, "owned_by": "deepseek"},
            {"id": "deepseek-reasoner", "object": "model", "created": 1, "owned_by": "deepseek"}
        ]
    })

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest, request: Request):
    # Get conversation id from header (tool can pass X-Conversation-ID)
    conv_id = request.headers.get("X-Conversation-ID", "default")

    # Extract last user message
    last_user = None
    for m in reversed(req.messages):
        if m.role == "user":
            last_user = m.content
            break
    if last_user is None:
        raise HTTPException(status_code=400, detail="No user message found")

    token = get_token()
    session_id = get_or_create_conv(conv_id)

    # Determine parent_message_id
    with lock:
        parent_id = sessions.get(conv_id, {}).get("last_user_message_id")

    # For non-streaming: collect all chunks into a single response
    if not req.stream:
        full = []
        try:
            for chunk in stream_chat_chunks(token, last_user, session_id, parent_id):
                full.append(chunk)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        full_text = "".join(full)
        update_parent_ids(conv_id)
        return JSONResponse({
            "id": f"chatcmpl-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": full_text},
                "finish_reason": "stop"
            }]
        })

    # Streaming: create the sync generator and wrap it
    try:
        sync_gen = stream_chat_chunks(token, last_user, session_id, parent_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # We need to update parent IDs after the stream completes. We can do that in a background task.
    async def stream_and_update():
        async for sse in sse_adapter(sync_gen, conv_id):
            yield sse
        update_parent_ids(conv_id)

    return StreamingResponse(stream_and_update(), media_type="text/event-stream")

# ────────────────────────────────
if __name__ == "__main__":
    print("Starting DeepSeek OpenAI proxy on http://0.0.0.0:8800")
    uvicorn.run(app, host="0.0.0.0", port=8800)
