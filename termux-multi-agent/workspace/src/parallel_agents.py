#!/usr/bin/env python3
"""1337 Team – Parallel multi‑agent system for A/B/C testing refactor strategies."""
import sys, os, json, time, threading, queue
from pathlib import Path

from templates.volley_logger import log_volley
from templates.priority_matrix import PriorityMatrix
from templates.skillopt_core import SkillTrainer, Rollout
import time
from datetime import datetime, timezone
skill_trainer = SkillTrainer()
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable

HOME = Path.home()
sys.path.insert(0, str(HOME / 'deepcli'))
sys.path.insert(0, str(HOME / 'cli-synthegration'))
sys.path.insert(0, str(HOME / 'termux-multi-agent'))

from deepcli.core import get_token, create_session, chat_completion, stream_completion
from success_metrics import RefactorELO, ComplexityEstimator
from synthegration_index import MessageIndex

@dataclass
class AgentTask:
    """One refactor attempt with a specific strategy."""
    id: str
    strategy: str  # e.g., 'minimal', 'aggressive', 'document-first', 'test-first'
    system_prompt: str
    target_file: str
    original_code: str
    language: str
    result: Optional[str] = None
    success: bool = False
    elo_delta: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    
    def run(self, token: str, session_id: str):

        volley_id = f"abc_{self.id}_{int(time.time())}"
        log_volley(
            volley_id=volley_id,
            from_agent="parallel_agent",
            to_agent="deepseek_coder",
            status="progress",
            volley_type="abc_test",
            file=self.target_file,
            strategy=self.strategy,
            priority=priority_matrix.get_priority(volley_id)
        )
        """Execute the refactor attempt."""
        self.start_time = time.time()
        user_prompt = f"File: {self.target_file}\nLanguage: {self.language}\n\nOriginal code:\n```\n{self.original_code}\n```\n\n{self.strategy} refactor this code. Reply with ONLY the improved code in a code block."
        
        try:
            response = chat_completion(token, user_prompt, session_id,
                                       model_type="default", auto_continue=True, max_continues=2)
            # Extract code block
            import re
            blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
            if blocks:
                self.result = blocks[-1]
                self.success = True
            else:
                self.result = response
                self.success = any(line.strip().startswith(('def ', 'class ', 'import ', 'from '))
                                  for line in response.splitlines())
        except Exception as e:
            self.result = str(e)
            self.success = False
        self.end_time = time.time()

        # --- Log volley end ---
        log_volley(
            volley_id=volley_id,
            from_agent="parallel_agent",
            to_agent="deepseek_coder",
            status="complete" if self.success else "failed",
            volley_type="abc_test",
            file=self.target_file,
            strategy=self.strategy,
            start_time=self.start_time,
            end_time=time.time(),
            duration_sec=time.time() - self.start_time,
            success=self.success,
            error=self.result if not self.success else None
        )
        # --- Save rollout for SkillOpt ---
        skill_trainer.save_rollout(Rollout(
            input=self.original_code,
            output=self.result,
            success=self.success,
            strategy=self.strategy,
            duration=time.time() - self.start_time,
            elo_delta=self.elo_delta,
            file=self.target_file,
            timestamp=str(int(time.time()))
        ))
        return self

