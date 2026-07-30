#!/bin/bash
# context_cache.sh – cache the orchestrator's context bundle
# Usage: source context_cache.sh
# Sets: CACHED_CONTEXT (path to cached bundle, or empty)

TARGET_FILE="$1"
CACHE_DIR="$HOME/.cache/context_cache"
mkdir -p "$CACHE_DIR"

# Hash the target file + its dependencies
TARGET_HASH=$(sha256sum "$TARGET_FILE" 2>/dev/null | cut -d' ' -f1)
CACHE_FILE="$CACHE_DIR/${TARGET_HASH}.json"

if [ -f "$CACHE_FILE" ]; then
  echo "Using cached context for $TARGET_FILE" >&2
  echo "$CACHE_FILE"
  exit 0
else
  echo "" >&2
  exit 1
fi
