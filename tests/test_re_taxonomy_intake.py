"""Tests for scripts/reverse_engineering/re_taxonomy_intake.py.

The happy-path filing is the taxonomy's own example record (Android
native-library analysis) rendered in form headings; the record must carry
exactly the fields taxonomy.py validate() consumes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.reverse_engineering.re_taxonomy_intake import (  # noqa: E402
    IntakeError, build_record, parse_form)

TAXONOMY = None
_tax_path = os.path.join(os.path.dirname(__file__), "..", "ops",
                         "reverse_engineering", "taxonomy.json")
if os.path.exists(_tax_path):
    from scripts.reverse_engineering.re_taxonomy_intake import load_taxonomy
    TAXONOMY = load_taxonomy(_tax_path)

FILING = """### Item name

Android native-library analysis

### Kind

category

### Parent node IDs

mobile-android, target-native

### Tags - target

native

### Tags - format

ELF

### Tags - architecture

ARM64

### Tags - method

hybrid

### Tags - objective

understanding

### Toolchain stages

acquire: apk-xref -> published artifact + provenance
extract: apktool, apk-xref -> manifest, permissions, DEX + native split
analyze-static: jadx, ghidra -> reconstructed logic per layer
observe-dynamic: frida -> runtime calls correlated

### Outputs

annotated-functions, managed-native-call-map, runtime-observations

### Description

Layered analysis of Android native libraries.

### Evidence expectation

reproduced

### Submitter Role{Moniker}

Toolkits{reverse-engineering-toolkits}
"""


def _build(body=FILING, **kw):
    return build_record(parse_form(body), taxonomy=TAXONOMY, **kw)


def test_example_filing_builds_node_record():
    rec = _build(issue_number=42)
    assert rec["schema"] == "re-taxonomy-intake/v1"
    assert rec["kind"] == "filing"
    node = rec["node"]
    assert node["id"] == "android-native-library-analysis"
    assert node["parents"] == ["mobile-android", "target-native"]
    assert node["tags"]["format"] == ["ELF"]
    assert [s["stage"] for s in rec["toolchain"]] == [
        "acquire", "extract", "analyze-static", "observe-dynamic"]
    assert rec["toolchain"][1]["tools"] == ["apktool", "apk-xref"]
    assert rec["source_issue"] == 42


def test_record_kind_and_evidence():
    body = FILING.replace("### Evidence expectation\n\nreproduced",
                          "### Item ID\n\nandroid-native-library-analysis\n\n"
                          "### Evidence level\n\nreproduced\n\n"
                          "### Validator result\n\npass (0 errors)")
    rec = _build(body)
    assert rec["kind"] == "record"
    assert rec["evidence"] == "reproduced"
    assert rec["validator_result"] == "pass (0 errors)"


def test_out_of_vocab_tag_refused():
    try:
        _build(FILING.replace("### Tags - format\n\nELF",
                              "### Tags - format\n\nCOFF"))
    except IntakeError as exc:
        assert "not in axis vocabulary" in str(exc)
    else:
        raise AssertionError("expected IntakeError")


def test_tool_node_requires_tool_role():
    body = FILING.replace("### Kind\n\ncategory", "### Kind\n\ntool")
    try:
        _build(body)
    except IntakeError as exc:
        assert "tool_role" in str(exc)
    else:
        raise AssertionError("expected IntakeError")
    ok = _build(body.replace("### Toolchain stages",
                             "### Tags - tool role\n\ndecompiler\n\n"
                             "### Toolchain stages"))
    assert ok["node"]["tags"]["tool_role"] == ["decompiler"]


def test_stage_order_and_unknown_parent_refused():
    bad_order = FILING.replace(
        "extract: apktool, apk-xref -> manifest, permissions, DEX + native split\nanalyze-static: jadx, ghidra -> reconstructed logic per layer",
        "analyze-static: jadx, ghidra -> reconstructed logic per layer\nextract: apktool, apk-xref -> manifest, permissions, DEX + native split")
    try:
        _build(bad_order)
    except IntakeError as exc:
        assert "out of workflow order" in str(exc)
    else:
        raise AssertionError("expected IntakeError")
    if TAXONOMY is not None:
        try:
            _build(FILING.replace("mobile-android, target-native",
                                  "no-such-node"))
        except IntakeError as exc:
            assert "does not resolve" in str(exc)
        else:
            raise AssertionError("expected IntakeError")


def test_secret_value_refused():
    try:
        _build(FILING.replace("Layered analysis of Android native libraries.",
                              "key ghp_" + "A" * 30))
    except IntakeError as exc:
        assert "secret" in str(exc)
    else:
        raise AssertionError("expected IntakeError")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(fns)}/{len(fns)} passed")
