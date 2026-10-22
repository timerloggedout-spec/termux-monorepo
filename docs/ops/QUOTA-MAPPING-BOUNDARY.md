# Complete quota mappings and owner-controlled publication

## Mappings are not live capacity

All 27 canonical provider families have explicit manager registrations, including typed unknown implementations where no endpoint-appropriate counter contract is verified. `scripts/provider_quota_mapping.py` dispatches already-received metadata without requests, retries or inference. `scripts/provider_quota_coverage.py` reconciles the canonical roster, service registry and parser capabilities.

There are six passive parser families: Groq, SambaNova, Hugging Face, Ollama, OpenRouter and SiliconFlow. SiliconFlow's historical parser is not executable; only Ollama and OpenRouter have explicit opt-in private service observers. Eighteen families remain documentation-only and three have unsupported/unknown sources. Registration completeness, parser availability, observation success and runtime admission remain separate states. No new model inference or quota reservation is added.

Hugging Face Hub counters do not describe inference-router capacity. SiliconFlow's historical balance parser is not a live source and cannot establish currency, token/request capacity or a reset. Ollama USD pools/legacy percentages are not request counts. Groq request/token windows and OpenRouter daily-request/monetary dimensions stay separate. Gemini documentation does not establish an account's tier; PR #1441 remains a separate unresolved review.

### Gemini reconciliation with the separate PR

At #1441 head `e17f7db4a0a05480f0a267b91344522837e00a3c`, Gemini's new `scripts/provider_quota_gemini.py:normalize_gemini_evidence` validates an internal caller-supplied private project/model envelope (RPM, input TPM and RPD), not a Google HTTP response schema. That PR also registers the manager as an implemented passive adapter and dispatches to the new normalizer. It always leaves live binding unverified and runtime admission unchanged. None of that parser or broader gate work is copied here.

This branch does not contain that module, so its generated totals remain six parser families, eighteen documentation-only and three unsupported/unknown. Coverage recognizes Gemini as the seventh parser only when both its implemented manager registration and callable normalizer are present. A manager-status edit alone cannot increase the count. In that combined state the totals become seven/seventeen/three; the two private service readers and unknown live-account validation do not change. Gemini's source kind is explicitly `caller_supplied_private_evidence`, and the endpoint dispatcher still rejects Gemini rather than inventing an HTTP collector. Regenerate both coverage and filtered publication snapshots after any future integration. #1441's review state and broader quota/gate changes remain independent; this compatibility handling is not merge approval.

## Read-only sources and storage

Balance observers use fixed HTTPS GET sources, verified TLS, no redirects, bounded responses and no fallback. SiliconFlow remains unsupported as an executable observer: the historical `/v1/user/info` source is disabled because [the official release notes](https://docs.siliconflow.cn/docs/release-notes/overview) report it stopped on Aug 14, 2026. No replacement host, alternate endpoint, or inferred quota source is permitted. Any passive historical parser is not evidence of a live source or a verified observation.

Private service output requires a new mode-0600 file in an owned mode-0700 directory outside Git worktrees. Its CLI prints status only. Never publish raw provider responses, secrets, credential aliases or private-data hashes. Only explicitly filtered, owner-selected numeric quota fields may enter the public dashboard payload. Keys, credentials and raw account/project/user identifiers are excluded regardless of every visibility setting.

## GitHub thresholds and optimizations

REST resource buckets, GraphQL points, App installation limits, user-token limits, repository `GITHUB_TOKEN` limits and Actions operational/billing limits are independent resources. Credential class is explicit and is never inferred from the numerical ceiling. [REST limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) and [GraphQL limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api) are documentation, not account entitlement.

The observer has a fixed source, bounded success cache, reset-aware expiry, per-credential/class process-memory isolation, concurrent-read coalescing and observed throttling cooldown. There is no automatic retry. An optional caller-supplied budget enforces `remaining_budget >= read_cost + reserve` before a read; this is a local guard, not GitHub-wide enforcement. Secondary remaining capacity is unknown. Existing legacy `gh_rate` reads now use this observer.

The registry also maps [Actions operational limits](https://docs.github.com/en/actions/reference/limits): workflow runtime, approval wait, matrix size, trigger-event and queue rates, concurrency-group queue capacity, hosted/self-hosted job runtime, self-hosted queue wait, and plan-specific hosted/macOS concurrency. These documented ceilings never become a fabricated remaining-capacity reading. Existing minutes, cache and artifact-retention resources remain separate.

## What has actually been observed

The existing trusted-master read-only quota path completed in [run 39709610431](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/39709610431), at `f8fe2c3cfe773027728ab756c3f94c6d379b7adb`. Its status-only artifact confirmed private preflight for repository-token REST and Actions cache; user-token, Copilot and Actions minutes remained unknown. A separate existing-connector read returned GitHub resource categories, but its credential class was not independently verified. Neither is proof of a separately validated App installation account.

The publication build may explicitly perform one authorized repository-token `/rate_limit` read in memory. Only sanitized selected usage/limits/availability are passed to the public filter; source response bodies, identifiers and credentials are never written to intermediate artifacts or logs. Unsupported providers stay unknown; no balances are invented to fill the display.

## Pub/Private controls act at publication time

The dashboard has no login wall. General usage, availability and documented limits are public by default as requested by the owner. Its admin selection controls choose whole-family visibility and nested field groups; they edit a local draft and export `quota-visibility/v1` configuration, not private data.

`scripts/quota_publication.py` applies `ops/quota/public-visibility.json` before producing the single public `data/quota-public.json` payload. Private families and nested fields are omitted from registry, coverage and readings together. The page does not fetch raw registry/readings/coverage fallbacks, and the deploy tree excludes older unfiltered quota JSON/text assets. The mirror replaces its generated subtree so removed assets are not retained by `keep_files`. This is publication control, not CSS hiding.

**Persistence step:** export the visibility draft, review it and replace `ops/quota/public-visibility.json` through the existing repository write/PR process. After that configuration reaches master, the existing Pages build regenerates and publishes the filtered payload. There is no browser-to-repository write credential or server-side write-back endpoint in the static page, so clicking a control alone does not change the published site. No new authentication system, account, grant, secret, paid service or schedule is introduced.

Public publication is not retroactive erasure: already-public repository source/history, downloaded data and third-party caches cannot be made private by changing a future build selection. Do not commit raw private readings to the repository. Unknown/stale readings remain visibly unknown/stale and never grant runtime admission.
