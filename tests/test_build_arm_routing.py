"""Contract tests for multi-arm build routing (issue #5151).

Pins: the arm registry shape (harness x endpoint, sourced from the
catalog of record), the Gemini budget of record (20/day = 4 reserved
escalation + 16 spendable primary, #5152 design c.6799068593), Baseten
as credit-funded (correction c.6786217937), the webWrapper arm CLASS
registered by shape only, the PERMANENT funded-out exclusion, runtime
selection with quota-terminal rotation, the DoE stamp set verbatim
(c.6786076278), and the build-dispatch workflow composition (selection
before builders, per-arm builder conditions, #5142 verify composing for
every arm, stamp fan-out to the scoring planes).
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "ops" / "dispatch" / "build-arms.json"
FEED = ROOT / "ops" / "que" / "feeds" / "arm-census.json"
WORKFLOW = ROOT / ".github" / "workflows" / "build-dispatch.yml"
CENSUS_WORKFLOW = ROOT / ".github" / "workflows" / "build-arm-census.yml"


def load_harness():
    spec = importlib.util.spec_from_file_location(
        "build_arm_harness", ROOT / "scripts" / "ops" / "build_arm_harness.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def arms_by_id():
    return {a["arm_id"]: a for a in registry()["arms"]}


# ---------------------------------------------------------------- registry

def test_registry_schema_and_required_fields():
    data = registry()
    assert data["schema"] == "build-arms/v1"
    for arm in data["arms"]:
        for field in ("arm_id", "harness", "endpoint", "model", "budget",
                      "status", "selectable", "census"):
            assert field in arm, f"{arm.get('arm_id')} missing {field}"
        for field in ("provider", "route_id", "secret_env", "url", "protocol", "source"):
            assert field in arm["endpoint"], f"{arm['arm_id']} endpoint missing {field}"
        for field in ("class", "quota_metric_source"):
            assert field in arm["budget"], f"{arm['arm_id']} budget missing {field}"
        assert "AUTO QUOTA LEDGER" in arm["budget"]["quota_metric_source"], (
            "per-arm budgets are read from the Cadence ledger (#5152)")


def test_registry_arms_are_the_census_seeded_set_plus_gemini():
    arms = arms_by_id()
    assert set(arms) >= {"mistral-codestral", "sealion-llama", "cohere-command-a",
                         "baseten-gpt-oss", "gemini-cli"}
    # Census round 1 (#5151 c.6786208798): these exact models were INVOKE OK.
    assert arms["mistral-codestral"]["model"] == "codestral-2508"
    assert arms["sealion-llama"]["model"] == "aisingapore/Llama-SEA-LION-v3-70B-IT"
    assert arms["cohere-command-a"]["model"] == "command-a-03-2025"
    assert arms["baseten-gpt-oss"]["model"] == "openai/gpt-oss-120b"
    for arm_id in ("mistral-codestral", "sealion-llama", "cohere-command-a", "baseten-gpt-oss"):
        assert arms[arm_id]["status"] in ("candidate", "eligible"), (
            "arms seed as CANDIDATE until the tool round-trip leg passes (c.6786217937)")
        assert arms[arm_id]["harness"] == "generic-agent-loop"
        assert arms[arm_id]["selectable"] is True


def test_gemini_arm_budget_is_the_ledger_record_of_record():
    gemini = arms_by_id()["gemini-cli"]
    assert gemini["harness"] == "run-gemini-cli"
    assert gemini["status"] == "eligible"
    budget = gemini["budget"]
    assert budget["daily_total"] == 20
    assert budget["reserved_escalation"] == 4
    assert budget["spendable_primary"] == 16
    assert budget["reserved_escalation"] + budget["spendable_primary"] == budget["daily_total"]


def test_baseten_is_credit_funded_not_free():
    baseten = arms_by_id()["baseten-gpt-oss"]
    assert baseten["budget"]["class"] == "credit-funded"
    assert baseten["budget"]["burn_aware"] is True


def test_webwrapper_is_a_class_shape_only():
    arms = arms_by_id()
    assert "webwrapper-class" in arms
    row = arms["webwrapper-class"]
    assert row.get("arm_class") == "webWrapper"
    assert row["selectable"] is False
    assert row["endpoint"]["url"] is None and row["model"] is None
    shapes = {s["shape"] for s in row["class_shapes"]}
    assert shapes == {"A", "D"}, "classes A internal-API+cookie, D MCP-over-session"


def test_funded_out_providers_are_never_arms():
    funded_out = {"huggingface", "deepinfra", "novita", "friendli",
                  "zai", "llm7", "routeway", "siliconflow"}
    providers = {(a["endpoint"].get("provider") or "") for a in registry()["arms"]}
    assert not (providers & funded_out), "PERMANENT funded-out providers are never build arms"
    assert "funded-out" in registry()["excluded_by_kind"]


# ---------------------------------------------------------------- selection

def test_selection_falls_back_to_gemini_when_census_passes_only_gemini():
    harness = load_harness()
    reg = registry()
    census = {"schema": "arm-census/v1", "arms": [
        {"arm_id": a["arm_id"], "verdict": "failed"} for a in reg["arms"]]}
    arm, reason = harness.select_arm(reg, census, "2026-11-11", "auto")
    assert arm["arm_id"] == "gemini-cli"
    assert "fallback-of-record" in reason


def test_selection_prefers_eligible_generic_free_tier_over_credit_funded():
    harness = load_harness()
    reg = registry()
    census = {"schema": "arm-census/v1", "arms": [
        {"arm_id": "baseten-gpt-oss", "verdict": "eligible"},
        {"arm_id": "sealion-llama", "verdict": "eligible"}]}
    arm, _ = harness.select_arm(reg, census, "2026-11-11", "auto")
    assert arm["arm_id"] == "sealion-llama", "free-tier rotates before credit-funded Baseten"


def test_eligible_free_tier_gemini_precedes_credit_funded_generic_arm():
    harness = load_harness()
    reg = registry()
    census = {"schema": "arm-census/v1", "arms": [
        {"arm_id": "baseten-gpt-oss", "verdict": "eligible"}]}
    arm, reason = harness.select_arm(reg, census, "2026-11-11", "auto")
    assert arm["arm_id"] == "gemini-cli"
    assert "free-tier Gemini" in reason


def test_auto_build_rotates_after_quota_terminal_to_next_free_generic(tmp_path, monkeypatch):
    harness = load_harness()
    reg_path = tmp_path / "registry.json"
    feed_path = tmp_path / "census.json"
    task_path = tmp_path / "task.md"
    stamp_path = tmp_path / "stamp.json"
    result_path = tmp_path / "result.json"
    output_path = tmp_path / "github-output"
    reg_path.write_text(json.dumps(registry()), encoding="utf-8")
    feed_path.write_text(json.dumps({"schema": "arm-census/v1", "arms": [
        {"arm_id": "mistral-codestral", "verdict": "eligible"},
        {"arm_id": "sealion-llama", "verdict": "eligible"}]}), encoding="utf-8")
    task_path.write_text("test task", encoding="utf-8")
    output_path.write_text("", encoding="utf-8")
    monkeypatch.setattr(harness, "harden_process", lambda: None)
    calls = []

    def fake_run(arm, task, root, max_turns):
        calls.append(arm["arm_id"])
        if len(calls) == 1:
            raise harness.QuotaTerminal("HTTP 429")
        return {"status": "completed", "turns": 1, "final": "ok",
                "usage": {"status": "measured", "tokens_in": 1, "tokens_out": 1}}

    monkeypatch.setattr(harness, "run_agent_loop", fake_run)
    monkeypatch.setenv("GITHUB_OUTPUT", str(output_path))
    rc = harness.main([
        "--registry", str(reg_path), "--census", str(feed_path),
        "--arm", "auto", "--task-file", str(task_path),
        "--stamp-out", str(stamp_path), "--result-out", str(result_path),
    ])
    assert rc == 0
    assert calls == ["mistral-codestral", "sealion-llama"]
    stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
    assert stamp["arm_id"] == "sealion-llama"
    assert "quota-terminal rotation" in stamp["selection_reason"]
    assert "arm_id=sealion-llama" in output_path.read_text(encoding="utf-8")
    assert stamp["rotation_attempts"] == [
        {"arm_id": "mistral-codestral", "status": "quota_terminal"},
        {"arm_id": "sealion-llama", "status": "completed"},
    ]


def test_selection_skips_quota_terminal_arm_day():
    harness = load_harness()
    reg = registry()
    census = {"schema": "arm-census/v1", "arms": [
        {"arm_id": "mistral-codestral", "verdict": "eligible",
         "quota_terminal": {"terminal": True, "date": "2026-11-11"}},
        {"arm_id": "sealion-llama", "verdict": "eligible",
         "quota_terminal": {"terminal": False}}]}
    arm, _ = harness.select_arm(reg, census, "2026-11-11", "auto")
    assert arm["arm_id"] == "sealion-llama", "429-terminal arm-day rotates, never backoff-burns"
    # Yesterday's terminal flag does not block today.
    census["arms"][0]["quota_terminal"]["date"] = "2026-11-10"
    arm, _ = harness.select_arm(reg, census, "2026-11-11", "auto")
    assert arm["arm_id"] == "mistral-codestral"


def test_explicit_selection_rejects_arm_terminal_for_pt_day():
    harness = load_harness()
    reg = registry()
    census = {"schema": "arm-census/v1", "arms": [
        {"arm_id": "mistral-codestral", "verdict": "eligible",
         "quota_terminal": {"terminal": True, "date": "2026-11-11"}}]}
    try:
        harness.select_arm(reg, census, "2026-11-11", "mistral-codestral")
    except harness.ArmFailure as exc:
        assert "quota-terminal" in str(exc)
    else:
        raise AssertionError("explicit selection must not override an arm-day quota terminal")


def test_selection_rejects_non_selectable_and_unknown_arms():
    harness = load_harness()
    reg = registry()
    for bad in ("webwrapper-class", "jules", "no-such-arm"):
        try:
            harness.select_arm(reg, {"arms": []}, "2026-11-11", bad)
        except harness.ArmFailure:
            continue
        raise AssertionError(f"selection must refuse {bad}")


# -------------------------------------------------------------------- stamp

DOE_STAMP_FIELDS = {
    "instance_key", "model_version", "run_id", "ts", "task_ref", "trigger",
    "set_index", "cumulative_n", "selection_reason",
}


def test_stamp_carries_the_full_doe_set():
    harness = load_harness()
    arm = arms_by_id()["mistral-codestral"]
    stamp = harness.build_stamp(
        arm=arm, run_id="12345", ts="2026-11-11T00:00:00Z", issue=5151,
        trigger="workflow_dispatch", selection_reason="rotation: test",
        outcome_status="completed", evidence_ref="actions run 12345",
        usage={"tokens_in": 10, "tokens_out": 5, "status": "measured"},
        quota_class="primary")
    for field in DOE_STAMP_FIELDS:
        assert stamp.get(field) not in (None, ""), f"stamp missing DoE field {field}"
    instance = stamp["instance"]
    for field in ("system_prompt", "tools", "role", "moniker", "context"):
        assert field in instance
    assert len(instance["system_prompt"]["sha256"]) == 64
    assert len(instance["tools"]["sha256"]) == 64
    assert stamp["model_version"] == "codestral-2508@codestral-2508"
    outcome = stamp["outcome"]
    for field in ("status", "evidence_ref", "origin", "corroboration_state"):
        assert outcome.get(field), f"outcome missing {field}"
    usage = stamp["usage"]
    for field in ("status", "bucket_slice_id"):
        assert usage.get(field), f"usage missing {field}"
    assert usage["tokens_in"] == 10 and usage["tokens_out"] == 5
    assert stamp["route_endpoint_id"] == "mistral::codestral-2508"
    # Fan-out compatibility: the canonical fields stamp_fanout.py reads.
    for field in ("dispatch_id", "provider", "model", "run", "quota"):
        assert field in stamp


def test_gemini_stamp_does_not_claim_generic_harness_fingerprints():
    harness = load_harness()
    stamp = harness.build_stamp(
        arm=arms_by_id()["gemini-cli"], run_id="9", ts="2026-11-11T00:00:00Z",
        issue=5151, trigger="workflow_dispatch", selection_reason="test",
        outcome_status="completed", evidence_ref="actions run 9", usage={})
    assert stamp["instance"]["system_prompt"]["sha256"] == "NOT_ESTABLISHED"
    assert stamp["instance"]["tools"]["sha256"] == "NOT_ESTABLISHED"
    assert stamp["instance_key"] == "NOT_ESTABLISHED"


def test_stamp_never_invents_usage():
    harness = load_harness()
    arm = arms_by_id()["gemini-cli"]
    stamp = harness.build_stamp(
        arm=arm, run_id=None, ts="2026-11-11T00:00:00Z", issue=None,
        trigger="test", selection_reason="test", outcome_status="failed",
        evidence_ref=None, usage={})
    assert stamp["usage"]["status"] == "not_established"
    assert stamp["usage"]["tokens_in"] is None


# --------------------------------------------------------- security gates

def test_read_file_probe_extracts_schema_without_truncation(tmp_path):
    harness = load_harness()
    target = tmp_path / "ops" / "dispatch" / "build-arms.json"
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"payload": "x" * 9000, "schema": "build-arms/v1"}), encoding="utf-8")
    assert harness.run_tool(tmp_path, "read_file", {"path": "ops/dispatch/build-arms.json"}) == "build-arms/v1"


def test_census_model_has_read_only_tool_allowlist():
    harness = load_harness()
    tools = harness.census_tool_definitions()
    names = [tool["function"]["name"] for tool in tools]
    assert names == ["read_file"]
    assert "run_command" not in names and "write_file" not in names


def test_model_subprocess_does_not_inherit_provider_or_github_credentials(tmp_path, monkeypatch):
    harness = load_harness()
    monkeypatch.setenv("MISTRAL_API_KEY", "provider-secret")
    monkeypatch.setenv("GH_TOKEN", "github-secret")
    monkeypatch.setenv("GITHUB_TOKEN", "workflow-secret")
    monkeypatch.setenv("PATH", "/usr/bin")
    monkeypatch.setenv("GITHUB_ENV", "/tmp/runner-env")
    monkeypatch.setenv("GITHUB_OUTPUT", "/tmp/runner-output")
    captured = {}

    class Result:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run(*args, **kwargs):
        captured.update(kwargs)
        return Result()

    monkeypatch.setattr(harness.subprocess, "run", fake_run)
    assert harness.run_tool(tmp_path, "run_command", {"command": "echo ok"}).startswith("exit=0")
    env = captured["env"]
    assert "MISTRAL_API_KEY" not in env
    assert "GH_TOKEN" not in env and "GITHUB_TOKEN" not in env
    assert env["PATH"] == "/usr/bin"
    assert "GITHUB_ENV" not in env and "GITHUB_OUTPUT" not in env


def test_census_requires_real_read_tool_result_and_exact_marker():
    source = (ROOT / "scripts" / "ops" / "build_arm_census.py").read_text(encoding="utf-8")
    assert "harness.census_tool_definitions()" in source
    assert 'call.get("name") != "read_file"' in source
    assert 'PROBE_MARKER in tool_result' in source
    assert '(final.get("content") or "").strip() == PROBE_MARKER' in source


def test_census_rejects_unknown_arm_input():
    source = (ROOT / "scripts" / "ops" / "build_arm_census.py").read_text(encoding="utf-8")
    assert "if args.arm and args.arm not in known_ids:" in source
    assert 'ap.error(f"unknown arm id: {args.arm}")' in source


def test_live_build_mints_write_token_only_after_agent_execution():
    text = CENSUS_WORKFLOW.read_text(encoding="utf-8")
    live = text[text.index("  live-build:"):]
    harness = live.index("Run the generic agent-loop harness")
    mint = live.index("Mint narrowly-scoped Swarm App token after model execution")
    checkout = live.index("Checkout PR head (read-only token; no persisted credentials)")
    assert checkout < harness < mint
    assert "persist-credentials: false" in live
    assert "permission-contents: write" in live and "permission-pull-requests: write" in live
    assert live.index("Run the generic agent-loop harness") < live.index("Mint narrowly-scoped Swarm App token after model execution")


def test_build_dispatch_defers_app_token_until_after_both_agent_builders():
    text = WORKFLOW.read_text(encoding="utf-8")
    mint = text.index("Mint narrowly-scoped Swarm App token after all model execution")
    gemini = text.index("Run Gemini CLI builder")
    generic = text.index("Run the generic agent-loop builder")
    assert gemini < mint and generic < mint
    gemini_step = text[gemini:text.index("Fetch the build task (generic arm)", gemini)]
    generic_end = text.index("Persist PT arm-day quota-terminal markers", generic)
    generic_step = text[generic:generic_end]
    assert "GH_TOKEN:" not in gemini_step
    assert "GH_TOKEN:" not in generic_step
    assert "persist-credentials: false" in text
    assert "baseline_sha=$(git rev-parse HEAD)" in text


def test_census_workflow_uses_quoted_input_and_immutable_artifact_actions():
    text = CENSUS_WORKFLOW.read_text(encoding="utf-8")
    assert "ARM_INPUT: ${{ inputs.arm }}" in text
    assert '--arm "$ARM_INPUT"' in text
    assert "format('--arm" not in text
    assert text.count("actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02") == 2


def test_build_dispatch_persists_and_rehydrates_pt_quota_terminals():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "build-arm-quota-terminal:v1" in text
    assert "issues/5151/comments?per_page=100" in text
    assert "arm-census-effective.json" in text
    assert "ZoneInfo('America/Los_Angeles')" in text
    assert "Persist PT arm-day quota-terminal markers" in text
    assert "steps.builder-generic.outputs.selection_reason" in text


def test_secret_bearing_agent_steps_exec_python_without_token_environment():
    census = CENSUS_WORKFLOW.read_text(encoding="utf-8")
    dispatch = WORKFLOW.read_text(encoding="utf-8")
    assert "exec python3 scripts/ops/build_arm_census.py" in census
    assert "exec python3 scripts/ops/build_arm_harness.py" in census
    assert "exec python3 scripts/ops/build_arm_harness.py" in dispatch
    assert "--selection-reason \"$SELECTION_REASON\"" in dispatch
    assert "BASE_BRANCH_SHA" in dispatch and "REF_SHA" in dispatch
    assert "baseline_sha=$(git rev-parse HEAD)" in dispatch
    assert "git checkout -B \"$BUILD_BRANCH\"" not in dispatch
    assert '"phase": "dispatch"' in dispatch
    assert "curl --fail-with-body" in dispatch
    assert "GH_TOKEN: ${{ github.token }}" in dispatch


# --------------------------------------------------------------------- feed

def test_census_feed_shape_and_two_arm_minimum():
    feed = json.loads(FEED.read_text(encoding="utf-8"))
    assert feed["schema"] == "arm-census/v1"
    assert len(feed["arms"]) >= 2, "done-evidence: >=2 arms census-passed or honestly failed"
    for row in feed["arms"]:
        for field in ("arm_id", "provider", "model", "budget_class", "checks", "verdict"):
            assert field in row, f"census row missing {field}"
        assert row["verdict"] in ("eligible", "failed")
        assert "agent_loop" in row["checks"]


# ----------------------------------------------------------------- workflow

def test_workflow_selects_arm_before_builders():
    text = WORKFLOW.read_text(encoding="utf-8")
    select = text.index("Select build arm")
    gemini = text.index("uses: google-github-actions/run-gemini-cli")
    generic = text.index("Run the generic agent-loop builder")
    assert select < gemini and select < generic
    assert "build_arm_harness.py" in text
    assert "--select" in text


def test_workflow_builders_are_arm_conditional():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "if: steps.arm.outputs.harness == 'run-gemini-cli'" in text
    assert "if: steps.arm.outputs.harness == 'generic-agent-loop'" in text


def test_workflow_generic_builder_commits_and_opens_pr():
    text = WORKFLOW.read_text(encoding="utf-8")
    start = text.index("Commit and open PR for the generic builder")
    end = text.index("Verify build completion evidence")
    step = text[start:end]
    assert "git push" in step and "gh pr create" in step
    assert "Do not merge" in step or "do not merge" in step.lower()


def test_workflow_stamp_fanout_after_verify():
    text = WORKFLOW.read_text(encoding="utf-8")
    verify = text.index("Verify build completion evidence")
    fanout = text.index("dispatch-stamp-fanout.yml")
    failure = text.index("if: failure()")
    assert verify < fanout < failure, (
        "the rotation stamp fans out to the scoring planes after the "
        "#5142 verify verdict, before failure surfacing")
    assert "build-dispatch-stamp.json" in text


def test_census_workflow_bounds_and_artifacts():
    text = CENSUS_WORKFLOW.read_text(encoding="utf-8")
    assert "build_arm_census.py" in text
    assert text.count("actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02") == 2
    assert "arm-live-build" in text, "the live-build leg fires on the label of record"
    for secret in ("MISTRAL_API_KEY", "SEALION_API_KEY", "COHERE_API_KEY", "BASETEN_API_KEY"):
        assert secret in text
