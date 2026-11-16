"""/v1/* — OpenAI-compatible chat completions with tool support.

Public API (importable from other modules):
  _flatten(messages, tools) -> str      render messages+tools into one prompt
  _extract_calls(text)      -> list     parse tool calls from model reply
  _strip(text)              -> str      remove tool-call markers from content
  router                                FastAPI APIRouter
"""
import json, re, sys, time, uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

sys.path.insert(0, str(Path(__file__).parent))
from deepcli.core import get_token, create_session, chat_completion

router = APIRouter(prefix="/v1", tags=["openai"])


# ─── Pydantic models ─────────────────────────────────────────────

class _Fn(BaseModel):
    name: str
    description: Optional[str] = ""
    parameters: Optional[dict] = None


class _Tool(BaseModel):
    type: str = "function"
    function: _Fn


class _Msg(BaseModel):
    role: str
    content: Any = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list] = None

    @field_validator("content", mode="before")
    @classmethod
    def _coerce(cls, v):
        if v is None or isinstance(v, str):
            return v
        if isinstance(v, list):
            out = []
            for b in v:
                if isinstance(b, dict):
                    t = b.get("text") or b.get("content")
                    if t: out.append(str(t))
                elif isinstance(b, str):
                    out.append(b)
            return "\n".join(out)
        return str(v)


class ChatReq(BaseModel):
    model: str = "deepseek-chat"
    messages: list[_Msg]
    tools: Optional[list[_Tool]] = None
    tool_choice: Any = None
    stream: bool = False
    temperature: Optional[float] = None
    session_id: Optional[str] = None


# ─── prompt rendering ────────────────────────────────────────────

_TOOL_PREAMBLE = """You have access to these tools. To CALL a tool, emit EXACTLY one or more blocks of this exact form (no markdown fences, no prose alongside):

<tool_call>{"name": "<tool_name>", "arguments": {<json>}}</tool_call>

Rules:
- Output ONLY <tool_call> block(s) when calling tools.
- If no tool is needed, answer normally in text.
- Multiple <tool_call> blocks allowed (one per line).
- Arguments MUST be valid JSON.

Available tools:
"""


def _render_tools(tools) -> str:
    lines = [_TOOL_PREAMBLE]
    for t in tools:
        f = t.function
        spec = f.parameters or {"type": "object", "properties": {}}
        lines.append(f"- {f.name}: {f.description or ''}")
        lines.append(f"  schema: {json.dumps(spec, ensure_ascii=False)}")
    return "\n".join(lines)


def _flatten(messages, tools) -> str:
    """Render OpenAI messages + tool schemas into one DeepSeek prompt string."""
    system_parts, convo = [], []
    for m in messages:
        r = (m.role or "").lower()
        if r == "system":
            if m.content: system_parts.append(str(m.content))
        elif r == "user":
            convo.append(str(m.content or ""))
        elif r == "assistant":
            if getattr(m, "tool_calls", None):
                for tc in m.tool_calls:
                    fn = tc.get("function", {}) if isinstance(tc, dict) else {}
                    convo.append(f"[assistant -> {fn.get('name','?')}({fn.get('arguments','{}')})]")
            if m.content:
                convo.append(f"[assistant] {m.content}")
        elif r == "tool":
            tid = getattr(m, "tool_call_id", "?") or "?"
            convo.append(f"[tool result id={tid}] {m.content or ''}")
    if tools:
        system_parts.append(_render_tools(tools))
    sys_text = "\n\n".join(system_parts).strip() or None
    prompt = "\n\n".join(convo).strip()
    if sys_text:
        prompt = f"[SYSTEM]\n{sys_text}\n\n[CONVERSATION]\n{prompt}"
    return prompt


# ─── tool-call extraction ────────────────────────────────────────

def _try_json(s):
    try:
        return json.loads(s)
    except Exception:
        return None


def _balanced_json_at(s: str, start: int):
    """Substring of s from start through the matching close brace, or None."""
    if start >= len(s) or s[start] != "{":
        return None
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        c = s[i]
        if esc:
            esc = False
            continue
        if c == "\\":
            esc = True
            continue
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start:i+1]
    return None


def _mk_call(name, arguments):
    return {
        "id": "call_" + uuid.uuid4().hex[:24],
        "type": "function",
        "function": {
            "name": str(name),
            "arguments": json.dumps(arguments or {}, ensure_ascii=False),
        },
    }


