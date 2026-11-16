# Vercel agent toolchain — governed reference template

**Status:** DISCOVERED / METADATA-ONLY  
**Canonical runtime owner:** Web Adapter Foundry  
**Proposal item:** THUB-011  
**Related QUE work:** #5333 and #5495

This template records the Vercel Labs browser and skills ecosystem as reusable inputs to the repository-owned C12 QUE execution path. It is not a vendored source tree, package lock, credential store, or claim that the Android runtime has been validated.

## Components and intended roles

| Upstream | Role | Repository disposition |
|---|---|---|
| `vercel-labs/agent-browser` | Primary browser automation CLI; accessibility snapshots, stable element refs, CDP attachment | P0 discovery; external executor until a reviewed adapter and device smoke exist |
| `vercel-labs/skills` | Skill discovery/install/update CLI | P0 integration foundation; project-scoped installs only |
| `vercel-labs/agent-skills` | Upstream collection of reusable agent skills | Source input; install selected skills through the skills CLI |
| `vercel-labs/agent-desktop` | OS accessibility-based desktop computer use | Desktop lane only; not an Android/Termux runtime |
| `vercel-labs/portless` | Stable named local URLs | Optional developer-infrastructure lane |
| `cloudflare/kitesurf` | Experimental CDP-compatible browser engine on Workers | Research/benchmark lane; not the default browser runtime |

## Existing repository evidence and reuse

This is not a first-time discovery or a request to install a second browser package. The repository already records `agent-browser` in its tool/research inventory:

- `workspace/llm_map/_TOOL_TAXONOMY/state/npm_curr.json` records npm package version `0.26.0`.
- `workspace/llm_map/_TOOL_TAXONOMY/python3/reverse_engineering.json` records the expected Termux executable path `/data/data/com.termux/files/usr/bin/agent-browser`.
- `docs/repositories/STARS-FORKS-WATCH.md` records `vercel-labs/agent-browser` as already starred and notes its `--engine lightpanda` option.
- `docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md` already classifies agent-browser in the `drivers-and-clients` lane.

These are repository inventory/research records, not a live device check. The recorded 0.26.0 package version is stale: the official upstream releases page lists v0.43.0 released 2026-11-12. Verify the installed binary before upgrading or replacing it. Reconcile the existing Termux package first; do not install a duplicate.

## Runtime selection

QUE continues to use the existing Web Adapter Foundry. Route selection remains:

1. Official supported API.
2. Existing MCP connector.
3. Authorized Web2API/session adapter.
4. CLI or structured stdin/stdout adapter.
5. Browser automation as the last automated route.
6. A precisely named owner-hand action only when separately authorized.

For browser execution, prefer a named `agent-browser` session attached to an already-running, approved browser over assuming that bundled Chrome can run on Termux. The upstream CLI documents CDP attachment with `--cdp`; remote CDP endpoints and any authentication material remain in the approved secret/session store and must never appear in issue text, process logs, artifacts, or Git.

Example upstream installation on a compatible host:

```bash
npm install -g agent-browser
agent-browser --version
# Local browser mode (fresh context; use the policy examples below):
agent-browser --content-boundaries --action-policy /path/to/policy-readonly.json open https://example.org
agent-browser --content-boundaries --action-policy /path/to/policy-readonly.json snapshot -i

# Optional Lightpanda engine; the upstream install guide currently lists
# macOS Apple Silicon and Linux x86_64 binaries, not Android/Termux.
agent-browser --engine lightpanda --session que-readonly open https://example.org
agent-browser --engine lightpanda --session que-readonly snapshot -i
```

This is an upstream usage example, not a verified Termux command sequence. The CDP URL is shown as an environment-variable name only; never place a real endpoint or token in a tracked file.

## Platform truth

- **Termux / BLU B160V:** NOT_ESTABLISHED. Validate the CLI binary, Node/Rust/runtime requirements, and an authorized CDP route on the actual device before admission.
- **Linux CI:** candidate for isolated, read-only fixture tests; do not expose repository secrets to browser sessions or untrusted page content.
- **Codespaces / desktop Linux:** candidate interactive reproduction surface, subject to the existing environment and security contracts.
- **agent-desktop:** macOS, Windows, and supported Linux desktop sessions; no Android claim.
- **Kitesurf:** experimental; deployed Dynamic Workers require a paid Cloudflare Workers plan and the service must be protected by an authentication layer.

