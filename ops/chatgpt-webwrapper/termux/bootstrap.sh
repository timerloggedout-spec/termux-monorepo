#!/data/data/com.termux/files/usr/bin/sh
# ChatGPT webWrapper — TERMUX device instance, one-shot setup.
#
# Run inside Termux, from this bundle dir (~/chatgpt-wrapper-termux after
# the fetch in README.md). Everything this script creates lives inside
# this dir; nothing is copied anywhere else on the device.
#
# Assumes Termux chromium + chromedriver are already installed (the
# owner's base install). If they are missing it prints exactly what to
# install and stops — it does not install system packages itself.
set -eu
cd "$(dirname "$0")"

fail=0

echo "== chatgpt-wrapper termux bootstrap =="

# --- Termux chromium + chromedriver (detect; clear message if missing) ---
CHROMIUM_BIN=""
for c in chromium chromium-browser "$PREFIX/bin/chromium" "$PREFIX/bin/chromium-browser"; do
    if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then CHROMIUM_BIN="$c"; break; fi
done
if [ -n "$CHROMIUM_BIN" ]; then
    echo "chromium:     FOUND ($CHROMIUM_BIN)"
else
    echo "chromium:     MISSING"
    echo "  -> install it in Termux first:  pkg install chromium"
    fail=1
fi

CHROMEDRIVER_BIN=""
for c in chromedriver "$PREFIX/bin/chromedriver"; do
    if command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; then CHROMEDRIVER_BIN="$c"; break; fi
done
if [ -n "$CHROMEDRIVER_BIN" ]; then
    echo "chromedriver: FOUND ($CHROMEDRIVER_BIN)"
else
    echo "chromedriver: MISSING"
    echo "  -> it ships with the Termux chromium package:  pkg install chromium"
    echo "     (if chromium is present but chromedriver is not: pkg reinstall chromium)"
    fail=1
fi

if [ "$fail" -ne 0 ]; then
    echo "bootstrap: STOPPED — browser binaries missing (see above)."
    exit 1
fi

# --- python deps ---
if ! command -v python3 >/dev/null 2>&1; then
    echo "python3:      MISSING -> install it in Termux first:  pkg install python"
    exit 1
fi
echo "python deps:  installing selenium + beautifulsoup4 via pip"
python3 -m pip install --quiet --disable-pip-version-check selenium beautifulsoup4

# --- bundle-local dirs (inside this dir only) ---
mkdir -p profile session_store scrape/full exports
chmod 700 profile session_store 2>/dev/null || true

# --- doctor: chromium binary, chromedriver, selenium import, profile writable ---
echo "== doctor =="
python3 core_se.py --doctor
touch .bootstrapped
echo "bootstrap: OK (marker .bootstrapped written; run ./run.sh)"
