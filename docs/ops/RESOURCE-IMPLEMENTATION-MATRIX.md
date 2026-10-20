# Resource implementation matrix and aggregate search

**25 resources, including every one of the 20 supplied links.** The supplied links resolve to 19 distinct references: FreeLLMAPI appears twice. The registry also includes Hex, Neon, Supabase, GitHub Codespaces, DigitalOcean, and the previously researched optional gpt4free reference. Google redirect wrappers and advertising parameters are removed, not followed; search queries remain queries. Source line numbers and hashes preserve attribution without copying the tracking URLs.

The working implementation is a portable, offline aggregate search over reviewed resource references and the existing commit-pinned provider claims. It does not turn a directory's “free” label into permission to deploy or invoke a service. Every record stays `runtime_eligible: false`.

## One mesh, different jobs

GitHub JSON/JSONL, commit identities, and run-attempt artifacts remain the evidence spine. Hex is an optional analytics surface, not the mesh itself. Database, compute, discovery, inference, and presentation services have different failure and recovery contracts.

| Surface | Implementation fit | Existing contract to adapt | Admission and recovery work still required |
|---|---|---|---|
| [Hex](https://hex.tech/docs) | Analytics and human-readable views | `scripts/hex_moneyball_export.py`, `docs/ops/HEX-MONEYBALL-INTEGRATION.md` | Sanitized export, workspace authorization, access checks; retain offline export if Hex is unavailable. No live Hex connection is claimed. |
| [Neon](https://neon.com/docs) | Postgres evidence projection | Existing `scripts/ops/lane_event.py` and `.github/actions/lane-event/action.yml`; canonical [evidence substrate](AGENT-EVIDENCE-SUBSTRATE.md) | Reuse native event identities; review the existing adapter's project-creation side effects before invocation. Test migrations, unique replay keys and restore; no project created here. |
| [Supabase](https://supabase.com/docs) | Independent Postgres/API projection | Native event contract in [evidence substrate](AGENT-EVIDENCE-SUBSTRATE.md); new provider adapter needed | RLS, migrations, idempotent replay, health and restore evidence; do not imply automatic Neon replication or failover. |
| [GitHub Codespaces](https://docs.github.com/en/codespaces) | Reproducible execution and workspace | Existing `codespace-create.yml`, `codespace-start.yml`, [credential SSOT](CODESPACE-CREDENTIALS-SSOT.md) | Verify account quota and scoped credentials; persist code and artifacts outside ephemeral compute. No workspace started here. |
| [DigitalOcean](https://docs.digitalocean.com) | Independent compute/hosting failure domain | [Bridge redundancy](BRIDGE-REDUNDANCY.md) and native evidence contracts; new deployment adapter needed | Approved resource/cost plan, reproducible image, health probes, backup and restore tests. No resource provisioned here. |

Official sources establish different cost categories, not account entitlements: [Hex pricing](https://hex.tech/pricing/) separates Community from paid/trial plans; [Neon plans](https://neon.com/docs/introduction/plans) and [Supabase pricing](https://supabase.com/pricing) document capped free tiers; [Codespaces billing](https://docs.github.com/billing/managing-billing-for-github-codespaces/about-billing-for-github-codespaces) ties included usage to account type. [DigitalOcean pricing](https://www.digitalocean.com/pricing) does not establish a blanket permanent free infrastructure tier. Quota exhaustion, pausing and credit expiration are separate failure modes. Multiple vendor names alone do not demonstrate redundancy.

## All supplied references

These rows document supplied references and implementation next actions, not verified service availability or upstream code approval. General lists are deliberately **registered, not recursively crawled**. A new collector needs its own reviewed parser, bounded transport and provenance tests.

| Reference | Type / mesh role | Implementation action |
|---|---|---|
| [Awesome free LLM APIs](https://github.com/mnfst/awesome-free-llm-apis) | Directory / discovery | Existing `provider_recon.py` imports commit-pinned data; maintain per-model account admission separately. |
| [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) | Proxy template / inference and discovery | Existing static import/register reference extraction; adapt ideas to native catalog and policy rather than running upstream proxy code. Supplied twice, one registry identity. |
| [GitHub awesome-free query](https://www.google.com/search?q=site%3Agithub.com+awesome+free) | Search / discovery | Preserve the query; triage results into reviewed canonical registry records, not automatic execution. |
| [Awesome free ChatGPT](https://github.com/LiLittleCat/awesome-free-chatgpt/blob/main/README_en.md) | Directory / discovery | Separate web-only tools from officially authorized APIs. |
| [Awesome free models](https://github.com/12britz/awesome-free-models) | Directory / discovery | Verify model licenses, modalities and actual hosting terms. |
| [Awesome legal](https://github.com/ankane/awesome-legal) | Directory / policy | Reference for legal and license research, not legal advice or blanket approval. |
| [Awesome free tools](https://github.com/abdessamadbettal/awesome-free-tools) | Directory / discovery | Review maintenance, license and primary-source terms for each candidate. |
| [Awesome free services](https://github.com/hql287/awesome-free-services) | Directory / discovery, compute and storage | Distinguish permanent free tiers, trials, credits and paid services. |
| [Awesome Free Developer Services](https://github.com/kebbbnnn/Awesome-Free-Developer-Services) | Directory / discovery | Verify existence, maintenance and official service terms before adding a pinned collector. |
| [Web Awesome discussion 1353](https://github.com/shoelace-style/webawesome/discussions/1353) | Discussion / presentation | Review UI ideas and component licensing before schema-specific adaptation. |
| [Developer tools 2026](https://github.com/spinov001-art/awesome-free-developer-tools-2026) | Directory / discovery | Verify maintenance; a year in the repository name is not freshness evidence. |
| [Nonprofit resources](https://github.com/athman3/awesome-free-nonprofits) | Directory / policy and discovery | Verify nonprofit eligibility rather than assuming this project qualifies. |
| [Startup resources](https://github.com/bllshttng/awesome-free-startup-resources) | Directory / discovery | Separate startup-only credits from generally available free tiers. |
| [Free web tools](https://github.com/aitaskorchestra/awesome-free-web-tools) | Directory / discovery | Review license, maintenance and account requirements. |
| [FreeLLMAPI search](https://www.google.com/search?q=freellmapi) | Search / discovery | Canonicalize and deduplicate new leads before reviewed registry additions. |
| [Together serverless](https://www.together.ai/serverless-inference) | Provider / inference | [Official pricing](https://www.together.ai/pricing) is model-specific; verify price, privacy, capabilities and account access before adapter admission. No general free entitlement inferred. |
| [Meta developer API](https://dev.meta.ai/lp/start-building) | Provider / inference | Verify current API/model contracts, region and terms. The official page documents priced usage; the supplied promotional URL is not proof of free access or a generic Llama endpoint. |
| [FreeLLMAPI topic](https://github.com/topics/freellmapi) | Topic / discovery | Topic membership is an untrusted lead, not approval or evidence of invocation. |
| [Fireworks GPT OSS page](https://fireworks.ai/models/fireworks/gpt-oss-120b) | Provider / inference | [Official pricing](https://fireworks.ai/pricing) describes usage/credit billing; verify model/account access. Training promotions do not prove free inference. |
| [gpt4free, optional prior reference](https://github.com/xtekky/gpt4free) | Access-method template / discovery | Retain [prior license and access-method review](FREE-LLM-PROVIDER-RECON.md); no upstream execution, cookies or HAR harvesting. |

## Search that works without a vendor account

The source of truth is [`resource-registry.json`](../../data/model-selection-market/resource-registry.json), schema `msm-resource-registry-v1`. It carries stable IDs, canonical URLs, tags, mesh roles, native implementation paths, next actions, evidence class, eligibility and supplied-input attribution. Registry additions are ordinary reviewed code changes. No resource URL becomes a fetch target merely by appearing in the registry.

```bash
# Rebuild the combined index from the checked-in registry and provider snapshot.
python3 -m scripts.model_selection_market.resource_index \
  --output /tmp/resource-index.json

# AND-token, case-insensitive search; filters keep distinct service roles visible.
python3 -m scripts.model_selection_market.resource_index --query 'postgres'
python3 -m scripts.model_selection_market.resource_index --query 'free' --mesh-role discovery
python3 -m scripts.model_selection_market.resource_index --kind service --query 'compute' --limit 50

# Regression contracts, including all supplied links and the workflow boundary.
python3 -m pytest -q tests/test_resource_index.py tests/test_resource_registry.py
```

The index preserves each provider candidate's source repository, full commit ID and file hashes; it does not merge two providers merely because names look similar. Resources and provider candidates retain separate record types. Results are deterministically ordered. Unknown/malformed schemas, dangling references, duplicate identities or attempted runtime eligibility fail before output replacement. Atomic writes preserve a previous valid index.

## Continuously extended, bounded by review

The existing [provider research workflow](../../.github/workflows/provider-recon-compound.yml) now builds `resource-index.json` from the **same run's freshly collected provider snapshot** and the reviewed registry. It retains the combined index alongside `provider-recon.json` and `cadence-plan.json` in immutable run-attempt artifacts (30-day retention). The existing daily catalog-completion event and manual dispatch are reused; no new scheduler, secret scope, cron or external database is introduced.

Provider changes extend the generated aggregate at the next successful refresh. Broader resource coverage grows through reviewed registry additions; general directories are not automatically scraped in this slice. The aggregate index is an artifact, not a second automatically committed data file. The publisher still changes **only** `data/model-selection-market/provider-recon.json`. Its restricted write authority, default-branch trust boundary and unchanged/no-write behavior remain intact. Artifact downloads expire; the registry and pinned snapshot remain reproducible from Git.

## Credential and production boundaries

[Issue #184](https://github.com/timerloggedout-spec/termux-monorepo/issues/184) was inspected, including all 80 currently returned comments, as a names-only authorization inventory; no credential value was copied into code, output, artifacts or this matrix. It did not provide a verified Neon, Supabase, DigitalOcean or Hex credential mapping in the inspected material. The integration returned HTTP 403 for repository Actions secret-name enumeration, so secret presence remains **unknown**, not absent. The [native provisioning map](secrets-provisioning-map.md) separates provider keys from similarly named GitHub PATs; do not interchange them.

This implementation needs no external service credentials. Service provisioning, inference, database writes and production routing remain separate scoped changes requiring destination/schema, least-privilege authorization, account evidence and recovery tests. The deliverable is a real searchable registry and workflow-integrated artifact path, not a claim that the entire multi-provider mesh is already deployed.

## Review evidence and actual collaborator attribution

The complete paginated GitHub records for [PR #1297](https://github.com/timerloggedout-spec/termux-monorepo/pull/1297) returned **0 formal submitted reviews**, **21 conversation comments**, and **0 inline review comments** when this follow-through was implemented. These are separate populations: a trigger request, bot status, or a comment saying review was requested is not a submitted review. The prior MSM-008 independent technical-review narrative in `DEBATE.md` remains a claimed local review with a documented P2 fix, not an authenticated GitHub review or proposal-wide consensus.

Conversation actors were `timerloggedout-spec` (4 comments), `ecc-tools[bot]` (6), `github-actions[bot]` (4), `chatgpt-codex-connector[bot]` (2), and one each from `blocksorg[bot]`, `qodo-code-review[bot]`, `vercel[bot]`, `gitar-bot[bot]`, and `coderabbitai[bot]`. Their presence proves those accounts posted, not that each participated in prioritization or approved reconciliation. The single PR commit is `515c47b620a64f5cc3574e2ba9a30b283a0aadb7`; its API author/committer GitHub identities are null. Neither its author text nor a shared operator account proves which human or agent authored it.

The records identify Q as the documented implementation driver and describe an independent local reviewer; the broader proposal names Grok as author/executor and the operator as requested authorizer. Those are **documented role claims**, not additional authenticated review authors. CodeRabbit, Devin, Copilot, and Jules trigger/moniker references must not be counted as completed prioritization, reconciliation, or formal review participation without corresponding outcome evidence. No separate linked prioritization/reconciliation record establishing those contributions was found. The defensible answer is that independent, named collaborator participation in these matrix decisions remains an evidence gap—not a consensus inferred from comment volume.

`review_evidence.py` now normalizes the four paginated event populations, preserves event IDs, commit identities and bound PR head SHA, excludes raw comment bodies/emails, and separates submitted reviews from pending reviews and conversation. The [batch workflow](../../.github/workflows/provider-batch.yml) collects this report read-only against production. Future counts are observed rather than hardcoded to this snapshot. Regression tests target actual GitHub commit/comment shapes and prevent moniker mentions from manufacturing authenticated authorship.

## Native provider implementation follow-through

[MSM-010 provider batch](PROVIDER-BATCH-IMPLEMENTATION.md) adds official Groq, Mistral and Gemini catalog/inference adapters with exact-model, expiring free-account admission. It reconciles all 160 research candidates, leaves unsupported families explicitly blocked, and ships no enabled account policy. The original registry's reference-only eligibility and restricted research publisher remain unchanged. This is not an assertion that all 185 records are inference providers or that every researched provider is deployed.
