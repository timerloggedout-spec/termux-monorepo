#!/usr/bin/env python3
"""DeepAgent - Advanced AI agent with DIRECT imports (no HTTP hop).

This agent is based on the deepcli/deepagent.py architecture and provides:
- Direct in-process execution
- Full tool access
- Session management
- Multi-provider support
- Termux integration
"""

import os
import sys
import json
import time
import uuid
import signal
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Union, Generator, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import from deepcli architecture
try:
    HOME = Path.home()
    sys.path.insert(0, str(HOME / "deepcli"))
    sys.path.insert(0, str(HOME))
    
    from deepcli.core import get_token, create_session, chat_completion, stream_completion
    _DEEPCLI_AVAILABLE = True
except Exception:
    _DEEPCLI_AVAILABLE = False
    print("Warning: deepcli not available, using fallback", file=sys.stderr)

from core.core import get_token as core_get_token
from core.session_manager import SessionManager
from bridge.mistralai_bridge import MistralAIBridge, get_mistral_bridge


@dataclass
class AgentConfig:
    """Configuration for DeepAgent."""
    name: str = "deepagent"
    provider: str = "mistralai"
    model: str = "mistral-large"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    max_steps: int = 16
    idle_sleep: float = 3.0
    auto_fix: bool = True
    use_deepagent: bool = True
    
    # Tool configurations
    tools: Dict[str, Any] = field(default_factory=dict)
    
    # Environment
    env: Dict[str, str] = field(default_factory=dict)


