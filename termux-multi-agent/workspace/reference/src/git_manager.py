import subprocess
import os
import time

class AgentGitManager:
    def __init__(self, workspace_root):
        self.workspace = os.path.abspath(workspace_root)
        self.identities = {
            "deepseek-v4-pro": {"name": "DeepSeek Coder Agent", "email": "v4pro@deepseek.agent"},
            "critic-judge": {"name": "Critic Judge Agent", "email": "judge@critic.agent"}
        }

    def create_feature_branch(self, base_branch="main"):
        if not os.path.exists(os.path.join(self.workspace, ".git")):
            subprocess.run(["git", "init"], cwd=self.workspace, capture_output=True)
            subprocess.run(["git", "add", "."], cwd=self.workspace, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial repository commit"], cwd=self.workspace, capture_output=True)
        branch_name = f"ai-refactor-{int(time.time())}"
        subprocess.run(["git", "checkout", base_branch], cwd=self.workspace, capture_output=True)
        result = subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.workspace, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to initialize Git branch: {result.stderr}")
        return branch_name

    def commit_as_agent(self, agent_id, commit_message, file_paths):
        identity = self.identities.get(agent_id, {"name": "Local Agent", "email": "agent@local.dev"})
        agent_env = os.environ.copy()
        agent_env["GIT_AUTHOR_NAME"] = identity["name"]
        agent_env["GIT_AUTHOR_EMAIL"] = identity["email"]
        agent_env["GIT_COMMITTER_NAME"] = identity["name"]
        agent_env["GIT_COMMITTER_EMAIL"] = identity["email"]
        for path in file_paths:
            subprocess.run(["git", "add", path], cwd=self.workspace, capture_output=True)
        result = subprocess.run(["git", "commit", "-m", commit_message], cwd=self.workspace, env=agent_env, capture_output=True, text=True)
        return result.returncode == 0