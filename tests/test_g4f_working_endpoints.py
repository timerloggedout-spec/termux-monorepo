"""g4f working-endpoints + universe data contracts."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_working_endpoints_consistent():
    doc = json.loads((ROOT / "data/g4f-working/working-endpoints.json").read_text())
    assert doc["schema"] == "g4f-working-endpoints/v1"
    assert doc["inference_ok"] == len(doc["endpoints"]) > 0
    assert doc["attempted"] == doc["universe"]["pairs_total"]
    assert sum(doc["providers_ok"].values()) == doc["inference_ok"]
    assert doc["production_admission_changed"] is False
    pairs = {(e["provider"], e["model"]) for e in doc["endpoints"]}
    assert len(pairs) == len(doc["endpoints"])  # deduped

def test_universe_counts():
    uni = json.loads((ROOT / "data/g4f-working/universe.json").read_text())
    assert uni["schema"] == "g4f-endpoint-universe/v1"
    assert uni["pairs_total"] == len(uni["pairs"])
    assert uni["fork_pairs_distinct"] == 4241  # 4242 raw sum double-counts 1
    assert uni["pairs_total"] > uni["fork_pairs_raw"]  # upstream expands the fork
    assert {(p["provider"], p["model"]) for p in uni["pairs"]} == {(p["provider"], p["model"]) for p in uni["pairs"]}