class L33TTeam:
    """Parallel agent orchestrator for A/B/C testing."""
    
    STRATEGIES = {
        'minimal': "Make only the minimal changes necessary.",
        'aggressive': "Aggressively optimize for performance and readability.",
        'safe': "Prioritize safety — add error handling and edge case coverage.",
        'document': "Add comprehensive docstrings and comments while refactoring.",
        'test-first': "First write test cases, then refactor to pass them.",
        'pythonic': "Make the code idiomatic and Pythonic using best practices.",
        'dry': "Eliminate all duplication (DRY principle) — extract shared logic.",
    }
    
    def __init__(self, max_parallel: int = 3):
        self.max_parallel = max_parallel
        self.token = get_token()
        self.results: List[AgentTask] = []
        self.elo = RefactorELO()
        self.complexity = ComplexityEstimator()
        self.timeline: List[Dict] = []
        self._load_timeline()
    
    def _load_timeline(self):
        timeline_file = HOME / 'cli-synthegration' / 'metrics' / 'agent_timeline.jsonl'
        if timeline_file.exists():
            with open(timeline_file) as f:
                for line in f:
                    if line.strip():
                        self.timeline.append(json.loads(line))
    
    def _save_timeline(self, entry: Dict):
        timeline_file = HOME / 'cli-synthegration' / 'metrics' / 'agent_timeline.jsonl'
        timeline_file.parent.mkdir(parents=True, exist_ok=True)
        entry['ts'] = datetime.now(timezone.utc).isoformat()
        self.timeline.append(entry)
        with open(timeline_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def run_abc_test(self, target_file: str, strategies: List[str] = None,
                     max_winners: int = 1) -> Dict:
        """Run A/B/C test: execute multiple strategies in parallel, pick winner."""
        if strategies is None:
            strategies = ['minimal', 'safe', 'pythonic']
        
        target_path = Path(target_file)
        if not target_path.exists():
            return {'error': f'File not found: {target_file}'}
        
        original = target_path.read_text()
        lang = target_path.suffix.lstrip('.') or 'python'
        
        # Create tasks
        tasks = []
        for i, strategy in enumerate(strategies):
            sys_prompt = self.STRATEGIES.get(strategy, strategy)
            task = AgentTask(
                id=f"agent-{i+1}",
                strategy=strategy,
                system_prompt=sys_prompt,
                target_file=target_file,
                original_code=original,
                language=lang
            )
            tasks.append(task)
        
        # Run in parallel using threads
        results_queue = queue.Queue()
        threads = []
        
        def worker(task):
            sid = create_session(self.token, "default")
            result = task.run(self.token, sid)
            results_queue.put(result)
        
        # Execute in batches of max_parallel
        for i in range(0, len(tasks), self.max_parallel):
            batch = tasks[i:i+self.max_parallel]
            batch_threads = []
            for task in batch:
                t = threading.Thread(target=worker, args=(task,))
                t.start()
                batch_threads.append(t)
            for t in batch_threads:
                t.join(timeout=120)
        
        # Collect results
        all_results = []
        while not results_queue.empty():
            all_results.append(results_queue.get())
        
        # Score results
        for task in all_results:
            # Calculate ELO delta
            task.elo_delta = self.elo.update(
                task.strategy, task.language, task.success,
                effort=self.complexity.estimate(task.original_code)[1]
            )
            
            # Apply the result if successful
            if task.success and task.result:
                output_file = target_path.parent / f"{target_path.stem}_{task.strategy}{target_path.suffix}"
                output_file.write_text(task.result)
                task.result = str(output_file)  # store path instead of full code
        
        # Sort by success then speed
        all_results.sort(key=lambda t: (-t.success, t.end_time - t.start_time))
        
        # Log to timeline
        for task in all_results:
            self._save_timeline({
                'type': 'abc_test',
                'target': target_file,
                'strategy': task.strategy,
                'success': task.success,
                'elo_delta': task.elo_delta,
                'duration': task.end_time - task.start_time,
                'agent_id': task.id
            })
        
        return {
            'total': len(all_results),
            'successful': sum(1 for t in all_results if t.success),
            'winners': [
                {'strategy': t.strategy, 'duration': f"{t.end_time - t.start_time:.1f}s",
                 'elo_delta': t.elo_delta, 'output': t.result}
                for t in all_results[:max_winners] if t.success
            ],
            'all': [
                {'strategy': t.strategy, 'success': t.success,
                 'duration': f"{t.end_time - t.start_time:.1f}s"}
                for t in all_results
            ]
        }
    
    def analyze_timeline(self, days: int = 30) -> Dict:
        """Analyze agent performance over time."""
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
        recent = [e for e in self.timeline
                 if datetime.fromisoformat(e['ts']).timestamp() > cutoff]
        
        by_strategy = {}
        for entry in recent:
            s = entry.get('strategy', 'unknown')
            if s not in by_strategy:
                by_strategy[s] = {'attempts': 0, 'successes': 0, 'total_duration': 0}
            by_strategy[s]['attempts'] += 1
            if entry.get('success'):
                by_strategy[s]['successes'] += 1
            by_strategy[s]['total_duration'] += entry.get('duration', 0)
        
        analysis = {}
        for s, stats in by_strategy.items():
            n = stats['attempts']
            analysis[s] = {
                'attempts': n,
                'success_rate': f"{stats['successes']/n*100:.1f}%" if n else 'N/A',
                'avg_duration': f"{stats['total_duration']/n:.1f}s" if n else 'N/A',
                'elo_rating': self.elo.ratings.get(
                    self.elo.pattern_hash(s, 'python'), 1200
                )
            }
        
        return {
            'period_days': days,
            'total_entries': len(recent),
            'by_strategy': analysis,
            'moving_average': self.elo.moving_average(window=50)
        }

if __name__ == '__main__':
    team = L33TTeam(max_parallel=3)
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        print(json.dumps(team.analyze_timeline(days), indent=2))
    elif len(sys.argv) > 2 and sys.argv[1] == 'test':
        target = sys.argv[2]
        strategies = sys.argv[3:] if len(sys.argv) > 3 else None
        result = team.run_abc_test(target, strategies)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: parallel_agents.py test <file> [strategy...]")
        print("       parallel_agents.py analyze [days]")
        print(f"\nAvailable strategies: {list(L33TTeam.STRATEGIES.keys())}")
