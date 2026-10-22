#!/usr/bin/env python3
"""Offline contract checks for the declarative GitLab integration registry."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "docs/ops/gitlab-integration-catalog.json").read_text())
doc = (ROOT / "docs/ops/GITLAB-INTEGRATION-CATALOG.md").read_text()
items = (ROOT / "docs/proposals/active/actions-refinements/ITEMS.md").read_text()
assert data["schema_version"] == "gitlab-integration-catalog.v1"
assert data["budget_policy"]["pooling"] is False
assert data["budget_policy"]["quota_bypass"] is False
assert data["reconciliation_authority"]["document"] == "docs/ops/GITHUB-GITLAB-GOVERNED-RECONCILIATION.md"
authority = (ROOT / data["reconciliation_authority"]["document"]).read_text()
assert "GitHub `master` is the canonical promotion spine" in authority
assert "never force-pushes" in authority and "auto-merges" in authority
entries = {x["id"]: x for x in data["integrations"]}
mcp = entries["gitlab-mcp"]
assert mcp["endpoint"] == "https://gitlab.com/api/v4/mcp"
assert mcp["auth"]["scope"] == "mcp" and mcp["auth"]["legacy_pat"] == "not_supported"
for entry in [*entries.values(), *data["optional_quota_service_candidates"]]:
    assert entry["enabled"] is False
    if "approval_required" in entry:
        assert entry["approval_required"] is True
    assert entry["cost_status"] == "cost_unknown"
duo = entries["gitlab-duo-cli"]
assert duo["entitlement"] == "unknown_for_this_account"
complements = data["optional_quota_service_candidates"]
assert {x["id"] for x in complements} == {"openrouter", "google-ai-studio-gemini"}
assert all(x["catalog_state"] == "existing_repo_provider" for x in complements)
assert all("not a new service" in x["role"] for x in complements)
assert all("cap bypass" in x["budget_boundary"] for x in complements)
additional = data["additional_capacity_options"]
assert {x["id"] for x in additional} == {"cerebras", "cloudflare-workers-ai"}
assert all(x["catalog_state"] == "existing_documented_candidate_without_verified_account" for x in additional)
assert all(x["status"] == "requires_account_verification_and_budget_approval" for x in additional)
assert all(x["enabled"] is False and x["cost_status"] == "cost_unknown" for x in additional)
assert all(x["actual_remaining"] is None for x in additional)
assert all("Independent" in x["quota_policy"] and "no pooling" in x["quota_policy"] for x in additional)
cerebras = next(x for x in additional if x["id"] == "cerebras")
assert "continuous token bucket" in cerebras["official_limit_reference"]
assert "not a permanently renewing free allowance" in cerebras["official_limit_reference"]
cloudflare = next(x for x in additional if x["id"] == "cloudflare-workers-ai")
assert "10,000 neurons per day" in cloudflare["official_limit_reference"]
assert "paid-only" in cloudflare["official_limit_reference"]
assert all("Zero-spend validation only" in x["validation_next_steps"] for x in additional)
assert all("Do not enable service" in x["validation_next_steps"] and "invocation adapter" in x["validation_next_steps"] for x in additional)
assert any(line.startswith("| AR-33 |") and "existing quota-provider complement" in line for line in items.splitlines())
assert "| AR-32 |" in items
assert "Implements: AR-33" in doc
assert "`mcp` scope" in doc and "legacy PAT" in doc and "cost/quota" in doc
assert "per service" in doc.lower() and "route around" in doc.lower()
assert "GITHUB-GITLAB-GOVERNED-RECONCILIATION.md" in doc
assert "not enabled" in doc and "does not authorize GitLab writes" in doc
assert "not new service candidates" in doc
assert "Additional capacity options" in doc
assert "zero-spend validation" in doc and "actual quota" in doc
print("GitLab integration catalog: OK")
