"""Issue #175 operator matrix schema."""
from __future__ import annotations

REQUIRED_ROOT = {"version", "issue", "updated_at", "master_sha", "tiers", "operator_rules"}
REQUIRED_ITEM = {"id", "title", "status", "priority"}
PRIORITIES = {"P0", "P1", "P2", "P3"}
STATUSES = {
    "LIVE", "GREEN", "MERGED", "OPEN", "HOT", "DIRTY", "HOLD",
    "PARTIAL", "TODO", "MONITOR", "UNKNOWN",
}
