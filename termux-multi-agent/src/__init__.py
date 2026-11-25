"""Legacy agent package, with optional monorepo adapters on its search path.

The existing test/bootstrap path intentionally prefers this package. Keep its
legacy modules authoritative, while making root-only Swarms/Research adapters
available without changing global sys.path or breaking standalone checkouts.
"""
from pathlib import Path

_optional_adapters = Path(__file__).resolve().parents[2] / "src"
if (_optional_adapters / "swarms_adapter.py").is_file():
    __path__.append(str(_optional_adapters))
