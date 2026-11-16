# fleet-apk

`[MUSEai]@{role:{apk-release}}`

Minimal native Android app for the fleet `.APK` release lane:
package `com.timerloggedout.fleet`, version in `VERSION` (semver; versionCode derived `major*10000+minor*100+patch`).

Built with Android SDK build-tools only (`aapt2`/`javac`/`d8`/`zipalign`/`apksigner`) — no Gradle, no AndroidX, no network dependencies.
Lane contract + recon: `docs/ops/APK-RELEASE-LANE.md`. Build: `scripts/apk/build_apk.sh`. Release: `.github/workflows/apk-release.yml` (tag `apk-v*` or dispatch).