def _extract_calls(text: str):
    """Parse tool calls from canonical <tool_call>, fenced JSON, or DSML variants."""
    if not text:
        return []
    out = []

    # Format A: <tool_call>{...}</tool_call> via brace-depth (handles nested JSON)
    for m in re.finditer(r"<?tool_call>\s*", text):
        j = text.find("{", m.end())
        if j == -1 or j - m.end() > 5:
            continue
        blob = _balanced_json_at(text, j)
        if not blob:
            continue
        obj = _try_json(blob)
        if isinstance(obj, dict) and "name" in obj:
            out.append(_mk_call(obj["name"], obj.get("arguments", {})))
    if out:
        return out

    # Format B: fenced JSON
    for m in re.finditer(r"```(?:json)?\s*", text):
        j = text.find("{", m.end())
        if j == -1 or j - m.end() > 5:
            continue
        blob = _balanced_json_at(text, j)
        if not blob:
            continue
        obj = _try_json(blob)
        if isinstance(obj, dict) and "name" in obj:
            out.append(_mk_call(obj["name"], obj.get("arguments", {})))
    if out:
        return out

    # Format C: DSML. Strip any non-word chars around "DSML", keep < and </.
    t = re.sub(r"<\s*[^\w<>]{0,15}DSML[^\w<>]{0,15}\s+",  "<",  text, flags=re.UNICODE)
    t = re.sub(r"</\s*[^\w<>]{0,15}DSML[^\w<>]{0,15}\s*", "</", t,    flags=re.UNICODE)

    if "<invoke " not in t and "<invoke\t" not in t and "<invoke\n" not in t:
        return out

    inv_open  = re.compile(r"<invoke\s+name=\"([^\"]+)\"[^>]*>", re.DOTALL)
    par_open  = re.compile(r"<parameter\s+name=\"([^\"]+)\"[^>]*>", re.DOTALL)
    par_close = re.compile(r"</parameter>", re.DOTALL)
    inv_close = re.compile(r"</invoke>", re.DOTALL)

    pos = 0
    while True:
        im = inv_open.search(t, pos)
        if not im:
            break
        name = im.group(1)
        # body is bounded by whichever comes first: next invoke open, or this invoke close
        next_open = inv_open.search(t, im.end())
        next_close = inv_close.search(t, im.end())
        boundary = len(t)
        if next_open:  boundary = min(boundary, next_open.start())
        if next_close: boundary = min(boundary, next_close.start())
        body = t[im.end():boundary]
        pos = boundary if boundary > im.end() else im.end() + 1
        args = {}
        pp = 0
        while True:
            pm = par_open.search(body, pp)
            if not pm:
                break
            key = pm.group(1)
            pc = par_close.search(body, pm.end())
            raw = body[pm.end():pc.start()].strip() if pc else body[pm.end():].strip()
            parsed = _try_json(raw)
            args[key] = parsed if parsed is not None else raw
            pp = pc.end() if pc else len(body)
        if args:
            out.append(_mk_call(name, args))
    return out


def _strip(text: str) -> str:
    t = re.sub(r"<?tool_call>.*?</tool_call>", "", text or "", flags=re.DOTALL)
    t = re.sub(r"```(?:json)?.*?```", "", t, flags=re.DOTALL)
    t = re.sub(r"<\s*[^\w<>]{0,15}DSML[^\w<>]{0,15}.*?</\s*[^\w<>]{0,15}DSML[^\w<>]{0,15}\s*\w+>", "", t, flags=re.DOTALL)
    t = re.sub(r"</?\s*[^\w<>]{0,15}DSML[^\w<>]{0,15}\s*(calls|invoke|parameter)?>", "", t)
    return t.strip()


# ─── rate-limit detection ────────────────────────────────────────

_RATE_MARKERS = ("Messages too frequent", "too frequent", "rate limit", "please wait")


def _rate_limited(text) -> bool:
    if not text:
        return False
    low = text.lower()
    return any(m.lower() in low for m in _RATE_MARKERS)


# ─── routes ──────────────────────────────────────────────────────

@router.get("/models")
def models():
    return {"object": "list", "data": [
        {"id": "deepseek-chat",     "object": "model", "owned_by": "deepseek-web"},
        {"id": "deepseek-reasoner", "object": "model", "owned_by": "deepseek-web"},
    ]}


@router.post("/chat/completions")
async def chat_completions(req: ChatReq):
    prompt = _flatten(req.messages, req.tools)
    if not prompt:
        raise HTTPException(400, "empty prompt")
    thinking = "reasoner" in req.model or req.model.endswith("-think")
    try:
        tok = get_token()
        sid = req.session_id or create_session(tok)
        reply = chat_completion(tok, prompt, sid, thinking=thinking, search=False,
                                auto_continue=True, max_continues=3)
    except SystemExit:
        raise HTTPException(500, "no deepcli session; run deepcli import-session")
    except Exception as e:
        raise HTTPException(502, f"{type(e).__name__}: {e}")

    if _rate_limited(reply):
        raise HTTPException(429, "deepseek web session rate limit: " + (reply or "")[:200])

    calls = _extract_calls(reply) if req.tools else []
    msg = {"role": "assistant", "content": _strip(reply) or None}
    finish = "stop"
    if calls:
        msg["tool_calls"] = calls
        finish = "tool_calls"
    return JSONResponse({
        "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": req.model,
        "session_id": sid,
        "choices": [{"index": 0, "message": msg, "finish_reason": finish}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    })
