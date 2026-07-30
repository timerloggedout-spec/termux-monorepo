#!/usr/bin/env python3
"""
CedarIndex – Short hash pointers for CEDARscript commands.
Usage:
  python3 cid.py "CREATE FILE x WITH y"   -> returns pointer (e.g., →a3f9)
  python3 cid.py "→a3f9"                  -> returns expanded command
  python3 cid.py --list                   -> show all mappings
"""
import hashlib, json, sys, re
from pathlib import Path

class CedarIndex:
    PREFIX = "→"
    HASH_LEN = 4
    INDEX_FILE = Path.home() / ".cedar" / "cedar_index.json"

    def __init__(self):
        self._ptr_to_cmd = {}
        self._cmd_to_ptr = {}
        self._load()

    def _load(self):
        if self.INDEX_FILE.exists():
            with open(self.INDEX_FILE) as f:
                d = json.load(f)
                self._ptr_to_cmd = d.get("p2c", {})
                self._cmd_to_ptr = d.get("c2p", {})
        else:
            self.INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
            self._save()

    def _save(self):
        with open(self.INDEX_FILE, "w") as f:
            json.dump({"p2c": self._ptr_to_cmd, "c2p": self._cmd_to_ptr}, f, indent=2)

    def _norm(self, s): return ' '.join(s.split())
    def _hash36(self, s):
        h = hashlib.sha256(self._norm(s).encode()).digest()
        n = int.from_bytes(h[:8], 'big')
        alpha = "0123456789abcdefghijklmnopqrstuvwxyz"
        res = ""
        while n:
            n, r = divmod(n, 36)
            res = alpha[r] + res
        return (res[:self.HASH_LEN]).ljust(self.HASH_LEN, '0')

    def register(self, cmd):
        norm = self._norm(cmd)
        if norm in self._cmd_to_ptr:
            return self._cmd_to_ptr[norm]
        ptr = self.PREFIX + self._hash36(cmd)
        col = 0
        while ptr in self._ptr_to_cmd and self._ptr_to_cmd[ptr] != norm:
            col += 1
            ptr = self.PREFIX + self._hash36(f"{cmd}{col}")
        self._ptr_to_cmd[ptr] = norm
        self._cmd_to_ptr[norm] = ptr
        self._save()
        return ptr

    def compress(self, cmd): return self.register(cmd)
    def expand(self, ptr): return self._ptr_to_cmd.get(ptr)

# All known CEDARscript commands (≥37)
ALL_COMMANDS = [
    "CREATE FILE path WITH content",
    "UPDATE FILE path ... END UPDATE",
    "INSERT AT BEGINNING OF FILE path CONTENT content",
    "INSERT AT END OF FILE path CONTENT content",
    "INSERT AT LINE line OF FILE path CONTENT content",
    "DELETE FILE path",
    "MOVE FILE src TO dst",
    "CREATE FUNCTION name ... END FUNCTION",
    "UPDATE FUNCTION name ... END UPDATE",
    "INSERT BEFORE FUNCTION name CONTENT code",
    "INSERT AFTER FUNCTION name CONTENT code",
    "INSERT AT BEGINNING OF FUNCTION name CONTENT code",
    "INSERT AT END OF FUNCTION name CONTENT code",
    "INSERT AT LINE line OF FUNCTION name CONTENT code",
    "DELETE FUNCTION name",
    "MOVE FUNCTION name BEFORE FUNCTION target",
    "MOVE FUNCTION name AFTER FUNCTION target",
    "CREATE CLASS name ... END CLASS",
    "UPDATE CLASS name ... END UPDATE",
    "CREATE METHOD method IN CLASS class ... END METHOD",
    "UPDATE METHOD method IN CLASS class ... END UPDATE",
    "INSERT BEFORE METHOD method IN CLASS class CONTENT code",
    "INSERT AFTER METHOD method IN CLASS class CONTENT code",
    "DELETE METHOD method IN CLASS class",
    "MOVE METHOD method IN CLASS class BEFORE METHOD target",
    "SELECT LOCATION OF FUNCTION name",
    "SELECT LOCATION OF CLASS name",
    "SELECT LOCATION OF METHOD method IN CLASS class",
    "SELECT LOCATION OF IDENTIFIER name",
    "SELECT CALLS OF FUNCTION name",
    "SELECT REFERENCES OF IDENTIFIER name",
    "SELECT DEFINITION OF IDENTIFIER name",
    "SELECT ALL FUNCTIONS IN FILE path",
    "SELECT ALL CLASSES IN FILE path",
    "SELECT ALL METHODS IN CLASS class",
    "SELECT ALL VARIABLES IN FILE path",
    "SELECT ALL IMPORTS IN FILE path",
    "RENAME FUNCTION old TO new",
    "RENAME CLASS old TO new",
    "RENAME METHOD old TO new IN CLASS class",
    "RENAME VARIABLE old TO new IN SCOPE file",
    "EXTRACT CODE FROM start TO end INTO FUNCTION new",
    "INLINE FUNCTION call",
    "ADD PARAMETER param TO FUNCTION func",
    "REMOVE PARAMETER param FROM FUNCTION func",
]

if __name__ == "__main__":
    ci = CedarIndex()
    if len(sys.argv) < 2:
        print("Usage: cid.py <command or pointer> [--list]")
        sys.exit(1)
    if sys.argv[1] == "--list":
        for ptr, cmd in ci._ptr_to_cmd.items():
            print(f"{ptr}  →  {cmd}")
        sys.exit(0)
    arg = sys.argv[1]
    if arg.startswith(CedarIndex.PREFIX):
        exp = ci.expand(arg)
        print(exp if exp else f"Unknown pointer: {arg}")
    else:
        # Try to register as a command
        ptr = ci.compress(arg)
        print(ptr)
        # Also pre‑register all standard commands if first run
        if len(ci._cmd_to_ptr) < 10:
            for cmd in ALL_COMMANDS:
                ci.compress(cmd)
            ci._save()
            print(f"Pre‑registered {len(ALL_COMMANDS)} commands.", file=sys.stderr)
