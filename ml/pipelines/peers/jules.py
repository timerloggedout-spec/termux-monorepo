"""Jules-family minesweeper. EXTRACT; do not overwrite."""
from __future__ import annotations

from typing import Any

JULES_LOGIN = "google-labs-jules[bot]"


def is_jules(pr: dict[str, Any]) -> bool:
    user = pr.get("user")
    login = user.get("login") if isinstance(user, dict) else (user or "")
    return str(login) == JULES_LOGIN or str(pr.get("head_ref") or "").startswith("jules-")
