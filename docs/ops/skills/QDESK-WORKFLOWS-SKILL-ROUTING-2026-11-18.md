# QDesk and WorkFlows: skill routing (2026-11-18)

## Decisions (/confirm, 2026-11-18)

- ✓ Placement: `vendor/skills-mirror/` (Siglary §6.5 E2 scope). Rejected: `skills/` (Siglary §1 binds `skills/**` at HARD).
- ⏸ Notation template (8 glyphs outside the issued set: ⨯ ⌘ ⤵ § ⊩ ⟁ ∎ ⋈ ↻ ⧖ ⌖): hold until Linguist ratifies. Siglary §6.1 HARD check fails until then.

## Export integrity

- Archive: `skills-SKILL-md-all.tar.gz`, 4,884,208 bytes, sha256 prefix `b2bfb4b5839bee93`.
- Parts: `skills-part-00.tgzpart` to `skills-part-04.tgzpart` (four parts at 1,024,000 bytes, one at 788,208). Checksums: `docs/ops/skills/archive-parts-SHA256SUMS.txt`.
- Rejoin: `cat skills-part-*.tgzpart > skills-SKILL-md-all.tar.gz`, then check the sha256 prefix.

## Coverage gap (stated)

- Mount holds 1,299 SKILL.md across 1,216 plugin directories.
- The skill index lists these skills absent from the mount: `ship-pr`, `orchestrate`, `dependency-vetting`, `pipelinemd`, `agent-army`, `review-pr`, `remediate-findings`, `review-change`, `publish-change`, `deliver-change`. Family `eb9bad6a-*` is absent in full.
- Action: supply the source for those families, then re-export.

## Route table: QDesk and WorkFlows need to skill

| Need | Skill | Archive path |
|---|---|---|
| Workflow authoring | github-actions | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:github-actions/SKILL.md |
| Composite actions | composite-actions | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:composite-actions/SKILL.md |
| Workflow security audit | zizmor | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:zizmor/SKILL.md |
| Write gates on protected paths | ai-governance | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:ai-governance/SKILL.md |
| PR comment triage | triage | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:triage/SKILL.md |
| CI speed and cost | ci-optimizer | plugins/b43e1b4c-9b74-4a04-a70f-676ba5b7eb40:ci-optimizer/SKILL.md |
| CI timings | ci-timings | plugins/b43e1b4c-9b74-4a04-a70f-676ba5b7eb40:ci-timings/SKILL.md |
| CI check | ci-check | plugins/b43e1b4c-9b74-4a04-a70f-676ba5b7eb40:ci-check/SKILL.md |
| Parallel lanes | dispatching-parallel-agents | plugins/681a497f-1fa2-48e6-96a6-3b55ac04e695:dispatching-parallel-agents/SKILL.md |
| Orchestrated fan-out | orchestration | plugins/11922719-c2b0-4b58-9751-2dd37b3f91f9:orchestration/SKILL.md |
| Dispatch | dispatch | plugins/5990c451-fd03-43c8-a487-a4397ebcbc6e:dispatch/SKILL.md |
| Secret leak scan | kingfisher | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:kingfisher/SKILL.md |
| Failure debugging | debug | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:debug/SKILL.md |
| Session handoff | handoff | plugins/11922719-c2b0-4b58-9751-2dd37b3f91f9:handoff/SKILL.md |
| Self-improvement | self-improve | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:self-improve/SKILL.md |
| Token cost | token-optimizer | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:token-optimizer/SKILL.md |
| MCP servers | mcp | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:mcp/SKILL.md |
| Agent setup | setup-agents | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:setup-agents/SKILL.md |
| Platform umbrella | platform-skills | plugins/a41aebb0-6257-4df3-9e6b-0e0e1e4409e2:platform-skills/SKILL.md |

## Connector write paths (GitHub)

- `GitHub_CoPilot_MCP` write tools (`push_files`, `create_or_update_file`, `delete_file`) are listed in the schema. The API returns 403 on tree and branch writes. Read paths work.
- `Composio` GitHub: the working write path, active under timerloggedout-spec.
- `upstash box_git`: clone, commit, push, create_pr through the GitHub installation. Needs a box. Read-only OAuth gets 403 on writes.
