#!/usr/bin/env python3
"""
CI mode for deepcli – runs the agent non-interactively,
reading GitHub event payload, using cached session, and outputting JSON.
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Ensure we can import from sibling modules
sys.path.insert(0, str(Path(__file__).parent))

from core import run_ci
from session_manager import ensure_session
from router import select_peer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', required=False, help='JSON event payload')
    parser.add_argument('--workspace', required=True, help='GitHub workspace path')
    parser.add_argument('--cache-dir', default='/tmp/deepseek-cache', help='Directory for session cache')
    args = parser.parse_args()

    # Set environment
    os.environ['GITHUB_WORKSPACE'] = args.workspace
    os.environ['DEEPSEEK_CACHE_DIR'] = args.cache_dir

    # Restrict permissions of cache_dir (0o700) to protect session details from local exposure
    os.makedirs(args.cache_dir, exist_ok=True)
    try:
        os.chmod(args.cache_dir, 0o700)
    except Exception:
        pass

    # Ensure session is valid (solve PoW if needed, restore from cache)
    session = ensure_session(cache_dir=args.cache_dir)

    # Parse event payload securely from GITHUB_EVENT_PATH if available
    event = {}
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if event_path and os.path.exists(event_path):
        try:
            with open(event_path, 'r') as f:
                event = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load event payload from GITHUB_EVENT_PATH: {e}")

    # Fallback to command-line arg if event is still empty
    if not event and args.event:
        try:
            event = json.loads(args.event)
        except json.JSONDecodeError:
            event = {}

    # Determine which provider to use (OpenRouter/Omni/DeepSeek)
    # The router returns a dict with 'provider' and 'endpoint'
    peer = select_peer(event, env=os.environ)

    # Run the agent loop (non-interactive)
    result = run_ci(
        event=event,
        session=session,
        peer=peer,
        workspace=args.workspace,
        operator_token=os.environ.get('OPERATOR_TOKEN'),
    )

    # Write output JSON securely for subsequent steps with 0o600 permissions
    output_path = Path('deepseek_output.json')
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    mode = 0o600
    try:
        fd = os.open(output_path, flags, mode)
        with open(fd, 'w') as f:
            json.dump(result, f, indent=2)
    except Exception:
        # Fallback standard write if os.open is unsupported
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        try:
            os.chmod(output_path, 0o600)
        except Exception:
            pass

    # Print summary to logs
    print(f"✅ CI run completed. Decisions: {result.get('actions', [])}")

if __name__ == '__main__':
    main()
