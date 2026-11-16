"""Names-only connector readiness. No tokens, no message bodies."""
from __future__ import annotations

# Probed 2026-10-11 by the operator session. Non-gate surfaces stay non-gate.
CONNECTORS: tuple[dict[str, str], ...] = (
    {
        "name": "github",
        "state": "LIVE",
        "lane": "CANDIDATE",
        "note": "authenticated as timerloggedout-spec; repo termux-monorepo readable",
    },
    {
        "name": "linear",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "team TER Termux-monorepo_linear answers; not a promote gate",
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
        "note": "auth ok; GitHub/Priority/termux-monorepo label present; mail is not a gate",
    },
    {
        "name": "notion",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
    {
        "name": "google-drive",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
    {
        "name": "grafana",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
    {
        "name": "mixpanel",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
    {
        "name": "stepie",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
    {
        "name": "gamma",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
    {
        "name": "figma",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
    {
        "name": "bigquery",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "connector listed; no read this cut",
    },
)


def connector_report() -> dict[str, object]:
    return {
        "writes": False,
        "secrets": False,
        "count": len(CONNECTORS),
        "connectors": list(CONNECTORS),
    }
