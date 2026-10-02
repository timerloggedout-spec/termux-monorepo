"""Scoped GitHub broker. Agent never sees GH_TOKEN.
Admin mode (GH_BROKER_ALLOW_ADMIN=1) lifts the forbidden-endpoint filter
and audit-logs every admin call. Default = safe."""
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ALLOWED = {
    "pr":    {"list", "view", "create", "diff", "checks", "comment", "status",
              "edit", "ready", "merge", "close", "reopen", "review"},
    "issue": {"list", "view", "create", "comment", "status", "edit",
              "close", "reopen", "delete", "lock", "unlock"},
    "run":   {"list", "view", "watch", "download", "rerun", "cancel"},
    "repo":  {"view", "clone", "list", "create", "delete", "edit",
              "fork", "rename", "archive"},
    "release": {"list", "view", "create", "delete", "edit", "upload"},
    "workflow": {"list", "view", "run", "enable", "disable"},
    "secret": {"list", "set", "delete"},
    "variable": {"list", "set", "delete"},
    "api":   None,   # endpoint filter applies (unless admin)
}

# Still blocked even in admin mode — these are the "you will regret this" ops
ALWAYS_FORBIDDEN = (
    "/installation",
    "/app/installations",
    "/enterprises/",
)

# Endpoints matching these are ALLOWED even though they contain forbidden substrings.
# Read-only lists only — no values, no writes.
SAFE_READ_PATHS = (
    "/environments/",      # GET .../environments/{env}/secrets (names only)
    "/environments",       # GET .../environments (list)
)

FORBIDDEN_API_SUBSTRINGS = (
    "DELETE", "/secrets", "/keys", "/collaborators",
    "/actions/secrets", "/actions/permissions",
    "/hooks", "/deploy_keys", "/invitations",
)
FORBIDDEN_API_METHODS = ("-X DELETE", "--method DELETE", "-XDELETE")

AUDIT_LOG = Path.home() / ".deepcli" / "logs" / "admin_gh.jsonl"


class GhBroker:
    def __init__(self, host: str = None):
        self.host = host or os.environ.get("GH_BROKER_HOST", "github.com")
        self.token = self._load_token()
        self.admin = os.environ.get("GH_BROKER_ALLOW_ADMIN", "").lower() in (
            "1", "true", "yes", "on"
        )

    def _load_token(self) -> str:
        tok = os.environ.get("GH_BROKER_TOKEN")
        if tok:
            return tok.strip()
        if yaml is None:
            raise RuntimeError("pyyaml required to read hosts.yml; pip install pyyaml")
        cfg = Path.home() / ".config" / "gh" / "hosts.yml"
        if not cfg.exists():
            raise RuntimeError(f"{cfg} not found; run `gh auth login`")
        data = yaml.safe_load(cfg.read_text())
        host_cfg = data.get(self.host) or {}
        tok = host_cfg.get("oauth_token")
        if not tok:
            raise RuntimeError(f"no oauth_token for {self.host} in hosts.yml")
        return tok.strip()

    def _check(self, argv):
        if not argv or not isinstance(argv, list):
            raise PermissionError("argv must be a non-empty list")
        if argv[0] not in ALLOWED:
            raise PermissionError(f"gh {argv[0]}: not in allowlist")
        allowed = ALLOWED[argv[0]]
        if allowed is not None:
            sub = argv[1] if len(argv) > 1 else ""
            if sub not in allowed:
                raise PermissionError(f"gh {argv[0]} {sub}: not in allowlist")
        if argv[0] == "api":
            joined = " ".join(argv)
            # allow safe reads first
            safe_read = any(sp in joined for sp in SAFE_READ_PATHS) and                         "-X DELETE" not in joined and                         "-X PUT" not in joined and                         "-X PATCH" not in joined and                         "-X POST" not in joined and                         "--method DELETE" not in joined
            for bad in ALWAYS_FORBIDDEN:
                if bad in joined:
                    raise PermissionError(f"gh api: '{bad}' always blocked")
            if not self.admin:
                if not safe_read:
                    for bad in FORBIDDEN_API_SUBSTRINGS:
                        if bad in joined:
                            raise PermissionError(f"gh api: '{bad}' blocked")
                for bad in FORBIDDEN_API_METHODS:
                    if bad in joined:
                        raise PermissionError(f"gh api: method DELETE blocked")

    def _audit(self, argv, result):
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "argv": argv,
            "cwd": os.getcwd(),
            "rc": result.returncode,
            "stdout_bytes": len(result.stdout or ""),
            "stderr_head": (result.stderr or "")[:200],
        }
        with AUDIT_LOG.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        try:
            AUDIT_LOG.chmod(0o600)
        except Exception:
            pass

    def run(self, argv, cwd=None, timeout=120, capture=True):
        self._check(argv)
        admin_call = self.admin and argv[0] == "api"
        t0 = time.time()
        env = {k: v for k, v in os.environ.items() if k != "GH_TOKEN"}
        env["GH_TOKEN"] = self.token
        env["GH_HOST"] = self.host
        env["GH_NO_UPDATE_NOTIFIER"] = "1"
        result = subprocess.run(
            ["gh", *argv],
            cwd=cwd, env=env,
            capture_output=capture, text=True, timeout=timeout,
        )
        if admin_call or result.returncode != 0:
            self._audit(argv, result)
        return result


if __name__ == "__main__":
    import sys
    b = GhBroker()
    mode = "ADMIN" if b.admin else "SAFE"
    print(f"[broker mode: {mode}]", file=sys.stderr)
    r = b.run(sys.argv[1:])
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    sys.exit(r.returncode)
