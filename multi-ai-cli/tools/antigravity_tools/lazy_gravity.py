"""
LazyGravity Bot
FOSS Discord/Telegram bot repository for remote Antigravity control.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable


class LazyGravityBot:
    """
    LazyGravity - A FOSS Discord/Telegram bot for remote Antigravity control.
    
    This bot allows you to remotely pass prompts and pipe terminal execution
    commands to your active Antigravity environments without needing direct
    access to the machine.
    
    Features:
    - Remote prompt execution
    - Terminal command piping
    - Multi-platform support (Discord, Telegram)
    - Session management
    """
    
    def __init__(self, 
                 api_key: str = None,
                 platform: str = "discord",
                 session_manager = None):
        """
        Initialize LazyGravity bot.
        
        Args:
            api_key: Platform API key (Discord bot token or Telegram bot token)
            platform: Platform to use ("discord" or "telegram")
            session_manager: Session manager for Antigravity
        """
        self.api_key = api_key or os.environ.get("LAZY_GRAVITY_API_KEY")
        self.platform = platform
        self.session_manager = session_manager
        self._bot = None
        self._running = False
        
    def is_available(self) -> bool:
        """Check if bot is available."""
        return bool(self.api_key) and self.platform in ["discord", "telegram"]
    
    async def start(self) -> bool:
        """Start the bot."""
        if not self.is_available():
            raise RuntimeError("Bot not available. Check API key and platform.")
        
        if self._running:
            return True
        
        if self.platform == "discord":
            await self._start_discord()
        elif self.platform == "telegram":
            await self._start_telegram()
        
        self._running = True
        return True
    
    async def stop(self) -> bool:
        """Stop the bot."""
        if not self._running:
            return True
        
        if self._bot:
            if self.platform == "discord":
                await self._bot.close()
            elif self.platform == "telegram":
                await self._bot.stop_polling()
        
        self._running = False
        return True
    
    async def _start_discord(self):
        """Start Discord bot."""
        try:
            import discord
            from discord.ext import commands
            
            intents = discord.Intents.default()
            intents.message_content = True
            
            self._bot = commands.Bot(command_prefix="!", intents=intents)
            
            @self._bot.event
            async def on_ready():
                print(f"LazyGravity Discord bot logged in as {self._bot.user}")
            
            @self._bot.command()
            async def agy(ctx, *, prompt: str):
                """Execute Antigravity prompt."""
                try:
                    # Use Antigravity backend to process prompt
                    from multi_ai_cli.backends.antigravity import AntigravitySDKBackend
                    backend = AntigravitySDKBackend(self.session_manager)
                    response = backend.send_message(prompt)
                    await ctx.send(f"**Antigravity Response:**\n{response}")
                except Exception as e:
                    await ctx.send(f"Error: {e}")
            
            @self._bot.command()
            async def exec(ctx, *, command: str):
                """Execute terminal command."""
                try:
                    import subprocess
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    output = result.stdout or result.stderr
                    await ctx.send(f"**Command Output:**\n```{output[:1000]}```")
                except Exception as e:
                    await ctx.send(f"Error: {e}")
            
            await self._bot.start(self.api_key)
            
        except ImportError:
            raise RuntimeError("discord.py not installed. Install with: pip install discord.py")
        except Exception as e:
            raise RuntimeError(f"Failed to start Discord bot: {e}")
    
    async def _start_telegram(self):
        """Start Telegram bot."""
        try:
            from telegram import Update, Bot
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
            
            self._bot = Bot(token=self.api_key)
            app = Application.builder().token(self.api_key).build()
            
            async def agy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Handle /agy command."""
                try:
                    prompt = " ".join(context.args)
                    if not prompt:
                        await update.message.reply_text("Usage: /agy <prompt>")
                        return
                    
                    from multi_ai_cli.backends.antigravity import AntigravitySDKBackend
                    backend = AntigravitySDKBackend(self.session_manager)
                    response = backend.send_message(prompt)
                    await update.message.reply_text(f"**Antigravity Response:**\n{response}")
                except Exception as e:
                    await update.message.reply_text(f"Error: {e}")
            
            async def exec_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
                """Handle /exec command."""
                try:
                    command = " ".join(context.args)
                    if not command:
                        await update.message.reply_text("Usage: /exec <command>")
                        return
                    
                    import subprocess
                    result = subprocess.run(
                        command,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    output = result.stdout or result.stderr
                    await update.message.reply_text(f"**Command Output:**\n```{output[:1000]}```")
                except Exception as e:
                    await update.message.reply_text(f"Error: {e}")
            
            app.add_handler(CommandHandler("agy", agy_command))
            app.add_handler(CommandHandler("exec", exec_command))
            
            await app.run_polling()
            
        except ImportError:
            raise RuntimeError("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
        except Exception as e:
            raise RuntimeError(f"Failed to start Telegram bot: {e}")
    
    async def send_prompt(self, prompt: str, channel_id: str = None) -> str:
        """
        Send a prompt to Antigravity via the bot.
        
        Args:
            prompt: The prompt to send
            channel_id: Optional channel ID to send to
            
        Returns:
            Response from Antigravity
        """
        if not self._running:
            raise RuntimeError("Bot is not running")
        
        try:
            from multi_ai_cli.backends.antigravity import AntigravitySDKBackend
            backend = AntigravitySDKBackend(self.session_manager)
            return backend.send_message(prompt)
        except Exception as e:
            raise RuntimeError(f"Failed to send prompt: {e}")
    
    async def execute_command(self, command: str, channel_id: str = None) -> str:
        """
        Execute a terminal command via the bot.
        
        Args:
            command: The command to execute
            channel_id: Optional channel ID to send output to
            
        Returns:
            Command output
        """
        try:
            import subprocess
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout or result.stderr
        except Exception as e:
            raise RuntimeError(f"Failed to execute command: {e}")
