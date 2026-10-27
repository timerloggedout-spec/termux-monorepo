# ITEMS — system-one-classifier-census

Every row of the source census (CENSUS.md) is a tracked item below.
Census rows start at `referenced` (directory-level evidence); a row's
state changes only on firsthand verification (SC-006).

## Workstreams

| ID | Item | State | Evidence / exit condition |
|---|---|---|---|
| SC-001 | Register this census as a proposal (this package) | executing | exit: registry entry + package merged; validator green |
| SC-002 | W1: fold census entries into the Tier-1 classifier map + provider catalogs with layer (model/adapter/runtime) and source URL per entry | proposed | exit: catalog/map diff merged; no double-count across layers |
| SC-003 | W2: evaluate self-hostable namesakes (Kev, Laya, Lev, Tev1, Strands Decider 2B, Nimble) as observatory trial candidates where a free route exists | proposed | exit: trial records via classifier-trial-dispatch, or a recorded no-free-route finding per candidate |
| SC-004 | W2: hosted/paid entries (Jev/TypeSafe et al.) remain referenced until the owner allows a paid route | proposed | exit: owner ruling recorded; no paid call before it |
| SC-005 | W3: track adapters/runtimes/directories as infrastructure options (Ollaya, simple-jev, laya.cpp, sys1, classifier.dev) | proposed | exit: options recorded in the Tier-1 map with layer tags |
| SC-006 | Verify directory-level entries firsthand before any state promotion beyond `referenced` | proposed | exit: per-entry firsthand check recorded in ITEMS.md |

## S1 — Namesakes (the fleet's observatory names)

| ID | Item | State | Source |
|---|---|---|---|
| S1-01 | Jev — TypeSafe AI — Hosted native typed decision model (Choice/Score/Noul); OpenRouter lists 1.13/1.14 | referenced | https://typesafe.ai/blog/introducing-system-one-models-and-jev |
| S1-02 | Kev — Jared Palmer — Open Jev-like family on Qwen (0.8B/4B/9B/27B); self-hosted, TypeSafe-compatible serving | referenced | https://github.com/jaredpalmer/kev |
| S1-03 | Laya — ConvAI Innovations — Non-autoregressive encoder decision family; English + multilingual checkpoints; open weights | referenced | https://github.com/NandhaKishorM/laya |
| S1-04 | Mev (recruiting) — Zhilin Wang — ~0.4B bidirectional encoder + decision head, fine-tuned from Laya for job-candidate matching | referenced | https://x.com/i/article/2101962974898397246 |
| S1-05 | mev — Mellow AI — Qwen3.5-4B LoRA selecting among 2-24 options; Apache-2.0; standard next-token head | referenced | https://huggingface.co/stay-mellow-ai/mev |

## S2 — Commercial, company, and laboratory families

| ID | Item | State | Source |
|---|---|---|---|
| S2-01 | Clef — Cloudflare — Decision family (Clef, Flash, omni); open-weight + hosted via Workers AI | referenced | https://www.forbes.com/sites/ronschmelzer/2026/10/12/decisions-decisions-a-guide-to-the-new-wave-of-ai-decision-models-besides-jev/ |
| S2-02 | pplx-decider — Perplexity — Multimodal decision family; 27B + Flash; v1.1/v1.2; open weights + hosted | referenced | https://openrouter.ai/rankings/decisions |
| S2-03 | d1 — Liquid AI — Hosted d1/d1-ultra; open d1-3B, d1-omni-600M | referenced | https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/ |
| S2-04 | GPT-6 Luna Decisions — OpenAI — Typed predicates/choices/scores over text+images; hosted Decisions API | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-05 | Microsoft-Decision-1 — Microsoft — Classification, agent routing, verification, workflow decisions; Foundry + OpenRouter | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-06 | Decider 1 / sd-1 — meraGPT — Hosted Choice/Score/Noul; closed weights; TypeSafe-compatible endpoint | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-07 | Trio-Spark — MachineFi — Decisions over text, images, sampled video frames; hosted, closed | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-08 | Solar Decide — Upstage — Long-context classification/scoring/routing; hosted beta, 512K context reported | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-09 | Mercury Decide — Inception — Structured choices/scores/yes-no; hosted; free rate-limited OpenRouter route reported | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-10 | Drex — Nace.AI — Enterprise decision family; OpenRouter v1.5/v2.0 | referenced | https://openrouter.ai/rankings/decisions |
| S2-11 | Span-01 — Respan — Behavior detection in AI traces (present/absent/not observable); specialized | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-12 | Tazo — Tazo Labs — Audio-native decisions for live voice agents; API by request | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-13 | djev — Maisa — Hosted typed decisions over text+images; invite/recovery-key access | referenced | https://api.djev.dev |
| S2-14 | Tev1 — Together AI — Experimental Qwen 4B/0.8B decision fine-tunes + published training recipe | referenced | https://github.com/togethercomputer/tev1 |
| S2-15 | Strands Decider 2B — AWS Strands Labs — Qwen-based decision model, pointer head + LoRA; open weights/data/scripts | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-16 | Nimble — Bespoke Labs — Qwen3.5-9B LoRA on contrastively curated data; open model + recipe | referenced | https://github.com/bespokelabsai/nimble |
| S2-17 | GLiNER2.5-Decide — Fastino — Encoder caller-defined classification/routing/scoring; Apache-2.0; CPU/GPU | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-18 | Standard One — Standard Thinking — 3B/8B text+image decision models; open + hosted; GGUF builds reported | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-19 | StartLux-Decision — StartLux — Dense + MoE typed decision models with image support; CC BY-NC weights | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-20 | Decision 2.0 — vLLM Semantic Router — Decision models 0.6B-27B; multiple questions per forward pass; Apache-2.0 | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-21 | Intern-Decision — InternLM — Multimodal 0.8B/2B/4B decision models with calibration tooling | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-22 | Security-One 27B — Superagent — Security triage: prompt injection, tool calls, code changes, alerts; Apache-2.0 | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-23 | Jeeves — PostHog — 9B Jev-like; reasoning training + pointer head + diffusion drafter | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-24 | Phocinae-Largha-150M — Phocinae — Small EN/ZH typed decision encoder with confidence gating; Apache-2.0 | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-25 | VideoJev — VideoJev project — Video grounding + multiple-choice QA, shared video context; 4B + 35B-A3B | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-26 | OpenThai-SystemOne — iApp/OpenThai — Thai/English 0.8B typed decision model; Apache-2.0; pip + Ollama | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S2-27 | Dwight 4B — Zime AI — Decision model for EN B2B sales-call transcripts; Apache-2.0; specialized | referenced | https://github.com/AnotiaWang/awesome-decision-models |

