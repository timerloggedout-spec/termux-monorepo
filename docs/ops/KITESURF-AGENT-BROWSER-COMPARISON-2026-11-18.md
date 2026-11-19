# Kitesurf vs agent-browser — local comparison trial

- **When:** 2026-11-18, ~16:39–16:47 UTC (single bounded session, ~25 min timebox)
- **Where:** this VM (Muse VM; 4 vCPU visible / ~1.5-CPU cell slice, 7.9 GB RAM total, RAM available fluctuated 0.5–2.6 GB during the trial due to other tenants)
- **Egress:** all VM traffic exits via an authenticated HTTP proxy (`hatch-egress-proxy:3128`, set via `http_proxy`/`https_proxy` env). This fact decides the whole trial — see Verdict.

## What "local" means for Kitesurf (from its README, repo `cloudflare/kitesurf` @ `74110e8`)

- Local path exists and needs **no Cloudflare account**: `pnpm install --frozen-lockfile` → `pnpm run dev`. Bazel builds the engine's WebAssembly, then `wrangler dev` (workerd/miniflare) serves it on `http://127.0.0.1:8787`; agents connect over CDP (`ws://127.0.0.1:8787/devtools/browser`, Puppeteer-compatible).
- Requirements: Bazelisk (as `bazel`), Node.js ≥ 22, pnpm 9.15.4, GCC + libstdc++ dev files. All satisfiable on this VM (Node v24.22.1, g++ present; pnpm + bazelisk installed job-locally for this trial).
- Caveats of record: page isolates use **Cloudflare Dynamic Workers** — a **Workers Paid plan** feature; the paid plan is required to run Kitesurf *deployed on Cloudflare* (local `wrangler dev` is the no-account path). README also warns: locally, page JavaScript runs in `workerd`, which is **not a hardened sandbox** — do not open untrusted sites with a local Kitesurf.
- First build compiles the full Rust core (Blitz HTML/DOM, Stylo CSS, Boa JS) through Bazel; README: "takes a while." It never got that far here (below).

## Battery results

Battery: (a) load https://example.com · (b) load https://timerloggedout-spec.github.io/tribute/ · (c) one scripted interaction.

| Engine | Step | Outcome | Wall time | Failure class |
|---|---|---|---|---|
| agent-browser 0.43.0 (Vercel, local Chromium) | (a) example.com | **FAIL** | ~6 s (incl. CLI start) | `net::ERR_TUNNEL_CONNECTION_FAILED` — Chromium cannot CONNECT-tunnel through the VM egress proxy. Identical to the 2026-11-17 trial; leg stopped there per protocol |
| agent-browser | (b) tribute page | UNRUN | — | blocked by (a) |
| agent-browser | (c) interaction | UNRUN | — | blocked by (a) |
| Kitesurf (cloudflare/kitesurf @ 74110e8) | setup: `git clone --depth 1` | OK | 25.8 s (63 MB) | — git/npm-class clients honor the env proxy fine |
| Kitesurf | setup: pnpm 9.15.4 + bazelisk install (job-local) | OK | 12.8 s | — |
| Kitesurf | setup: `pnpm install --frozen-lockfile` | OK | 27.3 s | — |
| Kitesurf | `pnpm run dev`, attempt 1 | **FAIL** | ~24 s | Bazel 9.3.0 server (JVM) crashed fetching the Bzlmod module registry: `java.util.NoSuchElementException` in `HttpURLConnection.doTunneling0` — the JDK's CONNECT tunnel through the egress proxy breaks. Bazel exit 37; engine never built, `wrangler dev` never started |
| Kitesurf | `pnpm run dev`, attempt 2 (explicit JVM proxy host/port/user/password props from the env proxy) | **FAIL** | <60 s | identical crash, identical class. Bazel cache stayed at 116 MB (bazel binary + server only; no toolchain/module downloads landed) |
| Kitesurf | (a) example.com | UNRUN | — | engine never started |
| Kitesurf | (b) tribute page | UNRUN | — | engine never started |
| Kitesurf | (c) interaction | UNRUN | — | engine never started |

No resource-draw figures for either engine's browsing: neither engine ever rendered a page. Kitesurf build resource draw is also unmeasured — it died in module resolution, before compilation.

## Verdict

- **Usable from this VM today: neither.** agent-browser installs, launches, and dies at the proxy tunnel on first navigation (reproduced twice, 2026-11-17 and today). Kitesurf's local path is real and account-free on paper, but its Bazel/JVM toolchain fetch dies in the *same* proxy's CONNECT tunnel — a different stack (JDK `HttpURLConnection`) failing against the same egress, while Node/git/npm clients traverse it without trouble (clone 26 s, pnpm install 27 s). The blocker is this VM's authenticated egress proxy and how Chromium's and the JDK's tunnel implementations handle it — an environment datum, not a verdict on either engine's quality.
- **What blocks what:** agent-browser ← Chromium net stack vs proxy CONNECT. Kitesurf ← JDK proxy tunneling during Bazel module fetch (before any compile; the heavy Rust build behind it is additionally untested on this ~1.5-CPU slice and would be slow if reached).
- **What the Workers-native form means for the mesh:** Kitesurf's natural home is not a VM-local install. Deployed, it is a browser *endpoint*: no browser container, CDP/Puppeteer interface, one isolate per navigation — browser capability shaped like the fleet's request/response mesh surfaces (a BrowserPod-class node other agents call), not like a local Chromium a seat drives. That deployment requires a Cloudflare account on the Workers Paid plan (Dynamic Workers) — a provisioning decision, not made here. The local form also carries the not-a-hardened-sandbox warning, which argues against running it locally against arbitrary web content even if the build were unblocked.

## Artifacts

- Clone: `~/workspace/compute-jobs/2026-11-18-kitesurf-compare/kitesurf/` (@ `74110e8`)
- Job-local toolchain: `~/workspace/compute-jobs/2026-11-18-kitesurf-compare/tools/` (pnpm 9.15.4, bazelisk)
- Build logs: `dev.log` (attempt 1), `dev2.log` (attempt 2) in this directory
- Trial processes cleaned up (`bazel shutdown` run; no engine or server left running)
