"""Names-only connector probe for 2026-10-14. No tokens, no message bodies."""
from __future__ import annotations

import json

from ml.pipelines.recon11.redact import assert_names_only

# Counts and titles only. Non-gate surfaces stay non-gate.
CONNECTORS: tuple[dict[str, str], ...] = (
    {
        "name": "github",
        "state": "LIVE",
        "lane": "CANDIDATE",
        "note": "authenticated as timerloggedout-spec; master tip 3e64bc65; recent master workflows success",
    },
    {
        "name": "linear",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "TER team answered; sampled issues are Done; not a promote gate",
    },
    {
        "name": "vercel",
        "state": "LIVE",
        "lane": "SUPERSEDE",
        "note": "project termux-monorepo is present; hobby rate-limit remains NON-GATE",
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
        "note": "private pages include Jules Task Queue and To Do List; content not copied",
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
        "note": "dashboard search returned HTTP 424 while the stack was paused; datasource list later returned 12 names; stack slug omitted; not a gate",
    },
    {
        "name": "mixpanel",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "Get-Projects returned 1 project id 4066774; display name omitted; no event query",
    },
    {
        "name": "stepie",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "open tasks still name SHAs 912ab126 and 0e1fee04; not a gate",
    },
    {
        "name": "gamma",
        "state": "NOT_PROBED",
        "lane": "NEED_EVIDENCE",
        "note": "analytics tool resolved; no gamma id on hand; not called",
    },
    {
        "name": "figma",
        "state": "LIVE",
        "lane": "NEED_EVIDENCE",
        "note": "whoami returned 1 starter plan; no file key on hand; file tools not called",
    },
    {
        "name": "bigquery",
        "state": "SCHEMA_ONLY",
        "lane": "NEED_EVIDENCE",
        "note": "list_dataset_ids requires projectId; none on hand; not called",
    },
)


def connector_report() -> dict[str, object]:
    payload = {
        "writes": False,
        "secrets": False,
        "probed_on": "2026-10-14",
        "count": len(CONNECTORS),
        "connectors": list(CONNECTORS),
    }
    assert_names_only(json.dumps(payload))
    return payload
