"""Append-only, privacy-bounded telemetry event logger."""
import json
import os
import re
import sys
import time

TELEMETRY_LOG = os.path.abspath(os.environ.get("TERMUX_TELEMETRY_LOG", "agent_telemetry_stream.json"))
_ALLOWED = {"run_id", "job_id", "request_id", "attempt_id", "parent_id",
            "adapter", "source_revision", "model", "provider", "outcome", "event"}
# Correlation is metadata, not a place for prompts, credentials, or arbitrary output.
_SAFE_VALUE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,159}$")
_ENUMS = {
    "adapter": {"swarms", "swarms-rs", "advanced-research", "hub-direct"},
    "outcome": {"success", "failure", "deny", "cancel", "UNKNOWN", "DENIED", "CANCELLED"},
    "event": {"request", "response", "error", "denied", "cancelled", "completed", "failed",
              "admission_denied", "admission_reserved", "execution_complete", "execution_failed", "execution_cancelled"},
}


def sanitize_correlation(context):
    """Return only allowlisted, short, printable metadata values."""
    if not isinstance(context, dict):
        return {}
    safe = {}
    for key in _ALLOWED:
        value = context.get(key)
        if (isinstance(value, str) and _SAFE_VALUE.fullmatch(value)
                and (key not in _ENUMS or value in _ENUMS[key])):
            safe[key] = value
    return safe


class TermuxTelemetryLogger:
    @staticmethod
    def configure(destination):
        """Set the operator-owned destination on this shared logger implementation."""
        global TELEMETRY_LOG
        TELEMETRY_LOG = os.path.abspath(os.fspath(destination))

    @staticmethod
    def notify(level, agent_id, message, target_file=None, attempt=None, *, context=None):
        # Messages are for static operational text only. Callers must not put upstream
        # exceptions, prompts, or response bodies here.
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        colors = {"INFO": "\033[94m[INFO]\033[0m", "SUCCESS": "\033[92m[SUCCESS]\033[0m",
                  "RETRY": "\033[93m[RETRY]\033[0m", "CRITICAL": "\033[91m[CRITICAL]\033[0m"}
        color_tag = colors.get(level, f"[{level}]")
        context_str = f" ({target_file} | Try #{attempt})" if target_file and attempt else ""
        print(f"{timestamp} {color_tag} [{agent_id}]{context_str}: {message}", file=sys.stderr)
        log_entry = {"timestamp": timestamp, "level": level, "agent": agent_id,
                     "target": target_file, "attempt": attempt, "message": message}
        safe = sanitize_correlation(context)
        if safe:
            log_entry["correlation"] = safe
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
