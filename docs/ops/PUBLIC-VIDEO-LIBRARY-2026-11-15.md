# Public video promotion and library — 2026-11-15

## Purpose

Make the already-published LoggedOut Timer YouTube content discoverable from the repository's public entry points. The YouTube uploads remain the source media; repository and site changes add navigation, context, and durable links.

## Canonical channel

- Channel: [LoggedOut Timer](https://www.youtube.com/@LoggedOutTimer-m9v)
- Latest update: [Releases are dropping soon. Find your place(s).](https://youtube.com/shorts/i0FusuYuRUs?is=ldjFTRznW8UjLRML)
- The latest update is an 8-second public Short published 2026-11-14. The upload has no description or caption track in the inspected metadata; copy must not imply unseen content.

## Curated public assets

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

View counts are intentionally omitted because they change and are not needed for discovery.

## Public placements

- Monorepo README: latest Short CTA and video-library link.
- Tribute dashboard: latest Short callout and Videos navigation link.
- GitHub Pages landing site: featured latest Short, Videos navigation link, and curated gallery.
- Text retrieval: `videos.md` mirrors the public gallery; the landing page links to `index.md`.
- Tribute Publishing view: [branch and PR reconciliation](https://timerloggedout-spec.github.io/tribute/publishing.html) links source divergence to the existing version-manifest and deployment-evidence surfaces.

## Publication and verification boundary

- YouTube media was already public before this repository work.
- Website PR #51 merged to `main` at `7b094e2d2fe8f203e5db3290360c1df885f331b7`; the gallery was fetched live at `https://timerloggedout-spec.github.io/videos.html` and returned the curated HTML and Markdown alternate.
- Monorepo PR #5456 merged to `master` at `dacd20c4c57c1e06c292de46674ec56e89498497`; README and Tribute source now contain the featured Short and Publishing reconciliation page.
- The existing `.github/workflows/tribute-dashboard-deploy.yml` is the canonical cross-repository publisher: it publishes the project hub to `gh-pages`, then mirrors the Tribute and Matrix subtrees into the user-site repository's `main` branch. The post-merge run is tracked at [workflow run 43720388998](https://github.com/timerloggedout-spec/termux-monorepo/actions/runs/43720388998); its Pages-enable job was still queued at the last inspection.
- The Tribute Publishing page is merged source but not yet live-verified; its public URL should not be described as deployed until that workflow completes and a fresh URL fetch succeeds.
- A branch or PR is not a publication. A merge, successful Pages deployment, and live URL verification are separate evidence steps.
- Keep this change scoped to repository and website promotion; do not upload, edit, pay-promote, or publish a YouTube Community post.
- Thumbnail links open YouTube; the gallery does not autoplay or embed multiple players.

## Reconciliation note

The earlier single-Short promotion branches were superseded by the curated gallery and consolidated monorepo PR. The website and monorepo publication changes are merged. Remaining work is deployment verification for the Tribute subtree; no unrelated branch was deleted or rewritten.
