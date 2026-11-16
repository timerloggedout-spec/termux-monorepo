#!/usr/bin/env python3
"""queuectl: producer / inspection CLI for the P1 device pull-queue Worker.

Stdlib only (same discipline as scripts/quota_poll.py). The Worker base URL
and bearer token come from the environment:

    DEVICE_QUEUE_URL    e.g. https://tmx-device-queue.<account>.workers.dev
    DEVICE_QUEUE_TOKEN  one of the producer token values (never printed)

Commands:
    queuectl.py enqueue --kind git-sync [--role engineer]
                        [--payload '<json>' | --payload @file.json]
                        [--dedupe <key>] [--ttl-hours 6] [--id <task-id>]
    queuectl.py show <task-id>
    queuectl.py health

The token is never printed, logged, or placed in a URL. Design:
docs/ops/P1-PULL-QUEUE-SPEC.md; operations: docs/ops/DEVICE-PULL-QUEUE.md.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "termux-monorepo-queuectl"}


def _config():
    url = os.environ.get("DEVICE_QUEUE_URL", "").rstrip("/")
    token = os.environ.get("DEVICE_QUEUE_TOKEN", "")
    if not url:
        print("error: DEVICE_QUEUE_URL is not set", file=sys.stderr)
        sys.exit(2)
    return url, token


def _request(method, path, token=None, body=None):
    url, _ = _config()
    headers = {**UA, "Accept": "application/json"}
    data = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8")
            return resp.status, (json.loads(text) if text else None)
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(text) if text else None
        except json.JSONDecodeError:
            payload = None
        return e.code, payload
    except urllib.error.URLError as e:
        print(f"error: request failed: {e.reason}", file=sys.stderr)
        sys.exit(1)


def _emit(status, payload):
    if payload is not None:
        print(json.dumps(payload, indent=2, sort_keys=True))
    if status >= 400:
        print(f"error: HTTP {status}", file=sys.stderr)
        return 1
    return 0


def _load_payload(raw):
    if raw is None:
        return None
    if raw.startswith("@"):
        with open(raw[1:], "r", encoding="utf-8") as fh:
            raw = fh.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw  # plain string payload


def cmd_enqueue(args):
    _, token = _config()
    if not token:
        print("error: DEVICE_QUEUE_TOKEN is not set", file=sys.stderr)
        return 2
    body = {"kind": args.kind, "role": args.role}
    payload = _load_payload(args.payload)
    if payload is not None:
        body["payload"] = payload
    if args.dedupe:
        body["dedupe_key"] = args.dedupe
    if args.id:
        body["id"] = args.id
    expires = datetime.now(timezone.utc) + timedelta(hours=args.ttl_hours)
    body["expires_at"] = expires.isoformat().replace("+00:00", "Z")
    status, resp = _request("POST", "/tasks", token=token, body=body)
    return _emit(status, resp)


def cmd_show(args):
    _, token = _config()
    if not token:
        print("error: DEVICE_QUEUE_TOKEN is not set", file=sys.stderr)
        return 2
    status, resp = _request("GET", f"/tasks/{args.task_id}", token=token)
    return _emit(status, resp)


def cmd_health(args):
    status, resp = _request("GET", "/health")
    return _emit(status, resp)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="queuectl",
        description="Producer/inspection CLI for the P1 device pull-queue Worker.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_enqueue = sub.add_parser("enqueue", help="enqueue a task for a device role")
    p_enqueue.add_argument("--kind", required=True,
                           help="task kind (allowlist: deepagent-run, git-commit-push, "
                                "git-sync, shell-allowlisted, heartbeat-only)")
    p_enqueue.add_argument("--role", default="engineer", help="device role (default: engineer)")
    p_enqueue.add_argument("--payload", default=None,
                           help="JSON payload, or @path to a file containing it")
    p_enqueue.add_argument("--dedupe", default=None, help="idempotency key")
    p_enqueue.add_argument("--ttl-hours", type=float, default=6.0,
                           help="task time-to-live in hours (default: 6)")
    p_enqueue.add_argument("--id", default=None, help="explicit task id (default: generated)")
    p_enqueue.set_defaults(func=cmd_enqueue)

    p_show = sub.add_parser("show", help="show one task row, including any receipt")
    p_show.add_argument("task_id")
    p_show.set_defaults(func=cmd_show)

    p_health = sub.add_parser("health", help="public queue health counts (no token needed)")
    p_health.set_defaults(func=cmd_health)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
