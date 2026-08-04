#!/usr/bin/env python3
"""Mistralai Vibe Code webWrapper CLI - Main Interface

This is the main entry point for multi-ai-cli, which provides a unified interface
for selecting between different AI providers (Mistral, DeepSeek, etc.).
"""
import os
import sys
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import core modules
from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher
from harvesters.code_harvester import CodeHarvester
from harvesters.search_engine import SearchEngine
from harvesters.extractor import CodeExtractor
from harvesters.analyzer import CodeAnalyzer
from tools.file_utils import FileUtils
from tools.git_utils import GitUtils
from tools.network_utils import NetworkUtils
from tools.termux_utils import TermuxUtils

console = Console()

# Configuration
CONFIG_DIR = Path.home() / ".mistralai-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Ensure directories exist
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", type=str, default=str(CONFIG_FILE), help="Path to config file")
def cli(verbose, config):
    """Multi-AI CLI - Unified interface for AI providers
    
    Select and use different AI providers (Mistral, DeepSeek, etc.)
    with code harvesting, search, and analysis capabilities.
    """
    global verbose_mode, config_path
    verbose_mode = verbose
    config_path = config
    
    if verbose:
        console.print("[bold blue]Multi-AI CLI[/bold blue]")
        console.print(f"Config: {config}")
        console.print(f"Verbose: {verbose}")

@cli.group()
def provider():
    """Provider selection and management."""
    pass

@provider.command()
@click.argument("name", required=False)
@click.option("--list", "-l", is_flag=True, help="List available providers")
def select(name, list):
    """
    List available AI providers or set the default provider.
    
    Parameters:
        name (str): Provider name to save as the default.
        list (bool): Whether to display available providers instead of selecting one.
    """
    if list or not name:
        # List available providers
        providers = get_available_providers()
        
        table = Table(title="Available AI Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Status", style="blue")
        
        for prov_name, prov_info in providers.items():
            status = "[green]Available[/green]" if prov_info.get("available", True) else "[red]Unavailable[/red]"
            table.add_row(prov_name, prov_info.get("description", ""), status)
        
        console.print(table)
        return
    
    # Set default provider
    cfg = load_config()
    cfg["default_provider"] = name
    save_config(cfg)
    console.print(f"[green]Default provider set to: {name}[/green]")

@provider.command()
@click.argument("provider_name", required=True)
@click.argument("args", nargs=-1, required=False)
def run(provider_name, args):
    """
    Run the selected provider's command-line interface.
    
    Parameters:
        provider_name (str): Name of the provider to execute.
        args (Iterable[str]): Arguments to pass to the provider's command-line interface.
    """
    providers = get_available_providers()
    
    if provider_name not in providers:
        console.print(f"[red]Unknown provider: {provider_name}[/red]")
        console.print(f"Available providers: {', '.join(providers.keys())}")
        return
    
    prov_info = providers[provider_name]
    
    if not prov_info.get("available", True):
        console.print(f"[red]Provider {provider_name} is not available[/red]")
        return
    
    # Execute the provider's CLI
    import subprocess
    
    if provider_name == "deepseek":
        # Run deepcli
        deepcli_path = Path.home() / "deepcli" / "deepcli.py"
        if deepcli_path.exists():
            cmd = ["python3", str(deepcli_path)] + list(args)
            console.print(f"[blue]Running: {' '.join(cmd)}[/blue]")
            result = subprocess.run(cmd, capture_output=True, text=True)
            console.print(result.stdout)
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]", file=sys.stderr)
            return
    
    elif provider_name == "deepseek-tui":
        # Run deepcli-tui
        tui_path = Path.home() / "deepcli-tui" / "tui.py"
        if tui_path.exists():
            cmd = ["python3", str(tui_path)] + list(args)
            console.print(f"[blue]Running: {' '.join(cmd)}[/blue]")
            result = subprocess.run(cmd, capture_output=True, text=True)
            console.print(result.stdout)
            if result.stderr:
                console.print(f"[red]{result.stderr}[/red]", file=sys.stderr)
            return
    
    elif provider_name == "mistral":
        # Use our native Mistral implementation
        console.print(f"[blue]Using native Mistral implementation[/blue]")
        # For now, just show help
        console.print("Native Mistral commands:")
        console.print("  mistralai-cli session new")
        console.print("  mistralai-cli chat send <message>")
        return
    
    console.print(f"[red]Provider {provider_name} execution not implemented[/red]")

