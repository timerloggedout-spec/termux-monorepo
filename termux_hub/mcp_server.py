"""Governed MCP server for the Termux/Android hub.

The server deliberately exposes a small allowlisted surface. It does not provide
an arbitrary shell tool, public HTTP listener, credential store, or OTP access.
"""

from __future__ import annotations

import json
import os
import platform
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from mcp.server import MCPServer

mcp = MCPServer(
    "termux-hub",
    instructions=(
        "Governed Android/Termux execution surface. Shell access is allowlisted; "
        "privileged Android access requires Shizuku/rish and remains allowlisted."
    ),
    version="0.1.0",
)

REPO = Path(
    os.environ.get("TERMUX_HUB_REPOSITORY", str(Path.home() / "termux-monorepo"))
).expanduser().resolve()
MAX_OUTPUT = 12000


def _run(argv: Sequence[str], *, timeout: int = 15, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        list(argv),
        cwd=str(cwd or REPO),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        shell=False,
    )
    output = (completed.stdout + ("\n" + completed.stderr if completed.stderr else "")).strip()
    return json.dumps(
        {
            "ok": completed.returncode == 0,
            "exit_code": completed.returncode,
            "output": output[:MAX_OUTPUT],
        }
    )


SHELL_RULES: dict[str, set[tuple[str, ...]]] = {
    "id": {()},
    "whoami": {()},
    "pwd": {()},
    "uname": {(), ("-a",)},
    "git": {
        ("status",),
        ("status", "--short"),
        ("rev-parse", "--show-toplevel"),
        ("rev-parse", "HEAD"),
        ("log", "-1", "--oneline"),
        ("diff", "--check"),
    },
    "python3": {("--version",)},
}

RISH_RULES: dict[str, set[tuple[str, ...]]] = {
    "id": {()},
    "getprop": {
        (),
        ("ro.product.model",),
        ("ro.build.version.release",),
        ("ro.build.version.sdk",),
    },
    "pm": {("list", "packages")},
    "settings": {("get", "secure", "enabled_accessibility_services")},
}


def _allowed(argv: Sequence[str], rules: dict[str, set[tuple[str, ...]]]) -> bool:
    return bool(argv) and argv[0] in rules and tuple(argv[1:]) in rules[argv[0]]


@mcp.tool()
def health() -> str:
    """Read-only hub readiness: Termux, Tailscale, SSH, Termux:API, and Shizuku."""
    result: dict[str, object] = {
        "python": platform.python_version(),
        "machine": platform.machine(),
        "repository": str(REPO),
        "tailscale": False,
        "sshd": False,
        "termux_api": False,
        "shizuku_rish": False,
        "shizuku_package": False,
    }

    if shutil.which("tailscale"):
        result["tailscale"] = True
        try:
            result["tailscale_ipv4"] = subprocess.check_output(
                ["tailscale", "ip", "-4"], text=True, timeout=5
            ).strip()
        except Exception:
            result["tailscale_ipv4"] = None

    if shutil.which("pgrep") and shutil.which("sshd"):
        result["sshd"] = subprocess.run(
            ["pgrep", "-x", "sshd"], capture_output=True
        ).returncode == 0

    result["termux_api"] = shutil.which("termux-battery-status") is not None

    if shutil.which("rish"):
        result["shizuku_rish"] = subprocess.run(
            ["rish", "-c", "id"], capture_output=True
        ).returncode == 0
        if result["shizuku_rish"]:
            result["shizuku_package"] = subprocess.run(
                ["rish", "-c", "pm path moe.shizuku.privileged.api"],
                capture_output=True,
            ).returncode == 0

    result["ready"] = bool(result["tailscale"] and result["sshd"])
    return json.dumps(result, sort_keys=True)


@mcp.tool()
def shell_readonly(argv: list[str]) -> str:
    """Run one allowlisted read-only Termux command without a shell."""
    if not _allowed(argv, SHELL_RULES):
        raise ValueError("command is outside the Termux hub read-only allowlist")
    return _run(argv, cwd=REPO)


@mcp.tool()
def android_battery() -> str:
    """Read Android battery state through Termux:API."""
    return _run(["termux-battery-status"])


@mcp.tool()
def android_wifi() -> str:
    """Read Android Wi-Fi connection state through Termux:API."""
    return _run(["termux-wifi-connectioninfo"])


@mcp.tool()
def android_device_info() -> str:
    """Read non-sensitive Android device properties."""
    properties = {}
    for key in (
        "ro.product.model",
        "ro.product.manufacturer",
        "ro.build.version.release",
        "ro.build.version.sdk",
    ):
        try:
            properties[key] = subprocess.check_output(
                ["getprop", key], text=True, timeout=5
            ).strip()
        except Exception:
            properties[key] = None
    return json.dumps(properties, sort_keys=True)


@mcp.tool()
def shizuku_readonly(argv: list[str]) -> str:
    """Run one allowlisted read-only Android command through Shizuku/rish."""
    if not shutil.which("rish"):
        raise RuntimeError("rish/Shizuku is not installed")
    if not _allowed(argv, RISH_RULES):
        raise ValueError("command is outside the Shizuku read-only allowlist")
    command = " ".join(shlex.quote(item) for item in argv)
    return _run(["rish", "-c", command])


if __name__ == "__main__":
    mcp.run(transport=os.environ.get("TERMUX_HUB_TRANSPORT", "stdio"))
