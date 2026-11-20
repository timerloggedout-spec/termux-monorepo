#!/usr/bin/env python3
"""
Linear client CLI for agent hooks (on-device / CI).

Requires LINEAR_API_KEY. See docs/LINEAR-AGENT-PROTOCOL.md.

Usage:
  python3 -m archwiz.linear_client status TER-14
  python3 -m archwiz.linear_client start TER-14
  python3 -m archwiz.linear_client done TER-14 --pr 16
  python3 -m archwiz.linear_client comment TER-14 "PR opened: https://..."
  python3 -m archwiz.linear_client create --title "..." [--priority 2]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from archwiz.sentry_init import init_sentry, capture_exception
    init_sentry()
except Exception:
    def capture_exception(exc):  # type: ignore
        pass

LINEAR_API = "https://api.linear.app/graphql"
TEAM_NAME = os.environ.get("LINEAR_TEAM", "Termux-monorepo_linear")
PROJECT_NAME = os.environ.get("LINEAR_PROJECT", "termux-monorepo hardening")


def _api_key() -> str:
    key = os.environ.get("LINEAR_API_KEY") or os.environ.get("LINEAR_API_TOKEN")
    if not key:
        print("LINEAR_API_KEY not set", file=sys.stderr)
        sys.exit(2)
    return key


def _http_post(body: dict) -> dict:
    headers = {
        "Authorization": _api_key(),
        "Content-Type": "application/json",
    }
    try:
        import requests
        r = requests.post(LINEAR_API, headers=headers, json=body, timeout=30)
        r.raise_for_status()
        data = r.json()
    except ImportError:
        import urllib.request
        req = urllib.request.Request(
            LINEAR_API,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data.get("data", {})


def gql(query: str, variables: Optional[dict] = None) -> dict:
    return _http_post({"query": query, "variables": variables or {}})


def get_issue(identifier: str) -> Optional[dict]:
    q = """
    query($id: String!) {
      issue(id: $id) {
        id identifier title url priority
        state { id name type }
        assignee { name }
        project { name }
      }
    }
    """
    try:
        return gql(q, {"id": identifier}).get("issue")
    except Exception:
        # fallback by number
        try:
            num = int(identifier.split("-")[-1])
        except ValueError:
            return None
        q2 = """
        query($n: Float!) {
          issues(filter: { number: { eq: $n } }, first: 1) {
            nodes {
              id identifier title url priority
              state { id name type }
              assignee { name }
              project { name }
            }
          }
        }
        """
        nodes = gql(q2, {"n": float(num)}).get("issues", {}).get("nodes", [])
        return nodes[0] if nodes else None


def team_states() -> Dict[str, str]:
    q = """
    query {
      teams {
        nodes {
          name
          states { nodes { id name type } }
        }
      }
    }
    """
    data = gql(q)
    out: Dict[str, str] = {}
    for t in data.get("teams", {}).get("nodes", []):
        for s in t.get("states", {}).get("nodes", []):
            out[s["name"].lower()] = s["id"]
            out[s["type"].lower()] = s["id"]
    return out


def set_state(issue_id: str, state_id: str) -> bool:
    q = """
    mutation($id: String!, $stateId: String!) {
      issueUpdate(id: $id, input: { stateId: $stateId }) {
        success
        issue { identifier state { name } }
      }
    }
    """
    data = gql(q, {"id": issue_id, "stateId": state_id})
    return bool(data.get("issueUpdate", {}).get("success"))


def add_comment(issue_id: str, body: str) -> bool:
    q = """
    mutation($id: String!, $body: String!) {
      commentCreate(input: { issueId: $id, body: $body }) {
        success
      }
    }
    """
    data = gql(q, {"id": issue_id, "body": body})
    return bool(data.get("commentCreate", {}).get("success"))


def create_issue(title: str, description: str = "", priority: int = 0) -> Optional[dict]:
    # resolve team id
    tq = """
    query {
      teams { nodes { id name } }
    }
    """
    teams = gql(tq).get("teams", {}).get("nodes", [])
    team_id = None
    for t in teams:
        if t["name"] == TEAM_NAME or TEAM_NAME.lower() in t["name"].lower():
            team_id = t["id"]
            break
    if not team_id and teams:
        team_id = teams[0]["id"]
    if not team_id:
        raise RuntimeError("No Linear team found")

    q = """
    mutation($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        success
        issue { id identifier title url }
      }
    }
    """
    inp: Dict[str, Any] = {"teamId": team_id, "title": title}
    if description:
        inp["description"] = description
    if priority:
        inp["priority"] = priority
    data = gql(q, {"input": inp})
    return data.get("issueCreate", {}).get("issue")


def cmd_status(identifier: str) -> int:
    issue = get_issue(identifier)
    if not issue:
        print(f"Not found: {identifier}", file=sys.stderr)
        return 1
    state = (issue.get("state") or {}).get("name", "?")
    print(f"{issue['identifier']}  [{state}]  {issue.get('title')}")
    print(f"  url: {issue.get('url')}")
    if issue.get("assignee"):
        print(f"  assignee: {issue['assignee'].get('name')}")
    return 0


def cmd_start(identifier: str) -> int:
    issue = get_issue(identifier)
    if not issue:
        print(f"Not found: {identifier}", file=sys.stderr)
        return 1
    states = team_states()
    sid = states.get("in progress") or states.get("started")
    if not sid:
        print("No In Progress state", file=sys.stderr)
        return 1
    ok = set_state(issue["id"], sid)
    print(f"start {identifier}: {ok}")
    return 0 if ok else 1


def cmd_done(identifier: str, pr: Optional[int] = None) -> int:
    issue = get_issue(identifier)
    if not issue:
        print(f"Not found: {identifier}", file=sys.stderr)
        return 1
    states = team_states()
    sid = states.get("done") or states.get("completed")
    if not sid:
        print("No Done state", file=sys.stderr)
        return 1
    ok = set_state(issue["id"], sid)
    if ok and pr:
        add_comment(
            issue["id"],
            f"Completed via PR #{pr} (agent hook). See docs/LINEAR-AGENT-PROTOCOL.md.",
        )
    print(f"done {identifier}: {ok}")
    return 0 if ok else 1


def cmd_comment(identifier: str, body: str) -> int:
    issue = get_issue(identifier)
    if not issue:
        print(f"Not found: {identifier}", file=sys.stderr)
        return 1
    ok = add_comment(issue["id"], body)
    print(f"comment {identifier}: {ok}")
    return 0 if ok else 1


def cmd_create(title: str, description: str, priority: int) -> int:
    issue = create_issue(title, description, priority)
    if not issue:
        print("create failed", file=sys.stderr)
        return 1
    print(f"created {issue['identifier']}: {issue.get('url')}")
    return 0


def main(argv: Optional[list] = None) -> int:
    p = argparse.ArgumentParser(prog="linear_client")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("status")
    s.add_argument("id")

    s = sub.add_parser("start")
    s.add_argument("id")

    s = sub.add_parser("done")
    s.add_argument("id")
    s.add_argument("--pr", type=int, default=None)

    s = sub.add_parser("comment")
    s.add_argument("id")
    s.add_argument("body")

    s = sub.add_parser("create")
    s.add_argument("--title", required=True)
    s.add_argument("--description", default="")
    s.add_argument("--priority", type=int, default=0)

    args = p.parse_args(argv)
    try:
        if args.cmd == "status":
            return cmd_status(args.id)
        if args.cmd == "start":
            return cmd_start(args.id)
        if args.cmd == "done":
            return cmd_done(args.id, args.pr)
        if args.cmd == "comment":
            return cmd_comment(args.id, args.body)
        if args.cmd == "create":
            return cmd_create(args.title, args.description, args.priority)
    except Exception as exc:
        capture_exception(exc)
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    # support both `python -m archwiz.linear_client` and direct script
    raise SystemExit(main())
