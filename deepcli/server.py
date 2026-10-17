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

# ── Hindsight tool surface ─────────────────────────────────────────────────
# Wires deepcli._v1_hindsight into the server and routes it through the
# quota-aware RoutedHindsightClient (cloud → codespace → local FTS5) declared
# in ops/routing.yaml. 402/429/5xx demote the cloud lane; the local FTS5 bank
# always remains a reachable sink, preserving `circuit_break_on_cost`.
try:
    from fastapi import APIRouter as _APIRouter

    try:
        from deepcli._v1_hindsight import build_hindsight_tools as _hindsight_tools
    except Exception:
        from _v1_hindsight import build_hindsight_tools as _hindsight_tools  # noqa

    _ROUTER_OK = False
    try:
        try:
            from deepcli._v1_hindsight_router import (
                RoutedHindsightClient as _RoutedClient,
            )
        except Exception:
            from _v1_hindsight_router import (  # noqa
                RoutedHindsightClient as _RoutedClient,
            )
        _routed_client = _RoutedClient()
        _ROUTER_OK = True
    except Exception as _re:  # pragma: no cover
        _routed_client = None
        print(f"[server] hindsight routed client unavailable: {_re}")

    def _tools():
        # Route the retain/recall/reflect handlers through the routed client
        # when available; fall back to the plain client otherwise.
        if _ROUTER_OK and _routed_client is not None:
            return _hindsight_tools(_routed_client)
        return _hindsight_tools()

    _hindsight_router = _APIRouter(prefix="/v1/hindsight", tags=["hindsight"])

    @_hindsight_router.get("/tools")
    async def _hindsight_tool_specs():
        _specs = _tools()
        return {
            "count": len(_specs),
            "tools": [
                {
                    "name": s.name,
                    "description": getattr(s, "description", ""),
                    "schema": dict(getattr(s, "schema", {}) or {}),
                }
                for s in _specs
            ],
        }

    @_hindsight_router.get("/health")
    async def _hindsight_health():
        import os as _os
        return {
            "base_url": _os.environ.get("HINDSIGHT_BASE_URL"),
            "bank_id": _os.environ.get("HINDSIGHT_BANK_ID"),
            "tools_available": len(_tools()),
            "routed": _ROUTER_OK,
        }

    @_hindsight_router.get("/router")
    async def _hindsight_router_status():
        # Reports circuit-breaker state for the routed client so the
        # Observatory can render lane health without probing the cloud.
        if _ROUTER_OK and _routed_client is not None and hasattr(_routed_client, "status"):
            return {"routed": True, **(dict(_routed_client.status()))}
        return {"routed": False, "reason": "RoutedHindsightClient unavailable"}

    @_hindsight_router.post("/invoke")
    async def _hindsight_invoke(body: dict):
        """Invoke one Hindsight tool by name.

        Body: {"tool": "hindsight_recall", "args": {...}}
        Dispatches to the same handlers advertised by GET /v1/hindsight/tools,
        so HTTP callers (curl, GH Actions, Agora) get identical semantics to
        the in-process deepagent tool path.
        """
        name = (body or {}).get("tool")
        args = (body or {}).get("args") or {}
        if not name:
            raise HTTPException(status_code=400, detail="missing 'tool'")
        if not isinstance(args, dict):
            raise HTTPException(status_code=400, detail="'args' must be an object")
        handlers = {s.name: s.handler for s in _tools()}
        handler = handlers.get(name)
        if handler is None:
            raise HTTPException(
                status_code=404,
                detail=f"unknown hindsight tool {name!r}; have {sorted(handlers)}",
            )
        try:
            result = await handler(**args)
        except TypeError as exc:
            # Bad/missing argument shape — surface as a 400, not a 500.
            raise HTTPException(status_code=400, detail=f"bad args: {exc}")
        return {"tool": name, "ok": True, "result": result}

    app.include_router(_hindsight_router)
    print(
        "[server] hindsight router mounted at /v1/hindsight "
        f"(routed={_ROUTER_OK})"
    )
except Exception as _e:  # pragma: no cover
    print(f"[server] hindsight router skipped: {_e}")


# ── OpenAI-compatible tool surface + agent runner ───────────────────────────
# Mount the /v1/chat/completions tool-calling router (_v1_tools) and the
# async agent-run router (_v1_agent) so the deepagent tool path
# (hindsight_retain / hindsight_recall / hindsight_reflect advertised to the
# model) and the /v1/agent/* job surface are actually served by this process.
# Invariant: the mount is best-effort; a missing optional dep degrades the
# surface but never prevents server startup.
try:
    try:
        from deepcli._v1_tools import router as _tools_router
    except Exception:
        from _v1_tools import router as _tools_router  # noqa
    app.include_router(_tools_router)
    print("[server] /v1 chat-completions (tool-calling) router mounted")
except Exception as _te:  # pragma: no cover
    print(f"[server] /v1 tools router skipped: {_te}")

try:
    try:
        from deepcli._v1_agent import router as _agent_router
    except Exception:
        from _v1_agent import router as _agent_router  # noqa
    app.include_router(_agent_router)
    print("[server] /v1/agent async-run router mounted")
except Exception as _ae:  # pragma: no cover
    print(f"[server] /v1/agent router skipped: {_ae}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)