def get_available_providers():
    """Describe the supported AI providers and their availability.
    
    Returns:
    	providers (dict): Provider metadata, including descriptions, availability,
    	and executable paths for subprocess-based providers.
    """
    providers = {
        "mistral": {
            "description": "Mistral AI (native implementation)",
            "available": True,
            "module": "native",
        },
        "deepseek": {
            "description": "DeepSeek CLI",
            "available": (Path.home() / "deepcli" / "deepcli.py").exists(),
            "module": "subprocess",
            "path": str(Path.home() / "deepcli" / "deepcli.py"),
        },
        "deepseek-tui": {
            "description": "DeepSeek TUI",
            "available": (Path.home() / "deepcli-tui" / "tui.py").exists(),
            "module": "subprocess",
            "path": str(Path.home() / "deepcli-tui" / "tui.py"),
        },
    }
    
    return providers

# Import existing functions from core
from core.core import (
    get_token, create_session, fetch_sessions, get_history,
    stream_completion, send_message, upload_file, wait_for_file,
    load_config, save_config, _set_last_session, MistralCore
)

@cli.group()
def session():
    """Session management commands (Mistral-specific)."""
    pass

@session.command()
@click.option("--model", "-m", type=str, default="mistral-large-latest", help="Model to use")
def new(model):
    """Create a new chat session."""
    try:
        core = MistralCore()
        session_id = core.create_session(model)
        console.print(f"[green]New session created: {session_id}[/green]")
        
        # Save to config
        cfg = load_config()
        cfg["last_session"] = session_id
        save_config(cfg)
    except Exception as e:
        console.print(f"[red]Error creating session: {e}[/red]")

@session.command()
def list():
    """
    List available chat sessions in a formatted table.
    
    If no sessions are available, displays a corresponding message. Errors are reported to the console.
    """
    try:
        core = MistralCore()
        sessions = core.list_sessions()
        
        if not sessions:
            console.print("[yellow]No sessions found[/yellow]")
            return
        
        table = Table(title="Chat Sessions")
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Created", style="blue")
        
        for session in sessions:
            sid = session.get("id") or session.get("chat_session_id", "unknown")
            title = session.get("title") or session.get("name", "(untitled)")
            created = session.get("created_at", "unknown")
            table.add_row(sid[:8] + "...", title, created[:10] if created else "unknown")
        
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error listing sessions: {e}[/red]")

@session.command()
@click.argument("session_id", required=False)
def select(session_id):
    """
    Select a session and save it as the current session.
    
    Parameters:
    	session_id: The session identifier to select. If omitted, prompts for a session from the available sessions.
    """
    try:
        if not session_id:
            # List sessions and let user choose
            core = MistralCore()
            sessions = core.list_sessions()
            
            if not sessions:
                console.print("[yellow]No sessions found[/yellow]")
                return
            
            table = Table(title="Select Session")
            table.add_column("Index", style="cyan")
            table.add_column("ID", style="green")
            table.add_column("Title", style="blue")
            
            for idx, session in enumerate(sessions):
                sid = session.get("id") or session.get("chat_session_id", "unknown")
                title = session.get("title") or session.get("name", "(untitled)")
                table.add_row(str(idx), sid[:8] + "...", title)
            
            console.print(table)
            console.print("[yellow]Enter the index of the session to select:[/yellow]")
            choice = input("> ")
            
            try:
                idx = int(choice)
                selected = sessions[idx]
                session_id = selected.get("id") or selected.get("chat_session_id")
            except (ValueError, IndexError):
                console.print("[red]Invalid selection[/red]")
                return
        
        # Save selection
        cfg = load_config()
        cfg["last_session"] = session_id
        save_config(cfg)
        console.print(f"[green]Selected session: {session_id}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error selecting session: {e}[/red]")

