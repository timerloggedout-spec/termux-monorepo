#!/usr/bin/env python3
"""Repository Harvester - Harvest code from Git repositories.

This module provides functionality to:
- Clone repositories
- Harvest code from repository history
- Extract commits, diffs, and file contents
- Work with local and remote repositories
"""

import os
import sys
import json
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Set, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from .file_harvester import FileHarvester, HarvestedFile


@dataclass
class HarvestedCommit:
    """Represents a harvested Git commit."""
    sha: str
    message: str
    author: str
    author_email: str
    date: str
    files_changed: List[str]
    insertions: int
    deletions: int
    diff: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sha": self.sha,
            "message": self.message,
            "author": self.author,
            "author_email": self.author_email,
            "date": self.date,
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "diff": self.diff,
            "metadata": self.metadata,
        }


@dataclass
class HarvestedRepository:
    """Represents a harvested repository."""
    name: str
    url: str
    local_path: str
    default_branch: str
    commits: List[HarvestedCommit] = field(default_factory=list)
    files: List[HarvestedFile] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "url": self.url,
            "local_path": self.local_path,
            "default_branch": self.default_branch,
            "commits": [c.to_dict() for c in self.commits],
            "files": [f.to_dict() for f in self.files],
            "metadata": self.metadata,
        }