@dataclass
class AgentStep:
    """Represents a single agent step."""
    step: int
    action: str
    input: Any
    output: Any
    duration: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "action": self.action,
            "input": self.input,
            "output": self.output,
            "duration": self.duration,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class AgentResult:
    """Result of an agent execution."""
    task: str
    steps: List[AgentStep] = field(default_factory=list)
    final_output: Any = None
    success: bool = True
    error: Optional[str] = None
    duration: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "steps": [s.to_dict() for s in self.steps],
            "final_output": self.final_output,
            "success": self.success,
            "error": self.error,
            "duration": self.duration,
            "metadata": self.metadata,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class DeepAgent:
    """Advanced AI agent with direct in-process execution.
    
    This agent provides:
    - Direct access to AI providers without HTTP overhead
    - Full tool integration
    - Session management
    - Multi-step task execution
    - Error recovery
    """
    
    # Available tools
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "gh",
                "description": "Run a GitHub CLI command",
                "parameters": {
                    "type": "object",
                    "properties": {"argv": {"type": "array", "items": {"type": "string"}}},
                    "required": ["argv"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "run",
                "description": "Run a shell command on Termux",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "argv": {"type": "array", "items": {"type": "string"}},
                        "cwd": {"type": "string"},
                        "idle_timeout_s": {"type": "integer"},
                        "hard_timeout_s": {"type": "integer"}
                    },
                    "required": ["argv"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}, "max_bytes": {"type": "integer"}},
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "mode": {"type": "string", "enum": ["text", "base64"]}
                    },
                    "required": ["path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_dir",
                "description": "List directory entries",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "glob",
                "description": "Glob files",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "glob": {"type": "string"}
                    },
                    "required": ["path", "glob"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "gh_get_file",
                "description": "Get file from GitHub",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string"},
                        "path": {"type": "string"},
                        "ref": {"type": "string"}
                    },
                    "required": ["repo", "path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "gh_edit_file",
                "description": "Edit file on GitHub",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repo": {"type": "string"},
                        "path": {"type": "string"},
                        "edits": {"type": "array"},
                        "message": {"type": "string"},
                        "branch": {"type": "string"}
                    },
                    "required": ["repo", "path", "edits"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "finish",
                "description": "Call when done",
                "parameters": {
                    "type": "object",
                    "properties": {"summary": {"type": "string"}},
                    "required": ["summary"]
                }
            }
        },
    ]
    
    # Run allowlist for security
    RUN_ALLOWED_BINS = {
        "git", "gh", "python3", "pip3", "node", "npm", "rg", "fd", "jq", "yq",
        "ls", "cat", "head", "tail", "wc", "find", "grep", "sed", "awk", "sort", "uniq",
        "curl", "adb", "echo", "pwd", "which", "stat", "df", "du", "date",
        "termux-notification", "termux-toast", "termux-clipboard-get",
        "termux-battery-status", "mkdir", "printf", "env", "uname", "id",
        "whoami", "base64", "touch", "sleep",
    }
    
    def __init__(
        self,
        config: Optional[AgentConfig] = None,
        bridge: Optional[MistralAIBridge] = None,
        session_id: Optional[str] = None,
        **kwargs
    ):
        """Initialize DeepAgent.
        
        Args:
            config: Agent configuration
            bridge: Mistral AI bridge instance
            session_id: Session ID for conversation
        """
        self.config = config or AgentConfig()
        self.bridge = bridge or get_mistral_bridge()
        self.session_id = session_id or f"agent-{uuid.uuid4().hex[:8]}"
        self._steps: List[AgentStep] = []
        self._running = False
        self._stopped = False
        self._lock = threading.Lock()
        
        # Initialize bridge
        if not self.bridge.is_available():
            print("Warning: Mistral AI bridge not available", file=sys.stderr)
    
    def _get_tool(self, name: str):
        """Get tool by name."""
        for tool in self.TOOLS:
            if tool["function"]["name"] == name:
                return tool
        return None
    
    def _execute_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool."""
        start_time = time.time()
        
        try:
            if name == "gh":
                return self._tool_gh(args)
            elif name == "run":
                return self._tool_run(args)
            elif name == "read_file":
                return self._tool_read_file(args)
            elif name == "write_file":
                return self._tool_write_file(args)
            elif name == "list_dir":
                return self._tool_list_dir(args)
            elif name == "glob":
                return self._tool_glob(args)
            elif name == "gh_get_file":
                return self._tool_gh_get_file(args)
            elif name == "gh_edit_file":
                return self._tool_gh_edit_file(args)
            elif name == "finish":
                return self._tool_finish(args)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            return {"error": str(e)}
        finally:
            duration = time.time() - start_time
            self._steps.append(AgentStep(
                step=len(self._steps) + 1,
                action=f"tool:{name}",
                input=args,
                output=None,
                duration=duration,
                success=False,
                error=str(e) if "e" in locals() else None,
            ))
    
    def _tool_gh(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GitHub CLI command."""
        argv = args.get("argv", [])
        
        try:
            result = subprocess.run(
                ["gh"] + argv,
                capture_output=True,
                text=True,
                timeout=300,
            )
            return {
                "rc": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"rc": -1, "error": "Timeout", "stdout": "", "stderr": ""}
    
    def _tool_run(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command."""
        import signal as _signal
        
        argv = args.get("argv", [])
        if not argv:
            return {"rc": -1, "error": "argv empty"}
        
        binname = argv[0].rsplit("/", 1)[-1]
        if binname not in self.RUN_ALLOWED_BINS:
            return {"rc": -1, "error": f"binary '{binname}' not allowlisted"}
        
        cwd = args.get("cwd") or str(Path.home())
        idle = int(args.get("idle_timeout_s", 30))
        hard = int(args.get("hard_timeout_s", 300))
        
        try:
            p = subprocess.Popen(
                argv,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                preexec_fn=os.setsid if os.name == "posix" else None,
                env={**os.environ, "PYTHONUNBUFFERED": "1"}
            )
            
            start = time.time()
            last = start
            out, err = [], []
            
            try:
                import selectors
                sel = selectors.DefaultSelector()
                sel.register(p.stdout, selectors.EVENT_READ, "o")
                sel.register(p.stderr, selectors.EVENT_READ, "e")
                
                while sel.get_map():
                    if time.time() - start > hard:
                        os.killpg(p.pid, _signal.SIGKILL)
                        break
                    
                    for key, _ in sel.select(timeout=1.0):
                        line = key.fileobj.readline()
                        if not line:
                            sel.unregister(key.fileobj)
                            continue
                        last = time.time()
                        (out if key.data == "o" else err).append(line)
                    
                    if time.time() - last > idle:
                        try:
                            os.killpg(p.pid, _signal.SIGINT)
                        except ProcessLookupError:
                            pass
                        try:
                            p.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            try:
                                os.killpg(p.pid, _signal.SIGTERM)
                                p.wait(3)
                            except Exception:
                                os.killpg(p.pid, _signal.SIGKILL)
                        break
            finally:
                try:
                    p.wait(timeout=3)
                except Exception:
                    pass
            
            return {
                "rc": p.returncode,
                "stdout": "".join(out)[-8000:],
                "stderr": "".join(err)[-2000:]
            }
        except Exception as e:
            return {"rc": -1, "error": str(e)}
    
    def _tool_read_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read a file."""
        path = args.get("path", "")
        max_bytes = args.get("max_bytes", 512 * 1024)
        
        try:
            p = Path(path).expanduser().resolve()
            HOME = Path.home()
            
            # Security check
            try:
                p.relative_to(HOME)
            except ValueError:
                raise PermissionError(f"path outside allowed roots: {p}")
            
            if not p.is_file():
                return {"error": "not a file", "path": str(p)}
            
            cap = min(max_bytes, 512 * 1024)
            data = p.read_bytes()[:cap]
            
            try:
                return {"path": str(p), "content": data.decode()}
            except UnicodeDecodeError:
                import base64
                return {"path": str(p), "content_base64": base64.b64encode(data).decode()}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_write_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Write to a file."""
        path = args.get("path", "")
        content = args.get("content", "")
        mode = args.get("mode", "text")
        
        try:
            p = Path(path).expanduser().resolve()
            HOME = Path.home()
            
            # Security check
            try:
                p.relative_to(HOME)
            except ValueError:
                raise PermissionError(f"path outside allowed roots: {p}")
            
            # Decode content
            if mode == "base64":
                import base64
                data = base64.b64decode(content)
            else:
                data = content.encode()
            
            # Check size
            max_size = 512 * 1024
            if len(data) > max_size:
                raise ValueError(f"content too large: {len(data)}")
            
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            
            try:
                os.chmod(p, 0o600)
            except Exception:
                pass
            
            return {"path": str(p), "bytes": len(data)}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_list_dir(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List directory entries."""
        path = args.get("path", "")
        
        try:
            p = Path(path).expanduser().resolve()
            HOME = Path.home()
            
            # Security check
            try:
                p.relative_to(HOME)
            except ValueError:
                raise PermissionError(f"path outside allowed roots: {p}")
            
            if not p.is_dir():
                return {"error": "not a dir"}
            
            entries = []
            for c in p.iterdir():
                if not c.is_symlink() or c.exists():
                    entries.append({
                        "name": c.name,
                        "type": "dir" if c.is_dir() else "file",
                        "size": c.stat().st_size
                    })
            
            return {"path": str(p), "entries": sorted(entries, key=lambda x: x["name"])}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_glob(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Glob files."""
        path = args.get("path", "")
        glob = args.get("glob", "")
        
        try:
            p = Path(path).expanduser().resolve()
            HOME = Path.home()
            
            # Security check
            try:
                p.relative_to(HOME)
            except ValueError:
                raise PermissionError(f"path outside allowed roots: {p}")
            
            hits = []
            for f in p.glob(glob):
                try:
                    hits.append(str(f.relative_to(p)))
                except ValueError:
                    hits.append(str(f))
                if len(hits) >= 500:
                    break
            
            return {"base": str(p), "matches": hits}
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_gh_get_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get file from GitHub."""
        import base64 as _b64
        import subprocess as _sp
        import json as _json
        
        repo = args.get("repo", "")
        path = args.get("path", "")
        ref = args.get("ref", "master")
        
        try:
            r = _sp.run(
                ["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}"],
                capture_output=True,
                text=True
            )
            
            if r.returncode != 0:
                return {"error": r.stderr[-400:]}
            
            try:
                d = _json.loads(r.stdout)
            except Exception as e:
                return {"error": f"json: {e}", "raw": r.stdout[:200]}
            
            b64 = (d.get("content") or "").replace(chr(10), "").replace(" ", "")
            b64 += "=" * ((-len(b64)) % 4)
            
            try:
                text = _b64.b64decode(b64).decode("utf-8", "replace")
            except Exception as e:
                return {"error": f"b64: {e}"}
            
            return {
                "path": d.get("path"),
                "sha": d.get("sha"),
                "size": d.get("size"),
                "content": text
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_gh_edit_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Edit file on GitHub."""
        import subprocess as _sp
        import json as _json
        import base64 as _b64
        
        repo = args.get("repo", "")
        path = args.get("path", "")
        edits = args.get("edits", [])
        message = args.get("message", f"edit {path}")
        branch = args.get("branch", "master")
        create = bool(args.get("create_if_missing"))
        
        try:
            # Fetch
            r = _sp.run(
                ["gh", "api", f"repos/{repo}/contents/{path}?ref={branch}"],
                capture_output=True,
                text=True
            )
            cur_sha = ""
            if r.returncode == 0:
                try:
                    d = _json.loads(r.stdout)
                    cur_sha = d.get("sha", "")
                    b64 = (d.get("content") or "").replace(chr(10), "").replace(" ", "")
                    b64 += "=" * ((-len(b64)) % 4)
                    text = _b64.b64decode(b64).decode("utf-8", "replace")
                except Exception as e:
                    return {"error": f"decode: {e}"}
            elif create and edits and not edits[0].get("old"):
                text = edits[0].get("new", "")
            else:
                return {"error": f"file not found: {path}", "stderr": r.stderr[-300:]}
            
            # Apply edits
            applied, errors = [], []
            for i, ed in enumerate(edits):
                old = ed.get("old", "")
                new = ed.get("new", "")
                if not old and not create:
                    errors.append(f"edit[{i}]: missing 'old'")
                    continue
                n = text.count(old)
                if n == 0:
                    errors.append(f"edit[{i}]: old text not found")
                    continue
                if n > 1:
                    errors.append(f"edit[{i}]: old text appears {n}x - must be unique")
                    continue
                text = text.replace(old, new, 1)
                applied.append(i)
            
            if errors and not applied:
                return {"error": "no edits applied", "details": errors}
            if not applied:
                return {"error": "no edits specified"}
            
            # Push
            body = {
                "message": message,
                "content": _b64.b64encode(text.encode()).decode(),
                "branch": branch
            }
            if cur_sha:
                body["sha"] = cur_sha
            
            r = _sp.run(
                ["gh", "api", f"repos/{repo}/contents/{path}", "-X", "PUT", "--input", "-"],
                input=_json.dumps(body),
                capture_output=True,
                text=True
            )
            
            if r.returncode != 0:
                return {"error": f"PUT failed: {r.stderr[-400:]}", "applied": applied, "errors": errors}
            
            resp = _json.loads(r.stdout)
            c = resp.get("content", {})
            return {
                "path": c.get("path"),
                "sha": c.get("sha"),
                "html_url": c.get("html_url"),
                "commit": resp.get("commit", {}).get("sha"),
                "applied": applied,
                "errors": errors
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _tool_finish(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Finish task."""
        summary = args.get("summary", "")
        self._stopped = True
        return {"status": "finished", "summary": summary}
    
    def execute(self, task: str, **kwargs) -> AgentResult:
        """Execute a task.
        
        Args:
            task: Task description
            
        Returns:
            AgentResult with execution details
        """
        start_time = time.time()
        self._steps = []
        self._running = True
        self._stopped = False
        
        try:
            # Add initial step
            self._steps.append(AgentStep(
                step=1,
                action="start",
                input={"task": task},
                output=None,
                duration=0,
                success=True,
            ))
            
            # Execute task
            result = self._execute_task(task, **kwargs)
            
            # Add final step
            self._steps.append(AgentStep(
                step=len(self._steps) + 1,
                action="finish",
                input={},
                output=result,
                duration=0,
                success=True,
            ))
            
            return AgentResult(
                task=task,
                steps=self._steps,
                final_output=result,
                success=True,
                duration=time.time() - start_time,
            )
        except Exception as e:
            self._steps.append(AgentStep(
                step=len(self._steps) + 1,
                action="error",
                input={},
                output=None,
                duration=0,
                success=False,
                error=str(e),
            ))
            return AgentResult(
                task=task,
                steps=self._steps,
                final_output=None,
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )
        finally:
            self._running = False
    
    def _execute_task(self, task: str, **kwargs) -> Any:
        """Execute a task using AI.
        
        Args:
            task: Task description
            
        Returns:
            Task result
        """
        # Use Mistral AI to plan and execute
        context = kwargs.get("context", [])
        
        # Build prompt
        prompt = f"You are a powerful AI agent. Execute the following task:\n\n{task}\n\n"
        prompt += "You have access to tools. Use them as needed.\n"
        prompt += "When done, call the 'finish' tool with a summary.\n"
        
        # Send to AI
        response = self.bridge.send_message(
            prompt,
            context=context,
            session_id=self.session_id,
        )
        
        return response
    
    def stream_execute(self, task: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """Stream task execution.
        
        Args:
            task: Task description
            
        Yields:
            Execution updates
        """
        start_time = time.time()
        self._steps = []
        self._running = True
        self._stopped = False
        
        try:
            yield {"type": "start", "task": task, "timestamp": time.time()}
            
            # Execute with streaming
            context = kwargs.get("context", [])
            
            prompt = f"You are a powerful AI agent. Execute the following task:\n\n{task}\n\n"
            prompt += "You have access to tools. Use them as needed.\n"
            prompt += "When done, call the 'finish' tool with a summary.\n"
            
            for chunk in self.bridge.stream_completion(
                prompt,
                context=context,
                session_id=self.session_id,
            ):
                yield {"type": "chunk", "content": chunk, "timestamp": time.time()}
            
            yield {"type": "done", "duration": time.time() - start_time}
        except Exception as e:
            yield {"type": "error", "error": str(e), "timestamp": time.time()}
        finally:
            self._running = False
    
    def stop(self):
        """Stop the agent."""
        self._stopped = True
        self._running = False


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "DeepAgent",
    "AgentConfig",
    "AgentStep",
    "AgentResult",
]
