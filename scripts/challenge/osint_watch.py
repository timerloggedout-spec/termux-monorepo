#!/usr/bin/env python3
"""Challenge full-spectrum OSINT watch (public sources only).

Contract: docs/ops/CHALLENGE-OSINT.md. Reads ops/challenge/coordinator.json,
(1) computes the coverage matrix (entity x event x populated) into
ops/challenge/osint/coverage.json, and (2) fetches each event's official
public page, hashes its text, and APPENDS a snapshot to
ops/challenge/osint/snapshots.json when the hash is new (prize/rules/
schedule changes surface as hash changes + excerpt diffs in the run log).
Snapshots are append-only; a failed fetch appends nothing and is reported.
Every coverage fact derives from the coordinator record at run time;
gaps stay NOT_ESTABLISHED — nothing is inferred.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re, sys, urllib.request
from datetime import date
from pathlib import Path

def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "challenge-osint-watch/1.0 (public page check)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode("utf-8", "replace")
    raw = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", raw)
    text = re.sub(r"<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def excerpt(text: str) -> str:
    hits = [m.start() for m in re.finditer(r"(prize|award|\$\s?\d)", text, re.I)]
    if not hits:
        return ""
    s = max(0, hits[0] - 80)
    return text[s:s + 400]

def coverage_of(ev: dict) -> dict:
    parts = ev.get("participants") or []
    judges = ev.get("judges") or []
    def signals(rows):
        return sum(1 for r in rows if isinstance(r, dict) and (r.get("signals") or r.get("past_wins") or r.get("snapshots")))
    return {
        "organizers": {"populated": bool(ev.get("organizers")), "count": len(ev.get("organizers") or [])},
        "dates": {"populated": any(isinstance(v, dict) for v in (ev.get("dates") or {}).values()), "count": sum(1 for v in (ev.get("dates") or {}).values() if isinstance(v, dict))},
        "prizes": {"populated": (ev.get("prizes") or {}).get("status") == "ESTABLISHED", "status": (ev.get("prizes") or {}).get("status", "NOT_ESTABLISHED"), "tiers": len((ev.get("prizes") or {}).get("tiers") or [])},
        "rules_constraints": {"populated": bool(ev.get("constraints")), "count": len(ev.get("constraints") or [])},
        "our_projects": {"populated": bool(ev.get("projects")), "count": len(ev.get("projects") or [])},
        "competitor_projects_participants": {"populated": bool(parts), "count": len(parts)},
        "judges": {"populated": bool(judges), "count": len(judges)},
        "entity_signals": {"populated": signals(parts + judges) > 0, "count": signals(parts + judges)},
        "recruitment": {"populated": any(isinstance(r, dict) and r.get("recruitment") for r in parts + judges), "count": sum(1 for r in parts + judges if isinstance(r, dict) and r.get("recruitment"))},
        "opportunity_cost": {"populated": bool(ev.get("opportunity_cost")), "ledger_entry": (ev.get("opportunity_cost") or {}).get("ledger_entry")},
        "field_size": {"status": (ev.get("field_size") or {}).get("status", "open_task"), "participants": (ev.get("field_size") or {}).get("participants"), "projects": (ev.get("field_size") or {}).get("projects")},
        "official_page_watch": {"populated": bool(ev.get("official_url")), "url": ev.get("official_url")},
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--no-fetch", action="store_true", help="coverage only (offline)")
    ns = ap.parse_args()
    root = Path(ns.root)
    coord = json.loads((root / "ops/challenge/coordinator.json").read_text())
    osint_dir = root / "ops/challenge/osint"
    osint_dir.mkdir(parents=True, exist_ok=True)
    snap_path = osint_dir / "snapshots.json"
    snaps = json.loads(snap_path.read_text()) if snap_path.exists() else {"schema": "challenge-osint-snapshots/v1", "snapshots": []}
    today = date.today().isoformat()
    matrix, changes = {}, []
    for ev in coord.get("events", []):
        eid = ev.get("id")
        matrix[eid] = coverage_of(ev)
        url = ev.get("official_url")
        if url and not ns.no_fetch:
            try:
                text = fetch_text(url)
            except Exception as exc:  # never fail the watch on one page
                print(f"::warning title=osint::{eid} fetch failed: {type(exc).__name__}")
                matrix[eid]["official_page_watch"]["fetch_status"] = f"failed:{type(exc).__name__}"
                continue
            digest = hashlib.sha256(text.encode()).hexdigest()
            seen = [s for s in snaps["snapshots"] if s.get("event") == eid]
            matrix[eid]["official_page_watch"]["fetch_status"] = "ok"
            matrix[eid]["official_page_watch"]["last_sha256"] = digest[:16]
            if not seen or seen[-1].get("sha256") != digest:
                snaps["snapshots"].append({"event": eid, "url": url, "fetched_at": today, "sha256": digest, "prize_excerpt": excerpt(text)})
                changes.append(eid)
                print(f"osint: {eid} page snapshot appended (change or baseline) sha {digest[:12]}")
    coverage = {"schema": "challenge-osint-coverage/v1", "generated_at": today,
                "source": "ops/challenge/coordinator.json at run time; public official pages for snapshots",
                "events": matrix,
                "summary": {
                    "events": len(matrix),
                    "participants_total": sum(v["competitor_projects_participants"]["count"] for v in matrix.values()),
                    "judges_total": sum(v["judges"]["count"] for v in matrix.values()),
                    "prizes_established": sum(1 for v in matrix.values() if v["prizes"]["populated"]),
                    "page_snapshots_total": len(snaps["snapshots"]),
                    "page_changes_this_run": changes}}
    (osint_dir / "coverage.json").write_text(json.dumps(coverage, indent=2) + "\n")
    snap_path.write_text(json.dumps(snaps, indent=2) + "\n")
    print(f"osint: coverage for {len(matrix)} events; snapshots {len(snaps['snapshots'])}; changes {changes}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
