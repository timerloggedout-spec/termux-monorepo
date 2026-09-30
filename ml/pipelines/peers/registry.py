"""Known peer logins. Do not treat bots as idle parking."""
from __future__ import annotations

PEER_LOGINS = {
    "google-labs-jules[bot]": "jules",
    "coderabbitai[bot]": "coderabbit",
    "devin-ai-integration[bot]": "devin",
    "copilot-swe-agent[bot]": "copilot",
    "github-actions[bot]": "actions",
    "timerloggedout-spec": "operator",
}


def classify_login(login: str) -> str:
    return PEER_LOGINS.get(str(login or ""), "unknown")
