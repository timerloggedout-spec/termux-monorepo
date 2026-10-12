"""Names-only connector readiness for 2026-10-12. No tokens, no message bodies."""
from __future__ import annotations

# Probed this cut. Non-gate surfaces stay non-gate. Counts and titles only.
CONNECTORS: tuple[dict[str, str], ...] = (
    {
        "name": "github",
        "state": "LIVE",
        "lane": "CANDIDATE",
        "note": "authenticated as timerloggedout-spec; 211 open PRs readable",
    },
    {
        "name": "linear",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "project termux-monorepo hardening is In Progress; not a promote gate",
    },
    {
        "name": "vercel",
        "state": "LIVE",
        "lane": "SUPERSEDE",
        "note": "project termux-monorepo exists; hobby rate-limit remains NON-GATE",
    },
    {
        "name": "gmail",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "label GitHub/Priority/termux-monorepo exists; message bodies not read",
    },
    {
        "name": "notion",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "recent page titled termux-monorepo Production Cockpit; content not copied",
    },
    {
        "name": "google-drive",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "title match termux-mcp-collaborator-recovery.skill; bytes not read",
    },
    {
        "name": "grafana",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "search answered with 0 dashboards matching termux; HTTP 424 not reproduced; not a gate",
    },
    {
        "name": "mixpanel",
        "state": "SCHEMA_ONLY",
        "lane": "NEED_EVIDENCE",
        "note": "list tools require project_id; id was not invented",
    },
    {
        "name": "stepie",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "task titles name older SHAs 912ab126 and 0e1fee04; not a gate",
    },
    {
        "name": "gamma",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "no gamma id on hand; analytics not called",
    },
    {
        "name": "figma",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "no file key on hand; file tools not called",
    },
    {
        "name": "bigquery",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "no dataset-list tool resolved this cut",
    },
)


def connector_report() -> dict[str, object]:
    return {
        "writes": False,
        "secrets": False,
        "probed_on": "2026-10-12",
        "count": len(CONNECTORS),
        "connectors": list(CONNECTORS),
    }
