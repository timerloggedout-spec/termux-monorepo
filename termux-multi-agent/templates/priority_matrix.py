from pathlib import Path
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PriorityScore:
    efficiency_impact: float
    elite_impact: float
    feature_impact: float
    total: float
    priority: str

class PriorityMatrix:
    def __init__(self, matrix_path: str = "~/termux-multi-agent/workspace/priority_matrix.json"):
        self.matrix_path = Path(matrix_path).expanduser()
        self.matrix_path.parent.mkdir(parents=True, exist_ok=True)
        self.scores: Dict[str, PriorityScore] = self._load_matrix()

    def _load_matrix(self) -> Dict[str, PriorityScore]:
        if not self.matrix_path.exists():
            return {}
        with open(self.matrix_path) as f:
            return {
                k: PriorityScore(**v)
                for k, v in json.load(f).items()
            }

    def _save_matrix(self):
        with open(self.matrix_path, "w") as f:
            json.dump(
                {k: v.__dict__ for k, v in self.scores.items()},
                f,
                indent=2
            )

    def score_task(
        self,
        task_id: str,
        efficiency_impact: float = 0,
        elite_impact: float = 0,
        feature_impact: float = 0,
        file: Optional[str] = None,
        volley_type: Optional[str] = None
    ) -> PriorityScore:
        total = efficiency_impact + elite_impact + feature_impact
        if total == 0:
            priority = "feature"
        else:
            if efficiency_impact >= elite_impact and efficiency_impact >= feature_impact:
                priority = "efficiency"
            elif elite_impact >= efficiency_impact and elite_impact >= feature_impact:
                priority = "elite"
            else:
                priority = "feature"
        score = PriorityScore(
            efficiency_impact=efficiency_impact,
            elite_impact=elite_impact,
            feature_impact=feature_impact,
            total=total,
            priority=priority
        )
        self.scores[task_id] = score
        self._save_matrix()
        return score

    def get_priority(self, task_id: str) -> str:
        return self.scores.get(task_id, PriorityScore(0, 0, 0, 0, "feature")).priority

    def get_top_tasks(self, priority: str, limit: int = 5) -> List[str]:
        filtered = [
            (task_id, score)
            for task_id, score in self.scores.items()
            if score.priority == priority
        ]
        filtered.sort(key=lambda x: x[1].total, reverse=True)
        return [task_id for task_id, _ in filtered[:limit]]

    def get_task_score(self, task_id: str) -> Optional[PriorityScore]:
        return self.scores.get(task_id)
