import stat

import pytest

from archwiz.context_relationships.rust_accel import RustAccelerationError, analyze_fragments


def test_accelerator_is_opt_out_when_no_binary_exists(monkeypatch):
    monkeypatch.setenv("CRG_RUST_ACCEL", "auto")
    monkeypatch.delenv("CRG_RUST_ACCEL_BIN", raising=False)
    assert analyze_fragments(
        [{"id": "a.py", "level": "file", "text": "print(1)\n", "children": []}]
    ) is None


def test_accelerator_can_be_required_and_fails_closed(monkeypatch, tmp_path):
    monkeypatch.setenv("CRG_RUST_ACCEL", "required")
    monkeypatch.setenv("CRG_RUST_ACCEL_BIN", str(tmp_path / "missing"))
    with pytest.raises(RustAccelerationError, match="missing"):
        analyze_fragments(
            [{"id": "a.py", "level": "file", "text": "print(1)\n", "children": []}]
        )


def test_accelerator_contract_accepts_bounded_json_output(monkeypatch, tmp_path):
    binary = tmp_path / "fake-accel.py"
    binary.write_text(
        "#!/usr/bin/env python3\n"
        "import json,sys\n"
        "rows=[json.loads(x) for x in sys.stdin if x.strip()]\n"
        "print(json.dumps({'fingerprints':[{'id':rows[0]['id'],'full_hash':'ab'*32,'ref_id':'x'*22}],"
        "'policies':[],'alpha':{}}))\n"
    )
    binary.chmod(binary.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("CRG_RUST_ACCEL", "required")
    monkeypatch.setenv("CRG_RUST_ACCEL_BIN", str(binary))

    result = analyze_fragments(
        [{"id": "a.py", "level": "file", "text": "print(1)\n", "children": []}]
    )
    assert result["fingerprints"][0]["id"] == "a.py"
    assert len(result["fingerprints"][0]["full_hash"]) == 64
    assert len(result["fingerprints"][0]["ref_id"]) == 22
