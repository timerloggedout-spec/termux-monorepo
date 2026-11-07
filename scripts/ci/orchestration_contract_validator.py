#!/usr/bin/env python3
"""Validate native orchestration schemas using only the Python standard library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "docs" / "ops"
TREATMENT = "ORCHESTRATION-TREATMENT.schema.json"
RECEIPT = "ORCHESTRATION-RECEIPT.schema.json"

EXPECTED_STATES = {
    "DISPATCHED", "QUEUED", "RUNNING", "WAITING", "STEERED",
    "RETRYING", "COMPLETED", "FAILED", "CANCELLED",
}
EXPECTED_OUTCOMES = {"TASK_PASS", "TASK_FAIL", "UNKNOWN"}
EXPECTED_PROMOTIONS = {"PROMOTABLE", "NOT_PROMOTABLE", "UNKNOWN"}
EXPECTED_TREATMENT_STATUSES = {
    "candidate", "experimental", "accepted", "deprecated", "rejected",
}


def _load(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing required schema: {path.as_posix()}")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read valid JSON from {path.as_posix()}: {exc}")
    else:
        if not isinstance(value, dict):
            errors.append(f"schema root must be an object: {path.as_posix()}")
        else:
            return value
    return None


def _check_schema(name: str, schema: dict[str, Any], errors: list[str]) -> bool:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{name}: unexpected or missing JSON Schema draft")
    if schema.get("type") != "object":
        errors.append(f"{name}: root type must be object")
    if schema.get("additionalProperties") is not False:
        errors.append(f"{name}: root must reject undeclared properties")

    properties = schema.get("properties")
    required = schema.get("required")
    structurally_valid = True
    if not isinstance(properties, dict):
        errors.append(f"{name}: properties must be an object")
        structurally_valid = False
    if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
        errors.append(f"{name}: required must be a string array")
        structurally_valid = False
    if not structurally_valid:
        return False
    missing = sorted(set(required) - set(properties))
    if missing:
        errors.append(f"{name}: required keys lack property definitions: {', '.join(missing)}")
        return False
    return True


def validate_contracts(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    schema_dir = root / "docs" / "ops"
    treatment = _load(schema_dir / TREATMENT, errors)
    receipt = _load(schema_dir / RECEIPT, errors)

    if treatment is not None and _check_schema(TREATMENT, treatment, errors):
        props = treatment["properties"]
        status = props.get("status")
        status_enum = status.get("enum") if isinstance(status, dict) else None
        if not isinstance(status_enum, list) or not all(isinstance(x, str) for x in status_enum) or set(status_enum) != EXPECTED_TREATMENT_STATUSES:
            errors.append(f"{TREATMENT}: status lifecycle enum drifted")
        if "wait_policy" not in treatment["required"]:
            errors.append(f"{TREATMENT}: wait_policy must be required")
        if "evidence_contract" not in treatment["required"]:
            errors.append(f"{TREATMENT}: evidence_contract must be required")
        sha = props.get("source_sha", {})
        if not isinstance(sha, dict) or sha.get("pattern") != "^[0-9a-f]{40}$":
            errors.append(f"{TREATMENT}: source_sha must be a lowercase 40-character commit SHA")

    if receipt is not None and _check_schema(RECEIPT, receipt, errors):
        props = receipt["properties"]
        for field, expected in (
            ("state", EXPECTED_STATES),
            ("outcome", EXPECTED_OUTCOMES),
            ("promotion", EXPECTED_PROMOTIONS),
        ):
            field_schema = props.get(field)
            actual = field_schema.get("enum") if isinstance(field_schema, dict) else None
            if not isinstance(actual, list) or not all(isinstance(x, str) for x in actual) or set(actual) != expected:
                errors.append(f"{RECEIPT}: {field} enum drifted")
        required_ids = {
            "orchestration_id", "cycle_id", "attempt_id", "action_id",
            "event_id", "repo", "ref", "sha", "evidence_ids",
        }
        missing_ids = sorted(required_ids - set(receipt["required"]))
        if missing_ids:
            errors.append(f"{RECEIPT}: missing required identity/evidence fields: {', '.join(missing_ids)}")
        sha = props.get("sha")
        if not isinstance(sha, dict) or sha.get("pattern") != "^[0-9a-f]{40}$":
            errors.append(f"{RECEIPT}: sha must be a lowercase 40-character commit SHA")
        observed_at = props.get("observed_at")
        if not isinstance(observed_at, dict) or observed_at.get("format") != "date-time":
            errors.append(f"{RECEIPT}: observed_at must use date-time format")

    skill_path = root / ".agents" / "skills" / "orchestration-treatment-registry" / "SKILL.md"
    try:
        skill = skill_path.read_text(encoding="utf-8")
    except OSError:
        errors.append("missing orchestration-treatment-registry skill")
    else:
        for required_ref in (
            TREATMENT, RECEIPT, "EVIDENCE-ENVELOPE.schema.json",
            "ACTION-EFFECT-EVENT.schema.json", "adaptive-wait",
            "context-relationship-graph",
        ):
            if required_ref not in skill:
                errors.append(f"orchestration-treatment-registry skill missing reference: {required_ref}")

    errors.extend(validate_issue_comment_router_contracts(root))
    return errors



ROUTER_WORKFLOW = ".github/workflows/issue-comment-router.yml"
ROUTED_WORKFLOWS = {
    "agent-review-auto-jules": {
        "path": ".github/workflows/agent-review-auto-jules.yml",
        "inputs": {"pr_number", "comment_id", "comment_updated_at", "source_event"},
        "required_inputs": {"pr_number", "comment_id", "comment_updated_at", "source_event"},
        "secret": "JULES_API_KEY",
        "direct_events": {"pull_request_review", "pull_request_review_comment"},
    },
    "gemini-dispatch": {
        "path": ".github/workflows/gemini-dispatch.yml",
        "inputs": {"issue_number", "pr_number", "comment_id", "comment_updated_at", "source_event"},
        "required_inputs": {"issue_number", "comment_id", "comment_updated_at", "source_event"},
        "secret": "GEMINI_API_KEY",
        "direct_events": {"pull_request", "issues", "pull_request_review", "pull_request_review_comment"},
    },
    "agent-jules-on-issues": {
        "path": ".github/workflows/agent-jules-on-issues.yml",
        "inputs": {"issue_number", "comment_id", "comment_updated_at", "source_event"},
        "required_inputs": {"issue_number", "comment_id", "comment_updated_at", "source_event"},
        "secret": "JULES_API_KEY",
        "direct_events": {"issues"},
    },
}


def _read_workflow(root: Path, relative: str, errors: list[str]) -> str:
    path = root / relative
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"missing or unreadable workflow {relative}: {exc}")
        return ""


def _on_block(workflow: str) -> str:
    match = re.search(r"(?ms)^on:\s*\n(.*?)(?=^[A-Za-z0-9_.-]+:\s*(?:$|\n)|\Z)", workflow)
    return match.group(1) if match else ""


def _has_event(on_block: str, event: str) -> bool:
    return re.search(rf"(?m)^  {re.escape(event)}:\s*$", on_block) is not None


def _has_workflow_call_input(on_block: str, name: str, required: bool = True) -> bool:
    call = re.search(r"(?ms)^  workflow_call:\s*\n(.*?)(?=^  [A-Za-z0-9_-]+:\s*$|\Z)", on_block)
    if not call:
        return False
    input_block = re.search(
        rf"(?ms)^      {re.escape(name)}:\s*\n(.*?)(?=^      [A-Za-z0-9_-]+:\s*$|\Z)",
        call.group(1),
    )
    if not input_block or not re.search(r"(?m)^        type: string\s*$", input_block.group(1)):
        return False
    if required and not re.search(r"(?m)^        required: true\s*$", input_block.group(1)):
        return False
    return True


def _script_blocks(workflow: str) -> list[str]:
    """Return literal YAML script-block bodies so expressions can be rejected there."""
    lines = workflow.splitlines()
    blocks: list[str] = []
    for index, line in enumerate(lines):
        match = re.match(r"^(\s*)script:\s*\|\s*$", line)
        if not match:
            continue
        parent_indent = len(match.group(1))
        body: list[str] = []
        for candidate in lines[index + 1:]:
            if candidate.strip() and len(candidate) - len(candidate.lstrip()) <= parent_indent:
                break
            body.append(candidate)
        blocks.append("\n".join(body))
    return blocks

def validate_issue_comment_router_contracts(root: Path = ROOT) -> list[str]:
    """Keep issue-comment fan-out centralized and every reusable target revision-bound."""
    errors: list[str] = []
    router = _read_workflow(root, ROUTER_WORKFLOW, errors)
    router_on = _on_block(router)

    if not _has_event(router_on, "issue_comment"):
        errors.append("issue-comment router must own the issue_comment trigger")
    if not re.search(r"(?m)^    types: \[created, edited\]\s*$", router_on):
        errors.append("issue-comment router must cover created and edited comment revisions")
    if not re.search(r"(?m)^permissions:\s*\n  contents: read\n  issues: write\n  pull-requests: write\s*$", router):
        errors.append("issue-comment router must grant only the bounded caller-job permission ceiling")
    if not re.search(r"(?m)^  route:\n    permissions: \{\}\s*$", router):
        errors.append("issue-comment router classifier job must have no token permissions")
    if "actions/github-script@f28e40c7f34bde8b3046d885e986cb6290c5673b" not in router:
        errors.append("issue-comment router must pin github-script to the approved immutable revision")
    if "actions/checkout" in router:
        errors.append("issue-comment router must not add a checkout")
    if "actions: write" in router or "github.rest.actions.createWorkflowDispatch" in router:
        errors.append("issue-comment router must use reusable calls, not workflow-dispatch write authority")
    if "github.event.comment.id" not in router or "github.event.comment.updated_at" not in router:
        errors.append("issue-comment router concurrency must be scoped to comment ID and revision")
    if not re.search(r"(?m)^  cancel-in-progress: false\s*$", router):
        errors.append("issue-comment router must not cancel a distinct comment event")
    for route in ("needs_agent_review", "needs_gemini", "needs_jules"):
        if route not in router:
            errors.append(f"issue-comment router is missing route output {route}")
    for token in (
        "coderabbitai[bot]", "qodo-code-review[bot]", "devin-ai-integration[bot]",
        "@gemini-cli", "@sparkFlux", "@jules", "OWNER", "MEMBER", "COLLABORATOR",
    ):
        if token not in router:
            errors.append(f"issue-comment router is missing trust/command contract: {token}")

    if "new Set(['OWNER', 'MEMBER', 'COLLABORATOR'])" not in router:
        errors.append("issue-comment router must use the exact repository collaborator association allowlist")
    jules_route = router.split("const needsJules =", 1)[-1].split("const needsGemini =", 1)[0]
    if not all(part in jules_route for part in ("action === 'created'", "!isPullRequest", "trustedHuman", "body.startsWith('@jules')", "body.startsWith('@Jules')")):
        errors.append("Jules route must remain created-only, trusted-human, exact-prefix, and non-PR")
    gemini_route = router.split("const needsGemini =", 1)[-1].split("const needsAgentReview =", 1)[0]
    if not all(part in gemini_route for part in ("action === 'created'", "trustedHuman", "body.startsWith('@gemini-cli')", "body.startsWith('@sparkFlux')", "body.startsWith('@sparkflux')")):
        errors.append("Gemini route must remain created-only, trusted-human, and exact-prefix")
    review_route = router.split("const needsAgentReview =", 1)[-1].split("const needsLedger =", 1)[0]
    if not all(part in review_route for part in ("['created', 'edited'].includes(action)", "isPullRequest", "actor.type === 'Bot'", "trustedProviderBots.has(login)")):
        errors.append("Agent review route must remain PR-only and provider-bot-only")
    if "source_event" not in router:
        errors.append("issue-comment router must pass source-event provenance")
    if "secrets: inherit" in router:
        errors.append("issue-comment router must not inherit the entire repository secret set")

    for route_name, contract in ROUTED_WORKFLOWS.items():
        target = _read_workflow(root, contract["path"], errors)
        target_on = _on_block(target)
        if _has_event(target_on, "issue_comment"):
            errors.append(f"{contract['path']} must not directly subscribe to issue_comment")
        if not _has_event(target_on, "workflow_call"):
            errors.append(f"{contract['path']} must expose workflow_call")
        for input_name in contract["inputs"]:
            if not _has_workflow_call_input(target_on, input_name, required=input_name in contract["required_inputs"]):
                errors.append(f"{contract['path']} workflow_call input is missing or mistyped: {input_name}")
        for event in contract["direct_events"]:
            if not _has_event(target_on, event):
                errors.append(f"{contract['path']} must preserve direct event trigger: {event}")
        if "github.rest.issues.getComment" not in target:
            errors.append(f"{contract['path']} must re-fetch the source comment by ID")
        if any("${{" in block for block in _script_blocks(target)):
            errors.append(f"{contract['path']} must pass workflow expressions through env/with data, never inline script/run source")
        target_job = {
            "agent-review-auto-jules": "detect-bot-feedback",
            "gemini-dispatch": "dispatch",
            "agent-jules-on-issues": "jules-on-mention",
        }[route_name]
        if f"  {target_job}:\n    needs: validate-source-comment" not in target:
            errors.append(f"{contract['path']} execution job must depend on source-comment validation")
        if "needs.validate-source-comment.outputs.valid == 'true'" not in target:
            errors.append(f"{contract['path']} execution job must reject an invalid source-comment revision")
        if "comment.updated_at === expectedUpdatedAt" not in target:
            errors.append(f"{contract['path']} must reject stale comment revisions")
        if "comment.issue_url" not in target:
            errors.append(f"{contract['path']} must verify the comment's issue identity")
        if f"      {contract['secret']}:" not in _on_block(target) or "required: false" not in _on_block(target):
            errors.append(f"{contract['path']} must declare its provider secret as optional workflow_call input")
        if f"{contract['secret']}: ${{{{ secrets.{contract['secret']} }}}}" not in router:
            errors.append(f"issue-comment router must pass only the target secret: {contract['secret']}")
        if f"uses: ./.github/workflows/{contract['path'].split('/')[-1]}" not in router:
            errors.append(f"issue-comment router is missing reusable route: {route_name}")

    return errors



def main() -> int:
    errors = validate_contracts()
    if errors:
        print("Orchestration contract validation FAILED:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Orchestration contract validation PASSED (stdlib-only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
