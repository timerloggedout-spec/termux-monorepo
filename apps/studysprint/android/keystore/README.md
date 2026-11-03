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

## The one rule

**All builds sign with this key.** If you build the APK any other way
(an ephemeral CI key, a key you generated locally), the resulting APK
will not install over anyone's existing copy — the update path breaks
silently for every installed device. `android/build.sh` fails loudly
when this keystore is missing; treat that as a stop, never as a prompt
to substitute another key.

## Scope

DEV / sideload only. StudySprint is distributed as a direct APK
download; it never ships through Google Play, holds no secrets, and
stores no credentials. If that distribution model ever changes, this
key does **not** carry over — a store release gets its own key and its
own ruling.

## Rotation (deliberate, breaking)

Rotating the key means every existing install must be uninstalled and
reinstalled — in-place updates across a key change are impossible by
Android's design. Rotate only as a single announced change that:

1. swaps this keystore file,
2. updates this note **and** the signing section in `APK.md` (path,
   alias, password, and the new certificate fingerprint), and
3. is announced as a breaking change for installed copies.