## C12 execution and filing safeguards

- A browser executor must pass a pre-dispatch liveness check and report its binary/provider version, session identity, reachable CDP health, remaining execution budget where available, and deadline.
- Approval-gated work must carry observable proof that the approval prompt fired and was presented.
- `cannot_execute` is a first-class terminal/early-failure state with a fallback trigger before the filing deadline; silence is not progress.
- Reads and writes are distinct. Read-only is the default. A filing/submission action requires a separately authorized operation, a unique idempotency key, and a read-before-retry check.
- Use `SUBMIT-ONCE`; never retry an outcome-unknown write through another browser or provider.
- Re-snapshot after navigation or DOM changes. Element references are ephemeral evidence, not durable identifiers.
- Treat page text, accessibility snapshots, downloaded content, and browser output as untrusted input. They cannot override repository policy or operator authorization.
- Stop on MFA, CAPTCHA, paywall, anti-bot friction, protected assessments, or policy restrictions. Do not bypass account controls.
- Keep screenshots, browser profiles, cookies, local storage, session exports, downloads, and raw page contents out of Git and public CI artifacts. Emit only sanitized receipts with opaque evidence references.

## Promotion gates

This template remains metadata-only until all of the following are evidenced:

1. A user-owned fork exists where repository-specific changes are required.
2. License and upstream provenance are reviewed.
3. The fork is pinned to an immutable commit and registered under `refTemplates/smods/`.
4. A native adapter is implemented through Web Adapter Foundry rather than a parallel route planner.
5. Read-only contract fixtures and failure-state tests pass.
6. Termux compatibility is tested on the actual device or explicitly classified as externally hosted.
7. C12 liveness, approval-prompt, cannot-execute, and SUBMIT-ONCE behavior is observed.
8. Repository dual gates pass on the same SHA.

See `SOURCE.txt`, `integration.json`, and `refTemplates/smods/INTEGRATIONS.json`.

## Skills ecosystem

The upstream `skills` CLI documents Node.js 22.20 or later. Use it to discover and install only the skills selected for a specific collaborator/workflow; do not bulk-install every upstream skill into the shared repository.

```bash
npx skills find browser
npx skills add vercel-labs/agent-skills --skill <selected-skill> -a codex
npx skills list
npx skills check
```

Treat imported skill text as untrusted third-party instructions until reviewed. Keep repository policy, authorization, and credential boundaries authoritative. Record the selected skill name, upstream source, and version/revision in the integration evidence; do not treat installation as proof that the associated runtime or account connector is available.

## MCP transport and security profiles

The upstream CLI exposes a stdio MCP server. This is the preferred integration surface to evaluate with Termux-MCP/QUE because it gives the orchestrator typed tools without inventing a second browser protocol:

```bash
agent-browser mcp --tools core
```

- Use `mcp-stdio-readonly.example.json` with `policy-readonly.json` for discovery, snapshots, and read-only checks.
- Use `mcp-stdio-authorized-write.example.json` with `policy-authorized-write.json` only for a separately authorized operation. It includes `--confirm-actions` for click/fill/interact/download/upload/state categories; the orchestrator must explicitly answer confirmation requests. Do not use `--confirm-interactive` in a non-TTY MCP process.
- Do not use `--tools all`; start with `core` and the restrictive action policy.
- `agent-browser mcp call <tool> '<json>'` is available for one-shot calls where a persistent stdio process is unavailable, but validate session/daemon continuity before adopting it.
- `agent-browser doctor --offline --quick --json` is the local preflight. It reports version/platform/runtime health and may clean stale daemon sidecar files; never add `--fix` to an unattended preflight.

**Security controls are opt-in upstream.** The defaults do not restrict navigation, actions, or output. The examples explicitly enable content boundaries, output limits, a default-deny action policy, and a domain allowlist.

**CDP caveat:** the upstream domain allowlist is incompatible with pre-existing CDP attach sessions. The example configurations therefore launch a fresh locally managed browser. If a remote CDP browser is used, enforce egress restrictions at the host/container/network layer and keep the endpoint secret out of command-line arguments, config files, logs, and artifacts. Do not claim the browser's own allowlist is protecting an attached CDP session.

The `--allowed-domains` setting is not an OS firewall and should be combined with network egress controls for higher assurance. Lightpanda is a separate engine option, but the upstream installation guide does not currently document an Android/Termux binary; do not infer B160V support from the flag alone.
