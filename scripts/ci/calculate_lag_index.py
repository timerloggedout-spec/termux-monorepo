#!/usr/bin/env python3
"""Compute response-time lag index for continuous-ops dynamic debounce/stale windows.
Fixes #155. Soft-fails without token (writes fallback JSON + SSOT table section).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

DEFAULT_DEBOUNCE_SEC = 45 * 60
DEFAULT_STALE_SEC = 2 * 60 * 60

def github_api_request(url: str, token: str | None):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "termux-monorepo-lag-index")
    req.add_header("Accept", "application/vnd.github.v3+json")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"API Error for {url}: {e}", file=sys.stderr)
        return None

def parse_iso8601(ts_str: str | None):
    if not ts_str:
        return None
    try:
        clean_ts = ts_str.replace("Z", "+00:00") if ts_str.endswith("Z") else ts_str
        dt = datetime.fromisoformat(clean_ts)
        return dt.replace(tzinfo=None) if dt.tzinfo else dt
    except ValueError:
        try:
            return datetime.strptime(ts_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return None

def write_outputs(metrics: dict, table_rows: list[str]) -> None:
    os.makedirs("docs/ops", exist_ok=True)
    with open("docs/ops/response_time_lag_index.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        f.write("\n")
    print("docs/ops/response_time_lag_index.json written")

    ssot_path = "docs/ops/LANE_CONSOLIDATION_SSOT.md"
    marker = "\n## Current Work & Dynamic Response Lags\n"
    g = metrics["global_averages"]
    table = marker + "\n"
    if table_rows:
        table += "| PR/Issue | Message Response Lag | Programmatic Response Lag | State |\n|---|---|---|---|\n"
        table += "\n".join(table_rows) + "\n"
    else:
        table += "*No summon events in recent history; defaults applied.*\n"
    table += (
        f"\n### Calculated Global Averages\n"
        f"- Message ack lag: {round(g['avg_message_response_lag_sec'] / 60, 1)} min\n"
        f"- Programmatic lag: {round(g['avg_actual_response_lag_sec'] / 3600, 1)} h\n"
        f"- Suggested debounce: {round(g['suggested_debounce_ms'] / 60000, 1)} min\n"
        f"- Suggested stale: {round(g['suggested_stale_ms'] / 3600000, 1)} h\n"
    )
    if os.path.exists(ssot_path):
        text = open(ssot_path, encoding="utf-8").read()
        if marker.strip() in text:
            idx = text.find(marker.strip())
            if idx >= 0:
                pre = text[:idx].rstrip()
                text = pre + "\n" + table
            else:
                text = text.rstrip() + "\n" + table
        else:
            text = text.rstrip() + "\n" + table
        open(ssot_path, "w", encoding="utf-8").write(text)
        print(f"{ssot_path} updated with lag table")
    else:
        open(ssot_path, "w", encoding="utf-8").write("# Lane Consolidation SSOT\n" + table)

def main() -> None:
    token = (
        os.environ.get("OPERATOR_GITHUB_TOKEN")
        or os.environ.get("OPERATOR_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
    )
    repo = os.environ.get("GITHUB_REPOSITORY") or "timerloggedout-spec/termux-monorepo"
    metrics = {
        "schema_version": 2,
        "disposition_model": {
            "summon": "opsSweep / auto-jules / explicit review request",
            "ack_pending": "bot promised review — NOT actionable for Jules",
            "quota_cooldown": "rate/review limit — WAIT until wait_until",
            "real_review": "substantive findings — actionable",
            "programmatic": "commit after summon"
        },
        "canonical_premature_pair": {
            "pr": 174,
            "ack_comment_id": 5260135328,
            "premature_jules_comment_id": 5260137282,
            "lesson": "Do not fire Jules on CodeRabbit 'I will re-review' ACK; wait for real_review"
        },
        "global_averages": {
            "avg_message_response_lag_sec": DEFAULT_DEBOUNCE_SEC,
            "avg_actual_response_lag_sec": DEFAULT_STALE_SEC,
            "suggested_debounce_ms": DEFAULT_DEBOUNCE_SEC * 1000,
            "suggested_stale_ms": DEFAULT_STALE_SEC * 1000,
        },
        "by_pr": {
            "174": {
                "open_disposition": "ack_pending",
                "jules_actionable": False,
                "wait_sec": 1200,
                "note": "CodeRabbit full review ACK at 5260135328; auto-jules 5260137282 was premature"
            }
        },
        "note": "Defaults aligned with high-perf continuous-ops. Recalculated by scripts/ci/calculate_lag_index.py on cron."
    }
    table_rows: list[str] = [
        "| PR #174 | N/A | N/A | CLOSED |"
    ]

    if not token:
        print("No token; writing fallback lag index", file=sys.stderr)
        write_outputs(metrics, table_rows)
        return

    open_prs = github_api_request(
        f"https://api.github.com/repos/{repo}/pulls?state=open&per_page=30", token
    ) or []
    closed_prs = github_api_request(
        f"https://api.github.com/repos/{repo}/pulls?state=closed&per_page=20", token
    ) or []
    all_prs = open_prs + closed_prs
    all_message_lags: list[float] = []
    all_actual_lags: list[float] = []
    agent_logins = [
        "google-labs-jules",
        "devin-ai-integration",
        "coderabbitai",
        "github-actions",
        "copilot",
        "gitar-bot",
        "blocksorg",
    ]

    def is_agent(username: str) -> bool:
        u = (username or "").lower()
        return any(a in u for a in agent_logins)

    for pr in all_prs:
        pr_number = pr["number"]
        comments = github_api_request(
            f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments?per_page=100",
            token,
        ) or []
        commits = github_api_request(
            f"https://api.github.com/repos/{repo}/pulls/{pr_number}/commits?per_page=100",
            token,
        ) or []
        timeline = []
        for c in comments:
            t = parse_iso8601(c.get("created_at"))
            if t:
                timeline.append(
                    {
                        "type": "comment",
                        "user": (c.get("user") or {}).get("login") or "unknown",
                        "body": c.get("body") or "",
                        "time": t,
                    }
                )
        for commit in commits:
            meta = commit.get("commit") or {}
            committer = meta.get("committer") or meta.get("author") or {}
            t = parse_iso8601(committer.get("date"))
            if t:
                timeline.append({"type": "commit", "user": "unknown", "time": t})
        timeline.sort(key=lambda x: x["time"])

        summon_time = None
        pr_message_lags: list[float] = []
        pr_actual_lags: list[float] = []
        actual_response_time = None
        message_response_time = None

        # v2 classification state
        open_disposition = "programmatic"
        jules_actionable = False
        wait_sec = 0

        for event in timeline:
            if event["type"] == "comment":
                body = event["body"]
                body_lower = body.lower()

                # Check for v2 classification
                # 1. Check for quota/cooldown keywords
                if any(k in body_lower for k in ("limit exceeded", "quota", "cooldown", "rate limit", "usage limit", "free-tier", "rate_limit", "hourly limit")):
                    open_disposition = "quota_cooldown"
                    jules_actionable = False
                    wait_sec = 3600
                # 2. Check for ack pending keywords
                elif any(k in body_lower for k in ("i will re-review", "promised review", "will look at", "i'll review", "ack", "review scheduled", "queued", "acknowledged")):
                    open_disposition = "ack_pending"
                    jules_actionable = False
                    wait_sec = 1200
                # 3. Check for summon keywords
                elif any(k in body_lower for k in ("<!-- continuous-agent-ops -->", "<!-- agent-auto-jules -->", "@jules", "@gemini-cli")):
                    open_disposition = "summon"
                    jules_actionable = True
                    wait_sec = 0
                # 4. Check for real review keywords
                elif any(k in body_lower for k in ("findings", "approved", "changes requested", "review complete", "lgtm", "looks good", "reviewed by")):
                    open_disposition = "real_review"
                    jules_actionable = True
                    wait_sec = 0

                is_summon = any(
                    m in body
                    for m in (
                        "<!-- continuous-agent-ops -->",
                        "<!-- agent-auto-jules -->",
                        "@jules",
                        "@gemini-cli",
                    )
                )
                if is_summon:
                    summon_time = event["time"]
                    message_response_time = None
                    actual_response_time = None
                    continue
                if summon_time and not message_response_time and is_agent(event["user"]):
                    message_response_time = event["time"]
                    lag = (message_response_time - summon_time).total_seconds()
                    pr_message_lags.append(lag)
                    all_message_lags.append(lag)
            elif event["type"] == "commit":
                open_disposition = "programmatic"
                jules_actionable = False
                wait_sec = 0
                if summon_time and not actual_response_time:
                    actual_response_time = event["time"]
                    lag = (actual_response_time - summon_time).total_seconds()
                    pr_actual_lags.append(lag)
                    all_actual_lags.append(lag)

        pr_avg_msg = sum(pr_message_lags) / len(pr_message_lags) if pr_message_lags else None
        pr_avg_act = sum(pr_actual_lags) / len(pr_actual_lags) if pr_actual_lags else None

        suggested_debounce = max(30 * 60, (pr_avg_msg or DEFAULT_DEBOUNCE_SEC) * 1.5)
        suggested_stale = max(60 * 60, (pr_avg_act or DEFAULT_STALE_SEC) * 1.5)

        # Merge calculated lags with classification state
        metrics["by_pr"][str(pr_number)] = {
            "avg_message_response_lag_sec": pr_avg_msg,
            "avg_actual_response_lag_sec": pr_avg_act,
            "suggested_debounce_ms": int(suggested_debounce * 1000),
            "suggested_stale_ms": int(suggested_stale * 1000),
            "open_disposition": open_disposition,
            "jules_actionable": jules_actionable,
            "wait_sec": wait_sec,
            "note": f"State computed automatically by lag compiler for PR {pr_number}."
        }
        msg_lag_str = f"{round(pr_avg_msg / 60, 1)} min" if pr_avg_msg else "N/A"
        act_lag_str = f"{round(pr_avg_act / 3600, 1)} hrs" if pr_avg_act else "N/A"
        table_rows.append(
            f"| PR #{pr_number} | {msg_lag_str} | {act_lag_str} | {pr['state'].upper()} |"
        )

    if all_message_lags:
        avg_msg = sum(all_message_lags) / len(all_message_lags)
        metrics["global_averages"]["avg_message_response_lag_sec"] = avg_msg
        metrics["global_averages"]["suggested_debounce_ms"] = int(
            max(30 * 60, avg_msg * 1.5) * 1000
        )
    if all_actual_lags:
        avg_act = sum(all_actual_lags) / len(all_actual_lags)
        metrics["global_averages"]["avg_actual_response_lag_sec"] = avg_act
        metrics["global_averages"]["suggested_stale_ms"] = int(
            max(60 * 60, avg_act * 1.5) * 1000
        )

    write_outputs(metrics, table_rows)

if __name__ == "__main__":
    main()
