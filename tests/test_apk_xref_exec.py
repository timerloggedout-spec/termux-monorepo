"""Tests for the apk-xref execution runner (filing parse + spec).

The pipeline itself shells the belt (ops/web_adapter_foundry/apk_xref.py),
whose behaviour is covered by tests/test_apk_xref.py; here we pin the
filing -> spec seam the workflow depends on.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                       / "ops" / "web_adapter_foundry"))
import apk_xref_exec as ex  # noqa: E402

FILING = """### Target ID

agora

### Paired repo brief

#2082

### Target repo URL

https://github.com/newo-ether/Agora

### Artifact source

github-releases

### Authorization basis

Public open-source repository.

### Side effect

read

### Execution venue

remote-service

### Evidence expectation

reproduced

### Submitter Role{Moniker}

foundry{intake}
"""


def test_parse_filing_sections():
    f = ex.parse_filing(FILING)
    assert f["Target ID"] == "agora"
    assert f["Target repo URL"] == "https://github.com/newo-ether/Agora"
    assert f["Submitter Role{Moniker}"] == "foundry{intake}"


def test_filing_spec_defaults():
    spec = ex.filing_spec(ex.parse_filing(FILING))
    assert spec == {"target_id": "agora",
                    "repo": "https://github.com/newo-ether/Agora",
                    "source": "github-releases", "package_id": "",
                    "package_id_via": "none",
                    "evidence": "reproduced"}


def test_filing_spec_blank_source_and_evidence_default():
    spec = ex.filing_spec({"Target ID": "x"})
    assert spec["source"] == "none-known"
    assert spec["evidence"] == "reproduced"


def test_submitter_is_role_moniker_form():
    assert ex.SUBMITTER == "reverse-engineering-toolkits{apk-xref-exec}"


def test_cap_findings_markdown_elides_lists_keeps_headings():
    big = "### Endpoints actually observed\n\n" + "\n".join(
        f"- https://example.com/api/v1/resource/{i}" for i in range(3000))
    text = ("### Target ID\n\nbig-target\n\n" + big +
            "\n\n### Verdict\n\ndivergences-found\n")
    capped = ex.cap_findings_markdown(text)
    assert len(capped) <= ex.ISSUE_BODY_LIMIT
    assert "### Target ID" in capped and "### Verdict" in capped
    assert "elided" in capped and "findings-full.md" in capped


def test_cap_findings_markdown_small_is_untouched():
    text = "### Target ID\n\nx\n"
    assert ex.cap_findings_markdown(text) == text


def test_filing_spec_body_scan_fallback():
    fields = {"Target ID": "relagent", "Artifact source": "f-droid",
              "Package ID": "none-known",
              "Target repo URL": "https://gitlab.com/RmMsr/relagent"}
    body = ("### Package ID\n\nnone-known\n\n### Source claims to check\n\n"
            "package org.venkado.relagent ships on f-droid.org — "
            "see https://apt.izzysoft.de/fdroid/repo for the mirror")
    spec = ex.filing_spec(fields, body)
    assert spec["package_id"] == "org.venkado.relagent"
    assert spec["package_id_via"] == "body-scan"


def test_filing_spec_field_wins_over_scan():
    fields = {"Target ID": "x", "Package ID": "com.example.right"}
    spec = ex.filing_spec(fields, "body mentions com.example.wrong here")
    assert spec["package_id"] == "com.example.right"
    assert spec["package_id_via"] == "field"
