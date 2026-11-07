# Dashboard Preview QA Checklist

`[MUSEai]@{role:{web-design}}` — standing checklist ∀ help-wanted dashboard previews.
Evidence base: pr-2579 preview autopsy + rendered 390px pass (2026-10-31).
Claims carry refs; a check w/o evidence = NOT ESTABLISHED, never assumed ✓.

## 0. Precondition — dispatchability

- Preview workflow ∈ master (`help-wanted-dashboard-preview.yml` + `scripts/build_dashboard_manifest.py` resolvable @master). `workflow_dispatch` requires the workflow on the default branch ⇒ ∅ dispatch while its PR is open.
- ∅ manual/local publish as a substitute w/o recording it as such: a hand publish MUST be labelled manual in the landing commit + the source PR comment (pr-2579 lesson: landing `timerloggedout-spec.github.io@573d4d6b56c0`, author=owner, ∅ run — initially indistinguishable from a workflow publish).

## 1. Dispatch

- [ ] Dispatch w/ explicit `source_ref` ∧ `preview_key=pr-<n>`; record run id in the source PR.
- [ ] Record `source_sha` = head of `source_ref` at dispatch time (branch name alone drifts).

## 2. Landing verify

- [ ] Landing commit ∈ `timerloggedout-spec.github.io` main: author=`github-actions[bot]` ∧ msg = workflow template. Any other author/msg ⇒ manual publish, flag it.
- [ ] Pages build run on the landing sha = success.
- [ ] Served URL 200: `https://timerloggedout-spec.github.io/previews/<key>/help-wanted/`.

## 3. Tree completeness (partial-tree gate)

- [ ] Preview `version-manifest.json`: `source_sha` == dispatched sha; `version` prefix == workflow prefix; `content_sha256` ≠ null ∀ pages.
- [ ] `manifest.pages` set == source tree `apps/help-wanted-dashboard/*.html` set @`source_sha`. Subset ⇒ preview is PARTIAL: name the included pages + reason in the source PR, never present it as the full dashboard (pr-2579: 3 of ~23 pages {index, admin-graph, versioning}).
- [ ] Preview `sitemap.xml` URL set == manifest page set.
- [ ] Staleness: at QA time, `source_sha` vs current PR head — head moved ⇒ QA verdicts bind to `source_sha` only, say so.

## 4. Mobile pass (rendered, ¬ predicted)

Method of record: headless Chromium, viewport 390x844, DSF 2, touch, Android UA; screenshots top + full per page. DOM/CSS inference alone = PREDICTED, label it as such (PM pass 2026-10-31 = predicted; this lane's headless pass = rendered).

Per page, record:
- [ ] `scrollWidth == 390` (page h-scroll ∅); internal scrollers (`.table-wrap` etc.) listed w/ client/scroll widths.
- [ ] Nav: row count when wrapped; toggle present ∨ accepted wrap; height before hero.
- [ ] `docHeight` + per-region heights for stacked layouts (admin-graph @390: canvas 456px + asides 5,182/12,441px ⇒ 18,739px total = collapse-toggle defect, measured).
- [ ] Fixed bottom bars / mobile-only controls: rendered `display` + button count (admin-graph `.mobile-bar`: flex, 8 btns ✓).
- [ ] Canvas/graph pages: initial zoom % + legibility verdict from the screenshot, + recovery path (Fit/Focus/fullscreen) present.
- [ ] Touch targets ≥44px on primary controls.

## 5. Data + error states

- [ ] Live-data widgets show current data (feed timestamps recorded); ∅ hardcoded values.
- [ ] Error states render honestly (versioning: prod manifest 404 pre-bootstrap ⇒ "Comparison unavailable" = PASS as an error state; the comparison table itself stays BLOCKED until a production `version-manifest.json` exists).

## 6. Report

- [ ] Verdicts labelled RENDERED ∨ PREDICTED ∨ BLOCKED, each w/ its `source_sha`.
- [ ] Fix list split per owning lane: shell pages/CSS ⇒ web-design; feature pages ⇒ their PR lane.
- [ ] Still-owed list explicit: real-device (B160V) pass ≠ headless (PTR/scroll behaviour unproven headless); blocked items named w/ their unblocker.
