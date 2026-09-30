"""Concurrent agent registry. Stay on product work; do not idle-park."""
from __future__ import annotations

from typing import Any

PEERS = {
    "jules": "google-labs-jules[bot]",
    "coderabbit": "coderabbitai[bot]",
    "devin": "devin-ai-integration[bot]",
    "qodo": "qodo-ai[bot]",
    "copilot": "copilot-swe-agent[bot]",
    "actions": "github-actions[bot]",
    "grok": "timerloggedout-spec",
}


def peer_of(login: str) -> str | None:
    login = str(login or "")
    for name, value in PEERS.items():
        if login == value or login.endswith(name):
            return name
    if login.endswith("[bot]"):
        return "bot"
    return None


def active_peers(prs: list[dict[str, Any]]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for pr in prs:
        user = pr.get("user")
        login = user.get("login") if isinstance(user, dict) else (user or pr.get("author") or "")
        name = peer_of(str(login)) or "human"
        out.setdefault(name, []).append(int(pr["number"]))
    return out
