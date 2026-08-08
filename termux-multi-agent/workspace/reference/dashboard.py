import time
import os
import json

TELEMETRY_LOG = "agent_telemetry_stream.json"

def clear_screen():
    print("\033[H\033[J", end="")

# Cache state variables to enable high-performance incremental I/O updates (state-tracking & seek/tell)
_last_position = 0
_active_jobs = {}

def read_latest_telemetry():
    """
    Optimized telemetry parser that incrementally parses new lines from the telemetry stream
    using state tracking and seek/tell operations, yielding massive performance gains on large log files.
    """
    global _last_position, _active_jobs
    if not os.path.exists(TELEMETRY_LOG):
        _last_position = 0
        _active_jobs = {}
        return []
    try:
        # Detect if log file has been truncated, rotated, or re-created
        file_size = os.path.getsize(TELEMETRY_LOG)
        if file_size < _last_position:
            _last_position = 0
            _active_jobs = {}

        with open(TELEMETRY_LOG, "r") as f:
            if _last_position > 0:
                f.seek(_last_position)
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    target = entry.get("target") or "System"
                    _active_jobs[target] = entry
                except json.JSONDecodeError:
                    continue
            _last_position = f.tell()
    except Exception:
        pass
    return list(_active_jobs.values())

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