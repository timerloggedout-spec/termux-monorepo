#!/usr/bin/env python3
"""Termux-specific utilities for Android environment."""
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rich.console import Console

console = Console()

class TermuxUtils:
    """Utilities specific to Termux environment."""
    
    @staticmethod
    def is_termux() -> bool:
        """Check if running in Termux."""
        return "com.termux" in os.environ.get("PREFIX", "")
    
    @staticmethod
    def get_termux_version() -> Optional[str]:
        """
        Retrieve the installed Termux version.
        
        Returns:
        	str: The Termux version, or None if it cannot be determined.
        """
        try:
            result = subprocess.run(
                ["termux-info"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.startswith("Termux version"):
                        return line.split(':', 1)[1].strip()
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_device_info() -> Dict:
        """
        Collect available Android device information.
        
        Returns:
            Dict: A dictionary containing available Android version, device model,
                and manufacturer values.
        """
        info = {}
        
        try:
            # Get Android version
            result = subprocess.run(
                ["getprop", "ro.build.version.release"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info["android_version"] = result.stdout.strip()
            
            # Get device model
            result = subprocess.run(
                ["getprop", "ro.product.model"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info["device_model"] = result.stdout.strip()
            
            # Get manufacturer
            result = subprocess.run(
                ["getprop", "ro.product.manufacturer"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info["manufacturer"] = result.stdout.strip()
            
        except Exception:
            pass
        
        return info
    
    @staticmethod
    def get_termux_storage() -> Optional[str]:
        """
        Determine the available Termux home directory.
        
        Returns:
        	str: The existing home directory path, or None if it does not exist.
        """
        storage_dir = os.environ.get("HOME", "/data/data/com.termux/files/home")
        if os.path.exists(storage_dir):
            return storage_dir
        return None
    
    @staticmethod
    def setup_storage() -> bool:
        """
        Request access to shared device storage in Termux.
        
        Returns:
            `true` if storage setup succeeds, `false` otherwise.
        """
        try:
            result = subprocess.run(
                ["termux-setup-storage"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_battery_status() -> Optional[Dict]:
        """
        Retrieve battery information from the Android system.
        
        Returns:
            Optional[Dict]: A dictionary of battery status fields, or `None` if the information cannot be retrieved.
        """
        try:
            result = subprocess.run(
                ["dumpsys", "battery"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                status = {}
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        status[key.strip()] = value.strip()
                return status
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_network_info() -> Optional[Dict]:
        """
        Determine the connectivity status reported by Android.
        
        Returns:
        	dict: A mapping containing connected Wi-Fi or mobile network types.
        	None: If the connectivity information cannot be retrieved.
        """
        try:
            result = subprocess.run(
                ["dumpsys", "connectivity"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                info = {}
                # Parse basic network info
                if "Wi-Fi" in result.stdout:
                    info["wifi"] = "connected"
                if "Mobile" in result.stdout:
                    info["mobile"] = "connected"
                return info
        except Exception:
            pass
        return None
    
    @staticmethod
    def send_notification(title: str, message: str) -> bool:
        """Send a notification using Termux."""
        try:
            result = subprocess.run(
                ["termux-notification", "--title", title, "--content", message],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def vibrate(duration: int = 100) -> bool:
        """
        Request device vibration for the specified duration.
        
        Parameters:
        	duration (int): Vibration duration in milliseconds. Defaults to 100.
        
        Returns:
        	bool: `True` if the vibration request succeeds, `False` otherwise.
        """
        try:
            result = subprocess.run(
                ["termux-vibrate", "-d", str(duration)],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_clipboard() -> Optional[str]:
        """Retrieve the current clipboard text.
        
        Returns:
        	str: The trimmed clipboard content, or `None` if retrieval fails.
        """
        try:
            result = subprocess.run(
                ["termux-clipboard-get"],
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
    def set_clipboard(text: str) -> bool:
        """
        Set the device clipboard content.
        
        Parameters:
        	text (str): Text to place on the clipboard.
        
        Returns:
        	`true` if the clipboard content was set successfully, `false` otherwise.
        """
        try:
            result = subprocess.run(
                ["termux-clipboard-set", text],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def share_text(text: str, title: str = "Share") -> bool:
        """
        Share text through Android's share interface.
        
        Parameters:
        	title (str): Accepted for API compatibility but not used.
        
        Returns:
        	bool: `true` if sharing succeeds, `false` otherwise.
        """
        try:
            result = subprocess.run(
                ["termux-share", "-a", "send", text],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def open_url(url: str) -> bool:
        """Open URL in browser."""
        try:
            result = subprocess.run(
                ["termux-open", url],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_installed_packages() -> List[str]:
        """Get list of installed Termux packages."""
        try:
            result = subprocess.run(
                ["pkg", "list-installed"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                packages = []
                for line in result.stdout.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        packages.append(line.split()[0])
                return packages
        except Exception:
            pass
        return []
    
    @staticmethod
    def install_package(package: str) -> bool:
        """Install a Termux package noninteractively.
        
        Parameters:
        	package (str): Name of the package to install.
        
        Returns:
        	bool: `True` if installation succeeds, `False` otherwise.
        """
        try:
            result = subprocess.run(
                ["pkg", "install", "-y", package],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @staticmethod
    def get_termux_env() -> Dict:
        """
        Collect defined Termux and Android environment variables.
        
        Returns:
            Dict: A mapping of available environment variable names to their values.
        """
        env = {}
        termux_vars = [
            "PREFIX", "HOME", "ANDROID_DATA", "ANDROID_ROOT",
            "TERMUX_VERSION", "TERMUX_API_VERSION"
        ]
        
        for var in termux_vars:
            value = os.environ.get(var)
            if value:
                env[var] = value
        
        return env

if __name__ == "__main__":
    # Example usage
    if TermuxUtils.is_termux():
        print("Running in Termux")
        print(f"Termux version: {TermuxUtils.get_termux_version()}")
        print(f"Device info: {TermuxUtils.get_device_info()}")
        print(f"Storage: {TermuxUtils.get_termux_storage()}")
        print(f"Battery: {TermuxUtils.get_battery_status()}")
        print(f"Network: {TermuxUtils.get_network_info()}")
        print(f"Environment: {TermuxUtils.get_termux_env()}")
    else:
        print("Not running in Termux")
