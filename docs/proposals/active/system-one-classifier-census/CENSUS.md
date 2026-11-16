# CENSUS — System One decision models (source document, preserved)

> Provenance: Perplexity research answer, inventory as of 2026-10-21,
> uploaded by the owner 2026-10-27 and registered as proposal
> `system-one-classifier-census`. Preserved verbatim as the evidence
> base; entries carry directory-level verification unless a primary
> source is linked. The proposal's ITEMS.md converts every row into a
> tracked item.

<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Please create a comprehensive table list of level 1(?) Classifiers (?) Like:[Mev, Jev, Laya, Kev, others].

Include their sources URL's in the table.
We're looking for every single one available.

The category you’re looking for is usually called **System One** models, also written “System 1,” “typed decision models,” or simply “decision models”—rather than “level 1 classifiers.” They take application state plus caller-defined questions or options and return choices, scores, or probabilities instead of an open-ended conversational response. Jev, Kev, and Laya belong to this ecosystem.[^1]

There are also two distinct models named Mev: a small recruiting-specific model and Mellow AI’s general decision fine-tune. I’ve included both rather than assuming which one you meant.[^2][^3]

Below is a broad, source-backed inventory as of October 21, 2026. It separates actual model families from inference adapters and runtimes, so the same underlying model isn’t misleadingly counted several times. I cannot guarantee “every single one”: public directories are changing rapidly, and some entries are experiments or announcements rather than production-ready releases.

## Scope and how to read the tables

- Each row is a model family or independently named project; related sizes and versions share a row.
- “Open weights” does not automatically mean unrestricted commercial use.
- Entries supported only by a directory or roundup are identified accordingly; inclusion is not a claim that I individually downloaded or tested them.
- Source URLs appear explicitly in the last column. Where a direct project URL was established, I use it; otherwise, I link to the directory or article documenting the entry.
- Ordinary chat models prompted to classify are excluded from the main inventory. Training-free decision adapters appear separately because they are relevant but are not new trained model families.[^1]


## 1. Your examples, including both Mevs

