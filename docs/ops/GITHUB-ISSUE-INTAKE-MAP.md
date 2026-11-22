# GitHub Issue Intake, Templates, Labels, and Triggers

**Canonical discovery map for** `timerloggedout-spec/termux-monorepo`.

Recon baseline: `master` at `b7a3aa85318fecbaa5ea8c362fdfbf8854d47d75`, observed 2026-11-22. This map records the executable event subscriptions, job-level guards, template metadata, dispatch admission, and downstream effects. It separates template labels from label-added triggers and from QUE admission.

## Start here

| Need | Source |
|---|---|
| Full issue-form and trigger map | This document |
| QUE dispatch-block contract | [ISSUE-TEMPLATE-DISPATCH.md](ISSUE-TEMPLATE-DISPATCH.md) |
| Issue categorization and lifecycle | [ISSUE-LIFECYCLE.md](ISSUE-LIFECYCLE.md) |
| Research provider/service intake | [RESEARCH-TRIGGERS.md](RESEARCH-TRIGGERS.md) |
| APK cross-reference forms | [APK-XREF-TEMPLATES.md](APK-XREF-TEMPLATES.md) |
| RE taxonomy/toolkit forms | [RE-TAXONOMY-TEMPLATES.md](RE-TAXONOMY-TEMPLATES.md) |
| EGM trigger stakes and lifecycle | [EGM-TEMPLATE-TRIGGER.md](EGM-TEMPLATE-TRIGGER.md) |
| Repository collaborator entry | [CLAUDE.md](../../CLAUDE.md) |
| Workflow source directory | [`.github/workflows/`](../../.github/workflows/) |
| Issue form source directory | [`.github/ISSUE_TEMPLATE/`](../../.github/ISSUE_TEMPLATE/) |

## Runtime model

```text
Issue form / API filing
        |
        v
Template labels + title prefix + body contract
        |
        +----------------------+-----------------------+
        |                      |                       |
        v                      v                       v
Direct event intake      Label-added command      Manual / scheduled
(open/edit/reopen)       (labeled)                lifecycle / observer
        |                      |                       |
        v                      v                       v
Parser + validator       Permission / flag gate   Census / label floor
        |                      |                       |
        +----------------------+-----------------------+
                               |
                               v
                  Comment / record / artifact / queue
                               |
                               v
                    QUE admission where declared
```

A template enters the QUE dispatch subset when it contains a `SWARM-DISPATCH-BEGIN` block. Specialized issue intake workflows remain distinct from that admission contract.

## 1. All 15 issue templates

