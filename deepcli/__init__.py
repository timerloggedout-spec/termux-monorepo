"""DeepCLI – DeepSeek web-wrapper CI agent + session manager."""
import os

__version__ = "0.1.0"

# Extend package path so nested modules in deepcli/deepcli/ (like core) are accessible via deepcli.core
_nested_path = os.path.join(os.path.dirname(__file__), "deepcli")
if os.path.exists(_nested_path) and _nested_path not in __path__:
    __path__.append(_nested_path)