class RepositoryHarvester:
    """Harvest code from Git repositories.
    
    This harvester provides functionality to:
    - Clone repositories (shallow or full)
    - Extract repository metadata
    - Harvest commits and their changes
    - Harvest files from specific branches or tags
    - Work with local repositories
    """
    
    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        file_harvester: Optional[FileHarvester] = None,
        clone_timeout: int = 300,  # 5 minutes
        max_depth: int = 10,  # Shallow clone depth
        include_submodules: bool = False,
        **kwargs
    ):
        """Initialize repository harvester.
        
        Args:
            cache_dir: Directory to cache cloned repositories
            file_harvester: FileHarvester instance for file harvesting
            clone_timeout: Timeout for clone operations (seconds)
            max_depth: Maximum depth for shallow clones
            include_submodules: Whether to include Git submodules
        """
        self.cache_dir = Path(cache_dir or (Path.home() / ".multi-ai-cli" / "repos"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.file_harvester = file_harvester or FileHarvester()
        self.clone_timeout = clone_timeout
        self.max_depth = max_depth
        self.include_submodules = include_submodules
        
        # Set restrictive permissions
        if self.cache_dir.exists() and not self.cache_dir.is_symlink():
            try:
                self.cache_dir.chmod(0o700)
            except Exception:
                pass
    
    def _run_git(self, args: List[str], cwd: Union[str, Path], timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """Run a Git command.
        
        Args:
            args: Git command arguments
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        cmd = ["git"] + args
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=timeout or self.clone_timeout,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)
    
    def _get_repo_name(self, url: str) -> str:
        """Extract repository name from URL."""
        # Remove .git suffix
        url = url.rstrip("/").rstrip(".git")
        
        # Extract name from URL
        if url.endswith(".git"):
            url = url[:-4]
        
        parts = url.split("/")
        if len(parts) >= 2:
            return f"{parts[-2]}_{parts[-1]}"
        return parts[-1]
    
    def _get_cache_path(self, url: str) -> Path:
        """Get cache path for a repository URL."""
        name = self._get_repo_name(url)
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
        return self.cache_dir / safe_name
    
    def clone(
        self,
        url: str,
        target_path: Optional[Union[str, Path]] = None,
        branch: Optional[str] = None,
        depth: Optional[int] = None,
        shallow: bool = True,
        **kwargs
    ) -> Path:
        """Clone a repository.
        
        Args:
            url: Repository URL
            target_path: Target path for clone (default: cache directory)
            branch: Branch to clone
            depth: Depth for shallow clone
            shallow: Whether to perform shallow clone
            
        Returns:
            Path to cloned repository
        """
        # Determine target path
        if target_path:
            clone_path = Path(target_path)
        else:
            clone_path = self._get_cache_path(url)
        
        # Check if already cloned
        if clone_path.exists():
            # Update existing clone
            rc, stdout, stderr = self._run_git(
                ["fetch", "--all", "--prune"],
                clone_path,
                timeout=60
            )
            if rc != 0:
                print(f"Failed to update {url}: {stderr}", file=sys.stderr)
            return clone_path
        
        # Create parent directory
        clone_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build clone command
        cmd = ["clone"]
        if shallow:
            cmd.append("--depth")
            cmd.append(str(depth or self.max_depth))
        if branch:
            cmd.append("--branch")
            cmd.append(branch)
        if self.include_submodules:
            cmd.append("--recurse-submodules")
        cmd.append(url)
        cmd.append(str(clone_path))
        
        # Execute clone
        rc, stdout, stderr = self._run_git(cmd, clone_path.parent, timeout=self.clone_timeout)
        
        if rc != 0:
            raise RuntimeError(f"Failed to clone {url}: {stderr}")
        
        # Set permissions
        if clone_path.exists() and not clone_path.is_symlink():
            try:
                clone_path.chmod(0o700)
            except Exception:
                pass
        
        return clone_path
    
    def get_repo_info(self, path: Union[str, Path]) -> Dict[str, Any]:
        """Get repository information.
        
        Args:
            path: Path to repository
            
        Returns:
            Dictionary with repository info
        """
        path = Path(path)
        
        # Get remote URL
        rc, url, _ = self._run_git(["remote", "get-url", "origin"], path)
        
        # Get default branch
        rc, branch, _ = self._run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], path)
        if rc != 0:
            rc, branch, _ = self._run_git(["branch", "-r", "--show-current"], path)
            if rc != 0:
                branch = "master"
        else:
            branch = branch.strip().split("/")[-1]
        
        # Get latest commit
        rc, commit, _ = self._run_git(["rev-parse", "HEAD"], path)
        
        # Get commit count
        rc, count, _ = self._run_git(["rev-list", "--count", "HEAD"], path)
        
        return {
            "path": str(path),
            "url": url.strip() if url else "",
            "default_branch": branch,
            "latest_commit": commit.strip() if commit else "",
            "commit_count": int(count.strip()) if count else 0,
        }
    
    def get_commit_history(
        self,
        path: Union[str, Path],
        branch: Optional[str] = None,
        max_commits: int = 100,
        since: Optional[str] = None,
        until: Optional[str] = None,
    ) -> Generator[HarvestedCommit, None, None]:
        """Get commit history.
        
        Args:
            path: Path to repository
            branch: Branch to get history from
            max_commits: Maximum number of commits to return
            since: Start date (ISO format)
            until: End date (ISO format)
            
        Yields:
            HarvestedCommit objects
        """
        path = Path(path)
        
        # Build git log command
        cmd = ["log", "--pretty=format:%H|%an|%ae|%ad|%s"]
        if branch:
            cmd.append(branch)
        if since:
            cmd.append(f"--since={since}")
        if until:
            cmd.append(f"--until={until}")
        cmd.append(f"-n{max_commits}")
        
        rc, output, _ = self._run_git(cmd, path)
        
        if rc != 0 or not output.strip():
            return
        
        for line in output.strip().split("\n"):
            if not line.strip():
                continue
            
            parts = line.split("|", 4)
            if len(parts) < 5:
                continue
            
            sha, author, author_email, date, message = parts[:5]
            
            # Get diff stats
            rc, stats, _ = self._run_git(
                ["show", "--stat", "--format=", sha],
                path
            )
            
            # Parse stats
            files_changed = []
            insertions = 0
            deletions = 0
            
            for stat_line in stats.strip().split("\n"):
                if not stat_line.strip():
                    continue
                if stat_line.startswith(" "):
                    files_changed.append(stat_line.strip())
                elif stat_line.endswith("insertion(s)"):
                    insertions = int(stat_line.split()[0])
                elif stat_line.endswith("deletion(s)"):
                    deletions = int(stat_line.split()[0])
            
            # Get full diff
            rc, diff, _ = self._run_git(
                ["show", sha],
                path
            )
            
            yield HarvestedCommit(
                sha=sha,
                message=message.strip(),
                author=author.strip(),
                author_email=author_email.strip(),
                date=date.strip(),
                files_changed=files_changed,
                insertions=insertions,
                deletions=deletions,
                diff=diff,
            )
    
    def get_file_history(
        self,
        path: Union[str, Path],
        file_path: str,
        max_commits: int = 100,
    ) -> Generator[Dict[str, Any], None, None]:
        """Get history of a specific file.
        
        Args:
            path: Path to repository
            file_path: Path to file within repository
            max_commits: Maximum number of commits to return
            
        Yields:
            Dictionary with commit info and file content
        """
        path = Path(path)
        
        # Get file history
        cmd = ["log", "--follow", "-p", "--pretty=format:%H|%an|%ad|%s", f"-n{max_commits}", "--", file_path]
        rc, output, _ = self._run_git(cmd, path)
        
        if rc != 0:
            return
        
        current_commit = None
        current_content = []
        
        for line in output.split("\n"):
            if line.startswith("commit ") or line.startswith("Author:"):
                continue
            
            if line and "|" in line and not line.startswith(" ") and current_commit is None:
                # New commit
                if current_content:
                    yield {
                        "commit": current_commit,
                        "content": "\n".join(current_content),
                    }
                    current_content = []
                
                parts = line.split("|", 3)
                if len(parts) >= 3:
                    current_commit = parts[0]
            elif current_commit is not None:
                current_content.append(line)
        
        # Yield last commit
        if current_commit and current_content:
            yield {
                "commit": current_commit,
                "content": "\n".join(current_content),
            }
    
    def harvest_repository(
        self,
        url: str,
        target_path: Optional[Union[str, Path]] = None,
        branch: Optional[str] = None,
        include_commits: bool = True,
        max_commits: int = 100,
        include_files: bool = True,
        file_extensions: Optional[Set[str]] = None,
        **kwargs
    ) -> HarvestedRepository:
        """Harvest a repository.
        
        Args:
            url: Repository URL
            target_path: Target path for clone
            branch: Branch to harvest
            include_commits: Whether to include commit history
            max_commits: Maximum number of commits to include
            include_files: Whether to include file contents
            file_extensions: File extensions to include
            
        Returns:
            HarvestedRepository object
        """
        # Clone repository
        clone_path = self.clone(url, target_path, branch)
        
        # Get repository info
        repo_info = self.get_repo_info(clone_path)
        
        # Harvest commits
        commits = []
        if include_commits:
            for commit in self.get_commit_history(clone_path, branch, max_commits):
                commits.append(commit)
        
        # Harvest files
        files = []
        if include_files:
            harvester = FileHarvester(
                base_path=clone_path,
                extensions=file_extensions,
            )
            files = list(harvester.harvest())
        
        return HarvestedRepository(
            name=self._get_repo_name(url),
            url=url,
            local_path=str(clone_path),
            default_branch=repo_info.get("default_branch", "master"),
            commits=commits,
            files=files,
            metadata=repo_info,
        )
    
    def harvest_to_json(
        self,
        url: str,
        output_path: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> str:
        """Harvest repository and return as JSON.
        
        Args:
            url: Repository URL
            output_path: Path to save JSON
            
        Returns:
            JSON string
        """
        repo = self.harvest_repository(url, **kwargs)
        data = repo.to_dict()
        json_str = json.dumps(data, indent=2)
        
        if output_path:
            Path(output_path).write_text(json_str, encoding="utf-8")
        
        return json_str
    
    def cleanup(self, path: Optional[Union[str, Path]] = None):
        """Clean up cached repositories.
        
        Args:
            path: Specific path to clean up (default: all)
        """
        if path:
            clean_path = Path(path)
            if clean_path.exists():
                try:
                    if clean_path.is_dir():
                        import shutil
                        shutil.rmtree(clean_path)
                    else:
                        clean_path.unlink()
                except Exception as e:
                    print(f"Failed to clean up {path}: {e}", file=sys.stderr)
        else:
            # Clean up all cached repos
            for repo_dir in self.cache_dir.iterdir():
                if repo_dir.is_dir():
                    self.cleanup(repo_dir)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "RepositoryHarvester",
    "HarvestedCommit",
    "HarvestedRepository",
]
