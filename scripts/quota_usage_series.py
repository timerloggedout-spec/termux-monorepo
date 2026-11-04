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
    build_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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

    # Vultr legs (owner order via D2 seat, 2026-11-03): the pack's
    # series5_vultr copy of ops/quota/vultr-usage.json. Populated
    # legs render as USD burn series; unprovisioned legs stay
    # explicit gap entries - present, never zero-filled.
    s5 = usage_pack.get("series5_vultr") or {}
    for leg_key, leg_title in (("instances", "Vultr instances"),
                               ("serverless",
                                "Vultr serverless inference")):
        leg = (s5.get("legs") or {}).get(leg_key) or {}
        pts = [{"t": p["t"], "v": p["v"]}
               for p in leg.get("points", [])
               if p.get("t") and p.get("v") is not None]
        if pts:
            service.append({
                "key": "vultr." + leg_key,
                "title": leg_title + " - $ burn",
                "unit": "USD", "kind": leg.get("kind", "estimated"),
                "metric": "usd_burn", "points": pts,
                "provenance": "ops/quota/vultr-usage.json via "
                              "quota-usage pack series5_vultr"})
        else:
            service.append({
                "key": "vultr." + leg_key,
                "title": leg_title + " - $ burn (gap)",
                "unit": "USD", "kind": "gap", "metric": "usd_burn",
                "points": [],
                "provenance": "ops/quota/vultr-usage.json via "
                              "quota-usage pack series5_vultr "
                              "(explicit gap: " +
                              str(leg.get("reason",
                                          "not established")) + ")"})

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

    # ---- Consumption pass (owner fix order 2026-11-03) ----
    # Per-call USAGE of record, distinct from the activity-proxy counts
    # above. Sources: ops/3l0/intake.jsonl (stamp_fanout's usage
    # {tokens_in, tokens_out} per routed call) + the routed-dispatch
    # corpus records' own usage{} blocks, keyed onto the SAME deduped
    # call set as the activity pass (the stamps dict above: routed-
    # dispatch records/stamps + nested-family carriers). A call is
    # usage-stamped when it carries a numeric token value on either
    # side, or a measured usage{} value in a provider-native unit.
    # Unstamped calls are COUNTED in consumption_gap below - named on
    # the page, never silently excluded (coverage honesty inverted).
    def _num(x):
        return x if isinstance(x, (int, float)) and not isinstance(x, bool) else None

    call_usage = {}
    quota_by_dispatch = {}
    session_usage = {}

    def add_quota(dispatch_key, quota):
        if not dispatch_key or not isinstance(quota, dict):
            return
        slot = quota_by_dispatch.setdefault(dispatch_key, {})
        for field in ("pool", "slice"):
            if slot.get(field) is None and quota.get(field) is not None:
                slot[field] = quota[field]

    def add_usage(dispatch_key, usage, source):
        if not dispatch_key or not isinstance(usage, dict):
            return
        tin, tout = _num(usage.get("tokens_in")), _num(usage.get("tokens_out"))
        value = _num(usage.get("value"))
        unit = usage.get("unit")
        if value is None and (tin is not None or tout is not None):
            value = (tin or 0) + (tout or 0)
            unit = unit or "tokens"
        if value is not None:
            call_usage[dispatch_key] = {"value": value, "unit": unit or "tokens",
                                        "status": "measured", "source": source}
        elif usage.get("status") in ("no-usage-surface", "waived", "fault", "pending"):
            call_usage.setdefault(dispatch_key, {"value": None, "unit": None,
                                                 "status": usage["status"],
                                                 "source": source,
                                                 "note": usage.get("note")})

    intake_path = Path(root) / "ops/3l0/intake.jsonl"
    if intake_path.is_file():
        for line in intake_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            prov = row.get("provider")
            if not prov or str(prov).lower() == "github-actions":
                continue
            key = row.get("dispatch_id") or (str(prov) + "|" +
                    str(row.get("model")) + "|" + str(row.get("ts")))
            if key not in stamps:
                stamps[key] = (str(prov), str(row.get("model")),
                               str(row.get("ts")))
            add_quota(row.get("dispatch_id"), row.get("quota"))
            add_usage(key, row.get("usage"), "ops/3l0/intake.jsonl")
    for sub in ("records", "stamps"):
        for f in sorted(Path(root).glob(
                "experiments/doe/routed-dispatch/" + sub + "/*.json")):
            try:
                rec = json.loads(f.read_text())
            except (OSError, ValueError):
                continue
            prov = rec.get("provider")
            if not prov or str(prov).lower() == "github-actions":
                continue
            key = rec.get("dispatch_id") or (str(prov) + "|" +
                    str(rec.get("model")) + "|" + str(rec.get("ts")))
            add_quota(rec.get("dispatch_id"), rec.get("quota"))
            add_usage(key, rec.get("usage"), "experiments/doe/routed-dispatch/" + sub)

    # Session-level desk usage is a separate carrier. Preserve its match
    # class: activity-proxy is activity, never consumption.
    for trav in desk.get("traversals", []):
        for row in trav.get("provider_usage", []):
            sid = row.get("session_id")
            usage = row.get("usage") or {}
            if sid and isinstance(usage, dict):
                session_usage.setdefault(str(sid), {
                    "value": _num(usage.get("value")),
                    "unit": usage.get("unit"),
                    "match": usage.get("match"),
                    "status": usage.get("status"),
                    "source": usage.get("source") or "ops/challenge/desk-feed.json",
                    "note": usage.get("note"),
                })

    stamped_calls = []   # (provider, model, ts, value, unit)
    gap_by_provider = {}
    gap_causes = {"no-usage-record": 0, "no-usage-surface": 0}
    for key, (pname, mname, tsv) in stamps.items():
        slug = fam_slug(pname)
        slot = gap_by_provider.setdefault(slug, {"provider": pname, "calls": 0,
                                                 "stamped": 0, "unstamped": 0})
        slot["calls"] += 1
        u = call_usage.get(key)
        if u and u["status"] == "measured":
            slot["stamped"] += 1
            stamped_calls.append((pname, mname, tsv, u["value"], u["unit"]))
        else:
            slot["unstamped"] += 1
            cause = ("no-usage-surface" if u and u["status"] == "no-usage-surface"
                     else "no-usage-record")
            gap_causes[cause] += 1
    total_calls = sum(s["calls"] for s in gap_by_provider.values())
    total_stamped = sum(s["stamped"] for s in gap_by_provider.values())
    consumption_gap = {
        "method": "fleet-self-count: routed calls of record (3L0 intake + "
                  "routed-dispatch records/stamps + nested-family carriers, "
                  "dispatch_id-deduped, github-actions excluded) vs calls "
                  "carrying a numeric usage value (provider-response tokens "
                  "or a measured provider-native usage{} value)",
        "routed_calls": total_calls,
        "usage_stamped": total_stamped,
        "unstamped": total_calls - total_stamped,
        "unstamped_share": (round((total_calls - total_stamped) / total_calls, 4)
                            if total_calls else None),
        "causes": gap_causes,
        "by_provider": gap_by_provider,
        "sources": ["ops/3l0/intake.jsonl",
                    "experiments/doe/routed-dispatch/records/*.json",
                    "experiments/doe/routed-dispatch/stamps/*.json",
                    "ops/tracking/nested-family.json"],
    }

    # Read-model projection: provider -> model (verbatim) -> role -> tasks.
    # The nested-family record is the task denominator; only exact dispatch_id
    # or session_id joins enrich a row. Missing usage remains explicit.
    task_providers = []
    task_coverage = {"tasks": 0, "established": 0, "activity_only": 0,
                     "no_usage_surface": 0, "waived": 0, "fault": 0,
                     "pending": 0, "not_established": 0}
    for prov in nested.get("providers", []):
        models_out = []
        for mod in prov.get("models", []):
            role_groups = {}
            for task in mod.get("tasks", []):
                did = task.get("dispatch_id")
                sid = task.get("session_id")
                usage = call_usage.get(did) if did else None
                attribution = "dispatch_id" if usage else "none"
                if not usage and sid and str(sid) in session_usage:
                    usage = session_usage[str(sid)]
                    attribution = "session_id"
                if usage and (usage.get("status") == "measured"
                              or (usage.get("match") == "exact"
                                  and _num(usage.get("value")) is not None)):
                    usage_view = {"value": usage.get("value"),
                                  "unit": usage.get("unit"), "match": "exact",
                                  "status": "established",
                                  "source": usage.get("source"), "note": None}
                elif usage and usage.get("match") == "activity-proxy" and usage.get("value") is not None:
                    usage_view = {"value": usage.get("value"),
                                  "unit": usage.get("unit"), "match": "activity-proxy",
                                  "status": "activity-only",
                                  "source": usage.get("source"),
                                  "note": usage.get("note")}
                elif usage and usage.get("status") in ("no-usage-surface", "waived", "fault", "pending"):
                    usage_view = {"value": None, "unit": None, "match": None,
                                  "status": usage.get("status"),
                                  "source": usage.get("source"),
                                  "note": usage.get("note") or ("Provider route exposes no per-call usage surface." if usage.get("status") == "no-usage-surface" else None)}
                else:
                    usage_view = {"value": None, "unit": None, "match": None,
                                  "status": "NOT_ESTABLISHED", "source": None,
                                  "note": "No exact dispatch_id or session_id usage record is available."}
                    attribution = "none"
                task_coverage["tasks"] += 1
                bucket = {"established": "established", "activity-only": "activity_only",
                          "no-usage-surface": "no_usage_surface", "waived": "waived",
                          "fault": "fault", "pending": "pending",
                          "NOT_ESTABLISHED": "not_established"}[usage_view["status"]]
                task_coverage[bucket] += 1
                role = task.get("role") or "NOT_ESTABLISHED"
                task_row = {
                    "task_class": task.get("task_class"),
                    "dispatch_id": did, "run_id": task.get("run_id"),
                    "workflow": task.get("workflow"), "session_id": sid,
                    "ts": task.get("ts"), "moniker": task.get("moniker"),
                    "context": task.get("context"), "outcome": task.get("outcome"),
                    "quota": quota_by_dispatch.get(did) if did else None,
                    "usage": usage_view, "attribution": attribution,
                    "source_ref": task.get("source_ref"),
                }
                role_groups.setdefault(role, []).append(task_row)
            roles_out = []
            for role, rows in sorted(role_groups.items()):
                participants = {}
                for row in rows:
                    participant = row.get("moniker") or "NOT_ESTABLISHED"
                    participants.setdefault(participant, []).append(row)
                roles_out.append({
                    "role": role,
                    "participants": [{"moniker": participant, "tasks": tasks}
                                     for participant, tasks in sorted(participants.items())],
                })
            models_out.append({"model": mod.get("model"), "roles": roles_out})
        task_providers.append({"provider": prov.get("provider"), "models": models_out})
    task_tree = {
        "schema": "quota.task-tree/v1",
        "generated_at": build_at,
        "source": "ops/tracking/nested-family.json + dispatch usage records + ops/challenge/desk-feed.json",
        "grouping": "provider -> model (verbatim) -> role (verbatim) -> participant (moniker) -> tasks",
        "providers": task_providers,
        "coverage": task_coverage,
        "notes": "Exact usage is joined by dispatch_id; session_id carriers retain their exact/activity-proxy class. No match remains NOT_ESTABLISHED. Quota pool/slice appear only when stamped on the matching dispatch record.",
    }

    cons_prov, cons_model = {}, {}
    for pname, mname, tsv, value, unit in stamped_calls:
        cons_prov.setdefault((fam_slug(pname), unit), []).append((tsv, value, pname))
        if mname and mname != "NOT ESTABLISHED":
            cons_model.setdefault((mname, unit), []).append((tsv, value, pname))
    for (slug, unit), pts in sorted(cons_prov.items()):
        pts.sort()
        run = 0; points = []
        for tsv, value, pname in pts:
            run += value
            points.append({"t": tsv, "v": run})
        provider.append({
            "key": slug + "::consumption",
            "title": pts[0][2] + " - consumption (cumulative, per-call usage of record)",
            "unit": unit, "kind": "consumption", "metric": "usage_value",
            "points": points,
            "provenance": "per-call usage records: ops/3l0/intake.jsonl usage{} + "
                          "routed-dispatch record usage{} (method: fleet-self-count/"
                          "response-usage; see docs/ops/QUOTA-USAGE-RECORDS.md)"})
    for (mname, unit), pts in sorted(cons_model.items()):
        pts.sort()
        run = 0; points = []
        for tsv, value, pname in pts:
            run += value
            points.append({"t": tsv, "v": run})
        model.append({
            "key": mname + "::consumption",
            "title": pts[0][2] + " - " + mname + " - consumption (cumulative)",
            "unit": unit, "kind": "consumption", "metric": "usage_value",
            "points": points,
            "provenance": "per-call usage records: ops/3l0/intake.jsonl usage{} + "
                          "routed-dispatch record usage{} (method: fleet-self-count/"
                          "response-usage; see docs/ops/QUOTA-USAGE-RECORDS.md)"})

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
    have = {s["key"].split("::")[0] for s in provider}
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
        "generated_at": build_at,
        "inputs_generated_at": {
            "ops/quota/quota-usage.json": usage_pack.get("generated_at"),
            "ops/tracking/nested-family.json": nested.get("generated_at")},
        "sources": ["ops/quota/quota-usage.json",
                    "ops/quota/vultr-usage.json",
                    "ops/challenge/desk-feed.json",
                    "ops/quota/allocation-plan.json",
                    "ops/quota/rate-limit-events.json",
                    "ops/tracking/nested-family.json",
                    "experiments/doe/routed-dispatch/records/*.json",
                    "experiments/doe/routed-dispatch/stamps/*.json",
                    "ops/3l0/intake.jsonl"],
        "axes": {"provider": provider, "service": service, "model": model, "events": events_axis},
        "coverage": coverage,
        "consumption_gap": consumption_gap,
        "task_tree": task_tree,
        "notes": {
            "model": "Model series are populated from stamped dispatch records (routed-dispatch fan-out + nested-family carriers): one point per stamped dispatch, cumulative, kind activity-proxy - dispatch counts, not consumption. Instances stamped NOT ESTABLISHED carry no model@version and are excluded; nothing is inferred. Consumption-class series (kind consumption) are built from per-call usage records - ops/3l0/intake.jsonl usage{tokens_in,tokens_out} and routed-dispatch record usage{} blocks - cumulative per provider and per model@version, exact record match only. Unstamped routed calls are counted in consumption_gap (named on the page), never silently excluded.",
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
