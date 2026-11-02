"""Owner-records store: envelope L1 rules, register-seed parity, and
XML parity (owner decisions D1-D5, confirmed 2026-11-01)."""
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "ops/owner-records"
INDEX = STORE / "index.json"
XSD = STORE / "owner-records.xsd"

spec = importlib.util.spec_from_file_location(
    "owner_records", ROOT / "scripts/owner_records.py")
orx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orx)


def envelope():
    return json.loads(INDEX.read_text())


def test_envelope_validates():
    assert orx.validate(envelope()) == []


def test_classes_and_keys_shape():
    env = envelope()
    assert [c["class"] for c in env["classes"]] == orx.CLASSES
    assert sorted(env["keys"]) == sorted(orx.KEY_CLASSES)
    by = {c["class"]: c for c in env["classes"]}
    assert by["bets"]["key_class"] is None
    for name in ("authorizations", "clearances", "bets"):
        assert by[name]["state"] == "not_established"
        assert by[name]["records"] == []


def test_seed_parity_with_registers():
    env = envelope()
    by = {c["class"]: c for c in env["classes"]}
    gate_lines = (ROOT / orx.GATES_PATH).read_text().splitlines()
    want_gates = sum(1 for _s, cells in orx.table_rows(gate_lines)
                     if len(cells) >= 4)
    assert len(by["gates"]["records"]) == want_gates
    req_lines = (ROOT / orx.REQUESTS_PATH).read_text().splitlines()
    want_open = sum(1 for s, cells in orx.table_rows(req_lines)
                    if s == "OPEN" and len(cells) >= 6
                    and cells[0].isdigit())
    got_open = [r for r in by["decisions"]["records"]
                if r["state"] == "OPEN"]
    assert len(got_open) == want_open == 16


def test_xml_parity(tmp_path):
    env = envelope()
    xml_text = orx.build_xml(env, tmp_path)
    root = ET.fromstring(xml_text)
    assert root.tag == "owner-records"
    assert root.get("schema") == "owner-records/v1"
    xml_records = {}
    for cel in root.findall("class"):
        for rel in cel.findall("record"):
            xml_records[rel.get("id")] = rel.get("state")
    env_records = {r["id"]: r["state"] for c in env["classes"]
                   for r in c["records"]}
    assert xml_records == env_records
    # No body ships plaintext: every body element is either empty with a
    # status attribute or (post key-step) armored ciphertext.
    for bel in root.iter("body"):
        if bel.get("status") is None:
            assert (bel.text or "").startswith("-----BEGIN AGE")


def test_xsd_wellformed():
    ET.parse(XSD)
