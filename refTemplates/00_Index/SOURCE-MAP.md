# SOURCE-MAP — refTemplates

## 01_Agent_Runtime (metadata-first)

| Slot | Preferred SOURCE | Disposition |
|---|---|---|
| vercel-agent-toolchain | https://github.com/vercel-labs/agent-browser · https://github.com/vercel-labs/skills · https://github.com/vercel-labs/agent-skills · https://github.com/vercel-labs/agent-desktop · https://github.com/vercel-labs/portless · https://github.com/cloudflare/kitesurf | Metadata-only; see `refTemplates/01_Agent_Runtime/vercel-agent-toolchain/integration.json` and `docs/ops/C12-AGENT-BROWSER-INTEGRATION.md` |

## 15_Research_Repo_Templates (tier A)

| Slot | Preferred SOURCE |
|------|------------------|
| jogyo-research-lab | https://github.com/Yeachan-Heo/My-Jogyo |
| docxology-template | https://github.com/docxology/template |
| yy-project-template | https://github.com/yy/project-template |
| buoyancy99-research-template | https://github.com/buoyancy99/research-template |
| yp-edu-research-project-template | https://github.com/yp-edu/research-project-template |
| seunghyukoh-research-template | https://github.com/seunghyukoh/research-template |
| irudik-repo-template | https://github.com/irudik/repo-template |
| jdingel-projecttemplate | https://github.com/jdingel/projecttemplate |
| 3rdCore-Research_Project_Template | https://github.com/3rdCore/Research_Project_Template |
| dicklesworthstone-agentic-flywheel | https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup |

The Flywheel slot is metadata-first and tracks a composable stack; it is not a request to run the upstream installer. See docs/ops/DICKLESWORTHSTONE-FLYWHEEL-INTEGRATION.md.

## Candidates (tier B — re-score on cadence)

From 489+ forks + starred set (examples):

- timerloggedout-spec/pyrite
- timerloggedout-spec/CodeWiki_fork
- timerloggedout-spec/alphadesk-terminal
- timerloggedout-spec/MOBIUS-Searcher
- Starred agent/research runtimes (hermes-agent, orca, openclaw, pi, …) — pattern harvest vs full slot

Policy: `docs/ops/RESEARCH-INTEGRATION-LANE.md`

## smods (live gitlinks)

See root `.gitmodules` for live gitlinks and `refTemplates/smods/INTEGRATIONS.json` for fork-required/deferred/pinned dispositions. A ledger entry alone is not a gitlink.

Live gitlinks:

AuditEngine_fork, batteries_fork, content-agent-routing-promptbase_fork, cost-of-remembering_fork, icm-architect_fork, icm-cctv_fork, interpretable-context-methodology_fork, mcp-android-ssh_fork, term_mcp_deepseek_fork, termux-mcp-server_fork, lego_fork

Pins intentional; no auto-advance without dual-gate green. Flywheel components remain metadata-only until a real customized fork and compatibility evidence exist.
