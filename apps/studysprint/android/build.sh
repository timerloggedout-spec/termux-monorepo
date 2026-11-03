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

echo "== dev keystore (generated per build environment if absent) =="
if [ ! -f dev.keystore ]; then
  keytool -genkeypair -keystore dev.keystore -alias studysprint \
    -keyalg RSA -keysize 2048 -validity 3650 \
    -storepass android -keypass android \
    -dname "CN=StudySprint Dev, O=timerloggedout-spec"
fi

echo "== aapt2 link =="
"$BT/aapt2" link -o app-unsigned.apk -I "$AJAR" \
  --manifest AndroidManifest.xml -A assets \
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
"$BT/apksigner" sign --ks dev.keystore --ks-pass pass:android \
  --key-pass pass:android --out studysprint.apk app-aligned.apk
"$BT/apksigner" verify --print-certs studysprint.apk
unzip -l studysprint.apk | grep -E "classes.dex|assets/web/index.html|assets/web/data/state.json" || {
  echo "APK is missing expected entries"; exit 1; }
echo "BUILT: $HERE/studysprint.apk"
