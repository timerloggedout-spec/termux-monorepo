# Proposal Process — ArchW1z

Structured lifecycle: **ingest → register → itemize → review → execute → close**.

**Also read:** `AGENTIC-PERMISSIONS.md` · `registry.yaml` · root `AGENTS.md` · `docs/CONSENSUS.md`

## Directory layout

```
docs/proposals/
  README.md
  PROCESS.md
  AGENTIC-PERMISSIONS.md
  registry.yaml
  _template/MANIFEST.md
  active/<id>/{MANIFEST.md,ITEMS.md,DEBATE.md?,source.md?}
  closed/<id>/
  legacy/
```

## States

| State | Meaning |
|-------|--------|
| draft | Author still writing |
| posted | In registry.yaml |
| in_review | ≥1 reviewer assigned |
| accepted | Execution may start |
| executing | Items being implemented |
| blocked | Waiting on human-only step |
| closed | Terminal under closed/ |

## Consensus

Item-scoped. See `docs/CONSENSUS.md` tiers. P0 needs second mind or Operator. Unposted chat is not consensus.

## Closing

All ITEMS terminal + Review log outcome + move active/ → closed/ + registry update.

## Gate coupling

1. repo-gate green
2. termux-smoke green
3. Item IDs cited
4. No unresolved critical PR threads

## Agent entrypoint

```text
1. Read AGENTS.md then registry.yaml
2. Pick highest-priority accepted/executing todo item
3. Branch off master-staging
4. PR → master-staging with Implements: <ITEM-ID>
5. Update ITEMS.md + registry when possible
6. Never close P0 security without Operator evidence
```

## Automation

| Script | Role |
|--------|------|
| `scripts/proposals/validate_registry.py` | registry.yaml ↔ active/ consistency |
| `scripts/proposals/record_vote.py` | append structured VOTE to DEBATE.md |
| `scripts/proposals/promote_proposal.py` | status transitions + optional close move |
| `.github/workflows/proposal-lifecycle.yml` | CI validate + PR checklist comment |

Large external proposals may live on a **docs/** branch with a **pointer** on master
(see `corrected_cloud_offload_evaluation.md` → `active/kimi-cloud-offload/`).
