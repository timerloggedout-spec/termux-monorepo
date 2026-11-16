# APK 0.1.0 — device install smoke (owner's device, 2026-11-03 ~04:36 PT)

Provenance: owner's device controller, screenshots captured during the
install smoke of the CI-built `studysprint.apk` (33.89 kB, per
01-download.jpg). Source files arrived .png-named but are JPEG bytes
(720x1612) — stored as .jpg, bytes untouched.

## PASS
- Download of the CI artifact (run 41621272959) · install completes
  (02-installing.jpg) · app launches in its WebView shell · all four
  views render their chrome and navigation works (Today · Plan /
  Receipt · Reader · SR Review).

## DEFECT (fix task filed from this smoke)
The build-time state never loads inside the WebView:
- "Loading your course..." never resolves (all views).
- Today shows no sessions; Plan shows the receipt heading with an
  empty receipt; SR Review shows no card.
- Footer reads "surface version ." — the version string is blank.
The same web bundle in mobile Chrome renders fully (see
evidence/web/device-today.jpg, 2026-11-03 02:50 PT), so the defect is
specific to the WebView asset/data path (state fetch from data/state.json
does not complete under the WebView's file-origin rules), not the core
or the bundle's logic. Fix + a fresh device smoke close this pack.