@cli.group()
def chat():
    """Chat commands (Mistral-specific)."""
    pass

@chat.command()
@click.argument("message", required=True)
@click.option("--session", "-s", type=str, help="Session ID to use")
@click.option("--model", "-m", type=str, default="mistral-large-latest", help="Model to use")
@click.option("--stream", is_flag=True, help="Stream the response")
def send(message, session, model, stream):
    """
    Send a message through the selected chat session and display the response.
    
    Parameters:
        message: Message content to send.
        session: Optional session identifier; uses the configured last session when omitted.
        model: Optional model to use for the response.
        stream: Whether to display the response as it is generated.
    """
    try:
        cfg = load_config()
        session_id = session or cfg.get("last_session")
        
        if not session_id:
            console.print("[red]No session selected. Use 'session new' or 'session select' first.[/red]")
            return
        
        core = MistralCore()
        
        if stream:
            console.print("[bold blue]Streaming response...[/bold blue]")
            response = core.stream_message(message, session_id, model=model)
        else:
            from rich.progress import Progress, SpinnerColumn, TextColumn
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Sending message...", total=None)
                response = core.send_message(message, session_id, model=model)
                progress.remove_task(task)
            
            console.print(f"[bold green]Response:[/bold green]")
            console.print(Panel(response, border_style="green"))
        
    except Exception as e:
        console.print(f"[red]Error sending message: {e}[/red]")

@chat.command()
@click.argument("session_id", required=False)
@click.option("--limit", "-n", type=int, default=10, help="Number of messages to show")
def history(session_id, limit):
    """
    Display recent messages from a chat session.
    
    Parameters:
    	session_id: The session identifier; when omitted, the configured last session is used.
    	limit: Maximum number of recent messages to display.
    """
    try:
        cfg = load_config()
        sid = session_id or cfg.get("last_session")
        
        if not sid:
            console.print("[red]No session selected. Use 'session new' or 'session select' first.[/red]")
            return
        
        core = MistralCore()
        messages = core.get_history(sid)
        
        if not messages:
            console.print("[yellow]No messages in this session[/yellow]")
            return
        
        # Show last 'limit' messages
        recent_messages = messages[-limit:]
        
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            if role == "user":
                console.print(f"[bold blue]User:[/bold blue] {content[:200]}{'...' if len(content) > 200 else ''}")
            elif role == "assistant":
                console.print(f"[bold green]Assistant:[/bold green] {content[:200]}{'...' if len(content) > 200 else ''}")
            else:
                console.print(f"[bold yellow]{role}:[/bold yellow] {content[:200]}{'...' if len(content) > 200 else ''}")
            console.print("---")
        
    except Exception as e:
        console.print(f"[red]Error getting history: {e}[/red]")

@cli.group()
def harvest():
    """Code harvesting commands."""
    pass

@harvest.command()
@click.argument("path", type=str, required=True)
@click.option("--recursive", "-r", is_flag=True, help="Harvest recursively")
@click.option("--patterns", "-p", type=str, multiple=True, help="File patterns to include")
@click.option("--output", "-o", type=str, help="Output file name")
def code(path, recursive, patterns, output):
    """Harvest code snippets from a file or directory and save them to storage.
    
    Parameters:
        path: File or directory to harvest.
        recursive: Whether to search directories recursively.
        patterns: Optional filename patterns used to filter directory harvesting.
        output: Optional storage name; a timestamped name is used when omitted.
    """
    try:
        harvester = CodeHarvester()
        
        from rich.progress import Progress, SpinnerColumn, TextColumn
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Harvesting code from {path}...", total=None)
            
            if os.path.isfile(path):
                snippets = harvester.harvest_file(path)
            else:
                snippets = harvester.harvest_directory(path, recursive, list(patterns) if patterns else None)
            
            progress.remove_task(task)
        
        console.print(f"[green]Harvested {len(snippets)} code snippets[/green]")
        
        if output:
            harvester.save_to_storage(output)
        else:
            # Save with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            harvester.save_to_storage(f"harvest_{timestamp}")
        
    except Exception as e:
        console.print(f"[red]Error harvesting code: {e}[/red]")

