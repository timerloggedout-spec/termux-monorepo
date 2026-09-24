#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="${TERMUX_MONOREPO_ROOT:-$HOME/termux-monorepo}"
REMOTE="${TERMUX_GITHUB_REMOTE:-git@github.com:timerloggedout-spec/termux-monorepo.git}"

pkg update -y
pkg install -y git gh openssh python

command -v git >/dev/null
command -v gh >/dev/null
command -v ssh >/dev/null
command -v python >/dev/null

git --version
gh --version | head -n 1

if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is installed but not authenticated; starting interactive GitHub login."
  gh auth login --hostname github.com --git-protocol ssh --web
fi

gh auth setup-git

if [ -d "$ROOT/.git" ]; then
  git -C "$ROOT" remote set-url origin "$REMOTE" 2>/dev/null || git -C "$ROOT" remote add origin "$REMOTE"
  git -C "$ROOT" fetch --prune origin
  git -C "$ROOT" status --short --branch
  git -C "$ROOT" remote -v
else
  echo "Repository checkout not found at $ROOT"
  echo "Clone with: git clone $REMOTE $ROOT"
fi

echo "CLI bootstrap complete."
