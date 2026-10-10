#!/usr/bin/env python3
"""Multi-AI CLI - Main entry point.

This module provides the main CLI interface for the multi-provider
AI integration system with Termux support.
"""

import os
import sys
import json
import argparse
import logging
import traceback
from typing import Optional, Dict, Any, List
from pathlib import Path

# Import hub components
from ..hub.termux_hub import TermuxHub, TermuxHubError, ProviderType, ProviderConfig
from ..hub.provider_router import ProviderRouter, ProviderRouterError, RoutingStrategy
from ..hub.agent_proxy import AgentProxy, AgentProxyError, AgentConfig, AgentStatus

# Import collab components
try:
    from ..collab.colab_client import ColabClient
    from ..collab.colab_notebook import ColabNotebook
    from ..collab.termux_integration import TermuxIntegration
    from ..collab.github_actions import GitHubActionsClient
    from ..collab.provenance import ProvenanceTracker
    _COLLAB_AVAILABLE = True
except ImportError:
    _COLLAB_AVAILABLE = False

# Import backends
try:
    from ..backends.mistralai import MistralAIBackend
    from ..backends.deepseek import DeepSeekBackend
    from ..backends.ai_studio import AIStudioBackend
    from ..backends.chapito import ChapitoBackend
    _BACKENDS_AVAILABLE = True
except ImportError:
    _BACKENDS_AVAILABLE = False


class CLIError(Exception):
    """Exception for CLI errors."""
    pass


