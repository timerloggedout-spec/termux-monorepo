# Platform Coordination Matrix

| System | Authoritative role | Evidence key | Mutation policy |
|---|---|---|---|
| GitHub | refs, commits, PRs, reviews, checks, Actions | SHA + run/check ID | controlled writes; no force-push |
| Linear | execution/project coordination | issue ID + Git SHA | link, prioritize, track |
| Notion | cockpit/runbook/synthesis | page URL + SHA references | human-readable coordination |
| Hex | experiment analysis | experiment ID + source SHA | analyze/publish findings |
| Vercel | deployment/preview evidence | deployment ID + commit SHA | deployment only; never infer code correctness |

## Cross-system rule

Every observation that can affect a promotion decision must carry a source SHA or an explicit non-code provenance identifier. Provider timestamps are preserved in UTC. A provider outage, quota skip, or rate limit is classified separately from a repository failure.

## Attention routing

1. Git graph divergence → GitHub reconciliation lane.
2. Failed repository gate → GitHub validation lane.
3. Review/check staleness → GitHub evidence lane.
4. Work ownership/prioritization → Linear.
5. Human synthesis/navigation → Notion.
6. A/B/MVT statistical comparison → Hex.
7. Preview/deployment regression → Vercel.

Never use one platform's success as proof of another platform's success.
