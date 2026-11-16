# Latency baseline — 2026-11-01 (VM vantage)

Owner flag (2026-11-01): inter-network latency becomes a **measured fleet
quantity**. Tonight's evidence — a Pages mirror lag misread as queueing,
Actions schedule under-delivery (~3.5 h on a `*/10` cron), PAT window waits —
was argued from impressions because no instrument existed. This document is
the first baseline from the standing instrument that now does:

- Instrument: `ops/latency/probe.py` (stdlib only), targets in
  `ops/latency/targets.json` (every target confirmed from a repo source,
  cited per target).
- Raw records: `ops/latency/reports/2026-11-01-baseline-vm.json`
  (schema `fleet-latency/v1`, generated 2026-11-02T07:49:12Z =
  2026-11-01 23:49 PT, vantage `vm`).
- Re-measurement: `.github/workflows/latency-probe.yml` — dispatch-only,
  state-gated (below). **No cron, no daemon, no fixed cadence anywhere.**

## Method

Per target: 3 unauthenticated HTTPS GETs via curl timing variables
(`time_namelookup / time_connect / time_appconnect / time_starttransfer /
time_total`), redirects not followed (a surface's first response is its real
edge behaviour). No authenticated calls; no inference or API quota is spent —
401/404 responses are expected on API surfaces and are fine; timing is the
product. `dns`, `tcp`, `tls` are segment durations; `ttfb` and `total` are
absolute from request start. Table values are medians of 3 runs, ms.

## Baseline (VM vantage, medians of 3)

| Surface | Status | DNS | TCP | TLS | TTFB | Total |
|---|---|---|---|---|---|---|
| github-api | 200 | 1.8 | 1.0 | 362.5 | 726.8 | 727.7 |
| github-web | 200 | 0.6 | 0.2 | 263.0 | 685.6 | 1047.5 |
| github-raw | 200 | 0.7 | 0.2 | 332.1 | 632.2 | 652.3 |
| github-pages | 200 | 0.6 | 0.1 | 405.1 | 740.2 | 740.4 |
| cloudflare-api | 404 | 0.6 | 0.4 | 335.7 | 591.2 | 591.3 |
| device-queue-worker | 200 | 0.6 | 0.1 | 316.3 | 754.2 | 754.3 |
| neon-api | 401 | 0.6 | 0.2 | 346.7 | 740.5 | 740.6 |
| fly-api | 200 | 0.6 | 0.2 | 549.1 | 1076.1 | 1123.4 |
| koyeb-api | 404 | 0.6 | 0.1 | 550.6 | 1137.6 | 1137.6 |
| vercel-fleet | 200 | 1.7 | 0.4 | 577.6 | 1088.1 | 1088.2 |
| openrouter | 200 | 0.7 | 0.2 | 296.1 | 625.5 | 1136.3 |
| groq | 401 | 0.7 | 0.2 | 295.0 | 663.7 | 663.8 |
| huggingface | 200 | 0.9 | 0.2 | 242.4 | 684.0 | 831.5 |
| cohere | 401 | 0.7 | 0.2 | 346.3 | 677.7 | 677.7 |
| mistral | 401 | 1.2 | 0.2 | 486.2 | 907.1 | 947.1 |
| cerebras | 403 | 0.7 | 0.1 | 398.5 | 800.8 | 800.9 |
| sambanova | 200 | 1.4 | 0.3 | 385.2 | 639.2 | 643.7 |
| siliconflow | 401 | 1.4 | 0.1 | 355.3 | 724.6 | 724.7 |

All 18 surfaces answered; none unreachable. Slowest medians: koyeb-api
(1137.6), fly-api (1123.4), openrouter total (1136.3 — its body transfer, not
its TTFB of 625.5, is the slow part), vercel-fleet (1088.2). Fastest:
cloudflare-api (591.3), sambanova (643.7), github-raw (652.3).

## Caveats — read these before quoting any number

