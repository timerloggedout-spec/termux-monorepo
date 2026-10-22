"""Private canonical-observation publication; never polls, loads keys, or guesses scope.

Only the credential-owning caller may affirm the authenticated account and its free
entitlement. A passive observation alone is deliberately insufficient authority.
"""
from __future__ import annotations

import fcntl
import json
import os
from pathlib import Path
import tempfile

from .admission import AdmissionDenied, bind_canonical_observation


def publish_observation(destination: Path, observation: dict, **verified_binding) -> dict:
    """Bind canonical normalized signals and atomically upsert one exact model.

    No raw headers, payloads, credentials, USD or percentage signals are persisted.
    Account/provider/scope remain private and the output is mode 0600. Existing
    malformed files fail closed rather than erasing someone else's quota state.
    """
    row = bind_canonical_observation(observation, **verified_binding)
    destination = Path(destination)
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock = os.open(str(destination) + ".lock", os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0), 0o600)
    temporary = None
    try:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if destination.is_symlink():
            raise AdmissionDenied("quota_source_symlink")
        doc = {"schema_version": 1, "records": []}
        if destination.exists():
            try:
                doc = json.loads(destination.read_text(encoding="utf-8"))
                if not isinstance(doc, dict) or doc.get("schema_version") != 1 or not isinstance(doc.get("records"), list):
                    raise ValueError("invalid quota source")
                if any(not isinstance(record, dict) for record in doc["records"]):
                    raise ValueError("invalid quota record")
            except (ValueError, OSError) as exc:
                raise AdmissionDenied("quota_source_malformed") from exc
        matches = [old for old in doc["records"] if (old.get("provider"), old.get("model")) == (row["provider"], row["model"])]
        if len(matches) > 1:
            raise AdmissionDenied("quota_binding_ambiguous")
        if matches and any(matches[0].get(key) != row.get(key) for key in ("account", "scope")):
            raise AdmissionDenied("quota_account_or_scope_rebinding_requires_review")
        # A newer observation never rolls a known window backwards.
        if matches and (matches[0].get("observed_at", "") > row["observed_at"]):
            raise AdmissionDenied("quota_observation_out_of_order")
        records = [old for old in doc["records"] if old not in matches] + [row]
        records.sort(key=lambda item: (str(item.get("provider")), str(item.get("model"))))
        fd, temporary = tempfile.mkstemp(prefix=".quota-observation-", dir=destination.parent)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump({"schema_version": 1, "records": records}, output, sort_keys=True, allow_nan=False)
            output.write("\n")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
        temporary = None
        directory = os.open(destination.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return row
    finally:
        if temporary is not None:
            os.unlink(temporary)
        os.close(lock)
