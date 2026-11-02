#!/usr/bin/env python3
"""ALL-4 RESULTS INDEX - one aggregation feed for the Viz results page.

Owner direction 2026-11-01 (feed counterpart): for each of
{ATES - 3L0 - Temporal - HindSight}, expose the results feed/record of
record + its current headline state in ONE index feed
(`ops/telemetry/results-index.json`, schema results-index/v1) that Viz
renders verbatim. Where a system has no results feed, the record of
record is NAMED (Actions run receipts / artifacts) - never invented.

Sources (all read at build time, nothing cached across runs):
  ATES      apps/tribute-dashboard/data/ates-feed.json (its own feed;
            its gaps[] declares: no committed results ledger - verdicts
            asserted in-run, receipts = 30-day Actions artifacts)
  3L0       ops/telemetry/session-history-3l0.jsonl (staged intake,
            observational; confirmed counts computed from the file)
  Temporal  Actions run receipts for temporal-engagement.yml +
            temporal-self-host-smoke.yml (no feed exists; API when a
            token is present, else NOT_ESTABLISHED_THIS_RUN)
  HindSight ops/telemetry/hindsight-retain-proof.json +
            ops/telemetry/hindsight-retain-state.json

Usage: results_index.py --root . --out ops/telemetry/results-index.json
"""
import argparse
import datetime
import json
import os
import sys
import urllib.request

SCHEMA = "results-index/v1"
REPO = "timerloggedout-spec/termux-monorepo"


