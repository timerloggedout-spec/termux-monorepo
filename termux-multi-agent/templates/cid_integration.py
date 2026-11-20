import json
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CIDPattern:
    name: str
    cedar_script: str
    cid_py: str
    file: str
    priority: str
    status: str

class CIDRegistry:
    def __init__(self, registry_path: str = "~/termux-multi-agent/workspace/cid_registry.json"):
        self.registry_path = Path(registry_path).expanduser()
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.patterns: Dict[str, CIDPattern] = self._load_registry()

    def _load_registry(self) -> Dict[str, CIDPattern]:
        if not self.registry_path.exists():
            return {}
        with open(self.registry_path) as f:
            return {
                k: CIDPattern(**v)
                for k, v in json.load(f).items()
            }

    def _save_registry(self):
        with open(self.registry_path, "w") as f:
            json.dump(
                {k: v.__dict__ for k, v in self.patterns.items()},
                f,
                indent=2
            )

    def add_seed(self, name: str, cedar_script: str, file: str, priority: str = "elite"):
        pattern = CIDPattern(
            name=name,
            cedar_script=cedar_script,
            cid_py="",
            file=file,
            priority=priority,
            status="seed"
        )
        self.patterns[name] = pattern
        self._save_registry()

    def evolve_to_cid(self, name: str, cid_py: str):
        if name in self.patterns:
            self.patterns[name].cid_py = cid_py
            self.patterns[name].status = "evolved"
            self._save_registry()

    def get_patterns_by_priority(self, priority: str) -> List[CIDPattern]:
        return [p for p in self.patterns.values() if p.priority == priority]

    def get_evolved_patterns(self) -> List[CIDPattern]:
        return [p for p in self.patterns.values() if p.status == "evolved"]
