---
type: object
cluster: platform
universe: live
status: initiated
entity: ops/github-apps/PROCESS.json
verified_at: 2026-11-01
---

# GitHub App Fleet

The **GitHub App Fleet** is the repository's set of specialist GitHub App identities. Each app is a scoped fleet actor with its own installation token bucket and permission set, so workflow and review actions are authored by the responsible identity instead of a shared token. Provisioning, custody, and the allocation queue are owned by the AppID process lane; this card routes to its records.

## Shape

- **Record of record:** `ops/github-apps/PROCESS.json` with its companion `docs/ops/GITHUB-APP-PROCESS.md` (custody, permissions ladder, distribution audit, capacity census, allocation queue). Where a roster file disagrees with PROCESS.json, PROCESS.json wins.
- **Live slate (8 apps):** Collector `5535733` · Publisher `5537873` · Reviewer `5539430` · Gate `5539499` · Lifecycle `5539639` · Swarm `5560920` · CrossReference `5564430` · RepoStory `5565297` (installed on the `repo-story` entry repo only).
- **Telemetry:** `docs/ops/GITHUB-APP-FLEET-TELEMETRY.md`; observations land in `ops/github-apps/observations/` and are collected under the Collector identity.
- **Custody boundary:** private keys live in per-app local connector custody (0600). Repository records carry names and IDs only — never key material.

## Read when

- Identifying which fleet actor authored or should author an action (checks, reviews, merges, lifecycle sweeps, swarm runs).
- Checking an app's permission scope, install scope, or provisioning state before relying on its actions.

## Connected to

- **owned-by:** the AppID process lane and its PROCESS records.
- **joins:** Change Control (who may merge), Provider Routing Governance (actor identities vs provider peers — different registries, do not conflate), and the Repo Organization tree lanes that act through these identities.
- **looks-like-but-is-not:** the Android `apps/fleet-apk` project, or a generic GitHub App tutorial surface.

## See

- Process record: [`docs/ops/GITHUB-APP-PROCESS.md`](../../../../docs/ops/GITHUB-APP-PROCESS.md)
- Telemetry: [`docs/ops/GITHUB-APP-FLEET-TELEMETRY.md`](../../../../docs/ops/GITHUB-APP-FLEET-TELEMETRY.md)
- Monikers: [`docs/ops/AGENT-MONIKERS.md`](../../../../docs/ops/AGENT-MONIKERS.md)
