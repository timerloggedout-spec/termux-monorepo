# Review publishing — workflow route of record

Owner directives (2026-11-26 PT): "FAIL if not gh pages published!", "WorkFlows publish.", "Dispatch templates trigger our QUE QDesk Build & publish; ensure the WorkFlow publishing is documented + updated."

## Rule

- Review surfaces publish to GitHub Pages **through repo workflows only**.
- Route review previews through GitHub Pages only. Vercel previews are rate-limited, and an upgrade is money (Owner-only).
- **Publish to `gh-pages` through workflows only; skip hand commits.** `tribute-dashboard-deploy.yml` (`publish-gh-pages`, peaceiris) rewrites the branch, and hand-added paths 404 after the next deploy (observed 2026-11-26 08:34 PT on `hackathon-desk/`).
- Previews land on the **user site** `timerloggedout-spec/timerloggedout-spec.github.io` (branch `main`) under `previews/<key>/…` with `keep_files: true`, so they persist across deploys.

## Route: filing ⇒ build ⇒ publish

1. **Filing = dispatch.** File through an issue template that carries a `SWARM-DISPATCH` block (`issue-dispatch/v1`), e.g. `project-task.yml`. Contract: [ISSUE-TEMPLATE-DISPATCH.md](ISSUE-TEMPLATE-DISPATCH.md).
2. **QUE admission.** `swarm-admission.yml` stamps ADMITTED/DEFERRED and labels `swarm-admitted` or `deferred-by-tier`.
3. **Route.** `project-task-dispatch.yml` validates intake (`dispatch-queued` / `intake-incomplete`). The QDesk claim fires `build-dispatch.yml`, which posts a receipt and opens a PR against master.
4. **Publish.** A per-surface workflow renders and publishes with peaceiris `keep_files: true` to the user site:

| Surface | Workflow | Preview URL |
|---|---|---|
| Tribute | `tribute-dashboard-preview.yml` (`source_ref`, `preview_key`) | `/previews/<key>/tribute/` |
| Teammate Portal (hackathon-desk) reference + status | `teammate-portal-status-publish.yml` (dispatch, master push on proposal docs, `:17`/`:47` cron) | `/previews/pr-5840/hackathon-desk/` |

## Teammate Portal status page

- Kept as the **reference ∧ done-board** for the Teammate Portal (Owner, 2026-11-26 09:14 PT).
- Source of truth for state: `docs/proposals/active/hackathon-desk/ITEMS.md` (the `State` column). Mark an item done in ITEMS.md in the PR that implements it (`Implements: HD-<n>`). The page re-renders on master push and every 30 min.
- It also lists dispatch issues labeled `teammate-portal` and PR #5840 state.
- Teammate Portal = opportunities ∧ challenges ∧ hackathons. It is a standalone surface; `apps/tribute-dashboard` (Tribute) is out of scope.

## Monitoring

Check routing on the filing: the admission stamp, then the intake receipt, then the build receipt and PR, then the publish run. A `deferred-by-tier` filing waits for the QUE drain; it stays queued as an issue.
