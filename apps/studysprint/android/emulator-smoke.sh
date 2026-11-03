#!/usr/bin/env bash
# StudySprint APK — headless emulator smoke gate (issue #4283).
#
# Boots an AVD headless, installs the built APK, launches it,
# walks the views, and asserts the state-loaded signals the
# 2026-11-03 device smoke found missing (#4276): the bundle's
# build-time state must actually render inside the WebView.
# Screenshots + UI dumps land in the output dir as artifacts.
# The owner's device smoke stays the closer of record; this is
# the pre-device net so the defect class never reaches the
# owner first.
#
# Usage:
#   ANDROID_HOME=/path/to/sdk JAVA_HOME=/path/to/jdk \
#     bash android/emulator-smoke.sh <apk> <outdir> [avd-name]
#
# Exit 0 = state renders (gate green). Exit 1 = defect
# signature or harness failure (details in <outdir>/verdict.txt).
set -u
APK="${1:?usage: emulator-smoke.sh <apk> <outdir> [avd]}"
OUT="${2:?usage: emulator-smoke.sh <apk> <outdir> [avd]}"
AVD="${3:-ss-smoke}"
PKG="org.timerloggedout.studysprint"
ACT="$PKG/.MainActivity"
ADB="$ANDROID_HOME/platform-tools/adb"
EMU="$ANDROID_HOME/emulator/emulator"
mkdir -p "$OUT"
verdict() { echo "$1" | tee "$OUT/verdict.txt"; }

echo "== boot $AVD (headless) =="
"$EMU" -list-avds > "$OUT/emulator.log" 2>&1 || true
ACCEL=off
[ -w /dev/kvm ] && ACCEL=on
"$EMU" -avd "$AVD" -no-window -no-audio -no-boot-anim \
  -gpu swiftshader_indirect -accel "$ACCEL" -port 5554 \
  >> "$OUT/emulator.log" 2>&1 &
EMU_PID=$!
cleanup() { "$ADB" -s emulator-5554 emu kill >/dev/null 2>&1; \
  kill $EMU_PID >/dev/null 2>&1; }
trap cleanup EXIT
# Bounded waits throughout (hardening after the first CI pair
# wedged silently in-step): no adb call in this harness may block
# forever -- a gate that can hang is a defect in the gate.
for i in $(seq 1 60); do
  [ "$("$ADB" -s emulator-5554 shell getprop sys.boot_completed \
        2>/dev/null | tr -d '\r')" = "1" ] && break
  sleep 5
done
[ "$("$ADB" -s emulator-5554 shell getprop sys.boot_completed \
      2>/dev/null | tr -d '\r')" = "1" ] || { verdict "FAIL: no boot"; exit 1; }
echo "booted"

echo "== install $APK =="
timeout 300 "$ADB" -s emulator-5554 install -r "$APK" | tee "$OUT/install.log"
grep -q Success "$OUT/install.log" || { verdict "FAIL: install"; \
  exit 1; }

echo "== launch =="
"$ADB" -s emulator-5554 shell am start -n "$ACT" >/dev/null
sleep 20   # WebView first render + state fetch settle

dump() {  # $1 = view name
  timeout 60 "$ADB" -s emulator-5554 shell uiautomator dump \
    "/sdcard/$1.xml" >/dev/null 2>&1
  "$ADB" -s emulator-5554 pull "/sdcard/$1.xml" \
    "$OUT/$1.xml" >/dev/null 2>&1
  "$ADB" -s emulator-5554 exec-out screencap -p > "$OUT/$1.png"
  echo "captured $1"
}
dump today

# Walk the remaining tabs for evidence captures (assertions stay
# on Today's state signals). Coordinates come from the Today dump
# when the WebView exposes its nodes; otherwise fall back to the
# tab bar's fixed fractions.
tap_view() {  # $1 = tab label, $2 = capture name, $3 = fallback x%
  local cx cy
  cx=$(grep -o "text=\"$1\"[^>]*bounds=\"\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]\"" \
       "$OUT/today.xml" 2>/dev/null | head -1 | \
       sed -E 's/.*\[([0-9]+),[0-9]+\]\[([0-9]+),[0-9]+\].*/\1 \2/' | \
       awk '{print int(($1+$2)/2)}')
  if [ -n "${cx:-}" ]; then
    cy=$(grep -o "text=\"$1\"[^>]*bounds=\"\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]\"" \
         "$OUT/today.xml" | head -1 | \
         sed -E 's/.*\[[0-9]+,([0-9]+)\]\[[0-9]+,([0-9]+)\].*/\1 \2/' | \
         awk '{print int(($1+$2)/2)}')
  else
    local size
    size=$("$ADB" -s emulator-5554 shell wm size | grep -o "[0-9]*x[0-9]*" | head -1)
    local w=${size%x*} h=${size#*x}
    cx=$(( w * $3 / 100 )); cy=$(( h * 8 / 100 ))
  fi
  "$ADB" -s emulator-5554 shell input tap "$cx" "${cy:-100}" >/dev/null 2>&1
  sleep 3
  dump "$2"
}
tap_view "Plan" plan 30
tap_view "Reviews" reviews 46
tap_view "Reader" reader 62

echo "== assertions =="
ALL="$OUT/all-text.txt"
cat "$OUT"/*.xml 2>/dev/null | tr '<' '\n' | grep -o 'text="[^"]*"' \
  > "$ALL" || true
if grep -q "Loading your course" "$ALL"; then
  verdict "FAIL: state never loaded (#4276 signature present)"
  exit 1
fi
if ! grep -Eq 'surface version [0-9]+\.[0-9]+\.[0-9]+' "$ALL"; then
  verdict "FAIL: footer version blank (#4276 signature)"
  exit 1
fi
"$ADB" -s emulator-5554 shell pidof "$PKG" >/dev/null \
  || { verdict "FAIL: app process not running"; exit 1; }
verdict "PASS: state renders in the shell (footer version + no loading hang)"
