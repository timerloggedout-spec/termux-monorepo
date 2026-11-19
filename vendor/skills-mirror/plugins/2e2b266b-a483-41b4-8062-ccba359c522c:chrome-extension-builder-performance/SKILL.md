---
name: chrome-extension-builder-performance
description: Measure and improve Chrome extension responsiveness, bundle size, injected-page impact, worker/network activity, storage usage, resource consumption, and cloud cost without security or UX regressions.
---

# Chrome Extension Builder: Performance

Before starting, read [shared policy boundaries](../chrome-extension-builder/references/policy-boundaries.md). Follow host safeguards, task-scoped inputs, synthetic fixtures, and the no-secrets/no-restricted-data boundary. Local tools and persistence are optional: check explicit environment access first; otherwise deliver the same role's useful sanitized findings, specification, code, or test plan in normal Markdown and mark execution unrun.

Baseline the built extension on representative pages. Read [platform architecture](../chrome-extension-builder/references/platform-architecture.md) and QA plan. Record device/browser, fixture size, network, cold/warm state, and repeated-run variance. Set product-appropriate budgets; targets are project choices, not Chrome guarantees.

- Measure time to usable, action latency, bundle/assets, long tasks, memory growth over navigation, worker wakeups, stored bytes, requests/bytes, and provider cost per useful task.
- Keep content scripts scoped/lightweight. Bound/debounce observers, avoid full rescans, schedule expensive work, clean listeners/nodes, prevent duplicate mounts. Compare page impact with/without extension.
- Worker jobs are event-driven, bounded, resumable. Never prevent shutdown as an optimization. Batch quota-aware writes, cache with retention/invalidation, avoid needless alarms/polls.
- Reduce dependencies/assets; lazy-load packaged code where supported, scope fonts, inspect production output. Size reduction never justifies remote executable code.
- Deduplicate cloud requests; bound retries with backoff/jitter, timeout/cancel, quotas, permitted caching. Show partial/errors. Caches must not cross accounts or leak sensitive data.

Deliver `docs/performance.md` with baseline/budgets/profiler evidence, changes, repeated before/after results, and tradeoffs. Rerun affected behavior/security tests. Exit when budgets pass without regression; unavailable hardware/browser measurements remain explicitly unverified.

## Context and outcome handoff

Compare exact comparable artifacts/fixtures and dated measurements; unknown baselines stay unknown. Human, scheduled, and retry outcomes are separate; counts/cost/duration charts require real sample sizes and sources. No 10x benefit claim from agent scores. Preserve the canonical report destination assigned by `references/team.json`; any overview is a dated view, not a competing authority.
