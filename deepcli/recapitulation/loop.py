"""loop.py — direct loop: _chat_once + loop + __main__.

Extracted from deepagent.py. Uses the direct deepcli.core client (no HTTP hop).
"""

import json
import os
import sys
import time

import session_store

from .runtime import _notify, _autosnapshot
from .tools import TOOLS, execute, _maybe_continue, _auto_feedback
from .retry import _record_retry, _retry_plan, _RATE_MARKERS

MAX_STEPS = int(os.environ.get("AGENT_MAX_STEPS", "16"))
IDLE_SLEEP = float(os.environ.get("AGENT_STEP_PACE", "3"))


def _chat_once(
    messages,
    tools,
    model="deepseek-chat",
    session_id=None,
    parent_message_id=None,
    system=None,
    max_continues=3,
):
    from deepcli.core import get_token, create_session, chat_completion

    tok = get_token()
    sid = session_id or create_session(tok)

    # publish session ctx so the feedback tool can see it
    import recapitulation.tools as _t

    _t._CURRENT_SESSION_CTX = {"token": tok, "sid": sid}

    from _v1_tools import _flatten as _fl, _extract_calls as _ex, _strip as _st

    class _M:  # minimal shim to reuse _flatten
        def __init__(self, d):
            self.role = d["role"]
            self.content = d.get("content")
            self.tool_calls = d.get("tool_calls")
            self.tool_call_id = d.get("tool_call_id")
            self.name = d.get("name")

    class _TM:
        def __init__(self, d):
            self.function = type(
                "F",
                (),
                {
                    "name": d["function"]["name"],
                    "description": d["function"].get("description", ""),
                    "parameters": d["function"].get("parameters")
                    or {"type": "object", "properties": {}},
                },
            )()

    msgs = [_M(m) for m in messages]
    tls = [_TM(t) for t in tools] if tools else None
    prompt = _fl(msgs, tls)

    reply = ""
    parent_id = parent_message_id
    last_rest = 0.0
    last_kind = "start"
    for phase, wait, burst_i in _retry_plan(max_bursts=6):
        if wait:
            time.sleep(wait)
        try:
            reply = chat_completion(
                tok,
                prompt,
                sid,
                parent_message_id=parent_id,
                thinking=("reasoner" in model),
                search=False,
                auto_continue=True,
                max_continues=max_continues,
            )
        except (ConnectionError, ConnectionResetError, TimeoutError, OSError) as e:
            last_kind = "transport"
            last_rest = wait
            print(f"    [retry {phase} #{burst_i} wait={wait:.1f}s] {type(e).__name__}")
            continue

        if any(m.lower() in (reply or "").lower() for m in _RATE_MARKERS):
            last_kind = "ratelimit"
            last_rest = wait
            print(f"    [retry {phase} #{burst_i} wait={wait:.1f}s] rate-limit text")
            continue

        # success — but check for truncated stream
        reply = _maybe_continue(tok, sid, reply)
        _fk = "ok" if last_kind == "start" else last_kind
        _auto_feedback(tok, sid, _fk)
        if last_kind != "start":
            _record_retry("success", last_rest, burst_i, last_kind)
        break
    else:
        _record_retry("failure", last_rest, -1, last_kind)
        raise RuntimeError(f"gave up after retries: {last_kind}")

    calls = _ex(reply) if tools else []
    content = _st(reply)

    # capture assistant message_id for the next turn's parent
    try:
        from deepcli.core import get_history as _hist

        h = _hist(tok, sid, force_refresh=True)
        for m in reversed(h):
            if m.get("role", "").upper() == "ASSISTANT":
                parent_id = m.get("message_id")
                break
    except Exception:
        parent_id = None

    return sid, content, calls, parent_id