1. **VM egress passes through a proxy, and the data proves it.** DNS is
   0.5–1.8 ms and TCP is 0.1–0.4 ms on *every* surface, near or far: those
   two segments measure reaching the local proxy, not the origin. The real
   network leg sits inside TLS and TTFB. On this vantage, **dns/tcp are
   proxy-local and not meaningful per-surface**; tls, ttfb and total are the
   comparable series.
2. **Every total sits in a ~0.6–1.2 s band** dominated by the proxy leg.
   These are not "the internet is slow" numbers; they are this vantage's
   cost of reaching anything. The baseline's value is **comparability over
   time from the same vantage**, not absolute truth.
3. **The Actions vantage will differ** — real DNS/TCP, no proxy, different
   geography. Cross-vantage deltas are indicative, not like-for-like; the
   state gate's thresholds are set wide for exactly this reason.
4. **Run-to-run spread is wide** (vercel-fleet runs: 780–1594 ms; openrouter:
   978–1267 ms). A median of 3 is a floor, not a precision instrument.

## What this instrument can and cannot see (vs tonight's incidents)

- **Pages mirror lag:** the probe times the Pages *serving edge*
  (github-pages: 740.4 ms, healthy). It **cannot** see build/mirror
  propagation delay — a stale mirror serving fast reads identical to a fresh
  one. Propagation lag is a content-freshness measurement (stamp
  comparison), not a latency one. Tonight's lag was server-side Pages
  build queueing; this instrument would have shown a healthy edge
  throughout, which is itself the useful negative evidence.
- **Actions schedule under-delivery (~3.5 h on a `*/10`):** GitHub-internal
  scheduler behaviour. **No network probe can see it** — api.github.com
  answers in ~728 ms total while schedules slip by hours. It is visible
  only in Actions run timestamps (the quota lane's evidence class).
- **PAT window waits:** rate-limit/quota windows (remaining/reset headers),
  not latency. api.github.com latency being ordinary tonight is consistent
  with the waits having been quota, not network.
- **What it can see:** reachability and response-latency shifts per surface
  — provider API degradation, the Cloudflare/Worker path, the Vercel mirror
  edge, Pages/raw serving — "is the path to X slow or down", as a measured
  quantity against this baseline instead of an impression.

## Re-measurement design (cadence law)

Re-measurement is **event/state-gated; there is no schedule**.

- **Actions vantage:** `.github/workflows/latency-probe.yml` is
  `workflow_dispatch` only (inputs: vantage note, target set full/core).
  The run probes, then applies the **state gate** in `probe.py --gate`
  against this checked-in baseline: a new report is committed to
  `ops/latency/reports/` (github-actions[bot] pattern, as in
  repository-observatory) **only if** some surface's median total deviates
  **>50% AND >300 ms**, or a surface errors / changes error state.
  Otherwise the job writes only a step summary ("no material delta") and
  commits nothing.
- **VM vantage:** re-runs are agent-initiated on anomaly events with the
  same script (`python3 ops/latency/probe.py --vantage vm`), compared with
  `--gate`. No VM daemon or cron is created.
- **Baseline replacement:** when a sustained shift or a vantage change
  warrants a new baseline, it lands by PR (like this one) and the workflow's
  baseline pointer is updated in the same PR.

## Target provenance notes

`ops/quota/provider-managers.json` records documentation sources only — it
has no API-base field — so provider bases were taken from the wired
adapter/catalog modules that registry indexes (`scripts/provider_model_catalog.py`,
`scripts/provider_quota_managers.py`, `scripts/ops/allocation_probe.py`):
the exact URLs fleet code calls. Neon and Koyeb are probed at the API hosts
the fleet itself uses (`console.neon.tech` `/api/v2` per
`scripts/quota_poll.py:106`; `app.koyeb.com` `/v1` per
`.github/workflows/koyeb-hindsight-deploy.yml`) — the same API surfaces as
api.neon.tech / api.koyeb.com. The Vercel target is the fleet mirror
hostname recorded in `docs/ops/SITE-MAP.md` (termux-monorepo.vercel.app),
not the platform edge.
