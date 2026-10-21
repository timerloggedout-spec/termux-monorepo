"""Lane rules for the 2026-10-11 live cut. Vocab v2 only."""
from __future__ import annotations

WHOLESALE = frozenset({432, 549, 601, 682, 724, 746, 787, 817})
STAGING = frozenset({48, 788})
MINESWEEPER_NUMBERS = frozenset({65, 140, 481, 630, 672, 680, 750, 884, 1151})
JULES_LOGIN = "google-labs-jules[bot]"
PRIORITY_NUMBERS = frozenset({67, 103, 543, 583, 714, 806, 809, 818, 963, 1057, 1073, 1080, 1102, 1103, 1104, 1201})
VALID_LANES = frozenset({"EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"})
INVALID_PARKING = frozenset({"HOLD", "WAIT", "OBSERVE"})
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
        login == JULES_LOGIN
        or number in MINESWEEPER_NUMBERS
        or "minesweeper" in title.lower()
        or title.startswith(("⚡", "🎨", "🛡️", "📖"))
    )
    if minesweeper:
        reasons.append("minesweeper-peer")
        return "EXTRACT", tuple(reasons), "do-not-overwrite-peer"
    lowered = title.lower()
    if "session recon" in lowered or lowered.startswith("ops: session"):
        reasons.append("session-pulse")
        return "SUPERSEDE", tuple(reasons), "supersede-generated-board-is-ssot"
    if title.startswith("feat(ml):"):
        reasons.append("ml-keep-alive-rebase")
        return "EXTRACT", tuple(reasons), "reextract-on-live-tip"
    reasons.append("dual-gate-unbound")
    return "NEED_EVIDENCE", tuple(reasons), "bind-dual-gate-on-this-sha"
