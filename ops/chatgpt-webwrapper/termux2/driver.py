#!/usr/bin/env python3
"""driver.py — ChatGPT webWrapper harvest driver, Termux instance (v2).

Thin driver over core.py (deepcli shape): enumerate the MonoRepo
project's conversations at the session layer, capture each one's
messages in core's shape ([{role, content}]), and stream every capture
straight to GitHub via sink.py — the device keeps only the session
cache, the run state, and the sink outbox (owner constraint: small
cache only).

Checkpointing rides the session store (the stack's session_store.py):
run state is saved atomically after EVERY conversation; a rerun resumes
by skipping completed ids. Per conversation, the capture also lands in
core's session cache, whose save hook fires the dispatch pipeline
(telemetry export records) — the model's fan-out, unchanged.

Telemetry fires from the entrypoint from the first attempt: run_started
is this driver's first action, before session establishment.

Stop-on-friction: any captcha / security check, account warning, or
rate limit ends the run with its class recorded. Run only against an
already-live participant session (see core.py --import-session).
"""
import json
import os
import sys
import time
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import core  # noqa: E402
import session_store  # noqa: E402
import sink  # noqa: E402
import telemetry  # noqa: E402

PROJECT_JSON = os.path.join(BASE, "project.json")
RUN_TASK_TEXT = "chatgpt-webwrapper harvest (termux2)"
RUN_KEY = session_store.task_key(RUN_TASK_TEXT, os.path.abspath(__file__))
PACE_SECONDS = 1.5


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state(project):
    state = session_store.load_run_state(RUN_KEY)
    if state is None:
        state = {
            "run_key": RUN_KEY,
            "project": project.get("name"),
            "project_id": project.get("project_id"),
            "census_total": None,
            "completed": [],
            "status": "new",
            "surface": "termux2",
        }
    return state


def checkpoint(state):
    session_store.save_run_state(RUN_KEY, state)


def capture_conversation(state, conv, title, messages):
    """Per-conversation path: session-store record + core session cache
    (fires the dispatch hook -> telemetry export) + streamed capture.
    No transcript file is kept on the device."""
    cid = conv["id"]
    if title and not conv.get("title"):
        conv["title"] = title
    store_path = core._cache_path(cid)
    key = session_store.task_key(conv.get("title") or cid, store_path)
    session_store.save(key, cid, meta={
        "last_task": conv.get("title") or cid,
        "title": conv.get("title"),
        "url": conv.get("url"),
        "project_id": state.get("project_id"),
    })
    core.save_session_cache(cid, messages)
    md = f"# {conv.get('title')}\n\n"
    md += f"- id: {cid}\n- url: {conv.get('url')}\n- captured_at: {now()}\n\n---\n\n"
    md += core.export_markdown(messages)
    sink_state, sink_ref = sink.store_capture(
        state.get("project_id"), cid, md, core.export_json(messages)
    )
    state["completed"].append({
        "id": cid,
        "title": conv.get("title"),
        "session_file": f"session_store/primary/{cid}.json",
        "task_key": key,
        "sink": sink_state,
        "sink_ref": sink_ref,
        "captured_at": now(),
    })
    checkpoint(state)
    return key, sink_state


def out(state, cls, **kw):
    print(json.dumps({"state": state, "class": cls, **kw}), flush=True)


def _finish(state, status):
    """Run-end leg: flush the outbox once more and stream the telemetry
    artifacts when a sink credential exists (best-effort, never blocks
    the run's own verdict)."""
    try:
        flushed = sink.flush_outbox()
        if flushed.get("pushed") or flushed.get("failed"):
            telemetry.emit("session_event", state="outbox_flush_end", **flushed)
    except Exception:
        pass
    if sink.enabled():
        pid = sink._safe(state.get("project_id"))
        for local, repo in (
            (os.path.join(BASE, "telemetry.jsonl"),
             f"{sink.HARVEST_ROOT}/{pid}/telemetry/telemetry.jsonl"),
            (os.path.join(BASE, "exports", "records.jsonl"),
             f"{sink.HARVEST_ROOT}/{pid}/telemetry/records.jsonl"),
            (os.path.join(BASE, "exports", "session-history.jsonl"),
             f"{sink.HARVEST_ROOT}/{pid}/telemetry/session-history.jsonl"),
            (os.path.join(BASE, "exports", "session-pointers.jsonl"),
             f"{sink.HARVEST_ROOT}/{pid}/telemetry/session-pointers.jsonl"),
        ):
            try:
                sink.push_bundle_file(local, repo, f"chatgpt harvest telemetry ({status})")
            except Exception:
                pass


