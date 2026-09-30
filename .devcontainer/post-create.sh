#!/usr/bin/env bash
set -euo pipefail

# pip tooling
python3 -m pip install --quiet --upgrade pip || true
python3 -m pip install --quiet ruff httpx pytest || true

# gitleaks
if ! command -v gitleaks >/dev/null 2>&1; then
  _arch=$(dpkg --print-architecture 2>/dev/null || echo amd64)
  case "$_arch" in
    arm64) _gl=arm64 ;;
    *)     _gl=x64 ;;
  esac
  curl -fsSL "https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_${_gl}.tar.gz" \
    | sudo tar -xz -C /usr/local/bin gitleaks || true
  sudo chmod +x /usr/local/bin/gitleaks 2>/dev/null || true
fi

echo "[post-create] done"
