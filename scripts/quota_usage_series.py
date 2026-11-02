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
    events_doc = load(root, "ops/quota/rate-limit-events.json") or {}
    nested = load(root, "ops/tracking/nested-family.json") or {}
    registry = load(root, "ops/quota/registry.json") or {}

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

    # Stamped dispatch usage (owner order 2026-11-01: model-axis
    # population). Sources: the routed-dispatch fan-out records +
    # stamps (experiments/doe/routed-dispatch/{records,stamps}/*.json)
    # and the nested-family carriers (ops/tracking/nested-family.json
    # tasks). Each stamp is ONE dispatch of a configured instance at
    # ts - activity class per the QUOTA-ATTRIBUTION contract (counts
    # render as activity-proxy, never as consumption). Deduped by
    # dispatch_id across sources. Models stamped NOT ESTABLISHED are
    # excluded - no inferred model@version. github-actions carriers
    # are CI builds, not model dispatches - excluded.
    stamps = {}

    def add_stamp(provider, model_name, ts, dispatch_id):
        if not provider or not model_name or not ts:
            return
        if model_name == "NOT ESTABLISHED":
            return
        if str(provider).lower() == "github-actions":
            return
        key = dispatch_id or (str(provider) + "|" + str(model_name)
                              + "|" + str(ts))
        stamps.setdefault(key, (str(provider), str(model_name),
                                str(ts)))

    for sub in ("records", "stamps"):
        for f in sorted(Path(root).glob(
                "experiments/doe/routed-dispatch/" + sub + "/*.json")):
            try:
                rec = json.loads(f.read_text())
            except (OSError, ValueError):
                continue
            add_stamp(rec.get("provider"), rec.get("model"),
                      rec.get("ts"), rec.get("dispatch_id"))
    for prov in nested.get("providers", []):
        for mod in prov.get("models", []):
            for t in mod.get("tasks", []):
                add_stamp(prov.get("provider"), mod.get("model"),
                          t.get("ts"), t.get("dispatch_id"))

    by_model = {}
    for pname, mname, tsv in stamps.values():
        slot = by_model.setdefault((pname.lower(), mname),
                                   {"provider": pname, "ts": []})
        slot["ts"].append(tsv)
    for (plow, model_name), slot in sorted(by_model.items()):
        tss = sorted(slot["ts"])
        model.append({
            "key": model_name,
            "title": slot["provider"] + " - " + model_name +
                     " - dispatches (cumulative)",
            "unit": "dispatches", "kind": "activity-proxy",
            "metric": "dispatches",
            "points": [{"t": t, "v": i + 1}
                       for i, t in enumerate(tss)],
            "provenance": "stamped dispatch records: experiments/doe/"
                          "routed-dispatch/{records,stamps} + "
                          "ops/tracking/nested-family.json tasks "
                          "(activity-proxy class)"})

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

    ev_by_bucket = {}
    for ev in events_doc.get("events", []):
        ev_by_bucket.setdefault(ev.get("bucket", "unknown"), []).append(ev)
    events_axis = []
    for bucket in sorted(ev_by_bucket):
        evs = sorted(ev_by_bucket[bucket], key=lambda e: e.get("at", ""))
        events_axis.append({"key": bucket,
                            "title": bucket + " - rate-limit events",
                            "unit": "events", "kind": "event",
                            "metric": "events",
                            "points": [{"t": e["at"], "v": 1,
                                        "class": e.get("class")}
                                       for e in evs if e.get("at")],
                            "provenance": "ops/quota/rate-limit-events.json"})

    # Denominator pass (owner amendment 2026-11-01: ALL Providers).
    # Every registry model-lane provider is PRESENT in the provider
    # axis - populated where stamped usage exists, an explicit gap
    # entry where it does not. Gaps are never absent and never
    # zero-filled: points stay empty, kind = "gap".
    reg_providers = {}
    for r in (registry.get("services") or []):
        if r.get("lane") == "model" and r.get("provider"):
            reg_providers.setdefault(fam_slug(r["provider"]),
                                     r["provider"])
    have = {s["key"] for s in provider}
    for slug in sorted(reg_providers):
        if slug not in have:
            provider.append({
                "key": slug,
                "title": reg_providers[slug] +
                         " - no stamped usage yet (gap)",
                "unit": None, "kind": "gap", "metric": None,
                "points": [],
                "provenance": "ops/quota/registry.json model lane "
                              "(denominator - present, unpopulated)"})
    coverage = {
        "providers_total": len(reg_providers),
        "providers_populated": len([s for s in provider
                                    if s.get("kind") != "gap"]),
        "providers_gap": len([s for s in provider
                              if s.get("kind") == "gap"]),
        "model_series": len(model),
        "model_populated": len([s for s in model if s.get("points")]),
    }

    for rows in (provider, service, model, events_axis):
        for s in rows:
            ts = [p["t"] for p in s.get("points", []) if p.get("t")]
            s["last_point_at"] = max(ts) if ts else None

    pack = {
        "schema": "quota.usage-series/v1",
        "generated_by": "scripts/quota_usage_series.py",
        "generated_at": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "inputs_generated_at": {
            "ops/quota/quota-usage.json": usage_pack.get("generated_at"),
            "ops/tracking/nested-family.json": nested.get("generated_at")},
        "sources": ["ops/quota/quota-usage.json",
                    "ops/challenge/desk-feed.json",
                    "ops/quota/allocation-plan.json",
                    "ops/quota/rate-limit-events.json",
                    "ops/tracking/nested-family.json",
                    "experiments/doe/routed-dispatch/records/*.json",
                    "experiments/doe/routed-dispatch/stamps/*.json"],
        "axes": {"provider": provider, "service": service, "model": model, "events": events_axis},
        "coverage": coverage,
        "notes": {
            "model": "Model series are populated from stamped dispatch records (routed-dispatch fan-out + nested-family carriers): one point per stamped dispatch, cumulative, kind activity-proxy - dispatch counts, not consumption. Instances stamped NOT ESTABLISHED carry no model@version and are excluded; nothing is inferred. Consumption-class model series still require usage{} values with an exact match on the same record.",
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
