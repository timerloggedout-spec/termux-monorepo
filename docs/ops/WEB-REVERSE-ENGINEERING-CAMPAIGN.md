# Web Reverse Engineering Campaign — the Origami

**One folded masterpiece, not two piles of candidates.** The Foundry
catalog (PR #1550, 11 upstreams) and the browser-lane imports
(PR #1551, 22 candidates) overlapped and competed. This campaign document
reconciles them into a **single categorically-nested taxonomy**, placed
under the broader umbrella, with one machine-readable SSOT.

## The umbrella (placement is taxonomy, not taste)

```text
🏖️ Umbrella: Connectors Tooling Abilities, All Surfaces (parent lane)
├── Integration Mesh Matrix            docs/ops/INTEGRATION-MESH-MATRIX.md
├── Device Pull Queue                  ops/device-queue/
├── Quota & Registry                   ops/quota/
├── Repository Observatory (S|F|W)     docs/repositories/
└── ☔ Campaign: Web Reverse Engineering      <-- THIS SCOPE
    ├── design SSOT        docs/ops/WEB-ADAPTER-FOUNDRY.md
    ├── campaign (this)    docs/ops/WEB-REVERSE-ENGINEERING-CAMPAIGN.md
    ├── loadable skill     .agents/skills/web-adapter-foundry/SKILL.md
    ├── runtime + SSOT     ops/web_adapter_foundry/
    │     waf.py · catalog.json · taxonomy.json · registry.schema.json
    ├── tests              tests/test_web_adapter_foundry.py
    └── account signals    docs/repositories/browser-lane-imports.json
                           (star = import signal, Observatory = census)
```

**Placement rules** (also in `taxonomy.json`): design/campaign docs in
`docs/ops/`; runtime + machine registries in `ops/web_adapter_foundry/`;
skills in `.agents/skills/`; tests in `tests/`; account-signal matrices in
`docs/repositories/`. A candidate is placed **exactly once** by primary
category; cross-membership lives in facets (`sources`, tiers, transports),
never in duplicated files.

## The fold — reconciliation of the candidate templates

31 unique candidates (11 Foundry + 22 browser-lane − 2 in both).
The two overlaps are single entries with dual provenance, not duplicates:

| Repo | In Foundry as | In browser-lane as | Folded placement |
|---|---|---|---|
| `greekr4/rever-browser` | investigation core | adjacent foundry peer | `capture-and-recon/cdp-workbenches` |
| `jackwener/OpenCLI` | execution core | website→CLI reference | `adapter-systems/website-to-cli` |

### Nested categories (counts from `taxonomy.json`)

| Category | n | Contents (primary placement) |
|---|---|---|
| `engines` | 6 | Lightpanda, Obscura, oxibrowser (thin-from-scratch) · browserless (fleet infra) · Carbonyl (Chromium-class) · Browsh (Firefox-class) |
| `drivers-and-clients` | 4 | chromedp, nodriver (CDP drivers) · patchright (stealth) · agent-browser (agent CLI) |
| `capture-and-recon` | 3 | rever-browser · REA · playwright-mcp |
| `code-recovery` | 1 | webcrack |
| `contract-synthesis` | 3 | mitmproxy2swagger · curlconverter · reverse-api-engineer |
| `adapter-systems` | 4 | OpenCLI + linxule fork · awesome-reverse-engineered · reverse-cli-anything (desktop) |
| `verification` | 1 | Schemathesis |
| `agent-layers` | 2 | browser-use · stagehand (offload-only) |
| `extraction-and-discovery` | 4 | firecrawl · crawl4ai · jina-reader · crawlee (the "reverse-SEO" end) |
| `substrate` | 3 | termux-packages · termux-x11 · Cromite (handset) |

Every node carries its facets: `sources` (which candidate set(s)),
`b160v_tier` where the browser lane assessed it, `import_status`
(already-starred / starred-2026-10-22 / candidate-not-imported),
`streaming` surface, licence, last push. Query it:

```bash
python3 -m ops.web_adapter_foundry.waf taxonomy                 # whole fold
python3 -m ops.web_adapter_foundry.waf taxonomy h4ckf0r0day/obscura
```

## Transports branch (stdin is one fold of five)

| Transport | Status | Shape |
|---|---|---|
| JSONL stdin/stdout | implemented (`waf serve`) | one envelope/line, protocol-only stdout |
| CLI | implemented (`waf`) | same `handle_request` |
| CDP over WebSocket | native to Tier-1 engines/drivers | browser control + event streaming |
| **SSE** | **implemented** (`ops/web_adapter_foundry/facade.py`: `GET /events` over the landed `sse_encode`/`EventBus`) | one-way result/event streams; publish-once, subscribers never re-execute |
| HTTP | **implemented** (same facade: `POST /invoke`, `GET /health`) | one envelope over HTTP -> one response, also published to `/events` |
| WebSocket / MCP | designed facades | over the same `handle_request`; MCP is its own protocol, never a JSONL label |

## B160V law (applies to every fold)

Playwright / Chromium / Selenium are known on-device failures on the
BLU B160V (crash / resource-exit Termux). Tier-1 thin engines on-device;
everything Chromium/Firefox-class offloaded, driven over CDP-WebSocket /
SSE / JSONL. See `docs/repositories/STARS-FORKS-WATCH.md` §3.

## Registered environments

Environments registered for RE / pentest work that are **not** taxonomy
candidates. The taxonomy folds the Foundry catalog + browser-lane candidate
sets exactly once (31 nodes, test-pinned in
`tests/test_web_adapter_foundry.py`); an environment with no
GitHub-canonical source has no fold, so it is registered here instead. If
one ever enters a candidate set, it folds in through the normal pipeline.

| Environment | Registered | Why it's here | Fleet fit |
|---|---|---|---|
| **Kali Linux** (kali.org · build scripts: gitlab.com/kalilinux) | 2026-10-26, at release 2026.3 | The lane's reference penetration-testing / RE environment, registered at the owner's direction as an *agentic environment* — a full toolset image an agent is given as its workbench, not another single-purpose adapter. | **Offload / container only.** 2026.3's refreshed build scripts each ship `build-in-container.sh` (auto-detects Docker/Podman, builds the official image inside a container; the full refresh is aimed at 2026.4), so images are built where containers run — never on the B160V. NetHunter is Kali's Android surface; it belongs to the device lanes and is not dispatched from here. New in 2026.3 and relevant to this campaign: `katana` (crawling/spidering), `dalfox` (XSS), `qsreplace`, `rustscan`, `snaffler-ng`. Status: registered reference environment — not a Foundry upstream, no fleet install yet. |

## Campaign order of operations

1. ✅ Foundry core + iDEAL doc (#1550) · ✅ Stars|Forks|Watch consolidation
   + Observatory v2.2 (#1551) · ✅ this reconciliation + taxonomy SSOT.
   Observatory verification (2026-10-22): first workflow_dispatch run left
   the Watching table empty — diagnosed: no `REPOSITORY_OBSERVATORY_TOKEN`
   secret exists, so the run fell back to `github.token`, which cannot
   read `/user/subscriptions` (and the public `/users/{owner}/subscriptions`
   route is a proven 204 — watch lists are not public). **Fixed the same
   day, no new provisioning:** PR #1560 added the repo's existing stored
   user token (`OPERATOR_GITHUB_TOKEN`, per the Issue #184 inventory) as
   the fallback before `github.token`; the next dispatch run succeeded
   and the committed matrix's Watching table holds **128 rows** — exactly
   the PAT-side evaluation count. Watching is now live in the daily run.
2. ✅ Tier-1 engine proof — **remote-first** (owner correction,
   2026-10-22), executed on GitHub Actions arm64 + x86_64
   (`tier1-engine-proof.yml`, dispatch-only; PRs #1563/#1564).
   **Measured** (`docs/ops/TIER1-ENGINE-PROOF-RESULTS.md`): both engines
   run natively on aarch64 and answer CDP — Obscura v0.2.5 (Chrome/145)
   at **32,052 kB** idle RSS, Lightpanda 1.0.1 at **17,008 kB** — phone-class
   footprints, an order of magnitude under Chromium-class. Round 1 failed
   (glob picked the tarball; a VA-space cap broke serve startup) and was
   diagnosed locally + fixed, which is the loop working as intended.
   Still open from this step: WS-level navigation/extraction depth
   (`/json/new` GET is refused; drive `Target.createTarget` over WS next)
   and on-device execution itself, gated on the pull-queue installer.
   Collaborator entry point for any Target 🎯: the Target Brief +
   `waf intake` flow in `.agents/skills/web-adapter-foundry/SKILL.md`.
   **Input surfaces landed (T.A.K. input layer):** the brief is filable as
   a GitHub Issue (`.github/ISSUE_TEMPLATE/target-brief.yml`, label
   `target-brief`) — filing/editing wakes `target-intake.yml` (event
   trigger, no cron), which parses the form back into the brief schema
   (`waf issue-intake`) and comments the dispatch plan onto the issue.
   CLI, JSONL and chat briefs converge on the same validation + planner.
   Per the owner (2026-10-23): the phone is a remote orchestrator for
   these dispatches; the dual B160V device surfaces are owned by their
   existing lanes and this campaign waits for them to stabilise before
   anything dispatches on-device.
3. Then: HTTP/SSE facade server over `handle_request` using the landed
   primitives; first real adapter (one authorised site, three read-only
   operations, Foundry milestone).
4. Observatory keeps the census: candidates enter by star, get verified
   through the Foundry promotion pipeline, and only then are adopted.
