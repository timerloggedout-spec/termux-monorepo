from pathlib import Path
from dataclasses import dataclass
import time

@dataclass
class ContextEntry:
    intent: str
    constraints: list
    evolved_context: list

class ContextManager:
    def __init__(self, context_path: str = "~/termux-multi-agent/context.md"):
        self.context_path = Path(context_path).expanduser()
        self.context_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.context_path.exists():
            self.context_path.write_text("# Repository Context\n\n## Intent\n\n## Constraints\n\n## Evolved Context\n")
    def add_constraint(self, constraint: str, reason: str):
        with open(self.context_path, "a") as f:
            f.write(f"- **{constraint}**: {reason}\n")
    def add_evolved_context(self, note: str):
        with open(self.context_path, "a") as f:
            f.write(f"- [{time.strftime('%Y-%m-%d')}] {note}\n")
    def get_context(self) -> str:
        return self.context_path.read_text()
