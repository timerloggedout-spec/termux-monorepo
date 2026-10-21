import json
import os
import stat
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
    if value == "." or ".." in p.parts or "/" in value or "\\" in value or p.is_absolute():
        raise ValueError(f"Path traversal detected in {name}: {value}")


def _dir_flags() -> int:
    required = ("O_DIRECTORY", "O_NOFOLLOW")
    if os.name == "nt" or not all(hasattr(os, name) for name in required) or os.open not in os.supports_dir_fd:
        raise ValueError("Secure descriptor-relative directory operations are unavailable")
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _open_directory(path: Path, create: bool = False, mode: Optional[int] = None) -> int:
    """Open each absolute path component without following symlinks."""
    flags = _dir_flags()
    if not path.is_absolute():
        raise ValueError(f"SSOT directory must be absolute: {path}")
    if path == Path(os.path.abspath(path)) and path.is_symlink():
        raise ValueError(f"Base directory is a symlink: {path}")
    fd = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            if component in ("", "."):
                continue
            try:
                child = os.open(component, flags, dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, mode or 0o700, dir_fd=fd)
                child = os.open(component, flags, dir_fd=fd)
            except OSError as e:
                if e.errno in (getattr(os, "ELOOP", 40), getattr(os, "ENOTDIR", 20)):
                    raise ValueError(f"Symlink detected in directory ancestry: {path}") from e
                raise
            os.close(fd)
            fd = child
        if mode is not None:
            os.fchmod(fd, mode)
        return fd
    except Exception:
        os.close(fd)
        raise


def _session_dir(path: Path, base: Path, create: bool = False) -> int:
    try:
        relative = path.relative_to(base)
    except ValueError as e:
        raise ValueError(f"Path is outside SSOT directory: {path}") from e
    root_fd = _open_directory(base, create=create)
    fd = root_fd
    try:
        for component in relative.parts:
            if component in ("", "."):
                continue
            try:
                child = os.open(component, _dir_flags(), dir_fd=fd)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(component, 0o700, dir_fd=fd)
                child = os.open(component, _dir_flags(), dir_fd=fd)
            except OSError as e:
                if e.errno in (getattr(os, "ELOOP", 40), getattr(os, "ENOTDIR", 20)):
                    raise ValueError(f"Symlink detected in path ancestry: {component}") from e
                raise
            if fd != root_fd:
                os.close(fd)
            fd = child
        return fd
    except Exception:
        if fd != root_fd:
            os.close(fd)
        os.close(root_fd)
        raise


def _open_file(path: Path, base: Path, flags: int, mode: int = 0o600) -> int:
    directory_fd = _session_dir(path.parent, base, create=False)
    try:
        file_fd = os.open(path.name, flags | os.O_NOFOLLOW | os.O_NONBLOCK, mode, dir_fd=directory_fd)
    finally:
        os.close(directory_fd)
    try:
        info = os.fstat(file_fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError(f"SSOT target must be a single-link regular file: {path}")
    except Exception:
        os.close(file_fd)
        raise
    return file_fd


def _secure_write(path: Path, content: str, append: bool = False, base_dir: Optional[Path] = None) -> None:
    base = base_dir or path.parent
    flags = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if append else 0)
    try:
        fd = _open_file(path, base, flags)
    except OSError as e:
        if e.errno == getattr(os, "ELOOP", 40):
            raise ValueError(f"Symlink detected in target path: {path}") from e
        raise ValueError(f"Failed secure open for {path}: {e}") from e
    try:
        os.fchmod(fd, 0o600)
        if not append:
            os.ftruncate(fd, 0)
        with os.fdopen(fd, "a" if append else "w", encoding="utf-8") as stream:
            fd = -1
            stream.write(content)
    finally:
        if fd >= 0:
            os.close(fd)


class SessionSSOT:
    """Minimal writer for the Session SSOT (Single Source of Truth)."""

    def __init__(self, provider: str, session_id: str, account: str = "default"):
        _validate_ssot_param("provider", provider)
        _validate_ssot_param("session_id", session_id)
        _validate_ssot_param("account", account)
        self.provider = provider
        self.session_id = session_id
        self.account = account
        self.base_dir = SSOT_DIR / provider / account / session_id
        try:
            fd = _session_dir(self.base_dir, SSOT_DIR, create=True)
            try:
                os.fchmod(fd, 0o700)
            finally:
                os.close(fd)
        except OSError as e:
            raise ValueError(f"Failed secure session directory setup: {e}") from e
        self.manifest_path = self.base_dir / "manifest.json"
        self.messages_path = self.base_dir / "messages.jsonl"
        self.events_path = self.base_dir / "events.jsonl"

    def upsert_manifest(self, title: Optional[str] = None, native_refs: Dict[str, Any] = None, capabilities: List[str] = None):
        """Write or update manifest.json."""
        now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        try:
            r_fd = _open_file(self.manifest_path, SSOT_DIR, os.O_RDONLY)
        except FileNotFoundError:
            manifest = {
                "schema_version": SCHEMA_VERSION, "session_id": self.session_id,
                "provider": self.provider, "account": self.account,
                "created_at": now, "status": "active"
            }
        except OSError as e:
            if e.errno == getattr(os, "ELOOP", 40):
                raise ValueError(f"Symlink detected in target path: {self.manifest_path}") from e
            raise ValueError(f"Failed secure read for {self.manifest_path}: {e}") from e
        else:
            with os.fdopen(r_fd, "r", encoding="utf-8") as stream:
                manifest = json.load(stream)
        manifest["updated_at"] = now
        if title: manifest["title"] = title
        if native_refs: manifest["native_refs"] = native_refs
        if capabilities: manifest["capabilities_used"] = capabilities
        _secure_write(self.manifest_path, json.dumps(manifest, indent=2) + "\n", base_dir=SSOT_DIR)

    def append_message(self, role: str, content: str, message_id: Optional[str] = None,
                       timestamp_source: str = "observed", provider_message_id: Optional[str] = None):
        msg = {
            "message_id": message_id or str(uuid.uuid4()), "role": role,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "timestamp_source": timestamp_source, "content": content,
            "provider_message_id": provider_message_id,
            "provenance": {"source": self.provider, "import_batch": None}
        }
        _secure_write(self.messages_path, json.dumps(msg) + "\n", append=True, base_dir=SSOT_DIR)

    def emit_event(self, event_type: str, source: str = "archwiz", correlation_id: Optional[str] = None, payload: Dict[str, Any] = None):
        event = {
            "event_id": str(uuid.uuid4()), "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "type": event_type, "provider": self.provider, "account": self.account,
            "session_id": self.session_id, "correlation_id": correlation_id, "source": source,
            "payload": payload, "schema_version": SCHEMA_VERSION
        }
        _secure_write(self.events_path, json.dumps(event) + "\n", append=True, base_dir=SSOT_DIR)


def save_session_ssot(provider: str, session_id: str, messages: List[Dict[str, Any]], title: Optional[str] = None):
    """Convenience helper to save a full session state to SSOT."""
    ssot = SessionSSOT(provider, session_id)
    ssot.upsert_manifest(title=title)
    for msg in messages:
        ssot.append_message(role=msg.get("role", "unknown"), content=msg.get("content", ""),
                            message_id=msg.get("message_id"), provider_message_id=msg.get("provider_message_id"))
    ssot.emit_event("SessionSaved", source="archwiz")
