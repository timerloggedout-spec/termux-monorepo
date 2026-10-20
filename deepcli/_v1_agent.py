"""/v1/agent — async agent-run endpoints.

POST /v1/agent                → start job, return {invocation_id, phase}
GET  /v1/agent/status/{id}    → {phase, elapsed_s, idle_s, last_line, tail[]}
POST /v1/agent/kill/{id}      → SIGINT then SIGTERM then SIGKILL
GET  /v1/agent/list           → recent jobs (last 20)

Every job writes progress to ~/.deepcli/logs/agent_<id>.log line-by-line.
idle_s = seconds since last log line was written → hang detection.
"""
import json, os, signal, subprocess, sys, threading, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

HOME = Path.home()
AGENT = HOME / "deepcli" / "agent.py"
LOGDIR = HOME / ".deepcli" / "logs"
TOKEN_FILE = HOME / ".deepcli" / "hub.token"

router = APIRouter(prefix="/v1", tags=["agent"])
_bearer = HTTPBearer(auto_error=False)

# ── job registry ──
JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()
HARD_TIMEOUT_S = 1800          # 30 min
IDLE_HANG_THRESHOLD_S = 120    # 2 min no output → report as "possibly_hung"


class AgentReq(BaseModel):
    task: str
    context: Optional[dict] = None
    cwd: Optional[str] = None
    dry_run: bool = False
    source: str = "unknown"


def _require_auth(creds: HTTPAuthorizationCredentials = Depends(_bearer)):
    expected = os.environ.get("HUB_TOKEN")
    if not expected and TOKEN_FILE.exists():
        expected = TOKEN_FILE.read_text().strip()
    if not expected:
        raise HTTPException(500, "hub token not configured")
    if creds is None or creds.credentials != expected:
        raise HTTPException(401, "invalid token")
    return True


def _job_log_path(inv_id: str) -> Path:
    LOGDIR.mkdir(parents=True, exist_ok=True)
    return LOGDIR / f"agent_{inv_id}.log"


def _job_meta_path(inv_id: str) -> Path:
    LOGDIR.mkdir(parents=True, exist_ok=True)
    return LOGDIR / f"agent_{inv_id}.meta.json"


def _write_meta(inv_id: str, meta: dict):
    try:
        _job_meta_path(inv_id).write_text(json.dumps(meta, indent=2))
    except Exception:
        pass


def _runner(inv_id: str, req: AgentReq):
    """Runs in a background thread. Writes to the job log line-by-line."""
    log_f = _job_log_path(inv_id)
    meta = {
        "invocation_id": inv_id,
        "source": req.source,
        "task_head": req.task[:300],
        "cwd": req.cwd or str(HOME),
        "dry_run": req.dry_run,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "phase": "running",
        "rc": None,
    }
    _write_meta(inv_id, meta)

    # effective task
    task = req.task.strip()
    if req.context:
        lines = [f"CONTEXT ({k}): {v}" for k, v in req.context.items()]
        task = "\n".join(lines) + "\n\nTASK:\n" + task

            # prefer deepagent if present and enabled (direct-import loop, no HTTP tax)
        _da = HOME / "deepcli" / "deepagent.py"
        _use_da = os.environ.get("DSH_USE_DEEPAGENT", "1") == "1"
        AGENT_BIN = _da if (_use_da and _da.exists()) else AGENT
        argv = [sys.executable, str(AGENT_BIN)]
    if req.dry_run:
        argv.append("--dry-run")
    argv.append(task)

    cwd = req.cwd or str(HOME)
    if not cwd.startswith(str(HOME)):
        with log_f.open("w") as fh:
            fh.write(f"ERROR: cwd outside home: {cwd}\n")
        meta.update({"phase": "error", "error": "cwd outside home"})
        _write_meta(inv_id, meta)
        with JOBS_LOCK:
            if inv_id in JOBS:
                JOBS[inv_id]["phase"] = "error"
        return

    # start with own process group so we can signal the whole tree
    proc = subprocess.Popen(
        argv, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
        preexec_fn=os.setsid,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )

    with JOBS_LOCK:
        if inv_id in JOBS:
            JOBS[inv_id]["pid"] = proc.pid

    started = time.time()
    with log_f.open("w") as fh:
        fh.write(f"# start {datetime.now(timezone.utc).isoformat()} pid={proc.pid}\n")
        fh.flush()
        try:
            for line in proc.stdout:
                fh.write(line)
                fh.flush()
                if time.time() - started > HARD_TIMEOUT_S:
                    try: os.killpg(proc.pid, signal.SIGKILL)
                    except Exception: pass
                    fh.write(f"\n# HARD TIMEOUT after {HARD_TIMEOUT_S}s\n")
                    break
            rc = proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            try: os.killpg(proc.pid, signal.SIGKILL)
            except Exception: pass
            rc = -9
        except Exception as e:
            fh.write(f"\n# runner exception: {type(e).__name__}: {e}\n")
            rc = -1
        finally:
            elapsed = round(time.time() - started, 2)
            fh.write(f"\n# end rc={rc} elapsed={elapsed}s\n")
            fh.flush()

    meta.update({
        "phase": "done",
        "rc": rc,
        "elapsed_s": elapsed,
        "ended_at": datetime.now(timezone.utc).isoformat(),
    })
    _write_meta(inv_id, meta)
    with JOBS_LOCK:
        if inv_id in JOBS:
            JOBS[inv_id].update({"phase": "done", "rc": rc, "elapsed_s": elapsed})


