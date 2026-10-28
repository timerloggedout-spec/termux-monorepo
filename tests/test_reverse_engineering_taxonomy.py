"""RE taxonomy tests — stdlib pytest, no network."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ops.reverse_engineering import taxonomy as rt  # noqa: E402


def tax():
    return rt.load_taxonomy()


def test_taxonomy_validates():
    assert rt.validate(tax()) == []


def test_polyhierarchy_android_dex_has_two_parents():
    n = rt.node(tax(), "bytecode-android-dex")
    assert set(n["parents"]) == {"target-bytecode", "mobile-android"}
    assert "mobile-android" in rt.node(tax(), "bytecode-android-dex")["parents"]
    kids = rt.node(tax(), "mobile-android")["children"]
    assert "bytecode-android-dex" in kids and "apk-xref" in kids


def test_kinds_stay_distinct():
    t = tax()
    kali = rt.node(t, "kali-linux")
    assert kali["kind"] == "tool"
    assert kali["tags"]["tool_role"] == ["workspace"]  # platform, not a discipline
    assert rt.node(t, "work-malware")["kind"] == "category"


def test_toolchains_reference_tools_and_stages_in_order():
    t = tax()
    android = rt.toolchain(t, "mobile-android")
    stages = [s["stage"] for s in android["stages"]]
    assert stages[0] == "acquire" and stages[-1] == "document"
    flat = [tool for s in android["stages"] for tool in s["tools"]]
    assert "apk-xref" in flat and "jadx" in flat and "frida" in flat
    assert rt.toolchain(t, "no-such-category") is None


def test_overlap_matrix_shape():
    om = tax()["overlap_matrix"]
    assert om["rows"]["mobile-android"]["instrumentation"] == "central"
    assert om["rows"]["work-malware"]["static"] == "central"
    for row in om["rows"].values():
        assert set(row) == set(om["methods"])


def test_example_record_resolves():
    t = tax()
    rec = t["example_record"]
    assert rec["toolchain"]["cross-validation"] == "apk-xref"
    assert rt.validate(t) == []  # record refs are part of validation


def test_validator_catches_damage():
    t = tax()
    t["nodes"].append({"id": "ghost", "kind": "tool", "parents": ["nowhere"],
                       "tags": {"tool_role": ["debugger"], "bogus-axis": ["x"]}})
    errs = rt.validate(t)
    assert any("unknown parent" in e for e in errs)
    assert any("unknown axis" in e for e in errs)
    assert any("does not descend" in e for e in errs)
