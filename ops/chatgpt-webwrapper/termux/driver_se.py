#!/usr/bin/env python3
"""ChatGPT webWrapper — harvest driver, TERMUX DEVICE INSTANCE.

Selenium form of driver.py over core_se.py. Participant actions only:
open the MonoRepo project on the surface, open each conversation in
census order, capture its messages in core's shape ([{role, content}]).

Checkpointing rides the session store, identical to driver.py:
  - per conversation: session_store.save(task_key, conversation_id, meta)
    + core_se.save_session_cache(conversation_id, messages) -> the
    session-store file, which fires the dispatch hook (listener pipeline
    -> telemetry records).
  - per run: session_store.save_run_state(RUN_KEY, state) atomically
    after EVERY conversation; a rerun resumes by skipping completed ids.
scrape/full/<id>.md is core_se.export_markdown of the capture, and
scrape/full/manifest.json is a read-model generated FROM the run state
(the store of record is the session store, not the manifest).

Serial pacing; stop-on-friction — any captcha, account warning, or rate
limit ends the run with its class recorded. Run only against an
already-live session (see core_se.py --establish / run.sh).

Immediate telemetry (owner ruling 2026-11-26): the entrypoint (run.sh)
emits run_started before session establishment begins; this driver emits
its own run_started before opening the session, then session_event /
conversation_captured / friction_event / run_finished in the existing
telemetry.py shapes. No deferred or post-hoc-only mode exists.
"""
import json
import os
import sys
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import core_se as core  # noqa: E402
import session_store  # noqa: E402
import telemetry  # noqa: E402

FULL_DIR = os.path.join(BASE, "scrape", "full")
MANIFEST = os.path.join(FULL_DIR, "manifest.json")
RUN_TASK_TEXT = "chatgpt-webwrapper harvest"
RUN_KEY = session_store.task_key(RUN_TASK_TEXT, os.path.abspath(__file__))


def project_json_path():
    """Census of record: the bundle's own project.json first (the copy
    that travels to the device), then the VM wrapper dir's."""
    for cand in (
        os.path.join(BASE, "project.json"),
        os.path.join(BASE, "..", "project.json"),
        os.path.expanduser("~/workspace/chatgpt-wrapper/project.json"),
    ):
        if os.path.exists(cand):
            return cand
    return os.path.join(BASE, "project.json")


PROJECT_JSON = project_json_path()


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
        }
    return state


def write_manifest_read_model(state, extra=None):
    """manifest.json is generated FROM the run state (read-model)."""
    m = {
        "project": state.get("project"),
        "project_id": state.get("project_id"),
        "census_total": state.get("census_total"),
        "captured_total": len(state.get("completed", [])),
        "completed": state.get("completed", []),
        "status": state.get("status"),
        "store_of_record": f"session_store/runs/{RUN_KEY}/state.json",
        "updated_at": now(),
    }
    if os.path.exists(MANIFEST):
        try:
            with open(MANIFEST) as f:
                prior = json.load(f)
            for k in ("attempts", "probe", "login", "preexisting_full_text"):
                if k in prior and k not in m:
                    m[k] = prior[k]
        except Exception:
            pass
    if extra:
        m.update(extra)
    if state.get("friction"):
        m["friction"] = state["friction"]
    if state.get("error"):
        m["error"] = state["error"]
    os.makedirs(FULL_DIR, exist_ok=True)
    tmp = MANIFEST + ".tmp"
    with open(tmp, "w") as f:
        json.dump(m, f, indent=2)
    os.replace(tmp, MANIFEST)
    return m


def checkpoint(state):
    session_store.save_run_state(RUN_KEY, state)
    write_manifest_read_model(state)


