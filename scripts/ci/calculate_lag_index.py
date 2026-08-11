#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime

# Define standard configurations as Single Source of Truth
COOLDOWN_CONFIGS = """# Lane Consolidation SSOT

This document is the **Single Source of Truth** for coordination, timing quotas, GHA debounces, and cooldown configurations across the monorepo's agentic pipelines.

## Active Quotas & Cooldown Configurations

| Layer / Component | Configuration Parameter | Value / Throttle | Purpose / Detail |
|---|---|---|---|
| **`model_router.py`** | Daily Soft Budget | Saved in `/tmp/model-router` | Elevated limits, OpenRouter free polling, ELO rankings |
| **`peer-review-orchestrator.yml`** | Auto-Fix Throttle | **45 minutes** | Cooldown between `@coderabbitai autofix` requests |
| **`peer-review-orchestrator.yml`** | Settle Delay | **90 seconds** | Settle time after autofix request before posting ready marker |
| **`agent-review-auto-jules.yml`** | Idempotent Window | **20 minutes** | Debounce window on bot feedback to avoid redundant Jules summons |
| **`agent-continuous-ops.yml`** | Sweep Debounce | **90 minutes** (Dynamic) | Time to wait after continuous ops comment before re-pinging |
| **`agent-continuous-ops.yml`** | Stale Agent Activity | **3 hours** (Dynamic) | Max idle time since last agent activity before nudging |
| **`agent-continuous-ops.yml`** | Schedule Interval | **Every 1 hour** (`17 * * * *`) | Backup cron job frequency to jump start stuck PRs |
| **`agent-continuous-ops.yml`** | Sweep Capacity | **8 to 20 PRs** | Max PRs evaluated per sweep |
"""

def github_api_request(url, token=None):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "Jules-Lag-Index-Calculator")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"API HTTP Error for {url}: {e.code} - {e.reason}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"API Error for {url}: {e}", file=sys.stderr)
        return None

