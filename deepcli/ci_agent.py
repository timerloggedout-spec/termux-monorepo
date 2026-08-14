"""
CI agent logic for DeepSeek integration.
Does not modify core.py – used by ci_mode.py.

Admin-scope defaults: thinking=True, expert=True (always).
Account-1 (primary) is PRIORITY default.
chat_session_id is required for /api/v0/chat/completion.
Artifact output is metadata only (no model text).

Supports:
  - pull_request opened/synchronize/reopened → PR review comment
  - issue_comment (created) with @deepcore/@deepseek triggers → issue reply
  - pull_request_review_comment (created) with @deepcore/@deepseek triggers → PR review reply
"""
import os
import re
import json
import subprocess
import time
import requests

from .session_manager import create_chat_session, get_pow_challenge, solve_pow, WASM_DIR

DEEPSEEK_BASE = "https://chat.deepseek.com"
STREAM_CONNECT_TIMEOUT = int(os.environ.get("DEEPSEEK_CONNECT_TIMEOUT", "30"))
STREAM_READ_TIMEOUT = int(os.environ.get("DEEPSEEK_READ_TIMEOUT", "1200"))


_AUTH_RE_PATTERNS = [
    re.compile(r"\bAuthorization Failed\b", re.IGNORECASE),
    re.compile(r"\binvalid token\b", re.IGNORECASE),
    re.compile(r"\b40003\b"),
    re.compile(r"\bHTTP\s+(401|403)\b"),
]

_CONN_RE_PATTERNS = [
    re.compile(r"\bConnection\b", re.IGNORECASE),
    re.compile(r"\btimeout\b", re.IGNORECASE),
    re.compile(r"\btimed out\b", re.IGNORECASE),
    re.compile(r"\bresolve\b", re.IGNORECASE),
    re.compile(r"\bunreachable\b", re.IGNORECASE),
]


def is_soft_skippable_error(e: Exception) -> bool:
    """
    Classify failures: only return True for authentication/credential failures
    or transient connection/network/timeout errors. Any other code crashes or
    server/logic defects remain hard-failures.
    """
    err_str = str(e)

    # 1. Strictly anchored Auth/Credential Failures
    if any(pat.search(err_str) for pat in _AUTH_RE_PATTERNS):
        return True

    # 2. Connection/timeout/resolving failures
    conn_exceptions = ["Connection", "Timeout", "NameResolution", "Dns", "AddrInfo"]
    if any(conn_exc in type(e).__name__ for conn_exc in conn_exceptions):
        return True
    if any(pat.search(err_str) for pat in _CONN_RE_PATTERNS):
        return True

    return False


# Triggers stripped from the user prompt before sending to the model.
_TRIGGER_RE = re.compile(
    r"(?i)@(?:deepcore|deepseek-ci|deepseek)\b",
)


def _parse_sse_chunk(line: str) -> str:
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

    for key in ("v", "content"):
        val = data.get(key)
        if isinstance(val, str) and val not in ("FINISHED",):
            return val

    v = data.get("v")
    if isinstance(v, dict):
        resp = v.get("response") or {}
        if isinstance(resp, dict):
            c = resp.get("content") or ""
            if isinstance(c, str) and c:
                return c

    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        delta = choices[0].get("delta") or choices[0].get("message") or {}
        if isinstance(delta, dict):
            c = delta.get("content") or ""
            if isinstance(c, str):
                return c
    return ""


def _ensure_chat_session_id(session: dict) -> str:
    sid = session.get("chat_session_id")
    if sid:
        return str(sid)
    token = session.get("token")
    if not token:
        raise RuntimeError("No token to create chat_session_id")
    sid = create_chat_session(token, cookies=session.get("cookies") or None, model_type="expert")
    session["chat_session_id"] = sid
    return sid


