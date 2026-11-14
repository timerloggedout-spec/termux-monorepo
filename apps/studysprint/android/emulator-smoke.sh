#!/usr/bin/env bash
# StudySprint APK — headless emulator smoke gate (issue #4283).
#
# Boots an AVD headless, installs the built APK, launches it,
# walks the views, and asserts the state-loaded signals the
# 2026-11-03 device smoke found missing (#4276): the bundle's
# build-time state must actually render inside the WebView.
# Screenshots + UI dumps + a screen recording (smoke.mp4,
# #4420) land in the output dir as artifacts.
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
REC_PATH=""
cleanup() {
  # Video evidence (#4420, owner standing requirement): stop the
  # screen recording and pull it BEFORE the emulator dies, on
  # every exit path -- verdict exits included (the trap fires on
  # EXIT). SIGINT makes screenrecord finalize the mp4 cleanly.
  # All mechanics log into the artifact (record.log); the pull
  # retries once, so a silent no-video run cannot recur.
  if [ -n "$REC_PATH" ]; then
    {
      echo "-- cleanup: stop + pull $REC_PATH --"
      "$ADB" -s emulator-5554 shell pkill -2 screenrecord 2>&1
      sleep 3
      "$ADB" -s emulator-5554 shell ls -la "$REC_PATH" 2>&1
      "$ADB" -s emulator-5554 pull "$REC_PATH" \
        "$OUT/smoke.mp4" 2>&1
      if [ ! -s "$OUT/smoke.mp4" ]; then
        echo "-- pull retry after settle --"
        sleep 3
        "$ADB" -s emulator-5554 pull "$REC_PATH" \
          "$OUT/smoke.mp4" 2>&1
      fi
      ls -la "$OUT/smoke.mp4" 2>&1
    } >> "$OUT/record.log" 2>&1 || true
  fi
  "$ADB" -s emulator-5554 emu kill >/dev/null 2>&1
  kill $EMU_PID >/dev/null 2>&1
}
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

echo "== record (video evidence, #4420) =="
# 175s cap: screenrecord's own ceiling is 180s; the gate's
# install + launch + per-view walk fits well inside it.
#
# Attempt ladder (attempt-4 finding): the plain detached form
# exited 0 on the host yet never executed on the device -- no
# mp4, no device-side log -- while uiautomator dumps to the
# same /sdcard succeeded in the same run. So the start is now
# a LADDER: each form is tried in order and VERIFIED by the
# output file's presence before the gate proceeds; every
# attempt logs into record.log; REC_PATH remembers which
# form/path won, and the cleanup pulls from exactly there.
# A run with no working form says so in record.log instead of
# failing silently.
start_recording() {
  local forms=(
    "screenrecord --time-limit 175 /sdcard/smoke.mp4 >/sdcard/screenrecord.log 2>&1 &"
    "setsid screenrecord --time-limit 175 /sdcard/smoke.mp4 >/sdcard/screenrecord.log 2>&1 </dev/null &"
    "screenrecord --time-limit 175 /data/local/tmp/smoke.mp4 >/data/local/tmp/screenrecord.log 2>&1 &"
  )
  local paths=(/sdcard/smoke.mp4 /sdcard/smoke.mp4 /data/local/tmp/smoke.mp4)
  : > "$OUT/record.log"
  local i
  for i in 0 1 2; do
    echo "-- record attempt $((i + 1)): ${forms[$i]}" >> "$OUT/record.log"
    "$ADB" -s emulator-5554 shell "${forms[$i]}" >/dev/null 2>&1 || true
    sleep 2
    if "$ADB" -s emulator-5554 shell "test -e ${paths[$i]}" \
        >/dev/null 2>&1; then
      REC_PATH="${paths[$i]}"
      echo "RECORDING via attempt $((i + 1)): $REC_PATH" \
        >> "$OUT/record.log"
      return 0
    fi
    "$ADB" -s emulator-5554 shell \
      "cat /sdcard/screenrecord.log /data/local/tmp/screenrecord.log" \
      >> "$OUT/record.log" 2>&1 || true
    "$ADB" -s emulator-5554 shell pkill -2 screenrecord \
      >/dev/null 2>&1 || true
  done
  echo "RECORDING FAILED: no form produced a file (logs above)" \
    >> "$OUT/record.log"
  return 0
}
start_recording

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
# Signals are checked on the JOINED text: uiautomator splits the
# footer into sibling nodes (attempt 3: "surface version " and
# "0.1.3" arrived as separate text= values), so a line-wise grep
# can never match the version signal even when the app renders
# fully. Joining the node values with spaces restores the
# sentence the user sees.
JOINED="$OUT/all-joined.txt"
sed 's/^text="//; s/"$//' "$ALL" | tr '\n' ' ' > "$JOINED" || true
if grep -q "Loading your course" "$JOINED"; then
  verdict "FAIL: state never loaded (#4276 signature present)"
  exit 1
fi
if ! grep -Eq 'surface version[[:space:]]+[0-9]+\.[0-9]+\.[0-9]+' \
    "$JOINED"; then
  verdict "FAIL: footer version blank (#4276 signature)"
  exit 1
fi
"$ADB" -s emulator-5554 shell pidof "$PKG" >/dev/null \
  || { verdict "FAIL: app process not running"; exit 1; }
verdict "PASS: state renders in the shell (footer version + no loading hang)"
