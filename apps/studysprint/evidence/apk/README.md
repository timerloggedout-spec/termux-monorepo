# APK evidence record (#4221)

The APK surface's release gates (APK.md) require demo/install
evidence in-tree. The device evidence itself lives beside this
record: `SMOKE.md` + the 01–07 captures (owner's device,
2026-11-03, landed by the D1 seat).

## apk-v0.1.0 — build + release record

- Build: CI run **41621272959** (`.github/workflows/
  studysprint-apk.yml`) — SUCCESS; artifact **13222824856**.
- Release asset: `studysprint.apk` attached to release
  **apk-v0.1.0** (id 432563137) by in-Actions run **41634663131**
  (the #4213 fix; the release previously carried 0 assets).
- Asset size: **33,887 bytes** — byte-identical in size to the
  CI artifact it was rebuilt from.
- Asset SHA-256:
  `3986aefc50abf71711805ffc83f64828eb3d0be489ce1db3cd9a9fd21abc8c9b`
  (computed from the released file itself).
- Contents (from the #4213 verification): `classes.dex` +
  bundled webApp (`assets/web/index.html`, `app.js`,
  `data/state.json`) inside the signed APK; signature verified
  by `apksigner verify` inside the build.

## Device smoke (2026-11-03) — PASS with one defect

`SMOKE.md` is the record: download + install + launch PASS;
all four views render their chrome and navigation works.
**Defect found**: the build-time state never loaded inside the
WebView ("Loading your course..." never resolved; footer
version blank) — `fetch("data/state.json")` does not complete
from a `file:///android_asset/` origin under the WebView's
file-origin rules, while the same bundle renders fully in
mobile Chrome.

**Fix (0.1.1, this patch line)**: the shell's WebViewClient
intercepts requests under its own `/android_asset/web/` path
and serves them from the APK assets with an
`Access-Control-Allow-Origin` header (`MainActivity.java`). A
fresh device smoke on the 0.1.1 build closes the defect; until
that smoke runs, the fix is verified by construction + tests,
not by device — stated plainly.

## Signing (0.1.1, #4222)

Signed with the committed project dev keystore
(`android/keystore/studysprint-dev.keystore`) — one stable
identity across build environments, so future builds install
as updates over one another. 0.1.0 itself was signed with a
per-environment generated key (the defect #4222 records); a
one-time reinstall may be required moving from 0.1.0 to 0.1.1.