@harvest.command()
@click.argument("text_file", type=str, required=True)
@click.option("--output", "-o", type=str, help="Output file name")
def text(text_file, output):
    """Harvest code snippets from a text file and save them to storage."""
    try:
        harvester = CodeHarvester()
        
        content = FileUtils.read_file(text_file)
        if not content:
            console.print(f"[red]Failed to read {text_file}[/red]")
            return
        
        snippets = harvester.harvest_from_text(content, text_file)
        console.print(f"[green]Harvested {len(snippets)} code snippets from text[/green]")
        
        if output:
            harvester.save_to_storage(output)
        else:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            harvester.save_to_storage(f"text_harvest_{timestamp}")
        
    except Exception as e:
        console.print(f"[red]Error harvesting from text: {e}[/red]")

@cli.group()
def search():
    """Search commands."""
    pass

@search.command()
@click.argument("query", type=str, required=True)
@click.option("--index", "-i", type=str, help="Index name to search")
@click.option("--limit", "-n", type=int, default=10, help="Number of results to show")
def code(query, index, limit):
    """
    Search harvested code and display matching results.
    
    Parameters:
    	query (str): Search query.
    	index (str): Optional path to a search index to load.
    	limit (int): Maximum number of results to display.
    """
    try:
        engine = SearchEngine()
        
        if index:
            if not engine.load_index(index):
                console.print(f"[red]Failed to load index: {index}[/red]")
                return
        
        results = engine.search(query, limit)
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
        
        console.print(f"[green]Found {len(results)} results:[/green]")
        
        for idx, result in enumerate(results, 1):
            console.print(f"\n[bold blue]Result {idx}:[/bold blue]")
            console.print(f"  Language: {result.language}")
            console.print(f"  Source: {result.source}")
            console.print(f"  File: {result.file_path}")
            console.print(f"  Score: {result.score:.2f}")
            console.print(f"  Content: {result.content[:200]}{'...' if len(result.content) > 200 else ''}")
        
    except Exception as e:
        console.print(f"[red]Error searching: {e}[/red]")

@search.command()
@click.argument("language", type=str, required=True)
@click.option("--query", "-q", type=str, default="", help="Additional query filter")
@click.option("--limit", "-n", type=int, default=10, help="Number of results to show")
def by_language(language, query, limit):
    """
    Search harvested code snippets by programming language and optional query.
    
    Parameters:
        language (str): Programming language to search for.
        query (str): Optional text to match within the snippets.
        limit (int): Maximum number of matching snippets to display.
    """
    try:
        engine = SearchEngine()
        results = engine.search_by_language(language, query, limit)
        
        if not results:
            console.print(f"[yellow]No {language} code found[/yellow]")
            return
        
        console.print(f"[green]Found {len(results)} {language} snippets:[/green]")
        
        for idx, result in enumerate(results, 1):
            console.print(f"\n[bold blue]Result {idx}:[/bold blue]")
            console.print(f"  Source: {result.source}")
            console.print(f"  File: {result.file_path}")
            console.print(f"  Content: {result.content[:200]}{'...' if len(result.content) > 200 else ''}")
        
    except Exception as e:
        console.print(f"[red]Error searching by language: {e}[/red]")

@cli.group()
def analyze():
    """Code analysis commands."""
    pass