def parse_iso8601(ts_str):
    if not ts_str:
        return None
    try:
        # standard ISO8601 like 2026-08-08T18:30:00Z
        return datetime.strptime(ts_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return None

def main():
    token = os.environ.get("OPERATOR_GITHUB_TOKEN") or os.environ.get("OPERATOR_TOKEN") or os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY") or "timerloggedout-spec/termux-monorepo"

    print(f"Running response time lag calculation for: {repo}")

    # Default fallbacks
    default_debounce_sec = 90 * 60  # 90m
    default_stale_sec = 3 * 60 * 60  # 3h

    metrics = {
        "global_averages": {
            "avg_message_response_lag_sec": default_debounce_sec,
            "avg_actual_response_lag_sec": default_stale_sec,
            "suggested_debounce_ms": default_debounce_sec * 1000,
            "suggested_stale_ms": default_stale_sec * 1000
        },
        "by_pr": {}
    }

    if not token:
        print("Warning: GITHUB_TOKEN not provided. Generating standard lag index with fallback values.")
        # Create directories if they don't exist
        os.makedirs("docs/ops", exist_ok=True)

        # Write dummy/fallback files
        with open("docs/ops/response_time_lag_index.json", "w") as f:
            json.dump(metrics, f, indent=2)

        ssot_content = COOLDOWN_CONFIGS + "\n## Current Work & Dynamic Response Lags\n\n*Running locally/offline. Fallback defaults applied.*\n\n| PR/Issue | Message Response Lag | Programmatic Response Lag | Status |\n|---|---|---|---|\n| Default Fallback | 1.5 hours | 3.0 hours | Active |\n"
        with open("docs/ops/LANE_CONSOLIDATION_SSOT.md", "w") as f:
            f.write(ssot_content)
        print("Fallback files written successfully.")
        return

    # Fetch open PRs
    print("Fetching open PRs...")
    open_prs = github_api_request(f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=30", token) or []
    print("Fetching closed PRs for historical data...")
    closed_prs = github_api_request(f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=20", token) or []

    all_prs = open_prs + closed_prs
    print(f"Total PRs retrieved for analysis: {len(all_prs)}")

    all_message_lags = []
    all_actual_lags = []

    pr_table_rows = []

    for pr in all_prs:
        pr_number = pr["number"]
        pr_title = pr["title"]
        pr_state = pr["state"]
        print(f"Analyzing PR #{pr_number} - {pr_title}...")

        # Get comments
        comments = github_api_request(f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments?per_page=100", token) or []
        # Get commits
        commits = github_api_request(f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits?per_page=100", token) or []

        # Chronological timeline of everything
        timeline = []
        for c in comments:
            t = parse_iso8601(c["created_at"])
            if t:
                timeline.append({
                    "type": "comment",
                    "user": c["user"]["login"] if c.get("user") else "unknown",
                    "body": c.get("body") or "",
                    "time": t
                })
        for commit in commits:
            commit_meta = commit.get("commit", {})
            committer = commit_meta.get("committer", {}) or commit_meta.get("author", {}) or {}
            t = parse_iso8601(committer.get("date"))
            if t:
                timeline.append({
                    "type": "commit",
                    "user": commit_meta.get("author", {}).get("name") or "unknown",
                    "time": t
                })

        # Sort timeline chronologically
        timeline.sort(key=lambda x: x["time"])

        # Trace summon events
        summon_time = None
        message_response_time = None
        actual_response_time = None

        pr_message_lags = []
        pr_actual_lags = []

        agent_logins = [
            'google-labs-jules', 'devin-ai-integration', 'coderabbitai',
            'github-actions', 'copilot', 'gitar-bot', 'blocksorg'
        ]

        def is_agent(username):
            u = (username or "").lower()
            return any(agent in u for agent in agent_logins)

        for event in timeline:
            if event["type"] == "comment":
                body = event["body"]
                # Is it a summon?
                is_summon = any(marker in body for marker in ["<!-- continuous-agent-ops -->", "<!-- agent-auto-jules -->", "@jules", "@gemini-cli"])
                if is_summon:
                    summon_time = event["time"]
                    message_response_time = None
                    actual_response_time = None
                    continue

                if summon_time:
                    # Look for first message response (bot acknowledgment)
                    if not message_response_time and is_agent(event["user"]):
                        message_response_time = event["time"]
                        lag = (message_response_time - summon_time).total_seconds()
                        pr_message_lags.append(lag)
                        all_message_lags.append(lag)

            elif event["type"] == "commit":
                if summon_time and not actual_response_time:
                    # Look for first programmatic response (commit after summon)
                    actual_response_time = event["time"]
                    lag = (actual_response_time - summon_time).total_seconds()
                    pr_actual_lags.append(lag)
                    all_actual_lags.append(lag)

        # Calculate PR averages
        pr_avg_msg = sum(pr_message_lags) / len(pr_message_lags) if pr_message_lags else None
        pr_avg_act = sum(pr_actual_lags) / len(pr_actual_lags) if pr_actual_lags else None

        if pr_avg_msg is not None or pr_avg_act is not None:
            suggested_debounce = max(30 * 60, pr_avg_msg * 1.5) if pr_avg_msg is not None else default_debounce_sec
            suggested_stale = max(60 * 60, pr_avg_act * 1.5) if pr_avg_act is not None else default_stale_sec

            metrics["by_pr"][str(pr_number)] = {
                "avg_message_response_lag_sec": pr_avg_msg,
                "avg_actual_response_lag_sec": pr_avg_act,
                "suggested_debounce_ms": int(suggested_debounce * 1000),
                "suggested_stale_ms": int(suggested_stale * 1000)
            }

            msg_lag_str = f"{round(pr_avg_msg / 60, 1)} min" if pr_avg_msg is not None else "N/A"
            act_lag_str = f"{round(pr_avg_act / 3600, 1)} hrs" if pr_avg_act is not None else "N/A"
            pr_table_rows.append(f"| PR #{pr_number} | {msg_lag_str} | {act_lag_str} | {pr_state.upper()} |")

    # Compute global averages
    if all_message_lags:
        avg_msg = sum(all_message_lags) / len(all_message_lags)
        metrics["global_averages"]["avg_message_response_lag_sec"] = avg_msg
        metrics["global_averages"]["suggested_debounce_ms"] = int(max(30 * 60, avg_msg * 1.5) * 1000)
    if all_actual_lags:
        avg_act = sum(all_actual_lags) / len(all_actual_lags)
        metrics["global_averages"]["avg_actual_response_lag_sec"] = avg_act
        metrics["global_averages"]["suggested_stale_ms"] = int(max(60 * 60, avg_act * 1.5) * 1000)

    # Ensure dirs
    os.makedirs("docs/ops", exist_ok=True)

    # Write JSON lag index
    with open("docs/ops/response_time_lag_index.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print("docs/ops/response_time_lag_index.json written successfully.")

    # Write Markdown SSOT
    table_content = "\n## Current Work & Dynamic Response Lags\n\n"
    if pr_table_rows:
        table_content += "| PR/Issue | Message Response Lag (Acknowledge) | Programmatic Response Lag (Commit/Review) | State |\n|---|---|---|---|\n"
        table_content += "\n".join(pr_table_rows) + "\n"
    else:
        table_content += "*No summon events/responses detected in recent history. Standard defaults applied.*\n"

    # Add historical averages
    g_avg = metrics["global_averages"]
    table_content += f"\n### Calculated Global Averages\n"
    table_content += f"- **Average Message Acknowledgment Lag:** {round(g_avg['avg_message_response_lag_sec'] / 60, 1)} minutes\n"
    table_content += f"- **Average Actual Programmatic Lag:** {round(g_avg['avg_actual_response_lag_sec'] / 3600, 1)} hours\n"
    table_content += f"- **Dynamic Debounce Window:** {round(g_avg['suggested_debounce_ms'] / 60000, 1)} minutes\n"
    table_content += f"- **Dynamic Stale Window:** {round(g_avg['suggested_stale_ms'] / 3600000, 1)} hours\n"

    # Add tracing of related issues
    table_content += """
### Monorepo Coordination Trace

This lane consolidation integrates and coordinates with the following historical and active work items:

- **Issue #118:** Context continuity (Session && Context Management)
- **Issue #109:** DeepSeek CI integration
- **Issue #112:** Executable workflow + ephemeral session policy
- **Issue #114:** Peer routing + web-wrapper opt-in
- **Issue #72:** Quota + session continuation foundations
- **PR #3:** Untrack historical session stores
"""

    ssot_content = COOLDOWN_CONFIGS + table_content
    with open("docs/ops/LANE_CONSOLIDATION_SSOT.md", "w") as f:
        f.write(ssot_content)
    print("docs/ops/LANE_CONSOLIDATION_SSOT.md updated successfully.")

if __name__ == "__main__":
    main()
