"""Lane rules shared by the frozen catalog. Vocab v2 only."""
from __future__ import annotations

WHOLESALE = frozenset({432, 549, 601, 682, 724, 746, 787, 817})
STALE_RECON = frozenset({1188})
MINESWEEPER_NUMBERS = frozenset({65, 140, 481, 630, 672, 680, 750})
JULES_LOGIN = "google-labs-jules[bot]"
CODERABBIT_FILE_BUDGET = 100
VALID_LANES = frozenset({"EXTRACT", "CANDIDATE", "NEED_EVIDENCE", "SUPERSEDE"})
INVALID_PARKING = frozenset({"HOLD", "WAIT", "OBSERVE"})


def classify_open_pr(*, number: int, base: str, login: str, title: str) -> tuple[str, tuple[str, ...], str]:
    if number in STALE_RECON:
        return "SUPERSEDE", ("stale-recon07",), "supersede-with-live-cut"
    if base != "master":
        return "NEED_EVIDENCE", (f"wrong-base:{base}",), "never-retarget"
    if number in WHOLESALE:
        return "EXTRACT", ("ml-wholesale-no-go",), "extract-only-keep-pipelines"
    if login == JULES_LOGIN or number in MINESWEEPER_NUMBERS:
        return "EXTRACT", ("minesweeper-peer",), "do-not-overwrite-peer"
    if title.startswith("feat(ml):"):
        return "EXTRACT", ("ml-keep-alive-rebase",), "reextract-on-live-tip"
    return "NEED_EVIDENCE", ("dual-gate-unbound",), "bind-dual-gate-on-this-sha"
