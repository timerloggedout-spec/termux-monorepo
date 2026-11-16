"""Tests for scripts/secrets_audit/audit.py (phantom-secret remediation)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts", "secrets_audit"))

import audit  # noqa: E402

PROV = {"FLY_IO_ORG_TOKEN", "OPERATOR_GITHUB_TOKEN", "ARCHWIZ_GITHUB_TOKEN",
        "GEMINI_API_KEY", "DEEPSEEK_API_KEY", "DEEPSEEK_AWS_WAF_TOKEN"}


def _refs(text, fn="x.yml"):
    return audit.scan_workflows.__wrapped__ if False else None


def _scan(tmp_path, files):
    for name, text in files.items():
        (tmp_path / name).write_text(text)
    return audit.scan_workflows(str(tmp_path))


def test_scan_excludes_filename_fragments(tmp_path):
    refs = _scan(tmp_path, {
        "a.yml": "run: node redact_secrets.cjs && bash provision-secrets.sh\n"
                 "env:\n  K: ${{ secrets.REAL_KEY }}\n"})
    assert "REAL_KEY" in refs
    assert "cjs" not in refs and "sh" not in refs


def test_classify_case_variant(tmp_path):
    refs = _scan(tmp_path, {"fly.yml": "env:\n  T: ${{ secrets.Fly_io_ORG_TOKEN }}\n"})
    recs = audit.classify(refs, PROV)
    assert len(recs) == 1
    assert recs[0]["class"] == "case-variant"
    assert recs[0]["replacement"] == "FLY_IO_ORG_TOKEN"


def test_classify_dead_branch_and_provisioning(tmp_path):
    refs = _scan(tmp_path, {
        "a.yml": "env:\n  A: ${{ secrets.DEAD || secrets.OPERATOR_GITHUB_TOKEN }}\n"
                 "  B: ${{ secrets.LONELY_KEY }}\n"})
    recs = {r["name"]: r for r in audit.classify(refs, PROV)}
    assert recs["DEAD"]["class"] == "dead-branch"
    assert recs["LONELY_KEY"]["class"] == "provisioning"


def test_classify_compiled_lock_file(tmp_path):
    refs = _scan(tmp_path, {
        "w.lock.yml": "env:\n  A: ${{ secrets.WHATEVER || secrets.GITHUB_TOKEN }}\n"})
    recs = audit.classify(refs, PROV)
    assert recs[0]["class"] == "compiled"


def test_drop_branch_head_middle_and_wrapped():
    assert audit.drop_branch(
        "${{ secrets.OPERATOR || secrets.ARCHWIZ_GITHUB_TOKEN }}", "OPERATOR"
    ) == "${{ secrets.ARCHWIZ_GITHUB_TOKEN }}"
    assert audit.drop_branch(
        "${{ secrets.GEMINI_API_KEY || secrets.GOOGLE_API_KEY }}", "GOOGLE_API_KEY"
    ) == "${{ secrets.GEMINI_API_KEY }}"
    wrapped = "${{ (secrets.OPERATOR || secrets.ARCHWIZ_GITHUB_TOKEN) && 'x' }}"
    out = audit.drop_branch(wrapped, "OPERATOR")
    assert out == "${{ (secrets.ARCHWIZ_GITHUB_TOKEN) && 'x' }}"
    # Token-boundary safety: OPERATOR must not bite OPERATOR_GITHUB_TOKEN.
    expr = "${{ secrets.OPERATOR_GITHUB_TOKEN || secrets.OPERATOR_TOKEN }}"
    assert audit.drop_branch(expr, "OPERATOR") == expr


def test_conditional_reference_is_not_a_dead_branch(tmp_path):
    line = ("api_key: ${{ matrix.provider == 'felo' && secrets.FELO_AI_API || "
            "matrix.provider == 'omni' && secrets.OMNI_API_KEY || "
            "secrets.OPENROUTER_API_KEY }}\n")
    refs = _scan(tmp_path, {"ce.yml": line})
    prov = PROV | {"FELO_AI_API", "OPENROUTER_API_KEY"}
    recs = {r["name"]: r for r in audit.classify(refs, prov)}
    assert recs["OMNI_API_KEY"]["class"] == "provisioning"
    assert audit.drop_branch(line.strip(), "OMNI_API_KEY") == line.strip()


def test_apply_case_variant(tmp_path):
    (tmp_path / "fly.yml").write_text("env:\n  T: ${{ secrets.Fly_io_ORG_TOKEN }}\n")
    report = {"provisioned": sorted(PROV),
              "records": audit.classify(audit.scan_workflows(str(tmp_path)), PROV)}
    changes = audit.apply_class(str(tmp_path), report, "case-variant")
    assert changes and changes[0]["count"] == 1
    assert "secrets.FLY_IO_ORG_TOKEN" in (tmp_path / "fly.yml").read_text()
