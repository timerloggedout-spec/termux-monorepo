#!/usr/bin/env python3
"""Multi-AI CLI - Main Entry Point

This is the main entry point for the multi-ai-cli project.
It provides a unified interface for selecting between different AI providers.

Usage:
    python -m multi_ai_cli.main [command] [options]
    
    or
    
    multi-ai-cli [command] [options]
"""
import sys
import os

# Add the multi-ai-cli directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mistralai_cli import cli

if __name__ == "__main__":
    # Check if we should run a specific provider directly
    if len(sys.argv) > 1 and sys.argv[1] == "--provider":
        # Handle provider selection
        if len(sys.argv) > 2:
            provider_name = sys.argv[2]
            args = sys.argv[3:]
            
            # Run the provider
            from mistralai_cli import get_available_providers, console
            
            providers = get_available_providers()
            if provider_name in providers:
                prov_info = providers[provider_name]
                if prov_info.get("available", True):
                    import subprocess
                    
                    if provider_name == "deepseek":
                        deepcli_path = os.path.expanduser("~/deepcli/deepcli.py")
                        if os.path.exists(deepcli_path):
                            cmd = ["python3", deepcli_path] + args
                            result = subprocess.run(cmd)
                            sys.exit(result.returncode)
                    
                    elif provider_name == "deepseek-tui":
                        tui_path = os.path.expanduser("~/deepcli-tui/tui.py")
                        if os.path.exists(tui_path):
                            cmd = ["python3", tui_path] + args
                            result = subprocess.run(cmd)
                            sys.exit(result.returncode)
            
            # If we get here, run the normal CLI
            cli()
        else:
            cli()
    else:
        # Run the normal CLI
        cli()
