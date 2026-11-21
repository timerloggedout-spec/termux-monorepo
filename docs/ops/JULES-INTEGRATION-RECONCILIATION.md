# Jules Integration Reconciliation

**Assessment date:** 2026-11-19  
**CNS work item:** CNS-15  
**Canonical repository workflows:** `.github/workflows/agent-jules-on-issues.yml`, `.github/workflows/agent-pr-jules-handoff.yml`, `.github/workflows/agent-review-auto-jules.yml`

## Decision

Preserve the repository's bounded Jules API integration as the canonical execution lane. Treat the supplied Jules workflow PDF as ecosystem reference material and adapt its examples to the repository's existing trust, source, branch, prompt, secret, and receipt contracts.

## Supplied PDF comparison

The supplied three-page PDF describes:
- Jules issue-label dispatch.
- Jules PR review and handoff patterns.
- VM setup guidance.
- A sample `google-labs-code/jules-action@v1` invocation using `gemini_api_key`.
- A reviewer example using `severity_threshold`.

The current repository implements a custom bounded Jules API session. Its issue workflow performs:
- Trusted actor and label authorization.
- `JULES_API_KEY` secret availability checks.
- Connected-source discovery.
- Source and branch validation.
- Bounded prompt construction with untrusted issue content fenced as data.
- Jules API session creation and attributable workflow receipts.

The current workflow tests explicitly protect the repository's selected API lane and action-reference boundary. Preserve these tests as the migration guard.

## Official action contract snapshot

The official Google Labs action metadata currently documents:
- `jules_api_key`
- `prompt`
- `starting_branch`
- `include_last_commit`
- `include_commit_log`

The official action contract is distinct from the repository's custom API integration. A migration to the official action requires a separate proposal, exact input/version verification, security review, source/branch policy reconciliation, and migration tests.

Official references:
- https://github.com/google-labs-code/jules-action/blob/main/README.md
- https://github.com/google-labs-code/jules-action/blob/main/action.yaml
- https://github.com/google-labs-code/jules-skills
- https://github.com/google-labs-code/jules-action/tree/main/examples

## Repository security and execution contract

1. Issue dispatch requires the repository's trusted actor and explicit `jules` label.
2. The workflow reads the connected repository source and validates the target branch before session creation.
3. The issue body remains untrusted input. The prompt builder frames it as task data and preserves repository instructions as the governing contract.
4. API credentials remain in GitHub Actions secrets and stay outside logs, prompts, comments, and artifacts.
5. A Jules session ID, source identity, target branch, task identity, and observed outcome form the invocation receipt.
6. Delegation remains distinct from completion. A later head mutation, exact-SHA gates, review disposition, and independent verification establish progress.
7. PR handoff comments require trusted authorship and a bounded `@jules` directive. Mutation receipts preserve baseline and observed head SHAs.

## Canonical tests

- `tests/test_agent_jules_on_issues.py`
- `tests/test_agent_pr_jules_handoff.py`

These tests cover trusted actor checks, label gating, source discovery, branch handling, prompt boundaries, action selection, and handoff receipts.

## CNS-15 acceptance

- [x] Supplied PDF reviewed against current repository workflows.
- [x] Official action input names checked against the action metadata.
- [x] Existing repository API lane and security boundary identified.
- [x] Existing workflow tests identified as the compatibility guard.
- [ ] Exact-head workflow tests pass on the CNS-15 integration revision.
- [ ] Live invocation receipt confirms provider/session attribution and the full handoff lifecycle.

**Status:** Architecture and source reconciliation complete; exact-head and live-invocation acceptance remain pending.
