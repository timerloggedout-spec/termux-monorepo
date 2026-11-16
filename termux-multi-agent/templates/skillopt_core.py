import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
import time

@dataclass
class Rollout:
    input: str
    output: str
    success: bool
    strategy: str
    duration: float
    elo_delta: float
    file: str
    timestamp: str

class SkillTrainer:
    def __init__(self, skills_dir: str = "~/termux-multi-agent/skills", rollouts_dir: str = "~/termux-multi-agent/skills/rollouts"):
        self.skills_dir = Path(skills_dir).expanduser()
        self.rollouts_dir = Path(rollouts_dir).expanduser()
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.rollouts_dir.mkdir(parents=True, exist_ok=True)
    def save_rollout(self, rollout: Rollout):
        rollout_path = self.rollouts_dir / f"{rollout.timestamp}_{rollout.strategy}.json"
        with open(rollout_path, "w") as f:
            json.dump(rollout.__dict__, f, indent=2)
    def load_rollouts(self) -> List[Rollout]:
        rollouts = []
        for file in self.rollouts_dir.glob("*.json"):
            with open(file) as f:
                data = json.load(f)
                rollouts.append(Rollout(**data))
        return rollouts
    def train_strategy(self, strategy: str, rollouts: List[Rollout]) -> Dict:
        strategy_file = self.skills_dir / f"{strategy}.md"
        if not strategy_file.exists():
            strategy_file.write_text(f"# {strategy}\n\n## Rules\n- Default rules for {strategy}.\n")
        successful_rollouts = [r for r in rollouts if r.strategy == strategy and r.success]
        if not successful_rollouts:
            return {"status": "no_data", "strategy": strategy}
        with open(strategy_file, "a") as f:
            f.write("\n## Successful Examples\n")
            for rollout in successful_rollouts[-5:]:
                f.write(f"\n### Example {rollout.timestamp}\n")
                f.write(f"- **Input**: {rollout.input[:100]}...\n")
                f.write(f"- **Output**: {rollout.output[:100]}...\n")
                f.write(f"- **Duration**: {rollout.duration:.2f}s\n")
        return {"status": "updated", "strategy": strategy, "examples_added": len(successful_rollouts[-5:])}
    def train_all(self):
        rollouts = self.load_rollouts()
        strategies = set(r.strategy for r in rollouts)
        results = {}
        for strategy in strategies:
            results[strategy] = self.train_strategy(strategy, rollouts)
        return results
