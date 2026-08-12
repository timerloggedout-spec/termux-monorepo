"""
CI agent logic for DeepSeek integration.
Does not modify core.py – used by ci_mode.py.

Admin-scope defaults: thinking=True, expert=True (always).
No quota model — frustrated-user retries only.
Account-1 primary; supports 2–3 simultaneous sessions.

IMPORTANT: DeepSeek web always streams SSE. A fixed 120s non-stream
timeout will abort multi-minute thinking. We stream-consume chunks
with a long read timeout instead.
"""
import os
import json
import subprocess
import time
import requests

DEEPSEEK_BASE = "https://chat.deepseek.com"
# Connect quickly; allow long idle between SSE chunks while model thinks
STREAM_CONNECT_TIMEOUT = int(os.environ.get("DEEPSEEK_CONNECT_TIMEOUT", "30"))
STREAM_READ_TIMEOUT = int(os.environ.get("DEEPSEEK_READ_TIMEOUT", "1200"))  # 20 minutes


def _parse_sse_chunk(line: str) -> str:
    """Extract text content from one SSE data line. Returns '' if none."""
    if not line or not line.startswith("data:"):
        return ""
    raw = line[5:].strip()
    if not raw or raw in ("[DONE]", "FINISHED"):
        return ""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return ""

    if not isinstance(data, dict):
        return ""

    # Shape A: {"v": "text"} or {"content": "text"}
    for key in ("v", "content"):
        val = data.get(key)
        if isinstance(val, str) and val not in ("FINISHED",):
            return val

    # Shape B: {"v": {"response": {"content": "..."}}}
    v = data.get("v")
    if isinstance(v, dict):
        resp = v.get("response") or {}
        if isinstance(resp, dict):
            c = resp.get("content") or ""
            if isinstance(c, str) and c:
                return c
        # thinking delta
        t = v.get("thinking_content") or v.get("thinking") or ""
        if isinstance(t, str) and t and os.environ.get("DEEPSEEK_INCLUDE_THINKING", "").lower() in ("1", "true", "yes"):
            return t

    # Shape C: OpenAI-like choices delta
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        delta = choices[0].get("delta") or choices[0].get("message") or {}
        if isinstance(delta, dict):
            c = delta.get("content") or ""
            if isinstance(c, str):
                return c

    return ""


def deepseek_chat(session, messages, thinking=True, expert=True):
    """
    Stream a chat completion from DeepSeek web API.

    Watches the SSE stream while the model thinks/responds — can take
    several minutes. Does NOT use a single-shot 120s non-stream POST.

    --thinking and --Expert are ALWAYS true by default (operator policy).
    """
    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Client-Platform": "web",
        "Origin": DEEPSEEK_BASE,
        "Referer": f"{DEEPSEEK_BASE}/",
    }
    # Optional PoW header if session carried one from ensure_session
    if session.get("pow_header"):
        headers["X-Ds-Pow-Response"] = session["pow_header"]

    s = requests.Session()
    s.cookies.update(session.get("cookies", {}))
    s.headers.update(headers)

    # Prefer last user prompt for web path; keep system context inlined
    system_parts = [m["content"] for m in messages if m.get("role") == "system"]
    user_parts = [m["content"] for m in messages if m.get("role") == "user"]
    prompt = "\n\n".join(user_parts) if user_parts else ""
    if system_parts:
        prompt = system_parts[0] + "\n\n" + prompt

    # Web completion payload (matches multi-ai-cli / deepcli core)
    payload = {
        "chat_session_id": session.get("chat_session_id"),
        "parent_message_id": session.get("parent_message_id"),
        "prompt": prompt,
        "ref_file_ids": [],
        "thinking_enabled": bool(thinking),
        "search_enabled": False,
        "stream": True,  # server always SSE anyway
    }
    # Drop null chat_session_id so server can allocate if needed
    if not payload["chat_session_id"]:
        payload.pop("chat_session_id", None)

    url = f"{DEEPSEEK_BASE}/api/v0/chat/completion"
    # Fallback OpenAI-style path if v0 rejects
    alt_url = f"{DEEPSEEK_BASE}/api/chat/completions"

    timeout = (STREAM_CONNECT_TIMEOUT, STREAM_READ_TIMEOUT)
    last_err = None

    for attempt_url, use_openai_shape in ((url, False), (alt_url, True)):
        try:
            body = payload
            if use_openai_shape:
                body = {
                    "messages": messages,
                    "stream": True,
                    "thinking": bool(thinking),
                    "expert": bool(expert),
                }
            resp = s.post(attempt_url, json=body, stream=True, timeout=timeout)
            if resp.status_code >= 400:
                last_err = f"HTTP {resp.status_code} on {attempt_url}"
                continue

            parts = []
            started = time.time()
            for line in resp.iter_lines(decode_unicode=True):
                if line is None:
                    continue
                chunk = _parse_sse_chunk(line if isinstance(line, str) else line.decode("utf-8", "replace"))
                if chunk:
                    parts.append(chunk)
            elapsed = time.time() - started
            text = "".join(parts).strip()
            if text:
                print(f"::notice::DeepSeek stream complete ({elapsed:.1f}s, {len(parts)} chunks, thinking={thinking})")
                return text
            last_err = f"Empty stream body from {attempt_url} after {elapsed:.1f}s"
        except requests.Timeout as e:
            last_err = f"Timeout after {STREAM_READ_TIMEOUT}s read window: {e}"
            # Do not fall through on timeout of long think — surface it
            break
        except requests.RequestException as e:
            last_err = str(e)
            continue

    raise RuntimeError(f"DeepSeek stream failed: {last_err}")


