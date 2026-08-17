# ICM Provider Routing Resource

> **Status: documentation contract only.** This resource makes provider-routing inputs inspectable. It does not poll a provider, invoke a model, change a secret, alter a GitHub Action, or become the runtime routing authority.

## Purpose and ownership

`routing.md` is the ICM entry point for a **nested provider-routing resource**. Unlike the static root aliases [`CLAUDE.md`](CLAUDE.md) and [`AGENTS.md`](AGENTS.md), it is intentionally maintained by the routing-resource lifecycle because its provider observations, review state, and related governance can change independently.

The canonical machine-readable runtime inputs remain in the repository’s existing provider configuration and workflow code. This ICM resource is a documentation overlay: it records authoritative inputs, observation boundaries, and human gates without copying provider credentials, model inventories, or executable rules.

## Read order

| Step | Read | Why it is authoritative |
|---|---|---|
| 1 | [`CONTEXT.md`](routing/CONTEXT.md) | Defines the routing-resource boundary, ownership, and update lifecycle. |
| 2 | [`providers/registry.md`](routing/providers/registry.md) | Maps provider records to the current source-of-truth configuration and existing GitHub governance. |
| 3 | [`providers/observation-log.md`](routing/providers/observation-log.md) | Records reviewed observations and explicitly distinguishes them from executable routing changes. |
| 4 | [`objects/knowledge/provider-routing.md`](objects/knowledge/provider-routing.md) | Shows the first-order ICM impact and the separate code/workflow gate. |

## Routing rules

1. **Static aliases remain static.** `CLAUDE.md` and `AGENTS.md` are byte-identical navigation aliases. This file is not an alias because it has a different owner and update cadence.
2. **The runtime stays canonical elsewhere.** This resource must link to the repository’s provider configuration, workflow scope, and issue/PR evidence rather than restating them as a competing router.
3. **Polling produces observations, not execution.** A future provider poll may append a reviewed observation record only after its source, cadence, credentials, retention, and failure behavior are approved. It cannot alter provider selection or model invocation through documentation.
4. **Provider changes are separately gated.** Any mutation of GitHub Actions, connectors, secrets, provider APIs, model routing, telemetry, or budget logic is deferred to the later code/workflow review phase.
5. **No credential material belongs here.** Record only secret names, not their values. Do not write tokens, endpoints with embedded credentials, or response payloads that contain sensitive data.

## GitHub Pages and CCTV boundary

A later GitHub Pages deployment can publish a **static rendering** of canonical CCTV card files for mobile viewing. GitHub Pages publishes files from a branch or an Actions-built artifact; it is not the live CCTV renderer, file watcher, WebSocket host, or response writer.[1] The renderer and any publication workflow remain out of this documentation-only change set.

## References

[1] [GitHub Pages: configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) — branch- and Actions-based static publication model.
