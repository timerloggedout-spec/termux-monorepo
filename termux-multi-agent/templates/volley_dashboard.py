import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import time

VOLLEY_LOG = Path("~/termux-multi-agent/workspace/volley_log.jsonl").expanduser()

def load_volleys() -> list:
    volleys = []
    if VOLLEY_LOG.exists():
        with open(VOLLEY_LOG) as f:
            for line in f:
                try:
                    volleys.append(json.loads(line))
                except:
                    continue
    return volleys

def generate_dashboard():
    volleys = load_volleys()
    if not volleys:
        print("No volleys logged yet.")
        return

    status_counts = defaultdict(int)
    agent_comms = defaultdict(lambda: defaultdict(int))
    priority_counts = defaultdict(int)
    type_counts = defaultdict(int)

    for v in volleys:
        status_counts[v["status"]] += 1
        agent_comms[v["from_agent"]][v["to_agent"]] += 1
        priority_counts[v["priority"]] += 1
        type_counts[v["type"]] += 1

    print("=" * 80)
    print(f"🏹 VOLLEY DASHBOARD | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print("\n📊 STATUS OVERVIEW:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status.upper():<10}: {count:>3} volleys")

    agents = sorted(set(
        list(agent_comms.keys()) +
        [to for from_ in agent_comms for to in agent_comms[from_]]
    ))
    print("\n🤖 AGENT COMMUNICATION:")
    print("     " + " | ".join(f"{agent:<15}" for agent in agents))
    print("-" * (18 + 16 * len(agents)))
    for from_agent in agents:
        row = [from_agent.ljust(15)]
        for to_agent in agents:
            count = agent_comms[from_agent].get(to_agent, 0)
            row.append(f"{count:>3}".ljust(15))
        print(" | ".join(row))

    print("\n⚡ PRIORITY MATRIX:")
    for priority, count in sorted(priority_counts.items()):
        print(f"  {priority.upper():<10}: {count:>3} volleys")

    print("\n🏷️  VOLLEY TYPES:")
    for volley_type, count in sorted(type_counts.items()):
        print(f"  {volley_type.upper():<10}: {count:>3} volleys")

    print("\n🕒 RECENT VOLLEYS:")
    for v in sorted(volleys, key=lambda x: x["start_time"], reverse=True)[:10]:
        duration = f"{v.get('duration_sec', 0)}s" if v.get("end_time") else "N/A"
        print(f"  {v['volley_id']:<20} | {v['from_agent']:<15} → {v['to_agent']:<15} | {v['status']:<10} | {v['priority']:<10} | {duration}")

    cedar_count = sum(1 for v in volleys if v.get("cedar_script"))
    cid_count = sum(1 for v in volleys if v.get("cid_py"))
    print(f"\n🧬 CEDARSCRIPT: {cedar_count} volleys | CID.py: {cid_count} volleys")

def watch_volleys(interval: int = 5):
    while True:
        generate_dashboard()
        time.sleep(interval)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        watch_volleys()
    else:
        generate_dashboard()
