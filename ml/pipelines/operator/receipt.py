from __future__ import annotations

from typing import Any

from ml.pipelines.lib.clock import utc_now


def receipt(*, head_sha: str, base_sha: str, state: str, decision: str, reason: str) -> dict[str, Any]:
    return {
        "operation": "ml-keep-alive-extract",
        "repo": "timerloggedout-spec/termux-monorepo",
        "base_sha": base_sha,
        "head_sha": head_sha,
        "observed_at": utc_now(),
        "state": state,
        "outcome": state,
        "decision": decision,
        "reason": reason,
        "issue": 175,
    }
