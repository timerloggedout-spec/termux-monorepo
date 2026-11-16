# The StudySprint signing key — collaborators, read this first

This directory holds the project's shared signing key:

- **File:** `studysprint-dev.keystore` (in this directory)
- **Alias:** `studysprint`
- **Password:** `android` (also printed in `android/build.sh`)
- **Certificate SHA-256:**
  `74623c3e84997c495c9aa2bb46891dfd4b3308b7614ac28cb438ff590caf908b`

## What this key is

A **DEV key, shared on purpose** (owner ruling, 2026-11-03). It is the
project's signing identity for sideload-distributed builds — it is not a
store key, it protects no secrets, and its being public in this repo is
deliberate. What it protects is **update continuity**: Android only
installs an update over an existing install when both are signed with
the same key.

> ⚠ **Scope warning:** this is a DEV key for sideload distribution only.
> Never use it as a store or production key. If the distribution model
> ever changes, a store/production release gets its own key and its own
> ruling — this key does not carry over.

## Build + sign

Requirements: JDK 17, the Android SDK (platform android-34,
build-tools 34.0.0), and python3. From the app root:

```bash
bash android/build.sh
```

The script changes into its own directory, regenerates the core state
the bundle carries, builds SDK-direct (aapt2 → javac → d8 → zipalign),
then signs with **this** keystore via `apksigner` and verifies the
signature. CI runs the same script (the `studysprint-apk` workflow), so
local and CI builds sign identically. There is no separate signing
step, and never a reason to sign by hand — if `build.sh` stops because
the keystore is missing, that is a stop, not a prompt to substitute
another key.

## The one rule

**All builds sign with this key.** If you build the APK any other way
(an ephemeral CI key, a key you generated locally), the resulting APK
will not install over anyone's existing copy — the update path breaks
silently for every installed device.

## Rotation (deliberate, breaking)

Rotating the key means every existing install must be **uninstalled
first** and reinstalled — in-place updates across a key change are
impossible by Android's design, and a changed signature with the same
versionCode is refused outright. Rotate only as a single announced
change that:

1. swaps this keystore file,
2. **bumps `android:versionCode` in `android/AndroidManifest.xml`** (and
   the versionName per the release), so the new-key builds are ordered
   after every old-key build,
3. updates this note **and** the signing section in `APK.md` (path,
   alias, password, and the new certificate fingerprint),
4. is announced as a breaking change for installed copies, with the
   uninstall-first instruction stated in the announcement.
