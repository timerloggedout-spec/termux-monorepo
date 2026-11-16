#!/usr/bin/env python3
"""VM workspace backup events -> Telemetry MEASUREMENT records.

Owner direction 2026-11-01: backup events become telemetry measurement
records {state_hash, export_id, publish_commit (backup repo), relay_commit
(monorepo), at}, joined to the monorepo commit stream by hash + time so
backup state is correlatable with the commit stream like every other
plane.

Source of record = Tracking lane's feed `ops/tracking/backup-relays.jsonl`
(backup-state/v1; the dashboard render source — telemetry READS it as
intake, never forks its numbers). Output = append-only
`ops/telemetry/backup-measurements.jsonl` (schema backup-measurement/v1),
immutable intake per DoE rule 8: idempotent on evidence_hash (sha256 of
the canonical source line); existing records are never rewritten.

relay_commit resolution: the monorepo commit that appended the source
line (commits API, path-filtered, oldest-append order). Resolved once,
then carried in the record forever. When the API is unavailable the
record ships with relay_commit = null + join state noted, and a later
run back-resolves it by APPENDING nothing — resolution only happens for
records not yet emitted (immutability wins over completeness).

Usage: backup_events.py --relays ops/tracking/backup-relays.jsonl
         --out ops/telemetry/backup-measurements.jsonl
         --receipt ops/telemetry/backup-measurements-receipt.json
         [--relay-map relay_map.json]   # {line_index: relay_sha}
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request

SCHEMA = "backup-measurement/v1"
REPO = "timerloggedout-spec/termux-monorepo"
RELAYS_PATH = "ops/tracking/backup-relays.jsonl"


def evidence_hash(line: str) -> str:
    return hashlib.sha256(line.strip().encode("utf-8")).hexdigest()


def _api(path: str, token: str):
    """API GET via the gh CLI when available (runner-native auth/UA),
    else urllib. Raises on failure - callers must NOT swallow silently
    (v1.2: the v1.1 in-run resolution failed silently to an empty map;
    errors now surface in the step log and the receipt)."""
    import subprocess
    try:
        out = subprocess.run(
            ["gh", "api", path.lstrip("/")],
            capture_output=True, text=True, timeout=90)
        if out.returncode == 0:
            return json.loads(out.stdout)
        raise RuntimeError(f"gh api failed: {out.stderr.strip()[:160]}")
    except FileNotFoundError:
        pass
    req = urllib.request.Request("https://api.github.com" + path, method="GET")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "telemetry-ingest-backup-events")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.build_opener().open(req, timeout=60) as resp:
        return json.loads(resp.read())


def resolve_relay_map(token: str) -> dict:
    """{line_index: relay_commit_sha} from the commits that touched the
    relays file, oldest first (each append commit adds its line)."""
    commits = _api(f"/repos/{REPO}/commits?path={RELAYS_PATH}&per_page=100",
                   token)
    out = {}
    for i, c in enumerate(reversed(commits)):
        out[i] = c["sha"]
    return out


def resolve_line_relays(token: str, intake_path: str, lines: list,
                        passthrough_lines: list) -> dict:
    """v1.1 per-LINE relay resolution for the unified events intake:
    passthrough lines (byte-identical to relays lines) inherit the
    relays append-commit map by line identity; native lines resolve by
    patch-match - the commit whose diff on the intake path adds that
    exact line. Returns {line_index_in_intake: relay_sha}."""
    out = {}
    by_text = {}
    idx_map = resolve_relay_map(token)
    for i, text in enumerate(passthrough_lines):
        if i in idx_map:
            by_text[text] = idx_map[i]
    native = []
    for i, line in enumerate(lines):
        if line in by_text:
            out[i] = by_text[line]
        else:
            native.append(i)
    if native:
        commits = _api(
            f"/repos/{REPO}/commits?path={intake_path}&per_page=100", token)
        added = {}  # line text -> sha (first/oldest introducing commit)
        for c in reversed(commits):
            full = _api(f"/repos/{REPO}/commits/{c['sha']}", token)
            for f in full.get("files", []):
                if f["filename"] != intake_path:
                    continue
                for pl in (f.get("patch") or "").splitlines():
                    if pl.startswith("+") and not pl.startswith("+++"):
                        added.setdefault(pl[1:], c["sha"])
        for i in native:
            if lines[i] in added:
                out[i] = added[lines[i]]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--relays", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--relay-map")
    ap.add_argument("--join-out",
                    help="also write the derived join sidecar (relay_commit "
                         "per evidence_hash for all records) at this path")
    ap.add_argument("--passthrough",
                    help="relays file whose lines pass through byte-identical "
                         "into the intake (v1.1 unified events intake)")
    ap.add_argument("--relays-repo-path", default=RELAYS_PATH,
                    help="repo path of the intake file (for patch-match)")
    ap.add_argument("--mode", default="live", choices=["live", "backfill"])
    args = ap.parse_args()

    lines = [l for l in open(args.relays, encoding="utf-8").read().splitlines()
             if l.strip()]
    existing = []
    if os.path.exists(args.out):
        existing = [json.loads(l) for l in open(args.out, encoding="utf-8")
                    if l.strip()]
    have = {r["evidence_hash"] for r in existing}

    relay_map = {}
    resolution_error = None
    if args.relay_map:
        relay_map = {int(k): v for k, v in
                     json.load(open(args.relay_map)).items()}
    else:
        token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
        if token:
            try:
                if args.passthrough and os.path.exists(args.passthrough):
                    pt = [l for l in open(args.passthrough, encoding="utf-8")
                          .read().splitlines() if l.strip()]
                    relay_map = resolve_line_relays(
                        token, args.relays_repo_path, lines, pt)
                else:
                    relay_map = resolve_relay_map(token)
            except Exception as exc:  # surface, never swallow (v1.2)
                resolution_error = f"{type(exc).__name__}: {exc}"[:200]
                print(f"::warning::relay resolution failed: {resolution_error}",
                      file=sys.stderr)
                relay_map = {}

    new = []
    for i, line in enumerate(lines):
        eh = evidence_hash(line)
        if eh in have:
            continue
        src = json.loads(line)
        rec = {
            "schema": SCHEMA,
            "kind": src.get("kind"),
            "at": src.get("at"),
            "state_hash": src.get("state_hash"),
            "export_id": src.get("export_id"),
            "publish_commit": src.get("publish_commit"),
            "publish_repo": ("timerloggedout-spec/muse-vm-workspace-backup"
                             if src.get("publish_commit") else None),
            "relay_commit": relay_map.get(i),
            "relay_repo": REPO,
            "join": {
                "by": "relay_commit (append commit) + at (event time)",
                "relay_resolved": i in relay_map,
                "stream": "monorepo master commits",
            },
            "origin": f"{args.mode}{{backup-events}}",
            "evidence_hash": eh,
        }
        new.append(rec)

    if new:
        with open(args.out, "a", encoding="utf-8") as fh:
            for rec in new:
                fh.write(json.dumps(rec, sort_keys=True) + "\n")
    total = existing + new
    receipt = {
        "schema": SCHEMA,
        "source_feed": args.relays_repo_path,
        "source_owner": "tracking lane (backup-state/v1 render source)",
        "records_total": len(total),
        "records_new": len(new),
        "by_kind": {},
        "relay_resolved": sum(1 for r in total
                              if r["join"]["relay_resolved"]),
        "with_publish_commit": sum(1 for r in total if r["publish_commit"]),
        "resolution_error": resolution_error,
    }
    if args.join_out:
        # Derived join sidecar (regenerable, NOT intake): resolves the
        # relay_commit for EVERY record in --out at build time, including
        # records emitted earlier with relay_resolved=false. Records
        # themselves stay immutable; consumers join via evidence_hash.
        join = {}
        src_lines = [l for l in open(args.relays, encoding="utf-8")
                     .read().splitlines() if l.strip()]
        by_hash = {}
        for i, l in enumerate(src_lines):
            sha = relay_map.get(i)
            if sha:
                by_hash[evidence_hash(l)] = sha
        for r in total:
            sha = r.get("relay_commit") or by_hash.get(r["evidence_hash"])
            if sha:
                join[r["evidence_hash"]] = {
                    "relay_commit": sha, "at": r["at"], "kind": r["kind"]}
        with open(args.join_out, "w", encoding="utf-8") as fh:
            json.dump({"schema": "backup-measurements-join/v1",
                       "records_joined": len(join), "join": join},
                      fh, indent=1, sort_keys=True)
        receipt["join_sidecar_records"] = len(join)
    for r in total:
        receipt["by_kind"][r["kind"]] = receipt["by_kind"].get(r["kind"], 0) + 1
    with open(args.receipt, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
    print(json.dumps(receipt, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
