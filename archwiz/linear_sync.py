#!/usr/bin/env python3
"""
Linear Sync Bridge for ArchWiz.

Syncs local task status (taDone.md / master_tasks.json) to Linear.app
using the Linear GraphQL API when LINEAR_API_KEY is set.

Falls back to dry-run / report mode when the key is absent so the bridge
remains usable for agents and CI without secrets.

Requires: requests (stdlib urllib used as fallback)
Optional: Sentry via archwiz.sentry_init
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add root to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from archwiz.config import ARCHWIZ_DIR, WORKSPACE_DIR, LOG_DIR

try:
    from archwiz.sentry_init import init_sentry, capture_exception, capture_message
    init_sentry()
except Exception:
    def capture_exception(exc):  # type: ignore
        pass
    def capture_message(msg, level="info"):  # type: ignore
        pass

LINEAR_API = "https://api.linear.app/graphql"
TEAM_KEY = os.environ.get("LINEAR_TEAM", "Termux-monorepo_linear")


def _http_post(url: str, headers: Dict[str, str], body: dict) -> dict:
    """Minimal HTTP POST with requests or urllib."""
    try:
        import requests
        r = requests.post(url, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        return r.json()
    except ImportError:
        import urllib.request
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))


def get_tasks() -> List[Dict[str, Any]]:
    master_tasks = ARCHWIZ_DIR / "master_tasks.json"
    if not master_tasks.exists():
        return []
    try:
        with open(master_tasks, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Failed to read {master_tasks}: {exc}", file=sys.stderr)
        capture_exception(exc)
        return []
    if isinstance(data, dict):
        data = data.get("tasks", [])
    if not isinstance(data, list):
        print(f"Unexpected task format in {master_tasks}", file=sys.stderr)
        return []
    return [t for t in data if isinstance(t, dict)]
ture/sentry-linear-integration

def get_done_tasks() -> List[str]:
    tadone = WORKSPACE_DIR / "termux-multi-agent" / "taDone.md"
    if tadone.exists():
        return tadone.read_text(encoding="utf-8").splitlines()
    # also check archwiz/taDone.md symlink target
    alt = ARCHWIZ_DIR / "taDone.md"
    if alt.exists():
        return alt.read_text(encoding="utf-8").splitlines()
    return []


def linear_query(api_key: str, query: str, variables: Optional[dict] = None) -> dict:
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    body = {"query": query, "variables": variables or {}}
    result = _http_post(LINEAR_API, headers, body)
    if "errors" in result:
        raise RuntimeError(f"Linear GraphQL errors: {result['errors']}")
    return result.get("data", {})


def find_issue_by_identifier(api_key: str, identifier: str) -> Optional[dict]:
    """Look up Linear issue by identifier e.g. TER-5."""
    q = """
    query($id: String!) {
      issue(id: $id) {
        id
        identifier
        title
        state { id name type }
      }
    }
    """
    try:
        data = linear_query(api_key, q, {"id": identifier})
        return data.get("issue")
    except Exception:
        # fallback: search by number
        try:
            num = int(identifier.split("-")[-1])
        except ValueError:
            return None
        q2 = """
        query($filter: IssueFilter) {
          issues(filter: $filter, first: 1) {
            nodes { id identifier title state { id name type } }
          }
        }
        """
        data = linear_query(api_key, q2, {"filter": {"number": {"eq": num}}})
        nodes = data.get("issues", {}).get("nodes", [])
        return nodes[0] if nodes else None


def update_issue_state(api_key: str, issue_id: str, state_id: str) -> bool:
    q = """
    mutation($id: String!, $stateId: String!) {
      issueUpdate(id: $id, input: { stateId: $stateId }) {
        success
        issue { id identifier state { name } }
      }
    }
    """
    data = linear_query(api_key, q, {"id": issue_id, "stateId": state_id})
    return bool(data.get("issueUpdate", {}).get("success"))


def list_team_states(api_key: str, team_name: str) -> Dict[str, str]:
    """Return map of state name (lower) -> state id."""
    q = """
    query($name: String!) {
      teams(filter: { name: { eq: $name } }) {
        nodes {
          id
          states { nodes { id name type } }
        }
      }
    }
    """
    data = linear_query(api_key, q, {"name": team_name})
    teams = data.get("teams", {}).get("nodes", [])
    if not teams:
        q2 = """
        query {
          teams {
            nodes { id name key states { nodes { id name type } } }
          }
        }
        """
        data = linear_query(api_key, q2)
        teams = data.get("teams", {}).get("nodes", [])
    mapping: Dict[str, str] = {}
    for t in teams:
        for s in t.get("states", {}).get("nodes", []):
            mapping[s["name"].lower()] = s["id"]
            mapping[s["type"].lower()] = s["id"]
    return mapping


def sync_to_linear(dry_run: bool = False) -> None:
    print("--- Linear Sync Bridge ---")
    tasks = get_tasks()
    done_lines = get_done_tasks()
    print(f"Found {len(tasks)} tasks in master_tasks.json")
    print(f"Found {len(done_lines)} entries in taDone.md")

    api_key = os.environ.get("LINEAR_API_KEY") or os.environ.get("LINEAR_API_TOKEN")
    if not api_key:
        print("LINEAR_API_KEY not set — running in report-only mode.")
        dry_run = True

    states: Dict[str, str] = {}
    if not dry_run and api_key:
        try:
            states = list_team_states(api_key, TEAM_KEY)
            print(f"Loaded {len(states)} Linear states")
        except Exception as exc:
            print(f"Failed to load Linear states: {exc}", file=sys.stderr)
            capture_exception(exc)
            dry_run = True

    done_state_id = states.get("done") or states.get("completed")
    todo_state_id = states.get("todo") or states.get("unstarted") or states.get("backlog")

    for task in tasks:
        task_id = str(task.get("id") or task.get("identifier") or "")
        title = task.get("title") or task.get("name") or task_id
        is_done = any(task_id and task_id in line for line in done_lines)
        status = "DONE" if is_done else "TODO"
        print(f"  [{task_id}] {title[:60]} -> {status}")

        if dry_run or not api_key or not task_id:
            continue

        try:
            issue = find_issue_by_identifier(api_key, task_id)
            if not issue:
                print(f"    (no Linear issue for {task_id})")
                continue
            target_state = done_state_id if is_done else todo_state_id
            if not target_state:
                print("    (no matching state id)")
                continue
            current = (issue.get("state") or {}).get("name", "").lower()
            if (is_done and current in ("done", "completed")) or (
                not is_done and current in ("todo", "backlog", "unstarted")
            ):
                print("    (already in correct state)")
                continue
            ok = update_issue_state(api_key, issue["id"], target_state)
            print(f"    updated: {ok}")
            if ok:
                capture_message(f"Linear sync: {task_id} -> {status}")
        except Exception as exc:
            print(f"    error: {exc}", file=sys.stderr)
            capture_exception(exc)

    print("Sync complete.")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv or "-n" in sys.argv
    sync_to_linear(dry_run=dry)ture/sentry-linear-integration
