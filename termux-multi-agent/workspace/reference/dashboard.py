import time
import os
import json

TELEMETRY_LOG = "agent_telemetry_stream.json"

# Stateful cache for high-performance incremental I/O parsing
_last_file_position = 0
_cached_active_jobs = {}

def clear_screen():
    print("\033[H\033[J", end="")

def read_latest_telemetry():
    # Optimized telemetry parser with state tracking and seek/tell operations.
    # Performs high-performance incremental I/O for massive speedups on large files.
    global _last_file_position, _cached_active_jobs
    if not os.path.exists(TELEMETRY_LOG):
        _last_file_position = 0
        _cached_active_jobs = {}
        return []

    try:
        file_size = os.path.getsize(TELEMETRY_LOG)
        # If file was truncated/recreated, reset the position and cache state
        if file_size < _last_file_position:
            _last_file_position = 0
            _cached_active_jobs = {}

        if file_size > _last_file_position:
            with open(TELEMETRY_LOG, "r") as f:
                f.seek(_last_file_position)
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        target = entry.get("target") or "System"
                        _cached_active_jobs[target] = entry
                    except json.JSONDecodeError:
                        continue
                _last_file_position = f.tell()
    except Exception:
        pass

    return list(_cached_active_jobs.values())

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