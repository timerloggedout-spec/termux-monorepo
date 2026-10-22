import json
import time
import os

TELEMETRY_LOG = "agent_telemetry_stream.json"

class TermuxTelemetryLogger:
    @staticmethod
    def notify(level, agent_id, message, target_file=None, attempt=None):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        colors = {"INFO": "\033[94m[INFO]\033[0m", "SUCCESS": "\033[92m[SUCCESS]\033[0m",
                  "RETRY": "\033[93m[RETRY]\033[0m", "CRITICAL": "\033[91m[CRITICAL]\033[0m"}
        color_tag = colors.get(level, f"[{level}]")
        context_str = f" ({target_file} | Try #{attempt})" if target_file and attempt else ""
        print(f"{timestamp} {color_tag} [{agent_id}]{context_str}: {message}")
        log_entry = {"timestamp": timestamp, "level": level, "agent": agent_id,
                     "target": target_file, "attempt": attempt, "message": message}
        # Security: Reject symlinks and open with atomic 0o600 permissions to avoid umask exposure
        if os.path.islink(TELEMETRY_LOG):
            return
        try:
            fd = os.open(TELEMETRY_LOG, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        except OSError:
            return
        try:
            if os.path.islink(TELEMETRY_LOG):
                os.close(fd)
                return
            with os.fdopen(fd, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass
        if not os.path.islink(TELEMETRY_LOG):
            try:
                os.chmod(TELEMETRY_LOG, 0o600)
            except Exception:
                pass

# In a monorepo checkout there is one telemetry implementation for legacy agent
# imports and root adapters. Preserve the existing standalone implementation
# above when the optional monorepo integration is absent.
from pathlib import Path as _Path
import importlib.util as _import_util
import sys as _sys

_shared_path = _Path(__file__).resolve().parents[2] / "src" / "telemetry.py"
if _shared_path.is_file() and (_shared_path.parent / "swarms_adapter.py").is_file():
    _shared_name = "_termux_shared_telemetry"
    _shared = _sys.modules.get(_shared_name)
    if _shared is None:
        _spec = _import_util.spec_from_file_location(_shared_name, _shared_path)
        _shared = _import_util.module_from_spec(_spec)
        _sys.modules[_shared_name] = _shared
        try:
            _spec.loader.exec_module(_shared)
        except BaseException:
            _sys.modules.pop(_shared_name, None)
            raise
    TermuxTelemetryLogger = _shared.TermuxTelemetryLogger
    _sys.modules[__name__] = _shared
