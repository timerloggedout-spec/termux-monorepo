"""Tests for .github/workflows/deepseek-ci.yml.

These tests validate the structure and security-relevant properties of the
DeepSeek CI workflow added in this PR:
  - the "review" job (peer Omni / OpenRouter routing via reusable actions)
  - the opt-in "deepseek-webwrapper" job (never runs on pull_request)

Structural assertions that require parsing the YAML are gated behind
``pytest.importorskip("yaml")`` so the suite still runs (with a reduced,
text-based set of checks) in environments where PyYAML is not installed.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "deepseek-ci.yml"


@pytest.fixture(scope="module")
def workflow_text():
    assert WORKFLOW_PATH.is_file(), f"Workflow file not found: {WORKFLOW_PATH}"
    return WORKFLOW_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def workflow_yaml():
    yaml = pytest.importorskip("yaml", reason="PyYAML not installed in this environment")
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Basic file sanity (no external dependencies required)
# ---------------------------------------------------------------------------

class TestWorkflowFileBasics:
    def test_file_exists(self):
        assert WORKFLOW_PATH.is_file()

    def test_file_is_non_empty_text(self, workflow_text):
        assert len(workflow_text) > 0
        assert "\x00" not in workflow_text

    def test_has_expected_workflow_name(self, workflow_text):
        assert "name: 'DeepSeek CI (peer Omni" in workflow_text

    def test_declares_both_jobs(self, workflow_text):
        assert re.search(r"^\s{2}review:\s*$", workflow_text, re.MULTILINE)
        assert re.search(r"^\s{2}deepseek-webwrapper:\s*$", workflow_text, re.MULTILINE)

    def test_top_level_permissions_are_empty(self, workflow_text):
        # The workflow-level default must be least-privilege; jobs opt in
        # to the specific permissions they need.
        assert re.search(r"^permissions:\s*\{\}\s*$", workflow_text, re.MULTILINE)

    def test_concurrency_group_is_scoped_per_pr(self, workflow_text):
        assert "group: deepseek-ci-${{ github.event.pull_request.number || github.run_id }}" in workflow_text
        assert "cancel-in-progress: true" in workflow_text


# ---------------------------------------------------------------------------
# Pinned action references (security: avoid mutable tags)
# ---------------------------------------------------------------------------

class TestPinnedActionReferences:
    @pytest.mark.parametrize(
        "action,sha,version_comment",
        [
            ("actions/checkout", "08c6903cd8c0fde910a37f88322edcfb5dd907a8", "v5.0.0"),
            ("actions/setup-node", "39370e3970a6d050c480ffad4ff0ed4d3fdee5af", "v4.1.0"),
            ("actions/setup-python", "0b93645e9fea7318ecaed2b4117511b8a72f1f55", "v5.3.0"),
        ],
    )
    def test_action_pinned_to_full_commit_sha(self, workflow_text, action, sha, version_comment):
        pattern = rf"uses:\s*{re.escape(action)}@{sha}\s*#\s*{re.escape(version_comment)}"
        assert re.search(pattern, workflow_text), (
            f"{action} must be pinned to full commit SHA {sha} (# {version_comment})"
        )

    def test_no_action_reference_uses_a_mutable_tag(self, workflow_text):
        # Every third-party `uses:` (excluding local composite actions starting
        # with "./") must be pinned with a 40-char commit SHA, not a floating tag
        # like @v5 or @main.
        for line in workflow_text.splitlines():
            m = re.search(r"uses:\s*([^\s#]+)", line)
            if not m:
                continue
            ref = m.group(1)
            if ref.startswith("./"):
                continue  # local composite action, not an external tag
            assert "@" in ref, f"External action reference missing pin: {ref}"
            sha = ref.split("@", 1)[1]
            assert re.fullmatch(r"[0-9a-f]{40}", sha), (
                f"External action {ref} is not pinned to a full 40-char commit SHA"
            )


# ---------------------------------------------------------------------------
# Secret / injection hardening in the inline shell script
# ---------------------------------------------------------------------------

class TestReviewPromptScriptHardening:
    def test_uses_random_delimiter_for_multiline_output(self, workflow_text):
        # Guards against PR-diff content terminating the heredoc/output early
        # (GITHUB_OUTPUT injection).
        assert 'DELIM="DSCR_$(openssl rand -hex 8)"' in workflow_text
        assert "prompt<<${DELIM}" in workflow_text

    def test_uses_set_euo_pipefail(self, workflow_text):
        assert "set -euo pipefail" in workflow_text

    def test_diff_fetch_is_bounded_in_size(self, workflow_text):
        # Truncate the diff to avoid unbounded payloads / huge prompts.
        assert "head -c 24000" in workflow_text

    def test_target_pr_is_validated_as_numeric(self, workflow_text):
        assert r'[[ "${TARGET_PR:-}" =~ ^[0-9]+$ ]]' in workflow_text


# ---------------------------------------------------------------------------
# Web-wrapper opt-in job: must never run implicitly on pull_request
# ---------------------------------------------------------------------------

class TestWebWrapperJobIsOptIn:
    def test_never_triggered_by_pull_request_condition(self, workflow_text):
        job_text = workflow_text.split("deepseek-webwrapper:", 1)[1]
        job_if = re.search(r"if:\s*\|\s*\n(.*?)\n\s*runs-on:", job_text, re.DOTALL)
        assert job_if, "Could not locate the deepseek-webwrapper job's `if:` condition"
        condition = job_if.group(1)
        assert "workflow_dispatch" in condition
        assert "pull_request" not in condition

    def test_requires_explicit_opt_in_flag(self, workflow_text):
        assert "inputs.enable_deepseek_webwrapper == true" in workflow_text
        assert "vars.DEEPSEEK_WEBWRAPPER_ENABLED == '1'" in workflow_text

    def test_has_bounded_timeout(self, workflow_text):
        job_text = workflow_text.split("deepseek-webwrapper:", 1)[1]
        assert re.search(r"timeout-minutes:\s*10", job_text)

    def test_job_permissions_are_read_only(self, workflow_text):
        job_text = workflow_text.split("deepseek-webwrapper:", 1)[1]
        job_text = job_text.split("steps:", 1)[0]
        assert re.search(r"permissions:\s*\n\s*contents:\s*read", job_text)
        assert "write" not in job_text

    def test_token_missing_is_handled_non_fatally(self, workflow_text):
        assert "DEEPSEEK_TOKEN not set" in workflow_text
        assert "skipping DeepSeek web-wrapper smoke test" in workflow_text

    def test_session_state_is_sandboxed_under_runner_temp(self, workflow_text):
        assert 'export HOME="${RUNNER_TEMP}/deepseek-webwrapper-home"' in workflow_text

    def test_transient_session_dir_is_always_discarded(self, workflow_text):
        # The cleanup step must run even if prior steps fail.
        idx = workflow_text.index("Discard transient session directory")
        cleanup_block = workflow_text[idx:]
        assert re.search(r"if:\s*always\(\)", cleanup_block)
        assert 'rm -rf "${RUNNER_TEMP}/deepseek-webwrapper-home"' in cleanup_block

    def test_smoke_test_failure_is_non_blocking(self, workflow_text):
        job_text = workflow_text.split("deepseek-webwrapper:", 1)[1]
        assert "except Exception as e:" in job_text
        assert "non-blocking" in job_text


# ---------------------------------------------------------------------------
# Structural checks that require a real YAML parse
# ---------------------------------------------------------------------------

class TestWorkflowStructure:
    def test_top_level_keys(self, workflow_yaml):
        assert workflow_yaml["name"] == (
            "DeepSeek CI (peer Omni \u2194 OpenRouter HTTPS + opt-in web-wrapper)"
        )
        # PyYAML parses the `on:` key as boolean True under YAML 1.1 rules.
        trigger_key = True if True in workflow_yaml else "on"
        assert trigger_key in workflow_yaml
        assert "concurrency" in workflow_yaml
        assert workflow_yaml["permissions"] == {}
        assert set(workflow_yaml["jobs"].keys()) == {"review", "deepseek-webwrapper"}

    def test_pull_request_trigger_types(self, workflow_yaml):
        trigger_key = True if True in workflow_yaml else "on"
        triggers = workflow_yaml[trigger_key]
        assert triggers["pull_request"]["types"] == ["opened", "synchronize", "reopened"]

    def test_workflow_dispatch_input_definition(self, workflow_yaml):
        trigger_key = True if True in workflow_yaml else "on"
        triggers = workflow_yaml[trigger_key]
        wd_input = triggers["workflow_dispatch"]["inputs"]["enable_deepseek_webwrapper"]
        assert wd_input["required"] is False
        assert wd_input["type"] == "boolean"
        assert wd_input["default"] is False

    def test_review_job_runner_and_permissions(self, workflow_yaml):
        review = workflow_yaml["jobs"]["review"]
        assert review["runs-on"] == "ubuntu-latest"
        assert review["permissions"] == {
            "contents": "read",
            "issues": "write",
            "pull-requests": "write",
        }

    def test_review_job_condition_excludes_forks_and_drafts(self, workflow_yaml):
        review = workflow_yaml["jobs"]["review"]
        condition = review["if"]
        assert "github.event_name == 'pull_request'" in condition
        assert "github.event.pull_request.head.repo.fork == false" in condition
        assert "github.event.pull_request.draft == false" in condition

    def test_review_job_step_names_in_order(self, workflow_yaml):
        review = workflow_yaml["jobs"]["review"]
        step_names = [s.get("name") for s in review["steps"] if "name" in s]
        assert step_names == [
            "Model router (peer Omni \u2194 OpenRouter)",
            "Note skip (no comment; shared soft budget)",
            "Build review prompt (API diff \u2014 independent of checkout ref)",
            "OmniRoute review (peer)",
            "OpenRouter review (peer)",
        ]

    def test_model_router_step_inputs(self, workflow_yaml):
        review = workflow_yaml["jobs"]["review"]
        router_step = next(s for s in review["steps"] if s.get("id") == "router")
        assert router_step["uses"] == "./.github/actions/model-router"
        assert router_step["with"]["role"] == "review"
        assert router_step["with"]["has-gemini"] is False

    def test_peer_review_steps_use_continue_on_error(self, workflow_yaml):
        review = workflow_yaml["jobs"]["review"]
        for name in ("OmniRoute review (peer)", "OpenRouter review (peer)"):
            step = next(s for s in review["steps"] if s.get("name") == name)
            assert step["continue-on-error"] is True

    def test_omni_and_openrouter_steps_are_mutually_exclusive_conditions(self, workflow_yaml):
        review = workflow_yaml["jobs"]["review"]
        omni_step = next(s for s in review["steps"] if s.get("name") == "OmniRoute review (peer)")
        openrouter_step = next(s for s in review["steps"] if s.get("name") == "OpenRouter review (peer)")
        assert "steps.router.outputs.provider == 'omni'" in omni_step["if"]
        assert "steps.router.outputs.provider == 'openrouter'" in openrouter_step["if"]

    def test_webwrapper_job_structure(self, workflow_yaml):
        job = workflow_yaml["jobs"]["deepseek-webwrapper"]
        assert job["runs-on"] == "ubuntu-latest"
        assert job["timeout-minutes"] == 10
        assert job["permissions"] == {"contents": "read"}
        step_names = [s.get("name") for s in job["steps"] if "name" in s]
        assert step_names == [
            "Setup Node.js (PoW WASM solver)",
            "Setup Python",
            "Install Python dependencies",
            "DeepSeek web-wrapper session + PoW smoke test (transient, opt-in)",
            "Discard transient session directory",
        ]

    def test_webwrapper_job_condition_requires_dispatch(self, workflow_yaml):
        job = workflow_yaml["jobs"]["deepseek-webwrapper"]
        condition = job["if"]
        assert "workflow_dispatch" in condition
        assert "pull_request" not in condition

    def test_setup_node_and_python_versions(self, workflow_yaml):
        job = workflow_yaml["jobs"]["deepseek-webwrapper"]
        node_step = next(s for s in job["steps"] if s.get("name") == "Setup Node.js (PoW WASM solver)")
        python_step = next(s for s in job["steps"] if s.get("name") == "Setup Python")
        assert node_step["with"]["node-version"] == "20"
        assert python_step["with"]["python-version"] == "3.11"

    def test_checkout_never_persists_credentials(self, workflow_yaml):
        for job in workflow_yaml["jobs"].values():
            for step in job["steps"]:
                if step.get("uses", "").startswith("actions/checkout@"):
                    assert step["with"]["persist-credentials"] is False

    def test_cleanup_step_runs_always(self, workflow_yaml):
        job = workflow_yaml["jobs"]["deepseek-webwrapper"]
        cleanup = next(s for s in job["steps"] if s.get("name") == "Discard transient session directory")
        assert cleanup["if"] == "always()"