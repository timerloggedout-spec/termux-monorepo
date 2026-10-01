#!/usr/bin/env python3
"""Colab GitHub Actions Integration - Run Colab workflows from GitHub Actions.

This module provides:
- GitHub Actions workflow integration
- Colab execution from workflows
- Result reporting
- Artifact management
- Environment configuration
"""

import os
import sys
import json
import time
import base64
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator
from dataclasses import dataclass, field

from .colab_client import ColabClient
from .colab_backend import ColabNotebook, ColabCell


@dataclass
class GithubActionsContext:
    """GitHub Actions context information."""
    workflow: str = ""
    run_number: str = ""
    run_id: str = ""
    job: str = ""
    step: str = ""
    actor: str = ""
    repository: str = ""
    ref: str = ""
    sha: str = ""
    workspace: str = ""
    
    @classmethod
    def from_environment(cls) -> "GithubActionsContext":
        """Create context from GitHub Actions environment variables."""
        return cls(
            workflow=os.environ.get("GITHUB_WORKFLOW", ""),
            run_number=os.environ.get("GITHUB_RUN_NUMBER", ""),
            run_id=os.environ.get("GITHUB_RUN_ID", ""),
            job=os.environ.get("GITHUB_JOB", ""),
            step=os.environ.get("GITHUB_STEP", ""),
            actor=os.environ.get("GITHUB_ACTOR", ""),
            repository=os.environ.get("GITHUB_REPOSITORY", ""),
            ref=os.environ.get("GITHUB_REF", ""),
            sha=os.environ.get("GITHUB_SHA", ""),
            workspace=os.environ.get("GITHUB_WORKSPACE", ""),
        )


