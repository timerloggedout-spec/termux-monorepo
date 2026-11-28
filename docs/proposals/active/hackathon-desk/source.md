# Hackathon Desk — source and reconnaissance record

## User intent

Build one webpage where a hackathon teammate can discover opportunities, challenges, hackathons, teammates, proposals, and current pipeline state, with a User Guide and Accessibility support. The operator selected GitHub-authenticated contribution flow and full scope on 2026-11-24.

## Canonical source map

| Concern | Source of truth | Consumer contract |
|---|---|---|
| Ranked opportunities | ops/que/feeds/opportunity-priority.json | que.opportunity-priority/v1; generated timestamp and stale/fresh horizon are first-class |
| Challenge events, participants, gates | ops/challenge/coordinator.json | docs/ops/CHALLENGE-SCHEMA.md; challenge coordinator is the machine source of truth |
| Browser-safe challenge projection | scripts/dashboards/challenge_public_feed.py → apps/tribute-dashboard/data/challenge-public-feed.json | challenge-public-feed/v1 allowlist; browser never fetches the raw coordinator; nested internal-metric exclusion is tested |
| Dispatch pipeline state | ops/challenge/dispatch-state-feed.json → ops/que/feeds/que-queue-feed.json (`dispatch_claims`) → apps/tribute-dashboard/data/que-queue-feed.json | dispatch-state-feed/v1 folded into que-queue-feed/v1; Hackathon Desk uses the embedded display projection and omits ranking scores/components |
| Countdown instants and prize projection | apps/tribute-dashboard/data/challenge-countdowns-feed.json | docs/ops/CHALLENGE-COUNTDOWNS-FEED.md; browser derives countdown state from instants |
| Desk traversals | apps/tribute-dashboard/data/desk-feed.json and ops/challenge/desk-feed.json | Traversal evidence only; deprecated priority-timebox fields do not rank opportunities |
| Queue and dispatch | apps/tribute-dashboard/data/que-queue-feed.json and apps/tribute-dashboard/data/dispatch-state-feed.json | Existing queue and dispatch projections; read-only |
| Proposal lifecycle | docs/proposals/registry.yaml, docs/proposals/PROCESS.md, .github/ISSUE_TEMPLATE/proposal.yml | Existing proposal lifecycle and GitHub issue/PR actions |
| Dashboard styling and deployment | apps/tribute-dashboard/dashboard.css, current Tribute pages, dashboard deployment workflows | Existing shared design system and static deployment |

## ICM route

- Domain object: docs/icm/objects/operations/challenge-program.md.
- Change-control process: docs/icm/processes/change-and-validate.md.
- ICM map maintenance: docs/icm/maintenance/CLAUDE.md, with the human checkpoint at 02_design.
- Proposed process card: docs/icm/processes/hackathon-desk.md.
- Proposed links: ICM route table, process index, change-impact index, and Challenge and Certifications Program object.
- This proposal records the intended route. The durable ICM map remains unchanged until the operator reviews the exact map-change proposal.

## Existing surface constraints

- apps/tribute-dashboard/desk.html is a read-only projection; actions navigate to GitHub.
- apps/tribute-dashboard/admin.html contains internal-only challenge metrics.
- apps/tribute-dashboard/dashboard.css supplies the shared design system and visible focus styles.
- apps/tribute-dashboard/countdowns.html demonstrates the existing countdown contract and client-side time derivation.
- Tribute is a static dashboard surface; deployment and mirror freshness require live verification.

## Access model

The supplied Discord username is a contact reference only. The teammate links their GitHub account by choosing their GitHub profile and uses GitHub sign-in for repository actions. Repository membership and write permissions remain under GitHub administration. The portal explains read, triage, and write boundaries and routes access requests to the repository owner; it never grants access itself.

## Exclusions

- Custom OAuth server, token storage, or browser-side GitHub writes.
- New user database, invitation service, or permission engine.
- Parallel proposal, challenge, QUE, scheduler, or dispatch state.
- Admin-only challenge metrics and private operational telemetry.
- Publishing teammate contact details without opt-in.
- Changes to workflow YAML or repository administration.
