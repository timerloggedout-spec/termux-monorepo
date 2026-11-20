from dataclasses import dataclass, field
from typing import Dict, List
from collections import defaultdict

@dataclass
class Task:
    id: str
    name: str
    duration: float
    depends_on: List[str] = field(default_factory=list)

@dataclass
class CPMResult:
    critical_path: List[str]
    parallel_groups: Dict[float, List[str]]
    total_duration: float

def compute_cpm(tasks: List[Task]) -> CPMResult:
    graph = {t.id: t for t in tasks}
    in_degree = defaultdict(int)
    adj = defaultdict(list)
    for task in tasks:
        for dep in task.depends_on:
            adj[dep].append(task.id)
            in_degree[task.id] += 1
    queue = [t.id for t in tasks if in_degree[t.id] == 0]
    topo_order = []
    while queue:
        node = queue.pop(0)
        topo_order.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    earliest = {t.id: 0.0 for t in tasks}
    for node in topo_order:
        task = graph[node]
        for dep in task.depends_on:
            if earliest[node] < earliest[dep] + graph[dep].duration:
                earliest[node] = earliest[dep] + graph[dep].duration
    latest = {t.id: earliest[t.id] + graph[t.id].duration for t in tasks}
    for node in reversed(topo_order):
        task = graph[node]
        for neighbor in adj[node]:
            if latest[node] > latest[neighbor] - graph[node].duration:
                latest[node] = latest[neighbor] - graph[node].duration
    critical_path = [node for node in topo_order if earliest[node] == latest[node]]
    parallel_groups = defaultdict(list)
    for node in topo_order:
        parallel_groups[earliest[node]].append(node)
    return CPMResult(
        critical_path=critical_path,
        parallel_groups=dict(parallel_groups),
        total_duration=max(earliest.values()) + max(t.duration for t in tasks)
    )
