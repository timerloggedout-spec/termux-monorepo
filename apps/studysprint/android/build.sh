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
python3 ../web/build_data.py

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
  echo "  keytool -genkeypair -keystore keystore/studysprint-dev.keystore \" >&2
  echo "    -alias studysprint -keyalg RSA -keysize 2048 -validity 3650 \" >&2
  echo "    -storepass android -keypass android \" >&2
  echo "    -dname \"CN=StudySprint Dev, O=timerloggedout-spec\"" >&2
  exit 1
fi

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
(cd dexout && zip -q -r ../app-with-dex.apk classes.dex)
"$BT/zipalign" -f 4 app-with-dex.apk app-aligned.apk

echo "== sign + verify =="
"$BT/apksigner" sign --ks "$KS" --ks-pass pass:android \
  --key-pass pass:android --out studysprint.apk app-aligned.apk
"$BT/apksigner" verify --print-certs studysprint.apk
unzip -l studysprint.apk | grep -E "classes.dex|assets/web/index.html|assets/web/data/state.json" || {
  echo "APK is missing expected entries"; exit 1; }
echo "BUILT: $HERE/studysprint.apk"
