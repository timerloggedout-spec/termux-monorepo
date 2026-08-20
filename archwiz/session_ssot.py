import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from archwiz.config import SSOT_DIR

SCHEMA_VERSION = 1

class SessionSSOT:
    """
    Minimal writer for the Session SSOT (Single Source of Truth).
    Follows docs/schemas/session-ssot.md.
    """

    def __init__(self, provider: str, session_id: str, account: str = "default"):
        self.provider = provider
        self.session_id = session_id
        self.account = account
        self.base_dir = SSOT_DIR / provider / account / session_id
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.manifest_path = self.base_dir / "manifest.json"
        self.messages_path = self.base_dir / "messages.jsonl"
        self.events_path = self.base_dir / "events.jsonl"

    def upsert_manifest(self, title: Optional[str] = None, native_refs: Dict[str, Any] = None, capabilities: List[str] = None):
        """Write or update manifest.json."""
        now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        if self.manifest_path.exists():
            with open(self.manifest_path, "r") as f:
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

        with open(self.manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")

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

        with open(self.messages_path, "a") as f:
            f.write(json.dumps(msg) + "\n")

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

        with open(self.events_path, "a") as f:
            f.write(json.dumps(event) + "\n")

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
