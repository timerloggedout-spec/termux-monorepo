"""_v1_delegate — parent-child dispatch and check-in protocol.

A parent agent (primary) can spawn a child agent process bound to a
second account, hand it a role + task, and poll for progress. The
parent keeps working in parallel; the child writes status rows the
parent reads.

Public API:
    assign(child_id, role, task, task_file, parent_session, account=2, cli=CLI)
    poll(child_id) -> latest status row
    active() -> list of live children
    cancel(child_id)
    journal(rec)

Layout:
    ~/.deepcli/coordination/assignments.jsonl   parent writes
    ~/.deepcli/coordination/status/<child>.jsonl child writes
    ~/.deepcli/coordination/pids/<child>.pid    child pid
"""

import os, json, time, signal, subprocess, pathlib

HOME = pathlib.Path.home()
COORD = HOME / ".deepcli" / "coordination"
ASSIGN = COORD / "assignments.jsonl"
STATUS = COORD / "status"
PIDS = COORD / "pids"
for d in (COORD, STATUS, PIDS):
    d.mkdir(parents=True, exist_ok=True)


def journal(rec):
    try:
        with ASSIGN.open("a") as f:
            f.write(json.dumps(rec, default=str) + "\n")
    except Exception:
        pass


def assign(child_id, *, role, task, task_file=None, parent_session=None,
           account=2, cli=None):
    """Spawn a child deepagent bound to `account`, in background.

    Returns {child_id, pid, log, status_file, started}.
    """
    da = HOME / "deepcli" / "deepagent.py"
    if cli is None:
        cli = [str(da)]
    log_dir = HOME / ".deepcli" / "logs" / "hygiene"
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / f"delegate-{child_id}.log"
    status_file = STATUS / f"{child_id}.jsonl"

    env = {**os.environ,
           "DEEPSEEK_ACCOUNT": str(account),
           "DEEPSEEK_CONFIG": str(HOME / ".deepcli" / f"config-{account}.json"),
           "DEEPAGENT_CHILD_ID": child_id,
           "DEEPAGENT_STATUS_FILE": str(status_file),
           "DEEPAGENT_PARENT_SESSION": parent_session or ""}

    cmd = ["python3", "-u"] + cli
    if task_file:
        cmd += ["--task-file", str(task_file), "--fresh"]
    cmd += [task or "delegated task"]

    with log.open("wb") as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT,
                             env=env, start_new_session=True, cwd=str(HOME))

    (PIDS / f"{child_id}.pid").write_text(str(p.pid))
    journal({"ts": int(time.time()),
             "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "op": "assign", "child": child_id, "role": role,
             "account": account, "pid": p.pid,
             "task": (task or "")[:200],
             "task_file": str(task_file) if task_file else None,
             "parent": parent_session})
    return {"child_id": child_id, "pid": p.pid,
            "log": str(log), "status_file": str(status_file)}


def poll(child_id):
    p = STATUS / f"{child_id}.jsonl"
    if not p.exists(): return None
    try:
        last = p.read_text().strip().splitlines()[-1]
        return json.loads(last)
    except Exception:
        return None


def active():
    out = []
    for pidf in PIDS.glob("*.pid"):
        try:
            pid = int(pidf.read_text().strip())
            os.kill(pid, 0)  # probe
            out.append({"child_id": pidf.stem, "pid": pid, "alive": True})
        except Exception:
            out.append({"child_id": pidf.stem, "pid": None, "alive": False})
    return out


def cancel(child_id):
    pidf = PIDS / f"{child_id}.pid"
    if not pidf.exists(): return {"cancelled": False, "reason": "unknown"}
    try:
        pid = int(pidf.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        journal({"ts": int(time.time()), "op": "cancel", "child": child_id})
        return {"cancelled": True, "pid": pid}
    except Exception as e:
        return {"cancelled": False, "reason": str(e)[:100]}
