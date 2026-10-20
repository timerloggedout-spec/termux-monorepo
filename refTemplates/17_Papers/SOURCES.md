# Papers / identity / scanner sources

**Intercom:** dense feedback is system-wide — `docs/ops/DENSE-FEEDBACK-INTERCOM.md` (not Paper2Agent-only).

## Source classes

| Class | Resolver | Notes |
|-------|----------|-------|
| arXiv | `https://arxiv.org/abs/<id>` | Preprints; prefer abs + pdf |
| GitXiv (deprecated) | original repo if recoverable | Prefer successors below |
| OpenAlex | via opencode-research-papers | Citation networks, no API key |
| Hugging Face Papers | `https://huggingface.co/papers` | Daily ML + GitHub impls |
| PapersFlow | papersflow.ai | Paper → GitHub code discovery |
| ORCID | `https://orcid.org/<id>` | Author identity |
| GRID.ac | GRID institution IDs | Org grounding |
| Google Scholar | scholar profiles | Citation checks |
| Nature / formal | DOI | High-weight claims |
| Patents | patent office / Google Patents | Implementation claims |
| Seeded | operator URL + note | First-class |

## GitXiv successors (active)

| Tool | URL | Role |
|------|-----|------|
| Hugging Face Papers | https://huggingface.co/papers | Trending ML + official code |
| PapersFlow | https://papersflow.ai | Auto extract GitHub from papers |
| papersflow-skills / MCP | https://github.com/papersflow-ai/papersflow-skills | Agent skills + DeepScan |
| alphaXiv OpenResearch | https://github.com/alphaXiv/OpenResearch | Local-first research agents |
| opencode-research-papers | https://github.com/saim-x/opencode-research-papers | arXiv + OpenAlex plugin (no keys) |
| ArXivAtlas | https://github.com/Jaluus/ArXivAtlas | Embedding cluster canvas |
| Connected Papers | connectedpapers.com | Citation graph from seed |
| Elicit / Consensus | elicit.com / consensus.app | Structured reviews / evidence |

## Local-first / Termux-friendly scanners

| Tool | Notes |
|------|-------|
| opencode-research-papers | Markdown out; strict anchor-concept mode |
| arxiv-dl / arxiv.py | Batch download + keyword queries |
| Docling | Scholarly PDF → structured MD/JSON |
| OpenResearch (`orx`) | Literature → hypothesis → experiment tree |

## Operator-seeded (2026-09-20)

| id | title / note | url | linked_slots | priority |
|----|--------------|-----|--------------|----------|
| **laya-convai** | Laya (ConvAI Innovations) | https://laya.convaiinnovations.com | 16_Org_Phased/laya | **HIGH** |
| glm-inference-infra | GLM dense feedback → intercom + Paper2Agent | https://z.ai/blog/glm-built-its-inference-infrastructure | DENSE-FEEDBACK-INTERCOM, Paper2Agent | HIGH |
| needle-3-cactus | Needle 3 on-device FM | https://cactuscompute.com/needle | 01_Agent_Runtime, 15_Research | normal |
| cactus-needle-github | cactus-compute/needle | https://github.com/cactus-compute/needle | 01_Agent_Runtime | normal |
| opencode-research-papers | arXiv + OpenAlex plugin | https://github.com/saim-x/opencode-research-papers | 17_Papers, scanners | normal |
| openresearch-alphaxiv | Research agents | https://github.com/alphaXiv/OpenResearch | 15_Research | normal |
| papersflow-code-discovery | Paper → GitHub | https://papersflow.ai | 17_Papers | normal |
| arxivatlas | Semantic arXiv canvas | https://github.com/Jaluus/ArXivAtlas | 17_Papers | normal |
| typesafe-system-one | System One + JEV waitlist | https://typesafe.ai/blog/introducing-system-one-models-and-jev | watchlist | watch |
| yt-hygMRgnDD7w | Operator research video | https://youtu.be/hygMRgnDD7w | seed | seed |

Scanners under `scripts/ci/refTemplates_*` — rate-limited, dual-gate, free-first.
