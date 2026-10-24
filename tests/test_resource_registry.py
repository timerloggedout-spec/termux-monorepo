"""MSM-008: supplied-link coverage and native workflow integration contracts."""
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/model-selection-market/resource-registry.json"


def registry():
    return json.loads(REGISTRY.read_text())


def test_every_supplied_link_has_a_canonical_resource_and_input_fingerprint():
    document = registry()
    assert document["schema_version"] == "msm-resource-registry-v1"
    inputs = document["source_inputs"]
    assert len(inputs) == 20
    assert [row["source_line"] for row in inputs] == [1, 3, *range(7, 25)]
    assert len({row["id"] for row in inputs}) == 20
    resources = {row["id"]: row for row in document["resources"]}
    covered = set()
    for row in inputs:
        assert len(row["input_sha256"]) == 64
        assert len(row["resource_ids"]) == 1
        resource_id = row["resource_ids"][0]
        covered.add(resource_id)
        assert row["url"] == resources[resource_id]["url"]
        parsed = urlsplit(row["url"])
        if parsed.netloc == "www.google.com":
            assert parsed.path == "/search"
            assert set(parse_qs(parsed.query)) == {"q"}
        else:
            assert not parsed.query
    assert len(covered) == 19  # FreeLLMAPI is supplied twice, not two projects.
    assert len(resources) == 28
    assert set(resources) - covered == {"hex", "neon", "supabase", "codespaces", "digitalocean", "gpt4free", "omnirouter-fork", "awesome-freellm-apis-open-free-llm-api", "free-inference"}


def test_resource_matrix_preserves_native_anchors_and_research_boundary():
    for row in registry()["resources"]:
        assert row["runtime_eligible"] is False
        assert row["evidence_class"] == "REFERENCE_ONLY"
        assert row["status"] == "discovery-only"
        assert row["next_action"].strip()
        assert row["mesh_roles"]
        assert row["implementation_paths"]
        for path in row["implementation_paths"]:
            assert (ROOT / path).is_file(), path


def test_human_matrix_documents_all_canonical_references():
    matrix = (ROOT / "docs/ops/RESOURCE-IMPLEMENTATION-MATRIX.md").read_text()
    for row in registry()["resources"]:
        assert row["url"] in matrix, row["id"]
    assert "20 supplied links" in matrix
    assert "26 resources" in matrix


def test_existing_cadence_generates_search_index_without_expanding_publication():
    workflow = (ROOT / ".github/workflows/provider-recon-compound.yml").read_text()
    assert "cron:" not in workflow
    assert "tests/test_resource_index.py tests/test_resource_registry.py" in workflow
    assert "--providers /tmp/provider-research/provider-recon.json --output /tmp/provider-research/resource-index.json" in workflow
    assert "head_repository.full_name == github.repository" in workflow
    assert "persist-credentials: false" in workflow
    assert "pull_request_target" not in workflow
    publisher = (ROOT / "scripts/model_selection_market/publish_recon.py").read_text()
    assert 'SNAPSHOT_PATH = "data/model-selection-market/provider-recon.json"' in publisher
    assert "resource-registry.json" not in publisher
    assert "resource-index.json" not in publisher


def test_real_aggregate_preserves_provider_integration_and_blocking_evidence():
    from scripts.model_selection_market.resource_index import build_index
    providers = json.loads((ROOT / "data/model-selection-market/provider-recon.json").read_text())
    index = build_index(registry(), providers)
    assert index["provider_integration_references"] == providers["integration_references"]
    assert index["provider_blocked_reasons"] == providers["blocked_reasons"]
    assert index["sources"] == sorted(providers["sources"], key=lambda row: row["repo"])
    assert len(index["source_inputs"]) == 20
