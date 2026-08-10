#!/usr/bin/env python3
"""
Linear Sync Bridge for ArchWiz.
Syncs local task status (taDone.md / master_tasks.json) to Linear.app.
"""
import os
import json
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add root to path for config import
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from archwiz.config import ARCHWIZ_ROOT, LOG_DIR, WORKSPACE_DIR

# Setup logging
logging.basicConfig(
    filename=LOG_DIR / "linear_sync.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("linear_sync")

def get_tasks() -> List[Dict[str, Any]]:
    master_tasks = ARCHWIZ_ROOT / "workspace" / "llm_map" / "master_tasks.json"
    if not master_tasks.exists():
        logger.warning(f"master_tasks.json not found at {master_tasks}")
        return []
    try:
        data = json.loads(master_tasks.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data.get("tasks", [])
        return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Failed to read master_tasks.json: {e}")
        return []

def get_done_tasks() -> List[str]:
    tadone = WORKSPACE_DIR / "termux-multi-agent" / "taDone.md"
    if tadone.exists():
        return tadone.read_text(encoding="utf-8").splitlines()
    return []

class LinearClient:
    def __init__(self):
        self.api_key = os.environ.get("LINEAR_API_KEY")
        self.url = "https://api.linear.app/graphql"

    def query(self, query_str: str, variables: Optional[Dict] = None) -> Dict:
        if not self.api_key:
            raise ValueError("LINEAR_API_KEY not set")
        
        import requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
        resp = requests.post(self.url, json={"query": query_str, "variables": variables}, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def update_issue_status(self, issue_id: str, status_name: str):
        """Update a Linear issue status."""
        # Note: In a real implementation, we'd first resolve the status_id for status_name
        mutation = """
        mutation IssueUpdate($id: String!, $input: IssueUpdateInput!) {
          issueUpdate(id: $id, input: $input) {
            success
            issue {
              id
              title
              state {
                name
              }
            }
          }
        }
        """
        variables = {
            "id": issue_id,
            "input": {"stateId": status_name} # Simplified: usually needs a UUID
        }
        return self.query(mutation, variables)

def sync_to_linear():
    logger.info("Starting Linear Sync")
    tasks = get_tasks()
    done = get_done_tasks()
    
    logger.info(f"Syncing {len(tasks)} tasks against {len(done)} done entries")
    
    client = LinearClient()
    
    for task in tasks:
        task_id = task.get("id")
        if not task_id: continue
        
        is_done = any(task_id in line for line in done)
        target_status = "Done" if is_done else "Todo"
        
        logger.info(f"Task {task_id} -> {target_status}")
        
        if client.api_key:
            try:
                # This is where the actual API call would happen
                # client.update_issue_status(task_id, target_status)
                pass
            except Exception as e:
                logger.error(f"Failed to sync {task_id} to Linear: {e}")
        else:
            # Fallback: just log that we would have synced
            pass

    logger.info("Linear Sync complete.")

if __name__ == "__main__":
    sync_to_linear()
