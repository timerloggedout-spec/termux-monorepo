#!/usr/bin/env python3
"""Read-only controller access diagnosis for the pinned secondary; never runs AGY.

Only the fixed identity handshake may retry. GitHub/Git checks run once, and a
lost response is unknown, never permission to replay a task or remote command.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import ipaddress
import json
import os
import signal
import subprocess
import time

ALIAS = "termux-device2"
HOST_KEY_ALIAS = "b160v-1"
REPOSITORY = "https://github.com/timerloggedout-spec/termux-monorepo.git"
IDENTITY = r'''set -eu
marker="$HOME/.local/share/agy-1497-secondary/worktree/.agy-secondary-id"
[ -f "$marker" ] && [ ! -L "$marker" ] || exit 21
[ "$(cat "$marker")" = tmx-node-55619bd5 ] || exit 21
[ "$(whoami)" = u0_a243 ] && [ "$(getprop ro.product.model)" = B160V ] || exit 21
printf '%s\n' ACCESS_IDENTITY_OK
'''
# No checkout/fetch, credential setup, settings read, service action, or task.
# Explicit remote deadlines also bound work if the controller disconnects.
GITHUB_GIT = IDENTITY + r'''
command -v timeout >/dev/null 2>&1 || { printf '%s\n' DEADLINE_UNAVAILABLE; exit 22; }
export GH_PROMPT_DISABLED=1 GIT_TERMINAL_PROMPT=0 GIT_OPTIONAL_LOCKS=0
export GIT_ASKPASS=/bin/false SSH_ASKPASS=/bin/false GCM_INTERACTIVE=never
# Ignore Git config/credential helpers, URL rewrites, hooks and repository state.
# This verifies public HTTPS Git connectivity, NOT private-repo/push authorization.
unset GIT_CONFIG_PARAMETERS GIT_CONFIG GIT_DIR GIT_WORK_TREE GIT_COMMON_DIR
export GIT_CONFIG_COUNT=0 GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_GLOBAL=/dev/null
probe() {
    label=$1; seconds=$2; binary=$3
    shift 3
    if ! command -v "$binary" >/dev/null 2>&1; then
        printf '%s_UNAVAILABLE\n' "$label"
    elif timeout -k 2 "$seconds" "$binary" "$@" >/dev/null 2>&1; then
        printf '%s_OK\n' "$label"
    else
        code=$?
        case "$code" in
            124|137) printf '%s_DEADLINE\n' "$label" ;;
            *) printf '%s_UNVERIFIED\n' "$label" ;;
        esac
    fi
}
probe GH_AUTH 10 gh auth status --active --hostname github.com
probe GH_API 10 gh api --hostname github.com user
probe GIT_REMOTE 15 git -C / -c credential.helper= -c credential.interactive=false -c core.hooksPath=/dev/null -c http.followRedirects=false ls-remote --exit-code https://github.com/timerloggedout-spec/termux-monorepo.git HEAD
printf '%s\n' ACCESS_CHECKS_DONE
'''

SSH_OPTIONS = [
    "-T", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
    "-o", "UpdateHostKeys=no", "-o", "AddKeysToAgent=no",
    "-o", "ForwardAgent=no", "-o", "ForwardX11=no",
    "-o", "ClearAllForwardings=yes", "-o", "PermitLocalCommand=no",
    "-o", "ControlMaster=no", "-o", "ControlPath=none",
    "-o", "ControlPersist=no", "-o", "ConnectionAttempts=1",
    "-o", "ConnectTimeout=8", "-o", "ServerAliveInterval=5",
    "-o", "ServerAliveCountMax=2", "-o", "RequestTTY=no",
]


@dataclass
class Result:
    code: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


def run(command: list[str], timeout: int) -> Result:
    """Bound controller and proxy descendants, without logging raw diagnostics."""
    env = dict(os.environ, LC_ALL="C")
    try:
        with subprocess.Popen(command, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, errors="replace", env=env,
                              start_new_session=True) as process:
            try:
                out, err = process.communicate(timeout=timeout)
                return Result(process.returncode, out, err)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                out, err = process.communicate()
                return Result(124, out, err, True)
    except OSError:
        return Result(127)


def ssh_command(remote: str) -> list[str]:
    return ["ssh", *SSH_OPTIONS, ALIAS, remote]


def effective_config(runner=run) -> dict[str, str] | None:
    result = runner(["ssh", "-G", *SSH_OPTIONS, ALIAS], 5)
    if result.code:
        return None
    config = {}
    for line in result.stdout.splitlines():
        key, _, value = line.partition(" ")
        config[key] = value.strip()
    try:
        address = ipaddress.ip_address(config.get("hostname", ""))
    except ValueError:
        return None
    # This tool is deliberately not a generic SSH wrapper. Require an existing
    # secondary pin file and alias; never learn/replace keys or choose a peer.
    known_hosts = config.get("userknownhostsfile", "").split()
    if not (address in ipaddress.ip_network("100.64.0.0/10")
            and config.get("hostkeyalias") == HOST_KEY_ALIAS
            and config.get("user") == "u0_a243"
            and config.get("port") == "8022"
            and len(known_hosts) == 1
            and os.path.basename(known_hosts[0]) == "known_hosts.device2"
            and os.path.isfile(os.path.expanduser(known_hosts[0]))
            and config.get("stricthostkeychecking") in ("yes", "true")
            and config.get("proxycommand", "none") != "none"):
        return None
    return config


def tailnet_status(host: str, socket: str | None, runner=run) -> dict:
    command = ["tailscale"]
    if socket:
        command.append("--socket=" + socket)
    result = runner([*command, "status", "--json"], 5)
    if result.code:
        return {"backend": "unknown", "peer": "unknown", "ssh_ready": False}
    try:
        data = json.loads(result.stdout)
        backend = "running" if data.get("BackendState") == "Running" else "not_running"
        peers = [p for p in data.get("Peer", {}).values()
                 if host in p.get("TailscaleIPs", [])]
        peer = "unknown"
        if len(peers) == 1 and isinstance(peers[0].get("Online"), bool):
            peer = "online" if peers[0]["Online"] else "offline"
        return {"backend": backend, "peer": peer, "ssh_ready": False}
    except (ValueError, TypeError, AttributeError):
        return {"backend": "unknown", "peer": "unknown", "ssh_ready": False}


def failure(result: Result) -> tuple[str, bool]:
    """Retry only known establishment failures, never arbitrary exit 255."""
    error = result.stderr.lower()
    if any(s in error for s in ("host key verification failed", "remote host identification has changed",
                                "no ed25519 host key is known", "offending ")):
        return "host_key_rejected", False
    if any(s in error for s in ("permission denied", "authentication failed", "too many authentication failures")):
        return "authentication_rejected", False
    if result.code == 21:
        return "secondary_identity_rejected", False
    if result.stdout:
        return "ssh_outcome_unknown", False
    transient = ("connection refused", "connection timed out", "no route to host",
                 "network is unreachable", "kex_exchange_identification: connection closed",
                 "kex_exchange_identification: read: connection reset by peer")
    if result.code == 255 and any(s in error for s in transient):
        return "connection_establishment_failed", True
    # A whole-process deadline can include remote command execution: ambiguous,
    # not positive evidence of an establishment failure, so do not retry it.
    return ("deadline_unknown" if result.timed_out else "ssh_outcome_unknown"), False


def preflight(attempts: int = 3, socket: str | None = None, runner=run, sleep=time.sleep) -> tuple[dict, int]:
    if not 1 <= attempts <= 3:
        raise ValueError("attempts must be between 1 and 3")
    report = {"schema_version": 1, "alias": ALIAS, "ready": False,
              "tailscale": {"backend": "unknown", "peer": "unknown", "ssh_ready": False},
              "ssh": {"listener": "unknown", "authentication": "unknown", "attempts": 0},
              "github_cli_auth": "not_checked", "github_api": "not_checked",
              "git_remote": "not_checked", "tasks_launched": 0,
              "replay_permitted": False}
    config = effective_config(runner)
    if config is None:
        report["reason"] = "pinned_secondary_config_required"
        return report, 10
    report["tailscale"] = tailnet_status(config["hostname"], socket, runner)
    for attempt in range(1, attempts + 1):
        result = runner(ssh_command(IDENTITY), 15)
        report["ssh"]["attempts"] = attempt
        if result.code == 0 and result.stdout.splitlines() == ["ACCESS_IDENTITY_OK"]:
            report["ssh"].update(listener="reachable", authentication="verified")
            break
        reason, retry = failure(result)
        report["reason"] = reason
        if reason == "authentication_rejected":
            report["ssh"].update(listener="reachable", authentication="rejected")
        if reason == "host_key_rejected":
            report["ssh"]["listener"] = "reachable_untrusted"
        if reason == "secondary_identity_rejected":
            report["ssh"].update(listener="reachable", authentication="identity_rejected")
        if "connection refused" in result.stderr.lower():
            report["ssh"]["listener"] = "refused"
        if not retry or attempt == attempts:
            return report, 20
        sleep(attempt)  # one and two seconds; no unbounded retry loop
    report.pop("reason", None)
    # Deliberately separate from the retry loop. If SSH drops here, even these
    # read-only commands are NOT replayed. No task command is ever accepted.
    result = runner(ssh_command(GITHUB_GIT), 45)
    lines = result.stdout.splitlines()
    suffixes = ("OK", "UNVERIFIED", "UNAVAILABLE", "DEADLINE")
    valid = (len(lines) == 5 and lines[0] == "ACCESS_IDENTITY_OK"
             and lines[1] in tuple("GH_AUTH_" + suffix for suffix in suffixes)
             and lines[2] in tuple("GH_API_" + suffix for suffix in suffixes)
             and lines[3] in tuple("GIT_REMOTE_" + suffix for suffix in suffixes)
             and lines[4] == "ACCESS_CHECKS_DONE")
    if result.code != 0 or not valid:
        report.update(github_cli_auth="unknown", github_api="unknown", git_remote="unknown",
                      reason="github_git_outcome_unknown_no_replay")
        return report, 30
    for field, prefix in (("github_cli_auth", "GH_AUTH"), ("github_api", "GH_API"),
                          ("git_remote", "GIT_REMOTE")):
        marker = next(line for line in lines if line.startswith(prefix + "_"))
        status = marker[len(prefix) + 1:]
        report[field] = {"OK": "verified", "UNVERIFIED": "not_verified",
                         "UNAVAILABLE": "unavailable", "DEADLINE": "deadline_unknown"}[status]
    report["ready"] = all(report[k] == "verified" for k in ("github_cli_auth", "github_api", "git_remote"))
    if not report["ready"]:
        report["reason"] = "github_git_checks_not_verified"
    return report, 0 if report["ready"] else 31


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempts", type=int, choices=range(1, 4), default=3,
                        help="Total fixed SSH handshake attempts, at most three")
    parser.add_argument("--tailscale-socket", help="Existing local userspace daemon socket; no configuration changes")
    args = parser.parse_args(argv)
    report, code = preflight(args.attempts, args.tailscale_socket)
    print(json.dumps(report, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