def capture_conversation(state, conv, messages, turn_ts=None):
    """The per-conversation conformance path (shared shape with
    driver.py): session-store record + message file (fires the dispatch
    hook) + markdown export + atomic run-state checkpoint."""
    cid = conv["id"]
    store_path = core._cache_path(cid)
    key = session_store.task_key(conv.get("title") or cid, store_path)
    session_store.save(key, cid, meta={
        "last_task": conv.get("title") or cid,
        "title": conv.get("title"),
        "url": conv.get("url"),
        "project_id": state.get("project_id"),
    })
    if turn_ts:
        core.save_session_cache(cid, messages, fire_hook=False)
        import dispatch_pipeline

        enriched = []
        for i, m in enumerate(messages):
            e = dict(m)
            if i < len(turn_ts) and turn_ts[i]:
                e["ts"] = turn_ts[i]
            enriched.append(e)
        dispatch_pipeline.trigger_dispatch(cid, enriched)
    else:
        core.save_session_cache(cid, messages)
    md_path = os.path.join(FULL_DIR, cid + ".md")
    os.makedirs(FULL_DIR, exist_ok=True)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# {conv.get('title')}\n\n")
        f.write(f"- id: {cid}\n- url: {conv.get('url')}\n- captured_at: {now()}\n\n---\n\n")
        f.write(core.export_markdown(messages))
    state["completed"].append(
        {"id": cid, "title": conv.get("title"), "file": f"scrape/full/{cid}.md",
         "session_file": f"session_store/{cid}.json", "task_key": key, "captured_at": now()}
    )
    checkpoint(state)
    return key


def out(state, cls, **kw):
    print(json.dumps({"state": state, "class": cls, **kw}), flush=True)


def main():
    with open(PROJECT_JSON) as f:
        project = json.load(f)
    project_url = project["url"]

    state = load_state(project)
    done = {c["id"] for c in state["completed"]}

    telemetry.emit("run_started", driver="driver_se.py", project_id=project.get("project_id"))
    try:
        with core.Session() as s:
            s.goto(core.HOME_URL, settle_ms=2000)
            s.check_friction()
            signed_in = s.is_signed_in()
            telemetry.emit("session_event", state="signed_in" if signed_in else "profile_logged_out", url=s.url)
            if not signed_in:
                out("no_session", "profile_logged_out", url=s.url)
                state["status"] = "no_session"
                checkpoint(state)
                telemetry.emit("run_finished", status="no_session", captured_total=len(state["completed"]))
                return 2
            convs = s.list_project_conversations(project_url)
            state["census_total"] = len(convs)
            state["status"] = "harvesting"
            checkpoint(state)
            captured = 0
            for conv in convs:
                if conv["id"] in done:
                    continue
                s.pause(2500)
                s.open_conversation(conv["url"])
                messages = s.read_messages()
                capture_conversation(state, conv, messages)
                done.add(conv["id"])
                captured += 1
                telemetry.emit(
                    "conversation_captured",
                    conversation_id=conv["id"],
                    title=conv["title"],
                    file=f"scrape/full/{conv['id']}.md",
                    session_file=f"session_store/{conv['id']}.json",
                    messages=len(messages),
                )
            state["status"] = "complete" if len(done) >= len(convs) else "partial"
            checkpoint(state)
            telemetry.emit("run_finished", status=state["status"], captured_this_run=captured,
                           captured_total=len(state["completed"]), census_total=len(convs))
            out("ok", "harvest_complete" if state["status"] == "complete" else "harvest_partial",
                captured_this_run=captured, captured_total=len(state["completed"]), census_total=len(convs))
            return 0
    except core.FrictionError as e:
        state["status"] = "stopped_on_friction"
        state["friction"] = {"class": e.cls, "url": e.url, "at": now()}
        checkpoint(state)
        telemetry.emit("friction_event", friction_class=e.cls, url=e.url)
        telemetry.emit("run_finished", status="stopped_on_friction", captured_total=len(state["completed"]))
        out("fail", e.cls, url=e.url, captured_total=len(state["completed"]))
        return 3
    except Exception as e:  # noqa: BLE001 - failure class surface
        state["status"] = "stopped_on_error"
        state["error"] = {"class": type(e).__name__, "detail": str(e)[:200], "at": now()}
        checkpoint(state)
        telemetry.emit("friction_event", friction_class=type(e).__name__, detail=str(e)[:200])
        telemetry.emit("run_finished", status="stopped_on_error", captured_total=len(state["completed"]))
        out("fail", type(e).__name__, detail=str(e)[:200], captured_total=len(state["completed"]))
        return 3


if __name__ == "__main__":
    sys.exit(main())
