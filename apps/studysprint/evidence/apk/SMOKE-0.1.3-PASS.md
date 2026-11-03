# APK device smoke — 0.1.3: PASS (2026-11-03)

Owner device smoke of the 0.1.3 build (device-smoke build of record: run
41668240689, artifact 13245909653, 38,860B), screen-recorded by the owner as
tester. This is the deciding leg of the rebound #4276 acceptance
(0.1.3 = emulator gate formal PASS, attempt 4 run 41670971342, ∧ this device PASS).

- Recording: `screen-20261103-081744.mp4` (720×1612, 129.9s, recorded 2026-11-03 ~08:15–08:18 PT)
  Drive original: https://drive.google.com/file/d/1JguswyD-mPmY3Sq44LjOJkROG1hOVhCG/view
- Verdict: **PASS** — frame-read firsthand (contribution desk):
  · t=8s: Today populated from the bundled state — "BIO 101 — Intro Biology
    (sample, synthetic)" · "Today (day 1): 2 session(s). First up: learn —
    cell structure (45 min)" · check-in controls live · a sprint started
    in-session. No "Loading your course…" anywhere in the sampled frames.
  · t=90s: SR Review live — FSRS scheduler selector · "All caught up — next
    card due 2026-11-04" · a grading receipt rendered (scheduler=sm2 grade=3)
    · footer reads "StudySprint webApp — surface version 0.1.3" (populated).
- Frames (header-cropped 64px per the standing privacy rule, 720×1548):
  `device-smoke-0.1.3-pass-01.jpg` (t=8s, Today) · `-02` (t=45s) · `-03`
  (t=90s, SR Review + 0.1.3 footer) · `-04` (t=125s)
- Consequence: #4276 acceptance closes (both legs). The apk-v0.1.3
  release-of-record cut executes via the release-cut automation; the
  submission packet's working-APK claim restores under its stated condition.
