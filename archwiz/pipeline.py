#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone
HOME = Path.home()
PIPE_LOG = HOME / 'archwiz/pipeline_log.jsonl'
def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr
def verify_and_tasque(task_id, target_file=''):
    entry = {'timestamp': datetime.now(timezone.utc).isoformat(), 'task_id': task_id, 'target_file': target_file}
    if target_file and target_file.endswith('.py'):
        code, out = run(['python3', str(HOME / 'archwiz/probe.py'), target_file, '--json'])
        entry['probe'] = {'returncode': code, 'output': out[:500]}
        if code != 0: entry['verdict'] = 'FAIL_PROBE'; return False, out
    code, out = run(['python3', str(HOME / 'archwiz/sentinel.py'), task_id])
    entry['sentinel'] = {'returncode': code, 'output': out[:500]}
    if code != 0: entry['verdict'] = 'REVIEW'; return False, out
    code, out = run(['python3', str(HOME / 'archwiz/tasque_declare.py'), task_id, 'autonomous completion', 'archwiz'])
    entry['tasque'] = {'returncode': code, 'output': out[:200]}
    entry['verdict'] = 'TASQUE'
    with open(PIPE_LOG, 'a') as f: f.write(json.dumps(entry) + '\n')
    return True, 'TasQue declared.'
if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(1)
    tid = sys.argv[1]; target = sys.argv[2] if len(sys.argv) > 2 else ''
    ok, msg = verify_and_tasque(tid, target)
    print(msg)
    sys.exit(0 if ok else 1)
