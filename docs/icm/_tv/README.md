# ICM CCTV Board Artifacts

## Initiated scope

This directory initiates the monorepo’s **file-backed CCTV visual layer**. Its Markdown cards mirror reviewed ICM state for a human-facing board. The cards are repository artifacts and remain readable without a renderer.

> **Canonicality rule:** The card is a visual mirror. The `source:` path in its front matter names the repository-native ICM record that remains canonical. A board view must never become the authority for routing, governance, provider execution, or maintenance decisions.

## Current mode

| Capability | Current state |
|---|---|
| Canonical card files | Initiated under `_tv/screens/` |
| Human response cage | Declared under `_tv/responses/` |
| Local CCTV renderer | Not started |
| File watcher or WebSocket | Not started |
| Termux MCP or BLU B160V access | Not used |
| Provider polling | Not configured |
| GitHub Pages site | Not enabled |
| Mobile static publication readiness | Supported by the card format; deployment deferred |

## Screen and card rules

1. One card represents one meaningful ICM outcome, decision, status, or checkpoint.
2. Every mirror card uses a repository-relative `source:` path when it represents a canonical ICM artifact.
3. Agents may write card files but must not write `_layout.json`; visual placement is owned by the human and renderer.
4. Interactive response files remain under `_tv/responses/<screen>/<id>.md` and require an explicitly named consuming process before use.
5. A blocked checkpoint ends an agent step pending human action; it does not trigger a service, job, device operation, or provider request.

## Mobile and GitHub Pages path

The CCTV reference includes a static exporter that turns canonical card files into an HTML board with a mobile viewport. A later GitHub Pages publication can serve such static output to a mobile browser. That future deployment must be a separate reviewed Actions/publication change because GitHub Pages publishes static content from a branch or a built artifact and does not host the reference renderer’s file watching or WebSocket loop.[1] [2]

## References

[1] [`refTemplates/smods/icm-cctv_fork/README.md`](../../../refTemplates/smods/icm-cctv_fork/README.md) — file-backed card ownership, live renderer, and static export pattern.
[2] [GitHub Pages: configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) — supported static publication sources.
