---
name: adaptive-wait
description: Adaptive WAIT for agentic GitHub operations. Re-fetch authoritative state, detect progress or stalls, keep useful disjoint work moving, and promote only from current-SHA evidence.
---

Session 2026-09-30 16:14 PDT:
- Live master `35eb6fde`. Dual-gate last proven on master at `c62f32f`.
- #935 dual-gate PASS on `45484370` (36739425345 / 36739425402).
- WAIT reason on promote: combined-status unstable from Vercel rate-limit, not dual-gate FAIL.
- Do not promote stale #175 keep-alives. Instant-fail path-unfiltered workflows are noise.

Agent-Identity: Grok (Administrator)
