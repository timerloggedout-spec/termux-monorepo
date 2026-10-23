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

## What is NOT yet proven

- **Navigation/extraction depth.** `GET /json/new?<url>` is refused by both engines
  (newer CDP expects PUT or WS-level `Target.createTarget`). The post-navigation RSS
  sample therefore equals idle. The follow-up probe drives a real WS CDP session:
  create target → navigate the fixture → extract the 25 JS-generated items →
  sample RSS under load.
- **On-device execution.** These are arm64-runner numbers, not B160V numbers. The
  on-device run stays gated on the device pull-queue's on-origin installer.

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
