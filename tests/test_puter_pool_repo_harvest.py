from __future__ import annotations

import json

from scripts import puter_pool_repo_harvest as harvest


def test_repo_harvest_uses_allowlist_and_extracts_operational_contracts(tmp_path):
    for relative in harvest.ALLOWLIST:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("router.get('/stats', handler);\nCREATE TABLE IF NOT EXISTS ai_responses (id TEXT);\nemit('request:completed');", encoding="utf-8")
    (tmp_path / ".env").write_text("PUTER_TOKEN=private-value", encoding="utf-8")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "pool.db").write_bytes(b"sqlite-private")
    result = harvest.harvest(tmp_path)
    assert result["schema"] == "provider-source-harvest/v1"
    assert "/stats" in result["capabilities"]["http_routes"]
    assert "ai_responses" in result["capabilities"]["sqlite_tables"]
    assert "request:completed" in result["capabilities"]["event_names"]
    assert all(row["path"] != ".env" for row in result["harvested_files"])
    assert all("pool.db" not in row["path"] for row in result["harvested_files"])
    assert "private-value" not in json.dumps(result)