def _load(root, rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _lines(root, rel):
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        return []
    return [l for l in open(p, encoding="utf-8") if l.strip()]


def _runs(workflow, token):
    req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/workflows/"
        f"{workflow}/runs?per_page=5", method="GET")
    req.add_header("Accept", "application/vnd.github+json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.build_opener().open(req, timeout=60) as resp:
        d = json.loads(resp.read())
    runs = d.get("workflow_runs", [])
    latest = runs[0] if runs else None
    return {"total_count": d.get("total_count"),
            "latest": ({"id": latest["id"], "at": latest["created_at"],
                        "conclusion": latest["conclusion"],
                        "event": latest["event"]} if latest else None)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--temporal-json",
                    help="precomputed {engagement, self_host_smoke} runs "
                         "summary (offline generation route)")
    ap.add_argument("--viz-out",
                    help="also emit the Viz row-contract twin "
                         "(results-index-feed/v1) at this path")
    args = ap.parse_args()
    now = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    systems = []

    # --- ATES ---
    ates = _load(args.root, "apps/tribute-dashboard/data/ates-feed.json")
    if ates:
        wfs = []
        for w in ates.get("data", {}).get("workflows", []):
            obs = w.get("observed_runs", {})
            lat = (obs.get("latest") or [{}])[0]
            wfs.append({"file": w.get("file"),
                        "total_runs": obs.get("total_runs"),
                        "latest_at": lat.get("created_at"),
                        "latest_conclusion": lat.get("conclusion")})
        systems.append({
            "id": "ates", "name": "ATES",
            "record_of_record": {
                "kind": "feed",
                "path": "apps/tribute-dashboard/data/ates-feed.json",
                "note": "No committed results ledger exists (feed gaps[] "
                        "of record): benchmark verdicts are asserted "
                        "inside workflow runs; run receipts publish as "
                        "30-day Actions artifacts."},
            "headline": {"feed_generated_at": ates.get("generated_at"),
                         "workflows": wfs,
                         "invariants": ates.get("data", {}).get("invariants")},
            "as_of": ates.get("generated_at")})
    else:
        systems.append({"id": "ates", "name": "ATES",
                        "record_of_record": {"kind": "feed",
                            "path": "apps/tribute-dashboard/data/ates-feed.json"},
                        "headline": {"state": "FEED_NOT_FOUND_AT_BUILD"},
                        "as_of": now})

    # --- 3L0 ---
    l30_lines = _lines(args.root, "ops/telemetry/session-history-3l0.jsonl")
    confirmed = 0
    for l in l30_lines:
        try:
            if (json.loads(l).get("outcome") or {}).get("confirmed") is not None:
                confirmed += 1
        except Exception:
            pass
    systems.append({
        "id": "3l0", "name": "3L0",
        "record_of_record": {
            "kind": "feed",
            "path": "ops/telemetry/session-history-3l0.jsonl",
            "note": "Staged intake (3l0-intake/v1) from the session-history "
                    "plane; observational fold - weights derive only "
                    "where confirmed != null (charter source class 2)."},
        "headline": {"staged_records": len(l30_lines),
                     "confirmed_non_null": confirmed,
                     "observational": True},
        "as_of": now})

    # --- Temporal ---
    temporal = {"id": "temporal", "name": "Temporal",
                "record_of_record": {
                    "kind": "actions-runs",
                    "ref": "Actions run receipts: temporal-engagement.yml "
                           "+ temporal-self-host-smoke.yml",
                    "note": "No results feed exists for Temporal; the run "
                            "receipts are the record of record."},
                "headline": {}, "as_of": now}
    if args.temporal_json:
        temporal["headline"] = json.load(open(args.temporal_json))
    else:
        try:
            if not token:
                raise RuntimeError("no token")
            temporal["headline"] = {
                "engagement": _runs("temporal-engagement.yml", token),
                "self_host_smoke": _runs("temporal-self-host-smoke.yml", token)}
        except Exception:
            temporal["headline"] = {"state": "NOT_ESTABLISHED_THIS_RUN",
                                    "reason": "Actions API unavailable at build"}
    systems.append(temporal)

    # --- HindSight ---
    proof = _load(args.root, "ops/telemetry/hindsight-retain-proof.json") or {}
    state = _load(args.root, "ops/telemetry/hindsight-retain-state.json") or {}
    systems.append({
        "id": "hindsight", "name": "HindSight",
        "record_of_record": {
            "kind": "receipts",
            "path": "ops/telemetry/hindsight-retain-proof.json + "
                    "ops/telemetry/hindsight-retain-state.json",
            "note": "Retain receipts are the population record; the bank "
                    "itself is verified via the gated verify step when "
                    "the proof passes."},
        "headline": {"payloads": proof.get("payloads"),
                     "proof_attempted": proof.get("attempted"),
                     "proof_ok": proof.get("ok"),
                     "retained_units": len(state),
                     "last_error_status": (proof.get("first_error") or {})
                     .get("status")},
        "as_of": now})

    doc = {"schema": SCHEMA, "generated_at": now, "systems": systems,
           "consumer": "viz all-4 results index page (render verbatim)"}
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)

    if args.viz_out:
        by_id = {s["id"]: s for s in systems}
        corpus = len(_lines(args.root, "ops/telemetry/session-history.jsonl"))
        ates_h = by_id["ates"]["headline"]
        ates_w = {w["file"].split("/")[-1]: w
                  for w in ates_h.get("workflows", [])}

        def row(label, state, record, at):
            return {"label": label, "state": state,
                    "record_of_record": record, "at": at}

        sections = [
            {"id": "ates", "name": "ATES", "generated_at": now,
             "note": by_id["ates"]["record_of_record"].get("note"),
             "rows": [
                 row("receipt runs",
                     ates_w.get("ates-phase-b-run-receipt.yml", {}).get("total_runs"),
                     "apps/tribute-dashboard/data/ates-feed.json",
                     ates_w.get("ates-phase-b-run-receipt.yml", {}).get("latest_at")),
                 row("benchmark runs",
                     ates_w.get("ates-orchestrator-benchmark.yml", {}).get("total_runs"),
                     "apps/tribute-dashboard/data/ates-feed.json",
                     ates_w.get("ates-orchestrator-benchmark.yml", {}).get("latest_at")),
                 row("governance/frame state",
                     f"{len(ates_h.get('invariants') or [])} invariants",
                     "apps/tribute-dashboard/data/ates-feed.json",
                     ates_h.get("feed_generated_at"))]},
            {"id": "3l0", "name": "3L0", "generated_at": now,
             "note": by_id["3l0"]["record_of_record"].get("note"),
             "rows": [
                 row("staged intake records",
                     by_id["3l0"]["headline"].get("staged_records"),
                     "ops/telemetry/session-history-3l0.jsonl", now),
                 row("confirmed (weights-eligible)",
                     by_id["3l0"]["headline"].get("confirmed_non_null"),
                     "ops/telemetry/session-history-3l0.jsonl", now),
                 row("routed-dispatch stamp corpus",
                     corpus, "ops/telemetry/session-history.jsonl", now)]},
            {"id": "temporal", "name": "Temporal", "generated_at": now,
             "note": by_id["temporal"]["record_of_record"].get("note"),
             "rows": [
                 row("engagement runs",
                     (by_id["temporal"]["headline"].get("engagement") or {})
                     .get("total_count"),
                     "Actions: temporal-engagement.yml",
                     ((by_id["temporal"]["headline"].get("engagement") or {})
                      .get("latest") or {}).get("at")),
                 row("self-host smoke runs",
                     (by_id["temporal"]["headline"].get("self_host_smoke") or {})
                     .get("total_count"),
                     "Actions: temporal-self-host-smoke.yml",
                     ((by_id["temporal"]["headline"].get("self_host_smoke") or {})
                      .get("latest") or {}).get("at")),
                 row("persistent instance", "none",
                     "Actions: temporal-engagement.yml", now)]},
            {"id": "hindsight", "name": "HindSight", "generated_at": now,
             "note": by_id["hindsight"]["record_of_record"].get("note"),
             "rows": [
                 row("receipts on record",
                     f"proof attempted {by_id['hindsight']['headline'].get('proof_attempted')}"
                     f" - ok {by_id['hindsight']['headline'].get('proof_ok')}"
                     f" - last error {by_id['hindsight']['headline'].get('last_error_status')}",
                     "ops/telemetry/hindsight-retain-proof.json", now),
                 row("retained population",
                     by_id["hindsight"]["headline"].get("retained_units"),
                     "ops/telemetry/hindsight-retain-state.json", now)]},
        ]
        viz = {"schema": "results-index-feed/v1", "generated_at": now,
               "sections": sections,
               "source": "ops/telemetry/results-index.json (same builder, "
                         "same values - render presentation)"}
        with open(args.viz_out, "w", encoding="utf-8") as fh:
            json.dump(viz, fh, indent=1, sort_keys=True)

    print(json.dumps({"systems": [s["id"] for s in systems],
                      "generated_at": now}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
