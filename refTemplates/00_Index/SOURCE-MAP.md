# SOURCE-MAP — refTemplates

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

## 18_Vector_Databases (metadata-first)

| Slot | Preferred SOURCE | Role |
|------|------------------|------|
| pinecone | https://docs.pinecone.io/ | Managed vector database; existing repo REST client and knowledge-sync consumer |
| pg_pinecone | https://github.com/pinecone-io/pg_pinecone | Apache-2.0 PostgreSQL extension; native and Pinecone-remote engine comparison candidate |
| pgvector | https://github.com/pgvector/pgvector | PostgreSQL vector baseline; source pin recorded in metadata |
| pinecone-mcp | https://github.com/pinecone-io/pinecone-mcp | Official Apache-2.0 developer MCP reference; optional interface, separate from the existing runtime adapter |

The managed Pinecone integration already lives in scripts/pinecone/ and .github/workflows/pinecone-knowledge.yml. The DoE compares retrieval engines over a frozen corpus and shared vectors; it keeps embedding-path comparisons separate. See experiments/doe/pinecone-vector-store/DESIGN.json.

## Candidates (tier B — re-score on cadence)

From 489+ forks + starred set (examples):

- timerloggedout-spec/pyrite
- timerloggedout-spec/CodeWiki_fork
- timerloggedout-spec/alphadesk-terminal
- timerloggedout-spec/MOBIUS-Searcher
- Starred agent/research runtimes (hermes-agent, orca, openclaw, pi, …) — pattern harvest vs full slot

Policy: `docs/ops/RESEARCH-INTEGRATION-LANE.md`

## smods (live gitlinks)

See root `.gitmodules`:

AuditEngine_fork, batteries_fork, content-agent-routing-promptbase_fork, cost-of-remembering_fork, icm-architect_fork, icm-cctv_fork, interpretable-context-methodology_fork, mcp-android-ssh_fork, term_mcp_deepseek_fork, termux-mcp-server_fork, lego_fork, Wingman_fork, GPTmetrics_fork, Reddit-Evidence-Usage-and-Stance-Analysis-Elon-Musk-Discussion_fork

Pins advance through dual-gate review. Pinecone pg_pinecone is catalogued as a pin candidate; custom fork creation remains pending. Add its gitlink after the custom fork, immutable reviewed pin, compatibility evidence, and passing gates are complete.
