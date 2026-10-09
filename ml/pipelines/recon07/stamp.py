"""SHA roles. Help-wanted observer tips are not promote SHAs."""
from __future__ import annotations

# Last dual-gate GREEN product commit recorded by the command center.
# Do not move this without repo-gate + termux-smoke SUCCESS on the new SHA.
PRODUCT_SHA = "8d36f149214f4a147932188bc424e7c29b8de444"

# Live master tip during this recon. help-wanted status refresh only.
OBSERVER_TIP = "9dc1e437088d2983d26043a16e608e2051f46d38"

# Writer SHA cited by docs/ops/generated/lane-matrix-status.md (2026-10-09T13:10Z).
BOARD_SHA = "cb940cc3eafc8105e913010b76757f255fa46511"

# Issue #175 body still stamps the 2026-09-29 #850 merge. Intent has drifted.
ISSUE_BODY_STAMP = "8424a50c"

VERSION = "0.7.0"
ISSUE = 175


def is_product_sha(sha: str) -> bool:
    return bool(sha) and (sha == PRODUCT_SHA or PRODUCT_SHA.startswith(sha) or sha.startswith(PRODUCT_SHA[:12]))


def is_observer_tip(sha: str) -> bool:
    return bool(sha) and (sha == OBSERVER_TIP or OBSERVER_TIP.startswith(sha) or sha.startswith(OBSERVER_TIP[:12]))


def promotable_tip(sha: str) -> bool:
    """Observer refreshes and the stale issue stamp are never promote authority."""
    if is_observer_tip(sha) or sha.startswith(ISSUE_BODY_STAMP):
        return False
    return is_product_sha(sha)


def stamp_report() -> dict[str, object]:
    return {
        "version": VERSION,
        "issue": ISSUE,
        "product_sha": PRODUCT_SHA,
        "observer_tip": OBSERVER_TIP,
        "board_sha": BOARD_SHA,
        "issue_body_stamp": ISSUE_BODY_STAMP,
        "observer_is_product": False,
        "issue_body_current": False,
        "promotable_observer_tip": promotable_tip(OBSERVER_TIP),
    }