@analyze.command()
@click.argument("file_path", type=str, required=True)
@click.option("--language", "-l", type=str, help="Language of the file")
def file(file_path, language):
    """Analyze a code file and display its structural metrics, complexity, and reported issues."""
    try:
        analyzer = CodeAnalyzer()
        
        content = FileUtils.read_file(file_path)
        if not content:
            console.print(f"[red]Failed to read {file_path}[/red]")
            return
        
        # Detect language if not specified
        if not language:
            extractor = CodeExtractor()
            language = extractor._detect_language(file_path, content)
        
        from rich.progress import Progress, SpinnerColumn, TextColumn
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Analyzing {file_path}...", total=None)
            result = analyzer.analyze(content, language)
            progress.remove_task(task)
        
        console.print(f"[bold green]Analysis Results for {file_path}:[/bold green]")
        console.print(f"  Language: {language}")
        console.print(f"  Lines: {result.metadata.get('line_count', 0)}")
        console.print(f"  Functions: {len(result.functions)}")
        console.print(f"  Classes: {len(result.classes)}")
        console.print(f"  Imports: {len(result.imports)}")
        console.print(f"  Dependencies: {len(result.dependencies)}")
        console.print(f"  Complexity: {result.complexity}")
        
        if result.issues:
            console.print(f"\n[bold red]Issues:[/bold red]")
            for issue in result.issues:
                console.print(f"  - {issue.get('type', 'unknown')}: {issue.get('message', '')}")
        
    except Exception as e:
        console.print(f"[red]Error analyzing file: {e}[/red]")

@cli.group()
def tools():
    """Group commands for extracting content, displaying system information, and cleaning up tool data."""
    pass

@tools.command()
@click.argument("text", type=str, required=True)
@click.option("--output", "-o", type=str, help="Output file path")
def extract(text, output):
    """
    Extracts code blocks from text and optionally saves them as JSON.
    
    Parameters:
        text (str): Text containing code blocks to extract.
        output (str): Optional path for the JSON file containing the extracted blocks.
    """
    try:
        extractor = CodeExtractor()
        extracted = extractor.extract_from_text(text, "input")
        
        console.print(f"[green]Extracted {len(extracted)} code blocks:[/green]")
        
        for idx, code in enumerate(extracted, 1):
            console.print(f"\n[bold blue]Block {idx}:[/bold blue]")
            console.print(f"  Language: {code.language}")
            console.print(f"  Content: {code.content[:200]}{'...' if len(code.content) > 200 else ''}")
        
        if output:
            import json
            with open(output, 'w') as f:
                json.dump([c.to_dict() for c in extracted], f, indent=2)
            console.print(f"[green]Saved to {output}[/green]")
        
    except Exception as e:
        console.print(f"[red]Error extracting code: {e}[/red]")

@tools.command()
def info():
    """
    Display system, environment, provider, and configuration information.
    """
    console.print("[bold blue]System Information[/bold blue]")
    
    # Basic info
    import platform
    console.print(f"  Platform: {platform.platform()}")
    console.print(f"  Python: {platform.python_version()}")
    console.print(f"  Processor: {platform.processor()}")
    
    # Termux info
    if TermuxUtils.is_termux():
        console.print("\n[bold blue]Termux Information[/bold blue]")
        console.print(f"  Termux: {TermuxUtils.get_termux_version()}")
        console.print(f"  Device: {TermuxUtils.get_device_info()}")
    
    # Git info
    if GitUtils.is_git_repo():
        console.print("\n[bold blue]Git Information[/bold blue]")
        console.print(f"  Root: {GitUtils.get_git_root()}")
        console.print(f"  Branch: {GitUtils.get_current_branch()}")
    
    # Available providers
    console.print("\n[bold blue]Available Providers[/bold blue]")
    providers = get_available_providers()
    for prov_name, prov_info in providers.items():
        status = "[green]Available[/green]" if prov_info.get("available", True) else "[red]Unavailable[/red]"
        console.print(f"  {prov_name}: {status}")
    
    # Config info
    console.print("\n[bold blue]Configuration[/bold blue]")
    cfg = load_config()
    console.print(f"  Config file: {config_path}")
    console.print(f"  Token available: {'Yes' if cfg.get('token') else 'No'}")
    console.print(f"  Last session: {cfg.get('last_session', 'None')}")
    console.print(f"  Default provider: {cfg.get('default_provider', 'None')}")

