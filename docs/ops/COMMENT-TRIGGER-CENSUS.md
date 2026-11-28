# Comment trigger census

Snapshot: `feat/trigger-workflow-registry-refresh`, 2026-11-27. Seventeen source-read workflows establish distinct comment selectors across slash commands, agent mentions, provider commands, and HTML markers.

| Workflow | Selector | Guards | Class |
|---|---|---|---|
| `sweep-accountability` | comment body starts with /sweep | workflow condition also permits non-comment event paths; command arm is the explicit issue-comment selector | slash-command |
| `build-dispatch` | comment body starts with @gemini-cli /build | author association OWNER/MEMBER/COLLABORATOR | mention-plus-command |
| `agent-jules-on-issues` | comment body starts with @jules or @Jules | non-PR issue; sender type User; author association OWNER/MEMBER/COLLABORATOR | mention |
| `agent-pr-jules-handoff` | comment body matches ^@jules or ^@Jules with whitespace or end boundary | user association OWNER/MEMBER/COLLABORATOR or allowed github-actions bot path; PR synchronize is a separate event arm | mention |
| `deepseek-ci` | comment body contains @deepcore, @deepCore, @deepseek, @deepseek-ci, deepseek, or DeepSeek | workflow also handles pull_request and workflow_dispatch; selector includes broad text matches | mention-or-keyword |
| `deepseek-termux-agent` | comment body contains @deepseek | issues.assigned, pull_request.assigned, and workflow_dispatch are separate event arms | mention |
| `agent-ecc-tools-ops` | comment starts /ecc-tools-ops or /ecc ops, or contains <!-- request-ecc-tools-ops --> | author association OWNER/MEMBER/COLLABORATOR; non-PR issue and PR lanes are distinct job conditions | slash-command-plus-marker |
| `ox-alpha-smoke` | comment body starts with /run-model followed by a space | comment must belong to a pull request; workflow_dispatch is a separate event arm | slash-command |
| `pr-evidence-evaluation` | comment body starts with /evaluate | comment must belong to a pull request; workflow also handles PR, review, review-comment and workflow_dispatch events | slash-command |
| `action-effectiveness-ledger` | comment body starts with /ledger | comment must belong to a pull request; workflow concurrency group includes event_name to isolate comment and PR runs | slash-command |
| `cellcog-review` | comment body contains @cellcog or @CellCog | comment must belong to a pull request; comment author must be non-bot | mention |
| `research-intake` | comment contains <!-- request-research --> | non-PR issue; workflow also accepts issues opened/reopened/edited | html-marker |
| `delphi-intake` | comment contains <!-- request-delphi-intake --> | workflow_dispatch is a separate entry arm | html-marker |
| `operator-wake` | comment contains <!-- request-operator-wake --> | workflow_dispatch is a separate entry arm | html-marker |
| `phantom-secrets-audit` | comment contains <!-- request-phantom-secrets-audit --> | workflow_dispatch and schedule are separate event arms | html-marker |
| `operator-variable-provision` | comment contains <!-- request-variable-provision --> | author association OWNER/MEMBER/COLLABORATOR; workflow_dispatch is a separate event arm | html-marker |
| `peer-review-orchestrator` | PR comment contains @coderabbitai, @qodo, devin review, or operator-action | comment must belong to a pull request; bot/receipt filters and authorized-association checks apply in the orchestration path | provider-command |

## Trigger semantics

- Slash commands are explicit comment prefixes such as `/sweep`, `/run-model`, `/evaluate`, and `/ledger`.
- Agent mentions use distinct boundary rules: Jules uses a starts-with or anchored regex; DeepSeek and CellCog use contains checks. Authorization and PR-vs-issue context vary by workflow.
- HTML markers are machine-readable comment payload selectors such as `<!-- request-research -->` and `<!-- request-delphi-intake -->`; each marker belongs to a specific intake route.
- Provider commands such as `@coderabbitai` and `@qodo` are consumed in the PR review orchestration path and are separate from human agent mentions.

## Coverage

This census is selected, not exhaustive. It records the workflow file SHA and line references for each selector. It describes configured source conditions, not actual invocation counts or runtime success. Several workflows have additional independent event arms; those are retained in the record guards and in the workflow event index.

Machine-readable records: `docs/ops/generated/comment-trigger-census.json`.
