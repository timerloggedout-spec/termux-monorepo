#!/usr/bin/env python3
"""Git utilities for version control operations."""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rich.console import Console

console = Console()

class GitUtils:
    """Utilities for Git operations."""
    
    @staticmethod
    def is_git_repo(directory: str = ".") -> bool:
        """Check if directory is a Git repository."""
        git_dir = Path(directory) / ".git"
        return git_dir.exists()
    
    @staticmethod
    def get_git_root(directory: str = ".") -> Optional[str]:
        """Get the root directory of the Git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_current_branch(directory: str = ".") -> Optional[str]:
        """
        Get the current Git branch for a directory.
        
        Parameters:
        	directory (str): Path to the Git working directory.
        
        Returns:
        	Optional[str]: The current branch name, or `None` if Git cannot determine it.
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_commits(directory: str = ".", limit: int = 10) -> List[Dict]:
        """
        Retrieve recent commits from a Git repository.
        
        Parameters:
            directory (str): Repository directory to inspect.
            limit (int): Maximum number of commits to retrieve.
        
        Returns:
            List[Dict]: Commit records containing the hash, author, date, and message. Returns an empty list if the Git command fails.
        """
        try:
            result = subprocess.run(
                ["git", "log", f"-n{limit}", "--pretty=format:%H|%an|%ad|%s"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3],
                        })
                return commits
        except Exception:
            pass
        return []
    
    @staticmethod
    def get_status(directory: str = ".") -> Dict:
        """
        Categorize the working tree changes in a Git repository.
        
        Parameters:
        	directory (str): The repository directory to inspect.
        
        Returns:
        	Dict: A mapping of change categories to file paths, or an empty dictionary if the status cannot be retrieved.
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                status = {
                    "modified": [],
                    "added": [],
                    "deleted": [],
                    "untracked": [],
                }
                
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('M '):
                        status["modified"].append(line[2:])
                    elif line.startswith('A '):
                        status["added"].append(line[2:])
                    elif line.startswith('D '):
                        status["deleted"].append(line[2:])
                    elif line.startswith('??'):
                        status["untracked"].append(line[3:])
                
                return status
        except Exception:
            pass
        return {}
    
    @staticmethod
    def commit(message: str, directory: str = ".", all_files: bool = False) -> bool:
        """
        Stage changes and create a Git commit with the specified message.
        
        Parameters:
            message (str): Commit message.
            directory (str): Repository directory.
            all_files (bool): Whether to stage all files in the repository.
        
        Returns:
            bool: `True` if the changes are committed successfully, `False` otherwise.
        """
        try:
            # Add files
            add_cmd = ["git", "add", "."] if all_files else ["git", "add"]
            result = subprocess.run(
                add_cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                console.print(f"[red]Git add failed: {result.stderr}[/]")
                return False
            
            # Commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                console.print(f"[green]Committed: {result.stdout.strip()}[/]")
                return True
            else:
                console.print(f"[red]Git commit failed: {result.stderr}[/]")
                return False
        except Exception as e:
            console.print(f"[red]Git commit error: {e}[/]")
            return False
    
    @staticmethod
    def push(remote: str = "origin", branch: str = None, directory: str = ".") -> bool:
        """
        Push changes to a remote branch.
        
        Parameters:
            remote (str): Name of the remote repository.
            branch (str): Branch to push, or `None` to use the current branch.
            directory (str): Repository directory.
        
        Returns:
            bool: `True` if the push succeeds, `False` otherwise.
        """
        try:
            if branch is None:
                branch = GitUtils.get_current_branch(directory)
            
            if branch is None:
                console.print("[red]No branch specified and unable to determine current branch[/]")
                return False
            
            result = subprocess.run(
                ["git", "push", remote, branch],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                console.print(f"[green]Pushed to {remote}/{branch}[/]")
                return True
            else:
                console.print(f"[red]Git push failed: {result.stderr}[/]")
                return False
        except Exception as e:
            console.print(f"[red]Git push error: {e}[/]")
            return False
    
    @staticmethod
    def pull(remote: str = "origin", branch: str = None, directory: str = ".") -> bool:
        """
        Pull changes for a branch from a remote repository.
        
        Parameters:
        	remote (str): Name of the remote repository.
        	branch (str): Branch to pull; if omitted, uses the current branch.
        	directory (str): Repository directory.
        
        Returns:
        	bool: `True` if the pull succeeds, `False` otherwise.
        """
        try:
            if branch is None:
                branch = GitUtils.get_current_branch(directory)
            
            if branch is None:
                console.print("[red]No branch specified and unable to determine current branch[/]")
                return False
            
            result = subprocess.run(
                ["git", "pull", remote, branch],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                console.print(f"[green]Pulled from {remote}/{branch}[/]")
                return True
            else:
                console.print(f"[red]Git pull failed: {result.stderr}[/]")
                return False
        except Exception as e:
            console.print(f"[red]Git pull error: {e}[/]")
            return False
    
    @staticmethod
    def checkout(branch: str, directory: str = ".", create: bool = False) -> bool:
        """Switch to an existing branch or create and switch to a new branch.
        
        Parameters:
        	branch (str): Name of the branch to check out.
        	directory (str): Repository directory in which to perform the checkout.
        	create (bool): Whether to create the branch before switching to it.
        
        Returns:
        	bool: `True` if the checkout succeeds, `False` otherwise.
        """
        try:
            if create:
                result = subprocess.run(
                    ["git", "checkout", "-b", branch],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            else:
                result = subprocess.run(
                    ["git", "checkout", branch],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            
            if result.returncode == 0:
                console.print(f"[green]Checked out {branch}[/]")
                return True
            else:
                console.print(f"[red]Git checkout failed: {result.stderr}[/]")
                return False
        except Exception as e:
            console.print(f"[red]Git checkout error: {e}[/]")
            return False
    
    @staticmethod
    def clone(repository: str, directory: str = None, branch: str = None) -> bool:
        """
        Clone a Git repository to an optional destination.
        
        Parameters:
        	repository (str): The repository URL or source path.
        	directory (str, optional): The destination directory.
        	branch (str, optional): The branch to check out.
        
        Returns:
        	bool: `True` if cloning succeeds, `False` otherwise.
        """
        try:
            cmd = ["git", "clone", repository]
            if directory:
                cmd.append(directory)
            if branch:
                cmd.extend(["--branch", branch])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                console.print(f"[green]Cloned {repository}[/]")
                return True
            else:
                console.print(f"[red]Git clone failed: {result.stderr}[/]")
                return False
        except Exception as e:
            console.print(f"[red]Git clone error: {e}[/]")
            return False
    
    @staticmethod
    def get_diff(file_path: str = None, directory: str = ".") -> Optional[str]:
        """Retrieve the working-tree changes from a Git repository.
        
        Parameters:
            file_path (str, optional): Path to restrict the diff to.
            directory (str): Directory containing the Git repository.
        
        Returns:
            str or None: The Git diff output, or `None` if the command fails.
        """
        try:
            cmd = ["git", "diff"]
            if file_path:
                cmd.append(file_path)
            
            result = subprocess.run(
                cmd,
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_remotes(directory: str = ".") -> List[str]:
        """
        List Git remotes configured for a repository.
        
        Parameters:
            directory (str): Path to the Git repository.
        
        Returns:
            List[str]: Remote names reported by Git, including repeated entries for
                separate remote URLs.
        """
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                remotes = []
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 2:
                        remotes.append(parts[0])
                return remotes
        except Exception:
            pass
        return []

if __name__ == "__main__":
    # Example usage
    if GitUtils.is_git_repo():
        print("This is a Git repository")
        print(f"Current branch: {GitUtils.get_current_branch()}")
        print(f"Git root: {GitUtils.get_git_root()}")
        
        # Get recent commits
        commits = GitUtils.get_commits(limit=5)
        print(f"Recent commits: {len(commits)}")
        for commit in commits:
            print(f"  - {commit['hash'][:7]}: {commit['message']}")
        
        # Get status
        status = GitUtils.get_status()
        print(f"Status: {status}")
    else:
        print("Not a Git repository")
