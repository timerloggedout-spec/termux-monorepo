# multi-ai-cli recon — 2026-10-02

## tree
/data/data/com.termux/files/home/multi-ai-cli
/data/data/com.termux/files/home/multi-ai-cli/RECON-2026-10-02
/data/data/com.termux/files/home/multi-ai-cli/RECON-2026-10-02/REPORT.md
/data/data/com.termux/files/home/multi-ai-cli/backends
/data/data/com.termux/files/home/multi-ai-cli/backends/__pycache__
/data/data/com.termux/files/home/multi-ai-cli/backends/__pycache__/deepseek.cpython-314.pyc
/data/data/com.termux/files/home/multi-ai-cli/backends/base.py
/data/data/com.termux/files/home/multi-ai-cli/backends/claude_web.py
/data/data/com.termux/files/home/multi-ai-cli/backends/colab.py
/data/data/com.termux/files/home/multi-ai-cli/backends/deepseek.py
/data/data/com.termux/files/home/multi-ai-cli/backends/gemini_web.py
/data/data/com.termux/files/home/multi-ai-cli/backends/mistral_web.py
/data/data/com.termux/files/home/multi-ai-cli/bridge
/data/data/com.termux/files/home/multi-ai-cli/bridge/mistral_bridge.py
/data/data/com.termux/files/home/multi-ai-cli/ci_mode.py
/data/data/com.termux/files/home/multi-ai-cli/cli.py
/data/data/com.termux/files/home/multi-ai-cli/config.yaml
/data/data/com.termux/files/home/multi-ai-cli/core
/data/data/com.termux/files/home/multi-ai-cli/core/__pycache__
/data/data/com.termux/files/home/multi-ai-cli/core/__pycache__/cache.cpython-314.pyc
/data/data/com.termux/files/home/multi-ai-cli/core/__pycache__/chat_dispatcher.cpython-314.pyc
/data/data/com.termux/files/home/multi-ai-cli/core/__pycache__/session_manager.cpython-314.pyc
/data/data/com.termux/files/home/multi-ai-cli/core/cache.py
/data/data/com.termux/files/home/multi-ai-cli/core/chat_dispatcher.py
/data/data/com.termux/files/home/multi-ai-cli/core/session_manager.py
/data/data/com.termux/files/home/multi-ai-cli/harvesters
/data/data/com.termux/files/home/multi-ai-cli/harvesters/capture-mistral-token.cjs
/data/data/com.termux/files/home/multi-ai-cli/harvesters/diag-mistral.cjs
/data/data/com.termux/files/home/multi-ai-cli/harvesters/mistral_cookies.cjs
/data/data/com.termux/files/home/multi-ai-cli/sandbox
/data/data/com.termux/files/home/multi-ai-cli/sandbox/README.md
/data/data/com.termux/files/home/multi-ai-cli/sandbox/backends
/data/data/com.termux/files/home/multi-ai-cli/sandbox/backends/mistral_v1.py
/data/data/com.termux/files/home/multi-ai-cli/utils
/data/data/com.termux/files/home/multi-ai-cli/utils/debug_deepseek.py
/data/data/com.termux/files/home/multi-ai-cli/utils/promote_backend.sh

## providers stubbed

## token dir
total 60
drwx------.  2 u0_a216 u0_a216  4096 Jun 27 00:20 .
drwx------. 86 u0_a216 u0_a216 12288 Oct  2 13:11 ..
-rw-------.  1 u0_a216 u0_a216  1444 Jun 27 00:20 mistral_chromium_cookies.json
-rwx------.  1 u0_a216 u0_a216  7002 Jun 26 23:35 mistral_cookies.json
-rw-------.  1 u0_a216 u0_a216 31540 Jun 27 00:20 mistral_debug.png

## cli.py head
#!/usr/bin/env python3
import click
from core.session_manager import SessionManager
from core.chat_dispatcher import ChatDispatcher

@click.group()
def cli():
    pass

@cli.command()
@click.option("--provider", "-p", default="deepseek")
@click.option("--session", "-s", default=None)
@click.argument("prompt")
def chat(provider, session, prompt):
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
    mgr = SessionManager()
    dispatcher = ChatDispatcher(mgr)
    try:
        click.echo(dispatcher.send(provider, code))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == "__main__":
    cli()

## README / docs
