#!/bin/bash
# Harmony Hub unified entry point – sets environment then delegates
export PYTHONPATH="$HOME/harmony_hub/src:$PYTHONPATH"
ACCOUNT="${SYNTH_ACCOUNT:-primary}"
SIGNATURE="${SYNTH_SIGNATURE:-user}"
PROJECT="${SYNTH_PROJECT:-synthegration}"
exec python3 -c "
import sys, os; sys.path.insert(0, '$HOME/harmony_hub/src')
from token_provider_v2 import get_token
from pathlib import Path
import json

# Load token for account
token = get_token('$ACCOUNT')
print(f'Account: $ACCOUNT | Token: {token[:4]}...{token[-4:]} | Signature: $SIGNATURE | Project: $PROJECT')
# Here we could actually call the target command (e.g. deepcli, agent, harvest)
# For now, just demonstrate.
"
