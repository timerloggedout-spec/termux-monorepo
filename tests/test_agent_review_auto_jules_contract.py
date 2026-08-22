from pathlib import Path


WORKFLOW = Path(".github/workflows/agent-review-auto-jules.yml")


def test_auto_jules_records_an_explicit_specialist_disposition():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "specialist_disposition: ${{ steps.meta.outputs.specialist_disposition }}" in source
    assert "const specialistDisposition = 'independent_implementation_specialist';" in source
    assert "`specialist_disposition: ${specialistDisposition}`" in source


def test_auto_jules_does_not_infer_coderabbit_branch_writes_from_feedback():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "provider-native branch write is never inferred from review text" in source
    assert "explicit confirm_branch_write=true" in source
    assert "CodeRabbit native AutoFix, fix-CI, and conflict actions are not inferred from this feedback" in source
    assert "@coderabbitai autofix" not in source


def test_auto_jules_keeps_existing_provider_controls_out_of_the_relay():
    source = WORKFLOW.read_text(encoding="utf-8")
    assert "Provider control or cooldown notice: keep in the authorized operator action path" in source
    assert "trustedLogins" in source
    assert "codeRabbitCooldown" in source