@router.post("/agent", dependencies=[Depends(_require_auth)])
async def _agent_start(req: AgentReq):
    if not AGENT.exists():
        raise HTTPException(500, f"agent.py missing: {AGENT}")

    # reject if another run is active
    with JOBS_LOCK:
        active = [j for j in JOBS.values() if j.get("phase") == "running"]
        if active:
            raise HTTPException(429, {
                "error": "another agent run is active",
                "active": [j["invocation_id"] for j in active],
            })

    inv_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[inv_id] = {
            "invocation_id": inv_id,
            "phase": "running",
            "started_at": time.time(),
            "source": req.source,
            "task_head": req.task[:200],
        }

    t = threading.Thread(target=_runner, args=(inv_id, req), daemon=True)
    t.start()

    return JSONResponse({
        "invocation_id": inv_id,
        "phase": "running",
        "log": str(_job_log_path(inv_id)),
        "status_url": f"/v1/agent/status/{inv_id}",
    }, status_code=202)


@router.get("/agent/status/{inv_id}", dependencies=[Depends(_require_auth)])
def _agent_status(inv_id: str):
    log_f = _job_log_path(inv_id)
    meta_f = _job_meta_path(inv_id)
    if not log_f.exists() and not meta_f.exists():
        raise HTTPException(404, "unknown invocation_id")

    with JOBS_LOCK:
        job = JOBS.get(inv_id, {})

    # compute idle time from log mtime
    idle_s = None
    elapsed_s = None
    tail = []
    if log_f.exists():
        st = log_f.stat()
        idle_s = round(time.time() - st.st_mtime, 1)
        try:
            tail = log_f.read_text(errors="replace").splitlines()[-25:]
        except Exception:
            tail = []

    if job.get("started_at"):
        elapsed_s = round(time.time() - job["started_at"], 1)

    phase = job.get("phase", "unknown")
    if phase == "running" and idle_s is not None and idle_s > IDLE_HANG_THRESHOLD_S:
        phase = "possibly_hung"

    meta = {}
    if meta_f.exists():
        try: meta = json.loads(meta_f.read_text())
        except Exception: pass

    return {
        "invocation_id": inv_id,
        "phase": phase,
        "idle_s": idle_s,
        "elapsed_s": elapsed_s,
        "rc": job.get("rc", meta.get("rc")),
        "pid": job.get("pid"),
        "tail": tail,
    }


@router.post("/agent/kill/{inv_id}", dependencies=[Depends(_require_auth)])
def _agent_kill(inv_id: str):
    with JOBS_LOCK:
        job = JOBS.get(inv_id)
    if not job:
        raise HTTPException(404, "unknown invocation_id")
    pid = job.get("pid")
    if not pid:
        return {"killed": False, "reason": "no pid yet"}
    signals = [signal.SIGINT, signal.SIGTERM, signal.SIGKILL]
    for i, sig in enumerate(signals):
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            return {"killed": True, "signal": sig.name}
        except Exception as e:
            return {"killed": False, "error": str(e)}
        time.sleep([5, 3, 0][i])
        try:
            os.kill(pid, 0)  # still alive?
        except ProcessLookupError:
            return {"killed": True, "signal": sig.name}
    return {"killed": False, "reason": "process ignored all signals"}


@router.get("/agent/list", dependencies=[Depends(_require_auth)])
def _agent_list():
    with JOBS_LOCK:
        jobs = sorted(JOBS.values(), key=lambda j: j.get("started_at", 0), reverse=True)[:20]
    return {"jobs": [
        {k: j.get(k) for k in ("invocation_id", "phase", "source", "task_head", "rc", "elapsed_s")}
        for j in jobs
    ]}