def main():
    with open(PROJECT_JSON) as f:
        project = json.load(f)
    project_id = project.get("project_id")
    project_url = project.get("url")

    state = load_state(project)
    done = {c["id"] for c in state["completed"]}

    telemetry.emit("run_started", driver="driver.py", surface="termux2",
                   project_id=project_id)
    try:
        flushed = sink.flush_outbox()
        if flushed.get("pushed") or flushed.get("remaining"):
            telemetry.emit("session_event", state="outbox_flush_start", **flushed)
    except Exception:
        pass

    try:
        sess = core.session_state()
        signed_in = bool(sess.get("has_token"))
        telemetry.emit("session_event",
                       state="signed_in" if signed_in else "profile_logged_out",
                       user=sess.get("user"))
        if not signed_in:
            out("no_session", "profile_logged_out")
            state["status"] = "no_session"
            checkpoint(state)
            telemetry.emit("run_finished", status="no_session",
                           captured_total=len(state["completed"]))
            return 2

        convs = core.list_project_conversations(project_id, project_url)
        state["census_total"] = len(convs)
        state["status"] = "harvesting"
        checkpoint(state)
        telemetry.emit("session_event", state="census",
                       found=len(convs), expected=project.get("chats"))

        captured = 0
        for conv in convs:
            if conv["id"] in done:
                continue
            time.sleep(PACE_SECONDS)
            title, messages = core.fetch_conversation(conv["id"])
            core.save_session_cache(conv["id"], messages)
            _, sink_state = capture_conversation(state, conv, title, messages)
            done.add(conv["id"])
            captured += 1
            telemetry.emit(
                "conversation_captured",
                conversation_id=conv["id"],
                title=conv.get("title"),
                session_file=f"session_store/primary/{conv['id']}.json",
                sink=sink_state,
                messages=len(messages),
            )
        state["status"] = "complete" if len(done) >= len(convs) else "partial"
        checkpoint(state)
        _finish(state, state["status"])
        telemetry.emit("run_finished", status=state["status"],
                       captured_this_run=captured,
                       captured_total=len(state["completed"]),
                       census_total=len(convs))
        out("ok", "harvest_complete" if state["status"] == "complete" else "harvest_partial",
            captured_this_run=captured, captured_total=len(state["completed"]),
            census_total=len(convs))
        return 0
    except core.FrictionError as e:
        state["status"] = "stopped_on_friction"
        state["friction"] = {"class": e.cls, "url": e.url, "at": now()}
        checkpoint(state)
        telemetry.emit("friction_event", friction_class=e.cls, url=e.url)
        telemetry.emit("run_finished", status="stopped_on_friction",
                       captured_total=len(state["completed"]))
        out("fail", e.cls, url=e.url, captured_total=len(state["completed"]))
        return 3
    except core.SessionExpired:
        state["status"] = "no_session"
        checkpoint(state)
        telemetry.emit("friction_event", friction_class="profile_logged_out")
        telemetry.emit("run_finished", status="no_session",
                       captured_total=len(state["completed"]))
        out("no_session", "profile_logged_out", captured_total=len(state["completed"]))
        return 2
    except Exception as e:  # noqa: BLE001 - failure class surface
        state["status"] = "stopped_on_error"
        state["error"] = {"class": type(e).__name__, "detail": str(e)[:200], "at": now()}
        checkpoint(state)
        telemetry.emit("friction_event", friction_class=type(e).__name__,
                       detail=str(e)[:200])
        telemetry.emit("run_finished", status="stopped_on_error",
                       captured_total=len(state["completed"]))
        out("fail", type(e).__name__, detail=str(e)[:200],
            captured_total=len(state["completed"]))
        return 3


if __name__ == "__main__":
    sys.exit(main())
