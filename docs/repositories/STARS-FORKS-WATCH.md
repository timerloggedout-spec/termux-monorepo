# Stars | Forks | Watch — Consolidated Evaluation

**Account:** `timerloggedout-spec` · **Evaluated programmatically:** 2026-10-22
(live GitHub API, fully paginated; recount at use time — counts drift)
**Canonical machine index:** `workspace/llm_map/repositories/repository-index.json`
**Navigation projection:** [`matrix.md`](./matrix.md) · **Collector:**
`scripts/github/repository_observatory.py` (v2.2 after this consolidation)

---

## 1. The numbers (live, 2026-10-22)

| Signal | Count | Notes |
|---|---|---|
| Owned repositories | **683** | all public |
| — owned forks | **665** | 97% of the account is fork-as-import |
| — owned originals | **18** | incl. `termux-monorepo`, `timerloggedout-spec.github.io` |
| Starred by the user | **3,108** → **3,114** | +6 starred during this pass (§4) |
| Watching (subscriptions) | **128** | via authenticated `/user/subscriptions` — the signal the old matrix never captured |
| Unique universe (owned ∪ starred ∪ watching) | **3,553** | before this pass's imports |
| Stars received on owned repos | **242** | `stargazers_count` summed over owned |
| Forks received on owned repos | **4** | of which `termux-monorepo` holds 2 |
| Subscribers on top owned repos | **0** | detail-fetched top 5: attention is outbound, not inbound — the account is a *curator/importer*, not (yet) an audience repo |
| Followers / following | 46 / 281 | profile-level context |

Top owned by stars is a long tail (max 2: `AI-codepilot_fork`). The mass of
the account is the **star graph**: 3,108 starred repos, top topics
`python 195 · ai 163 · mcp 148 · ai-agents 146 · llm 129 · rust 113 ·
cli 88 · claude-code 78`; top languages Python 730, TypeScript 345,
Rust 224. Biggest stars in the graph: `sindresorhus/awesome` 523k,
`openclaw/openclaw` 393k, `morluto/rea` 366k (already a Foundry component).

## 2. Existing matrices — found, consolidated

Already initialized in this repo (the hint was right):

