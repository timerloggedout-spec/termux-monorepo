"""Names-only connector readiness for 2026-10-19. No tokens, no message bodies."""
from __future__ import annotations

# Probed this cut. Non-gate surfaces stay non-gate. Counts and titles only.
CONNECTORS: tuple[dict[str, str], ...] = (
    {
        "name": "github",
        "state": "LIVE",
        "lane": "CANDIDATE",
        "note": "authenticated as timerloggedout-spec; 173 open PRs readable",
    },
    {
        "name": "linear",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "TER issues readable; TER-21 still Todo; not a promote gate",
    },
    {
        "name": "vercel",
        "state": "LIVE",
        "lane": "SUPERSEDE",
        "note": "project named termux-monorepo still listed; hobby rate-limit remains NON-GATE",
    },
    {
        "name": "gmail",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "label GitHub/Priority/termux-monorepo present; message bodies not read",
    },
    {
        "name": "notion",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "page title termux-monorepo Production Cockpit still searchable; content not copied",
    },
    {
        "name": "google-drive",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "recent title matches include Termux telemetry images; bytes not read",
    },
    {
        "name": "grafana",
        "state": "DEGRADED",
        "lane": "NEED_EVIDENCE",
        "note": "list_datasources returned HTTP 424 stack paused; not a gate",
    },
    {
        "name": "mixpanel",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "Get-Projects returned 1 project; token tool not called",
    },
    {
        "name": "stepie",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "12 in-progress goals; primary title Harden tunnel canary skips; open tasks still name older SHAs",
    },
    {
        "name": "gamma",
        "state": "EMPTY",
        "lane": "NEED_EVIDENCE",
        "note": "search q=termux and title query termux returned 0 gammas; analytics not called",
    },
    {
        "name": "figma",
        "state": "AUTHENTICATED",
        "lane": "NEED_EVIDENCE",
        "note": "whoami returned one starter plan with a View seat; no file opened",
    },
    {
        "name": "bigquery",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "list_dataset_ids requires projectId; none recorded in-repo; id was not invented",
    },
)


def connector_report() -> dict[str, object]:
    return {
        "writes": False,
        "secrets": False,
        "probed_on": "2026-10-19",
        "count": len(CONNECTORS),
        "connectors": list(CONNECTORS),
    }