def _pow_header(session: dict) -> str | None:
    if session.get("pow_header"):
        return session["pow_header"]
    token = session.get("token")
    if not token:
        return None
    try:
        challenge = get_pow_challenge(token, cookies=session.get("cookies") or None)
        solver = WASM_DIR / "pow_solver.js"
        import subprocess as sp
        proc = sp.run(
            ["node", str(solver)],
            input=json.dumps(challenge),
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode == 0 and proc.stdout.strip().isdigit():
            import base64
            answer = int(proc.stdout.strip())
            payload = {
                "algorithm": challenge.get("algorithm", "DeepSeekHashV1"),
                "challenge": challenge["challenge"],
                "salt": challenge["salt"],
                "answer": answer,
                "signature": challenge["signature"],
                "target_path": challenge.get("target_path", "/api/v0/chat/completion"),
            }
            hdr = base64.b64encode(json.dumps(payload).encode()).decode()
            session["pow_header"] = hdr
            return hdr
    except Exception as e:
        print(f"::warning::PoW header skip: {e}")
    return None


def deepseek_chat(session, messages, thinking=True):
    """
    Stream completion with required chat_session_id + optional PoW header.
    Multi-minute thinking supported via long SSE read timeout.
    Note: expert mode is set via model_type="expert" during session creation, not per-message.
    """
    chat_session_id = _ensure_chat_session_id(session)
    pow_hdr = _pow_header(session)

    headers = {
        "Authorization": f"Bearer {session['token']}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "X-Client-Platform": "web",
        "Origin": DEEPSEEK_BASE,
        "Referer": f"{DEEPSEEK_BASE}/a/chat/s/{chat_session_id}",
    }
    if pow_hdr:
        headers["X-Ds-Pow-Response"] = pow_hdr

    system_parts = [m["content"] for m in messages if m.get("role") == "system"]
    user_parts = [m["content"] for m in messages if m.get("role") == "user"]
    prompt = "\n\n".join(user_parts) if user_parts else ""
    if system_parts:
        prompt = system_parts[0] + "\n\n" + prompt

    payload = {
        "chat_session_id": chat_session_id,
        "parent_message_id": session.get("parent_message_id"),
        "prompt": prompt,
        "ref_file_ids": [],
        "thinking_enabled": bool(thinking),
        "search_enabled": False,
        "stream": True,
    }

    url = f"{DEEPSEEK_BASE}/api/v0/chat/completion"
    timeout = (STREAM_CONNECT_TIMEOUT, STREAM_READ_TIMEOUT)

    with requests.Session() as s:
        s.cookies.update(session.get("cookies", {}))
        s.headers.update(headers)

        with s.post(url, json=payload, stream=True, timeout=timeout) as resp:
            if resp.status_code >= 400:
                raise RuntimeError(f"HTTP {resp.status_code} on completion: {resp.text[:300]}")

            parts = []
            started = time.time()
            for line in resp.iter_lines(decode_unicode=True):
                if line is None:
                    continue
                text_line = line if isinstance(line, str) else line.decode("utf-8", "replace")
                chunk = _parse_sse_chunk(text_line)
                if chunk:
                    parts.append(chunk)
            elapsed = time.time() - started
            text = "".join(parts).strip()
            if not text:
                raise RuntimeError(f"Empty SSE stream after {elapsed:.1f}s (chat_session_id={chat_session_id})")
            print(
                f"::notice::DeepSeek stream ok ({elapsed:.1f}s, {len(parts)} chunks, "
                f"account={session.get('account')}, chat_session_id={chat_session_id})"
            )
            return text


def _post_gh_comment(gh_env, repo, target, body, kind="issue"):
    """Post comment via gh CLI. kind is 'issue' or 'pr'. Returns (ok, error)."""
    cmd = [
        "gh",
        "pr" if kind == "pr" else "issue",
        "comment",
        str(target),
        "--body",
        body[:2000],
        "--repo",
        repo,
    ]
    try:
        r = subprocess.run(cmd, env=gh_env, capture_output=True, text=True, timeout=90)
        if r.returncode == 0:
            return True, None
        err = (r.stderr or r.stdout or "Unknown error")[:200]
        return False, err
    except subprocess.TimeoutExpired:
        return False, "Timeout posting comment"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:100]}"


