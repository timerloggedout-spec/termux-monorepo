#!/usr/bin/env python3
"""Validate names-only credential inventory for issue #184."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "ops" / "credential-surfaces.jsonl"
SCHEMA = ROOT / "schemas" / "ops" / "credential-surface.schema.json"
FORBIDDEN = {
    "value",
    "token",
    "secret",
    "password",
    "api_key",
    "private_key",
    "authorization",
    "key_material",
    "pat_value",
}
REQUIRED = {
    "surface_id",
    "name",
    "class",
    "owner_surface",
    "last_used_class",
    "intended_use",
    "rotation_status",
    "issue",
    "observed_at",
}
CLASSES = {
    "actions_secret",
    "fine_grained_pat",
    "classic_pat",
    "oauth_app",
    "github_app",
    "ssh_key",
    "device_keyring",
}
LAST_USED = {"never", "week", "two_weeks", "month", "quarter", "expired", "unknown"}
ROTATION = {
    "active",
    "rotate",
    "delete",
    "expired_delete",
    "unused_candidate_delete",
}


def load_rows(path: Path):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append((n, json.loads(line)))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{n}: invalid JSON: {exc}") from exc
    return rows


def validate() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if schema.get("title") != "Names-only credential surface":
        raise SystemExit("schema title mismatch")
    seen = set()
    for n, row in load_rows(DATA):
        extra_forbidden = FORBIDDEN.intersection(row)
        if extra_forbidden:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: forbidden fields {sorted(extra_forbidden)}")
        missing = REQUIRED.difference(row)
        if missing:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: missing {sorted(missing)}")
        if row["surface_id"] in seen:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: duplicate surface_id")
        seen.add(row["surface_id"])
        if row["class"] not in CLASSES:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: invalid class")
        if row["last_used_class"] not in LAST_USED:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: invalid last_used_class")
        if row["rotation_status"] not in ROTATION:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: invalid rotation_status")
        if row["issue"] != 184:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: issue must be 184")
        blob = json.dumps(row)
        if "ghp_" in blob or "github_pat_" in blob or "sk-" in blob:
            raise SystemExit(f"credential-surfaces.jsonl:{n}: looks like secret material")
    if len(seen) < 4:
        raise SystemExit("inventory too small to be useful")
    print(f"credential inventory validation: OK ({len(seen)} surfaces)")


def main() -> None:
    validate()


if __name__ == "__main__":
    main()