def loop(task, dry_run=False, model="deepseek-chat", task_path=None, fresh=False):
    """Loop until finish OR no-progress detected. Ceiling is safety, not policy."""
    print(f"\n▶ task: {task}\n")
    _t0 = time.time()
    key = session_store.task_key(task, task_path)
    _notify(
        "run",
        "🤖 Agent starting",
        f"task: {task[:120]}\nsrc: {os.environ.get('AGENT_SOURCE', 'manual')}",
    )

    if fresh:
        session_store.forget(key)
        sid = None
        print(f"  [session] fresh (forced, key={key})")
    else:
        _rec = session_store.load(key)
        if _rec and _rec.get("session_id"):
            sid = _rec["session_id"]
            print(f"  [session] resuming {sid[:12]}…  runs={_rec.get('runs', 0)}")
        else:
            sid = None
            print(f"  [session] fresh (key={key})")

    SAFETY_CEILING = int(os.environ.get("AGENT_SAFETY_CEILING", "60"))
    NO_PROGRESS_LIMIT = int(os.environ.get("AGENT_NO_PROGRESS_LIMIT", "5"))
    msgs = [{"role": "user", "content": task}]
    parent_id = None
    seen_sigs = []
    no_progress = 0
    for step in range(SAFETY_CEILING):
        print(f"── step {step + 1}/<dynamic> ──")
        if step > 0 and IDLE_SLEEP:
            time.sleep(IDLE_SLEEP)
        sid, content, calls, next_parent = _chat_once(
            msgs, TOOLS, model=model, session_id=sid, parent_message_id=parent_id
        )
        parent_id = next_parent
        if content:
            print(f"  (assistant): {content[:200]}")
        if not calls:
            print(
                f"\n✔ done (no tool calls — treating as implicit finish)\n{content}\n"
            )
            if sid and not dry_run:
                session_store.save(key, sid, meta={"last_task": task[:200]})
                print(f"  [session] saved {sid[:12]}… for key={key}")
            try:
                _elapsed = round(time.time() - _t0, 1)
            except Exception:
                _elapsed = 0.0
            if not dry_run:
                try:
                    _autosnapshot("implicit_finish")
                except Exception:
                    pass
                try:
                    _notify(
                        "run",
                        "✅ Agent done (implicit)",
                        f"sid={sid[:12] if sid else '?'}  elapsed={_elapsed}s\n{content[:200]}",
                        priority="high",
                    )
                except Exception:
                    pass
            return content
        am = {
            "role": "assistant",
            "content": content or None,
            "tool_calls": [
                {
                    "id": c["id"],
                    "type": "function",
                    "function": {
                        "name": c["function"]["name"],
                        "arguments": c["function"]["arguments"],
                    },
                }
                for c in calls
            ],
        }
        msgs.append(am)
        step_had_progress = False
        for c in calls:
            fn = c["function"]["name"]
            raw = c["function"]["arguments"]
            sig = f"{fn}::{raw[:200]}"
            print(f"  ▶ {fn}({raw[:120]})")
            if sig in seen_sigs[-12:]:
                print("    [repeat blocked — skipping duplicate call]")
                msgs.append(
                    {
                        "role": "tool",
                        "tool_call_id": c["id"],
                        "content": "SKIPPED: this exact call was already made; result is in prior tool message. Do not repeat.",
                    }
                )
                continue
            seen_sigs.append(sig)
            step_had_progress = True
            if dry_run:
                continue
            result = execute(c)
            if (
                fn == "finish"
                and isinstance(result, dict)
                and result.get("finished") is True
            ):
                print(f"\n✔ FINISH\n{result.get('summary', '')}\n")
                if sid and not dry_run:
                    session_store.save(key, sid, meta={"last_task": task[:200]})
                    print(f"  [session] saved {sid[:12]}… for key={key}")
                try:
                    _elapsed = round(time.time() - _t0, 1)
                except Exception:
                    _elapsed = 0.0
                _autosnapshot("finish")
                _notify(
                    "run",
                    "✅ Agent done",
                    f"sid={sid[:12] if sid else '?'}  elapsed={_elapsed}s\n{result.get('summary', '')[:200]}",
                    priority="high",
                )
                return result.get("summary", "")
            printable = json.dumps(result) if not isinstance(result, str) else result
            if not printable.lstrip().startswith(("ERROR", "BLOCKED", '{"error"')):
                step_had_progress = True
            print(f"    ← {printable[:300]}")
            msgs.append({"role": "tool", "tool_call_id": c["id"], "content": printable})
        if step_had_progress:
            no_progress = 0
        else:
            no_progress += 1
            print(f"    [no-progress {no_progress}/{NO_PROGRESS_LIMIT}]")
            if no_progress >= NO_PROGRESS_LIMIT:
                print(f"\n✗ stalled after {step + 1} steps (no progress)")
                return content or ""
    print(f"\n✗ hit SAFETY_CEILING={SAFETY_CEILING}\n")
    return ""


if __name__ == "__main__":
    argv = sys.argv[1:]
    dry = False
    fresh = False
    task_path = None
    if "--dry-run" in argv:
        dry = True
        argv.remove("--dry-run")
    if "--fresh" in argv:
        fresh = True
        argv.remove("--fresh")
    if "--task-file" in argv:
        i = argv.index("--task-file")
        if i + 1 < len(argv):
            task_path = argv[i + 1]
            del argv[i : i + 2]
    if not argv:
        print('usage: deepagent.py [--dry-run] [--fresh] [--task-file P] "<task>"')
        sys.exit(2)
    loop(" ".join(argv), dry_run=dry, task_path=task_path, fresh=fresh)
