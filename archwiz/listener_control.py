#!/usr/bin/env python3
"""Safe start/stop for the activity listener using a PID file."""
import subprocess, os, sys, time
from pathlib import Path

HOME = Path.home()
PID_FILE = HOME / 'archwiz/.listener.pid'
LISTENER = HOME / 'archwiz/activity_listener.py'

def start():
    if PID_FILE.exists():
        pid = PID_FILE.read_text().strip()
        if pid and Path(f'/proc/{pid}').exists():
            print("Listener already running.")
            return
    env = {**os.environ, 'ARCHWIZ_MODE': 'auto'}
    proc = subprocess.Popen(
        ['python3', str(LISTENER)],
        env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL, start_new_session=True
    )
    PID_FILE.write_text(str(proc.pid))
    print(f"Listener started (pid {proc.pid}).")

def stop():
    if not PID_FILE.exists():
        print("Listener not running.")
        return
    pid = PID_FILE.read_text().strip()
    if pid:
        try:
            os.kill(int(pid), 9)
        except:
            pass
    PID_FILE.unlink(missing_ok=True)
    print("Listener stopped.")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: listener_control.py start|stop|restart")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == 'start':
        start()
    elif cmd == 'stop':
        stop()
    elif cmd == 'restart':
        stop()
        time.sleep(1)
        start()
    else:
        print(f"Unknown command: {cmd}")
