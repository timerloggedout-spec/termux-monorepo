#!/usr/bin/env python3
"""Build ops/quota/swarm-feed.json (quota.swarm-feed/v1) - the swarm-
scoped quota feed for quota-swarm.html. Swarm (owner definition
2026-11-01) = ALL providers' inference model endpoints participating
in 3L0 DoE. Envelope aligned with Tracking's nested-family/v1
{schema, generated_at, generated_by, spec, sources, summary,
providers, gaps}: providers are families (registry model-lane records
grouped by id family; the 61 g4f.* upstreams nest under ONE g4f
family), each carrying its registry records with limits, the census
verdict/evidence for the family, readings status, and any usage
series points. The GitHub rate-limit events series
(ops/quota/rate-limit-events.json) is embedded whole. Values are
carried only where a source establishes them - the public readings
projection withholds account values by design, so remaining/used
stay null there and the census evidence class says what is known.
stdlib only.

Usage: python3 scripts/quota_swarm_feed.py [--root .] [--out PATH]
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def load(root, rel):
    p = Path(root) / rel
    return json.loads(p.read_text()) if p.exists() else None


def fam_of(rec_id):
    return str(rec_id).split(".")[0]


def build(root):
    reg = load(root, "ops/quota/registry.json") or {}
    census = load(root, "ops/quota/allocation-verification.json") or {}
    status = load(root, "docs/ops/generated/quota-status.json") or {}
    series = load(root, "ops/quota/usage-series.json") or {}
    events_doc = load(root, "ops/quota/rate-limit-events.json") or {}

    cen_by_fam = {}
    for row in census.get("rows", []):
        cen_by_fam[str(row.get("provider"))] = row
    # census names the google family 'gemini'/'jules'; registry ids use
    # 'gemini' for model records already - alias google-family rows.
    read_by_id = {}
    for r in status.get("readings", []):
        read_by_id[r.get("resource_id")] = r
    pts_by_key = {}
    for axis in (series.get("axes") or {}).values():
        for s in axis:
            if s.get("points"):
                pts_by_key.setdefault(s.get("key"), s)

    model_recs = [s for s in reg.get("services", [])
                  if s.get("lane") == "model"]
    fams = {}
    for rec in model_recs:
        fams.setdefault(fam_of(rec["id"]), []).append(rec)

    providers = []
    census_api_verified = 0
    for fam in sorted(fams):
        recs = sorted(fams[fam], key=lambda r: r["id"])
        cen = cen_by_fam.get(fam)
        if fam == "gemini":
            cen = cen_by_fam.get("gemini") or cen_by_fam.get("google")
        verified = bool(cen and cen.get("evidence") == "api-verified")
        if verified:
            census_api_verified += 1
        records = []
        for rec in recs:
            rd = read_by_id.get(rec["id"]) or {}
            records.append({
                "id": rec["id"],
                "provider": rec.get("provider"),
                "metric": rec.get("metric"),
                "limit": rec.get("limit"),
                "unit": rec.get("unit"),
                "window": rec.get("window"),
                "reset": rec.get("reset"),
                "live": rec.get("live"),
                "readings": {
                    "status": rd.get("status"),
                    "used": rd.get("used"),
                    "remaining": None,
                    "evidence_status": rd.get("evidence_status"),
                    "horizon": rd.get("horizon"),
                    "observed_at": rd.get("observed_at"),
                } if rd else None,
                "usage_series": pts_by_key.get(rec["id"])
                or pts_by_key.get(fam),
                "populated": bool(
                    pts_by_key.get(rec["id"]) or pts_by_key.get(fam))
                or (bool(rd) and (rd.get("status") not in (None, "unknown")
                                  or rd.get("used") is not None
                                  or rd.get("observed_at"))),
            })
        fam_bases = set()
        for r in records:
            rdg = r.get("readings") or {}
            if rdg and (rdg.get("status") not in (None, "unknown")
                        or rdg.get("used") is not None
                        or rdg.get("observed_at")):
                fam_bases.add("readings")
            if r.get("usage_series"):
                fam_bases.add("usage-series")
        if cen:
            fam_bases.add("census")
        providers.append({
            "provider": fam,
            "record_count": len(records),
            "providers_distinct": len({r.get("provider") for r in recs}),
            "census_api_verified": verified,
            "population": {
                "state": "populated" if fam_bases else "gap",
                "bases": sorted(fam_bases),
            },
            "census": ({
                "verdict": cen.get("verdict"),
                "evidence": cen.get("evidence"),
                "free_tier": cen.get("free_tier"),
                "credits": cen.get("credits"),
                "replenishment": cen.get("replenishment"),
                "flags": cen.get("flags"),
            } if cen else None),
            "records": records,
        })

    events = events_doc.get("events", [])
    feed = {
        "schema": "quota.swarm-feed/v1",
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "scripts/quota_swarm_feed.py",
        "spec": {
            "doc": "docs/ops/PROVIDER-DISPATCH-CAPABILITY.md",
            "grouping": "family (registry id prefix) > registry records; "
                        "g4f upstreams nest under the single g4f family",
            "envelope": "aligned with Tracking nested-family/v1 "
                        "{schema, generated_at, generated_by, spec, "
                        "sources, summary, providers, gaps}",
            "swarm_definition": "owner 2026-11-01: ALL providers' "
                                "inference model endpoints participating "
                                "in 3L0 DoE",
            "verification_semantics": (
                "census_api_verified reflects allocation-census API evidence only; "
                "it does not establish inference invocation, free eligibility, "
                "or routing admission."
            ),
        },
        "sources": [
            {"id": "registry", "path": "ops/quota/registry.json",
             "generated_at": reg.get("generated_at")},
            {"id": "census", "path": "ops/quota/allocation-verification.json",
             "generated_at": census.get("generated_at")},
            {"id": "readings", "path": "docs/ops/generated/quota-status.json",
             "generated_at": status.get("generated_at")},
            {"id": "usage-series", "path": "ops/quota/usage-series.json",
             "generated_at": series.get("generated_at")},
            {"id": "rate-limit-events",
             "path": "ops/quota/rate-limit-events.json",
             "generated_at": events_doc.get("generated_at")},
        ],
        "summary": {
            "registry_model_records": len(model_recs),
            "distinct_providers": len({r.get("provider")
                                       for r in model_recs}),
            "families": len(providers),
            "families_direct": len(providers) - (1 if "g4f" in fams else 0),
            "g4f_children": len(fams.get("g4f", [])),
            "census_api_verified_families": census_api_verified,
            "rate_limit_events": len(events),
            "families_populated": len([p for p in providers
                                       if p["population"]["state"]
                                       == "populated"]),
            "families_gap": len([p for p in providers
                                 if p["population"]["state"] == "gap"]),
            "records_populated": sum(
                1 for p in providers for r in p["records"]
                if r.get("populated")),
            "records_total": len(model_recs),
            "population": {
                "providers_total": len({r.get("provider")
                                        for r in model_recs}),
                "providers_populated": len({
                    r["provider"] for p in providers
                    for r in p["records"] if r.get("populated")}),
                "providers_gap": len({r.get("provider")
                                      for r in model_recs}) - len({
                    r["provider"] for p in providers
                    for r in p["records"] if r.get("populated")}),
                "families_total": len(providers),
                "families_populated": len([p for p in providers
                                           if p["population"]["state"]
                                           == "populated"]),
                "families_gap": len([p for p in providers
                                     if p["population"]["state"]
                                     == "gap"]),
            },
        },
        "providers": providers,
        "events": {
            "schema": events_doc.get("schema"),
            "source": "ops/quota/rate-limit-events.json",
            "events": events,
        },
        "gaps": [
            "readings used/remaining are null in the public projection "
            "by design (account values withheld); per-provider "
            "remaining/usage render only where the census or a usage "
            "series establishes them.",
            "families with no census row carry census=null - their "
            "allocation state is not-established, not zero.",
        ],
    }
    return feed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    feed = build(a.root)
    out = Path(a.out) if a.out else Path(a.root) / "ops/quota/swarm-feed.json"
    out.write_text(json.dumps(feed, indent=1) + "\n")
    print("wrote", out, feed["summary"])


if __name__ == "__main__":
    main()
