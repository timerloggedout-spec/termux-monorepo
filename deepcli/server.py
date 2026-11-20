#!/usr/bin/env python3
"""OpenAI-compatible API server using DeepSeek internal API."""
import sys, json, time, uuid, threading
from pathlib import Path
from typing import Dict, Any, Optional

# Ensure deepcli is importable
sys.path.insert(0, str(Path(__file__).parent))  # deepcli root
from deepcli.core import (
    get_token, create_session, stream_completion, get_history, _set_last_session
)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="DeepSeek Local API")

# Session store: maps external conversation_id → (deepseek_session_id, last_user_message_id)
sessions: Dict[str, Dict[str, Any]] = {}
lock = threading.Lock()

# ---------- Models ----------
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = "deepseek-chat"
    messages: list[Message]
    stream: bool = False
    temperature: Optional[float] = None
    # You can add other fields, but we ignore them for now

# ---------- Helpers ----------
def get_or_create_session(conversation_id: str) -> str:
    with lock:
        if conversation_id in sessions:
            return sessions[conversation_id]["session_id"]

        # Create new DeepSeek session
        token = get_token()
        sid = create_session(token)
        sessions[conversation_id] = {
            "session_id": sid,
            "last_user_message_id": None,
            "last_assistant_message_id": None,
        }
        _set_last_session(sid)  # optional, for CLI consistency
        return sid

def update_parent_ids(conversation_id: str):
    """Fetch latest history from DeepSeek and update parent IDs."""
    token = get_token()
    sid = sessions[conversation_id]["session_id"]
    msgs = get_history(token, sid, force_refresh=True)
    if not msgs:
        return
    # Find last user and last assistant message
    last_user = last_assistant = None
    for m in msgs:
        if m["role"].upper() == "USER":
            last_user = m["message_id"]
        elif m["role"].upper() == "ASSISTANT":
            last_assistant = m["message_id"]
    with lock:
        sessions[conversation_id]["last_user_message_id"] = last_user
        sessions[conversation_id]["last_assistant_message_id"] = last_assistant

# ---------- OpenAI streaming generator ----------
async def openai_stream_generator(prompt: str, session_id: str, parent_id: Optional[str],
                                  thinking: bool, search: bool):
    """Generate OpenAI-style SSE chunks from DeepSeek stream."""
    # We need to capture the streaming output from core.stream_completion().
    # It currently prints to console; we'll redirect it.
    import io
    from contextlib import redirect_stdout

    f = io.StringIO()
    try:
        with redirect_stdout(f):
            stream_completion(
                token=get_token(),
                prompt=prompt,
                session_id=session_id,
                parent_message_id=parent_id,
                thinking=thinking,
                search=search,
                file_ids=None,
                auto_retry=True
            )
    except Exception as e:
        yield f'data: {{"error": "{str(e)}"}}\n\n'
        yield 'data: [DONE]\n\n'
        return

    # The captured output is plain text chunks printed by stream_completion.
    # We need to split it and send as SSE deltas.
    full_text = f.getvalue()
    # For simplicity, send the whole text as one chunk. For true streaming,
    # you'd need to modify stream_completion to yield tokens.
    # A quick workaround: split by whitespace to simulate token streaming.
    words = full_text.split()
    for word in words:
        chunk = {
            "choices": [{
                "delta": {"content": word + " "},
                "index": 0,
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        time.sleep(0.01)  # tiny delay for visual effect

    # Send final chunk with finish_reason
    final_chunk = {
        "choices": [{
            "delta": {},
            "index": 0,
            "finish_reason": "stop"
        }]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

# ---------- Endpoint ----------
@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    # Extract last user message
    last_user = None
    for m in reversed(req.messages):
        if m.role == "user":
            last_user = m.content
            break
    if last_user is None:
        raise HTTPException(status_code=400, detail="No user message found")

    # Use a conversation ID based on request identity (e.g., from header or generate)
    # For simplicity, we reuse the same session across all requests.
    # In production, derive a unique ID per conversation.
    conversation_id = "default"
    session_id = get_or_create_session(conversation_id)

    # Determine parent_message_id: use last user message ID if available
    token = get_token()
    parent_id = None
    with lock:
        parent_id = sessions[conversation_id]["last_user_message_id"]

    # For streaming
    if req.stream:
        return StreamingResponse(
            openai_stream_generator(
                prompt=last_user,
                session_id=session_id,
                parent_id=parent_id,
                thinking=False,   # you can make this configurable
                search=False
            ),
            media_type="text/event-stream"
        )

    # Non-streaming: call send_message (or use the same stream but collect)
    # send_message is already non-streaming but doesn't support thinking/search.
    # We'll use chat_completion wrapper from core.py if available.
    from deepcli.core import chat_completion as core_chat_completion
    full_reply = core_chat_completion(
        token=token,
        prompt=last_user,
        session_id=session_id,
        parent_message_id=parent_id,
        thinking=False,
        search=False,
        auto_continue=True
    )

    # Update parent IDs for next turn
    update_parent_ids(conversation_id)

    return JSONResponse(content={
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": full_reply},
            "finish_reason": "stop"
        }]
    })

@app.get("/v1/models")
async def list_models():
    return JSONResponse(content={
        "object": "list",
        "data": [
            {"id": "deepseek-chat", "object": "model", "created": 1, "owned_by": "deepseek"},
            {"id": "deepseek-reasoner", "object": "model", "created": 1, "owned_by": "deepseek"}
        ]
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
