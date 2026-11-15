# BRR → QUE / QDesk integration

## Decision

Branch Reconciliation Registry (BRR) is an observer and intake producer inside the existing QDesk self-repair cycle. It does not own a second scheduler, queue, task ranker, claim engine, or promotion engine.

The existing \`.github/workflows/qdesk-self-repair.yml\` three-hour cycle is the sole recurring execution owner. It builds the complete BRR inventory, passes the JSON snapshot to QUE intake, and retains the report as a 90-day Actions artifact. The standalone BRR workflow is CI-only: it validates code on relevant pushes and pull requests, with no schedule or manual dispatch.

## Siglary DO Statements

### DO-01 — Observe all branches
**DO** enumerate every repository branch from the paginated GitHub branches API. **DO** fetch the corresponding remote refs and compare commit ancestry against the default branch. **DO** retain branch SHA, protection state, ahead/behind counts, linked PRs, PR base refs, and unresolved conditions. **DO NOT** infer completeness from a bounded search result or partial page.

Acceptance: inventory count equals the complete API result; every returned branch has a record or an explicit parse failure; schema is \`branch-reconciliation-registry/v1\`.

### DO-02 — Convert findings into QUE work
**DO** create/update idempotent \`que:self-repair\` issues for \`ahead-only\`, \`diverged\`, \`unresolved-local-ref\`, and \`unrelated-or-unavailable-history\`. **DO** include branch name, observed tip SHA, disposition, ahead/behind counts, linked PRs and declared base refs. **DO** use branch + tip SHA + disposition as the evidence identity. **DO NOT** create tickets for clean/behind-only branches unless a later policy explicitly adds a reason.

Acceptance: same-tip reruns update the same open issue; a changed tip creates a new evidence epoch; malformed schema fails closed.

### DO-03 — Reuse QUE task-plane machinery
**DO** pass the intake items through existing QUE ranking, auto-claim, lease/reclaim, escalation and Desk surfaces. **DO NOT** introduce a second queue, scheduler, claim system, or rank algorithm. A claim is assignment only, never merge authorization.

Acceptance: intake issues carry existing QUE labels and are visible to existing feed/claim consumers without changing their contracts.

### DO-04 — Preserve authority boundaries
**DO** retain QDesk/Desk review, independent DoE verification, exact-head CI, branch protection and owner gates. **DO NOT** merge, close, push, retarget, or delete branches from BRR or QUE intake. Unknown remains unresolved; behind-only does not mean disposable.

Acceptance: tests prove no branch mutation API is called; promotion remains a separately authorized operation.

### DO-05 — Operate without manual dispatch
**DO** run BRR as part of the existing QDesk scheduled cycle. **DO** keep a PR/push validation workflow for tests only. **DO NOT** add a second schedule or workflow_dispatch trigger for BRR.

Acceptance: only the existing QDesk cadence produces recurring inventory; CI validates changes without becoming another production poller.

### DO-06 — Retain evidence and recover safely
**DO** retain JSON and Markdown inventory artifacts for 90 days. **DO** expose per-cycle intake outcomes in the QDesk job summary. **DO** defer on API rate limits and retry on the next scheduled cycle. **DO NOT** call queued, running, skipped, cancelled, or failed runs successful.

Acceptance: artifact upload is required; missing inventory fails before issue filing; rate-limit states are explicit.

## Disposition → QUE mapping

| BRR state | QUE action |
|---|---|
| ahead-only | review unique commits |
| diverged | higher-priority reconciliation |
| unresolved-local-ref | evidence recovery; promotion blocked |
| unrelated-or-unavailable-history | ancestry recovery; promotion blocked |
| identical / behind-only | inventory only; never auto-archive/delete |

The existing per-cycle issue cap remains in force. The complete inventory is retained even when some candidate issues are deferred; the next scheduled cycle reconsiders them.

## Operational graph

\`\`\`text
QDesk scheduled cycle
  → BRR paginated census
  → Git ancestry classification
  → immutable inventory artifact
  → QUE idempotent issue intake
  → existing rank / claim / lease / escalation
  → Desk + QDesk + independent DoE
  → separate promotion decision
\`\`\`

## State discipline

A plan is not an implementation. A commit is not runtime evidence. A queued or running workflow is not success. A green CI run is not permission to promote. Missing evidence is unknown, not zero. Every operational state claim must cite the exact PR, SHA, and workflow run that proves it.
