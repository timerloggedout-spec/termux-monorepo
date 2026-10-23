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
| **SSE** | **primitives landed this PR** (`sse_encode`, `EventBus`) | one-way result/event streams; publish-once, subscribers never re-execute |
| WebSocket / HTTP / MCP | designed facades | over the same `handle_request`; MCP is its own protocol, never a JSONL label |

## B160V law (applies to every fold)

Playwright / Chromium / Selenium are known on-device failures on the
BLU B160V (crash / resource-exit Termux). Tier-1 thin engines on-device;
everything Chromium/Firefox-class offloaded, driven over CDP-WebSocket /
SSE / JSONL. See `docs/repositories/STARS-FORKS-WATCH.md` §3.

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
2. Next: Tier-1 engine proof — **remote-first** (owner correction,
   2026-10-22). Muse's paired-device channel to the B160V exposes only
   alarms/calendar/contacts/notifications/network/battery — **no Termux
   shell** — and the device pull-queue's on-origin installer has not been
   run yet, so nothing in this chat can execute on the phone today.
   Proofs therefore run on remote free services: GitHub Actions
   (incl. arm64 runners / QEMU aarch64 + memory caps approximating the
   B160V), Hugging Face / Colab-class instances as x86 reference points.
   The B160V runs adapters *later*, via the queue, once its installer
   lands; measured remote numbers gate that step.
   Collaborator entry point for any Target 🎯: the Target Brief +
   `waf intake` flow in `.agents/skills/web-adapter-foundry/SKILL.md`.
3. Then: HTTP/SSE facade server over `handle_request` using the landed
   primitives; first real adapter (one authorised site, three read-only
   operations, Foundry milestone).
4. Observatory keeps the census: candidates enter by star, get verified
   through the Foundry promotion pipeline, and only then are adopted.