## S3 — Independent, academic, and community models

| ID | Item | State | Source |
|---|---|---|---|
| S3-01 | CLM — Contrastive-LM — System One models trained with a contrastive state-action objective | referenced | https://github.com/Contrastive-LM/CLM |
| S3-02 | Lev — Interfaze — Qwen3.5-4B LoRA with zero-output-token decisions; compatible server | referenced | https://huggingface.co/interfaze-ai/lev |
| S3-03 | Von — wfzyx — Small ModernBERT non-autoregressive decision model; repo archived in index | referenced | https://github.com/wfzyx/von |
| S3-04 | NanoJev — TianyuCodings — 0.6B parallel decision model; game demos + training pipeline | referenced | https://github.com/TianyuCodings/NanoJev |
| S3-05 | jevlike — vinnylarouge — One-pass context+options scorer; explicitly not TypeSafe's architecture | referenced | https://github.com/vinnylarouge/jevlike |
| S3-06 | decider family — Mapika — Qwen/Gemma family, multiple sizes + vision variant; compatible endpoint | referenced | https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/ |
| S3-07 | RSI-Jev — RSI-Jev project — Recursively developed decision models; selectable effort; vision variants | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-08 | jev-style — jev-style project — Local 0.8B decision model; PyTorch/MLX; compatible + MCP servers, guard hook | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-09 | PlayJev — PlayJev project — Small vision decision model for browser games; weights + browser demo | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-10 | OneJev — OmniJev team — Multimodal typed decision family 0.8B-27B; open weights reported | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-11 | jevos — feder-cr — Small CPU MiniCPM-derived model; directory documents Noul-only serving | referenced | https://github.com/feder-cr/jev |
| S3-12 | WebJev — WebJev project — Browser-action and target selection model; Apache-2.0 weights/data/recipe | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-13 | Vev — Vev project — Vision-enabled Qwen 4B/9B decision models; noncommercial weights | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-14 | JEV-27B / JEV-9B — AutoTrust — Distilled from Jev; combined decision + generation serving; Apache-2.0 reported | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-15 | Winnow — Winnow project — Gemma-based 12B/E4B typed decision models; llama.cpp serving | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-16 | JevK5 — allebee — Qwen-based 2B/4B/9B family; Apache-2.0; CUDA + GGUF | referenced | https://github.com/allebee/jevk5 |
| S3-17 | JevAlt (Deem/Karar/Wahler) — Mert Kaya — English/Turkish/German 4B decision models; GGUF + local serving | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-18 | reflex — kshetrajna12 — Small decision model on a frozen Qwen backbone; local server; WebGPU build | referenced | https://github.com/kshetrajna12/reflex |
| S3-19 | imajev — imajev project — Photo comparison / record-checking decisions incl. unknown option; MLX + PyTorch | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-20 | NeoHorse-Jev-4B — TokenRhythm — Text/single-image decision model, prefill-only inference; Apache-2.0 | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-21 | WaterSheep — WaterSheep project — Text decisions incl. Choice/Score/Noul/multilabel; Apache-2.0 | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-22 | Wald-4B — Wald project — Fully trained Qwen decoder; optional thinking; calibrated option probabilities | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-23 | Valen — Valen-Team — Multimodal 0.8B/2B/4B System One models; code/data/demo; Apache-2.0 | referenced | https://github.com/Valen-Team/Valen |
| S3-24 | OpenJev (weight project) — Trained single-pass decision model with calibration + serving; CC BY-NC weights | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S3-25 | Open-Jev — Zefan Cai — Trained decision-head adapters 2B/9B/27B; check code/weight licenses separately | referenced | https://github.com/Zefan-Cai/Open-Jev |
| S3-26 | InnerJev — Fudan/Tongji/KCL — 4B/27B single-pass decision models distilled from reasoning; academic | referenced | https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/ |
| S3-27 | Rizzo Flow — Rizzo AI Academy — Small family with native + Jev-compatible endpoints; Apache-2.0 reported | referenced | https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/ |
| S3-28 | AgentJev-0.6B — malevrigns — Small candidate-head model for agent-state decisions | referenced | https://github.com/malevrigns/agent-jev |
| S3-29 | openJev-verdict 2.0 — Heman10x-NGU — ~151M non-autoregressive calibrated decision engine; experimental | referenced | https://github.com/Heman10x-NGU/openJev-verdict-2.0 |

