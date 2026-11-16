#!/usr/bin/env bash
# [MUSEai]@{role:{apk-release}} :: SDK-direct .APK build (∅ Gradle, ∅ network)
# In : VERSION (arg1 ∨ env VERSION ∨ apps/fleet-apk/VERSION), KEYSTORE_FILE/KEYSTORE_PASS/KEY_ALIAS/KEY_PASS (env, optional)
# Out: dist/fleet-<version>.apk (signed+verified) ∧ dist/SHA256SUMS ∧ env SIGNING_MODE ∈ {release-keystore, ephemeral-debug}
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
APP="$ROOT/apps/fleet-apk"
VERSION="${1:-${VERSION:-$(tr -d '[:space:]' < "$APP/VERSION")}}"
IFS='.' read -r MAJ MIN PAT <<< "$VERSION"
VERSION_CODE=$(( MAJ * 10000 + MIN * 100 + PAT ))

SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/local/lib/android/sdk}}"
BT="$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)"
ANDROID_JAR="$(ls "$SDK"/platforms/android-*/android.jar | sort -V | tail -1)"
echo "sdk=$SDK build-tools=$BT platform=$ANDROID_JAR version=$VERSION code=$VERSION_CODE"

WORK="$ROOT/build/apk-work"; DIST="$ROOT/dist"
rm -rf "$WORK"; mkdir -p "$WORK/classes" "$WORK/dex" "$DIST"

# Signing material: caller-provided keystore wins; else ephemeral debug keystore generated in-runner (∅ commit, ∅ custody claim)
if [ -n "${KEYSTORE_FILE:-}" ] && [ -f "$KEYSTORE_FILE" ]; then
  KS="$KEYSTORE_FILE"; KS_PASS="${KEYSTORE_PASS:-}"; ALIAS="${KEY_ALIAS:-}"; K_PASS="${KEY_PASS:-$KS_PASS}"
  SIGNING_MODE="release-keystore"
else
  KS="$WORK/debug.keystore"; KS_PASS="android"; ALIAS="androiddebugkey"; K_PASS="android"
  keytool -genkeypair -keystore "$KS" -storepass "$KS_PASS" -keypass "$K_PASS" -alias "$ALIAS" \
    -keyalg RSA -keysize 2048 -validity 10950 -dname "CN=Fleet APK Ephemeral Debug,O=timerloggedout-spec" >/dev/null 2>&1
  SIGNING_MODE="ephemeral-debug"
fi
echo "SIGNING_MODE=$SIGNING_MODE" | tee "$DIST/SIGNING_MODE"
[ -n "${GITHUB_ENV:-}" ] && echo "SIGNING_MODE=$SIGNING_MODE" >> "$GITHUB_ENV"

"$BT/aapt2" link -o "$WORK/base.apk" -I "$ANDROID_JAR" --manifest "$APP/AndroidManifest.xml" \
  --min-sdk-version 26 --target-sdk-version 34 --version-code "$VERSION_CODE" --version-name "$VERSION"
javac -source 8 -target 8 -classpath "$ANDROID_JAR" -d "$WORK/classes" $(find "$APP/src" -name '*.java')
"$BT/d8" --lib "$ANDROID_JAR" --min-api 26 --output "$WORK/dex" $(find "$WORK/classes" -name '*.class')
cp "$WORK/base.apk" "$WORK/unsigned.apk"
( cd "$WORK/dex" && zip -q "$WORK/unsigned.apk" classes.dex )
"$BT/zipalign" -f -p 4 "$WORK/unsigned.apk" "$WORK/aligned.apk"
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$KS_PASS" --key-pass "pass:$K_PASS" --ks-key-alias "$ALIAS" \
  --out "$DIST/fleet-$VERSION.apk" "$WORK/aligned.apk"
"$BT/apksigner" verify --verbose --print-certs "$DIST/fleet-$VERSION.apk"
( cd "$DIST" && sha256sum "fleet-$VERSION.apk" > SHA256SUMS && cat SHA256SUMS )
ls -l "$DIST"