| Model / family | Developer | What it is | Deployment / important distinction | Source URLs |
| :-- | :-- | :-- | :-- | :-- |
| Jev | TypeSafe AI | Native typed decision model supporting Choice, Score, and Noul questions. | Hosted; OpenRouter lists Jev 1.13 and 1.14. [^1][^4] | [https://typesafe.ai/blog/introducing-system-one-models-and-jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) ; [https://openrouter.ai/rankings/decisions](https://openrouter.ai/rankings/decisions) |
| Kev | Jared Palmer | Open Jev-like decision family built on Qwen; published sizes include 0.8B, 4B, 9B, and 27B across the sources. | Self-hosted; TypeSafe-compatible serving. [^5][^6] | [https://github.com/jaredpalmer/kev](https://github.com/jaredpalmer/kev) |
| Laya | Convai Innovations / NandhaKishorM | Non-autoregressive encoder-based decision family; English and multilingual checkpoints. | Open weights; local deployment and compatible serving. [^1][^6] | [https://github.com/NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) |
| Mev — recruiting | Zhilin Wang / recruiting project | Approximately 0.4B bidirectional encoder with a decision head, fine-tuned from Laya for job–candidate matching. | Domain-specific; the announcement does not by itself establish a generally downloadable release. [^2] | [https://x.com/i/article/2101962974898397246](https://x.com/i/article/2101962974898397246) |
| mev — Mellow AI | Mellow AI / stay-mellow-ai | Qwen3.5-4B LoRA fine-tune selecting among 2–24 options. | Downloadable Apache-2.0 weights; uses a standard next-token head, not Jev’s native non-autoregressive runtime. [^3] | [https://huggingface.co/stay-mellow-ai/mev](https://huggingface.co/stay-mellow-ai/mev) |

## 2. Commercial, company, and laboratory model families

Some entries below also have open weights; this is an organizational grouping, not a closed-versus-open distinction.


| Model / family | Developer | Scope / distinguishing feature | Availability or qualification | Source URLs |
| :-- | :-- | :-- | :-- | :-- |
| Clef | Cloudflare | Decision family covering Clef, Clef Flash, and Clef-omni; multimedia support varies by variant. | Open-weight and hosted through Workers AI. [^7][^1] | [https://www.forbes.com/sites/ronschmelzer/2026/10/12/decisions-decisions-a-guide-to-the-new-wave-of-ai-decision-models-besides-jev/](https://www.forbes.com/sites/ronschmelzer/2026/10/12/decisions-decisions-a-guide-to-the-new-wave-of-ai-decision-models-besides-jev/) |
| pplx-decider / Perplexity Decider | Perplexity | Multimodal decision family; sources list 27B and Flash variants, with v1.1 and v1.2 releases. | Open weights plus hosted inference. [^5][^4] | [https://openrouter.ai/rankings/decisions](https://openrouter.ai/rankings/decisions) ; [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| d1 | Liquid AI | Hosted d1 and d1-ultra; open d1-3B and d1-omni-600M variants. | Hosted and local options; licensing differs from Apache-2.0. [^5] | [https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/](https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/) |
| GPT-6 Luna Decisions / OpenAI Decisions API | OpenAI | Typed predicates, choices, and scores over text and images. | Hosted API; its schema is distinct from Jev’s. [^5][^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) ; [https://openrouter.ai/rankings/decisions](https://openrouter.ai/rankings/decisions) |
| Microsoft-Decision-1 | Microsoft | Classification, agent routing, verification, and workflow decisions. | Foundry and OpenRouter; directory documents a System One endpoint. [^7][^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Decider 1 / state-decider-1 / sd-1 | meraGPT | Hosted Choice, Score, and Noul decisions. | Closed weights; TypeSafe-compatible endpoint; documented context and label limits. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Trio-Spark | MachineFi | Decisions over text, images, and sampled video frames. | Hosted, closed weights; directory-listed. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Solar Decide / Solar Decide Flash | Upstage | Long-context classification, scoring, and workflow routing. | Hosted beta; directory reports a 512K context. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Mercury Decide | Inception | Structured choices, scores, and yes/no decisions. | Hosted; free rate-limited OpenRouter route reported. [^7][^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) ; [https://openrouter.ai/rankings/decisions](https://openrouter.ai/rankings/decisions) |
| Drex | Nace.AI | Enterprise-oriented decision model family. | OpenRouter lists v1.5 and v2.0; release and licensing details need version-specific checking. [^7][^4] | [https://openrouter.ai/rankings/decisions](https://openrouter.ai/rankings/decisions) |
| Span-01 / Span-01 Lite | Respan | Behavior detection in AI traces; outputs present, absent, or not observable. | Specialized behavior classifier rather than a fully general decision model. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Tazo | Tazo Labs | Audio-native decisions for live voice agents, such as respond, wait, yield, and escalate. | API access by request; directory-listed. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| djev | Maisa | Hosted typed decisions over text and images. | Invite/recovery-key access; separate from other similarly named community projects. [^1] | [https://api.djev.dev](https://api.djev.dev) ; [https://github.com/Davipar/djev-dev](https://github.com/Davipar/djev-dev) |
| Tev1 | Together AI | Experimental Qwen-based 4B and 0.8B decision fine-tunes; published training recipe. | Downloadable / hosted; verify current weight-license terms. [^1][^5] | [https://github.com/togethercomputer/tev1](https://github.com/togethercomputer/tev1) ; [https://www.together.ai/blog/how-to-train-your-own-jev](https://www.together.ai/blog/how-to-train-your-own-jev) |
| Strands Decider 2B | AWS Strands Labs | Qwen-based decision model with pointer head and LoRA. | Open weights, training data, and scripts; local deployment. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Nimble / Bespoke-Nimble-9B | Bespoke Labs | Qwen3.5-9B LoRA trained on contrastively curated data. | Open model and recipe; local deployment. [^1][^6] | [https://github.com/bespokelabsai/nimble](https://github.com/bespokelabsai/nimble) |
| GLiNER2.5-Decide | Fastino | Encoder-based caller-defined classification, routing, and scoring; extraction capabilities too. | Apache-2.0; CPU/GPU; not a native Jev API substitute. [^1][^5] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Standard One | Standard Thinking | 3B and 8B text-and-image decision models. | Open and hosted; compatible endpoint, adapters, merged weights, and GGUF builds reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| StartLux-Decision | StartLux | Dense and mixture-of-experts typed decision models with image support. | Apache-2.0 code; CC BY-NC 4.0 weights. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Decision 2.0 | vLLM Semantic Router | Decision models from 0.6B to 27B; multiple questions per forward pass. | Apache-2.0; directory-listed. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Intern-Decision | InternLM | Multimodal 0.8B, 2B, and 4B decision models with calibration tooling. | Weights and training / inference code reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Security-One 27B | Superagent | Specialized security triage: prompt injection, tool calls, code changes, and alerts. | Apache-2.0; directory-listed. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Jeeves | PostHog | 9B Jev-like model combining reasoning-oriented training with a pointer head and diffusion drafter. | Public training code and data reported; directory-listed. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Phocinae-Largha-150M-v1 | Phocinae | Small English/Chinese typed decision encoder with confidence gating. | Apache-2.0; specialist training/evaluation caveats apply. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| VideoJev | VideoJev project | Video grounding and multiple-choice QA using shared video context. | Open 4B and 35B-A3B models reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| OpenThai-SystemOne | iApp / OpenThai | Thai/English 0.8B typed decision model. | Apache-2.0; pip package and Ollama build reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Dwight 4B | Zime AI | Decision model for English B2B sales-call transcripts; separate JSON-insight mode. | Apache-2.0; specialized rather than general-purpose. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |

## 3. Independent, academic, and community models

| Model / family | Developer / identity | Scope / distinguishing feature | Availability or qualification | Source URLs |
| :-- | :-- | :-- | :-- | :-- |
| CLM — Contrastive Language Models | Contrastive-LM | System One models trained with a contrastive state–action objective. | Independent approach; not simply another Jev wrapper. [^6] | [https://github.com/Contrastive-LM/CLM](https://github.com/Contrastive-LM/CLM) |
| Lev | Interfaze | Qwen3.5-4B LoRA with zero-output-token decisions. | Open model; compatible server reported. [^1] | [https://huggingface.co/interfaze-ai/lev](https://huggingface.co/interfaze-ai/lev) |
| Von | wfzyx | Small ModernBERT-based non-autoregressive decision model. | Open local implementation; repository marked archived in the index. [^6][^1] | [https://github.com/wfzyx/von](https://github.com/wfzyx/von) |
| NanoJev | TianyuCodings | 0.6B parallel decision model with game demonstrations and training pipeline. | Open code / weights reported. [^6][^1] | [https://github.com/TianyuCodings/NanoJev](https://github.com/TianyuCodings/NanoJev) |
| jevlike | vinnylarouge | One-pass context-plus-options scorer; game and navigation examples. | Explicitly not a reproduction of TypeSafe’s architecture. [^1] | [https://github.com/vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike) |
| decider family | Mapika | Qwen / Gemma-based family with multiple sizes and a vision variant. | Open self-hosted models; compatible endpoint reported. [^5] | [https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/](https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/) |
| RSI-Jev | RSI-Jev project | Recursively developed decision models with selectable inference effort and vision variants. | Open weights; directory-listed. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| jev-style | jev-style project | Local 0.8B decision model with PyTorch / MLX options. | Compatible server, MCP server, and guard hook reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| PlayJev | PlayJev project | Small vision-based decision model trained for browser games. | Open weights and browser demo reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| OneJev | OmniJev team | Multimodal typed decision family, 0.8B–27B. | Open weights reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| jevos | feder-cr | Small CPU-oriented MiniCPM-derived decision model. | Directory documents Noul-only serving; Choice and Score are not implemented there. [^1] | [https://github.com/feder-cr/jev](https://github.com/feder-cr/jev) |
| WebJev | WebJev project | Browser-action and target selection model. | Apache-2.0 weights, data, and training recipe reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Vev | Vev project | Vision-enabled Qwen 4B / 9B decision models. | Open code; weights restricted to noncommercial use. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| JEV-27B / JEV-9B | AutoTrust | Models distilled from Jev; combined decision and ordinary-generation serving. | Apache-2.0 reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Winnow | Winnow project | Gemma-based 12B / E4B typed decision models. | Apache-2.0; llama.cpp-based serving reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| JevK5 | allebee / alibiserikbay | Qwen-based 2B, 4B, and 9B decision family. | Apache-2.0; CUDA and GGUF runtimes. [^6][^1] | [https://github.com/allebee/jevk5](https://github.com/allebee/jevk5) |
| JevAlt — Deem / Karar / Wähler | Mert Kaya | English, Turkish, and German 4B decision models. | GGUF builds and compatible local serving reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| reflex | kshetrajna12 | Small decision model on a frozen Qwen backbone. | Local compatible server; WebGPU build indexed. [^6][^1] | [https://github.com/kshetrajna12/reflex](https://github.com/kshetrajna12/reflex) |
| imajev | imajev project | Photo comparison / record-checking decisions, including an unknown option. | Apache-2.0; MLX and PyTorch reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| NeoHorse-Jev-4B | TokenRhythm | Text / single-image decision model using prefill-only inference. | Apache-2.0; compatible serving reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| WaterSheep | WaterSheep project | Text decisions including Choice, Score, Noul, and multilabel questions. | Apache-2.0; directory-listed. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Wald-4B | Wald project | Fully trained Qwen-based decoder with optional thinking and calibrated option probabilities. | Apache-2.0; self-hosted GPU server reported. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Valen | Valen-Team | Multimodal 0.8B, 2B, and 4B System One models. | Apache-2.0; code, data, and demo reported. [^6][^1] | [https://github.com/Valen-Team/Valen](https://github.com/Valen-Team/Valen) |
| OpenJev — independent weight project | Project listed separately in the community directory | Trained single-pass decision model with calibration and serving code. | CC BY-NC 4.0 weights; Apache-2.0 helper/server code. Not SemIf or the DiffusionGemma server. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Open-Jev | Zefan Cai | Trained decision-head adapters, including 2B, 9B, and 27B versions. | Project code and weight licensing should be checked separately. [^5][^6] | [https://github.com/Zefan-Cai/Open-Jev](https://github.com/Zefan-Cai/Open-Jev) |
| InnerJev | Fudan / Tongji / King’s College London academic team | 4B and 27B single-pass decision models distilled from reasoning. | Academic code reported; cited roundup does not establish the license. [^5] | [https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/](https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/) |
| Rizzo Flow | Rizzo AI Academy | Small decision-model family with native and Jev-compatible endpoints. | Apache-2.0 reported; choice-option limits apply. [^5] | [https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/](https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/) |
| AgentJev-0.6B | malevrigns | Small candidate-head model for agent-state decisions. | Open implementation indexed. [^6] | [https://github.com/malevrigns/agent-jev](https://github.com/malevrigns/agent-jev) |
| openJev-verdict 2.0 / Verdict | Heman10x-NGU | Approximately 151M non-autoregressive calibrated decision engine. | Experimental project; benchmark claims are project-reported. [^6] | [https://github.com/Heman10x-NGU/openJev-verdict-2.0](https://github.com/Heman10x-NGU/openJev-verdict-2.0) |

## 4. Decision adapters and inference techniques—not necessarily new models

These are relevant to “every available option,” but counting them as independent trained classifiers would blur an important distinction.


| Project | What it provides | Why it is separate from the model inventory | Source URLs |
| :-- | :-- | :-- | :-- |
| SemIf, formerly OpenJev | Typed decisions by reading option logits from existing open models. | Inference technique / implementation rather than a single unique backbone. [^1] | [https://github.com/TheoLeeCJ/SemIf-OpenJev](https://github.com/TheoLeeCJ/SemIf-OpenJev) |
| AnyJev / Tacit | Training-free decision method; also self-distilled Tacit models. | Mixed entry: AnyJev is a method, while Tacit denotes trained derivatives. [^1] | [https://github.com/nokia-applied-research/AnyJev](https://github.com/nokia-applied-research/AnyJev) |
| LitJev | Decision serving from existing Qwen models without training. | Adapter / inference implementation. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| TetraJev | Combines multiple frozen-model decision readings and confidence gates. | Decision pipeline rather than a new trained backbone. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| simple-jev | Turns compatible open models into classification endpoints. | Serving adapter, including a Laya backend. [^1] | [https://github.com/featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev) |
| jevmlx | Parallel constrained decisions using MLX models. | Apple Silicon inference implementation. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| JEVfire | Parallel decisions using CUDA LLMs and vLLM. | Inference implementation. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| PocketJev | iPhone visual decisions with MLX and option logits. | On-device application / inference technique. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| jev-visual | Educational shared-context visual candidate scoring. | Experimental inference implementation. [^1] | [https://github.com/hr98w/jev-visual](https://github.com/hr98w/jev-visual) |
| OpenJev — DiffusionGemma server | Decision API over DiffusionGemma and other backends. | Server using existing models; distinct from the similarly named trained-weight projects. [^1] | [https://github.com/razorback16/openjev](https://github.com/razorback16/openjev) |
| openjev-sglang | Prefill-only compatible endpoint over open models. | Serving implementation; indexed as archived. [^6] | [https://github.com/ekzhang/openjev-sglang](https://github.com/ekzhang/openjev-sglang) |
| LocalJev | Local Jev-compatible API. | Local serving project; not established here as a unique trained model family. [^6] | [https://github.com/githubnext/localjev](https://github.com/githubnext/localjev) |
| jeff | Self-hosted Jev replacement powered by GLiFormer. | Adapter / serving layer over another model architecture. [^6] | [https://github.com/logan-markewich/jeff](https://github.com/logan-markewich/jeff) |
| TypeAR / TypeLLM | Jev-inspired type-safe decoding. | Related decoding approach, not necessarily a direct decision-model substitute. [^6] | [https://github.com/TypeLLM/TypeLLM](https://github.com/TypeLLM/TypeLLM) |
| daseinlabs/open-jev | MLX implementation with custom fine-tuning. | Implementation / training stack; independent checkpoint status not established by the index alone. [^6] | [https://github.com/daseinlabs/open-jev](https://github.com/daseinlabs/open-jev) |
| JevForge | Data synthesis, training, and candidate-branch scoring stack. | Toolchain for building models rather than one model. [^6] | [https://github.com/zwliJay/jev-forge](https://github.com/zwliJay/jev-forge) |

## 5. Runtimes, ports, and directories worth tracking

These broaden access but should not inflate the model count.


| Resource | Role | Source URLs |
| :-- | :-- | :-- |
| Ollaya | Local model manager / server for Laya, Kev, Von, Decider, Nimble, and other decision models. [^1] | [https://github.com/ollaya-dev/ollaya](https://github.com/ollaya-dev/ollaya) |
| Laya-MLX | Native Apple Silicon port of Laya. [^1] | [https://github.com/mizorewww/laya-mlx](https://github.com/mizorewww/laya-mlx) |
| Laya-CoreML | Core ML / Neural Engine port of Laya. [^1] | [https://github.com/mizorewww/laya-coreml](https://github.com/mizorewww/laya-coreml) |
| laya.cpp | Native C++ / ggml Laya inference and compatible server. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| sys1 | Rust / Candle decision-model server. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Bud Decision Studio | Desktop environment for running, evaluating, and training decision models. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| TurinTech compressed models | Converted / compressed builds of existing decision families, not wholly separate model families. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| classifier.dev | Shared interface for Jev, Laya, and Kev. [^8] | [https://classifier.dev/](https://classifier.dev/) |
| Awesome Decision Models | Broad directory separating hosted APIs, open models, techniques, runtimes, SDKs, applications, and papers. [^1] | [https://github.com/AnotiaWang/awesome-decision-models](https://github.com/AnotiaWang/awesome-decision-models) |
| Jevland repository index | Wider ecosystem index; its hundreds of repositories include applications, integrations, demos, and benchmarks—not hundreds of distinct models. [^6] | [https://jevland.mnimiy.com/repos/](https://jevland.mnimiy.com/repos/) |
| OpenRouter decision rankings | Useful for tracking hosted versions and actual routed usage; usage ranking is not an accuracy leaderboard. [^4] | [https://openrouter.ai/rankings/decisions](https://openrouter.ai/rankings/decisions) |

## Important distinctions before treating this as a complete registry

### “System One” is a category label, not a standardized model level

The shared idea is bounded, structured decision-making. The implementations vary: bidirectional encoders, decoder models with pointer heads, next-token option scoring, and adapters around existing LLMs all appear in this ecosystem. Consequently, two products advertising “decision models” may differ substantially in computation and API behavior. Mellow’s mev explicitly documents this difference from Jev.[^3][^1]

### API compatibility is not capability equivalence

A compatible request format does not establish equal context limits, modalities, supported question types, calibration, or accuracy. For example, the directory documents jevos as accepting Noul questions only, despite broader descriptions elsewhere.[^6][^1]

### The remaining completeness gap is identifiable

This inventory covers the named model families and relevant adjacent projects surfaced by the broad directory, ecosystem index, two major comparative articles, OpenRouter’s current rankings, and the two Mev sources. However, some entries still have directory-level rather than individually inspected primary-source verification, and variants, quantizations, private releases, and newly published checkpoints remain an open-ended set. The source material also disagrees on some version, backbone, and licensing details, so I have avoided presenting a falsely precise universal count or cross-model performance ranking.[^5][^7][^6][^1]

<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^20][^21][^22][^23][^24][^25][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/AnotiaWang/awesome-decision-models

[^2]: https://x.com/i/article/2101962974898397246

[^3]: https://huggingface.co/stay-mellow-ai/mev

[^4]: https://openrouter.ai/rankings/decisions

[^5]: https://www.marktechpost.com/2026/10/17/20-jev-alternatives-the-decision-models-taking-on-typesafe-in-2026/

[^6]: https://jevland.mnimiy.com/repos/

[^7]: https://www.forbes.com/sites/ronschmelzer/2026/10/12/decisions-decisions-a-guide-to-the-new-wave-of-ai-decision-models-besides-jev/

[^8]: https://classifier.dev/

[^9]: https://typesafe.ai/blog/introducing-system-one-models-and-jev

[^10]: https://www.firecrawl.dev/blog/what-is-jev

[^11]: https://github.com/walidboulanouar/awesome-jev-use-cases

[^12]: https://www.towardsdeeplearning.com/typesafe-spent-two-years-building-jev-in-secret-open-source-cloned-it-in-4-days-6020238ae08f

[^13]: https://thelearningcurvenjack.substack.com/p/not-just-another-cklassifier-njack

[^14]: https://github.com/dhruvmehra/jevbench/blob/main/README.md

[^15]: https://www.sciencedirect.com/science/article/pii/S2096720926000321

[^16]: https://www.gosearch.ai/blog/ai-decision-models-in-2026/

[^17]: https://www.noroeste.com.mx/hubnegocios/la-arquitectura-invisible-del-dinero-en-blockchain-quien-controla-el-orden-antes-del-consenso-AA26045858

[^18]: https://www.airflow.com/about-us/blog/article?article_id=34\&article_desc=How-does-an-MEV-System-Improve-Indoor-Air-Quality

[^19]: https://featherless.ai/models/stay-mellow-ai/mev

[^20]: https://metatext.io/decision-models/mev

[^21]: https://www.marktechpost.com/2026/10/09/microsoft-ai-releases-microsoft-decision-1-a-qwen3-5-9b-decision-scoring-model/

[^22]: https://rpcfast.com/blog/ai-mev-agents-explained-on-solana

[^23]: https://benchlm.ai/models/microsoft-decision-1

[^24]: https://www.reddit.com/r/LocalLLaMA/comments/1x38cvw/microsoft_fumbles_yet_again_promising_80ms_on/

[^25]: https://www.techflowpost.com/en-US/article/34752

