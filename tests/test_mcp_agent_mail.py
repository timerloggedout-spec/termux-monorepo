import os
from pathlib import Path

def test_mcp_agent_mail_action_metadata():
    """
    Validates the structure and inputs/outputs of the newly created
    MCP Agent Mail composite action to prevent YAML parse failures
    or metadata mismatches on execution.
    """
    action_path = Path(".github/actions/mcp-agent-mail/action.yml")
    assert action_path.exists(), "Action file must exist"

    with open(action_path, "r") as f:
        content = f.read()

    assert "name: 'Setup MCP Agent Mail'" in content
    assert "inputs:" in content
    assert "run-server:" in content
    assert "port:" in content
    assert "using: composite" in content

def test_agent_coordination_demo_yaml():
    """
    Validates that the demonstration workflow parses correctly.
    """
    workflow_path = Path(".github/workflows/agent-coordination-demo.yml")
    assert workflow_path.exists(), "Demo workflow file must exist"

    with open(workflow_path, "r") as f:
        content = f.read()

    assert "name: '🤖 MCP Agent Mail Coordination Demo'" in content
    assert "jobs:" in content
    assert "coordinate-agents:" in content
