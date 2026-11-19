# Skills discovery map (2026-11-19)

Purpose: link exported skills to the repo artifacts they serve, so discovery starts from the repo.

## Verified repo anchors

| Anchor | Path | Role |
|---|---|---|
| BRR intake | scripts/que/branch_reconciliation_intake.py | Projects BRR dispositions into QUE intake |
| BRR proposal | docs/proposals/active/qdesk-self-repair/PROPOSAL.md | Defines BRR as observer inside QDesk cycle |
| BRR items | docs/proposals/active/qdesk-self-repair/ITEMS.md | QSR-BRR-001 and QSR-BRR-002 |
| BRR integration doc | docs/ops/BRR-QUE-QDESK-INTEGRATION.md | Decision record |
| BRR backlog | ops/compute/BACKLOG.md | BRR v2 registry: 4,103 branches |
| Pointer index | archwiz/POINTER_INDEX.md | Pointer table: cockpit, tool index |
| Tool index | archwiz/TOOL_INDEX.md | pointer_index.py builds hash to location map |
| Index alignment | scripts/linguist/index_alignment.py | Checks pointer index targets |
| Pointer fabric | docs/ops/CONTEXT-RELATIONSHIP-POINTER-FABRIC.md | Forward and reverse pointer resolution |

## Skill to anchor map

| Skill family | Path (archive) | Anchor it serves |
|---|---|---|
| Branch triage | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:triage/SKILL.md | BRR dispositions |
| Workflow security | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:zizmor/SKILL.md | .github/workflows |
| Write gates | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:ai-governance/SKILL.md | Protected paths |
| Secret scan | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:kingfisher/SKILL.md | Credential exposure |
| CI cost | plugins/b43e1b4c-9b74-4a04-a70f-676ba5b7eb40:ci-optimizer/SKILL.md | Workflow runs |
| Parallel lanes | plugins/681a497f-1fa2-48e6-96a6-3b55ac04e695:dispatching-parallel-agents/SKILL.md | QUE lanes |
| Session handoff | plugins/11922719-c2b0-4b58-9751-2dd37b3f91f9:handoff/SKILL.md | Ledger and cockpit |

Full routing: docs/ops/skills/QDESK-WORKFLOWS-SKILL-ROUTING-2026-11-18.md
Full inventory: docs/ops/skills/SKILLS-INVENTORY-2026-11-18.md

## Gap

Skills from the eb9bad6a family are absent from the mount, so this map cannot link them. Supply source to close the gap.