def _handle_issue_comment(event, session, peer, gh_env, thinking):
    """Reply to an issue (or PR-as-issue) comment that mentioned deepCore."""
    comment = event.get("comment") or {}
    body = (comment.get("body") or "").strip()
    issue = event.get("issue") or {}
    issue_number = issue.get("number")
    repo = (event.get("repository") or {}).get("full_name")
    account = session.get("account") or peer.get("account") or "primary"

    if not issue_number or not repo:
        return {
            "actions": [],
            "error": "issue_comment missing issue.number or repository.full_name",
            "event": "issue_comment",
        }

    # Strip trigger tokens so the model sees the actual request.
    prompt = _TRIGGER_RE.sub("", body).strip()
    if not prompt:
        prompt = (
            "You were mentioned on a GitHub issue. "
            "Acknowledge and ask how you can help (one short paragraph)."
        )

    issue_title = issue.get("title") or ""
    messages = [
        {
            "role": "system",
            "content": (
                "You are deepCore (DeepSeek CI agent) in Expert mode with thinking enabled. "
                "Reply helpfully and concisely to the user's request on this GitHub issue. "
                "Do not invent secrets, tokens, or private data. Keep the reply under ~1500 chars."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Issue #{issue_number}: {issue_title}\n\n"
                f"User request:\n{prompt}"
            ),
        },
    ]

    try:
        analysis = deepseek_chat(session, messages, thinking=thinking)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)[:200]}"
        print(f"::error::DeepSeek stream error (issue_comment): {error_msg}")
        return {
            "actions": [],
            "error": f"DeepSeek API error: {error_msg}",
            "event": "issue_comment",
            "issue": issue_number,
            "account": account,
            "soft_skippable": is_soft_skippable_error(e),
        }

    # Prefix with moniker for clarity in the thread.
    reply = f"**`deepCore`**\n\n{analysis}"
    ok, err = _post_gh_comment(gh_env, repo, issue_number, reply, kind="issue")
    if not ok:
        print(f"::error::Failed to post issue comment: {err}")
        return {
            "actions": [{
                "type": "issue_reply_failed",
                "issue": issue_number,
                "comment_posted": False,
                "error": err,
                "account": account,
            }],
            "error": f"Failed to post issue comment: {err}",
            "event": "issue_comment",
            "issue": issue_number,
            "account": account,
            "chat_session_id": session.get("chat_session_id"),
        }

    return {
        "actions": [{
            "type": "issue_reply",
            "issue": issue_number,
            "comment_posted": True,
            "thinking": thinking,
            "account": account,
            "chat_session_id": session.get("chat_session_id"),
        }],
        "event": "issue_comment",
        "issue": issue_number,
        "provider_used": peer.get("provider", "deepseek"),
        "thinking": thinking,
        "account": account,
        "chat_session_id": session.get("chat_session_id"),
    }