class MultiAICLI:
    """Main CLI class for Multi-AI integration.
    
    This class provides:
    - Command parsing and execution
    - Hub and router management
    - Agent management
    - Collab integration
    """
    
    def __init__(self):
        """Initialize the CLI."""
        self.hub: Optional[TermuxHub] = None
        self.router: Optional[ProviderRouter] = None
        self.agent_proxy: Optional[AgentProxy] = None
        self.termux_integration: Optional[Any] = None
        self.colab_client: Optional[Any] = None
        self.github_client: Optional[Any] = None
        self.provenance: Optional[Any] = None
        
        # Configuration
        self.config_dir = os.path.expanduser("~/.termux_ai_cli")
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.config: Dict[str, Any] = {}
        
        # Load configuration
        self._load_config()
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self._initialize_components()
    
    def _load_config(self):
        """Load configuration from file."""
        os.makedirs(self.config_dir, exist_ok=True)
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file) as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
                self.config = {}
        else:
            # Create default config
            self.config = {
                "default_provider": "mistralai",
                "providers": {
                    "mistralai": {"enabled": True, "priority": 1},
                    "deepseek": {"enabled": True, "priority": 2},
                    "ai_studio": {"enabled": True, "priority": 3},
                    "chapito": {"enabled": True, "priority": 4},
                    "colab": {"enabled": True, "priority": 5},
                },
                "logging": {
                    "level": "INFO",
                    "file": os.path.join(self.config_dir, "multi_ai_cli.log"),
                },
            }
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save config: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config.get("logging", {})
        level = getattr(logging, log_config.get("level", "INFO"), logging.INFO)
        log_file = log_config.get("file", os.path.join(self.config_dir, "multi_ai_cli.log"))
        
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout),
            ],
        )
    
    def _initialize_components(self):
        """Initialize all components."""
        try:
            # Initialize hub
            self.hub = TermuxHub(
                config_dir=self.config_dir,
                default_provider=self.config.get("default_provider", "mistralai"),
            )
            
            # Initialize router
            self.router = ProviderRouter(
                hub=self.hub,
                strategy=RoutingStrategy(self.config.get("routing_strategy", "priority")),
            )
            
            # Initialize agent proxy
            self.agent_proxy = AgentProxy(
                hub=self.hub,
                router=self.router,
            )
            
            # Initialize collab components if available
            if _COLLAB_AVAILABLE:
                self.termux_integration = TermuxIntegration()
                self.colab_client = ColabClient()
                self.github_client = GitHubActionsClient()
                self.provenance = ProvenanceTracker()
            
            logging.info("Multi-AI CLI components initialized")
            
        except Exception as e:
            logging.error(f"Failed to initialize components: {e}")
            traceback.print_exc()
            raise CLIError(f"Initialization failed: {e}")
    
    def run(self, args: Optional[List[str]] = None):
        """Run the CLI with given arguments.
        
        Args:
            args: Command line arguments (defaults to sys.argv)
        """
        if args is None:
            args = sys.argv[1:]
        
        # Create parser
        parser = self._create_parser()
        
        try:
            # Parse arguments
            parsed_args = parser.parse_args(args)
            
            # Handle commands
            if hasattr(parsed_args, "func"):
                parsed_args.func(parsed_args)
            else:
                parser.print_help()
                
        except CLIError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser.
        
        Returns:
            Configured ArgumentParser
        """
        parser = argparse.ArgumentParser(
            prog="multi-ai-cli",
            description="Multi-AI CLI - Unified interface for AI providers",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  multi-ai-cli chat --provider mistralai --message "Hello, world!"
  multi-ai-cli agent create --name my-agent --provider mistralai
  multi-ai-cli collab notebook create --name my-notebook
  multi-ai-cli provider list
  multi-ai-cli session create --provider deepseek
            """,
        )
        
        # Add subparsers
        subparsers = parser.add_subparsers(
            title="commands",
            dest="command",
            help="Available commands",
        )
        
        # Chat command
        self._add_chat_command(subparsers)
        
        # Agent commands
        self._add_agent_commands(subparsers)
        
        # Collab commands
        if _COLLAB_AVAILABLE:
            self._add_collab_commands(subparsers)
        
        # Provider commands
        self._add_provider_commands(subparsers)
        
        # Session commands
        self._add_session_commands(subparsers)
        
        # Tool commands
        self._add_tool_commands(subparsers)
        
        # Hub commands
        self._add_hub_commands(subparsers)
        
        # GitHub commands
        if _COLLAB_AVAILABLE:
            self._add_github_commands(subparsers)
        
        # Termux commands
        if _COLLAB_AVAILABLE:
            self._add_termux_commands(subparsers)
        
        return parser
    
    def _add_chat_command(self, subparsers: Any):
        """Add chat command."""
        parser = subparsers.add_parser(
            "chat",
            help="Chat with AI providers",
            description="Send messages to AI providers and receive responses",
        )
        
        parser.add_argument(
            "--provider", "-p",
            type=str,
            default=None,
            help="Provider to use (default: configured default)",
        )
        
        parser.add_argument(
            "--model", "-m",
            type=str,
            default=None,
            help="Model to use",
        )
        
        parser.add_argument(
            "--message", "-M",
            type=str,
            default=None,
            help="Message to send",
        )
        
        parser.add_argument(
            "--session", "-s",
            type=str,
            default=None,
            help="Session ID for existing session",
        )
        
        parser.add_argument(
            "--stream",
            action="store_true",
            help="Stream the response",
        )
        
        parser.add_argument(
            "--temperature", "-t",
            type=float,
            default=0.7,
            help="Temperature setting (0.0-1.0)",
        )
        
        parser.add_argument(
            "--max-tokens",
            type=int,
            default=4096,
            help="Maximum tokens in response",
        )
        
        parser.add_argument(
            "--tools",
            type=str,
            nargs="*",
            default=[],
            help="List of tools to enable",
        )
        
        parser.set_defaults(func=self._handle_chat)
    
    def _handle_chat(self, args: Any):
        """Handle chat command."""
        if not args.message:
            raise CLIError("Message is required. Use --message or -M.")
        
        try:
            # Use router for intelligent routing
            if args.provider:
                response = self.router.route_request(
                    message=args.message,
                    action="chat",
                    preferred_provider=args.provider,
                    session_id=args.session,
                    model=args.model,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    tools=args.tools,
                    stream=args.stream,
                )
            else:
                response = self.router.route_request(
                    message=args.message,
                    action="chat",
                    session_id=args.session,
                    model=args.model,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                    tools=args.tools,
                    stream=args.stream,
                )
            
            if args.stream:
                for chunk in response:
                    print(chunk, end="", flush=True)
                print()
            else:
                print(response)
                
        except Exception as e:
            raise CLIError(f"Chat failed: {e}")
    
    def _add_agent_commands(self, subparsers: Any):
        """Add agent commands."""
        # Agent subparser
        agent_parser = subparsers.add_parser(
            "agent",
            help="Manage AI agents",
            description="Create, manage, and interact with AI agents",
        )
        
        agent_subparsers = agent_parser.add_subparsers(
            title="agent_commands",
            dest="agent_command",
        )
        
        # Create agent
        create_parser = agent_subparsers.add_parser(
            "create",
            help="Create a new agent",
        )
        create_parser.add_argument(
            "--name", "-n",
            type=str,
            required=True,
            help="Agent name",
        )
        create_parser.add_argument(
            "--provider", "-p",
            type=str,
            required=True,
            help="Provider to use",
        )
        create_parser.add_argument(
            "--model", "-m",
            type=str,
            default=None,
            help="Model to use",
        )
        create_parser.add_argument(
            "--system-prompt", "-s",
            type=str,
            default="",
            help="System prompt for the agent",
        )
        create_parser.add_argument(
            "--tools",
            type=str,
            nargs="*",
            default=[],
            help="List of tools to enable",
        )
        create_parser.add_argument(
            "--temperature", "-t",
            type=float,
            default=0.7,
            help="Temperature setting",
        )
        create_parser.add_argument(
            "--max-tokens",
            type=int,
            default=4096,
            help="Maximum tokens",
        )
        create_parser.add_argument(
            "--memory-size",
            type=int,
            default=100,
            help="Memory size (number of messages to retain)",
        )
        create_parser.add_argument(
            "--max-iterations",
            type=int,
            default=10,
            help="Maximum number of iterations",
        )
        create_parser.set_defaults(func=self._handle_agent_create)
        
        # List agents
        list_parser = agent_subparsers.add_parser(
            "list",
            help="List all agents",
        )
        list_parser.set_defaults(func=self._handle_agent_list)
        
        # Send message to agent
        send_parser = agent_subparsers.add_parser(
            "send",
            help="Send a message to an agent",
        )
        send_parser.add_argument(
            "--agent-id", "-a",
            type=str,
            required=True,
            help="Agent ID",
        )
        send_parser.add_argument(
            "--message", "-M",
            type=str,
            required=True,
            help="Message to send",
        )
        send_parser.add_argument(
            "--stream",
            action="store_true",
            help="Stream the response",
        )
        send_parser.set_defaults(func=self._handle_agent_send)
        
        # Run agent on task
        run_parser = agent_subparsers.add_parser(
            "run",
            help="Run an agent on a task",
        )
        run_parser.add_argument(
            "--agent-id", "-a",
            type=str,
            required=True,
            help="Agent ID",
        )
        run_parser.add_argument(
            "--task", "-t",
            type=str,
            required=True,
            help="Task description",
        )
        run_parser.add_argument(
            "--max-iterations",
            type=int,
            default=None,
            help="Maximum iterations (overrides agent config)",
        )
        run_parser.set_defaults(func=self._handle_agent_run)
        
        # Get agent info
        info_parser = agent_subparsers.add_parser(
            "info",
            help="Get agent information",
        )
        info_parser.add_argument(
            "--agent-id", "-a",
            type=str,
            required=True,
            help="Agent ID",
        )
        info_parser.set_defaults(func=self._handle_agent_info)
        
        # Destroy agent
        destroy_parser = agent_subparsers.add_parser(
            "destroy",
            help="Destroy an agent",
        )
        destroy_parser.add_argument(
            "--agent-id", "-a",
            type=str,
            required=True,
            help="Agent ID",
        )
        destroy_parser.set_defaults(func=self._handle_agent_destroy)
        
        # Conversation history
        history_parser = agent_subparsers.add_parser(
            "history",
            help="Get conversation history",
        )
        history_parser.add_argument(
            "--agent-id", "-a",
            type=str,
            required=True,
            help="Agent ID",
        )
        history_parser.set_defaults(func=self._handle_agent_history)
    
    def _handle_agent_create(self, args: Any):
        """Handle agent create command."""
        try:
            agent_id = self.agent_proxy.create_agent(
                name=args.name,
                provider=args.provider,
                model=args.model or self.config.get("default_model", "mistral-tiny"),
                system_prompt=args.system_prompt,
                tools=args.tools,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                memory_size=args.memory_size,
                max_iterations=args.max_iterations,
            )
            print(f"Created agent: {agent_id}")
            
            # Save agent ID to config for future reference
            if "agents" not in self.config:
                self.config["agents"] = {}
            self.config["agents"][args.name] = agent_id
            self._save_config()
            
        except Exception as e:
            raise CLIError(f"Failed to create agent: {e}")
    
    def _handle_agent_list(self, args: Any):
        """Handle agent list command."""
        try:
            agents = self.agent_proxy.list_agents()
            if not agents:
                print("No agents found.")
                return
            
            print("Agents:")
            for agent_id in agents:
                config = self.agent_proxy.get_agent(agent_id)
                state = self.agent_proxy.get_agent_state(agent_id)
                print(f"  {agent_id}: {config.name} ({state.status.value})")
                
        except Exception as e:
            raise CLIError(f"Failed to list agents: {e}")
    
    def _handle_agent_send(self, args: Any):
        """Handle agent send command."""
        try:
            response = self.agent_proxy.send_message(
                agent_id=args.agent_id,
                content=args.message,
                stream=args.stream,
            )
            
            if args.stream:
                for chunk in response:
                    print(chunk, end="", flush=True)
                print()
            else:
                print(response)
                
        except Exception as e:
            raise CLIError(f"Failed to send message to agent: {e}")
    
    def _handle_agent_run(self, args: Any):
        """Handle agent run command."""
        try:
            response = self.agent_proxy.run_agent(
                agent_id=args.agent_id,
                task=args.task,
                max_iterations=args.max_iterations,
            )
            print(response)
            
        except Exception as e:
            raise CLIError(f"Failed to run agent: {e}")
    
    def _handle_agent_info(self, args: Any):
        """Handle agent info command."""
        try:
            config = self.agent_proxy.get_agent(args.agent_id)
            state = self.agent_proxy.get_agent_state(args.agent_id)
            
            print(f"Agent: {config.name}")
            print(f"  ID: {config.agent_id}")
            print(f"  Provider: {config.provider}")
            print(f"  Model: {config.model}")
            print(f"  Status: {state.status.value}")
            print(f"  Tools: {config.tools}")
            print(f"  Temperature: {config.temperature}")
            print(f"  Max Tokens: {config.max_tokens}")
            print(f"  Memory Size: {config.memory_size}")
            print(f"  Max Iterations: {config.max_iterations}")
            print(f"  System Prompt: {config.system_prompt[:100]}..." if len(config.system_prompt) > 100 else f"  System Prompt: {config.system_prompt}")
            
        except Exception as e:
            raise CLIError(f"Failed to get agent info: {e}")
    
    def _handle_agent_destroy(self, args: Any):
        """Handle agent destroy command."""
        try:
            self.agent_proxy.destroy_agent(args.agent_id)
            print(f"Destroyed agent: {args.agent_id}")
            
            # Remove from config
            if "agents" in self.config:
                for name, aid in list(self.config["agents"].items()):
                    if aid == args.agent_id:
                        del self.config["agents"][name]
                        self._save_config()
                        break
                        
        except Exception as e:
            raise CLIError(f"Failed to destroy agent: {e}")
    
    def _handle_agent_history(self, args: Any):
        """Handle agent history command."""
        try:
            messages = self.agent_proxy.get_conversation(args.agent_id)
            if not messages:
                print("No conversation history.")
                return
            
            for message in messages:
                print(f"[{message.role.value.upper()}] {message.content[:200]}" + ("..." if len(message.content) > 200 else ""))
                
        except Exception as e:
            raise CLIError(f"Failed to get conversation history: {e}")
    
    def _add_collab_commands(self, subparsers: Any):
        """Add collab commands."""
        # Collab subparser
        collab_parser = subparsers.add_parser(
            "collab",
            help="Google Colab integration",
            description="Manage Google Colab notebooks and execution",
        )
        
        collab_subparsers = collab_parser.add_subparsers(
            title="collab_commands",
            dest="collab_command",
        )
        
        # Notebook commands
        notebook_parser = collab_subparsers.add_parser(
            "notebook",
            help="Manage notebooks",
        )
        notebook_subparsers = notebook_parser.add_subparsers(
            title="notebook_commands",
            dest="notebook_command",
        )
        
        # Create notebook
        create_parser = notebook_subparsers.add_parser(
            "create",
            help="Create a new notebook",
        )
        create_parser.add_argument(
            "--name", "-n",
            type=str,
            required=True,
            help="Notebook name",
        )
        create_parser.add_argument(
            "--content", "-c",
            type=str,
            default="",
            help="Initial notebook content",
        )
        create_parser.set_defaults(func=self._handle_collab_notebook_create)
        
        # List notebooks
        list_parser = notebook_subparsers.add_parser(
            "list",
            help="List notebooks",
        )
        list_parser.set_defaults(func=self._handle_collab_notebook_list)
        
        # Execute cell
        execute_parser = notebook_subparsers.add_parser(
            "execute",
            help="Execute a cell",
        )
        execute_parser.add_argument(
            "--notebook-id", "-n",
            type=str,
            required=True,
            help="Notebook ID",
        )
        execute_parser.add_argument(
            "--cell-index", "-c",
            type=int,
            required=True,
            help="Cell index",
        )
        execute_parser.set_defaults(func=self._handle_collab_cell_execute)
        
        # Inject code
        inject_parser = notebook_subparsers.add_parser(
            "inject",
            help="Inject code into a notebook",
        )
        inject_parser.add_argument(
            "--notebook-id", "-n",
            type=str,
            required=True,
            help="Notebook ID",
        )
        inject_parser.add_argument(
            "--code", "-c",
            type=str,
            required=True,
            help="Code to inject",
        )
        inject_parser.add_argument(
            "--cell-index",
            type=int,
            default=None,
            help="Cell index to inject at (default: append)",
        )
        inject_parser.set_defaults(func=self._handle_collab_code_inject)
    
    def _handle_collab_notebook_create(self, args: Any):
        """Handle collab notebook create command."""
        if not _COLLAB_AVAILABLE:
            raise CLIError("Collab integration not available")
        
        try:
            notebook = self.colab_client.create_notebook(
                name=args.name,
                content=args.content,
            )
            print(f"Created notebook: {notebook.notebook_id}")
            
        except Exception as e:
            raise CLIError(f"Failed to create notebook: {e}")
    
    def _handle_collab_notebook_list(self, args: Any):
        """Handle collab notebook list command."""
        if not _COLLAB_AVAILABLE:
            raise CLIError("Collab integration not available")
        
        try:
            notebooks = self.colab_client.list_notebooks()
            if not notebooks:
                print("No notebooks found.")
                return
            
            print("Notebooks:")
            for notebook in notebooks:
                print(f"  {notebook.notebook_id}: {notebook.name}")
                
        except Exception as e:
            raise CLIError(f"Failed to list notebooks: {e}")
    
    def _handle_collab_cell_execute(self, args: Any):
        """Handle collab cell execute command."""
        if not _COLLAB_AVAILABLE:
            raise CLIError("Collab integration not available")
        
        try:
            result = self.colab_client.execute_cell(
                notebook_id=args.notebook_id,
                cell_index=args.cell_index,
            )
            print(f"Cell executed: {result}")
            
        except Exception as e:
            raise CLIError(f"Failed to execute cell: {e}")
    
    def _handle_collab_code_inject(self, args: Any):
        """Handle collab code inject command."""
        if not _COLLAB_AVAILABLE:
            raise CLIError("Collab integration not available")
        
        try:
            result = self.colab_client.inject_code(
                notebook_id=args.notebook_id,
                code=args.code,
                cell_index=args.cell_index,
            )
            print(f"Code injected: {result}")
            
        except Exception as e:
            raise CLIError(f"Failed to inject code: {e}")
    
    def _add_provider_commands(self, subparsers: Any):
        """Add provider commands."""
        # Provider subparser
        provider_parser = subparsers.add_parser(
            "provider",
            help="Manage providers",
            description="List, add, remove, and configure providers",
        )
        
        provider_subparsers = provider_parser.add_subparsers(
            title="provider_commands",
            dest="provider_command",
        )
        
        # List providers
        list_parser = provider_subparsers.add_parser(
            "list",
            help="List all providers",
        )
        list_parser.set_defaults(func=self._handle_provider_list)
        
        # Get provider info
        info_parser = provider_subparsers.add_parser(
            "info",
            help="Get provider information",
        )
        info_parser.add_argument(
            "--provider", "-p",
            type=str,
            required=True,
            help="Provider name",
        )
        info_parser.set_defaults(func=self._handle_provider_info)
        
        # Set default provider
        default_parser = provider_subparsers.add_parser(
            "default",
            help="Set default provider",
        )
        default_parser.add_argument(
            "--provider", "-p",
            type=str,
            required=True,
            help="Provider name",
        )
        default_parser.set_defaults(func=self._handle_provider_default)
    
    def _handle_provider_list(self, args: Any):
        """Handle provider list command."""
        try:
            providers = self.hub.list_providers()
            if not providers:
                print("No providers found.")
                return
            
            print("Providers:")
            for provider in providers:
                config = self.hub._providers[provider]
                print(f"  {provider}: {config.provider_type.value} (priority={config.priority}, enabled={config.enabled})")
                
        except Exception as e:
            raise CLIError(f"Failed to list providers: {e}")
    
    def _handle_provider_info(self, args: Any):
        """Handle provider info command."""
        try:
            if args.provider not in self.hub.list_providers():
                raise CLIError(f"Provider '{args.provider}' not found")
            
            config = self.hub._providers[args.provider]
            
            print(f"Provider: {args.provider}")
            print(f"  Type: {config.provider_type.value}")
            print(f"  Enabled: {config.enabled}")
            print(f"  Priority: {config.priority}")
            print(f"  Base URL: {config.base_url or 'default'}")
            print(f"  Timeout: {config.timeout}")
            print(f"  Max Retries: {config.max_retries}")
            print(f"  Proxy: {config.proxy or 'none'}")
            print(f"  Impersonate: {config.impersonate or 'none'}")
            
            # Get models if available
            try:
                provider = self.hub.get_provider(args.provider)
                if hasattr(provider, "list_models"):
                    models = provider.list_models()
                    print(f"  Models: {models}")
            except Exception:
                pass
                
        except Exception as e:
            raise CLIError(f"Failed to get provider info: {e}")
    
    def _handle_provider_default(self, args: Any):
        """Handle provider default command."""
        try:
            if args.provider not in self.hub.list_providers():
                raise CLIError(f"Provider '{args.provider}' not found")
            
            self.hub.default_provider = args.provider
            self.config["default_provider"] = args.provider
            self._save_config()
            
            print(f"Default provider set to: {args.provider}")
            
        except Exception as e:
            raise CLIError(f"Failed to set default provider: {e}")
    
    def _add_session_commands(self, subparsers: Any):
        """Add session commands."""
        # Session subparser
        session_parser = subparsers.add_parser(
            "session",
            help="Manage sessions",
            description="Create, list, and destroy chat sessions",
        )
        
        session_subparsers = session_parser.add_subparsers(
            title="session_commands",
            dest="session_command",
        )
        
        # Create session
        create_parser = session_subparsers.add_parser(
            "create",
            help="Create a new session",
        )
        create_parser.add_argument(
            "--provider", "-p",
            type=str,
            default=None,
            help="Provider to use (default: configured default)",
        )
        create_parser.add_argument(
            "--model", "-m",
            type=str,
            default=None,
            help="Model to use",
        )
        create_parser.add_argument(
            "--system-prompt", "-s",
            type=str,
            default="",
            help="System prompt for the session",
        )
        create_parser.add_argument(
            "--temperature", "-t",
            type=float,
            default=0.7,
            help="Temperature setting",
        )
        create_parser.add_argument(
            "--max-tokens",
            type=int,
            default=4096,
            help="Maximum tokens",
        )
        create_parser.set_defaults(func=self._handle_session_create)
        
        # List sessions
        list_parser = session_subparsers.add_parser(
            "list",
            help="List all sessions",
        )
        list_parser.set_defaults(func=self._handle_session_list)
        
        # Destroy session
        destroy_parser = session_subparsers.add_parser(
            "destroy",
            help="Destroy a session",
        )
        destroy_parser.add_argument(
            "--session-id", "-s",
            type=str,
            required=True,
            help="Session ID",
        )
        destroy_parser.set_defaults(func=self._handle_session_destroy)
        
        # Send message to session
        send_parser = session_subparsers.add_parser(
            "send",
            help="Send a message to a session",
        )
        send_parser.add_argument(
            "--session-id", "-s",
            type=str,
            required=True,
            help="Session ID",
        )
        send_parser.add_argument(
            "--message", "-M",
            type=str,
            required=True,
            help="Message to send",
        )
        send_parser.add_argument(
            "--stream",
            action="store_true",
            help="Stream the response",
        )
        send_parser.set_defaults(func=self._handle_session_send)
    
    def _handle_session_create(self, args: Any):
        """Handle session create command."""
        try:
            session_id = self.hub.create_session(
                provider=args.provider,
                model=args.model,
                system_prompt=args.system_prompt,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
            print(f"Created session: {session_id}")
            
        except Exception as e:
            raise CLIError(f"Failed to create session: {e}")
    
    def _handle_session_list(self, args: Any):
        """Handle session list command."""
        try:
            sessions = self.hub.list_sessions()
            if not sessions:
                print("No sessions found.")
                return
            
            print("Sessions:")
            for session_id in sessions:
                session = self.hub.get_session(session_id)
                print(f"  {session_id}: provider={session.provider}, model={session.model}")
                
        except Exception as e:
            raise CLIError(f"Failed to list sessions: {e}")
    
    def _handle_session_destroy(self, args: Any):
        """Handle session destroy command."""
        try:
            self.hub.destroy_session(args.session_id)
            print(f"Destroyed session: {args.session_id}")
            
        except Exception as e:
            raise CLIError(f"Failed to destroy session: {e}")
    
    def _handle_session_send(self, args: Any):
        """Handle session send command."""
        try:
            response = self.hub.send_message(
                session_id=args.session_id,
                message=args.message,
                stream=args.stream,
            )
            
            if args.stream:
                for chunk in response:
                    print(chunk, end="", flush=True)
                print()
            else:
                print(response)
                
        except Exception as e:
            raise CLIError(f"Failed to send message to session: {e}")
    
    def _add_tool_commands(self, subparsers: Any):
        """Add tool commands."""
        # Tool subparser
        tool_parser = subparsers.add_parser(
            "tool",
            help="Manage tools",
            description="List and manage available tools",
        )
        
        tool_subparsers = tool_parser.add_subparsers(
            title="tool_commands",
            dest="tool_command",
        )
        
        # List tools
        list_parser = tool_subparsers.add_parser(
            "list",
            help="List all tools",
        )
        list_parser.set_defaults(func=self._handle_tool_list)
        
        # Execute tool
        execute_parser = tool_subparsers.add_parser(
            "execute",
            help="Execute a tool",
        )
        execute_parser.add_argument(
            "--name", "-n",
            type=str,
            required=True,
            help="Tool name",
        )
        execute_parser.add_argument(
            "--arguments", "-a",
            type=str,
            default="{}",
            help="Tool arguments as JSON",
        )
        execute_parser.set_defaults(func=self._handle_tool_execute)
    
    def _handle_tool_list(self, args: Any):
        """Handle tool list command."""
        try:
            tools = self.agent_proxy.tool_registry
            if not tools:
                print("No tools found.")
                return
            
            print("Tools:")
            for name, tool in tools.items():
                print(f"  {name}: {tool.description}")
                
        except Exception as e:
            raise CLIError(f"Failed to list tools: {e}")
    
    def _handle_tool_execute(self, args: Any):
        """Handle tool execute command."""
        try:
            # Parse arguments
            try:
                arguments = json.loads(args.arguments)
            except json.JSONDecodeError:
                arguments = {}
            
            # Create a tool call
            from ..hub.agent_proxy import ToolCall
            tool_call = ToolCall(
                id=str(uuid.uuid4()),
                name=args.name,
                arguments=arguments,
            )
            
            # Execute the tool
            result = self.agent_proxy._execute_tool("tool_execution", tool_call)
            
            if result.is_error:
                print(f"Error: {result.error_message}")
            else:
                print(result.content)
                
        except Exception as e:
            raise CLIError(f"Failed to execute tool: {e}")
    
    def _add_hub_commands(self, subparsers: Any):
        """Add hub commands."""
        # Hub subparser
        hub_parser = subparsers.add_parser(
            "hub",
            help="Manage the hub",
            description="Control and configure the multi-provider hub",
        )
        
        hub_subparsers = hub_parser.add_subparsers(
            title="hub_commands",
            dest="hub_command",
        )
        
        # Status
        status_parser = hub_subparsers.add_parser(
            "status",
            help="Get hub status",
        )
        status_parser.set_defaults(func=self._handle_hub_status)
        
        # Router stats
        router_parser = hub_subparsers.add_parser(
            "router-stats",
            help="Get router statistics",
        )
        router_parser.set_defaults(func=self._handle_hub_router_stats)
        
        # Reset router stats
        reset_parser = hub_subparsers.add_parser(
            "reset-stats",
            help="Reset router statistics",
        )
        reset_parser.set_defaults(func=self._handle_hub_reset_stats)
        
        # Set routing strategy
        strategy_parser = hub_subparsers.add_parser(
            "routing-strategy",
            help="Set routing strategy",
        )
        strategy_parser.add_argument(
            "--strategy", "-s",
            type=str,
            choices=[s.value for s in RoutingStrategy],
            required=True,
            help="Routing strategy",
        )
        strategy_parser.set_defaults(func=self._handle_hub_routing_strategy)
    
    def _handle_hub_status(self, args: Any):
        """Handle hub status command."""
        try:
            print("Hub Status:")
            print(f"  Default Provider: {self.hub.default_provider}")
            print(f"  Providers: {len(self.hub.list_providers())}")
            print(f"  Sessions: {len(self.hub.list_sessions())}")
            print(f"  Agents: {len(self.agent_proxy.list_agents())}")
            print(f"  Transport: {type(self.hub.get_transport()).__name__ if self.hub.get_transport() else 'None'}")
            
        except Exception as e:
            raise CLIError(f"Failed to get hub status: {e}")
    
    def _handle_hub_router_stats(self, args: Any):
        """Handle hub router stats command."""
        try:
            stats = self.router.get_stats()
            print("Router Statistics:")
            print(f"  Total Requests: {stats['total_requests']}")
            print(f"  Successful: {stats['successful_requests']}")
            print(f"  Failed: {stats['failed_requests']}")
            print(f"  Strategy: {stats['strategy']}")
            print(f"  Provider Requests: {stats['provider_requests']}")
            print(f"  Provider Errors: {stats['provider_errors']}")
            
        except Exception as e:
            raise CLIError(f"Failed to get router stats: {e}")
    
    def _handle_hub_reset_stats(self, args: Any):
        """Handle hub reset stats command."""
        try:
            self.router.reset_stats()
            print("Router statistics reset.")
            
        except Exception as e:
            raise CLIError(f"Failed to reset stats: {e}")
    
    def _handle_hub_routing_strategy(self, args: Any):
        """Handle hub routing strategy command."""
        try:
            strategy = RoutingStrategy(args.strategy)
            self.router.set_strategy(strategy)
            self.config["routing_strategy"] = args.strategy
            self._save_config()
            print(f"Routing strategy set to: {args.strategy}")
            
        except Exception as e:
            raise CLIError(f"Failed to set routing strategy: {e}")
    
    def _add_github_commands(self, subparsers: Any):
        """Add GitHub commands."""
        if not _COLLAB_AVAILABLE:
            return
        
        # GitHub subparser
        github_parser = subparsers.add_parser(
            "github",
            help="GitHub Actions integration",
            description="Run and manage GitHub Actions workflows",
        )
        
        github_subparsers = github_parser.add_subparsers(
            title="github_commands",
            dest="github_command",
        )
        
        # Run workflow
        run_parser = github_subparsers.add_parser(
            "run",
            help="Run a workflow",
        )
        run_parser.add_argument(
            "--repo", "-r",
            type=str,
            required=True,
            help="Repository (owner/repo)",
        )
        run_parser.add_argument(
            "--workflow", "-w",
            type=str,
            required=True,
            help="Workflow ID or filename",
        )
        run_parser.add_argument(
            "--branch", "-b",
            type=str,
            default="main",
            help="Branch name",
        )
        run_parser.set_defaults(func=self._handle_github_run)
        
        # List workflows
        list_parser = github_subparsers.add_parser(
            "list",
            help="List workflows",
        )
        list_parser.add_argument(
            "--repo", "-r",
            type=str,
            required=True,
            help="Repository (owner/repo)",
        )
        list_parser.set_defaults(func=self._handle_github_list)
    
    def _handle_github_run(self, args: Any):
        """Handle GitHub run command."""
        try:
            result = self.github_client.run_workflow(
                repo=args.repo,
                workflow_id=args.workflow,
                branch=args.branch,
            )
            print(f"Workflow started: {result}")
            
        except Exception as e:
            raise CLIError(f"Failed to run workflow: {e}")
    
    def _handle_github_list(self, args: Any):
        """Handle GitHub list command."""
        try:
            workflows = self.github_client.list_workflows(args.repo)
            if not workflows:
                print("No workflows found.")
                return
            
            print("Workflows:")
            for workflow in workflows:
                print(f"  {workflow['id']}: {workflow['name']}")
                
        except Exception as e:
            raise CLIError(f"Failed to list workflows: {e}")
    
    def _add_termux_commands(self, subparsers: Any):
        """Add Termux commands."""
        if not _COLLAB_AVAILABLE:
            return
        
        # Termux subparser
        termux_parser = subparsers.add_parser(
            "termux",
            help="Termux integration",
            description="Termux-specific commands and integration",
        )
        
        termux_subparsers = termux_parser.add_subparsers(
            title="termux_commands",
            dest="termux_command",
        )
        
        # Setup SSH tunnel
        tunnel_parser = termux_subparsers.add_parser(
            "tunnel",
            help="Setup SSH tunnel for Colab",
        )
        tunnel_parser.add_argument(
            "--port", "-p",
            type=int,
            default=8080,
            help="Local port",
        )
        tunnel_parser.add_argument(
            "--remote-port", "-r",
            type=int,
            default=22,
            help="Remote port",
        )
        tunnel_parser.set_defaults(func=self._handle_termux_tunnel)
        
        # Check environment
        check_parser = termux_subparsers.add_parser(
            "check",
            help="Check Termux environment",
        )
        check_parser.set_defaults(func=self._handle_termux_check)
    
    def _handle_termux_tunnel(self, args: Any):
        """Handle Termux tunnel command."""
        try:
            result = self.termux_integration.setup_ssh_tunnel(
                local_port=args.port,
                remote_port=args.remote_port,
            )
            print(f"SSH tunnel setup: {result}")
            
        except Exception as e:
            raise CLIError(f"Failed to setup SSH tunnel: {e}")
    
    def _handle_termux_check(self, args: Any):
        """Handle Termux check command."""
        try:
            info = self.termux_integration.get_environment_info()
            print("Termux Environment:")
            for key, value in info.items():
                print(f"  {key}: {value}")
            
        except Exception as e:
            raise CLIError(f"Failed to check environment: {e}")


def main():
    """Main entry point for the CLI."""
    import sys
    
    # Set up import path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    try:
        cli = MultiAICLI()
        cli.run()
    except CLIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "main",
    "CLIError",
    "MultiAICLI",
]
