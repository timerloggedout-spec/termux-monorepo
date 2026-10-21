import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from archwiz.config import SSOT_DIR

SCHEMA_VERSION = 1


def _validate_ssot_param(name: str, value: str) -> None:
    if not value or not isinstance(value, str):
        raise ValueError(f"Invalid {name}: must be a non-empty string")
    p = Path(value)
    if ".." in p.parts or "/" in value or "\\" in value or p.is_absolute():
        raise ValueError(f"Path traversal detected in {name}: {value}")


def _secure_write(path: Path, content: str, append: bool = False) -> None:
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError(f"Symlink detected in target path or parent: {path}")
    flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if append else os.O_TRUNC)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "a" if append else "w", encoding="utf-8") as f:
        f.write(content)


class SessionSSOT:
    """
    Minimal writer for the Session SSOT (Single Source of Truth).
    Follows docs/schemas/session-ssot.md.
    """

    def __init__(self, provider: str, session_id: str, account: str = "default"):
        _validate_ssot_param("provider", provider)
        _validate_ssot_param("session_id", session_id)
        _validate_ssot_param("account", account)

        self.provider = provider
        self.session_id = session_id
        self.account = account

        if SSOT_DIR.is_symlink():
            raise ValueError(f"SSOT_DIR is a symlink: {SSOT_DIR}")

        self.base_dir = SSOT_DIR / provider / account / session_id
        if self.base_dir.is_symlink() or self.base_dir.parent.is_symlink():
            raise ValueError(f"Symlink detected in SSOT directory path: {self.base_dir}")

        self.base_dir.mkdir(parents=True, exist_ok=True)
        if not self.base_dir.is_symlink():
            try:
                self.base_dir.chmod(0o700)
            except Exception:
                pass

        self.manifest_path = self.base_dir / "manifest.json"
        self.messages_path = self.base_dir / "messages.jsonl"
        self.events_path = self.base_dir / "events.jsonl"

    def upsert_manifest(self, title: Optional[str] = None, native_refs: Dict[str, Any] = None, capabilities: List[str] = None):
        """Write or update manifest.json."""
        now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        if self.manifest_path.is_symlink():
            raise ValueError(f"Symlink manifest path rejected: {self.manifest_path}")

        if self.manifest_path.exists():
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        else:
            manifest = {
                "schema_version": SCHEMA_VERSION,
                "session_id": self.session_id,
                "provider": self.provider,
                "account": self.account,
                "created_at": now,
                "status": "active"
            }

        manifest["updated_at"] = now
        if title: manifest["title"] = title
        if native_refs: manifest["native_refs"] = native_refs
        if capabilities: manifest["capabilities_used"] = capabilities

        _secure_write(self.manifest_path, json.dumps(manifest, indent=2) + "\n", append=False)

    def append_message(self, role: str, content: str, message_id: Optional[str] = None,
                       timestamp_source: str = "observed", provider_message_id: Optional[str] = None):
        """Append a message to messages.jsonl."""
        msg = {
            "message_id": message_id or str(uuid.uuid4()),
            "role": role,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "timestamp_source": timestamp_source,
            "content": content,
            "provider_message_id": provider_message_id,
            "provenance": {"source": self.provider, "import_batch": None}
        }

        _secure_write(self.messages_path, json.dumps(msg) + "\n", append=True)

    def emit_event(self, event_type: str, source: str = "archwiz", correlation_id: Optional[str] = None, payload: Dict[str, Any] = None):
        """Emit an event to events.jsonl."""
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "type": event_type,
            "provider": self.provider,
            "account": self.account,
            "session_id": self.session_id,
            "correlation_id": correlation_id,
            "source": source,
            "payload": payload,
            "schema_version": SCHEMA_VERSION
        }

        _secure_write(self.events_path, json.dumps(event) + "\n", append=True)

def save_session_ssot(provider: str, session_id: str, messages: List[Dict[str, Any]], title: Optional[str] = None):
    """Convenience helper to save a full session state to SSOT."""
    ssot = SessionSSOT(provider, session_id)
    ssot.upsert_manifest(title=title)

    for msg in messages:
        ssot.append_message(
            role=msg.get("role", "unknown"),
            content=msg.get("content", ""),
            message_id=msg.get("message_id"),
            provider_message_id=msg.get("provider_message_id")
        )

    ssot.emit_event("SessionSaved", source="archwiz")
