#!/usr/bin/env python3
"""Backup-state record — the dashboard records the backups (owner order
2026-11-01; spec: docs/ops/BACKUP-STATE.md, schema backup-state/v1).

METADATA ONLY: export history {id, at, T0/T1 counts, state hash},
drill verdicts, and the current marker. No file paths, no manifest
content, no backup content of any kind.

Sources (all committed; the generator is offline):
  1. relays   ops/tracking/backup-relays.jsonl — export outcomes
              relayed from the hook runs that perform the exports
              (state hash + publish commit live only there / VM-side).
  2. snapshot scripts/tracking/backup_snapshot.json — stamped API read
              of the private backup repo (EXPORT.json extract + drill
              reports + export commits), refreshed by
              fetch_snapshots.py when a token can reach that repo;
              fail-soft: a failed refresh keeps the last-good data and
              records its status.
Single-writer: repo-tracking-collect.yml. Outputs:
ops/tracking/backup-state.json +
apps/help-wanted-dashboard/data/backup-state-feed.json (byte-identical).
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = "backup-state/v1"
NOT_ESTABLISHED = "NOT_ESTABLISHED"
_EXPORT_MSG = re.compile(r"export\s+(exp-\S+)\s+t0=(\d+)\s+t1=(\d+)")


def _iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _blank_export(export_id: str) -> dict:
    return {"id": export_id, "at": None, "t0": None, "t1": None,
            "manifest_only": None, "excluded": None, "bytes": None,
            "gates_pass": None, "publish_commit": None, "state_hash": None}


def build(base=None, now=None) -> dict:
    base = base or ROOT
    now = now or datetime.now(timezone.utc)
    gaps: list[str] = []
    exports: dict[str, dict] = {}

    def merge(export_id, **fields):
        if not export_id:
            return
        row = exports.setdefault(export_id, _blank_export(export_id))
        for k, v in fields.items():
            if v is not None and row.get(k) is None:
                row[k] = v

    # --- source 2: backup-repo snapshot (API extract) ---
    snap = _read_json(base / "scripts" / "tracking" / "backup_snapshot.json")
    snap_status = None
    n_drills = 0
    drills: list[dict] = []
    if isinstance(snap, dict):
        snap_status = snap.get("status")
        ex = snap.get("export") or {}
        counts = ex.get("counts") or {}
        merge(ex.get("export_id"), at=ex.get("exported_at"),
              t0=counts.get("t0"), t1=counts.get("t1"),
              manifest_only=counts.get("manifest_only"),
              excluded=counts.get("excluded"), bytes=counts.get("bytes"),
              gates_pass=(ex.get("gates") or {}).get("pass"))
        for c in snap.get("commits", []) or []:
            msg = c.get("message") or ""
            m = _EXPORT_MSG.search(msg)
            if m:
                merge(m.group(1), publish_commit=c.get("sha"),
                      t0=int(m.group(2)), t1=int(m.group(3)), at=c.get("at"))
        for d in snap.get("drills", []) or []:
            drills.append({
                "report": d.get("report"), "export_id": d.get("export_id"),
                "verdict": d.get("verdict"),
                "t0": {"checked": d.get("checked"), "mismatched": d.get("mismatched"),
                       "excluded_absent": d.get("excluded_absent")},
                "t1": {"checked": d.get("t1_checked"), "consistent": d.get("t1_consistent"),
                       "missing": d.get("t1_missing")},
                "restored_bytes": d.get("restored_bytes"), "mode": d.get("mode"),
            })
            n_drills += 1
        if snap_status not in ("ok", None):
            gaps.append(f"backup snapshot refresh status={snap_status} "
                        f"(read_at {snap.get('read_at')}): data may be stale; relays remain live")
    else:
        gaps.append("backup snapshot absent: no API extract committed yet (relay-only record)")

    # --- source 1: relays from the hook runs ---
    rpath = base / "ops" / "tracking" / "backup-relays.jsonl"
    relays = []
    if rpath.exists():
        for line in rpath.read_text().splitlines():
            if line.strip():
                try:
                    relays.append(json.loads(line))
                except Exception:
                    continue
    marker = {"state_hash": NOT_ESTABLISHED, "export_id": None, "source": NOT_ESTABLISHED}
    for r in relays:
        if r.get("kind") == "export":
            merge(r.get("export_id"), at=r.get("at"),
                  publish_commit=r.get("publish_commit"),
                  state_hash=r.get("state_hash"),
                  t0=r.get("t0"), t1=r.get("t1"))
    export_relays = [r for r in relays if r.get("kind") == "export" and r.get("state_hash")]
    if export_relays:
        last = export_relays[-1]
        marker = {"state_hash": last.get("state_hash"),
                  "export_id": last.get("export_id"), "source": "relay"}
    else:
        gaps.append("marker state hash NOT_ESTABLISHED: no export relay carries one yet "
                    "(marker lives VM-side; hook-run relays populate it)")

    rows = sorted(exports.values(), key=lambda e: str(e.get("at") or ""), reverse=True)
    drills.sort(key=lambda d: str(d.get("export_id") or ""), reverse=True)
    return {
        "schema": SCHEMA,
        "generated_at": _iso(now),
        "generated_by": "scripts/tracking/backup_state.py via repo-tracking-collect.yml (single-writer)",
        "spec": {"doc": "docs/ops/BACKUP-STATE.md",
                 "metadata_only": "counts, hashes, verdicts — never file paths or backup content"},
        "sources": [
            {"id": "relays", "path": "ops/tracking/backup-relays.jsonl", "records": len(relays)},
            {"id": "snapshot", "path": "scripts/tracking/backup_snapshot.json",
             "status": snap_status, "read_at": snap.get("read_at") if isinstance(snap, dict) else None},
        ],
        "marker": marker,
        "exports": rows,
        "drills": drills,
        "summary": {
            "exports": len(rows), "drills": len(drills),
            "last_export_at": rows[0].get("at") if rows else None,
            "last_export_id": rows[0].get("id") if rows else None,
            "last_drill_verdict": drills[0].get("verdict") if drills else None,
        },
        "gaps": gaps,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="build in memory only, print summary")
    ns = ap.parse_args()
    feed = build()
    if ns.check:
        print(json.dumps(feed["summary"], indent=1))
        print("gaps:", len(feed["gaps"]))
        return 0
    out = json.dumps(feed, indent=1, sort_keys=False) + "\n"
    (ROOT / "ops" / "tracking").mkdir(parents=True, exist_ok=True)
    (ROOT / "ops" / "tracking" / "backup-state.json").write_text(out)
    dash = ROOT / "apps" / "help-wanted-dashboard" / "data"
    dash.mkdir(parents=True, exist_ok=True)
    (dash / "backup-state-feed.json").write_text(out)
    print(f"backup-state: exports={feed['summary']['exports']} drills={feed['summary']['drills']} "
          f"gaps={len(feed['gaps'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
