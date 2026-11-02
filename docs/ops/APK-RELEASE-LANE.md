# APK Release Lane — fleet .APK distribution

`[MUSEai]@{role:{apk-release}}` · born 2026-10-31 (recon @master same day) · distributions of the monorepo fleet as installable Android packages.

## Recon findings (2026-10-31, firsthand via PAT API)

- **GitHub Releases ∅ · tags ∅ · native Android app ∅** (code search ∀ `.kt`/`gradle`/`AndroidManifest.xml`/capacitor = 0; `apps/` = 9 web/Python surfaces; "iDEAL" hits = word-only). Sole APK-touching workflow = `apk-xref-intake.yml` (reverse-engineering xref, ≠ release).
- Actions secret names (62): ∅ `ANDROID_*`/`KEYSTORE*`/`APK_*` ⇒ signing custody = greenfield.
- ⇒ This lane is a **greenfield build**, not a repair.

## Surface

| Piece | Path | Note |
|---|---|---|
| App (master baseline / comparison Arm M) | `apps/fleet-apk/` | pkg `com.timerloggedout.fleet`; `VERSION` file = version source of truth; `src/android/FleetActivity.java` + `src/android/AndroidManifest.xml` (minSdk 24 / targetSdk 34) |
| Build | `scripts/apk/build_apk.sh` | SDK build-tools direct: `aapt2 compile+link → javac → d8 → zipalign → apksigner sign/verify` + SHA256SUMS; ∅ Gradle, ∅ network fetches |
| Workflow | `.github/workflows/apk-release.yml` | trigger tag `apk-v*` ∨ `workflow_dispatch`; `permissions.contents: write` only |
| Tests | `tests/test_apk_lane.py` | manifest/version coherence, workflow trigger + custody hygiene |

## Signing custody (names ONLY — values never in repo/chat)

Production signing activates iff these Actions secret **names** exist (owner provisioning): `ANDROID_KEYSTORE_BASE64` · `ANDROID_KEYSTORE_PASSWORD` · `ANDROID_KEY_ALIAS` · `ANDROID_KEY_PASSWORD`.

∅ provisioned ⇒ workflow fail-softs to an **in-runner ephemeral debug keystore** and stamps `SIGNING_MODE=ephemeral-debug` into release notes + artifact `SIGNING_MODE` file. Ephemeral releases are installable proof artifacts, explicitly **not** production-signed.

## Release flow

1. Tag `apk-v<semver>` (or dispatch with optional semver override; default = `VERSION`).
2. Workflow builds+signs+verifies, uploads workflow artifact (backup surface), creates GitHub Release `fleet-<semver>.apk` + `SHA256SUMS`.
3. Verify: re-download release asset ∧ `sha256sum -c SHA256SUMS`.

Token class (amended 2026-11-02): job declares `contents: write`, but in-runner `GITHUB_TOKEN` received HTTP 403 `Resource not accessible by integration` on `POST /releases` for non-master refs (arm-A proof runs 41422144649 + tag run 41422211229; build/sign/verify steps succeeded, artifact uploaded) ⇒ the release step alone uses the provisioned `OPERATOR_GITHUB_TOKEN` secret (PAT-class, name verified in the live secrets census) as an interim. End-state remains the Termux Fleet ApkRelease AppID migration (contents:write app token, QUEUED with AppID lane 7075f9c0).

First proven release: **apk-v0.1.0** (dispatch run 41272927031, 2026-11-01) — `fleet-0.1.0.apk` 8619B, checksum re-download ✓, signing ephemeral-debug disclosed.

Accuracy note (2026-11-02): the first publication attempt of this amendment (branch apk-release/token-class-fix, PR snapshots read as #3722/#3723) landed 0-byte file contents via the contents-API write path ⊕ was merged only in incoherent API snapshots, never in landed content — master-history content reads are the oracle; this v2 republication is content-verified blob-by-blob.

## Parallel-versioning DoE

`experiments/doe/apk-1-parallel-versioning/` — same micro-spec (runtime version display) built by provider dispatch routes (Jules/Gemini/DeepSeek) vs this lane's Muse v0.1.0 as baseline Arm M; evaluator (≠ builders) selects on committed records.