## S4 — Decision adapters and inference techniques (not new models)

| ID | Item | State | Source |
|---|---|---|---|
| S4-01 | SemIf (formerly OpenJev) — Typed decisions from option logits of existing open models; inference technique | referenced | https://github.com/TheoLeeCJ/SemIf-OpenJev |
| S4-02 | AnyJev / Tacit — Nokia Applied Research — Training-free decision method + self-distilled Tacit models | referenced | https://github.com/nokia-applied-research/AnyJev |
| S4-03 | LitJev — Decision serving from existing Qwen models without training; adapter | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S4-04 | TetraJev — Combines multiple frozen-model decision readings + confidence gates; pipeline | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S4-05 | simple-jev — featherless-ai — Turns compatible open models into classification endpoints; incl. Laya backend | referenced | https://github.com/featherless-ai/simple-jev |
| S4-06 | jevmlx — Parallel constrained decisions with MLX models; Apple Silicon | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S4-07 | JEVfire — Parallel decisions using CUDA LLMs + vLLM; inference implementation | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S4-08 | PocketJev — iPhone visual decisions with MLX + option logits; on-device app/technique | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S4-09 | jev-visual — hr98w — Educational shared-context visual candidate scoring; experimental | referenced | https://github.com/hr98w/jev-visual |
| S4-10 | OpenJev (DiffusionGemma server) — razorback16 — Decision API over DiffusionGemma + other backends; server, not weights | referenced | https://github.com/razorback16/openjev |
| S4-11 | openjev-sglang — ekzhang — Prefill-only compatible endpoint over open models; indexed archived | referenced | https://github.com/ekzhang/openjev-sglang |
| S4-12 | LocalJev — githubnext — Local Jev-compatible API; unique trained family not established | referenced | https://github.com/githubnext/localjev |
| S4-13 | jeff — logan-markewich — Self-hosted Jev replacement powered by GLiFormer; adapter/serving | referenced | https://github.com/logan-markewich/jeff |
| S4-14 | TypeAR / TypeLLM — Jev-inspired type-safe decoding; related approach, not a direct substitute | referenced | https://github.com/TypeLLM/TypeLLM |
| S4-15 | daseinlabs/open-jev — MLX implementation with custom fine-tuning; checkpoint status unestablished | referenced | https://github.com/daseinlabs/open-jev |
| S4-16 | JevForge — zwliJay — Data synthesis + training + candidate-branch scoring stack; toolchain | referenced | https://github.com/zwliJay/jev-forge |

## S5 — Runtimes, ports, and directories

| ID | Item | State | Source |
|---|---|---|---|
| S5-01 | Ollaya — Local model manager/server for Laya, Kev, Von, Decider, Nimble + others | referenced | https://github.com/ollaya-dev/ollaya |
| S5-02 | Laya-MLX — Native Apple Silicon port of Laya | referenced | https://github.com/mizorewww/laya-mlx |
| S5-03 | Laya-CoreML — Core ML / Neural Engine port of Laya | referenced | https://github.com/mizorewww/laya-coreml |
| S5-04 | laya.cpp — Native C++/ggml Laya inference + compatible server | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S5-05 | sys1 — Rust/Candle decision-model server | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S5-06 | Bud Decision Studio — Desktop environment to run, evaluate, and train decision models | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S5-07 | TurinTech compressed models — Converted/compressed builds of existing families; not separate families | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S5-08 | classifier.dev — Shared interface for Jev, Laya, and Kev | referenced | https://classifier.dev/ |
| S5-09 | Awesome Decision Models — Directory separating hosted APIs, open models, techniques, runtimes, SDKs, apps, papers | referenced | https://github.com/AnotiaWang/awesome-decision-models |
| S5-10 | Jevland repository index — Ecosystem index; hundreds of repos incl. apps/integrations/demos, not distinct models | referenced | https://jevland.mnimiy.com/repos/ |
| S5-11 | OpenRouter decision rankings — Hosted versions + routed usage tracking; usage is not an accuracy leaderboard | referenced | https://openrouter.ai/rankings/decisions |
