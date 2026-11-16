#!/usr/bin/env python3
"""[MUSEai]@{role:{appid-migration-plan}} — emit data.sql (idempotent upserts)
from the filed dry-run inventory JSON. Stdlib only; deterministic."""
import json, sys

def lit(v):
    if v is None: return "NULL"
    if isinstance(v, bool): return "true" if v else "false"
    if isinstance(v, (int, float)): return str(v)
    if isinstance(v, (dict, list)): return "'" + json.dumps(v).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"

inv = json.load(open(sys.argv[1]))
out = []
for a in inv["apps"]:
    out.append(
        "INSERT INTO appid_cp_apps (app_id, slug, role, installation_id, account, repository_selection, custody_ref, sec03_pair_present, observed_at) VALUES ("
        + ", ".join([lit(a["app_id"]), lit(a["slug"]), lit(a["role"]), lit(a["installation_id"]), lit(a["account"]),
                     lit(a["repository_selection"]), lit(a["custody_ref"]), lit(str(a["sec03_pair_present"])), lit(a["observed_at"])])
        + ") ON CONFLICT (app_id) DO UPDATE SET installation_id=EXCLUDED.installation_id, repository_selection=EXCLUDED.repository_selection, sec03_pair_present=EXCLUDED.sec03_pair_present, observed_at=EXCLUDED.observed_at;")
    out.append(
        "INSERT INTO appid_cp_permission_snapshots (app_id, declared, observed, drift, observed_at, probe_ref) VALUES ("
        + ", ".join([lit(a["app_id"]), lit(a["declared"]), lit(a["observed"]), lit(a["drift"]), lit(a["observed_at"]),
                     lit("custody-helper probe " + inv["generated_at"])])
        + ");")
waves = [
    ("MIG-01", "skipped", "repository-observatory = user-identity surface (NOT migratable)"),
    ("MIG-02", "migrated", "reviewer-metrics-collect reads on Collector token (PR #2446)"),
    ("MIG-03", "skipped", "Delphi feed collectors on per-repo bucket; traffic-feed NOT migratable"),
    ("MIG-04", "skipped", "provider-availability has no GitHub probe portion"),
    ("MIG-05", "skipped", "recon/observer class on per-repo bucket"),
    ("MIG-06", "skipped", "workflow writes on per-repo bucket; Publisher adoption optional"),
    ("MIG-07", "migrated", "Publisher-token publish+merge path proven (PR #2472); rollout per-lane opt-in"),
    ("MIG-08", "skipped", "peer-review-orchestrator: operator steps identity-bound by design"),
    ("MIG-09", "skipped", "repo-gate verdicts are its own job check-runs (Actions identity)"),
    ("MIG-10", "skipped", "issue-lifecycle/proposal-lifecycle on Actions job token"),
    ("MIG-11", "blocked", "per-item calls/run into quota registry — open, quota lane"),
    ("MIG-RR-01", "blocked", "HELD: repo-replay own-repo build; monorepo read-only until validated + submoduled"),
    ("MIG-RR-02", "migrated", "Publisher installation extended to repo-replay; route exercised, PAT calls = 0"),
]
for w, s, n in waves:
    out.append("INSERT INTO appid_cp_migration_waves (wave_id, state, items_ref, note) VALUES ("
               + ", ".join([lit(w), lit(s), lit("ops/github-apps/MIGRATION-ITEMS.md"), lit(n)])
               + ") ON CONFLICT (wave_id) DO UPDATE SET state=EXCLUDED.state, note=EXCLUDED.note;")
receipt = {"token_source": "per-App custody helpers (JWT -> installation), zero write tokens",
           "identities": "8 AppIDs (PROCESS.json SSOT)", "method": inv["method"],
           "fleet_drift": inv["fleet_drift"], "artifact": "inventory-2026-11-03.json"}
out.append("INSERT INTO appid_cp_replay_runs (run_id, wave_id, snapshot_ref, classification, receipt) VALUES ("
           + ", ".join([lit("inventory-dry-run-2026-11-03"), lit("MIG-01..11+RR"), lit("inventory-2026-11-03.json"),
                        lit("MATCH" if inv["fleet_drift"] == "none" else "DRIFT"), lit(receipt)])
           + ") ON CONFLICT (run_id) DO NOTHING;")
print("\n".join(out))
