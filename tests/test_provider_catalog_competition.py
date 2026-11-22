import hashlib
import json

import pytest

from scripts.provider_catalog_competition import populate


def test_populate_writes_both_catalogues_from_one_v5_snapshot(tmp_path):
    source = tmp_path / "incumbent-source.json"
    output = tmp_path / "catalogues"
    source_bytes = (
        b'{"schema":"provider-model-catalog/v5","observed_at":"2026-11-21T00:00:00Z",'
        b'"providers":["fixture"],"models":[{"provider":"fixture","id":"model-a",'
        b'"pricing":{"prompt":"0.0001"}}]}'
    )
    source.write_bytes(source_bytes)

    manifest = populate(source, output)

    incumbent_bytes = (output / "incumbent-v5.json").read_bytes()
    inspired = json.loads((output / "vultr-inspired-v1.json").read_text(encoding="utf-8"))
    stored_manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))

    assert incumbent_bytes == source_bytes
    assert inspired["catalogue"] == "VultrInspired"
    assert inspired["models"][0]["id"] == "model-a"
    assert manifest == stored_manifest
    assert manifest["source_sha256"] == hashlib.sha256(source_bytes).hexdigest()
    assert [variant["catalogue"] for variant in manifest["variants"]] == [
        "Incumbent", "VultrInspired"
    ]
    assert manifest["execution"]["network_requests"] == 0


def test_populate_rejects_non_v5_input(tmp_path):
    source = tmp_path / "wrong.json"
    source.write_text('{"schema":"other"}', encoding="utf-8")

    with pytest.raises(ValueError, match="unsupported_incumbent_schema"):
        populate(source, tmp_path / "output")
