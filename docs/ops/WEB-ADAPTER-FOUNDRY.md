# Web Adapter Foundry — iDEAL Document

**Evidence-backed web operation discovery and adapter synthesis.**
Upgraded and provisioned in this repo 2026-10-22 from a curated research
pass (Perplexity, owner-supplied) — consolidated, live-verified against the
GitHub API at build time, and landed with a working runtime core, not just
prose.

| Surface | Path |
|---|---|
| This document (design SSOT) | `docs/ops/WEB-ADAPTER-FOUNDRY.md` |
| Loadable skill | `.agents/skills/web-adapter-foundry/SKILL.md` |
| Runtime core (stdlib Python) | `ops/web_adapter_foundry/waf.py` |
| Upstream catalog (machine-readable) | `ops/web_adapter_foundry/catalog.json` |
| Registry schema | `ops/web_adapter_foundry/registry.schema.json` |
| Example registry | `ops/web_adapter_foundry/examples/example.registry.json` |
| Campaign + reconciled taxonomy | `docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md` · `ops/web_adapter_foundry/taxonomy.json` |
| Tests | `tests/test_web_adapter_foundry.py` |

---

## 1. The category

> **Evidence-backed web operation discovery and adapter synthesis.**

```text
Website interaction
  -> network capture + script analysis + bounded probes
  -> operation model: inputs, outputs, authentication, state, sequencing, errors
  -> verified execution adapter
  -> CLI / stdin-stdout / SDK / HTTP / MCP
```

Two distinct, both valid outcomes:

