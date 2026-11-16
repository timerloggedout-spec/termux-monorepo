#!/usr/bin/env python3
"""Podium load — dataset JSON -> Neon insert SQL (append-only tables).

[MUSEai]@{role:{scraping-tools}}

Emits idempotent SQL (ON CONFLICT DO NOTHING) for podium_crawls,
podium_observations, podium_conflicts from a podium-dataset/v1 file.
The workflow applies it with psql when LANE_EVENTS_DATABASE_URL is
provisioned; without the secret the step DEFERs (prints, writes nothing).
Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys


def lit(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def jsonb(obj) -> str:
    return lit(json.dumps(obj, ensure_ascii=False)) + "::jsonb"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Podium dataset -> SQL")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    ds = json.load(open(args.dataset, encoding="utf-8"))
    version = ds["version"]
    crawl_key = hashlib.sha256(version.encode()).hexdigest()
    counts = {}
    for e in ds["entities"].values():
        counts[e["kind"]] = counts.get(e["kind"], 0) + 1

    lines = ["BEGIN;"]
    lines.append(
        "INSERT INTO podium_crawls (crawl_key, version, captured_at, collector, counts) "
        f"VALUES ({lit(crawl_key)}, {lit(version)}, "
        f"{lit(ds['generated_from']['snapshot_captured_at'])}::timestamptz, "
        f"{lit(ds['generated_from']['collector'])}, {jsonb(counts)}) "
        "ON CONFLICT (crawl_key) DO NOTHING;"
    )
    for key, e in ds["entities"].items():
        obs_key = hashlib.sha256(
            f"{crawl_key}|{key}|{e['content_hash']}".encode()).hexdigest()
        lines.append(
            "INSERT INTO podium_observations "
            "(obs_key, crawl_key, entity_key, kind, fields, content_hash, receipts) "
            f"VALUES ({lit(obs_key)}, {lit(crawl_key)}, {lit(key)}, {lit(e['kind'])}, "
            f"{jsonb(e['fields'])}, {lit(e['content_hash'])}, {jsonb(e['receipts'])}) "
            "ON CONFLICT (crawl_key, entity_key) DO NOTHING;"
        )
    for c in ds["conflicts"]:
        ck = hashlib.sha256(
            f"{crawl_key}|{c['entity']}|{c['field']}|{json.dumps(c['values'], sort_keys=True)}"
            .encode()).hexdigest()
        lines.append(
            "INSERT INTO podium_conflicts "
            "(conflict_key, crawl_key, entity_key, field, values, receipts, note) "
            f"VALUES ({lit(ck)}, {lit(crawl_key)}, {lit(c['entity'])}, {lit(c['field'])}, "
            f"{jsonb(c['values'])}, {jsonb(c.get('receipts', []))}, "
            f"{lit(c.get('note', ''))}) ON CONFLICT (conflict_key) DO NOTHING;"
        )
    lines.append("COMMIT;")
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"sql: crawls=1 observations={len(ds['entities'])} "
          f"conflicts={len(ds['conflicts'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
