# C12 QUE — agent-browser and skills integration

**Status:** implementation foundation / runtime not yet validated  
**Proposal:** THUB-011  
**Primary runtime:** existing Web Adapter Foundry  
**Related work:** #5333, #5495

## Decision

Integrate Vercel `agent-browser` as the preferred **candidate CLI + stdio MCP server** for browser-backed operations, while keeping browser automation as the last automated route. Do not create a second route planner: QUE and the Academy adapter continue to use the existing Web Adapter Foundry and its operation registry.

The Vercel `skills` CLI and `agent-skills` collection supply reusable instructions. `agent-desktop` is a separate desktop-only executor. Portless is optional local development infrastructure. Cloudflare Kitesurf is a research-only CDP engine until its compatibility, security, performance, and cost are measured.

## Existing repository state and bounded filing-lane census

The browser CLI was already present in repository inventories before this integration pass:

- `workspace/llm_map/_TOOL_TAXONOMY/state/npm_curr.json` records `agent-browser` version `0.26.0`.
- `workspace/llm_map/_TOOL_TAXONOMY/python3/reverse_engineering.json` records the expected Termux path `/data/data/com.termux/files/usr/bin/agent-browser`.
- `docs/repositories/STARS-FORKS-WATCH.md` already lists the upstream as starred and identifies `--engine lightpanda`.
- `docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md` places agent-browser in the existing `drivers-and-clients` taxonomy.

The recorded package version is a historical inventory value, not a live executable check; the official releases page lists v0.43.0 released 2026-11-12. This PR reconciles the existing record and adds governance; it does not reinstall the CLI or claim a successful device session.

