# Admin Graph — MOBILE 📱 FIRST

**Product priority: phone first. Desktop is the responsive enhancement.**

Admin Graph is a published surface inside the installable Tribute PWA. The canonical implementation remains apps/tribute-dashboard/admin-graph.html.

## Release and PWA ownership

- Public route: https://timerloggedout-spec.github.io/tribute/admin-graph.html
- Publisher: .github/workflows/tribute-dashboard-deploy.yml
- Application subtree: apps/tribute-dashboard/
- Existing publication lanes: Tribute GitHub Pages mirror and timerloggedout-spec.github.io user-site mirror.
- Install contract: apps/tribute-dashboard/manifest.webmanifest, sw.js, and install.js.
- Lane authority: docs/DEPLOYMENT-LANES.md for Vercel lanes and .github/workflows/tribute-dashboard-deploy.yml for the existing Tribute Pages/user-site publication path.

Admin Graph ships through its established Tribute publication path. Preserve the existing PWA identity, manifest scope, service worker, install flow, publisher concurrency, and route ownership. A new hosting project or parallel publisher requires an explicit lane proposal and an update to the owning deployment SSOT.

## Phone acceptance baseline

| Area | Required behavior |
|---|---|
| Viewports | 320–430 CSS px; portrait and landscape; viewport-fit=cover |
| Navigation | Thumb-reachable primary actions; fixed bottom action bar; safe-area padding |
| Touch | 44 CSS px minimum targets; visible pressed/focus states; zero hover-only workflows |
| Canvas | Touch pan, pinch/zoom, fit-to-view, node tap/selection, scroll containment |
| Search | Visible input, previous/next/clear buttons in the touch-visible canvas toolbar, on-screen keyboard support |
| Inspector | Single-column flow; readable fields; touch-sized editing and actions |
| Keyboard | Hardware shortcuts as optional accelerators; core workflows remain touch-operable |
| Accessibility | Accessible names, live search status, focus-visible treatment, reduced-motion support |
| Performance | Fast initial render and responsive interactions on real mobile hardware |
| Data integrity | Search and navigation remain view state; model, exports, and Δ diff stay canonical |

## Definition of done

1. Run tests/test_admin_graph_validation.py and the repository's required gates.
2. Validate the page at 320px, 375px, 390px, and 430px widths, in portrait and landscape.
3. Exercise search, match cycling, clear, node selection, group expansion, inspector editing, canvas controls, and every bottom-bar action using touch.
4. Exercise the on-screen keyboard and safe-area insets on Android Chrome and iOS Safari/PWA where available.
5. Verify the published route and source SHA through the existing Tribute publisher evidence.
6. Record browser/device evidence separately from source-level assertions.

## Regression ownership

- Repository policy: CLAUDE.md
- Visible project declaration: README.md
- Source-level regression: tests/test_admin_graph_validation.py
- PWA install wiring: tests/test_pwa_install.py
- Publisher: .github/workflows/tribute-dashboard-deploy.yml
