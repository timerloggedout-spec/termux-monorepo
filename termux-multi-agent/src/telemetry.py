import json
import time
import os

# Secure process umask to prevent any brief world-readable windows
try:
    os.umask(0o077)
except Exception:
    pass

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

        is_new = not os.path.exists(TELEMETRY_LOG)
        with open(TELEMETRY_LOG, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        if is_new:
            try:
                os.chmod(TELEMETRY_LOG, 0o600)
            except Exception:
                pass