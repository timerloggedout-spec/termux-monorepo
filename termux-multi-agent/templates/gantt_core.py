import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime, timedelta

@dataclass
class GanttTask:
    id: str
    name: str
    start: str
    end: str
    dependencies: List[str] = None
    type: str = "task"

    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

class GanttChart:
    def __init__(self, output_path: str = "~/termux-multi-agent/workspace/gantt.json"):
        self.output_path = Path(output_path).expanduser()
        self.tasks: List[GanttTask] = []
    def add_task(self, task: GanttTask):
        self.tasks.append(task)
    def add_forecast_tasks(self, count: int = 5, avg_duration_minutes: int = 10):
        now = datetime.now()
        for i in range(count):
            start = now + timedelta(minutes=i * avg_duration_minutes)
            end = start + timedelta(minutes=avg_duration_minutes)
            self.tasks.append(GanttTask(
                id=f"forecast_{i}",
                name=f"Predicted Task {i+1}",
                start=start.isoformat(),
                end=end.isoformat(),
                type="forecast"
            ))
    def save(self):
        with open(self.output_path, "w") as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)
    def to_mermaid(self) -> str:
        lines = ["gantt"]
        lines.append("    dateFormat  YYYY-MM-DDTHH:mm:ss")
        lines.append("    axisFormat %H:%M")
        for task in self.tasks:
            lines.append(f"    {task.name} :{task.id}, {task.start}, {task.end}")
            if task.dependencies:
                for dep in task.dependencies:
                    lines.append(f"    {dep} --> {task.id}")
        return "\n".join(lines)