| Template | Labels at filing | Event route | Dispatch block | Current behavior |
|---|---|---|---|---|
| [`apk-cross-reference.yml`](../../.github/ISSUE_TEMPLATE/apk-cross-reference.yml) | `apk-xref` | `apk-xref-intake.yml`: issues `opened`, `reopened`, `edited` | — | Parses the request into `apk-xref/v1`; edit re-runs intake |
| [`apk-cross-reference-findings.yml`](../../.github/ISSUE_TEMPLATE/apk-cross-reference-findings.yml) | `apk-xref` | Same `apk-xref-intake.yml` route | — | Parses findings; the parser derives request/findings from the submitted fields |
| [`bug.yml`](../../.github/ISSUE_TEMPLATE/bug.yml) | `bug` | Generic issue lifecycle | — | Label-at-birth; deterministic label pass focuses on unlabelled issues |
| [`data-ingestion.yml`](../../.github/ISSUE_TEMPLATE/data-ingestion.yml) | `data-ingestion` | Challenge-entries lane hand triage | — | Dedicated intake workflow remains pending; the form and `ops/data_ingestion/README.md` describe the manual route |
| [`delphi-rfp.yml`](../../.github/ISSUE_TEMPLATE/delphi-rfp.yml) | `delphi:rfp` | `delphi-gate.yml`: issues `opened`, `edited`, `labeled`, `reopened`; issue comments; hourly sweep | — | Label-gated oracle/panel workflow; conversational intake also uses `delphi-intake.yml` |
| [`egm-review.yml`](../../.github/ISSUE_TEMPLATE/egm-review.yml) | `egm-review` | `egm-review-dispatch.yml`: issues `opened`, `reopened`; 30-minute sweep | — | Label or `[egm]` title prefix; stamps the instance; sweep enforces the fail-closed review leg |
| [`game-development-task.yml`](../../.github/ISSUE_TEMPLATE/game-development-task.yml) | `game-development` | `swarm-admission.yml`, then `game-development-dispatch.yml` on admission workflow completion | Yes — lane `game-development`, tier 3 | Downstream route consumes the `issue-admission` artifact and queues only an admitted matching filing |
| [`project-task.yml`](../../.github/ISSUE_TEMPLATE/project-task.yml) | `project-task` | `project-task-dispatch.yml`: issues `opened`, `reopened`; also matched by `swarm-admission.yml` | Yes — lane `swarm-dispatch`, tier 3 | Direct intake parses and queues; see the admission-bypass finding in §5 |
| [`proposal.yml`](../../.github/ISSUE_TEMPLATE/proposal.yml) | `proposal` | Generic issue lifecycle; proposal document validation is a separate PR/push route | — | Label-at-birth; proposal registry validation runs from `proposal-lifecycle.yml` when proposal files change |
| [`research-provider.yml`](../../.github/ISSUE_TEMPLATE/research-provider.yml) | `research`, `research:provider` | `research-intake.yml`: issues `opened`, `reopened`, `edited`; marker comment | — | Deterministic provider seed intake; edit/reopen/comment can re-run it |
| [`research-service.yml`](../../.github/ISSUE_TEMPLATE/research-service.yml) | `research`, `research:service` | Same `research-intake.yml` route | — | Deterministic service/repository seed intake |
| [`reverse-engineering-taxonomy.yml`](../../.github/ISSUE_TEMPLATE/reverse-engineering-taxonomy.yml) | `re-taxonomy` | `re-taxonomy-intake.yml`: issues `opened`, `reopened`, `edited` | — | Parses and validates a taxonomy/toolkit proposal |
| [`reverse-engineering-taxonomy-record.yml`](../../.github/ISSUE_TEMPLATE/reverse-engineering-taxonomy-record.yml) | `re-taxonomy` | Same `re-taxonomy-intake.yml` route | — | Parses the validated placement/evidence record |
| [`roadmap-completion.md`](../../.github/ISSUE_TEMPLATE/roadmap-completion.md) | `roadmap`, `completion`, `enhancement`; add `roadmap:{slug}` and `exercise:{slug}` for a specific exercise | `roadmap-completion.yml`: issues `opened`, `edited`, `labeled`, `reopened`; push to matching `evidence.json`; manual dispatch | — | Validates the configured evidence file and posts a result to the matching issue; badge/README publication and closure remain explicit follow-up steps |
| [`target-brief.yml`](../../.github/ISSUE_TEMPLATE/target-brief.yml) | `target-brief` | `target-intake.yml`: issues `opened`, `edited`, `reopened` | — | Validates scope/authorization and comments a taxonomy-mapped Foundry dispatch plan |

The directory contains 15 templates. `.github/ISSUE_TEMPLATE/config.yml` is absent, so GitHub's default blank-issue behavior remains available.

## 2. QUE dispatch-block coverage

The executable admission parser is `scripts/ops/swarm_admission.py`. It scans `.github/ISSUE_TEMPLATE/*.yml`, matches declared labels/title prefixes, and evaluates the block through the tier → after → chain → flow guard order.

| Template | Block lane | Tier | Declared route | Downstream admission evidence |
|---|---|---:|---|---|
| `project-task.yml` | `swarm-dispatch` | 3 | `project-task-dispatch.yml` | Admission workflow evaluates the block; direct issue-event intake remains active, creating the divergence in §5 |
| `game-development-task.yml` | `game-development` | 3 | `game-development-dispatch.yml` | Route consumes the `issue-admission` artifact and requires `decision: admitted` |

The other 13 forms use specialized direct intake or manual lifecycle handling. Their event route and label behavior are listed in §1.

## 3. Label-added triggers outside ordinary form creation

These workflows subscribe to `issues: [labeled]` or `pull_request: [labeled]`. A template's label-at-birth is part of its `opened` payload; that event remains distinct from a later label-added event.