| Matrix | Where | State before this pass |
|---|---|---|
| Repository Observatory (owned + starred) | `scripts/github/repository_observatory.py`, daily workflow `repository-observatory.yml` (04:17 UTC), canonical JSON + `matrix.md` (refreshed 2026-10-22 09:26Z) | **Stars ✓, Watch ✗, Forks only as a role flag, no received aggregates** |
| Integration Mesh Matrix | `docs/ops/INTEGRATION-MESH-MATRIX.md` + 6h poll on issue #1505 | apps/integrations, not repo signals |
| Web Adapter Foundry catalog | `ops/web_adapter_foundry/catalog.json` (PR #1550) | tool curation, not account signals |

**Consolidation landed with this document (Observatory v2.2):**

- `watching` provenance: `build_records(owned, starred, watching)` merges
  `/user/subscriptions`; markdown gains **Watching** and **Owned forks**
  tables; the daily workflow passes `--watching` and degrades gracefully
  when its token cannot read subscriptions (never breaks the index).
- Counts now include `watching`, `owned_forks`, `stars_received_on_owned`,
  `forks_received_on_owned`; records carry `watchers`/`subscribers`.
- New deterministic domain: **`browser`** (headless / CDP / Playwright /
  Puppeteer / Selenium / WebDriver / Chromium terms).
- Schema enum extended to `owned | starred | watching`
  (`repository-observatory.schema.json`). Unit tests: 13 passing
  (4 new: watching merge, watching-only role, browser domain, fork counts).
- This file is the human evaluation layer over the canonical JSON;
  poller-output rule unchanged (raw snapshots are never committed).

## 3. Browser lane — the delegated find, B160V-filtered

**Owner history (2026-10-22): Playwright, Chromium and Selenium have all
been attempted on the BLU B160V and FAILED — usually crashing /
resource-exiting Termux.** So this lane is tiered by survivability, not by
hype. Delegated discovery returned 22 verified candidates (live API,
2026-10-22); machine-readable form: [`browser-lane-imports.json`](./browser-lane-imports.json).

### Tier 1 — on-device-thin (the only engines that belong on the B160V)

| Repo | Why | Streaming/control |
|---|---|---|
| [lightpanda-io/browser](https://github.com/lightpanda-io/browser) (36,868★) | Headless browser from scratch in Zig; CDP-compatible; vendor-claimed ~123 MB/100 pages vs ~2 GB Chrome — *project benchmark* | CDP over WebSocket |
| [h4ckf0r0day/obscura](https://github.com/h4ckf0r0day/obscura) (29,158★) | Rust headless engine (V8, no Chromium), ~70 MiB binary (project claim), aarch64 binaries, built-in MCP — **already starred + watching** | CDP over WebSocket, MCP |
| [chromedp/chromedp](https://github.com/chromedp/chromedp) (13,330★) | Go CDP driver, no Node — the driver for the two engines above | CDP over WebSocket |
| [project-oxi/oxibrowser](https://github.com/project-oxi/oxibrowser) (35★) | Pure-Rust Servo headless, CDP + JSON CLI — watchlist tier, very young | CDP, JSON CLI |
| lynx / w3m via [termux/termux-packages](https://github.com/termux/termux-packages) | The native Termux text browsers; [termux/termux-x11](https://github.com/termux/termux-x11) is the GUI route (Chromium exists only under `x11-packages/`) | — |

### Tier 2 — offload-only (browser runs elsewhere; device is a thin client)

browserless (fleet deployment layer), patchright (undetected Playwright),
nodriver (direct-CDP Python), browser-use (118,884★ agent layer),
stagehand, crawlee (its **HTTP mode is device-safe** — browser mode is not),
crawl4ai, firecrawl (194,271★, already starred). Every one of these drives
a Chromium/Firefox-class engine — the known B160V killers — so they run on
a server/CI and the phone talks to them over **WebSocket / SSE / HTTP /
JSONL**, never locally.

### Tier 3 — handset / terminal curiosities

Cromite (real Android GUI browser, arm64 APK), Carbonyl (Chromium in a
terminal — still Chromium, stale since 2024-07), Browsh (headless Firefox
in a TTY). Not automation answers for this device.

### Already in the universe (no import needed)

`obscura` (starred+watching), `vercel-labs/agent-browser` (starred; CLI
that can drive Lightpanda via `--engine lightpanda`), `jackwener/OpenCLI`,
`kalil0321/reverse-api-engineer`, `firecrawl/firecrawl` (all starred) —
plus 49 strong-signal browser-lane repos in the refined in-universe scan
(277 under the loose keyword scan; the refined count is the honest one).

### Honest gap

No actively-maintained headless browser purpose-built to run *inside
Termux itself* was found. The Termux answer is compositional: Tier-1
engines (aarch64 builds) + native text browsers + offload for everything
heavy.

## 4. Current imports — updated this pass

Starred programmatically via the API (204 each, total verified
3,108 → 3,114) — the Observatory picks these up on its next daily run:

`lightpanda-io/browser` · `chromedp/chromedp` · `greekr4/rever-browser`
(Foundry core, was unstarred) · `project-oxi/oxibrowser` ·
`termux/termux-packages` · `termux/termux-x11`

Starring is the account's import signal (starred = research seed, per the
Observatory README — not adoption, not trust). Unstar reverses any of it.

## 5. Transports: stdin is one of four (owner note, 2026-10-22)

For the Web Adapter Foundry (`docs/ops/WEB-ADAPTER-FOUNDRY.md`, PR #1550):

```text
Operation registry -> CLI | JSONL stdin/stdout | HTTP | MCP
Streaming class:    CDP over WebSocket (browsers already speak it)
                    SSE for one-way event/result streams
                    WebSocket for bidirectional control
```

CDP — the protocol Tier-1 engines and drivers above all share — is *itself*
WebSocket-native, so a Foundry executor for Lightpanda/Obscura gets
streaming for free; SSE fits the poller/queue patterns this fleet already
runs (device queue, quota panel). The JSONL core stays the canonical
envelope; WS/SSE are facades over the same `handle_request`, exactly like
HTTP/MCP in the Foundry design. Building the WS/SSE facade is the named
next step, after a Tier-1 engine is proven on-device.

## 6. Failure handling

Per owner instruction: if a step in this pipeline fails, diagnostics +
fixing are delegated, then the process resumes — this pass already ran
that loop twice: (1) the loose browser scan's 277 hits were polluted by
file managers/web apps matching `android|in your browser`, diagnosed and
re-run under strong-signal rules (49); (2) a service restart killed the
first refined run pre-write, re-dispatched to completion with dumps saved
(`dumps.json` stays local — poller-output rule).
