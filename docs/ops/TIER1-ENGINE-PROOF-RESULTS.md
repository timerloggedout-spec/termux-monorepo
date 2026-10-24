# Tier-1 Engine Proof — Measured Results (2026-10-22)

[MUSEai]@{role:{inventory}} — campaign step 2, executed remote-first per the owner's
correction (the B160V has no shell channel from Muse and its pull-queue installer
has not run; GitHub's arm64 runners are the B160V architecture analogue).

## Verdict

**Both Tier-1 thin engines run natively on aarch64 and answer CDP, at phone-class
resident memory.** Lightpanda idles at ~17 MB RSS; Obscura at ~32 MB RSS. Either fits
a B160V-class budget with an order of magnitude to spare versus any Chromium-class
engine. The Tier-1 direction is proven; what remains unproven is page navigation
depth (below) and on-device execution itself (gated on the queue installer).

## Measured (GitHub Actions run 39909905893, proof v2, artifacts tier1-proof-*)

| Engine | Arch | CDP `/json/version` | Browser string | Serve RSS (VmHWM, idle) |
|---|---|---|---|---|
| Obscura v0.2.5 | aarch64 | ✅ answered | Chrome/145.0.0.0 (V8 14.5) | **32,052 kB** |
| Lightpanda 1.0.1 | aarch64 | ✅ answered | Lightpanda/1.0 | **17,008 kB** |
| Obscura v0.2.5 | x86_64 | ✅ answered | Chrome/145.0.0.0 | 34,712 kB |
| Lightpanda 1.0.1 | x86_64 | ✅ answered | Lightpanda/1.0 | 17,616 kB |

Local x86_64 corroboration of the same pinned binaries (same script, this
workstation): Obscura 32,976 kB, Lightpanda 12,616 kB — same class, no surprises.

## Navigation depth — PROVEN (round 3, run 40040338046, proof v3 / PR #1603)

`GET /json/new` is refused by both engines, so v3 drives the real WS protocol
with a stdlib-only probe (`proof/cdp_probe.py`): WS connect →
`Target.createTarget` → attach (flatten) → `Page.navigate` → load event →
`Runtime.evaluate` extraction of the fixture's 25 JS-generated items +
status text + embedded JSON. **Both engines pass the full round trip on
both architectures**, and RSS is now measured genuinely loaded:

| Engine | Arch | Idle RSS | Loaded RSS (after extraction) | Items extracted |
|---|---|---|---|---|
| Obscura v0.2.5 | aarch64 | 31,924 kB | **38,224 kB** | 25/25 |
| Lightpanda 1.0.1 | aarch64 | 17,016 kB | **25,980 kB** | 25/25 |
| Obscura v0.2.5 | x86_64 | 34,784 kB | 42,760 kB | 25/25 |
| Lightpanda 1.0.1 | x86_64 | 17,628 kB | 26,244 kB | 25/25 |

## What is NOT yet proven

- **On-device execution.** These are arm64-runner numbers, not B160V numbers. The
  on-device run stays gated on the device lanes stabilising (owner, 2026-10-23)
  and the pull-queue's on-origin installer.
- **Authenticated sessions.** The Foundry never ingests cookies itself (the
  envelope validator refuses `cookie:` bodies; operations carry `account_ref`
  only). Cookie/session ingestion is the separate origin-device lane
  (`deepseek-cli/inject-cookies.cjs`, `multi-ai-cli/harvesters/`,
  `cli-synthegration/extract_bearer_from_cookies.js`, the deepcli browser
  profile) — the Foundry's `session-reuse` purpose consumes that lane's
  output by reference once its infrastructure lands.

## Round 1 — failed, diagnosed, fixed (the loop working as intended)

Run 39908222462 completed with neither engine answering. Diagnosis was done locally
with the same binaries *before* rewriting: (1) the binary-discovery glob matched
`obscura.tar.gz`/`obscura-worker` instead of the engine; (2) a 512 MB `ulimit -v`
address-space cap silently prevented serve startup (V8/Zig reserve large VA space)
— the cap was removed, replaced by the honest metric: measured RSS; (3) Obscura
blocks loopback by default (SSRF guard), so the fixture probe now passes
`--allow-private-network` explicitly. Fixes landed in PR #1564; round 2 (above)
is the result.

## Engine notes from the proof

- Obscura ships `obscura` + `obscura-worker`, commands `serve|fetch|scrape|mcp`,
  `-p/--port`, `--stealth`, `--obey-robots`, `--allow-private-network`. Its CDP
  surface is Chromium-shaped (`/devtools/browser` WS URL).
- Lightpanda ships a single binary, commands `serve|fetch|mcp|run|agent|version`;
  `serve` is a WebSocket CDP server whose WS URL is the root path; it also answers
  HTTP `/json/version`.
- Both are already in the origami taxonomy (engines) with their execution sites
  unchanged: on-device-thin once the device lane opens, remote-service today.
