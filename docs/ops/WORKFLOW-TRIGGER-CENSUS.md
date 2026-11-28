# Workflow trigger census — selected routes

Snapshot: `feat/trigger-workflow-registry-generator`, 2026-11-28. Scope: nine source-read workflows demonstrating issue admission, issue intake, workflow handoff, mentions, slash commands, manual dispatch, and typed repository events. This is a verified exemplar set, not the exhaustive 333-workflow directory inventory. The generated automation catalog contains 332 entries. `research-astute-private-repo-provisioner.yml` is present in the directory but absent from the catalog; `project-repository-visibility.yml` is catalogued with an authority mismatch.

| Workflow | Event(s) | Selector / gate | Authority |
|---|---|---|---|
| `swarm-admission` | `issues` [opened, reopened] | Template matching by declared labels or title prefix in scripts/ops/swarm_admission.py; gate: issue-dispatch/v1 template match + QUE tier → after → chain → flow projection | bounded-state-write |
| `project-task-dispatch` | `issues` [opened, reopened] | issue has project-task label OR title starts [task] OR body contains ### Task / spec; gate: intake parser; only valid parse proceeds to dispatch queue | bounded-state-write |
| `game-development-dispatch` | `workflow_run` [completed] | admission handoff artifact identifies game-development-task and decision admitted; gate: upstream conclusion success + handoff artifact validation + task parser | bounded-state-write |
| `agent-jules-on-issues` | `issues` [labeled]; `issue_comment` [created] | Label jules/Jules/JULES; or comment body starts @jules/@Jules from User with OWNER/MEMBER/COLLABORATOR association on non-PR issue; gate: label path has trusted-actor verification; mention path has trusted association and user/non-PR context | bounded-state-write |
| `build-dispatch` | `issue_comment` [created]; `workflow_dispatch` | manual dispatch OR comment starts @gemini-cli /build from OWNER/MEMBER/COLLABORATOR; gate: workflow job condition + route/arm validation | writer |
| `provider-command-dispatch` | `workflow_dispatch`; `repository_dispatch` [provider-command] | explicit provider-command event or operator-supplied manual inputs; gate: allowlisted provider/action, PR/head SHA and policy validations | bounded-state-write |
| `delphi-intake` | `issue_comment` [created]; `workflow_dispatch` | comment body contains <!-- request-delphi-intake --> OR manual dispatch; gate: intake job condition and form/input validation | bounded-state-write |
| `project-repository-visibility` | `push` (master, path-filtered) | Versioned owner request + authenticated owner/admin + repository identity checks | writer |
| `research-astute-private-repo-provisioner` | `push` (master, path-filtered) | Versioned private-repository request + authenticated owner + Research-Astute admin + target/allocation checks | writer |

## Source-level findings

- Jules supports two distinct entry arms: a trusted label event (`jules`, `Jules`, `JULES`) and a trusted-user comment beginning with `@jules` or `@Jules` on a non-PR issue. The workflow also has a non-executing receipt job for issue/comment events.
- `@gemini-cli /build` is a comment command on `issue_comment.created`; the same workflow exposes `workflow_dispatch` inputs for issue number, branch, build arm, and quota class.
- Delphi intake recognizes the exact HTML marker `<!-- request-delphi-intake -->` or manual dispatch with structured inputs.
- Provider command dispatch accepts manual input or `repository_dispatch` type `provider-command`; provider and action are bounded by the workflow's allowlist checks.
- Game-development dispatch is a downstream `workflow_run` consumer of successful `swarm-admission` runs and validates the one-run handoff artifact before queueing.
- Research Astute provisioning uses `gh api --method POST /orgs/$ORG_NAME/repos` to create an external private repository. Its declared `contents: read` permission is narrower than its effective external-token action; source-level authority is writer.

## Evidence and limits

Each record stores the source blob SHA. Event subscriptions and selectors above are extracted from workflow YAML/job conditions; runtime outcomes still require workflow-run evidence. At this 2026-11-28 census snapshot, the workflow directory contained 333 YAML files and `docs/ops/generated/automation-workflow-catalog.json` contained 332 records. `research-astute-private-repo-provisioner.yml` was uncatalogued. `project-repository-visibility.yml` is catalogued, with a separate catalog/source authority mismatch. This census records configured behavior, not proof that a route fired successfully.
