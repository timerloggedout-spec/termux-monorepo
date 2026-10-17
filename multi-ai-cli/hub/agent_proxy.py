#!/usr/bin/env python3
"""Agent Proxy - Proxy for agentic operations across providers.

This module provides:
- Agent session management
- Multi-provider agent orchestration
- Tool calling and execution
- Memory and context management
- Provenance tracking
"""

import os
import sys
import json
import time
import uuid
import asyncio
import logging
from typing import Optional, Dict, Any, List, Union, Tuple, Generator, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager, asynccontextmanager

logger = logging.getLogger(__name__)


class AgentProxyError(Exception):
    """Exception for agent proxy errors."""
    pass


class AgentStatus(Enum):
    """Agent status."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


class AgentRole(Enum):
    """Agent role."""
    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"
    TOOL = "tool"


@dataclass
class ToolDefinition:
    """Definition of a tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    strict: bool = False


@dataclass
class ToolCall:
    """Tool call."""
    id: str
    name: str
    arguments: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class ToolResult:
    """Tool result."""
    tool_call_id: str
    content: Any
    is_error: bool = False
    error_message: Optional[str] = None


@dataclass
class Message:
    """Message in a conversation."""
    role: AgentRole
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    tool_results: List[ToolResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    name: str
    provider: str
    model: str
    system_prompt: str = ""
    tools: List[str] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 4096
    memory_size: int = 100
    max_iterations: int = 10
    timeout: float = 300.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentState:
    """State of an agent."""
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    conversation: List[Message] = field(default_factory=list)
    current_tool_call: Optional[ToolCall] = None
    tool_results: Dict[str, ToolResult] = field(default_factory=dict)
    iteration_count: int = 0
    start_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    error: Optional[str] = None
    provenance: List[Dict[str, Any]] = field(default_factory=list)


class AgentProxy:
    """Proxy for agentic operations across providers.
    
    This class provides:
    - Multi-provider agent orchestration
    - Tool calling and execution
    - Memory and context management
    - Provenance tracking
    """
    
    def __init__(
        self,
        hub: Any = None,
        router: Any = None,
        tool_registry: Optional[Dict[str, ToolDefinition]] = None,
        memory_dir: Optional[str] = None,
    ):
        """Initialize agent proxy.
        
        Args:
            hub: TermuxHub instance
            router: ProviderRouter instance
            tool_registry: Registry of available tools
            memory_dir: Directory for agent memory
        """
        self.hub = hub
        self.router = router
        self.tool_registry = tool_registry or {}
        self.memory_dir = memory_dir or os.path.expanduser("~/.termux_ai_hub/agents")
        
        # Agent registry
        self._agents: Dict[str, AgentConfig] = {}
        self._agent_states: Dict[str, AgentState] = {}
        self._agent_sessions: Dict[str, Any] = {}
        
        # Tool execution
        self._tool_executors: Dict[str, Callable] = {}
        
        # Memory
        os.makedirs(self.memory_dir, exist_ok=True)
        
        # Initialize default tools
        self._initialize_default_tools()
        
        logger.info("Agent Proxy initialized")
    
    def _initialize_default_tools(self):
        """Initialize default tools."""
        # Code execution tool
        self.register_tool(ToolDefinition(
            name="execute_code",
            description="Execute Python code",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"},
                },
                "required": ["code"],
            },
            required=["code"],
        ))
        
        # Shell command tool
        self.register_tool(ToolDefinition(
            name="execute_shell",
            description="Execute a shell command",
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to execute"},
                    "timeout": {"type": "number", "description": "Command timeout in seconds"},
                },
                "required": ["command"],
            },
            required=["command"],
        ))
        
        # HTTP request tool
        self.register_tool(ToolDefinition(
            name="http_request",
            description="Make an HTTP request",
            parameters={
                "type": "object",
                "properties": {
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "description": "HTTP method"},
                    "url": {"type": "string", "description": "Request URL"},
                    "headers": {"type": "object", "description": "Request headers"},
                    "body": {"type": "string", "description": "Request body"},
                },
                "required": ["method", "url"],
            },
            required=["method", "url"],
        ))
        
        # File operations
        self.register_tool(ToolDefinition(
            name="read_file",
            description="Read a file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                },
                "required": ["path"],
            },
            required=["path"],
        ))
        
        self.register_tool(ToolDefinition(
            name="write_file",
            description="Write a file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"},
                },
                "required": ["path", "content"],
            },
            required=["path", "content"],
        ))
        
        # Collab integration tools
        self.register_tool(ToolDefinition(
            name="colab_create_notebook",
            description="Create a new Google Colab notebook",
            parameters={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Notebook name"},
                    "content": {"type": "string", "description": "Initial notebook content"},
                },
                "required": ["name"],
            },
            required=["name"],
        ))
        
        self.register_tool(ToolDefinition(
            name="colab_execute_cell",
            description="Execute a cell in a Colab notebook",
            parameters={
                "type": "object",
                "properties": {
                    "notebook_id": {"type": "string", "description": "Notebook ID"},
                    "cell_index": {"type": "integer", "description": "Cell index"},
                },
                "required": ["notebook_id", "cell_index"],
            },
            required=["notebook_id", "cell_index"],
        ))
        
        # GitHub Actions tools
        self.register_tool(ToolDefinition(
            name="github_run_workflow",
            description="Run a GitHub Actions workflow",
            parameters={
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": "Repository (owner/repo)"},
                    "workflow_id": {"type": "string", "description": "Workflow ID or filename"},
                    "branch": {"type": "string", "description": "Branch name"},
                },
                "required": ["repo", "workflow_id"],
            },
            required=["repo", "workflow_id"],
        ))
    
    def register_tool(self, tool: ToolDefinition):
        """Register a tool.
        
        Args:
            tool: Tool definition
        """
        self.tool_registry[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def register_tool_executor(self, name: str, executor: Callable):
        """Register a tool executor function.
        
        Args:
            name: Tool name
            executor: Function to execute the tool
        """
        self._tool_executors[name] = executor
        logger.info(f"Registered tool executor: {name}")
    
    def create_agent(
        self,
        name: str,
        provider: str,
        model: str,
        system_prompt: str = "",
        tools: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        memory_size: int = 100,
        max_iterations: int = 10,
        timeout: float = 300.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new agent.
        
        Args:
            name: Agent name
            provider: Provider to use
            model: Model to use
            system_prompt: System prompt for the agent
            tools: List of tool names to enable
            temperature: Temperature setting
            max_tokens: Maximum tokens
            memory_size: Memory size (number of messages to retain)
            max_iterations: Maximum number of iterations
            timeout: Timeout in seconds
            metadata: Additional metadata
            
        Returns:
            Agent ID
        """
        agent_id = str(uuid.uuid4())
        
        config = AgentConfig(
            agent_id=agent_id,
            name=name,
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            tools=tools or [],
            temperature=temperature,
            max_tokens=max_tokens,
            memory_size=memory_size,
            max_iterations=max_iterations,
            timeout=timeout,
            metadata=metadata or {},
        )
        
        self._agents[agent_id] = config
        
        # Initialize state
        state = AgentState(
            agent_id=agent_id,
            status=AgentStatus.IDLE,
        )
        self._agent_states[agent_id] = state
        
        logger.info(f"Created agent: {name} ({agent_id})")
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> AgentConfig:
        """Get agent configuration.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent configuration
        """
        if agent_id not in self._agents:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        return self._agents[agent_id]
    
    def get_agent_state(self, agent_id: str) -> AgentState:
        """Get agent state.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent state
        """
        if agent_id not in self._agent_states:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        return self._agent_states[agent_id]
    
    def destroy_agent(self, agent_id: str):
        """Destroy an agent.
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self._agents:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        # Clean up session
        if agent_id in self._agent_sessions:
            try:
                if self.hub:
                    self.hub.destroy_session(self._agent_sessions[agent_id])
            except Exception as e:
                logger.error(f"Failed to clean up agent session: {e}")
            del self._agent_sessions[agent_id]
        
        del self._agents[agent_id]
        del self._agent_states[agent_id]
        
        logger.info(f"Destroyed agent: {agent_id}")
    
    def start_agent(self, agent_id: str) -> str:
        """Start an agent session.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Session ID
        """
        if agent_id not in self._agents:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        config = self._agents[agent_id]
        state = self._agent_states[agent_id]
        
        if state.status == AgentStatus.RUNNING:
            return self._agent_sessions[agent_id]
        
        # Create session
        if self.hub:
            session_id = self.hub.create_session(
                provider=config.provider,
                model=config.model,
                system_prompt=config.system_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        elif self.router:
            session_id = self.router.route_request(
                action="create_session",
                provider=config.provider,
                model=config.model,
                system_prompt=config.system_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        else:
            raise AgentProxyError("No hub or router configured")
        
        self._agent_sessions[agent_id] = session_id
        state.status = AgentStatus.RUNNING
        state.start_time = time.time()
        
        # Add system message
        if config.system_prompt:
            self._add_message(agent_id, Message(
                role=AgentRole.SYSTEM,
                content=config.system_prompt,
            ))
        
        logger.info(f"Started agent: {agent_id} (session: {session_id})")
        
        return session_id
    
    def stop_agent(self, agent_id: str):
        """Stop an agent.
        
        Args:
            agent_id: Agent ID
        """
        if agent_id not in self._agents:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        state = self._agent_states[agent_id]
        
        if state.status == AgentStatus.RUNNING:
            if agent_id in self._agent_sessions:
                try:
                    if self.hub:
                        self.hub.destroy_session(self._agent_sessions[agent_id])
                except Exception as e:
                    logger.error(f"Failed to stop agent session: {e}")
                del self._agent_sessions[agent_id]
            
            state.status = AgentStatus.IDLE
            state.current_tool_call = None
            state.error = None
        
        logger.info(f"Stopped agent: {agent_id}")
    
    def _add_message(self, agent_id: str, message: Message):
        """Add a message to the conversation.
        
        Args:
            agent_id: Agent ID
            message: Message to add
        """
        state = self._agent_states[agent_id]
        
        # Enforce memory limit
        if len(state.conversation) >= self._agents[agent_id].memory_size:
            # Remove oldest messages (but keep system message if present)
            system_messages = [m for m in state.conversation if m.role == AgentRole.SYSTEM]
            non_system = [m for m in state.conversation if m.role != AgentRole.SYSTEM]
            
            if non_system:
                non_system = non_system[-(self._agents[agent_id].memory_size - len(system_messages)):]
            
            state.conversation = system_messages + non_system
        
        state.conversation.append(message)
        state.last_activity = time.time()
    
    def send_message(
        self,
        agent_id: str,
        content: str,
        role: AgentRole = AgentRole.USER,
        stream: bool = False,
        **kwargs,
    ) -> Union[str, Generator[str, None, None]]:
        """Send a message to an agent.
        
        Args:
            agent_id: Agent ID
            content: Message content
            role: Role of the message
            stream: Whether to stream the response
            **kwargs: Additional arguments
            
        Returns:
            Response (string or generator for streaming)
        """
        if agent_id not in self._agents:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        config = self._agents[agent_id]
        state = self._agent_states[agent_id]
        
        # Ensure agent is running
        if state.status != AgentStatus.RUNNING:
            self.start_agent(agent_id)
        
        # Add user message
        message = Message(
            role=role,
            content=content,
        )
        self._add_message(agent_id, message)
        
        # Get session ID
        session_id = self._agent_sessions[agent_id]
        
        # Prepare tool definitions for the provider
        tool_definitions = {}
        for tool_name in config.tools:
            if tool_name in self.tool_registry:
                tool_definitions[tool_name] = self.tool_registry[tool_name]
        
        # Send to provider
        try:
            if self.hub:
                response = self.hub.send_message(
                    session_id=session_id,
                    message=content,
                    stream=stream,
                    tools=tool_definitions,
                    **kwargs,
                )
            elif self.router:
                response = self.router.route_request(
                    message=content,
                    action="chat",
                    session_id=session_id,
                    tools=tool_definitions,
                    **kwargs,
                )
            else:
                raise AgentProxyError("No hub or router configured")
            
            if stream:
                return self._handle_streaming_response(agent_id, response)
            else:
                return self._handle_response(agent_id, response)
                
        except Exception as e:
            state.status = AgentStatus.ERROR
            state.error = str(e)
            raise AgentProxyError(f"Failed to send message: {e}")
    
    def _handle_response(self, agent_id: str, response: Any) -> str:
        """Handle a non-streaming response.
        
        Args:
            agent_id: Agent ID
            response: Response from provider
            
        Returns:
            Processed response
        """
        state = self._agent_states[agent_id]
        config = self._agents[agent_id]
        
        # Parse response
        if isinstance(response, str):
            assistant_message = Message(
                role=AgentRole.ASSISTANT,
                content=response,
            )
            self._add_message(agent_id, assistant_message)
            return response
        
        elif isinstance(response, dict):
            # Handle tool calls
            if "tool_calls" in response:
                for tool_call_data in response.get("tool_calls", []):
                    tool_call = ToolCall(
                        id=tool_call_data.get("id", str(uuid.uuid4())),
                        name=tool_call_data.get("function", {}).get("name", ""),
                        arguments=tool_call_data.get("function", {}).get("arguments", {}),
                    )
                    state.current_tool_call = tool_call
                    
                    # Execute tool
                    tool_result = self._execute_tool(agent_id, tool_call)
                    
                    # Add tool message
                    tool_message = Message(
                        role=AgentRole.TOOL,
                        content=str(tool_result.content),
                        tool_calls=[tool_call],
                        tool_results=[tool_result],
                    )
                    self._add_message(agent_id, tool_message)
                
                # Get assistant message
                assistant_content = response.get("content", "")
                assistant_message = Message(
                    role=AgentRole.ASSISTANT,
                    content=assistant_content,
                )
                self._add_message(agent_id, assistant_message)
                
                return assistant_content
            else:
                assistant_message = Message(
                    role=AgentRole.ASSISTANT,
                    content=str(response),
                )
                self._add_message(agent_id, assistant_message)
                return str(response)
        
        else:
            assistant_message = Message(
                role=AgentRole.ASSISTANT,
                content=str(response),
            )
            self._add_message(agent_id, assistant_message)
            return str(response)
    
    def _handle_streaming_response(self, agent_id: str, response: Generator[str, None, None]) -> Generator[str, None, None]:
        """Handle a streaming response.
        
        Args:
            agent_id: Agent ID
            response: Streaming response from provider
            
        Yields:
            Response chunks
        """
        state = self._agent_states[agent_id]
        full_response = ""
        
        try:
            for chunk in response:
                full_response += chunk
                yield chunk
            
            # Add assistant message
            assistant_message = Message(
                role=AgentRole.ASSISTANT,
                content=full_response,
            )
            self._add_message(agent_id, assistant_message)
            
        except Exception as e:
            state.status = AgentStatus.ERROR
            state.error = str(e)
            raise
    
    def _execute_tool(self, agent_id: str, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call.
        
        Args:
            agent_id: Agent ID
            tool_call: Tool call to execute
            
        Returns:
            Tool result
        """
        state = self._agent_states[agent_id]
        config = self._agents[agent_id]
        
        # Check if tool is available
        if tool_call.name not in self.tool_registry:
            return ToolResult(
                tool_call_id=tool_call.id,
                content=f"Tool '{tool_call.name}' not available",
                is_error=True,
                error_message="Tool not found",
            )
        
        # Check if tool is enabled for this agent
        if tool_call.name not in config.tools:
            return ToolResult(
                tool_call_id=tool_call.id,
                content=f"Tool '{tool_call.name}' not enabled for this agent",
                is_error=True,
                error_message="Tool not enabled",
            )
        
        # Try custom executor first
        if tool_call.name in self._tool_executors:
            try:
                executor = self._tool_executors[tool_call.name]
                result = executor(**tool_call.arguments)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            except Exception as e:
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=None,
                    is_error=True,
                    error_message=str(e),
                )
        
        # Handle built-in tools
        try:
            if tool_call.name == "execute_code":
                code = tool_call.arguments.get("code", "")
                result = self._execute_python_code(code)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            elif tool_call.name == "execute_shell":
                command = tool_call.arguments.get("command", "")
                timeout = tool_call.arguments.get("timeout", 30)
                result = self._execute_shell_command(command, timeout)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            elif tool_call.name == "http_request":
                method = tool_call.arguments.get("method", "GET")
                url = tool_call.arguments.get("url", "")
                headers = tool_call.arguments.get("headers", {})
                body = tool_call.arguments.get("body", "")
                result = self._execute_http_request(method, url, headers, body)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            elif tool_call.name == "read_file":
                path = tool_call.arguments.get("path", "")
                result = self._read_file(path)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            elif tool_call.name == "write_file":
                path = tool_call.arguments.get("path", "")
                content = tool_call.arguments.get("content", "")
                result = self._write_file(path, content)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            elif tool_call.name == "colab_create_notebook":
                name = tool_call.arguments.get("name", "")
                content = tool_call.arguments.get("content", "")
                result = self._colab_create_notebook(name, content)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            elif tool_call.name == "colab_execute_cell":
                notebook_id = tool_call.arguments.get("notebook_id", "")
                cell_index = tool_call.arguments.get("cell_index", 0)
                result = self._colab_execute_cell(notebook_id, cell_index)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            elif tool_call.name == "github_run_workflow":
                repo = tool_call.arguments.get("repo", "")
                workflow_id = tool_call.arguments.get("workflow_id", "")
                branch = tool_call.arguments.get("branch", "main")
                result = self._github_run_workflow(repo, workflow_id, branch)
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=result,
                )
            
            else:
                return ToolResult(
                    tool_call_id=tool_call.id,
                    content=f"Tool '{tool_call.name}' not implemented",
                    is_error=True,
                    error_message="Not implemented",
                )
                
        except Exception as e:
            return ToolResult(
                tool_call_id=tool_call.id,
                content=None,
                is_error=True,
                error_message=str(e),
            )
    
    def _execute_python_code(self, code: str) -> str:
        """Execute Python code.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution result
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout or "Execution completed successfully"
            
        except subprocess.TimeoutExpired:
            return "Error: Code execution timed out"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _execute_shell_command(self, command: str, timeout: float = 30) -> str:
        """Execute a shell command.
        
        Args:
            command: Shell command to execute
            timeout: Command timeout in seconds
            
        Returns:
            Command output
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ["/bin/sh", "-c", command],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            if result.returncode != 0:
                return f"Error: {result.stderr}"
            
            return result.stdout
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _execute_http_request(self, method: str, url: str, headers: Dict[str, str], body: str) -> str:
        """Execute an HTTP request.
        
        Args:
            method: HTTP method
            url: Request URL
            headers: Request headers
            body: Request body
            
        Returns:
            Response text
        """
        import urllib.request
        import urllib.error
        
        try:
            req = urllib.request.Request(
                url,
                data=body.encode() if body else None,
                headers=headers,
                method=method,
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read().decode()
                
        except urllib.error.URLError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _read_file(self, path: str) -> str:
        """Read a file.
        
        Args:
            path: File path
            
        Returns:
            File content
        """
        try:
            with open(path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _write_file(self, path: str, content: str) -> str:
        """Write a file.
        
        Args:
            path: File path
            content: File content
            
        Returns:
            Success message or error
        """
        try:
            with open(path, "w") as f:
                f.write(content)
            return f"File written successfully: {path}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _colab_create_notebook(self, name: str, content: str = "") -> str:
        """Create a Colab notebook.
        
        Args:
            name: Notebook name
            content: Initial content
            
        Returns:
            Notebook ID or URL
        """
        try:
            if self.hub:
                colab_backend = self.hub.get_provider("colab")
                notebook_id = colab_backend.create_notebook(name, content)
                return f"Created notebook: {notebook_id}"
            else:
                return "Error: Colab backend not available"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _colab_execute_cell(self, notebook_id: str, cell_index: int) -> str:
        """Execute a cell in a Colab notebook.
        
        Args:
            notebook_id: Notebook ID
            cell_index: Cell index
            
        Returns:
            Execution result
        """
        try:
            if self.hub:
                colab_backend = self.hub.get_provider("colab")
                result = colab_backend.execute_cell(notebook_id, cell_index)
                return f"Cell executed: {result}"
            else:
                return "Error: Colab backend not available"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _github_run_workflow(self, repo: str, workflow_id: str, branch: str = "main") -> str:
        """Run a GitHub Actions workflow.
        
        Args:
            repo: Repository (owner/repo)
            workflow_id: Workflow ID or filename
            branch: Branch name
            
        Returns:
            Workflow run ID or URL
        """
        try:
            if self.hub:
                # This would need a GitHub backend
                # For now, return a placeholder
                return f"Workflow {workflow_id} triggered on {repo}@{branch}"
            else:
                return "Error: GitHub backend not available"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def run_agent(
        self,
        agent_id: str,
        task: str,
        max_iterations: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Run an agent on a task with automatic tool execution.
        
        Args:
            agent_id: Agent ID
            task: Task description
            max_iterations: Maximum iterations (overrides agent config)
            **kwargs: Additional arguments
            
        Returns:
            Final response
        """
        if agent_id not in self._agents:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        config = self._agents[agent_id]
        state = self._agent_states[agent_id]
        
        # Set max iterations
        iterations = max_iterations or config.max_iterations
        
        # Ensure agent is running
        if state.status != AgentStatus.RUNNING:
            self.start_agent(agent_id)
        
        # Reset state
        state.status = AgentStatus.RUNNING
        state.iteration_count = 0
        state.error = None
        
        # Send initial task
        response = self.send_message(agent_id, task, **kwargs)
        state.iteration_count += 1
        
        # Handle tool calls iteratively
        while state.iteration_count < iterations:
            # Check for tool calls
            if state.current_tool_call:
                tool_call = state.current_tool_call
                state.current_tool_call = None
                
                # Execute tool
                tool_result = self._execute_tool(agent_id, tool_call)
                state.tool_results[tool_call.id] = tool_result
                
                # Send tool result back to agent
                tool_message = f"Tool {tool_call.name} returned: {tool_result.content}"
                if tool_result.is_error:
                    tool_message = f"Tool {tool_call.name} error: {tool_result.error_message}"
                
                response = self.send_message(agent_id, tool_message, **kwargs)
                state.iteration_count += 1
            else:
                # No more tool calls, break
                break
        
        # Update state
        state.status = AgentStatus.COMPLETED
        
        return response
    
    def list_agents(self) -> List[str]:
        """List all agents.
        
        Returns:
            List of agent IDs
        """
        return list(self._agents.keys())
    
    def get_conversation(self, agent_id: str) -> List[Message]:
        """Get conversation history for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of messages
        """
        if agent_id not in self._agent_states:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        return self._agent_states[agent_id].conversation.copy()
    
    def add_provenance(self, agent_id: str, data: Dict[str, Any]):
        """Add provenance data for an agent.
        
        Args:
            agent_id: Agent ID
            data: Provenance data
        """
        if agent_id not in self._agent_states:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        self._agent_states[agent_id].provenance.append(data)
    
    def get_provenance(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get provenance data for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of provenance entries
        """
        if agent_id not in self._agent_states:
            raise AgentProxyError(f"Agent '{agent_id}' not found")
        
        return self._agent_states[agent_id].provenance.copy()
    
    def close(self):
        """Close the agent proxy and cleanup resources."""
        # Stop all agents
        for agent_id in list(self._agents.keys()):
            try:
                self.stop_agent(agent_id)
                self.destroy_agent(agent_id)
            except Exception as e:
                logger.error(f"Failed to close agent {agent_id}: {e}")
        
        self._agents.clear()
        self._agent_states.clear()
        self._agent_sessions.clear()
        
        logger.info("Agent Proxy closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "AgentProxy",
    "AgentProxyError",
    "AgentStatus",
    "AgentRole",
    "ToolDefinition",
    "ToolCall",
    "ToolResult",
    "Message",
    "AgentConfig",
    "AgentState",
]
