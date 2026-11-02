#!/usr/bin/env python3
"""Build ops/quota/usage-series.json (quota.usage-series/v1) from committed
sources only: the quota-usage pack (measured/reconstructed series), the
desk-feed usage{} stamps (activity-proxy class) and allocation-plan pools
(context targets). Honesty contract (QUOTA-ATTRIBUTION): consumption renders
only where a usage{} match is exact; activity counts stay labeled
activity-proxy; missing data stays missing - no zero-fill, no interpolation,
no inferred model@version. stdlib only.

Freshness stamps (2026-11-02, owner staleness flag): the pack carries
generated_at (this build), inputs_generated_at (the quota-usage pack's own
generated_at) and a per-series last_point_at, so the graphs page can show
pack age and flag stale series instead of presenting frozen data as
current. Refresh automation: .github/workflows/quota-usage-series-refresh.yml
(push on inputs + dispatch; no cron).

Usage: python3 scripts/quota_usage_series.py [--root .] [--out PATH]
"""
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

KIND_BY_MATCH = {"exact": "usage-exact", "activity-proxy": "activity-proxy"}


def load(root, rel):
    p = Path(root) / rel
    return json.loads(p.read_text()) if p.exists() else None


def fam_slug(provider):
    tok = re.split(r"[\s(]", str(provider).strip().lower())[0]
    return tok or "unknown"


def window_end(row):
    w = row.get("window")
    if isinstance(w, str) and "->" in w:
        end = w.split("->")[1].strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}T", end):
            return end
    return None


def build(root):
    usage_pack = load(root, "ops/quota/quota-usage.json") or {}
    desk = load(root, "ops/challenge/desk-feed.json") or {}
    plan = load(root, "ops/quota/allocation-plan.json") or {}

    provider, service, model = [], [], []

    s1 = usage_pack.get("series1_api_core") or {}
    pts = [{"t": p["at"], "v": p["remaining"]} for p in s1.get("points", [])
           if p.get("at") and p.get("remaining") is not None]
    if pts:
        entry = {"key": "github", "title": "GitHub API core - remaining",
                 "unit": s1.get("unit", "requests/hour"), "kind": "measured",
                 "metric": "remaining", "points": pts,
                 "provenance": "ops/quota/quota-usage.json series1_api_core"}
        provider.append(dict(entry))
        service.append({**entry, "key": "github.api.user_token",
                        "title": "github.api.user_token (PAT bucket) - "
                                 "API core remaining"})

    s3 = usage_pack.get("series3_actions") or {}
    days = s3.get("days", [])
    for metric, kind, unit in (("runs_delta", "reconstructed", "runs/day"),
                               ("minutes_est", "estimated", "minutes/day")):
        pts = [{"t": d["date"], "v": d[metric]} for d in days
               if d.get("date") and d.get(metric) is not None]
        if pts:
            service.append({"key": "github.actions", "title":
                            "GitHub Actions volume - " + metric,
                            "unit": unit, "kind": kind, "metric": metric,
                            "points": pts,
                            "provenance": "ops/quota/quota-usage.json "
                                          "series3_actions (" +
                                          s3.get("title", "") + ")"})

    for trav in desk.get("traversals", []):
        for row in trav.get("provider_usage", []):
            u = row.get("usage") or {}
            end = window_end(row)
            if u.get("value") is None or not end:
                continue
            kind = KIND_BY_MATCH.get(u.get("match"), "activity-proxy")
            fam = fam_slug(row.get("provider"))
            series = {"key": fam, "title": str(row.get("provider")) +
                      " - " + str(u.get("unit")),
                      "unit": u.get("unit"), "kind": kind,
                      "metric": u.get("unit"),
                      "points": [{"t": end, "v": u["value"]}],
                      "provenance": "ops/challenge/desk-feed.json usage{} "
                                    "(session " +
                                    str(row.get("session_id")) + ")"}
            provider.append(series)
            if row.get("activities") is not None:
                provider.append({**series, "unit": "activities",
                                 "metric": "activities",
                                 "title": str(row.get("provider")) +
                                          " - activities",
                                 "points": [{"t": end,
                                             "v": row["activities"]}]})
            m = row.get("model")
            if m and m != "NOT ESTABLISHED":
                model.append({**series, "key": m,
                              "title": m + " - " + str(u.get("unit"))})

    pools = {p["id"]: p.get("target_flow_per_min")
             for p in plan.get("pools", [])}
    for s in provider:
        t = pools.get(s["key"])
        if t:
            s["context"] = {"target_flow_per_min": t,
                            "source": "ops/quota/allocation-plan.json pool "
                                      + s["key"],
                            "note": "plan target flow - context only, "
                                    "not usage; plotted only if units match"}

    for rows in (provider, service, model):
        for s in rows:
            ts = [p["t"] for p in s.get("points", []) if p.get("t")]
            s["last_point_at"] = max(ts) if ts else None

    pack = {
        "schema": "quota.usage-series/v1",
        "generated_by": "scripts/quota_usage_series.py",
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "inputs_generated_at": {
            "ops/quota/quota-usage.json": usage_pack.get("generated_at")},
        "sources": ["ops/quota/quota-usage.json",
                    "ops/challenge/desk-feed.json",
                    "ops/quota/allocation-plan.json"],
        "axes": {"provider": provider, "service": service, "model": model},
        "notes": {
            "model": "Per-model series require a stamped model@version AND "
                     "a usage{} value on the same record. Jules-class rows "
                     "carry no model@version (NOT ESTABLISHED) and the "
                     "Muse rows carry no usage value (waived), so the "
                     "model axis is empty until live-3 dispatch records "
                     "(EXPERIMENT rev 1.1 usage{}) land. Empty is the "
                     "honest state - nothing is inferred.",
            "readings": "The public readings snapshots "
                        "(docs/ops/generated/quota-status.json) carry no "
                        "usage values by design (status-only projection); "
                        "they are not a usage series source.",
            "gaps": "Points exist only where a source observed a value. "
                    "Segments spanning >3x the series minimum step and >its "
                    "median step render dotted (gap signal); no zero-fill, "
                    "no interpolation.",
        },
    }
    return pack


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    pack = build(a.root)
    out = Path(a.out) if a.out else Path(a.root) / "ops/quota/usage-series.json"
    out.write_text(json.dumps(pack, indent=1) + "\n")
    counts = {k: len(v) for k, v in pack["axes"].items()}
    print("wrote", out, counts)


if __name__ == "__main__":
    main()
