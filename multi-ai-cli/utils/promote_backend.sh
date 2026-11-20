#!/usr/bin/env bash
# promote_backend.sh <sandbox_name> <target_name> [--force]
# Moves a backend from sandbox/backends/ to backends/ after testing
set -e
SBOX=~/multi-ai-cli/sandbox/backends
PROD=~/multi-ai-cli/backends
name="$1"
target="${2:-$name}"
force="$3"
src="$SBOX/$name.py"
dst="$PROD/$target.py"
if [ ! -f "$src" ]; then echo "No such sandbox backend: $src"; exit 1; fi
if [ -f "$dst" ] && [ "$force" != "--force" ]; then echo "Target exists. Use --force to overwrite."; exit 1; fi
# Gate 1: is_available() must return True when token present
python3 -c "
import sys; sys.path.insert(0, '$SBOX')
from ${name} import *
if not backend.is_available():
    print('FAIL: is_available() returned False')
    sys.exit(1)
print('Gate 1 passed')
"
# Gate 2: send_message() returns non-empty string
python3 -c "
import sys; sys.path.insert(0, '$SBOX')
from ${name} import *
reply = backend.send_message('Hello', [])
if not reply or len(reply) < 5:
    print('FAIL: empty or short reply')
    sys.exit(1)
print('Gate 2 passed')
"
cp "$src" "$dst"
echo "Promoted $name → $target"
# Log
echo "$(date -Iseconds) $name → $target" >> ~/multi-ai-cli/promotions.log