@dataclass
class ColabWorkflowResult:
    """Result of a Colab workflow execution."""
    success: bool
    notebook_id: str
    execution_id: str
    outputs: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "notebook_id": self.notebook_id,
            "execution_id": self.execution_id,
            "outputs": self.outputs,
            "errors": self.errors,
            "duration": self.duration,
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ColabGithubActions:
    """Colab integration for GitHub Actions.
    
    This class provides:
    - Workflow execution from GitHub Actions
    - Result reporting
    - Artifact management
    - Environment configuration
    """
    
    def __init__(
        self,
        colab_client: Optional[ColabClient] = None,
        context: Optional[GithubActionsContext] = None,
        **kwargs
    ):
        """Initialize GitHub Actions integration.
        
        Args:
            colab_client: Colab client instance
            context: GitHub Actions context
        """
        self.colab_client = colab_client or ColabClient(**kwargs)
        self.context = context or GithubActionsContext.from_environment()
        self._start_time = time.time()
    
    def execute_workflow(
        self,
        notebook_id: Optional[str] = None,
        steps: List[Dict[str, Any]] = None,
    ) -> ColabWorkflowResult:
        """Execute a Colab workflow from GitHub Actions.
        
        Args:
            notebook_id: Notebook ID to use
            steps: Workflow steps
            
        Returns:
            Workflow result
        """
        start_time = time.time()
        errors = []
        outputs = []
        execution_id = f"gha-{self.context.run_id}-{int(time.time())}"
        
        try:
            # Load or create notebook
            if notebook_id:
                notebook = self.colab_client.get_notebook(notebook_id)
            else:
                notebook = self.colab_client.create_notebook(
                    name=f"GHA-{self.context.workflow}-{self.context.run_number}"
                )
                notebook_id = notebook.notebook_id
            
            # Add workflow metadata
            self._add_workflow_metadata(notebook, execution_id)
            
            # Execute steps
            for step in steps:
                try:
                    step_result = self._execute_step(notebook_id, step)
                    outputs.append(step_result)
                except Exception as e:
                    errors.append(str(e))
                    # Add error to notebook
                    self.colab_client.add_markdown_cell(
                        f"## Error in step {step.get('name', 'unnamed')}\n\n{e}",
                        notebook_id
                    )
            
            # Save notebook
            self.colab_client.save_notebook(notebook)
            
            return ColabWorkflowResult(
                success=len(errors) == 0,
                notebook_id=notebook_id,
                execution_id=execution_id,
                outputs=outputs,
                errors=errors,
                duration=time.time() - start_time,
                metadata={
                    "workflow": self.context.workflow,
                    "run_number": self.context.run_number,
                    "run_id": self.context.run_id,
                    "repository": self.context.repository,
                    "ref": self.context.ref,
                    "sha": self.context.sha,
                }
            )
        except Exception as e:
            return ColabWorkflowResult(
                success=False,
                notebook_id=notebook_id or "",
                execution_id=execution_id,
                errors=[str(e)],
                duration=time.time() - start_time,
            )
    
    def _add_workflow_metadata(self, notebook: ColabNotebook, execution_id: str):
        """Add workflow metadata to notebook."""
        metadata_cell = f"""# GitHub Actions Workflow Execution

**Execution ID:** {execution_id}
**Workflow:** {self.context.workflow}
**Run Number:** {self.context.run_number}
**Run ID:** {self.context.run_id}
**Repository:** {self.context.repository}
**Ref:** {self.context.ref}
**SHA:** {self.context.sha}
**Actor:** {self.context.actor}

---

## Execution Details

**Started:** {time.ctime(self._start_time)}
**Status:** Running
"""
        self.colab_client.add_markdown_cell(metadata_cell, notebook.notebook_id)
    
    def _execute_step(
        self,
        notebook_id: str,
        step: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single workflow step.
        
        Args:
            notebook_id: Notebook ID
            step: Step configuration
            
        Returns:
            Step result
        """
        action = step.get("action", "execute")
        
        if action == "execute":
            code = step.get("code", "")
            result = self.colab_client.execute(code, notebook_id)
            return {"action": "execute", "code": code, "result": result}
        
        elif action == "add_cell":
            cell_type = step.get("cell_type", "code")
            source = step.get("source", "")
            cell = self.colab_client.add_code_cell(source, notebook_id)
            return {"action": "add_cell", "cell_type": cell_type, "cell": cell.to_dict()}
        
        elif action == "markdown":
            markdown = step.get("markdown", "")
            cell = self.colab_client.add_markdown_cell(markdown, notebook_id)
            return {"action": "markdown", "cell": cell.to_dict()}
        
        elif action == "save":
            notebook = self.colab_client.get_notebook(notebook_id)
            saved = self.colab_client.save_notebook(notebook)
            return {"action": "save", "saved": saved}
        
        elif action == "restart":
            restarted = self.colab_client.restart_runtime(notebook_id)
            return {"action": "restart", "restarted": restarted}
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def report_result(self, result: ColabWorkflowResult):
        """Report workflow result to GitHub Actions.
        
        Args:
            result: Workflow result
        """
        # Set output variables
        self._set_output("notebook_id", result.notebook_id)
        self._set_output("execution_id", result.execution_id)
        self._set_output("success", str(result.success).lower())
        self._set_output("duration", str(result.duration))
        
        # Set error output if any
        if result.errors:
            self._set_output("errors", json.dumps(result.errors))
        
        # Log summary
        print(f"::notice::Colab Workflow {result.execution_id}")
        print(f"::notice::Notebook: {result.notebook_id}")
        print(f"::notice::Success: {result.success}")
        print(f"::notice::Duration: {result.duration:.2f}s")
        
        if result.errors:
            for error in result.errors:
                print(f"::error::Colab Error: {error}")
    
    def _set_output(self, name: str, value: str):
        """Set GitHub Actions output variable.
        
        Args:
            name: Variable name
            value: Variable value
        """
        print(f"::set-output name={name}::{value}")
    
    def create_artifact(
        self,
        notebook_id: str,
        name: str = "colab-notebook",
    ) -> bool:
        """Create GitHub Actions artifact from notebook.
        
        Args:
            notebook_id: Notebook ID
            name: Artifact name
            
        Returns:
            True if successful
        """
        try:
            notebook = self.colab_client.get_notebook(notebook_id)
            
            # Export notebook to JSON
            notebook_json = notebook.to_json()
            
            # Create artifact directory
            artifact_dir = Path(os.environ.get("GITHUB_WORKSPACE", ".")) / "artifacts" / name
            artifact_dir.mkdir(parents=True, exist_ok=True)
            
            # Save notebook
            notebook_path = artifact_dir / f"{notebook.name or notebook_id}.ipynb"
            notebook_path.write_text(notebook_json, encoding="utf-8")
            
            # Save metadata
            metadata = {
                "execution_id": f"gha-{self.context.run_id}",
                "notebook_id": notebook_id,
                "workflow": self.context.workflow,
                "run_number": self.context.run_number,
                "timestamp": time.ctime(),
            }
            metadata_path = artifact_dir / "metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            
            return True
        except Exception as e:
            print(f"Error creating artifact: {e}", file=sys.stderr)
            return False
    
    def upload_artifact(
        self,
        notebook_id: str,
        name: str = "colab-notebook",
    ) -> bool:
        """Upload notebook as GitHub Actions artifact.
        
        Args:
            notebook_id: Notebook ID
            name: Artifact name
            
        Returns:
            True if successful
        """
        if self.create_artifact(notebook_id, name):
            # GitHub Actions will automatically upload artifacts
            # from the artifacts directory
            return True
        return False
    
    def get_environment(self) -> Dict[str, str]:
        """Get GitHub Actions environment variables.
        
        Returns:
            Dictionary of environment variables
        """
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith("GITHUB_"):
                env_vars[key] = value
        return env_vars
    
    def configure_from_secrets(
        self,
        cookie_secret: str = "COLAB_COOKIES",
        notebook_secret: str = "COLAB_NOTEBOOK_ID",
    ):
        """Configure from GitHub secrets.
        
        Args:
            cookie_secret: Name of secret containing cookies
            notebook_secret: Name of secret containing notebook ID
        """
        # Get cookies from secret
        cookies = os.environ.get(cookie_secret)
        if cookies:
            # Save to temporary file
            cookie_path = Path(f"/tmp/colab_cookies_{os.getpid()}.json")
            cookie_path.write_text(cookies, encoding="utf-8")
            self.colab_client = ColabClient(cookie_path=str(cookie_path))
        
        # Get notebook ID from secret
        notebook_id = os.environ.get(notebook_secret)
        if notebook_id:
            self.default_notebook_id = notebook_id
            self.colab_client.default_notebook_id = notebook_id
    
    def run_from_workflow(
        self,
        workflow_file: Union[str, Path],
    ) -> ColabWorkflowResult:
        """Run workflow from YAML file.
        
        Args:
            workflow_file: Path to workflow YAML file
            
        Returns:
            Workflow result
        """
        import yaml
        
        with open(workflow_file) as f:
            workflow = yaml.safe_load(f)
        
        steps = workflow.get("steps", [])
        notebook_id = workflow.get("notebook_id")
        
        return self.execute_workflow(notebook_id, steps)


# =============================================================================
# Convenience Functions for GitHub Actions
# =============================================================================

_default_gha: Optional[ColabGithubActions] = None


def get_github_actions() -> ColabGithubActions:
    """Get the default GitHub Actions integration.
    
    Returns:
        ColabGithubActions instance
    """
    global _default_gha
    
    if _default_gha is None:
        _default_gha = ColabGithubActions()
    
    return _default_gha


def run_colab_workflow(
    notebook_id: Optional[str] = None,
    steps: Optional[List[Dict[str, Any]]] = None,
    workflow_file: Optional[str] = None,
) -> ColabWorkflowResult:
    """Run a Colab workflow from GitHub Actions.
    
    Args:
        notebook_id: Notebook ID
        steps: Workflow steps
        workflow_file: Path to workflow YAML file
        
    Returns:
        Workflow result
    """
    gha = get_github_actions()
    
    if workflow_file:
        return gha.run_from_workflow(workflow_file)
    
    return gha.execute_workflow(notebook_id, steps)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "ColabGithubActions",
    "GithubActionsContext",
    "ColabWorkflowResult",
    "get_github_actions",
    "run_colab_workflow",
]
