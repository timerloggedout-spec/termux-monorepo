import time
import os
import json

TELEMETRY_LOG = "agent_telemetry_stream.json"

def clear_screen():
    print("\033[H\033[J", end="")

# State-tracking cache and position pointers for incremental I/O performance optimization
_active_jobs_cache = {}
_last_file_pos = 0
_last_file_ino = None
_last_file_mtime = 0

def read_latest_telemetry():
    global _last_file_pos, _active_jobs_cache, _last_file_ino, _last_file_mtime
    if not os.path.exists(TELEMETRY_LOG):
        _active_jobs_cache = {}
        _last_file_pos = 0
        _last_file_ino = None
        _last_file_mtime = 0
        return []
    try:
        stat_info = os.stat(TELEMETRY_LOG)
        file_size = stat_info.st_size
        file_ino = stat_info.st_ino
        file_mtime = stat_info.st_mtime

        if (file_size < _last_file_pos or
            _last_file_ino is None or
            _last_file_ino != file_ino or
            file_mtime < _last_file_mtime):
            _active_jobs_cache = {}
            _last_file_pos = 0
            _last_file_ino = file_ino
            _last_file_mtime = file_mtime

        with open(TELEMETRY_LOG, "r") as f:
            if _last_file_pos > 0:
                f.seek(_last_file_pos)
            while True:
                curr_pos = f.tell()
                line = f.readline()
                if not line:
                    break
                if not line.endswith("\n"):
                    f.seek(curr_pos)
                    break
                _last_file_pos = f.tell()
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    target = entry.get("target") or "System"
                    _active_jobs_cache[target] = entry
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return list(_active_jobs_cache.values())

def render_dashboard():
    clear_screen()
    print("=" * 65)
    print(" ⚡ TERMUX MULTI-AGENT PARALLEL TELEMETRY DASHBOARD ⚡ ")
    print("=" * 65)
    print(f" Last Sync: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 65)
    print(f"{'TARGET FILE':<20} | {'AGENT':<16} | {'TRY':<4} | {'STATUS':<15}")
    print("-" * 65)

    jobs = read_latest_telemetry()
    if not jobs:
        print(" [ Waiting for background agent pipelines to initialize... ]")
    for job in jobs:
        target = job.get("target") or "Global"
        if len(target) > 18:
            target = "..." + target[-15:]
        agent = job.get("agent", "Unknown")
        attempt = str(job.get("attempt") or "-")
        level = job.get("level", "INFO")

        if level == "SUCCESS":
            status_str = "\033[92mSUCCESS\033[0m"
        elif level == "RETRY":
            status_str = "\033[93mRETRYING\033[0m"
        elif level == "CRITICAL":
            status_str = "\033[91mCRITICAL\033[0m"
        else:
            status_str = "\033[94mPROCESSING\033[0m"

        print(f"{target:<20} | {agent:<16} | {attempt:<4} | {status_str:<15}")
        print(f" ↳ Msg: {job.get('message', '')[:60]}")
        print("-" * 65)

def main():
    try:
        while True:
            render_dashboard()
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nExiting Dashboard Viewer.")

if __name__ == '__main__':
    main()