| Label / command | Workflow | Trigger and guard | Effect / qualification |
|---|---|---|---|
| `jules`, `Jules`, `JULES` | [`agent-jules-on-issues.yml`](../../.github/workflows/agent-jules-on-issues.yml) | Issue `labeled`; trusted collaborator comment beginning `@jules` or `@Jules` | Bounded Jules session after actor permission verification |
| `jules` | [`doe-live1-audit.yml`](../../.github/workflows/doe-live1-audit.yml) | Issue `labeled`; manual dispatch also supported | Separate DoE live-1 assignment-ledger audit; the shared label fans out to both Jules and DoE lanes |
| `ecc-tools`, `ecc`, `ECC` | [`agent-ecc-tools-ops.yml`](../../.github/workflows/agent-ecc-tools-ops.yml) | Issue `labeled`; authorized issue comments | Outbound commands require repository variable `ECC_TOOLS_APP_ENABLED=true` |
| `mesh:request` | [`mesh-request.yml`](../../.github/workflows/mesh-request.yml) | Issue `labeled`; manual dispatch also supported | Appends an allowlisted mesh request |
| `arm-live-build` | [`build-arm-census.yml`](../../.github/workflows/build-arm-census.yml) | Pull request `labeled` event | Starts the live-build proof leg for the labeled PR |

## 4. Broad observers and lifecycle automation

| Workflow | Subscription / cadence | Role |
|---|---|---|
| [`swarm-admission.yml`](../../.github/workflows/swarm-admission.yml) | Issues `opened`, `reopened` | Scans issue templates for dispatch blocks; stamps `swarm-admitted` or `deferred-by-tier` |
| [`issue-lifecycle-triage.yml`](../../.github/workflows/issue-lifecycle-triage.yml) | Issues `opened`, `reopened`; Tuesday 07:17 UTC; manual dispatch | Deterministic label floor for unlabelled open issues only |
| [`issue-observatory.yml`](../../.github/workflows/issue-observatory.yml) | Issues `opened`, `edited`, `labeled`, `unlabeled`, `closed`, `reopened`; manual dispatch | Read-only relationship/similarity observation and artifact publication |
| [`sweep-accountability.yml`](../../.github/workflows/sweep-accountability.yml) | Issues `opened`, `edited`, `closed`, `reopened`, `labeled`, `unlabeled`, `assigned`, `unassigned`; PR lifecycle; push/schedule/manual; issue comments | Accountability census and receipt ledger; non-master refs skip receipt pushes |
| [`issue-comment-router.yml`](../../.github/workflows/issue-comment-router.yml) | Issue comments `created` | Classifies `@jules`, `@gemini`, and `Implements:`; route steps are placeholder echoes |
| [`delphi-intake.yml`](../../.github/workflows/delphi-intake.yml) | Issue comments `created` with `<!-- request-delphi-intake -->`; manual dispatch | Creates a completed `delphi:rfp` issue from conversational intake |
| [`research-intake.yml`](../../.github/workflows/research-intake.yml) | Issues `opened`, `reopened`, `edited`; marker comment | Deterministic research seed intake; its event subscription intentionally omits `labeled` |
| [`roadmap-sync.yml`](../../.github/workflows/roadmap-sync.yml) | Monday schedule; manual dispatch | Syncs the `roadmaps/` tree; it is separate from the roadmap-completion issue form |
| [`roadmap-completion.yml`](../../.github/workflows/roadmap-completion.yml) | Issues `opened`, `edited`, `labeled`, `reopened`; push to matching exercise `evidence.json`; manual dispatch | Runs `roadmap-completions/scripts/verify-completion.py`, summarizes evidence checks, and comments on matching open issues |
| [`proposal-lifecycle.yml`](../../.github/workflows/proposal-lifecycle.yml) | PR/push paths under `docs/proposals/**` and `scripts/proposals/**`; manual dispatch | Validates the proposal registry and PR hygiene; it is separate from proposal issue intake |

### Deterministic label floor

`scripts/issue_lifecycle/triage_labels.py` applies labels only to open issues whose label set is empty. It uses title-prefix rules and the existing label allowlist:

