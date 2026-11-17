# Public video promotion and library — 2026-11-17

## Purpose

Make the already-published LoggedOut Timer YouTube content discoverable from the repository's public entry points. YouTube remains the source for the existing channel uploads. New operational walkthroughs may be hosted on Cloudinary and embedded directly in the gallery; repository and site changes add navigation, context, and durable links.

## Canonical channel

- Channel: [LoggedOut Timer](https://www.youtube.com/@LoggedOutTimer-m9v)
- Latest update: [Releases are dropping soon. Find your place(s).](https://youtube.com/shorts/i0FusuYuRUs?is=ldjFTRznW8UjLRML)
- The latest update is an 8-second public Short published 2026-11-14. The upload has no description or caption track in the inspected metadata; copy must not imply unseen content.

## Curated public assets (14 selected videos)

| Group | Video | Duration | Published | Purpose |
|---|---|---:|---|---|
| Latest | [Releases are dropping soon. Find your place(s).](https://youtube.com/shorts/i0FusuYuRUs?is=ldjFTRznW8UjLRML) | 0:08 | 2026-11-14 | Current channel update |
| Termux | [timerloggedout-spec termux-monorepo](https://www.youtube.com/shorts/DNREnvgjIv0) | 0:08 | 2026-11-15 | Repository teaser |
| Termux | [Termux MonoRepo timerloggedout-spec](https://www.youtube.com/shorts/VkjO57haraQ) | 0:10 | 2026-11-15 | Repository teaser |
| Termux | [GitHub · termux-monorepo](https://www.youtube.com/shorts/4Qf0OAq4d7c) | 0:08 | 2026-11-15 | Repository discovery |
| Site | [GitHub Pages + termux-monorepo](https://www.youtube.com/shorts/ixpUUm4pkdQ) | 0:08 | 2026-11-14 | Connects site and source |
| StudySprint | [0.5.1 narrated demo](https://www.youtube.com/watch?v=gUC3RqTZXCQ) | 1:24 | 2026-11-04 | Current product walkthrough |
| StudySprint | [0.5.1 current-surface evidence reel](https://www.youtube.com/watch?v=-CNherwZM-o) | 1:44 | 2026-11-04 | Android, web and TUI evidence |
| Quarantine Browser Clerk | [Browser-agent demo](https://www.youtube.com/watch?v=z-hkwnUFOqM) | 2:23 | 2026-11-04 | Product/security demo |
| Archive | [StudySprint v0.4.0 demo](https://www.youtube.com/watch?v=WK9LMwpvHUk) | 2:55 | 2026-11-03 | Earlier release; superseded by 0.5.1 demos |
| Delphi Oracle | [Evidence Over Claims v1.0.0 walkthrough](https://www.youtube.com/watch?v=AZSeqOI5H9M) | 1:48 | 2026-11-03 | Evidence-gate oracle walkthrough |
| StudySprint | [Strands Agents SDK demo](https://www.youtube.com/watch?v=N3HBRV4LOGQ) | 1:10 | 2026-11-01 | Earlier architecture walkthrough |
| Archive | [StudySprint v0.3.0 demo](https://www.youtube.com/watch?v=AKCqOCXAFu0) | 2:34 | 2026-11-03 | Earlier release |
| Archive | [StudySprint v0.2.0 demo](https://www.youtube.com/watch?v=eFXyOYTpuvg) | 1:40 | 2026-11-01 | Earlier release |\n| Operations | [Admin Interaction Graph — live runtime walkthrough](https://res.cloudinary.com/cc4wyoa6/video/upload/v1794874227/loggedout-timer/product-demos/admin-graph-live-runtime-walkthrough.mp4) | 2:21 | 2026-11-17 | Narrated implementation preview: workflow/job events, validation, D1, live graph pulses and health |

View counts are intentionally omitted because they change and are not needed for discovery.

## Public placements

- Monorepo README: latest Short CTA and video-library link.
- Tribute dashboard: latest Short callout and Videos navigation link.
- GitHub Pages landing site: featured latest Short, Videos navigation link, and curated gallery, including the inline Admin Graph walkthrough.
- Text retrieval: `videos.md` mirrors the public gallery; the landing page links to `index.md`.
- Tribute Publishing view: [branch and PR reconciliation](https://timerloggedout-spec.github.io/tribute/publishing.html) links source divergence to the existing version-manifest and deployment-evidence surfaces.

## Publication and verification boundary

- YouTube media was already public before this repository work.
- Website PR #51 merged to `main` at `7b094e2d2fe8f203e5db3290360c1df885f331b7`; the gallery was fetched live at `https://timerloggedout-spec.github.io/videos.html` and returned the curated HTML and Markdown alternate.
- The gallery was then expanded from 9 to 13 selected videos (adding Delphi Oracle v1.0.0, the StudySprint Strands SDK demo, and v0.3.0/v0.2.0 release history). Source is merged on website `main` at `47e63f33f80a8a51191ac00339b1df32337774a3` (13-ID HTML/Markdown gallery, homepage feature cards, and navigation guard). Its Pages build is queued, and the latest live fetch still showed the prior 9-video deployment at the last check.
- Monorepo PR #5456 merged to `master` at `dacd20c4c57c1e06c292de46674ec56e89498497`; README and Tribute source now contain the featured Short and Publishing reconciliation page.
- The existing `.github/workflows/tribute-dashboard-deploy.yml` is the canonical cross-repository publisher: it publishes the project hub to `gh-pages`, then mirrors the Tribute and Matrix subtrees into the user-site repository's `main` branch. It now uses concurrency group `tribute-dashboard-publish` with `cancel-in-progress: false`, allowing an active publication to finish while newer pending snapshots supersede older pending ones. Publisher run [43720388998](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43720388998) has now completed successfully, including `publish-gh-pages`, the user-site mirror, pruning, and fast-forward of the legacy Pages source branch. Website `main` and `main-landing-studysprint-link` now match at `109e80fabae0e130c9e40c63347a96b355675397`; the 13-video gallery and homepage feature cards are present on the actual Pages source branch. The resulting website Pages run [43721574521](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/actions/runs/43721574521) is queued before its build job. Latest current-source publisher [43721531226](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43721531226) is pending behind the serialized publisher queue; it will update the Tribute subtree with the newer workflow-evidence and Pages-source-alignment panels.
- The Tribute Publishing page is merged source but not yet live-verified; its public URL should not be described as deployed until that workflow completes and a fresh URL fetch succeeds.
- The GitHub Pages legacy source branch `main-landing-studysprint-link` was 10 commits behind website `main` (0 ahead) at the earlier comparison. The canonical publisher's `Fast-forward legacy user-site Pages source branch` step has now succeeded; the two branches compare as identical at `07e5352d98ea8c548866d6488965283ef36083ac`. The subsequent Pages deployment run is [43721574521](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/actions/runs/43721574521), currently queued; the live URL still requires a fresh post-deploy check.
- A branch or PR is not a publication. A merge, successful Pages deployment, and live URL verification are separate evidence steps.
- Keep this change scoped to repository and website promotion; do not upload, edit, pay-promote, or publish YouTube media or a YouTube Community post.
- Existing YouTube thumbnails open YouTube. The gallery embeds only the Admin Graph walkthrough inline; no autoplay or multiple players are used.

## Reconciliation note

The earlier single-Short promotion branches were superseded by the curated gallery and consolidated monorepo PR. The website and monorepo publication changes are merged. Remaining work is deployment verification for the Tribute subtree; no unrelated branch was deleted or rewritten.


## Latest operational walkthrough update — 2026-11-17

- The Admin Interaction Graph walkthrough was created as a 140.6-second narrated motion-graphics explainer (1280×720, H.264 video, AAC audio) and uploaded as a public Cloudinary video asset: [MP4](https://res.cloudinary.com/cc4wyoa6/video/upload/v1794874227/loggedout-timer/product-demos/admin-graph-live-runtime-walkthrough.mp4).
- The published Descript review/share page is [available here](https://share.descript.com/view/VBqxWH42Wpy); the editable project is [available here](https://web.descript.com/c1967942-652a-4de5-9f7f-f417cead7ba7/853db).
- Website PR [#52](https://github.com/timerloggedout-spec/timerloggedout-spec.github.io/pull/52) merged to `main` at `3c521cc3fe923b9c8092275f7bc1925cc03e4efc`. Both `main` and `main-landing-studysprint-link` now point to the same commit; the legacy Pages source was advanced with a non-force fast-forward.
- A fresh page scrape of [videos.html](https://timerloggedout-spec.github.io/videos.html) confirmed the deployed gallery contains the inline Cloudinary MP4 player, the implementation-preview description and the published video link. The `videos.md` mirror is also present on the Pages source branch.
- The video is explicitly an implementation preview, not a production screen recording. It covers the GitHub Actions workflow/job lifecycle, scheduled workflow reconciliation, metadata-only event normalization, GitHub API verification, Cloudflare Worker/D1 ingestion and deduplication, dashboard polling and pulses, health reporting, and the activation boundary. Production activation of the runtime implementation still depends on PR #5538 merging and subsequent live-event verification.
