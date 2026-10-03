#!/usr/bin/env python3
import click
from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher
from tools.antigravity_tools import LazyGravityBot, AntimatterBridge, AuditAgent, SearchBridge
from backends.antigravity.antigravity_cli import AntigravityCLIBackend
from backends.antigravity.antigravity_sdk import AntigravitySDKBackend
from backends.antigravity.headless_config import HeadlessConfigBackend
from foss.eigent_ai import EigentAIBackend
from foss.open_code import OpenCodeBackend
from foss.velocity import VelocityBackend

@click.group()
def cli():
    """Multi-AI CLI - A unified interface for various AI backends."""
    pass

@cli.group()
def antigravity():
    """Antigravity tools and commands."""
    pass

@antigravity.command(name="cli")
@click.option("--api-key", "-k", envvar="GEMINI_API_KEY", help="Google AI Studio API key")
@click.option("--provider", "-p", default="gemini", help="Provider to use")
@click.option("--headless", is_flag=True, help="Run in headless mode")
@click.argument("prompt")
def antigravity_cli(api_key, provider, headless, prompt):
    """Run Antigravity CLI (agy) with the given prompt."""
    mgr = SessionManager()
    try:
        backend = AntigravityCLIBackend(mgr)
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        if provider:
            os.environ["AGY_PROVIDER"] = provider
        
        response = backend.send_message(prompt)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@antigravity.command(name="sdk")
@click.option("--api-key", "-k", envvar="GEMINI_API_KEY", help="Google AI Studio API key")
@click.option("--provider", "-p", default="gemini", help="Provider to use")
@click.argument("prompt")
def antigravity_sdk(api_key, provider, prompt):
    """Run Antigravity Python SDK with the given prompt."""
    mgr = SessionManager()
    try:
        backend = AntigravitySDKBackend(mgr)
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        if provider:
            os.environ["AGY_PROVIDER"] = provider
        
        response = backend.send_message(prompt)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@antigravity.command(name="headless")
@click.option("--api-key", "-k", envvar="GEMINI_API_KEY", help="Google AI Studio API key")
@click.option("--provider", "-p", default="gemini", help="Provider to use")
@click.argument("prompt")
def antigravity_headless(api_key, provider, prompt):
    """Run Antigravity in headless mode."""
    mgr = SessionManager()
    try:
        backend = HeadlessConfigBackend(mgr)
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
        if provider:
            os.environ["AGY_PROVIDER"] = provider
        
        response = backend.send_message(prompt)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.group()
def tools():
    """AI tools and utilities."""
    pass

@tools.command(name="audit")
@click.option("--path", "-p", default=".", help="Path to codebase")
@click.option("--type", "-t", type=click.Choice(["codebase", "security", "performance", "dependencies"]), 
              default="codebase", help="Type of audit")
def audit_tool(path, type):
    """Run audit agent on codebase."""
    try:
        agent = AuditAgent()
        
        if type == "codebase":
            result = agent.audit_codebase(path)
        elif type == "security":
            result = agent.security_scan(path)
        elif type == "performance":
            result = agent.performance_analysis(path)
        elif type == "dependencies":
            result = agent.dependency_audit(path)
        
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@tools.command(name="search")
@click.option("--query", "-q", required=True, help="Search query")
@click.option("--type", "-t", type=click.Choice(["web", "code", "docs", "local"]), 
              default="web", help="Type of search")
@click.option("--limit", "-l", default=5, help="Maximum results")
def search_tool(query, type, limit):
    """Run search bridge."""
    try:
        bridge = SearchBridge()
        
        if type == "web":
            results = bridge.web_search(query, limit)
        elif type == "code":
            results = bridge.code_search(query, limit=limit)
        elif type == "docs":
            results = bridge.documentation_search(query, limit=limit)
        elif type == "local":
            results = bridge.local_search(query, limit=limit)
        
        click.echo(json.dumps(results, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.group()
def foss():
    """FOSS alternatives to Antigravity."""
    pass

@foss.command(name="eigent")
@click.option("--base-url", "-u", default="http://localhost:8000", help="Eigent AI server URL")
@click.option("--api-key", "-k", envvar="EIGENT_API_KEY", help="Eigent AI API key")
@click.argument("prompt")
def eigent_ai(base_url, api_key, prompt):
    """Run Eigent AI backend."""
    mgr = SessionManager()
    try:
        backend = EigentAIBackend(mgr, base_url=base_url, api_key=api_key)
        response = backend.send_message(prompt)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@foss.command(name="opencode")
@click.option("--model", "-m", default="default", help="Model to use")
@click.option("--provider", "-p", default="auto", help="Provider to use")
@click.argument("prompt")
def open_code(model, provider, prompt):
    """Run OpenCode backend."""
    mgr = SessionManager()
    try:
        backend = OpenCodeBackend(mgr, model=model, provider=provider)
        response = backend.send_message(prompt)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@foss.command(name="velocity")
@click.option("--model", "-m", default="default", help="Model to use")
@click.option("--provider", "-p", default="auto", help="Provider to use")
@click.argument("prompt")
def velocity(model, provider, prompt):
    """Run Velocity backend."""
    mgr = SessionManager()
    try:
        backend = VelocityBackend(mgr, model=model, provider=provider)
        response = backend.send_message(prompt)
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option("--provider", "-p", default="deepseek")
@click.option("--session", "-s", default=None)
@click.argument("prompt")
def chat(provider, session, prompt):
    """Send a chat message using the specified provider."""
    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, prompt, session))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.option("--provider", "-p", default="colab")
@click.argument("code")
def execute(provider, code):
    """Execute code using the specified provider."""
    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, code))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    import os
    cli()
