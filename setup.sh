#!/usr/bin/env bash
set -euo pipefail

echo "Setting up minimal environment (requirements-base)"
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements-base.txt

# Ensure token directory exists
python3 - <<'PY'
from archwiz import config as aw_config
p = aw_config.get_tokens_dir()
print('Ensured tokens dir at', p)
PY

echo "Done. For heavy dependencies (flair, torch), follow the project's README and use a proper x86_64 environment or Colab." 
