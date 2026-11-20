# CNS Integration — Source and Evidence Basis

## Repository source of truth

This proposal is based on the inspected `master` tree at commit `939ecc225675541d1ad5b829b427c7ac77ac2642` on 2026-11-20, plus the exact files and active pull requests linked below.

CNS is a repository-wide architectural synthesis. The inspected tree contains the component organs; this proposal establishes their integration contract and status model.

## Canonical architecture sources

- `CLAUDE.md` — FA-ADE posture, BIUDL motion, governance sequence, dual gates, and adaptive wait.
- `docs/architecture/AGENT-TEAM-CONTROL-PLANE.md` — manager, scout, telemetry, review, MoneyBall/3L0, and BIUDL.
- `docs/ops/AGENT-TEAM-ORCHESTRATION.md` — manager/router separation, contributor identity, admission, and execution adapters.
- `docs/ops/CONTEXT-RELATIONSHIP-INDEX.md` — context graph model, edge confidence, context deltas, temporal traversal, and authority.
- `docs/ops/3L0-PLANE.md` — 3L0 scoring authority and separation from MoneyBall.
- `docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd` — evidence corpus, reducers, snapshots, and read-only presentation.
- `docs/proposals/PROCESS.md` and `docs/proposals/registry.yaml` — proposal lifecycle and active-work registry.

## Active implementation evidence

- [PR #5525 — Brain kernel and MOSAIC](https://github.com/timerloggedout-spec/termux-monorepo/pull/5525): merged Rust kernel and specialist contract.
- [PR #5544 — ORBIT / SHIELD](https://github.com/timerloggedout-spec/termux-monorepo/pull/5544): open draft at assessment; arbitration and context-admission implementation.
- [PR #5637 — Synaptic Bus](https://github.com/timerloggedout-spec/termux-monorepo/pull/5637): open draft at assessment; envelope, registry, compatibility, and receipt adapter.
- [PR #5635 — notation enforcement](https://github.com/timerloggedout-spec/termux-monorepo/pull/5635): open at assessment; notation and style enforcement proposal.
- [PR #5665 — PCDOE-008](https://github.com/timerloggedout-spec/termux-monorepo/pull/5665): open draft at assessment; prioritization policy and shadow implementation.
- [CRG proposal](../context-relationship-graph/MANIFEST.md): canonical relationship graph and Historical Corpus Explorer extension.

## Status discipline

Repository presence proves that an artifact exists. A merged PR proves that its commit entered the branch. A green workflow proves the checks represented by that workflow. A runtime integration claim requires an attributable runtime receipt. This proposal preserves those distinctions.

The registry and map classify each connection as verified, derived, proposed, or unresolved. The CNS health model reports freshness and coverage from canonical records.

## Uploaded reference review

### Loopy API / Loop Library skill JSON

The supplied `skill-loopy-api-loop-library-skill.json` defines nine routes: Discover, Find, Audit/Loop Doctor, Adapt, Craft, Run, Debrief, Save/Reuse, and Publish. Its six-step feedback cycle is Observe → Choose → Act → Verify → Record → Repeat or stop. It defines terminal states `success`, `clean no-op`, `blocked`, `approval-required`, `exhausted`, and `stagnated`, plus bounded-run receipts and explicit approval boundaries for consequential actions.

The repository already has a broader twelve-step adaptive-feedback-cycle contract with historical correlation, provider/catalog observation, adaptive waiting, and outcome verification. CNS-14 integrates the bounded-loop terminal-state and receipt semantics into that canonical skill while preserving the existing twelve-step operating model. The supplied project has no root `LOOPS.md`; CNS-14 therefore focuses on the existing skill and inventory.

Upstream references:
- [Forward Future Loopy repository](https://github.com/Forward-Future/loopy)
- [Loopy skill and Loop Library separation](https://github.com/Forward-Future/loopy/blob/main/README.md)
- [Loop Library website](https://signals.forwardfuture.ai/loop-library/)

### Jules Skills, Actions, and Workflows PDF

The supplied three-page PDF describes the Jules ecosystem, a label-triggered issue workflow, a PR review workflow, and VM setup guidance. Its example uses `google-labs-code/jules-action@v1` with `gemini_api_key`, and its reviewer example supplies `severity_threshold`.

The current repository issue workflow has a different, security-specific contract: trusted label-actor authorization, `JULES_API_KEY` availability checks, connected-source discovery, branch validation, untrusted issue payload fencing, and a bounded Jules API session. Its tests explicitly assert that the workflow avoids the legacy `google-labs-code/jules-action@` and `google-labs-code/jules-invoke@v1` actions. CNS-15 preserves this repository contract and treats the PDF examples as ecosystem reference material requiring current compatibility checks.

Current official references:
- [Google Labs Jules Action README](https://github.com/google-labs-code/jules-action/blob/main/README.md)
- [Google Labs Jules Action input contract](https://github.com/google-labs-code/jules-action/blob/main/action.yaml)
- [Google Labs Jules Skills repository](https://github.com/google-labs-code/jules-skills)
- [Official Jules workflow examples and security guidance](https://github.com/google-labs-code/jules-action/tree/main/examples)

The official action metadata lists `jules_api_key`, `prompt`, `starting_branch`, `include_last_commit`, and `include_commit_log`. The repository's current custom API lane remains a distinct integration choice. CNS-15 validates its existing trigger, permissions, source identity, branch, secret, and receipt contracts rather than replacing them with a sample action.
