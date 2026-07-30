#!/usr/bin/env python3
"""
Agent Execution CLI Wrapper - Per-role access control with command logging
Builds on CEDARscript principles with Utility Belt promotion system
"""
import sys
import os
import json
import subprocess
import logging
import time
import shlex
import fcntl
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================
================
# Configuration & Data Structures
# ============================================================
================

@dataclass
class CommandAttempt:
    """Record of a command execution attempt"""
    command: str
    role: str
    timestamp: float
    exit_code: int
    stdout: str
    stderr: str
    allowed: bool
    execution_time_ms: int
    promoted_to_utility: bool = False

class UtilityBelt:
    """Manages promotion of useful commands to utility belt status"""
    
    UTILITY_BELT_PATH = Path.home() / ".agent_cli_utility_belt.json"
    PROMOTION_THRESHOLD = 5  # Number of successful uses before promotion
    UTILITY_COMMANDS_PATH = Path("/usr/local/bin/agent-utils")
    
    @classmethod
    def load_stats(cls) -> Dict[str, int]:
        """Load command usage statistics"""
        if cls.UTILITY_BELT_PATH.exists():
            with open(cls.UTILITY_BELT_PATH, 'r') as f:
                return json.load(f)
        return {}
    
    @classmethod
    def save_stats(cls, stats: Dict[str, int]) -> None:
        """Save command usage statistics"""
        with open(cls.UTILITY_BELT_PATH, 'w') as f:
            json.dump(stats, f, indent=2)
    
    @classmethod
    def record_usage(cls, command: str, success: bool) -> bool:
        """Record command usage and return True if promoted to utility belt"""
        if not success:
            return False
        
        stats = cls.load_stats()
        base_cmd = command.split()[0] if command else command
        stats[base_cmd] = stats.get(base_cmd, 0) + 1
        
        promoted = False
        if stats[base_cmd] >= cls.PROMOTION_THRESHOLD:
            promoted = cls._promote_to_utility(base_cmd)
            if promoted:
                stats[f"{base_cmd}_promoted"] = stats.get(f"{base_cmd}_promoted", 0) + 1
        
        cls.save_stats(stats)
        return promoted
    
    @classmethod
    def _promote_to_utility(cls, command: str) -> bool:
        """Promote a command to the utility belt (create symlink/alias)"""
        try:
            cls.UTILITY_COMMANDS_PATH.mkdir(parents=True, exist_ok=True)
            
            # Find actual command path
            result = subprocess.run(
                ['which', command], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                cmd_path = result.stdout.strip()
                link_path = cls.UTILITY_COMMANDS_PATH / command
                
                if not link_path.exists():
                    os.symlink(cmd_path, link_path)
                    logging.info(f"Promoted '{command}' to Utility Belt: {link_path}")
                    return True
            
            return False
        except Exception as e:
            logging.error(f"Failed to promote '{command}' to utility belt: {e}")
            return False

class AccessPolicy:
    """Loads and validates access policies from JSON configuration"""
    
    DEFAULT_POLICY = {
        "roles": {
            "developer": {
                "allowed_commands": ["jq", "grep", "python3", "pip", "git", "make", "gcc", "clang"],
                "max_execution_time": 60,
                "requires_confirmation": False
            },
            "linguist": {
                "allowed_commands": ["jq", "gzip", "tar", "grep", "wc", "sort", "uniq"],
                "max_execution_time": 30,
                "requires_confirmation": False
            },
            "operator": {
                "allowed_commands": ["ls", "cat", "head", "tail", "echo", "printf", "wc"],
                "max_execution_time": 10,
                "requires_confirmation": True
            },
            "admin": {
                "allowed_commands": ["*"],
                "max_execution_time": 300,
                "requires_confirmation": False
            }
        },
        "blacklisted_patterns": [
            "rm -rf /", "dd if=", "mkfs", "format", "chmod 777",
            "> /dev/sda", "curl.*|.*sh", "wget.*|.*bash"
        ],
        "logging": {
            "log_file": "/var/log/agent_cli.log",
            "max_log_size_mb": 100,
            "log_commands": True,
            "log_output": True,
            "log_environment": False
        }
    }
    
    def __init__(self, policy_path: Optional[Path] = None):
        self.policy_path = policy_path or Path("access_policy.json")
        self.policy = self._load_policy()
        self._ensure_log_directory()
    
    def _load_policy(self) -> Dict:
        """Load policy from file or create default"""
        if self.policy_path.exists():
            try:
                with open(self.policy_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults for any missing keys
                    return self._merge_policy(self.DEFAULT_POLICY.copy(), loaded)
            except Exception as e:
                logging.error(f"Failed to load policy: {e}, using defaults")
        
        # Create default policy file
        self._save_policy(self.DEFAULT_POLICY)
        return self.DEFAULT_POLICY.copy()
    
    def _merge_policy(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two policy dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._merge_policy(base[key], value)
            else:
                base[key] = value
        return base
    
    def _save_policy(self, policy: Dict) -> None:
        """Save policy to file"""
        with open(self.policy_path, 'w') as f:
            json.dump(policy, f, indent=2)
    
    def _ensure_log_directory(self) -> None:
        """Ensure log directory exists"""
        log_path = Path(self.policy.get("logging", {}).get("log_file", "/var/log/agent_cli.log"))
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def is_command_allowed(self, command: str, role: str) -> Tuple[bool, str]:
        """Check if a command is allowed for the given role"""
        role_config = self.policy.get("roles", {}).get(role, {})
        
        if not role_config:
            return False, f"Role '{role}' not found in policy"
        
        allowed = role_config.get("allowed_commands", [])
        base_cmd = command.split()[0] if command else command
        
        # Check for wildcard (admin access)
        if "*" in allowed:
            # Still check blacklist
            if self._is_blacklisted(command):
                return False, f"Command pattern blacklisted: {command[:50]}"
            return True, "Admin access granted"
        
        # Check explicit allowlist
        if base_cmd in allowed:
            # Check blacklist patterns
            if self._is_blacklisted(command):
                return False, f"Command pattern blacklisted: {command[:50]}"
            return True, "Command allowed by policy"
        
        return False, f"Command '{base_cmd}' not allowed for role '{role}'"
    
    def _is_blacklisted(self, command: str) -> bool:
        """Check if command matches any blacklisted pattern"""
        blacklist = self.policy.get("blacklisted_patterns", [])
        for pattern in blacklist:
            # Simple pattern matching - can be enhanced with regex
            if pattern in command:
                return True
        return False
    
    def get_max_execution_time(self, role: str) -> int:
        """Get maximum execution time for a role"""
        return self.policy.get("roles", {}).get(role, {}).get("max_execution_time", 30)
    
    def requires_confirmation(self, role: str) -> bool:
        """Check if role requires confirmation before execution"""
        return self.policy.get("roles", {}).get(role, {}).get("requires_confirmation", False)

class SecureCommandExecutor:
    """Executes commands with sandboxing and resource limits"""
    
    def __init__(self, cwd: Optional[Path] = None, env_whitelist: List[str] = None):
        self.cwd = cwd or Path.cwd()
        self.env_whitelist = env_whitelist or ["PATH", "HOME", "USER", "LANG", "LC_ALL"]
    
    def execute(self, command: str, timeout_sec: int = 30) -> Tuple[int, str, str, float]:
        """Execute command with timeout and return results"""
        start_time = time.time()
        
        # Sanitize environment
        safe_env = {}
        for key in self.env_whitelist:
            if key in os.environ:
                safe_env[key] = os.environ[key]
        
        # Add safe PATH
        safe_env["PATH"] = "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        
        try:
            # Parse command safely
            args = shlex.split(command)
            
            # Execute with timeout
            result = subprocess.run(
                args,
                cwd=self.cwd,
                env=safe_env,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False
            )
            
            execution_time = (time.time() - start_time) * 1000  # ms
            
            return (
                result.returncode,
                result.stdout,
                result.stderr,
                execution_time
            )
            
        except subprocess.TimeoutExpired:
            execution_time = (time.time() - start_time) * 1000
            return (-1, "", f"Command timed out after {timeout_sec} seconds", execution_time)
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return (-2, "", f"Execution error: {str(e)}", execution_time)

class AgentCLILogger:
    """Handles structured logging of all command executions"""
    
    def __init__(self, policy: AccessPolicy):
        self.policy = policy
        self.log_config = policy.policy.get("logging", {})
        self.log_file = Path(self.log_config.get("log_file", "/var/log/agent_cli.log"))
        self.max_size_mb = self.log_config.get("max_log_size_mb", 100)
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging handlers"""
        # Rotate log if too large
        if self.log_file.exists() and self.log_file.stat().st_size > self.max_size_mb * 1024 * 1024:
            self._rotate_log()
        
        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stderr)
            ]
        )
    
    def _rotate_log(self) -> None:
        """Rotate log file with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated_path = self.log_file.with_suffix(f".{timestamp}.log")
        self.log_file.rename(rotated_path)
    
    def log_command(self, attempt: CommandAttempt) -> None:
        """Log a command execution attempt"""
        if not self.log_config.get("log_commands", True):
            return
        
        log_entry = {
            "timestamp": attempt.timestamp,
            "timestamp_iso": datetime.fromtimestamp(attempt.timestamp).isoformat(),
            "role": attempt.role,
            "command": attempt.command,
            "exit_code": attempt.exit_code,
            "allowed": attempt.allowed,
            "execution_time_ms": attempt.execution_time_ms,
            "promoted_to_utility": attempt.promoted_to_utility
        }
        
        if self.log_config.get("log_output", True):
            # Truncate output for log file (keep first/last 1000 chars)
            stdout_trunc = attempt.stdout[:1000] + "..." if len(attempt.stdout) > 1000 else attempt.stdout
            stderr_trunc = attempt.stderr[:1000] + "..." if len(attempt.stderr) > 1000 else attempt.stderr
            log_entry["stdout"] = stdout_trunc
            log_entry["stderr"] = stderr_trunc
        
        if self.log_config.get("log_environment", False):
            log_entry["environment"] = {
                k: v for k, v in os.environ.items() 
                if k in ["PATH", "HOME", "USER", "PWD", "SHELL"]
            }
        
        # Write structured log entry
        logging.info(json.dumps(log_entry))
        
        # Also write to audit log for compliance
        self._write_audit_log(attempt)
    
    def _write_audit_log(self, attempt: CommandAttempt) -> None:
        """Write to separate audit log for security review"""
        audit_log = self.log_file.with_suffix(".audit.json")
        audit_entry = {
            "timestamp": attempt.timestamp,
            "role": attempt.role,
            "command": attempt.command,
            "allowed": attempt.allowed,
            "exit_code": attempt.exit_code
        }
        
        with open(audit_log, 'a') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(json.dumps(audit_entry) + "\n")
            fcntl.flock(f, fcntl.LOCK_UN)

class AgentCLIWrapper:
    """Main CLI wrapper with role-based access control"""
    
    def __init__(self, policy_path: Optional[Path] = None):
        self.policy = AccessPolicy(policy_path)
        self.logger = AgentCLILogger(self.policy)
        self.role = self._get_role()
        self.executor = SecureCommandExecutor()
    
    def _get_role(self) -> str:
        """Get role from environment or prompt"""
        # Check environment variable first
        role = os.environ.get("AGENT_ROLE", "").lower()
        
        if role and role in self.policy.policy.get("roles", {}):
            return role
        
        # Check for role file
        role_file = Path.home() / ".agent_role"
        if role_file.exists():
            role = role_file.read_text().strip().lower()
            if role in self.policy.policy.get("roles", {}):
                return role
        
        # Prompt user
        print(f"Available roles: {', '.join(self.policy.policy.get('roles', {}).keys())}")
        while True:
            role = input("Enter your role: ").strip().lower()
            if role in self.policy.policy.get("roles", {}):
                # Save role for future
                role_file.write_text(role)
                return role
            print(f"Invalid role. Choose from: {', '.join(self.policy.policy.get('roles', {}).keys())}")
    
    def _confirm_execution(self, command: str) -> bool:
        """Request confirmation before executing command"""
        print(f"\n⚠️  Command requires confirmation: {command}")
        response = input(f"Execute this command? [y/N]: ").strip().lower()
        return response in ['y', 'yes']
    
    def execute_command(self, command: str) -> CommandAttempt:
        """Execute a command with full access control and logging"""
        if not command or command.strip() == "":
            return None
        
        # Check if command is allowed
        allowed, message = self.policy.is_command_allowed(command, self.role)
        
        attempt = CommandAttempt(
            command=command,
            role=self.role,
            timestamp=time.time(),
            exit_code=-1,
            stdout="",
            stderr="",
            allowed=allowed,
            execution_time_ms=0,
            promoted_to_utility=False
        )
        
        if not allowed:
            attempt.stderr = message
            attempt.exit_code = 403
            self.logger.log_command(attempt)
            print(f"❌ Access Denied: {message}", file=sys.stderr)
            return attempt
        
        # Check if confirmation is required
        if self.policy.requires_confirmation(self.role):
            if not self._confirm_execution(command):
                attempt.stderr = "Execution cancelled by user"
                attempt.exit_code = 130
                self.logger.log_command(attempt)
                print("❌ Execution cancelled")
                return attempt
        
        # Execute the command with timeout
        timeout = self.policy.get_max_execution_time(self.role)
        print(f"🔒 Executing as '{self.role}' (timeout: {timeout}s): {command}")
        
        exit_code, stdout, stderr, exec_time = self.executor.execute(command, timeout)
        
        attempt.exit_code = exit_code
        attempt.stdout = stdout
        attempt.stderr = stderr
        attempt.execution_time_ms = int(exec_time)
        
        # Check for utility belt promotion
        if exit_code == 0:
            promoted = UtilityBelt.record_usage(command.split()[0] if command else command, True)
            attempt.promoted_to_utility = promoted
            if promoted:
                print(f"🏆 Command promoted to Utility Belt!")
        
        # Log the attempt
        self.logger.log_command(attempt)
        
        # Display output
        if stdout:
            print(stdout)
        if stderr and exit_code != 0:
            print(stderr, file=sys.stderr)
        
        # Show execution summary
        status = "✅" if exit_code == 0 else "❌"
        print(f"{status} Exit code: {exit_code} | Time: {exec_time:.0f}ms")
        
        return attempt
    
    def run_interactive(self) -> None:
        """Run interactive CLI session"""
        print(f"\n{'='*60}")
        print(f"🔐 Agent CLI Execution Wrapper - Role: {self.role}")
        print(f"{'='*60}")
        print(f"Commands are logged to: {self.logger.log_file}")
        print(f"Type 'exit' or press Ctrl+D to quit")
        print(f"Type 'help' for available commands\n")
        
        while True:
            try:
                # Show prompt with role
                prompt = f"[{self.role}] $ "
                command = input(prompt).strip()
                
                if command.lower() in ['exit', 'quit']:
                    print("Goodbye! 👋")
                    break
                
                if command.lower() == 'help':
                    self._show_help()
                    continue
                
                if command.lower() == 'stats':
                    self._show_stats()
                    continue
                
                if command.lower() == 'policy':
                    self._show_policy()
                    continue
                
                if command:
                    self.execute_command(command)
                    
            except KeyboardInterrupt:
                print("\nInterrupted")
                continue
            except EOFError:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Unexpected error: {e}", file=sys.stderr)
    
    def _show_help(self) -> None:
        """Display help information"""
        help_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                    Agent CLI Commands                        ║
╠══════════════════════════════════════════════════════════════╣
║  help    - Show this help message                            ║
║  stats   - Show command usage statistics and utility belt    ║
║  policy  - Display current access policy for your role       ║
║  exit    - Exit the CLI wrapper                              ║
╠══════════════════════════════════════════════════════════════╣
║  Any shell command will be validated against your role's     ║
║  access policy and logged for audit purposes.                ║
║                                                              ║
║  Commands that prove useful are automatically promoted to    ║
║  the Utility Belt for system-wide availability.              ║
╚══════════════════════════════════════════════════════════════╝
"""
        print(help_text)
    
    def _show_stats(self) -> None:
        """Show usage statistics"""
        stats = UtilityBelt.load_stats()
        if not stats:
            print("No usage statistics available yet.")
            return
        
        print("\n📊 Command Usage Statistics:")
        print("-" * 40)
        for cmd, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:20]:
            if not cmd.endswith("_promoted"):
                promoted = stats.get(f"{cmd}_promoted", 0)
                marker = "🏆 " if promoted > 0 else "   "
                print(f"{marker}{cmd:20} {count:>6} executions")
        
        # Show utility belt location
        if UtilityBelt.UTILITY_COMMANDS_PATH.exists():
            utils = list(UtilityBelt.UTILITY_COMMANDS_PATH.iterdir())
            if utils:
                print(f"\n🔧 Utility Belt Commands: {UtilityBelt.UTILITY_COMMANDS_PATH}")
                for util in utils:
                    print(f"   → {util.name}")
    
    def _show_policy(self) -> None:
        """Show current policy for this role"""
        role_config = self.policy.policy.get("roles", {}).get(self.role, {})
        
        print(f"\n📋 Access Policy for role: {self.role}")
        print("-" * 50)
        print(f"Allowed commands: {', '.join(role_config.get('allowed_commands', []))}")
        print(f"Max execution time: {role_config.get('max_execution_time', 30)}s")
        print(f"Requires confirmation: {role_config.get('requires_confirmation', False)}")
        
        if self.policy.policy.get("blacklisted_patterns"):
            print(f"\n🚫 Blacklisted patterns: {', '.join(self.policy.policy.get('blacklisted_patterns', []))}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agent CLI Execution Wrapper with RBAC and logging"
    )
    parser.add_argument(
        "-c", "--command",
        help="Command to execute (non-interactive mode)"
    )
    parser.add_argument(
        "-p", "--policy",
        help="Path to access policy JSON file",
        type=Path
    )
    parser.add_argument(
        "-r", "--role",
        help="Override role for this execution",
        choices=['developer', 'linguist', 'operator', 'admin']
    )
    
    args = parser.parse_args()
    
    # Override role if provided
    if args.role:
        os.environ["AGENT_ROLE"] = args.role
    
    wrapper = AgentCLIWrapper(args.policy)
    
    if args.command:
        # Non-interactive mode
        result = wrapper.execute_command(args.command)
        sys.exit(result.exit_code if result else 1)
    else:
        # Interactive mode
        wrapper.run_interactive()

if __name__ == "__main__":
    main()