def run_ci(event, session, peer, workspace, operator_token):
    """
    Non-interactive agent loop.
    Returns a dict of actions taken.
    """
    gh_env = os.environ.copy()
    if operator_token:
        gh_env["GH_TOKEN"] = operator_token

    pr_number = event.get("pull_request", {}).get("number")
    repo = event.get("repository", {}).get("full_name")
    action = event.get("action")
    decisions = []

    thinking = os.environ.get("DEEPSEEK_THINKING", "true").lower() not in ("0", "false", "no")
    expert = os.environ.get("DEEPSEEK_EXPERT", "true").lower() not in ("0", "false", "no")

    if action in ["opened", "synchronize", "reopened"] and pr_number:
        if not repo:
            return {"actions": [], "error": "Missing repository.full_name in event"}

        try:
            diff = subprocess.check_output(
                ["gh", "pr", "diff", str(pr_number), "--repo", repo],
                env=gh_env, text=True, timeout=120,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            return {"actions": [], "error": f"Failed to get PR diff: {e}"}

        truncated = len(diff) > 8000
        user_content = diff[:8000]
        if truncated:
            user_content += "\n\n[diff truncated; remainder omitted]"

        messages = [
            {
                "role": "system",
                "content": (
                    "You are DeepSeek v4-Pro in Expert mode with thinking enabled. "
                    "Senior software engineer reviewing a pull request. "
                    "Provide a concise summary of potential issues, risks, and improvements."
                ),
            },
            {"role": "user", "content": user_content},
        ]

        try:
            analysis = deepseek_chat(session, messages, thinking=thinking, expert=expert)
        except Exception as e:
            print(f"::error::DeepSeek stream error: {type(e).__name__}: {e}")
            analysis = f"DeepSeek API error: {type(e).__name__}"

        comment_ok = False
        try:
            r = subprocess.run(
                ["gh", "pr", "comment", str(pr_number), "--body", analysis[:2000], "--repo", repo],
                env=gh_env, check=False, timeout=60,
            )
            comment_ok = r.returncode == 0
        except subprocess.TimeoutExpired:
            comment_ok = False

        if comment_ok:
            decisions.append({
                "type": "pr_review",
                "pr": pr_number,
                "summary": analysis[:200],
                "thinking": thinking,
                "expert": expert,
                "account": "account-1",
            })

    return {
        "actions": decisions,
        "event": action,
        "pr": pr_number,
        "provider_used": peer.get("provider", "deepseek"),
        "thinking": thinking,
        "expert": expert,
        "account": "account-1",
    }
