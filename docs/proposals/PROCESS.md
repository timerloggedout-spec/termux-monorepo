# Proposal Process — ArchW1z

Structured lifecycle: **ingest → register → itemize → review → execute → close**.

**Also read:** `AGENTIC-PERMISSIONS.md` · `registry.yaml` · root `CLAUDE.md` · `docs/CONSENSUS.md`

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

Item-scoped. See `docs/CONSENSUS.md` tiers. P0 needs a second mind or Operator. Record consensus in the proposal; chat alone is not the durable record.

## Closing

All ITEMS terminal + Review log outcome + move active/ → closed/ + registry update.

## Gate coupling

1. `repo_gate.py` green
2. `termux_smoke.py` green
3. Item IDs cited
4. No unresolved critical PR threads

## Agent entrypoint

```text
1. Read CLAUDE.md then registry.yaml
2. Pick the highest-priority accepted/executing todo item
3. Branch from the active integration base defined by CLAUDE.md
4. Open a PR with Implements: <ITEM-ID>
5. Update ITEMS.md + registry when possible
6. Keep human-only security decisions with the Operator
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
