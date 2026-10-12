"""Lane rules for the 2026-10-12 cut. Vocab v2 only.

Corrects two recon09 drifts without rewriting that frozen cut:
- Jules author login is `app/google-labs-jules` on the REST list, not only `[bot]`.
- Titles containing "session note" are session pulses (generated board is SSOT).
"""
from __future__ import annotations

WHOLESALE = frozenset({432, 549, 601, 682, 724, 746, 787, 817})
STAGING = frozenset({48, 788})
MINESWEEPER_NUMBERS = frozenset({65, 140, 481, 630, 672, 680, 750, 884, 1151, 1198, 1199, 1202, 1203, 1204, 1206, 1207, 1210, 1211})
JULES_LOGINS = frozenset({"google-labs-jules[bot]", "app/google-labs-jules"})
VALID_LANES = frozenset({"EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"})
INVALID_PARKING = frozenset({"HOLD", "WAIT", "OBSERVE"})
EMOJI_PREFIXES = ("⚡", "🎨", "🛡️", "📖")
CODERABBIT_FILE_BUDGET = 100


def classify_open_pr(*, number: int, base: str, login: str, title: str, draft: bool = False) -> tuple[str, tuple[str, ...], str]:
    """Return lane, reasons, action. Never emit HOLD/WAIT/OBSERVE."""
    reasons: list[str] = []
    if draft:
        reasons.append("draft")
    if number in STAGING or base != "master":
        reasons.append(f"wrong-base:{base}")
        return "NEED_EVIDENCE", tuple(reasons), "never-retarget"
    if number in WHOLESALE or (
        title.startswith("feat(ml):") and ("keep-alive" in title or "observe-mode" in title)
    ):
        reasons.append("ml-wholesale-no-go")
        return "EXTRACT", tuple(reasons), "extract-only-keep-pipelines"
    minesweeper = (
        login in JULES_LOGINS
        or number in MINESWEEPER_NUMBERS
        or "minesweeper" in title.lower()
        or title.startswith(EMOJI_PREFIXES)
    )
    if minesweeper:
        reasons.append("minesweeper-peer")
        return "EXTRACT", tuple(reasons), "do-not-overwrite-peer"
    lowered = title.lower()
    if "session recon" in lowered or "session note" in lowered or lowered.startswith("ops: session"):
        reasons.append("session-pulse")
        return "SUPERSEDE", tuple(reasons), "supersede-generated-board-is-ssot"
    if title.startswith("feat(ml):"):
        reasons.append("ml-keep-alive-rebase")
        return "EXTRACT", tuple(reasons), "reextract-on-live-tip"
    reasons.append("dual-gate-unbound")
    return "NEED_EVIDENCE", tuple(reasons), "bind-dual-gate-on-this-sha"
