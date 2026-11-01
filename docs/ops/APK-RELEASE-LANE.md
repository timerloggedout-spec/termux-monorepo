# APK Release Lane

`[MUSEai]@{role:{apk-release}}` — fleet `.APK` build → sign → GitHub Release lane. Repo-automation only (VM = sandbox law): all building/signing/releasing runs in `.github/workflows/apk-release.yml` on GitHub runners.

## Recon @master (2026-10-31, PAT API firsthand)

| Surface | State |
|---|---|
| Releases | ∅ (`GET /releases` = `[]`) |
| Tags | ∅ (`GET /tags` = `[]`) |
| Workflows | ~230; APK-adjacent = only `apk-xref-intake.yml` (RE cross-reference of *external* APKs, `ops/web_adapter_foundry/apk_xref.py`) — ∅ build/release/sign workflow |
| App sources | `apps/` = 9 web/python surfaces (`studysprint` = Python, `help-wanted-dashboard` = static HTML, …); ∅ `build.gradle`/`settings.gradle`/`AndroidManifest.xml`/`.kt`/`capacitor` anywhere (code-search totals 0) — ∅ native Android app existed |
| `iDEAL` | ∅ app by that name; search hits = the word "ideal" in docs only |
| Signing assets | Actions secrets = 62 names (live list 2026-10-31); ∅ Android/keystore name among them (`ANDROID_*`, `*KEYSTORE*`, `APK_*` all absent) — names only, values never read |

Verdict: greenfield lane. First artifact = new minimal native app `apps/fleet-apk/` (package `com.timerloggedout.fleet`), not a wrapper of an existing app.

## Design

- **Build**: `scripts/apk/build_apk.sh` — Android SDK build-tools direct (`aapt2 link` → `javac` → `d8` → `zipalign` → `apksigner sign`+`verify`), preinstalled on `ubuntu-latest`. ∅ Gradle, ∅ AndroidX, ∅ network fetches ⇒ deterministic + fast. Programmatic UI only (∅ `R`/resources).
- **Versioning**: `apps/fleet-apk/VERSION` semver; versionCode = `major*10000+minor*100+patch`. Tag form `apk-v<semver>`.
- **Trigger**: push tag `apk-v*` ∨ `workflow_dispatch` (optional version override; prerelease default `true` on dispatch).
- **Signing custody**: keystore lives only as Actions secrets, referenced by NAME: `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`. When present ⇒ `SIGNING_MODE=release-keystore`. When absent ⇒ fail-soft: in-runner **ephemeral** debug keystore (generated per-run, never committed), `SIGNING_MODE=ephemeral-debug`, disclosed in the Release notes + `dist/SIGNING_MODE`. An ephemeral-signed artifact is installable proof, **not** production signing.
- **Owner provisioning item** (only step that upgrades proof → production): provision the 4 `ANDROID_KEYSTORE_*` secret names above with a real release keystore. ∅ values in chat/files/commits, ever.
- **Release**: `gh release create apk-v<version>` with `fleet-<version>.apk` + `SHA256SUMS`; job token `contents: write` only; workflow artifact uploaded as backup surface.

## Web presence tie-in

Install/download surface = the GitHub Release page (`/releases/tag/apk-v<version>`) until Web Design PM (`f2acba6f`) links it from the fleet web surfaces — coordination routes via main, per tasking; this lane publishes the stable Release URL only.

## Proof

First end-to-end run + Release URL are recorded in the landing PR / lane report to main; verify any release with `apksigner verify` + `sha256sum -c SHA256SUMS` against the downloaded artifact.
