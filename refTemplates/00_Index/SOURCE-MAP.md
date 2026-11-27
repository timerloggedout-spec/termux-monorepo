# SOURCE-MAP — refTemplates

## 05_Safety_Observability

| Slot | Preferred SOURCE | Role |
|---|---|---|
| opentelemetry-collector | https://github.com/open-telemetry/opentelemetry-collector | Neutral telemetry receive/process/export |
| signoz | https://github.com/SigNoz/signoz | OTel-native operational observability |
| hyperdx-clickstack | https://github.com/hyperdxio/hyperdx | Search-first logs/traces/metrics/session replay |
| openobserve | https://github.com/openobserve/openobserve | Unified logs/metrics/traces |
| parca | https://github.com/parca-dev/parca | Continuous profiling |
| pyroscope | https://github.com/grafana/pyroscope | Continuous profiling |
| coralogix-comparator | https://coralogix.com/docs/ | Commercial capability comparator |

## 11_Evaluation_Quality

| Slot | Preferred SOURCE | Role |
|---|---|---|
| langfuse | https://github.com/langfuse/langfuse | LLM traces, datasets, experiments, scores |
| phoenix | https://github.com/Arize-ai/phoenix | LLM traces, evaluations, datasets, experiments |

## 15_Research_Repo_Templates (tier A — 12)

| Slot | Preferred SOURCE |
|---|---|
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
| opencode-research-papers | https://github.com/saim-x/opencode-research-papers |
| cactus-needle | https://github.com/cactus-compute/needle |

The Flywheel slot is metadata-first and tracks a composable stack; it is not a request to run the upstream installer. See docs/ops/DICKLESWORTHSTONE-FLYWHEEL-INTEGRATION.md.

## Candidates (tier B — re-score on cadence)

From the existing 489+ forks + starred set (examples):
- timerloggedout-spec/pyrite
- timerloggedout-spec/CodeWiki_fork
- timerloggedout-spec/alphadesk-terminal
- timerloggedout-spec/MOBIUS-Searcher
- Starred agent/research runtimes (hermes-agent, orca, openclaw, pi, …) — pattern harvest vs full slot

Policy: docs/ops/RESEARCH-INTEGRATION-LANE.md.

## smods (live gitlinks + cited inspiration register)

See root .gitmodules for live custom-adapted gitlinks: AuditEngine_fork, batteries_fork, content-agent-routing-promptbase_fork, cost-of-remembering_fork, icm-architect_fork, icm-cctv_fork, interpretable-context-methodology_fork, mcp-android-ssh_fork, term_mcp_deepseek_fork, termux-mcp-server_fork, lego_fork, GPTmetrics_fork, Wingman_fork, and other registered pins.

Cited inspiration sources are catalogued separately in smods/INSPIRATION-SOURCES.md. Notary, ShipProof, and the unresolved Transcend showcase candidate are metadata-only citations, not gitlinks or runtime dependencies.

Promote live pins after a real customized fork, immutable reviewed pin, compatibility evidence, and passing gates.

## 10_Infrastructure

| Slot | Preferred SOURCE | Disposition |
|---|---|---|
| osx-forge | https://github.com/credkellar/OSx | Pattern candidate; Docker Hub overview reviewed, upstream source inspection pending |

## Registry semantics

- Entries are source references and comparison targets.
- Registration creates no clone, dependency, deployment, or promotion.
- Each candidate directory carries README.md and SOURCE.txt.
- License labels remain provisional until verified at an immutable revision.
