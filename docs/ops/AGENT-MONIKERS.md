# Agent Monikers (SSOT)

Creative **display** call-signs for high-performance agent orchestration.

**Critical:** Do **not** `@`-mention monikers that collide with real GitHub usernames.
Use backticks or plain text for display. Live triggers remain the original handles
(plus approved aliases registered in the matching workflow).

| Role | Display moniker | Live trigger (callable) | Notes |
|------|-----------------|-------------------------|-------|
| Jules (implementation) | `heyVern` | `@jules` | App only reacts to `@jules` |
| Gemini CLI (on-demand) | `sparkFlux` | `@gemini-cli` | Dispatch also accepts case-insensitive `@sparkFlux` as alias |
| DeepSeek CI (review/invoke) | `deepCore` | `@deepseek` / `@deepseek-ci` | Workflow also accepts case-insensitive `@deepCore`; labels `deepseek-ci`, `deepseek`, `deepCore` |
| CodeRabbit (review) | `codeHound` | `@coderabbitai` | Reviewer identity unchanged |
| Devin (review/fix) | `devinForge` | Devin app | |
| Continuous-ops sweep | `opsSweep` | (GHA) | Marker: `<!-- continuous-agent-ops -->` |
| OPERATOR / Grok | `archW1z` | human OWNER | Signing: `Signed-off-by: Grok (OPERATOR)` |
| Leet-Seek Admin / Full-scope Operator | `l337S33k` | (human / future profile role) | **Full admin across all repositories.** Parity with (and intended ≥) current OPERATOR/`archW1z`. Full-scope PAT + org/repo admin. Profile roles will be created under this moniker. Display only — do **not** `@`-mention. |
| Peer orchestrator | `peerGate` | (GHA) | |\n| Gemini / Gemini CLI contributor lane | `geminiMesh` | non-callable display | Provider/agent ecosystem identity; live trigger remains `@gemini-cli` where supported |\n| OpenRouter contributor lane | `routeMesh` | non-callable display | Provider/catalog/evaluation contributor; never a GitHub actor identity |\n| FELO contributor lane | `feloForge` | non-callable display | Provider/research/inference contributor; callable only through configured adapters |\n| Hugging Face contributor lane | `hfFoundry` | non-callable display | Hub/model/dataset/evaluation contributor; callable only through configured adapters |\n| Contributor-role coordinator | `roleMesh` | non-callable display | Cross-provider role/provenance coordination; no provider identity implied |

## Contributor lanes and role expansion\n\nContributor monikers are **display identities**, not GitHub usernames and not proof of authorship. A contributor lane may represent a provider, agent ecosystem, model family, execution adapter, or research/evaluation surface.\n\n| Contributor | Primary roles | Identity boundary |\n|---|---|---|\n| Gemini / Gemini CLI | review, triage, implementation, research, evaluation | provider/agent lane; GitHub actor remains separate |\n| OpenRouter | routing, catalog, inference, evaluation, benchmark | provider/catalog lane; model identity is separate |\n| FELO | research, inference, benchmark, evaluation, adapter | provider lane; account identity is separate |\n| Hugging Face | model, dataset, benchmark, evaluation, inference, research | Hub ecosystem lane; repo/model identity is separate |\n\nRole vocabulary is extensible: `research`, `evaluation`, `benchmark`, `inference`, `routing`, `catalog`, `dataset`, `adapter`, `review`, `triage`, `implementation`, `integration`, `documentation`, `evidence`, `orchestration`.\n\nAttribution MUST preserve provider/model/adapter/role plus workflow/job/step, event, PR/issue, SHA, and confidence. Incorporation of output is not provider authorship.\n\n## Rules

1. Automated comments: **display** moniker in backticks; **ping** only the live trigger (`@jules`, `@gemini-cli`, `@deepseek` / `@deepseek-ci`).
2. Workflows matching a live trigger **must** also accept the display moniker case-insensitively where registered above.
3. Never put secrets or Class 3/4 material in moniker docs.
4. If a moniker string is later registered as a GH username we do not control, keep it non-@ only.

## High-performance intent

Monikers reduce ambiguous role ownership under load without notifying strangers.