- **Browser-backed adapter** — a deterministic command executes inside an
  authenticated browser session (OpenCLI's explicit model).
- **Direct protocol adapter** — an extracted client reproduces the requests
  without the original UI (rever-browser documents replay, macros, CLI
  compilation, Python-client export). Per operation, this must be *verified*,
  never assumed.

Acceptance criterion: **repeatable, validated operation**, not "generated
wrapper."

## 2. Curated upstream stack — live-verified 2026-10-22

Stars / pushed / licence as returned by the GitHub API at build time;
recount at use time (counts drift). Upstreams are composed, not vendored.

| Project | Role | Licence | Last push |
|---|---|---|---|
| [greekr4/rever-browser](https://github.com/greekr4/rever-browser) | Closest end-to-end: CDP capture, script inspection, deobfuscation, crypto tracing, replay, WASM, macros, CLI + Python export; ships a Claude Code skill | MIT | 2026-10-21 |
| [jackwener/opencli](https://github.com/jackwener/opencli) | Closest website->CLI: logged-in browser bridge, reusable site adapters, `opencli-browser` + `opencli-adapter-author` skills | Apache-2.0 | 2026-10-20 |
| [morluto/rea](https://github.com/morluto/rea) | Broad RE substrate: web structure/scripts/network, JS/Electron, HAR/SAZ, native/.NET — inspection provider, not the whole pipeline | MIT | 2026-10-22 |
| [alufers/mitmproxy2swagger](https://github.com/alufers/mitmproxy2swagger) | Captured traffic -> draft OpenAPI 3.0 (review + second pass are part of its workflow) | — | 2026-10-19 |
| [j4k0xb/webcrack](https://github.com/j4k0xb/webcrack) | JS recovery: obfuscator.io deobfuscation, unminify, transpile, webpack/browserify unpack | MIT | 2026-07-26 |
| [curlconverter/curlconverter](https://github.com/curlconverter/curlconverter) | Captured request -> code seed (Python/JS/many), CLI | MIT | 2026-03-10 |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Playwright via MCP, structured accessibility snapshots | Apache-2.0 | 2026-10-22 |
| [schemathesis/schemathesis](https://github.com/schemathesis/schemathesis) | Contract-driven verification from OpenAPI/GraphQL; chained ops, property-based | MIT | 2026-10-22 |
| [alexgaoth/awesome-reverse-engineered](https://github.com/alexgaoth/awesome-reverse-engineered) | Discovery: search for an existing client before building one (leads, not truth) | MIT | 2026-10-22 |
| [leileqiTHU/reverse-cli-anything](https://github.com/leileqiTHU/reverse-cli-anything) | Adjacent: closed-source desktop/Electron -> CLI recovery + verification | MIT | 2026-10-16 |
| [linxule/opencli](https://github.com/linxule/opencli) | OpenCLI fork (websites + Electron + local CLIs, recording workflow) — evaluate independently, do not assume upstream compatibility | Apache-2.0 | 2026-04-04 |

**Consolidation rule — smallest stack that satisfies the target:**
existing-client discovery -> rever-browser investigation -> OpenCLI
browser-backed commands -> webcrack when inspection needs it ->
mitmproxy2swagger for REST/OpenAPI drafts -> Schemathesis verification ->
REA only when the target warrants the broader substrate.

## 3. `stdin` is a transport, not the endpoint model

```text
                              +- CLI arguments
                              +- JSONL stdin/stdout
Operation registry -> Executor +- Python/TypeScript SDK
                              +- HTTP gateway
                              +- MCP tool facade
```

- **Endpoint** = network address + method/protocol details.
- **Operation** = the user-meaningful capability (may span several
  endpoints + browser steps — e.g. `report.export` = create job, poll,
  download; model it as one stateful operation).
- **Transport** = how the caller invokes it.

### Invocation envelope (implemented in `waf.py`)

```json
{"id": "req-001", "operation": "reports.list", "account_ref": "workspace-a",
 "input": {"limit": 20, "cursor": null},
 "execution": {"mode": "auto", "deadline_ms": 15000}}
```

```json
{"id": "req-001", "ok": true, "data": {"items": [], "next_cursor": null},
 "meta": {"executor": "browser-context-request", "adapter_version": "0.1.0",
          "evidence_ref": "run-0082"}}
```

Transport rules, enforced by the core: one request / one terminal response
per JSONL line; stdout = protocol only, logs to stderr; credentials via
account/session references, never request bodies (credential-shaped input
is refused); streaming uses a separate versioned envelope; MCP is its own
protocol implementation, not a label for JSONL.

## 4. Agentic implementation architecture

```text
Discovery supervisor
  +- Existing-client researcher
  +- Browser/network observer
  +- Static-analysis worker
  +- Probe planner + executor
  +- Adapter synthesizer
  +- Independent verifier
        -> versioned operation registry
        -> execution router: direct protocol | browser context | UI macro
```

**Stage 1 — Scope & capture.** Allowed domains/accounts, read vs
state-changing, probe budget/concurrency, retention, authorisation gates.
One named workflow at a time. Out: workflow manifest, sanitised capture,
session requirements, operation candidates.

**Stage 2 — Recover semantics.** Correlate UI action -> request sequence,
inputs -> fields, responses -> visible output, token generation -> session
rules, pagination/retries/polling/errors. Every conclusion labelled
`observed | inferred | reproduced | contradicted | unknown`. A string in a
bundle is never automatically a verified endpoint.

**Stage 3 — Bounded probes** (ordered, in `waf.PROBES`). Probing, in this
stack's reverse-engineering sense (owner definition, 2026-10-27): **finding
the DOMs from the request** — starting from a captured request, attribute
the DOMs behind it (the response structures and rendered trees it produces
or feeds, and the endpoint + fields that select them). The differential
probes verify DOMs already found; they never substitute for finding them:

| Probe | Question |
|---|---|
| request-inventory | Which requests does the surface actually make? |
| dom-attribution | For this request, which DOMs does it produce or feed? |
| dom-data-source | Which endpoint serves each DOM, and which request fields/headers select it? |
| exact-replay | Does the captured operation still work? |
| single-field-change | Which input controls which DOM? |
| header-removal | Which headers are actually required? |
| fresh-session | Is behaviour tied to one session? |
| expiry | What must be refreshed, and when? |
| pagination-boundary | How does traversal terminate? |
| browser-vs-direct | Can this DOM be reached without the browser? |
| controlled-error | What failure contract should the adapter expose? |

Within the authorised workflow only — no automatic broad vuln scanning,
account-boundary exploration, or state-changing fuzzing.

**Stage 4 — Synthesise the contract.** mitmproxy2swagger draft reconciled
with observed workflows (its own workflow includes manual review). Rich
metadata beside the schema — see `examples/example.registry.json`:
operation_id, status, side_effect, executor, session rules, evidence
(captures + tests), fallback. Never force WebSocket/stream/multi-step
workflows into a REST-only model.

**Stage 5 — Generate & independently verify.** curlconverter / OpenCLI /
rever exports are seeds, not final clients. Independent verifier checks:
schema conformance, account/session selection, pagination completeness,
expired auth, error normalisation, redaction, write-retry safety,
UI-vs-programmatic agreement. Schemathesis on authorised targets — a
generated schema can be wrong, so its tests alone are not semantic proof.

**Stage 6 — Promote, monitor, repair.** State machine enforced by
`waf.can_promote`:

```text
discovered -> captured -> modeled -> reproduced -> verified -> canary -> stable
stable -> degraded -> (investigate) -> modeled -> ... re-verify
```

Repair workers may modify an adapter but never silently expand the domain
allowlist, account access, or write permissions.

## 5. Failure modes (design around them)

- **Browser dependence is a valid result** — record `direct-http |
  browser-context-request | browser-ui-workflow` honestly; promote toward
  direct only on equivalent tests.
- **Deobfuscation != reproducibility** — keep the original script hash +
  transformation record beside derived analysis.
- **Capture coverage != feature coverage** — track
  `workflow -> observed operations -> verified adapters -> regression tests`.
- **Deterministic != safe to retry** — explicit outcomes `completed |
  rejected | not_started | outcome_unknown`; a write with an unknown
  outcome is never auto-repeated via fallback (the registry validator
  refuses fallback executors on write operations).

## 6. Distribution (this repo)

```text
.agents/skills/web-adapter-foundry/SKILL.md   # loadable skill (all collaborators)
ops/web_adapter_foundry/{waf.py,catalog.json,registry.schema.json,examples/}
tests/test_web_adapter_foundry.py             # envelope, registry, probes,
                                              # promotion, JSONL round-trip
docs/ops/WEB-ADAPTER-FOUNDRY.md               # this document
SKILLS.md + docs/ops/SKILLS-INVENTORY.md      # index entries
```

Run it:

```bash
python3 -m ops.web_adapter_foundry.waf catalog
python3 -m ops.web_adapter_foundry.waf validate ops/web_adapter_foundry/examples/example.registry.json
printf '%s\n' '{"id":"r1","operation":"foundry.ping"}' | python3 -m ops.web_adapter_foundry.waf serve --registry ops/web_adapter_foundry/examples/example.registry.json
python3 -m pytest tests/test_web_adapter_foundry.py -q
```

## 7. First milestone

One authorised site, three read-only operations (list / get one /
paginate-or-export), built in order: Capture (sanitised, traceable) ->
Reproduce (outside the manual interaction) -> Classify (browser dependence
recorded) -> Wrap (one envelope) -> Verify (session expiry, pagination,
errors, account isolation) -> Expose (CLI + JSONL on the same code) ->
Repair (a controlled break triggers investigation, no permission expansion).

## Sources

Upstream READMEs/repos as catalogued in `catalog.json` (live-verified
2026-10-22 via the GitHub API): rever-browser, OpenCLI (upstream + guide),
REA, mitmproxy2swagger, webcrack, curlconverter, playwright-mcp,
Schemathesis (+ its ARCHITECTURE.md), awesome-reverse-engineered,
reverse-cli-anything, linxule/opencli. Research curation: owner-supplied
Perplexity pass, 2026-10-22 (50 references on file with the owner upload;
the load-bearing ones are the eleven repos above).