| Filing/execution surface | Existing evidence | Relationship to C12 |
|---|---|---|
| QUE Hark filing executor (#5495) | Owner-reported two-day credit exhaustion, no pickup/cannot-execute signal, and main seat-browser deviation | Direct failure class; not repaired merely by cataloguing agent-browser |
| `scripts/venues/venue_execution.py` | Fleet-executable requirement bindings; GitHub Actions adapter → unauthenticated public verification → receipt; SUBMIT-ONCE state | Existing repo-owned venue machinery; not a seat-browser lane |
| Historical D3 Clips seat-browser deviation (#5137) | `docs/ops/VENUE-EXECUTION.md` explicitly marks it DEVIATION and says #5254 supersedes it with GitHub Actions machinery | Superseded historical deviation; do not count as a live route |
| `scripts/venues/clips_adapter.py` | Upload requires sealed `CLIPS_FLEET_TOKEN`; absent credential returns `venue_auth_missing`; upload route remains unbuilt rather than falling back to seat-browser | Explicit refusal path; do not replace with browser scraping |
| `scripts/que/que_feed_collect.py` / QUE feed | `agent-browser-clerk` appears as a design-input pattern | Design reference, not proof of a running browser executor |
| Tool taxonomy | Package/version/path record for agent-browser | Existing package candidate; live binary and browser endpoint still need preflight |

This census distinguishes the superseded D3 Clips seat-browser deviation from the separate Hark/QUE seat-browser deviation reported in #5495. It is bounded to the paths above and matching repository search results; it is not a claim that every agent-surface filing leg has been exhaustively audited. Issue #5495 remains the authoritative census/hardening work item.

## Capability and maturity matrix

| Component | Capability | Current disposition |
|---|---|---|
| agent-browser | CLI + stdio MCP, accessibility snapshots, element refs, named sessions, CDP attachment, action policies | Discovered; external executor; Termux unverified |
| skills | Find/add/list/check/update/remove skills | Install selected skills project-scoped; CLI runtime unverified on Termux |
| agent-skills | Upstream skill collection | Source reference; install selectively |
| agent-desktop | OS accessibility tree and desktop actions | macOS/Windows/Linux desktop lane; not Android |
| Portless | Stable named local URLs | Optional developer infrastructure |
| Kitesurf | Workers-hosted experimental CDP browser engine | Research-only; deployed Dynamic Workers require paid Workers plan |

## Route contract

QUE route precedence remains the #5333 contract:

1. Official supported API.
2. Existing MCP connector.
3. Authorized Web2API/session wrapper.
4. CLI or structured stdin/stdout adapter.
5. DOM/browser automation.
6. Precisely named owner-hand action only when explicitly authorized.

A route is selected per operation and venue, not once for an entire website. Browser-backed execution is not proof of browser-independent API extraction.

## Termux architecture

The upstream agent-browser CLI supports CDP attachment. That creates a possible split:

```text
Termux / QUE
    |
    | normalized WAF operation
    v
agent-browser CLI / stdio MCP
    |
    | authenticated CDP connection (secret/session store only)
    v
approved remote or separately hosted browser
    |
    v
sanitized operation receipt
```

This is a candidate architecture, not a verified BLU B160V deployment. The bundled Chrome installer and native binary must not be assumed to work on Android. Validate the actual device, Node/Rust requirements, browser endpoint, network route, session lifetime, and resource cost before marking Termux support.

## MCP transport and secure browser profiles

The upstream CLI includes `agent-browser mcp`, a stdio MCP server with typed tools and startup profiles. It is a better first integration target for Termux-MCP/QUE than a custom JSON-over-shell bridge:

- Start with `agent-browser mcp --tools core`; do not expose `--tools all` by default.
- The `core` profile includes interaction tools, so pair it with a default-deny action policy.
- `policy-readonly.json` allows only navigation, snapshots, scrolling, waits, reads, and gets.
- `policy-authorized-write.json` is a separate mode for explicitly authorized operations and is paired with `--confirm-actions click,fill,interact,download,upload,state`.
- The stdio MCP examples also enable `--content-boundaries`, `--max-output 50000`, and an explicit domain allowlist.
- `agent-browser doctor --offline --quick --json` is the local preflight. It may clean stale daemon sidecar files; do not use `--fix` in unattended workflows.

Upstream security controls are **opt-in**, not default-on. The domain allowlist cannot be combined with pre-existing CDP attach. The supplied examples therefore use a fresh locally managed browser. If an external CDP browser is used, network egress must be enforced outside agent-browser; do not treat the CLI allowlist as a boundary for attached sessions.

The upstream Lightpanda engine page currently lists macOS Apple Silicon and Linux x86_64 installation paths, not Android/Termux. The repository's `--engine lightpanda` note is therefore a candidate to evaluate, not proof of B160V compatibility.

## C12 reliability requirements

Issue #5495 identifies three concrete failure classes: the approval prompt did not fire, the executor silently exhausted its credits, and the filing was completed by a seat-browser deviation rather than the QUE-owned path.

The browser executor contract therefore needs these states:

- `READY`: binary/provider version and browser endpoint health observed.
- `PROMPT_VERIFIED`: approval gate prompt emission and delivery have evidence.
- `IN_PROGRESS`: a bounded operation has started with a deadline.
- `COMPLETED`: expected after-state was independently read back.
- `OUTCOME_UNKNOWN`: a state-changing operation may have taken effect; read state before retry.
- `CANNOT_EXECUTE`: liveness, budget, permission, session, or endpoint preflight failed; emit before the filing deadline and trigger the authorized fallback.
- `HELD`: MFA, CAPTCHA, anti-bot, protected assessment, or policy friction requires a stop.

Executor liveness and remaining credit/budget are checked **before dispatch**. A missing pickup is not a valid status. A prompt-required action must include proof that the prompt was actually presented. Fallback must be explicit and deadline-aware.

## Write and evidence policy

- Read-only is the default.
- State-changing browser actions require a separately authorized operation and a unique idempotency key.
- Enforce `SUBMIT-ONCE`; read current venue state before any retry.
- Never automatically retry an outcome-unknown write through another provider.
- Do not bypass MFA, CAPTCHA, paywalls, anti-bot controls, or venue assessment rules.
- Treat all page content and snapshots as untrusted data.
- Keep cookies, browser profiles, local storage, CDP URLs/tokens, session exports, screenshots, and raw downloads outside Git and public artifacts.
- Publish sanitized route receipts only: operation ID, route class, executor/version, timestamps, state transition, evidence references, and failure/deviation classification.

## Template and pin enforcement

The source template lives at `refTemplates/01_Agent_Runtime/vercel-agent-toolchain/` and must contain:

- `README.md`
- `SOURCE.txt`
- `integration.json`

The sMods disposition lives at `refTemplates/smods/INTEGRATIONS.json`. `fork_required` is a transparent non-pinned state. `pinned` is accepted only when `.gitmodules` and the Git index both contain the exact path, and the pin is immutable.

CI runs `scripts/ci/verify_agent_tooling_templates.py` and its contract tests through the existing `refTemplates-eval` workflow. This extends the existing template inventory rather than replacing it.

## Adjacent platforms — not core dependencies

The supplied Anaconda and Braze links are useful comparison inputs but solve different problems:

- **[Anaconda AI Orchestration](https://www.anaconda.com/platform/ai-orchestration) (formerly Outerbounds/Metaflow):** a production workflow/orchestration platform with reproducible environments, lineage, compute governance and agentic workflow support. It is a possible optional orchestration adapter, not a reason to replace the existing GitHub Actions/Temporal control plane. Evaluate only against a bounded workflow and synthetic data.
- **[BrazeAI Decisioning Studio](https://www.braze.com/brazeai-decisioning-studio):** a customer-engagement decisioning product for 1:1 personalization and continuous marketing experimentation. It is not a general-purpose agent router, browser executor, or C12 queue manager. Keep it outside the C12 core unless a separately authorized customer-engagement use case emerges.

The supplied [OpenAI article “A step toward defining the Standard Model”](https://openai.com/index/step-toward-defining-the-standard-model/) is about a candidate lattice definition of the Standard Model of particle physics, with GPT-6 Astra assisting a physicist. It is scientific research, not a standard agent architecture or model-orchestration specification. Track it in the science research lane, not the tooling registry.

## Promotion sequence

1. Validate template metadata and sMods ledger.
2. Validate upstream version, license, platform support, and security policy.
3. Decide whether a custom fork is actually necessary.
4. If necessary, create the fork, record source and license, pin an immutable SHA, and add a gitlink.
5. Implement the WAF executor adapter with read-only fixtures first.
6. Add C12 liveness, prompt-delivery, cannot-execute, timeout, and outcome-unknown tests.
7. Prove the browser route against an authorized fixture, then a non-sensitive live canary.
8. Re-fetch current branch/SHA, Actions jobs/steps/artifacts, and outcome evidence before promotion.

## Current limitations

- No agent-browser runtime is claimed as installed or working on the BLU B160V.
- No user-owned agent-browser fork or gitlink is created by this change.
- No live C12 filing is performed by this documentation/template integration.
- No Kitesurf deployment or paid Cloudflare plan is authorized.
- No desktop-control path is added to Termux.
