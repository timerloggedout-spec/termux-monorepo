# APK device smoke — 0.1.1: FAIL (2026-11-03)

Owner device smoke of the 0.1.1 build (CI run 41645713037, artifact 13234982037,
APK 38,057B, signer cert 74623c3e…908b), screen-recorded by the owner as tester.

- Recording: `screen-20261103-073809.mp4` (720×1612, 101.5s, recorded 2026-11-03 07:36–07:38 PT)
  Drive original: https://drive.google.com/file/d/1qs60y3ldCaFm-F_hLHncaErBrRMec3RE/view
- Verdict: **FAIL** — #4276 reproduces on real-device WebViews.
  Frame-read firsthand (D1 seat + contribution desk): "Loading your course…"
  persists from the first frame to the last · footer reads "surface version ."
  (version BLANK) · Today and SR views empty — the bundled course state
  (data/state.json) never loads. The app shell and the Ingest file picker do
  respond (a syllabus file parses in-session); the state fetch is the dead leg.
- Frames (header-cropped 64px per the standing privacy rule, 720×1548):
  `device-smoke-0.1.1-fail-01.jpg` (t=5s) · `-02` (t=50s, Ingest view, blank-version footer) · `-03` (t=95s)
- Consequence: no 0.1.1 release-of-record swap. The fix is #4412
  (WebViewAssetLoader https-origin serving → surfaces 0.1.3, PR #4423);
  #4276 acceptance rebinds to 0.1.3 = emulator gate green on the new head
  ∧ a fresh owner device smoke PASS.