@tools.command()
def cleanup():
    """Remove and recreate the session cache, harvested-code storage, and search-index directories.
    
    Errors are reported to the console.
    """
    try:
        # Clean up cache
        cache_dir = os.path.join(os.path.expanduser("~/.mistralai-cli"), "session_store")
        if os.path.exists(cache_dir):
            import shutil
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir, exist_ok=True)
            console.print(f"[green]Cleaned up session cache[/green]")
        
        # Clean up harvest storage
        harvest_dir = os.path.join(os.path.expanduser("~/.mistralai-cli"), "harvested_code")
        if os.path.exists(harvest_dir):
            import shutil
            shutil.rmtree(harvest_dir)
            os.makedirs(harvest_dir, exist_ok=True)
            console.print(f"[green]Cleaned up harvested code storage[/green]")
        
        # Clean up search index
        index_dir = os.path.join(os.path.expanduser("~/.mistralai-cli"), "search_index")
        if os.path.exists(index_dir):
            import shutil
            shutil.rmtree(index_dir)
            os.makedirs(index_dir, exist_ok=True)
            console.print(f"[green]Cleaned up search index[/green]")
        
        console.print("[green]Cleanup complete[/green]")
        
    except Exception as e:
        console.print(f"[red]Error during cleanup: {e}[/red]")

@cli.command()
@click.argument("command", required=False)
@click.option("--interactive", "-i", is_flag=True, help="Start interactive mode")
def shell(command, interactive):
    """
    Start an interactive command shell or execute a single command.
    
    Parameters:
        command (str): Command to execute when interactive mode is disabled.
        interactive (bool): Whether to start the interactive shell.
    """
    if interactive or not command:
        console.print("[bold blue]Multi-AI CLI - Interactive Mode[/bold blue]")
        console.print("Type 'help' for available commands, 'exit' to quit")
        
        while True:
            try:
                cmd = input("multi-ai> ").strip()
                
                if not cmd:
                    continue
                elif cmd.lower() in ['exit', 'quit', 'q']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif cmd.lower() in ['help', 'h']:
                    console.print("\n[bold green]Available Commands:[/bold green]")
                    console.print("  provider select - Select AI provider")
                    console.print("  provider run <name> - Run a provider's CLI")
                    console.print("  session new - Create new session")
                    console.print("  session list - List all sessions")
                    console.print("  session select - Select a session")
                    console.print("  chat send <message> - Send message to current session")
                    console.print("  chat history - Show chat history")
                    console.print("  harvest code <path> - Harvest code from path")
                    console.print("  search code <query> - Search harvested code")
                    console.print("  analyze file <path> - Analyze a code file")
                    console.print("  tools info - Show system information")
                    console.print("  tools cleanup - Clean up temporary files")
                    console.print("  help - Show this help")
                    console.print("  exit - Exit interactive mode")
                else:
                    # Parse and execute command
                    import subprocess
                    result = subprocess.run(
                        ["python3", "-m", "multi_ai_cli.mistralai_cli", "--"] + cmd.split(),
                        capture_output=True,
                        text=True
                    )
                    if result.stdout:
                        console.print(result.stdout)
                    if result.stderr:
                        console.print(f"[red]{result.stderr}[/red]", file=sys.stderr)
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    else:
        # Execute single command
        console.print(f"[yellow]Executing: {command}[/yellow]")
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "multi_ai_cli.mistralai_cli", "--"] + command.split(),
            capture_output=True,
            text=True
        )
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(f"[red]{result.stderr}[/red]", file=sys.stderr)

if __name__ == "__main__":
    # Set up error handling
    try:
        cli()
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
