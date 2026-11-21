# Docker Hub `credkellar` profile — page 1 observation

**Observed:** 2026-11-15  
**Source:** https://hub.docker.com/u/credkellar  
**Page:** 1 of 3 (profile displayed 1–30 of 90 repositories)  
**Completeness:** page 1 only; pages 2–3 remain uninspected. This is a partial census, not a complete inventory.

The profile page identifies the Docker Hub community user as **Credkellar-boop / Darion Kellar** and links to GitHub `ddkellar01`. This link is a useful identity lead; it does not establish that every repository under the Docker namespace is authored by that GitHub account or that the two GitHub handles are the same person.

## Observed repositories (30)

Names and descriptions below are transcribed from the profile listing. Descriptions are publisher-supplied and not independently verified.

| # | Docker Hub repository | Profile description |
|---:|---|---|
| 1 | `credkellar/omnistream-media-transformer` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 2 | `credkellar/omnistream-api-gateway` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 3 | `credkellar/omnistream-metadata-service` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 4 | `credkellar/omnistream-transcoding-worker` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 5 | `credkellar/omnistream-video-ingest-service` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 6 | `credkellar/omnistream-auth-manager` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 7 | `credkellar/omnistream-youtube-adapter` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 8 | `credkellar/omnistream-streaming-service` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 9 | `credkellar/omnistream-x-adapter` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 10 | `credkellar/omnistream-promotion-orchestrator` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 11 | `credkellar/omnistream-analytics-aggregator` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 12 | `credkellar/omnistream-facebook-adapter` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 13 | `credkellar/omnistream-snapchat-adapter` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 14 | `credkellar/omnistream-instagram-adapter` | OmniStream platform: HLS/DASH video streaming + social cross-promotion, Kafka microservices, FFmpeg. |
| 15 | `credkellar/llm-brutalforce-10k` | 2,000-bot R&D engine: 1,000 scouts sandbox-test new inventions, 1,000 workers brute-force verify all. |
| 16 | `credkellar/gpu-distributed-compressor` | Distributed GPU gradient compression for LLM training: PowerSGD, INT8/Top-K quantization, DeepSpeed. |
| 17 | `credkellar/monad-ultra-infinite-matrix` | A Monad reverse-engineering lab: EVM forensics, CVSS bounty, contract audit and fleet agents in one. |
| 18 | `credkellar/agents-xcorps` | Runs bank AI agent fleets: Front 45%, Middle 30%, Back 25% — from 100 to 250,000 bots. |
| 19 | `credkellar/intuition` | 13-AI multi-expert hardware council in pure Python stdlib for Gemini, Grok, Claude & more. |
| 20 | `credkellar/plan-test-deploy-promote-monetize` | One interface for the full creator pipeline: PLAN, TEST, DEPLOY, PROMOTE, MONETIZE with 11 AI tools. |
| 21 | `credkellar/facevoiceid` | Multi-factor biometric auth: face recognition + voiceprint verification, local-first, with full API. |
| 22 | `credkellar/terms-x-conditions` | Educational security research lab: web consent mechanics, client trust flaws & terms bypass vectors. |
| 23 | `credkellar/ommihear-ai` | Gemini AI hearing ecosystem: real-time scam defense for the elderly, dynamic EQ, haptic pet collars. |
| 24 | `credkellar/prism-vortex` | Multi-agent threat scouting & data-fusion engine: geospatial, identity, telemetry intel, fused live. |
| 25 | `credkellar/rhea-max-payout` | NEAR/Rust audit harness for Rhea Finance: Kani proofs, AI scanning, and $250k CVSS scoring. |
| 26 | `credkellar/neurobypass` | Red-team framework for evaluating AI guardrail resilience: prompt mutations, scanning, judging. |
| 27 | `credkellar/eduguard-abstractor` | EdTech AI guardrail + model abstraction: PII masking, Socratic compliance, Gemini/Claude/OpenAI. |
| 28 | `credkellar/hyper-ai-runtime` | Polyglot AI execution engine for multi-accelerator LLM/SLM orchestration, eBPF & edge telemetry. |
| 29 | `credkellar/mon-ultra-matrix` | Monad reverse-engineering lab: EVM/ABI RE, contract audits, tx forensics and a Gemini agent planner. |
| 30 | `credkellar/iso-iecx` | Autonomous AI framework for ISO/IEC standards compliance and automated video generation. |

## Triage implications

- **Direct RE / security review:** Sandbox-API, Hack-Dhe-Net, DiffRE-Lab, PHP-Vuln-RE, malware research/sandbox images, `terms-x-conditions`, `neurobypass`, `rhea-max-payout`, and the Monad/EVM pair.
- **Potential sensitive-data boundary:** `facevoiceid` (biometrics), `prism-vortex` (identity/geospatial/telemetry), and `ommihear-ai` (health-adjacent audio context) require privacy/data-handling review before any use.
- **Large composite / orchestration claims:** `llm-brutalforce-10k`, `agents-xcorps`, `mon-ultra-matrix`, and `monad-ultra-infinite-matrix` need component-level deduplication and resource/permission analysis.
- **OmniStream cluster:** 14 related images are presented as one platform family. Treat them as a coordinated candidate cluster, not 14 independent integrations; map service boundaries, image digests and shared source before assessment.
- **Not an RE adoption signal:** many profile entries are AI, media, compliance, finance or creator products. Retain them in the census, but do not force them into the RE taxonomy.

## Follow-up

Capture pages 2 and 3 with their page numbers, timestamps and exact 30-row windows. Record per-image tags/digests/size separately; the profile listing does not provide a complete immutable image manifest.
