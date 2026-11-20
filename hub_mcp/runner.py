"""Local deterministic execution for validated Termux hub jobs."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable

from .policy import get_capability
from .protocol import Job, JobValidationError, ResultEnvelope, redact, utc_now


class ReplayStore:
    """Small atomically-written idempotency store suitable for a single B160V worker."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self) -> set[str]:
        if not self.path.exists():
            return set()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise JobValidationError(f"Cannot read replay store: {exc}") from exc
        if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
            raise JobValidationError("Replay store is malformed")
        return set(data)

    def contains(self, job_id: str) -> bool:
        return job_id in self._load()

    def record(self, job_id: str) -> None:
        entries = self._load()
        entries.add(job_id)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, dir=self.path.parent, prefix=".processed-"
        ) as handle:
            json.dump(sorted(entries), handle, indent=2)
            handle.write("\n")
            temporary_path = Path(handle.name)
        os.replace(temporary_path, self.path)


def execute(job: Job, repository: Path, replay_store: ReplayStore) -> ResultEnvelope:
    """Execute one approved capability without a shell and record it exactly once."""
    if replay_store.contains(job.job_id):
        raise JobValidationError(f"Replay rejected for job_id {job.job_id}")
    spec = get_capability(job.capability)
    command = spec.render_command(repository.resolve(), job.arguments)
    started_at = utc_now()
    try:
        completed = subprocess.run(
            command,
            cwd=repository,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=spec.timeout_seconds,
            check=False,
            shell=False,
        )
        result = ResultEnvelope(
            job_id=job.job_id,
            job_digest=job.digest,
            capability=job.capability,
            success=completed.returncode == 0,
            exit_code=completed.returncode,
            stdout=redact(completed.stdout),
            stderr=redact(completed.stderr),
            started_at=started_at,
            finished_at=utc_now(),
        )
    except subprocess.TimeoutExpired as exc:
        result = ResultEnvelope(
            job_id=job.job_id,
            job_digest=job.digest,
            capability=job.capability,
            success=False,
            exit_code=None,
            stdout=redact(exc.stdout or ""),
            stderr=redact(exc.stderr or f"Timed out after {spec.timeout_seconds}s"),
            started_at=started_at,
            finished_at=utc_now(),
        )
    replay_store.record(job.job_id)
    return result


def execute_payload(payload: dict, repository: Path, state_directory: Path) -> dict:
    """Validate and execute a raw JSON-compatible payload for a single-worker hub."""
    job = Job.from_mapping(payload)
    result = execute(job, repository, ReplayStore(state_directory / "processed_jobs.json"))
    return result.to_mapping()
