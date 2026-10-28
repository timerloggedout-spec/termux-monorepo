# Platform201 — LIVE record (2026-10-27)

Platform201 (formerly **Shoal Stack**; domain shoalstack.com, public branding "Shoal")
is a visual graph cloud infrastructure platform: deploy backends, workers and web
apps in a live graph, into Google Cloud managed by Platform201.

## Live evidence (verified firsthand 2026-10-27)

- Account: signed in via **Google** at app.platform201.com (fleet rule: no GitHub
  sign-in route). No payment method entered; no card on file.
- Plan: **Solo — $0/mo, "Current"** in Billing. Credits observed: **$20.00 USD**;
  estimated monthly cost $0.00.
- Solo caps (Billing, console-observed): 3 projects; 1 environment per project;
  1 seat; 3 nodes each of container / function / gateway / scheduler /
  MongoDB-integration / Neon-DB-integration.
- Project: **n0nplatform201-live** (Hello World (Vite) blueprint: Gateway → Vite
  container, Node.js 20, port 5173), Production environment.
- Deployment 1: completed, console status "(Deployed)", "Your deployment is live".
  Runs on Platform201-managed GCP (Cloud Run, europe-west2) — not fleet GCP.
- Live URL (opened and verified): 
  https://ringerhollow-kangaroorose-killerpuddle.eu1.platform201.live/
  — serves "Welcome to Platform201 / Your Vite Example is running."
- A starter project "My Project" pre-existed in the space (Gateway + Welcome App,
  not deployed by this lane).

## Registry wiring in this PR

- `ops/quota/registry.json`: new record `platform201.projects` (Solo, limit 3).
- `ops/delphi/surfaces.json`: `platform201.solo` → sourced=true, registry_id
  `platform201.projects`, horizon H0, auth note updated (live web account,
  console-only; still **no API token and no Actions credential** — that remains
  the integration gap vs Vercel/Render-class surfaces).

## History

Before this record the surface was REGISTERED-ONLY: a Delphi catalog entry
(sourced=false, limit null) plus the "Platform201 Planning Queue" name cited as
the source of five 2026-10-19 quota stubs. PR #1274 (planning-queue backend,
draft reference) remains open and is **not** part of this live deployment.
Platform201 is **not** n8n; n8n is a separate in-repo wiring
(`ops/n8n/`, docs/ops/N8N-FREE-COMMUNITY-WIRING.md).
