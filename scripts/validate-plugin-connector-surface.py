#!/usr/bin/env python3
"""Validate the checked-in live connector surface registry.

This validates repository data only. It does not claim that provider credentials
or runtime authorization are healthy; live authorization must be established
by the connector steward and recorded separately.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / ".github" / "connectors" / "runtime-surface.json"

data = json.loads(REGISTRY.read_text(encoding="utf-8"))
providers = data["providers"]

assert data["provider_count"] == len(providers), "provider_count mismatch"
assert data["action_count"] == sum(p["action_count"] for p in providers), "action_count mismatch"
assert len({p["provider"] for p in providers}) == len(providers), "duplicate provider"
assert all(p["action_count"] > 0 for p in providers), "empty provider action count"

all_actions = []
for provider in providers:
    assert provider["initialization_owner"], f"missing owner: {provider['provider']}"
    assert provider["validation_owner"], f"missing validation owner: {provider['provider']}"
    assert provider["handoff"], f"missing handoff: {provider['provider']}"
    for action in provider["sample_actions"]:
        all_actions.append(action)
assert len(all_actions) == len(set(all_actions)), "duplicate sample action"

print(
    f"connector surface registry OK: "
    f"{data['provider_count']} providers / {data['action_count']} actions"
)
