#!/usr/bin/env bash
# StudySprint APK — SDK-direct build (no Gradle), mirroring the
# fleet-apk pipeline: aapt2 link -> javac -> d8 -> zipalign ->
# apksigner. Requires: JDK 17 + Android SDK (platform android-34,
# build-tools 34.0.0) + python3 (core state regeneration).
set -euo pipefail

SDK="${ANDROID_SDK_ROOT:-/opt/android-sdk}"
BT="$SDK/build-tools/34.0.0"
AJAR="$SDK/platforms/android-34/android.jar"
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

echo "== regenerate the core state the bundle carries =="
# Reproducible build (#4438): SOURCE_DATE_EPOCH pins both the
# bundle state's clock and every zip entry timestamp, so two
# builds from the same tree are byte-identical. Release cuts
# set it from the tag; local builds leave it unset (state as
# of now, entry times normalized anyway).
if [ -n "${SOURCE_DATE_EPOCH:-}" ]; then
  STUDYSPRINT_BUILD_NOW="$(date -u -d "@$SOURCE_DATE_EPOCH" +%Y-%m-%dT%H:%M:%S+00:00)" \
    python3 ../web/build_data.py
else
  python3 ../web/build_data.py
fi

echo "== stage assets: the webApp bundle =="
rm -rf assets gen classes dexout
mkdir -p assets classes dexout
cp -r ../web assets/web
rm -rf assets/web/__pycache__

echo "== signing keystore: the committed project dev keystore =="
# #4222: ONE stable keystore, committed at
# keystore/studysprint-dev.keystore, signs every build in every
# environment — so a later build installs as an update over an
# earlier one. The old behavior (generate a fresh key whenever
# one was absent) made each environment's build uninstallable
# over another's. This is a DEV key: its password ("android")
# is published here on purpose; it protects nothing but update
# identity. If the keystore is missing, FAIL — never silently
# mint a divergent identity.
KS="$HERE/keystore/studysprint-dev.keystore"
if [ ! -f "$KS" ]; then
  echo "MISSING: $KS" >&2
  echo "Restore it from the repo (it is committed). Regenerate" >&2
  echo "ONLY as a deliberate identity reset, once, and commit:" >&2
  echo '  keytool -genkeypair -keystore keystore/studysprint-dev.keystore -alias studysprint -keyalg RSA -keysize 2048 -validity 3650 -storepass android -keypass android -dname "CN=StudySprint Dev, O=timerloggedout-spec"' >&2
  exit 1
fi

# versionCode RULE (#4438): AndroidManifest.xml's versionCode
# bumps by +1 at EVERY APK release cut (2 at the 0.2.0 cut) --
# Android only offers an install-as-update when the code is
# strictly greater, whatever versionName says. A cut that
# forgets the bump ships an APK existing installs refuse.
echo "== compile app resources (launcher icon, #4222) =="
"$BT/aapt2" compile --dir res -o res.zip

echo "== aapt2 link =="
"$BT/aapt2" link -o app-unsigned.apk -I "$AJAR" \
  --manifest AndroidManifest.xml -A assets res.zip \
  --min-sdk-version 26 --target-sdk-version 34

echo "== javac =="
javac -cp "$AJAR" -d classes $(find src -name '*.java')

echo "== d8 =="
"$BT/d8" --lib "$AJAR" --output dexout \
  $(find classes -name '*.class')

echo "== add dex + align =="
cp app-unsigned.apk app-with-dex.apk
# Zip timestamps are the reproducible-build leak: pin the dex
# entry to the zip epoch (1980, matching aapt2's entries).
touch -d "@${SOURCE_DATE_EPOCH:-0}" dexout/classes.dex
(cd dexout && zip -q -X -r ../app-with-dex.apk classes.dex)
"$BT/zipalign" -f 4 app-with-dex.apk app-aligned.apk

echo "== sign + verify =="
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android \
  --key-pass pass:android --out studysprint.apk app-aligned.apk
"$BT/apksigner" verify --print-certs studysprint.apk
unzip -l studysprint.apk | grep -E "classes.dex|assets/web/index.html|assets/web/data/state.json" || {
  echo "APK is missing expected entries"; exit 1; }
echo "BUILT: $HERE/studysprint.apk"
