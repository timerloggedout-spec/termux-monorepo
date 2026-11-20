from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ci.validate_cns_architecture import (
    validate_authority_matrix,
    validate_identity_contract,
    validate_integration_map,
    validate_organ_registry,
)


def sample_registry(root: Path) -> dict:
    source = root / "source.md"
    source.write_text("canonical source\n", encoding="utf-8")
    return {
        "schema_version": "cns-organ-registry/v1",
        "source_ref": "master@abc123",
        "organs": [
            {
                "id": "brain",
                "name": "Brain",
                "plane": "cognition",
                "status": "implemented",
                "owner": "brain",
                "canonical_sources": ["source.md"],
                "responsibilities": ["reasoning"],
                "authority_boundary": "Produces advisory reasoning.",
                "evidence_class": "verified",
            }
        ],
    }


class CNSArchitectureContractTests(unittest.TestCase):
    def test_valid_organ_registry_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = validate_organ_registry(sample_registry(root), root)
        self.assertEqual(result, [])

    def test_duplicate_organ_ids_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = sample_registry(root)
            registry["organs"].append(dict(registry["organs"][0]))
            result = validate_organ_registry(registry, root)
        self.assertTrue(any("duplicate organ id" in item for item in result))

    def test_missing_canonical_source_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = sample_registry(root)
            registry["organs"][0]["canonical_sources"] = ["missing.md"]
            result = validate_organ_registry(registry, root)
        self.assertTrue(any("missing canonical source" in item for item in result))

    def test_proposed_organ_requires_proposed_evidence_class(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = sample_registry(root)
            registry["organs"][0]["status"] = "proposed_open_draft"
            result = validate_organ_registry(registry, root)
        self.assertTrue(any("must use evidence_class=proposed" in item for item in result))

    def test_map_requires_all_edge_classifications(self) -> None:
        content = """# CNS Integration Map
**Legend:** verified, derived, proposed
```mermaid
flowchart TD
 A[Brain] --> B[Manager]
```
"""
        result = validate_integration_map(content)
        self.assertTrue(any("unresolved" in item for item in result))

    def test_map_rejects_unclassified_edges(self) -> None:
        content = """# CNS Integration Map
**Legend:** verified, derived, proposed, unresolved
```mermaid
flowchart TD
 A[Brain] --> B[Manager]
```
"""
        result = validate_integration_map(content)
        self.assertTrue(any("unclassified edge" in item for item in result))

    def test_valid_map_passes(self) -> None:
        content = """# CNS Integration Map
**Legend:** verified, derived, proposed, unresolved
```mermaid
flowchart TD
 A[Brain] -->|verified| B[Manager]
```
"""
        self.assertEqual(validate_integration_map(content), [])

    def test_identity_contract_requires_all_correlation_dimensions(self) -> None:
        content = (
            "repository source_sha task_id scope_id orchestration_id cycle_id "
            "attempt_id agent_id provider_id model_id adapter_id run_id "
            "artifact_id outcome_id NOT_ESTABLISHED"
        )
        self.assertEqual(validate_identity_contract(content), [])

    def test_identity_contract_reports_missing_dimensions(self) -> None:
        result = validate_identity_contract("repository source_sha provider_id")
        self.assertTrue(any("task_id" in item for item in result))

    def test_authority_matrix_rejects_duplicate_domains(self) -> None:
        content = """# CNS Authority Matrix
| Domain | Canonical owner | CNS relationship | Permission boundary |
|---|---|---|---|
| Routing | Router | Selection | Adapter required |
| Routing | ORBIT | Arbitration | Observe only |
"""
        result = validate_authority_matrix(content)
        self.assertTrue(any("duplicate authority domain" in item for item in result))

    def test_authority_matrix_requires_single_owner_rows(self) -> None:
        content = """# CNS Authority Matrix
| Domain | Canonical owner | CNS relationship | Permission boundary |
|---|---|---|---|
| Routing | Router | Selection | Adapter required |
| Evidence | ATES | Observation | Source evidence |
"""
        self.assertEqual(validate_authority_matrix(content), [])


if __name__ == "__main__":
    unittest.main()
