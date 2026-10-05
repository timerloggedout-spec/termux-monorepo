"""_v1_provenance — attribution ledger for every file write.

Records who wrote what, when, from which session, with before/after
file shas. Enables attribution: given a failed runtime state, walk the
ledger backwards to the exact session+message that introduced the
breaking line.

Public API:
    record(path, before_sha, after_sha, writer, session, msg_hash, tool, commit=None)
    file_sha(path)
    trace(path, sha) -> list of records that produced this sha
    blame(path, line_no) -> record for the change that last touched the line
"""

import json, hashlib, pathlib, time

HOME = pathlib.Path.home()
LEDGER = HOME / ".deepcli" / "logs" / "provenance.jsonl"
BLAME_DIR = HOME / ".deepcli" / "provenance"


def file_sha(path):
    """Return sha256 of file contents, or None if missing."""
    try:
        return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    except Exception:
        return None


def record(*, path, before_sha, after_sha, writer, session,
           msg_hash=None, tool=None, commit=None, note=None):
    """Append one provenance row."""
    row = {
        "ts": int(time.time()),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "path": str(path),
        "before_sha": before_sha,
        "after_sha": after_sha,
        "writer": writer,         # "agent" | "human" | "workflow:<name>" | "svc:<name>"
        "session": session,       # agent session id
        "msg_hash": msg_hash,     # assistant code-block hash that produced this
        "tool": tool,             # "write_file" | "gh_edit_file" | "gh_put" | ...
        "commit": commit,         # git commit that carried it, if known
        "note": note,
    }
    try:
        LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with LEDGER.open("a") as f:
            f.write(json.dumps(row, default=str) + "\n")
    except Exception:
        pass
    return row


def trace(path, sha=None):
    """Return ledger rows that produced the given sha (or all rows for path)."""
    rows = []
    try:
        for line in LEDGER.read_text(errors="ignore").splitlines():
            try: r = json.loads(line)
            except Exception: continue
            if r.get("path") != str(path): continue
            if sha and r.get("after_sha") != sha: continue
            rows.append(r)
    except Exception:
        pass
    return rows


def snapshot_and_record(*, path, writer, session, msg_hash=None, tool=None,
                        commit=None, note=None):
    """Convenience: hash before, call the writer, hash after, record."""
    path = pathlib.Path(path)
    before = file_sha(path)
    yield_after = None
    try:
        yield_after = yield
    finally:
        after = file_sha(path)
        record(path=path, before_sha=before, after_sha=after, writer=writer,
               session=session, msg_hash=msg_hash, tool=tool, commit=commit,
               note=note)


def blame(path, line_no):
    """Crude blame: find the ledger row for this path whose after_sha matches
    the current file, then return it. For line-level blame, we'd need a
    diff-per-write pass — deferred."""
    cur = file_sha(path)
    rows = trace(path, cur)
    if not rows: return None
    return rows[-1]