def run_ci(event, session, peer, workspace, operator_token):
    """
    Run CI agent for PR review or issue_comment reply.
    Requires operator_token for gh CLI operations.
    Artifact fields are metadata only (no model text).
    """
    if not operator_token:
        return {
            "actions": [],
            "error": "OPERATOR_TOKEN required for gh CLI operations",
            "event": event.get("action"),
            "pr": event.get("pull_request", {}).get("number"),
        }

    gh_env = os.environ.copy()
    gh_env["GH_TOKEN"] = operator_token

    thinking = os.environ.get("DEEPSEEK_THINKING", "true").lower() not in ("0", "false", "no")
    account = session.get("account") or peer.get("account") or "primary"

    # --- issue_comment path (issue or PR discussion) ---
    # GitHub delivers issue_comment for both issues and PRs (with issue key).
    # pull_request_review_comment events have comment + pull_request but no issue key.
    if event.get("comment") and event.get("issue"):
        return _handle_issue_comment(event, session, peer, gh_env, thinking)

    # --- pull_request_review_comment path ---
    # Review comments have comment + pull_request but no issue key.
    # Handle them as PR comments (reply to review thread).
    if event.get("comment") and event.get("pull_request") and not event.get("issue"):
        comment = event.get("comment") or {}
        body = (comment.get("body") or "").strip()
        pr = event.get("pull_request") or {}
        pr_number = pr.get("number")
        repo = (event.get("repository") or {}).get("full_name")

        if not pr_number or not repo:
            return {
                "actions": [],
                "error": "pull_request_review_comment missing pull_request.number or repository.full_name",
                "event": "pull_request_review_comment",
            }

        # Strip trigger tokens so the model sees the actual request.
        prompt = _TRIGGER_RE.sub("", body).strip()
        if not prompt:
            prompt = (
                "You were mentioned in a pull request review comment. "
                "Acknowledge and ask how you can help (one short paragraph)."
            )

        pr_title = pr.get("title") or ""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are deepCore (DeepSeek CI agent) in Expert mode with thinking enabled. "
                    "Reply helpfully and concisely to the user's request on this GitHub pull request review. "
                    "Do not invent secrets, tokens, or private data. Keep the reply under ~1500 chars."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"PR #{pr_number}: {pr_title}\n\n"
                    f"User request in review comment:\n{prompt}"
                ),
            },
        ]

        try:
            analysis = deepseek_chat(session, messages, thinking=thinking)
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)[:200]}"
            print(f"::error::DeepSeek stream error (pull_request_review_comment): {error_msg}")
            return {
                "actions": [],
                "error": f"DeepSeek API error: {error_msg}",
                "event": "pull_request_review_comment",
                "pr": pr_number,
                "account": account,
                "soft_skippable": is_soft_skippable_error(e),
            }

        # Post as PR comment (gh pr comment works for both regular and review comments).
        reply = f"**`deepCore`**\n\n{analysis}"
        ok, err = _post_gh_comment(gh_env, repo, pr_number, reply, kind="pr")
        if not ok:
            print(f"::error::Failed to post PR review reply: {err}")
            return {
                "actions": [{
                    "type": "pr_review_reply_failed",
                    "pr": pr_number,
                    "comment_posted": False,
                    "error": err,
                    "account": account,
                }],
                "error": f"Failed to post PR review reply: {err}",
                "event": "pull_request_review_comment",
                "pr": pr_number,
                "account": account,
                "chat_session_id": session.get("chat_session_id"),
            }

        return {
            "actions": [{
                "type": "pr_review_reply",
                "pr": pr_number,
                "comment_posted": True,
                "thinking": thinking,
                "account": account,
                "chat_session_id": session.get("chat_session_id"),
            }],
            "event": "pull_request_review_comment",
            "pr": pr_number,
            "provider_used": peer.get("provider", "deepseek"),
            "thinking": thinking,
            "account": account,
            "chat_session_id": session.get("chat_session_id"),
        }

    # --- PR lifecycle path ---
    pr_number = event.get("pull_request", {}).get("number")
    repo = event.get("repository", {}).get("full_name")
    action = event.get("action")
    decisions = []
    comment_ok = None
    comment_error = None

    if action in ["opened", "synchronize", "reopened"] and pr_number:
        if not repo:
            return {"actions": [], "error": "Missing repository.full_name in event"}

        try:
            diff = subprocess.check_output(
                ["gh", "pr", "diff", str(pr_number), "--repo", repo],
                env=gh_env, text=True, timeout=180,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            return {
                "actions": [],
                "error": f"Failed to get PR diff: {e}",
                "event": action,
                "pr": pr_number,
            }

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
            analysis = deepseek_chat(session, messages, thinking=thinking)
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)[:200]}"
            print(f"::error::DeepSeek stream error: {error_msg}")
            return {
                "actions": [],
                "error": f"DeepSeek API error: {error_msg}",
                "event": action,
                "pr": pr_number,
                "account": account,
                "soft_skippable": is_soft_skippable_error(e),
            }

        comment_ok, comment_error = _post_gh_comment(
            gh_env, repo, pr_number, analysis, kind="pr"
        )
        if not comment_ok:
            print(f"::error::Failed to post PR comment: {comment_error}")

        if comment_ok:
            decisions.append({
                "type": "pr_review",
                "pr": pr_number,
                "comment_posted": True,
                "thinking": thinking,
                "account": account,
                "chat_session_id": session.get("chat_session_id"),
            })
        else:
            decisions.append({
                "type": "pr_review_failed",
                "pr": pr_number,
                "comment_posted": False,
                "error": comment_error,
                "account": account,
            })

    result = {
        "actions": decisions,
        "event": action,
        "pr": pr_number,
        "provider_used": peer.get("provider", "deepseek"),
        "thinking": thinking,
        "account": account,
        "chat_session_id": session.get("chat_session_id"),
    }

    if comment_ok is False and comment_error:
        result["error"] = f"Failed to post PR comment: {comment_error}"

    return result
