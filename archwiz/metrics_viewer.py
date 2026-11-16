#!/usr/bin/env python3
"""ArchWiz Live Metrics — last entries + live tail, color‑aligned."""
import json, os, sys, time, select
from pathlib import Path
from datetime import datetime

R = '\033[1;31m'; G = '\033[1;32m'; Y = '\033[1;33m'
C = '\033[1;36m'; W = '\033[1;37m'; N = '\033[0m'
BOLD = '\033[1m'

LOG = Path.home() / 'workspace/llm_map/metrics_log.jsonl'

def color_val(val, high_good=True):
    if val is None: return f'{W} --{N}'
    if high_good:
        if val >= 80: return f'{G}{val:>3d}{N}'
        if val >= 50: return f'{Y}{val:>3d}{N}'
        return f'{R}{val:>3d}{N}'
    else:
        if val <= 5:  return f'{G}{val:>3d}{N}'
        if val <= 20: return f'{Y}{val:>3d}{N}'
        return f'{R}{val:>3d}{N}'

def header():
    os.system('clear')
    print(f"{C}{'─'*70}{N}")
    print(f"{G}⚡ ARCHWIZ LIVE METRICS{C}{datetime.now().strftime('%H:%M:%S'):>40}{N}")
    print(f"{C}{'─'*70}{N}")
    print(f" {'FILE':<42s} {'SHOCK':>6s} {'NEXUS':>6s} {'RELI':>6s} {'STAB':>5s} {'ECHO':>5s}")
    print(f"{C}{'─'*70}{N}")

def print_entry(obj):
    f = obj.get('file','?')[-40:]
    sw = obj.get('shockwave')
    nx = obj.get('nexus')
    rl = obj.get('reliability')
    st = obj.get('stability_days')
    ec = obj.get('echo')
    print(f" {f:<42s} {color_val(sw):>6s} {color_val(nx):>6s} {color_val(rl):>6s} {color_val(st):>5s} {color_val(ec,False):>5s}")

def replay_last(n=15):
    if not LOG.exists():
        print(f"{Y}No metrics file found.{N}")
        return
    lines = LOG.read_text().strip().splitlines()
    for line in lines[-n:]:
        try:
            print_entry(json.loads(line))
        except:
            pass

def follow():
    if not LOG.exists():
        return
    with open(LOG, 'r') as f:
        f.seek(0, 2)  # end
        count = 0
        while True:
            line = f.readline()
            if line:
                try:
                    print_entry(json.loads(line))
                    count += 1
                except:
                    pass
            else:
                if sys.stdin in select.select([sys.stdin], [], [], 0.2)[0]:
                    key = sys.stdin.read(1)
                    if key.lower() == 'q':
                        break
                time.sleep(0.1)
            # Reprint header every 20 lines to keep it visible
            if count > 0 and count % 20 == 0:
                header()
                print(f"{Y}  ... live ({count} new entries) ...{N}")

if __name__ == '__main__':
    header()
    print(f"{Y}  Last entries:{N}")
    print(f"{C}{'─'*70}{N}")
    replay_last(15)
    print(f"{C}{'─'*70}{N}")
    print(f"{Y}  Watching live — press 'q' to return, Ctrl+C for emergency exit{N}")
    try:
        follow()
    except KeyboardInterrupt:
        print(f"\n{R}Emergency exit — shell kept whole.{N}")
        sys.exit(0)
    print(f"\n{G}Returning to ArchWiz menu.{N}")