| Title prefix | Proposed labels |
|---|---|
| `[actions incident]` | `bug`, `ci` |
| `[dph-` | `enhancement`, `automation` |
| `deepagent task:` | `agent` |
| `fix(`, `fix:`, `bug:`, `[bug]` | `bug` |
| `ops:`, `ops(` | `ops` |
| `feat:`, `feat(` | `enhancement` |
| `[target]`, `[target ` | `target-brief` |
| `[delphi:rfp]`, `delphi:rfp` | `delphi:rfp` |
| `proposal:`, `[proposal]` | `proposal`; add `research` when the title includes `investigate` |

The label pass reads the existing taxonomy and preserves every issue that already carries a label. Template-assigned labels therefore remain the primary creation-time classification.

## 5. Verified alignment gaps

1. **Project Task admission bypass.** `project-task.yml` declares a QUE dispatch block and `swarm-admission.yml` evaluates it. The current `project-task-dispatch.yml` also subscribes directly to issue `opened/reopened` events and queues after parser success. Its current input is the issue event rather than the `issue-admission` artifact. The direct path leaves an admission bypass; the Game Development route provides the artifact-gated comparison pattern.
2. **Research trigger documentation drift.** `research-intake.yml` subscribes to `opened/reopened/edited` and marker comments. Its workflow header and older trigger prose previously described `labeled`; this map records the executable subscription and the accompanying documentation correction.
3. **Roadmap completion automation.** `roadmap-completion.yml` now handles issue lifecycle events, matching evidence pushes, and manual dispatch. `verify-completion.py` checks configured evidence paths, code constraints, submitted test-result metadata, documentation requirements, and required portfolio files from a local directory or GitHub repository tree. It posts a result to the matching issue. Badge generation, README publication, and automatic issue closure remain separate publication work; the template now describes this exact boundary.
4. **Gemini lifecycle history.** `gemini-dispatch.yml` is retired (2026-11-12). The `@gemini` classification in `issue-comment-router.yml` remains a placeholder; current issue categorization uses the deterministic label floor and the specialized routes above.

## 6. Discovery and maintenance

Use these commands to inspect live GitHub state:

```bash
gh issue list --repo timerloggedout-spec/termux-monorepo --state open --limit 100
gh label list --repo timerloggedout-spec/termux-monorepo --limit 1000
gh workflow list --repo timerloggedout-spec/termux-monorepo
gh issue list --repo timerloggedout-spec/termux-monorepo --label research:provider --state all
```

When adding or changing an issue form, update this map in the same change with its labels, event subscription, job guard, parser, admission status, and output. When adding a label trigger, record the exact event surface and any permission/feature gate. Preserve the distinction between `opened`, `edited`, `reopened`, and `labeled`; each represents a separate event contract. `issue-intake-coverage.yml` runs the source-backed coverage audit on template, workflow, and map changes; it requires every form, template label, and labeled-event workflow to appear in this map.

## Source files

- Templates: `.github/ISSUE_TEMPLATE/*.yml` and `.github/ISSUE_TEMPLATE/roadmap-completion.md`
- Admission: `.github/workflows/swarm-admission.yml`, `scripts/ops/swarm_admission.py`, `ops/quota/dispatch-tiers.json`
- Intake: `.github/workflows/{apk-xref-intake,re-taxonomy-intake,research-intake,target-intake,project-task-dispatch,game-development-dispatch,egm-review-dispatch,delphi-gate,delphi-intake}.yml`
- Lifecycle: `.github/workflows/issue-lifecycle-triage.yml`, `scripts/issue_lifecycle/triage_labels.py`
- Label commands: `.github/workflows/{agent-jules-on-issues,agent-ecc-tools-ops,mesh-request,doe-live1-audit,build-arm-census}.yml`
- Observation: `.github/workflows/issue-observatory.yml`, `.github/workflows/issue-comment-router.yml`, `.github/workflows/sweep-accountability.yml`
- Roadmap completion: `.github/workflows/roadmap-completion.yml`, `roadmap-completions/scripts/verify-completion.py`, `roadmap-completions/config/verification-rules.yaml`
- Intake coverage guard: `.github/workflows/issue-intake-coverage.yml`, `scripts/ci/issue_intake_coverage.py`, `tests/test_issue_intake_coverage.py`
