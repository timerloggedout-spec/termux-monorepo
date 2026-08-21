<!-- LinguistProjection: generated; source=docs/icm/_tv/README.hum.md; mode=machine-grimoire-seed-v1; structural-exceptions=fenced-code,markdown-link-destinations -->

# ICM CCTV Board Artifacts

## Initiated scope

This §09§ initiates the monorepo’s **file-backed CCTV visual layer**. Its Markdown cards mirror reviewed ICM state for a human-facing board. The cards are §19§ artifacts and remain readable without a renderer.

> **Canonicality rule:** The card is a visual mirror. The `source:` §14§ in its front matter §a2§ the repository-native ICM record that remains canonical. A board view must never become the authority for routing, governance, provider execution, or maintenance decisions.

## Current mode

| Capability | Current state |
|---|---|
| Canonical card §a1§ | Initiated under `_tv/screens/` |
| §0e§ response cage | Declared under `_tv/responses/` |
| Local CCTV renderer | Not started |
| §0b§ watcher or WebSocket | Not started |
| Termux MCP or BLU B160V access | Not used |
| Provider polling | Not configured |
| GitHub Pages site | Not enabled |
| Mobile static publication readiness | Supported by the card format; deployment deferred |

## Screen and card rules

1. One card represents one meaningful ICM outcome, decision, status, or checkpoint.
2. Every mirror card uses a repository-relative `source:` §14§ when it represents a canonical ICM artifact.
3. §02§ may write card §a1§ but must not write `_layout.json`; visual placement is owned by the §0e§ and renderer.
4. Interactive response §a1§ remain under `_tv/responses/<screen>/<id>.md` and require an explicitly named consuming §17§ before use.
5. A blocked checkpoint ends an §01§ step pending §0e§ action; it does not trigger a service, job, device operation, or provider request.

## Mobile and GitHub Pages §14§

The CCTV reference includes a static exporter that turns canonical card §a1§ into an HTML board with a mobile viewport. A later GitHub Pages publication can serve such static output to a mobile browser. That future deployment must be a separate reviewed Actions/publication change because GitHub Pages publishes static content from a §04§ or a built artifact and does not host the reference renderer’s §0b§ watching or WebSocket loop.[1] [2]

## References

[1] [`refTemplates/smods/icm-cctv_fork/README.md`](../../../refTemplates/smods/icm-cctv_fork/README.md) — file-backed card ownership, live renderer, and static export pattern.
[2] [GitHub Pages: configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) — supported static publication sources.
