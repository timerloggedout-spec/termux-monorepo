# Papers / identity / scanner sources

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

| id | title / note | url | linked_slots |
|----|--------------|-----|--------------|
| needle-3-cactus | Needle 3 — 8–29 MB foundation model; tool calls + extraction on-device | https://cactuscompute.com/needle | 01_Agent_Runtime, 15_Research |
| cactus-needle-github | cactus-compute/needle source | https://github.com/cactus-compute/needle | 01_Agent_Runtime |
| glm-inference-infra | GLM Paper2Agent template: dense feedback, Infra Agent, RSI path | https://z.ai/blog/glm-built-its-inference-infrastructure | 15_Research, Paper2Agent |
| opencode-research-papers | arXiv + OpenAlex OpenCode plugin | https://github.com/saim-x/opencode-research-papers | 17_Papers, scanners |
| openresearch-alphaxiv | Turn coding agents into research agents | https://github.com/alphaXiv/OpenResearch | 15_Research, jogyo |
| papersflow-code-discovery | Paper → GitHub implementation finder | https://papersflow.ai | 17_Papers |
| arxivatlas | Semantic arXiv canvas | https://github.com/Jaluus/ArXivAtlas | 17_Papers |
| laya-convai | Laya (ConvAI Innovations) — watch surface | https://laya.convaiinnovations.com | watchlist |
| typesafe-system-one | System One Models + JEV waitlist | https://typesafe.ai/blog/introducing-system-one-models-and-jev | watchlist |
| yt-hygMRgnDD7w | Operator research video seed | https://youtu.be/hygMRgnDD7w | seed |

Scanners implement under `scripts/ci/refTemplates_*` per CONTINUOUS-EVAL — rate-limited, dual-gate, free-first.
