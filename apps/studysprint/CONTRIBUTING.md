# Contributing to StudySprint

## Building the APK — signing (read this first)

Every APK build signs with the project's committed DEV keystore:

- **Key:** `android/keystore/studysprint-dev.keystore` — it is in this
  tree; build with the key that is here, never a substitute.
- **Alias:** `studysprint` · **Password:** `android`
- **Build + sign:** `bash android/build.sh` (JDK 17 + Android SDK
  platform android-34 / build-tools 34.0.0 + python3). The script
  builds and signs in one pass and fails loudly if the keystore is
  missing — treat that as a stop.

**The one rule: all builds sign with this key.** Android refuses an
update signed by a different key over an existing install, so a build
signed any other way silently breaks updates for every installed copy.

**Scope:** this is a DEV key for sideload distribution only — never a
store or production key.

Full details (certificate fingerprint, rotation procedure):
[APK.md](APK.md), "Signing — the project key", and the note beside the
key at `android/keystore/README.md`.
